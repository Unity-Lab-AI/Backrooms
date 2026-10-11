"""Scroll the mouse wheel over a point in RimWorld only: python .local/qa/wheel.py X Y CLICKS [--real] (neg = down)
Same frame mapping as game-click.py; Unity's OWN mouse, posted to the game window."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
fx, fy, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
try:
    cx, cy = om.from_frame(fx, fy)
except Exception as e:
    sys.exit("REFUSED: %s" % e)
sys.exit(om.run(om.wheel, cx, cy, n, real="--real" in sys.argv))
