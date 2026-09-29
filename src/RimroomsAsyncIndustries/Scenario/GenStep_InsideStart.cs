using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// The solo/group start: the map itself is a Backrooms coordinate.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"remember the other one is solo/group start..
    /// group have been known to end up together inside so leets use the in backrooms start to be
    /// 1-5 pawns player settable with normal set up or edb prepare carefully mod and or character
    /// editor"*.
    ///
    /// ## No Harmony, and no trick
    ///
    /// Core picks the starting map's generator as
    /// <c>initData.mapGeneratorDef ?? settlement.MapGeneratorDef</c>, and
    /// <see cref="ScenPart_RimroomsStart.PreMapGenerate"/> has always assigned
    /// <c>Find.GameInitData.mapGeneratorDef</c> from the start def. A start that wants to open
    /// inside the Backrooms simply names a different generator, and Core does the rest. The map
    /// size comes from the same place, so the coordinate fills the map **to every edge** rather
    /// than sitting as an island in open ground.
    ///
    /// ## What it does not do, deliberately
    ///
    /// **No power, and no lights.** The destination generator wires a chemfuel generator and
    /// conduits because a branch arrives at a coordinate with a gate behind it and a reason to
    /// light the place. Nobody wired this one. The survivors have whatever light they carried in,
    /// which is what `docs/SCENARIOS.md` gives them in the kit, and the dark is the point.
    ///
    /// **No gate anchor and no return cell.** Those exist at a destination because something
    /// opened onto it. Nothing opened onto this. There is no way home and finding one is the
    /// whole opening.
    ///
    /// **The coordinate is not registered in the branch atlas.** It is the map the colony lives
    /// on, saved whole like any colony map, so a reload cannot silently produce a different
    /// place. Turning where you were trapped into a coordinate you can dial back to is a
    /// convergence feature and belongs with the escape route, not with the opening.
    /// </summary>
    public sealed class GenStep_InsideStart : GenStep
    {
        public override int SeedPart { get { return 81940263; } }

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
                    out staff, out roles, out refusal))
                { throw new InvalidOperationException(refusal); }
                receipt.staff = staff;
                receipt.staffRoles = roles;
                receipt.acceptedSupplies =
                    new List<string>(Current.Game.GetComponent<RimroomsStartupComponent>().SupplySummary);
                BuildInside(start, map);
                receipt.setupComplete = true;
            }
            catch (Exception exception)
            {
                receipt.failure = "RR_Start_PhysicalSetupFailed";
                Log.Error("[Rimrooms][Scenario] Inside start setup stopped; existing placements are retained: "
                    + exception);
                throw;
            }
        }

        private static void BuildInside(RimroomsStartDef start, Map map)
        {
            if (map.Size.x != DestinationService.MapWidth || map.Size.z != DestinationService.MapHeight)
            { throw new InvalidOperationException("An inside start must use the coordinate map size."); }

            // A layout plan, not a saved record. The colony map is saved whole, so nothing here
            // has to survive a reload; what has to be true is that the rooms are a legal
            // coordinate graph, which is the same check every destination passes.
            CoordinateRecord plan = new CoordinateRecord
            {
                id = start.scenarioId + ":origin",
                label = start.label,
                seed = Math.Abs(Gen.HashCombineInt(Find.World.info.Seed, SeedSalt)),
                generatorVersion = 1,
                depth = Math.Max(1, start.insideStartDepth),
            };
            string failure;
            if (!DestinationService.EnsureRoomGraph(plan, out failure))
            { throw new InvalidOperationException("Inside start room graph refused: " + failure); }

            TerrainDef concrete = DefDatabase<TerrainDef>.GetNamedSilentFail("Concrete");
            TerrainDef voidFloor = DefDatabase<TerrainDef>.GetNamedSilentFail("WaterDeep");
            ThingDef wallStuff = BackroomsPalette.For(plan.Depth, plan.Seed).wallStuff ?? ThingDefOf.Steel;
            if (concrete == null || voidFloor == null || ThingDefOf.Wall == null)
            { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }

            // The same shell a destination gets: rock to every edge, thick roof over every cell,
            // rooms carved out of it. Invariant 13 lives in there and must not be re-implemented.
            GenStep_BackroomsDestination.BuildShell(map, plan, concrete, voidFloor,
                ThingDefOf.Wall, wallStuff);

            IntVec3 startSpot = FindStandingCell(map, plan);
            if (!startSpot.IsValid)
            { throw new InvalidOperationException("Inside start found nowhere for anybody to stand."); }
            MapGenerator.PlayerStartSpot = startSpot;
            MapGenerator.rootsToUnfog.Add(startSpot);
        }

        private const int SeedSalt = 51438907;

        /// <summary>
        /// Somewhere inside a room that a person can actually be put down.
        ///
        /// Rooms are searched in index order and cells in order within them, so the answer is the
        /// same every time for a given layout rather than following whatever order a collection
        /// happened to enumerate in. Invariant 26, applied to a search instead of a roll.
        /// </summary>
        private static IntVec3 FindStandingCell(Map map, CoordinateRecord plan)
        {
            List<RoomRecord> rooms = new List<RoomRecord>(plan.Rooms);
            rooms.Sort((left, right) => left.Index.CompareTo(right.Index));
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null) { continue; }
                foreach (IntVec3 cell in room.Bounds.ContractedBy(1).Cells)
                {
                    if (!cell.InBounds(map) || !cell.Standable(map)) { continue; }
                    if (cell.GetEdifice(map) != null) { continue; }
                    return cell;
                }
            }
            return IntVec3.Invalid;
        }
    }
}
