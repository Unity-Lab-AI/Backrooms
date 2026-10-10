"""Replace the focused numeric field with a signed number using real keys: python .local/qa/type-neg.py -600"""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, sys, time
u = ctypes.WinDLL("user32")
def k(v):
    u.keybd_event(v, 0, 0, 0); time.sleep(0.03); u.keybd_event(v, 0, 2, 0); time.sleep(0.05)
u.keybd_event(0x11, 0, 0, 0); time.sleep(0.03); k(0x41); u.keybd_event(0x11, 0, 2, 0); time.sleep(0.05)
k(0x2E); k(0x08)
for c in sys.argv[1]:
    if c == "-": k(0xBD)
    elif c == " ": k(0x20)
    else: k(ord(c.upper()))      # VK codes are the uppercase ASCII values; ord('e') is not a key

print("typed", sys.argv[1])
