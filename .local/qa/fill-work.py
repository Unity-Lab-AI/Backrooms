"""Owner: "no prioties should be left blank". Read the Work tab grid once, click every blank cell
twice (blank -> 4 -> 3), then re-read. Cells still blank afterwards are incapable (cannot be set).
Work tab must be open; RimWorld foreground."""
import subprocess, sys, time, glob, os
from PIL import Image
COLS = [273,305,336,367,398,429,459,490,521,552,583,614,644,675,706,737,768,798,829,860,890,921,952,983,1014,1045,1076,1106,1137,1168,1199,1230,1261,1292,1323]
ROWS = [639,664,689,714,739,764]
def shot():
    subprocess.run([sys.executable, ".local/qa/eyes.py"], capture_output=True)
    return Image.open(max(glob.glob(".local/qa/evidence/eyes/RRQA-eyes-*.png"), key=os.path.getmtime)).convert("L")
def blank(im, x, y):
    c = im.crop((x-7, y-8, x+7, y+8))
    return sum(1 for p in c.getdata() if p > 150) < 6
im = shot()
todo = [(x, y) for y in ROWS for x in COLS if blank(im, x, y)]
print("blank cells", len(todo))
for x, y in todo:
    for _ in range(2):
        r = subprocess.run([sys.executable, ".local/qa/game-click.py", str(x), str(y)], capture_output=True, text=True).stdout
        if not r.startswith("ok"): sys.exit("STOP " + r)
        time.sleep(0.15)
im = shot()
left = [(x, y) for y in ROWS for x in COLS if blank(im, x, y)]
print("still blank (incapable)", len(left))
