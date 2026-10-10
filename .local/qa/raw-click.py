"""Click RimWorld at a pixel of a bridge screenshot (3840 x H_IMG image), scaled to the real client.
python .local/qa/raw-click.py IMG_X IMG_Y [IMG_H]   -- same foreground/under-point safety as game-click.py"""
import os as _os, sys as _sys
# LOCKED (owner, 2026-10-09: "HOW MANY TIMES HAVE I SAID DONT FIGHT ME ... U WERE OPENING THE MICROSOFT STORE
# REPEADILEY USING HOTKEYS ... IF I TAKE THE FUCKING MOUSE OR KEEYS I HAVE TO BE ABLE TO TALK TO YOU"):
# real mouse/keyboard input only when the owner has just lent it, signalled by OWNER_LENT_MOUSE=1.
if _os.environ.get("OWNER_LENT_MOUSE") != "1":
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, sys, time
from ctypes import wintypes
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
u.WindowFromPoint.argtypes = [wintypes.POINT]; u.WindowFromPoint.restype = wintypes.HWND
u.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]; u.GetAncestor.restype = wintypes.HWND
ix, iy = float(sys.argv[1]), float(sys.argv[2]); ih = float(sys.argv[3]) if len(sys.argv) > 3 else 2054.0
g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
cr = wintypes.RECT(); u.GetClientRect(g, ctypes.byref(cr)); o = wintypes.POINT(0, 0); u.ClientToScreen(g, ctypes.byref(o))
x = o.x + int(ix * cr.right / 3840.0); y = o.y + int(iy * cr.bottom / ih)
if u.GetForegroundWindow() != g:
    u.keybd_event(0x12, 0, 0, 0); u.SetForegroundWindow(g); u.keybd_event(0x12, 0, 2, 0); time.sleep(0.35)
if not (u.GetForegroundWindow() == g and u.GetAncestor(u.WindowFromPoint(wintypes.POINT(x, y)), 2) == g): sys.exit("REFUSED")
u.SetCursorPos(x, y); time.sleep(0.15); u.mouse_event(2, 0, 0, 0, 0); time.sleep(0.06); u.mouse_event(4, 0, 0, 0, 0)
print("ok", x, y)
