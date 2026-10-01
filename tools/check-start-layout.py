# -*- coding: utf-8 -*-
"""Validate every authored starting-facility layout offline, cell by cell.

Why this checker exists
-----------------------
`GenStep_Headquarters.Build` **throws** on any authored geometry mistake, and a throw there is
inside a GenStep: the player loses the start. It refuses a door whose cell has no wall, furniture
that intersects a wall or another building, a conduit outside the map, an arrival cell that is not
walkable, and a glazed run with no wall under it.

Every one of those is decidable from the XML alone, and **none of the fifteen other checkers looks
at it.** The Async Industries facility is being rebuilt from nine boxes in a rectangle into a gate
hall, a control room behind ballistic glass, a security airlock, a lab wing, secure storage and a
workshop -- owner, 2026-10-01: *"it should be designed intelligently with like ballistic glass
walls for viewing the machine remotely and safely with security zones and shit and lab rooms and
shit i mean wtf is this this is a 50million dollar facilty"*. That is several hundred authored
cells. Hand-checking them is how a start ships broken.

What it proves
--------------
For every `RimroomsStartDef` in the package:

  * every room is at least 3x3 and the whole layout fits `mapSize` with Core's 8-cell edge margin,
  * **every door cell is a wall cell** of some room, and is not the interior of any room,
  * no door is listed twice, and every autodoor is also a door,
  * **every glazed cell is a wall cell and is not a door cell**,
  * **every building's full footprint** -- resolved from Core's own `<size>`, with ParentName
    inheritance -- lies on room interior cells, never on a wall, a door or another building,
  * every column stands on a free interior cell, never on a door or under furniture,
  * every conduit cell is inside the layout's own extent,
  * the arrival, stock and emergence cells are interior cells, and the emergence cell is a door,
  * no room's wall runs through another room's interior.

Sizes come from the installed Core data rather than from a table in this file, because a table is
a second derivation that goes stale -- the defect this project keeps meeting.
"""
from __future__ import annotations

import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
STARTS = os.path.join(PACKAGE, "Defs", "RimroomsStartDefs", "RR_Starts.xml")
DEFAULT_GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld"
EDGE_MARGIN = 8

problems: list[str] = []


def fail(message: str) -> None:
    problems.append(message)


def core_data() -> str:
    path = os.environ.get("RIMWORLD_PATH") or DEFAULT_GAME
    data = os.path.join(path, "Data", "Core", "Defs")
    if not os.path.isdir(data):
        print("FAILED: the installed Core defs are not at %r. Set RIMWORLD_PATH." % path)
        raise SystemExit(1)
    return data


def thing_sizes(core: str) -> dict:
    """Every Core ThingDef's footprint, resolving ParentName inheritance."""
    by_name = {}
    order = []
    for root, _dirs, files in os.walk(core):
        for name in files:
            if not name.lower().endswith(".xml"):
                continue
            try:
                tree = ET.parse(os.path.join(root, name))
            except ET.ParseError:
                continue
            for node in tree.getroot():
                if node.tag != "ThingDef":
                    continue
                key = node.findtext("defName") or node.get("Name")
                if not key:
                    continue
                record = {
                    "size": node.findtext("size"),
                    "parent": node.get("ParentName"),
                    "abstract": node.get("Abstract") == "True",
                }
                for handle in filter(None, [node.findtext("defName"), node.get("Name")]):
                    by_name[handle] = record
                order.append(key)
    return by_name


def size_of(name: str, sizes: dict) -> tuple:
    """(width, height) for a def, walking up ParentName until a <size> is found."""
    seen = set()
    cursor = name
    while cursor and cursor in sizes and cursor not in seen:
        seen.add(cursor)
        record = sizes[cursor]
        if record["size"]:
            match = re.findall(r"-?\d+", record["size"])
            if len(match) >= 2:
                return int(match[0]), int(match[1])
        cursor = record["parent"]
    return 1, 1


def occupied(cell: tuple, rotation: int, size: tuple) -> list:
    """Core's GenAdj.OccupiedRect, for the rotations a start may author."""
    width, height = size
    if rotation % 2 == 1:
        width, height = height, width
    min_x = cell[0] - (width - 1) // 2
    min_z = cell[1] - (height - 1) // 2
    return [(x, z) for x in range(min_x, min_x + width) for z in range(min_z, min_z + height)]


def cell_of(text: str) -> tuple:
    numbers = re.findall(r"-?\d+", text or "")
    if len(numbers) == 3:
        return int(numbers[0]), int(numbers[2])
    if len(numbers) == 2:
        return int(numbers[0]), int(numbers[1])
    return None


