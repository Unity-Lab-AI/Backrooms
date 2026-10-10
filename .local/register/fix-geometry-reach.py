# -*- coding: utf-8 -*-
"""Three shape systems were all switched off at depth 1, so every first-level room was a box.

Owner, verbatim: *"and you can have back to back roomes and mazes of halways of varied widtchs
and lengs and odd variers walls and contructions making narrows , expansies, triangle, octangones,
rombones, all the geomentry and mixetrues and odd contructions of doors walls corners deadends
doors to now where not just doors on 4 cosides of nothing but square rooms"*.

**THE MACHINERY WAS ALREADY WRITTEN AND ALL OF IT WAS OFF.** Three separate systems, each with
the same first line:

    RockIntrusionCells      if (room == null || depth <= 1) { yield break; }
    CorridorHalfWidthBetween  if (first == null || second == null || depth <= 1) { return 2; }
    Derange                 only when GetRoomLibraryVersion >= 2

`RockIntrusionCells` fills a room's corners with quarter-ellipses -- fill two adjacent and you
have a trapezoid, two opposite and you have a rhombus, all four and you have an octagon, which is
most of the list the owner just gave. `CorridorHalfWidthBetween` varies hallway width between
three cells and five. **None of it could run on the level the owner walked.**

So shape asks what the dressing, the inhabitants and the walls now ask: **how far is this room
from the spawn hall?** The hall and its neighbours stay square and plain -- that is the arrival,
and it should read as the one built thing. Everything beyond gets corners eaten, widths varied
and proportions deranged, more so the further out it is.

**ONE FUNCTION, BOTH READERS.** `ShapeDepthOf` is called by the generator, which carves the rock,
and by `CandidateIsSafe`, which proves the room is still walkable with it carved. Two readers
deriving the same lattice independently is exactly the defect that stopped every coordinate
generating from 0.7.8-dev to 0.12.47-dev, and a shaped room the validator believed was square
would be the same bug with a prettier outline.

Measured over the planner's own room list rather than a saved field, so it needs no save-format
change and works on every coordinate already recorded.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

HELPER_ANCHOR = u"        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)"

HELPER = u'''        /// <summary>Links walked before a room counts as one level deeper, for shaping.</summary>
        internal const int LinksPerShapeBand = 3;

        /// <summary>The most distance can add to a room's shaping depth.</summary>
        internal const int MaximumShapeBand = 4;

        /// <summary>
        /// The depth this room is SHAPED at: the coordinate's own, plus how far it is from the
        /// spawn hall.
        ///
        /// Owner: *"you can have back to back roomes and mazes of halways of varied widtchs and
        /// lengs ... triangle, octangones, rombones, all the geomentry"*, and *"not just doors on
        /// 4 cosides of nothing but square rooms"*.
        ///
        /// **Every shape system in this file refused to run at depth 1**, so the level the owner
        /// walked was all rectangles with identical corridors. The hall and its neighbours should
        /// stay square -- that is the arrival, and it is meant to read as the one built thing --
        /// and everything past it should come apart. Distance is what says which is which.
        ///
        /// **Called by both readers.** The generator carves rock from it and `CandidateIsSafe`
        /// proves the room walkable against it; a shaped room the validator believed was square
        /// is the defect that stopped every coordinate generating for thirty-nine checkpoints,
        /// wearing a prettier outline.
        /// </summary>
        internal static int ShapeDepthOf(List<RoomRecord> rooms, RoomRecord room, int depth)
        {
            if (rooms == null || room == null) { return depth; }
            int hops = HopsTo(rooms, room.index);
            if (hops < 0) { return depth; }
            int band = hops / LinksPerShapeBand;
            if (band > MaximumShapeBand) { band = MaximumShapeBand; }
            return depth + band;
        }

        /// <summary>Links from the threshold room to this one, or -1 when unreachable.</summary>
        private static int HopsTo(List<RoomRecord> rooms, int roomIndex)
        {
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int index = 0; index < rooms.Count; index++)
            {
                if (rooms[index] != null) { byIndex[rooms[index].index] = rooms[index]; }
            }
            if (!byIndex.ContainsKey(0)) { return -1; }
            var seen = new Dictionary<int, int> { { 0, 0 } };
            var pending = new Queue<int>();
            pending.Enqueue(0);
            while (pending.Count > 0)
            {
                int current = pending.Dequeue();
                if (current == roomIndex) { return seen[current]; }
                RoomRecord room;
                if (!byIndex.TryGetValue(current, out room) || room.links == null) { continue; }
                for (int index = 0; index < room.links.Count; index++)
                {
                    int next = room.links[index];
                    if (seen.ContainsKey(next) || !byIndex.ContainsKey(next)) { continue; }
                    seen[next] = seen[current] + 1;
                    pending.Enqueue(next);
                }
            }
            int found;
            return seen.TryGetValue(roomIndex, out found) ? found : -1;
        }

        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)'''

text = io.open(PLANNER, encoding="utf-8").read()
if text.count(HELPER_ANCHOR) != 1:
    print("PLANNER ANCHOR PROBLEM: %d" % text.count(HELPER_ANCHOR))
    raise SystemExit(1)
text = text.replace(HELPER_ANCHOR, HELPER, 1)

# CandidateIsSafe shapes with the same number the generator will.
SAFE_OLD = u'''                foreach (IntVec3 rock in RockIntrusionCells(room, depth))
                { floor[rock.x, rock.z] = false; }'''
SAFE_NEW = u'''                // The SAME shaping depth the generator will carve with. Passing the
                // coordinate's own depth here while the generator used a per-room one would be
                // a validator proving a room that is not the room that gets built.
                foreach (IntVec3 rock in RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth)))
                { floor[rock.x, rock.z] = false; }'''
if text.count(SAFE_OLD) != 1:
    print("SAFE ANCHOR PROBLEM: %d" % text.count(SAFE_OLD))
    raise SystemExit(1)
text = text.replace(SAFE_OLD, SAFE_NEW, 1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(text)
print("ShapeDepthOf added; the validator shapes with it")

GEN_OLD = u'''                var intrusions = new HashSet<IntVec3>(
                    RoomLayoutPlanner.RockIntrusionCells(room, coordinateDepth));'''
GEN_NEW = u'''                // Shaped by how far this room is from the spawn hall, not by the
                // coordinate's own depth -- which switched every shape system off on level 0 and
                // made the first level all rectangles. The SAME call CandidateIsSafe made when
                // it proved this room walkable.
                var intrusions = new HashSet<IntVec3>(
                    RoomLayoutPlanner.RockIntrusionCells(room,
                        RoomLayoutPlanner.ShapeDepthOf(coordinate.Rooms, room, coordinateDepth)));'''
gen = io.open(GEN, encoding="utf-8").read()
if gen.count(GEN_OLD) != 1:
    print("GEN ANCHOR PROBLEM: %d" % gen.count(GEN_OLD))
    raise SystemExit(1)
io.open(GEN, "w", encoding="utf-8", newline="").write(gen.replace(GEN_OLD, GEN_NEW, 1))
print("the generator carves with it too")
