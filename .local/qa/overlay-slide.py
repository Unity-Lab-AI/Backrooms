"""Slide the always-on overlay aside (still visible, still on top) so left-edge game UI can be clicked.
    python .local/qa/overlay-slide.py right|home"""
import ctypes, sys
from ctypes import wintypes
u = ctypes.windll.user32; ctypes.windll.shcore.SetProcessDpiAwareness(2)
u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
h = u.FindWindowW(None, "Unity Plays RimWorld")
x = 3840 - 570 if sys.argv[1] == "right" else 10
ok = u.SetWindowPos(h, wintypes.HWND(-1), x, 30, 560, 1300, 0x0040 | 0x0010)
r = wintypes.RECT(); u.GetWindowRect(h, ctypes.byref(r)); print("overlay at", r.left, "ok", ok)
