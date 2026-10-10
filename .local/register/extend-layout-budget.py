# -*- coding: utf-8 -*-
"""The open-map budget claims, added to proof-coordinate-layout.py.

The budget belongs in this proof because it is the direct consequence of the geometry it already
measures: a 300x300 coordinate that is never unloaded is what makes a cap necessary.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

text = io.open(PROOF, encoding="utf-8").read()

ANCHOR = 'print("")\nif failures:'

NEW = '''print("")
print("HOW MANY PLACES MAY BE HELD OPEN AT ONCE")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"dont let them go more than 5 remember the games
# mechanics and limits built in if they find a gate to a world map tile or a deeper backrroms and
# they have 5 mpas they should gett a warning this gate is blocked your holding open too many
# gates, but per scerio styled"*, clarified by *"5 is the limit of other colonies available so a
# backrooms level should be one colonly bacskicly in my thinking"*.
budget = read(os.path.join(SRC, "Portals", "OpenMapBudget.cs"))
frontier = read(os.path.join(SRC, "Portals", "NaturalFrontierService.cs"))
startdef = read(os.path.join(SRC, "Scenario", "RimroomsStartDef.cs"))
keyed = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                          "English", "Keyed", "RR_Portals.xml"))
parent = read(os.path.join(SRC, "Generation", "RimroomsDestinationMapParent.cs"))

check("A COORDINATE MAP IS STILL NEVER UNLOADED, WHICH IS WHY A CAP IS NEEDED AT ALL",
      "public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)" in parent
      and "return false;" in parent,
      "-- a coordinate is a place you can go back to. That was free at 60x60 and is not at "
      "300x300, and the cap is what replaced the eviction the owner first asked for and then "
      "superseded")

check("THE BUDGET IS READ FROM THE GAME'S OWN COLONY LIMIT, NOT HARD-CODED",
      "Prefs.MaxNumberOfPlayerSettlements" in budget
      and "= 5;" not in budget,
      "-- *\\"remember the games mechanics and limits built in\\"*. Core enforces that pref in "
      "SettleUtility as count >= Prefs.MaxNumberOfPlayerSettlements, and it is a 1-to-5 player "
      "slider, so a player who moves it to 3 gets 3")

check("a scenario may set its own budget, which is what per-scenario means",
      "public int openMapBudget;" in startdef
      and "part.startDef.openMapBudget" in budget
      and "scenario > 0 ? scenario" in budget,
      "-- *\\"but per scerio styled\\"*; zero defers to the player's own limit")

check("THE BUDGET HAS A FLOOR, OR THE SOLO START BREAKS ON A CLEAN NEW GAME",
      "MinimumBudget = 2" in budget and "Mathf.Max(MinimumBudget, budget)" in budget,
      "-- the pref can be set to 1, and the solo/group start opens a coordinate during "
      "PostGameStart when the surface map already counts as one held place. Without the floor "
      "that scenario would refuse its own opening")

check("a Backrooms level counts against the budget exactly as a colony does",
      "map.Parent is Generation.RimroomsDestinationMapParent) { held++; }" in budget
      and "map.IsPlayerHome && map.Parent is Settlement) { held++; }" in budget,
      "-- *\\"a backrooms level should be one colonly bacskicly in my thinking\\"*. Core's own "
      "count cannot see a coordinate map, so this counts both")

# The ORDER of the two checks inside Discover is the whole argument, so it is measured as an
# ordering rather than as the presence of a call.
way_out_at = frontier.find("CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);")
block_at = frontier.find("if (!OpenMapBudget.CanOpenAnother)")
mint_at = frontier.find("campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered)")
check("A BLOCKED GATE IS REFUSED BEFORE ANY COORDINATE IS MINTED",
      block_at >= 0 and mint_at >= 0 and block_at < mint_at,
      "-- minting one and then refusing would leave a place nobody can reach recorded against "
      "the branch. Block at %d, mint at %d" % (block_at, mint_at))

check("THE BUDGET NEVER CLOSES THE LAST DOOR HOME",
      way_out_at >= 0 and block_at >= 0 and way_out_at < block_at,
      "-- a doorway may lead OUT instead of deeper, and a way home costs no map: it records a "
      "world tile rather than minting a place. Checking the budget first would strand a crew "
      "that is deep and full up, which is the same trap the depth cap is ordered to avoid. "
      "Way-out at %d, budget at %d" % (way_out_at, block_at))

check("the one place a coordinate map is generated also enforces it",
      "coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother" in service,
      "-- the doorway refusal is where a player should be TOLD; this is the backstop for a "
      "machine gate, a saved address or a recovery path. Only when a NEW map would be made: "
      "recalling a coordinate that already has its site must never be refused")

check("the refusal says what the owner said",
      "RR_Frontier_TooManyGatesHeld" in keyed
      and "holding open too many gates" in keyed
      and "RR_Frontier_TooManyGatesHeld" in budget,
      "-- *\\"they should gett a warning this gate is blocked your holding open too many "
      "gates\\"*, and the message names the way out of it")

check("WAYS ONWARD SCALE WITH THE SIZE OF THE PLACE",
      "MinimumFrontiersPerCoordinate = 4" in frontier
      and "MaximumFrontiersPerCoordinate = 6" in frontier
      and "Cap = FrontiersFor(record)" in frontier,
      "-- owner direction: four to six per level. Two was right for a six-room 60x60 coordinate "
      "and wrong for a 300x300 one")

depth_reach = re.search(r"MaximumNaturalDepth\\s*=\\s*(\\d+)", frontier)
check("the natural chain reaches deeper than it did",
      depth_reach is not None and int(depth_reach.group(1)) >= 6,
      "-- raised from 3 to %s, together with the budget that makes a deeper chain affordable"
      % (depth_reach.group(1) if depth_reach else "MISSING"))

print("")
if failures:'''

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("budget claims added to proof-coordinate-layout")
