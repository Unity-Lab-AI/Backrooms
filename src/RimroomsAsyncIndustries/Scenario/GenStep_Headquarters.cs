using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// RR-FAC: the site is reserved and flattened before Core generates rock on it.
    ///
    /// **Order 100 is load-bearing.** Core's `ElevationFertility` runs at 10 and
    /// `RocksFromGrid` at 200, and `RocksFromGrid` spawns a rock formation in every cell whose
    /// elevation exceeds **0.7** -- plus natural rock roof above 0.728 and 0.798. Sitting at
    /// order 100, between the two, this step can lower the elevation under the facility so
    /// those rocks are **never generated in the first place**.
    ///
    /// That is the difference between a building on open ground and a building inside a
    /// 234-cell hole carved out of a mountain. The carve still happens -- see
    /// `HeadquartersBuilder.BurnIntoPlace` -- because rivers, ruins and other mods' gen steps
    /// can still put something here, but for rock it is prevention rather than demolition.
    ///
    /// This step used to sit at order 5, where it also set terrain across the footprint. Both
    /// were wrong: at order 5 it ran before `ElevationFertility` created the grid at all, and
    /// any terrain it wrote was overwritten by Core's `Terrain` step at order 210.
    /// </summary>
    public sealed class GenStep_HeadquartersTerrain : GenStep
    {
        /// <summary>
        /// The elevation written under the facility. Core's `GenStep_RocksFromGrid` uses
        /// **0.7** as its rock threshold, so anything comfortably below it yields open ground
        /// with no formation and no natural roof.
        /// </summary>
        private const float BuildableElevation = 0.55f;

        /// <summary>
        /// Cells of flattened ground kept outside the footprint. Rock roof generates from the
        /// same grid, so a formation flush against an outer wall would hang its roof over the
        /// building.
        /// </summary>
        private const int FlattenMargin = 2;

        public override int SeedPart { get { return 81940261; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            RimroomsStartDef start = HeadquartersBuilder.StartForMap(map);
            if (start == null) { return; }
            // The layout is authored in its own coordinates and offset onto whatever map the
            // player chose; see HeadquartersLayout.
            IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            foreach (IntVec3 cell in HeadquartersLayout.Site(start, offset, FlattenMargin).Cells)
            {
                if (!cell.InBounds(map)) { continue; }
                if (elevation[cell] > BuildableElevation) { elevation[cell] = BuildableElevation; }
            }
            MapGenerator.PlayerStartSpot = start.arrivalCell + offset;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell + offset);
            // Registered before Core's scatterers run: ScatterRuinsSimple and ScatterShrines
            // both read UsedRects at order 750 and will not place on top of the facility.
            foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))
            { MapGenerator.UsedRects.Add(rect); }
        }
    }

    public sealed class GenStep_HeadquartersFacility : GenStep
    {
        public override int SeedPart { get { return 81940262; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            RimroomsStartDef start = HeadquartersBuilder.StartForMap(map);
            if (start == null) { return; }
            HeadquartersSetupComponent receipt = map.GetComponent<HeadquartersSetupComponent>();
            if (receipt == null || receipt.setupStarted) { return; }
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
                // **Hand the start spot back to Core rather than re-throwing.**
                //
                // Re-throwing only reached `MapGenerator.GenerateContentsIntoMap`, which logs
                // and carries on, so it bought nothing -- and it left the player standing on an
                // arrival cell inside a building that does not exist. Core's
                // `GenStep_FindPlayerStartSpot` runs at order 850, after this step, and only
                // picks a spot when none is valid. Clearing it lets Core choose a real one.
                MapGenerator.PlayerStartSpot = IntVec3.Invalid;
            }
        }
    }

    internal static class HeadquartersBuilder
    {
        /// <summary>
        /// The start this map belongs to, or **null** when this map is not the initial company
        /// start.
        ///
        /// **Null rather than a throw, and that is the load-bearing detail of 0.12.46-dev.**
        /// These gen steps now live in Core's `Base_Player`, which runs for **every** player map
        /// a game ever generates -- a second settlement, a quest site, a reloaded world. A step
        /// that threw there would break all of them. It used to throw because it only ever ran
        /// inside a generator this mod owned and nothing else could reach it.
        /// </summary>
        internal static RimroomsStartDef StartForMap(Map map)
        {
            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;
            if (part == null || part.startDef == null || Find.GameInitData == null) { return null; }
            if (map.Tile != Find.GameInitData.startingTile) { return null; }
            if (Current.Game.GetComponent<RimroomsCampaignComponent>().HasBranch) { return null; }
            // The map does not have to BE the authored size -- it has to be able to hold the
            // layout. The player picks the size at world setup and the tile they arrive on.
            if (!HeadquartersLayout.Fits(part.startDef, map.Size)) { return null; }
            return part.startDef;
        }

        /// <summary>
        /// Clear the ground the facility needs before a single wall is placed.
        ///
        /// ## Why this exists
        ///
        /// Owner direction, 2026-09-30, verbatim: *"i think the issue was there was shit where it
        /// planned on putting the store and pawns so it errored it needs a like a burn into place
        /// functiions to carve everyhting out and cut everything down and fill in with soil where
        /// water is unmder where the store needs to propigate before game start"*.
        ///
        /// Until 0.12.47-dev `Build` **refused** a footprint it did not own: it threw
        /// `Headquarters wall intersects generated structure` at the first occupied cell. That
        /// was survivable while a generator of ours handed it flat, empty Soil. Once Core
        /// generated the map, the Store's 1020-cell footprint on the owner's 300x300 map held
        /// **164 Marble and 70 Granite formations, 177 cells of natural rock roof, roughly 440
        /// plant cells, 34 cells of rubble and chunks, and two monkeys** -- measured cell by cell
        /// in the live game. It threw on its very first cell.
        ///
        /// Refusing was the wrong instinct in the first place. Every vanilla structure gen step
        /// -- ruins, shrines, ancient complexes -- clears what is under it. This does the same
        /// thing, in one pass, before anything is placed, so a site that cannot be prepared
        /// fails before the map has a half-built building on it.
        ///
        /// ## What it deliberately does not touch
        ///
        /// **Pawns.** Nothing here destroys a living thing; Core spawns animals at order 1200,
        /// after this, and they walk in from the edges. And a `Building` that belongs to a
        /// faction is destroyed but **named in a warning first** -- that would mean another
        /// mod's gen step placed a structure inside the footprint despite the `UsedRects`
        /// reservation, and it should be visible rather than silent.
        /// </summary>
        internal static void BurnIntoPlace(RimroomsStartDef start, Map map, IntVec3 offset)
        {
            foreach (IntVec3 cell in HeadquartersLayout.Site(start, offset, 0).Cells)
            {
                if (!cell.InBounds(map)) { continue; }
                // Carve everything out and cut everything down. Copied first: destroying a
                // thing mutates the cell's own thing list.
                List<Thing> present = new List<Thing>(cell.GetThingList(map));
                foreach (Thing thing in present)
                {
                    if (thing.def.category == ThingCategory.Pawn || !thing.def.destroyable) { continue; }
                    if (thing.def.category == ThingCategory.Building && thing.Faction != null)
                    {
                        Log.Warning("[Rimrooms][Scenario] Clearing a faction structure inside the reserved company footprint at "
                            + cell + ": " + thing.def.defName + " (" + thing.Faction.GetUniqueLoadID() + ")");
                    }
                    thing.Destroy(DestroyMode.Vanish);
                }
                // Natural rock roof outlives the formation under it, and an unsupported one
                // leaves the facility in permanent darkness.
                RoofDef roof = map.roofGrid.RoofAt(cell);
                if (roof != null && roof.isNatural) { map.roofGrid.SetRoof(cell, null); }
                // Fill in with soil where water is. Impassable terrain is included: a wall on
                // it would be unreachable from inside.
                TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
                if (terrain.IsWater || terrain.passability == Traversability.Impassable)
                { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }
            }
        }

        internal static void Build(RimroomsStartDef start, Map map, HeadquartersSetupComponent receipt)
        {
            IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);
            if (!(start.arrivalCell + offset).InBounds(map) || !(start.stockCell + offset).InBounds(map))
            { throw new InvalidOperationException("Headquarters arrival or receiving position is outside the map."); }
            // Before a single wall: the whole site, in one pass.
            BurnIntoPlace(start, map, offset);
            foreach (RimroomsRoomPlan room in start.rooms)
            {
                CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));
                if (room.width < 3 || room.height < 3 || !rect.Min.InBounds(map) || !rect.Max.InBounds(map))
                { throw new InvalidOperationException("Invalid headquarters room rectangle."); }
                foreach (IntVec3 cell in rect.Cells)
                {
                    bool edge = cell.x == rect.minX || cell.x == rect.maxX || cell.z == rect.minZ || cell.z == rect.maxZ;
                    if (room.floor) { map.terrainGrid.SetTerrain(cell, start.floorTerrain); }
                    if (edge)
                    {
                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);
                        wall.SetFactionDirect(Faction.OfPlayer);
                        GenSpawn.Spawn(wall, cell, map);
                    }
                    else if (room.roofed) { map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed); }
                    map.areaManager.Home[cell] = true;
                }
            }
            // **THE COLUMNS, before anything is glazed or opened.** A roof is supported only
            // within 6.9 cells of a wall, and the gate hall is twenty cells across: without
            // these its middle is unsupported, and an unsupported roof collapses on whoever is
            // standing under it the first time somebody deconstructs the wall holding it up.
            foreach (IntVec3 authored in start.pillars)
            {
                IntVec3 cell = authored + offset;
                if (!cell.InBounds(map) || cell.GetEdifice(map) != null)
                { throw new InvalidOperationException("Headquarters column has no free cell at " + cell); }
                Thing column = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);
                column.SetFactionDirect(Faction.OfPlayer);
                GenSpawn.Spawn(column, cell, map);
            }
            // **THE VIEWING WALLS, before the doors.** Owner: *"ballistic glass  walls for
            // viewing the machine remotely and safely"*. Done after the rooms, so the run is
            // replacing a wall this generator placed itself, and before the doors so a door cell
            // is never glazed over -- the door loop below still demands an ordinary wall, which
            // is the check that catches an authored overlap between the two lists.
            foreach (RimroomsWallRunPlan run in start.glazing)
            {
                ThingDef glass = ResolveFirstLoaded(run.thingDefNames);
                ThingDef pane = glass == null || !glass.MadeFromStuff
                    ? null : ResolveFirstLoaded(run.stuffDefNames) ?? start.wallStuff;
                for (int step = 0; step < run.length; step++)
                {
                    IntVec3 cell = run.CellAt(step) + offset;
                    Building wall = cell.InBounds(map) ? cell.GetEdifice(map) : null;
                    if (wall == null || wall.def != ThingDefOf.Wall)
                    { throw new InvalidOperationException("Headquarters glazing has no generated wall at " + cell); }
                    // Nothing to swap to. An ordinary wall is left standing: a solid viewing wall
                    // is a cosmetic loss and a missing wall is a hole in a sealed gate hall.
                    if (glass == null) { continue; }
                    wall.Destroy(DestroyMode.Vanish);
                    Thing glazed = ThingMaker.MakeThing(glass, pane);
                    glazed.SetFactionDirect(Faction.OfPlayer);
                    GenSpawn.Spawn(glazed, cell, map);
                }
            }
            foreach (IntVec3 authored in start.doors)
            {
                IntVec3 cell = authored + offset;
                Building wall = cell.GetEdifice(map);
                if (wall == null || wall.def != ThingDefOf.Wall) { throw new InvalidOperationException("Headquarters door has no generated wall at " + cell); }
                wall.Destroy(DestroyMode.Vanish);
                // An airlock's doors are automatic; every other door is ordinary. Autodoor is
                // Core, so this is not an optional resolution -- a start that named one and did
                // not get it would be a package fault, not a profile difference.
                // `ThingDefOf.Autodoor` does not exist; Core's named-def set has `Door` and not
                // the automatic one. Looked up by name, and an ordinary door stands in rather
                // than failing a start over a door's kind.
                ThingDef doorDef = ThingDefOf.Door;
                if (start.autodoors.Contains(authored))
                { doorDef = DefDatabase<ThingDef>.GetNamedSilentFail("Autodoor") ?? ThingDefOf.Door; }
                Thing door = ThingMaker.MakeThing(doorDef, ThingDefOf.Steel);
                door.SetFactionDirect(Faction.OfPlayer);
                GenSpawn.Spawn(door, cell, map);
            }
            int index = 0;
            foreach (RimroomsBuildingPlan plan in start.buildings)
            {
                if (plan.thing == null) { throw new InvalidOperationException("Unresolved headquarters building definition."); }
                Rot4 rotation = new Rot4(plan.rotation);
                IntVec3 where = plan.cell + offset;
                foreach (IntVec3 cell in GenAdj.OccupiedRect(where, rotation, plan.thing.size).Cells)
                {
                    // The burn cleared natural cover, so an edifice here is one of OUR OWN walls
                    // -- an authored furniture cell overlapping an authored wall. That is a def
                    // error, not a map-generation collision, and it must still be refused.
                    if (!cell.InBounds(map) || cell.GetEdifice(map) != null)
                    { throw new InvalidOperationException("Headquarters furniture intersects a wall/building at " + cell); }
                }
                Thing building = ThingMaker.MakeThing(plan.thing, plan.stuff);
                building.SetFactionDirect(Faction.OfPlayer);
                building.TryGetComp<CompQuality>()?.SetQuality(QualityCategory.Normal, ArtGenerationContext.Outsider);
                GenSpawn.Spawn(building, where, map, rotation);
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
                for (int step = 0; step < line.length; step++)
                {
                    IntVec3 cell = line.start + offset
                        + new IntVec3(line.alongX ? step : 0, 0, line.alongX ? 0 : step);
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
            //
            // **Guarded, for the reason the destination generator was.** Core throws out of this
            // when its transmitter bookkeeping is inconsistent, and a throw here is inside a
            // GenStep: it would stop the headquarters being built and cost the player the start.
            // A facility with an unresolved power net is a facility that resolves it on the next
            // tick; a facility that does not exist is a dead game.
            try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms][Start] The headquarters power net could not be resolved at "
                    + "generation. The facility is built and Core will resolve it on the next "
                    + "tick. " + error);
            }
            // Editable native scenario parts/possessions own supplies. Never replay start.stock here.
            if (!(start.arrivalCell + offset).Standable(map))
            { throw new InvalidOperationException("Headquarters arrival position is not walkable."); }
            MapGenerator.PlayerStartSpot = start.arrivalCell + offset;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell + offset);
            foreach (IntVec3 door in start.doors) { MapGenerator.rootsToUnfog.Add(door + offset); }
        }

        /// <summary>
        /// The first named def the game has actually loaded, or null.
        ///
        /// This is how an Optional mod's content is used without depending on it. A `ThingDef`
        /// field in the def would be a cross-reference, and an unresolved cross-reference
        /// discards the whole containing def -- which took `Door` and `Autodoor` out of the game
        /// once and produced 587 errors before the main menu.
        /// </summary>
        private static ThingDef ResolveFirstLoaded(List<string> names)
        {
            if (names == null) { return null; }
            for (int index = 0; index < names.Count; index++)
            {
                if (string.IsNullOrWhiteSpace(names[index])) { continue; }
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(names[index]);
                if (def != null) { return def; }
            }
            return null;
        }
    }
}
