"""Closed-loop manual work priorities (owner, 2026-10-09: "your prioties for work are all fucked come on fix it for
next time u know how to do it fix why u didnt do it and do it"). The first pass clicked blind -- a fixed number of
clicks, never checked -- so a moved mouse or a missed click left wrong numbers. Now: read the cell's number from a
screenshot by colour, click once, read again, until it shows the target. Stops the moment the owner takes the mouse."""
import os, re, subprocess, sys, time
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.expandvars(r"%USERPROFILE%/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots")
SC = 0.5517
COL = {"Firefight": 363, "Patient": 404, "Doctor": 445, "Haul": 608, "Cook": 975, "Hunt": 1016, "Construct": 1057,
       "Grow": 1098, "Mine": 1139, "PlantCut": 1180, "Smith": 1261, "Tailor": 1302, "Craft": 1424}
ROW = {"Gee": 185, "Scar": 218, "Unity": 251}
PLAN = {"Gee": {"Firefight": 1, "Patient": 1, "Cook": 2, "Grow": 2, "Doctor": 1},
        "Scar": {"Firefight": 1, "Patient": 1, "Construct": 1, "Craft": 2, "Smith": 2, "Tailor": 2},
        "Unity": {"Firefight": 1, "Patient": 1, "Hunt": 1, "Mine": 2, "Haul": 2, "Doctor": 2}}
def px(who, c):
    return int(COL[c] / SC), int(1380 + ROW[who] / SC)
def read(who, c):
    out = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", "rimworld/take_screenshot", '{"suppressMessage":true}'], capture_output=True, text=True).stdout
    name = re.search(r"rimbridge_[0-9_]*\.png", out).group(0); time.sleep(0.2)
    im = Image.open(os.path.join(SHOTS, name)).convert("RGB"); x, y = px(who, c)
    pts = [im.getpixel((x + dx, y + dy)) for dx in range(-9, 10, 2) for dy in range(-12, 13, 2)]
    bright = [p for p in pts if sum(p) > 300]
    if not bright: return None
    r = sum(p[0] for p in bright) / len(bright); g = sum(p[1] for p in bright) / len(bright); b = sum(p[2] for p in bright) / len(bright)
    if g > r + 40 and g > b + 40: return 1                 # green
    if r > 200 and g > 170 and b < 120: return 2           # yellow
    if abs(r - g) < 25 and abs(g - b) < 25: return 4       # grey
    return 3                                               # beige
import ctypes
from ctypes import wintypes
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2); G = u.FindWindowW(None, "RimWorld by Ludeon Studios")
def ready():
    """In front, and the owner's mouse still for 3 s."""
    a = wintypes.POINT(); u.GetCursorPos(ctypes.byref(a)); time.sleep(3); b = wintypes.POINT(); u.GetCursorPos(ctypes.byref(b))
    return u.GetForegroundWindow() == G and not u.IsIconic(G) and (a.x, a.y) == (b.x, b.y)
if "--wait" in sys.argv:
    while not ready(): pass
    subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", "rimworld/open_main_tab", '{"mainTabId":"main-tab:Work"}'], capture_output=True)
    time.sleep(0.8)
    try: os.remove(os.path.join(HERE, "_cursor.json"))
    except Exception: pass
log = []
for who, cols in PLAN.items():
    for c, want in cols.items():
        while os.path.exists(os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", ".popup.json")): time.sleep(2)
        for step in range(6):
            now = read(who, c)
            if now == want: break
            x, y = px(who, c)
            r = subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(x), str(y)], capture_output=True, text=True)
            if "click" not in r.stdout: sys.exit("STOPPED: " + (r.stdout + r.stderr).strip())
            time.sleep(0.35)
        log.append("%s %s=%s" % (who, c, read(who, c)))
print("; ".join(log))
