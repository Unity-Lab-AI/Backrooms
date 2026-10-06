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
#
# **AND WHICH OF THEM MOUNT IN A WALL, WHICH THIS PROOF DID NOT KNOW AND THE GENERATOR DID.**
#
# This reported **23 failures** against `RR_AsyncIndustriesStart` -- seven `Cooler` cells and
# sixteen `Vent` cells -- each saying *"occupies wall cell x,z; the generator throws"*. Every one
# was a **false red**, and the authority is the installed game: `Cooler` and `Vent` both declare
# `<canPlaceOverWall>true</canPlaceOverWall>`, which is what lets a player build one into a
# standing wall.
#
# `GenStep_Headquarters` has known this all along and carries the arithmetic: for a thing with that
# flag it **destroys its own wall and continues**, exactly as the game does, and throws for anything
# without it. Its own comment records that these twenty wall cells once threw and why they stopped.
#
# **So the generator and this proof were two derivations of one Core rule, and the proof was the
# stale one.** It now reads the same flag from the same place. A cooler in a wall is a cooler doing
# its job; a bench in a wall is still a def error and still reported.
sizes = {}
over_wall = set()
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
        building = node.find("building")
        if building is not None and (building.findtext("canPlaceOverWall") or "").strip().lower()                 == "true":
            over_wall.add(name.strip())

# --------------------------------------------------------------------------- our starts
starts = []
for path in glob.glob(os.path.join(MOD, "Defs", "RimroomsStartDefs", "*.xml")):
    for node in ET.parse(path).getroot():
        if not node.tag.endswith("RimroomsStartDef"):
            continue
        rooms = []
        for room in (node.find("rooms") or []):
            # The roofed flag comes along now: it is load-bearing for the breezeway, which is
            # the only unroofed room in the facility and the reason the generators can vent.
            rooms.append((int(room.findtext("x")), int(room.findtext("z")),
                          int(room.findtext("width")), int(room.findtext("height")),
                          (room.findtext("roofed") or "true").strip().lower() != "false"))
        doors = [cell(li.text) for li in (node.find("doors") or [])]
        buildings = []
        for plan in (node.find("buildings") or []):
            buildings.append((plan.findtext("thing"), cell(plan.findtext("cell")),
                              int(plan.findtext("rotation") or "0")))
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
    for (x, z, w, h, _roofed) in start["rooms"]:
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

    # **THE PREMISE OF THIS CLAIM WAS FALSE, corrected 0.12.73-dev.** It read *"wall on wall is
    # the collision the generator actually throws on"* and refused any two rooms sharing a wall
    # cell. `Verse.GenSpawn.Spawn`, decompiled from the installed 1.6 assembly, **never throws**:
    # it logs for out-of-bounds or already-spawned and otherwise calls `WipeExistingThings`, and
    # `SpawningWipes(Wall, Wall)` is true, so the second wall simply replaces the first. A wing
    # built against the compound's outer wall is ordinary architecture and the rule forbade it.
    #
    # **This is the third time a claim here has been wrong about its own premise** -- the version
    # before it refused an interior room inside an outer shell (invariant 130), which is how this
    # headquarters has always been built. So the rule is now the one that is actually true and
    # actually harmful, and it is the same rule `tools/check-start-layout.py` enforces: a room's
    # wall must not cross another room's INTERIOR unless it is nested inside it.
    def _contains(outer, inner):
        return (outer[0] <= inner[0] and outer[1] <= inner[1]
                and outer[0] + outer[2] >= inner[0] + inner[2]
                and outer[1] + outer[3] >= inner[1] + inner[3])

    crossing_fault = []
    for outer in start["rooms"]:
        outer_interior = {(cx, cz)
                          for cx in range(outer[0] + 1, outer[0] + outer[2] - 1)
                          for cz in range(outer[1] + 1, outer[1] + outer[3] - 1)}
        for inner in start["rooms"]:
            if inner is outer or _contains(outer, inner):
                continue
            imx, imz = inner[0] + inner[2] - 1, inner[1] + inner[3] - 1
            inner_walls = {(cx, cz)
                           for cx in range(inner[0], imx + 1)
                           for cz in range(inner[1], imz + 1)
                           if cx in (inner[0], imx) or cz in (inner[1], imz)}
            crossing_fault.extend(sorted(inner_walls & outer_interior))

    check("%s has no wall crossing another room's interior" % name, not crossing_fault,
          "-- a wall in the middle of a room at " + str(sorted(set(crossing_fault))[:4]))

    check("%s is re-validated cell by cell by checker sixteen" % name,
          os.path.isfile(os.path.join(REPO, "tools", "check-start-layout.py")),
          "-- `tools/check-start-layout.py` reads the emitted XML and re-derives every door, "
          "glazed cell, footprint and conduit from Core's own sizes. Two readers, and the one "
          "that validates did not author")

    # Doors must replace a wall the generator actually built.
    for door in start["doors"]:
        check("%s door %s sits on a wall" % (name, str(door)), door in walls,
              "-- generator throws: door has no generated wall here")

    open_cells = (interior | set(start["doors"])) - (walls - set(start["doors"]))

    # Buildings must not sit on a wall, and must not sit on each other.
    taken = {}
    for thing, origin, rotation in start["buildings"]:
        sx, sz = sizes.get(thing, (1, 1))
        # **CORE MOVES THE CENTRE OF AN EVEN-DIMENSION BUILDING BEFORE TAKING THE RECT.**
        # `GenAdj.AdjustForRotation`, decompiled from the installed 1.6 assembly: for a rotation
        # other than north it swaps the axes if horizontal and then, if a dimension is even,
        # shifts the centre by one. So a 3x2 comms console facing SOUTH occupies the two rows at
        # and below its position, not above it.
        #
        # **This was the third copy of that rule in this repository** -- checker sixteen and the
        # facility generator had the same gap -- and all three said the owner's console overlapped
        # the viewing glass it is actually sitting against. Three derivations of one Core rule is
        # the defect this project keeps meeting; these are now the same arithmetic in three
        # places, each citing the decompiled source.
        ax, az = origin
        if not (sx == 1 and sz == 1):
            if rotation % 2 == 1:
                sx, sz = sz, sx
            shift = {0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}[rotation % 4]
            if sx % 2 == 0:
                ax += shift[0]
            if sz % 2 == 0:
                az += shift[1]
        minx = ax - (sx - 1) // 2
        minz = az - (sz - 1) // 2
        for cx in range(minx, minx + sx):
            for cz in range(minz, minz + sz):
                if (cx, cz) in walls and thing not in over_wall:
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

    for (x, z, w, h, _roofed) in start["rooms"]:
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
# own gate", and the extent chosen at the fork was through depth 3 -- raised to SIX on
# 2026-09-30, together with the open-map budget that makes a deeper chain affordable.
FRONTIER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                        "NaturalFrontierService.cs")
frontier = io.open(FRONTIER, encoding="utf-8-sig").read()

