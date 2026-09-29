using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// The fieldwork families — mining, hunting, plant cutting and growing-zone work — kept
    /// together because they answer their candidate question the same way: **the player has
    /// already said, on that map, that this work is wanted.**
    ///
    /// Mining, hunting and plant cutting are driven by *designations*, and growing-zone work by
    /// a *zone*. Both are recorded on the map itself, through `map.designationManager` and
    /// `map.zoneManager`, which are public and map-explicit. So "is there work of this kind
    /// over there" is answerable exactly and without guessing — it is a question about what the
    /// player marked, not about what a pawn could reach.
    ///
    /// That makes these the safest families in the whole layer: nothing is ever inferred. If
    /// the player never designated anything on a Backrooms coordinate, nobody crosses a gate to
    /// mine, hunt or cut anything there.
    ///
    /// **One simplification worth naming.** A deployment provider answers *one question*, not
    /// one question per Core work giver. Sowing and harvesting are two Core givers, but the
    /// question "is there growing-zone work on that map" is one question, and on arrival Core's
    /// own two givers pick whichever applies. So they share a provider rather than duplicating
    /// one. The same holds for cutting and harvesting by designation.
    /// </summary>
    internal static class FieldworkScan
    {
        internal const int MaximumCandidates = 24;

        /// <summary>
        /// Whether that map carries any live designation of this def. Map-explicit: Core's own
        /// givers ask exactly this of their own map in `ShouldSkip`.
        /// </summary>
        internal static bool AnyDesignation(Map map, DesignationDef definition)
        {
            return map != null && definition != null && map.designationManager != null &&
                map.designationManager.AnySpawnedDesignationOfDef(definition);
        }

        /// <summary>
        /// The first designated target of this def on that map that is not fogged and is inside
        /// this worker's observed allowed area there, or null.
        /// </summary>
        internal static Thing FirstDesignatedThing(Map map, DesignationDef definition, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (map == null || definition == null || map.designationManager == null) { return null; }
            int examined = 0;
            foreach (Designation designation in map.designationManager.SpawnedDesignationsOfDef(definition))
            {
                if (examined >= MaximumCandidates) { break; }
                examined++;
                Thing target = designation.target.Thing;
                if (target == null || target.Destroyed || !target.Spawned || target.Map != map)
                { continue; }
                if (target.Position.Fogged(map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, target.Position)) { continue; }
                return target;
            }
            return null;
        }

        /// <summary>
        /// Whether that map carries any designated *cell* of this def — mining marks cells, not
        /// only things. Bounded, and fogged cells are skipped.
        /// </summary>
        internal static bool AnyDesignatedCell(Map map, DesignationDef definition, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (map == null || definition == null || map.designationManager == null) { return false; }
            int examined = 0;
            foreach (Designation designation in map.designationManager.SpawnedDesignationsOfDef(definition))
            {
                if (examined >= MaximumCandidates) { break; }
                examined++;
                IntVec3 cell = designation.target.Cell;
                if (!cell.IsValid || !cell.InBounds(map)) { continue; }
                if (cell.Fogged(map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                return true;
            }
            return false;
        }

        internal static bool WorkActive(Pawn pawn, WorkTypeDef workType)
        {
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }
    }

    /// <summary>
    /// A miner crossing a gate to work designated rock over there. Mining marks **cells**, so
    /// the candidate question is about designated cells rather than things.
    ///
    /// Core's own `WorkGiver_Miner.ShouldSkip` asks precisely this of its own map, and its
    /// `PotentialWorkThingsGlobal` goes through `MineAIUtility.PotentialMineables(pawn)` — which
    /// takes the pawn and so is arrival-only. The definitive decision stays entirely Core's.
    /// </summary>
    public sealed class MiningProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.Mining; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_MiningLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Mining"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return FieldworkScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return FieldworkScan.AnyDesignatedCell(map, DesignationDefOf.Mine, pawn, work) ||
                FieldworkScan.AnyDesignatedCell(map, DesignationDefOf.MineVein, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            // Core's own skip test, on the map the worker is standing on.
            return FieldworkScan.AnyDesignation(pawn.Map, DesignationDefOf.Mine) ||
                FieldworkScan.AnyDesignation(pawn.Map, DesignationDefOf.MineVein);
        }
    }

    /// <summary>
    /// A hunter crossing a gate to take a designated animal over there.
    ///
    /// The two weapon tests are Core's own `public static` helpers on `WorkGiver_HunterHunt`,
    /// and both read only the pawn's equipment and apparel, so they are map-free and are asked
    /// in <see cref="WorkerEligible"/> rather than reimplemented. A hunter with the wrong
    /// weapon is never sent anywhere.
    /// </summary>
    public sealed class HuntingProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.Hunting; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_HuntingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Hunting"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            if (!FieldworkScan.WorkActive(pawn, WorkType)) { return false; }
            if (pawn.equipment == null) { return false; }
            // Core's own gates, map-free and public.
            if (!WorkGiver_HunterHunt.HasHuntingWeapon(pawn)) { return false; }
            return !WorkGiver_HunterHunt.HasShieldAndRangedWeapon(pawn);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            Thing quarry = FieldworkScan.FirstDesignatedThing(map, DesignationDefOf.Hunt, pawn, work);
            // Core requires an animal or wild man; a designation on anything else is not our work.
            var animal = quarry as Pawn;
            return animal != null && animal.AnimalOrWildMan() && !animal.Dead;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            return FieldworkScan.AnyDesignation(pawn.Map, DesignationDefOf.Hunt);
        }
    }

    /// <summary>
    /// Someone crossing a gate to cut or harvest plants the player designated over there.
    ///
    /// Cutting and harvesting are two Core designations and two Core givers, but one question:
    /// has the player marked plants on that map. On arrival Core's own givers pick whichever
    /// applies, so they share a provider instead of duplicating one.
    /// </summary>
    public sealed class PlantCuttingProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.PlantCutting; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_PlantCuttingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("PlantCutting"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return FieldworkScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return Designated(map, DesignationDefOf.CutPlant, pawn, work) ||
                Designated(map, DesignationDefOf.HarvestPlant, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            return FieldworkScan.AnyDesignation(pawn.Map, DesignationDefOf.CutPlant) ||
                FieldworkScan.AnyDesignation(pawn.Map, DesignationDefOf.HarvestPlant);
        }

        private static bool Designated(Map map, DesignationDef definition, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            Thing target = FieldworkScan.FirstDesignatedThing(map, definition, pawn, work);
            var plant = target as Plant;
            return plant != null && !plant.Destroyed;
        }
    }

    /// <summary>
    /// A grower crossing a gate to work a growing zone over there.
    ///
    /// Sowing and harvesting are two Core givers; "is there growing-zone work on that map" is
    /// one question, so this is one provider.
    ///
    /// **What is deliberately not touched: `WorkGiver_Grower.wantedPlantDef`.** It is static
    /// mutable state that Core writes during its own scan through `CalculateWantedPlantDef`.
    /// Reading it would be meaningless and writing it from a speculative remote probe could
    /// corrupt a scan in progress on another map — which is exactly the class of side effect
    /// the remote-probe prohibition exists to prevent. So the candidate half asks only about
    /// the zone and the plants standing in it, and Core computes the wanted def itself, locally,
    /// when the grower arrives.
    /// </summary>
    public sealed class GrowingProvider : ConnectedDeploymentProvider
    {
        private const int MaximumZonesPerMap = 12;
        private const int MaximumCellsPerZone = 40;

        public override string ProviderId { get { return ConnectedDeploymentProviders.Growing; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_GrowingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Growing"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return FieldworkScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            List<Zone> zones = map.zoneManager == null ? null : map.zoneManager.AllZones;
            if (zones == null || zones.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(zones.Count, MaximumZonesPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < zones.Count; position++)
            {
                if (examined >= MaximumZonesPerMap) { break; }
                examined++;
                var growing = zones[position] as Zone_Growing;
                if (growing == null || growing.Map != map) { continue; }
                if (ZoneHasWork(growing, map, pawn, work)) { return true; }
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            List<Zone> zones = pawn.Map.zoneManager == null ? null : pawn.Map.zoneManager.AllZones;
            if (zones == null) { return false; }
            for (int index = 0; index < zones.Count; index++)
            {
                var growing = zones[index] as Zone_Growing;
                if (growing == null) { continue; }
                if (ZoneHasWork(growing, pawn.Map, pawn, null)) { return true; }
            }
            return false;
        }

        /// <summary>
        /// Whether this growing zone has something to do. Facts about the zone and the plants
        /// standing in it, both of which belong to the zone's own map.
        ///
        /// <paramref name="work"/> is null when asked locally, because the observed-area check
        /// is only meaningful for a map the worker is not standing on.
        /// </summary>
        private static bool ZoneHasWork(Zone_Growing zone, Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            List<IntVec3> cells = zone.Cells;
            if (cells == null || cells.Count == 0) { return false; }
            // Sowing: the zone itself says whether it will accept sowing now.
            bool sowWanted = zone.allowSow && zone.CanAcceptSowNow() && zone.GetPlantDefToGrow() != null;
            int examined = 0;
            for (int index = 0; index < cells.Count; index++)
            {
                if (examined >= MaximumCellsPerZone) { break; }
                examined++;
                IntVec3 cell = cells[index];
                if (!cell.IsValid || !cell.InBounds(map) || cell.Fogged(map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                Plant plant = cell.GetPlant(map);
                if (plant == null)
                {
                    // An empty, unfogged cell in a zone that wants sowing is work.
                    if (sowWanted) { return true; }
                    continue;
                }
                // Harvesting: every one of these is a fact about the plant.
                if (plant.LifeStage != PlantLifeStage.Mature) { continue; }
                if (!plant.HarvestableNow || !plant.CanYieldNow()) { continue; }
                if (!plant.def.plant.autoHarvestable) { continue; }
                // Core refuses to cut a plant the zone is protecting unless it is the one the
                // zone wants grown.
                if (!zone.allowCut && plant.def != zone.GetPlantDefToGrow()) { continue; }
                return true;
            }
            return false;
        }
    }
}
