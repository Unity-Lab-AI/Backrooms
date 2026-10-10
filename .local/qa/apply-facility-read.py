# -*- coding: utf-8 -*-
"""Turn the owner's live facility into `RR_AsyncIndustriesStart`'s own data.

Owner, 2026-10-06: *"ANd thhese places i put everything is exact and purposfully and should use
them exactly."* So every cell below comes from the read, never from a judgement about where a thing
ought to go.

What this writes
----------------
* `<conduits>`   the live transmitter set, recompressed into runs
* `<removedWalls>` the six authored wall cells the owner cut open
* `<autodoors>`  the gate door they moved
* `<buildings>`  their additions, with material; the eight real deletions dropped
* and three things they asked for that are not in the read: a trade beacon in every room that
  holds a shelf, the card table finished, and the four freezer coolers carrying their temperature.

Multi-cell footprints are the fiddly part
-----------------------------------------
A read reports cells, and `<buildings>` wants one entry per thing. A `WoodFiredGenerator` is 2x2, so
ten live cells are between two and three generators depending on how they sit. Cells of one def are
therefore clustered and each cluster reduced to **its anchor**, which RimWorld takes as the centre:
`min + (size-1)/2`.

**Anything that does not divide cleanly is reported rather than guessed.** A cluster whose cell count
is not a multiple of the footprint means the read saw a partial footprint -- a thing straddling the
edge of the snapshot rect -- and inventing an anchor for it would place a generator one cell off
where the owner put it.
"""
import importlib.util
import io
import json
import os
import re
import sys
from collections import defaultdict

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")
DEF_NAME = "RR_AsyncIndustriesStart"
TRANSMITTER = ("PowerConduit", "HiddenConduit")
FREEZER_COOLERS = {(51, 19), (51, 20), (51, 21), (51, 22)}
FREEZER_TARGET = "-8"


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def size_of(index, name):
    record = index.get(name) or {}
    raw = record.get("size")
    if not raw:
        return 1, 1
    match = re.match(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", raw)
    return (int(match.group(1)), int(match.group(2))) if match else (1, 1)


def clusters(cells, width, height):
    """Group cells of one def into footprint-sized blocks, lowest corner first."""
    remaining = set(cells)
    found = []
    for cell in sorted(remaining):
        if cell not in remaining:
            continue
        block = {(cell[0] + dx, cell[1] + dz)
                 for dx in range(width) for dz in range(height)}
        if block <= remaining:
            remaining -= block
            found.append((cell, True))
        else:
            remaining.discard(cell)
            found.append((cell, False))
    return found


def runs_from(cells):
    """Loose cells back into runs, because `<conduits>` is authored as runs."""
    remaining = set(cells)
    out = []
    for cell in sorted(remaining):
        if cell not in remaining:
            continue
        length = 1
        while (cell[0] + length, cell[1]) in remaining:
            length += 1
        if length > 1:
            for step in range(length):
                remaining.discard((cell[0] + step, cell[1]))
            out.append((cell, length, True))
            continue
        length = 1
        while (cell[0], cell[1] + length) in remaining:
            length += 1
        for step in range(length):
            remaining.discard((cell[0], cell[1] + length - 1 - step))
        out.append((cell, length, False))
    return out


def main():
    fd = load("fd", os.path.join(HERE, "facility-diff.py"))
    fc = load("fc", os.path.join(HERE, "facility-changes.py"))
    plan = fd.authored(DEF_NAME)
    walls, openings, wall_stuff = fc.authored_walls(DEF_NAME)
    index = fc.def_index()

    snapshot = os.path.join(HERE, "facility-%s.json" % DEF_NAME)
    saved = json.load(io.open(snapshot, encoding="utf-8-sig"))
    live_raw, terrain_raw = fd.live_cells(saved["tiles"])
    off_x, off_z = saved["offset"]
    live = {(x - off_x, z - off_z): v for (x, z), v in live_raw.items()}
    terrain = {(x - off_x, z - off_z): v for (x, z), v in terrain_raw.items()}

    # ---------------------------------------------------------------- conduits
    conduit_cells = {c for c, items in live.items()
                     if any(i["thing"] in TRANSMITTER for i in items)}

    # ---------------------------------------------------------------- walls
    added_walls = []
    for cell, items in live.items():
        for item in items:
            if item["thing"] == "Wall" and cell not in walls:
                added_walls.append((cell, item["stuff"]))
    removed_walls = []
    for cell in walls:
        if cell not in terrain:
            continue
        standing = live.get(cell) or []
        if any(i["thing"] == "Wall" or i["thing"] in ("Door", "Autodoor") for i in standing):
            continue
        # A wall cell now holding a vent, cooler or autodoor is NOT a removal -- the generator
        # replaces its own wall for anything the game marks `canPlaceOverWall`.
        if any((index.get(i["thing"]) or {}).get("category") == "Building" for i in standing):
            continue
        removed_walls.append(cell)

    # ---------------------------------------------------------------- doors added
    added_doors = [c for c, items in live.items()
                   if any(i["thing"] == "Autodoor" for i in items) and c not in openings]

    # ---------------------------------------------------------------- buildings added
    by_def = defaultdict(set)
    authored_occupied = {}
    rotations = {}
    root = __import__("xml.etree.ElementTree", fromlist=["ElementTree"]).parse(STARTS).getroot()
    node = next(n for n in root if (n.findtext("defName") or "") == DEF_NAME)
    for li in node.find("buildings").findall("li"):
        m = re.search(r"\(\s*(-?\d+)\s*,\s*-?\d+\s*,\s*(-?\d+)\s*\)", li.findtext("cell") or "")
        if m:
            rotations[(int(m.group(1)), int(m.group(2)))] = int(li.findtext("rotation") or 0)
    for cell, names in plan["buildings"].items():
        for name in names:
            for covered in fc.footprint(cell, name, rotations.get(cell, 0), index):
                authored_occupied.setdefault(covered, set()).add(name)

    for cell, items in live.items():
        for item in items:
            name = item["thing"]
            if name in TRANSMITTER or name == "Wall" or name in ("Door", "Autodoor"):
                continue
            if fc.NATURAL.match(name):
                continue
            if (index.get(name) or {}).get("category") != "Building":
                continue
            # **NO AUTHORED-OCCUPANCY FILTER HERE, and removing it is the fix for seven false
            # "partial footprints".** A thing the owner MOVED overlaps its own old position: the
            # comms console authored at (32,33) is 3x2, and they slid it one row to (32,32), so half
            # its live cells sat inside the authored footprint and were dropped -- leaving three
            # orphan cells that could not form a 3x2 and were reported as partial.
            #
            # Clustering EVERY live cell and then diffing ANCHORS handles a move correctly: the new
            # anchor is absent from the authored set and the old one is absent from the live set, so
            # one shows as added and the other as removed, which is what a move is.
            by_def[(name, item["stuff"])].add(cell)

    # Every authored anchor, so a live anchor can be recognised as already authored.
    authored_anchors = set()
    for cell, names in plan["buildings"].items():
        for name in names:
            authored_anchors.add((name, cell))

    additions = []
    partials = []
    for (name, stuff), cells in sorted(by_def.items()):
        width, height = size_of(index, name)
        for corner, whole in clusters(cells, width, height):
            anchor = (corner[0] + (width - 1) // 2, corner[1] + (height - 1) // 2)
            if not whole:
                partials.append((name, stuff, corner, width, height))
            elif (name, anchor) not in authored_anchors:
                additions.append((name, stuff, anchor))

    # ---------------------------------------------------------------- deletions
    # **AN AUTHORED THING IS PRESENT ONLY IF A LIVE ANCHOR SITS ON ITS OWN CELL.**
    #
    # The first version asked whether *any* cell of its footprint held that def, and that is true
    # for a thing the owner MOVED BY ONE CELL -- so an authored generator at (23,36) read as present
    # while a new one was also added at (23,35), and `check-start-layout` caught the two overlapping.
    # The live anchors are exact, so comparing anchors is exact.
    live_anchors = set()
    for (name, _stuff), cells in by_def.items():
        width, height = size_of(index, name)
        for corner, whole in clusters(cells, width, height):
            if whole:
                live_anchors.add(
                    (name, (corner[0] + (width - 1) // 2, corner[1] + (height - 1) // 2)))

    absent = []
    for cell, names in plan["buildings"].items():
        if cell not in terrain:
            continue
        for name in names:
            # An ITEM is hauled by pawns, so not finding it where it was authored proves nothing.
            if (index.get(name) or {}).get("category") != "Building":
                continue
            if (name, cell) not in live_anchors:
                absent.append((cell, name))

    # **A MOVED THING KEEPS ITS FACING, and without this one did not.**
    #
    # `get_cells_info` carries no rotation, so every addition was emitted as rotation 0. For most
    # things that is invisible; for anything with an interaction cell it is not. The comms console
    # the owner slid one row down came back facing north and put its interaction cell **inside a
    # wall**, where nobody could ever stand to use it -- caught by `check-start-layout`.
    #
    # So an addition whose def also appears among the absences is a MOVE, and it inherits the
    # rotation that entry was authored with. Anything genuinely new keeps 0, which is correct: the
    # owner placed it and a read cannot tell us more than it knows.
    absent_rotations = {}
    for cell, name in absent:
        if name not in absent_rotations:
            absent_rotations[name] = rotations.get(cell, 0)
    additions = [(name, stuff, anchor, absent_rotations.get(name, 0))
                 for name, stuff, anchor in additions]

    # ---------------------------------------------------------------- trade beacons
    shelf_rooms = []
    for room in plan["rooms"]:
        x0, z0, w, h = room
        inside = {(x, z) for x in range(x0 + 1, x0 + w - 1) for z in range(z0 + 1, z0 + h - 1)}
        if not inside:
            continue
        holds_shelf = any(any(i["thing"] == "Shelf" for i in (live.get(c) or [])) for c in inside)
        if not holds_shelf:
            continue
        centre = (x0 + w // 2, z0 + h // 2)
        # The middle of the room, moved to the nearest free inside cell if the middle is taken --
        # the owner said the middle, and a beacon that refuses to spawn is worse than one a cell off.
        free = sorted(inside, key=lambda c: (abs(c[0] - centre[0]) + abs(c[1] - centre[1])))
        chosen = next((c for c in free
                       if not (live.get(c) or [])
                       and c not in authored_occupied
                       and c not in conduit_cells), None)
        if chosen is not None:
            shelf_rooms.append((room, chosen))

    say("apply-facility-read  %s" % DEF_NAME)
    say("  conduit cells        : %d -> %d run(s)" % (len(conduit_cells),
                                                      len(runs_from(conduit_cells))))
    say("  walls added          : %d" % len(added_walls))
    say("  walls removed        : %d" % len(removed_walls))
    say("  autodoors added      : %d  %s" % (len(added_doors), added_doors))
    say("  buildings added      : %d" % len(additions))
    say("  partial footprints   : %d  (reported, never guessed)" % len(partials))
    say("  authored but absent  : %d" % len(absent))
    say("  rooms holding a shelf: %d -> a beacon each" % len(shelf_rooms))
    say("")
    for name, stuff, corner, w, h in partials:
        say("    PARTIAL %-22s at %s needs %dx%d" % (name, corner, w, h))
    if partials:
        say("")
    say("  additions by kind:")
    counts = defaultdict(int)
    for name, stuff, anchor, _rotation in additions:
        counts[(name, stuff)] += 1
    for (name, stuff), count in sorted(counts.items(), key=lambda kv: -kv[1]):
        say("    %-24s %-16s %d" % (name, stuff or "-", count))
    say("")
    say("  absent, to be dropped from the def:")
    for cell, name in sorted(absent):
        say("    (%2d, %2d)  %s" % (cell[0], cell[1], name))

    out = {
        "conduits": [[list(c), length, along] for c, length, along in runs_from(conduit_cells)],
        "removedWalls": sorted(removed_walls),
        "autodoorsAsBuildings": sorted(added_doors),
        "addedWalls": [[list(c), s] for c, s in sorted(added_walls)],
        "additions": [[n, s, list(a), r] for n, s, a, r in additions],
        "absent": [[list(c), n] for c, n in sorted(absent)],
        "beacons": [list(c) for _, c in shelf_rooms],
        "freezerCoolers": sorted(list(c) for c in FREEZER_COOLERS),
        "freezerTarget": FREEZER_TARGET,
    }
    path = os.path.join(HERE, "facility-apply-%s.json" % DEF_NAME)
    io.open(path, "w", encoding="utf-8", newline=NL).write(json.dumps(out, indent=1))
    say("")
    say("wrote %s" % os.path.relpath(path, REPO).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
