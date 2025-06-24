#!/usr/bin/env python3
"""
mini_focus_openai.py  – GPT-4o-mini code-runner with progress + feedback

• Paste your OpenAI key below (or `export OPENAI_API_KEY=` in your shell).
• Type a request, hit **Run** → the app asks the cheap GPT-4o-mini model
  for a Python script, shows the code, executes it, and reports Success/Fail.
• After the run, 👍 / 👎 buttons appear; they archive the script to
  ./success/ or ./fail/ at the repository root.
"""

# ───────────────────────────────── API KEY ────────────────────────────────────
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file into environment variables

api_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
print(f"My API Key is: {api_key[:20]}...")  # Print just to confirm it's loaded

# ──────────────────────────────────────────────────────────────────────────────

import os, re, sys, subprocess, tempfile, textwrap, datetime, pathlib, objc
import openai
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSTextView, NSScrollView, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect
)
from Foundation import NSObject, NSLog

# ───────────────────────────── OpenAI helpers ────────────────────────────────
MODEL_ID = "gpt-4o-mini"      # cheapest GPT-4-class model (June 2025)

SYSTEM_PROMPT = textwrap.dedent("""
    You are a macOS automation agent.
    Always reply ONLY with a complete runnable Python 3 program, wrapped in a
    triple-back-tick code block. Do not add extra commentary outside the block.
""").strip()

def generate_python_code(user_prompt: str) -> str:
    """
    Ask GPT-4o-mini for a Python script and return it as a plain string.
    """
    client = openai.OpenAI(api_key=(OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")))
    if not client.api_key:
        raise RuntimeError("OPENAI_API_KEY missing – paste it at top or set env var")

    rsp = client.chat.completions.create(
        model       = MODEL_ID,
        temperature = 0.1,
        max_tokens  = 1024,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ]
    )
    msg = rsp.choices[0].message.content
    m = re.search(r"```(?:python)?\s*(.+?)\s*```", msg, re.DOTALL)
    if not m:
        raise ValueError("Model reply lacked a Python code block:\n" + msg)
    return m.group(1)

def run_code(code_text: str) -> bool:
    """
    Save `code_text` to a temp .py file and execute it with the current Python.
    Returns True if exit status == 0, else False.
    """
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
        tf.write(code_text)
        tf.flush()
        tf_path = tf.name
    NSLog(f"[GPT-4o] Running generated script {tf_path}")
    try:
        subprocess.run([sys.executable, tf_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        NSLog(f"[ERROR] Script failed: {e}")
        return False
    finally:
        os.remove(tf_path)

# ───────────────────────────── Cocoa UI objects ──────────────────────────────
ROOT_DIR = pathlib.Path(__file__).resolve().parent
(ROOT_DIR / "success").mkdir(exist_ok=True)
(ROOT_DIR / "fail").mkdir(exist_ok=True)

class Delegate(NSObject):
    """Holds callbacks and state for the window."""
    last_code: str = ""
    last_success: bool = False

    # wired to Run button
    def run_(self, sender):                        # noqa: N802
        # widgets referenced directly via attributes set in make_window()
        prompt = self.field.stringValue().strip()
        if not prompt:
            return

        self._set_status("Working…")
        self._toggle_feedback(visible=False)
        self.code_view.setString_("")

        try:
            code = generate_python_code(prompt)
            self.last_code = code
            self.code_view.setString_(code)

            success = run_code(code)
            self.last_success = success
            self._set_status("✓ Success" if success else "✗ Failed")
        except Exception as exc:
            self.last_success = False
            self._set_status(f"✗ Failed: {exc}")
            NSLog(f"[ERROR] {exc!r}")
        finally:
            self._toggle_feedback(visible=True)

    # wired to 👍 button
    def thumbUp_(self, sender):                    # noqa: N802
        self._save_feedback(success=True)

    # wired to 👎 button
    def thumbDown_(self, sender):                  # noqa: N802
        self._save_feedback(success=False)

    # internal helpers
    def _set_status(self, text: str):
        self.status_lbl.setStringValue_(text)

    def _toggle_feedback(self, *, visible: bool):
        self.up_btn.setHidden_(not visible)
        self.down_btn.setHidden_(not visible)

    def _save_feedback(self, *, success: bool):
        if not self.last_code:
            return
        folder = ROOT_DIR / ("success" if success else "fail")
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filepath = folder / f"{ts}.py"
        filepath.write_text(self.last_code, encoding="utf-8")
        NSLog(f"[UI] Saved script to {filepath}")
        self._toggle_feedback(visible=False)

# single delegate retained for app lifetime
GLOBAL_DELEGATE = Delegate.alloc().init()

def make_window():
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, 640, 440),
        NSWindowStyleMaskTitled,
        NSBackingStoreBuffered,
        False)
    win.center()
    win.setTitle_("GPT-4o Mini Runner")

    # input field
    field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 390, 600, 26))
    field.setPlaceholderString_("Ask GPT-4o-mini to do something…")
    field.setEditable_(True)

    # status label (borderless)
    status_lbl = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 360, 600, 20))
    status_lbl.setEditable_(False)
    status_lbl.setBezeled_(False)
    status_lbl.setDrawsBackground_(False)
    status_lbl.setStringValue_("Idle")

    # scrollable text view for code
    scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 90, 600, 260))
    code_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 260))
    code_view.setEditable_(False)
    scroll.setDocumentView_(code_view)
    scroll.setHasVerticalScroller_(True)

    # buttons
    run_btn = NSButton.alloc().initWithFrame_(NSMakeRect(520, 40, 100, 32))
    run_btn.setTitle_("Run")
    run_btn.setTarget_(GLOBAL_DELEGATE)
    run_btn.setAction_("run:")

    up_btn = NSButton.alloc().initWithFrame_(NSMakeRect(360, 40, 60, 32))
    up_btn.setTitle_("👍")
    up_btn.setTarget_(GLOBAL_DELEGATE)
    up_btn.setAction_("thumbUp:")
    up_btn.setHidden_(True)

    down_btn = NSButton.alloc().initWithFrame_(NSMakeRect(430, 40, 60, 32))
    down_btn.setTitle_("👎")
    down_btn.setTarget_(GLOBAL_DELEGATE)
    down_btn.setAction_("thumbDown:")
    down_btn.setHidden_(True)

    # add to window
    for v in (field, status_lbl, scroll, run_btn, up_btn, down_btn):
        win.contentView().addSubview_(v)

    # expose widgets on the delegate for easy access
    GLOBAL_DELEGATE.field      = field
    GLOBAL_DELEGATE.status_lbl = status_lbl
    GLOBAL_DELEGATE.code_view  = code_view
    GLOBAL_DELEGATE.up_btn     = up_btn
    GLOBAL_DELEGATE.down_btn   = down_btn

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    return win

# ──────────────────────────────── main() ─────────────────────────────
if __name__ == "__main__":
    try:
        NSRunningApplication.currentApplication().activateWithOptions_(
            NSApplicationActivateIgnoringOtherApps
        )
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        make_window()
        app.run()
    except objc.error as e:
        print("\n[CRITICAL] Objective-C exception:", e, file=sys.stderr)
        raise

