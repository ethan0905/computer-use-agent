#!/usr/bin/env python3
"""
mini_focus_openai.py – GPT‑4o‑mini code‑runner with live retrieval‑augmented few‑shot learning.

Revision history
────────────────
• 2025‑06‑24 d  Fail‑cache prevents repeats; GUI runner.
• 2025‑06‑25 e  Switched to retrieval‑augmented few‑shot with embeddings for immediate updates.
"""

from __future__ import annotations

from dotenv import load_dotenv
import os, re, sys, subprocess, tempfile, datetime, pathlib, objc, json
import numpy as np
import openai
from typing import List
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSTextView, NSScrollView, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect,
    NSSegmentedControl,
)
from Foundation import NSObject, NSLog
import importlib
import capture

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing – set env var or .env file")
CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL_ID = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are a macOS automation agent. Always reply ONLY with a complete "
    "runnable Python 3 program, wrapped in a triple-back-tick code block.\n\n"
    "🛡️ SAFETY & STABILITY RULES\n"
    "1. Never Embed API Keys in AppleScript – credentials stay outside scripts.\n"
    "2. Check App Availability before sending commands; launch the app if needed.\n"
    "3. Use try/on error blocks generously to handle failures gracefully.\n"
    "4. Avoid hard-coded delays; poll for the target condition instead.\n"
    "5. Never assume window indexes are stable; reference by name or title.\n\n"
    "🧠 INTELLIGENCE & ADAPTABILITY RULES\n"
    "6. Query current state first, then act (e.g. check a checkbox before toggling).\n"
    "7. Fall back on UI scripting (System Events) for apps without AppleScript APIs.\n"
    "8. Standardize window-focus logic (set frontmost, activate, etc.).\n"
    "9. Always test for permissions and enablement; detect missing Accessibility rights.\n"
)

ROOT_DIR = pathlib.Path(__file__).resolve().parent
STORE_PATH = ROOT_DIR / "experiences.jsonl"

def get_embedding(text: str, engine: str = "text-embedding-ada-002") -> list[float]:
    resp = CLIENT.embeddings.create(model=engine, input=[text])
    return resp.data[0].embedding  # type: ignore

def distances_from_embeddings(target: list[float], others: list[list[float]]) -> list[float]:
    t = np.array(target)
    t_norm = np.linalg.norm(t)
    res = []
    for vec in others:
        v = np.array(vec)
        norm_v = np.linalg.norm(v)
        if t_norm == 0 or norm_v == 0:
            res.append(1.0)
        else:
            cos = float(np.dot(t, v) / (t_norm * norm_v))
            res.append(1.0 - cos)
    return res

(ROOT_DIR / "success").mkdir(exist_ok=True)
(ROOT_DIR / "fail").mkdir(exist_ok=True)

successes: List[dict] = []
failures: List[dict] = []
if STORE_PATH.exists():
    with open(STORE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("reward") == 1:
                successes.append(rec)
            else:
                failures.append(rec)

for rec in successes + failures:
    if "embedding" not in rec:
        rec["embedding"] = get_embedding(rec["prompt"])

def generate_python_code(prompt: str) -> str:
    prompt_emb = get_embedding(prompt)
    succ_embs = [r["embedding"] for r in successes]
    succ_dists = distances_from_embeddings(prompt_emb, succ_embs)
    top_succ = sorted(zip(succ_dists, successes), key=lambda x: x[0])[:3]
    fail_embs = [r["embedding"] for r in failures]
    fail_dists = distances_from_embeddings(prompt_emb, fail_embs)
    top_fail = sorted(zip(fail_dists, failures), key=lambda x: x[0])[:2]

    shots = ""
    for _, ex in top_succ:
        shots += f"### Good Example\nUser: {ex['prompt']}\nAssistant:\n```python\n{ex['code']}```\n\n"
    if top_fail:
        shots += "### Avoid These Patterns\n"
        for _, ex in top_fail:
            shots += f"- {ex['prompt']}\n"
        shots += "\n"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": shots + f"### New Request\n{prompt}"},
    ]
    rsp = CLIENT.chat.completions.create(
        model=MODEL_ID,
        temperature=0.1,
        max_tokens=1024,
        messages=messages,
    )
    msg = rsp.choices[0].message.content
    m = re.search(r"```(?:python)?\s*(.+?)\s*```", msg, re.DOTALL)
    if not m:
        raise ValueError("Model reply lacked a Python code block:\n" + msg)
    return m.group(1)

