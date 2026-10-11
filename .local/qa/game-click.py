"""Click (and optionally type) on RimWorld ONLY. Coordinates in the 1600x900 eyes.py frame.

    python .local/qa/game-click.py X Y [--shift] [--right] [--type "text"] [--real]

Unity's OWN mouse and keyboard: every event is posted to the RimWorld window handle at client coordinates,
so nothing can land in another window and the owner's cursor and focus are never touched. field-type.py once
typed into the owner's Twitch browser because it trusted "whatever is under the point"; posted input has no
"under the point". --real falls back to the owner's cursor through own_mouse's settle-and-defer guard.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
fx, fy = int(sys.argv[1]), int(sys.argv[2])
text = sys.argv[sys.argv.index("--type") + 1] if "--type" in sys.argv else None
try:
    # eyes.py frames are the game's CLIENT area, 1600 wide, same scale both axes
    x, y = om.from_frame(fx, fy)
    out = om.click(x, y, button="right" if "--right" in sys.argv else "left",
                   mods=("shift",) if "--shift" in sys.argv else (), real="--real" in sys.argv)
    if out.startswith("deferred"): sys.exit(out)
    if text:
        import time; time.sleep(0.3)
        om.type_keys(text)
except SystemExit:
    raise
except Exception as e:
    sys.exit("REFUSED: %s" % e)
print("ok", x, y)
