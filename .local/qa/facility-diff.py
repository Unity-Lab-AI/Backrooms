#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read a live starting facility, diff it against the authored one, and emit the def edit.

Owner direction, 2026-10-05, verbatim: *"as i load up the different scenerios we will be needing to
fix the layout of the starting facilities(i will be manual using pawns to change the layout and fix
some thing, to which you will use the api mod to see what exactly i change/add to the starting
facilities that you will be making standard and default to the starting scenrios so that the
problems like broken conduit lines are repaired by me, then updated to match for the mods defualt
facilities)"*

So the loop is: **the owner fixes it in game, this reads the fix, and the fix becomes the default.**

Why this exists before the launch rather than during it
-------------------------------------------------------
The owner's time in the game is the scarce thing. Working out the cell format, the 1024-cell call
cap and the def shape **while they wait** would spend their session on my homework. The authored
half below is exact and testable offline; only the live read needs the game.

The three starting facilities are **fully authored data**, not procedural output -- rooms,
buildings, doors and conduit runs, all in `RR_Starts.xml`:

    RR_AsyncIndustriesStart   60x60   15 rooms   87 buildings   23 doors   17 conduit runs
    RR_FurnitureStoreStart    50x50    6 rooms   27 buildings    8 doors    5 conduit runs
    RR_SoloGroupStart         60x60    1 room     0 buildings    1 door     0 conduit runs

That is why a hand-fix can become the default at all: there is a single place to write it.

**Blueprints and frames count as the owner's intent.** They said they will move pawns to build, and
construction takes time. Waiting for a conduit to finish before reading it would make the loop as
slow as the building. A blueprint at a cell is a decision already made.

Usage
-----
    python .local/qa/facility-diff.py authored RR_AsyncIndustriesStart
    python .local/qa/facility-diff.py snapshot RR_AsyncIndustriesStart      # game must be running
    python .local/qa/facility-diff.py diff     RR_AsyncIndustriesStart

`snapshot` writes `.local/qa/facility-<defName>.json` and never touches the game. Every bridge call
used here is read-only.

What this loop CAN and CANNOT carry back
----------------------------------------
Read off `RimroomsStartDef` rather than hoped for, because a change the def cannot express is an
hour of the owner's time that cannot be kept.

**Carries:** a new or moved building with its `thing`, `stuff`, `cell` and `rotation`; a conduit
run; a door; an autodoor; a pillar; a battery's starting charge (`batteryFraction`); a generator's
starting fuel (`fuelFraction`); a glazing wall run.

**Does NOT carry, and both need saying before the session rather than after:**

* **A per-cell floor change.** Flooring is `floorTerrain` for the whole facility plus a per-room
  `floor` boolean. There is no per-cell terrain list, so re-flooring one room's corner cannot be
  expressed as data -- it would need a new field.
* **A knocked-through wall.** Walls are generated from the room rectangles, so removing one means
  re-authoring the rooms rather than recording a deletion. The diff will report the wall as
  *authored but absent live*, which is the signal -- the fix is a room edit, not a building edit.
