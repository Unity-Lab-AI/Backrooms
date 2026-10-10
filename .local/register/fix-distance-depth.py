# -*- coding: utf-8 -*-
"""Distance from the spawn hall counts as depth, so the first level stops being empty.

Owner, after walking it: *"not enough loot"*, *"not enough weird stuff like a room with a lost
person or a room full of bodies or suppplies or a labratory ofr class room or hospital of
manufactuing room or tool sheed or weapons locker"*, and the shape they want:

    *"the normal yellow backrooms look isnt the whole floor but the main spanw room and going
     deeping in can mean the numner of branch hallways and rooms distancing from the main portal
     spawn in the back rooms continuw on into the map with variations and oddity and events and
     locations and places that vary more even on the first level"*

WHY THERE WAS NOTHING TO FIND, AND THE FILE SAYS IT OUT LOUD. `RR_RoomArchetypes.xml` opens with

    minDepth is what keeps the shallow yellow rooms empty. Nothing here can appear at [depth 1]

and every one of the fourteen archetypes declares `minDepth` of 2 or more. `Select` enforces it
with `if (depth <= 1) { return null; }`. **So a first level has exactly zero archetypes, by
design** -- no laboratory, no ward, no storeroom, no salvage, no loot. The owner explored a level
that was built to be empty.

THE FIX IS NOT "TURN IT OFF", IT IS THE OWNER'S OWN SENTENCE MADE LITERAL. **Distance from the
spawn hall counts as depth.** A room three links from the threshold is dressed as though it were
one level deeper; six links as two deeper; and so on. So on a single first level:

    hops 0-2   ->  effective depth 1  ->  nothing. The yellow rooms, as they are now
    hops 3-5   ->  effective depth 2  ->  laboratory, workshop, dormitory, canteen, storeroom,
                                          office, salvage
    hops 6-8   ->  effective depth 3  ->  and nursery, machine hall, ward
    hops 9-11  ->  effective depth 4  ->  and gallery, duplicate
    hops 12+   ->  effective depth 5  ->  and wrong, hoard

**The yellow look is the hall and its neighbours, and it gets stranger the further you walk** --
which is what *"the normal yellow backrooms look isnt the whole floor but the main spanw room"*
asks for, and it needed no new content at all: fourteen archetypes were already written and the
first level could not reach any of them.

Measured in LINKS, not in cells. The link graph is what a player actually walks, so a room on the
far side of the map that happens to be two doors from the hall is still near it -- which is the
honest reading of *"distancing from the main portal spawn"*.

Capped, because a first level that reached the deepest content at its far edge would leave
nothing for the sixth. Deeper coordinates start higher and reach the same ceiling sooner, so
depth still means something on its own.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomArchetypeService.cs")
BUILDER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomContentBuilder.cs")

# --------------------------------------------------------------------------- #
# The helper, on the service beside the selector it feeds.
# --------------------------------------------------------------------------- #
HELPER_ANCHOR = u"        public static RimroomsRoomArchetypeDef Select(string familyId, int depth, int seed,"

HELPER = u'''        /// <summary>Links walked before a room counts as one level deeper.</summary>
        public const int LinksPerDepthBand = 3;

        /// <summary>The most a room's distance can add to its depth.</summary>
        public const int MaximumDistanceBand = 4;

        /// <summary>
        /// **Distance from the spawn hall counts as depth.** Owner: *"the normal yellow backrooms
        /// look isnt the whole floor but the main spanw room and going deeping in can mean the
        /// numner of branch hallways and rooms distancing from the main portal spawn ... with
        /// variations and oddity ... even on the first level"*.
        ///
        /// Every archetype declares `minDepth` of 2 or more and `Select` refuses depth 1
        /// outright, so a first level was **built to be empty** and the owner walked one and said
        /// so. Rather than lowering fourteen thresholds, the room's own distance is added to the
        /// depth: near the hall nothing qualifies and the yellow rooms stay yellow, and the
        /// further out a room is the more of the existing library it can reach.
        ///
        /// Measured in LINKS, because the link graph is what a player walks -- a room across the
        /// map that is two doors from the hall is still near it.
        ///
        /// Capped, so a first level cannot reach the deepest content at its far edge and leave
        /// nothing for the sixth.
        /// </summary>
        public static int EffectiveDepth(CoordinateRecord coordinate, RoomRecord room, int depth)
        {
            if (coordinate == null || room == null) { return depth; }
            int hops = HopsFromThreshold(coordinate, room.Index);
            if (hops < 0) { return depth; }
            int band = hops / LinksPerDepthBand;
            if (band > MaximumDistanceBand) { band = MaximumDistanceBand; }
            return depth + band;
        }

        /// <summary>
        /// Links from the threshold room to this one, or -1 when it cannot be reached.
        ///
        /// Breadth-first over the saved link graph, cached per coordinate because every room in
        /// the level asks the same question during one dressing pass.
        /// </summary>
        private static int HopsFromThreshold(CoordinateRecord coordinate, int roomIndex)
        {
            Dictionary<int, int> hops;
            if (!hopCache.TryGetValue(coordinate.Id, out hops) || hops == null)
            {
                hops = MeasureHops(coordinate);
                hopCache[coordinate.Id] = hops;
            }
            int found;
            return hops.TryGetValue(roomIndex, out found) ? found : -1;
        }

        private static readonly Dictionary<string, Dictionary<int, int>> hopCache =
            new Dictionary<string, Dictionary<int, int>>();

        private static Dictionary<int, int> MeasureHops(CoordinateRecord coordinate)
        {
            var hops = new Dictionary<int, int>();
            if (coordinate.Rooms == null || coordinate.Rooms.Count == 0) { return hops; }
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int index = 0; index < coordinate.Rooms.Count; index++)
            {
                RoomRecord room = coordinate.Rooms[index];
                if (room != null) { byIndex[room.Index] = room; }
            }
            // The threshold is room zero: where the player arrives, and the hall everything is
            // measured from.
            if (!byIndex.ContainsKey(0)) { return hops; }
            var queue = new Queue<int>();
            queue.Enqueue(0);
            hops[0] = 0;
            while (queue.Count > 0)
            {
                int current = queue.Dequeue();
                RoomRecord room;
                if (!byIndex.TryGetValue(current, out room) || room.links == null) { continue; }
                for (int index = 0; index < room.links.Count; index++)
                {
                    int next = room.links[index];
                    if (hops.ContainsKey(next) || !byIndex.ContainsKey(next)) { continue; }
                    hops[next] = hops[current] + 1;
                    queue.Enqueue(next);
                }
            }
            return hops;
        }

        /// <summary>Forget the measured graphs; the maps they describe belong to another game.</summary>
        public static void ClearHopCache() { hopCache.Clear(); }

        public static RimroomsRoomArchetypeDef Select(string familyId, int depth, int seed,'''

text = io.open(SERVICE, encoding="utf-8").read()
if text.count(HELPER_ANCHOR) != 1:
    print("SERVICE ANCHOR PROBLEM: %d" % text.count(HELPER_ANCHOR))
    raise SystemExit(1)
text = text.replace(HELPER_ANCHOR, HELPER, 1)

for need in ("using System.Collections.Generic;", "using RimroomsAsyncIndustries.Company;"):
    if need not in text:
        text = text.replace("using System;", "using System;\n" + need, 1)
io.open(SERVICE, "w", encoding="utf-8", newline="").write(text)
print("effective depth added to the archetype service")

# --------------------------------------------------------------------------- #
# The caller passes the effective depth.
# --------------------------------------------------------------------------- #
CALL_OLD = u'''            RimroomsRoomArchetypeDef archetype =
                RoomArchetypeService.Select(dresser.familyId, depth, seed, dresser.index);'''
CALL_NEW = u'''            // **Distance from the spawn hall counts as depth.** A room beside the hall is
            // dressed as the shallow yellow rooms always were; one a dozen links out is dressed
            // like somewhere several levels down. Owner: *"variations and oddity and events and
            // locations and places that vary more even on the first level"*.
            int dressingDepth = RoomArchetypeService.EffectiveDepth(coordinate, dresser, depth);
            RimroomsRoomArchetypeDef archetype =
                RoomArchetypeService.Select(dresser.familyId, dressingDepth, seed, dresser.index);'''

builder = io.open(BUILDER, encoding="utf-8").read()
if builder.count(CALL_OLD) != 1:
    print("BUILDER ANCHOR PROBLEM: %d" % builder.count(CALL_OLD))
    raise SystemExit(1)
builder = builder.replace(CALL_OLD, CALL_NEW, 1)

# The depth-scaled resolution below it must use the same number, or a room would be chosen as
# deep and furnished as shallow.
RES_OLD = u"                    ThingDef definition = RoomArchetypeService.Resolve(archetype, slot, seed, index, depth);"
RES_NEW = u"                    ThingDef definition = RoomArchetypeService.Resolve(archetype, slot, seed, index, dressingDepth);"
if builder.count(RES_OLD) != 1:
    print("RESOLVE ANCHOR PROBLEM: %d" % builder.count(RES_OLD))
    raise SystemExit(1)
builder = builder.replace(RES_OLD, RES_NEW, 1)

io.open(BUILDER, "w", encoding="utf-8", newline="").write(builder)
print("the dressing uses it, and so does what it resolves")
