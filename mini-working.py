#!/usr/bin/env python3
"""
mini_focus_ok.py  –  proven working core UI
"""
import subprocess, objc, sys
from AppKit import (
    NSApplication, NSRunningApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationActivateIgnoringOtherApps,
    NSWindow, NSTextField, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect
)
from Foundation import NSObject

YT_SCRIPT = '''
tell application "Google Chrome"
    activate
    open location "https://www.youtube.com"
end tell'''

class Delegate(NSObject):
    def run_(self, sender):                # noqa: N802
        field = sender.window().contentView().subviews()[0]
        txt = field.stringValue()
        print("[DEBUG] RUN – field text:", txt or "(empty)")
        subprocess.run(["osascript", "-e", YT_SCRIPT])
    def cancel_(self, _):                  # noqa: N802
        print("[DEBUG] CANCEL – quitting")
        NSApplication.sharedApplication().terminate_(None)

GLOBAL_DELEGATE = Delegate.alloc().init()  # keep alive

def make_window():
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, 480, 120),
        NSWindowStyleMaskTitled,
        NSBackingStoreBuffered,
        False)
    win.center();  win.setTitle_("FocusTest")

    field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 70, 440, 24))
    field.setPlaceholderString_("Type here…")
    field.setEditable_(True); field.setBezeled_(True)

    run_btn    = NSButton.alloc().initWithFrame_(NSMakeRect(260, 20, 100, 30))
    cancel_btn = NSButton.alloc().initWithFrame_(NSMakeRect(120, 20, 100, 30))
    run_btn.setTitle_("Run"); cancel_btn.setTitle_("Cancel")

    run_btn.setTarget_(GLOBAL_DELEGATE);    run_btn.setAction_("run:")
    cancel_btn.setTarget_(GLOBAL_DELEGATE); cancel_btn.setAction_("cancel:")

    for v in (field, run_btn, cancel_btn):
        win.contentView().addSubview_(v)

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    print("[DEBUG] Window ready – caret should blink")
    return win

if __name__ == "__main__":
    try:
        NSRunningApplication.currentApplication().activateWithOptions_(
            NSApplicationActivateIgnoringOtherApps)

        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        make_window()
        app.run()

    except objc.error as e:
        print("\n[CRITICAL] Objective-C exception:", e)
        raise

