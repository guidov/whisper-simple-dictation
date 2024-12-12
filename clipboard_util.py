import pynput
import time

def type_using_clipboard(text):
    """Type text using keyboard controller."""
    controller = pynput.keyboard.Controller()
    for char in text:
        controller.press(char)
        controller.release(char)
        time.sleep(0.001)

