using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>Builds the saved six-to-eight-room graph without consuming a generation roll.</summary>
    public sealed class GenStep_BackroomsDestination : GenStep
    {
        private const int GeneratorSeedPart = 72910463;
        private const float InitialRoomTemperature = 20f;
        /// <summary>
        /// The most conduit cells one coordinate may hold.
        ///
        /// **512 was sized for a 60x60 map and it killed every level below depth 1.** Modelled
        /// against what the routing actually does — `FindConduitRoute` BFSes from the whole wired
        /// set, so routes share a spine and the total is far under the sum of the distances:
        ///
        ///     depth 1:   460 cells    depth 4: 1,061
        ///     depth 2:   625          depth 5: 1,211
        ///     depth 3:   828          depth 6: 1,436
        ///
        /// Depth 1 fitted under 512 **by forty cells**, which is the worst possible failure mode:
        /// the first level a player opens would have generated and every one below it would have
        /// died, so it would have looked fixed.
        ///
        /// Four thousand leaves room for a deranged layout and for whatever the dressing adds,
        /// and the conduit is `HiddenConduit` so a long run costs nothing visually. **Exceeding
        /// it now stops the wiring rather than destroying the coordinate** — see
        /// <see cref="TrySpawnNativeConduit"/>.
        /// </summary>
        private const int MaxNativePowerConduits = 4000;
        /// <summary>
        /// Most stacks of fuel a generated coordinate will prime its generator with.
        ///
        /// **A refusal rather than a clamp**, which is the point: a fuel whose stack
        /// size makes the authored run cost more than this many stacks is skipped
        /// entirely rather than part-filled, because a generator holding a token
        /// amount reads as broken where an unfuelled one reads as unfuelled.
        /// </summary>
        private const int MaxInitialFuelStacks = 16;

        public override int SeedPart { get { return GeneratorSeedPart; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            RimroomsDestinationMapParent parent = map == null ? null : map.Parent as RimroomsDestinationMapParent;
            CoordinateRecord coordinate = null;
            try
            {
                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                coordinate = campaign == null || parent == null ? null :
                    campaign.Coordinates.FirstOrDefault(record => record.Id == parent.CoordinateId);
                if (parent == null || coordinate == null || coordinate.Site != parent ||
                    map.Size.x != DestinationService.MapWidth || map.Size.z != DestinationService.MapHeight ||
                    !DestinationService.EnsureRoomGraph(coordinate, out _) ||
                    DestinationService.ComputeFingerprint(coordinate) != parent.LayoutFingerprint)
                {
                    throw new InvalidOperationException("RR_Generation_MapOwnerOrGraphMismatch");
                }
                if (!parent.TryBeginLayout())
                {
                    throw new InvalidOperationException("RR_Generation_RefusedToReplaceSavedLayout");
                }
                TerrainDef concrete = DefDatabase<TerrainDef>.GetNamedSilentFail("Concrete");
                TerrainDef voidFloor = DefDatabase<TerrainDef>.GetNamedSilentFail("WaterDeep");
                TerrainDef pavedFloor = DefDatabase<TerrainDef>.GetNamedSilentFail("PavedTile");
                ThingDef wallDef = ThingDefOf.Wall;
                // Walls take the palette's material too, so the shallow yellow rooms are
                // wood and the deeper bands are not. Steel stays the fallback if a
                // palette material is somehow unavailable.
                // The band's own choice is the fallback, and at depth 1 it is the answer: the
                // yellow rooms are wood-walled and stay that way, for the same reason nothing
                // else deforms at the surface band.
                //
                // **Deeper, the walls come from the coordinate's palette.** Owner direction:
                // *"wild variatiosn of material typeds in all items equaipment walls floors ..."*.
                // `BackroomsPalette` names exactly two wall materials -- WoodLog or Steel --
                // across five bands, which is a hard-coded pair where every other material in
                // the place is drawn from whatever the profile offers. Asking
                // CoordinateMaterials means a profile that adds stone or metal widens the walls
                // exactly as it already widens the furniture, and nothing here names a material.
                // The band's own choice, which at level 0 IS the answer: owner direction,
                // *"depth 0 in the backrroms is the standard yellow style"*, and the yellow rooms
                // are wood-walled. It stays the fallback everywhere.
                ThingDef wallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff
                    ?? ThingDefOf.Steel;
                ThingDef anchorDef = DefDatabase<ThingDef>.GetNamedSilentFail("Door");
                // Core ships a wall-mounted lamp, which is both closer to the overhead
                // fluorescent the setting wants and better for the look in a second way:
                // an endless corridor reads as endless precisely because nothing is
                // standing in it. Generation used StandingLamp before, which put
                // furniture in the middle of every room.
                ThingDef lightDef = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).light;
                // **The floor-standing fallback for a light that cannot be mounted.** The
                // palette resolves `WallLamp` for most bands, and an attachment with no wall
                // behind it is a guaranteed throw inside Core's power rebuild -- see
                // WallAttachmentHolds. Not in the required-def check below: a profile without
                // a standing lamp gets a darker corridor, not a refused coordinate.
                ThingDef floorLightDef = DefDatabase<ThingDef>.GetNamedSilentFail("StandingLamp");
                ThingDef climateDef = DefDatabase<ThingDef>.GetNamedSilentFail("Heater");
                ThingDef generatorDef = DefDatabase<ThingDef>.GetNamedSilentFail("ChemfuelPoweredGenerator");
                ThingDef fuelDef = DefDatabase<ThingDef>.GetNamedSilentFail("Chemfuel");
                ThingDef conduitDef = DefDatabase<ThingDef>.GetNamedSilentFail("HiddenConduit");
                if (concrete == null || voidFloor == null || pavedFloor == null || wallDef == null || wallStuff == null ||
                    anchorDef == null || lightDef == null || climateDef == null || generatorDef == null ||
                    fuelDef == null || conduitDef == null)
                {
                    throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing");
                }

                List<IntVec3> corridorSides = BuildShell(map, coordinate, concrete,
                    voidFloor, wallDef, wallStuff);

                RoomRecord threshold = coordinate.Rooms.First(room => room.familyId == "threshold_room");
                IntVec3 anchorPosition = FindBuildingCell(
                    map,
                    threshold,
                    anchorDef);
                Thing anchor = MakeBuilding(anchorDef, anchorDef.MadeFromStuff ? ThingDefOf.Steel : null);
                if (!(anchor is Building_Door)) { throw new InvalidOperationException("RR_Generation_InvalidDoorDef"); }
                anchor.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(anchor, anchorPosition, map, Rot4.North);
                anchor.SetForbidden(false, false);

                RoomRecord office = coordinate.Rooms.First(room => room.familyId == "office_copy");
                IntVec3 officeEvidenceCell = FindClearInteriorCell(map, office, office.Bounds.CenterCell);
                RoomRecord climateRoom = coordinate.Rooms.FirstOrDefault(room => room.familyId == "utility_room") ??
                    coordinate.Rooms.First(room => room.familyId == "service_passage");
                IntVec3 entryCell = FindClearInteriorCell(map,
                    threshold,
                    threshold.Bounds.Min + new IntVec3(3, 0, 3),
                    new HashSet<IntVec3> { officeEvidenceCell, anchorPosition });
                IntVec3 returnCell = FindAdjacentSafeCell(map, threshold, anchor);

                var reservedProviderCells = new HashSet<IntVec3>
                    { officeEvidenceCell, anchorPosition, entryCell, returnCell };
                foreach (IntVec3 cell in anchor.OccupiedRect().ExpandedBy(1).Cells)
                { reservedProviderCells.Add(cell); }
                // **The fixture decides where it can go.** `BackroomsPalette` resolves `WallLamp`,
                // which is `building.isAttachment` with a `Placeworker_AttachedToWall` and
                // `drawOffsetNorth (0,0,0.9)` -- it draws almost a full cell INTO the wall it is
                // mounted on. Placed on an open interior cell it drew a sconce hanging in the
                // middle of the floor, which also defeats the reason the palette chose it: an
                // endless corridor reads as endless precisely because nothing is standing in it.
                //
                // Branching on the def rather than the def NAME, because the palette still falls
                // back to `StandingLamp`, which stands on the floor and must keep doing so.
                // **THE GENERATOR AND THE CLIMATE UNIT CHOOSE THEIR CELLS BEFORE ANY LIGHT DOES.**
                // This block sat below the light loop, and that order was harmless while a room
                // light was a one-cell lamp in a wall. The first launch with the three-cell strip
                // failed two coordinates in a row with `RR_Generation_NoSafeRoomCell` out of
                // `FindPoweredBuildingCell`: the strip took the clear floor beside the centre of
                // the utility room, and the two-by-two generator had nowhere left to stand. A
                // generator that cannot be placed costs the coordinate; a strip that cannot be
                // placed becomes a standing lamp. So the thing that cannot fail goes first.
                IntVec3 generatorCell = FindPoweredBuildingCell(map, climateRoom, generatorDef,
                    reservedProviderCells, climateRoom.Bounds.CenterCell + new IntVec3(2, 0, 0));
                ReserveFootprint(generatorCell, generatorDef, reservedProviderCells);
                IntVec3 climateCell = FindPoweredBuildingCell(map, climateRoom, climateDef,
                    reservedProviderCells, climateRoom.Bounds.CenterCell + new IntVec3(-2, 0, 0));
                ReserveFootprint(climateCell, climateDef, reservedProviderCells);
                IntVec3 fuelCell = FindClearInteriorCell(map, climateRoom, generatorCell + IntVec3.East,
                    reservedProviderCells);

                var lightCells = new List<IntVec3>();
                var lightFacings = new List<Rot4>();
                var lightDefs = new List<ThingDef>();
                bool wallMounted = lightDef.building != null && lightDef.building.isAttachment;
                // **OUR FIXTURE IS A STRIP, NOT A POINT.** `RR_SiteFluorescentFitted` is three cells
                // long, so every placement rule written for a one-cell lamp has to ask about a
                // footprint instead. Decided by the def's size rather than its name, so a profile
                // that swaps the fixture for another shape is handled by the same branch.
                bool strip = !wallMounted && (lightDef.size.x > 1 || lightDef.size.z > 1);
                foreach (RoomRecord room in coordinate.Rooms.OrderBy(value => value.Index))
                {
                    IntVec3 lightCell = IntVec3.Invalid;
                    Rot4 facing = Rot4.North;
                    ThingDef roomLightDef = lightDef;
                    if (wallMounted)
                    {
                        lightCell = FindWallAttachmentCell(map, room, room.Bounds.CenterCell,
                            wallDef, reservedProviderCells, out facing);
                    }
                    else if (strip)
                    {
                        lightCell = TryFindFootprintCell(map, room, lightDef, reservedProviderCells,
                            room.Bounds.CenterCell + new IntVec3(0, 0, 2));
                    }
                    if (!lightCell.IsValid)
                    {
                        // **No wall to mount on, or no run of floor long enough for the strip.**
                        // This used to fall through placing `lightDef` on an open floor cell facing
                        // north -- and when the palette's light is `WallLamp`, that is an attachment
                        // with nothing behind it, which is a guaranteed throw inside Core's power
                        // rebuild. See WallAttachmentHolds. The room still gets a light; it is a
                        // floor-standing one, which is what the palette's own fallback has always
                        // been.
                        facing = Rot4.North;
                        roomLightDef = wallMounted || strip ? floorLightDef ?? lightDef : lightDef;
                        lightCell = FindClearInteriorCell(map, room,
                            room.Bounds.CenterCell + new IntVec3(0, 0, 2), reservedProviderCells);
                    }
                    lightCells.Add(lightCell);
                    lightFacings.Add(facing);
                    lightDefs.Add(roomLightDef);
                    // The whole footprint, which for a one-cell lamp is the one cell it always was.
                    ReserveFootprint(lightCell, roomLightDef, reservedProviderCells);
                }
                var consumerFootprints = new List<CellRect>
                { GenAdj.OccupiedRect(climateCell, Rot4.North, climateDef.size) };
                for (int index = 0; index < lightCells.Count; index++)
                {
                    // Only a light that draws power is a consumer. The fitted fluorescent runs off
                    // the building rather than the crew's generator -- see its def for the
                    // arithmetic -- so routing a conduit to it would wire nothing.
                    if (!lightDefs[index].HasComp(typeof(CompPowerTrader))) { continue; }
                    consumerFootprints.Add(GenAdj.OccupiedRect(lightCells[index], Rot4.North,
                        lightDefs[index].size));
                }
                Thing generator = MakeBuilding(generatorDef, generatorDef.MadeFromStuff ? ThingDefOf.Steel : null);
                generator.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(generator, generatorCell, map, Rot4.North);
                if (!generator.Spawned || generator.Map != map)
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                PrimeNativeGenerator(generator, fuelDef, fuelCell, climateRoom, reservedProviderCells, map);

                Thing climate = MakeBuilding(climateDef, climateDef.MadeFromStuff ? ThingDefOf.Steel : null);
                climate.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(climate, climateCell, map, Rot4.North);
                if (!climate.Spawned || climate.Map != map)
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }

                // Kept, rather than counted again later. Re-deriving how many lights should exist
                // is what broke this generator for thirty-nine checkpoints; see
                // ValidateNativePowerNetwork.
                var placedLights = new List<Thing>();
                for (int index = 0; index < coordinate.Rooms.Count; index++)
                {
                    // **Through the one spawner**, which refuses to leave an attachment hanging
                    // in mid-air; see WallAttachmentHolds for what that cost.
                    Thing light = SpawnAttachableLight(map, lightDefs[index], floorLightDef,
                        lightCells[index], lightFacings[index]);
                    if (light == null)
                    { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                    placedLights.Add(light);
                }

                // **A LAMP ON EVERY PILLAR.** Owner: *"the main grand themed backrooms universe
                // rooms need like a wall light on every column wall used as in the universe of
                // backrooms the basic rooms are well lit"*. One lamp in an eighty-cell hall is
                // not the Backrooms; flat even over-lighting is the whole look.
                SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted,
                    reservedProviderCells, placedLights);
                // **AND A STRIP IN EVERY BAY**, which is the same even grid the pillar lamps made
                // but in our own fixture: one fitting midway between each pillar and the next.
                // Owner: *"in the bacrooms lights are normally spaced"*.
                if (strip)
                { SpawnBayStrips(map, coordinate, lightDef, reservedProviderCells, placedLights); }

                // **AND THE HALLWAYS GET THE SAME TREATMENT.** Owner: *"rooms as halways with
                // the exact shit thats in the rooms"*. A corridor that is lit and furnished is
                // part of the building; one that is neither is a tunnel between beads, which is
                // what *"a string of pears"* was describing.
                DressCorridors(map, coordinate, corridorSides, lightDef, floorLightDef, placedLights,
                    reservedProviderCells);

                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);

                // **WIRED LAST, AND THAT ORDER IS THE WHOLE FIX.**
                //
                // This ran FIRST, before the generator, the climate unit, the ceiling lights and
                // the pillar lamps were spawned -- so conduits went down on empty cells and then
                // every powered building in the coordinate was spawned **on top of one**. Several
                // mods in the owner's profile attach a hidden conduit under a powered building
                // automatically, which makes a second transmitter on a cell that already had
                // ours, on every single one of those cells.
                //
                // Core refuses the second transmitter -- *"there can't be two transmitters on the
                // same cell"* -- and leaves its own bookkeeping inconsistent, so the rebuild
                // below threw a `NullReferenceException` out of
                // `PowerConnectionMaker.TryConnectToAnyPowerNet`. **That threw out of
                // `GenStep.Generate`, so the level stopped being built, `EnsureSite` reported
                // failure, and `SoloGroupOpening` never marked the gate door.** The owner's
                // report was *"the door isnt blue, and its not portaling people to the
                // backrooms"*, three launches running.
                //
                // Wiring after everything exists is what makes `AlreadyTransmits` able to answer
                // truthfully: a cell another mod has already wired is skipped, because it is
                // already wired. The guard was right and it simply ran too early to see anything.
                //
                // Nothing between the old position and this one reads the power grid, and a
                // conduit is not an edifice and does not block standability, so no placement
                // decision above changes. It is also the direction this generator already moved
                // once -- see `ConnectStrayConsumers`, which replaced pre-wiring whole rooms.
                // **Before a single conduit, and before Core is asked to connect anything.** An
                // attachment with no wall behind it makes Core's own power rebuild throw out of
                // `Map.FinalizeInit`, which discards the finished level; see
                // RemoveUnattachedAttachments. Run after every placer, because the point is to
                // not depend on all of them being right.
                RemoveUnattachedAttachments(map, coordinate, placedLights);

                HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(map, voidFloor, conduitDef,
                    GenAdj.OccupiedRect(generatorCell, Rot4.North, generatorDef.size), consumerFootprints);
                // Native spawn notifications are queued; rebuild connections now without ticking
                // the power simulation so readiness checks see the actual shared grid.
                //
                // **Nothing asks twice after a refusal.** A failed rebuild leaves Core's delayed
                // queue half-applied, and calling again re-applies it; see RebuildPowerNets.
                if (RebuildPowerNets(map, coordinate) &&
                    // Whatever the dressing just placed that draws power, wired now that it
                    // exists. This is what replaced pre-wiring whole rooms on the chance
                    // something would land in them -- see SpawnNativePowerNetwork.
                    ConnectStrayConsumers(map, coordinate, voidFloor, conduitDef, wiredCells, generator))
                {
                    // The sweep rebuilds after each consumer it wires, so this only matters for
                    // the conduit-cap exit, which leaves the last conduits unregistered.
                    RebuildPowerNets(map, coordinate);
                }
                // **Reported, never fatal.** A coordinate whose heater or one lamp failed to join
                // the grid is dark and cold and completely playable. A coordinate that does not
                // exist costs the player the gate that leads to it -- which is exactly what
                // happened on the fifth launch: the owner reported *"i dont see a natural gate"*,
                // and the cause was this validation aborting the whole layout, so
                // `MarkLayoutReady` never ran, so `SoloGroupOpening` had no threshold anchor to
                // register against. The structural validation below stays fatal, because a
                // coordinate you cannot walk through really is broken.
                string powerFault = ValidateNativePowerNetwork(map, generator, climate, placedLights);
                if (powerFault != null)
                {
                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id +
                        " generated with an incomplete native power grid (" + powerFault +
                        "). The space, its gate anchor and its way home are unaffected.");
                }
                MapGenerator.PlayerStartSpot = entryCell;
                MapGenerator.rootsToUnfog.Add(entryCell);
                MapGenerator.rootsToUnfog.Add(returnCell);

                ValidatePlacedLayout(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);

                // Everything this coordinate contains is marked as having come out of the
                // Backrooms, in one pass, here and nowhere else. The mark is what odd contracts
                // ask for, so it is also the thing a player would most like to forge: marking
                // on spawn instead would let somebody haul ordinary goods in, drop them, and
                // carry them back out as odd. Doing it once at generation, before the map can
                // be reached, means the mark can only be earned by taking what was already
                // there. See Economy/OddOriginService.
                // Bodies are DISCOVERABLE CONTENT rather than encounters, so they are placed
                // with the space rather than paced by the escalation ladder: finding one should
                // not wait on a danger band, and a corpse does not act. Living inhabitants are
                // placed on arrival instead, which is what keeps "a first visit is always quiet"
                // true. Placed before the odd-origin pass so the bodies and what they carry are
                // marked along with everything else the coordinate produced.
                Threats.InhabitantService.PopulateDead(map, coordinate, reservedProviderCells);

                coordinate.oddGoodsDefNames = Economy.OddOriginService.MarkGeneratedContents(map);

                parent.MarkLayoutReady(entryCell, returnCell, officeEvidenceCell, anchor);
            }
            catch (Exception error)
            {
                InvalidOperationException layoutError = error as InvalidOperationException;
                string failureKey = layoutError != null && layoutError.Message.StartsWith("RR_Generation_", StringComparison.Ordinal)
                    ? layoutError.Message : "RR_Generation_MapBuildFailed";
                parent?.MarkGenerationFailed(failureKey);
                Log.Error("[Rimrooms][Generation] Site layout stopped; existing coordinate/map are retained: " + error);
                throw;
            }
        }


        /// <summary>
        /// The coordinate shell: rock to every edge, thick roof over every cell, and the
        /// rooms carved out of it.
        ///
        /// **Shared by both generators on purpose.** A destination reached through a gate
        /// and the place the solo/group start is already standing in are furnished quite
        /// differently - one has a gate anchor and a way home, the other has neither - but
        /// the shell is identical, and the shell is what carries invariant 13: **a Backrooms
        /// coordinate has no outside, and its roof is never removable.**
        ///
        /// A second copy of this would drift, and what would drift out of it is the promise
        /// that you cannot dig your way into open sky. The roof is deliberately thick and never
        /// `RoofConstructed`: constructed roof can be removed.
        ///
        /// **And it is our own non-collapsing roof rather than Core's `RoofRockThick`.** Owner
        /// direction, 2026-09-30: *"backrooms can not and shall not have cave ins so removing
        /// walls floors columns shall not cause mountain overhead to column collapse"*, scoped
        /// to *"tgis is only for backrooms"*. See `BackroomsContainmentMapComponent.OverheadRoof`.
        ///
        /// Carve the coordinate and return the cells along its corridor walls, so the hallways
        /// can be lit and dressed like the rooms they join.
        /// </summary>
        internal static List<IntVec3> BuildShell(Map map, CoordinateRecord coordinate,
            TerrainDef concrete,
            TerrainDef voidFloor, ThingDef wallDef, ThingDef wallStuff)
        {
            ClearMapContents(map);
            // Owner direction 2026-09-29: a Backrooms environment can never have an
            // outside, and the whole seed map sits inside mountain roof. So the base pass
            // roofs *every* cell with thick rock rather than leaving it open, and fills the
            // space between rooms with solid mineable rock.
            //
            // The rock is doing two jobs. It supports the thick roof, which is what stops
            // Core's own collapse check from finding a vast unsupported ceiling; and it is
            // material the player can mine, which the same owner direction explicitly wants
            // ("areas minable and of all types of materisals throughout"). Nothing here
            // restricts the pickaxe: thick roof never vanishes on collapse, so a coordinate
            // can be mined to nothing and still never open a hole in the world.
            List<ThingDef> rockTypes = NaturalRockTypesFor(map);
            RoofDef overheadRoof = BackroomsContainmentMapComponent.OverheadRoof;
            foreach (IntVec3 cell in map.AllCells)
            {
                map.terrainGrid.SetTerrain(cell, voidFloor);
                map.roofGrid.SetRoof(cell, overheadRoof);
            }
            FillWithRock(map, coordinate, rockTypes);

            int coordinateDepth = RoomLayoutPlanner.DepthOf(coordinate);
            // **THE COORDINATE'S MOTIF, derived here rather than handed in.** Owner, 2026-10-03:
            // *"repeated patternes in variations"*. `CandidateIsSafe` derives the identical motif
            // from the identical record, so the rock this carves is the rock it proved walkable.
            // Passing it along a chain instead would be a second derivation of one rule.
            CoordinateMotif motif = CoordinateMotif.For(coordinate);
            foreach (RoomRecord room in coordinate.Rooms)
            {
                // Owner direction, 2026-09-30: *"everything doesnt have to be square rooms"*.
                // Rock is left standing in the corners, from the SAME function CandidateIsSafe
                // proved the room walkable against -- see RoomLayoutPlanner.RockIntrusionCells.
                // Shaped by how far this room is from the spawn hall, not by the
                // coordinate's own depth -- which switched every shape system off on level 0 and
                // made the first level all rectangles. The SAME call CandidateIsSafe made when
                // it proved this room walkable.
                var intrusions = new HashSet<IntVec3>(
                    RoomLayoutPlanner.RockIntrusionCells(room,
                        RoomLayoutPlanner.ShapeDepthOf(coordinate.Rooms, room, coordinateDepth),
                        motif));
                foreach (IntVec3 cell in room.Bounds.Cells)
                {
                    // The roof goes overhead either way: an intrusion is rock inside the room,
                    // not a hole in the world.
                    map.roofGrid.SetRoof(cell, overheadRoof);
                    if (intrusions.Contains(cell)) { continue; }
                    // Carve the room out of the rock, keeping the thick roof overhead. The
                    // roof is deliberately NOT RoofConstructed: constructed roof is
                    // removable, and all roof in a Backrooms coordinate must never be.
                    ClearRock(map, cell);
                    map.terrainGrid.SetTerrain(cell, concrete);
                }
            }
            // **A HALLWAY IS A ROOM.** Owner: *"rooms as halways with the exact shit thats
            // in the rooms"*. The palette and the wall material go in with the carve, so a
            // corridor is part of the same building rather than a service tunnel between rooms.
            List<IntVec3> corridorSides = BuildCorridors(coordinate.Rooms, map, coordinate,
                wallDef, wallStuff, coordinateDepth);

            // **THE ROCK IS MADE WORTH DIGGING, and it happens HERE for a reason.** Owner,
            // 2026-10-03: *"where there is mountain walls and no rooms areas minable need to have
            // resources that you can mine like steel gold plasteel, gems, all of them"* and *"we
            // should have doors that lead no where but to an ore or gem vein, and veins leading to
            // other rooms"*.
            //
            // After the rooms and the corridors, because what is left standing at this point is
            // exactly the rock a player can dig, and `OreVeinBuilder` only ever swaps plain
            // natural rock for ore-bearing natural rock. Run before the carve it would seam the
            // floor plan; run here it cannot touch a route, a wall or a doorway, which is why it
            // is allowed to route veins freely across the whole map.
            OreVeinBuilder.Place(map, coordinate, coordinateDepth);

            foreach (RoomRecord room in coordinate.Rooms)
            {
                // **Walls are chosen PER ROOM deeper in.** Owner correction: *"we want every
                // type of wall and material for all things randomly"*. One material for the whole
                // level was the thing being corrected -- and per ROOM rather than per CELL because
                // a wall whose every cell is a different stone is a patchwork rather than a wall,
                // and BuildRoomWalls places one room's ring at a time, so the room is the unit
                // the geometry already has.
                //
                // **THE YELLOW LOOK IS THE HALL AND WHAT SURROUNDS IT, NOT THE FLOOR.** Owner:
                // *"the normal yellow backrooms look isnt the whole floor but the main spanw
                // room"*. This used to test `coordinate.Depth`, so at level 0 EVERY room on a
                // three-hundred-cell map took the band's wood and the whole level read as one
                // corridor -- which is the level the owner walked and called *"nothing but what
                // it currently is"*.
                //
                // Measured per room now, by distance from the spawn hall: the arrival and its
                // neighbours keep the band's wood exactly as before, and the further out a room
                // is the more its walls are drawn from whatever the profile offers.
                int wallDepth = RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth);
                ThingDef roomWallStuff = wallDepth <= CoordinateMaterials.CoherentDepth
                    ? wallStuff
                    : (CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index) ?? wallStuff);
                BuildRoomWalls(room, coordinate.Rooms, map, wallDef, roomWallStuff);
                // Owner direction, 2026-09-30, verbatim: *"u can use walls as pillars making the
                // 0 level rooms be grand large spaces"*. A depth-1 hall is eighty cells across,
                // and an eighty-cell room with nothing in it is a field, not a hall.
                //
                // **The lattice is decided in RoomLayoutPlanner.PillarCells and nowhere else**,
                // because the planner has to prove the room is still walkable with the pillars in
                // it before any map exists. Two places deriving the same lattice independently is
                // exactly the defect that stopped every coordinate generating for thirty-nine
                // checkpoints.
                //
                // This replaced a single wall at the room's centre cell. A lone centre support
                // was right for a 14-cell room and pointless in an 80-cell one -- and it sat on
                // the centre cross, which the lattice now deliberately leaves clear.
                // **A ROOM'S PILLARS ARE MADE OF THE SAME THING ITS WALLS ARE.**
                //
                // This passed `wallStuff` -- the level band's material -- while the ring around
                // the same room was built from `roomWallStuff`. So a hall whose walls had been
                // drawn from the profile stood on pillars in the band's wood or steel: stone
                // walls, wooden columns, in the one room big enough for anybody to notice.
                //
                // Owner direction, verbatim: *"we want every type of wall and material for all
                // things randomly"*, and *"wild variatiosn of material typeds in all items
                // equaipment walls floors lights furnature and benches"*. A pillar is a wall --
                // it is literally `wallDef` -- so it takes the room's material for the same
                // reason the ring does, and per **room** rather than per cell for the same reason
                // too: a column whose every cell is a different stone is a patchwork, not a
                // column.
                //
                // Nothing structural changes. Any wall stuff holds a roof, so the
                // `RoofMaxSupportDistance` lattice is untouched; this is only what the pillar is
                // built from.
                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))
                { PlaceWall(map, pillar, wallDef, roomWallStuff); }
            }
            PlaceNativeDoors(coordinate.Rooms, map);
            return corridorSides;
        }

        public override void PostMapInitialized(Map map, GenStepParams parms)
        {
            RimroomsDestinationMapParent parent = map == null ? null : map.Parent as RimroomsDestinationMapParent;
            if (parent == null || !parent.LayoutReady || parent.Map != map) { return; }
            foreach (Room room in map.regionGrid.AllRooms)
            {
                if (room != null && !room.UsesOutdoorTemperature)
                {
                    room.TempTracker.Temperature = InitialRoomTemperature;
                }
            }
        }

        private static IntVec3 FindPoweredBuildingCell(Map map, RoomRecord room, ThingDef definition,
            HashSet<IntVec3> reserved, IntVec3 preferred)
        {
            CellRect usable = room.Bounds.ContractedBy(1);
            IntVec3 center = room.Bounds.CenterCell;
            foreach (IntVec3 candidate in OrderedInteriorCells(room, preferred))
            {
                CellRect footprint = GenAdj.OccupiedRect(candidate, Rot4.North, definition.size);
                bool fits = true;
                foreach (IntVec3 cell in footprint.Cells)
                {
                    if (!usable.Contains(cell) || !cell.InBounds(map) || reserved.Contains(cell) ||
                        !cell.Standable(map) || cell.GetEdifice(map) != null || cell.GetFirstItem(map) != null ||
                        Math.Abs(cell.x - center.x) <= 1 || Math.Abs(cell.z - center.z) <= 1)
                    {
                        fits = false;
                        break;
                    }
                }
                if (fits) { return candidate; }
            }
            throw new InvalidOperationException("RR_Generation_NoSafeRoomCell");
        }

        private static void ReserveFootprint(IntVec3 position, ThingDef definition, HashSet<IntVec3> reserved)
        {
            foreach (IntVec3 cell in GenAdj.OccupiedRect(position, Rot4.North, definition.size).Cells)
            { reserved.Add(cell); }
        }

        /// <summary>
        /// The same question <see cref="FindPoweredBuildingCell"/> asks, answered with
        /// <c>IntVec3.Invalid</c> instead of a throw.
        ///
        /// A light is lighting. A room too cramped for a three-cell strip gets a standing lamp
        /// from the caller's fallback; it must never cost the coordinate, which is the decision this
        /// generator has already made about every light placement rule it has.
        /// </summary>
        private static IntVec3 TryFindFootprintCell(Map map, RoomRecord room, ThingDef definition,
            HashSet<IntVec3> reserved, IntVec3 preferred)
        {
            if (map == null || room == null || definition == null) { return IntVec3.Invalid; }
            CellRect usable = room.Bounds.ContractedBy(1);
            IntVec3 center = room.Bounds.CenterCell;
            foreach (IntVec3 candidate in OrderedInteriorCells(room, preferred))
            {
                if (FootprintClear(map, GenAdj.OccupiedRect(candidate, Rot4.North, definition.size),
                        usable, center, reserved))
                { return candidate; }
            }
            return IntVec3.Invalid;
        }

        /// <summary>
        /// Whether every cell of this footprint is open floor inside the room, off the reserved set
        /// and off the three-cell route cross -- the one rule every multi-cell placement here shares.
        /// </summary>
        private static bool FootprintClear(Map map, CellRect footprint, CellRect usable, IntVec3 center,
            HashSet<IntVec3> reserved)
        {
            foreach (IntVec3 cell in footprint.Cells)
            {
                if (!usable.Contains(cell) || !cell.InBounds(map) || reserved.Contains(cell) ||
                    !cell.Standable(map) || cell.GetEdifice(map) != null || cell.GetFirstItem(map) != null ||
                    Math.Abs(cell.x - center.x) <= 1 || Math.Abs(cell.z - center.z) <= 1)
                { return false; }
            }
            return true;
        }

        /// <summary>
        /// Conduit from the generator to each known consumer, and nothing more.
        ///
        /// **This used to carpet every powered room with conduit, and that is what stopped every
        /// 300x300 coordinate from generating.** The carpet existed for one stated reason:
        /// `RoomContentBuilder` adds another lamp to each powered room *after* the grid is laid,
        /// so the room was pre-wired to catch it. At 12x12 rooms that was about a hundred cells.
        /// At depth 1 a service_passage is 60x80, so `ContractedBy(1)` is **4,524 cells** against
        /// a `MaxNativePowerConduits` cap of **512** — an eightfold blowout on the first powered
        /// room, every time.
        ///
        /// Wiring four thousand cells to catch one lamp is the wrong shape at any size. The lamp
        /// is picked up by <see cref="ConnectStrayConsumers"/> after content placement instead.
        ///
        /// Returns the wired set, so that later pass can route from the grid that exists.
        /// </summary>
        private static HashSet<IntVec3> SpawnNativePowerNetwork(Map map, TerrainDef voidFloor,
            ThingDef conduitDef, CellRect generatorFootprint, IEnumerable<CellRect> consumerFootprints)
        {
            var wiredCells = new HashSet<IntVec3>();
            foreach (IntVec3 cell in generatorFootprint.Cells.OrderBy(value => value.x).ThenBy(value => value.z))
            {
                if (!cell.InBounds(map) || map.terrainGrid.TerrainAt(cell) == voidFloor)
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                // These cells are logical BFS roots owned by the generator itself. A physical
                // conduit here would create a duplicate transmitter on the generator footprint.
                wiredCells.Add(cell);
            }

            foreach (CellRect consumer in consumerFootprints)
            {
                if (wiredCells.Count >= MaxNativePowerConduits) { break; }
                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells, consumer);
                // An empty route means this consumer could not be reached. Skipped, not fatal:
                // the same rule the stray pass and the power validation already follow.
                for (int step = 0; step < route.Count; step++)
                {
                    if (wiredCells.Count >= MaxNativePowerConduits) { break; }
                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells,
                        consumer);
                }
            }

            return wiredCells;
        }

        /// <summary>
        /// Connect anything that draws power and is not on the generator's net yet.
        ///
        /// Run **after** `RoomContentBuilder.Populate`, because that is when the lamps and benches
        /// the archetype dressing places actually exist. This replaces pre-wiring whole rooms on
        /// the chance that something would land in them.
        ///
        /// Uses the same map-wide `CompPowerTrader` sweep `ValidateNativePowerNetwork` uses to
        /// *detect* the problem — so the thing that reports a stray consumer and the thing that
        /// fixes one agree by construction rather than by two people remembering the same rule.
        ///
        /// **Never throws.** A lamp that cannot be reached is a dark corner; the validation below
        /// reports it and the coordinate still exists. Losing the whole place over a conduit is
        /// what this checkpoint is fixing.
        ///
        /// Returns whether the grid is still answering. False means a rebuild refused part-way
        /// and the sweep stopped, so the caller must not rebuild again either.
        /// </summary>
        private static bool ConnectStrayConsumers(Map map, CoordinateRecord coordinate,
            TerrainDef voidFloor, ThingDef conduitDef,
            HashSet<IntVec3> wiredCells, Thing generator)
        {
            CompPowerPlant plant = generator == null ? null : generator.TryGetComp<CompPowerPlant>();
            if (plant == null || wiredCells == null) { return true; }
            // Ordered, so the routing is the same on a regenerated coordinate.
            List<Thing> consumers = map.listerThings.AllThings
                .Where(thing => thing != null && thing.Spawned && thing.Map == map &&
                    thing.TryGetComp<CompPowerTrader>() != null)
                .OrderBy(thing => thing.Position.x).ThenBy(thing => thing.Position.z)
                .ThenBy(thing => thing.def.defName, StringComparer.Ordinal)
                .ToList();
            for (int index = 0; index < consumers.Count; index++)
            {
                Thing consumer = consumers[index];
                CompPowerTrader power = consumer.TryGetComp<CompPowerTrader>();
                if (power == null || power.PowerNet == plant.PowerNet) { continue; }
                if (wiredCells.Count >= MaxNativePowerConduits) { return true; }
                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells,
                    consumer.OccupiedRect());
                bool capped = false;
                for (int step = 0; step < route.Count; step++)
                {
                    if (wiredCells.Count >= MaxNativePowerConduits) { capped = true; break; }
                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells,
                        consumer.OccupiedRect());
                }
                // **Stop the sweep the first time the rebuild fails.** Every decision after that
                // reads `power.PowerNet` out of bookkeeping Core has already told us is wrong, and
                // every further call re-applies its half-processed queue. See RebuildPowerNets:
                // this loop is where the owner's sixty-two warnings came from.
                if (!RebuildPowerNets(map, coordinate)) { return false; }
                if (capped) { return true; }
            }
            return true;
        }

        /// <summary>
        /// A conduit where one will fit, and silence where it will not.
        ///
        /// The throwing form is kept for the generator's own footprint and the known consumer
        /// routes, where a failure really is a generator fault. This form is for the opportunistic
        /// pass, where a cell that cannot take a conduit is a dark corner rather than a broken
        /// coordinate.
        /// </summary>
        private static void TrySpawnNativeConduit(Map map, TerrainDef voidFloor, ThingDef conduitDef,
            IntVec3 cell, HashSet<IntVec3> wiredCells, CellRect exemptFootprint)
        {
            // **THE SAME EXEMPTION THE ROUTE SEARCH MAKES, AND IT HAS TO BE BOTH OR NEITHER.**
            // `FindConduitRoute` now admits the last step onto the consumer's own footprint so a
            // wall-mounted lamp can be reached at all. Refusing to place the conduit there would
            // have produced a route that ends one cell short -- a fix that passes a reading and
            // changes nothing, which is worse than the defect because it looks solved.
            //
            // Narrow on purpose: only cells of the thing being wired. The void rule still keeps
            // conduits out of solid rock everywhere else.
            if (!cell.InBounds(map)) { return; }
            if (map.terrainGrid.TerrainAt(cell) == voidFloor && !exemptFootprint.Contains(cell))
            { return; }
            if (!wiredCells.Add(cell)) { return; }
            if (AlreadyTransmits(map, cell)) { return; }
            Thing conduit = MakeBuilding(conduitDef, null);
            conduit.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(conduit, cell, map, Rot4.North);
        }

        /// <summary>
        /// Rebuild Core's power nets, and **never let the power grid cost the coordinate.**
        ///
        /// This was `map.powerNetManager.UpdatePowerNetsAndConnections_First()`, called bare in
        /// three places. Core throws out of it when its transmitter bookkeeping is inconsistent --
        /// which a duplicate transmitter on one cell makes it -- and because this runs inside
        /// `GenStep.Generate`, **that one throw stopped the whole level being built.** The
        /// coordinate's map existed and was never finished, `EnsureSite` reported failure, and
        /// `SoloGroupOpening` never reached the step that marks the gate door. Three launches in a
        /// row the owner reported a door that was not blue, and all three times the door was
        /// fine and the level behind it was not.
        ///
        /// **The decision was already made and written down twelve lines below**, about the power
        /// validation: *"A coordinate whose heater or one lamp failed to join the grid is dark and
        /// cold and completely playable. A coordinate that does not exist costs the player the
        /// gate that leads to it."* The validation honoured it. The rebuild it validates did not.
        ///
        /// Caught broadly on purpose: the throw comes from inside Core, through another mod's
        /// comp in the general case, and there is no exception type that usefully distinguishes
        /// *"this grid is wrong"* from *"this grid is wrong in a way we predicted"*. The warning
        /// names the coordinate so a bad grid is still findable in a log.
        /// </summary>
        /// <remarks>
        /// **Returns false once, and then is not asked again.** The owner's log carried
        /// **sixty-two** copies of the warning below and, in the middle of them, Core's
        /// *"Tried to register trasmitter ... but there is already a power net here"* -- naming
        /// the generator, on the generator's own cell, which no conduit of ours can ever occupy.
        ///
        /// **The retry is what produced that.** Core processes its delayed register/deregister
        /// queue inside this call and only clears the entries it processed **after** the loop, so
        /// a throw part-way through leaves the already-applied entries queued. Calling again
        /// re-applies them, and re-registering a transmitter that is already registered is the
        /// permanent fault this generator documents in `AlreadyTransmits`. So the first failure
        /// was the real one and the next sixty-one were self-inflicted.
        ///
        /// The exception is logged **in full** rather than by type name. Sixty-two lines reading
        /// `(NullReferenceException)` could not say which Core method or which thing, and that
        /// was the whole question; one line with a stack can answer it next time.
        /// </remarks>
        private static bool RebuildPowerNets(Map map, CoordinateRecord coordinate)
        {
            if (map == null || map.powerNetManager == null) { return false; }
            try
            {
                map.powerNetManager.UpdatePowerNetsAndConnections_First();
                return true;
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms][Generation] Coordinate "
                    + (coordinate == null ? "(unknown)" : coordinate.Id)
                    + " could not rebuild its power connections, and will not be asked again this"
                    + " generation. The space, its gate anchor and its way home are unaffected. "
                    + exception);
                return false;
            }
        }

        /// <summary>
        /// Whether something on this cell already carries power along it.
        ///
        /// **TWO TRANSMITTERS ON ONE CELL IS A PERMANENT FAULT, not a warning.** Core's
        /// `PowerNetManager` refuses the second one -- *"there is already a power net here. There
        /// can't be two transmitters on the same cell"* -- and leaves its own bookkeeping
        /// inconsistent, so `PowerConnectionMaker.TryConnectToAnyPowerNet` throws a
        /// `NullReferenceException` out of `Map.FinalizeInit` **and then out of every single
        /// Update for the rest of the session.** The owner's log had hundreds of them.
        ///
        /// `wiredCells` is this generator's own bookkeeping and **cannot see a transmitter
        /// somebody else put there.** Several mods in the owner's profile attach a hidden conduit
        /// under a powered building automatically, and the lamps this generator now places on
        /// every pillar are powered buildings -- so a conduit route crossing a lamp's cell lands
        /// on a transmitter that is already there.
        ///
        /// Core answers the question itself through `ThingDef.EverTransmitsPower`, which is the
        /// same property `PowerNetManager` registers on, so this cannot disagree with it. Asked
        /// of whatever is on the cell rather than of a def we expect, because the point is
        /// precisely that we did not put it there.
        /// </summary>
        private static bool AlreadyTransmits(Map map, IntVec3 cell)
        {
            List<Thing> things = cell.GetThingList(map);
            for (int index = 0; index < things.Count; index++)
            {
                Thing thing = things[index];
                if (thing != null && thing.def != null && thing.def.EverTransmitsPower)
                { return true; }
            }
            return false;
        }

        private static List<IntVec3> FindConduitRoute(Map map, TerrainDef voidFloor,
            HashSet<IntVec3> wiredCells, CellRect target)
        {
            var pending = new Queue<IntVec3>();
            var roots = new HashSet<IntVec3>();
            var previous = new Dictionary<IntVec3, IntVec3>();
            foreach (IntVec3 cell in wiredCells.OrderBy(value => value.x).ThenBy(value => value.z))
            {
                if (!cell.InBounds(map) || map.terrainGrid.TerrainAt(cell) == voidFloor || !roots.Add(cell)) { continue; }
                pending.Enqueue(cell);
            }
            IntVec3 destination = IntVec3.Invalid;
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            while (pending.Count > 0)
            {
                IntVec3 current = pending.Dequeue();
                if (target.Contains(current)) { destination = current; break; }
                foreach (IntVec3 direction in directions)
                {
                    IntVec3 next = current + direction;
                    // **THE CONSUMER'S OWN FOOTPRINT IS EXEMPT FROM THE VOID RULE, AND A WALL LAMP
                    // IS WHY.** `voidFloor` is `WaterDeep` and `BuildShell` sets it on **every cell
                    // of the map** before the rooms are carved -- so only a room's *interior* ever
                    // gets a floor, and a room's own **wall cells keep void terrain**.
                    //
                    // A `WallLamp` is mounted *in* a wall, so its only cell is a void cell, so this
                    // search could never arrive at it and the lamp was never wired. That is exactly
                    // what the owner's 2026-10-06 log reported: *"WallLamp is not on the generator's
                    // power net"* -- and wall lamps are the Backrooms look, so it is the fixture
                    // most likely to be left dark.
                    //
                    // **Exempting only the target keeps the rock impassable to routing.** The void
                    // rule exists so conduits do not tunnel through solid rock between rooms, and it
                    // still does: this admits the last step onto the thing being wired and nothing
                    // else. A conduit under a wall is ordinary vanilla construction.
                    bool exempt = target.Contains(next);
                    if (!next.InBounds(map) ||
                        (!exempt && map.terrainGrid.TerrainAt(next) == voidFloor) ||
                        roots.Contains(next) || previous.ContainsKey(next)) { continue; }
                    previous[next] = current;
                    pending.Enqueue(next);
                }
            }
            // **Empty rather than fatal.** A consumer the conduit cannot reach is a dark
            // corner; the caller skips it and `ValidateNativePowerNetwork` reports it. Throwing
            // here destroyed the whole coordinate, which is the defect that cost two launches.
            if (!destination.IsValid) { return new List<IntVec3>(); }

            var route = new List<IntVec3>();
            IntVec3 cursor = destination;
            route.Add(cursor);
            while (!roots.Contains(cursor))
            {
                IntVec3 predecessor;
                // Same reasoning: a broken trail is a dark corner, not a dead place.
                if (!previous.TryGetValue(cursor, out predecessor)) { return new List<IntVec3>(); }
                cursor = predecessor;
                route.Add(cursor);
            }
            route.Reverse();
            return route;
        }

        private static void PrimeNativeGenerator(Thing generator, ThingDef fuelDef, IntVec3 preferredFuelCell,
            RoomRecord room, HashSet<IntVec3> reserved, Map map)
        {
            CompRefuelable refuelable = generator == null ? null : generator.TryGetComp<CompRefuelable>();
            if (refuelable == null || fuelDef == null || fuelDef.stackLimit < 1)
            { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }
            int units = refuelable.GetFuelCountToFullyRefuel();
            long requiredStacks = units < 1 ? 0 : ((long)units + fuelDef.stackLimit - 1) / fuelDef.stackLimit;
            if (units < 1 || requiredStacks > MaxInitialFuelStacks)
            { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }

            var fuel = new List<Thing>();
            int remaining = units;
            foreach (IntVec3 cell in OrderedInteriorCells(room, preferredFuelCell))
            {
                if (remaining <= 0) { break; }
                if (!cell.InBounds(map) || !cell.Standable(map) || reserved.Contains(cell) ||
                    cell.GetEdifice(map) != null || cell.GetFirstItem(map) != null) { continue; }
                Thing stack = ThingMaker.MakeThing(fuelDef);
                stack.stackCount = Math.Min(remaining, fuelDef.stackLimit);
                GenSpawn.Spawn(stack, cell, map);
                if (!stack.Spawned || stack.Map != map)
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                fuel.Add(stack);
                reserved.Add(cell);
                remaining -= stack.stackCount;
            }
            if (remaining != 0 || fuel.Count != (int)requiredStacks)
            { throw new InvalidOperationException("RR_Generation_NoSafeRoomCell"); }

            refuelable.Refuel(fuel);
            if (!refuelable.HasFuel || !refuelable.IsFull)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
        }

        /// <summary>
        /// Whether everything on this coordinate that needs power is on the generator's grid.
        /// Returns a short human-readable fault, or **null** when the grid is complete.
        ///
        /// ## The bug this replaces, because it is the most expensive one this project has had
        ///
        /// Until 0.12.48-dev this method counted things whose `def == lightDef` and required the
        /// total to equal a formula re-derived from the coordinate:
        ///
        ///     Rooms.Count + Rooms.Count(service_passage or utility_room)
        ///
        /// The extra lamps in that formula are placed by <see cref="RoomContentBuilder"/>, which
        /// spawns a hard-coded **`StandingLamp`**. The formula was correct while `lightDef` was
        /// also `StandingLamp`. **`BackroomsPalette` switched the fixture to `WallLamp` at
        /// 0.7.8-dev**, so from that checkpoint the count of `WallLamp`s could never include the
        /// `StandingLamp`s the formula expected. `climateRoom` requires at least one
        /// service_passage or utility_room to exist, so the shortfall was **guaranteed** and
        /// **every coordinate failed to generate for thirty-nine checkpoints.** No proof caught
        /// it because they read source text, and nothing had ever run this generator until a
        /// player reached a gate.
        ///
        /// ## Why this shape cannot go stale the same way
        ///
        /// It never names a def and never predicts a count. The lights are the list the caller
        /// **actually spawned**, and the last check sweeps **every `CompPowerTrader` on the map**
        /// — so a lamp, bench or heater that any other code adds later is covered automatically,
        /// which is what the formula was trying and failing to do by arithmetic.
        /// </summary>
        private static string ValidateNativePowerNetwork(Map map, Thing generator, Thing heater,
            List<Thing> placedLights)
        {
            CompPowerPlant plant = generator == null ? null : generator.TryGetComp<CompPowerPlant>();
            CompRefuelable fuel = generator == null ? null : generator.TryGetComp<CompRefuelable>();
            if (plant == null) { return "the generator has no power-plant component"; }
            if (plant.PowerNet == null) { return "the generator is not on any power net"; }
            if (fuel == null || !fuel.HasFuel) { return "the generator has no fuel"; }
            if (heater == null || !heater.Spawned || heater.Map != map)
            { return "the climate unit is not on this map"; }

            foreach (Thing light in placedLights)
            {
                if (light == null || !light.Spawned || light.Map != map)
                { return "a room light is not on this map"; }
            }

            // Every consumer, whatever placed it and whatever def it is. This is the invariant a
            // player can actually see -- nothing here is dark or cold -- and it covers the lamps
            // RoomContentBuilder adds after the grid is laid without naming them.
            //
            // **A light that draws no power is not a consumer.** The fitted fluorescent lights
            // itself; asking the grid about it would fault every coordinate for the fixture
            // working as designed.
            var consumers = new List<Thing> { heater };
            foreach (Thing light in placedLights)
            {
                if (light.TryGetComp<CompPowerTrader>() != null) { consumers.Add(light); }
            }
            foreach (Thing thing in map.listerThings.AllThings)
            {
                if (thing == null || !thing.Spawned || thing.Map != map || consumers.Contains(thing))
                { continue; }
                if (thing.TryGetComp<CompPowerTrader>() != null) { consumers.Add(thing); }
            }
            foreach (Thing consumer in consumers)
            {
                CompPowerTrader power = consumer.TryGetComp<CompPowerTrader>();
                if (power == null)
                { return consumer.def.defName + " cannot draw power"; }
                if (power.PowerNet == null || power.PowerNet != plant.PowerNet)
                { return consumer.def.defName + " is not on the generator's power net"; }
            }
            return null;
        }

        private static void ClearMapContents(Map map)
        {
            foreach (Thing thing in map.listerThings.AllThings.ToList())
            {
                if (thing != null && !thing.Destroyed)
                {
                    thing.Destroy(DestroyMode.Vanish);
                }
            }
        }

        private static void BuildRoomWalls(
            RoomRecord room,
            IReadOnlyList<RoomRecord> rooms,
            Map map,
            ThingDef wallDef,
            ThingDef wallStuff)
        {
            CellRect bounds = room.Bounds;
            foreach (IntVec3 cell in bounds.Cells)
            {
                bool edge = cell.x == bounds.minX || cell.x == bounds.maxX ||
                    cell.z == bounds.minZ || cell.z == bounds.maxZ;
                if (edge && !IsDoorOpening(room, rooms, cell))
                {
                    PlaceWall(map, cell, wallDef, wallStuff);
                }
            }
        }

        private static bool IsDoorOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            return RoomLayoutPlanner.DoorOpening(room, rooms, cell);
        }

        private static void PlaceNativeDoors(IReadOnlyList<RoomRecord> rooms, Map map)
        {
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("Door");
            if (definition == null) { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }
            foreach (RoomRecord room in rooms)
            {
                foreach (IntVec3 cell in room.Bounds.Cells.Where(c => IsDoorOpening(room, rooms, c)))
                {
                    SpawnNativeDoor(map, cell, definition,
                        cell.x == room.Bounds.minX || cell.x == room.Bounds.maxX ? Rot4.East : Rot4.North,
                        true);
                }
            }
        }

        /// <summary>
        /// One Core door, spawned the one way this generator spawns them. Lifted out of
        /// <see cref="PlaceNativeDoors"/> so the door across a corridor is the same door as the
        /// one in a room's wall, rather than a second spawner that could drift from it.
        ///
        /// A room door is held open, as it always was. A corridor door is not: it is there to end
        /// one stretch of hallway and begin the next, and a door that stands closed is what does
        /// that for a crew walking the place.
        /// </summary>
        private static void SpawnNativeDoor(Map map, IntVec3 cell, ThingDef definition, Rot4 rotation,
            bool holdOpen)
        {
            Building_Door door = ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.Steel : null) as Building_Door;
            if (door == null || cell.GetEdifice(map) != null) { throw new InvalidOperationException("RR_Generation_InvalidDoorDef"); }
            door.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(door, cell, map, rotation);
            if (!door.Spawned || door.Map != map || door.Open) { throw new InvalidOperationException("RR_Generation_InvalidDoorDef"); }
            door.SetForbidden(false, false);
            if (!holdOpen) { return; }
            if (!door.HoldOpen)
            {
                // Invoke the same public native command the player uses; no field reflection or custom door simulation.
                string label = "CommandToggleDoorHoldOpen".Translate().ToString();
                Command_Toggle hold = door.GetGizmos().OfType<Command_Toggle>()
                    .FirstOrDefault(c => c.hotKey == KeyBindingDefOf.Misc3 && c.defaultLabel == label);
                if (hold != null && hold.toggleAction != null) { hold.toggleAction(); }
            }
            if (!door.HoldOpen || door.Open)
            { Log.Warning("[Rimrooms][Generation] Native closed/hold-open door setup unavailable; inspect first-encounter timing."); }
        }

        /// <summary>
        /// The corridors between linked rooms.
        ///
        /// **The width is not a constant any more.** Owner direction, 2026-09-30: *"everything
        /// doesnt have to be ... rectangle halways"*. It comes from
        /// `RoomLayoutPlanner.CorridorHalfWidthBetween`, which `CandidateIsSafe` also reads, so
        /// the reachability the planner proved is the reachability that gets built.
        ///
        /// Carve the routes between rooms, **as rooms**, and report the cells along their walls
        /// that can hold something.
        ///
        /// Owner: *"the hall ways are just rectangles and arnt correctly the themed color and
        /// materials"*, and *"i see the whole map is almost like a string of pears. when it
        /// should just be basicly \"rooms\" as halways with the exact shit thats in the rooms"*.
        ///
        /// **Two hardcoded values were the whole of it.** The floor was the raw carve terrain --
        /// `concrete`, what rock becomes when you clear it -- while every room got the band's
        /// palette floor with accent stripes from `PaintRoom`. And the walls were
        /// `ThingDefOf.Steel`, literally, while a room's walls come from the coordinate's own
        /// materials and carry the band's colour. So a themed yellow room opened onto a grey
        /// steel tunnel, on every link, at every depth.
        ///
        /// The palette comes from `BackroomsPalette.SetFloor`, which is the same call `PaintRoom`
        /// makes, so a corridor cannot drift from the rooms it joins.
        ///
        /// Returns the cells one in from each corridor wall, for the lamps and the dressing. The
        /// **centre line is never included**: a corridor is a route, and the same reasoning that
        /// reserves a room's route cross applies to the whole of a corridor's length.
        /// </summary>
        private static List<IntVec3> BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map,
            CoordinateRecord coordinate, ThingDef wallDef, ThingDef wallStuff, int depth)
        {
            var sides = new List<IntVec3>();
            BackroomsPalette.Look look = BackroomsPalette.For(depth,
                DestinationService.StableHash(coordinate.Seed, coordinate.Id + ":corridors", 1));

            // **EVERY LEG OF EVERY CORRIDOR IS COLLECTED BEFORE A SINGLE CELL IS CUT, and a bend
            // is why.** A three-leg route puts one leg's wall line squarely inside the next leg's
            // floor at the turn -- that is not an edge case, it is what a corner is -- so a carver
            // that walks one pair at a time would wall off the inside of its own corridor. The two
            // walls of a bend's middle leg do the same to the legs either side of it.
            //
            // So the floor of the whole level's corridor network is known first, and a wall is
            // only placed on a cell that no leg anywhere carries floor on. **The planner needs no
            // matching rule**, because `CandidateIsSafe` models corridors by marking floor and
            // never by marking walls: a cell that is floor for one leg is floor, and a cell that
            // is nobody's floor was never walkable to begin with. One rule, one reader each.
            var legsByPair = new List<List<RoomLayoutPlanner.CorridorLeg>>();
            var corridorFloor = new HashSet<IntVec3>();
            foreach (RoomRecord room in rooms)
            {
                foreach (int linkedIndex in room.Links.Where(index => index > room.Index))
                {
                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);
                    // **THE SHAPE COMES FROM THE PLANNER, not from a second derivation here.**
                    // This block rebuilt the corridor's ranges itself -- the extents, the width
                    // offsets, the wall lines and the back-to-back skip -- while `CandidateIsSafe`
                    // rebuilt the same ranges to prove the level walkable. Two readers of one
                    // rule is the defect this project has paid for most often, and the corridor
                    // was the last shape in the generator still derived twice.
                    //
                    // `CorridorLegs` returns no legs for a back-to-back pair, because the doorway
                    // in the shared wall is the route; the planner prunes any link it could not
                    // route, so an empty list here means back to back and nothing else.
                    List<RoomLayoutPlanner.CorridorLeg> legs = RoomLayoutPlanner.CorridorLegs(
                        room, other,
                        Math.Max(RoomLayoutPlanner.ShapeDepthOf(rooms, room, depth),
                            RoomLayoutPlanner.ShapeDepthOf(rooms, other, depth)),
                        rooms);
                    if (legs.Count == 0) { continue; }
                    legsByPair.Add(legs);
                    for (int index = 0; index < legs.Count; index++)
                    {
                        foreach (IntVec3 cell in legs[index].Floor.Cells) { corridorFloor.Add(cell); }
                    }
                }
            }

            foreach (List<RoomLayoutPlanner.CorridorLeg> legs in legsByPair)
            {
                for (int index = 0; index < legs.Count; index++)
                {
                    RoomLayoutPlanner.CorridorLeg leg = legs[index];
                    foreach (IntVec3 cell in leg.Floor.Cells)
                    {
                        SetWalkableRoofedCell(map, cell, look.floor);
                        PaintCorridorCell(map, cell, look, leg.AlongX ? cell.x : cell.z);
                    }
                }
                foreach (IntVec3 cell in RoomLayoutPlanner.CorridorSideCells(legs))
                { sides.Add(cell); }
            }

            foreach (List<RoomLayoutPlanner.CorridorLeg> legs in legsByPair)
            {
                for (int index = 0; index < legs.Count; index++)
                {
                    foreach (IntVec3 cell in legs[index].WallLow.Cells)
                    { PlaceCorridorWall(map, cell, wallDef, wallStuff, look, corridorFloor); }
                    foreach (IntVec3 cell in legs[index].WallHigh.Cells)
                    { PlaceCorridorWall(map, cell, wallDef, wallStuff, look, corridorFloor); }
                }
            }

            // **A DOOR ACROSS EVERY LEG, so the hallways are not one room.** Owner: *"the hallways
            // were one massive room so entering one door basicly explored the whole fucking map"*.
            // Every corridor joins every other corridor with nothing between them, so Core's fog
            // flood -- which stops at a door and nowhere else -- took the whole network the moment
            // a crew stepped out of the threshold room. One door at the midpoint of each leg turns
            // the network into stretches, and a stretch is revealed by walking it.
            //
            // A leg too short to have a middle, and a midpoint that is also another leg's floor (a
            // junction), get no door: a door in a junction is a door in the middle of a crossing.
            var everyLeg = new List<RoomLayoutPlanner.CorridorLeg>();
            foreach (List<RoomLayoutPlanner.CorridorLeg> legs in legsByPair) { everyLeg.AddRange(legs); }
            ThingDef doorDef = DefDatabase<ThingDef>.GetNamedSilentFail("Door");
            for (int index = 0; index < everyLeg.Count; index++)
            { PlaceCorridorDoor(map, everyLeg, index, doorDef, wallDef, wallStuff, look); }
            return sides;
        }

        /// <summary>Shortest leg that gets a door across its middle. Below this it is a doorway, not a hall.</summary>
        private const int ShortestDooredLeg = 9;

        /// <summary>
        /// A wall across this leg at its midpoint with a door in the centre lane. See the caller
        /// for why. Silent when it cannot: a stretch that stays joined to its neighbour is a longer
        /// stretch, not a broken coordinate.
        /// </summary>
        private static void PlaceCorridorDoor(Map map, List<RoomLayoutPlanner.CorridorLeg> legs, int index,
            ThingDef doorDef, ThingDef wallDef, ThingDef wallStuff, BackroomsPalette.Look look)
        {
            if (doorDef == null) { return; }
            RoomLayoutPlanner.CorridorLeg leg = legs[index];
            CellRect floor = leg.Floor;
            int from = leg.AlongX ? floor.minX : floor.minZ;
            int to = leg.AlongX ? floor.maxX : floor.maxZ;
            if (to - from + 1 < ShortestDooredLeg) { return; }
            int mid = (from + to) / 2;
            int lane = leg.AlongX ? (floor.minZ + floor.maxZ) / 2 : (floor.minX + floor.maxX) / 2;
            var line = new List<IntVec3>();
            foreach (IntVec3 cell in floor.Cells)
            {
                if ((leg.AlongX ? cell.x : cell.z) != mid) { continue; }
                for (int other = 0; other < legs.Count; other++)
                {
                    if (other != index && legs[other].Floor.Contains(cell)) { return; }
                }
                if (!cell.InBounds(map) || cell.GetEdifice(map) != null) { return; }
                line.Add(cell);
            }
            foreach (IntVec3 cell in line)
            {
                bool isDoor = (leg.AlongX ? cell.z : cell.x) == lane;
                if (isDoor)
                {
                    // A door across an east-west hall stands in a north-south line, which is the
                    // rotation PlaceNativeDoors uses for a door in a room's east or west wall.
                    SpawnNativeDoor(map, cell, doorDef, leg.AlongX ? Rot4.East : Rot4.North, false);
                    continue;
                }
                PlaceWall(map, cell, wallDef, wallStuff);
                Thing wall = cell.GetEdifice(map);
                if (wall != null && wall.def == wallDef)
                { wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor); }
            }
        }

        /// <summary>
        /// A corridor cell takes the band's floor, with the same accent stripe a room gets.
        ///
        /// `BackroomsPalette.SetFloor` is the call `PaintRoom` makes, so a corridor and the rooms
        /// it joins cannot read as different buildings -- which is what *"arnt correctly the
        /// themed color and materials"* was describing.
        /// </summary>
        private static void PaintCorridorCell(Map map, IntVec3 cell, BackroomsPalette.Look look,
            int along)
        {
            if (look.floor == null) { return; }
            TerrainDef terrain = look.accent != null && along % 4 == 0 ? look.accent : look.floor;
            BackroomsPalette.SetFloor(map, cell, terrain, look.floorColor);
        }

        /// <summary>
        /// A corridor wall is the coordinate's wall in the coordinate's material, in the band's
        /// colour.
        ///
        /// It was `ThingDefOf.Steel`, hardcoded, on every corridor of every coordinate at every
        /// depth -- so the owner's *"every type of wall and material for all things randomly"*
        /// was honoured for rooms and contradicted one cell outside them.
        /// </summary>
        private static void PlaceCorridorWall(Map map, IntVec3 cell, ThingDef wallDef,
            ThingDef wallStuff, BackroomsPalette.Look look, HashSet<IntVec3> corridorFloor)
        {
            // **A CORRIDOR NEVER WALLS OFF ITS OWN FLOOR.** At a bend one leg's wall line runs
            // through the next leg's floor, and two corridors sharing a lane do the same to each
            // other. `PlaceWall` throws `RR_Generation_WallOverlap` on an occupied cell -- which
            // is the right behaviour for a room and would kill generation here -- so the carver
            // settles the whole network's floor first and a wall yields to it.
            if (corridorFloor != null && corridorFloor.Contains(cell)) { return; }
            // A room's own wall already standing here does the job a corridor wall would, and
            // replacing it is not available: the doorway sits at the midpoint of that same wall.
            //
            // **BUT THE ROCK FILL IS NOT A WALL, AND THIS LINE THOUGHT IT WAS.** `BuildShell`
            // fills every cell of the map with natural rock before anything is carved, and natural
            // rock is an edifice -- so this test was true on every corridor wall cell of every
            // coordinate, and **not one corridor wall was ever built.** The owner walked it:
            // *"the hallways were all rock mountain, when they were to be wooden walls on the
            // inital normal backrooms themed areas"*. The palette, the material and the colour
            // below were all correct and all unreachable. `PlaceWall` clears rock itself, which is
            // why the rooms' walls were fine: they never asked this question first.
            Building standing = cell.InBounds(map) ? cell.GetEdifice(map) : null;
            if (standing != null &&
                !(standing.def.building != null && standing.def.building.isNaturalRock))
            { return; }
            PlaceWall(map, cell, wallDef, wallStuff);
            Thing wall = cell.InBounds(map) ? cell.GetEdifice(map) : null;
            if (wall != null && wall.def == wallDef)
            { wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor); }
        }

        /// <summary>
        /// The rock types this map's own tile would naturally have, so a coordinate is made of
        /// the same stone the world around it is. Falls back to any single natural rock def if
        /// the world cannot answer, and to nothing at all if the game has no natural rock —
        /// in which case the space between rooms simply stays as it was.
        /// </summary>
        private static List<ThingDef> NaturalRockTypesFor(Map map)
        {
            var types = new List<ThingDef>();
            if (Find.World != null)
            {
                IEnumerable<ThingDef> natural = Find.World.NaturalRockTypesIn(map.Tile);
                if (natural != null)
                {
                    foreach (ThingDef candidate in natural)
                    {
                        if (candidate != null && candidate.building != null &&
                            candidate.building.isNaturalRock)
                        { types.Add(candidate); }
                    }
                }
            }
            if (types.Count > 0) { return types; }
            foreach (ThingDef candidate in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (candidate.building != null && candidate.building.isNaturalRock &&
                    !candidate.building.isResourceRock)
                { types.Add(candidate); return types; }
            }
            return types;
        }

        /// <summary>
        /// Fill the whole map with solid natural rock, deterministically varied across the
        /// available types. Rooms and corridors are carved back out afterwards.
        ///
        /// The variety is drawn from the coordinate's own saved seed and the cell position, so
        /// the same coordinate is always made of the same stone in the same places — revisiting
        /// a known space never reshuffles it, which is the same rule every other generated
        /// property of a coordinate follows.
        ///
        /// Solid rock everywhere a room or corridor is not.
        ///
        /// **Region rebuilding is suspended for the duration**, which is the same thing Core's
        /// own `GenStep_RocksFromGrid` does and for the same reason: every spawn would otherwise
        /// ask the region grid to re-partition the map. At 60x60 that was 3,600 cells and nobody
        /// noticed. At 300x300 it is up to 90,000, and leaving it on makes the work quadratic in
        /// the worst case. The flag is restored in a `finally` so a throw mid-fill cannot leave
        /// the map with region updates switched off.
        /// </summary>
        private static void FillWithRock(Map map, CoordinateRecord coordinate, List<ThingDef> rockTypes)
        {
            if (rockTypes == null || rockTypes.Count == 0) { return; }
            bool updaterWasEnabled = map.regionAndRoomUpdater.Enabled;
            map.regionAndRoomUpdater.Enabled = false;
            try
            {
                foreach (IntVec3 cell in map.AllCells)
                {
                    if (cell.GetEdifice(map) != null) { continue; }
                    int draw = CampaignSeed.Derive(coordinate.Seed, "rock:" + cell.x + "," + cell.z, 1);
                    ThingDef rock = rockTypes[draw % rockTypes.Count];
                    GenSpawn.Spawn(ThingMaker.MakeThing(rock), cell, map);
                }
            }
            finally { map.regionAndRoomUpdater.Enabled = updaterWasEnabled; }
        }

        /// <summary>Remove whatever natural rock stands in this cell, so a space can be carved.</summary>
        private static void ClearRock(Map map, IntVec3 cell)
        {
            if (!cell.InBounds(map)) { return; }
            Building edifice = cell.GetEdifice(map);
            if (edifice != null && edifice.def.building != null && edifice.def.building.isNaturalRock)
            { edifice.Destroy(DestroyMode.Vanish); }
        }

        private static void SetWalkableRoofedCell(Map map, IntVec3 cell, TerrainDef floor)
        {
            if (!cell.InBounds(map)) { throw new InvalidOperationException("RR_Generation_CorridorOutOfBounds"); }
            // A corridor is carved through the rock fill, so the rock has to go or the corridor
            // would be impassable and the coordinate would be cut into disconnected rooms.
            ClearRock(map, cell);
            map.terrainGrid.SetTerrain(cell, floor);
            // Thick, like every other roofed cell in a coordinate, because constructed roof
            // can be removed and no roof here ever may be.
            map.roofGrid.SetRoof(cell, BackroomsContainmentMapComponent.OverheadRoof);
        }

        private static void PlaceWall(Map map, IntVec3 cell, ThingDef wallDef, ThingDef wallStuff)
        {
            if (!cell.InBounds(map)) { throw new InvalidOperationException("RR_Generation_WallOutOfBounds"); }
            // Natural rock is the fill this coordinate was carved out of, and a wall replacing
            // it is expected rather than an error. The overlap check below still fires for
            // anything else, because that would mean two generated structures collided, which
            // is a real generator fault and must not be silently tolerated.
            ClearRock(map, cell);
            Thing existing = cell.GetEdifice(map);
            if (existing != null)
            {
                throw new InvalidOperationException("RR_Generation_WallOverlap");
            }
            Thing wall = ThingMaker.MakeThing(wallDef, wallStuff);
            GenSpawn.Spawn(wall, cell, map);
        }

        private static IntVec3 FindBuildingCell(Map map, RoomRecord room, ThingDef definition)
        {
            IntVec3 center = room.Bounds.CenterCell;
            foreach (IntVec3 candidate in OrderedInteriorCells(room, center))
            {
                var occupied = GenAdj.OccupiedRect(candidate, Rot4.North, definition.size);
                bool fits = true;
                foreach (IntVec3 cell in occupied.Cells)
                {
                    if (!room.Bounds.Contains(cell) || cell.x == room.Bounds.minX || cell.x == room.Bounds.maxX ||
                        cell.z == room.Bounds.minZ || cell.z == room.Bounds.maxZ || !cell.InBounds(map) ||
                        cell.GetEdifice(map) != null)
                    {
                        fits = false;
                        break;
                    }
                }
                if (fits) { return candidate; }
            }
            throw new InvalidOperationException("RR_Generation_NoReturnAnchorCell");
        }

        private static Thing MakeBuilding(ThingDef definition, ThingDef stuff)
        {
            if (definition.category != ThingCategory.Building)
            {
                throw new InvalidOperationException("RR_Generation_InvalidFixtureDef");
            }
            return ThingMaker.MakeThing(definition, stuff);
        }

        private static IntVec3 FindClearInteriorCell(
            Map map,
            RoomRecord room,
            IntVec3 preferred,
            HashSet<IntVec3> reserved = null)
        {
            foreach (IntVec3 cell in OrderedInteriorCells(room, preferred))
            {
                bool reservedCell = reserved != null && reserved.Contains(cell);
                if (!reservedCell && cell.InBounds(map) && cell.Standable(map) &&
                    cell.GetEdifice(map) == null)
                {
                    return cell;
                }
            }
            throw new InvalidOperationException("RR_Generation_NoSafeRoomCell");
        }

        /// <summary>
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
                        // **Facing INTO the pillar, which is the opposite of what this did.**
                        // Core reads the wall at `position + rotation.FacingCell`, so a lamp one
                        // cell north of a pillar has to face SOUTH to be attached to it. Facing
                        // north looked for a wall two cells past the pillar, found open floor,
                        // and left `GenConstruct.GetWallAttachedTo` returning null -- which Core
                        // dereferences without checking. See WallAttachmentHolds.
                        //
                        // The comment that was here said *"facing out of the pillar: the lamp
                        // draws into the wall behind it, and the wall behind it is the pillar"*.
                        // The intent was right and the arithmetic was inverted.
                        Rot4 facing = Rot4.FromIntVec3(directions[side]).Opposite;
                        if (!WallAttachmentHolds(map, lightDef, cell, facing)) { continue; }
                        Thing lamp = SpawnAttachableLight(map, lightDef, null, cell, facing);
                        if (lamp == null) { continue; }
                        reserved.Add(cell);
                        TintLamp(lamp, coordinate, room, pillar);
                        placedLights.Add(lamp);
                        break;
                    }
                }
            }
        }

        /// <summary>
        /// A strip of our fixture in every bay of a pillared hall: midway between each pillar and
        /// the next one east of it, on the pillar's own row.
        ///
        /// Owner: *"there are thousands of lights just mass numbers of lights in piles and piles of
        /// llights, in the bacrooms lights are normally spaced"*. The pillar lamps were already a
        /// grid; this is the same grid in the fixture the owner drew, one fitting per six-by-six
        /// bay. The lattice is `RoomLayoutPlanner.PillarCells` and nowhere else, for the reason
        /// written on <see cref="SpawnPillarLamps"/>.
        ///
        /// Silent on failure, like every light placer here: a bay that cannot take a strip is a
        /// darker bay.
        /// </summary>
        private static void SpawnBayStrips(Map map, CoordinateRecord coordinate, ThingDef lightDef,
            HashSet<IntVec3> reserved, List<Thing> placedLights)
        {
            if (map == null || coordinate == null || coordinate.Rooms == null || lightDef == null) { return; }
            var step = new IntVec3(RoomLayoutPlanner.PillarSpacing / 2, 0, 0);
            for (int index = 0; index < coordinate.Rooms.Count; index++)
            {
                RoomRecord room = coordinate.Rooms[index];
                if (room == null) { continue; }
                CellRect usable = room.Bounds.ContractedBy(1);
                IntVec3 center = room.Bounds.CenterCell;
                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))
                {
                    IntVec3 at = pillar + step;
                    if (!FootprintClear(map, GenAdj.OccupiedRect(at, Rot4.North, lightDef.size),
                            usable, center, reserved))
                    { continue; }
                    Thing lamp = SpawnAttachableLight(map, lightDef, null, at, Rot4.North);
                    if (lamp == null) { continue; }
                    ReserveFootprint(at, lightDef, reserved);
                    TintLamp(lamp, coordinate, room, pillar);
                    placedLights.Add(lamp);
                }
            }
        }

        /// <summary>How many cells of corridor wall per lamp.</summary>
        private const int CorridorLampSpacing = 7;

        /// <summary>
        /// How many cells of corridor wall per fixture.
        ///
        /// **Eleven put a fixture on every eleventh side cell of several thousand**, and a third
        /// of those rolled a plant pot: the owner's save held 258 pots on one level. Owner,
        /// 2026-10-07: *"and we dont neee 1000 of them on one level"*. Twenty-three is a fixture
        /// every two dozen cells of wall -- a hallway with something in it now and then, which is
        /// what a hallway looks like.
        /// </summary>
        private const int CorridorFixtureSpacing = 23;

        /// <summary>
        /// Most plant pots the corridors of one coordinate may hold. The rooms still place their
        /// own as family fixtures; this caps the hallways, which is where the pile came from.
        /// </summary>
        private const int MaxCorridorPlantPots = 12;

        /// <summary>
        /// Light and furnish the hallways, against their walls only.
        ///
        /// Owner: *"i see the whole map is almost like a string of pears. when it should just be
        /// basicly \"rooms\" as halways with the exact shit thats in the rooms"*.
        ///
        /// `BuildCorridors` reports the cells one in from each corridor wall and **never the
        /// centre line**, so everything placed here is against a wall and the route through the
        /// corridor stays as clear as a room's reserved cross. A three-cell corridor has no side
        /// to speak of and gets nothing; a five-cell one does.
        ///
        /// The fixtures are the families the rooms already use, so a hallway reads as more of the
        /// same building rather than as a themed set of its own -- which is the whole of the
        /// owner's correction.
        ///
        /// Silent on every failure, like `DressRoom`: a corridor that could not take a lamp is a
        /// dark stretch of corridor, and a coordinate must never be lost over scenery.
        /// </summary>
        private static void DressCorridors(Map map, CoordinateRecord coordinate,
            List<IntVec3> sides, ThingDef lightDef, ThingDef floorLightDef, List<Thing> placedLights,
            HashSet<IntVec3> reserved)
        {
            if (map == null || coordinate == null || sides == null || sides.Count == 0) { return; }
            // Ordered, so a regenerated coordinate dresses its corridors identically.
            sides.Sort(delegate (IntVec3 left, IntVec3 right)
            {
                if (left.z != right.z) { return left.z - right.z; }
                return left.x - right.x;
            });

            // **NO LAMP IN THE FIXTURE LIST.** `StandingLamp` was in it, so on top of the corridor
            // lighting every eleventh side cell could roll a second, powered, floor-standing lamp.
            // The owner's save held 1,521 of them. Corridor light comes from the lighting pass
            // below and from nowhere else.
            var fixtures = new List<ThingDef>();
            foreach (string name in new[] { "Shelf", "Stool", "PlantPot" })
            {
                ThingDef candidate = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (candidate != null) { fixtures.Add(candidate); }
            }

            // **SPACED BY WHERE A CELL IS, NOT BY WHERE IT SITS IN A LIST.** This was
            // `index % CorridorLampSpacing` over the side cells sorted by row -- so a hall running
            // east-west got a lamp every seventh cell, and a hall running north-south, whose side
            // cells sit one per row interleaved with every other corridor's, got lamps wherever
            // the seventh entry happened to fall. At a junction the two piled up. Owner: *"piles
            // and piles of llights"*. A cell's own coordinate is the same on every row of the map,
            // so a strip every seventh cell along the hall is a strip every seventh cell.
            var sideSet = new HashSet<IntVec3>(sides);
            bool strip = lightDef != null && !(lightDef.building != null && lightDef.building.isAttachment)
                && (lightDef.size.x > 1 || lightDef.size.z > 1);
            int plantPots = 0;

            for (int index = 0; index < sides.Count; index++)
            {
                IntVec3 cell = sides[index];
                if (!cell.InBounds(map) || reserved.Contains(cell)) { continue; }
                if (!cell.Standable(map) || cell.GetEdifice(map) != null) { continue; }
                if (cell.GetFirstItem(map) != null) { continue; }

                if (strip)
                {
                    // A strip lies along the hall, so it needs the cell on either side of it to be
                    // side cells too: that is what keeps it against the wall and out of the lane.
                    Rot4 along = Rot4.Invalid;
                    if (cell.x % CorridorLampSpacing == 0 && sideSet.Contains(cell + IntVec3.West)
                        && sideSet.Contains(cell + IntVec3.East))
                    { along = Rot4.North; }
                    else if (cell.z % CorridorLampSpacing == 0 && sideSet.Contains(cell + IntVec3.South)
                        && sideSet.Contains(cell + IntVec3.North))
                    { along = Rot4.East; }
                    if (along.IsValid)
                    {
                        CellRect footprint = GenAdj.OccupiedRect(cell, along, lightDef.size);
                        bool clear = true;
                        foreach (IntVec3 part in footprint.Cells)
                        {
                            if (!part.InBounds(map) || reserved.Contains(part) || !part.Standable(map)
                                || part.GetEdifice(map) != null || part.GetFirstItem(map) != null)
                            { clear = false; break; }
                        }
                        if (clear)
                        {
                            Thing fitting = SpawnAttachableLight(map, lightDef, null, cell, along);
                            if (fitting != null)
                            {
                                foreach (IntVec3 part in footprint.Cells) { reserved.Add(part); }
                                TintLamp(fitting, coordinate, null, cell);
                                placedLights.Add(fitting);
                                continue;
                            }
                        }
                    }
                }
                else if (lightDef != null && (cell.x + cell.z) % CorridorLampSpacing == 0)
                {
                    // **Through the one spawner, which finds the wall.** This was
                    // `GenSpawn.Spawn(lamp, cell, map, Rot4.North)` with no wall test of any
                    // kind, and `BackroomsPalette` resolves `WallLamp`, which is an attachment.
                    // A corridor side cell has its wall on exactly one side and almost never the
                    // north one, so most corridor lamps in the place were hanging in mid-air --
                    // and one of those is enough to throw Core's power rebuild out of
                    // `Map.FinalizeInit` and cost the whole level. See WallAttachmentHolds.
                    Thing lamp = SpawnAttachableLight(map, lightDef, floorLightDef, cell, Rot4.North);
                    if (lamp == null) { continue; }
                    reserved.Add(cell);
                    placedLights.Add(lamp);
                    continue;
                }

                if (fixtures.Count == 0 || index % CorridorFixtureSpacing != 0) { continue; }
                int roll = DestinationService.StableHash(coordinate.Seed,
                    "corridorfixture:" + cell.x + "," + cell.z, 1);
                if (roll < 0) { roll = ~roll; }
                ThingDef definition = fixtures[roll % fixtures.Count];
                // Single-cell only: a wider footprint against a corridor wall is how a route
                // stops being a route.
                if (definition.size.x != 1 || definition.size.z != 1) { continue; }
                if (definition.defName == "PlantPot")
                {
                    if (plantPots >= MaxCorridorPlantPots) { continue; }
                    plantPots++;
                }
                // The corridor fixtures are Core defs by name, but a profile is free to patch one
                // into a wall attachment, and an unattached attachment costs the whole level. The
                // sweep would catch it; refusing to place it is cheaper. See WallAttachmentHolds.
                if (!WallAttachmentHolds(map, definition, cell, Rot4.North)) { continue; }
                Thing fixture = ThingMaker.MakeThing(definition,
                    CoordinateMaterials.StuffFor(definition, coordinate, roll));
                if (fixture == null) { continue; }
                // **NOBODY'S, AND FORBIDDEN UNTIL SEEN -- the same two rules the room dressing
                // follows, which this path never did.** Owner: *"the flower pot in the back rooms
                // needs to be forbiden setting them so pawns dont try to plant 100 flower pots"*.
                // This set `Faction.OfPlayer` and never forbade, so every corridor pot was colony
                // property the tick the map existed -- and Core's sowing work looks only at
                // colony-owned growers, which is exactly why the room pots, which carry no
                // faction, never pulled anybody. `UnexploredWorkMapComponent` releases the forbid
                // when the cell is seen; claiming the pot is the player's to do.
                GenSpawn.Spawn(fixture, cell, map, Rot4.North);
                if (!fixture.Spawned || fixture.Map != map) { continue; }
                GeneratedContent.Quieten(fixture);
                reserved.Add(cell);
                if (definition == lightDef) { placedLights.Add(fixture); }
            }
        }

        /// <summary>
        /// Give this lamp a tone of its own.
        ///
        /// Owner: *"we need more lights and mixedered varies of lights"*. The count is answered by
        /// a lamp on every pillar; this is the variety.
        ///
        /// **`CompGlower.GlowColor` and `GlowRadius` are per-instance overrides in Core** -- the
        /// same mechanism that lights one door blue without touching any other door in the game --
        /// so lamps differ from each other with no new def, no new texture and no patch.
        ///
        /// Four tones: office white, a colder fluorescent, the green-yellow of a tube on its way
        /// out, and a dim one with its reach cut by a third. **The dim one is dimmer, never off**:
        /// the owner's *"the basic rooms are well lit"* is the theme, and a dark Backrooms is a
        /// different place entirely.
        ///
        /// Seeded from the coordinate and the pillar, so the same lamp is the same colour on
        /// every visit.
        /// </summary>
        private static void TintLamp(Thing lamp, CoordinateRecord coordinate, RoomRecord room,
            IntVec3 pillar)
        {
            if (lamp == null) { return; }
            CompGlower glower = lamp.TryGetComp<CompGlower>();
            if (glower == null) { return; }
            int seed = coordinate == null ? 0 : coordinate.Seed;
            int draw = DestinationService.StableHash(seed,
                "lamp:" + pillar.x + "," + pillar.z, room == null ? 0 : room.Index);
            if (draw < 0) { draw = ~draw; }
            switch (draw % 4)
            {
                case 0:
                    return;                                   // the ordinary office white
                case 1:
                    glower.GlowColor = new ColorInt(188, 206, 232, 0);   // colder fluorescent
                    return;
                case 2:
                    glower.GlowColor = new ColorInt(214, 222, 142, 0);   // a tube going out
                    return;
                default:
                    // Dimmer, not off. A stretch of corridor darker than the rest reads as a
                    // building left running; a dark one reads as a different game.
                    glower.GlowRadius = glower.GlowRadius * 2f / 3f;
                    return;
            }
        }

        /// <summary>
        /// Removes anything on this coordinate that is a wall attachment and is not attached to a
        /// wall, before Core is asked to wire the place.
        ///
        /// ## Why a sweep as well as a correct spawner
        ///
        /// `SpawnAttachableLight` is the rule and three callers obey it. **This is what makes the
        /// fourth caller harmless.** The cost of getting it wrong is not a missing lamp, it is
        /// `Map.FinalizeInit` throwing at step four of fifteen, the whole level discarded, and
        /// `Root level exception in Update()` every tick afterwards -- and that cost was paid
        /// twice, by two different placers, written two checkpoints apart. A failure that
        /// expensive and that easy to reintroduce deserves a net under it.
        ///
        /// So the invariant is enforced on the finished map rather than trusted from the
        /// placements: whatever put it there, an attachment facing open floor does not survive to
        /// be wired. The worst case is a dark corner, which is the trade this generator makes
        /// everywhere else.
        ///
        /// **Only things on this coordinate's own map, spawned by this generation.** Nothing here
        /// reaches another map or another mod's buildings.
        /// </summary>
        private static void RemoveUnattachedAttachments(Map map, CoordinateRecord coordinate,
            List<Thing> placedLights)
        {
            if (map == null || map.listerThings == null) { return; }
            List<Thing> stranded = map.listerThings.AllThings
                .Where(thing => thing != null && thing.Spawned && thing.Map == map &&
                    thing.def != null && thing.def.building != null && thing.def.building.isAttachment &&
                    GenConstruct.GetWallAttachedTo(thing) == null)
                .OrderBy(thing => thing.Position.x).ThenBy(thing => thing.Position.z)
                .ThenBy(thing => thing.def.defName, StringComparer.Ordinal)
                .ToList();
            if (stranded.Count == 0) { return; }
            Log.Warning("[Rimrooms][Generation] Coordinate " + (coordinate == null ? "(unknown)" : coordinate.Id)
                + ": removed " + stranded.Count + " wall attachment(s) with no wall behind them ("
                + string.Join(", ", stranded.Select(thing => thing.def.defName + " at " + thing.Position
                    + " facing " + thing.Rotation).Distinct().ToArray())
                + "). Core dereferences that wall without checking it, so leaving one would cost "
                + "the whole level. The space, its gate anchor and its way home are unaffected.");
            for (int index = 0; index < stranded.Count; index++)
            {
                Thing thing = stranded[index];
                if (placedLights != null) { placedLights.Remove(thing); }
                thing.Destroy(DestroyMode.Vanish);
            }
        }

        /// <summary>
        /// Whether a wall attachment standing on this cell with this facing really is attached to
        /// something.
        ///
        /// ## This is the defect that cost the owner two launches, and it is a one-line rule
        ///
        /// `RimWorld.PowerConnectionMaker.TryConnectToAnyPowerNet`, Core 1.6, verbatim:
        ///
        /// <code>
        /// BestTransmitterForConnector(pc.parent.def.building.isAttachment
        ///     ? GenConstruct.GetWallAttachedTo(pc.parent).Position
        ///     : pc.parent.Position, pc.parent.Map, disallowedNets);
        /// </code>
        ///
        /// **Core dereferences that wall without checking it.** `GetWallAttachedTo` returns null
        /// when the cell at `position + rotation.FacingCell` holds nothing with
        /// `building.supportsWallAttachments`, so **an attachment facing open floor is a
        /// guaranteed `NullReferenceException` inside Core's own power rebuild** -- and that
        /// rebuild is step four of fifteen in `Map.FinalizeInit`, so regions, pens, plant growth
        /// rates, every `PostMapInit` and the wealth recount never run. The throw leaves
        /// `MapGenerator.GenerateMap`, so `GetOrGenerateMap` throws, so `EnsureSite` reports
        /// failure and `SoloGroupOpening` never moves anybody inside.
        ///
        /// Owner: *"why are my colonists on the world map!!!!!!!!! they should be in the backrooms
        /// in this scenerio"*. And: *"we loaded solo/group start into the backrooms correctly
        /// before"* -- **they did.** `BackroomsPalette` resolves `WallLamp`, which is
        /// `isAttachment`, and the only placer that existed then was
        /// <see cref="FindWallAttachmentCell"/>, which finds the wall first and faces it. The two
        /// placers added afterwards did not: the pillar lamps faced **away** from the pillar they
        /// were mounted on, and the corridor lamps were spawned `Rot4.North` with no wall test at
        /// all. One mistake, made twice, in the two checkpoints the owner is calling a regression.
        ///
        /// Because the queue Core throws out of is never cleared, it re-runs every tick --
        /// `Root level exception in Update()` for the rest of the session, plus *"there is already
        /// a power net here"* when the re-run re-registers the generator.
        ///
        /// **Asked of Core's own function, not re-derived.** Core is what dereferences the answer,
        /// so Core is the only thing whose opinion matters; a local copy of the rule could
        /// disagree with it, and that disagreement is this project's most expensive defect shape.
        /// Non-attachments answer true, because they have nothing to be attached to.
        /// </summary>
        private static bool WallAttachmentHolds(Map map, ThingDef def, IntVec3 cell, Rot4 facing)
        {
            if (map == null || def == null || def.building == null || !def.building.isAttachment)
            { return true; }
            if (!cell.IsValid || !cell.InBounds(map)) { return false; }
            return GenConstruct.GetWallAttachedTo(cell, facing, map) != null;
        }

        /// <summary>
        /// One lamp, spawned only in a way Core can survive: the palette's fixture when it is
        /// genuinely against a wall, the floor-standing fallback when it is not, and **nothing at
        /// all** rather than an attachment hanging in mid-air.
        ///
        /// **One spawner, three callers** -- the room lights, the pillar lamps and the corridor
        /// dressing. All three placed a `WallLamp` their own way and two of the three were wrong;
        /// see <see cref="WallAttachmentHolds"/>. A rule enforced in one place cannot be forgotten
        /// by the next placer somebody adds.
        ///
        /// The preferred facing is tried first so a caller that already knows which wall it meant
        /// keeps it, and the other three are tried before the fixture is given up on: a lamp on a
        /// corridor side cell has a wall on exactly one side and the caller cannot know which.
        /// </summary>
        private static Thing SpawnAttachableLight(Map map, ThingDef lightDef, ThingDef floorLightDef,
            IntVec3 cell, Rot4 preferredFacing)
        {
            if (map == null || !cell.IsValid || !cell.InBounds(map)) { return null; }
            ThingDef chosen = lightDef;
            Rot4 rotation = preferredFacing;
            if (!WallAttachmentHolds(map, lightDef, cell, preferredFacing))
            {
                bool held = false;
                for (int index = 0; index < 4; index++)
                {
                    var candidate = new Rot4(index);
                    if (!WallAttachmentHolds(map, lightDef, cell, candidate)) { continue; }
                    rotation = candidate;
                    held = true;
                    break;
                }
                if (!held)
                {
                    // The floor-standing fallback, and it is checked too: a profile that made its
                    // standing lamp an attachment would otherwise reintroduce the same throw
                    // through the thing meant to avoid it.
                    chosen = floorLightDef;
                    rotation = Rot4.North;
                    if (chosen == null || !WallAttachmentHolds(map, chosen, cell, rotation))
                    { return null; }
                }
            }
            Thing light = MakeBuilding(chosen, chosen.MadeFromStuff ? ThingDefOf.Steel : null);
            if (light == null) { return null; }
            light.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(light, cell, map, rotation);
            return light.Spawned && light.Map == map ? light : null;
        }

        /// <summary>
        /// An interior cell with one of the room's own walls directly behind it, and the rotation
        /// that faces that wall.
        ///
        /// A wall attachment draws itself almost a full cell in its facing direction, so the
        /// rotation is not decoration -- it is the difference between a lamp on the wall and a
        /// lamp hanging over the floor. The wall must be the room's own wall def: a door also
        /// holds up roof, and a lamp mounted on a door is mounted on nothing the moment it opens.
        /// </summary>
        private static IntVec3 FindWallAttachmentCell(Map map, RoomRecord room, IntVec3 preferred,
            ThingDef wallDef, HashSet<IntVec3> reserved, out Rot4 facing)
        {
            facing = Rot4.North;
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            foreach (IntVec3 candidate in OrderedInteriorCells(room, preferred))
            {
                if ((reserved != null && reserved.Contains(candidate)) || !candidate.InBounds(map) ||
                    !candidate.Standable(map) || candidate.GetEdifice(map) != null)
                { continue; }
                foreach (IntVec3 direction in directions)
                {
                    IntVec3 behind = candidate + direction;
                    if (!behind.InBounds(map)) { continue; }
                    Building wall = behind.GetEdifice(map);
                    if (wall == null || wall.def != wallDef) { continue; }
                    facing = Rot4.FromIntVec3(direction);
                    return candidate;
                }
            }
            // **Invalid rather than a throw, deliberately.** A small room whose wall-adjacent
            // cells are all reserved -- the threshold room holds the gate anchor, the entry cell,
            // the return cell and the anchor's whole expanded rect -- would otherwise fail the
            // coordinate outright. A lamp standing on the floor is a cosmetic compromise; a
            // coordinate that does not generate costs the player the gate. This method exists
            // BECAUSE a light placement rule took the whole map down for thirty-nine checkpoints.
            return IntVec3.Invalid;
        }

        private static IEnumerable<IntVec3> OrderedInteriorCells(RoomRecord room, IntVec3 preferred)
        {
            return room.Bounds.Cells
                .Where(cell => cell.x > room.Bounds.minX && cell.x < room.Bounds.maxX &&
                    cell.z > room.Bounds.minZ && cell.z < room.Bounds.maxZ)
                .OrderBy(cell => cell.DistanceToSquared(preferred));
        }

        private static IntVec3 FindAdjacentSafeCell(Map map, RoomRecord threshold, Thing anchor)
        {
            if (anchor == null || anchor.Destroyed || anchor.Map != map || threshold == null)
            {
                throw new InvalidOperationException("RR_Generation_NoReturnCell");
            }
            CellRect footprint = GenAdj.OccupiedRect(anchor.Position, anchor.Rotation, anchor.def.size);
            foreach (IntVec3 candidate in OrderedInteriorCells(threshold, anchor.Position))
            {
                if (!candidate.InBounds(map) || !candidate.Standable(map) || footprint.Contains(candidate)) { continue; }
                foreach (IntVec3 buildingCell in footprint.Cells)
                {
                    if (Math.Abs(candidate.x - buildingCell.x) + Math.Abs(candidate.z - buildingCell.z) == 1)
                    {
                        return candidate;
                    }
                }
            }
            throw new InvalidOperationException("RR_Generation_NoReturnCell");
        }

        private static void ValidatePlacedLayout(
            Map map,
            CoordinateRecord coordinate,
            IntVec3 entry,
            IntVec3 returnCell,
            IntVec3 officeCell,
            Thing anchor)
        {
            using (Core.RimroomsDiagnostics.Measure("route-validation"))
            { ValidatePlacedLayoutCore(map, coordinate, entry, returnCell, officeCell, anchor); }
        }

        private static void ValidatePlacedLayoutCore(Map map, CoordinateRecord coordinate, IntVec3 entry,
            IntVec3 returnCell, IntVec3 officeCell, Thing anchor)
        {
            if (!entry.Standable(map) || !returnCell.Standable(map) || !officeCell.Standable(map) ||
                anchor == null || anchor.Destroyed || anchor.Map != map)
            {
                throw new InvalidOperationException("RR_Generation_InvalidStartOrObjectiveCell");
            }
            foreach (RoomRecord room in coordinate.Rooms)
            {
                if (room == null) { continue; }
                // **ONLY A ROOM THAT CLAIMS A ROUTE HAS TO HAVE ONE, AND THIS LINE IS WHY THE
                // OWNER'S SOLO START DIED ON THE WORLD MAP.**
                //
                // Owner report, 2026-10-06: *"i tried the solo/group start and the people and
                // everything spawned in the world tile map incorrectly... i didnt even see a
                // natrual gate"*. One throw here produced every symptom of that report:
                // `MarkLayoutReady` never ran, so `ValidateExistingMap` saw `!LayoutReady`,
                // so `EnsureSite` failed, so `SoloGroupOpening` returned at step 2 -- before the
                // surface door is marked as the way out and before anybody is moved inside.
                //
                // **`RoomLayoutPlanner` had already settled the rule and this validator was
                // asking a different question**, which is two derivations of one rule -- the
                // defect this project keeps meeting. The planner's own words:
                //
                //   "the reachability proof now asks its question of rooms that **claim** a
                //    route. A room with links must be walkable to; a room with none is a vault,
                //    and the rock around it is `Mineable` like all the fill, so it is reachable
                //    in the only sense this room wants to be."
                //
                // `SealedFamily` is authored with **zero links on purpose** -- `CandidateIsSafe`
                // asserts exactly that -- because a sealed vault is meant to be found by mining,
                // which is the whole of the owner's *"veins leading to other rooms so insentive
                // to mine things out to find isolated undiscorvered rooms"*. So the planner
                // approved a layout and this method then killed the coordinate for containing the
                // feature the planner had deliberately put in it.
                //
                // **Tested on `Links` rather than on the family name**, so there is one
                // derivation and not two: a future family that is also sealed inherits the rule
                // instead of needing to be remembered here.
                if (room.Links == null || room.Links.Count == 0) { continue; }
                IntVec3 walkable = OrderedInteriorCells(room, room.Bounds.CenterCell)
                    .FirstOrDefault(cell => cell.InBounds(map) && cell.Standable(map));
                if (!walkable.IsValid || !Reachable(map, entry, walkable))
                {
                    // **THE FAILURE NAMES THE ROOM, because the one that fired said nothing.**
                    // `RR_Generation_UnreachableRoom` cost a log dive to attribute and still did
                    // not say which room, which family, or whether the fault was no standable
                    // cell at all versus a standable cell with no route. The thrown message stays
                    // the bare key -- it is a keyed string a player reads, and
                    // `FailedSiteRecovery` matches on it -- so the detail goes beside it.
                    // **ONE OPTIONAL ROOM NO LONGER COSTS THE WHOLE COORDINATE, 2026-10-09.** Found
                    // playing the solo/group inside start: a `borrowed_corridor` at (268,63)-(275,70)
                    // claimed four links with no route from the entry, and this line refused the
                    // coordinate -- so the door that led to it offered "Walk through" and then went
                    // nowhere. Owner, verbatim: *"your not walking through the door correctly u are
                    // doing it wrong !!! figure it out not keep doing whats not working"*.
                    //
                    // An unreachable linked room is now treated exactly as the planner already treats
                    // a sealed vault: its walls come down and the rock around it is `Mineable`, so it
                    // is reached by working toward it. What strands people is the office and the way
                    // home, and those two stay fatal just below. The detail still goes to the log so
                    // the planner fault behind it can be found.
                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id + " room "
                        + room.Index + " (" + room.FamilyId + ") at " + room.Bounds
                        + " claims " + room.Links.Count + " link(s) and "
                        + (walkable.IsValid
                            ? "its interior cell " + walkable + " has no route from the entry at "
                                + entry + "."
                            : "has no standable interior cell at all.")
                        + " Kept as a room to dig to; the coordinate stands.");
                    continue;
                }
            }
            if (!Reachable(map, entry, officeCell) || !Reachable(map, entry, returnCell))
            {
                throw new InvalidOperationException("RR_Generation_UnreachableRequiredCell");
            }
            RoomContentMapComponent content = map.GetComponent<RoomContentMapComponent>();
            if (content == null || !content.PopulationComplete || content.Clues.Count != coordinate.Rooms.Count)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
            foreach (RoomClueRecord clue in content.Clues)
            {
                Thing landmark = clue.Landmark;
                if (landmark == null || !landmark.Spawned || landmark.Map != map)
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                // A furniture clue may be impassable; a real, reachable adjacent inspection or
                // pickup cell is what makes it readable.
                CellRect footprint = landmark.OccupiedRect();
                bool reachable = footprint.ExpandedBy(1).Cells.Any(cell => cell.InBounds(map) && cell.Standable(map) &&
                    (footprint.Contains(cell) || footprint.Cells.Any(part =>
                        Math.Abs(cell.x - part.x) + Math.Abs(cell.z - part.z) == 1)) && Reachable(map, entry, cell));
                // **Reported, never fatal, and that is the decision this generator already made
                // twice.** Its own words about the power grid: *"A coordinate whose heater or one
                // lamp failed to join the grid is dark and cold and completely playable. A
                // coordinate that does not exist costs the player the gate that leads to it."*
                // One clue nobody can walk up to is one awkward room. Throwing here took the
                // whole level, and with it the gate, the way home and the owner's start --
                // *"i ended up in the world map with no connection to the back rooms"*.
                //
                // `RoomContentBuilder.RouteTrunk` is what makes this rare; this is what makes it
                // survivable. The structural checks below and above stay fatal, because a
                // coordinate you cannot walk through really is broken.
                //
                // **It also leaves one throw site for `RR_Generation_UnreachableRequiredCell`.**
                // Two sites raising one key is why that log could not say which had fired, and
                // reading the source could not answer it either.
                // **A SEALED VAULT'S CLUE IS UNREACHABLE BY DESIGN, and warning about it was the
                // one warning every launch produced.** *"the clue Gold in room 32 ... has no
                // reachable cell beside it"* appeared on 2026-10-06 and again on the first fresh
                // start of 2026-10-07, both times in the vault: a room with no links whose only
                // way in is a pick, dressed with gold on purpose. Measured against `Links`, the
                // same test the room loop above uses, so there is one derivation and not two.
                RoomRecord clueRoom = coordinate.Rooms.FirstOrDefault(room => room.Index == clue.RoomIndex);
                bool sealedRoom = clueRoom != null && (clueRoom.Links == null || clueRoom.Links.Count == 0);
                if (!reachable && !sealedRoom)
                {
                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id + ": the clue "
                        + landmark.def.defName + " in room " + clue.RoomIndex + " at "
                        + landmark.Position + " has no reachable cell beside it, so that one room's"
                        + " evidence cannot be collected. The space, its gate anchor and its way"
                        + " home are unaffected.");
                }
            }
        }

        private static bool Reachable(Map map, IntVec3 start, IntVec3 target)
        {
            if (!start.InBounds(map) || !target.InBounds(map) || !start.Standable(map) || !target.Standable(map))
            {
                return false;
            }
            var seen = new HashSet<IntVec3> { start };
            var pending = new Queue<IntVec3>();
            pending.Enqueue(start);
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            while (pending.Count > 0)
            {
                IntVec3 current = pending.Dequeue();
                if (current == target) { return true; }
                foreach (IntVec3 direction in directions)
                {
                    IntVec3 next = current + direction;
                    if (DestinationService.CanTraverseRouteCell(map, next) && seen.Add(next)) { pending.Enqueue(next); }
                }
            }
            return false;
        }
    }
}
