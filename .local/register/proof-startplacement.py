# -*- coding: utf-8 -*-
"""The start places onto the player's own map, and a named door is a natural gate.

Owner reports, 2026-09-30, verbatim:

    "store stare was not the map i chose with the buildings being built there instead i was stuck
     in a super micro blocked in area AND there wasnt a Backrooms natural Gate for me to enter"

    "the map size is selected on world seteup before world generation by the player and they
     select the tile they appear in so the store gets genreeate in that selected tiles map"

    "ther is a natural gate that leads to a seeded fixed backrooms and all backrooms have portals
     that lead deeper and lead to the world maps tiles"

Two defects, both measured before being fixed:

  * **The mod overrode the chosen map size.** `ScenPart_RimroomsStart` did
    `Find.GameInitData.mapSize = startDef.mapSize`, forcing 50 for the Store and 60 for the
    others, against RimWorld's smallest new-game option of 200. A 50x50 map is 2,500 cells where
    a default map is 62,500, and the shop occupied 41% of it with an 8-cell margin. **Nothing was
    sealed** -- every layout flood-fills to 100% reachable -- the map itself was the cage.

  * **The Store had no Backrooms connection at all.** `SoloGroupOpening.Open` returned
    immediately unless `insideStart`, and nothing in the headquarters generator creates a
    connection, so there was no door to enter. The deeper and world-tile halves the owner
    describes already existed in `NaturalFrontierService` and `RecordWorldExit`; only the seeding
    was missing.

Run from the repository root.
"""
import io
import os
import re
import sys
import math
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


part = strip_cs(read(os.path.join(SRC, "Scenario", "ScenPart_RimroomsStart.cs")))
gen = strip_cs(read(os.path.join(SRC, "Scenario", "GenStep_Headquarters.cs")))
layout = strip_cs(read(os.path.join(SRC, "Scenario", "HeadquartersLayout.cs")))
opening = strip_cs(read(os.path.join(SRC, "Scenario", "SoloGroupOpening.cs")))
startdef = strip_cs(read(os.path.join(SRC, "Scenario", "RimroomsStartDef.cs")))
page = strip_cs(read(os.path.join(SRC, "Scenario", "Page_RimroomsCompanySetup.cs")))
frontier = strip_cs(read(os.path.join(SRC, "Portals", "NaturalFrontierService.cs")))
starts_xml = read(STARTS)
arrival_part = strip_cs(read(os.path.join(SRC, "Scenario", "ScenPart_RimroomsArrival.cs")))
scenarios_xml = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                                  "ScenarioDefs", "RR_Scenarios.xml"))

# --------------------------------------------------------------------------------------------
print("")
print("the player's map size and tile are honoured")
print("-" * 88)

check("THE MOD NO LONGER OVERRIDES THE CHOSEN MAP SIZE",
      "Find.GameInitData.mapSize =" not in part,
      "-- forcing it is what produced *\"not the map i chose ... a super micro blocked in "
      "area\"*: 50x50 against RimWorld's smallest option of 200")

check("the generator requires the layout to FIT rather than to match a size",
      "HeadquartersLayout.Fits(part.startDef, map.Size)" in gen
      and "map.Size.x != part.startDef.mapSize" not in gen,
      "-- an exact-size guard is what made forcing the size necessary in the first place")

# ---------------------------------------------------------------- 0.12.46-dev
# Owner direction: **"the map generator is not our mod"**. Core generates the tile; the facility
# is added onto it. These are the claims that keep it that way.
check("THE MOD NO LONGER CHOOSES THE MAP GENERATOR",
      "Find.GameInitData.mapGeneratorDef =" not in part,
      "-- replacing Core's Base_Player gave flat Soil with a building on it: no rock, no plants, "
      "no biome character. And Map Preview simulates the REAL generator, so the preview a player "
      "rerolled against was a picture of a map the mod discarded")

check("no start def names a generator, and the field is gone",
      "public MapGeneratorDef mapGenerator;" not in startdef
      and "<mapGenerator>" not in starts_xml,
      "-- a field nothing reads is a job nobody finished; it is retired, not orphaned")

patch_path = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Patches",
                          "RR_StartGenSteps.xml")
