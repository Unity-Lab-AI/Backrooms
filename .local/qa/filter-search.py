"""Shelf filter = only what a search matches: Clear all, type TERM in the filter search, Allow all.
    python .local/qa/filter-search.py X Z TERM
The search box is typed with Unity's own keyboard (keys posted to the game window), never the owner's."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import own_mouse as om   # Unity's own mouse and keyboard: posted to the game window, never the owner's

import ctypes, importlib.util, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
x, z, term = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
u = ctypes.WinDLL("user32")
def k(v): om.key(v)
e.call("rimworld/clear_selection"); e.call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); e.call("rimworld/click_cell", {"x": x, "z": z}); time.sleep(0.3)
st = e.find(e.layout(), lambda t: t == "Storage")
if st and not e.find(e.layout(), lambda t: t == "Clear all"): e.call("rimworld/click_ui_target", {"targetId": st["targetId"]}); time.sleep(0.4)
e.call("rimworld/click_ui_target", {"targetId": e.find(e.layout(), lambda t: t == "Clear all")["targetId"]}); time.sleep(0.3)
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "310", "807"], capture_output=True); time.sleep(0.3)
k(0x23)
for _ in range(30): k(0x08)
for ch in term.upper(): k(0x20 if ch == " " else ord(ch))
time.sleep(0.5)
e.call("rimworld/click_ui_target", {"targetId": e.find(e.layout(), lambda t: t == "Allow all")["targetId"]}); time.sleep(0.3)
subprocess.run([PY, os.path.join(HERE, "raw-click.py"), "310", "807"], capture_output=True); time.sleep(0.2)
for _ in range(30): k(0x08)
time.sleep(0.4)
n = "fs_%d" % int(time.time()); e.call("rimworld/take_screenshot", {"fileName": n})
from PIL import Image
Image.open(os.path.join(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots"), n + ".png")).crop((0, 600, 700, 1600)).save(os.path.join(HERE, "shots", "fs.png"))
print("set", x, z, term)
