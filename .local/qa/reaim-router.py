"""Re-aim the claims and plants the seven-form lane router moved.

All of these were written earlier in this same session against the single
three-leg elbow. The owner then answered the degree fork with *"it shouldnt
just be one option there needs to be wide varying variations of all types so
dont limit yourself"*, and the elbow became seven route forms. Every claim is
re-aimed at what the code became; none is relaxed.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-coordinate-layout.py"
PLANTS = ".local/register/plant-coordinate-layout.py"

EDITS = [
    # ------------------------------------------------------------------- the ceiling, four -> eight
    (PROOF,
     '      and "private const int MaximumUndirectedEdgesPerRoom = 4;" in service' + NL
     + '      and "private const int MaximumUndirectedEdgesPerRoom = 2;" not in service',
     '      and "private const int MaximumUndirectedEdgesPerRoom = 8;" in service' + NL
     + '      and "private const int MaximumUndirectedEdgesPerRoom = 2;" not in service'),

    (PROOF,
     '      "at two it refused every maze that used the links the bend had just made possible. Four is "' + NL
     + '      "the grid geometry stated, not a preference. The floor is untouched, and it is the half of "',
     '      "at two it refused every maze that used the links the bend had just made possible. **And the "' + NL
     + '      "same again at four**, once the five-leg route forms reached the eight span-two offsets as '
     'well. "' + NL
     + '      "Eight is the grid geometry stated -- sixteen candidate neighbours, so eight undirected "' + NL
     + '      "edges -- not a preference, and it bounds the layout TOTAL rather than one room, so a "' + NL
     + '      "junction may hold more while the average stays low. The floor is untouched, and it is the '
     'half of "'),

    # --------------------------------------------- the push, no longer restricted to a dead end
    (PROOF,
     'check("and only a DEAD END is ever pushed, found by its link count",' + NL
     + '      "if (rooms[index].links.Count != 1) { continue; }" in planner' + NL
     + '      and "PushAgainst(rooms, rooms[index], rooms[host]);" in planner' + NL
     + '      and "private static void PushAgainst(List<RoomRecord> rooms, RoomRecord mover," in planner,' + NL
     + '      "-- a room with one connection cannot re-route anything by moving, and in a braided maze a "' + NL
     + '      "dead end is found by asking rather than by knowing which rooms were added last. The old "' + NL
     + '      "claim pinned `rooms[rooms.Count - 1]`, which was the spur loop\'s last-added room")',
     'check("ANY ROOM MAY BE PUSHED BACK TO BACK, because the push now proves itself",' + NL
     + '      "if (rooms[index].links.Count < 1) { continue; }" in planner' + NL
     + '      and "PushAgainst(rooms, rooms[index], rooms[host], depth);" in planner' + NL
     + '      and "int host = rooms[index].links[(roll / 7) % rooms[index].links.Count];" in planner' + NL
     + '      and "private static void PushAgainst(List<RoomRecord> rooms, RoomRecord mover," in planner' + NL
     + '      and "if (rooms[index].links.Count != 1) { continue; }" not in planner_code,' + NL
     + '      "-- it was restricted to rooms with exactly ONE link, on the reasoning that such a room "' + NL
     + '      "cannot re-route anything by moving. True, and the only guarantee available while nothing "' + NL
     + '      "checked whether a move broke a corridor. **The degree work then made the restriction "' + NL
     + '      "bite**: at an average of five links a level has few dead ends left, and the measured "' + NL
     + '      "back-to-back count fell from 131 to 23 -- a feature the owner asked for twice, shrinking "' + NL
     + '      "as a side effect of a different one, which the probe printed and nobody would otherwise "' + NL
     + '      "have seen. `PushAgainst` now proves the move itself, so the link count stops being the "' + NL
     + '      "condition, and which neighbour it goes wall to wall with is drawn rather than always the "' + NL
     + '      "first link it happens to hold")'),

    # ------------------------------------------------------- the push's fourth condition
    (PROOF,
     '      and "if (onMap && !collides && SharesWall(mover, anchorRoom)) { return; }" in planner' + NL
     + '      and "mover.x = originalX;" in planner,' + NL
     + '      "-- the slot a spur leaves is not the slot it arrives in, and the arrival may belong to a "' + NL
     + '      "third room. All three conditions are checked -- on the map, no collision, and `SharesWall` "' + NL
     + '      "agrees -- because a pair the pushing code thinks is back to back and the doorway code "' + NL
     + '      "does not is a sealed room")',
     '      and "if (onMap && !collides && !blocksARoute && SharesWall(mover, anchorRoom)) { return; }"' + NL
     + '      in planner' + NL
     + '      and "private static bool EveryLinkRoutes(List<RoomRecord> rooms, RoomRecord mover, int depth)"' + NL
     + '      in planner' + NL
     + '      and "if (!AreNeighbourRooms(room, other)) { return false; }" in planner' + NL
     + '      and "mover.x = originalX;" in planner,' + NL
     + '      "-- the slot a room leaves is not the slot it arrives in, and the arrival may belong to a "' + NL
     + '      "third room. **FOUR conditions now, and the fourth is what made it safe to push any room "' + NL
     + '      "rather than only a dead end**: on the map, no collision, no existing link broken, and "' + NL
     + '      "`SharesWall` agrees -- because a pair the pushing code thinks is back to back and the "' + NL
     + '      "doorway code does not is a sealed room. And the fourth asks the SHAPE gate as well as the "' + NL
     + '      "route, because the shape gate is what `ValidateRooms` asks: a push slides a room by most "' + NL
     + '      "of its own span, enough to carry a reach-braid link past `FurthestLinkedCentres`, measured "' + NL
     + '      "as a candidate refusal at 106 cells against a stated 96 while the route stayed perfectly "' + NL
     + '      "carvable")'),

    # ------------------------------------------------------------------ the router, seven forms
    (PROOF,
     'check("A CORRIDOR CAN BEND, AND THE BEND RUNS IN THE ROCK LANE",' + NL
     + '      "private static List<CorridorLeg> BentLegs(RoomRecord first, RoomRecord second, int depth,"' + NL
     + '      in planner' + NL
     + '      and "return BentLegs(first, second, depth, rooms);" in planner' + NL
     + '      and "private static List<CorridorLeg> ElbowThroughLane(CellRect a, CellRect b, IntVec3 centreA,"' + NL
     + '      in planner' + NL
     + '      and "int laneX = (centreA.x + centreB.x) / 2;" in planner' + NL
     + '      and "int laneZ = (centreA.z + centreB.z) / 2;" in planner,' + NL
     + '      "-- DEFINED AND CALLED. A dogleg between two room CENTRES is not merely absent from this "' + NL
     + '      "generator, it is unsafe: at depth 1 the diagonal pair (0,0)-(1,1) would run from (36,36) "' + NL
     + '      "toward x=81 and straight through the room at slot (1,0). The bend therefore runs on the "' + NL
     + '      "midpoint of the two centres, which is a lane midline only for a pair one slot apart on "' + NL
     + '      "each axis -- and that is the condition `BentLegs` refuses on")',
     'check("A CORRIDOR CAN BEND, AND THE BEND RUNS IN THE ROCK LANE",' + NL
     + '      "private static List<CorridorLeg> BentLegs(RoomRecord first, RoomRecord second, int depth,"' + NL
     + '      in planner' + NL
     + '      and "return BentLegs(first, second, depth, rooms);" in planner' + NL
     + '      and "private static int LaneBeyond(int wall, bool forward, int halfWidth)" in planner' + NL
     + '      and "return forward ? wall + 1 + halfWidth : wall - 1 - halfWidth;" in planner,' + NL
     + '      "-- DEFINED AND CALLED. A dogleg between two room CENTRES is not merely absent from this "' + NL
     + '      "generator, it is unsafe: at depth 1 the diagonal pair (0,0)-(1,1) would run from (36,36) "' + NL
     + '      "toward x=81 and straight through the room at slot (1,0). **And the lane is defined by a "' + NL
     + '      "room\'s own wall rather than by the slot grid** -- the line whose near wall lands one cell "' + NL
     + '      "past it -- which means a route needs nothing but the two rooms\' rects to compute. No '
     'reader "' + NL
     + '      "has to be told the slot spacing, so no reader can be told a different one")'),

    (PROOF,
     'check("and the bend is THREE legs, so its corner is a full block of floor",' + NL
     + '      "legs.Add(LegAlongX(outFrom, outTo, centreA.z, halfWidth));" in planner' + NL
     + '      and "legs.Add(LegAlongX(inFrom, inTo, centreB.z, halfWidth));" in planner' + NL
     + '      and "if (candidate.Count == 3 && LegsClearEveryRoom(candidate, rooms))" in planner,',
     'check("AND THERE ARE SEVEN ROUTE FORMS, because one bend shape is a signature",' + NL
     + '      "internal const int RouteForms = 7;" in planner' + NL
     + '      and "int form = (roll + attempt) % RouteForms;" in planner' + NL
     + '      and "for (int attempt = 0; attempt < RouteForms; attempt++)" in planner' + NL
     + '      and "private static void BuildRouteWaypoints(List<IntVec3> points, CellRect a, CellRect b,"' + NL
     + '      in planner' + NL
     # **THE U-TURN BY NAME.** Owner: *"u -turns"*. Form 6 leaves through the wall facing AWAY
     # from the destination and doubles back, which is the literal article rather than a loop in
     # the graph that a player might happen to walk backwards.
     + '      and "int wrongWayX = eastward ? a.minX - 1 : a.maxX + 1;" in planner' + NL
     + '      and "int laneAway = LaneBeyond(eastward ? a.minX : a.maxX, !eastward, halfWidth);" in planner' + NL
     + '      and "if (candidate.Count > 0 && LegsClearEveryRoom(candidate, rooms))" in planner,'),

    (PROOF,
     '      "-- out of the room, along the lane, back in. Each leg overruns the turn by `halfWidth - 1`: "' + NL
     + '      "the reachability flood is FOUR-directional, so a corner that met only diagonally would "' + NL
     + '      "read as connected to a person and as sealed to the check")',
     '      "-- two elbows through a lane beside the FIRST room, two through a lane beside the SECOND, "' + NL
     + '      "two five-leg routes that reach a slot TWO away, and one U-TURN that leaves through the "' + NL
     + '      "wall facing away from where it is going. Owner, answering the degree fork: *\\"it '
     'shouldnt "' + NL
     + '      "just be one option there needs to be wide varying variations of all types so dont limit "' + NL
     + '      "yourself\\"*, and *\\"u -turns\\"* by name. The five-leg forms are what lift the degree "' + NL
     + '      "ceiling past the eight a diagonal can manage, measured from max 8 to max 13-16. Each leg "' + NL
     + '      "overruns its turn by `halfWidth - 1`: the reachability flood is FOUR-directional, so a "' + NL
     + '      "corner that met only diagonally would read as connected to a person and as sealed to the "' + NL
     + '      "check -- and the two TERMINI are deliberately not extended, because they sit one cell "' + NL
     + '      "outside a room\'s wall and extending them would put corridor floor inside the room")'),

    (PROOF,
     '      and planner.count("LegsClearEveryRoom(") == 4,',
     '      and planner.count("LegsClearEveryRoom(") == 5' + NL
     + '      and "if (!envelope.Overlaps(bounds)) { continue; }" in planner,'),

    (PROOF,
     '      "-- DEFINED AND CALLED FOUR TIMES: once per bent candidate, and twice on the straight run. "',
     '      "-- DEFINED AND CALLED FOUR TIMES: once per route form tried, once in `EveryLinkRoutes` by '
     'way "' + NL
     + '      "of `CorridorLegs`, and twice on the straight run -- plus a single envelope rect around the "' + NL
     + '      "whole route, which answers almost every room in one test and changes no verdict, because a "' + NL
     + '      "room that misses the envelope cannot touch a leg inside it. "'),

    # ----------------------------------------------------------------------------- the two plants
    (PLANTS,
     '    ("rooms stop being pushed together at all", PLANNER,' + NL
     + '     "                PushAgainst(rooms, rooms[index], rooms[host]);" + chr(10), ""),',
     '    ("rooms stop being pushed together at all", PLANNER,' + NL
     + '     "                PushAgainst(rooms, rooms[index], rooms[host], depth);" + chr(10), ""),' + NL
     + NL
     + '    ("the push goes back to only ever moving a dead end, so back-to-back pairs collapse", PLANNER,' + NL
     + '     "                if (rooms[index].links.Count < 1) { continue; }",' + NL
     + '     "                if (rooms[index].links.Count != 1) { continue; }"),' + NL
     + NL
     + '    ("THE PUSH STOPS CHECKING WHETHER IT BROKE SOMEBODY ELSE\'S CORRIDOR", PLANNER,' + NL
     + '     "bool blocksARoute = !EveryLinkRoutes(rooms, mover, depth);",' + NL
     + '     "bool blocksARoute = false;"),' + NL
     + NL
     + '    ("and the moved room is allowed to carry a link past the stated reach", PLANNER,' + NL
     + '     "                    if (!AreNeighbourRooms(room, other)) { return false; }" + chr(10), ""),'),

    (PLANTS,
     '    ("the bend loses its last leg, so the route stops short of the second room", PLANNER,' + NL
     + '     "                legs.Add(LegAlongX(inFrom, inTo, centreB.z, halfWidth));" + NL, ""),',
     '    ("THE ROUTE FORMS COLLAPSE TO ONE, so every bend in the game is the same shape", PLANNER,' + NL
     + '     "                int form = (roll + attempt) % RouteForms;",' + NL
     + '     "                int form = 0;"),' + NL
     + NL
     + '    ("THE U-TURN IS GONE, so no corridor ever leaves a room the wrong way", PLANNER,' + NL
     + '     "                    int wrongWayX = eastward ? a.minX - 1 : a.maxX + 1;",' + NL
     + '     "                    int wrongWayX = eastward ? a.maxX + 1 : a.minX - 1;"),' + NL
     + NL
     + '    ("the route terminus is extended into the room it is supposed to stop outside of", PLANNER,' + NL
     + '     "                if (index != 0) { start -= step * reach; }",' + NL
     + '     "                start -= step * reach;"),' + NL
     + NL
     + '    ("THE REACH BRAID IS GONE, so the degree ceiling falls back to a diagonal\'s eight", PLANNER,' + NL
     + '     "                    if (roll % ReachBraidRarity != 0) { continue; }",' + NL
     + '     "                    if (true) { continue; }"),'),
]

problems = 0
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8").read()
    found = text.count(old)
    if found != 1:
        print("NOT UNIQUE (%d) in %s: %s" % (found, path.split("/")[-1], old.splitlines()[0][:78]))
        problems += 1
        continue
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new))
    print("ok %s: %s" % (path.split("/")[-1], old.splitlines()[0][:78]))

if problems:
    print("%d edit(s) did not apply" % problems)
    sys.exit(1)
print("router claims and plants re-aimed")
