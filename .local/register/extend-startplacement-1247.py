# -*- coding: utf-8 -*-
"""Add the burn-into-place and never-throw-at-arrival claims to proof-startplacement.py.

Every anchor asserted before anything is written, one write at the end.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-startplacement.py")

text = io.open(PROOF, encoding="utf-8").read()

READ_ANCHOR = u'starts_xml = read(STARTS)'
READ_NEW = u'''starts_xml = read(STARTS)
arrival = strip_cs(read(os.path.join(SRC, "Scenario", "ScenPart_RimroomsArrival.cs")))
scenarios_xml = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                                  "ScenarioDefs", "RR_Scenarios.xml"))'''

TAIL_ANCHOR = u'''print("")
if failures:'''

TAIL_NEW = u'''# --------------------------------------------------------------------------------------------
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
    r"<defName>RR_HeadquartersTerrain</defName>\\s*<order>(\\d+)</order>", scenarios_xml)
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

burn_body = gen[burn_at:gen.find("\\n        }\\n", burn_at)] if burn_at >= 0 else ""
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
      "-- owner direction, verbatim: *\\"fill in with soil where water is\\"*")

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
catch_body = gen[catch_at:gen.find("\\n        }\\n", catch_at)] if catch_at >= 0 else ""
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
      "throw" not in arrival,
      "-- THIS is what made the fourth launch unplayable. GenerateIntoMap is called from Core's "
      "GenStep_ScenParts, and MapGenerator.GenerateContentsIntoMap abandons a gen step at its "
      "first exception, so Core's ENTIRE scenario step died: no colonists, no supplies. "
      "list_colonists returned 0 on the live map")

check("an incomplete receipt still delivers Core's own arrival",
      arrival.count("base.GenerateIntoMap(map);") >= 2
      and "!receipt.setupComplete" in arrival
      and "Log.Error(" in arrival,
      "-- a subclass of ScenPart_PlayerPawnsArriveMethod is an ADDITION to Core's arrival, not "
      "a replacement for it; found %d base call(s)" % arrival.count("base.GenerateIntoMap(map);"))

check("the fallback path still records that stock was granted once",
      arrival.count("receipt.arrivalStarted = true;") >= 2
      and arrival.count("if (receipt.arrivalStarted) { return; }") >= 2,
      "-- otherwise a retry re-enumerates the native starting-thing factories and grants "
      "supplies twice; found %d record(s) and %d guard(s)"
      % (arrival.count("receipt.arrivalStarted = true;"),
         arrival.count("if (receipt.arrivalStarted) { return; }")))

print("")
if failures:'''

problems = []
for anchor in (READ_ANCHOR, TAIL_ANCHOR):
    if text.count(anchor) != 1:
        problems.append("%d occurrence(s) of %r" % (text.count(anchor), anchor[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(READ_ANCHOR, READ_NEW, 1)
text = text.replace(TAIL_ANCHOR, TAIL_NEW, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("proof extended with the 0.12.47-dev claims")
