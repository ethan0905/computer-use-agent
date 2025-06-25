#!/usr/bin/env python3
from __future__ import annotations
from dotenv import load_dotenv
import os, re, sys, subprocess, tempfile, datetime, pathlib, objc, json
import numpy as np, openai
from typing import List
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular, NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSTextView, NSScrollView, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect
)
from Foundation import NSObject, NSLog

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")
CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL_ID = "gpt-4o-mini"
ROOT_DIR = pathlib.Path(__file__).resolve().parent
STORE = ROOT_DIR / "experiences.jsonl"

def get_embed(text: str, engine: str = "text-embedding-ada-002") -> list[float]:
    resp = CLIENT.embeddings.create(model=engine, input=[text])
    return resp.data[0].embedding  # type: ignore

def cosd(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    na, nb = np.linalg.norm(a_arr), np.linalg.norm(b_arr)
    return 1.0 - (0.0 if na == 0 or nb == 0 else float(np.dot(a_arr, b_arr) / (na * nb)))

(ROOT_DIR / "success").mkdir(exist_ok=True)
(ROOT_DIR / "fail").mkdir(exist_ok=True)
succ, fail = [], []
if STORE.exists():
    for line in STORE.read_text().splitlines():
        rec = json.loads(line)
        (succ if rec.get("reward") == 1 else fail).append(rec)
for rec in succ + fail:
    rec.setdefault("embed", get_embed(rec["prompt"]))

def gen_code(prompt: str) -> str:
    emb = get_embed(prompt)
    topk = lambda arr, k: sorted(((cosd(emb, r.get("embed", [])), r) for r in arr), key=lambda x: x[0])[:k]
    goods = topk(succ, 3)
    bads = topk(fail, 2)
    shots = ""
    for _, r in goods:
        shots += f"### Good Example\nUser: {r['prompt']}\nAssistant:\n```python\n{r['code']}```\n\n"
    if bads:
        shots += "### Avoid These Patterns\n"
        for _, r in bads:
            shots += f"- {r['prompt']}\n"
        shots += "\n"
    resp = CLIENT.chat.completions.create(
        model=MODEL_ID,
        temperature=0.1,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "You are a macOS automation agent."},
            {"role": "user", "content": shots + f"### New Request\n{prompt}"}
        ]
    )
    text = resp.choices[0].message.content
    m = re.search(r"```(?:python)?\s*(.+?)\s*```", text, re.DOTALL)
    if not m:
        raise ValueError(text)
    return m.group(1)

