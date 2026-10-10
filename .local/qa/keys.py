"""Send real virtual-key presses to the focused game field (click it first with hands.py).

Unicode key events from `hands.py --type` do not reach RimWorld's numeric fields; virtual keys do.
    python .local/qa/keys.py --clear 10000   # select-all, delete, type 10000
    python .local/qa/keys.py --esc           # Escape: drops a live architect designator (press_cancel does not)
"""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, sys, time
u = ctypes.WinDLL("user32")
def k(v, up_only=False):
    u.keybd_event(v, 0, 0, 0); time.sleep(0.03); u.keybd_event(v, 0, 2, 0); time.sleep(0.06)
args = sys.argv[1:]
if args and args[0] == "--esc":
    k(0x1B); print("escape sent"); sys.exit(0)
if args and args[0] == "--clear":
    args = args[1:]
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.03); k(0x41); u.keybd_event(0x11, 0, 2, 0); time.sleep(0.05)
    k(0x2E); k(0x08)
for c in " ".join(args):
    k(ord(c.upper()) if c.isalnum() else ord(c))
print("keys sent")
