"""Every powered building in the base, and whether it has power.

    python .local/qa/power-audit.py [x0 z0 x1 z1]     (default: the walled base, x100-200 z70-145)

Owner, 2026-10-09: "you have shit all over your base that doesnt have power". Reads the map in tiles,
groups the cells of each building, selects one cell of each and reads its inspect line: "Not connected
to power", or "Grid excess: N W (M Wd stored)". Prints the unpowered ones and every distinct grid seen.
"""
import importlib.util, json, os, re, socket, subprocess, sys, time, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
box = [int(v) for v in sys.argv[1:5]] if len(sys.argv) > 4 else [100, 70, 200, 145]
sys.argv = [sys.argv[0], "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
b = e.b
SKIP = re.compile(r"^(Wall|.*Conduit|Door$|Fence|.*Bed$|Bed|DoubleBed|Shelf|Pew|Plant_|Sculpture|Chunk|Corpse|Filth|Blueprint|Frame|"
                  r"EndTable|Dresser|Table|DiningChair|Stool|Armchair|Grave|Sarcoph|Campfire|TorchLamp|Brazier|Altar|Throne|Effigy|"
                  r"Horseshoe|GameOfUr|Chess|PenMarker|Lectern|Steel$|Wood|Silver|Meal|Raw|Hay|Meat|Leather|Cloth|Component|Medicine|"
                  r"Blocks|Minified|Apparel|Gun_|Melee|Smokeleaf|Human|Animal|Pawn|Sandbag|Barricade|Rock|Mineable|SteamGeyser|Hidden)", re.I)
def unwrap(r):
    for k in ("result", "structuredContent"):
        if isinstance(r, dict) and k in r: r = r[k]
    if isinstance(r, dict) and "content" in r:
        for c in r["content"]:
            if c.get("type") == "text":
                try: return json.loads(c["text"])
                except Exception: pass
    return r
cells = {}
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as sk:
    b.exchange(sk, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsPowerAudit/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    for x in range(box[0], box[2], 24):
        for z in range(box[1], box[3], 20):
            r = unwrap(b.exchange(sk, buf, "tools/call", {"name": "rimworld/get_cells_info", "arguments": {"x": x, "z": z, "width": min(24, box[2] - x), "height": min(20, box[3] - z)}}))
            for c in (r or {}).get("cells", []):
                for t in c.get("things", []):
                    d = t.get("defName", "")
                    if d and not SKIP.match(d) and t.get("className", "").startswith(("Verse.Building", "RimWorld.Building")):
                        cells.setdefault(d, set()).add((c["x"], c["z"]))
groups = []
for d, cs in cells.items():
    left = set(cs)
    while left:
        start = left.pop(); g = [start]; stack = [start]
        while stack:
            cx, cz = stack.pop()
            for n in ((cx + 1, cz), (cx - 1, cz), (cx, cz + 1), (cx, cz - 1)):
                if n in left: left.remove(n); g.append(n); stack.append(n)
        groups.append((d, min(g)))
dead, grids, nopower = [], {}, 0
for d, (x, z) in sorted(groups):
    subprocess.run([sys.executable, os.path.join(HERE, "click-cell.py"), str(x), str(z)], capture_output=True)
    lab = next((e.plain(el["label"]) for el in e.layout() if "Power needed" in e.plain(el["label"]) or "Not connected" in e.plain(el["label"])), "")
    if not lab: nopower += 1; continue
    if "Not connected" in lab: dead.append("%s(%d,%d) not connected" % (d, x, z)); continue
    m = re.search(r"Grid excess: (-?\d+) W \((\d+) Wd stored\)", lab)
    if m:
        grids.setdefault((m.group(1), m.group(2)), []).append("%s(%d,%d)" % (d, x, z))
        if int(m.group(2)) == 0 and int(m.group(1)) <= 0: dead.append("%s(%d,%d) dead grid" % (d, x, z))
e.call("rimworld/clear_selection")
print("buildings checked:", len(groups), "| no power line (not electric):", nopower)
print("UNPOWERED:", dead or "-")
for k, v in grids.items(): print("GRID excess %s W, stored %s Wd: %d buildings" % (k[0], k[1], len(v)))
