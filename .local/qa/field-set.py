"""Set a RimWorld numeric text field: python .local/qa/field-set.py X Y VALUE   (frame coords)
Clicks the field, clears it with End + Backspace, types VALUE (a leading '-' uses VK_OEM_MINUS)."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om   # Unity's own mouse and keyboard: posted to the game window, never the owner's
x, y, val = sys.argv[1], sys.argv[2], sys.argv[3]
r = subprocess.run([sys.executable, ".local/qa/game-click.py", x, y], capture_output=True, text=True)
if r.returncode: sys.exit(r.stdout + r.stderr)
try:
    om.clear_field(8)
    for ch in val: om.key(0xBD if ch == "-" else ord(ch))
except Exception as e:
    sys.exit("REFUSED: %s" % e)
print("set", x, y, val)
