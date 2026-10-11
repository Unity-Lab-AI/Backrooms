"""Click RimWorld with Unity's OWN mouse: posted to the game window, the owner's cursor never moves.
Takes SCREENSHOT pixels (3840x2054 render); the render sits 53px down in the 2160 window.
    python real-click.py X Y [--double] [--right] [--real]
--real uses the owner's cursor instead, only after their input has settled, and defers the instant they move."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
args = [a for a in sys.argv[1:] if not a.startswith("--")]
try:
    cx, cy = om.from_screen(int(float(args[0])), int(float(args[1])) + 53)
except Exception as e:
    sys.exit("REFUSED: %s" % e)
sys.exit(om.run(om.click, cx, cy, button="right" if "--right" in sys.argv else "left",
                double="--double" in sys.argv, real="--real" in sys.argv))
