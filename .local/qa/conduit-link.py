"""Find conduit networks with no power source and lay the shortest hidden-conduit path from each one to a
powered network. Owner, 2026-10-09: "you still have holes in you embrasures and wires that arent connected
just not connected string of conduit".

    python .local/qa/conduit-link.py [--dry]
"""
import importlib.util, json, os, socket, subprocess, sys, uuid
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(sp); sp.loader.exec_module(b)
def unwrap(r):
    for k in ("result", "structuredContent"):
        if isinstance(r, dict) and k in r: r = r[k]
    if isinstance(r, dict) and "content" in r:
        for c in r["content"]:
            if c.get("type") == "text": return json.loads(c["text"])
    return r
cells = {}
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "Link/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    for x in range(90, 210, 25):
        for z in range(50, 150, 20):
            r = unwrap(b.exchange(s, buf, "tools/call", {"name": "rimworld/get_cells_info", "arguments": {"x": x, "z": z, "width": 25, "height": 20}}))
            for c in r.get("cells", []): cells[(c["x"], c["z"])] = c
defs = lambda p: [t.get("defName", "") for t in cells[p].get("things", [])]
BAT = ("Battery", "SmallEfficient", "SmallHyper", "SmallUltra")
TR = lambda d: d in ("PowerConduit", "HiddenConduit", "WaterproofConduit", "Blueprint_HiddenConduit", "Blueprint_PowerConduit") or d.startswith(BAT)
SRC = lambda d: "Generator" in d or d.startswith(BAT)
cond = {p for p in cells if any(TR(d) for d in defs(p))}
src = {p for p in cells if any(SRC(d) for d in defs(p))}
seen, comps = set(), []
for p in cond:
    if p in seen: continue
    st, comp = [p], {p}; seen.add(p)
    while st:
        q = st.pop()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (q[0] + dx, q[1] + dz)
            if n in cond and n not in seen: seen.add(n); comp.add(n); st.append(n)
    comps.append(comp)
powered = set()
for comp in comps:
    if any(abs(p[0] - q[0]) <= 6 and abs(p[1] - q[1]) <= 6 for p in comp for q in src): powered |= comp
# cells a hidden conduit cannot go on: water and anything impassable that is not a wall/embrasure/door
def ok(p):
    c = cells.get(p)
    if not c: return False
    if "Water" in (c.get("terrainDefName") or ""): return False
    sd = c.get("solidThingDefs") or []
    return all(("Wall" in d or "Embrasure" in d or "Door" in d or "Cooler" in d or "Vent" in d) for d in sd)
lay = []
for comp in comps:
    if comp & powered or len(comp) < 1: continue
    prev = {p: None for p in comp}; dq = deque(comp); hit = None
    while dq:
        q = dq.popleft()
        if q in powered: hit = q; break
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (q[0] + dx, q[1] + dz)
            if n not in prev and (n in powered or ok(n)) and abs(n[0] - q[0]) + abs(n[1] - q[1]) == 1:
                prev[n] = q; dq.append(n)
                if len(prev) > 6000: dq.clear()
    if not hit: print("no path for", sorted(comp)[:3]); continue
    path, q = [], prev[hit]
    while q is not None and q not in comp: path.append(q); q = prev[q]
    lay += path; powered |= comp | set(path)
    print("link %s -> %s via %d cells" % (sorted(comp)[0], hit, len(path)))
lay = sorted(set(lay))
print("laying", len(lay))
if lay and "--dry" not in sys.argv:
    o = subprocess.run([sys.executable, os.path.join(HERE, "designate-cells.py"), "architect-designator:power:build-hiddenconduit",
                        " ".join("%d,%d" % p for p in lay)], capture_output=True, text=True).stdout
    print(o.strip().splitlines()[-1] if o.strip() else "?")
