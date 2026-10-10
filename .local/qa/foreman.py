"""Foreman: the bridge cannot hold shift while choosing a menu option, so orders cannot be stacked (owner,
2026-10-09: "you qarnt shift clicking right, so the last task is all that lands"). Instead, every few seconds,
each colonist who is not on a need (eat, sleep, recreation, tending) and not already building gets the next
ranked job as a Prioritize order -- a queue fed one item at a time. Background; stop it with TaskStop.
Camera-safe: it jumps the camera only when it has to issue an order, then hands it back to the follower."""
import importlib.util, json, os, socket, sys, time, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
def session():
    port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
    b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "foreman/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf
s, buf = session()
def call(n, a=None):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r); return r.get("structuredContent", r)
NEEDS = ("Ingest", "LayDown", "Lovin", "SocialRelax", "Skygaze", "GoSwimming", "Play", "TendPatient", "Rescue", "Wait_Combat",
         "Meditate", "Pray", "VisitSickPawn", "Wear", "Equip", "UseNeurotrainer", "Joy", "Relax", "Watch", "Chess", "Horseshoe")
BUSY = ("FinishFrame", "PlaceNoCostFrame", "HaulToContainer", "Mine", "BuildRoof", "SmoothFloor", "Deconstruct", "Repair", "RR_")
def rank(x, z, d):
    if "Cooler" in d: return 0
    if 153 <= x <= 160 and 132 <= z <= 139: return 1
    if 140 <= x <= 150 and 130 <= z <= 138: return 2
    if 161 <= x <= 168 and 146 <= z <= 154: return 3
    if 139 <= x <= 145 and 146 <= z <= 152: return 4
    if d in ("Vin_Embrasure", "Door", "Wall"): return 5
    return 6
def jobs():
    out = []
    for (x, z, w, h) in ((133, 124, 32, 32), (165, 124, 8, 32)):
        for c in call("rimworld/get_cells_info", {"x": x, "z": z, "width": w, "height": h}).get("cells", []):
            d = (c.get("blueprintBuildDefs") or []) + (c.get("frameBuildDefs") or [])
            if d: out.append((rank(c["x"], c["z"], d[0]), c["x"], c["z"]))
    return sorted(out)
OK = ("Prioritize working on", "Prioritize constructing", "Prioritize finishing", "Prioritize mining")
tried = {}
while True:
    try:
        cols = [c for c in call("rimworld/list_colonists").get("colonists", []) if c.get("mapId") == "Map_0" and not c.get("drafted")]
        idle = [c for c in cols if not any(k in (c.get("job") or "") for k in NEEDS + BUSY)]
        if idle:
            call("rimworld/select_pawn", {"pawnName": idle[0]["name"]})
            todo = jobs()
            for c in idle:
                for _, x, z in todo:
                    if time.time() - tried.get((c["name"], x, z), 0) < 120: continue
                    tried[(c["name"], x, z)] = time.time()
                    call("rimworld/select_pawn", {"pawnName": c["name"]}); call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.15)
                    call("rimworld/right_click_cell", {"x": x, "z": z})
                    o = [q.get("label") for q in (call("rimworld/get_context_menu_options").get("options") or [])]
                    lab = next((l for l in o if l and l.startswith(OK)), None)
                    if lab:
                        call("rimworld/execute_context_menu_option", {"label": lab}); print(c["name"], "->", lab, (x, z), flush=True); break
                    call("rimworld/close_context_menu")
            call("rimworld/clear_selection")
    except Exception as e:
        try: s, buf = session()
        except Exception: pass
    time.sleep(4)
