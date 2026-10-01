using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// The three upkeep families — cleaning, repair and firefighting — kept together because
    /// they share a shape and, more importantly, they share one decisive Core rule.
    ///
    /// **All three only ever happen inside that map's Home area.** Core's own givers check
    /// `map.areaManager.Home[position]` and refuse outright otherwise:
    /// `WorkGiver_CleanFilth` reads `listerFilthInHomeArea`, `WorkGiver_Repair` fails with
    /// `NotInHomeAreaTrans`, and `WorkGiver_FightFires` does the same for any fire that is not
    /// burning on a pawn. `areaManager` is a public field on `Map`, so this is a map-explicit
    /// question and is fair to ask about a map nobody is standing on.
    ///
    /// That single fact settles the scope of all three for free: a generated Backrooms
    /// coordinate with no Home area set attracts none of this work, exactly as it attracts
    /// none of Core's own. Nobody crosses a gate to sweep an anomalous corridor, because the
    /// player never told anyone it was home. If the player *does* set a Home area on the far
    /// side, upkeep follows — which is the right and unsurprising behaviour.
    ///
    /// None of the three issues any work. On arrival Core's own giver takes over locally.
    /// </summary>
    internal static class UpkeepScan
    {
        /// <summary>How many candidates any one upkeep pass may look at.</summary>
        internal const int MaximumCandidates = 24;

        /// <summary>
        /// Whether this cell is inside that map's Home area. The shared precondition for all
        /// three families, and map-explicit: `Map.areaManager` is public and `Home` is indexed
        /// by cell, so no pawn and no other map is involved.
        /// </summary>
        internal static bool InHomeArea(Map map, IntVec3 cell)
        {
            return map != null && map.areaManager != null && map.areaManager.Home != null &&
                cell.IsValid && map.areaManager.Home[cell];
        }
    }

    /// <summary>
    /// A cleaner crossing a gate to deal with filth in the Home area over there.
    ///
    /// `map.listerFilthInHomeArea.FilthInHomeArea` is Core's own map-explicit list and already
    /// applies the Home-area filter, so the candidate half reads exactly what Core reads.
    /// `TicksSinceThickened` and `Fogged` are facts about the filth. Only the reservation is
    /// left to arrival.
    /// </summary>
    public sealed class CleaningProvider : ConnectedDeploymentProvider
    {
        /// <summary>Core's own threshold, not one of ours.</summary>
        private const int MinimumTicksSinceThickened = 600;

        public override string ProviderId { get { return ConnectedDeploymentProviders.Cleaning; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_CleaningLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Cleaning"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            // Weather work first: both are a TrueCount comparison on an area, so a map with no
            // snow area and no pollution area leaves in two integer reads.
            if (AnyWeatherToClear(map, pawn, work)) { return true; }
            List<Thing> filth = FilthOn(map);
            if (filth == null || filth.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(filth.Count, UpkeepScan.MaximumCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < filth.Count; position++)
            {
                if (examined >= UpkeepScan.MaximumCandidates) { break; }
                examined++;
                if (!Candidate(filth[position] as Filth, map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, filth[position].Position)) { continue; }
                return true;
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            if (AnyWeatherToClear(pawn.Map, pawn, null)) { return true; }
            List<Thing> filth = FilthOn(pawn.Map);
            if (filth == null) { return false; }
            for (int index = 0; index < filth.Count; index++)
            {
                if (!Candidate(filth[index] as Filth, pawn.Map)) { continue; }
                if (!pawn.CanReserve(filth[index], 1, -1, null, false)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// How many marked cells one remote pass may look at. Areas are cell sets and a player
        /// can paint a large one.
        /// </summary>
        private const int MaximumWeatherCellsPerMap = 24;

        /// <summary>
        /// Snow, sand or pollution the player marked for clearing on that map.
        ///
        /// **Live only since the ordinary-map endpoint landed at 0.6.9-dev.**
        /// `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded `Area_SnowOrSandClear` and
        /// `Area_PollutionClear` as not covered *and correctly so*, with the reason written down:
        /// a Backrooms coordinate **has no outside and therefore no weather**, so nothing
        /// accumulates there and the areas have nothing in them. A registered remote site is an
        /// ordinary world map, which does get snow and can be polluted, so the reason expired.
        ///
        /// On a coordinate this still finds nothing, because there is still nothing to find.
        ///
        /// Both halves are facts about the map asked about, taken from Core's own givers:
        /// `WorkGiver_ClearSnowOrSand` refuses below `0.2f` of snow **or** sand depth, and
        /// `WorkGiver_ClearPollution` asks `map.pollutionGrid.IsPolluted(cell)`. Neither takes a
        /// pawn, so Core's real question is asked here rather than substituted for. The
        /// reservation is all that is left to arrival.
        ///
        /// `map.pollutionGrid` is null without Biotech, which is the only gate either route
        /// needs: an absent expansion is an empty world, not a condition.
        /// </summary>
        private static bool AnyWeatherToClear(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map.areaManager == null) { return false; }
            return AnyMarked(map, pawn, work, map.areaManager.SnowOrSandClear, true) ||
                AnyMarked(map, pawn, work, map.areaManager.PollutionClear, false);
        }

        private static bool AnyMarked(Map map, Pawn pawn, RimroomsConnectedWorkComponent work,
            Area area, bool snow)
        {
            if (area == null || area.TrueCount == 0) { return false; }
            if (!snow && map.pollutionGrid == null) { return false; }
            int examined = 0;
            foreach (IntVec3 cell in area.ActiveCells)
            {
                if (work != null && examined >= MaximumWeatherCellsPerMap) { break; }
                examined++;
                if (!cell.IsValid || !cell.InBounds(map) || cell.Fogged(map)) { continue; }
                if (snow)
                {
                    // Core's own threshold, and it is an OR: either depth alone is enough.
                    if (map.snowGrid == null) { continue; }
                    if (map.snowGrid.GetDepth(cell) < 0.2f && cell.GetSandDepth(map) < 0.2f)
                    { continue; }
                }
                else if (!map.pollutionGrid.IsPolluted(cell)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                if (work == null && !pawn.CanReserve(cell, 1, -1, null)) { continue; }
                return true;
            }
            return false;
        }

        private static List<Thing> FilthOn(Map map)
        {
            return map.listerFilthInHomeArea == null ? null : map.listerFilthInHomeArea.FilthInHomeArea;
        }

        private static bool Candidate(Filth filth, Map map)
        {
            if (filth == null || filth.Destroyed || !filth.Spawned || filth.Map != map) { return false; }
            // The lister is already Home-area filtered, but Core re-checks it in HasJobOnThing
            // because the area can change under it, and so does this.
            if (!UpkeepScan.InHomeArea(map, filth.Position)) { return false; }
            if (filth.Fogged()) { return false; }
            return filth.TicksSinceThickened >= MinimumTicksSinceThickened;
        }
    }

    /// <summary>
    /// A builder crossing a gate to repair damaged buildings of ours in the Home area there.
    ///
    /// `map.listerBuildingsRepairable.RepairableBuildings(faction)` is Core's own map-explicit
    /// list, taking the faction as a parameter, so it can be asked of any map. `PawnCanRepairEver`
    /// is map-free — it reads the def, `useHitPoints`, `building.repairable` and the faction.
    /// `PawnCanRepairNow` is **not** remote-safe, because it consults `pawn.Map`'s own lister;
    /// its remaining conditions are re-asked here against the building's own map instead.
    /// </summary>
    public sealed class RepairProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.Repair; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_RepairLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Construction"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            List<Thing> damaged = RepairableOn(map, pawn.Faction);
            if (damaged == null || damaged.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(damaged.Count, UpkeepScan.MaximumCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < damaged.Count; position++)
            {
                if (examined >= UpkeepScan.MaximumCandidates) { break; }
                examined++;
                if (!Candidate(damaged[position] as Building, pawn, map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, damaged[position].Position)) { continue; }
                return true;
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            List<Thing> damaged = RepairableOn(pawn.Map, pawn.Faction);
            if (damaged == null) { return false; }
            for (int index = 0; index < damaged.Count; index++)
            {
                var building = damaged[index] as Building;
                if (building == null) { continue; }
                // Core's own definitive check, which is only meaningful on the pawn's own map.
                if (!RepairUtility.PawnCanRepairNow(pawn, building)) { continue; }
                if (!UpkeepScan.InHomeArea(pawn.Map, building.Position)) { continue; }
                if (!pawn.CanReserve(building, 1, -1, null, false)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Core's own repairable list for a named map and faction.
        ///
        /// **Internal rather than private because the clear squad calls it.** *"fix broken walls
        /// and equipment"* needs the set of damaged player buildings, and this is already the
        /// mod's single wrapper for the question. A second hand-rolled scan would be a second
        /// derivation of a rule Core owns, which is the defect this project keeps meeting.
        /// </summary>
        internal static List<Thing> RepairableOn(Map map, Faction faction)
        {
            if (map.listerBuildingsRepairable == null || faction == null) { return null; }
            return map.listerBuildingsRepairable.RepairableBuildings(faction);
        }

        /// <summary>
        /// Every rule reads the building, its def, its own map's designations, or the pawn's
        /// faction. None reads the worker's map.
        /// </summary>
        private static bool Candidate(Building building, Pawn pawn, Map map)
        {
            if (building == null || building.Destroyed || !building.Spawned || building.Map != map)
            { return false; }
            // Map-free half of Core's own repair test: def, hit points, repairable, faction.
            if (!RepairUtility.PawnCanRepairEver(pawn, building)) { return false; }
            if (building.HitPoints >= building.MaxHitPoints) { return false; }
            if (building.IsBurning()) { return false; }
            if (!UpkeepScan.InHomeArea(map, building.Position)) { return false; }
            // Something already marked for removal is not repaired, and Core checks each of
            // these against the building's own map, which is exactly what is available here.
            DesignationManager designations = map.designationManager;
            if (designations == null) { return true; }
            if (designations.DesignationOn(building, DesignationDefOf.Deconstruct) != null)
            { return false; }
            if (building.def.mineable)
            {
                if (designations.DesignationAt(building.Position, DesignationDefOf.Mine) != null)
                { return false; }
                if (designations.DesignationAt(building.Position, DesignationDefOf.MineVein) != null)
                { return false; }
            }
            return true;
        }
    }

    /// <summary>
    /// A firefighter crossing a gate to beat out fires in the Home area over there.
    ///
    /// **The danger question, answered honestly.** This is the first family where crossing
    /// *toward* trouble is the entire point, and it is worth being explicit: Core's own
    /// `WorkGiver_FightFires` uses `Danger.Deadly` for its local pathing, but **the crossing
    /// itself does not**. `ConnectedCrossing.StepToward` uses `pawn.NormalMaxDanger()`, as
    /// every automatic cross-gate step does, because a player order may accept deadly danger
    /// and automatic work may not. So a colonist will cross to fight a fire only while the
    /// route to the gate is within its own danger policy, and a burning map on the far side
    /// does not by itself override that. That is deliberate and it is the conservative
    /// reading: losing somebody in transit to a fire they were never ordered to fight would
    /// be strictly worse than the fire.
    ///
    /// Fires burning **on a pawn** are excluded from the remote half entirely. Core handles
    /// those with a proximity rule measured from the *firefighter's* position, which is
    /// meaningless across a gate, and someone burning on another map needs a local response
    /// rather than a traveller.
    /// </summary>
    public sealed class FirefightingProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.Firefighting; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_FirefightingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Firefighter"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            // Core's own capability gate for anything that is not a pawn on fire.
            if (pawn.WorkTagIsDisabled(WorkTags.Firefighting)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            ThingDef fireDef = ThingDefOf.Fire;
            if (fireDef == null) { return false; }
            List<Thing> fires = map.listerThings.ThingsOfDef(fireDef);
            if (fires.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(fires.Count, UpkeepScan.MaximumCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < fires.Count; position++)
            {
                if (examined >= UpkeepScan.MaximumCandidates) { break; }
                examined++;
                if (!Candidate(fires[position] as Fire, map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, fires[position].Position)) { continue; }
                return true;
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            ThingDef fireDef = ThingDefOf.Fire;
            if (fireDef == null) { return false; }
            List<Thing> fires = pawn.Map.listerThings.ThingsOfDef(fireDef);
            for (int index = 0; index < fires.Count; index++)
            {
                var fire = fires[index] as Fire;
                if (!Candidate(fire, pawn.Map)) { continue; }
                // Core's own "somebody is already dealing with this one" rule. Its
                // WorkGiver_FightFires is `internal`, so the rule is reproduced here from the
                // same public pieces it uses rather than called: the fire's own reservation
                // manager, and whether the respected reserver is standing within five cells.
                if (FireIsBeingHandled(fire, pawn)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether somebody is already close enough to this fire to be dealing with it.
        /// Reproduces Core's own rule — reserver within five cells — because the class that
        /// owns it is internal. The distance and the reservation both come from the fire's own
        /// map, so this is only asked on arrival, where a real reserver position exists.
        /// </summary>
        private static bool FireIsBeingHandled(Fire fire, Pawn potentialHandler)
        {
            if (fire == null || !fire.Spawned || fire.Map == null ||
                fire.Map.reservationManager == null)
            { return false; }
            Pawn reserver = fire.Map.reservationManager.FirstRespectedReserver(fire, potentialHandler);
            return reserver != null && reserver.Position.InHorDistOf(fire.Position, 5f);
        }

        /// <summary>
        /// Facts about the fire and its own map only. Fires on pawns are excluded, for the
        /// reason given on the class.
        /// </summary>
        private static bool Candidate(Fire fire, Map map)
        {
            if (fire == null || fire.Destroyed || !fire.Spawned || fire.Map != map) { return false; }
            if (fire.parent is Pawn) { return false; }
            if (fire.Position.Fogged(map)) { return false; }
            return UpkeepScan.InHomeArea(map, fire.Position);
        }
    }
}
