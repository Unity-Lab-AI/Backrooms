"""Storage priority chain + filters (Unity's own mouse: posted to the game window, never the owner's cursor).
Selection by real click (click-cell.py); copy/paste by API gizmos; priority dropdown option by real click."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import own_mouse as om   # Unity's own mouse and keyboard: posted to the game window, never the owner's

import ctypes, importlib.util, json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
u = ctypes.WinDLL("user32")
from PIL import Image
def k(v): om.key(v)
def raw(x, y): subprocess.run([PY, os.path.join(HERE, "raw-click.py"), str(int(x)), str(int(y))], capture_output=True); time.sleep(0.35)
def gizmos(): return json.dumps(e.call("rimworld/list_selected_gizmos"))
def gz(label):
    m = re.search(r'"id": "(selection-gizmo:[^"]+)"[^{}]*?"label": "%s"' % re.escape(label), gizmos())
    return bool(m) and bool(e.call("rimworld/execute_gizmo", {"gizmoId": m.group(1)}).get("success"))
def sel(x, z):
    e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection"); e.call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.3)
    for _ in range(4):
        subprocess.run([PY, os.path.join(HERE, "click-cell.py"), str(x), str(z)], capture_output=True); time.sleep(0.3)
        if "Copy settings" in gizmos(): return True
    return False
def storage_tab():
    if not e.find(e.layout(), lambda t: t.startswith("Priority:")):
        st = e.find(e.layout(), lambda t: t == "Storage")
        if st: e.call("rimworld/click_ui_target", {"targetId": st["targetId"]}); time.sleep(0.4)
def priority(level):
    storage_tab(); pr = e.find(e.layout(), lambda t: t.startswith("Priority:"))
    if not pr: return "no button"
    if e.plain(pr["label"]).endswith(level): return level
    e.call("rimworld/click_ui_target", {"targetId": pr["targetId"]}); time.sleep(0.5)
    o = e.find(e.layout(), lambda t: t.strip() == level); r = o["screenRect"]; raw((r["x"] + r["width"] / 2) * 2, (r["y"] + r["height"] / 2) * 2)
    pr = e.find(e.layout(), lambda t: t.startswith("Priority:")); return e.plain(pr["label"]) if pr else "?"
def pix(x, y):
    e.call("rimworld/take_screenshot", {"fileName": "sfx"})
    return Image.open(os.path.join(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots"), "sfx.png")).convert("RGB").getpixel((x, y))
def search(term):
    raw(310, 807); k(0x23)
    for _ in range(30): k(0x08)
    for ch in term.upper(): k(0x20 if ch == " " else ord(ch))
    time.sleep(0.5)
def setrow(label, on):
    storage_tab(); el = e.find(e.layout(), lambda t: t.strip() == label)
    if not el: return label + "?"
    y = int((el["screenRect"]["y"] + el["screenRect"]["height"] / 2) * 2)
    for _ in range(3):
        p = pix(508, y); is_on = p[1] > p[0] + 60
        if is_on == on: return "%s=%s" % (label, on)
        raw(508, y)
    return label + " FAILED"
def paste_to(cells):
    n = 0
    for x, z in cells:
        if sel(x, z) and gz("Paste settings"): n += 1
    return n
