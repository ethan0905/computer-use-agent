#!/usr/bin/env python3
"""
mini_focus_openai.py – GPT‑4o‑mini code‑runner with live feedback

Rev. 2025‑06‑24 — **Smarter cache using GPT‑4o‑mini**
─────────────────────────────────────────────────────
• Exit button (prev. rev.) still quits gracefully.
• **Semantic cache** — Before hitting the API, we now:
  1. Collect up to *MAX_CANDIDATES* scripts in the *success/* folder that look
     vaguely similar to the user’s prompt (quick fuzzy match).
  2. For each candidate, ask GPT‑4o‑mini: *“Does this script fully satisfy the
     new request? Reply YES/NO.”*  – The first YES wins; that script is shown &
     executed instantly, skipping generation.

This makes the runner reuse previous solutions even when the wording is
slightly different (e.g. “Draw Mandelbrot set” vs “Plot a Mandelbrot fractal”).
"""

# ───────────────────────────────── API KEY ────────────────────────────────────
from dotenv import load_dotenv
import os, re, sys, subprocess, tempfile, textwrap, datetime, pathlib, objc, difflib
import openai
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSTextView, NSScrollView, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect,
)
from Foundation import NSObject, NSLog

load_dotenv()  # .env → env vars
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing – set env var or .env file")
print(f"API key loaded: {OPENAI_API_KEY[:6]}…")

# ───────────────────────────── OpenAI helpers ────────────────────────────────
CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL_ID = "gpt-4o-mini"  # cheapest GPT‑4‑class model (June 2025)
EMBED_MODEL = "text-embedding-3-small"

SYSTEM_PROMPT = (
    "You are a macOS automation agent. Always reply ONLY with a complete "
    "runnable Python 3 program, wrapped in a triple‑back‑tick code block."
)

ROOT_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR.joinpath("success").mkdir(exist_ok=True)
ROOT_DIR.joinpath("fail").mkdir(exist_ok=True)

_slug_rx = re.compile(r"[^a-z0-9]+")

def slugify(text: str) -> str:
    slug = _slug_rx.sub("-", text.lower()).strip("-")[:60]
    return slug or "untitled"

# ──────────────────────── Generation & execution ────────────────────────────

def generate_python_code(user_prompt: str) -> str:
    rsp = CLIENT.chat.completions.create(
        model=MODEL_ID,
        temperature=0.1,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = rsp.choices[0].message.content
    m = re.search(r"```(?:python)?\s*(.+?)\s*```", content, re.DOTALL)
    if not m:
        raise ValueError("Model reply lacked a Python code block:\n" + content)
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

# ──────────────────────── Smart‑cache utilities ─────────────────────────────
MAX_CANDIDATES = 15  # upper bound to avoid long loops / cost
FUZZY_THRESHOLD = 0.25  # quick ratio gate before asking the model


def list_candidate_files(prompt: str):
    """Return up to MAX_CANDIDATES likely matching .py files from success/."""
    success_dir = ROOT_DIR / "success"
    files = list(success_dir.glob("*.py"))
    scored = []
    for fp in files:
        try:
            first_line = fp.read_text(encoding="utf-8", errors="ignore").split("\n", 1)[0]
        except Exception:
            continue
        ratio = difflib.SequenceMatcher(None, prompt.lower(), first_line.lower()).ratio()
        if ratio >= FUZZY_THRESHOLD:
            scored.append((ratio, fp))
    scored.sort(reverse=True)  # best first
    return [fp for _, fp in scored[:MAX_CANDIDATES]]


def gpt_confirms_match(prompt: str, code: str) -> bool:
    """Ask GPT‑4o‑mini if *code* satisfies *prompt*. Returns True/False."""
    try:
        rsp = CLIENT.chat.completions.create(
            model=MODEL_ID,
            temperature=0,
            max_tokens=4,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise evaluator. Answer strictly YES or NO."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Does the following Python script fully satisfy *all* parts "
                        "of the user's request?\n\n"
                        f"User request:\n{prompt}\n\nPython script:\n```python\n{code[:2000]}\n```"
                    ),
                },
            ],
        )
        ans = rsp.choices[0].message.content.strip().upper()
        return ans.startswith("YES")
    except Exception as exc:
        NSLog(f"[WARN] match‑check error: {exc}")
        return False


def find_cached_code(prompt: str) -> str | None:
    """Return code text if a cached script satisfies *prompt*, else None."""
    for fp in list_candidate_files(prompt):
        try:
            code = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        if gpt_confirms_match(prompt, code):
            NSLog(f"[Cache] Reusing {fp.name}")
            return code
    return None

# ───────────────────────────── Cocoa UI layer ───────────────────────────────
class Delegate(NSObject):
    last_code: str = ""
    last_prompt: str = ""
    last_success: bool = False

    def run_(self, _):  # noqa: N802
        prompt = self.field.stringValue().strip()
        if not prompt:
            return

        self._update_status("Working…")
        self._toggle_feedback(False)
        self.code_view.setString_("")

        # 1️⃣ Smart cache lookup
        cached = find_cached_code(prompt)
        if cached is not None:
            self.last_code = cached
            self.code_view.setString_(cached)
            ok = run_code(cached)
            self.last_success = ok
            self._update_status("✓ Success (cached)" if ok else "✗ Failed (cached)")
            self._toggle_feedback(True)
            return

        # 2️⃣ Fallback – generate new code
        try:
            code = generate_python_code(prompt)
            self.last_code = code
            self.code_view.setString_(code)
            ok = run_code(code)
            self.last_success = ok
            self._update_status("✓ Success" if ok else "✗ Failed")
        except Exception as exc:
            self.last_success = False
            self._update_status(f"✗ Failed: {exc}")
            NSLog(f"[ERROR] {exc!r}")
        finally:
            self._toggle_feedback(True)

    def thumbUp_(self, _):  # noqa: N802
        self._save_feedback(True)

    def thumbDown_(self, _):  # noqa: N802
        self._save_feedback(False)

    def exit_(self, _):  # noqa: N802
        NSApplication.sharedApplication().terminate_(None)

    # ---------------- helpers ----------------
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
        slug = slugify(self.last_prompt)
        fp = folder / f"{slug}__{ts}.py"
        header = (
            f"# Prompt: {self.last_prompt}\n# Outcome: {'success' if success else 'fail'}\n\n"
        )
        fp.write_text(header + self.last_code, encoding="utf-8")
        NSLog(f"[UI] Saved script to {fp}")
        self._toggle_feedback(False)

# One delegate retained for app lifetime
GLOBAL_DELEGATE = Delegate.alloc().init()


def make_window():
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, 640, 440),
        NSWindowStyleMaskTitled,
        NSBackingStoreBuffered,
        False,
    )
    win.center()
    win.setTitle_("GPT‑4o Mini Runner")

    # Widgets
    field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 390, 600, 26))
    field.setPlaceholderString_("Ask GPT‑4o‑mini to do something…")

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

    for v in (field, status_lbl, scroll, run_btn, up_btn, down_btn, exit_btn):
        win.contentView().addSubview_(v)

    # Delegate wiring
    GLOBAL_DELEGATE.field = field
    GLOBAL_DELEGATE.status_lbl = status_lbl
    GLOBAL_DELEGATE.code_view = code_view
    GLOBAL_DELEGATE.up_btn = up_btn
    GLOBAL_DELEGATE.down_btn = down_btn

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    return win

# ─────────────────────────────────── main() ──────────────────────────────────
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
        print("\n[CRITICAL] Objective‑C exception:", e, file=sys.stderr)
        raise
