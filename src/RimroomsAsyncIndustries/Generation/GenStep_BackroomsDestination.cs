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
        private const int MaxNativePowerConduits = 512;
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
                ThingDef wallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff
                    ?? ThingDefOf.Steel;
                ThingDef anchorDef = DefDatabase<ThingDef>.GetNamedSilentFail("Door");
                // Core ships a wall-mounted lamp, which is both closer to the overhead
                // fluorescent the setting wants and better for the look in a second way:
                // an endless corridor reads as endless precisely because nothing is
                // standing in it. Generation used StandingLamp before, which put
                // furniture in the middle of every room.
                ThingDef lightDef = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).light;
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

                BuildShell(map, coordinate, concrete, voidFloor, wallDef, wallStuff);

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
                var lightCells = new List<IntVec3>();
                var lightFacings = new List<Rot4>();
                bool wallMounted = lightDef.building != null && lightDef.building.isAttachment;
                foreach (RoomRecord room in coordinate.Rooms.OrderBy(value => value.Index))
                {
                    IntVec3 lightCell;
                    Rot4 facing = Rot4.North;
                    lightCell = wallMounted
                        ? FindWallAttachmentCell(map, room, room.Bounds.CenterCell,
                            wallDef, reservedProviderCells, out facing)
                        : IntVec3.Invalid;
                    if (!lightCell.IsValid)
                    {
                        // No wall to mount on, or a floor-standing fixture. Either way it goes
                        // where it always went, facing north.
                        facing = Rot4.North;
                        lightCell = FindClearInteriorCell(map, room,
                            room.Bounds.CenterCell + new IntVec3(0, 0, 2), reservedProviderCells);
                    }
                    lightCells.Add(lightCell);
                    lightFacings.Add(facing);
                    reservedProviderCells.Add(lightCell);
                }
                IntVec3 generatorCell = FindPoweredBuildingCell(map, climateRoom, generatorDef,
                    reservedProviderCells, climateRoom.Bounds.CenterCell + new IntVec3(2, 0, 0));
                ReserveFootprint(generatorCell, generatorDef, reservedProviderCells);
                IntVec3 climateCell = FindPoweredBuildingCell(map, climateRoom, climateDef,
                    reservedProviderCells, climateRoom.Bounds.CenterCell + new IntVec3(-2, 0, 0));
                ReserveFootprint(climateCell, climateDef, reservedProviderCells);
                IntVec3 fuelCell = FindClearInteriorCell(map, climateRoom, generatorCell + IntVec3.East,
                    reservedProviderCells);

                var consumerFootprints = new List<CellRect>
                { GenAdj.OccupiedRect(climateCell, Rot4.North, climateDef.size) };
                consumerFootprints.AddRange(lightCells.Select(cell =>
                    GenAdj.OccupiedRect(cell, Rot4.North, lightDef.size)));
                List<CellRect> poweredRoomCoverage = coordinate.Rooms
                    .Where(room => room.familyId == "service_passage" || room.familyId == "utility_room")
                    .Select(room => room.Bounds.ContractedBy(1)).ToList();
                SpawnNativePowerNetwork(map, voidFloor, conduitDef,
                    GenAdj.OccupiedRect(generatorCell, Rot4.North, generatorDef.size), consumerFootprints,
                    poweredRoomCoverage);

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
                    Thing light = MakeBuilding(lightDef, lightDef.MadeFromStuff ? ThingDefOf.Steel : null);
                    light.SetFaction(Faction.OfPlayer);
                    GenSpawn.Spawn(light, lightCells[index], map, lightFacings[index]);
                    if (!light.Spawned || light.Map != map)
                    { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                    placedLights.Add(light);
                }

                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);
                // Native spawn notifications are queued; rebuild connections now without ticking
                // the power simulation so readiness checks see the actual shared grid.
                map.powerNetManager.UpdatePowerNetsAndConnections_First();
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
        /// </summary>
        internal static void BuildShell(Map map, CoordinateRecord coordinate, TerrainDef concrete,
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
            foreach (RoomRecord room in coordinate.Rooms)
            {
                // Owner direction, 2026-09-30: *"everything doesnt have to be square rooms"*.
                // Rock is left standing in the corners, from the SAME function CandidateIsSafe
                // proved the room walkable against -- see RoomLayoutPlanner.RockIntrusionCells.
                var intrusions = new HashSet<IntVec3>(
                    RoomLayoutPlanner.RockIntrusionCells(room, coordinateDepth));
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
            BuildCorridors(coordinate.Rooms, map, concrete, coordinateDepth);

            foreach (RoomRecord room in coordinate.Rooms)
            {
                BuildRoomWalls(room, coordinate.Rooms, map, wallDef, wallStuff);
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
                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))
                { PlaceWall(map, pillar, wallDef, wallStuff); }
            }
            PlaceNativeDoors(coordinate.Rooms, map);
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

        private static void SpawnNativePowerNetwork(Map map, TerrainDef voidFloor, ThingDef conduitDef,
            CellRect generatorFootprint, IEnumerable<CellRect> consumerFootprints,
            IEnumerable<CellRect> poweredRoomCoverage)
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
                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells, consumer);
                foreach (IntVec3 cell in route)
                { SpawnNativeConduit(map, voidFloor, conduitDef, cell, wiredCells); }
            }

            // RoomContentBuilder adds another Core lamp to every service/utility room after this
            // method. Wire each such room first so those later loads join the real native network.
            foreach (IntVec3 cell in poweredRoomCoverage.SelectMany(room => room.Cells)
                .Distinct().OrderBy(value => value.x).ThenBy(value => value.z))
            { SpawnNativeConduit(map, voidFloor, conduitDef, cell, wiredCells); }
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
                    if (!next.InBounds(map) || map.terrainGrid.TerrainAt(next) == voidFloor ||
                        roots.Contains(next) || previous.ContainsKey(next)) { continue; }
                    previous[next] = current;
                    pending.Enqueue(next);
                }
            }
            if (!destination.IsValid) { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }

            var route = new List<IntVec3>();
            IntVec3 cursor = destination;
            route.Add(cursor);
            while (!roots.Contains(cursor))
            {
                IntVec3 predecessor;
                if (!previous.TryGetValue(cursor, out predecessor))
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                cursor = predecessor;
                route.Add(cursor);
            }
            route.Reverse();
            return route;
        }

        private static void SpawnNativeConduit(Map map, TerrainDef voidFloor, ThingDef conduitDef,
            IntVec3 cell, HashSet<IntVec3> wiredCells)
        {
            if (!cell.InBounds(map) || map.terrainGrid.TerrainAt(cell) == voidFloor)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
            if (!wiredCells.Add(cell)) { return; }
            if (wiredCells.Count > MaxNativePowerConduits)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
            Thing conduit = MakeBuilding(conduitDef, null);
            conduit.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(conduit, cell, map, Rot4.North);
            if (!conduit.Spawned || conduit.Map != map)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
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
            var consumers = new List<Thing>(placedLights) { heater };
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
                    Building_Door door = ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.Steel : null) as Building_Door;
                    if (door == null || cell.GetEdifice(map) != null) { throw new InvalidOperationException("RR_Generation_InvalidDoorDef"); }
                    door.SetFaction(Faction.OfPlayer);
                    GenSpawn.Spawn(door, cell, map, cell.x == room.Bounds.minX || cell.x == room.Bounds.maxX ? Rot4.East : Rot4.North);
                    if (!door.Spawned || door.Map != map || door.Open) { throw new InvalidOperationException("RR_Generation_InvalidDoorDef"); }
                    door.SetForbidden(false, false);
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
            }
        }

        /// <summary>
        /// The corridors between linked rooms.
        ///
        /// **The width is not a constant any more.** Owner direction, 2026-09-30: *"everything
        /// doesnt have to be ... rectangle halways"*. It comes from
        /// `RoomLayoutPlanner.CorridorHalfWidthBetween`, which `CandidateIsSafe` also reads, so
        /// the reachability the planner proved is the reachability that gets built.
        /// </summary>
        private static void BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map, TerrainDef floor,
            int depth)
        {
            foreach (RoomRecord room in rooms)
            {
                foreach (int linkedIndex in room.Links.Where(index => index > room.Index))
                {
                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);
                    int halfWidth = RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth);
                    CellRect first = room.Bounds;
                    CellRect second = other.Bounds;
                    if (first.CenterCell.z == second.CenterCell.z)
                    {
                        int fromX = Math.Min(first.maxX, second.maxX) + 1;
                        int toX = Math.Max(first.minX, second.minX) - 1;
                        int centerZ = first.CenterCell.z;
                        for (int x = fromX; x <= toX; x++)
                        {
                            for (int offset = -halfWidth + 1; offset <= halfWidth - 1; offset++)
                            {
                                SetWalkableRoofedCell(map, new IntVec3(x, 0, centerZ + offset), floor);
                            }
                            PlaceWall(map, new IntVec3(x, 0, centerZ - halfWidth), ThingDefOf.Wall, ThingDefOf.Steel);
                            PlaceWall(map, new IntVec3(x, 0, centerZ + halfWidth), ThingDefOf.Wall, ThingDefOf.Steel);
                        }
                    }
                    else if (first.CenterCell.x == second.CenterCell.x)
                    {
                        int fromZ = Math.Min(first.maxZ, second.maxZ) + 1;
                        int toZ = Math.Max(first.minZ, second.minZ) - 1;
                        int centerX = first.CenterCell.x;
                        for (int z = fromZ; z <= toZ; z++)
                        {
                            for (int offset = -halfWidth + 1; offset <= halfWidth - 1; offset++)
                            {
                                SetWalkableRoofedCell(map, new IntVec3(centerX + offset, 0, z), floor);
                            }
                            PlaceWall(map, new IntVec3(centerX - halfWidth, 0, z), ThingDefOf.Wall, ThingDefOf.Steel);
                            PlaceWall(map, new IntVec3(centerX + halfWidth, 0, z), ThingDefOf.Wall, ThingDefOf.Steel);
                        }
                    }
                    else
                    {
                        throw new InvalidOperationException("RR_Generation_NonAdjacentRooms");
                    }
                }
            }
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
        /// </summary>
        /// <summary>
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
                IntVec3 walkable = OrderedInteriorCells(room, room.Bounds.CenterCell)
                    .FirstOrDefault(cell => cell.InBounds(map) && cell.Standable(map));
                if (!walkable.IsValid || !Reachable(map, entry, walkable))
                {
                    throw new InvalidOperationException("RR_Generation_UnreachableRoom");
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
                // A furniture clue may be impassable; require a real, reachable adjacent inspection/pickup cell.
                CellRect footprint = landmark.OccupiedRect();
                bool reachable = footprint.ExpandedBy(1).Cells.Any(cell => cell.InBounds(map) && cell.Standable(map) &&
                    (footprint.Contains(cell) || footprint.Cells.Any(part =>
                        Math.Abs(cell.x - part.x) + Math.Abs(cell.z - part.z) == 1)) && Reachable(map, entry, cell));
                if (!reachable) { throw new InvalidOperationException("RR_Generation_UnreachableRequiredCell"); }
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
