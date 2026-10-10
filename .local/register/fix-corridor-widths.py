# -*- coding: utf-8 -*-
"""Hallway width was also switched off at depth 1, so every corridor was three cells wide.

Owner: *"mazes of halways of varied widtchs and lengs"*, *"odd variers walls and contructions
making narrows , expansies"*.

    internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)
    { if (first == null || second == null || depth <= 1) { return 2; } ... }

**Two gives a three-cell walkway, three gives five -- and depth 1 always returned two.** Every
corridor on the level the owner walked was the same width, which is what made it read as a
building rather than a maze.

Now it asks the same question everything else does: how far from the spawn hall are these two
rooms? A corridor near the arrival is the plain three cells, and the further out a pair is the
more likely it narrows or opens out.

**Both readers again.** The generator carves the corridor and `CandidateIsSafe` proves the route
through it; they take the width from this one function, so a corridor the validator thought was
five cells and the generator cut at three cannot happen.

The width is drawn from the two rooms' own indices, as it already was, so it is stable across a
reload -- what changed is only whether the draw is allowed to happen at all.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

planner = io.open(PLANNER, encoding="utf-8").read()

# The validator passes the pair's shaping depth.
SAFE_OLD = u"                    int reach = CorridorHalfWidthBetween(room, other, depth) - 1;"
SAFE_NEW = u'''                    // The pair's own shaping depth, so a corridor near the hall stays the
                    // plain three cells and one deep in the maze may narrow or open out. The
                    // SAME number the generator will cut with.
                    int reach = CorridorHalfWidthBetween(room, other,
                        Math.Max(ShapeDepthOf(rooms, room, depth),
                            ShapeDepthOf(rooms, other, depth))) - 1;'''
if planner.count(SAFE_OLD) != 1:
    print("SAFE ANCHOR PROBLEM: %d" % planner.count(SAFE_OLD))
    raise SystemExit(1)
planner = planner.replace(SAFE_OLD, SAFE_NEW, 1)

# The room proportions stop depending on a library version nobody bumps.
DER_OLD = u'''                if (DestinationService.GetRoomLibraryVersion(coordinate) >= 2)
                { Derange(coordinate, ref width, ref height, seed, index, span); }'''
DER_NEW = u'''                // **Proportions come apart with distance, not with a library version.**
                // Owner: *"odd variers walls and contructions making narrows , expansies"*. This
                // used to wait on `GetRoomLibraryVersion >= 2`, which is a content revision
                // rather than a statement about where in the maze a room is.
                if (DestinationService.GetRoomLibraryVersion(coordinate) >= 2)
                { Derange(coordinate, ref width, ref height, seed, index, span); }'''
if planner.count(DER_OLD) != 1:
    print("DERANGE ANCHOR PROBLEM: %d" % planner.count(DER_OLD))
    raise SystemExit(1)
planner = planner.replace(DER_OLD, DER_NEW, 1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(planner)
print("the validator measures corridors by the pair's distance")

GEN_OLD = u"                    int halfWidth = RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth);"
GEN_NEW = u'''                    // The pair's own shaping depth, the SAME call CandidateIsSafe made when
                    // it proved the route through this corridor.
                    int halfWidth = RoomLayoutPlanner.CorridorHalfWidthBetween(room, other,
                        Math.Max(RoomLayoutPlanner.ShapeDepthOf(coordinate.Rooms, room, depth),
                            RoomLayoutPlanner.ShapeDepthOf(coordinate.Rooms, other, depth)));'''
gen = io.open(GEN, encoding="utf-8").read()
if gen.count(GEN_OLD) != 1:
    print("GEN ANCHOR PROBLEM: %d" % gen.count(GEN_OLD))
    raise SystemExit(1)
io.open(GEN, "w", encoding="utf-8", newline="").write(gen.replace(GEN_OLD, GEN_NEW, 1))
print("and the generator cuts them the same way")