check("the gen steps are patched into Core's own generator", os.path.isfile(patch_path))
if os.path.isfile(patch_path):
    patch = read(patch_path)
    check("the patch ADDS rather than replaces",
          'Class="PatchOperationAdd"' in patch and "PatchOperationReplace" not in
          re.sub(r"<!--.*?-->", " ", patch, flags=re.S),
          "-- a replace would take ownership of Base_Player's genSteps and silently drop every "
          "step Core and every other mod put there")
    check("it targets Base_Player's genSteps",
          'Defs/MapGeneratorDef[defName="Base_Player"]/genSteps' in patch)
    check("both of our steps are added",
          "RR_HeadquartersTerrain" in patch and "RR_HeadquartersFacility" in patch)

# The guard's body is read on its own, because a `throw` planted INSIDE it changes none of
# the surrounding facts -- the method still exists and the callers still null-check it.
guard_body = ""
guard_at = gen.find("internal static RimroomsStartDef StartForMap(Map map)")
if guard_at >= 0:
    guard_body = gen[guard_at:gen.find("\n        }", guard_at)]
check("THE GEN STEPS RETURN QUIETLY WHEN IT IS NOT THE COMPANY START",
      guard_at >= 0
      and "throw" not in guard_body
      and guard_body.count("return null;") >= 4
      and gen.count("if (start == null) { return; }") >= 2
      and "RequireStart" not in gen,
      "-- these now run inside Base_Player, which generates EVERY player map a game ever makes. "
      "A throw there would break a second settlement, a quest site, a reloaded world. The guard "
      "used to throw, and that is the single thing that had to change before the patch was safe")

check("THE TERRAIN STEP NO LONGER FLATTENS THE WHOLE MAP",
      "foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain" not in gen
      and "foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))" in gen,
      "-- overwriting every cell is what produced *\"bare dirt not even vegitation\"*; only the "
      "footprint is prepared now and the rest of the tile is Core's")

check("the start is still placed on the tile the player chose",
      "map.Tile != Find.GameInitData.startingTile" in gen,
      "-- this was always right and must stay: the facility belongs on their tile")

# Every consumer of an authored cell must offset, or the facility tears apart. Counted, because
# missing ONE of them is the failure mode and a bare `in` test cannot see which.
check("the offset is applied to every authored cell",
      gen.count("HeadquartersLayout.Offset(start, map.Size)") >= 2
      and gen.count("+ offset") >= 5
      and "room.Rect.MovedBy" in gen,
      "-- found %d Offset call(s) and %d applications; rooms, doors, buildings, conduits, "
      "arrival and stock all need it" % (gen.count("HeadquartersLayout.Offset(start, map.Size)"),
                                         gen.count("+ offset")))

# Definition AND uses. A bare name test passes against any renaming of it -- the trap this
# session has now been caught by in five consecutive batches.
check("the layout is centred, with a margin from the edge",
      "EdgeMargin = 8" in layout and layout.count("EdgeMargin") >= 5
      and "/ 2 - extent.minX" in layout,
      "-- Core's map edge is not buildable and mountains generate inward, so a layout flush to "
      "the border is unreachable on one side")

check("the offset is clamped so the layout cannot cross an edge",
      "if (offsetX > maxX)" in layout and "if (offsetX < minX)" in layout)

check("the setup page shows the REAL map size, not the authored one",
      "Find.GameInitData.mapSize" in page and "start.mapSize" not in page,
      "-- showing the def's number would tell the player something untrue about their game")

# --------------------------------------------------------------------------------------------
print("")
print("a start that names a door begins with a natural gate")
print("-" * 88)

check("THE OPENING IS NO LONGER INSIDE-START ONLY",
      "if (start == null || !start.emergenceDoorCell.IsValid) { return null; }" in opening
      and "if (start == null || !start.insideStart) { return null; }" not in opening,
      "-- this early return is why the Store had no connection at all")

check("only an inside start is moved into the coordinate",
      "if (start.insideStart)" in opening and "MoveOpeningPartyInside(surface, inside, entry);"
      in opening,
      "-- a surface start with a natural gate keeps its crew in their own building")

check("a surface natural gate records its own event",
      'RecordEvent("RR_Event_NaturalGateOpening"' in opening)

