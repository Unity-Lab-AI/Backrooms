"""Real click on RimWorld while the owner's standing loan applies (owner, 2026-10-09: "use cursor if u need it
jusdt dont fight me if i take control"). Takes SCREENSHOT pixels (3840x2054 render); the render sits 53px down in
the 2160 window. Refuses unless RimWorld is foreground; stops if the cursor moved since our last placement.
    python real-click.py X Y [--double] [--right]"""
import ctypes, json, os, sys, time
from ctypes import wintypes
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if u.GetForegroundWindow() != g: sys.exit("REFUSED: RimWorld is not foreground (owner has the screen)")
LAST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cursor.json")
p = wintypes.POINT(); u.GetCursorPos(ctypes.byref(p))
# OWNER_LENT_MOUSE=1 is the owner handing the cursor over for one burst (2026-10-10: "take control of mouse if
# u need" / "you have to use the mouse to change the work priorities come on get it done"). The foreground check
# above still stands -- the screen is never taken, only the cursor, and only while the game is already in front.
if os.environ.get("OWNER_LENT_MOUSE") != "1":
    try:
        last = json.load(open(LAST))
        if time.time() - last["t"] < 20 and abs(last["x"] - p.x) + abs(last["y"] - p.y) > 6:
            sys.exit("STOP: the owner moved the mouse -- they have control")
    except Exception:
        pass
x, y = int(float(sys.argv[1])), int(float(sys.argv[2])) + 53
down, up = (8, 16) if "--right" in sys.argv else (2, 4)
u.SetCursorPos(x, y); time.sleep(0.25)
for i in range(2 if "--double" in sys.argv else 1):
    u.mouse_event(down, 0, 0, 0, 0); time.sleep(0.06); u.mouse_event(up, 0, 0, 0, 0); time.sleep(0.08)
json.dump({"x": x, "y": y, "t": time.time()}, open(LAST, "w"))
print("click", x, y)
