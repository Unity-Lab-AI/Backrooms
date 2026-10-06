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
  * **every interaction cell is a standable interior cell**, so a bench or console can
    actually be used -- Core requires a pawn to stand on exactly that cell,
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
                    # **The game's own permission to stand in a wall.** `Vent`, `Cooler` and
                    # `Autodoor` carry it, and it is what lets a player build one into a standing
                    # wall. Read rather than hard-coded, so a mod or a DLC adding another
                    # wall-mountable thing is covered without touching this rule.
                    "overWall": (node.find("building") is not None
                                 and (node.find("building").findtext("canPlaceOverWall") or "")
                                 .strip().lower() == "true"),
                    "parent": node.get("ParentName"),
                    "abstract": node.get("Abstract") == "True",
                    "interaction": node.findtext("interactionCellOffset"),
                    "hasInteraction": node.findtext("hasInteractionCell"),
                }
                for handle in filter(None, [node.findtext("defName"), node.get("Name")]):
                    by_name[handle] = record
                order.append(key)
    return by_name


def over_wall(name: str, sizes: dict) -> bool:
    """Whether the game lets this thing be built into a standing wall.

    **This rule used to be unconditional and it was right until 0.12.99-dev.** The generator threw
    on any furniture cell holding an edifice, so a vent in a wall was a def error. The owner then
    fixed their facility by hand and put **thirteen vents and seven coolers into walls**, which is
    what those things are for -- so the generator learned `canPlaceOverWall` and this rule has to
    learn it too.

    Teaching the rule rather than deleting it: a bench or a bed on a wall cell is still a def error
    and still caught, which is most of what this check was ever for.
    """
    record = sizes.get(name) or {}
    return bool(record.get("overWall"))


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


def adjust_for_rotation(cell, size, rotation):
    """Core's `GenAdj.AdjustForRotation`, which shifts the centre of an even-dimension building.

    **This was missing and it mattered.** A 3x2 comms console at rotation South does NOT occupy
    the two rows north of its position: `size.z % 2 == 0` so Core moves the centre one cell south
    first. Without this the console the owner placed against the viewing glass read as overlapping
    the glass, and the only reason that was caught is that the game had already accepted it.

    Decompiled from the installed 1.6 assembly rather than remembered -- reasoning from memory
    about Core is what produced the wrong answer twice today.
    """
    width, height = size
    if rotation % 2 == 1:
        width, height = height, width
    shift = {0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}[rotation % 4]
    x, z = cell
    if not (size[0] == 1 and size[1] == 1):
        if width % 2 == 0:
            x += shift[0]
        if height % 2 == 0:
            z += shift[1]
    return (x, z), (width, height)


def interaction_cell(cell, offset, rotation):
    """Core's `ThingUtility.InteractionCellWhenAt`: the position plus the offset, rotated."""
    ox, oz = offset
    rotation %= 4
    if rotation == 0:
        dx, dz = ox, oz
    elif rotation == 1:
        dx, dz = oz, -ox
    elif rotation == 2:
        dx, dz = -ox, -oz
    else:
        dx, dz = -oz, ox
    return (cell[0] + dx, cell[1] + dz)


def interaction_of(name: str, sizes: dict):
    """(offset, True) when this def has an interaction cell, else (None, False)."""
    seen = set()
    cursor = name
    offset = None
    has = False
    while cursor and cursor in sizes and cursor not in seen:
        seen.add(cursor)
        record = sizes[cursor]
        if offset is None and record.get("interaction"):
            numbers = re.findall(r"-?\d+", record["interaction"])
            if len(numbers) >= 3:
                offset = (int(numbers[0]), int(numbers[2]))
            elif len(numbers) == 2:
                offset = (int(numbers[0]), int(numbers[1]))
        if record.get("hasInteraction") and record["hasInteraction"].strip().lower() == "true":
            has = True
        cursor = record["parent"]
    return offset, has


def occupied(cell: tuple, rotation: int, size: tuple) -> list:
    """Core's `GenAdj.OccupiedRect`, rotation adjustment included."""
    (cx, cz), (width, height) = adjust_for_rotation(cell, size, rotation)
    min_x = cx - (width - 1) // 2
    min_z = cz - (height - 1) // 2
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
        # **A BENCH WHOSE INTERACTION CELL IS A WALL CAN NEVER BE USED**, and the owner's whole
        # gate saga was a console they could not staff. `IsOperatorOnStation` requires the pawn to
        # stand on exactly that cell, so a layout that puts it in a wall makes the gate
        # unopenable with nothing on screen to explain it.
        offset, has_interaction = interaction_of(thing, sizes)
        if has_interaction and offset is not None:
            spot = interaction_cell(cell, offset, rotation)
            if spot in walls:
                fail("%s: %s at %s has its interaction cell on the wall %s -- nobody can ever "
                     "stand there to use it" % (label, thing, cell, spot))
            elif spot not in interiors:
                fail("%s: %s at %s has its interaction cell at %s, outside every room"
                     % (label, thing, cell, spot))
        for occupied_cell in occupied(cell, rotation, size_of(thing, sizes)):
            if occupied_cell in walls and not over_wall(thing, sizes):
                fail("%s: %s at %s covers the wall cell %s -- the generator throws here"
                     % (label, thing, cell, occupied_cell))
            elif occupied_cell not in interiors and not (
                    over_wall(thing, sizes) and occupied_cell in walls):
                # **A wall-mountable thing ON a wall cell is not "outside a room".** The owner put
                # the freezer's four coolers on the facility's OUTER wall, which is how a freezer
                # is built -- it has to exhaust somewhere that is not the room it is cooling. A
                # perimeter wall cell is in `walls` and never in `interiors`, so the unconditional
                # rule reported seven correct coolers as outside the building.
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
