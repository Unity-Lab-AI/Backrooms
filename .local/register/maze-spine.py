# -*- coding: utf-8 -*-
"""Every level becomes a maze. The owner named the algorithm without seeing it.

> *"all the backrooms so far are just one lone strain of perals arangement that snakes back and
> forth across the map like one series line... i want them to be mazes like xcrazy like all levels
> mazes do you unerstand! lsd crazy shaped mazes"*

**That is a description of the code.** `Build` walked the slot grid row-major with alternating
direction, called it *"the serpentine"* in its own comment, and linked room N to room N-1. One
line that snakes back and forth. Every branch was a one-room dead end hung off it afterwards, so
the topology was a spine with alcoves -- which reads as a single route however many rooms it has,
because it **is** a single route.

## What replaces it

A **randomised depth-first maze** over the slot grid, grown from the hall, then **braided**.

  * The carve order at each slot is a rotation chosen from that slot's own hash, so the walk turns
    unpredictably instead of sweeping. This is what makes it branch everywhere rather than snake.
  * Every visited slot is a room linked to the slot the walk came from, so the graph is a
    **spanning tree**: connected by construction, which is what `CandidateIsSafe` needs, with no
    pathfinding anywhere in the planner.
  * **Then the braid**, and this is the part that makes it a maze rather than a tree: adjacent
    rooms that the walk left unconnected get linked back with a one-in-three draw. A pure tree has
    exactly one route between any two rooms -- walk it wrong and you backtrack. A braided maze has
    loops, junctions that lie, and corridors that rejoin somewhere you did not expect.

**Every link is still between grid-adjacent slots**, which is the invariant everything else rests
on: `AreGridNeighbors` requires linked rooms' centres to share a row or a column, and the corridor
builder carves straight between centres. A maze on the grid satisfies that for free; this is why
the maze is over the slot grid and not over cells.

## What the families become

The hall is index 0. The **deepest room the walk reached** is the way home -- in a maze that is a
genuinely distant place rather than the end of a line. One room in the middle is the office copy.
**Every dead end becomes a storage nook or a utility room**, because in a maze dead ends are
plentiful and that is exactly what those families are for; the rest cycle the repeating families
with `service_passage` guaranteed, which `ValidateRooms` requires.

Back-to-back pairs are still only ever dead ends pushed against their single neighbour, for the
same reason as before: a room with one link cannot re-route anything by moving.

## The fallback stays a serpentine, deliberately

`FallbackCandidate` is the safety net -- the layout taken when all three candidates are refused.
It keeps the old simple walk, because the thing you fall back to should be the thing with the
fewest ways to be surprising.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")

OLD_START = u"""            // The serpentine: row-major with alternating direction, so consecutive entries are
            // always grid neighbours and the chain needs no pathfinding to be connected."""
OLD_END = u"""            return rooms;
        }

        /// <summary>
        /// Index 0 is the threshold, the last chain room is the way home, and one room in the
        /// middle is the office copy."""

