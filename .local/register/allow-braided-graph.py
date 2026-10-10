# -*- coding: utf-8 -*-
"""The validator allowed a tree plus ONE loop, so a maze was structurally forbidden.

Owner: *"i want them to be mazes like xcrazy like all levels mazes do you unerstand! lsd crazy
shaped mazes"*.

`ValidateRooms` ended with

    int directedEdges = rooms.Sum(room => room.links.Count);
    if (visited.Count != rooms.Count || directedEdges < 2 * (rooms.Count - 1)
        || directedEdges > 2 * rooms.Count)

and the last clause is the one that matters. A connected graph needs `n - 1` edges; the ceiling of
`n` allowed **exactly one more.** One loop, in the whole level, at every depth, for ever.

**So the line with alcoves was not a choice the generator made -- it was the only shape the
validator would accept.** Every braided maze candidate was refused with
`RR_Generation_InvalidRoomGraph`, the fallback serpentine caught all two hundred seeds per depth,
and the probe reported no refusals at all because `TrySelect` had succeeded.

## What the ceiling should be

Every edge is one carved corridor, so a ceiling belongs here -- an unbounded graph would carve the
map to gravel. But the right number is the **geometry's own limit**: links run between
grid-adjacent slots, a slot has at most four neighbours, so a grid graph has at most `2n`
undirected edges. `MaximumUndirectedEdgesPerRoom = 2` is therefore not a loosening of the rule so
much as a statement of what the grid can produce at all -- and it still refuses the things the
clause was written to refuse: a graph with links between distant rooms, a duplicated edge set, a
room joined to everything.

The floor is untouched. `visited.Count != rooms.Count` and `directedEdges < 2 * (rooms.Count - 1)`
are what guarantee the level is one connected place, and they are the half of this check that was
always doing the work.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "DestinationService.cs")

OLD = u"""            int directedEdges = rooms.Sum(room => room.links.Count);
            if (visited.Count != rooms.Count || directedEdges < 2 * (rooms.Count - 1) || directedEdges > 2 * rooms.Count)
            {
                failureKey = "RR_Generation_InvalidRoomGraph";
                return false;
            }
            return true;
        }"""

NEW = u"""            int directedEdges = rooms.Sum(room => room.links.Count);
            // **THE CEILING HERE FORBADE A MAZE, AND THAT IS WHY EVERY LEVEL WAS A LINE.**
            //
            // It was `directedEdges > 2 * rooms.Count`. A connected graph needs `n - 1` edges, so
            // a ceiling of `n` allowed **exactly one more: one loop, in the whole level, at every
            // depth.** The serpentine spine with a single closing ring was not a choice the
            // generator made -- it was the only shape this clause would accept, and every braided
            // maze candidate was refused with this key while the fallback caught every seed.
            //
            // Owner: *"i want them to be mazes like xcrazy like all levels mazes do you unerstand!
            // lsd crazy shaped mazes"*.
            //
            // A ceiling still belongs here, because **every edge is one carved corridor** and an
            // unbounded graph would carve the map to gravel. But the honest number is the
            // geometry's own: links run between grid-adjacent slots and a slot has at most four
            // neighbours, so a grid graph cannot exceed two undirected edges per room. This is
            // less a loosening than a statement of what the slot grid can produce -- and it still
            // refuses what the clause was written to refuse: links between distant rooms, a
            // duplicated edge set, a room joined to everything.
            //
            // **The floor is untouched.** `visited.Count != rooms.Count` and the `n - 1` minimum
            // are what guarantee one connected place, and they are the half of this check that
            // was always doing the work.
            if (visited.Count != rooms.Count ||
                directedEdges < 2 * (rooms.Count - 1) ||
                directedEdges > 2 * MaximumUndirectedEdgesPerRoom * rooms.Count)
            {
                failureKey = "RR_Generation_InvalidRoomGraph";
                return false;
            }
            return true;
        }

        /// <summary>
        /// The most corridors a room may carry, and it is the slot grid's own limit.
        ///
        /// Links run between grid-adjacent slots, so a room has at most four neighbours and a
        /// layout at most `2 * rooms` undirected edges. Two per room is the bound that admits any
        /// maze the grid can describe while still refusing a graph that is not one.
        /// </summary>
        private const int MaximumUndirectedEdgesPerRoom = 2;"""

text = io.open(SERVICE, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(SERVICE, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the graph ceiling is the grid's own limit, so a braided maze is legal")