print("")
cap = re.search(r"MaximumNaturalDepth\s*=\s*(\d+)", frontier)
check("the natural chain has a declared depth limit", cap is not None,
      "-- without one the Backrooms hands out free doorways forever and no gate is ever needed")
if cap:
    # **The owner raised this to six on 2026-09-30**, having chosen three at an earlier fork,
    # alongside the map budget that makes a deeper chain affordable. What is asserted is that the
    # reach is a real, finite, stated number -- not that it is any particular one, because that is
    # the owner's to move and this claim failing for the right reason cost a checkpoint to notice.
    reach = int(cap.group(1))
    check("the natural depth limit is a stated, finite reach (%d)" % reach,
          2 <= reach <= 8,
          "-- a doorway chain has to stop somewhere or the graph is unbounded; the owner sets "
          "where, and it is 6 since 0.12.49-dev")

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

def _rr_read(*parts):
    return io.open(os.path.join(REPO, *parts), encoding="utf-8-sig").read()


services = _rr_read("src", "RimroomsAsyncIndustries", "Company", "CampaignServices.cs")
component = _rr_read("src", "RimroomsAsyncIndustries", "Company", "RimroomsCampaignComponent.cs")
gatecomp = _rr_read("src", "RimroomsAsyncIndustries", "Gate", "CompRimroomsGate.cs")
starts_xml = _rr_read("Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")

# ------------------------------- the corporate start disabled itself on turn one
# Owner: *"it says : Company Records could not be reconsiled blah blah blah.... and none of our
# buttons work"*. `[Rimrooms][Save] Campaign integrity failed` is logged on the line immediately
# before `Initialized ... scenario=async_industries`, because `InitializeBranch` validates the
# records it has just seeded.
#
# `BuildProjectTree` set `insightCommitted = done` and **never set `insightOperationId`**, and
# `ValidateRecordRelationships` requires a committed insight to carry one. So every pre-completed
# project was a save-integrity fault, `stateFaultKey` was set and `CanOperate` went false -- every
# button in the mod refusing. **The corporate start is the only one that names completed
# projects**, so it is the only start this broke, and it broke it from the day it was written.
check("A PRE-COMPLETED PROJECT CARRIES THE RECEIPT ITS COMMITMENT IMPLIES",
      "insightOperationId = done ? projectId + \":insight\" : null," in services
      and "string projectId = branchId + \":project:\" + definition.defName;" in services
      and "insightCommitted = done," in services,
      "-- the validator requires `!insightCommitted || insightOperationId` is non-empty, and this "
      "field was never written. The id is the format `InvestigationServices` uses when the player "
      "commits an insight, built from the record's own id so the two cannot drift")

