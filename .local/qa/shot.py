"""Bridge screenshot -> .local/qa/_w.png at 1600 wide (optional crop x0 y0 x1 y1 in render pixels)."""
import os, re, subprocess, sys, time
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.expandvars(r"%USERPROFILE%/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots")
for i in range(4):
    out = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", "rimworld/take_screenshot",
                          '{"suppressMessage":true}'], capture_output=True, text=True).stdout
    m = re.search(r"rimbridge_[0-9_]*\.png", out)
    if m and os.path.exists(os.path.join(D, m.group(0))): break
    time.sleep(1)
else:
    sys.exit("no screenshot")
time.sleep(0.3)
im = Image.open(os.path.join(D, m.group(0)))
if len(sys.argv) == 5:
    im = im.crop(tuple(int(v) for v in sys.argv[1:5]))
im.thumbnail((1600, 1600)); im.save(os.path.join(HERE, "_w.png")); print("ok")