def run_code(code_text: str) -> bool:
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
        tf.write(code_text)
        tf.flush()
        tf_path = tf.name
    NSLog(f"[Runner] Executing {tf_path}")
    try:
        subprocess.run([sys.executable, tf_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        NSLog(f"[ERROR] Script failed: {e}")
        return False
    finally:
        os.remove(tf_path)

class Delegate(NSObject):
    def regenerateCapturedFlow_(self, _):
        # Regenerate AppleScript for the last captured flow
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
    last_code: str = ""
    last_prompt: str = ""
    last_success: bool = False

    def run_(self, _):
        prompt = self.field.stringValue().strip()
        if not prompt:
            return

        self.last_prompt = prompt
        self._update_status("Working…")
        self._toggle_feedback(False)
        self.code_view.setString_("")

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
        NSApplication.sharedApplication().terminate_(None)

    def toggleCapture_(self, sender):
        # Toggle capture mode on/off
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
        # Save the captured flow with the user-provided prompt
        prompt = self.save_prompt_field.stringValue().strip()
        if not prompt:
            self._update_status("Please enter a prompt to save this flow.")
            return
        code = self.last_code
        if not code:
            self._update_status("No captured code to save.")
            return
        import datetime, re, json, pathlib, os
        ROOT_DIR = pathlib.Path(__file__).resolve().parent
        STORE_PATH = ROOT_DIR / "experiences.jsonl"
        folder = ROOT_DIR / "success"
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:60] or "untitled"
        fp = folder / f"{slug}__{ts}.py"
        header = f"# Prompt: {prompt}\n# Outcome: success\n\n"
        fp.write_text(header + code, encoding="utf-8")
        rec = {"prompt": prompt, "code": code, "reward": 1, "timestamp": datetime.datetime.now().isoformat()}
        try:
            from openai import OpenAI
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            CLIENT = OpenAI(api_key=OPENAI_API_KEY)
            rec["embedding"] = CLIENT.embeddings.create(model="text-embedding-ada-002", input=[prompt]).data[0].embedding
        except Exception:
            rec["embedding"] = []
        with open(STORE_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + "\n")
        self._update_status("Captured flow saved and will be used for smart cache retrieval.")
        self._show_save_prompt_field(False)

    def _show_save_prompt_field(self, show: bool):
        if not hasattr(self, 'save_prompt_field') or not hasattr(self, 'save_prompt_btn'):
            return
        self.save_prompt_field.setHidden_(not show)
        self.save_prompt_btn.setHidden_(not show)
    # Use this when loading AppleScript from smart cache (not a Cocoa action)
    # This method is for internal Python use only and will not be exposed to Objective-C.
    # Do NOT use as a button action or with a trailing underscore.
    # Use this when loading AppleScript from smart cache (not a Cocoa action)
    # This method is for internal Python use only and will not be exposed to Objective-C.
    # Do NOT use as a button action or with a trailing underscore.
    # If you ever see a PyObjC error about this method, check for typos or accidental underscores.
    # Internal Python-only method: not exposed to Objective-C
    def _load_cached_script(self, code, prompt):
        self.last_code = code
        self.last_prompt = prompt
        self.code_view.setString_(code)
        self._applescript_tag = 'cache'
        self._update_status("Loaded AppleScript from smart cache. Click 'Test it' to run.")

    def testScript_(self, _):
        # Save AppleScript to temp file and run it, tagging the source
        import tempfile, subprocess, re
        code = self.code_view.string()
        # Tag: check if code was just generated or from smart cache
        tag = getattr(self, '_applescript_tag', None)
        if tag is None:
            tag = 'generated'  # Default to generated if not set
        if tag == 'cache':
            print("[AppleScript EXECUTION] Source: smart cache")
        else:
            print("[AppleScript EXECUTION] Source: generated")
        print(f"testing initiated [{tag}]")
        # Remove any markdown code block wrappers
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
        # Regenerate AppleScript with a new prompt for robustness
        print("Regenerating AppleScript for robustness...")
        prompt = self.last_prompt or "[Captured Flow]"
        # Add a hint to the prompt to maximize success
        regen_prompt = prompt + "\n# Regenerate for maximum reliability. Use alternative strategies if needed."
        applescript = capture.CAPTURE_SESSION.export_applescript()  # This will use the latest events
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
        folder = ROOT_DIR / ("success" if success else "fail")
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", self.last_prompt.lower()).strip("-")[:60] or "untitled"
        fp = folder / f"{slug}__{ts}.py"
        header = f"# Prompt: {self.last_prompt}\n# Outcome: {'success' if success else 'fail'}\n\n"
        fp.write_text(header + self.last_code, encoding="utf-8")
        NSLog(f"[UI] Saved script to {fp}")

        rec = {"prompt": self.last_prompt, "code": self.last_code, "reward": int(success), "timestamp": datetime.datetime.now().isoformat()}
        rec["embedding"] = get_embedding(rec["prompt"])
        (successes if success else failures).append(rec)
        with open(STORE_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + "\n")

        self._toggle_feedback(False)

global GLOBAL_DELEGATE
GLOBAL_DELEGATE = Delegate.alloc().init()

def make_window():
    # Add regenerate code button for captured flows
    regenerate_captured_btn = NSButton.alloc().initWithFrame_(NSMakeRect(560, 70, 60, 26))
    regenerate_captured_btn.setTitle_("Regenerate")
    regenerate_captured_btn.setTarget_(GLOBAL_DELEGATE)
    regenerate_captured_btn.setAction_("regenerateCapturedFlow:")
    regenerate_captured_btn.setHidden_(True)
    regenerate_btn = NSButton.alloc().initWithFrame_(NSMakeRect(470, 10, 120, 26))
    regenerate_btn.setTitle_("Regenerate")
    regenerate_btn.setTarget_(GLOBAL_DELEGATE)
    regenerate_btn.setAction_("regenerateScript:")
    regenerate_btn.setHidden_(True)
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(0, 0, 640, 440), NSWindowStyleMaskTitled, NSBackingStoreBuffered, False)
    win.center()
    win.setTitle_("GPT-4o Mini Runner")

    field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 390, 600, 26))
    field.setPlaceholderString_("Ask GPT-4o-mini to do something…")

    status_lbl = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 360, 600, 20))
    status_lbl.setEditable_(False)
    status_lbl.setBezeled_(False)
    status_lbl.setDrawsBackground_(False)

    scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 90, 600, 260))
    code_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 260))
    code_view.setEditable_(False)
    scroll.setDocumentView_(code_view)
    scroll.setHasVerticalScroller_(True)

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

    exit_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 40, 100, 32))
    exit_btn.setTitle_("Exit")
    exit_btn.setTarget_(GLOBAL_DELEGATE)
    exit_btn.setAction_("exit:")

    capture_btn = NSButton.alloc().initWithFrame_(NSMakeRect(240, 40, 110, 32))
    capture_btn.setTitle_("Capture")
    capture_btn.setTarget_(GLOBAL_DELEGATE)
    capture_btn.setAction_("toggleCapture:")

    test_btn = NSButton.alloc().initWithFrame_(NSMakeRect(360, 10, 100, 26))
    test_btn.setTitle_("Test it")
    test_btn.setTarget_(GLOBAL_DELEGATE)
    test_btn.setAction_("testScript:")
    test_btn.setHidden_(True)

    # Add input field and button for saving captured flow prompt
    save_prompt_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 70, 400, 26))
    save_prompt_field.setPlaceholderString_("Describe this flow in your own words (for smart cache retrieval)…")
    save_prompt_field.setHidden_(True)
    save_prompt_btn = NSButton.alloc().initWithFrame_(NSMakeRect(430, 70, 120, 26))
    save_prompt_btn.setTitle_("Save Flow Prompt")
    save_prompt_btn.setTarget_(GLOBAL_DELEGATE)
    save_prompt_btn.setAction_("saveCapturedFlow:")
    save_prompt_btn.setHidden_(True)

    for v in (field, status_lbl, scroll, run_btn, up_btn, down_btn, exit_btn, capture_btn, test_btn, regenerate_btn, save_prompt_field, save_prompt_btn, regenerate_captured_btn):
        win.contentView().addSubview_(v)

    GLOBAL_DELEGATE.field = field
    GLOBAL_DELEGATE.status_lbl = status_lbl
    GLOBAL_DELEGATE.code_view = code_view
    GLOBAL_DELEGATE.up_btn = up_btn
    GLOBAL_DELEGATE.down_btn = down_btn
    GLOBAL_DELEGATE.test_btn = test_btn
    GLOBAL_DELEGATE.regenerate_btn = regenerate_btn
    GLOBAL_DELEGATE.save_prompt_field = save_prompt_field
    GLOBAL_DELEGATE.save_prompt_btn = save_prompt_btn
    GLOBAL_DELEGATE.regenerate_captured_btn = regenerate_captured_btn

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    return win

if __name__ == "__main__":
    try:
        NSRunningApplication.currentApplication().activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        make_window()
        app.run()
    except objc.error as e:
        print("\n[CRITICAL] Objective‑C exception:", e, file=sys.stderr)
        raise
