from Foundation import NSObject, NSLog
from runner import run_code
from codegen import generate_python_code
from storage import save_flow
import capture
import os
import datetime

from config import ROOT_DIR

class Delegate(NSObject):
    def showHistory_(self, _):
        from AppKit import NSWindow, NSScrollView, NSTextView, NSButton, NSTextField, NSMakeRect, NSWindowStyleMaskTitled, NSBackingStoreBuffered
        from storage import load_cache
        successes, failures = load_cache()
        all_flows = successes + failures
        all_flows.sort(key=lambda r: r.get('timestamp', ''), reverse=True)
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(100, 100, 800, 500), NSWindowStyleMaskTitled, NSBackingStoreBuffered, False)
        win.setTitle_("History: Successes & Failures")
        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 90, 760, 350))
        text_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 760, 350))
        text_view.setEditable_(False)
        scroll.setDocumentView_(text_view)
        scroll.setHasVerticalScroller_(True)
        # Search/filter field
        search_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 450, 300, 26))
        search_field.setPlaceholderString_("Search prompt or code…")
        search_btn = NSButton.alloc().initWithFrame_(NSMakeRect(330, 450, 80, 26))
        search_btn.setTitle_("Filter")
        search_btn.setTarget_(self)
        search_btn.setAction_("filterHistory:")
        # Compose history text
        def render_history(flows):
            lines = []
            for idx, rec in enumerate(flows):
                lines.append(f"[{idx+1}] {'✔️' if rec.get('reward')==1 else '❌'} {rec.get('timestamp','')}\nPrompt: {rec.get('prompt','')}\n")
            return "\n".join(lines)
        text_view.setString_(render_history(all_flows))
        # Add Replay, Edit, Delete fields/buttons
        idx_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 20, 60, 26))
        idx_field.setPlaceholderString_("#")
        replay_btn = NSButton.alloc().initWithFrame_(NSMakeRect(90, 20, 80, 26))
        replay_btn.setTitle_("Replay")
        replay_btn.setTarget_(self)
        replay_btn.setAction_("replayHistory:")
        edit_btn = NSButton.alloc().initWithFrame_(NSMakeRect(180, 20, 80, 26))
        edit_btn.setTitle_("Edit")
        edit_btn.setTarget_(self)
        edit_btn.setAction_("editHistory:")
        delete_btn = NSButton.alloc().initWithFrame_(NSMakeRect(270, 20, 80, 26))
        delete_btn.setTitle_("Delete")
        delete_btn.setTarget_(self)
        delete_btn.setAction_("deleteHistory:")
        # Store for later
        self._history_flows = all_flows
        self._history_idx_field = idx_field
        self._history_win = win
        self._history_text_view = text_view
        self._history_search_field = search_field
        self._history_all_flows = all_flows
        win.contentView().addSubview_(scroll)
        win.contentView().addSubview_(idx_field)
        win.contentView().addSubview_(replay_btn)
        win.contentView().addSubview_(edit_btn)
        win.contentView().addSubview_(delete_btn)
        win.contentView().addSubview_(search_field)
        win.contentView().addSubview_(search_btn)
        win.makeKeyAndOrderFront_(None)

    def filterHistory_(self, _):
        query = self._history_search_field.stringValue().strip().lower()
        if not query:
            filtered = self._history_all_flows
        else:
            filtered = [rec for rec in self._history_all_flows if query in rec.get('prompt','').lower() or query in rec.get('code','').lower()]
        # Update the text view
        lines = []
        for idx, rec in enumerate(filtered):
            lines.append(f"[{idx+1}] {'✔️' if rec.get('reward')==1 else '❌'} {rec.get('timestamp','')}\nPrompt: {rec.get('prompt','')}\n")
        self._history_text_view.setString_("\n".join(lines))
        self._history_flows = filtered

    def replayHistory_(self, _):
        idx = int(self._history_idx_field.stringValue() or "0") - 1
        if 0 <= idx < len(self._history_flows):
            rec = self._history_flows[idx]
            self._load_cached_script(rec["code"], rec["prompt"])
            self._applescript_tag = 'cache'
            try:
                ok = run_code(rec["code"])
                self.last_success = ok
                self._update_status("✓ Success (replayed)" if ok else "✗ Failed (replayed)")
            except Exception as exc:
                self.last_success = False
                self._update_status(f"✗ Failed (replayed): {exc}")
                NSLog(f"[ERROR] {exc!r}")
            self._toggle_feedback(True)

    def editHistory_(self, _):
        idx = int(self._history_idx_field.stringValue() or "0") - 1
        if 0 <= idx < len(self._history_flows):
            rec = self._history_flows[idx]
            # Load code for editing in the main code view
            self._load_cached_script(rec["code"], rec["prompt"])
            self._applescript_tag = 'edit'
            self._update_status("Edit the code and click Run to test changes.")
            self._toggle_feedback(False)

    def deleteHistory_(self, _):
        import json
        idx = int(self._history_idx_field.stringValue() or "0") - 1
        if 0 <= idx < len(self._history_flows):
            rec = self._history_flows[idx]
            # Remove from file
            from config import STORE_PATH
            with open(STORE_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(STORE_PATH, 'w', encoding='utf-8') as f:
                for line in lines:
                    try:
                        entry = json.loads(line)
                        if not (entry.get('prompt') == rec.get('prompt') and entry.get('timestamp') == rec.get('timestamp')):
                            f.write(line)
                    except Exception:
                        f.write(line)
            self._update_status("Deleted from history. Please close and reopen history to refresh.")
    last_code: str = ""
    last_prompt: str = ""
    last_success: bool = False

    def regenerateCapturedFlow_(self, _):
        self._update_status("Regenerating AppleScript for captured flow...")
        applescript = capture.CAPTURE_SESSION.export_applescript()
        self.last_code = applescript
        self.code_view.setString_(applescript)
        self._applescript_tag = 'regenerated'
        self._update_status("AppleScript regenerated for captured flow. Click 'Test it' to try again.")
        self._show_regenerate_captured_btn(False)

    def _show_regenerate_captured_btn(self, show: bool):
        if not hasattr(self, 'regenerate_captured_btn'):
            return
        self.regenerate_captured_btn.setHidden_(not show)

    def run_(self, _):
        prompt = self.field.stringValue().strip()
        if not prompt:
            return
        self.last_prompt = prompt
        self._update_status("Working…")
        self._toggle_feedback(False)
        self.code_view.setString_("")
        # --- SMART CACHE LOGIC ---
        from storage import load_cache
        successes, _ = load_cache()
        for rec in successes:
            if rec["prompt"].strip().lower() == prompt.strip().lower():
                self._load_cached_script(rec["code"], rec["prompt"])
                self._applescript_tag = 'cache'
                # Automatically run the cached code
                try:
                    ok = run_code(rec["code"])
                    self.last_success = ok
                    self._update_status("✓ Success (from smart cache)" if ok else "✗ Failed (from smart cache)")
                except Exception as exc:
                    self.last_success = False
                    self._update_status(f"✗ Failed (from smart cache): {exc}")
                    NSLog(f"[ERROR] {exc!r}")
                self._toggle_feedback(True)
                return
        # --- END SMART CACHE LOGIC ---
        try:
            code = generate_python_code(prompt)
            self.last_code = code
            self.code_view.setString_(code)
            self._applescript_tag = 'generated'
            ok = run_code(code)
            self.last_success = ok
            self._update_status("✓ Success" if ok else "✗ Failed")
        except Exception as exc:
            self.last_success = False
            self._update_status(f"✗ Failed: {exc}")
            NSLog(f"[ERROR] {exc!r}")
        finally:
            self._toggle_feedback(True)

    def thumbUp_(self, _):
        self._save_feedback(True)

    def thumbDown_(self, _):
        self._save_feedback(False)

    def exit_(self, _):
        from AppKit import NSApplication
        NSApplication.sharedApplication().terminate_(None)

    def toggleCapture_(self, sender):
        if not hasattr(self, '_capture_active') or not self._capture_active:
            capture.CAPTURE_SESSION.start()
            self._update_status("Capture mode: Recording all clicks and keys…")
            self._capture_active = True
        else:
            capture.CAPTURE_SESSION.stop()
            applescript = capture.CAPTURE_SESSION.export_applescript()
            self.last_code = applescript
            self.last_prompt = "[Captured Flow]"
            self.code_view.setString_(applescript)
            self._applescript_tag = 'generated'
            self._update_status("Capture stopped. AppleScript generated.")
            self._capture_active = False
            self.test_btn.setHidden_(False)
            self._show_save_prompt_field(True)
            self._show_regenerate_captured_btn(True)

    def saveCapturedFlow_(self, _):
        prompt = self.save_prompt_field.stringValue().strip()
        if not prompt:
            self._update_status("Please enter a prompt to save this flow.")
            return
        code = self.last_code
        if not code:
            self._update_status("No captured code to save.")
            return
        save_flow(prompt, code, 1, "success")
        self._update_status("Captured flow saved and will be used for smart cache retrieval.")
        self._show_save_prompt_field(False)

    def _show_save_prompt_field(self, show: bool):
        if not hasattr(self, 'save_prompt_field') or not hasattr(self, 'save_prompt_btn'):
            return
        self.save_prompt_field.setHidden_(not show)
        self.save_prompt_btn.setHidden_(not show)

    def _load_cached_script(self, code, prompt):
        self.last_code = code
        self.last_prompt = prompt
        self.code_view.setString_(code)
        self._applescript_tag = 'cache'
        self._update_status("Loaded AppleScript from smart cache. Click 'Test it' to run.")

    def testScript_(self, _):
        import tempfile, subprocess, re
        code = self.code_view.string()
        tag = getattr(self, '_applescript_tag', None)
        if tag is None:
            tag = 'generated'
        if tag == 'cache':
            print("[AppleScript EXECUTION] Source: smart cache")
        else:
            print("[AppleScript EXECUTION] Source: generated")
        print(f"testing initiated [{tag}]")
        applescript_code = re.sub(r"```applescript\\s*", "", code, flags=re.IGNORECASE)
        applescript_code = re.sub(r"```", "", applescript_code)
        applescript_code = applescript_code.strip()
        print("AppleScript code to be executed:\n" + applescript_code)
        with tempfile.NamedTemporaryFile("w+", suffix=".applescript", delete=False) as tf:
            tf.write(applescript_code)
            tf.flush()
            tf_path = tf.name
        try:
            result = subprocess.run(["osascript", tf_path], capture_output=True, text=True)
            if result.returncode == 0:
                self._update_status(f"AppleScript [{tag}] ran successfully. Click 👍 if it worked!")
            else:
                self._update_status(f"AppleScript [{tag}] error: {result.stderr.strip()}")
                self._show_regenerate_button(True)
        except Exception as e:
            self._update_status(f"Failed to run AppleScript [{tag}]: {e}")
            self._show_regenerate_button(True)
        finally:
            os.remove(tf_path)
        self._toggle_feedback(True)

    def regenerateScript_(self, _):
        print("Regenerating AppleScript for robustness...")
        prompt = self.last_prompt or "[Captured Flow]"
        regen_prompt = prompt + "\n# Regenerate for maximum reliability. Use alternative strategies if needed."
        applescript = capture.CAPTURE_SESSION.export_applescript()
        self.last_code = applescript
        self.code_view.setString_(applescript)
        self._applescript_tag = 'regenerated'
        self._update_status("AppleScript regenerated. Click 'Test it' to try again.")
        self._show_regenerate_button(False)

    def _show_regenerate_button(self, show: bool):
        if not hasattr(self, 'regenerate_btn'):
            return
        self.regenerate_btn.setHidden_(not show)

    def _update_status(self, text: str):
        self.status_lbl.setStringValue_(text)

    def _toggle_feedback(self, visible: bool):
        self.up_btn.setHidden_(not visible)
        self.down_btn.setHidden_(not visible)

    def _save_feedback(self, success: bool):
        if not self.last_code or not self.last_prompt:
            return
        save_flow(self.last_prompt, self.last_code, int(success), "success" if success else "fail")
        self._toggle_feedback(False)
