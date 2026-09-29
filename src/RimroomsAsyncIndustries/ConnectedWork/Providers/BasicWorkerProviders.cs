using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// The last two work-type gaps the coverage audit found: `BasicWorker` and `Fishing`.
    ///
    /// Both turned out to be **exactly** the shape of families that already exist, which is
    /// why they are together in one file and why neither needed a new idea. `BasicWorker` is
    /// designation-driven like the fieldwork four; `Fishing` is zone-driven like growing.
    /// Finding that out was the work; writing them was not.
    /// </summary>
    internal static class BasicWorkerScan
    {
        internal const int MaximumZonesPerMap = 12;

        internal static bool WorkActive(Pawn pawn, WorkTypeDef workType)
        {
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }
    }

    /// <summary>
    /// A worker crossing a gate to flick a switch, open a container, or eject fuel on the
    /// other side.
    ///
    /// **Designation-driven only, and every one of them genuinely is.** All three Core givers
    /// read nothing but their own designation off the map:
    ///
    /// <code>
    /// WorkGiver_Flick.ShouldSkip     -> !map.designationManager.AnySpawnedDesignationOfDef(Flick)
    /// WorkGiver_Open.ShouldSkip      -> !map.designationManager.AnySpawnedDesignationOfDef(Open)
    /// WorkGiver_EjectFuel.ShouldSkip -> !map.designationManager.AnySpawnedDesignationOfDef(EjectFuel)
    /// </code>
    ///
    /// so this family sits with the fieldwork ones where **nothing is inferred**: no
    /// designation, nobody goes. That also makes it the single most useful small thing in the
    /// work layer — flicking a switch on a far map is a real, ordinary thing a player asks for
    /// and could not previously get, and a power switch is exactly the sort of object a
    /// Backrooms facility is full of.
    ///
    /// `BasicWorker`'s other three givers are deliberately not here. `ExtractSkull` and
    /// `ChangeTreeMode` are Ideology ritual-adjacent content, and `BasicReleasePrisoner` is
    /// custody work the warden family already justifies a crossing for. Each would need its
    /// own review; none is claimed.
    ///
    /// The scan reuses `FieldworkScan`, which already owns the designation questions, rather
    /// than asking them a second way.
    /// </summary>
    public sealed class BasicWorkerProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId
        { get { return ConnectedDeploymentProviders.BasicWorker; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_BasicWorkerLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("BasicWorker"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return BasicWorkerScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return Marked(map, DesignationDefOf.Flick, pawn, work) ||
                Marked(map, DesignationDefOf.Open, pawn, work) ||
                Marked(map, DesignationDefOf.EjectFuel, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            Map map = pawn.Map;
            return FieldworkScan.AnyDesignation(map, DesignationDefOf.Flick) ||
                FieldworkScan.AnyDesignation(map, DesignationDefOf.Open) ||
                FieldworkScan.AnyDesignation(map, DesignationDefOf.EjectFuel);
        }

        /// <summary>
        /// A designated thing on that map this worker could reach through its observed area.
        /// `DesignationDefOf.Open` and `EjectFuel` may be null on an install that lacks them,
        /// which `FirstDesignatedThing` already tolerates.
        /// </summary>
        private static bool Marked(Map map, DesignationDef definition, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (definition == null) { return false; }
            Thing target = FieldworkScan.FirstDesignatedThing(map, definition, pawn, work);
            return target != null && !target.Destroyed && target.Spawned;
        }
    }

    /// <summary>
    /// A fisher crossing a gate to a fishing zone on the other side.
    ///
    /// ## The generation question, settled before the work question
    ///
    /// The coverage audit deferred this one on purpose: `Fishing` needs water, and whether a
    /// generated Backrooms coordinate ever *has* fishable water is a generation question, not
    /// a work question. If the answer were no, the honest record would have been "unnecessary"
    /// rather than "unbuilt".
    ///
    /// The answer is yes. `GenStep_BackroomsDestination` uses `WaterDeep` as its void floor,
    /// so a coordinate genuinely carries water terrain.
    ///
    /// ## But the deciding fact is that fishing is zone-driven
    ///
    /// Core's `WorkGiver_Fish` will not fish anywhere the **player** has not painted a
    /// `Zone_Fishing`:
    ///
    /// <code>
    /// if (allZone is Zone_Fishing { ShouldFishNow: not false, HasAnyFishableCells: not false })
    /// </code>
    ///
    /// which puts this family squarely with growing zones — nothing is inferred, and a
    /// coordinate full of void floor that the player never zoned attracts nobody. So the
    /// terrain question turns out not to be load-bearing at all: whether that water is a lake
    /// or an abyss, the player decides by painting or not painting, and `IsFishable` checks
    /// the water body type on that map either way.
    ///
    /// Both gates are facts about the zone and its own map. `ShouldFishNow` reads `Allowed`,
    /// `OverTargetPopulation`, `PausedDueToResourceCount` and `UnderTargetResourceCount`;
    /// `IsFishable` reads the cell's terrain and water body type. **Neither takes a pawn.**
    ///
    /// Left to arrival, because Core's own `NonScanJob` does all of it once the worker is
    /// standing there: choosing the zone, picking a fishable cell, finding a stand spot out of
    /// the water, the reservations, and the ideoligion check on slaughtering fish.
    ///
    /// Odyssey content, so `GetNamedSilentFail("Fishing")` returns null without it and the
    /// provider is unavailable — the same degradation childcare and dark study use.
    /// </summary>
    public sealed class FishingProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId
        { get { return ConnectedDeploymentProviders.Fishing; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_FishingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Fishing"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return BasicWorkerScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return AnyFishingZone(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            return AnyFishingZone(pawn.Map, pawn, null);
        }

        private static bool AnyFishingZone(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            List<Zone> zones = map.zoneManager == null ? null : map.zoneManager.AllZones;
            if (zones == null || zones.Count == 0) { return false; }
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(zones.Count, BasicWorkerScan.MaximumZonesPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < zones.Count; position++)
            {
                if (work != null && examined >= BasicWorkerScan.MaximumZonesPerMap) { break; }
                var fishing = zones[position] as Zone_Fishing;
                if (fishing == null) { continue; }
                // Only a real fishing zone counts against the window, so a map full of
                // stockpiles does not exhaust the budget before reaching one.
                examined++;
                if (fishing.Map != map) { continue; }
                if (!fishing.ShouldFishNow || !fishing.HasAnyFishableCells) { continue; }
                if (work == null) { return true; }
                List<IntVec3> cells = fishing.Cells;
                if (cells == null || cells.Count == 0) { continue; }
                // One representative cell for the observed-area question. The zone is a
                // contiguous painted region, so any of its cells answers "can this worker
                // see and reach that part of the map" as well as another.
                if (work.ObservedAreaAllows(pawn, map, cells[0])) { return true; }
            }
            return false;
        }
    }
}
