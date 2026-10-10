"""Shift+left-click a pixel (eyes.py frame): python .local/qa/shift-click.py x y"""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, subprocess, sys, time
u = ctypes.WinDLL("user32")
u.keybd_event(0x10, 0, 0, 0); time.sleep(0.05)
try:
    subprocess.run([sys.executable, ".local/qa/hands.py", sys.argv[1], sys.argv[2]], capture_output=True)
finally:
    time.sleep(0.05); u.keybd_event(0x10, 0, 2, 0)
print("shift-clicked")