check("and the validator still refuses a committed insight with no receipt",
      "(!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))" in component,
      "-- the rule was right. **A committed insight with no receipt is exactly the double-payment "
      "hole this check exists for**, so it is the seeding that changed and not the rule")

# **SCOPED TO THE ELEMENT.** `RR_GateTelemetry` also appears in this file's own COMMENT, which
# explains that it puts PortalWindowTier at 1 -- so a plant deleting it from the list left the
# comment standing and a whole-file claim was satisfied by it. Fortieth instance.
_cp = starts_xml.find("<completedProjects>")
completed_block = None if _cp < 0 else starts_xml[_cp:starts_xml.find("</completedProjects>", _cp)]
check("and the corporate start is the only one that begins with research finished",
      starts_xml.count("<completedProjects>") == 1
      and completed_block is not None
      and completed_block.count("<li>") == 8
      and "RR_GateTelemetry" in completed_block
      and "RR_Commerce_NegotiatedTerms" in completed_block,
      "-- eight projects, all of them faults until now. The other two starts carry an empty list, "
      "which is why they never showed this")

# -------------------------------------------- a toggle on the door, where a player looks
# Owner: *"i have no idea how the gate is suppose to work as there doesnt be a toggle option to
# turn it from a normal door to a machine gate door"*. `CompGetGizmosExtra` opened with
# `if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }`, so an undesignated
# door offered NOTHING and the only route from a door to a gate was a pane in the Operations tab
# -- which the state fault above was also refusing.
check("AN UNDESIGNATED DOOR OFFERS THE WAY TO BECOME A GATE",
      "private IEnumerable<Gizmo> MakeGateGizmos()" in gatecomp
      and "foreach (Gizmo gizmo in MakeGateGizmos()) { yield return gizmo; }" in gatecomp
      and "if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }"
      not in gatecomp,
      "-- DEFINED AND CALLED, and the old early return is GONE rather than merely bypassed")

# `SoleCandidate` is `PreferredProvider` since 0.13.0-dev. The method returns the candidate the
# button binds -- one of OURS where exactly one exists, the sole native one otherwise -- so the old
# name described a rule the method had stopped following.
check("and it only ever offers what the binding would accept",
      "UI.MainTabWindow_Operations.PreferredProvider(" in gatecomp
      and gatecomp.count("UI.MainTabWindow_Operations.PreferredProvider(") == 3
      and "campaign.Headquarters != parent.Map" in gatecomp
      and "ShowOrderResult(BindNativeInfrastructure(console, battery, bench));" in gatecomp
      # **THE REFUSAL BRANCH, not just the calls that feed it.** A plant replacing this test with
      # `if (false)` left every asserted line standing while the toggle bound whatever the scan
      # handed back, including null. Seventh instance this run of the same gap.
      and "if (console == null || battery == null || bench == null)" in gatecomp,
      "-- all three providers, the headquarters requirement checked before the button is shown so "
      "a button that can only refuse is never shown, and the decision left entirely to "
      "`BindNativeInfrastructure`. **A second place to ask, not a second opinion**")

check("and an ambiguous or missing provider is named rather than silent",
      "RR_NativeGate_NoSingleConsole" in gatecomp
      and "RR_NativeGate_NoSingleBattery" in gatecomp
      and "RR_NativeGate_ChooseBench" in gatecomp,
      "-- the player needs to know which piece to build or which choice to make, and *\"it did "
      "nothing\"* tells them neither")

def _file(*parts):
    return io.open(os.path.join(SRC, "RimroomsAsyncIndustries", *parts),
                   encoding="utf-8-sig").read()


_steps = _file("UI", "OperationsGateSteps.cs")
# **THE ELEVEN CHECKS ARE NO LONGER IN THE WINDOW.** Owner, 2026-10-04: *"and when u set a
# door to be a gatew  that gate should tell you next step in the game world not just in the
# operations tab and machine tab"*. The list is read by the door now as well, so it lives in
# the gate's own namespace and the window draws it.
_checklist = _file("Gate", "GateStartupChecklist.cs")
_gate = _file("Gate", "CompRimroomsGate.cs")
_portals = _file("UI", "OperationsPortalNetwork.cs")
_hq = _file("Scenario", "GenStep_Headquarters.cs")
_startdef = _file("Scenario", "RimroomsStartDef.cs")
_expeditions = _file("UI", "OperationsExpeditions.cs")

