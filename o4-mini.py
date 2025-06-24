#!/usr/bin/env python3
"""
mini_focus_openai.py  – UI + GPT-4o-mini code-runner

HOW TO USE
----------
1. pip install --upgrade openai
2. Paste your OpenAI key below (or export OPENAI_API_KEY in your shell).
3. Run:  python3 mini_focus_openai.py
4. Type a natural-language request, press Run – watch GPT-4o-mini
   generate a Python snippet and execute it on your Mac.

⚠️  The generated code runs **un-sandboxed** with the same
    privileges as this script.  Review model output if security matters.
"""

# ⇢ 1)  ▒▒▒  PASTE YOUR KEY BETWEEN THE QUOTES  ▒▒▒
OPENAI_API_KEY = "sk-proj-o"          # ← or leave blank & rely on env var
# ---------------------------------------------------------------------

import os, re, sys, objc, subprocess, tempfile, textwrap
import openai
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect
)
from Foundation import NSObject, NSLog

### ───────────────────────── OpenAI helper ──────────────────────────
MODEL_ID = "gpt-4o-mini"          # cheapest GPT-4-class model (June 2025)

SYSTEM_PROMPT = textwrap.dedent("""
    You are a macOS automation agent.
    Always answer ONLY with an entire runnable Python 3 program that performs
    the user’s request. Wrap your answer in triple back-ticks.
    Do not add explanations or comments outside the code block.
""").strip()

def generate_python_code(user_prompt: str) -> str:
    """
    Ask GPT-4o-mini for a Python script and return the raw code string.
    """
    client = openai.OpenAI(api_key=(OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")))
    if not client.api_key:
        raise RuntimeError("OPENAI_API_KEY missing – paste in file or export env var")

    response = client.chat.completions.create(
        model=MODEL_ID,
        temperature=0.1,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ]
    )
    msg = response.choices[0].message.content
    # Extract first ```python ... ``` block or any ``` ... ``` block
    match = re.search(r"```(?:python)?\s*(.+?)\s*```", msg, re.DOTALL)
    if not match:
        raise ValueError("Model response did not contain a code block:\n" + msg)
    return match.group(1)

def run_generated_code(code_text: str):
    """
    Save `code_text` to a temp .py file and run it with the system Python.
    """
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
        tf.write(code_text)
        tf.flush()
        tf_path = tf.name
    NSLog(f"[GPT-4o] Running generated script: {tf_path}")
    try:
        subprocess.run([sys.executable, tf_path], check=True)
    finally:
        os.remove(tf_path)

### ─────────────────────────── Cocoa UI ─────────────────────────────
class Delegate(NSObject):
    def run_(self, sender):                # noqa: N802
        field = sender.window().contentView().subviews()[0]
        prompt = field.stringValue().strip()
        if not prompt:
            NSLog("[UI] Empty prompt; ignoring.")
            return
        NSLog(f"[UI] Prompt: «{prompt}»")
        try:
            code = generate_python_code(prompt)
            NSLog(f"[GPT-4o] Generated code ↓↓↓\n{code}\n↑↑↑")
            run_generated_code(code)
        except Exception as e:
            NSLog(f"[ERROR] {e!r}")
            # Quick & dirty alert via print; improve as you like
            print("\n[ERROR]", e, file=sys.stderr)

    def cancel_(self, _):                  # noqa: N802
        NSLog("[UI] Cancel – quitting")
        NSApplication.sharedApplication().terminate_(None)

GLOBAL_DELEGATE = Delegate.alloc().init()  # keep alive

def make_window():
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, 500, 130),
        NSWindowStyleMaskTitled,
        NSBackingStoreBuffered,
        False)
    win.center();  win.setTitle_("GPT-4o Mini Runner")

    field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 75, 460, 24))
    field.setPlaceholderString_("Ask GPT-4o-mini to do something…")
    field.setEditable_(True); field.setBezeled_(True)

    run_btn    = NSButton.alloc().initWithFrame_(NSMakeRect(280, 25, 100, 32))
    cancel_btn = NSButton.alloc().initWithFrame_(NSMakeRect(120, 25, 100, 32))
    run_btn.setTitle_("Run"); cancel_btn.setTitle_("Quit")

    run_btn.setTarget_(GLOBAL_DELEGATE);    run_btn.setAction_("run:")
    cancel_btn.setTarget_(GLOBAL_DELEGATE); cancel_btn.setAction_("cancel:")

    for v in (field, run_btn, cancel_btn):
        win.contentView().addSubview_(v)

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    NSLog("[UI] Window ready – caret should blink")
    return win

### ──────────────────────────── main() ──────────────────────────────
if __name__ == "__main__":
    try:
        NSRunningApplication.currentApplication().activateWithOptions_(
            NSApplicationActivateIgnoringOtherApps)
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        make_window()
        app.run()
    except objc.error as e:
        print("\n[CRITICAL] Objective-C exception:", e, file=sys.stderr)
        raise

