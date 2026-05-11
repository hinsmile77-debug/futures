"""Live mouse position helper for Windows.

Usage:
    python scripts\show_mouse_position.py

Features:
    - Prints current mouse cursor position in screen coordinates
    - Shows the foreground window title/class
    - Helps capture exact click targets for CYBOS login automation

Stop with Ctrl+C.
"""

import ctypes
import ctypes.wintypes
import time


user32 = ctypes.windll.user32


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
    ]


def get_cursor_pos():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def get_foreground_window_info():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return 0, "", ""

    title_buf = ctypes.create_unicode_buffer(512)
    class_buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, title_buf, len(title_buf))
    user32.GetClassNameW(hwnd, class_buf, len(class_buf))
    return hwnd, title_buf.value, class_buf.value


def main():
    print("Mouse tracker started. Move the cursor to a target and read the coordinates.")
    print("Press Ctrl+C to stop.")
    print("")

    last_line = None
    try:
        while True:
            x, y = get_cursor_pos()
            hwnd, title, cls = get_foreground_window_info()
            line = "x={:<5d} y={:<5d} hwnd={} class={} title={}".format(
                x, y, hwnd, cls or "-", title or "-"
            )
            if line != last_line:
                print("\r" + line + " " * 20, end="", flush=True)
                last_line = line
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
