"""Read a growing zone's Allow-sowing toggle STATE before touching it.

2026-10-10: the no-sow pass clicked the toggle blind, so a plot already switched off got switched back on by
the next pass. Whatever field carries the state, it is in the gizmo object -- this dumps one selected zone's
gizmos verbatim so the toggle can be driven by reading, never by counting clicks.

    python .local/qa/zone-sow-probe.py            # waits for RimWorld in front
"""
import ctypes, importlib.util, json, os, socket, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); sock = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
b.exchange(sock, buf, "session/hello", {"token": tok, "bridgeVersion": "sowprobe/1", "platform": "windows",
                                        "launchId": str(uuid.uuid4())})
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
GAME = u.FindWindowW(None, "RimWorld by Ludeon Studios")

def call(n, a=None):
    r = b.exchange(sock, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

while not (u.GetForegroundWindow() == GAME and not u.IsIconic(GAME)): time.sleep(1)

plot = json.load(open(os.path.join(HERE, "_plots.json")))[0]      # a camp field: selection works there
zid, x, z = plot["crop"], plot["x"] + 2, plot["z"] + 2
call("rimworld/press_cancel")
call("rimworld/select_pawn", {"pawnName": "Scar"}); call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
call("rimworld/clear_selection"); call("rimworld/click_cell", {"x": x, "z": z}); time.sleep(0.3)
if not call("rimworld/list_selected_gizmos").get("selectedCount"):
    vr = call("rimworld/get_camera_state")["viewRect"]
    w = vr["maxX"] - vr["minX"] + 1; h = vr["maxZ"] - vr["minZ"] + 1
    subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"),
                    str(int((x - vr["minX"] + 0.5) / w * 3840.0)), str(int((vr["maxZ"] - z + 0.5) / h * 2054.0))],
                   capture_output=True, text=True, env=dict(os.environ, OWNER_LENT_MOUSE="1"),
                   creationflags=0x08000000 if os.name == "nt" else 0)
    time.sleep(0.4)

gz = call("rimworld/list_selected_gizmos")
print("zone", zid, "at", (x, z), "selectedCount", gz.get("selectedCount"))
for g in gz.get("gizmos", []):
    if "sow" in (g.get("label") or "").lower() or "sow" in json.dumps(g).lower():
        print(json.dumps(g, indent=1)[:1200])
json.dump(gz, open(os.path.join(HERE, "_sow_probe.json"), "w"), indent=1)
print("gizmo labels:", [g.get("label") for g in gz.get("gizmos", [])])
print("gizmo fields:", sorted({k for g in gz.get("gizmos", []) for k in g}))

def targets():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("screenRect") and o.get("label") is not None: out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout")); return out

g = next((o for o in targets() if (o.get("label") or "").startswith("Plant:") and o["screenRect"]["y"] > 850), None)
print("Plant gizmo:", (g or {}).get("label"))
if g:
    rc = g["screenRect"]
    subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"),
                    str(int((rc["x"] + rc["width"] / 2) * 2)), str(int((rc["y"] + rc["height"] / 2 - 30) * 2))],
                   capture_output=True, text=True, env=dict(os.environ, OWNER_LENT_MOUSE="1"),
                   creationflags=0x08000000 if os.name == "nt" else 0)
    time.sleep(0.6)
    labs = sorted({(o.get("label") or "").strip() for o in targets() if (o.get("label") or "").strip()})
    json.dump(labs, open(os.path.join(HERE, "_plant_options.json"), "w"), indent=0)
    print(len(labs), "labels visible with the menu open:")
    for l in labs[:60]: print("  ", l)
call("rimworld/press_cancel"); call("rimworld/clear_selection")