check("THE DOOR LOOKUP IS OFFSET",
      "start.emergenceDoorCell + HeadquartersLayout.Offset(start, surface.Size)" in opening,
      "-- the layout moves onto the player's map, so reading the authored cell would look for a "
      "door where no door is. This is the single easiest thing to miss in the whole change")

check("any start may name a door, and it must be one of its own",
      "if (emergenceDoorCell.IsValid && (doors == null || !doors.Contains(emergenceDoorCell)))"
      in startdef,
      "-- a cell that is not in the doors list has no door generated at it, so the opening would "
      "find nothing to mark")

check("an inside start must still name one",
      "if (insideStart && !emergenceDoorCell.IsValid)" in startdef)

# The Store, specifically, because it is the start the owner played.
store = re.search(r"<defName>RR_FurnitureStoreStart</defName>(.*?)"
                  r"</RimroomsAsyncIndustries\.Scenario\.RimroomsStartDef>", starts_xml, re.S)
check("the Store names its back-room door", store is not None
      and "<emergenceDoorCell>(35, 0, 34)</emergenceDoorCell>" in store.group(1),
      "-- *\"a door in the back that should not be there\"* is the scenario's own description")
check("that cell is one of the Store's declared doors",
      store is not None and "<li>(35, 0, 34)</li>" in store.group(1))

check("the deeper and world-tile halves already exist and are untouched",
      "MaximumNaturalDepth" in frontier and "MaximumFrontiersPerCoordinate" in frontier
      and "RecordWorldExit" in frontier,
      "-- the owner's *\"portals that lead deeper and lead to the world maps tiles\"* was "
      "already built; only the seeding of the first one was missing")

# --------------------------------------------------------------------------------------------
print("")
print("every layout is reachable, and fits any map the player can pick")
print("-" * 88)


def start_block(name):
    found = re.search(r"<defName>%s</defName>(.*?)</RimroomsAsyncIndustries\.Scenario\."
                      r"RimroomsStartDef>" % name, starts_xml, re.S)
    return found.group(1) if found else ""


for name in ("RR_AsyncIndustriesStart", "RR_FurnitureStoreStart", "RR_SoloGroupStart"):
    body = start_block(name)
    rooms = [(int(a), int(b), int(c), int(d)) for a, b, c, d in re.findall(
        r"<x>(\d+)</x><z>(\d+)</z><width>(\d+)</width><height>(\d+)</height>", body)]
    if not rooms:
        check("%s declares rooms" % name, False)
        continue
    min_x = min(r[0] for r in rooms)
    max_x = max(r[0] + r[2] - 1 for r in rooms)
    min_z = min(r[1] for r in rooms)
    max_z = max(r[1] + r[3] - 1 for r in rooms)
    needed = max(max_x - min_x + 1, max_z - min_z + 1) + 16
    check("%s fits the smallest map RimWorld offers (200)" % name, needed <= 200,
          "-- needs %d" % needed)

    doors = set((int(a), int(b)) for a, b in re.findall(
        r"<li>\((\d+),\s*\d+,\s*(\d+)\)</li>", re.search(r"<doors>(.*?)</doors>", body, re.S).group(1)))
    walls = set()
    for x, z, w, h in rooms:
        for cx in range(x, x + w):
            for cz in range(z, z + h):
                if cx in (x, x + w - 1) or cz in (z, z + h - 1):
                    walls.add((cx, cz))
    walls -= doors
    arrival = re.search(r"<arrivalCell>\((\d+),\s*\d+,\s*(\d+)\)</arrivalCell>", body)
    start_cell = (int(arrival.group(1)), int(arrival.group(2))) if arrival else None
    reachable = set()
    if start_cell and start_cell not in walls:
        queue = deque([start_cell])
        reachable.add(start_cell)
        while queue:
            cx, cz = queue.popleft()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (cx + dx, cz + dz)
                if not (0 <= nxt[0] < 300 and 0 <= nxt[1] < 300):
                    continue
                if nxt in walls or nxt in reachable:
                    continue
                reachable.add(nxt)
                queue.append(nxt)
    # Every declared room's interior must be reachable from the arrival cell. A sealed room is
    # the bug the owner's "blocked in" report made me go and measure for the first time.
    sealed = []
    for x, z, w, h in rooms:
        interior = set((cx, cz) for cx in range(x + 1, x + w - 1) for cz in range(z + 1, z + h - 1))
        if interior and not (interior & reachable):
            sealed.append("x %d..%d z %d..%d" % (x, x + w - 1, z, z + h - 1))
    check("%s has no room sealed off from its arrival cell" % name, not sealed,
          "-- %s" % "; ".join(sealed))

