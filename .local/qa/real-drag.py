"""Real middle-button drag on RimWorld only, while the owner has lent the mouse (OWNER_LENT_MOUSE=1).
Screen pixels; refuses unless RimWorld is foreground.  python real-drag.py X0 Y0 X1 Y1 [--wheel N]"""
import os, sys, time, ctypes
if os.environ.get("OWNER_LENT_MOUSE") != "1": sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if u.GetForegroundWindow() != g: sys.exit("REFUSED: RimWorld is not foreground")
a = [int(v) for v in sys.argv[1:5]]
MD, MU, WH = 0x0020, 0x0040, 0x0800
if "--wheel" in sys.argv:
    n = int(sys.argv[sys.argv.index("--wheel") + 1]); u.SetCursorPos(a[0], a[1]); time.sleep(0.1)
    for i in range(abs(n)):
        if u.GetForegroundWindow() != g: sys.exit("stopped: focus left RimWorld")
        u.mouse_event(WH, 0, 0, 120 if n > 0 else -120, 0); time.sleep(0.15)
    sys.exit(0)
u.SetCursorPos(a[0], a[1]); time.sleep(0.1); u.mouse_event(MD, 0, 0, 0, 0); time.sleep(0.1)
for i in range(1, 26):
    if u.GetForegroundWindow() != g: u.mouse_event(MU, 0, 0, 0, 0); sys.exit("stopped: focus left RimWorld")
    u.SetCursorPos(a[0] + (a[2] - a[0]) * i // 25, a[1] + (a[3] - a[1]) * i // 25); time.sleep(0.03)
u.mouse_event(MU, 0, 0, 0, 0); print("dragged")
