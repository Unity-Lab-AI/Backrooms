using System;
using System.Collections.Generic;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Adapters
{
    /// <summary>
    /// Storage hauling across a gate, in both directions: fetch an actual object from
    /// the map that holds it, carry it through in real hands under native mass and
    /// stack limits, and place it in storage the destination map's own settings
    /// accept. No stock counter, no remote consumption, no cloned stack.
    ///
    /// The candidate search runs against an explicit Map and asks only questions that
    /// are genuinely map-parameterised. The decisions that depend on the worker —
    /// forbidden, allowed area, reachability, reservations — are deliberately not
    /// asked until the worker is standing on that map, because Core answers those
    /// against <c>pawn.Map</c> and would otherwise answer about the wrong side.
    /// </summary>
    public sealed class ConnectedHaulingAdapter : ConnectedWorkAdapter
    {
        internal const string FetchJobDefName = "RR_ConnectedFetch";
        internal const string DeliverJobDefName = "RR_ConnectedDeliver";
        internal const string DeliverContainerJobDefName = "RR_ConnectedDeliverContainer";

        /// <summary>
        /// Arriving to find the planned storage gone. Not a failure: the object is
        /// physically here in real hands, and ordinary hauling takes it from there.
        /// </summary>
        internal const string NoStorageOnArrivalKey = "RR_ConnectedWork_NoStorageOnArrival";

        // Every search below is capped. A planning pass costs a fixed amount whatever
        // the size of the colony, the site or the graph.
        private const int MaximumConnectedMapsPerPass = 4;
        private const int MaximumLooseCandidatesPerMap = 24;
        private const int MaximumStoredCandidatesPerMap = 24;
        private const int MaximumGroupsPerCandidate = 8;
        private const int MaximumCellsPerGroup = 24;

        public override string AdapterId { get { return ConnectedWorkAdapters.StorageHauling; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_HaulingLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            return failureKey == NoStorageOnArrivalKey
                ? ConnectedWorkPhase.Completed : base.TerminalPhaseFor(failureKey);
        }

        public override ConnectedWorkIntent TryPlan(Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (work == null || !work.CanOperate || campaign == null || pawn == null || !pawn.Spawned ||
                pawn.Map == null || pawn.carryTracker == null || !campaign.OwnsMap(pawn.Map))
            { return null; }
            // The gate rule, asked before any planning: only this company's own
            // people may ever decide to cross, whoever asked for the work.
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }

            Map home = pawn.Map;
            List<Map> connected = ConnectedMaps(campaign, home, pawn);
            for (int index = 0; index < connected.Count; index++)
            {
                Map other = connected[index];
                // A destination that just turned this worker away is left alone for a
                // while, so a refusal cannot become a daily round trip to nowhere.
                if (work.DestinationRecentlyRefused(pawn, other)) { continue; }
                PortalRouteStep step;
                bool pending;
                if (!work.Routes.TryNextStep(home, other, out step, out pending))
                {
                    // Pending means the bounded search has not finished, which is not
                    // the same as unconnected. Either way this pass simply moves on.
                    continue;
                }
                // Collect where the worker already stands before sending it through a
                // gate to collect. A trip that starts here costs one crossing; a trip
                // that starts over there costs two, so given the choice the nearer
                // work wins. This also gives the behaviour the fantasy wants without
                // hard-coding a favoured direction: a worker inside the Backrooms
                // takes what it finds home, and a worker at headquarters only carries
                // goods inward when the player deliberately built better storage
                // there to carry them to.
                ConnectedWorkIntent fromHere = TryPlanTransfer(pawn, work, home, other, step);
                if (fromHere != null) { return fromHere; }
                ConnectedWorkIntent fromThere = TryPlanTransfer(pawn, work, other, home, step);
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

            // The worker is on this map now, so Core's own precondition is finally
            // answering about this map: haulability, fog, forbidden and allowed area.
            if (!HaulAIUtility.PawnCanAutomaticallyHaul(pawn, source, false))
            { return "RR_ConnectedWork_ObjectUnavailable"; }

            int wanted = Math.Min(intent.RequestedCount, source.stackCount);
            if (wanted < 1 || pawn.carryTracker.MaxStackSpaceEver(source.def) < 1)
            { return "RR_ConnectedWork_CannotCarry"; }
            // A native reservation, taken locally by the real worker. The planning
            // lease never claimed this and never excluded the pawn who just did.
            if (!pawn.CanReserveAndReach(source, PathEndMode.ClosestTouch, pawn.NormalMaxDanger(), 1, wanted))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            return null;
        }

        public override Job FetchJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(FetchJobDefName);
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

            // The definitive storage decision. Both the worker and the object are on
            // this map, so this is the ordinary native search, not a remote guess.
            StoragePriority current = StoreUtility.CurrentStoragePriorityOf(cargo);
            IntVec3 cell;
            IHaulDestination destination;
            if (!StoreUtility.TryFindBestBetterStorageFor(cargo, pawn, pawn.Map, current,
                    pawn.Faction, out cell, out destination))
            { return NoStorageOnArrivalKey; }

            // Core's own branch, mirrored exactly: a slot-group parent is delivered to
            // by cell, and a container that exposes an inner ThingOwner is delivered
            // into. Following Core here is what makes shelves, graves and the storage
            // framework mods work without a separate adapter for each of them.
            if (!(destination is ISlotGroupParent))
            {
                Thing container = destination as Thing;
                if (container != null && !container.Destroyed && container.Spawned &&
                    container.Map == pawn.Map && container.TryGetInnerInteractableThingOwner() != null &&
                    !container.IsForbidden(pawn) &&
                    pawn.CanReserveAndReach(container, PathEndMode.Touch, pawn.NormalMaxDanger()))
                {
                    intent.RecordResolvedContainer(container);
                    return null;
                }
                // The best destination turned out to be unusable. Fall back to the best
                // plain cell before giving up, rather than setting the object down.
                if (!StoreUtility.TryFindBestBetterStoreCellFor(cargo, pawn, pawn.Map, current,
                        pawn.Faction, out cell))
                { return NoStorageOnArrivalKey; }
            }
            if (!cell.IsValid ||
                !pawn.CanReserveAndReach(cell, PathEndMode.ClosestTouch, pawn.NormalMaxDanger()))
            { return NoStorageOnArrivalKey; }
            intent.RecordResolvedStoreCell(cell);
            return null;
        }

        public override Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (intent == null || cargo == null || cargo != intent.Cargo) { return null; }

            Thing container = intent.FinalTarget;
            if (container != null)
            {
                JobDef containerDefinition = DefDatabase<JobDef>.GetNamedSilentFail(DeliverContainerJobDefName);
                ThingOwner owner = container.Destroyed || !container.Spawned || container.Map != pawn.Map
                    ? null : container.TryGetInnerInteractableThingOwner();
                if (containerDefinition == null || owner == null) { return null; }
                int accepted = Math.Min(cargo.stackCount, owner.GetCountCanAccept(cargo));
                if (accepted < 1) { return null; }
                Job containerJob = JobMaker.MakeJob(containerDefinition, cargo, container);
                containerJob.count = accepted;
                containerJob.haulMode = HaulMode.ToContainer;
                return containerJob;
            }

            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(DeliverJobDefName);
            if (definition == null || !intent.CandidateStoreCell.IsValid) { return null; }
            Job job = JobMaker.MakeJob(definition, cargo, intent.CandidateStoreCell);
            job.count = cargo.stackCount;
            job.haulMode = HaulMode.ToCellStorage;
            return job;
        }

        // ----- candidate search -----

        /// <summary>
        /// A deterministic rotating offset, with no randomness so a reload cannot
        /// change what a pass sees. Every bounded scan below examines a *window*
        /// rather than a fixed prefix. That matters because this branch may hold many
        /// gates at once: with a prefix, the fifth and sixth connected space would be
        /// starved forever. It is the same principle the route search already follows,
        /// where running out of budget must never become a permanent answer.
        /// </summary>
        private static int RotationOffset(int count, Pawn pawn)
        {
            if (count <= 1) { return 0; }
            long turn = Find.TickManager.TicksGame / RimroomsConnectedWorkComponent.PlanningCooldownTicks;
            int offset = (int)((turn + pawn.thingIDNumber) % count);
            return offset < 0 ? offset + count : offset;
        }

        /// <summary>
        /// Where a window of <paramref name="budget"/> items should start so that it
        /// always fits inside <paramref name="count"/> and still reaches every position
        /// across successive passes. A pass therefore spends its whole budget instead
        /// of being cut short near the end of the collection.
        /// </summary>
        private static int WindowStart(int count, int budget, Pawn pawn)
        {
            return count <= budget ? 0 : RotationOffset(count - budget + 1, pawn);
        }

        private static List<Map> ConnectedMaps(RimroomsCampaignComponent campaign, Map home, Pawn pawn)
        {
            var result = new List<Map>();
            List<Map> maps = Find.Maps;
            if (maps.Count == 0) { return result; }
            int start = RotationOffset(maps.Count, pawn);
            for (int step = 0; step < maps.Count && result.Count < MaximumConnectedMapsPerPass; step++)
            {
                Map map = maps[(start + step) % maps.Count];
                if (map == home || !campaign.OwnsMap(map)) { continue; }
                result.Add(map);
            }
            return result;
        }

        private ConnectedWorkIntent TryPlanTransfer(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map storeMap, PortalRouteStep step)
        {
            // Candidate source one: what the fetch map's own lister already considers
            // loose, which on a Backrooms floor is the salvage lying around.
            ICollection<Thing> loose = fetchMap.listerHaulables.ThingsPotentiallyNeedingHauling();
            int windowStart = WindowStart(loose.Count, MaximumLooseCandidatesPerMap, pawn);
            int position = 0;
            int examined = 0;
            foreach (Thing thing in loose)
            {
                // Walking the collection is cheap; only the windowed entries pay for a
                // storage search. A big floor of salvage is covered across passes.
                if (position++ < windowStart) { continue; }
                if (examined >= MaximumLooseCandidatesPerMap) { break; }
                examined++;
                ConnectedWorkIntent opened = TryOpenFor(pawn, work, thing, fetchMap, storeMap, step);
                if (opened != null) { return opened; }
            }
            // Candidate source two: what that map's lister deliberately never offers.
            // Core excludes anything already in its best storage *on its own map*, so
            // a crate sitting in a perfectly good far stockpile is invisible to it
            // even when the player has built strictly better storage on this side.
            // Without this pass, "bring it home" would silently not work.
            return TryPlanFromStorage(pawn, work, fetchMap, storeMap, step);
        }

        private ConnectedWorkIntent TryPlanFromStorage(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map storeMap, PortalRouteStep step)
        {
            List<SlotGroup> groups = fetchMap.haulDestinationManager.AllGroupsListInPriorityOrder;
            if (groups.Count == 0) { return null; }
            int start = RotationOffset(groups.Count, pawn);
            int examined = 0;
            // Within a pass this follows the map's own storage priority order; the
            // rotating start is what stops a stockpile past the cap from being
            // permanently invisible.
            for (int rotation = 0; rotation < groups.Count; rotation++)
            {
                if (examined >= MaximumStoredCandidatesPerMap) { break; }
                SlotGroup group = groups[(start + rotation) % groups.Count];
                if (group == null) { continue; }
                foreach (Thing held in group.HeldThings)
                {
                    if (examined >= MaximumStoredCandidatesPerMap) { break; }
                    examined++;
                    ConnectedWorkIntent opened = TryOpenFor(pawn, work, held, fetchMap, storeMap, step);
                    if (opened != null) { return opened; }
                }
            }
            return null;
        }

        private ConnectedWorkIntent TryOpenFor(Pawn pawn, RimroomsConnectedWorkComponent work, Thing thing,
            Map fetchMap, Map storeMap, PortalRouteStep step)
        {
            if (!CandidateObject(thing, fetchMap)) { return null; }
            int available = thing.stackCount - work.LeasedCount(thing);
            if (available < 1) { return null; }
            int carryable = pawn.carryTracker.MaxStackSpaceEver(thing.def);
            if (carryable < 1) { return null; }
            IntVec3 cell;
            if (!TryFindCandidateStoreCell(storeMap, thing, out cell)) { return null; }
            // Allowed areas, as far as this worker has ever been observed on those
            // maps. Unobserved reads as unrestricted, which is Core's own answer for a
            // map no area was set on. The definitive per-pawn check still runs on
            // arrival; this only avoids planning a trip we already know ends in a
            // refusal. See RimroomsConnectedWorkComponent.ObservedAreaAllows.
            if (!work.ObservedAreaAllows(pawn, fetchMap, thing.Position) ||
                !work.ObservedAreaAllows(pawn, storeMap, cell))
            { return null; }
            if (step != null && step.Destination != null && step.Source != null &&
                !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
            { return null; }
            return work.Open(this, pawn, thing, storeMap, cell, Math.Min(available, carryable), null, step);
        }

        private static bool CandidateObject(Thing thing, Map fetchMap)
        {
            if (thing == null || thing.Destroyed || !thing.Spawned || thing.Map != fetchMap ||
                thing.def == null || thing.stackCount < 1)
            { return false; }
            // People and remains are never storage cargo. Carrying someone downed,
            // dead or imprisoned back through a gate is allowed by the traversal
            // policy, but it is rescue, capture or burial work, and those families
            // own their own custody, bed and grave rules.
            if (thing is Pawn || thing is Corpse) { return false; }
            if (!thing.def.EverHaulable || thing.def.category != ThingCategory.Item) { return false; }
            // Faction-level forbidding is a property of the object, so it is safe to
            // read from anywhere. Per-pawn forbidding and allowed areas are not, and
            // are deliberately left to the definitive check on arrival.
            if (thing.IsForbidden(Faction.OfPlayer) || thing.IsBurning()) { return false; }
            // Nothing in unrevealed rooms. A gate is not x-ray vision.
            return !thing.Position.Fogged(fetchMap);
        }

        private static bool TryFindCandidateStoreCell(Map storeMap, Thing thing, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            StoragePriority current = StoreUtility.CurrentStoragePriorityOf(thing);
            List<SlotGroup> groups = storeMap.haulDestinationManager.AllGroupsListInPriorityOrder;
            int groupsExamined = 0;
            for (int index = 0; index < groups.Count; index++)
            {
                if (groupsExamined >= MaximumGroupsPerCandidate) { break; }
                SlotGroup group = groups[index];
                if (group == null || group.Settings == null || group.Settings.Priority <= current ||
                    !group.Settings.AllowedToAccept(thing))
                { continue; }
                groupsExamined++;
                List<IntVec3> cells = group.CellsList;
                int limit = Math.Min(cells.Count, MaximumCellsPerGroup);
                for (int cellIndex = 0; cellIndex < limit; cellIndex++)
                {
                    // The one storage predicate Core itself parameterises by Map, and
                    // uses this way internally, so it answers about the other side
                    // instead of quietly answering about the worker's side.
                    if (!cells[cellIndex].IsValidStorageFor(storeMap, thing)) { continue; }
                    cell = cells[cellIndex];
                    return true;
                }
            }
            return false;
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