# --------------------------------------------------------------------------------------------
# 0.12.47-dev -- the fourth launch. Owner, verbatim: *"i did a store start the map loaded
# correctly but i had pop up company could not finish startup company placement stopped... so
# wtf is up with this??? also the starting store structure was not built and i have no pawns on
# the map to control"*, and the direction: *"it needs a like a burn into place functiions to
# carve everyhting out and cut everything down and fill in with soil where water is unmder where
# the store needs to propigate before game start"*.
#
# Measured in the live game through RimBridgeServer before any of this was written: 234 of the
# Store's 1020 footprint cells held Marble or Granite formations, 177 cells carried natural rock
# roof, and `rimworld/list_colonists` returned ZERO.
print("")
print("  -- the site is prepared rather than refused --")

# The order is a NUMBER and the claim is an inequality. A test for the literal "100" would pass
# against 1000, and a test for the def name alone would pass against any order at all.
terrain_order = re.search(
    r"<defName>RR_HeadquartersTerrain</defName>\s*<order>(\d+)</order>", scenarios_xml)
check("THE TERRAIN STEP RUNS AFTER CORE BUILDS THE ELEVATION GRID AND BEFORE CORE READS IT",
      terrain_order is not None and 10 < int(terrain_order.group(1)) < 200,
      "-- Core's ElevationFertility is order 10 and RocksFromGrid is order 200. At the previous "
      "order of 5 the elevation grid did not exist yet; after 200 the rock is already spawned. "
      "Found order %s" % (terrain_order.group(1) if terrain_order else "MISSING"))

check("THE FACILITY SITE IS LOWERED BELOW CORE'S ROCK THRESHOLD SO NO ROCK GENERATES ON IT",
      "private const float BuildableElevation = 0.55f;" in gen
      and "MapGenFloatGrid elevation = MapGenerator.Elevation;" in gen
      and "elevation[cell] = BuildableElevation;" in gen
      and "if (elevation[cell] > BuildableElevation)" in gen,
      "-- GenStep_RocksFromGrid spawns a formation wherever elevation exceeds 0.7 and natural "
      "roof above 0.728. Prevention beats demolition: without this the facility sits in a "
      "234-cell hole carved out of a mountain")

# Definition AND the call AND the call's POSITION. A burn that runs after the walls are placed
# would destroy them.
burn_at = gen.find("internal static void BurnIntoPlace(")
call_at = gen.find("BurnIntoPlace(start, map, offset);")
rooms_at = gen.find("foreach (RimroomsRoomPlan room in start.rooms)")
check("THE FOOTPRINT IS BURNED CLEAR BEFORE THE FIRST WALL IS PLACED",
      burn_at >= 0 and call_at >= 0 and rooms_at >= 0 and call_at < rooms_at,
      "-- definition at %d, call at %d, the room loop at %d; a burn that ran after placement "
      "would destroy the facility it just built" % (burn_at, call_at, rooms_at))

burn_body = gen[burn_at:gen.find("\n        }\n", burn_at)] if burn_at >= 0 else ""
check("it carves everything out and cuts everything down",
      "thing.Destroy(DestroyMode.Vanish);" in burn_body
      and "new List<Thing>(cell.GetThingList(map))" in burn_body,
      "-- the list is copied first because destroying a thing mutates the cell's own thing list")

check("it clears the natural rock roof the formation leaves behind",
      "roof.isNatural" in burn_body and "map.roofGrid.SetRoof(cell, null);" in burn_body,
      "-- natural roof outlives the rock under it; 177 footprint cells carried it and an "
      "unsupported one leaves the facility in permanent darkness")

check("it fills in with soil where water is",
      "terrain.IsWater" in burn_body
      and "map.terrainGrid.SetTerrain(cell, start.outdoorTerrain);" in burn_body
      and "Traversability.Impassable" in burn_body,
      "-- owner direction, verbatim: *\"fill in with soil where water is\"*")

