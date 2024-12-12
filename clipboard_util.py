import os
import subprocess
import sys

gnome_desktops = ['X-Cinnamon', 'XFCE']

def is_gnome(desktop):
    return desktop.endswith("GNOME") or desktop in gnome_desktops

def base_copy_cmd():
    if 'WAYLAND_DISPLAY' in os.environ:
        return ['wl-copy']
    return ['xclip', '-selection', 'clipboard']

def copy_to_clipboard(text_to_copy):
    try:
        process = subprocess.Popen(base_copy_cmd(), stdin=subprocess.PIPE)
        process.communicate(input=text_to_copy.encode("utf-8"))
    except FileNotFoundError as e:
        sys.exit(f"Required command not found: {e}")
    except Exception as e:
        sys.exit(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    snippet = "This is the text I want to copy to the clipboard."
    copy_to_clipboard(snippet)

