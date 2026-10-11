"""Read the real labels out of a growing zone's Plant: menu, so the crop job stops guessing them.

2026-10-10: the crop job asked for "Plant berry" and the menu answered *no option* -- the labels are the
game's own, with 294 mods in the list, so they are read once from the live menu and written to
`_plant_options.json` for `cursor-jobs.py` to match against.

    python .local/qa/plant-options.py        # waits for RimWorld in front, then reads the menu
"""
import ctypes, importlib.util, json, os, socket, subprocess, sys, time, uuid
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); sock = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
b.exchange(sock, buf, "session/hello", {"token": tok, "bridgeVersion": "plantopts/1", "platform": "windows",
                                        "launchId": str(uuid.uuid4())})
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
GAME = u.FindWindowW(None, "RimWorld by Ludeon Studios")

def call(n, a=None):
    r = b.exchange(sock, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

def front():
    return u.GetForegroundWindow() == GAME and not u.IsIconic(GAME)

def targets():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("targetId") and o.get("screenRect"): out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout")); return out

def click(px, py):
    subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(int(px)), str(int(py))],
                   capture_output=True, text=True,
                   creationflags=0x08000000 if os.name == "nt" else 0)
    time.sleep(0.4)

while not front(): time.sleep(1)

plot = json.load(open(os.path.join(HERE, "_plots.json")))[0]
x, z = plot["x"] + 2, plot["z"] + 2
call("rimworld/press_cancel")
call("rimworld/select_pawn", {"pawnName": "Scar"}); call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
call("rimworld/clear_selection"); call("rimworld/click_cell", {"x": x, "z": z}); time.sleep(0.3)
if not call("rimworld/list_selected_gizmos").get("selectedCount"):
    vr = call("rimworld/get_camera_state")["viewRect"]
    w = vr["maxX"] - vr["minX"] + 1; h = vr["maxZ"] - vr["minZ"] + 1
    click((x - vr["minX"] + 0.5) / w * 3840.0, (vr["maxZ"] - z + 0.5) / h * 2054.0)

gz = [g.get("label") for g in call("rimworld/list_selected_gizmos").get("gizmos", [])]
print("gizmos:", gz)
g = next((o for o in targets() if (o.get("label") or "").startswith("Plant:") and o["screenRect"]["y"] > 850), None)
if not g: sys.exit("no Plant: gizmo -- selection failed")
rc = g["screenRect"]
click((rc["x"] + rc["width"] / 2) * 2, (rc["y"] + rc["height"] / 2 - 30) * 2)
opts = sorted({(o.get("label") or "").strip() for o in targets() if (o.get("label") or "").strip()})
json.dump(opts, open(os.path.join(HERE, "_plant_options.json"), "w"), indent=0)
print(len(opts), "menu labels written")
for o in opts: print(" ", o)
call("rimworld/press_cancel"); call("rimworld/clear_selection")