# ------------------------------------------- the machine tab is numbered, and the checks are live
# Owner: *"the whole machine  tab needs to be numbered and everything step 1 step 2... ect ect so
# fucking simple a 6 yr old chimp can do it"*, *"it needs to have checks showing the start up
# connection checks are complete or unfinished yet"*, *"and it need to explain conciselky how"*.
check("THE MACHINE TAB OPENS WITH NUMBERED START-UP CHECKS",
      "private void DrawGateStartupChecks(Listing_Standard listing" in _steps
      and "DrawGateStartupChecks(listing, campaign);" in _expeditions
      and _expeditions.index("DrawGateStartupChecks(listing, campaign);")
      < _expeditions.index("DrawNativeGateBinding(listing, campaign);"),
      "-- DEFINED AND CALLED, and called FIRST: the checks are the thing that says which of the "
      "two panels below to use, and in which order")

check("and there are ELEVEN of them, each with a done flag and a how",
      all(("Number = %d," % n) in _checklist for n in range(1, 12))
      and all(('"RR_Steps_%dLabel"' % n) in _checklist for n in range(1, 12))
      and all(('"RR_Steps_%dHow"' % n) in _checklist for n in range(1, 12))
      and "public string How;" in _checklist
      and "public bool Done;" in _checklist,
      "-- a step with a label and no instruction is the panel the owner was already looking at")

# **AND THERE IS EXACTLY ONE LIST OF THEM.** This is the property the extraction exists to
# create and the one that would rot silently: pasting the eleven conditions back into the
# window would compile, pass every other claim here, and then drift from the door. Two
# derivations of one rule is the defect this project keeps meeting -- it is what made
# `RR_Gate_CalibrationUnavailable` read *"the gate is not ready for calibration"* for eight
# conditions including *already calibrated*.
check("AND THE WINDOW HOLDS NO SECOND COPY OF THEM",
      "Number = 1," not in _steps
      and "struct GateStep" not in _steps
      and "GateStartupChecklist.Steps(gate)" in _steps,
      "-- the window draws the list and does not own it, so the status board and the door's "
      "own inspect card cannot disagree about whether something is done")

check("AND THE FIRST UNFINISHED ONE IS NAMED ON ITS OWN LINE",
      "GateStartupChecklist.NextIncomplete(steps)" in _steps
      and "internal static GateStep NextIncomplete(" in _checklist
      and "steps.FirstOrDefault(step => !step.Done)" in _checklist
      and '"RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)' in _steps
      and '"RR_Steps_Progress".Translate(' in _steps,
      "-- *\"im fucking lost on what to do ive done like 50 things in a row\"*. Eleven lines is "
      "still a list to read; the answer to *what do i do* is one of them and it is said once at "
      "the top")

# **STRONGER NOW, NOT WEAKER.** This asserted that a DONE row omitted its instruction while an
# unfinished one still carried it -- which was the right call when every row was a wrapped
# paragraph. Owner, 2026-10-04: *"not every step having its own type up of whats next and things
# can be shortend and more concise and dirrect with tools tips would less cluter it"*. So **no
# row carries an instruction**: the surface is a light, a glyph, a number and a few words, the
# detail is the row's tooltip, and one next-step line at the top answers *what do i do*.
# Measured by `check-operations-density.py`: 356 on-screen words to 58.
check("and NO row repeats an instruction -- the detail is on hover",
      '"RR_Steps_Row".Translate(step.Number.ToString(), step.Label)' in _steps
      and "TooltipHandler.TipRegion(row, step.Done" in _steps
      and '"RR_Steps_TipToDo".Translate(step.Label, step.How)' in _steps
      and "RR_Steps_LineToDo" not in _steps,
      "-- otherwise the list becomes a wall of advice about things already handled, which is "
      "exactly what the owner walked into and called a novel")

check("and a binding fault is reported as a FAULT rather than as a step",
      '"RR_Steps_Fault".Translate(gate.NativeBindingFailureKey.Translate())' in _steps,
      "-- it is something that was done and has since broken, and it blocks every step after the "
      "one it broke")

check("THE ORDER MATCHES WHAT THE CODE ACTUALLY ENFORCES",
      _checklist.index("Number = 4,") < _checklist.index("Number = 5,")
      and _checklist.index("Number = 8,") < _checklist.index("Number = 10,")
      and "workshop != null && workshop.IsGateControl" in _checklist
      and "station != null && station.IsGateControl" in _checklist,
      "-- gate control on the TABLE must precede the assembly, because `AvailableOnNow` withdraws "
      "the recipe from a bench in normal operation; gate control on the CONSOLE must precede "
      "staffing, because `BeginSpinUp` refuses while either is doing its day job. A player "
      "following the list top to bottom never meets a step that cannot be done yet")

