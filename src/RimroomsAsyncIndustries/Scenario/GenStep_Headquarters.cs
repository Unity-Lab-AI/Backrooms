using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>RR-FAC: terrain prepared before any site/biome extra steps run.</summary>
    public sealed class GenStep_HeadquartersTerrain : GenStep
    {
        public override int SeedPart { get { return 81940261; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            RimroomsStartDef start = HeadquartersBuilder.RequireStart(map);
            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }
            MapGenerator.PlayerStartSpot = start.arrivalCell;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell);
            foreach (RimroomsRoomPlan room in start.rooms)
            { MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects").Add(room.Rect); }
        }
    }

    public sealed class GenStep_HeadquartersFacility : GenStep
    {
        public override int SeedPart { get { return 81940262; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            RimroomsStartDef start = HeadquartersBuilder.RequireStart(map);
            HeadquartersSetupComponent receipt = map.GetComponent<HeadquartersSetupComponent>();
            if (receipt.setupStarted) { return; }
            receipt.setupStarted = true;
            receipt.receiptVersion = 2;
            receipt.startDefName = start.defName;
            try
            {
                List<Pawn> staff;
                List<string> roles;
                string refusal;
                if (!ScenPart_RimroomsStart.TryGetStaff(start, Find.GameInitData.startingAndOptionalPawns,
                    out staff, out roles, out refusal)) { throw new InvalidOperationException(refusal); }
                receipt.staff = staff;
                receipt.staffRoles = roles;
                receipt.acceptedSupplies = new List<string>(Current.Game.GetComponent<RimroomsStartupComponent>().SupplySummary);
                HeadquartersBuilder.Build(start, map, receipt);
                receipt.setupComplete = true;
            }
            catch (Exception exception)
            {
                receipt.failure = "RR_Start_PhysicalSetupFailed";
                Log.Error("[Rimrooms][Scenario] Headquarters setup stopped; existing placements are retained: " + exception);
                throw;
            }
        }
    }

    internal static class HeadquartersBuilder
    {
        internal static RimroomsStartDef RequireStart(Map map)
        {
            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;
            if (part == null || part.startDef == null || Find.GameInitData == null ||
                map.Size.x != part.startDef.mapSize || map.Size.z != part.startDef.mapSize ||
                map.Tile != Find.GameInitData.startingTile ||
                Current.Game.GetComponent<RimroomsCampaignComponent>().HasBranch)
            { throw new InvalidOperationException("[Rimrooms] Headquarters generator used outside the initial company start."); }
            return part.startDef;
        }

        internal static void Build(RimroomsStartDef start, Map map, HeadquartersSetupComponent receipt)
        {
            if (!start.arrivalCell.InBounds(map) || !start.stockCell.InBounds(map))
            { throw new InvalidOperationException("Headquarters arrival or receiving position is outside the map."); }
            foreach (RimroomsRoomPlan room in start.rooms)
            {
                CellRect rect = room.Rect;
                if (room.width < 3 || room.height < 3 || !rect.Min.InBounds(map) || !rect.Max.InBounds(map))
                { throw new InvalidOperationException("Invalid headquarters room rectangle."); }
                foreach (IntVec3 cell in rect.Cells)
                {
                    bool edge = cell.x == rect.minX || cell.x == rect.maxX || cell.z == rect.minZ || cell.z == rect.maxZ;
                    if (room.floor) { map.terrainGrid.SetTerrain(cell, start.floorTerrain); }
                    if (edge)
                    {
                        if (cell.GetEdifice(map) != null) { throw new InvalidOperationException("Headquarters wall intersects generated structure at " + cell); }
                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);
                        wall.SetFactionDirect(Faction.OfPlayer);
                        GenSpawn.Spawn(wall, cell, map);
                    }
                    else if (room.roofed) { map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed); }
                    map.areaManager.Home[cell] = true;
                }
            }
            foreach (IntVec3 cell in start.doors)
            {
                Building wall = cell.GetEdifice(map);
                if (wall == null || wall.def != ThingDefOf.Wall) { throw new InvalidOperationException("Headquarters door has no generated wall at " + cell); }
                wall.Destroy(DestroyMode.Vanish);
                Thing door = ThingMaker.MakeThing(ThingDefOf.Door, ThingDefOf.Steel);
                door.SetFactionDirect(Faction.OfPlayer);
                GenSpawn.Spawn(door, cell, map);
            }
            int index = 0;
            foreach (RimroomsBuildingPlan plan in start.buildings)
            {
                if (plan.thing == null) { throw new InvalidOperationException("Unresolved headquarters building definition."); }
                Rot4 rotation = new Rot4(plan.rotation);
                foreach (IntVec3 cell in GenAdj.OccupiedRect(plan.cell, rotation, plan.thing.size).Cells)
                {
                    if (!cell.InBounds(map) || cell.GetEdifice(map) != null)
                    { throw new InvalidOperationException("Headquarters furniture intersects a wall/building at " + cell); }
                }
                Thing building = ThingMaker.MakeThing(plan.thing, plan.stuff);
                building.SetFactionDirect(Faction.OfPlayer);
                building.TryGetComp<CompQuality>()?.SetQuality(QualityCategory.Normal, ArtGenerationContext.Outsider);
                GenSpawn.Spawn(building, plan.cell, map, rotation);
                Building_Bed bed = building as Building_Bed;
                if (bed != null && plan.medical) { bed.Medical = true; }
                CompRefuelable fuel = building.TryGetComp<CompRefuelable>();
                if (fuel != null && plan.fuelFraction > 0f) { fuel.Refuel(fuel.Props.fuelCapacity * Mathf.Clamp01(plan.fuelFraction)); }
                CompPowerBattery battery = building.TryGetComp<CompPowerBattery>();
                if (battery != null && plan.batteryFraction > 0f) { battery.SetStoredEnergyPct(Mathf.Clamp01(plan.batteryFraction)); }
                receipt.placedRecords.Add("building:" + index++ + ":" + building.GetUniqueLoadID());
            }
            foreach (RimroomsConduitPlan line in start.conduits)
            {
                if (line.length < 1 || line.length > start.mapSize) { throw new InvalidOperationException("Invalid starting conduit run."); }
                for (int offset = 0; offset < line.length; offset++)
                {
                    IntVec3 cell = line.start + new IntVec3(line.alongX ? offset : 0, 0, line.alongX ? 0 : offset);
                    if (!cell.InBounds(map)) { throw new InvalidOperationException("Starting conduit outside headquarters."); }
                    // Native generators/batteries can already transmit across this cell.
                    // A second conduit transmitter under them would duplicate the native grid registration.
                    bool exists = cell.GetThingList(map).Exists(t => t.def == ThingDefOf.PowerConduit ||
                        t.TryGetComp<CompPower>()?.Props.transmitsPower == true);
                    if (!exists)
                    {
                        Thing conduit = ThingMaker.MakeThing(ThingDefOf.PowerConduit);
                        conduit.SetFactionDirect(Faction.OfPlayer);
                        GenSpawn.Spawn(conduit, cell, map);
                    }
                }
            }
            // Resolve queued native connections only. Core ticks own power, fuel and battery simulation.
            map.powerNetManager.UpdatePowerNetsAndConnections_First();
            // Editable native scenario parts/possessions own supplies. Never replay start.stock here.
            if (!start.arrivalCell.Standable(map))
            { throw new InvalidOperationException("Headquarters arrival position is not walkable."); }
            MapGenerator.PlayerStartSpot = start.arrivalCell;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell);
            foreach (IntVec3 door in start.doors) { MapGenerator.rootsToUnfog.Add(door); }
        }
    }
}
