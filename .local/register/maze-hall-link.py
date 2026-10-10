# -*- coding: utf-8 -*-
"""The maze could not link to its own hall, so every real candidate was refused.

The probe said `rooms 24.0` and `widest 40` at **every** depth, which is the fallback serpentine's
signature -- `MinSlotsPerAxis * MinSlotsPerAxis * 2 / 3` is exactly 24, and the fallback builds no
grand hall. So all three maze candidates were being refused and the safety net was catching every
seed, while `refused 0/200` reported success.

## Why they were refused

`ValidateRooms` requires `AreGridNeighbors` of every linked pair: their **centres must share a row
or a column**, because `BuildCorridors` carves straight between those centres.

The hall spans two slots, so its centre sits **between** them -- x = 58 at depth 1, which is no
slot's centre. The walk started at the hall's second slot and its first step could be northward,
linking the hall to a room whose centre shares neither axis with it. One such link and the whole
candidate is illegal.

The old serpentine never hit this because `order[2]` is always the next slot **in the same row**,
so the hall's only link shared its centre row by accident of the traversal.

## The fix

The walk asks `AreNeighbourRooms` -- the same question `ValidateRooms` will ask -- before it
accepts a step, and declines the direction when the answer is no. The slot is left unvisited and
is reached later from a different parent, which a maze can do and a line cannot. So the hall links
only along its own row, and everything else is linked by whichever neighbour the walk arrives
from.

**One predicate, asked by the builder and the validator**, which is the discipline this file keeps
having to relearn: a layout that is built one way and proved another is the defect that stopped
every coordinate generating for thirty-nine checkpoints.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")

OLD = u"""                    int parent = slotOf[current];
                    var room = MakeRoom(coordinate, rooms.Count, "survey_lobby", next, spacing,
                        VariedRoomSpan(spacing, next, seed, depth), seed, false, depth);
                    rooms.Add(room);
                    slotOf[next] = room.index;
                    hops[room.index] = hops[parent] + 1;
                    Link(rooms, room.index, parent);
                    stack.Add(next);
                    advanced = true;
                    break;"""

NEW = u"""                    int parent = slotOf[current];
                    var room = MakeRoom(coordinate, rooms.Count, "survey_lobby", next, spacing,
                        VariedRoomSpan(spacing, next, seed, depth), seed, false, depth);
                    // **THE SAME QUESTION `ValidateRooms` WILL ASK.** `AreGridNeighbors` requires
                    // a linked pair's centres to share a row or a column, because `BuildCorridors`
                    // carves straight between them. The hall spans two slots, so its centre sits
                    // BETWEEN them -- 58 at depth 1, which is no slot's centre -- and a step from
                    // the hall in any direction but along its own row produces a link the
                    // validator refuses. **That one link made every maze candidate illegal**, and
                    // the fallback serpentine quietly caught every seed while the probe reported
                    // no refusals at all.
                    //
                    // Declined rather than forced: the slot stays unvisited and is reached later
                    // from a different parent, which is a thing a maze can do and a line cannot.
                    if (!AreNeighbourRooms(rooms[parent], room)) { continue; }
                    rooms.Add(room);
                    slotOf[next] = room.index;
                    hops[room.index] = hops[parent] + 1;
                    Link(rooms, room.index, parent);
                    stack.Add(next);
                    advanced = true;
                    break;"""

text = io.open(PLANNER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the walk declines a step the validator would refuse")
