"""Search the open filter for TERM and click its row's box ONE time (owner: "click the option s one not twice").
    python .local/qa/click-row-once.py TERM [Y]   (Y = screenshot px of the row, default 1185)"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import own_mouse as om   # Unity's own mouse and keyboard: posted to the game window, never the owner's

import ctypes, subprocess, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
term = sys.argv[1]; y = sys.argv[2] if len(sys.argv) > 2 else "1185"
u = ctypes.WinDLL("user32")
def k(v): om.key(v)
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "310", "807"], capture_output=True); time.sleep(0.3); k(0x23)
for _ in range(12): k(0x08)
for ch in term.upper(): k(ord(ch))
time.sleep(0.6)
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "508", y], capture_output=True); time.sleep(0.4)
print("clicked once:", term)
