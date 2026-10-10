"""Set a RimWorld numeric text field: python .local/qa/field-set.py X Y VALUE   (frame coords)
Clicks the field, clears it with End + Backspace, types VALUE (a leading '-' uses VK_OEM_MINUS)."""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import ctypes, subprocess, sys, time
x, y, val = sys.argv[1], sys.argv[2], sys.argv[3]
r = subprocess.run([sys.executable, ".local/qa/game-click.py", x, y], capture_output=True, text=True)
if r.returncode: sys.exit(r.stdout + r.stderr)
u = ctypes.WinDLL("user32"); g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if u.GetForegroundWindow() != g: sys.exit("REFUSED: RimWorld not foreground")
def k(v): u.keybd_event(v, 0, 0, 0); time.sleep(0.02); u.keybd_event(v, 0, 2, 0); time.sleep(0.02)
k(0x23)
for _ in range(8): k(0x08)
for ch in val:
    if u.GetForegroundWindow() != g: sys.exit("REFUSED mid-text")
    k(0xBD if ch == "-" else ord(ch))
print("set", x, y, val)