# ------------------------------------------- the DOOR says what to do next, in the world
# Owner, 2026-10-04, verbatim: *"and when u set a door to be a gatew  that gate should tell you
# next step in the game world not just in the operations tab and machine tab"*.
#
# **The card carried ten readouts and not one answer.** Condition, operator, kill switch,
# servicing, power reserve and its breakdown, the ramp, the equipment links, the live window --
# every one of them answering *what is the state* and none of them *what do I do*. The owner's
# report about the panel was *"ive done like 50 things in a row and its still not opening"*; this
# is the same gap on the object itself.
check("THE GATE'S OWN INSPECT CARD NAMES THE NEXT STEP",
      "private string NextStepReadout()" in _gate
      and "GateStartupChecklist.Steps(this)" in _gate
      and "GateStartupChecklist.NextIncomplete(steps)" in _gate
      and '"RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)' in _gate,
      "-- and it asks the SAME list the status board draws, so the door and the window cannot "
      "tell a player two different next steps")

check("and it is FIRST on the card",
      # **THE ARRAY LITERAL IS THE AUTHORITY ON ORDER.** The first draft compared the
      # index of the method NAME against a later readout and failed against correct code:
      # the method is defined below the call that uses it, so its first textual appearance
      # says nothing about where its output lands on the card.
      "new[] { NextStepReadout(), status," in _gate,
      "-- it is the only line on that card a stuck player needs, and it was being added under ten "
      "lines of state")

# **THE GUARD IS THE LOAD-BEARING PART AND IT IS EASY TO LOSE.** `CompProperties_RimroomsGate` is
# attached to EVERY Core door by the native binding patch, so a next-step line computed before the
# `!IsDesignated` return would print gate start-up advice on every bedroom door on the map.
check("AND EVERY OTHER DOOR IN THE GAME STAYS SILENT",
      _gate.index('if (!IsDesignated) { return null; }')
      < _gate.index("{ NextStepReadout(), status,"),
      "-- the not-designated return comes FIRST, so a door nobody made a gate says nothing at all")

# ------------------------------- setting the coordinate, and opening it, FROM THE DOOR
# Owner, 2026-10-04, verbatim: *"and everything that the machine needs to start up should be able
# to do in the worlkd from the devices themselfes with pawns controls and actrions not just in the
# opetaions tab,, ie setting the cordinace and all of those things need  to show"*.
#
# A designated gate already offered eleven commands on the door. **The two it did not offer were
# the two the owner named**: choosing which place it dials, and opening it. Both existed only as
# buttons in the pane the same message calls a text wall, so a player could build, crew and
# calibrate the machine entirely in the world and then had to go and find a tab to aim it.
_address = _file("Gate", "GateAddressControls.cs")

check("SETTING THE GATE'S ADDRESS IS A COMMAND ON THE DOOR",
      "private IEnumerable<Gizmo> AddressGizmos()" in _address
      and "foreach (Gizmo gizmo in AddressGizmos()) { yield return gizmo; }" in _gate
      and '"RR_GateAddress_SetLabel".Translate()' in _address,
      "-- DEFINED AND CALLED. A gizmo method with no caller in `CompGetGizmosExtra` is the defect "
      "class the wiring checker exists for, and it accounts for four of five bond defects")

check("and it calls THE SAME service the pane calls, with the freeze notice in front of it",
      "PortalAddressService.RegisterLaboratoryAddress(this, captured)" in _address
      and "Presentation.RimroomsGenerationNotice.Announce(captured, () =>" in _address,
      "-- a second surface on one authority, not a second derivation of one rule. And the notice "
      "needs a caller that is not waiting on a return value, which a gizmo action is and a tick "
      "is not")

check("AND OPENING IT GOES THROUGH BeginSpinUp, not straight to the opening",
      "ShowOrderResult(BeginSpinUp(captured.Id))" in _address
      and '"RR_GateAddress_OpenLabel".Translate(' in _address,
      "-- opening is *\"a ramp up process that takes a bit of time\"*, and there is exactly one "
      "way a laboratory gate opens whichever surface started it")

# **DISABLED, NEVER HIDDEN.** Owner's standing complaint is *"ive done like 50 things in a row and
# its still not opening"*. A command that vanishes when it cannot run teaches a player nothing.
check("and both commands grey out WITH A REASON rather than disappearing",
      'setAddress.Disable("RR_GateAddress_NoneKnown".Translate())' in _address
      and 'open.Disable("RR_GateAddress_NoAddressSet".Translate())' in _address
      and 'open.Disable("RR_GateAddress_AlreadyOpen".Translate())' in _address
      and 'open.Disable("RR_GateAddress_AlreadyRamping".Translate())' in _address
      # The commands are yielded unconditionally; only their enabled state varies.
      and _address.index("yield return setAddress;") > _address.index("setAddress.Disable(")
      and _address.index("yield return open;") > _address.index("open.Disable("),
      "-- a player who cannot find the button cannot tell whether it is blocked or missing, and "
      "the refusal is the answer to the question they are already asking")

