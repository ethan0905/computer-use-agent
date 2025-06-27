"""
capture_worker.py – Standalone event capture process for mouse/keyboard events.
Writes events to a JSONL file until interrupted (Ctrl+C or SIGTERM).
"""
import sys, json, datetime, signal
from pynput import mouse, keyboard

if len(sys.argv) < 2:
    print("Usage: python capture_worker.py <output_file.jsonl>")
    sys.exit(1)

output_path = sys.argv[1]
events = []
running = True

def record_event(event):
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