def run_code(code: str) -> bool:
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
        tf.write(code)
        tf.flush()
        path = tf.name
    NSLog(f"[Run] {path}")
    try:
        subprocess.run([sys.executable, path], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        os.remove(path)

class Delegate(NSObject):
    tasks: List[str] = []
    idx: int = 0
    mode: str = "normal"
    last_prompt: str = ""
    last_code: str = ""
    last_success: bool = False

    def run_(self, _):
        if self.mode == "teach":
            self._run_subtask()
        else:
            self._run_gen()

    def _run_gen(self):
        prompt = self.field.stringValue().strip()
        if not prompt:
            return
        self.last_prompt = prompt
        self._set_status("Working…")
        self._toggle_buttons(False)
        try:
            code = gen_code(prompt)
            self.last_code = code
            self.code_view.setString_(code)
            ok = run_code(code)
            self.last_success = ok
            self._set_status("✓ Success" if ok else "✗ Failed")
        except Exception as e:
            self.last_success = False
            self._set_status(f"✗ {e}")
        self._toggle_buttons(True)

    def startTeach_(self, _):
        prompt = self.field.stringValue().strip()
        if not prompt:
            return
        self.last_prompt = prompt
        resp = CLIENT.chat.completions.create(
            model=MODEL_ID,
            temperature=0.2,
            max_tokens=256,
            messages=[
                {"role": "system", "content": "You are a task splitter."},
                {"role": "user", "content": f"Split this into ordered subtasks with titles only: {prompt}"}
            ]
        )
        lines = resp.choices[0].message.content.splitlines()
        self.tasks = [l.strip() for l in lines if l.strip()]
        self.idx = 0
        self.mode = "teach"
        self._next_subtask()

    def stopTeach_(self, _):
        self.mode = "normal"
        self.tasks = []
        self.idx = 0
        self._set_status("Stopped")

    def _next_subtask(self):
        if self.idx < len(self.tasks):
            sub = self.tasks[self.idx]
            self.field.setStringValue_(sub)
            self._set_status(f"Subtask {self.idx+1}/{len(self.tasks)}")
            self._toggle_buttons(False)
        else:
            self.mode = "confirm"
            self._set_status("All subtasks done. Confirm save?")
            self._toggle_buttons(True)

    def _run_subtask(self):
        prompt = self.field.stringValue().strip()
        self._set_status("Running…")
        try:
            code = gen_code(prompt)
            self.last_code = code
            self.code_view.setString_(code)
            ok = run_code(code)
            self.last_success = ok
            self._set_status("✓ Success" if ok else "✗ Failed")
        except Exception as e:
            self.last_success = False
            self._set_status(f"✗ {e}")
        self._toggle_buttons(True)

    def thumbUp_(self, _):
        if self.mode == "teach":
            self.idx += 1
            self._next_subtask()
        elif self.mode == "confirm":
            seq = {
                "prompt": self.last_prompt,
                "subtasks": self.tasks,
                "timestamp": datetime.datetime.now().isoformat()
            }
            with open(STORE, 'a') as f:
                f.write(json.dumps(seq) + "\n")
            self.stopTeach_(None)
        else:
            self._save_feedback(True)

    def thumbDown_(self, _):
        if self.mode in ("teach", "confirm"):
            return
        self._save_feedback(False)

    def _save_feedback(self, success: bool):
        folder = ROOT_DIR / ("success" if success else "fail")
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", self.last_prompt.lower()).strip("-")[:60] or "untitled"
        fp = folder / f"{slug}__{ts}.py"
        fp.write_text(self.last_code, encoding="utf-8")
        rec = {
            "prompt": self.last_prompt,
            "code": self.last_code,
            "reward": int(success),
            "timestamp": datetime.datetime.now().isoformat()
        }
        rec["embed"] = get_embed(rec["prompt"])
        (succ if success else fail).append(rec)
        with open(STORE, 'a') as f:
            f.write(json.dumps(rec) + "\n")
        self._toggle_buttons(False)

    def exit_(self, _):
        NSApplication.sharedApplication().terminate_(None)

    def _set_status(self, text: str):
        self.status_lbl.setStringValue_(text)

    def _toggle_buttons(self, visible: bool):
        self.up_btn.setHidden_(not visible)
        self.down_btn.setHidden_(not visible)

class AppDelegate(Delegate):
    pass

def make_window():
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, 640, 480),
        NSWindowStyleMaskTitled,
        NSBackingStoreBuffered,
        False
    )
    win.center()
    win.setTitle_("GPT-4o Mini Runner")

    field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 430, 400, 26))
    status = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 400, 600, 20))
    status.setEditable_(False)
    status.setBezeled_(False)
    status.setDrawsBackground_(False)

    scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 130, 600, 260))
    cv = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 260))
    cv.setEditable_(False)
    scroll.setDocumentView_(cv)
    scroll.setHasVerticalScroller_(True)

    run_btn = NSButton.alloc().initWithFrame_(NSMakeRect(520, 80, 100, 32))
    run_btn.setTitle_("Run")
    run_btn.setTarget_(GLOBAL_DELEGATE)
    run_btn.setAction_("run:")

    teach_btn = NSButton.alloc().initWithFrame_(NSMakeRect(420, 80, 90, 32))
    teach_btn.setTitle_("Teach")
    teach_btn.setTarget_(GLOBAL_DELEGATE)
    teach_btn.setAction_("startTeach:")

    stop_btn = NSButton.alloc().initWithFrame_(NSMakeRect(320, 80, 90, 32))
    stop_btn.setTitle_("Stop")
    stop_btn.setTarget_(GLOBAL_DELEGATE)
    stop_btn.setAction_("stopTeach:")

    up_btn = NSButton.alloc().initWithFrame_(NSMakeRect(360, 40, 60, 32))
    up_btn.setTitle_("👍")
    up_btn.setTarget_(GLOBAL_DELEGATE)
    up_btn.setAction_("thumbUp:")

    down_btn = NSButton.alloc().initWithFrame_(NSMakeRect(430, 40, 60, 32))
    down_btn.setTitle_("👎")
    down_btn.setTarget_(GLOBAL_DELEGATE)
    down_btn.setAction_("thumbDown:")

    exit_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 40, 100, 32))
    exit_btn.setTitle_("Exit")
    exit_btn.setTarget_(GLOBAL_DELEGATE)
    exit_btn.setAction_("exit:")

    for w in (field, status, scroll, run_btn, teach_btn, stop_btn, up_btn, down_btn, exit_btn):
        win.contentView().addSubview_(w)

    GLOBAL_DELEGATE.field = field
    GLOBAL_DELEGATE.status_lbl = status
    GLOBAL_DELEGATE.code_view = cv
    GLOBAL_DELEGATE.up_btn = up_btn
    GLOBAL_DELEGATE.down_btn = down_btn

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    return win

global GLOBAL_DELEGATE
GLOBAL_DELEGATE = AppDelegate.alloc().init()

if __name__ == "__main__":
    NSRunningApplication.currentApplication().activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    make_window()
    app.run()
