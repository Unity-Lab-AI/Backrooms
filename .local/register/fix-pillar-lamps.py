# -*- coding: utf-8 -*-
"""One lamp per room is why the Backrooms are dark. A lamp on every pillar is why they are not.

Owner, verbatim: *"and we need more lights and mixedered varies of lights but the main grand
themed backrooms universe rooms need like a wall light on every column wall used as in the
universe of backrooms the basic rooms are well lit"*.

**Exactly one light was placed per room**, whatever the room's size. A depth-1 hall is eighty
cells across and had a single sconce in it. The owner is right that this is a theme and not a
convenience: the yellow rooms are *lit*, flatly and evenly and far too much, and that is the
whole look.

THE PILLARS ARE ALREADY THERE AND ALREADY KNOWN. `RoomLayoutPlanner.PillarCells` is the single
place the lattice is decided -- the generator spawns from it and `CandidateIsSafe` proves the
room stays walkable with it -- so every pillar is a cell with a wall on it, which is exactly what
a `WallLamp` needs. **No new content, no new def, and no second opinion about where pillars are:
the same method both other readers use.**

Mounted on the pillar, facing out of it. Only where the palette resolved a wall-mounted fixture,
because the fallback `StandingLamp` stands on the floor, and a floor lamp beside every pillar is
furniture rather than lighting.

**Wired by the pass that already exists.** `ConnectStrayConsumers` runs after the dressing and
sweeps every `CompPowerTrader` on the map, so these need no bespoke wiring -- and they are added
to `placedLights` so the power validation counts what was actually placed rather than
re-deriving a number, which is the defect that stopped every coordinate generating for
thirty-nine checkpoints.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

CALL_OLD = u'''                    placedLights.Add(light);
                }

                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);'''

CALL_NEW = u'''                    placedLights.Add(light);
                }

                // **A LAMP ON EVERY PILLAR.** Owner: *"the main grand themed backrooms universe
                // rooms need like a wall light on every column wall used as in the universe of
                // backrooms the basic rooms are well lit"*. One lamp in an eighty-cell hall is
                // not the Backrooms; flat even over-lighting is the whole look.
                SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted,
                    reservedProviderCells, placedLights);

                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);'''

METHOD_ANCHOR = u"        private static IntVec3 FindWallAttachmentCell(Map map, RoomRecord room, IntVec3 preferred,"

METHOD = u'''        /// <summary>
        /// A wall lamp on each of a room's pillars, so the basic rooms are lit the way the
        /// Backrooms are lit.
        ///
        /// Owner: *"we need more lights ... the main grand themed backrooms universe rooms need
        /// like a wall light on every column wall used as in the universe of backrooms the basic
        /// rooms are well lit"*.
        ///
        /// **The lattice comes from `RoomLayoutPlanner.PillarCells` and nowhere else.** That is
        /// the same method the pillar spawner and `CandidateIsSafe` use, so this cannot drift
        /// from where the pillars actually are -- two readers deriving the same lattice
        /// independently is precisely the defect that stopped every coordinate generating from
        /// 0.7.8-dev to 0.12.47-dev.
        ///
        /// Only for a wall-mounted fixture. The palette falls back to `StandingLamp`, which
        /// stands on the floor, and a floor lamp beside every pillar is furniture rather than
        /// lighting.
        ///
        /// Silent on failure, every time. A pillar with no free cell beside it simply has no
        /// lamp: this is lighting, and a coordinate must never be lost over how bright it is.
        /// </summary>
        private static void SpawnPillarLamps(Map map, CoordinateRecord coordinate, ThingDef wallDef,
            ThingDef lightDef, bool wallMounted, HashSet<IntVec3> reserved, List<Thing> placedLights)
        {
            if (!wallMounted || map == null || coordinate == null || lightDef == null) { return; }
            if (coordinate.Rooms == null) { return; }
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            for (int index = 0; index < coordinate.Rooms.Count; index++)
            {
                RoomRecord room = coordinate.Rooms[index];
                if (room == null) { continue; }
                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))
                {
                    for (int side = 0; side < directions.Length; side++)
                    {
                        IntVec3 cell = pillar + directions[side];
                        if (!cell.InBounds(map) || reserved.Contains(cell)) { continue; }
                        if (!room.Bounds.ContractedBy(1).Contains(cell)) { continue; }
                        if (!cell.Standable(map) || cell.GetEdifice(map) != null) { continue; }
                        // Facing out of the pillar: the lamp draws into the wall behind it, and
                        // the wall behind it is the pillar.
                        Rot4 facing = Rot4.FromIntVec3(directions[side]);
                        Thing lamp = MakeBuilding(lightDef, lightDef.MadeFromStuff ? ThingDefOf.Steel : null);
                        if (lamp == null) { break; }
                        lamp.SetFaction(Faction.OfPlayer);
                        GenSpawn.Spawn(lamp, cell, map, facing);
                        if (!lamp.Spawned || lamp.Map != map) { break; }
                        reserved.Add(cell);
                        placedLights.Add(lamp);
                        break;
                    }
                }
            }
        }

        private static IntVec3 FindWallAttachmentCell(Map map, RoomRecord room, IntVec3 preferred,'''

text = io.open(GEN, encoding="utf-8").read()
if text.count(CALL_OLD) != 1:
    print("CALL ANCHOR PROBLEM: %d" % text.count(CALL_OLD))
    raise SystemExit(1)
text = text.replace(CALL_OLD, CALL_NEW, 1)
if text.count(METHOD_ANCHOR) != 1:
    print("METHOD ANCHOR PROBLEM: %d" % text.count(METHOD_ANCHOR))
    raise SystemExit(1)
text = text.replace(METHOD_ANCHOR, METHOD, 1)
io.open(GEN, "w", encoding="utf-8", newline="").write(text)
print("a wall lamp on every pillar")
