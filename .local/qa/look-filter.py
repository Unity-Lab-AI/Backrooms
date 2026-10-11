"""Open a storage's filter and screenshot the Foods / Plant matter / Herbal medicine rows -- LOOK ONLY, no box
clicks (owner, 2026-10-09: "click the option s one not twice"). Writes .local/qa/shots/look.png.
    python .local/qa/look-filter.py X Z"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import own_mouse as om   # Unity's own mouse and keyboard: posted to the game window, never the owner's

import importlib.util, os, subprocess, sys, time, ctypes
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
x, z = int(sys.argv[1]), int(sys.argv[2]); sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
u = ctypes.WinDLL("user32")
def k(v): om.key(v)
from PIL import Image
SH = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots")
e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection"); e.call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.3)
r = e.call("rimworld/click_cell", {"x": x, "z": z}); print("selected", [o.get("label") for o in r.get("selectionAfter", {}).get("selectedObjects", [])])
st = e.find(e.layout(), lambda t: t == "Storage")
if st and not e.find(e.layout(), lambda t: t.startswith("Priority:")): e.call("rimworld/click_ui_target", {"targetId": st["targetId"]}); time.sleep(0.4)
print([e.plain(l["label"]) for l in e.layout() if e.plain(l["label"]).startswith("Priority:")])
parts = []
for term in ("", "PLANT", "HERBAL"):
    subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "310", "807"], capture_output=True); time.sleep(0.3); k(0x23)
    for _ in range(12): k(0x08)
    for ch in term: k(ord(ch))
    time.sleep(0.5); n = "look_" + (term or "top"); e.call("rimworld/take_screenshot", {"fileName": n, "suppressMessage": True})
    parts.append(Image.open(os.path.join(SH, n + ".png")).crop((0, 1000, 700, 1250)))
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "310", "807"], capture_output=True); time.sleep(0.3); k(0x23)
for _ in range(12): k(0x08)
o = Image.new("RGB", (700, 750))
for i, p in enumerate(parts): o.paste(p, (0, 250 * i))
o.save(os.path.join(HERE, "shots", "look.png"))