check("AND THE FLOAT MENUS SHOW THE ADDRESS CODE, NOT THE RAW ID",
      "captured.AddressCode" in _address
      and "place.AddressCode" in _address
      and '"RR_GateAddress_Option".Translate(captured.AddressCode,' in _address,
      "-- owner: *\"only like the !A-01 address code is needed to be displayed to thew player\"*, "
      "and a float menu row has nowhere to put a tooltip carrying the internal identifier")

# ---------------------------------------------- the refusals name their cause
check("CALIBRATION REFUSES WITH THE REASON, AND 'ALREADY DONE' IS ONE OF THEM",
      "public string CalibrationBlockerKey()" in _gate
      and 'if (calibrated) { return "RR_Gate_AlreadyCalibrated"; }' in _gate
      and "string blocker = CalibrationBlockerKey();" in _gate
      and "return pawn != null && pawn == assignedOperator && CalibrationBlockerKey() == null;"
      in _gate,
      "-- one message covered all eight conditions INCLUDING `calibrated`, so a player whose crew "
      "had finished the work was told it could not start. And `CanCalibrate` asks the blocker "
      "rather than restating it, so the predicate and the message cannot disagree")

check("and staffing the console does the same",
      "public string StaffConsoleBlockerKey()" in _gate
      and "string blocker = StaffConsoleBlockerKey();" in _gate
      # **SCOPED TO THE METHOD.** The first draft asserted the key was gone from the whole file
      # and failed against correct code: `OrderAssignedJob` still uses it for a missing job def
      # and a pawn who cannot take the job, which are the things it actually describes. Forty-
      # fourth instance of the scoping trap. What matters is that `OrderStaffConsole` no longer
      # answers four different questions with it.
      and '"RR_Gate_JobUnavailable"' not in _gate[
          _gate.index("public CompanyActionResult OrderStaffConsole()"):
          _gate.index("public string CalibrationBlockerKey()")],
      "-- one key covered four problems with four different fixes, and that method no longer "
      "reaches for it")

check("AND THE PORTAL PANEL SAYS WHY WHEN IT HAS NO BUTTON TO OFFER",
      '"RR_Portals_NoLaboratoryAddress".Translate()' in _portals
      and "private static IEnumerable<string> GateOpeningBlockers(CompRimroomsGate gate)" in _portals
      and "foreach (string blocker in GateOpeningBlockers(gate))" in _portals
      and '"RR_Portals_BlockedConsoleNormalOp".Translate(gate.LinkedConsole.LabelCap)' in _portals,
      "-- the open buttons are drawn per remembered address, so a gate with none showed an empty "
      "panel. **That is what the owner spent an afternoon on.** It names which component is in "
      "normal operation, because the save said the table was switched and the console was not")

# ---------------------------------------------- the facility is a plan, and it is checked
# Owner: *"it should be designed intelligently with like ballistic glass  walls for viewing the
# machine remotely and safely with security zones and shit and lab rooms and shit i mean wtf is
# this this is a 50million dollar facilty"*.
check("THE VIEWING WALLS ARE NAMED AS STRINGS, NEVER AS A CROSS-REFERENCE",
      "public List<RimroomsWallRunPlan> glazing" in _startdef
      and "public List<string> thingDefNames" in _startdef
      and "private static ThingDef ResolveFirstLoaded(List<string> names)" in _hq
      and "DefDatabase<ThingDef>.GetNamedSilentFail(names[index])" in _hq,
      "-- a `ThingDef` field is resolved at load and an unresolved one discards the WHOLE "
      "containing def. That took `Door` and `Autodoor` out of the game once and produced 587 red "
      "lines before the main menu. The glass is from an Optional mod")

check("and a profile without the glass gets a wall, not a hole",
      "if (glass == null) { continue; }" in _hq
      and 'throw new InvalidOperationException("Headquarters glazing has no generated wall at "'
      in _hq,
      "-- a solid viewing wall is a cosmetic loss; a missing wall is a hole in a sealed gate hall")

check("THE AIRLOCK IS TWO AUTOMATIC DOORS IN SERIES",
      "public List<IntVec3> autodoors" in _startdef
      and 'DefDatabase<ThingDef>.GetNamedSilentFail("Autodoor") ?? ThingDefOf.Door' in _hq
      and "An autodoor cell must also be listed in doors" in _startdef,
      "-- *\"with security zones and shit\"*. `ThingDefOf.Autodoor` does not exist, so it is "
      "looked up by name with an ordinary door standing in rather than failing a start over a "
      "door's kind")

