# -*- coding: utf-8 -*-
"""What the owner changed in the live facility, classified so the report is readable.

**The raw diff was unreadable and that was the point of writing this.** `facility-diff.py diff`
reported **647 added thing cells**, because the generator makes every room rectangle's edge into a
`Wall` and those walls are not in `<buildings>` -- so every wall that was always there looked new.
A report nobody can read is a report that gets skimmed, and the owner said their placements are
*"exact and purposfully"*.

So the authored wall set is reconstructed from the same rule the generator uses, read out of
`HeadquartersBuilder.Build`:

    foreach room: foreach cell in room.Rect:
        edge = cell.x == minX || cell.x == maxX || cell.z == minZ || cell.z == maxZ
        if edge: spawn Wall of start.wallStuff          // BlocksGranite
    foreach pillars: spawn Wall of start.wallStuff

Doors, autodoors and glazing runs replace a wall on their cell, so they are removed from the set.

Then every live cell falls into exactly one bucket:

  * **wall kept**        an authored wall cell holding a wall of the authored material
  * **wall re-materialled** an authored wall cell holding a wall of a DIFFERENT material
  * **wall added**       a wall where the layout authored none
  * **wall removed**     an authored wall cell holding no wall and no door
  * **thing added**      anything else the `<buildings>` list does not place
  * **thing missing**    an authored building with nothing live on its cell

That last bucket is the one to read carefully: it is both *the owner deleted it* and *it never
spawned*, and the two need different fixes.
"""
import importlib.util
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")

DOORS = ("Door", "Autodoor")
DEF_INDEX = os.path.join(HERE, "def-index.json")


def def_index():
    """defName -> {category, size}, built from the game's and this mod's own ThingDefs.

    **Two filters depend on this and the raw report was unreadable without either.**

    * **Only `category == Building` is layout.** The first report listed `Steel`, `WoodLog`,
      `ComponentSpacer`, `Gun_ChargeRifle`, `MealSurvivalPack` and three `Human` as things the
      owner *added* -- they are the starting stock and the colonists standing on it.
    * **A multi-cell building occupies more than its authored cell.** `CommsConsole` is 3x2, so a
      console authored at one cell showed its other five as additions. Same for every generator,
      bench, bed and shelf.

    **Built preferring `ThingDef` over any other def type sharing the name**, because a `PrefabDef`
    called `Shelf` overwrote the real one and left it categoryless with a prefab's footprint.
    Category and size are inherited up `ParentName`, which is how `Wall` gets `Building` at all.
    """
    if not os.path.isfile(DEF_INDEX):
        raise SystemExit("def-index.json is missing; it is built from the game's Data folders")
    return json.load(io.open(DEF_INDEX, encoding="utf-8-sig"))


