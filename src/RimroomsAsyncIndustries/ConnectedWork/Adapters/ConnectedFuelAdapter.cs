using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Adapters
{
    /// <summary>
    /// Carrying fuel through a gate to something of ours that has run dry over there.
    ///
    /// **Refuel and rearm are one family, and Core says so.** The register listed them as two,
    /// but Core's own `RearmTurrets` work giver is `WorkGiver_Refuel_Turret` — a refuel giver
    /// restricted to turrets — because a turret's shells are held in a `CompRefuelable` with a
    /// shell fuel filter. So one adapter covers a wood-fired generator, a smithy, a mortar and
    /// an autocannon, and each takes whatever its own `fuelFilter` accepts. Building two
    /// families would have duplicated the same code against the same comp.
    ///
    /// The hook is the same one the medicine and food families use, confirmed in
    /// `RefuelWorkGiverUtility.FindBestFuel`: it searches `pawn.Map` — and the refueller is
    /// standing next to the thing being refuelled, so **the fuel has to be on that thing's
    /// map**. Putting it there is the whole job; Core finds and consumes it itself.
    ///
    /// ## What Core decides, and this family does not
    ///
    /// * <c>CompRefuelable.Props.fuelFilter</c> decides what counts as fuel for that specific
    ///   object. Never our own list, so a modded machine with an unusual fuel works for free.
    /// * <c>IsFull</c>, <c>TargetFuelLevel</c> and <c>ShouldAutoRefuelNow</c> decide whether it
    ///   wants fuel at all, including the player's own target-fuel slider and the
    ///   auto-refuel toggle. A machine the player set to not auto-refuel is left alone.
    /// * **How much is consumed is never computed here.** Core has its own arithmetic over
    ///   `FuelMultiplierCurrentDifficulty` and the fuel curve, and guessing at a count would be
    ///   inventing a number. This family delivers a carry-load of qualifying fuel when that map
    ///   has none, and stops there.
    ///
    /// ## Deliberately narrow
    ///
    /// The trigger is **"something of ours on that map wants fuel, and there is no fuel it
    /// accepts anywhere on that map."** Not "it is below target" — a machine that is merely
    /// half full while a barrel of chemfuel sits ten cells away is a local hauling job, and
    /// ordinary refuelling will do it. Only an actual absence justifies a gate crossing.
    /// </summary>
    public sealed class ConnectedFuelAdapter : ConnectedWorkAdapter
    {
        /// <summary>It has fuel now. Not a failure; what was carried is real and here.</summary>
        internal const string FuelledKey = "RR_ConnectedWork_AlreadyFuelled";

        private const int MaximumTargetsPerMap = 24;
        private const int MaximumFuelCandidates = 24;
        private const int MaximumPresenceCandidates = 48;

        public override string AdapterId { get { return ConnectedWorkAdapters.FuelSupply; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_FuelLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            if (failureKey == FuelledKey || failureKey == "RR_ConnectedWork_NoStorageOnArrival")
            { return ConnectedWorkPhase.Completed; }
            return base.TerminalPhaseFor(failureKey);
        }

        public override ConnectedWorkIntent TryPlan(Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (work == null || !work.CanOperate || campaign == null || pawn == null || !pawn.Spawned ||
                pawn.Map == null || pawn.carryTracker == null || !campaign.OwnsMap(pawn.Map))
            { return null; }
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }

            Map home = pawn.Map;
            List<Map> connected = ConnectedWorkScan.ConnectedMaps(campaign, home, pawn);
            for (int index = 0; index < connected.Count; index++)
            {
                Map other = connected[index];
                if (work.DestinationRecentlyRefused(pawn, other)) { continue; }
                PortalRouteStep step;
                bool pending;
                if (!work.Routes.TryNextStep(home, other, out step, out pending)) { continue; }
                if (step != null && step.Destination != null &&
                    !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
                { continue; }

                ConnectedWorkIntent fromHere = TryPlanSupply(pawn, work, home, other, step);
                if (fromHere != null) { return fromHere; }
                ConnectedWorkIntent fromThere = TryPlanSupply(pawn, work, other, home, step);
                if (fromThere != null) { return fromThere; }
            }
            return null;
        }

        public override string RevalidateAtFetchSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            if (source == null || source.Destroyed || !source.Spawned || pawn == null ||
                pawn.carryTracker == null || source.Map != pawn.Map ||
                source.GetUniqueLoadID() != intent.SourceThingLoadId || source.stackCount < 1)
            { return "RR_ConnectedWork_ObjectGone"; }
            if (!StillDry(intent, source.def)) { return FuelledKey; }
            if (!HaulAIUtility.PawnCanAutomaticallyHaul(pawn, source, false))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            int wanted = Math.Min(intent.RequestedCount, source.stackCount);
            if (wanted < 1 || pawn.carryTracker.MaxStackSpaceEver(source.def) < 1)
            { return "RR_ConnectedWork_CannotCarry"; }
            if (!pawn.CanReserveAndReach(source, PathEndMode.ClosestTouch, pawn.NormalMaxDanger(), 1, wanted))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            return null;
        }

        public override Job FetchJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.FetchJobDefName);
            if (definition == null || source == null || pawn == null || pawn.carryTracker == null)
            { return null; }
            int count = Math.Min(intent.RequestedCount, source.stackCount);
            count = Math.Min(count, pawn.carryTracker.MaxStackSpaceEver(source.def));
            if (count < 1) { return null; }
            Job job = JobMaker.MakeJob(definition, source);
            job.count = count;
            return job;
        }

        public override string RevalidateAtStoreSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (intent == null || cargo == null || cargo != intent.Cargo || cargo.Destroyed ||
                cargo.GetUniqueLoadID() != intent.CargoLoadId)
            { return "RR_ConnectedWork_CargoGone"; }
            // Like food, deliberately not refused when the need has passed: fuel keeps, and
            // storing it on that map is the right outcome either way.
            IntVec3 cell;
            if (!StoreUtility.TryFindBestBetterStorageFor(cargo, pawn, pawn.Map,
                StoragePriority.Unstored, pawn.Faction, out cell, out IHaulDestination _) ||
                !cell.IsValid)
            { return "RR_ConnectedWork_NoStorageOnArrival"; }
            intent.RecordResolvedCellForTarget(cell);
            return null;
        }

        public override Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.DeliverJobDefName);
            if (definition == null || intent == null || cargo == null || cargo != intent.Cargo)
            { return null; }
            IntVec3 cell = intent.CandidateStoreCell;
            if (!cell.IsValid || !cell.InBounds(pawn.Map)) { return null; }
            Job job = JobMaker.MakeJob(definition, cargo, cell);
            job.count = cargo.stackCount;
            job.haulMode = HaulMode.ToCellStorage;
            return job;
        }

        // ----- candidate search, explicit-map only -----

        private ConnectedWorkIntent TryPlanSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map targetMap, PortalRouteStep step)
        {
            List<Thing> refuelables = targetMap.listerThings
                .ThingsInGroup(ThingRequestGroup.Refuelable);
            if (refuelables.Count == 0) { return null; }
            int windowStart = ConnectedWorkScan.WindowStart(refuelables.Count, MaximumTargetsPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < refuelables.Count; position++)
            {
                if (examined >= MaximumTargetsPerMap) { break; }
                examined++;
                Thing target = refuelables[position];
                CompRefuelable comp = WantsFuel(target, pawn, targetMap);
                if (comp == null) { continue; }
                if (!work.ObservedAreaAllows(pawn, targetMap, target.Position)) { continue; }
                // Only a genuine absence justifies a crossing. Something half full with a
                // barrel nearby is a local hauling job.
                if (AnyFuelOn(targetMap, comp)) { continue; }
                ConnectedWorkIntent opened = TryOpenSupply(pawn, work, fetchMap, targetMap,
                    target, comp, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// The refuelable comp if this thing of ours wants fuel, else null. Every rule is a
        /// fact about the thing, its comp and its own map — including the player's own
        /// auto-refuel toggle and target-fuel level, both of which are respected rather than
        /// overridden.
        /// </summary>
        private static CompRefuelable WantsFuel(Thing target, Pawn pawn, Map map)
        {
            if (target == null || target.Destroyed || !target.Spawned || target.Map != map)
            { return null; }
            if (target.Faction != pawn.Faction) { return null; }
            if (target.IsBurning() || target.Position.Fogged(map)) { return null; }
            CompRefuelable comp = target.TryGetComp<CompRefuelable>();
            if (comp == null || comp.Props == null || comp.Props.fuelFilter == null) { return null; }
            if (comp.IsFull) { return null; }
            // The player said not to refuel this automatically.
            if (!comp.allowAutoRefuel) { return null; }
            if (comp.FuelPercentOfMax > 0f && !comp.Props.allowRefuelIfNotEmpty) { return null; }
            return comp.ShouldAutoRefuelNow ? comp : null;
        }

        private ConnectedWorkIntent TryOpenSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map targetMap, Thing target, CompRefuelable comp, PortalRouteStep step)
        {
            ThingFilter filter = comp.Props.fuelFilter;
            List<Thing> available = fetchMap.listerThings.AllThings;
            int windowStart = ConnectedWorkScan.WindowStart(available.Count, MaximumFuelCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < available.Count; position++)
            {
                if (examined >= MaximumFuelCandidates) { break; }
                examined++;
                Thing stack = available[position];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != fetchMap ||
                    stack.stackCount < 1 || stack is Pawn)
                { continue; }
                // The object's own fuel filter decides what fuel is, so a modded machine with
                // an unusual fuel is handled without this family knowing what it is.
                if (!filter.Allows(stack)) { continue; }
                if (!stack.def.EverHaulable || stack.IsForbidden(Faction.OfPlayer) || stack.IsBurning())
                { continue; }
                if (stack.Position.Fogged(fetchMap)) { continue; }
                if (!work.ObservedAreaAllows(pawn, fetchMap, stack.Position)) { continue; }

                int free = stack.stackCount - work.LeasedCount(stack);
                if (free < 1) { continue; }
                int carryable = pawn.carryTracker.MaxStackSpaceEver(stack.def);
                if (carryable < 1) { continue; }
                int quantity = Math.Min(free, carryable);
                if (quantity < 1) { continue; }

                ConnectedWorkIntent opened = work.Open(this, pawn, stack, targetMap,
                    IntVec3.Invalid, quantity, target, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>Whether that map already holds fuel this object would accept.</summary>
        private static bool AnyFuelOn(Map map, CompRefuelable comp)
        {
            ThingFilter filter = comp.Props.fuelFilter;
            List<Thing> present = map.listerThings.AllThings;
            int examined = 0;
            for (int index = 0; index < present.Count; index++)
            {
                if (examined >= MaximumPresenceCandidates) { break; }
                Thing thing = present[index];
                if (thing == null || thing.Destroyed || !thing.Spawned || thing.Map != map ||
                    thing is Pawn)
                { continue; }
                if (!filter.Allows(thing)) { continue; }
                examined++;
                if (thing.IsForbidden(Faction.OfPlayer) || thing.Position.Fogged(map)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>Whether the recorded object still wants fuel and still has none there.</summary>
        private static bool StillDry(ConnectedWorkIntent intent, ThingDef def)
        {
            Thing target = intent == null ? null : intent.FinalTarget;
            if (target == null || def == null || target.MapHeld == null) { return false; }
            CompRefuelable comp = target.TryGetComp<CompRefuelable>();
            if (comp == null || comp.Props == null || comp.Props.fuelFilter == null) { return false; }
            if (comp.IsFull || !comp.allowAutoRefuel) { return false; }
            if (!comp.Props.fuelFilter.Allows(def)) { return false; }
            return !AnyFuelOn(target.MapHeld, comp);
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
