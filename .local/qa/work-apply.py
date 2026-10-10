"""Set the Work grid to the owner's rule, one cell at a time with read-back.
Rule (owner, PLAYBOOK): Firefight..Cook = 1 for everyone; each colonist's specialty = 2; all else 3;
nothing blank unless the pawn is incapable."""
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import subprocess, sys, time, glob, os, importlib.util
spec = importlib.util.spec_from_file_location("wr", ".local/qa/work-read.py"); wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
NAMES = ["Gee","Scar","Unity","Alfonzoid","Rev","Stee","Steeve","Steve","Steve2","Steve3"]
SPEC = {"Gee":[16,18,33], "Scar":[17,22,23,26], "Unity":[19,20,30,31], "Alfonzoid":[18,20,33], "Rev":[16,24,25], "Stee":[17,30,33], "Steeve":[17,26], "Steve":[25,30], "Steve2":[18,30], "Steve3":[16,30]}
ORDER = [4,3,2,1,0]
def shot():
    subprocess.run([sys.executable, ".local/qa/eyes.py"], capture_output=True)
    return wr.read(max(glob.glob(".local/qa/evidence/eyes/RRQA-eyes-*.png"), key=os.path.getmtime))
def click(x, y):
    r = subprocess.run([sys.executable, ".local/qa/game-click.py", str(x), str(y)], capture_output=True, text=True).stdout
    if not r.startswith("ok"): sys.exit("STOP " + r)
def park():
    import ctypes; u = ctypes.windll.user32; ctypes.windll.shcore.SetProcessDpiAwareness(2); u.SetCursorPos(2600, 600)
park(); grid = shot(); changed = 0; incap = 0
ONLY = os.environ.get("WORK_ONLY")
for ri, name in enumerate(NAMES):
    if ONLY and name not in ONLY.split(","): continue
    for ci in range(len(wr.COLS)):
        target = 1 if ci <= 15 else (2 if ci in SPEC[name] else 3)
        v = grid[ri][ci]
        tries = 0
        while v != target and tries < 2:
            n = (ORDER.index(target) - ORDER.index(v)) % 5
            for _ in range(n): click(wr.COLS[ci], wr.ROWS[ri]); time.sleep(0.12)
            park(); time.sleep(0.15); grid = shot(); nv = grid[ri][ci]
            if v == 0 and nv == 0: incap += 1; break   # incapable: stays blank
            v = nv; tries += 1; changed += 1
        if v != target and v != 0: print("MISMATCH", name, ci, v, "want", target)
print("changed", changed, "incapable", incap)