check("NOTHING LIVING IS BURNED",
      "thing.def.category == ThingCategory.Pawn" in burn_body
      and burn_body.count("continue;") >= 2,
      "-- Core spawns animals at order 1200, after this, and they walk in from the edges. Two "
      "monkeys were standing in the measured footprint")

check("a faction structure inside the reserved footprint is NAMED before it is cleared",
      "Log.Warning(" in burn_body and "thing.Faction != null" in burn_body,
      "-- that would mean another mod's gen step placed a structure here despite the UsedRects "
      "reservation, and it must be visible rather than silent")

check("THE WALL NO LONGER REFUSES GROUND CORE GENERATED",
      "Headquarters wall intersects generated structure" not in gen,
      "-- this threw on the footprint's VERY FIRST cell, (133, 0, 135), on a Granite formation "
      "with 900 hit points. Refusing was the wrong instinct: every vanilla structure gen step "
      "clears what is under it")

# The catch block read on its own, because a `throw` planted inside it changes nothing else.
catch_at = gen.find("catch (Exception exception)")
catch_body = gen[catch_at:gen.find("\n        }\n", catch_at)] if catch_at >= 0 else ""
check("A FAILED FACILITY HANDS THE START SPOT BACK TO CORE INSTEAD OF RE-THROWING",
      catch_at >= 0
      and "MapGenerator.PlayerStartSpot = IntVec3.Invalid;" in catch_body
      and "throw;" not in catch_body,
      "-- re-throwing only reached GenerateContentsIntoMap, which logs and carries on, so it "
      "bought nothing and left the player standing on an arrival cell inside a building that "
      "does not exist. FindPlayerStartSpot runs at order 850, after this, and only picks a spot "
      "when none is valid")

print("")
print("  -- the player keeps their colonists even when our own work fails --")

check("THE ARRIVAL NEVER THROWS OUT OF CORE'S SCENARIO STEP",
      "throw" not in arrival_part,
      "-- THIS is what made the fourth launch unplayable. GenerateIntoMap is called from Core's "
      "GenStep_ScenParts, and MapGenerator.GenerateContentsIntoMap abandons a gen step at its "
      "first exception, so Core's ENTIRE scenario step died: no colonists, no supplies. "
      "list_colonists returned 0 on the live map")

check("an incomplete receipt still delivers Core's own arrival",
      arrival_part.count("base.GenerateIntoMap(map);") >= 2
      and "!receipt.setupComplete" in arrival_part
      and "Log.Error(" in arrival_part,
      "-- a subclass of ScenPart_PlayerPawnsArriveMethod is an ADDITION to Core's arrival, not "
      "a replacement for it; found %d base call(s)" % arrival_part.count("base.GenerateIntoMap(map);"))

check("the fallback path still records that stock was granted once",
      arrival_part.count("receipt.arrivalStarted = true;") >= 2
      and arrival_part.count("if (receipt.arrivalStarted) { return; }") >= 2,
      "-- otherwise a retry re-enumerates the native starting-thing factories and grants "
      "supplies twice; found %d record(s) and %d guard(s)"
      % (arrival_part.count("receipt.arrivalStarted = true;"),
         arrival_part.count("if (receipt.arrivalStarted) { return; }")))

# --------------------------------------------------------------------------------------------
# Owner requirement, 2026-09-30, verbatim: *"and the store facilities walls floors and all of it
# have to be reconfigureable deconstructable and minifyable(the minify mod) just like the game
# with the mods allows"*.
#
# Register row [128] MinifyEverything mutates `ThingDef.minifiedDef` and
# `building.alwaysUninstallable` at startup -- on DEFS, not on instances. The facility is built
# from Core defs only, so whatever it does to a wall applies to ours. What is left to check is
# that nothing this mod does makes its own placements special.
print("")
print("  -- the facility is the player's to take apart --")