NEW = u'''            // The serpentine, kept for the FALLBACK CANDIDATE ONLY: row-major with alternating
            // direction, so consecutive entries are always grid neighbours. It is the layout
            // taken when all three real candidates are refused, and the thing you fall back to
            // should be the thing with the fewest ways to be surprising.
            var order = new List<IntVec2>();
            for (int row = 0; row < slots; row++)
            {
                for (int column = 0; column < slots; column++)
                {
                    int x = row % 2 == 0 ? column : slots - 1 - column;
                    order.Add(new IntVec2(x, row));
                }
            }

            if (fallback) { return BuildSerpentine(coordinate, order, spacing, seed, depth); }
            return BuildMaze(coordinate, slots, spacing, seed, depth);
        }

        /// <summary>How many adjacent pairs the maze walk left unlinked get linked back.</summary>
        internal const int BraidRarity = 3;

        /// <summary>
        /// A randomised depth-first maze over the slot grid, grown from the hall, then braided.
        ///
        /// ## What this replaced, and the owner described it exactly
        ///
        /// *"all the backrooms so far are just one lone strain of perals arangement that snakes
        /// back and forth across the map like one series line... i want them to be mazes like
        /// xcrazy like all levels mazes do you unerstand!"*
        ///
        /// The spine was a **serpentine**: the slot grid walked row-major with alternating
        /// direction, room N linked to room N-1. One line that snakes back and forth, by
        /// construction and by its own comment. Dead ends were hung off it afterwards, so the
        /// topology was a corridor with alcoves -- which reads as a single route however many
        /// rooms it has, because it is one.
        ///
        /// ## Why a depth-first maze, and why braided
        ///
        /// The carve order at each slot is rotated by that slot's own hash, so the walk turns
        /// unpredictably instead of sweeping, and it branches everywhere. Every visited slot links
        /// to the slot the walk arrived from, so the result is a **spanning tree** -- connected by
        /// construction, which is exactly what `CandidateIsSafe` has to prove, with no
        /// pathfinding anywhere in the planner.
        ///
        /// **Then the braid, which is what makes it a maze rather than a tree.** A pure tree has
        /// exactly one route between any two rooms: walk it wrong and you backtrack. Linking back
        /// one in <see cref="BraidRarity"/> of the adjacent pairs the walk left alone gives loops,
        /// junctions that lie, and corridors that rejoin somewhere unexpected.
        ///
        /// ## The invariant this is built to respect
        ///
        /// **Every link is between grid-adjacent slots.** `AreGridNeighbors` requires linked
        /// rooms' centres to share a row or a column, and `BuildCorridors` carves straight between
        /// those centres. A maze over the SLOT GRID satisfies that for free -- which is why the
        /// maze is over slots and not over cells.
        ///
        /// Deterministic throughout: every choice comes from `DestinationService.StableHash` over
        /// the coordinate's own seed, so a level is the same maze every time it is visited.
        /// </summary>
        private static List<RoomRecord> BuildMaze(CoordinateRecord coordinate, int slots,
            int spacing, int seed, int depth)
        {
            var rooms = new List<RoomRecord>();
            // **THE GRAND HALL YOU ARRIVE IN, AND THEN THE MAZE.** Owner: *"the normal yellow
            // backrooms look isnt the whole floor but the main spanw room"*. The threshold takes
            // TWO adjacent slots, so at depth 1 it is about eighty cells across while everything
            // past it is a third of that.
            var hallFirst = new IntVec2(0, 0);
            var hallSecond = new IntVec2(1, 0);
            rooms.Add(MakeHall(coordinate, hallFirst, hallSecond, spacing, seed, depth));

            // slotOf[slot] is the room index standing in it, or absent.
            var slotOf = new Dictionary<IntVec2, int> { { hallFirst, 0 }, { hallSecond, 0 } };
            var hops = new Dictionary<int, int> { { 0, 0 } };

            // The walk. An explicit stack rather than recursion: a ten-by-ten grid is a hundred
            // frames deep in the worst case and this runs during map generation.
            var stack = new List<IntVec2> { hallSecond };
            IntVec2[] directions =
            {
                new IntVec2(1, 0), new IntVec2(0, 1), new IntVec2(-1, 0), new IntVec2(0, -1),
            };
            int budget = MaxRooms;

            while (stack.Count > 0 && rooms.Count < budget)
            {
                IntVec2 current = stack[stack.Count - 1];
                // The rotation is what stops this being a sweep. Taken from the slot itself, so
                // the same coordinate always turns the same way.
                int turn = DestinationService.StableHash(seed,
                    "maze:" + current.x + "," + current.z, depth);
                if (turn < 0) { turn = ~turn; }

                bool advanced = false;
                for (int step = 0; step < directions.Length; step++)
                {
                    IntVec2 direction = directions[(turn + step) % directions.Length];
                    var next = new IntVec2(current.x + direction.x, current.z + direction.z);
                    if (next.x < 0 || next.z < 0 || next.x >= slots || next.z >= slots) { continue; }
                    if (slotOf.ContainsKey(next)) { continue; }

                    int parent = slotOf[current];
                    var room = MakeRoom(coordinate, rooms.Count, "survey_lobby", next, spacing,
                        VariedRoomSpan(spacing, next, seed, depth), seed, false, depth);
                    rooms.Add(room);
                    slotOf[next] = room.index;
                    hops[room.index] = hops[parent] + 1;
                    Link(rooms, room.index, parent);
                    stack.Add(next);
                    advanced = true;
                    break;
                }
                if (!advanced) { stack.RemoveAt(stack.Count - 1); }
            }

            // **THE BRAID.** Adjacent rooms the walk left unconnected, linked back one in three.
            // Without this the maze is a tree and there is exactly one route between any two
            // rooms; with it there are loops and junctions that lie. Ordered by slot so the set
            // of braids is the same on every visit.
            var slotList = new List<IntVec2>(slotOf.Keys);
            slotList.Sort(delegate (IntVec2 left, IntVec2 right)
            {
                if (left.z != right.z) { return left.z - right.z; }
                return left.x - right.x;
            });
            for (int index = 0; index < slotList.Count; index++)
            {
                IntVec2 slot = slotList[index];
                int here = slotOf[slot];
                // East and north only: every pair is then considered exactly once.
                for (int side = 0; side < 2; side++)
                {
                    var next = side == 0
                        ? new IntVec2(slot.x + 1, slot.z) : new IntVec2(slot.x, slot.z + 1);
                    int there;
                    if (!slotOf.TryGetValue(next, out there) || there == here) { continue; }
                    if (rooms[here].links.Contains(there)) { continue; }
                    int roll = DestinationService.StableHash(seed,
                        "braid:" + slot.x + "," + slot.z + ":" + side, depth);
                    if (roll < 0) { roll = ~roll; }
                    if (roll % BraidRarity != 0) { continue; }
                    // The corridor builder needs the two centres to share an axis, which the
                    // hall's two-slot span can break. `AreNeighbourRooms` is the same question
                    // `ValidateRooms` will ask, so a braid it would refuse is never made.
                    if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }
                    Link(rooms, here, there);
                }
            }

            AssignMazeFamilies(rooms, hops, seed);

            // **BACK TO BACK**, and still only ever a dead end. Owner: *"and you can have back to
            // back roomes"*. A room with one link cannot re-route anything by moving.
            for (int index = 1; index < rooms.Count; index++)
            {
                if (rooms[index].links.Count != 1) { continue; }
                int host = rooms[index].links[0];
                if (host == 0) { continue; }
                int roll = DestinationService.StableHash(seed,
                    "backtoback:" + rooms[index].x + "," + rooms[index].z, depth);
                if (roll < 0) { roll = ~roll; }
                if (roll % 3 != 0) { continue; }
                PushAgainst(rooms, rooms[index], rooms[host]);
            }
            return rooms;
        }

        /// <summary>
        /// Who each room is, once the maze exists.
        ///
        /// The three unique families are unique because something depends on there being exactly
        /// one: the gate anchor, the evidence book, and the way out. `ValidateRooms` refuses a
        /// graph that has two of any of them or none of `service_passage`.
        ///
        /// **The way home is the deepest room the walk reached**, which in a maze is a genuinely
        /// distant place rather than the end of a line. **Every dead end becomes a storage nook or
        /// a utility room**, because a maze has dead ends in quantity and that is precisely what
        /// those two families are -- and `CandidateIsSafe` asserts both of them have exactly one
        /// link, which a dead end does by definition.
        /// </summary>
        private static void AssignMazeFamilies(List<RoomRecord> rooms, Dictionary<int, int> hops,
            int seed)
        {
            rooms[0].familyId = UniqueFamilies[0];
            if (rooms.Count < 2) { return; }

            int deepest = 1;
            for (int index = 1; index < rooms.Count; index++)
            {
                int far;
                int best;
                if (!hops.TryGetValue(index, out far)) { continue; }
                if (!hops.TryGetValue(deepest, out best) || far > best) { deepest = index; }
            }

            // The office copy is never the way home and never the hall, and it is a room with
            // more than one link where one exists: the evidence book should be somewhere a crew
            // passes through rather than at the end of a cul-de-sac.
            int office = -1;
            for (int offset = 0; offset < rooms.Count; offset++)
            {
                int index = 1 + (Math.Abs(seed / 23) + offset) % Math.Max(1, rooms.Count - 1);
                if (index == deepest || rooms[index].links.Count < 2) { continue; }
                office = index;
                break;
            }
            if (office < 0) { office = deepest == 1 && rooms.Count > 2 ? 2 : 1; }

            for (int index = 1; index < rooms.Count; index++)
            {
                if (index == deepest) { rooms[index].familyId = UniqueFamilies[2]; continue; }
                if (index == office) { rooms[index].familyId = UniqueFamilies[1]; continue; }
                if (rooms[index].links.Count == 1)
                {
                    rooms[index].familyId = SpurFamilies[index % SpurFamilies.Length];
                    continue;
                }
                rooms[index].familyId = ChainFamilies[Math.Abs(seed / 7 + index) % ChainFamilies.Length];
            }

            // `service_passage` must appear at least once: the generator's climate room is
            // FirstOrDefault(utility_room) ?? First(service_passage), and the second half of that
            // throws when there is none. `ValidateRooms` refuses the graph as well.
            bool hasPassage = false;
            for (int index = 0; index < rooms.Count; index++)
            {
                if (rooms[index].familyId == "service_passage") { hasPassage = true; break; }
            }
            if (hasPassage) { return; }
            for (int index = 1; index < rooms.Count; index++)
            {
                if (index == deepest || index == office || rooms[index].links.Count == 1) { continue; }
                rooms[index].familyId = "service_passage";
                return;
            }
            // A maze of nothing but dead ends and two unique rooms is not a maze this can happen
            // to at any depth the planner produces, but if it ever did, the passage has to exist.
            for (int index = 1; index < rooms.Count; index++)
            {
                if (index == deepest || index == office) { continue; }
                rooms[index].familyId = "service_passage";
                return;
            }
        }

        /// <summary>
        /// The old serpentine, kept for the fallback candidate alone. See <see cref="BuildMaze"/>
        /// for why it is no longer what a level looks like.
        /// </summary>
        private static List<RoomRecord> BuildSerpentine(CoordinateRecord coordinate,
            List<IntVec2> order, int spacing, int seed, int depth)
        {
            int chainLength = MinSlotsPerAxis * MinSlotsPerAxis * 2 / 3;
            if (chainLength < 6) { chainLength = 6; }
            if (chainLength > MaxRooms * 2 / 3) { chainLength = MaxRooms * 2 / 3; }
            if (chainLength > order.Count) { chainLength = order.Count; }

            var rooms = new List<RoomRecord>();
            var taken = new HashSet<IntVec2>();
            for (int index = 0; index < order.Count && rooms.Count < chainLength; index++)
            {
                IntVec2 slot = order[index];
                if (!taken.Add(slot)) { continue; }
                string family = ChainFamilyFor(rooms.Count, chainLength, seed);
                rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,
                    VariedRoomSpan(spacing, slot, seed, depth), seed, true, depth));
            }
            for (int index = 1; index < rooms.Count; index++) { Link(rooms, index - 1, index); }
            if (AreNeighbourRooms(rooms[0], rooms[rooms.Count - 1]) &&
                !rooms[0].links.Contains(rooms.Count - 1))
            { Link(rooms, rooms.Count - 1, 0); }
            return rooms;
        }

        /// <summary>
        /// Index 0 is the threshold, the last chain room is the way home, and one room in the
        /// middle is the office copy."""'''

text = io.open(PLANNER, encoding="utf-8").read()
start = text.index(OLD_START)
end = text.index(OLD_END)
old = text[start:end]
if u"The serpentine: row-major" not in old or u"PushAgainst(rooms, rooms[rooms.Count - 1]" not in old:
    print("REPLACED REGION LOOKS WRONG: %r" % old[:160])
    raise SystemExit(1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(
    text[:start] + NEW + text[end + len(OLD_END):])
print("the spine is a braided maze; the serpentine survives as the fallback (%d lines replaced)"
      % old.count("\n"))
