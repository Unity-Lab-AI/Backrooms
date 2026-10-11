"""Send virtual-key presses to the game's focused field (click it first with hands.py).

Unicode key events from `hands.py --type` do not reach RimWorld's numeric fields; virtual keys do.
Unity's OWN keyboard: the keys are posted to the RimWorld window, never pressed on the owner's keyboard.
    python .local/qa/keys.py --clear 10000   # empty the field, type 10000
    python .local/qa/keys.py --esc           # Escape: drops a live architect designator (press_cancel does not)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
args = sys.argv[1:]
try:
    if args and args[0] == "--esc":
        om.key(0x1B); print("escape sent"); sys.exit(0)
    if args and args[0] == "--clear":
        args = args[1:]
        om.key(0x41, ("ctrl",)); om.key(0x2E); om.clear_field(12)
    om.type_keys(" ".join(args))
except SystemExit:
    raise
except Exception as e:
    sys.exit("REFUSED: %s" % e)
print("keys sent")
