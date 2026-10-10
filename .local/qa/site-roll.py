"""Roll a random starting site and crop the site-info panel for reading. Usage: site-roll.py N"""
import subprocess, sys, time, glob, os
from PIL import Image
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
outs = []
for i in range(n):
    subprocess.run([sys.executable, ".local/qa/hands.py", "733", "871"], capture_output=True)
    time.sleep(2.5)
    r = subprocess.run([sys.executable, ".local/qa/eyes.py"], capture_output=True, text=True).stdout
    p = [l.split(":", 1)[1].strip().split("  (")[0] for l in r.splitlines() if l.startswith("READ THIS")][0]
    im = Image.open(p).crop((0, 290, 365, 520)); outs.append(im)
w = 365; sheet = Image.new("RGB", (w * len(outs), 230))
for i, im in enumerate(outs): sheet.paste(im, (w * i, 0))
sheet.save(".local/qa/evidence/eyes/site-sheet.png"); print("sheet", len(outs))
