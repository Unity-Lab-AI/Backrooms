"""RimWorld's own mouse: post a left click straight into the RimWorld window as window messages.
The owner's real cursor never moves, no keys are sent, no other app is touched. Owner, 2026-10-09:
"yopu need you own fucking mouse for rimworld you idot dont use mine", then, asked how to proceed with
the new-game pages: "option 3 u do it" (use this in-window clicker).

    python .local/qa/vclick.py IMG_X IMG_Y        # pixel of a bridge screenshot (3840 x 2054)
"""
import ctypes, sys, time
from ctypes import wintypes

u = ctypes.WinDLL("user32")
ctypes.windll.shcore.SetProcessDpiAwareness(2)
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON = 0x0200, 0x0201, 0x0202, 0x0001

ix, iy = float(sys.argv[1]), float(sys.argv[2])
g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if not g:
    sys.exit("no RimWorld window")
cr = wintypes.RECT()
u.GetClientRect(g, ctypes.byref(cr))
# the game renders at its own resolution (the screenshot size); in exclusive fullscreen the window can be
# taller than that (3840x2160 vs a 3840x2054 render) and the game reads message coordinates in render pixels,
# so post the screenshot pixel as-is unless the window really is a different scale
# minimized: the client rect is 0x0, so scaling would post every click to 0,0 -- post the render pixel as-is
# (owner, 2026-10-09: "ur mouse needs to work in background bitch")
if abs(cr.right - 3840) < 2 or cr.right == 0:
    x, y = int(ix), int(iy)
else:
    x = int(ix * cr.right / 3840.0); y = int(iy * cr.bottom / 2054.0)
lp = (y << 16) | (x & 0xFFFF)
u.PostMessageW(g, WM_MOUSEMOVE, 0, lp); time.sleep(0.15)   # let a frame see the cursor arrive
u.PostMessageW(g, WM_MOUSEMOVE, 0, lp); time.sleep(0.10)
u.PostMessageW(g, WM_LBUTTONDOWN, MK_LBUTTON, lp); time.sleep(0.12)
u.PostMessageW(g, WM_LBUTTONUP, 0, lp)
print("vclick", x, y)
