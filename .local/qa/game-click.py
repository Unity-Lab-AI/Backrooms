"""Click (and optionally type) on RimWorld ONLY. Coordinates in the 1600x900 eyes.py frame.

    python .local/qa/game-click.py X Y [--shift] [--type "text"]

Raises RimWorld, then refuses unless the top-level window under the point IS RimWorld and RimWorld
is foreground -- re-checked before every keystroke. field-type.py once typed into the owner's
Twitch browser because it trusted "whatever is under the point".
"""
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
fx, fy = int(sys.argv[1]), int(sys.argv[2])
shift = "--shift" in sys.argv
right = "--right" in sys.argv
text = sys.argv[sys.argv.index("--type") + 1] if "--type" in sys.argv else None
game = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if not game: sys.exit("RimWorld window not found")
# eyes.py frames are the game's CLIENT area: map through the client origin and size, so a windowed
# game (title bar) clicks where the frame says.
cr = wintypes.RECT(); u.GetClientRect(game, ctypes.byref(cr))
org = wintypes.POINT(0, 0); u.ClientToScreen(game, ctypes.byref(org))
x = org.x + int(fx * cr.right / 1600.0); y = org.y + int(fy * cr.right / 1600.0)   # eyes frame is 1600 wide, same scale both axes
if u.GetForegroundWindow() != game:   # Alt-raise only when needed: Alt drops a focused text field
    u.keybd_event(0x12, 0, 0, 0); u.SetForegroundWindow(game); u.keybd_event(0x12, 0, 2, 0); time.sleep(0.35)
def safe():
    under = u.GetAncestor(u.WindowFromPoint(wintypes.POINT(x, y)), 2)
    return u.GetForegroundWindow() == game and under == game
if not safe():
    under = u.GetAncestor(u.WindowFromPoint(wintypes.POINT(x, y)), 2)
    b = ctypes.create_unicode_buffer(128); u.GetWindowTextW(under, b, 128)
    sys.exit("REFUSED: window under point is '%s' (or RimWorld not foreground)" % b.value)
u.SetCursorPos(x, y); time.sleep(0.15)
if not safe(): sys.exit("REFUSED: focus changed")
if shift: u.keybd_event(0x10, 0, 0, 0); time.sleep(0.04)
(u.mouse_event(8, 0, 0, 0, 0), time.sleep(0.06), u.mouse_event(16, 0, 0, 0, 0)) if right else (u.mouse_event(2, 0, 0, 0, 0), time.sleep(0.06), u.mouse_event(4, 0, 0, 0, 0))
if shift: time.sleep(0.04); u.keybd_event(0x10, 0, 2, 0)
if text:
    time.sleep(0.3)
    for c in text:
        if not safe(): sys.exit("REFUSED mid-text: focus changed")
        vk = u.VkKeyScanW(ord(c)); sh = (vk >> 8) & 1; v = vk & 0xff
        if sh: u.keybd_event(0x10, 0, 0, 0)
        u.keybd_event(v, 0, 0, 0); time.sleep(0.02); u.keybd_event(v, 0, 2, 0)
        if sh: u.keybd_event(0x10, 0, 2, 0)
        time.sleep(0.03)
print("ok", x, y)
