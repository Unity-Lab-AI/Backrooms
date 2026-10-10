# -*- coding: utf-8 -*-
"""Re-aim the two claims and one plant the arrangements work moved, and add the
claims the roads, blocks and exact prune need."""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-coordinate-layout.py"
PLANTS = ".local/register/plant-coordinate-layout.py"

EDITS = [
    # ------------------------------------------------- the width authority gained the room list
    (PROOF,
     '      "internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)"' + NL
     + '      in planner',
     '      ("internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth,"' + NL
     + '       + chr(10) + "            IReadOnlyList<RoomRecord> rooms)") in planner'),

    (PROOF,
     '      and "int halfWidth = CorridorHalfWidthBetween(first, second, depth);" in planner',
     '      and "int halfWidth = CorridorHalfWidthBetween(first, second, depth, rooms);" in planner'),

    # ------------------------------------------------------------ the prune became exact
    (PROOF,
     '      and "if (a.x == b.x || a.z == b.z) { continue; }" in planner' + NL
     + '      and "other.links.Remove(room.index);" in planner,' + NL
     + '      "-- DEFINED AND CALLED, last, after every room has stopped moving. Two things decided after "' + NL
     + '      "the braid can take a lane away: `PushAgainst` slides a dead end into somebody\'s lane, and "' + NL
     + '      "`ShapeDepthOf` shifts as links are added, which changes the width the pair asks for. **It "' + NL
     + '      "only ever removes a diagonal, which is what makes it safe** -- the spanning tree the walk "' + NL
     + '      "built is entirely non-diagonal, so pruning cannot disconnect the level")',
     '      and "other.links.Remove(room.index);" in planner' + NL
     + '      # **EXACT NOW, NOT CONSERVATIVE.** It refused to touch anything whose centres shared an' + NL
     + '      # axis, reasoning that the spanning tree is entirely non-diagonal. True and too coarse:' + NL
     + '      # the reach braid makes links two slots apart ALONG an axis, and the neighbourhood push' + NL
     + '      # can leave one of those routeless. The clause skipped it and `CandidateIsSafe` refused' + NL
     + '      # the whole layout -- the probe printed `link 2-6 has no route under it`.' + NL
     + '      and "if (LinkedGraphIsWhole(rooms)) { continue; }" in planner' + NL
     + '      and "private static bool LinkedGraphIsWhole(List<RoomRecord> rooms)" in planner' + NL
     + '      and "if (a.x == b.x || a.z == b.z) { continue; }" not in planner_code,' + NL
     + '      "-- DEFINED AND CALLED, last, after every room has stopped moving. **Remove the edge, and "' + NL
     + '      "keep the removal only if every room still claiming a route can still be reached from the "' + NL
     + '      "threshold.** A load-bearing link stays and the candidate is refused, which is correct and "' + NL
     + '      "is what the next candidate answers. Asking the question directly is both exact and easier "' + NL
     + '      "to reason about than guessing which edges the tree owns")'),

    # ----------------------------------------------------------------------------- the plant
    (PLANTS,
     '     "            int halfWidth = CorridorHalfWidthBetween(first, second, depth);",' + NL
     + '     "            int halfWidth = 2;"),',
     '     "            int halfWidth = CorridorHalfWidthBetween(first, second, depth, rooms);",' + NL
     + '     "            int halfWidth = 2;"),' + NL + NL
     + '    # ------------------------------------------------- roads, blocks, and the exact prune' + NL
     + '    ("A ROAD STOPS BEING WIDE, so a through-line reads as ordinary hallways", PLANNER,' + NL
     + '     "            if (OnRoad(first, second, rooms)) { return 3; }" + chr(10), ""),' + NL + NL
     + '    ("and a road is no longer recognised as a run that carries on past its ends", PLANNER,' + NL
     + '     "            return ContinuesPast(second, first, rooms, alongX)" + chr(10)' + NL
     + '     + "                || ContinuesPast(first, second, rooms, alongX);",' + NL
     + '     "            return false;"),' + NL + NL
     + '    ("THE NEIGHBOURHOOD BLOCK IS NEVER FORMED", PLANNER,' + NL
     + '     "                { PushAgainst(rooms, terrace[index], rooms[hub], depth); }",' + NL
     + '     "                { }"),' + NL + NL
     + '    ("and it stops offering the mobile rooms first, so every push snaps back", PLANNER,' + NL
     + '     "                terrace.Sort((left, right) => left.links.Count != right.links.Count" + chr(10)' + NL
     + '     + "                    ? left.links.Count - right.links.Count" + chr(10)' + NL
     + '     + "                    : left.index - right.index);" + chr(10), ""),' + NL + NL
     + '    ("THE PRUNE GOES BACK TO GUESSING WHICH EDGES THE TREE OWNS", PLANNER,' + NL
     + '     "                    if (LinkedGraphIsWhole(rooms)) { continue; }",' + NL
     + '     "                    if (a.x == b.x || a.z == b.z) { continue; }"),' + NL + NL
     + '    ("and a removal that disconnects the level is no longer put back", PLANNER,' + NL
     + '     "                    if (LinkedGraphIsWhole(rooms)) { continue; }" + chr(10), ""),'),
]