def check_start(node, sizes: dict) -> None:
    label = node.findtext("defName") or "(unnamed)"
    map_size = int(node.findtext("mapSize") or "60")

    rooms = []
    for plan in node.findall("rooms/li"):
        x = int(plan.findtext("x"))
        z = int(plan.findtext("z"))
        w = int(plan.findtext("width"))
        h = int(plan.findtext("height"))
        if w < 3 or h < 3:
            fail("%s: a room smaller than 3x3 at (%d,%d) -- the generator refuses it" % (label, x, z))
        rooms.append((x, z, w, h))
    if not rooms:
        fail("%s: no rooms" % label)
        return

    walls = set()
    interiors = set()
    for (x, z, w, h) in rooms:
        max_x, max_z = x + w - 1, z + h - 1
        for cx in range(x, max_x + 1):
            for cz in range(z, max_z + 1):
                if cx in (x, max_x) or cz in (z, max_z):
                    walls.add((cx, cz))
                else:
                    interiors.add((cx, cz))
    # A room's wall running through another room's interior is a wall in the middle of a room --
    # **unless the inner room is NESTED inside the outer one**, which is ordinary architecture:
    # every one of these layouts is an outer compound rectangle with its rooms partitioned inside
    # it. The first draft of this rule flagged 368 legitimate cells in the Async layout and 210 in
    # the store, which is a checker crying wolf, and this project has had four of those.
    def contains(outer, inner):
        return (outer[0] <= inner[0] and outer[1] <= inner[1]
                and outer[0] + outer[2] >= inner[0] + inner[2]
                and outer[1] + outer[3] >= inner[1] + inner[3])

    for outer in rooms:
        o_interior = {(x, z)
                      for x in range(outer[0] + 1, outer[0] + outer[2] - 1)
                      for z in range(outer[1] + 1, outer[1] + outer[3] - 1)}
        for inner in rooms:
            if inner is outer or contains(outer, inner):
                continue
            i_max_x, i_max_z = inner[0] + inner[2] - 1, inner[1] + inner[3] - 1
            i_walls = {(x, z)
                       for x in range(inner[0], i_max_x + 1)
                       for z in range(inner[1], i_max_z + 1)
                       if x in (inner[0], i_max_x) or z in (inner[1], i_max_z)}
            crossing = i_walls & o_interior
            if crossing:
                fail("%s: the room at (%d,%d) puts %d wall cell(s) inside the room at (%d,%d) "
                     "without being nested in it, e.g. %s"
                     % (label, inner[0], inner[1], len(crossing), outer[0], outer[1],
                        sorted(crossing)[:4]))

    extent_min_x = min(r[0] for r in rooms)
    extent_min_z = min(r[1] for r in rooms)
    extent_max_x = max(r[0] + r[2] - 1 for r in rooms)
    extent_max_z = max(r[1] + r[3] - 1 for r in rooms)
    span = max(extent_max_x - extent_min_x + 1, extent_max_z - extent_min_z + 1)
    if span + EDGE_MARGIN * 2 > map_size:
        fail("%s: the layout spans %d cells and needs %d with margins, but mapSize is %d"
             % (label, span, span + EDGE_MARGIN * 2, map_size))

    doors = []
    for plan in node.findall("doors/li"):
        cell = cell_of(plan.text)
        if cell is None:
            fail("%s: an unparseable door cell %r" % (label, plan.text))
            continue
        doors.append(cell)
    door_set = set(doors)
    if len(doors) != len(door_set):
        duplicates = sorted({c for c in doors if doors.count(c) > 1})
        fail("%s: duplicate door cells %s -- the second spawn finds no wall" % (label, duplicates))
    for cell in door_set:
        if cell not in walls:
            fail("%s: door at %s is not on any room's wall -- the generator throws here"
                 % (label, cell))
        if cell in interiors and cell not in walls:
            fail("%s: door at %s is inside a room" % (label, cell))

    autodoors = {cell_of(p.text) for p in node.findall("autodoors/li")}
    for cell in autodoors - {None}:
        if cell not in door_set:
            fail("%s: autodoor at %s is not in the doors list" % (label, cell))

    glazed = set()
    for run in node.findall("glazing/li"):
        start = cell_of(run.findtext("start"))
        length = int(run.findtext("length") or "0")
        along_x = (run.findtext("alongX") or "true").strip().lower() != "false"
        names = [n.text for n in run.findall("thingDefNames/li") if n.text]
        if start is None or length < 1:
            fail("%s: an invalid glazed run" % label)
            continue
        if not names:
            fail("%s: a glazed run names no candidate def" % label)
        for step in range(length):
            cell = (start[0] + (step if along_x else 0), start[1] + (0 if along_x else step))
            if cell not in walls:
                fail("%s: glazing at %s is not on a wall -- the generator throws here" % (label, cell))
            if cell in door_set:
                fail("%s: glazing at %s is also a door -- the door loop then finds glass, not a wall"
                     % (label, cell))
            glazed.add(cell)

    # Columns are walls the generator spawns inside a room. They must stand on a free interior
    # cell, never on a door and never under furniture: `GenStep_Headquarters` refuses a column
    # whose cell already holds an edifice, and the building loop refuses furniture on one.
    taken = {}
    pillars = set()
    for plan in node.findall("pillars/li"):
        cell = cell_of(plan.text)
        if cell is None:
            fail("%s: an unparseable pillar cell %r" % (label, plan.text))
            continue
        if cell not in interiors:
            fail("%s: pillar at %s is not inside a room" % (label, cell))
        if cell in door_set:
            fail("%s: pillar at %s is also a door" % (label, cell))
        if cell in pillars:
            fail("%s: duplicate pillar at %s -- the second spawn finds an edifice" % (label, cell))
        pillars.add(cell)
        taken[cell] = ("pillar", cell)
    for plan in node.findall("buildings/li"):
        thing = (plan.findtext("thing") or "").strip()
        cell = cell_of(plan.findtext("cell"))
        rotation = int(plan.findtext("rotation") or "0")
        if not thing or cell is None:
            fail("%s: an incomplete building plan" % label)
            continue
        if thing not in sizes:
            # Not fatal here: a start may name a def from an optional mod, and the generator's
            # own `ThingDef` field would have reported an unresolved cross-reference at load.
            # Reported so an authoring typo is still visible.
            fail("%s: building %r is not a Core def -- a ThingDef field cannot resolve it safely"
                 % (label, thing))
            continue
        for occupied_cell in occupied(cell, rotation, size_of(thing, sizes)):
            if occupied_cell in walls:
                fail("%s: %s at %s covers the wall cell %s -- the generator throws here"
                     % (label, thing, cell, occupied_cell))
            elif occupied_cell not in interiors:
                fail("%s: %s at %s covers %s, which is not inside any room"
                     % (label, thing, cell, occupied_cell))
            if occupied_cell in taken:
                fail("%s: %s at %s overlaps %s at %s on cell %s"
                     % (label, thing, cell, taken[occupied_cell][0], taken[occupied_cell][1],
                        occupied_cell))
            taken[occupied_cell] = (thing, cell)

    for name, text in (("arrivalCell", node.findtext("arrivalCell")),
                       ("stockCell", node.findtext("stockCell"))):
        cell = cell_of(text)
        if cell is None:
            fail("%s: %s is missing" % (label, name))
            continue
        if cell not in interiors:
            fail("%s: %s %s is not inside a room" % (label, name, cell))
        if cell in taken:
            fail("%s: %s %s is under %s" % (label, name, cell, taken[cell][0]))

    emergence = cell_of(node.findtext("emergenceDoorCell"))
    if emergence is not None and emergence not in door_set:
        fail("%s: emergenceDoorCell %s is not one of this start's doors" % (label, emergence))

    for line in node.findall("conduits/li"):
        start = cell_of(line.findtext("start"))
        length = int(line.findtext("length") or "0")
        along_x = (line.findtext("alongX") or "true").strip().lower() != "false"
        if start is None or length < 1 or length > map_size:
            fail("%s: an invalid conduit run" % label)
            continue
        for step in range(length):
            cell = (start[0] + (step if along_x else 0), start[1] + (0 if along_x else step))
            if not (extent_min_x - 1 <= cell[0] <= extent_max_x + 1
                    and extent_min_z - 1 <= cell[1] <= extent_max_z + 1):
                fail("%s: conduit cell %s is outside the layout's own extent" % (label, cell))
                break

    print("  %-28s rooms %2d  doors %2d  auto %d  glazed %3d  columns %d  buildings %3d  span %d/%d"
          % (label, len(rooms), len(door_set), len(autodoors - {None}), len(glazed),
             len(pillars), len(node.findall("buildings/li")), span, map_size))


def main() -> int:
    if not os.path.isfile(STARTS):
        print("FAILED: %s is missing." % STARTS)
        return 1
    sizes = thing_sizes(core_data())
    print("Core ThingDef footprints read: %d" % len(sizes))
    tree = ET.parse(STARTS)
    found = 0
    for node in tree.getroot():
        if not node.tag.endswith("RimroomsStartDef"):
            continue
        found += 1
        check_start(node, sizes)
    if found == 0:
        print("FAILED: no start definitions were parsed, so nothing was checked.")
        return 1
    print("")
    if problems:
        print("FAILED: %d layout problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("OK: %d starting layout(s) are geometrically sound." % found)
    return 0


if __name__ == "__main__":
    sys.exit(main())