def footprint(cell, def_name, rotation, index):
    """Every cell a building of this def occupies when placed at `cell`.

    RimWorld anchors a multi-cell building at its CENTRE, so the occupied rect runs from
    `cell - (size-1)/2` to that plus size. A non-square footprint swaps its axes on an odd
    rotation, which is why rotation is read rather than ignored.
    """
    record = index.get(def_name) or {}
    size = record.get("size")
    if not size:
        return {cell}
    match = re.match(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", size)
    if match is None:
        return {cell}
    width, height = int(match.group(1)), int(match.group(2))
    if (rotation or 0) % 2 == 1:
        width, height = height, width
    x0 = cell[0] - (width - 1) // 2
    z0 = cell[1] - (height - 1) // 2
    return {(x0 + dx, z0 + dz) for dx in range(width) for dz in range(height)}
NATURAL = re.compile(r"^(Mineable|Sandstone|Granite|Limestone|Marble|Slate)|Rock$|"
                     r"^(Plant_|Filth_|Chunk|Rubble|SteamGeyser)")
TRANSMITTER = ("PowerConduit", "HiddenConduit")


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


def authored_walls(def_name):
    """Every cell the generator puts a wall on, and the material it uses."""
    root = ET.parse(STARTS).getroot()
    node = next((n for n in root if (n.findtext("defName") or "") == def_name), None)
    if node is None:
        raise SystemExit("no start def named %r" % def_name)
    stuff = (node.findtext("wallStuff") or "").strip() or None

    def cells_of(tag):
        out = set()
        block = node.find(tag)
        for li in ([] if block is None else block.findall("li")):
            text = li.text if li.text and li.text.strip() else li.findtext("start")
            match = re.search(r"\(\s*(-?\d+)\s*,\s*-?\d+\s*,\s*(-?\d+)\s*\)", text or "")
            if match is None:
                continue
            x, z = int(match.group(1)), int(match.group(2))
            length = li.findtext("length")
            if length:
                along = (li.findtext("alongX") or "false").strip().lower() == "true"
                for step in range(int(length)):
                    out.add((x + step, z) if along else (x, z + step))
            else:
                out.add((x, z))
        return out

    walls = set()
    block = node.find("rooms")
    for li in ([] if block is None else block.findall("li")):
        x0, z0 = int(li.findtext("x")), int(li.findtext("z"))
        w, h = int(li.findtext("width")), int(li.findtext("height"))
        x1, z1 = x0 + w - 1, z0 + h - 1
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    walls.add((x, z))
    walls |= cells_of("pillars")
    # A door, an autodoor or a glazing run replaces the wall on its cell.
    openings = cells_of("doors") | cells_of("autodoors") | cells_of("glazing")
    return walls - openings, openings, stuff


def main(argv):
    def_name = argv[1] if len(argv) > 1 else "RR_AsyncIndustriesStart"
    fd = load("fd", os.path.join(HERE, "facility-diff.py"))
    plan = fd.authored(def_name)
    walls, openings, wall_stuff = authored_walls(def_name)

    path = os.path.join(HERE, "facility-%s.json" % def_name)
    if not os.path.isfile(path):
        raise SystemExit("no snapshot; run facility-diff.py snapshot %s first" % def_name)
    saved = json.load(io.open(path, encoding="utf-8-sig"))
    live_raw, terrain_raw = fd.live_cells(saved["tiles"])
    off_x, off_z = saved.get("offset") or [0, 0]
    live = {(x - off_x, z - off_z): v for (x, z), v in live_raw.items()}
    terrain = {(x - off_x, z - off_z): v for (x, z), v in terrain_raw.items()}

    index = def_index()
    authored_things = plan["buildings"]
    # Rotation per authored cell, read from the def rather than assumed zero.
    root = ET.parse(STARTS).getroot()
    node = next(n for n in root if (n.findtext("defName") or "") == def_name)
    rotations = {}
    block = node.find("buildings")
    for li in ([] if block is None else block.findall("li")):
        m = re.search(r"\(\s*(-?\d+)\s*,\s*-?\d+\s*,\s*(-?\d+)\s*\)", li.findtext("cell") or "")
        if m:
            rotations[(int(m.group(1)), int(m.group(2)))] = int(li.findtext("rotation") or 0)
    # Every cell any authored building occupies, mapped back to the def that owns it.
    occupied = {}
    for cell, names in authored_things.items():
        for name in names:
            for covered in footprint(cell, name, rotations.get(cell, 0), index):
                occupied.setdefault(covered, set()).add(name)
    authored_conduit = set(plan["conduits"])

    kept = Counter()
    rematerialled = []
    wall_added = []
    wall_removed = []
    thing_added = defaultdict(list)
    conduit_added = set()
    conduit_missing = set()
    live_conduit = set()

    for cell, items in live.items():
        for item in items:
            name = item["thing"]
            if NATURAL.match(name):
                continue
            if name in TRANSMITTER:
                live_conduit.add(cell)
                continue
            if name == "Wall":
                if cell in walls:
                    if wall_stuff and item["stuff"] and item["stuff"] != wall_stuff:
                        rematerialled.append((cell, item["stuff"]))
                    else:
                        kept["wall"] += 1
                else:
                    wall_added.append((cell, item["stuff"], item["kind"]))
                continue
            if name in DOORS:
                if cell not in openings:
                    thing_added[name].append((cell, item["stuff"], item["kind"]))
                else:
                    kept["door"] += 1
                continue
            if (index.get(name) or {}).get("category") != "Building":
                # Stock on the floor and colonists standing on it are not layout.
                kept["not layout"] += 1
                continue
            if name in (occupied.get(cell) or set()):
                kept["authored thing"] += 1
            else:
                thing_added[name].append((cell, item["stuff"], item["kind"]))

    for cell in walls:
        items = live.get(cell) or []
        if not any(i["thing"] == "Wall" or i["thing"] in DOORS for i in items):
            if cell in terrain:
                wall_removed.append(cell)

    conduit_added = live_conduit - authored_conduit
    conduit_missing = authored_conduit - live_conduit
    # An authored building counts as present if it is anywhere in its own footprint, because a
    # multi-cell thing reports from whichever cells the read walked.
    thing_missing = []
    for c, names in authored_things.items():
        if c not in terrain:
            continue
        for name in names:
            cells = footprint(c, name, rotations.get(c, 0), index)
            if not any(any(i["thing"] == name for i in (live.get(k) or [])) for k in cells):
                thing_missing.append((c, name))

    say("facility-changes  %s" % def_name)
    say("  offset (%d, %d) on a %s-wide map; %d live cell(s) read"
        % (off_x, off_z, saved.get("mapWidth", "?"), len(live)))
    say("  authored wall cells %d (material %s), openings %d"
        % (len(walls), wall_stuff, len(openings)))
    say("")
    say("  UNCHANGED      walls %d, doors %d, authored things %d"
        % (kept["wall"], kept["door"], kept["authored thing"]))
    say("  NOT LAYOUT     %d cell-thing(s): stock, items and pawns" % kept["not layout"])
    say("")
    say("  WALLS ADDED            : %d" % len(wall_added))
    say("  WALLS REMOVED          : %d" % len(wall_removed))
    say("  WALLS RE-MATERIALLED   : %d" % len(rematerialled))
    say("  CONDUIT CELLS ADDED    : %d" % len(conduit_added))
    say("  CONDUIT CELLS MISSING  : %d" % len(conduit_missing))
    say("  THINGS ADDED           : %d cell(s), %d kind(s)"
        % (sum(len(v) for v in thing_added.values()), len(thing_added)))
    say("  AUTHORED THINGS ABSENT : %d" % len(thing_missing))
    say("")

    if wall_added:
        by_stuff = Counter(s or "(none)" for _, s, _ in wall_added)
        say("  --- walls the owner added, by material ---")
        for stuff, count in by_stuff.most_common():
            say("      %-22s %d cell(s)" % (stuff, count))
        say("")
    if rematerialled:
        say("  --- walls whose material the owner changed ---")
        for stuff, count in Counter(s for _, s in rematerialled).most_common():
            say("      %-22s %d cell(s)" % (stuff, count))
        say("")
    if thing_added:
        say("  --- things the owner added, by kind ---")
        for name, entries in sorted(thing_added.items(), key=lambda kv: -len(kv[1])):
            marks = Counter(k for _, _, k in entries)
            detail = "" if list(marks) == ["thing"] else "  [%s]" % ", ".join(
                "%d %s" % (n, k) for k, n in marks.items())
            say("      %-30s %3d  %s%s"
                % (name, len(entries),
                   ", ".join("(%d,%d)" % c for c, _, _ in entries[:6])
                   + (" ..." if len(entries) > 6 else ""), detail))
        say("")
    if thing_missing:
        say("  --- authored things that are not there (deleted, or never spawned) ---")
        for cell, name in sorted(thing_missing):
            say("      (%2d, %2d)  %s" % (cell[0], cell[1], name))
        say("")
    if wall_removed:
        say("  --- authored wall cells now open ---")
        say("      " + ", ".join("(%d,%d)" % c for c in sorted(wall_removed)))
        say("")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
