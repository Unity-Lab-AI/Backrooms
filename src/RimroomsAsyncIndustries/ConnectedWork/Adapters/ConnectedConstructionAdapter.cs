using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Adapters
{
    /// <summary>
    /// Carrying real building material through a gate to a real build site, so a
    /// half-finished structure on one side can be finished with steel that only exists
    /// on the other.
    ///
    /// This is the first family whose destination is a native *work object* rather than
    /// storage or a bed, and so the first real use of the intent's final-target field for
    /// what schema 1 reserved it for. The target is known at planning time here, unlike
    /// hauling and casualties where it is only resolved on arrival.
    ///
    /// Nothing about native construction is reimplemented. The material requirement stays
    /// the constructible's own (`IConstructible.ThingCountNeeded`), the delivery goes into
    /// the frame's own `resourceContainer` through Core's own container toils, and the
    /// work of building is Core's local job as it always was. In particular this never
    /// inflates `itemAvailability` or pretends a remote stack is local, which is the trap
    /// the pinned review warns about: the material physically travels.
    ///
    /// Blueprints are handled as well as frames, because Core's own
    /// `Toils_Construct.MakeSolidThingFromBlueprintIfNecessary` turns a blueprint into a
    /// frame at the moment of delivery. Using Core's toil rather than a private
    /// reimplementation is what makes the first delivery to an untouched blueprint work.
    /// </summary>
    public sealed class ConnectedConstructionAdapter : ConnectedWorkAdapter
    {
        internal const string DeliverJobDefName = "RR_ConnectedDeliverToSite";

        /// <summary>The site no longer wants this material. Not a failure; the trip is over.</summary>
        internal const string SiteSatisfiedKey = "RR_ConnectedWork_SiteSatisfied";

        private const int MaximumSitesPerMap = 16;
        private const int MaximumResourceCandidates = 24;

        public override string AdapterId { get { return ConnectedWorkAdapters.ConstructionSupply; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_ConstructionLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            // Arriving to find the site already supplied is a finished trip with a
            // different ending. The material is physically here and in real hands, and
            // ordinary hauling will put it away.
            return failureKey == SiteSatisfiedKey
                ? ConnectedWorkPhase.Completed : base.TerminalPhaseFor(failureKey);
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

                // Collect where the worker already stands before crossing to collect, the
                // same cost rule the hauling family uses: one crossing beats two.
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
            // The site may have been finished or cancelled while the worker walked here.
            // Checking before the pickup avoids carrying steel nobody wants any more.
            if (StillNeeded(intent) < 1) { return SiteSatisfiedKey; }
            if (!HaulAIUtility.PawnCanAutomaticallyHaul(pawn, source, false))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            int wanted = System.Math.Min(intent.RequestedCount, source.stackCount);
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
            int count = System.Math.Min(intent.RequestedCount, source.stackCount);
            count = System.Math.Min(count, pawn.carryTracker.MaxStackSpaceEver(source.def));
            // Never carry more than the site can still take.
            int needed = StillNeeded(intent);
            if (needed > 0) { count = System.Math.Min(count, needed); }
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
            Thing site = intent.FinalTarget;
            var constructible = site as IConstructible;
            if (site == null || site.Destroyed || !site.Spawned || site.Map != pawn.Map ||
                constructible == null)
            { return SiteSatisfiedKey; }
            if (constructible.IsCompleted() || constructible.ThingCountNeeded(cargo.def) < 1)
            { return SiteSatisfiedKey; }
            if (site.IsForbidden(pawn) ||
                !pawn.CanReach(site, PathEndMode.Touch, pawn.NormalMaxDanger()))
            { return SiteSatisfiedKey; }
            intent.RecordResolvedTarget(site);
            return null;
        }

        public override Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            Thing site = intent == null ? null : intent.FinalTarget;
            var constructible = site as IConstructible;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(DeliverJobDefName);
            if (definition == null || cargo == null || cargo != intent.Cargo || site == null ||
                constructible == null || site.Destroyed || !site.Spawned || site.Map != pawn.Map)
            { return null; }
            int accepted = constructible.ThingCountNeeded(cargo.def);
            var enroute = site as IHaulEnroute;
            if (enroute != null)
            { accepted = System.Math.Min(accepted, enroute.SpaceRemainingFor(cargo.def)); }
            accepted = System.Math.Min(accepted, cargo.stackCount);
            if (accepted < 1) { return null; }
            Job job = JobMaker.MakeJob(definition, cargo, site);
            job.count = accepted;
            job.haulMode = HaulMode.ToContainer;
            return job;
        }

        // ----- candidate search -----

        private ConnectedWorkIntent TryPlanSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map storeMap, PortalRouteStep step)
        {
            List<Thing> sites = BuildSites(storeMap, pawn);
            for (int index = 0; index < sites.Count; index++)
            {
                Thing site = sites[index];
                var constructible = site as IConstructible;
                if (constructible == null || constructible.IsCompleted()) { continue; }
                List<ThingDefCountClass> cost = constructible.TotalMaterialCost();
                if (cost == null) { continue; }
                for (int material = 0; material < cost.Count; material++)
                {
                    ThingDefCountClass required = cost[material];
                    if (required == null || required.thingDef == null) { continue; }
                    int needed = constructible.ThingCountNeeded(required.thingDef);
                    if (needed < 1) { continue; }
                    ConnectedWorkIntent opened = TryOpenSupply(pawn, work, fetchMap, storeMap,
                        site, required.thingDef, needed, step);
                    if (opened != null) { return opened; }
                }
            }
            return null;
        }

        /// <summary>
        /// Build sites on an explicit map, from that map's own listers. A rotating window
        /// so a large site queue cannot starve its own tail.
        /// </summary>
        private static List<Thing> BuildSites(Map map, Pawn pawn)
        {
            var result = new List<Thing>();
            if (map == null) { return result; }
            List<Thing> frames = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame);
            List<Thing> blueprints = map.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint);
            int total = frames.Count + blueprints.Count;
            int windowStart = ConnectedWorkScan.WindowStart(total, MaximumSitesPerMap, pawn);
            int position = 0;
            // Frames first: a frame is a build already under way and stalled, which is the
            // case cross-gate supply exists for.
            for (int index = 0; index < frames.Count && result.Count < MaximumSitesPerMap; index++)
            {
                if (position++ < windowStart) { continue; }
                if (Usable(frames[index], pawn)) { result.Add(frames[index]); }
            }
            for (int index = 0; index < blueprints.Count && result.Count < MaximumSitesPerMap; index++)
            {
                if (position++ < windowStart) { continue; }
                if (Usable(blueprints[index], pawn)) { result.Add(blueprints[index]); }
            }
            return result;
        }

        private static bool Usable(Thing site, Pawn pawn)
        {
            return site != null && !site.Destroyed && site.Spawned &&
                site.Faction == Faction.OfPlayer && !site.IsForbidden(Faction.OfPlayer) &&
                !site.Position.Fogged(site.Map);
        }

        private ConnectedWorkIntent TryOpenSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map storeMap, Thing site, ThingDef material, int needed, PortalRouteStep step)
        {
            if (!work.ObservedAreaAllows(pawn, storeMap, site.Position)) { return null; }
            if (step != null && step.Destination != null &&
                !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
            { return null; }

            List<Thing> stacks = fetchMap.listerThings.ThingsOfDef(material);
            int windowStart = ConnectedWorkScan.WindowStart(stacks.Count, MaximumResourceCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < stacks.Count; position++)
            {
                if (examined >= MaximumResourceCandidates) { break; }
                examined++;
                Thing stack = stacks[position];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != fetchMap ||
                    stack.stackCount < 1 || stack is Pawn || stack is Corpse)
                { continue; }
                if (!stack.def.EverHaulable || stack.IsForbidden(Faction.OfPlayer) || stack.IsBurning())
                { continue; }
                if (stack.Position.Fogged(fetchMap)) { continue; }
                if (!work.ObservedAreaAllows(pawn, fetchMap, stack.Position)) { continue; }
                int available = stack.stackCount - work.LeasedCount(stack);
                if (available < 1) { continue; }
                int carryable = pawn.carryTracker.MaxStackSpaceEver(stack.def);
                if (carryable < 1) { continue; }
                int quantity = System.Math.Min(System.Math.Min(available, carryable), needed);
                if (quantity < 1) { continue; }
                // The site is the final target and it is known now, unlike the other
                // families where the destination is only resolved on arrival.
                ConnectedWorkIntent opened = work.Open(this, pawn, stack, storeMap,
                    IntVec3.Invalid, quantity, site, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>How much of the carried or requested material the site still wants.</summary>
        private static int StillNeeded(ConnectedWorkIntent intent)
        {
            Thing site = intent == null ? null : intent.FinalTarget;
            var constructible = site as IConstructible;
            Thing source = intent == null ? null : intent.SourceThing;
            if (site == null || site.Destroyed || !site.Spawned || constructible == null ||
                source == null || source.def == null)
            { return 0; }
            return constructible.IsCompleted() ? 0 : constructible.ThingCountNeeded(source.def);
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
