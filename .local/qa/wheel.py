"""Scroll the mouse wheel over a point in RimWorld only: python .local/qa/wheel.py X Y CLICKS (neg = down)
Same frame mapping and refusal rules as game-click.py."""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, sys, time
from ctypes import wintypes
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
u.WindowFromPoint.argtypes = [wintypes.POINT]; u.WindowFromPoint.restype = wintypes.HWND
u.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]; u.GetAncestor.restype = wintypes.HWND
fx, fy, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
game = u.FindWindowW(None, "RimWorld by Ludeon Studios")
cr = wintypes.RECT(); u.GetClientRect(game, ctypes.byref(cr))
org = wintypes.POINT(0, 0); u.ClientToScreen(game, ctypes.byref(org))
x = org.x + int(fx * cr.right / 1600.0); y = org.y + int(fy * cr.right / 1600.0)
if u.GetForegroundWindow() != game or u.GetAncestor(u.WindowFromPoint(wintypes.POINT(x, y)), 2) != game:
    sys.exit("REFUSED: RimWorld not foreground or not under the point")
u.SetCursorPos(x, y)
for _ in range(abs(n)):
    u.mouse_event(0x0800, 0, 0, 120 if n > 0 else -120 & 0xFFFFFFFF, 0)
print("wheel", n)
