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
        private const int CorridorHalfWidth = 2;
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
                ThingDef wallStuff = ThingDefOf.Steel;
                ThingDef anchorDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_ReturnAnchor");
                ThingDef lightDef = DefDatabase<ThingDef>.GetNamedSilentFail("StandingLamp");
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

                ClearMapContents(map);
                foreach (IntVec3 cell in map.AllCells)
                {
                    map.terrainGrid.SetTerrain(cell, voidFloor);
                    map.roofGrid.SetRoof(cell, null);
                }

                foreach (RoomRecord room in coordinate.Rooms)
                {
                    foreach (IntVec3 cell in room.Bounds.Cells)
                    {
                        map.terrainGrid.SetTerrain(cell, concrete);
                        map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed);
                    }
                }
                BuildCorridors(coordinate.Rooms, map, concrete);

                foreach (RoomRecord room in coordinate.Rooms)
                {
                    BuildRoomWalls(room, coordinate.Rooms, map, wallDef, wallStuff);
                    // A center support complements perimeter walls across the bounded room proportions.
                    PlaceWall(map, room.Bounds.CenterCell, wallDef, wallStuff);
                }
                PlaceNativeDoors(coordinate.Rooms, map);

                RoomRecord threshold = coordinate.Rooms.First(room => room.familyId == "threshold_room");
                IntVec3 anchorPosition = FindBuildingCell(
                    map,
                    threshold,
                    anchorDef);
                Thing anchor = MakeBuilding(anchorDef, anchorDef.MadeFromStuff ? ThingDefOf.Steel : null);
                GenSpawn.Spawn(anchor, anchorPosition, map, Rot4.North);

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
                var lightCells = new List<IntVec3>();
                foreach (RoomRecord room in coordinate.Rooms.OrderBy(value => value.Index))
                {
                    IntVec3 lightCell = FindClearInteriorCell(map, room,
                        room.Bounds.CenterCell + new IntVec3(0, 0, 2), reservedProviderCells);
                    lightCells.Add(lightCell);
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

                for (int index = 0; index < coordinate.Rooms.Count; index++)
                {
                    Thing light = MakeBuilding(lightDef, lightDef.MadeFromStuff ? ThingDefOf.Steel : null);
                    light.SetFaction(Faction.OfPlayer);
                    GenSpawn.Spawn(light, lightCells[index], map, Rot4.North);
                    if (!light.Spawned || light.Map != map)
                    { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                }

                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);
                // Native spawn notifications are queued; rebuild connections now without ticking
                // the power simulation so readiness checks see the actual shared grid.
                map.powerNetManager.UpdatePowerNetsAndConnections_First();
                int expectedPowerLights = coordinate.Rooms.Count + coordinate.Rooms.Count(room =>
                    room.familyId == "service_passage" || room.familyId == "utility_room");
                ValidateNativePowerNetwork(map, generator, climate, lightDef, expectedPowerLights);
                MapGenerator.PlayerStartSpot = entryCell;
                MapGenerator.rootsToUnfog.Add(entryCell);
                MapGenerator.rootsToUnfog.Add(returnCell);

                ValidatePlacedLayout(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);
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

        private static void ValidateNativePowerNetwork(Map map, Thing generator, Thing heater,
            ThingDef lightDef, int expectedRoomLights)
        {
            CompPowerPlant plant = generator == null ? null : generator.TryGetComp<CompPowerPlant>();
            CompRefuelable fuel = generator == null ? null : generator.TryGetComp<CompRefuelable>();
            if (plant == null || plant.PowerNet == null || fuel == null || !fuel.HasFuel ||
                heater == null || !heater.Spawned || heater.Map != map)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }

            List<Thing> lights = map.listerThings.AllThings.Where(thing => thing != null &&
                thing.Spawned && thing.Map == map && thing.def == lightDef).ToList();
            if (lights.Count != expectedRoomLights)
            { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
            var consumers = new List<Thing>(lights) { heater };
            foreach (Thing consumer in consumers)
            {
                CompPowerTrader power = consumer.TryGetComp<CompPowerTrader>();
                if (power == null || power.PowerNet == null || power.PowerNet != plant.PowerNet)
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
            }
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

        private static void BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map, TerrainDef floor)
        {
            foreach (RoomRecord room in rooms)
            {
                foreach (int linkedIndex in room.Links.Where(index => index > room.Index))
                {
                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);
                    CellRect first = room.Bounds;
                    CellRect second = other.Bounds;
                    if (first.CenterCell.z == second.CenterCell.z)
                    {
                        int fromX = Math.Min(first.maxX, second.maxX) + 1;
                        int toX = Math.Max(first.minX, second.minX) - 1;
                        int centerZ = first.CenterCell.z;
                        for (int x = fromX; x <= toX; x++)
                        {
                            for (int offset = -CorridorHalfWidth + 1; offset <= CorridorHalfWidth - 1; offset++)
                            {
                                SetWalkableRoofedCell(map, new IntVec3(x, 0, centerZ + offset), floor);
                            }
                            PlaceWall(map, new IntVec3(x, 0, centerZ - CorridorHalfWidth), ThingDefOf.Wall, ThingDefOf.Steel);
                            PlaceWall(map, new IntVec3(x, 0, centerZ + CorridorHalfWidth), ThingDefOf.Wall, ThingDefOf.Steel);
                        }
                    }
                    else if (first.CenterCell.x == second.CenterCell.x)
                    {
                        int fromZ = Math.Min(first.maxZ, second.maxZ) + 1;
                        int toZ = Math.Max(first.minZ, second.minZ) - 1;
                        int centerX = first.CenterCell.x;
                        for (int z = fromZ; z <= toZ; z++)
                        {
                            for (int offset = -CorridorHalfWidth + 1; offset <= CorridorHalfWidth - 1; offset++)
                            {
                                SetWalkableRoofedCell(map, new IntVec3(centerX + offset, 0, z), floor);
                            }
                            PlaceWall(map, new IntVec3(centerX - CorridorHalfWidth, 0, z), ThingDefOf.Wall, ThingDefOf.Steel);
                            PlaceWall(map, new IntVec3(centerX + CorridorHalfWidth, 0, z), ThingDefOf.Wall, ThingDefOf.Steel);
                        }
                    }
                    else
                    {
                        throw new InvalidOperationException("RR_Generation_NonAdjacentRooms");
                    }
                }
            }
        }

        private static void SetWalkableRoofedCell(Map map, IntVec3 cell, TerrainDef floor)
        {
            if (!cell.InBounds(map)) { throw new InvalidOperationException("RR_Generation_CorridorOutOfBounds"); }
            map.terrainGrid.SetTerrain(cell, floor);
            map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed);
        }

        private static void PlaceWall(Map map, IntVec3 cell, ThingDef wallDef, ThingDef wallStuff)
        {
            if (!cell.InBounds(map)) { throw new InvalidOperationException("RR_Generation_WallOutOfBounds"); }
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
