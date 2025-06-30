from Foundation import NSObject, NSLog
from runner import run_code
from codegen import generate_python_code
from storage import save_flow
import capture
import os
import datetime
from config import ROOT_DIR
# Ensure all AppKit symbols are available for UI layout
from AppKit import (
    NSWindow, NSButton, NSTextField, NSScrollView, NSView, NSMakeRect, NSWindowStyleMaskTitled, NSBackingStoreBuffered,
    NSStackView, NSUserInterfaceLayoutOrientationVertical
    , NSFont
)

class Delegate(NSObject):
    def decompose_(self, _):
        from complex import decompose_request
        from AppKit import NSWindow, NSButton, NSTextField, NSMakeRect, NSWindowStyleMaskTitled, NSBackingStoreBuffered
        prompt = self.field.stringValue().strip()
        if not prompt:
            return
        self._update_status("Decomposing…")
        steps = decompose_request(prompt)
        self._step_descriptions = steps
        self._step_codes = [generate_python_code(s) for s in steps]
        self._step_valid = [False] * len(steps)
        # Main complex task window
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(120, 120, 740, 520), NSWindowStyleMaskTitled, NSBackingStoreBuffered, False)
        win.setTitle_("Complex Task!")
        win.setReleasedWhenClosed_(False)  # Prevent window from being deallocated
        # --- Scrollable area for prompt + steps ---
        scroll_height = 340
        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(10, 60, 720, scroll_height))
        scroll.setHasVerticalScroller_(True)
        # Use a plain NSView for stacking rows manually (not NSStackView, which can be buggy with dynamic content in PyObjC)
        steps_view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 700, 1000))
        scroll.setDocumentView_(steps_view)
        content_root = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 740, 520))
        win.setContentView_(content_root)
        win.makeKeyAndOrderFront_(None)
        scroll.setAutoresizingMask_(18)  # width + height flexible
        steps_view.setAutoresizingMask_(18)
        content_root.addSubview_(scroll)
        # --- Editable prompt field inside scrollable area ---
        prompt_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 10, 660, 24))
        prompt_field.setStringValue_(prompt)
        prompt_field.setBezeled_(True)
        prompt_field.setDrawsBackground_(True)
        prompt_field.setEditable_(True)
        prompt_field.setSelectable_(True)
        prompt_field.setFont_(NSFont.boldSystemFontOfSize_(14))
        steps_view.addSubview_(prompt_field)
        self._decompose_prompt_field = prompt_field
        # --- Step fields and buttons inside scrollable area ---
        self._step_test_btns = []
        self._step_validate_btns = []
        self._step_regen_btns = []
        self._step_delete_btns = []
        self._step_fields = []
        self._step_row_views = []
        def add_step_row(idx, desc):
            y = 50 + idx * 40
            row_view = NSView.alloc().initWithFrame_(NSMakeRect(0, y, 700, 36))
            # Editable step field
            step_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 6, 340, 24))
            step_field.setStringValue_(desc)
            step_field.setBezeled_(True)
            step_field.setDrawsBackground_(True)
            step_field.setEditable_(True)
            step_field.setSelectable_(True)
            step_field.setFont_(NSFont.systemFontOfSize_(13))
            row_view.addSubview_(step_field)
            # Test button
            test_btn = NSButton.alloc().initWithFrame_(NSMakeRect(370, 6, 60, 24))
            test_btn.setTitle_("Test")
            test_btn.setTag_(idx)
            test_btn.setTarget_(self)
            test_btn.setAction_("testStepInList:")
            test_btn.setEnabled_(True)
            row_view.addSubview_(test_btn)
            # Regenerate button
            regen_btn = NSButton.alloc().initWithFrame_(NSMakeRect(435, 6, 80, 24))
            regen_btn.setTitle_("Regenerate")
            regen_btn.setTag_(idx)
            regen_btn.setTarget_(self)
            regen_btn.setAction_("regenerateStepInList:")
            regen_btn.setEnabled_(True)
            row_view.addSubview_(regen_btn)
            # Validate button
            validate_btn = NSButton.alloc().initWithFrame_(NSMakeRect(520, 6, 70, 24))
            validate_btn.setTitle_("Validate")
            validate_btn.setTag_(idx)
            validate_btn.setTarget_(self)
            validate_btn.setAction_("validateStepInList:")
            validate_btn.setEnabled_(True)
            row_view.addSubview_(validate_btn)
            # Delete button
            delete_btn = NSButton.alloc().initWithFrame_(NSMakeRect(600, 6, 60, 24))
            delete_btn.setTitle_("Delete")
            delete_btn.setTag_(idx)
            delete_btn.setTarget_(self)
            delete_btn.setAction_("deleteStepInList:")
            delete_btn.setEnabled_(True)
            row_view.addSubview_(delete_btn)
            # Store references
            self._step_fields.insert(idx, step_field)
            self._step_test_btns.insert(idx, test_btn)
            self._step_regen_btns.insert(idx, regen_btn)
            self._step_validate_btns.insert(idx, validate_btn)
            self._step_delete_btns.insert(idx, delete_btn)
            self._step_row_views.insert(idx, row_view)
            steps_view.addSubview_(row_view)
        # Add all initial steps
        for idx, desc in enumerate(steps):
            add_step_row(idx, desc)
        self._step_descriptions = [f.stringValue() for f in self._step_fields]
        # Adjust steps_view height to fit all rows
        steps_view.setFrame_(NSMakeRect(0, 0, 700, 50 + len(steps) * 40 + 20))
        # Add Step button OUTSIDE scrollable area
        add_btn = NSButton.alloc().initWithFrame_(NSMakeRect(620, 470, 90, 28))
        add_btn.setTitle_("Add Step")
        add_btn.setTarget_(self)
        add_btn.setAction_("addStepInList:")
        content_root.addSubview_(add_btn)
        # Go back, Test all, Validate all OUTSIDE scrollable area
        back_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 10, 140, 28))
        back_btn.setTitle_("Go back to menu")
        back_btn.setTarget_(self)
        back_btn.setAction_("closeStepList:")
        content_root.addSubview_(back_btn)
        test_all_btn = NSButton.alloc().initWithFrame_(NSMakeRect(370, 10, 100, 28))
        test_all_btn.setTitle_("Test all")
        test_all_btn.setTarget_(self)
        test_all_btn.setAction_("testAllSteps:")
        content_root.addSubview_(test_all_btn)
        validate_all_btn = NSButton.alloc().initWithFrame_(NSMakeRect(480, 10, 120, 28))
        validate_all_btn.setTitle_("Validate All")
        validate_all_btn.setTarget_(self)
        validate_all_btn.setAction_("validateAllSteps:")
        content_root.addSubview_(validate_all_btn)
        self._step_list_win = win
        self._step_scroll = scroll
        self._step_content_view = stack_view
        self._add_step_btn = add_btn
        win.makeKeyAndOrderFront_(None)

    def addStepInList_(self, _):
        idx = len(self._step_fields)
        # Add new row to stack view
        row_view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 700, 36))
        step_field = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 6, 340, 24))
        step_field.setStringValue_("")
        step_field.setBezeled_(True)
        step_field.setDrawsBackground_(True)
        step_field.setEditable_(True)
        step_field.setSelectable_(True)
        row_view.addSubview_(step_field)
        test_btn = NSButton.alloc().initWithFrame_(NSMakeRect(350, 6, 60, 24))
        test_btn.setTitle_("Test")
        test_btn.setTag_(idx)
        test_btn.setTarget_(self)
        test_btn.setAction_("testStepInList:")
        test_btn.setEnabled_(True)
        row_view.addSubview_(test_btn)
        regen_btn = NSButton.alloc().initWithFrame_(NSMakeRect(415, 6, 80, 24))
        regen_btn.setTitle_("Regenerate")
        regen_btn.setTag_(idx)
        regen_btn.setTarget_(self)
        regen_btn.setAction_("regenerateStepInList:")
        regen_btn.setEnabled_(True)
        row_view.addSubview_(regen_btn)
        validate_btn = NSButton.alloc().initWithFrame_(NSMakeRect(500, 6, 70, 24))
        validate_btn.setTitle_("Validate")
        validate_btn.setTag_(idx)
        validate_btn.setTarget_(self)
        validate_btn.setAction_("validateStepInList:")
        validate_btn.setEnabled_(True)
        row_view.addSubview_(validate_btn)
        delete_btn = NSButton.alloc().initWithFrame_(NSMakeRect(580, 6, 60, 24))
        delete_btn.setTitle_("Delete")
        delete_btn.setTag_(idx)
        delete_btn.setTarget_(self)
        delete_btn.setAction_("deleteStepInList:")
        delete_btn.setEnabled_(True)
        row_view.addSubview_(delete_btn)
        self._step_fields.append(step_field)
        self._step_test_btns.append(test_btn)
        self._step_regen_btns.append(regen_btn)
        self._step_validate_btns.append(validate_btn)
        self._step_delete_btns.append(delete_btn)
        self._step_row_views.append(row_view)
        self._step_codes.append("")
        self._step_valid.append(False)
        self._step_descriptions.append("")
        self._step_scroll.documentView().addArrangedSubview_(row_view)
        # Scroll to bottom
        self._step_scroll.contentView().scrollToPoint_((0, self._step_scroll.documentView().frame().size.height))

    def deleteStepInList_(self, sender):
        idx = sender.tag()
        # Remove row view from stack view
        row_view = self._step_row_views.pop(idx)
        self._step_scroll.documentView().removeArrangedSubview_(row_view)
        row_view.removeFromSuperview()
        # Remove from all lists
        self._step_fields.pop(idx)
        self._step_test_btns.pop(idx)
        self._step_regen_btns.pop(idx)
        self._step_validate_btns.pop(idx)
        self._step_delete_btns.pop(idx)
        self._step_descriptions.pop(idx)
        self._step_codes.pop(idx)
        self._step_valid.pop(idx)
        # Re-tag all remaining buttons
        for i in range(len(self._step_row_views)):
            for btn_list in [self._step_test_btns, self._step_regen_btns, self._step_validate_btns, self._step_delete_btns]:
                btn_list[i].setTag_(i)
        # Go back to menu button
        back_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 5, 140, 28))
        back_btn.setTitle_("Go back to menu")
        back_btn.setTarget_(self)
        back_btn.setAction_("closeStepList:")
        win.contentView().addSubview_(back_btn)
        # Test all button
        test_all_btn = NSButton.alloc().initWithFrame_(NSMakeRect(370, 5, 100, 28))
        test_all_btn.setTitle_("Test all")
        test_all_btn.setTarget_(self)
        test_all_btn.setAction_("testAllSteps:")
        win.contentView().addSubview_(test_all_btn)
        # Validate all button
        validate_all_btn = NSButton.alloc().initWithFrame_(NSMakeRect(480, 5, 120, 28))
        validate_all_btn.setTitle_("Validate All")
        validate_all_btn.setTarget_(self)
        validate_all_btn.setAction_("validateAllSteps:")
        win.contentView().addSubview_(validate_all_btn)
        self._step_list_win = win
        win.makeKeyAndOrderFront_(None)


    # --- CLEANED: Only one set of handlers for stepwise/decompose mode ---
    def testStepInList_(self, sender):
        idx = sender.tag()
        # Get current step description from editable field
        desc = self._step_fields[idx].stringValue()
        self._step_descriptions[idx] = desc
        code = self._step_codes[idx] = generate_python_code(desc)
        print(f"[UI LOG] Test button pressed for step {idx+1} | Description: {desc}")
        try:
            import tempfile, subprocess, sys
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
                tf.write(code)
                tf.flush()
                tf_path = tf.name
            result = subprocess.run([sys.executable, tf_path], capture_output=True, text=True)
            output = result.stdout.strip()
            error = result.stderr.strip()
            if result.returncode == 0:
                print(f"[UI LOG] Step {idx+1} test result: Success\nOutput:\n{output}")
                self._update_status(f"Step {idx+1} test: Success")
            else:
                print(f"[UI LOG] Step {idx+1} test result: Failed\nError:\n{error}")
                self._update_status(f"Step {idx+1} test failed: {error}")
        except Exception as exc:
            print(f"[UI LOG] Step {idx+1} test failed: {exc}")
            self._update_status(f"Step {idx+1} test failed: {exc}")
        finally:
            try:
                os.remove(tf_path)
            except Exception:
                pass

    def regenerateStepInList_(self, sender):
        idx = sender.tag()
        desc = self._step_fields[idx].stringValue()
        self._step_descriptions[idx] = desc
        print(f"[UI LOG] Regenerate button pressed for step {idx+1} | Description: {desc}")
        code = generate_python_code(desc)
        self._step_codes[idx] = code
        print(f"[UI LOG] Step {idx+1} regenerated code: {code[:80]}{'...' if len(code) > 80 else ''}")
        self._update_status(f"Step {idx+1} regenerated.")

    def validateStepInList_(self, sender):
        idx = sender.tag()
        desc = self._step_fields[idx].stringValue()
        self._step_descriptions[idx] = desc
        print(f"[UI LOG] Validate button pressed for step {idx+1} | Description: {desc}")
        self._step_valid[idx] = True
        print(f"[UI LOG] Step {idx+1} validated.")
        self._update_status(f"Step {idx+1} validated.")

    def testAllSteps_(self, _):
        print("[UI LOG] Test all button pressed")
        for idx, step_field in enumerate(self._step_fields):
            desc = step_field.stringValue()
            self._step_descriptions[idx] = desc
            code = self._step_codes[idx] = generate_python_code(desc)
            try:
                import tempfile, subprocess, sys
                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
                    tf.write(code)
                    tf.flush()
                    tf_path = tf.name
                result = subprocess.run([sys.executable, tf_path], capture_output=True, text=True)
                output = result.stdout.strip()
                error = result.stderr.strip()
                if result.returncode == 0:
                    print(f"[UI LOG] Step {idx+1} test result: Success\nOutput:\n{output}")
                    self._update_status(f"Step {idx+1} test: Success")
                else:
                    print(f"[UI LOG] Step {idx+1} test result: Failed\nError:\n{error}")
                    self._update_status(f"Step {idx+1} test failed: {error}")
            except Exception as exc:
                print(f"[UI LOG] Step {idx+1} test failed: {exc}")
                self._update_status(f"Step {idx+1} test failed: {exc}")
            finally:
                try:
                    os.remove(tf_path)
                except Exception:
                    pass

    def validateAllSteps_(self, _):
        print("[UI LOG] Validate all button pressed")
        # Update all step descriptions from fields
        for idx, step_field in enumerate(self._step_fields):
            desc = step_field.stringValue()
            self._step_descriptions[idx] = desc
        # Update prompt from editable field
        prompt = self._decompose_prompt_field.stringValue()
        if all(self._step_valid):
            full_code = '\n\n'.join(self._step_codes)
            save_flow(prompt, full_code, 1, "success")
            self._update_status("All steps validated and full flow stored as success!")
            self._step_list_win.close()
        else:
            self._update_status("Please validate each step before storing.")

    def closeStepList_(self, _):
        if hasattr(self, '_step_list_win') and self._step_list_win:
            self._step_list_win.close()

    def _show_step_editor(self, idx):
        from AppKit import NSWindow, NSTextView, NSButton, NSMakeRect, NSWindowStyleMaskTitled, NSBackingStoreBuffered
        if hasattr(self, '_step_win') and self._step_win:
            self._step_win.close()
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(150, 150, 700, 400), NSWindowStyleMaskTitled, NSBackingStoreBuffered, False)
        win.setTitle_(f"Step {idx+1} of {len(self._step_descriptions)}: Edit, Test, Validate")
        code_view = NSTextView.alloc().initWithFrame_(NSMakeRect(20, 80, 660, 260))
        code_view.setString_(self._step_codes[idx])
        code_view.setEditable_(True)
        test_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 30, 120, 32))
        test_btn.setTitle_("Test Step")
        test_btn.setTarget_(self)
        test_btn.setAction_("testStep:")
        validate_btn = NSButton.alloc().initWithFrame_(NSMakeRect(160, 30, 120, 32))
        validate_btn.setTitle_("Validate Step")
        validate_btn.setTarget_(self)
        validate_btn.setAction_("validateStep:")
        win.contentView().addSubview_(code_view)
        win.contentView().addSubview_(test_btn)
        win.contentView().addSubview_(validate_btn)
        self._step_win = win
        self._step_code_view = code_view
        win.makeKeyAndOrderFront_(None)

    def testStep_(self, _):
        idx = self._step_idx
        code = self._step_code_view.string()
        self._step_codes[idx] = code
        try:
            ok = run_code(code)
            self._update_status(f"Step {idx+1} test: {'Success' if ok else 'Failed'}")
        except Exception as exc:
            self._update_status(f"Step {idx+1} test failed: {exc}")

    def validateStep_(self, _):
        idx = self._step_idx
        code = self._step_code_view.string()
        self._step_codes[idx] = code
        self._step_valid[idx] = True
        if idx + 1 < len(self._step_descriptions):
            self._step_idx += 1
            self._show_step_editor(self._step_idx)
        else:
            # All steps validated, store the flow
            full_code = '\n\n'.join(self._step_codes)
            save_flow(self.field.stringValue().strip(), full_code, 1, "success")
            self._update_status("All steps validated and full flow stored as success!")
            self._step_win.close()
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
        from embeddings import get_embedding, distances_from_embeddings
        import numpy as np
        successes, _ = load_cache()
        # Fuzzy matching using embedding similarity
        prompt_emb = get_embedding(prompt)
        succ_embs = [rec["embedding"] for rec in successes if rec.get("embedding")]
        if succ_embs:
            dists = distances_from_embeddings(prompt_emb, succ_embs)
            min_idx = int(np.argmin(dists))
            min_dist = dists[min_idx]
            # Threshold for fuzzy match (tune as needed, e.g. 0.15)
            if min_dist < 0.18:
                rec = successes[min_idx]
                # Improved parameterization with debug/status output
                import re
                code = rec["code"]
                def extract_params(text):
                    # Extract quoted substrings (messages)
                    quoted = re.findall(r"'([^']*)'|\"([^\"]*)\"", text)
                    flat = [q for pair in quoted for q in pair if q]
                    # Extract names after 'to' (e.g., to John Doe)
                    names = re.findall(r"to ([A-Za-z0-9_ ]+)", text)
                    # Extract numbers (e.g., +1234567890)
                    numbers = re.findall(r"\+\d{6,15}", text)
                    return flat, names, numbers
                old_msg, old_names, old_numbers = extract_params(rec["prompt"])
                new_msg, new_names, new_numbers = extract_params(prompt)
                debug_lines = []
                debug_lines.append(f"[DEBUG] Fuzzy match: {rec['prompt']} (dist={min_dist:.3f})")
                debug_lines.append(f"[DEBUG] Old msg: {old_msg}, New msg: {new_msg}")
                debug_lines.append(f"[DEBUG] Old names: {old_names}, New names: {new_names}")
                debug_lines.append(f"[DEBUG] Old numbers: {old_numbers}, New numbers: {new_numbers}")
                # Replace all old messages with new messages (if same count)
                if old_msg and new_msg and len(old_msg) == len(new_msg):
                    for o, n in zip(old_msg, new_msg):
                        if o in code:
                            code = code.replace(o, n)
                            debug_lines.append(f"[DEBUG] Replaced message: '{o}' -> '{n}'")
                # Replace all old names with new names (if same count)
                if old_names and new_names and len(old_names) == len(new_names):
                    for o, n in zip(old_names, new_names):
                        if o in code:
                            code = re.sub(re.escape(o), n, code, count=1)
                            debug_lines.append(f"[DEBUG] Replaced name: '{o}' -> '{n}'")
                # Replace all old numbers with new numbers (if same count)
                if old_numbers and new_numbers and len(old_numbers) == len(new_numbers):
                    for o, n in zip(old_numbers, new_numbers):
                        if o in code:
                            code = code.replace(o, n)
                            debug_lines.append(f"[DEBUG] Replaced number: '{o}' -> '{n}'")
                # If no replacements were made, or code is unchanged, fall back to generation
                if code == rec["code"]:
                    debug_lines.append("[DEBUG] No parameterization possible, falling back to code generation.")
                    self._update_status("\n".join(debug_lines))
                else:
                    self._load_cached_script(code, prompt)
                    self._applescript_tag = 'cache'
                    self._update_status("\n".join(debug_lines))
                    try:
                        ok = run_code(code)
                        self.last_success = ok
                        self._update_status("\n".join(debug_lines+["✓ Success (from smart cache, fuzzy match)" if ok else "✗ Failed (from smart cache, fuzzy match)"]))
                    except Exception as exc:
                        self.last_success = False
                        self._update_status("\n".join(debug_lines+[f"✗ Failed (from smart cache, fuzzy match): {exc}"]))
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