CLAIMS = '''
# ======================================================================================
# ROADS AND NEIGHBOURHOODS ARE ARRANGEMENTS, NOT KINDS OF ROOM
#
# Owner, 2026-10-03: *"so its more rooma corradors facilites infastructure roads neighborrs
# hood malls shoopping centers military"*. The queue row worked this out about itself:
# *"roads and neighborrs hood in particular are not room shapes at all -- they are
# arrangements of rooms, which is a layout feature rather than a dressing one."*
# ======================================================================================

check("A ROAD IS A RUN THAT CARRIES ON, AND ITS CORRIDORS ARE THE WIDE ONES",
      "internal static bool OnRoad(RoomRecord first, RoomRecord second," in planner
      and "if (OnRoad(first, second, rooms)) { return 3; }" in planner
      and "private static bool ContinuesPast(RoomRecord from, RoomRecord through," in planner,
      "-- a single room with lane markings in it is a room, not a road. A road is three or more "
      "rooms in a line with **one wide corridor running through all of them**, and you can only "
      "see that from the layout. Derived from the saved graph and stored nowhere, so the carver, "
      "the reachability proof and the probe all get the same answer -- a `bool isRoad` on "
      "`RoomRecord` would have needed a schema migration to say what the links already say")

# **AND THE ROAD BRAID WAS MEASURED, FOUND TO DO NOTHING, AND DELETED.** A pass that picked a
# row and linked every slot along it changed the longest straight run not at all: 6 to 8 either
# way, which at depth 3 and deeper is the whole slot row. At an average of five links per room
# the braids already join almost every adjacent collinear pair.
check("and there is no road braid, with the measurement that removed it recorded",
      "THERE IS NO ROAD BRAID, AND THAT IS A MEASUREMENT RATHER THAN AN OMISSION" in planner
      and '"road:line"' not in planner_code,
      "-- a pass whose effect nobody can measure is a pass nobody can defend. The comment is the "
      "evidence, so the next person does not write it again")

check("A NEIGHBOURHOOD IS A BLOCK, formed while the rooms can still move",
      "{ PushAgainst(rooms, terrace[index], rooms[hub], depth); }" in planner
      and "terrace.Sort((left, right) => left.links.Count != right.links.Count" in planner
      and 'StableHash(seed, "neighbourhood:hub", depth)' in planner,
      "-- the back-to-back push rolls per room, so its pairs are SCATTERED: two to three hundred "
      "per depth and not one of them a block. **Order matters twice here.** It runs before the "
      "diagonal and reach braids, because a room holding five or six links cannot slide at all -- "
      "`PushAgainst` undoes any move carrying one past `FurthestLinkedCentres`, and placed after "
      "them this measured as a no-op, 3 with it and 3 without. And the hub's neighbours are "
      "offered least-connected first, so the mobile ones are tried before the hopeless ones have "
      "shifted the geometry. Measured after both: back-to-back pairs up about half again, 248 to "
      "376 at depth 1 and 366 to 488 at depth 3, with blocks of four")

check("and every move still proves itself, because nothing here relaxes PushAgainst",
      "bool blocksARoute = !EveryLinkRoutes(rooms, mover, depth);" in planner
      and "if (onMap && !collides && !blocksARoute && SharesWall(mover, anchorRoom)) { return; }"
      in planner,
      "-- this chooses which rooms to offer and in what order. All four conditions still have to "
      "hold or the move is undone: on the map, nothing overlapped, no existing link's route or "
      "shape broken, and `SharesWall` agreeing afterwards")

'''


def apply(path, old, new):
    text = io.open(path, encoding="utf-8").read()
    found = text.count(old)
    if found != 1:
        print("NOT UNIQUE (%d) in %s: %s" % (found, path.split("/")[-1], old.splitlines()[0][:70]))
        return False
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new))
    return True


problems = 0
for path, old, new in EDITS:
    if apply(path, old, new):
        print("ok %s: %s" % (path.split("/")[-1], old.splitlines()[0][:70]))
    else:
        problems += 1

gate = ("if failures:" + NL
        + '    print("PROOF FAILED: %d claim(s)" % len(failures))' + NL
        + "    sys.exit(1)" + NL)
text = io.open(PROOF, encoding="utf-8").read()
if text.count(gate) != 1:
    print("exit gate not found exactly once")
    problems += 1
else:
    io.open(PROOF, "w", encoding="utf-8", newline=NL).write(text.replace(gate, CLAIMS + gate))
    print("four arrangement claims inserted before the exit gate")

if problems:
    sys.exit(1)
