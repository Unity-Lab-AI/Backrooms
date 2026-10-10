"""Set a growing zone's crop through the real zone gizmo.   python .local/qa/set-crop.py X Z "Psychoid plant" """
import os as _os, sys as _sys
if _os.environ.get("OWNER_LENT_MOUSE") != "1":   # owner, 2026-10-09: "DONT FIGHT ME" -- real input locked
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")

import importlib.util, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
x, z, crop = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
def raw(r, dy=0): subprocess.run([PY, os.path.join(HERE, "raw-click.py"), str(int((r["x"] + r["width"] / 2) * 2)), str(int((r["y"] + r["height"] / 2 + dy) * 2))], capture_output=True); time.sleep(0.6)
e.call("rimworld/clear_selection"); e.call("rimworld/jump_camera_to_cell", {"x": int(x), "z": int(z)}); time.sleep(0.3)
subprocess.run([PY, os.path.join(HERE, "click-cell.py"), x, z], capture_output=True); time.sleep(0.4)
g = e.find(e.layout(), lambda t: t.startswith("Plant:"))
if not g: sys.exit("no Plant gizmo -- the click did not select the zone")
raw(g["screenRect"], -30)
# the crop picker is a scrolling window whose layout rects don't match its drawn tiles (rows below the fold
# fell through to the map). Type the crop into its search box, then click the one tile left: screenshot px.
import ctypes
u = ctypes.WinDLL("user32")
def k(v): u.keybd_event(v, 0, 0, 0); time.sleep(0.03); u.keybd_event(v, 0, 2, 0); time.sleep(0.03)
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "1515", "558"], capture_output=True); time.sleep(0.3)
for ch in crop.split()[0].upper(): k(ord(ch))
time.sleep(0.5)
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "1236", "670"], capture_output=True); time.sleep(0.6)
print([e.plain(el["label"]).strip() for el in e.layout() if e.plain(el["label"]).startswith("Plant:")])
e.call("rimworld/clear_selection")
