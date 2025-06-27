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
                        self.events.append(json.loads(line))
            except Exception as e:
                print(f"[Capture] Failed to read events: {e}")
        print(f"[Capture] Stopped. {len(self.events)} events captured.")

    def record_event(self, event: Dict[str, Any]):
        if self.active:
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
        self.record_event({
            'type': 'key_press',
            'key': k,
            'timestamp': datetime.datetime.now().isoformat()
        })

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
        # Use OpenAI 4o-mini to convert captured events to AppleScript
        import openai, os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "-- ERROR: OPENAI_API_KEY not set."
        CLIENT = openai.OpenAI(api_key=api_key)
        prompt = (
            "Convert the following macOS mouse and keyboard event log into a complete, runnable AppleScript that will reproduce the actions. "
            "Use System Events for mouse and keyboard automation. Only output the AppleScript code.\n\n"
            f"EVENT LOG (JSONL):\n" + '\n'.join([json.dumps(e) for e in self.events])
        )
        try:
            rsp = CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=512,
                messages=[
                    {"role": "system", "content": "You are an expert in macOS AppleScript automation."},
                    {"role": "user", "content": prompt}
                ],
            )
            msg = rsp.choices[0].message.content
            # Extract AppleScript code block if present
            import re
            m = re.search(r"```applescript\\s*(.+?)\\s*```", msg, re.DOTALL)
            if m:
                return m.group(1)
            return msg.strip()
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
