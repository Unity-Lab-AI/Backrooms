# -*- coding: utf-8 -*-
"""Finish the arrangements work: drop the measured-dead road braid, form the
neighbourhood while rooms can still move, and make the prune exact.

Every slice asserts end > start. The last attempt took `t.index(A):t.index(B)`
where B had moved above A, produced an empty match, and `str.replace("")`
inserted the replacement between every character in the file -- 154,124 copies
of one method. Cheap to check, catastrophic not to.
"""
import io
import sys

NL = chr(10)
PATH = "src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs"


def slice_between(text, start_marker, end_marker):
    start = text.index(start_marker)
    end = text.index(end_marker)
    if end <= start:
        raise AssertionError("slice runs backwards: %r is not after %r"
                             % (end_marker[:50], start_marker[:50]))
    return start, end


text = io.open(PATH, encoding="utf-8").read()

# ---------------------------------------------------------------- A. the road braid comes out
ROAD_NOTE = '''            // **THERE IS NO ROAD BRAID, AND THAT IS A MEASUREMENT RATHER THAN AN OMISSION.**
            // Owner, 2026-10-03: *"so its more rooma corradors facilites infastructure roads
            // neighborrs hood malls shoopping centers military"*.
            //
            // One was written here -- pick a row or column, link every occupied slot along it --
            // and the probe was taught to report the longest straight run of linked rooms before
            // and after it. **The numbers were identical: 6 to 8 either way, which at depth 3 and
            // deeper is the entire slot row.** At an average of five links per room the braids
            // already join almost every adjacent collinear pair, so a line across the level exists
            // by arithmetic and forcing one adds nothing. Deleted rather than kept as insurance: a
            // pass whose effect nobody can measure is a pass nobody can defend.
            //
            // **What was missing was never the run. It was that the run did not LOOK like a
            // road.** Every corridor along it was whatever width its own pair rolled, so a
            // through-line read as a chain of ordinary hallways. `OnRoad` is the answer and it is
            // a question about the finished graph: a corridor whose straight run carries on past
            // either end is always cut at the wide half-width. See `CorridorHalfWidthBetween`.

'''
start, end = slice_between(text,
                           "            // **THE ROAD: a straight run linked end to end",
                           "            AssignMazeFamilies(rooms, hops, seed);")
text = text[:start] + ROAD_NOTE + text[end:]
print("A: road braid removed")

# ------------------------------------- B. the neighbourhood moves ahead of the later braids
start, end = slice_between(text,
                           "            // **THE NEIGHBOURHOOD: a block of rooms wall to wall off one hub.**",
                           "            PruneUnroutableLinks(rooms, depth);")
block = text[start:end]
text = text[:start] + text[end:]

block = block.replace(
    "            // **THE NEIGHBOURHOOD: a block of rooms wall to wall off one hub.** Owner, same",
    "            // **THE NEIGHBOURHOOD: a block of rooms wall to wall off one hub, formed WHILE"
    + NL + "            // THE ROOMS CAN STILL MOVE.** Owner, same")

block = block.replace(
    """            // which rooms to offer; it relaxes nothing.**""",
    """            // which rooms to offer; it relaxes nothing.**
            //
            // **AND IT RUNS HERE, BEFORE THE DIAGONAL AND REACH BRAIDS, WHICH THE PROBE INSISTED
            // ON.** Written after them it measured as a no-op: the largest wall-to-wall group came
            // out at 3 with it and 3 without. A room holding five or six links cannot slide at
            // all, because `PushAgainst` undoes any move that carries one of them past
            // `FurthestLinkedCentres` -- so by the time a hub was picked, nothing around it was
            // mobile. At this point a room holds about two and a half links and a push lands; the
            // braids that follow route to where the rooms ended up. That is the right order
            // anyway, because the arrangement is part of the layout rather than a nudge applied to
            // a finished one.""")

block = block.replace(
    """                for (int index = 0; index < rooms[hub].links.Count; index++)
                {
                    int neighbour = rooms[hub].links[index];
                    if (neighbour == 0 || neighbour == hub) { continue; }
                    RoomRecord mover = rooms.FirstOrDefault(r => r != null && r.index == neighbour);
                    if (mover == null || SharesWall(mover, rooms[hub])) { continue; }
                    PushAgainst(rooms, mover, rooms[hub], depth);
                }""",
    """                // **LEAST-CONNECTED FIRST.** `PushAgainst` undoes a move that breaks an
                // existing link's route or carries one past `FurthestLinkedCentres`, and a move is
                // most of a room's own span -- so the more links a room holds the likelier it is
                // to snap straight back. Offered in whatever order the link list happened to be
                // in, the hopeless ones shifted the geometry before the mobile ones were tried.
                var terrace = new List<RoomRecord>();
                for (int index = 0; index < rooms[hub].links.Count; index++)
                {
                    int neighbour = rooms[hub].links[index];
                    if (neighbour == 0 || neighbour == hub) { continue; }
                    RoomRecord mover = rooms.FirstOrDefault(r => r != null && r.index == neighbour);
                    if (mover == null || mover.links == null || SharesWall(mover, rooms[hub]))
                    { continue; }
                    terrace.Add(mover);
                }
                terrace.Sort((left, right) => left.links.Count != right.links.Count
                    ? left.links.Count - right.links.Count
                    : left.index - right.index);
                for (int index = 0; index < terrace.Count; index++)
                { PushAgainst(rooms, terrace[index], rooms[hub], depth); }""")

