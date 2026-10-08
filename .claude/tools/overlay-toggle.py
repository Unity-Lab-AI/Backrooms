"""Hide or show the Unity Plays RimWorld overlay: python .claude/tools/overlay-toggle.py hide|show

Used while working in RimWorld's left-side panels (inspect tabs, bills, prisoner tab), which the
top-left overlay covers. 'show' re-pins it topmost and raises RimWorld under it.
"""
import ctypes, sys, time
from ctypes import wintypes
u = ctypes.WinDLL("user32")
u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]


def find(title):
    r = []
    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        n = u.GetWindowTextLengthW(h)
        if n:
            b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1)
            if b.value == title: r.append(h)
        return True
    u.EnumWindows(cb, 0)
    return r[0] if r else None


o = find("Unity Plays RimWorld")
g = find("RimWorld by Ludeon Studios")
if o:
    if sys.argv[1:] == ["hide"]:
        u.ShowWindow(o, 0)
    else:
        u.ShowWindow(o, 4)
        u.SetWindowPos(o, wintypes.HWND(-1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
if g:
    u.ShowWindow(g, 9); u.SetForegroundWindow(g)
