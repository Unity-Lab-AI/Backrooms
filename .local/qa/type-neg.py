"""Replace the game's focused numeric field with a signed number: python .local/qa/type-neg.py -600
Unity's OWN keyboard: the keys are posted to the RimWorld window, never pressed on the owner's keyboard."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om
try:
    om.key(0x41, ("ctrl",)); om.key(0x2E); om.clear_field(12)
    for c in sys.argv[1]:
        if c == "-": om.key(0xBD)
        elif c == " ": om.key(0x20)
        else: om.key(ord(c.upper()))      # VK codes are the uppercase ASCII values; ord('e') is not a key
except Exception as e:
    sys.exit("REFUSED: %s" % e)
print("typed", sys.argv[1])
