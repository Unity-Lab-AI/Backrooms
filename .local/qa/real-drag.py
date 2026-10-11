"""Middle-button drag (or wheel) on RimWorld with Unity's OWN mouse: posted to the game window.
Screen pixels.  python real-drag.py X0 Y0 X1 Y1 [--wheel N] [--real]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
a = [int(v) for v in sys.argv[1:5]]
real = "--real" in sys.argv
try:
    x0, y0 = om.from_screen(a[0], a[1]); x1, y1 = om.from_screen(a[2], a[3])
except Exception as e:
    sys.exit("REFUSED: %s" % e)
if "--wheel" in sys.argv:
    sys.exit(om.run(om.wheel, x0, y0, int(sys.argv[sys.argv.index("--wheel") + 1]), real=real))
sys.exit(om.run(om.drag, x0, y0, x1, y1, button="middle", steps=25, real=real))
