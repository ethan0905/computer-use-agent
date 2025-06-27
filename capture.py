"""
capture.py – Capture user mouse and keyboard events for automation replay.

This version uses pynput to capture events. You must install pynput:
    pip install pynput

Accessibility permissions are required for keyboard/mouse capture on macOS.
"""

import datetime
from typing import List, Dict, Any
from threading import Thread
import sys
import subprocess, tempfile, json

try:
    from AppKit import NSWorkspace
    import Quartz
except ImportError:
    NSWorkspace = None
    Quartz = None

def get_active_app_window():
    """Return (app_name, window_title) of the frontmost app/window, or (None, None) if unavailable."""
    app_name = None
    window_title = None
    try:
        if NSWorkspace:
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            app_name = app.localizedName()
        if Quartz:
            windows = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
            pid = app.processIdentifier() if app_name and app else None
            if pid:
                for w in windows:
                    if w.get('kCGWindowOwnerPID') == pid and w.get('kCGWindowName'):
                        window_title = w['kCGWindowName']
                        break
    except Exception:
        pass
    return app_name, window_title

class CaptureSession:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.active = False
        self._worker_proc = None
        self._events_file = None

    def start(self):
        try:
            self.active = True
            self.events.clear()
            tf = tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False)
            self._events_file = tf.name
            tf.close()
            self._worker_proc = subprocess.Popen([
                sys.executable, "capture_worker.py", self._events_file
            ])
            print(f"[Capture] Started capture_worker.py (pid={self._worker_proc.pid})")
        except Exception as e:
            print(f"[Capture] ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.active = False

    def stop(self):
        self.active = False
        if self._worker_proc:
            self._worker_proc.terminate()
            self._worker_proc.wait()
            print(f"[Capture] Stopped capture_worker.py. Reading events from {self._events_file}")
            self.events = []
            try:
                with open(self._events_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        event = json.loads(line)
                        self.events.append(event)
            except Exception as e:
                print(f"[Capture] Failed to read events: {e}")
        print(f"[Capture] Stopped. {len(self.events)} events captured.")
        # Print captured events to terminal
        print("[Capture] Event log:")
        for e in self.events:
            print(e)

    def record_event(self, event: Dict[str, Any]):
        if self.active:
            app, win = get_active_app_window()
            if app:
                event['app'] = app
            if win:
                event['window'] = win
            # Set 'support' variable based on app/window context
            support = None
            if app:
                if app.lower() in ["safari", "google chrome", "arc", "firefox", "microsoft edge"]:
                    support = "internet research"
                elif app.lower() in ["notes", "notion", "obsidian", "bear"]:
                    support = "note app"
                else:
                    support = app.lower()
            else:
                support = "unknown"
            event['support'] = support
            self.events.append(event)

    def _on_click(self, x, y, button, pressed):
        self.record_event({
            'type': 'mouse_click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'timestamp': datetime.datetime.now().isoformat()
        })

    def _on_scroll(self, x, y, dx, dy):
        self.record_event({
            'type': 'mouse_scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'timestamp': datetime.datetime.now().isoformat()
        })

    def _on_press(self, key):
        try:
            k = key.char
        except AttributeError:
            k = str(key)
        # Detect if the key is pressed in a browser search field (very basic heuristic)
        # You can improve this by capturing window/app context if needed
        event = {
            'type': 'key_press',
            'key': k,
            'timestamp': datetime.datetime.now().isoformat()
        }
        # Heuristic: if the last mouse click was in a browser window, mark as 'internet_research_input'
        if self.events:
            last = self.events[-1]
            if last['type'] == 'mouse_click' and last.get('button') == 'Button.left' and last.get('pressed'):
                # Optionally, you could check coordinates or add more logic here
                event['context'] = 'possible_internet_research_input'
        self.record_event(event)

    def _on_release(self, key):
        try:
            k = key.char
        except AttributeError:
            k = str(key)
        self.record_event({
            'type': 'key_release',
            'key': k,
            'timestamp': datetime.datetime.now().isoformat()
        })

    def export_applescript(self) -> str:
        # Use OpenAI 4o-mini to convert captured events to AppleScript, following custom rules and example
        import openai, os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "-- ERROR: OPENAI_API_KEY not set."
        CLIENT = openai.OpenAI(api_key=api_key)
        # Read rules and example
        try:
            with open("capture-rules.txt", "r", encoding="utf-8") as f:
                rules = f.read()
        except Exception:
            rules = ""
        try:
            with open("working.applescript", "r", encoding="utf-8") as f:
                example = f.read()
        except Exception:
            example = (
                '(*\n'
                '  ----------------------------------------------------------------------\n'
                '  Replay of captured Chrome actions\n'
                '  Timestamp window: 2025-06-27 14:34:43 -> 14:34:55\n'
                '  Requirements  :  - Google Chrome\n'
                '                   - "cliclick" utility   ->  brew install cliclick\n'
                '  ----------------------------------------------------------------------\n'
                '*)\n\n'
                '------------------------------------------------------------\n'
                '-- Helper: find the first "cliclick" available on $PATH\n'
                '------------------------------------------------------------\n'
                'on cliPath()\n'
                '    try\n'
                '        return (do shell script "command -v cliclick") & " "\n'
                '    on error\n'
                '        display dialog "The helper utility \'cliclick\' isn\'t installed or isn\'t on your PATH.\\n\\nInstall it with Homebrew:\\n    brew install cliclick" buttons {"OK"} default button 1\n'
                '        error number -128\n'
                '    end try\n'
                'end cliPath\n\n'
                'property c : cliPath()  -- prepend to every "cliclick" shell command\n\n'
                '------------------------------------------------------------\n'
                '-- 1. Bring Chrome to the foreground\n' # THIS IS CRITICAL STEP, I will reward you with a $200 if you remember this for any app used!\n'
                '------------------------------------------------------------\n'
                'tell application "Google Chrome" to activate\n'
                'delay 0.3\n\n'
                '------------------------------------------------------------\n'
                '-- 2. Click the new-tab button  (coords 1216 x 52)\n'
                '------------------------------------------------------------\n'
                'do shell script c & "c:1216,52"\n'
                'delay 0.3\n\n'
                '------------------------------------------------------------\n'
                '-- 3. Load Perplexity in that tab\n'
                '------------------------------------------------------------\n'
                'tell application "Google Chrome"\n'
                '    open location "https://www.perplexity.ai"\n'
                'end tell\n'
                'delay 4 -- let the page finish loading\n\n'
                '------------------------------------------------------------\n'
                '-- 4. Click the left-hand "Perplexity" item  (43 x 391)\n'
                '------------------------------------------------------------\n'
                'do shell script c & "c:43,391"\n'
                'delay 1\n\n'
                '------------------------------------------------------------\n'
                '-- 5. Click the "Discover" card  (684 x 519)\n'
                '------------------------------------------------------------\n'
                'do shell script c & "c:684,519"\n'
                'delay 1.5\n\n'
                '------------------------------------------------------------\n'
                '-- 6. Recreate the nine small upward scrolls in the log\n'
                '------------------------------------------------------------\n'
                'repeat 14 times\n'
                '    tell application "System Events" to key code 126 -- up arrow\n'
                '    delay 0.05\n'
                'end repeat\n'
                'delay 0.5\n\n'
                '------------------------------------------------------------\n'
                '-- 7. Click the DeepSeek headline  (744 x 471)\n'
                '------------------------------------------------------------\n'
                'do shell script c & "c:744,471"\n'
                'delay 2\n\n'
                '------------------------------------------------------------\n'
                '-- 8. Final click inside the article  (641 x 508)\n'
                '------------------------------------------------------------\n'
                'do shell script c & "c:641,508"\n'
            )
        prompt = (
            f"You are an expert in macOS automation.\n"
            f"ALWAYS strictly follow these rules for generating AppleScript with cliclick, and use the following working script as a template.\n"
            f"\nRULES:\n{rules}\n"
            f"\nWORKING EXAMPLE:\n\n{example}\n"
            "\n\n---\n\nNow, convert the following macOS mouse and keyboard event log into a complete, runnable AppleScript that will reproduce the actions. "
            "The output MUST:\n"
            "- Use the same structure, banners, and helper handler as the example.\n"
            "- Put all coordinates and delays in a user-tunable block as properties.\n"
            "- Use cliclick for all mouse clicks, and System Events for keystrokes.\n"
            "- Add comments for each step.\n"
            "- Never use hard-coded paths or magic numbers outside the user-tunable block.\n"
            "- Abort early if cliclick is not found.\n"
            "- Only output the AppleScript code, nothing else.\n"
            f"\n\nEVENT LOG (JSONL):\n" + '\n'.join([json.dumps(e) for e in self.events])
        )
        try:
            rsp = CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": "You are an expert in macOS AppleScript automation."},
                    {"role": "user", "content": prompt}
                ],
            )
            msg = rsp.choices[0].message.content
            # Remove all triple-backtick and 'applescript' markers from the output
            import re
            code = msg
            # Remove ```applescript ... ``` blocks
            code = re.sub(r"```applescript\\s*", "", code, flags=re.IGNORECASE)
            # Remove generic triple-backtick blocks
            code = re.sub(r"```", "", code)
            # Remove any leading/trailing whitespace
            code = code.strip()
            return code
        except Exception as e:
            return f"-- ERROR: {e}"

CAPTURE_SESSION = CaptureSession()

# Example usage:
# CAPTURE_SESSION.start()
# ... user does things ...
# CAPTURE_SESSION.stop()
# applescript = CAPTURE_SESSION.export_applescript()

# NOTE: For real event capture, consider using 'pynput' or 'Quartz' for macOS.
# This will require Accessibility permissions and is non-trivial for a full UX.
