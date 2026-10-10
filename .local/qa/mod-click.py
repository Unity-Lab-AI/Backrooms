"""Click a pixel N times holding a modifier: python .local/qa/mod-click.py ctrl|shift x y [n]"""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, subprocess, sys, time
u = ctypes.WinDLL("user32")
vk = {"ctrl": 0x11, "shift": 0x10}[sys.argv[1]]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 1
for _ in range(n):
    u.keybd_event(vk, 0, 0, 0); time.sleep(0.05)
    subprocess.run([sys.executable, ".local/qa/hands.py", sys.argv[2], sys.argv[3]], capture_output=True)
    time.sleep(0.05); u.keybd_event(vk, 0, 2, 0); time.sleep(0.15)
print("clicked", n)
