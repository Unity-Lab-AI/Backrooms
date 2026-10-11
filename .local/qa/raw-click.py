"""Click RimWorld at a pixel of a bridge screenshot (3840 x H_IMG image), scaled to the real client.
python .local/qa/raw-click.py IMG_X IMG_Y [IMG_H] [--real]
Unity's OWN mouse: posted to the game window; the owner's cursor and focus are never touched."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ix, iy = float(args[0]), float(args[1]); ih = float(args[2]) if len(args) > 2 else 2054.0
try:
    cx, cy = om.from_shot(ix, iy, ih)
except Exception as e:
    sys.exit("REFUSED: %s" % e)
try:
    out = om.click(cx, cy, real="--real" in sys.argv)
except Exception as e:
    sys.exit("REFUSED: %s" % e)
if out.startswith("deferred"): sys.exit(out)
print("ok", cx, cy)