anchor = "            // **THE DIAGONAL BRAID, AND IT IS WHAT ANSWERS THE DEGREE COMPLAINT.**"
if text.count(anchor) != 1:
    print("diagonal braid anchor not unique")
    sys.exit(1)
text = text.replace(anchor, block + anchor)
print("B: neighbourhood moved ahead of the diagonal and reach braids")

# ------------------------------------------------------------- C. the prune becomes exact
PRUNE = '''        private static void PruneUnroutableLinks(List<RoomRecord> rooms, int depth)
        {
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null || room.links == null) { continue; }
                for (int at = room.links.Count - 1; at >= 0; at--)
                {
                    int otherIndex = room.links[at];
                    if (otherIndex <= room.index) { continue; }
                    RoomRecord other = rooms.FirstOrDefault(r => r != null && r.index == otherIndex);
                    if (other == null || SharesWall(room, other)) { continue; }
                    int legDepth = Math.Max(ShapeDepthOf(rooms, room, depth),
                        ShapeDepthOf(rooms, other, depth));
                    if (CorridorLegs(room, other, legDepth, rooms).Count > 0) { continue; }
                    // **TAKEN OUT, THEN PUT BACK IF THE PLACE FELL APART.** This refused to touch
                    // anything whose centres shared an axis, on the reasoning that the spanning
                    // tree is entirely non-diagonal so removing only diagonals cannot disconnect
                    // the level. True, and too coarse: the reach braid makes links two slots apart
                    // ALONG an axis, and the neighbourhood push can leave one of those with no
                    // route. The clause skipped it, `CandidateIsSafe` then refused the whole
                    // layout, and the probe printed `link 2-6 has no route under it`.
                    //
                    // Asking directly is exact and easier to reason about: remove the edge, and
                    // keep the removal only if every room still claiming a route can still be
                    // reached from the threshold. A load-bearing link stays and the candidate is
                    // refused -- which is correct, and the next candidate answers it.
                    room.links.RemoveAt(at);
                    other.links.Remove(room.index);
                    if (LinkedGraphIsWhole(rooms)) { continue; }
                    room.links.Insert(at > room.links.Count ? room.links.Count : at, otherIndex);
                    other.links.Add(room.index);
                }
            }
        }

        /// <summary>
        /// Whether every room that claims a route can still be reached from the threshold.
        ///
        /// The same question `DestinationService.ValidateRooms` asks of a saved graph, asked here
        /// of one being built, so a removal cannot produce a layout the validator would refuse. A
        /// room with no links is a sealed vault and is deliberately not expected to be reachable
        /// across floor -- see <see cref="SealedFamily"/>.
        /// </summary>
        private static bool LinkedGraphIsWhole(List<RoomRecord> rooms)
        {
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int index = 0; index < rooms.Count; index++)
            {
                if (rooms[index] != null) { byIndex[rooms[index].index] = rooms[index]; }
            }
            if (!byIndex.ContainsKey(0)) { return false; }
            var seen = new HashSet<int> { 0 };
            var pending = new Queue<int>();
            pending.Enqueue(0);
            while (pending.Count > 0)
            {
                RoomRecord current;
                if (!byIndex.TryGetValue(pending.Dequeue(), out current) || current.links == null)
                { continue; }
                for (int index = 0; index < current.links.Count; index++)
                {
                    if (seen.Add(current.links[index])) { pending.Enqueue(current.links[index]); }
                }
            }
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null || room.links == null || room.links.Count == 0) { continue; }
                if (!seen.Contains(room.index)) { return false; }
            }
            return true;
        }
'''
start, end = slice_between(
    text,
    "        private static void PruneUnroutableLinks(List<RoomRecord> rooms, int depth)",
    "        /// Who each room is, once the maze exists.")
text = text[:start] + PRUNE + NL + text[end:]
print("C: prune is now exact")

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text)
occurrences = text.count("PruneUnroutableLinks")
print("PruneUnroutableLinks occurrences: %d (expect 4)" % occurrences)
if occurrences != 4:
    print("FILE LOOKS WRONG -- do not build")
    sys.exit(1)
