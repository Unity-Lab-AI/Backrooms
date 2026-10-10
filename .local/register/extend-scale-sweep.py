# -*- coding: utf-8 -*-
"""The scale sweep as proof claims: the cap is sized, and nothing in the wiring is fatal."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENP = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

text = io.open(GENP, encoding="utf-8").read()
ANCHOR = 'print("")\nif failures:'

NEW = '''print("")
print("THE SCALE SWEEP: THE CONDUIT CAP IS SIZED FOR THE MAP IT IS ON")
print("-" * 78)

# Owner: *"its suppose to be built and working 100% we finished the build yesterday!"* -- correct,
# and the right answer was to stop finding these one launch at a time. Every constant in the
# generation path was sized against a 300x300 map, 80-cell rooms and 42 rooms.
#
# Two more would have killed a coordinate, both the same family as the light count at 0.12.48-dev
# and the conduit carpet at 0.12.52-dev: a number written against the old scale that no proof can
# see has stopped fitting.
#
# THIS CLAIM MODELS THE ROUTING AND COMPARES IT TO THE CAP THE SOURCE HOLDS, so the cap cannot
# silently stop fitting again. FindConduitRoute BFSes from the whole wired set, so routes share a
# spine and the total is far below the sum of the distances -- which is why the answer is about
# 1,600 rather than tens of thousands.
from collections import deque as _deque

_CAP = re.search(r"const\\s+int\\s+MaxNativePowerConduits\\s*=\\s*(\\d+)", genstep)
_MAPW = re.search(r"const\\s+int\\s+MapWidth\\s*=\\s*(\\d+)",
                  read(os.path.join(SRC, "Generation", "DestinationService.cs")))
_PL = read(os.path.join(SRC, "Generation", "RoomLayoutPlanner.cs"))


def _planner_const(name):
    found = re.search(r"const\\s+int\\s+%s\\s*=\\s*(\\d+)" % name, _PL)
    return int(found.group(1)) if found else None


def _conduits_needed(depth, mapw, margin, gap, mins, maxs, maxrooms):
    slots = max(mins, min(maxs, mins + max(0, depth - 1)))
    spacing = (mapw - margin * 2) // slots
    span = spacing - gap
    if span % 2:
        span -= 1
    span = max(8, span)
    order = []
    for row in range(slots):
        for col in range(slots):
            order.append((col if row % 2 == 0 else slots - 1 - col, row))
    chain = max(6, min(maxrooms, min(len(order), len(order) * 2 // 3)))
    rooms = [order[i] for i in range(chain)]

    def centre(index):
        return margin + spacing // 2 + spacing * index

    walk = set()
    for sx, sz in rooms:
        cx, cz = centre(sx), centre(sz)
        for x in range(cx - span // 2 + 1, cx + span // 2):
            for z in range(cz - span // 2 + 1, cz + span // 2):
                walk.add((x, z))
    for i in range(1, chain):
        a, b = rooms[i - 1], rooms[i]
        ax, az, bx, bz = centre(a[0]), centre(a[1]), centre(b[0]), centre(b[1])
        if az == bz:
            for x in range(min(ax, bx), max(ax, bx) + 1):
                for dz in (-1, 0, 1):
                    walk.add((x, az + dz))
        else:
            for z in range(min(az, bz), max(az, bz) + 1):
                for dx in (-1, 0, 1):
                    walk.add((ax + dx, z))
    # One lamp per room plus a heater, and then the same again to stand in for whatever the
    # depth-scaled dressing adds. If it fits at double, it fits.
    consumers = [(centre(sx), centre(sz) + 2) for sx, sz in rooms]
    consumers.append((centre(rooms[0][0]) - 2, centre(rooms[0][1])))
    consumers += [(centre(sx) + 3, centre(sz) - 3) for sx, sz in rooms]
    wired = set([(centre(rooms[0][0]) + 2, centre(rooms[0][1]))])
    for target in consumers:
        if target in wired:
            continue
        previous = {}
        pending = _deque(wired)
        seen = set(wired)
        hit = None
        while pending:
            cell = pending.popleft()
            if cell == target:
                hit = cell
                break
            for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (cell[0] + step[0], cell[1] + step[1])
                if near in seen or near not in walk:
                    continue
                seen.add(near)
                previous[near] = cell
                pending.append(near)
        if hit is None:
            continue
        cell = hit
        while cell in previous:
            wired.add(cell)
            cell = previous[cell]
    return chain, len(wired)


_margin = _planner_const("Margin")
_gap = _planner_const("SlotGap")
_mins = _planner_const("MinSlotsPerAxis")
_maxs = _planner_const("MaxSlotsPerAxis")
_maxrooms = _planner_const("MaxRooms")
_readable = (_CAP is not None and _MAPW is not None and None not in
             (_margin, _gap, _mins, _maxs, _maxrooms))
check("every constant this sizing needs was found in the source",
      _readable,
      "-- a renamed constant must fail here rather than be silently skipped, or this claim would "
      "pass by modelling nothing")

if _readable:
    _cap = int(_CAP.group(1))
    _worst = 0
    print("     depth rooms  conduits needed  cap")
    for _depth in range(1, 9):
        _rooms, _needed = _conduits_needed(_depth, int(_MAPW.group(1)), _margin, _gap,
                                           _mins, _maxs, _maxrooms)
        _worst = max(_worst, _needed)
        print("     %5d %5d %16d %4d" % (_depth, _rooms, _needed, _cap))
    check("THE CONDUIT CAP FITS EVERY DEPTH, WITH DOUBLE THE CONSUMERS",
          _worst <= _cap,
          "-- worst case %d against a cap of %d. 512 was sized for 60x60: depth 1 fitted under it "
          "by forty cells and every level below died, which is the worst failure mode there is "
          "because it looks fixed" % (_worst, _cap))
    check("and it is not absurdly oversized either",
          _cap <= _worst * 6,
          "-- headroom is %.1fx. A cap so large it can never bind is not a cap"
          % (float(_cap) / max(1, _worst)))

check("NOTHING IN THE WIRING CAN DESTROY A COORDINATE ANY MORE",
      "if (!destination.IsValid) { return new List<IntVec3>(); }" in genstep
      and "if (!previous.TryGetValue(cursor, out predecessor)) { return new List<IntVec3>(); }"
      in genstep,
      "-- a consumer the conduit cannot reach is a dark corner. Both of these threw, and a throw "
      "here destroyed the whole place: the exact defect that cost the fifth and sixth launches")

check("the known-consumer routes use the non-throwing placement too",
      "SpawnNativeConduit(" not in
      genstep.split("foreach (CellRect consumer in consumerFootprints)")[1].split("}")[0]
      .replace("TrySpawnNativeConduit(", ""),
      "-- the throwing form is now reserved for the generator's own footprint, where a failure "
      "really is a generator fault")

check("and both loops stop at the cap rather than passing it",
      genstep.count("if (wiredCells.Count >= MaxNativePowerConduits) { break; }") >= 2,
      "-- stopping the wiring is the degradation; throwing was the bug")

''' + ANCHOR

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(GENP, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("scale-sweep claims added")
