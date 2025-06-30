from AppKit import (
    NSWindow, NSTextField, NSTextView, NSScrollView, NSButton,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSMakeRect
)
from ui_delegate import Delegate

global GLOBAL_DELEGATE
GLOBAL_DELEGATE = Delegate.alloc().init()

def make_window():
    # Add History button
    history_btn = NSButton.alloc().initWithFrame_(NSMakeRect(140, 40, 90, 32))
    history_btn.setTitle_("History")
    history_btn.setTarget_(GLOBAL_DELEGATE)
    history_btn.setAction_("showHistory:")

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

    save_prompt_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 70, 400, 26))
    save_prompt_field.setPlaceholderString_("Describe this flow in your own words (for smart cache retrieval)…")
    save_prompt_field.setHidden_(True)
    save_prompt_btn = NSButton.alloc().initWithFrame_(NSMakeRect(430, 70, 120, 26))
    save_prompt_btn.setTitle_("Save Flow Prompt")
    save_prompt_btn.setTarget_(GLOBAL_DELEGATE)
    save_prompt_btn.setAction_("saveCapturedFlow:")
    save_prompt_btn.setHidden_(True)

    for v in (field, status_lbl, scroll, run_btn, up_btn, down_btn, exit_btn, capture_btn, history_btn, test_btn, regenerate_btn, save_prompt_field, save_prompt_btn, regenerate_captured_btn):
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
    GLOBAL_DELEGATE.history_btn = history_btn

    win.makeKeyAndOrderFront_(None)
    win.makeFirstResponder_(field)
    return win