# Counted against the spawns. Missing the faction on ONE of the three kinds is the failure mode,
# and a bare `in` test cannot see which one.
check("EVERY THING THE FACILITY PLACES BELONGS TO THE PLAYER",
      gen.count("SetFactionDirect(Faction.OfPlayer)") >= 3
      and gen.count("GenSpawn.Spawn(") >= 4
      and "wall.SetFactionDirect(Faction.OfPlayer);" in gen
      and "door.SetFactionDirect(Faction.OfPlayer);" in gen
      and "building.SetFactionDirect(Faction.OfPlayer);" in gen,
      "-- player faction is all Designator_Deconstruct and Designator_Uninstall require; found "
      "%d faction assignment(s) against %d spawn(s)"
      % (gen.count("SetFactionDirect(Faction.OfPlayer)"), gen.count("GenSpawn.Spawn(")))

check("the facility places Core defs only, so the minify mod can reach them",
      "ThingDefOf.Wall" in gen and "ThingDefOf.Door" in gen
      and "ThingMaker.MakeThing(plan.thing, plan.stuff)" in gen
      and "new ThingDef" not in gen,
      "-- MinifyEverything patches ThingDefs at startup; a def of our own would be outside its "
      "reach and could not be made minifiable by it at all")

check("the floor goes down through SetTerrain, so Remove Floor works",
      "map.terrainGrid.SetTerrain(cell, start.floorTerrain);" in gen,
      "-- TerrainGrid.SetTerrain records the displaced terrain in underGrid for any layerable "
      "floor, and CanRemoveTopLayerAt needs exactly that")

check("nothing in the facility path blocks a deconstruct or uninstall designation",
      "DesignationDefOf.Deconstruct" not in gen and "DesignationDefOf.Uninstall" not in gen
      and "designationManager" not in gen,
      "-- the facility must behave like anything else the player owns")

# The roof-support rule, replicated. RoofCollapseUtility.RoofMaxSupportDistance is 6.9 and
# support is a flood fill over ROOFED cells within that distance looking for a holdsRoof
# edifice -- so a wall reachable only by leaving the roof does not count. Walls and doors both
# hold roof, so the door cells make no difference.
ROOF_SUPPORT_DISTANCE = 6.9


def unsupported_roof(rooms):
    walls = set()
    roofed = set()
    for x, z, w, h, is_roofed in rooms:
        for cx in range(x, x + w):
            for cz in range(z, z + h):
                if cx in (x, x + w - 1) or cz in (z, z + h - 1):
                    walls.add((cx, cz))
                elif is_roofed:
                    roofed.add((cx, cz))
    # A wall cell beats an enclosing room's interior: the wall is what actually gets spawned.
    roofed -= walls
    bad = []
    for cell in sorted(roofed):
        seen = set([cell])
        queue = deque([cell])
        supported = False
        while queue and not supported:
            here = queue.popleft()
            for step in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (here[0] + step[0], here[1] + step[1])
                if math.hypot(near[0] - cell[0], near[1] - cell[1]) > ROOF_SUPPORT_DISTANCE:
                    continue
                if near in walls:
                    supported = True
                    break
            if supported:
                break
            for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (here[0] + step[0], here[1] + step[1])
                if near in seen or near not in roofed:
                    continue
                if math.hypot(near[0] - cell[0], near[1] - cell[1]) > ROOF_SUPPORT_DISTANCE:
                    continue
                seen.add(near)
                queue.append(near)
        if not supported:
            bad.append(cell)
    return roofed, walls, bad


for name in ("RR_AsyncIndustriesStart", "RR_FurnitureStoreStart", "RR_SoloGroupStart"):
    body = start_block(name)
    plans = [(int(x), int(z), int(w), int(h), roofed == "true") for x, z, w, h, roofed in
             re.findall(r"<li><x>(-?\d+)</x><z>(-?\d+)</z><width>(\d+)</width>"
                        r"<height>(\d+)</height><roofed>(\w+)</roofed>", body)]
    roofed_cells, wall_cells, bad_cells = unsupported_roof(plans)
    check("%s ROOFS NOTHING IT CANNOT HOLD UP" % name,
          len(plans) > 0 and not bad_cells,
          "-- %d roofed cell(s) and %d wall cell(s); %d cell(s) out of support range, e.g. %s. "
          "Deconstructing a wall under unsupported roof collapses it, so a layout like this "
          "drops a roof on the player's pawns the first time they remodel"
          % (len(roofed_cells), len(wall_cells), len(bad_cells), bad_cells[:6]))

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the facility generates on the player's chosen tile and map size, centred and "
      "reachable, and any start that names a door begins with a permanently open natural gate")
