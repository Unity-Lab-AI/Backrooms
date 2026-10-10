"""Restore RimWorld WITHOUT taking focus, then post an in-window click (vclick) right away -- for while the
game is in exclusive fullscreen and minimizes itself whenever it isn't focused. Never touches the owner's
cursor, keyboard or focus (owner, 2026-10-09: "no i have to be able to work while you play").
    python .local/qa/vclick-up.py IMG_X IMG_Y"""
import ctypes, os, subprocess, sys, time
sys.exit("REFUSED: restoring RimWorld pops it over the owner's screen (owner, 2026-10-09: \"okay so stop tabing my screen\")")
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if u.IsIconic(g):
    u.ShowWindowAsync(g, 4)          # SW_SHOWNOACTIVATE
    for _ in range(20):
        time.sleep(0.1)
        if not u.IsIconic(g): break
    time.sleep(0.4)
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vclick.py"), sys.argv[1], sys.argv[2]])
