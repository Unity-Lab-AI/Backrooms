"""Room survey for the HVAC plan: every roofed indoor room in the base, its size, its climate units, and
which rooms it shares a straight wall with (where an over-wall vent can go).

    python .local/qa/rooms.py [x0 z0 x1 z1]      writes .local/qa/_rooms.json and prints a table

Owner, 2026-10-09: "you never fucking did the vents ac and heat for all rooms and halls".
Rooms = 4-connected roofed cells that are not wall/door. Climate units: Heater, Cooler(+over-wall),
Vent(+over-wall) found on or in the room's cells or its bounding walls.
"""
import importlib.util, json, os, socket, sys, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
X0, Z0, X1, Z1 = [int(v) for v in sys.argv[1:5]] if len(sys.argv) > 4 else (100, 70, 200, 145)
def unwrap(r):
    for k in ("result", "structuredContent"):
        if isinstance(r, dict) and k in r: r = r[k]
    if isinstance(r, dict) and "content" in r:
        for c in r["content"]:
            if c.get("type") == "text":
                try: return json.loads(c["text"])
                except Exception: pass
    return r
cell = {}
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsRooms/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    for x in range(X0, X1, 20):
        for z in range(Z0, Z1, 15):
            r = unwrap(b.exchange(s, buf, "tools/call", {"name": "rimworld/get_cells_info", "arguments": {"x": x, "z": z, "width": min(20, X1 - x), "height": min(15, Z1 - z)}}))
            for c in (r or {}).get("cells", []):
                sd = c.get("solidThingDefs") or []
                defs = [t.get("defName", "") for t in c.get("things", [])]
                kind = "wall" if any("Wall" in t for t in sd) or any(d in ("Cooler", "Vent") for d in defs) else \
                       "door" if any("Door" in t or "Gate" in t for t in sd) else ("in" if c.get("roofDefName") else "out")
                cell[(c["x"], c["z"])] = (kind, defs)
rooms, rid = [], {}
for p, (k, _) in cell.items():
    if k != "in" or p in rid: continue
    n = len(rooms); stack = [p]; rid[p] = n; cs = []
    while stack:
        q = stack.pop(); cs.append(q)
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nq = (q[0] + d[0], q[1] + d[1])
            if nq in cell and cell[nq][0] == "in" and nq not in rid: rid[nq] = n; stack.append(nq)
    rooms.append(cs)
out = []
for n, cs in enumerate(rooms):
    if len(cs) < 4: continue
    units, nb, outside, outs = [], {}, False, []
    seen_walls = set()
    for (x, z) in cs:
        for t in cell[(x, z)][1]:
            if t in ("Heater", "Cooler", "Vent") or "Cooler_Over" in t or "Vent_Over" in t or t.startswith(("Blueprint_Heater", "Blueprint_Vent", "Blueprint_Cooler")):
                units.append((t, x, z))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            w = (x + dx, z + dz)
            if w not in cell or cell[w][0] not in ("wall",): continue
            for t in cell[w][1]:
                if t in ("Cooler", "Vent") or "Over" in t or t.startswith(("Blueprint_Vent", "Blueprint_Cooler", "Blueprint_Heater")):
                    if w not in seen_walls: units.append((t, w[0], w[1])); seen_walls.add(w)
            far = (x + 2 * dx, z + 2 * dz)
            if far in cell:
                if cell[far][0] == "in" and rid.get(far) != n:
                    nb.setdefault(rid[far], []).append([w[0], w[1], "EW" if dx else "NS"])
                elif cell[far][0] == "out":
                    outside = True; outs.append([w[0], w[1], {(1,0):"E",(-1,0):"W",(0,1):"N",(0,-1):"S"}[(dx,dz)]])
    xs = [c[0] for c in cs]; zs = [c[1] for c in cs]
    out.append({"id": n, "size": len(cs), "box": [min(xs), min(zs), max(xs), max(zs)], "units": units,
                "neighbors": {str(k): v[:3] for k, v in nb.items()}, "outside_wall": outside, "outs": outs})
json.dump(out, open(os.path.join(HERE, "_rooms.json"), "w"), indent=1)
for r in sorted(out, key=lambda r: (r["box"][1], r["box"][0])):
    print("room %3d size %4d box %-20s units %-40s nb %s%s" % (r["id"], r["size"], r["box"], [u[0] for u in r["units"]], sorted(int(k) for k in r["neighbors"]), " OUT" if r["outside_wall"] else ""))
