#!/usr/bin/env python3
"""
mini_focus_openai.py – GPT‑4o‑mini code‑runner with live feedback, smart success cache
                      + fail‑cache negative examples

Revision history
────────────────
• 2025‑06‑24 a  Initial GUI runner.
• 2025‑06‑24 b  Semantic cache + feedback archive bug‑fix.
• 2025‑06‑24 c  FIX: completed GUI button wiring.
• 2025‑06‑25 d  Fail‑cache now actively prevents repeat mistakes:
                – fuzzy retrieval from fail/  
                – top examples passed to GPT as “do‑NOT‑do” context.
"""

# ───────────────────────────── imports & API key ─────────────────────────────
from __future__ import annotations

from dotenv import load_dotenv
import os, re, sys, subprocess, tempfile, textwrap, datetime, pathlib, difflib, objc
import openai
from typing import List
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSTextView, NSScrollView, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect,
)
from Foundation import NSObject, NSLog

# Load environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing – set env var or .env file")
print(f"API key loaded: {OPENAI_API_KEY[:6]}…")

# ───────────────────────────── OpenAI helpers ────────────────────────────────
CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL_ID = "gpt-4o-mini"  # cheapest GPT‑4‑class model (June 2025)

SYSTEM_PROMPT = (
    "You are a macOS automation agent. Always reply ONLY with a complete "
    "runnable Python 3 program, wrapped in a triple-back-tick code block.\n\n"
    "When generating AppleScript you MUST follow these rules:\n"
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
    ""
)

ROOT_DIR = pathlib.Path(__file__).resolve().parent
(ROOT_DIR / "success").mkdir(exist_ok=True)
(ROOT_DIR / "fail").mkdir(exist_ok=True)

_slug_rx = re.compile(r"[^a-z0-9]+")

def slugify(text: str) -> str:
    slug = _slug_rx.sub("-", text.lower()).strip("-")[:60]
    return slug or "untitled"

# ─────────────────────────── generation & execution ─────────────────────────

MAX_CANDIDATES = 15
FUZZY_THRESHOLD = 0.25
MAX_FAIL_EXAMPLES = 3  # how many negative examples to feed back


def generate_python_code(user_prompt: str, bad_snippets: List[str] | None = None) -> str:
    """Generate Python code via GPT‑4o‑mini while telling it what *not* to do."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # Inject negative examples so the model avoids repeating past failures.
    if bad_snippets:
        neg_prompt = (
            "The following Python scripts were previously generated for the *same* "
            "request but FAILED every test (the user thumbs‑down'ed them). "
            "Do NOT reuse their logic, structure, or mistakes. Produce a *different* "
            "implementation that fully satisfies the request.\n\n"
        )
        neg_prompt += "\n\n---\n\n".join(
            f"```python\n{textwrap.dedent(snippet).strip()}\n```" for snippet in bad_snippets
        )
        messages.append({"role": "user", "content": neg_prompt})

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
    """Write *code_text* to a temp file, run it, return True on 0‑exit."""
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

# ───────────────────────────── smart‑cache logic ─────────────────────────────


def _list_candidate_files(folder: pathlib.Path, prompt: str):
    """Return likely matching *.py files from *folder*, ranked by fuzzy ratio."""
    scored = []
    for fp in folder.glob("*.py"):
        try:
            first_line = fp.read_text(encoding="utf-8", errors="ignore").split("\n", 1)[0]
        except Exception:
            continue
        ratio = difflib.SequenceMatcher(None, prompt.lower(), first_line.lower()).ratio()
        if ratio >= FUZZY_THRESHOLD:
            scored.append((ratio, fp))
    scored.sort(reverse=True)
    return [fp for _, fp in scored[:MAX_CANDIDATES]]


def list_success_candidates(prompt: str):
    return _list_candidate_files(ROOT_DIR / "success", prompt)


def list_fail_candidates(prompt: str):
    return _list_candidate_files(ROOT_DIR / "fail", prompt)


def gpt_confirms_match(prompt: str, code: str) -> bool:
    """Ask GPT‑4o‑mini if *code* satisfies *prompt*. Strict YES/NO."""
    try:
        rsp = CLIENT.chat.completions.create(
            model=MODEL_ID,
            temperature=0,
            max_tokens=4,
            messages=[
                {"role": "system", "content": "Answer strictly YES or NO."},
                {
                    "role": "user",
                    "content": (
                        "Does this Python script fully satisfy the request?\n"\
                        f"Request: {prompt}\n\nScript (truncated):```python\n{code[:2000]}\n```"
                    ),
                },
            ],
        )
        return rsp.choices[0].message.content.strip().upper().startswith("YES")
    except Exception as exc:
        NSLog(f"[WARN] match‑check error: {exc}")
        return False


def find_cached_code(prompt: str) -> str | None:
    for fp in list_success_candidates(prompt):
        try:
            code = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        if gpt_confirms_match(prompt, code):
            NSLog(f"[Cache] Reusing {fp.name}")
            return code
    return None


def get_fail_snippets(prompt: str, max_examples: int = MAX_FAIL_EXAMPLES) -> List[str]:
    """Return up to *max_examples* snippets from failed scripts similar to *prompt*."""
    snippets: List[str] = []
    for fp in list_fail_candidates(prompt):
        try:
            code = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        # Only keep the first ~200 lines to save tokens
        snippet = "\n".join(code.split("\n")[:200])
        snippets.append(snippet)
        if len(snippets) >= max_examples:
            break
    return snippets

# ───────────────────────────── Cocoa UI layer ───────────────────────────────

class Delegate(NSObject):
    last_code: str = ""
    last_prompt: str = ""
    last_success: bool = False

    # ---------- button actions ----------
    def run_(self, _):  # noqa: N802
        prompt = self.field.stringValue().strip()
        if not prompt:
            return

        self.last_prompt = prompt  # needed for feedback archiving
        self._update_status("Working…")
        self._toggle_feedback(False)
        self.code_view.setString_("")

        # 1️⃣ try success cache
        cached = find_cached_code(prompt)
        if cached is not None:
            self.last_code = cached
            self.code_view.setString_(cached)
            ok = run_code(cached)
            self.last_success = ok
            self._update_status("✓ Success (cached)" if ok else "✗ Failed (cached)")
            self._toggle_feedback(True)
            return

        # 2️⃣ generate new, with fail‑cache negative examples
        bad_snippets = get_fail_snippets(prompt)
        try:
            code = generate_python_code(prompt, bad_snippets)
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

    # ---------- internal helpers ----------
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

# keep delegate alive
global GLOBAL_DELEGATE
GLOBAL_DELEGATE = Delegate.alloc().init()

# ───────────────────────── window construction ──────────────────────────────

def make_window():
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, 640, 440),
        NSWindowStyleMaskTitled,
        NSBackingStoreBuffered,
        False,
    )
    win.center()
    win.setTitle_("GPT‑4o Mini Runner")

    # widgets --------------------------------------------------------------
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

    # pack into window -----------------------------------------------------
    for v in (field, status_lbl, scroll, run_btn, up_btn, down_btn, exit_btn):
        win.contentView().addSubview_(v)

    # expose widgets to delegate
    GLOBAL_DELEGATE.field = field
    GLOBAL_DELEGATE.status_lbl = status_lbl
    GLOBAL_DELEGATE.code_view = code_view
    GLOBAL_DELEGATE.up_btn = up_btn
    GLOBAL_DELEGATE.down_btn = down_btn

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    return win

# ────────────────────────────────── main() ───────────────────────────────────
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
