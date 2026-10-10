"""Climate for every room that has none (owner, 2026-10-09: "ac and heat is still not solved base wide" /
"prison need ac and heat and vents and stuff, i told you all rooms keep at it").
CLUSTER RULE FIRST (owner, 2026-10-09: "hnot heater in every room and ac on every wall vents vents vents!!!!"
/ "3 rooms per one based on size"): a room next to a room that already has climate gets an over-wall VENT
into it (a cluster serves up to 3 rooms, fewer when they are big); only a room with no conditioned
neighbour gets its own cooler + heater, and then its own neighbours vent off it. For each roofed room of 6+
cells with no heater, cooler or vent on or around it:
  * a wall cell with open ground beyond -> over-wall cooler, hot side out (rot = direction of the outside)
    and a heater on a free floor cell beside a wall;
  * no outside wall -> an over-wall vent into a neighbour room that already has climate units.
Everything is placed through hvac-place.py (the real Architect UI, rotated).

    python .local/qa/hvac-auto.py [--dry] [--max N]
"""
import importlib.util, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
DRY = "--dry" in sys.argv; NOTOWERS = "--no-towers" in sys.argv; MAX = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 999
sys.argv = ["x"]
s = importlib.util.spec_from_file_location("c", os.path.join(HERE, "checklist.py")); c = importlib.util.module_from_spec(s); s.loader.exec_module(c)
cells, _ = c.scan(); rid, rs = c.rooms(cells)
DIRS = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}
def plain_wall(p):
    d = c.defs(cells[p]) if p in cells else []
    return any(t == "Wall" for t in d) and not any(("Cooler" in t or "Vent" in t or "Heater" in t or "Blueprint" in t or "Embrasure" in t) for t in d)
def units(cs):
    n = 0
    for x, z in cs:
        for dx, dz in [(0, 0)] + list(DIRS.values()):
            p = (x + dx, z + dz)
            if p in cells and any(("Cooler" in t or "Heater" in t or "Vent" in t) for t in c.defs(cells[p])): n += 1
    return n
served = {}   # room id -> cells already hanging off its unit through vents
def cluster_ok(j, size):
    """A unit serves at most 3 rooms and about 120 cells in all ("3 rooms per one based on size")."""
    n, cells_ = served.get(j, (1, len(rs[j])))
    if n >= 3 or cells_ + size > 120: return False
    served[j] = (n + 1, cells_ + size); return True
done = 0
for i, cs in enumerate(rs):
    if len(cs) < 6 or units(cs) or done >= MAX: continue
    # gun towers sit outside the wall line: last in line when steel is short (--no-towers)
    if NOTOWERS and any(x < 108 or x > 192 or z < 64 or z > 136 for x, z in cs): continue
    # embrasure rooms leak air: never conditioned (owner, 2026-10-09: "embrasures leak air dont condition")
    if any("Embrasure" in t for x, z in cs for dx, dz in DIRS.values() if (x + dx, z + dz) in cells for t in c.defs(cells[(x + dx, z + dz)])): continue
    xs = [p[0] for p in cs]; zs = [p[1] for p in cs]; box = (min(xs), min(zs), max(xs), max(zs))
    vent = None
    for x, z in cs:
        for r, (dx, dz) in DIRS.items():
            w = (x + dx, z + dz); o = (x + 2 * dx, z + 2 * dz)
            if plain_wall(w) and o in rid and rid[o] != i and units(rs[rid[o]]) and cluster_ok(rid[o], len(cs)):
                vent = (w, 0 if dz else 1); break
        if vent: break
    if vent:
        print("room %s size %d: vent %s rot %d (shares its neighbour's unit)" % (box, len(cs), vent[0], vent[1]))
        if not DRY: print(subprocess.run([PY, os.path.join(HERE, "hvac-place.py"), "overvent", str(vent[1]), "%d,%d" % vent[0]], capture_output=True, text=True).stdout.strip())
        done += 1; continue
    cool = None
    for x, z in cs:
        for r, (dx, dz) in DIRS.items():
            w = (x + dx, z + dz); o = (x + 2 * dx, z + 2 * dz)
            if plain_wall(w) and o in cells and c.kind(cells[o]) == "out": cool = (w, r); break
        if cool: break
    if cool:
        heat = next(((x, z) for x, z in cs if not [t for t in c.defs(cells[(x, z)]) if not t.startswith(("Filth", "Plant"))]
                     and any(c.kind(cells[(x + dx, z + dz)]) == "wall" for dx, dz in DIRS.values() if (x + dx, z + dz) in cells)
                     and (x, z) != (cool[0][0] - DIRS[cool[1]][0], cool[0][1] - DIRS[cool[1]][1])), None)
        print("room %s size %d: cooler %s rot %d, heater %s" % (box, len(cs), cool[0], cool[1], heat))
        if not DRY:
            print(subprocess.run([PY, os.path.join(HERE, "hvac-place.py"), "overcooler", str(cool[1]), "%d,%d" % cool[0]], capture_output=True, text=True).stdout.strip())
            # a heater has no rotation: the build API places it directly (the UI click path kept failing)
            if heat: print("heater", subprocess.run([PY, os.path.join(HERE, "designate-cells.py"), "architect-designator:temperature:build-heater", "%d,%d" % heat], capture_output=True, text=True).stdout.strip())
        done += 1; continue
    vent = None
    for x, z in cs:
        for r, (dx, dz) in DIRS.items():
            w = (x + dx, z + dz); o = (x + 2 * dx, z + 2 * dz)
            if plain_wall(w) and o in rid and rid[o] != i and units(rs[rid[o]]): vent = (w, 0 if dz else 1); break
        if vent: break
    print("room %s size %d: %s" % (box, len(cs), ("vent %s rot %d" % vent) if vent else "NO outside wall and no conditioned neighbour"))
    if vent and not DRY:
        print(subprocess.run([PY, os.path.join(HERE, "hvac-place.py"), "overvent", str(vent[1]), "%d,%d" % vent[0]], capture_output=True, text=True).stdout.strip())
    done += 1