check("AND THE HEADQUARTERS POWER REBUILD CAN NO LONGER COST THE START",
      "try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }" in _hq
      and "The headquarters power net could not be resolved at " in _hq,
      "-- this was bare inside a GenStep, which is exactly the shape that cost two launches in "
      "the destination generator. A facility that resolves its net one tick late is playable; one "
      "that does not exist is a dead game")

# ------------------------------------- a ramp is not an open connection
# Owner, 2026-10-01: *"every check mark is complete but it still says: the lab connection to that
# address is not connected.. but the checked staps says otherwise"*. Step 11 read
# `IsOpening || IsSpinningUp`, so pressing "open a session" ticked all eleven while the connection
# was still ramping -- and `PortalTravelService` then refused the crossing with
# `RR_PortalTravel_SessionClosed`, **which was true**. The tick was the thing that was wrong.
check("A RAMPING CONNECTION DOES NOT COUNT AS AN OPEN ONE",
      "Done = haveGate && gate.IsOpening," in _checklist
      and "bool ramping = haveGate && gate.IsSpinningUp;" in _checklist
      and "(gate.SpinUpProgress * 100f).ToString(\"F0\")" in _checklist
      # **THE BRANCH, not the flag and the key.** This asserted that `ramping` was computed and
      # that the keyed string existed; a plant setting `How = false` left both true and the ramp
      # never reported its progress again. **Ninth instance of machinery-not-behaviour**, and the
      # plant caught the claim rather than the other way round.
      and ("                How = ramping" + chr(10)
           + '                    ? "RR_Steps_11HowRamping".Translate(') in _checklist
      # The old disjunction is GONE, not merely bypassed -- and now in BOTH places, because
      # the door reads this list too and a copy of the old rule in the window would be
      # invisible to the door.
      and "gate.IsOpening || gate.IsSpinningUp" not in _checklist
      and "gate.IsOpening || gate.IsSpinningUp" not in _steps,
      "-- `IsSpinningUp` is defined as `!IsOpening`, so they are distinct states and the step says "
      "which one it is in, with the live percentage. The ramp is work and it bleeds back down if "
      "the operator leaves, which is the one thing a player watching it needs told")

check("AND THE LIST SAYS WHAT TO DO ONCE IT IS OPEN",
      '"RR_Steps_NowCross".Translate()' in _steps
      and "if (gate != null && gate.IsOpening)" in _steps,
      "-- the eleven checks end at a live connection and the player's goal is on the far side of "
      "it. Nothing said *now send somebody*, which is why a completed list still left the owner "
      "asking what they were missing")

# ------------------------------- Core moves the centre of an even-dimension building
check("THE FOOTPRINT MODEL APPLIES CORE'S ROTATION ADJUSTMENT",
      "{0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}" in
      io.open(os.path.join(REPO, "tools", "check-start-layout.py"), encoding="utf-8").read()
      and "{0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}" in
      io.open(os.path.join(REPO, ".local", "register", "build-async-facility.py"),
              encoding="utf-8").read(),
      "-- `GenAdj.AdjustForRotation` swaps the axes for a horizontal rotation and then shifts the "
      "centre by one for an even dimension, so a 3x2 console facing SOUTH occupies the rows at "
      "and BELOW its position. **Three copies of this rule disagreed with Core** and all three "
      "said the owner's console overlapped the glass it is sitting against")

_layout_checker = io.open(os.path.join(REPO, "tools", "check-start-layout.py"),
                          encoding="utf-8").read()
check("AND A BENCH WHOSE INTERACTION CELL IS A WALL IS REFUSED",
      # **THE CALL, not the words in it.** This asserted the message text appeared in the file,
      # and a plant that commented the whole `fail(...)` out left the words sitting in a comment.
      # Forty-fifth instance of the scoping trap, and again a plant caught the claim.
      ("            if spot in walls:" + chr(10)
       + '                fail("%s: %s at %s has its interaction cell on the wall %s')
      in _layout_checker
      and "def interaction_cell(" in _layout_checker,
      "-- `IsOperatorOnStation` requires the pawn to stand on exactly that cell. **The rule found "
      "a real defect the day it was written**: the Furniture Store's comms console had its "
      "interaction cell in the staff room's north wall, so it had never been usable -- and "
      "reaching the corporation is that scenario's whole achievement")

