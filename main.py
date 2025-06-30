import sys
import objc
from AppKit import NSApplication, NSRunningApplication, NSApplicationActivationPolicyRegular, NSApplicationActivateIgnoringOtherApps
from window import make_window

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
