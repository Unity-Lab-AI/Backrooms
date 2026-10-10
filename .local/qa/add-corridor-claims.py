"""Add the proof claims the bent-corridor, degree, vault and fill work needs.

**PLACED BEFORE THE EXIT GATE, deliberately.** Appending a claim after
`if failures: sys.exit(1)` records a failure nothing acts on -- that happened
once in this repo and the plants caught it, not the author.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-coordinate-layout.py"

GATE = (
    "if failures:" + NL
    + '    print("PROOF FAILED: %d claim(s)" % len(failures))' + NL
    + "    sys.exit(1)" + NL
)

CLAIMS = '''
# ======================================================================================
# THE CORRIDOR BENDS, THE DEGREE RISES, AND SOME ROOMS HAVE NO WAY IN AT ALL
#
# Owner, 2026-10-03: *"and make sure hallways and corradors and shit arent all straight ...
# u -turns, multiple coices on directions to take in every rooms"*, *"room connected to like
# 0 - 10 other rooms"*, *"not have so much empty rock space where nothing exists"* and
# *"insentive to mine things out to find isolated undiscorvered rooms when mining and
# deconsturcting wals"*.
#
# Measured before any of it was written: average degree **2.2 to 2.4**, maximum **4**, roomfill
# **17.1%** at depth five. Every one of those is the slot grid's arithmetic rather than a tuning,
# which is why each claim below asserts a rule and not a number.
# ======================================================================================

check("A CORRIDOR CAN BEND, AND THE BEND RUNS IN THE ROCK LANE",
      "private static List<CorridorLeg> BentLegs(RoomRecord first, RoomRecord second, int depth,"
      in planner
      and "return BentLegs(first, second, depth, rooms);" in planner
      and "private static List<CorridorLeg> ElbowThroughLane(CellRect a, CellRect b, IntVec3 centreA,"
      in planner
      and "int laneX = (centreA.x + centreB.x) / 2;" in planner
      and "int laneZ = (centreA.z + centreB.z) / 2;" in planner,
      "-- DEFINED AND CALLED. A dogleg between two room CENTRES is not merely absent from this "
      "generator, it is unsafe: at depth 1 the diagonal pair (0,0)-(1,1) would run from (36,36) "
      "toward x=81 and straight through the room at slot (1,0). The bend therefore runs on the "
      "midpoint of the two centres, which is a lane midline only for a pair one slot apart on "
      "each axis -- and that is the condition `BentLegs` refuses on")

check("and the bend is THREE legs, so its corner is a full block of floor",
      "legs.Add(LegAlongX(outFrom, outTo, centreA.z, halfWidth));" in planner
      and "legs.Add(LegAlongX(inFrom, inTo, centreB.z, halfWidth));" in planner
      and "if (candidate.Count == 3 && LegsClearEveryRoom(candidate, rooms))" in planner,
      "-- out of the room, along the lane, back in. Each leg overruns the turn by `halfWidth - 1`: "
      "the reachability flood is FOUR-directional, so a corner that met only diagonally would "
      "read as connected to a person and as sealed to the check")

# **THE ONE SAFETY GATE ON A BENT ROUTE, and it is stricter than it needs to be on purpose.** A
# corridor wall sharing a cell with a room wall is harmless by itself -- but a room's doorway sits
# at a point on that same wall, and a corridor wall landing on a doorway SEALS THE ROOM. That is
# the unreachable-room class that cost this project thirty-nine checkpoints.
check("AND EVERY ROUTE IS PROVED CLEAR OF EVERY ROOM BEFORE IT IS CARVED",
      "private static bool LegsClearEveryRoom(List<CorridorLeg> legs, IReadOnlyList<RoomRecord> rooms)"
      in planner
      and "if (leg.Floor.Overlaps(bounds) || leg.WallLow.Overlaps(bounds) ||" in planner
      and planner.count("LegsClearEveryRoom(") == 4,
      "-- DEFINED AND CALLED FOUR TIMES: once per bent candidate, and twice on the straight run. "
      "The straight run never needed it while a corridor could only join grid-adjacent slots, "
      "because the gap between two such slots holds nothing. `TryStraightCorridor` can now join a "
      "pair that merely overlaps on one axis, and two rooms in the same row two slots apart would "
      "be carved straight through the room between them")

check("NO GRAPH EDGE STANDS WITHOUT A ROUTE UNDER IT",
      "private static void PruneUnroutableLinks(List<RoomRecord> rooms, int depth)" in planner
      and "PruneUnroutableLinks(rooms, depth);" in planner
      and "if (a.x == b.x || a.z == b.z) { continue; }" in planner
      and "other.links.Remove(room.index);" in planner,
      "-- DEFINED AND CALLED, last, after every room has stopped moving. Two things decided after "
      "the braid can take a lane away: `PushAgainst` slides a dead end into somebody's lane, and "
      "`ShapeDepthOf` shifts as links are added, which changes the width the pair asks for. **It "
      "only ever removes a diagonal, which is what makes it safe** -- the spanning tree the walk "
      "built is entirely non-diagonal, so pruning cannot disconnect the level")

check("and the WALK refuses a step it could not carve, which is what makes that prune safe",
      "if (CorridorLegs(rooms[parent], room, depth, rooms).Count == 0 &&" in planner
      and "!SharesWall(rooms[parent], room))" in planner,
      "-- the walk builds the spanning tree, so a tree edge with no corridor under it is a level "
      "that cannot be carved -- and the prune deliberately refuses to touch a non-diagonal link, "
      "because taking one away is the thing that would disconnect the place")

check("THE DIAGONAL BRAID EXISTS, so a room is a junction rather than a stop on a line",
      'StableHash(seed,' in planner
      and '"diagonal:" + slot.x + "," + slot.z + ":" + side, depth);' in planner
      and "? new IntVec2(slot.x + 1, slot.z + 1)" in planner
      and ": new IntVec2(slot.x + 1, slot.z - 1);" in planner
      and "internal const int DiagonalBraidRarity = 2;" in planner,
      "-- north-east and south-east only, so each diagonal pair is considered exactly once, the "
      "same reason the orthogonal braid takes east and north alone. A slot has four diagonal "
      "neighbours as well as four orthogonal ones, so the degree ceiling is eight rather than the "
      "measured four")

check("and one slot in eight is a JUNCTION that takes every link it can, so the degree SPREADS",
      "internal const int JunctionRarity = 8;" in planner
      and "private static bool SlotIsJunction(int seed, IntVec2 slot, int depth)" in planner
      and planner.count("SlotIsJunction(seed, slot, depth)") == 3,
      "-- DEFINED AND CALLED FROM BOTH BRAIDS. A single rarity moves every room to the same new "
      "average and leaves the RANGE as narrow as it was; *\\"0 - 10 other rooms\\"* asks for a "
      "spread. A junction is the top of it at eight ways out, and a sealed vault is the bottom "
      "at none")

# **THE OWNER'S EXPLICIT ZERO CASE, and the clause that made it unbuildable.** `CandidateIsSafe`
# proved EVERY room reachable across carved floor, so a room with no links was refused outright --
# the degree spec's lower end could not exist. The later direction is what makes zero legal rather
# than broken: an *"isolated undiscorvered room"* is MEANT to have no way in, and the way in is a
# pick. The guarantee is not weakened: the defect that clause exists to catch is a room the
# generator believed it had connected and had not, and every such room HAS links.
check("A SEALED VAULT HAS NO LINKS, AND THE REACHABILITY PROOF KNOWS THE DIFFERENCE",
      'internal const string SealedFamily = "sealed_vault";' in planner
      and "rooms.All(room => room.links.Count == 0 || seen.Contains(room.Bounds.CenterCell))"
      in planner
      and "rooms.Where(room => room.familyId == SealedFamily).All(room => room.links.Count == 0)"
      in planner
      and "rooms.All(room => seen.Contains(room.Bounds.CenterCell))" not in planner_code,
      "-- a room that CLAIMS a route must have one; a vault claims none. And the family is held to "
      "that from the other side too, so a vault that somehow gained a link fails the candidate "
      "rather than quietly becoming an ordinary room")

check("and its slot is reserved BEFORE the walk, which is what makes it sealed",
      'StableHash(seed, "sealed:" + attempt, depth)' in planner
      and "if (slotOf.ContainsKey(next) || sealedSlots.Contains(next)) { continue; }" in planner
      and "int budget = Math.Max(1, MaxRooms - sealedSlots.Count);" in planner,
      "-- nothing can link to a slot that was never in `slotOf` while the walk and both braids "
      "were running. **And the budget is the measured half**: the walk reaches `MaxRooms` from "
      "depth 3 onward, so a vault appended afterwards was silently dropped every time -- `deg0` "
      "read 0.0% at depth 3 and deeper while the slots had been reserved and the rock left "
      "standing. The probe printed the zero; nobody reasoned it out")

check("and the validator counts a vault as a room but not as a disconnection",
      "int linkedRooms = rooms.Count(room => room.links.Count > 0);" in service
      and "rooms.Any(room => room.links.Count > 0 && !visited.Contains(room.index))" in service
      and "directedEdges < 2 * (linkedRooms - 1)" in service
      and "visited.Count != rooms.Count" not in service_code,
      "-- every room with links must be in the same connected piece as the threshold, and the edge "
      "floor follows that: a connected piece of `linked` rooms needs `linked - 1` edges, not "
      "`rooms - 1`. The ceiling still counts every room, because a vault is still a room the map "
      "has to hold")

# **THE DOOR POSITION WAS NEVER A DOOR RULE.** Owner: *"non default fdoor possitions in rooms so
# doors are not just on each side, can have doors al over"*. `DoorOpening` read
# `cell.z == room.Bounds.CenterCell.z`, and that was not a choice -- a corridor could only run
# along a line both centres shared, so the wall midpoint was the only cell one could arrive at.
check("A DOOR IS WHERE THE CORRIDOR ARRIVES, NOT THE MIDDLE OF A WALL",
      "internal static bool TryStraightCorridor(RoomRecord first, RoomRecord second," in planner
      and "if (TryStraightCorridor(room, other, out alongX, out line))" in planner
      and "if (other.Bounds.minX > bounds.maxX && cell.x == bounds.maxX && cell.z == line)"
      in planner
      and "cell.z == room.Bounds.CenterCell.z" not in planner_code,
      "-- the corridor names the line it runs along and the door is wherever that line meets the "
      "wall. **It also unsealed the grand hall**: the hall spans two slots so its centre sits "
      "between them, matching no slot's centre, and a room directly above it shared neither axis "
      "-- so the maze walk could leave the hall along one row and nowhere else")

check("and the straight run prefers the FIRST room's centre line, so every old pair is unchanged",
      "line = centreA.z >= low && centreA.z <= high ? centreA.z" in planner
      and ": centreB.z >= low && centreB.z <= high ? centreB.z : (low + high) / 2;" in planner,
      "-- which is what makes this a generalisation rather than a change: a grid-adjacent pair "
      "shares a centre line, so it is chosen first and the corridor is the one that was always "
      "carved. The second room's line is the hall's case, and the overlap midpoint is the "
      "fallback when neither centre is inside it")

check("THE SPAN VARIATION MAY NOT EAT THE CORRIDOR LANE",
      "int lane = SlotGap - (2 * NarrowestCorridorHalfWidth + 1);" in planner
      and "if (reach > lane) { reach = lane; }" in planner
      and "internal const int NarrowestCorridorHalfWidth = 2;" in planner,
      "-- two neighbours both rolled to their widest leave `SlotGap - 2 * reach` cells of rock "
      "between them, and the narrowest corridor is five cells including its walls. Below that the "
      "pair gets no route, the step is declined, the level comes out smaller and nothing says why. "
      "**It had never bitten because the numbers happened to leave exactly five at every depth** "
      "-- a constraint satisfied by luck, which bit the moment the slot grid changed")

check("AND THE SPACE IS FILLED BY FEWER, LARGER ROOMS, which is the same instruction twice",
      "internal const int Margin = 6;" in planner
      and "internal const int MaxSlotsPerAxis = 8;" in planner
      and "internal const int MaxRooms = 60;" in planner,
      "-- the fraction of a slot a room occupies is `(1 - SlotGap / spacing)^2`, and spacing is "
      "the map divided by the slot count, so **a FINER grid fills LESS space**: the rock between "
      "rooms is a fixed ten cells per boundary and more slots means more boundaries. At ten slots "
      "the span had fallen to sixteen against a twenty-seven spacing and roomfill measured 17.1%. "
      "So *\\"leas than 60-100 romms\\"* and *\\"FILL THE SPACE WITH ROOMS\\"* are not in conflict "
      "-- fewer larger rooms is what fills a fixed map, and a margin of fourteen on four sides was "
      "throwing away a fifth of every one of them")

'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(GATE) != 1:
    print("exit gate not found exactly once (%d)" % text.count(GATE))
    sys.exit(1)
io.open(PROOF, "w", encoding="utf-8", newline=NL).write(text.replace(GATE, CLAIMS + GATE))
print("claims inserted before the exit gate")