# ---------------------------------------- the power room and the breezeway
# Owner: *"actuall make onbe of the rooms a power room and where the generators are should be a
# breeze way thats unroffeced area complete just that area they are in thats inclose by walls and
# doors"*, and *"generators out side batteries inside"*.
_async = [s for s in starts if s["defName"] == "RR_AsyncIndustriesStart"][0]
_rooms = {(r[0], r[1]): r for r in _async["rooms"]}
check("ROOFED FALSE CLEARS A ROOF RATHER THAN SKIPPING IT",
      "map.roofGrid.SetRoof(cell, room.roofed ? RoofDefOf.RoofConstructed : null);" in
      io.open(os.path.join(SRC, "RimroomsAsyncIndustries", "Scenario",
                           "GenStep_Headquarters.cs"), encoding="utf-8-sig").read(),
      "-- every room is nested inside a roofed compound, so a nested room asking for no roof got "
      "one anyway from the pass that ran first. `roofed: false` was meaningless for exactly the "
      "case it is needed in")

check("THE GENERATORS STAND IN A WALLED, DOORED, UNROOFED BREEZEWAY",
      (22, 34) in _rooms and _rooms[(22, 34)][4] is False
      and any(thing == "WoodFiredGenerator" and 23 <= origin[0] <= 26 and 35 <= origin[1] <= 40
              for thing, origin, _rot in _async["buildings"])
      and (22, 37) in [tuple(d) for d in _async["doors"]],
      "-- *\"generators out side batteries inside\"*. A fuel generator in a sealed room cooks the "
      "room; venting it to the sky while keeping it inside the compound is what a breezeway is "
      "for. It is the only unroofed room in the facility and it has a door like any other")

check("and the batteries are inside, in a power room of their own",
      (22, 25) in _rooms and _rooms[(22, 25)][4] is True
      and sum(1 for thing, origin, _rot in _async["buildings"]
              if thing == "Battery" and 23 <= origin[0] <= 26 and 26 <= origin[1] <= 31) >= 4
      and not any(thing == "Battery" and origin[0] >= 29 for thing, origin, _rot
                  in _async["buildings"]),
      "-- the bank moved out of the control room, which is where it was only because the first "
      "authoring had nowhere better to put it")

check("AND THE OWNER'S OWN POSITIONS ARE WHERE THE OWNER PUT THEM",
      any(thing == "CommsConsole" and origin == (32, 33) and rot == 2
          for thing, origin, rot in _async["buildings"])
      and any(thing == "TableMachining" and origin == (45, 33)
              for thing, origin, _rot in _async["buildings"]),
      "-- read out of `Autosave-3.rws` and converted by the layout offset of (120,120) on their "
      "300-cell map. *\"thats where i want them so fix there spawn position\"*")

print("")
# =============================================================== what a dispatch requires
# **The owner found this in a running game**: *"if i use approach gate and dispach to coordinate
# it says no book, i have no books"*. `ExpeditionCargo.RecordBooksRequired` is 1, of
# `CompRouteEvidence.NativeCarrierDef`, and the laboratory start spawned none -- so the first
# dispatch on every fresh lab start refused, and nothing in the battery noticed.
#
# **Derived, never listed.** The count and the def name are read out of the source, so a change
# to either fails here instead of silently making the start short. A hand-typed list is how the
# recorder-to-book change at 0.12.24-dev slipped past in the first place.
_cargo = io.open(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Expedition",
                              "ExpeditionCargo.cs"), encoding="utf-8-sig").read()
_route = io.open(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Investigation",
                              "CompRouteEvidence.cs"), encoding="utf-8-sig").read()
_required = re.search(r"RecordBooksRequired\s*=\s*(\d+)", _cargo)
_carrier = re.search(r'GetNamedSilentFail\("([A-Za-z_]+)"\)', _route)
_starts_xml = io.open(os.path.join(
    REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs", "RimroomsStartDefs",
    "RR_Starts.xml"), encoding="utf-8-sig").read()
_lab = re.search(r"<scenarioId>async_industries</scenarioId>.*?(?=<RimroomsStartDef>|$)",
                 _starts_xml, re.S)
_lab_block = _lab.group(0) if _lab else ""
_book_count = len(re.findall(r"<thing>%s</thing>" % (_carrier.group(1) if _carrier else "NOPE"),
                             _lab_block))

check("THE LABORATORY START SHIPS THE BOOK EVERY DISPATCH REQUIRES",
      _required is not None and _carrier is not None
      and _book_count >= int(_required.group(1)),
      "-- `ExpeditionCargo` needs %s of %r and the start spawns %d. **A start that cannot run "
      "its own first objective is the defect the owner hit in play**"
      % (_required.group(1) if _required else "?",
         _carrier.group(1) if _carrier else "?", _book_count))

check("and it ships a spare, because a branch that loses its only book cannot work",
      _book_count >= 2,
      "-- one to take into the field and one in reserve")


if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every start's layout builds, and no room is sealed")