"""
import importlib.util
import io
import json
import os
import re
import socket
import sys
import xml.etree.ElementTree as ET

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")

# `rimworld/get_cells_info` refuses more than 1024 cells per call, so a 44x44 facility is tiled.
# 31x31 = 961 keeps a margin under the cap rather than sitting on it.
TILE = 31

CELL = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def bridge():
    """The live client, IMPORTED rather than copied.

    Its endpoint discovery reads the port and token out of `Player.log`, and a second copy of that
    would drift the first time the log format moved. Standing rule in this repository: import,
    never copy, anything two tools agree about.
    """
    spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- the authored facility
def parse_cell(text):
    match = CELL.search(text or "")
    if match is None:
        return None
    return int(match.group(1)), int(match.group(3))


def authored(def_name):
    """Everything `RR_Starts.xml` says this facility contains, keyed by (x, z)."""
    root = ET.parse(STARTS).getroot()
    chosen = None
    for node in root:
        if (node.findtext("defName") or "") == def_name:
            chosen = node
            break
    if chosen is None:
        raise SystemExit("no start def named %r in RR_Starts.xml" % def_name)

    rooms = []
    node = chosen.find("rooms")
    for li in ([] if node is None else node.findall("li")):
        rooms.append((int(li.findtext("x")), int(li.findtext("z")),
                      int(li.findtext("width")), int(li.findtext("height"))))

    buildings = {}
    node = chosen.find("buildings")
    for li in ([] if node is None else node.findall("li")):
        cell = parse_cell(li.findtext("cell"))
        if cell is None:
            continue
        buildings.setdefault(cell, []).append(li.findtext("thing"))

    doors = set()
    node = chosen.find("doors")
    for li in ([] if node is None else node.findall("li")):
        cell = parse_cell(li.text)
        if cell is not None:
            doors.add(cell)

    # A run is a start cell, a length and an axis. Expanded to cells so a live conduit can be
    # compared against it at all -- the live map has no concept of a run.
    conduits = set()
    runs = []
    node = chosen.find("conduits")
    for li in ([] if node is None else node.findall("li")):
        start = parse_cell(li.findtext("start"))
        length = int(li.findtext("length"))
        along_x = (li.findtext("alongX") or "false").strip().lower() == "true"
        if start is None:
            continue
        runs.append((start, length, along_x))
        for step in range(length):
            conduits.add((start[0] + step, start[1]) if along_x else (start[0], start[1] + step))

    bounds = None
    if rooms:
        x0 = min(r[0] for r in rooms)
        z0 = min(r[1] for r in rooms)
        x1 = max(r[0] + r[2] for r in rooms)
        z1 = max(r[1] + r[3] for r in rooms)
        bounds = (x0, z0, x1 - x0, z1 - z0)

    return {
        "defName": def_name,
        "mapSize": int(chosen.findtext("mapSize") or 0),
        "bounds": bounds,
        "rooms": rooms,
        "buildings": buildings,
        "doors": sorted(doors),
        "conduits": sorted(conduits),
        "runs": runs,
    }


# --------------------------------------------------------------------------- the live facility
def snapshot(def_name):
    plan = authored(def_name)
    if plan["bounds"] is None:
        raise SystemExit("%s authors no rooms, so there is no footprint to read" % def_name)
    x0, z0, width, height = plan["bounds"]
    # One cell of margin: the owner may well build just outside the authored rect, and a fix this
    # tool cannot see is a fix that silently does not ship.
    x0 -= 1
    z0 -= 1
    width += 2
    height += 2

    # **THE AUTHORED COORDINATES ARE NOT THE MAP'S.** `GenStep_Headquarters` offsets the layout
    # onto whatever map the player chose, and the first live run of this tool read 2,116 cells of
    # unexplored mountain because of it. The offset is computed from the game's own arithmetic and
    # then CONFIRMED by probing a distinctive authored building, because a computed offset nobody
    # checks is a silent mis-aim that reports every building as deleted.
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("rr_offset", os.path.join(HERE, "facility-offset.py"))
    _fo = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_fo)
    probe = next((c for c, names in plan["buildings"].items()
                  if "CommsConsole" in names), None)
    off_x, off_z, map_width, note = _fo.live_offset(
        plan, probe_cell=probe, probe_expect="CommsConsole" if probe else None)
    say("  %s" % note)
    if "OFFSET IS WRONG" in note:
        raise SystemExit("refusing to snapshot against an unconfirmed offset")
    x0 += off_x
    z0 += off_z

    client = bridge()
    port, token = client.endpoint()
    tiles = []
    for tx in range(x0, x0 + width, TILE):
        for tz in range(z0, z0 + height, TILE):
            tiles.append((tx, tz, min(TILE, x0 + width - tx), min(TILE, z0 + height - tz)))

    results = []
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=client.TIMEOUT) as sock:
        client.exchange(sock, buf, "session/hello",
                        {"token": token, "client": {"name": client.CLIENT, "version": "1"}})
        for tx, tz, tw, th in tiles:
            say("  reading %2d x %2d at (%d, %d)" % (tw, th, tx, tz))
            results.append(client.exchange(sock, buf, "tools/call", {
                "name": "rimworld/get_cells_info",
                "arguments": {"x": tx, "z": tz, "width": tw, "height": th}}))

    out = os.path.join(HERE, "facility-%s.json" % def_name)
    io.open(out, "w", encoding="utf-8", newline=NL).write(
        json.dumps({"defName": def_name, "rect": [x0, z0, width, height],
                    "offset": [off_x, off_z], "mapWidth": map_width,
                    "tiles": results}, indent=1))
    say("")
    say("wrote %s  (%d tile(s))" % (os.path.relpath(out, REPO).replace(os.sep, "/"), len(results)))
    say("")
    say("Raw keys in the first tile, so the reader below can be aimed exactly rather than guessed:")
    say("  " + json.dumps(shape(results[0]))[:900])
    return 0


def shape(value, depth=0):
    """The structure of a response without its bulk -- keys and types only, two levels deep."""
    if depth > 2:
        return "..."
    if isinstance(value, dict):
        return {k: shape(v, depth + 1) for k, v in list(value.items())[:12]}
    if isinstance(value, list):
        return [shape(value[0], depth + 1), "...x%d" % len(value)] if value else []
    return type(value).__name__


def live_cells(payload):
    """Every (x, z) -> the things standing there, plus the terrain under them.

    **The field names are measured, not guessed.** The first live run printed the response shape
    and it is `cells[]` with `x`, `z`, `terrainDefName`, `roofDefName` and a `things[]` whose
    entries carry `defName`, `label`, `className`, `stuffDefName`, `isBlueprint`, `isFrame` and
    `hitPoints`.

    **`stuffDefName` is present and that matters more than it looks** -- the owner's fix included
    *"added and removed some walls(granite and steel)"*, and a granite wall written back as a
    steel one is a wrong default that looks right.

    **Rotation is NOT in this response.** It is emitted as 0 and the diff says so out loud, rather
    than silently shipping a bench facing the wrong way. Anything directional is confirmed by eye
    before it ships.

    Blueprints and frames are kept and marked: they are a decision already made, and waiting for
    construction would make this loop as slow as building.
    """
    found = {}
    terrain = {}
    for tile in payload:
        for cell in (tile.get("cells") or []):
            x, z = cell.get("x"), cell.get("z")
            if not isinstance(x, int) or not isinstance(z, int):
                continue
            terrain[(x, z)] = cell.get("terrainDefName")
            for thing in (cell.get("things") or []):
                if not isinstance(thing, dict):
                    continue
                name = thing.get("defName")
                if not name:
                    continue
                kind = "thing"
                if thing.get("isBlueprint") or thing.get("isBlueprintBuild"):
                    kind = "blueprint"
                    name = thing.get("blueprintBuildDefName") or name
                elif thing.get("isFrame"):
                    kind = "frame"
                    name = thing.get("frameBuildDefName") or name
                found.setdefault((x, z), []).append({
                    "thing": str(name),
                    "stuff": thing.get("stuffDefName"),
                    "rotation": None,
                    "label": thing.get("label"),
                    "className": thing.get("className"),
                    "kind": kind,
                })
    return found, terrain


# Natural rock and terrain this facility sits in. Not things the owner placed, and listing them as
# additions would bury the real diff in two thousand lines of mountain.
NATURAL = re.compile(r"^(Mineable|Sandstone|Granite|Limestone|Marble|Slate|Steel$)|Rock$|"
                     r"^(Plant_|Filth_|Chunk|Rubble)")


TRANSMITTER = ("PowerConduit", "HiddenConduit")


def diff(def_name):
    path = os.path.join(HERE, "facility-%s.json" % def_name)
    if not os.path.isfile(path):
        raise SystemExit("no snapshot yet; run:  python .local/qa/facility-diff.py snapshot %s"
                         % def_name)
    saved = json.load(io.open(path, encoding="utf-8-sig"))
    plan = authored(def_name)
    live, terrain = live_cells(saved["tiles"])
    # Back into authored coordinates, so the emitted XML is in the same frame as the file it is
    # pasted into. Without this every cell would be 120 off and the def would place the facility
    # outside its own rooms.
    off_x, off_z = saved.get("offset") or [0, 0]
    live = {(x - off_x, z - off_z): v for (x, z), v in live.items()}
    terrain = {(x - off_x, z - off_z): v for (x, z), v in terrain.items()}
    say("  offset applied : (%d, %d) on a %s-wide map"
        % (off_x, off_z, saved.get("mapWidth", "?")))
    if not live:
        say("THE SNAPSHOT PARSED TO ZERO CELLS. That is a reader fault, not an empty facility -- "
            "the bridge's response shape is not one `live_cells` walks. Run `snapshot` again and "
            "read the printed key shape; aiming the reader is a one-line change.")
        return 1

    live_conduit = {c for c, items in live.items()
                    if any(i["thing"] in TRANSMITTER for i in items)}
    live_things = {c: [i for i in items
                       if i["thing"] not in TRANSMITTER and not NATURAL.match(i["thing"])]
                   for c, items in live.items()}
    live_things = {c: v for c, v in live_things.items() if v}

    added_conduit = sorted(live_conduit - set(plan["conduits"]))
    lost_conduit = sorted(set(plan["conduits"]) - live_conduit)

    authored_things = set(plan["buildings"])
    added_things = sorted(c for c in live_things if c not in authored_things)
    removed_things = sorted(c for c in authored_things if c not in live_things)

    say("facility-diff  %s" % def_name)
    say("  authored   : %d building cell(s), %d conduit cell(s) across %d run(s), %d door(s)"
        % (len(plan["buildings"]), len(plan["conduits"]), len(plan["runs"]), len(plan["doors"])))
    say("  live       : %d cell(s) with things, %d carrying a transmitter"
        % (len(live_things), len(live_conduit)))
    say("")
    say("  ADDED conduit cells (the owner's repair)   : %d" % len(added_conduit))
    say("  conduit cells authored but NOT live        : %d" % len(lost_conduit))
    say("  ADDED thing cells                          : %d" % len(added_things))
    say("  authored thing cells with nothing live     : %d" % len(removed_things))
    say("")

    if added_conduit:
        say("  --- paste into <conduits> of %s ---" % def_name)
        for start, length, along_x in compress(added_conduit):
            say("    <li><start>(%d, 0, %d)</start><length>%d</length><alongX>%s</alongX></li>"
                % (start[0], start[1], length, "true" if along_x else "false"))
        say("")
    if added_things:
        say("  --- paste into <buildings> of %s ---" % def_name)
        for cell in added_things:
            for item in live_things[cell]:
                parts = ["<thing>%s</thing>" % item["thing"]]
                if item.get("stuff"):
                    parts.append("<stuff>%s</stuff>" % item["stuff"])
                parts.append("<cell>(%d, 0, %d)</cell>" % (cell[0], cell[1]))
                parts.append("<rotation>%d</rotation>"
                             % (item["rotation"] if isinstance(item.get("rotation"), int) else 0))
                mark = "" if item["kind"] == "thing" else "   <!-- %s, not built yet -->" % item["kind"]
                say("    <li>%s</li>%s" % ("".join(parts), mark))
        missing_rot = [i for c in added_things for i in live_things[c]
                       if not isinstance(i.get("rotation"), int)]
        if missing_rot:
            say("      NOTE: %d entry/entries came back with no rotation, so they are emitted as 0. "
                "Check any directional thing -- a bed, a door, a bench -- before this ships."
                % len(missing_rot))
        say("")
    if removed_things:
        say("  --- authored but absent live, first 20 (deleted by the owner, or never spawned) ---")
        for cell in removed_things[:20]:
            say("    (%d, 0, %d)  authored: %s"
                % (cell[0], cell[1], ", ".join(plan["buildings"][cell])))
        say("")
    if not (added_conduit or added_things or removed_things):
        say("  NO DIFFERENCE. The live facility matches what is authored.")
    return 0


def compress(cells):
    """Turn loose cells back into runs, because `<conduits>` is authored as runs and not as cells.

    Greedy along x first, then z. A run is how the def expresses it, so emitting 42 single-cell
    entries where the file holds one run of 42 would be correct data in a form nobody can read.
    """
    remaining = set(cells)
    runs = []
    for cell in sorted(remaining):
        if cell not in remaining:
            continue
        length = 1
        while (cell[0] + length, cell[1]) in remaining:
            length += 1
        if length > 1:
            for step in range(length):
                remaining.discard((cell[0] + step, cell[1]))
            runs.append((cell, length, True))
            continue
        length = 1
        while (cell[0], cell[1] + length) in remaining:
            length += 1
        for step in range(length):
            remaining.discard((cell[0], cell[1] + step))
        runs.append((cell, length, length == 1 or False))
    return runs


# --------------------------------------------------------------------------- power connectivity
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"


def power_roles():
    """Every ThingDef the installed game ships, split into what draws power and what carries it.

    Read out of the game's own `Data` folders rather than from a list here, for the reason every
    other lookup in this project is: a hand-kept list of powered buildings is wrong the moment
    Ludeon ships one more. `basePowerConsumption` above zero draws; below zero generates;
    `transmitsPower` carries.
    """
    import glob
    draws, carries, generates = set(), set(), set()
    for path in glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root:
            name = node.findtext("defName")
            if not name:
                continue
            for comp in node.iter():
                if comp.get("Class") not in ("CompProperties_Power",):
                    continue
                if (comp.findtext("transmitsPower") or "").strip().lower() == "true":
                    carries.add(name)
                raw = comp.findtext("basePowerConsumption")
                if raw:
                    try:
                        value = float(raw)
                    except ValueError:
                        continue
                    if value > 0:
                        draws.add(name)
                    elif value < 0:
                        generates.add(name)
    return draws, carries, generates


def power(def_name):
    """Is every powered building in the authored facility actually on the grid?

    **This is the owner's reported problem, checked before they spend a session on it:** *"problems
    like broken conduit lines are repaired by me"*. A conduit run that stops two cells short of a
    wing leaves that wing dark, and nothing in the build refuses it, because the runs are authored
    data and no instrument has ever read them as a network.

    The adjacency used is deliberately **generous** -- a consumer counts as connected if a
    transmitter sits on any of its own cells or any of the eight around it, and transmitters link
    cardinally. Generous is the right direction for a pre-flight check: a false alarm costs a
    glance, and a missed break costs the owner's time in game.
    """
    plan = authored(def_name)
    if not os.path.isdir(GAME_DATA):
        say("the game's Data folder is not here, so powered buildings cannot be identified; "
            "this is skipped rather than passed")
        return 2
    draws, carries, generates = power_roles()

    transmitters = set(plan["conduits"])
    sources = []
    consumers = []
    for cell, names in plan["buildings"].items():
        for name in names:
            if name in carries or name in generates:
                transmitters.add(cell)
            if name in generates:
                sources.append((cell, name))
            elif name in draws:
                consumers.append((cell, name))

    # Union-find over transmitter cells, linked cardinally.
    parent = {c: c for c in transmitters}

    def root(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]
            c = parent[c]
        return c

    for (x, z) in list(transmitters):
        for nx, nz in ((x + 1, z), (x, z + 1)):
            if (nx, nz) in parent:
                a, b = root((x, z)), root((nx, nz))
                if a != b:
                    parent[a] = b

    def attached(cell):
        x, z = cell
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if (x + dx, z + dz) in parent:
                    return root((x + dx, z + dz))
        return None

    powered_nets = {attached(c) for c, _ in sources} - {None}
    orphans = []
    unpowered_nets = []
    for cell, name in consumers:
        net = attached(cell)
        if net is None:
            orphans.append((cell, name, "no transmitter within one cell"))
        elif net not in powered_nets:
            unpowered_nets.append((cell, name, "on a grid with no generator on it"))

    say("facility power  %s" % def_name)
    say("  powered building defs known from the game : %d draw, %d transmit, %d generate"
        % (len(draws), len(carries), len(generates)))
    say("  authored transmitter cells                : %d" % len(transmitters))
    say("  separate grids                            : %d" % len({root(c) for c in parent}))
    say("  generators / batteries                    : %d" % len(sources))
    say("  power-drawing buildings                   : %d" % len(consumers))
    say("")
    if not sources:
        say("  NOTE: this facility authors no generator at all, so every consumer reads as "
            "unpowered. That is the design for a start meant to begin dark -- check the start's "
            "own intent before treating it as a fault.")
    problems = orphans + unpowered_nets
    if not problems:
        say("  EVERY powered building is on a grid that has a generator on it.")
        return 0
    say("  %d POWERED BUILDING(S) ARE NOT CONNECTED:" % len(problems))
    for cell, name, why in problems:
        say("    (%d, 0, %d)  %-32s %s" % (cell[0], cell[1], name, why))
    say("")
    say("      Each is a cell the owner would otherwise have to find by looking at a dark "
        "building in game. Fixing the authored run is cheaper than fixing it twice.")
    return 1


def main(argv):
    if len(argv) >= 3 and argv[1] == "power":
        return power(argv[2])
    if len(argv) < 3 or argv[1] not in ("authored", "snapshot", "diff"):
        say(__doc__.strip().split("Usage")[-1])
        return 1
    mode, def_name = argv[1], argv[2]
    if mode == "authored":
        plan = authored(def_name)
        say("authored  %s" % def_name)
        say("  map size        : %d" % plan["mapSize"])
        say("  footprint       : %s" % (plan["bounds"],))
        say("  rooms           : %d" % len(plan["rooms"]))
        say("  building cells  : %d" % len(plan["buildings"]))
        say("  doors           : %d" % len(plan["doors"]))
        say("  conduit runs    : %d, covering %d cell(s)"
            % (len(plan["runs"]), len(plan["conduits"])))
        overlap = [c for c in plan["buildings"] if c in set(plan["conduits"])]
        say("  cells where a building sits on an authored conduit : %d" % len(overlap))
        return 0
    if mode == "snapshot":
        return snapshot(def_name)
    return diff(def_name)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
