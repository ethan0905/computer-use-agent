"""
capture_worker.py – Standalone event capture process for mouse/keyboard events.
Writes events to a JSONL file until interrupted (Ctrl+C or SIGTERM).
"""
import sys, json, datetime, signal
from pynput import mouse, keyboard

# Add AppKit/Quartz for app/window detection
try:
    from AppKit import NSWorkspace
    import Quartz
except ImportError:
    NSWorkspace = None
    Quartz = None

def get_active_app_window():
    app_name = None
    window_title = None
    try:
        if NSWorkspace:
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            app_name = app.localizedName()
        if Quartz:
            windows = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
            pid = app.processIdentifier() if app_name and app else None
            if pid:
                for w in windows:
                    if w.get('kCGWindowOwnerPID') == pid and w.get('kCGWindowName'):
                        window_title = w['kCGWindowName']
                        break
    except Exception:
        pass
    return app_name, window_title

def classify_support(app):
    if not app:
        return "unknown"
    app_l = app.lower()
    if app_l in ["safari", "google chrome", "arc", "firefox", "microsoft edge"]:
        return "internet research"
    elif app_l in ["notes", "notion", "obsidian", "bear"]:
        return "note app"
    else:
        return app_l

if len(sys.argv) < 2:
    print("Usage: python capture_worker.py <output_file.jsonl>")
    sys.exit(1)

output_path = sys.argv[1]
events = []
running = True

def record_event(event):
    # Enrich event with app/window/support at capture time
    app, win = get_active_app_window()
    if app:
        event['app'] = app
    if win:
        event['window'] = win
    event['support'] = classify_support(app)
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')

def on_click(x, y, button, pressed):
    record_event({
        'type': 'mouse_click',
        'x': x,
        'y': y,
        'button': str(button),
        'pressed': pressed,
        'timestamp': datetime.datetime.now().isoformat()
    })

def on_scroll(x, y, dx, dy):
    record_event({
        'type': 'mouse_scroll',
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy,
        'timestamp': datetime.datetime.now().isoformat()
    })

def on_press(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)
    record_event({
        'type': 'key_press',
        'key': k,
        'timestamp': datetime.datetime.now().isoformat()
    })

def on_release(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)
    record_event({
        'type': 'key_release',
        'key': k,
        'timestamp': datetime.datetime.now().isoformat()
    })

def stop_all(signum, frame):
    global running
    running = False
    print("[CaptureWorker] Stopping event capture.")
    sys.exit(0)

signal.signal(signal.SIGINT, stop_all)
signal.signal(signal.SIGTERM, stop_all)

print(f"[CaptureWorker] Writing events to {output_path}")

mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener.start()
keyboard_listener.start()

try:
    while running:
        mouse_listener.join(0.1)
        keyboard_listener.join(0.1)
except KeyboardInterrupt:
    stop_all(None, None)
finally:
    mouse_listener.stop()
    keyboard_listener.stop()
    print("[CaptureWorker] Done.")
