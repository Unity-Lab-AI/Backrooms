"""Pause, rank every unbuilt job in camp, shift-queue Prioritize orders round-robin per awake colonist, unpause.
Owner, 2026-10-09: "pauseing till everything is set and use shift slick to mass complete prioriities"."""
import importlib.util, socket, uuid, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "qb/1", "platform": "windows", "launchId": str(uuid.uuid4())})
def call(n, a=None):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r); return r.get("structuredContent", r)
per = int(sys.argv[1]) if len(sys.argv) > 1 else 10
call("rimworld/pause_game")
cols = call("rimworld/list_colonists").get("colonists", [])
crew = [c["name"] for c in cols if c["mapId"] == "Map_0" and c.get("job") not in ("LayDown",) and not c.get("downed")]
call("rimworld/select_pawn", {"pawnName": crew[0] if crew else "Gee"})
todo = []
for (x, z, w, h) in ((133, 124, 32, 32), (165, 124, 8, 32)):
    for c in call("rimworld/get_cells_info", {"x": x, "z": z, "width": w, "height": h})["cells"]:
        d = (c.get("blueprintBuildDefs") or []) + (c.get("frameBuildDefs") or [])
        if d: todo.append((c["x"], c["z"], d[0]))
def rank(t):
    x, z, d = t
    if "Cooler" in d: return 0
    if 153 <= x <= 160 and 132 <= z <= 139: return 1
    if 140 <= x <= 150 and 130 <= z <= 138: return 2
    if 161 <= x <= 168 and 146 <= z <= 154: return 3
    if 139 <= x <= 145 and 146 <= z <= 152: return 4
    if d in ("Vin_Embrasure", "Door", "Wall"): return 5
    return 6
todo.sort(key=rank); cnt = {p: 0 for p in crew}; skipped = 0
for x, z, d in todo:
    free = [p for p in crew if cnt[p] < per]
    if not free: break
    p = min(free, key=lambda q: cnt[q])
    def menu(pp):
        call("rimworld/select_pawn", {"pawnName": pp}); call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.15)
        call("rimworld/right_click_cell", {"x": x, "z": z, **({"modifiers": "shift"} if cnt.get(pp) else {})})
        return [q.get("label") for q in (call("rimworld/get_context_menu_options").get("options") or [])]
    o = menu(p)
    if any("Not assigned to mining" in (l or "") for l in o) and "Unity" in crew and cnt.get("Unity", 0) < per:
        call("rimworld/close_context_menu"); p = "Unity"; o = menu(p)        # rock in the way: the miner digs it first
    lab = next((l for l in o if l and (l.startswith("Prioritize working on") or l.startswith("Prioritize constructing") or l.startswith("Prioritize mining") or l.startswith("Prioritize finishing"))), None)
    if lab: call("rimworld/execute_context_menu_option", {"label": lab}); cnt[p] += 1
    else: call("rimworld/close_context_menu"); skipped += 1
for p in crew: call("rimworld/set_draft", {"pawnName": p, "drafted": False})
call("rimworld/set_time_speed", {"speed": "Normal"})
print("unbuilt", len(todo), "queued", cnt, "skipped", skipped)
