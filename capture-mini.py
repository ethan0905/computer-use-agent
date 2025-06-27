from pynput import mouse, keyboard

def on_click(x, y, button, pressed):
    print('Mouse click:', x, y, button, pressed)

def on_press(key):
    print('Key press:', key)

mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()
mouse_listener.join()
keyboard_listener.join()
