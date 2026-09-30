# -*- coding: utf-8 -*-
"""Validate every start's headquarters geometry without launching the game.

The property this exists for
----------------------------
`GenStep_Headquarters` builds a start's layout by throwing on anything it does not like:

    "Headquarters wall intersects generated structure at ..."
    "Headquarters door has no generated wall at ..."
    "Invalid headquarters room rectangle."

Every one of those is a **new-game crash**, and none of them is visible to the compiler, to any
checker, or to a reading of the XML. The numbers look fine right up until a player picks the
scenario.

Worse than a crash is the one that does not throw: **a room with no way into it**. The map
generates, the colony starts, and a third of the shop is simply sealed. Nothing reports that
ever, so this flood-fills from the arrival cell and insists every room interior is reachable.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def cell(text):
    numbers = re.findall(r"-?\d+", text or "")
    return (int(numbers[0]), int(numbers[2])) if len(numbers) >= 3 else None


# --------------------------------------------------------------------------- Core building sizes
sizes = {}
for path in glob.glob(os.path.join(GAME, "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        continue
    for node in root.iter("ThingDef"):
        name = node.findtext("defName")
        raw = node.findtext("size")
        if not name:
            continue
        if raw:
            numbers = re.findall(r"\d+", raw)
            if len(numbers) >= 2:
                sizes[name.strip()] = (int(numbers[0]), int(numbers[1]))
        else:
            sizes.setdefault(name.strip(), (1, 1))

# --------------------------------------------------------------------------- our starts
starts = []
for path in glob.glob(os.path.join(MOD, "Defs", "RimroomsStartDefs", "*.xml")):
    for node in ET.parse(path).getroot():
        if not node.tag.endswith("RimroomsStartDef"):
            continue
        rooms = []
        for room in (node.find("rooms") or []):
            rooms.append((int(room.findtext("x")), int(room.findtext("z")),
                          int(room.findtext("width")), int(room.findtext("height"))))
        doors = [cell(li.text) for li in (node.find("doors") or [])]
        buildings = []
        for plan in (node.find("buildings") or []):
            buildings.append((plan.findtext("thing"), cell(plan.findtext("cell"))))
        starts.append({
            "defName": node.findtext("defName"),
            "mapSize": int(node.findtext("mapSize") or "60"),
            "rooms": rooms,
            "doors": doors,
            "buildings": buildings,
            "arrival": cell(node.findtext("arrivalCell")),
            "stock": cell(node.findtext("stockCell")),
            "roles": len(node.find("roles") or []),
            "projects": [li.text.strip() for li in (node.find("completedProjects") or []) if li.text],
            "contact": (node.findtext("beginsInCorporationContact") or "false").strip().lower(),
            "inside": (node.findtext("insideStart") or "false").strip().lower() == "true",
            "generator": (node.findtext("mapGenerator") or "").strip(),
            "conduits": len(node.find("conduits") or []),
            "exitDoor": cell(node.findtext("emergenceDoorCell")),
        })

projects_available = set()
for path in glob.glob(os.path.join(MOD, "Defs", "RimroomsProjectDefs", "*.xml")):
    for node in ET.parse(path).getroot():
        name = node.findtext("defName")
        if name:
            projects_available.add(name.strip())

generators = {}
for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root.iter("MapGeneratorDef"):
        name = node.findtext("defName")
        if name:
            generators[name.strip()] = [li.text.strip() for li in (node.find("genSteps") or []) if li.text]
    for node in root.iter("GenStepDef"):
        name = node.findtext("defName")
        step = node.find("genStep")
        if name and step is not None:
            generators.setdefault("genstep:" + name.strip(), [step.get("Class") or ""])

SRC = os.path.join(REPO, "src")
source_text = ""
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    source_text += io.open(path, encoding="utf-8-sig").read()

print("starts          : %d" % len(starts))
print("core sizes known: %d" % len(sizes))
print("")

check("the mod ships more than one start", len(starts) > 1,
      "-- the campaign chart names three")

for start in starts:
    name = start["defName"]
    size = start["mapSize"]
    print("  --- %s (%dx%d, %d rooms, %d doors) ---" % (name, size, size,
                                                        len(start["rooms"]), len(start["doors"])))

    # **REVERSED at 0.12.46-dev, and the old wording shows why it was wrong.** This used to
    # require every start to name a generator this package ships, and called Core falling back
    # to *"an ordinary colony map"* the failure. An ordinary colony map for the tile the player
    # chose is exactly what they want -- owner direction: **"the map generator is not our mod"**.
    #
    # Replacing Core's `Base_Player` gave a flat-Soil map with a building on it, with no rock, no
    # plants and no biome character, and **Map Preview simulates the real generator**, so the
    # preview a player rerolled against was a picture of a map the mod discarded.
    #
    # So the claim is now the opposite: **no start may name a generator at all.**
    check("%s names NO map generator, so Core generates the tile" % name,
          not start["generator"],
          "-- it names '%s'. Core's Base_Player runs the whole chain -- elevation, fertility, "
          "biome terrain, caves, rocks, plants, animals, ruins, rivers, roads -- and the "
          "facility is added onto it by gen steps patched into that generator"
          % start["generator"])
    for step in generators.get(start["generator"], []):
        cls = generators.get("genstep:" + step, [""])[0]
        short = cls.split(".")[-1] if cls else ""
        if not short:
            continue
        check("%s genstep %s resolves to a real class" % (name, step),
              ("class " + short) in source_text,
              "-- named in XML, defined nowhere; the step silently does nothing")

    # An inside start's people begin in a coordinate generated BESIDE the surface map, so it has
    # an ordinary layout like the others -- just a very small one -- and it additionally has to
    # name which of its own doors is the way out.
    if start["inside"]:
        check("%s names an emergence door" % name, start["exitDoor"] is not None,
              "-- nothing to mark, so the start would have no registered exit at all")
        check("%s emergence door is one of its own doors" % name,
              start["exitDoor"] in start["doors"],
              "-- no door is generated at %s, so there is nothing to mark"
              % str(start["exitDoor"]))

    # Walls, and interiors, exactly as the generator lays them.
    #    The first version of the wall rule asserted that a room's wall must not land inside
    #    another room's interior, and it failed on a layout that is correct -- an interior room
    #    inside an outer shell, which is how the Async headquarters has always been built. THE
    #    ASSERTION WAS WRONG (invariant 130). `GenStep_Headquarters` throws only when a wall
    #    lands where an EDIFICE already is, and an interior cell has none. The real rule is that
    #    two rooms must not share a wall CELL.
    walls, interior, floors = set(), set(), set()
    overlap_fault = []
    for (x, z, w, h) in start["rooms"]:
        check("%s room %d,%d is at least 3x3" % (name, x, z), w >= 3 and h >= 3)
        check("%s room %d,%d fits the map" % (name, x, z),
              0 <= x and 0 <= z and x + w - 1 < size and z + h - 1 < size,
              "-- spans to %d,%d on a %d-wide map" % (x + w - 1, z + h - 1, size))
        for cx in range(x, x + w):
            for cz in range(z, z + h):
                edge = cx in (x, x + w - 1) or cz in (z, z + h - 1)
                if edge:
                    # Wall on wall is the collision the generator actually throws on.
                    if (cx, cz) in walls:
                        overlap_fault.append((cx, cz))
                    walls.add((cx, cz))
                else:
                    interior.add((cx, cz))
                floors.add((cx, cz))

    check("%s has no two rooms sharing a wall cell" % name, not overlap_fault,
          "-- generator throws at " + str(sorted(set(overlap_fault))[:4]))

    # Doors must replace a wall the generator actually built.
    for door in start["doors"]:
        check("%s door %s sits on a wall" % (name, str(door)), door in walls,
              "-- generator throws: door has no generated wall here")

    open_cells = (interior | set(start["doors"])) - (walls - set(start["doors"]))

    # Buildings must not sit on a wall, and must not sit on each other.
    taken = {}
    for thing, origin in start["buildings"]:
        sx, sz = sizes.get(thing, (1, 1))
        minx = origin[0] - (sx - 1) // 2
        minz = origin[1] - (sz - 1) // 2
        for cx in range(minx, minx + sx):
            for cz in range(minz, minz + sz):
                if (cx, cz) in walls:
                    check("%s %s at %s clears the walls" % (name, thing, str(origin)), False,
                          "-- occupies wall cell %d,%d; the generator throws" % (cx, cz))
                if (cx, cz) in taken:
                    check("%s %s at %s does not overlap %s"
                          % (name, thing, str(origin), taken[(cx, cz)]), False,
                          "-- both claim %d,%d" % (cx, cz))
                taken[(cx, cz)] = thing
    check("%s building placements are clear of walls and each other" % name,
          not any(f.startswith("%s " % name) and ("clears the walls" in f or "does not overlap" in f)
                  for f in failures))

    # Arrival and stock must be somewhere a pawn and a crate can actually be.
    check("%s arrival cell is inside a room" % name, start["arrival"] in interior,
          "-- %s is a wall or open ground" % str(start["arrival"]))
    check("%s stock cell is inside a room" % name, start["stock"] in interior,
          "-- %s is a wall or open ground" % str(start["stock"]))

    # THE ONE THAT DOES NOT THROW. Flood fill and insist every room interior is reachable.
    seen = set()
    queue = deque()
    if start["arrival"] in open_cells:
        queue.append(start["arrival"])
        seen.add(start["arrival"])
    while queue:
        cx, cz = queue.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (cx + dx, cz + dz)
            if nxt in seen or not (0 <= nxt[0] < size and 0 <= nxt[1] < size):
                continue
            if nxt in walls and nxt not in start["doors"]:
                continue
            if nxt not in floors and nxt not in start["doors"]:
                # Outside every rectangle is open ground; it is walkable and worth crossing.
                seen.add(nxt)
                queue.append(nxt)
                continue
            seen.add(nxt)
            queue.append(nxt)

    for (x, z, w, h) in start["rooms"]:
        if w < 3 or h < 3:
            continue
        inner = {(cx, cz) for cx in range(x + 1, x + w - 1) for cz in range(z + 1, z + h - 1)}
        check("%s room %d,%d is reachable from the arrival cell" % (name, x, z),
              bool(inner & seen),
              "-- SEALED. The map generates and the room can never be entered")

    # A start declares only what begins finished, and a name that matches no project is a
    # silent skip at runtime: the player is quietly given less than the scenario claims.
    for project in start["projects"]:
        check("%s starting project %s exists" % (name, project), project in projects_available,
              "-- skipped at runtime, so the start silently grants less than it says")

    check("%s declares between one and five roles (%d)" % (name, start["roles"]),
          1 <= start["roles"] <= 5)
    print("")

# The chart's rule: exactly one start opens in corporation contact, and the other two have to
# earn it. If a new start ever ships already in contact, the clean-up team and the courier come
# with it, and the absence that makes those openings frightening is gone.
in_contact = [s["defName"] for s in starts if s["contact"] == "true"]
check("exactly one start begins in corporation contact (%d)" % len(in_contact),
      len(in_contact) == 1, "-- in contact: " + ", ".join(in_contact))
check("the start in contact is Async Industries",
      in_contact == ["RR_AsyncIndustriesStart"] if in_contact else False)

# And the one in contact is the only one that begins with research finished.
for start in starts:
    if start["contact"] != "true":
        check("%s begins with no research finished" % start["defName"], not start["projects"],
              "-- a start without a corporation behind it has not been taught anything")

# --------------------------------------------------------------------------- the solo opening
# The guaranteed exit. Owner: "needs to 100% have a exit to map natural portal on their first
# backrroms level". A survey draw cannot deliver a guarantee, so the opening registers the
# connection directly -- and the ORDER of its steps is the safety of it.
OPENING = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario", "SoloGroupOpening.cs")
if os.path.isfile(OPENING):
    opening = io.open(OPENING, encoding="utf-8-sig").read()
    print("")
    i_site = opening.find("DestinationService.EnsureSite(")
    i_mark = opening.find("anchor.Mark()")
    i_reg = opening.find("PortalAddressService.RegisterEmergenceAddress(")
    i_move = opening.find("MoveOpeningPartyInside(")

    check("the opening generates a real coordinate", i_site != -1,
          "-- without a RimroomsDestinationMapParent no connection can ever be registered")
    check("the opening marks the surface door", i_mark != -1,
          "-- the network refuses an Emergence endpoint that is not marked")
    check("the opening registers the way out", i_reg != -1,
          "-- the exit would not exist, which is the one thing the direction requires at 100%")
    check("the opening moves the party inside", i_move != -1,
          "-- they would start on the surface, not in the Backrooms")

    # THE claim. Registering before moving means a failure anywhere above leaves everybody
    # standing safely on the surface. Moving first would seal a group inside a coordinate with
    # no registered way out, which is the exact trap invariant 28 forbids.
    check("the way out is registered BEFORE anybody is moved inside",
          i_reg != -1 and i_move != -1 and i_reg < i_move,
          "-- a failure would seal the group inside with no registered exit")
    check("the door is marked before the connection is registered",
          i_mark != -1 and i_reg != -1 and i_mark < i_reg,
          "-- the network would refuse an unmarked Emergence endpoint")

# --------------------------------------------------------------------------- the natural chain
# Owner direction: "with natural portals deeper to an extent till they would need to buidl theri
# own gate", and the extent chosen at the fork was through depth 3.
FRONTIER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                        "NaturalFrontierService.cs")
frontier = io.open(FRONTIER, encoding="utf-8-sig").read()

print("")
cap = re.search(r"MaximumNaturalDepth\s*=\s*(\d+)", frontier)
check("the natural chain has a declared depth limit", cap is not None,
      "-- without one the Backrooms hands out free doorways forever and no gate is ever needed")
if cap:
    check("the natural depth limit is 3 (%s)" % cap.group(1), cap.group(1) == "3",
          "-- the owner chose through depth 3 at the fork")

# THE one that matters. The cap must be applied AFTER the way-out attempt, or a crew standing at
# the deepest natural band can never find a door home and the band becomes a trap. Invariant 28
# forbids an unavoidable failure, and this is exactly the shape one would take.
#    Keyed off the REFUSAL rather than off a comparison expression. The first version matched
#    the literal text "depth > MaximumNaturalDepth", which meant renaming the variable made the
#    claim fail OPEN -- it reported a failure for the wrong reason and would have reported a pass
#    for a genuinely reordered cap that used a different variable name. The refusal key is the
#    thing that actually happens and cannot be renamed without the keyed string moving too.
wayout = frontier.find("TryRecordWayOut(")
capcheck = frontier.find('Refused("RR_Frontier_BeyondNaturalReach")')
check("the depth cap refusal exists", capcheck != -1,
      "-- nothing stops the natural chain, so free doorways go on forever")
check("the way-out attempt runs before the depth cap",
      wayout != -1 and capcheck != -1 and wayout < capcheck,
      "-- the deepest natural band would become a trap with no door home")

# A refusal a player reads must be a real string, or they see the raw key.
KEYED = os.path.join(MOD, "Languages", "English", "Keyed")
keyed_text = ""
for path in glob.glob(os.path.join(KEYED, "*.xml")):
    keyed_text += io.open(path, encoding="utf-8-sig").read()
for key in sorted(set(re.findall(r'Refused\("(RR_Frontier_\w+)"\)', frontier))):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed_text,
          "-- the player would be shown the raw key")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every start's layout builds, and no room is sealed")
