using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// An artist crossing a gate to paint, or to strip paint, on the other side.
    ///
    /// ## The other half of the row the eleven container givers came from
    ///
    /// The coverage row's own words on why it could not close were three things, not one:
    /// the eleven DLC container givers, *"the **four painting givers** in `Art`"*, and any
    /// wholly mod-added work type. The four were the quietest of the three and the easiest
    /// to lose, because `Art` already has a family — `BillWorkArt`, which crosses for
    /// sculpting — and a work type that is already covered reads as finished.
    ///
    /// It was not. `WorkGiver_DoBill` and the painting givers share nothing: a bill lives on
    /// a bench and is chosen from a bill stack, and paint lives on a **designation** and is
    /// chosen by the player pointing at a floor or a wall. `BillWorkArt` asks
    /// `BillWorkProvider` whether any bench on that map has a deliverable bill, which is
    /// false on a map with fifty painted-blue designations and no sculpting bench. So a
    /// colonist would never cross for any of it.
    ///
    /// ## All four are designation-driven, and that settles the shape
    ///
    /// Every one begins the same way, and the four `ShouldSkip` bodies are the whole
    /// argument for putting this family beside `BasicWorkerProvider` rather than inventing
    /// anything:
    ///
    /// <code>
    /// WorkGiver_PaintFloor.ShouldSkip           -> !map.designationManager.AnySpawnedDesignationOfDef(PaintFloor)
    /// WorkGiver_PaintBuilding.ShouldSkip        -> !map.designationManager.AnySpawnedDesignationOfDef(PaintBuilding)
    /// WorkGiver_RemovePaintFloor.ShouldSkip     -> !map.designationManager.AnySpawnedDesignationOfDef(RemovePaintFloor)
    /// WorkGiver_RemovePaintBuilding.ShouldSkip  -> !map.designationManager.AnySpawnedDesignationOfDef(RemovePaintBuilding)
    /// </code>
    ///
    /// So **nothing is inferred**: no designation, nobody crosses. That is the property the
    /// fieldwork families are built on and it is the reason this one is safe — a Backrooms
    /// coordinate full of stained yellow wall attracts nobody until the player says so.
    /// The scan reuses <see cref="FieldworkScan"/>, which already owns the designation
    /// questions, rather than asking them a second way.
    ///
    /// ## The two conditions worth reading out of Core rather than guessing
    ///
    /// **Paint needs dye, and stripping paint does not.** `ShouldPaintCell` and
    /// `ShouldPaintThing` both end in a `checkDye` branch over
    /// `map.listerThings.ThingsOfDef(ThingDefOf.Dye)` and refuse with `NoIngredient` when
    /// none is reachable; neither remove-paint giver mentions dye at all. Sending an artist
    /// across a gate to a wall it cannot paint because the dye is at home is a wasted
    /// crossing that Core would refuse on arrival, so the candidate half asks for dye
    /// **presence** on that map — necessary, not sufficient, because `CanReserveAndReach` is
    /// not ours to ask remotely.
    ///
    /// **A colour already applied is not work.** Core compares the designation's own
    /// `colorDef` against what is there: `map.terrainGrid.ColorAt(cell)` for a floor and
    /// `Building.PaintColorDef` for a building. Both are facts about the map asked about, so
    /// both are asked here rather than deferred, and a stale designation over an
    /// already-blue wall cannot pull anybody through a gate.
    ///
    /// The conflicting-designation refusals are Core's too, and they are read from **the
    /// target's** designation manager rather than the worker's, because here those are
    /// different maps: a cell marked both `PaintFloor` and `RemovePaintFloor`, or a floor
    /// also marked `RemoveFloor`, or a building also marked `Deconstruct`, is no work.
    ///
    /// What is left to arrival is everything pawn-specific, and Core does all of it:
    /// `pawn.CanReserve` against `ReservationLayerDefOf.Floor`, the dye reach, the radial
    /// job-queue build-out, and `RemovePaintFloor`'s under-terrain affordance test.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py use RR-UI` and `family interface` carry the rows that bear on
    /// colour and style, and none of them creates a seam here. **Floors, walls and paint are
    /// terrain and building state**; this provider reads Core's own grids and Core's own
    /// designations and writes nothing, so a mod that adds paintable content is covered by
    /// `terrain.isPaintable` and `def.building.paintable` without being named, and a mod
    /// that adds colours is covered because the colour compared is whatever the designation
    /// carries. There is no list of paints here to fall out of date.
    ///
    /// The one row worth stating a position on is the standing wall rule: this mod's own
    /// yellow-room look is generated terrain and stuff, not paint, so a player painting a
    /// coordinate's floors changes their colony's appearance and nothing about generation.
    /// Nothing is patched and every mod may be absent.
    /// </summary>
    public sealed class PaintingProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId
        { get { return ConnectedDeploymentProviders.Painting; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_PaintingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Art"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return FieldworkScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn))
            { return false; }
            return AnyStrippableFloor(map, pawn, work) ||
                AnyStrippableBuilding(map, pawn, work) ||
                AnyPaintableFloor(map, pawn, work) ||
                AnyPaintableBuilding(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            Map map = pawn.Map;
            // The definitive half is the same four questions, unwindowed: releasing a
            // deployment with a wall still marked would plan the worker straight back.
            return AnyStrippableFloor(map, pawn, null) ||
                AnyStrippableBuilding(map, pawn, null) ||
                AnyPaintableFloor(map, pawn, null) ||
                AnyPaintableBuilding(map, pawn, null);
        }

        // ------------------------------------------------------------ stripping paint -- //

        /// <summary>
        /// `RemovePaintFloor`. No dye needed — Core's giver never mentions it. The
        /// under-terrain affordance test is left to arrival because it is cheap there and
        /// only ever narrows the answer.
        /// </summary>
        private static bool AnyStrippableFloor(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            return AnyMarkedCell(map, pawn, work, DesignationDefOf.RemovePaintFloor,
                delegate(IntVec3 cell)
            {
                TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
                if (terrain == null || !terrain.isPaintable) { return false; }
                return NoConflict(map, cell, DesignationDefOf.PaintFloor,
                    DesignationDefOf.RemoveFloor);
            });
        }

        /// <summary>`RemovePaintBuilding`. Paintable, marked, not being deconstructed, not on fire.</summary>
        private static bool AnyStrippableBuilding(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            return AnyMarkedThing(map, pawn, work, DesignationDefOf.RemovePaintBuilding,
                delegate(Thing target, Designation designation)
            {
                if (!Paintable(target)) { return false; }
                if (target.IsBurning()) { return false; }
                return NoConflictOn(map, target, DesignationDefOf.Deconstruct,
                    DesignationDefOf.PaintBuilding);
            });
        }

        // ------------------------------------------------------------ applying paint -- //

        /// <summary>
        /// `PaintFloor`. A marked, paintable cell whose colour is not already the one asked
        /// for, with no conflicting designation, and dye on that map.
        /// </summary>
        private static bool AnyPaintableFloor(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (!DyePresent(map, pawn, work)) { return false; }
            return AnyMarkedCellColoured(map, pawn, work, DesignationDefOf.PaintFloor,
                delegate(IntVec3 cell, ColorDef wanted)
            {
                TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
                if (terrain == null || !terrain.isPaintable) { return false; }
                if (map.terrainGrid.ColorAt(cell) == wanted) { return false; }
                return NoConflict(map, cell, DesignationDefOf.RemoveFloor,
                    DesignationDefOf.RemovePaintFloor);
            });
        }

        /// <summary>
        /// `PaintBuilding`. As above, against `Building.PaintColorDef` instead of the
        /// terrain colour grid.
        /// </summary>
        private static bool AnyPaintableBuilding(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (!DyePresent(map, pawn, work)) { return false; }
            return AnyMarkedThing(map, pawn, work, DesignationDefOf.PaintBuilding,
                delegate(Thing target, Designation designation)
            {
                if (!Paintable(target) || designation.colorDef == null) { return false; }
                var building = target as Building;
                if (building != null && building.PaintColorDef == designation.colorDef)
                { return false; }
                if (target.IsBurning()) { return false; }
                return NoConflictOn(map, target, DesignationDefOf.Deconstruct,
                    DesignationDefOf.RemovePaintBuilding);
            });
        }

        // ------------------------------------------------------------------ shared -- //

        /// <summary>
        /// Dye on that map, unforbidden and unhidden. The presence substitute for Core's
        /// `CanReserveAndReach` sweep over `ThingsOfDef(Dye)`, which is pawn-specific. A
        /// remove-paint route never asks this, because Core never does.
        /// </summary>
        private static bool DyePresent(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            ThingDef dye = ThingDefOf.Dye;
            if (dye == null || map.listerThings == null) { return false; }
            List<Thing> stacks = map.listerThings.ThingsOfDef(dye);
            int budget = FieldworkScan.MaximumCandidates;
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(stacks.Count, budget, pawn);
            int examined = 0;
            for (int position = windowStart; position < stacks.Count; position++)
            {
                if (work != null && examined >= budget) { break; }
                examined++;
                Thing stack = stacks[position];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != map)
                { continue; }
                if (stack.IsForbidden(Faction.OfPlayer)) { continue; }
                if (stack.Position.Fogged(map)) { continue; }
                if (work == null && !pawn.CanReserve(stack)) { continue; }
                return true;
            }
            return false;
        }

        private static bool Paintable(Thing target)
        {
            return target != null && target.def != null && target.def.building != null &&
                target.def.building.paintable;
        }

        /// <summary>
        /// Neither conflicting designation stands on this cell. Read from the target map's
        /// own manager: Core reads `pawn.Map.designationManager` because in Core they are
        /// the same map, and here they are not.
        /// </summary>
        private static bool NoConflict(Map map, IntVec3 cell, DesignationDef first,
            DesignationDef second)
        {
            if (map.designationManager == null) { return true; }
            if (first != null && map.designationManager.DesignationAt(cell, first) != null)
            { return false; }
            return second == null || map.designationManager.DesignationAt(cell, second) == null;
        }

        private static bool NoConflictOn(Map map, Thing target, DesignationDef first,
            DesignationDef second)
        {
            if (map.designationManager == null) { return true; }
            if (first != null && map.designationManager.DesignationOn(target, first) != null)
            { return false; }
            return second == null || map.designationManager.DesignationOn(target, second) == null;
        }

        // ------------------------------------------------------------ the two walks -- //

        private delegate bool CellRule(IntVec3 cell);

        private delegate bool ColouredCellRule(IntVec3 cell, ColorDef wanted);

        private delegate bool ThingRule(Thing target, Designation designation);

        /// <summary>
        /// Walk that def's designated cells on that map, bounded, skipping fogged cells and
        /// anything outside this worker's observed allowed area there.
        /// </summary>
        private static bool AnyMarkedCell(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work, DesignationDef definition, CellRule rule)
        {
            return AnyMarkedCellColoured(map, pawn, work, definition,
                delegate(IntVec3 cell, ColorDef wanted) { return rule(cell); });
        }

        private static bool AnyMarkedCellColoured(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work, DesignationDef definition,
            ColouredCellRule rule)
        {
            if (definition == null || map.designationManager == null || map.terrainGrid == null)
            { return false; }
            int windowStart = work == null ? 0
                : FieldworkScan.DesignationWindowStart(map, definition, pawn);
            int position = 0;
            int examined = 0;
            foreach (Designation designation in
                map.designationManager.SpawnedDesignationsOfDef(definition))
            {
                if (position++ < windowStart) { continue; }
                if (work != null && examined >= FieldworkScan.MaximumCandidates) { break; }
                examined++;
                IntVec3 cell = designation.target.Cell;
                if (!cell.IsValid || !cell.InBounds(map) || cell.Fogged(map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                if (!rule(cell, designation.colorDef)) { continue; }
                if (work == null &&
                    !pawn.CanReserve(cell, 1, -1, ReservationLayerDefOf.Floor))
                { continue; }
                return true;
            }
            return false;
        }

        private static bool AnyMarkedThing(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work, DesignationDef definition, ThingRule rule)
        {
            if (definition == null || map.designationManager == null) { return false; }
            int windowStart = work == null ? 0
                : FieldworkScan.DesignationWindowStart(map, definition, pawn);
            int position = 0;
            int examined = 0;
            foreach (Designation designation in
                map.designationManager.SpawnedDesignationsOfDef(definition))
            {
                if (position++ < windowStart) { continue; }
                if (work != null && examined >= FieldworkScan.MaximumCandidates) { break; }
                examined++;
                Thing target = designation.target.Thing;
                if (target == null || target.Destroyed || !target.Spawned || target.Map != map)
                { continue; }
                if (target.Position.Fogged(map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, target.Position))
                { continue; }
                if (!rule(target, designation)) { continue; }
                if (work == null && !pawn.CanReserve(target)) { continue; }
                return true;
            }
            return false;
        }
    }
}
