from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/event0')  # Replace with the correct input device

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        if key_event.keystate == key_event.key_down:
            print(f"Key {key_event.keycode} pressed")


