"""Put the eight main-base fields back and switch sowing OFF on every one of them.

Owner, 2026-10-10, verbatim: *"and every fucking field is potatoes and i told you to set all those field to
the NE far from camp to no soe as its to far away and we havent moved in yet"*. Deleting them was the wrong
answer -- the fields are planned ground and they stay drawn; what has to be off is **Allow sowing**, so
nobody walks the map to plant them before the crew moves in. The rects come back from
`_ne_plots_bounds.json`, and the toggle is a real click: a bridge click does not select a zone.

    python .local/qa/ne-nosow.py        # waits for RimWorld in front, then redraws and switches each off
"""
import ctypes, importlib.util, json, os, socket, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); sock = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
b.exchange(sock, buf, "session/hello", {"token": tok, "bridgeVersion": "nenosow/1", "platform": "windows",
                                        "launchId": str(uuid.uuid4())})
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
GAME = u.FindWindowW(None, "RimWorld by Ludeon Studios")
GROW = "architect-designator:zone:highlight-designator-zoneadd-growing"

def call(n, a=None):
    r = b.exchange(sock, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

def front(): return u.GetForegroundWindow() == GAME and not u.IsIconic(GAME)

def targets():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("targetId") and o.get("screenRect"): out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout")); return out

def rclick(px, py):
    subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(int(px)), str(int(py))],
                   capture_output=True, text=True, env=dict(os.environ, OWNER_LENT_MOUSE="1"),
                   creationflags=0x08000000 if os.name == "nt" else 0)
    time.sleep(0.35)

def select(x, z):
    call("rimworld/press_cancel")
    call("rimworld/select_pawn", {"pawnName": "Scar"}); call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    call("rimworld/clear_selection"); call("rimworld/click_cell", {"x": x, "z": z}); time.sleep(0.25)
    if call("rimworld/list_selected_gizmos").get("selectedCount"): return True
    vr = call("rimworld/get_camera_state")["viewRect"]
    w = vr["maxX"] - vr["minX"] + 1; h = vr["maxZ"] - vr["minZ"] + 1
    rclick((x - vr["minX"] + 0.5) / w * 3840.0, (vr["maxZ"] - z + 0.5) / h * 2054.0)
    return bool(call("rimworld/list_selected_gizmos").get("selectedCount"))

bounds = json.load(open(os.path.join(HERE, "_ne_plots_bounds.json")))
# the four plots whose rects were read before deletion, plus the two west columns at the same rows
for zid, r in list(bounds.items()):
    pass
EXTRA = {"Zone_12": {"x0": 204, "x1": 212, "z0": 174, "z1": 183},
         "Zone_13": {"x0": 224, "x1": 234, "z0": 174, "z1": 183}}
for k, v in EXTRA.items(): bounds.setdefault(k, v)

while not front(): time.sleep(1)

made = []
for zid, r in sorted(bounds.items()):
    call("rimworld/clear_selection")
    n = call("rimworld/apply_architect_designator", {"designatorId": GROW, "x": r["x0"], "z": r["z0"],
                                                    "width": r["x1"] - r["x0"] + 1,
                                                    "height": r["z1"] - r["z0"] + 1}).get("acceptedCellCount")
    made.append((zid, r["x0"], r["z0"], n))
    print("redrew", zid, "at", (r["x0"], r["z0"]), "cells", n)
call("rimworld/press_cancel")

off = 0
for zid, x0, z0, n in made:
    if not n: continue
    if not select(x0 + 1, z0 + 1): print(zid, "select failed"); continue
    g = next((o for o in targets() if (o.get("label") or "") == "Allow sowing"
              and o["screenRect"]["y"] > 850), None)
    if not g: print(zid, "no Allow sowing toggle"); continue
    rc = g["screenRect"]
    rclick((rc["x"] + rc["width"] / 2) * 2, (rc["y"] + rc["height"] / 2 - 30) * 2)
    off += 1
    print(zid, "sowing switched off")
call("rimworld/press_cancel"); call("rimworld/clear_selection")
print("redrew %d plots, sowing off on %d" % (len(made), off))
