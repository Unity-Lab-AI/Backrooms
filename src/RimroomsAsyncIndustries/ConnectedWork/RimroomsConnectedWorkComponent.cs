using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Core;
using RimroomsAsyncIndustries.Portals;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// The branch's saved cross-map work state: every live work intent, the planning
    /// lease each one holds, and the bounded maintenance that keeps them honest.
    ///
    /// What this component is not: it is not a scheduler that pushes errands at
    /// pawns. Work is still chosen by Core, through ordinary WorkGivers, in the
    /// pawn's own priority and schedule order. This component only remembers what a
    /// worker committed to, so a trip that spans two maps and several native jobs
    /// survives the job boundaries, a save and a reload.
    ///
    /// A lease here coordinates this company's own planners and nothing else. It is
    /// not a native reservation, it excludes no native pawn, and it never travels to
    /// another map as a claim. Real custody starts when a real pawn picks the object
    /// up on the map that holds it.
    /// </summary>
    public sealed class RimroomsConnectedWorkComponent : GameComponent
    {
        private const int CurrentSchema = 1;

        /// <summary>Bounded saved growth. A refused plan is retried later, never queued.</summary>
        internal const int MaximumIntents = 64;

        /// <summary>
        /// Bounded saved growth for deployments. Lower than the intent cap on purpose: a
        /// deployment occupies a whole worker for as long as there is work to do, so a
        /// branch that had thirty-two people standing on other maps would have nobody
        /// left at home. The cap is a floor under that, not a scheduling policy.
        /// </summary>
        internal const int MaximumDeployments = 32;

        /// <summary>
        /// How long a plan stays valid before it is abandoned. A trip that has not
        /// progressed inside this window is stale by definition: the world it was
        /// planned against has moved on. Roughly three in-game hours.
        /// </summary>
        internal const int LeaseDurationTicks = 7500;

        /// <summary>
        /// How many crossing segments one intent may be handed before it is written
        /// off. This is the loop guard: a route that keeps being refused at the
        /// threshold must fail visibly instead of ordering the same walk forever.
        /// </summary>
        internal const int MaximumCrossAttempts = 8;

        /// <summary>How long before the same worker may run a planning pass again.</summary>
        internal const int PlanningCooldownTicks = 180;

        private const int MaintenanceInterval = 60;
        private const int MaximumCooldownEntries = 256;

        /// <summary>Bounded saved growth for allowed-area observations.</summary>
        internal const int MaximumAreaObservations = 256;

        /// <summary>
        /// How long a worker leaves a destination alone after a trip there failed.
        /// This stops a worker spending its whole day walking to a gate for a place
        /// that keeps refusing it, without ever hiding the destination permanently.
        /// </summary>
        internal const int DestinationRefusalTicks = 15000;

        private int schema = CurrentSchema;
        private long nextSequence = 1;
        private List<ConnectedWorkIntent> intents = new List<ConnectedWorkIntent>();
        private List<ConnectedDeploymentIntent> deployments = new List<ConnectedDeploymentIntent>();
        private List<ConnectedAreaObservation> areaObservations = new List<ConnectedAreaObservation>();
        private string stateFaultKey;

        // Transient. Planning throttles and topology cursors own no game object and
        // are deliberately not saved; they are rebuilt from nothing after a load.
        private readonly Dictionary<string, int> planningCooldown =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> destinationRefusal =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly ConnectedRouteService routes = new ConnectedRouteService();

        public RimroomsConnectedWorkComponent(Game game) { }

        public string StateFaultKey { get { return stateFaultKey; } }
        public IReadOnlyList<ConnectedWorkIntent> Intents { get { return intents.AsReadOnly(); } }
        public IReadOnlyList<ConnectedDeploymentIntent> Deployments { get { return deployments.AsReadOnly(); } }
        public ConnectedRouteService Routes { get { return routes; } }
        public int LiveIntentCount { get { return intents.Count(intent => intent != null && intent.IsLive); } }
        public int LiveDeploymentCount
        { get { return deployments.Count(deployment => deployment != null && deployment.IsLive); } }

        private RimroomsCampaignComponent Campaign
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }
        private RimroomsPortalNetwork Network
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); } }
        private RimroomsPortalCrossingService Crossings
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalCrossingService>(); } }

        /// <summary>
        /// Whether cross-map work may be planned or continued at all right now. A
        /// faulted save, a faulted network or a faulted crossing service disables the
        /// whole layer rather than letting it operate on state it cannot trust.
        /// </summary>
        public bool CanOperate
        {
            get
            {
                RimroomsCampaignComponent campaign = Campaign;
                RimroomsPortalNetwork network = Network;
                RimroomsPortalCrossingService crossings = Crossings;
                return stateFaultKey == null && schema == CurrentSchema && campaign != null &&
                    campaign.CanOperate && network != null && !network.HasStateFault &&
                    crossings != null && crossings.StateFaultKey == null;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schema, "rr_connectedWorkSchema", CurrentSchema, forceSave: true);
            Scribe_Values.Look(ref nextSequence, "rr_connectedWorkNextSequence", 1L);
            Scribe_Collections.Look(ref intents, "rr_connectedWorkIntents", LookMode.Deep);
            // Additive; absent from every save before travel-to-work, which correctly
            // loads as "nobody is deployed". No schema bump, so older saves load as they
            // are, exactly like the area observations added before this.
            Scribe_Collections.Look(ref deployments, "rr_connectedWorkDeployments", LookMode.Deep);
            // Additive; absent from a 0.5.0-dev save, which correctly loads as "no
            // observations yet" and therefore as unrestricted everywhere, matching
            // Core's own default. No schema bump, so older saves are not rejected.
            Scribe_Collections.Look(ref areaObservations, "rr_connectedWorkAreaObservations", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                intents = intents ?? new List<ConnectedWorkIntent>();
                deployments = deployments ?? new List<ConnectedDeploymentIntent>();
                areaObservations = areaObservations ?? new List<ConnectedAreaObservation>();
                // A removed area or unloaded map leaves a useless row behind.
                areaObservations.RemoveAll(observation => observation == null ||
                    string.IsNullOrEmpty(observation.PawnLoadId) || observation.Map == null);
                routes.Clear();
                planningCooldown.Clear();
                destinationRefusal.Clear();
                ValidateSavedState();
            }
        }

        // ----- queries -----

        /// <summary>The one live intent this worker owns, if any. A worker never holds two.</summary>
        public ConnectedWorkIntent ActiveIntentFor(Pawn pawn)
        {
            return pawn == null ? null
                : intents.FirstOrDefault(intent => intent != null && intent.IsLive && intent.Pawn == pawn);
        }

        /// <summary>
        /// The one live deployment this worker owns, if any. A worker never holds two,
        /// and never holds a deployment and a carry trip at the same time.
        /// </summary>
        public ConnectedDeploymentIntent ActiveDeploymentFor(Pawn pawn)
        {
            return pawn == null ? null : deployments.FirstOrDefault(
                deployment => deployment != null && deployment.IsLive && deployment.Pawn == pawn);
        }

        /// <summary>
        /// Whether this worker already owes this company a cross-map commitment of any
        /// kind. One chokepoint for the rule, so a family added later cannot forget it:
        /// a worker promised two things would abandon one of them, and which one it
        /// abandoned would depend on job-search timing rather than on anything designed.
        /// </summary>
        public bool HasLiveCommitment(Pawn pawn)
        { return ActiveIntentFor(pawn) != null || ActiveDeploymentFor(pawn) != null; }

        /// <summary>
        /// How much of this exact object this company's own planners have already
        /// promised to someone. Native pawns are unaffected by this number; it exists
        /// only so two of our own plans cannot both count on the same stack.
        /// </summary>
        public int LeasedCount(Thing thing)
        {
            if (thing == null) { return 0; }
            int total = 0;
            foreach (ConnectedWorkIntent intent in intents)
            {
                if (intent != null && intent.HoldsLease && intent.SourceThing == thing)
                { total += intent.RequestedCount; }
            }
            return total;
        }

        /// <summary>
        /// Write down this worker's allowed area for the map it is standing on right
        /// now. Cheap, and the only legitimate moment the answer is observable.
        /// </summary>
        public void ObserveAreaHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.playerSettings == null) { return; }
            if (!pawn.playerSettings.SupportsAllowedAreas) { return; }
            Area here = pawn.playerSettings.EffectiveAreaRestrictionInPawnCurrentMap;
            string loadId = pawn.GetUniqueLoadID();
            int tick = Find.TickManager.TicksGame;
            for (int index = 0; index < areaObservations.Count; index++)
            {
                ConnectedAreaObservation existing = areaObservations[index];
                if (existing == null || existing.Map != pawn.Map || existing.PawnLoadId != loadId) { continue; }
                existing.Update(here, tick);
                return;
            }
            if (areaObservations.Count >= MaximumAreaObservations)
            {
                // Drop the least recently confirmed row rather than refusing to learn.
                int oldest = 0;
                for (int index = 1; index < areaObservations.Count; index++)
                {
                    if (areaObservations[index].ObservedTick < areaObservations[oldest].ObservedTick)
                    { oldest = index; }
                }
                areaObservations.RemoveAt(oldest);
            }
            areaObservations.Add(new ConnectedAreaObservation(pawn, pawn.Map, here, tick));
        }

        /// <summary>
        /// Whether a cell on a map the worker is not standing on is inside that
        /// worker's allowed area there, as far as we have ever been able to observe.
        /// An unobserved map answers true, for the same reason Core answers
        /// unrestricted for a map no area was ever set on.
        ///
        /// This is deliberately an observation and not a guarantee. The definitive
        /// per-pawn check still runs on arrival; this only stops us planning trips we
        /// already have evidence the worker will be turned away from.
        /// </summary>
        public bool ObservedAreaAllows(Pawn pawn, Map map, IntVec3 cell)
        {
            if (pawn == null || map == null) { return true; }
            string loadId = pawn.GetUniqueLoadID();
            for (int index = 0; index < areaObservations.Count; index++)
            {
                ConnectedAreaObservation observation = areaObservations[index];
                if (observation == null || observation.Map != map || observation.PawnLoadId != loadId) { continue; }
                return observation.Allows(cell);
            }
            return true;
        }

        /// <summary>Leave a destination alone for a while after a trip there failed.</summary>
        public void NoteDestinationRefused(Pawn pawn, Map map)
        {
            if (pawn == null || map == null) { return; }
            if (destinationRefusal.Count >= MaximumCooldownEntries) { destinationRefusal.Clear(); }
            destinationRefusal[RefusalKey(pawn, map)] =
                Find.TickManager.TicksGame + DestinationRefusalTicks;
        }

        public bool DestinationRecentlyRefused(Pawn pawn, Map map)
        {
            if (pawn == null || map == null) { return false; }
            int readyTick;
            return destinationRefusal.TryGetValue(RefusalKey(pawn, map), out readyTick) &&
                Find.TickManager.TicksGame < readyTick;
        }

        private static string RefusalKey(Pawn pawn, Map map)
        { return pawn.GetUniqueLoadID() + "|" + map.uniqueID; }

        public bool MayPlanFor(Pawn pawn)
        {
            if (pawn == null) { return false; }
            int readyTick;
            return !planningCooldown.TryGetValue(pawn.GetUniqueLoadID(), out readyTick) ||
                Find.TickManager.TicksGame >= readyTick;
        }

        public void NotePlanningPass(Pawn pawn)
        {
            if (pawn == null) { return; }
            if (planningCooldown.Count >= MaximumCooldownEntries) { planningCooldown.Clear(); }
            planningCooldown[pawn.GetUniqueLoadID()] = Find.TickManager.TicksGame + PlanningCooldownTicks;
        }

        // ----- mutation -----

        /// <summary>
        /// Open one intent and take its lease. Every argument is checked here rather
        /// than trusted from the adapter, so a future family cannot open something
        /// the saved state would not accept.
        /// </summary>
        public ConnectedWorkIntent Open(ConnectedWorkAdapter adapter, Pawn pawn, Thing sourceThing,
            Map storeMap, IntVec3 candidateStoreCell, int requestedCount, Thing finalTarget,
            PortalRouteStep plannedStep)
        {
            RimroomsCampaignComponent campaign = Campaign;
            RimroomsPortalNetwork network = Network;
            if (!CanOperate || adapter == null || pawn == null || sourceThing == null || storeMap == null ||
                requestedCount < 1 || nextSequence == long.MaxValue) { return null; }
            if (!sourceThing.Spawned || sourceThing.Destroyed || sourceThing.Map == null ||
                requestedCount > sourceThing.stackCount) { return null; }
            if (!campaign.OwnsMap(sourceThing.Map) || !campaign.OwnsMap(storeMap)) { return null; }
            if (HasLiveCommitment(pawn)) { return null; }
            if (LiveIntentCount >= MaximumIntents || intents.Count >= MaximumIntents * 2) { return null; }
            if (LeasedCount(sourceThing) + requestedCount > sourceThing.stackCount) { return null; }

            string id = campaign.BranchId + ":work:" + adapter.AdapterId + ":" + nextSequence;
            if (intents.Any(intent => intent != null && intent.Id == id)) { return null; }
            var created = new ConnectedWorkIntent(id, campaign.BranchId, adapter, pawn, sourceThing,
                storeMap, candidateStoreCell, requestedCount, finalTarget, plannedStep,
                network.TopologyRevision, Find.TickManager.TicksGame, LeaseDurationTicks);
            intents.Add(created);
            nextSequence++;
            ValidateSavedState();
            if (stateFaultKey != null)
            {
                // Never leave the branch faulted because of a record we just added.
                intents.Remove(created);
                nextSequence--;
                ValidateSavedState();
                return null;
            }
            return created;
        }

        /// <summary>
        /// Open one travel-to-work deployment. Every argument is checked here rather than
        /// trusted from the provider, for the same reason the carry families are: a future
        /// provider must not be able to open something the saved state would reject.
        ///
        /// There is no lease over an object here, because a deployment promises nothing to
        /// anyone about anything physical. It reserves only this worker's attention.
        /// </summary>
        public ConnectedDeploymentIntent OpenDeployment(ConnectedDeploymentProvider provider, Pawn pawn,
            Map destinationMap, PortalRouteStep plannedStep)
        {
            RimroomsCampaignComponent campaign = Campaign;
            RimroomsPortalNetwork network = Network;
            if (!CanOperate || provider == null || pawn == null || destinationMap == null ||
                nextSequence == long.MaxValue) { return null; }
            if (!pawn.Spawned || pawn.Map == null || pawn.Map == destinationMap) { return null; }
            if (!campaign.OwnsMap(pawn.Map) || !campaign.OwnsMap(destinationMap)) { return null; }
            if (HasLiveCommitment(pawn)) { return null; }
            if (LiveDeploymentCount >= MaximumDeployments ||
                deployments.Count >= MaximumDeployments * 2) { return null; }

            string id = campaign.BranchId + ":deploy:" + provider.ProviderId + ":" + nextSequence;
            if (deployments.Any(deployment => deployment != null && deployment.Id == id)) { return null; }
            var created = new ConnectedDeploymentIntent(id, campaign.BranchId, provider, pawn,
                destinationMap, plannedStep, network.TopologyRevision,
                Find.TickManager.TicksGame, LeaseDurationTicks);
            deployments.Add(created);
            nextSequence++;
            ValidateSavedState();
            if (stateFaultKey != null)
            {
                // Never leave the branch faulted because of a record we just added.
                deployments.Remove(created);
                nextSequence--;
                ValidateSavedState();
                return null;
            }
            return created;
        }

        /// <summary>
        /// The worker is standing on the map it was sent to, and there is still work of
        /// its kind there. Called on every job search while it is deployed, which is what
        /// keeps the record alive: a deployment does not run on a countdown once the
        /// worker has arrived, it runs on the work still being there.
        /// </summary>
        public void NoteArrival(ConnectedDeploymentIntent deployment)
        {
            if (deployment == null || !deployment.IsLive) { return; }
            if (deployment.Phase == ConnectedDeploymentPhase.Travelling)
            {
                deployment.RecordArrival(Find.TickManager.TicksGame, LeaseDurationTicks);
                return;
            }
            deployment.RenewLease(Find.TickManager.TicksGame, LeaseDurationTicks);
        }

        public void NoteCrossAttempt(ConnectedDeploymentIntent deployment)
        {
            if (deployment == null || !deployment.IsLive) { return; }
            deployment.NoteCrossAttempt();
            deployment.RenewLease(Find.TickManager.TicksGame, LeaseDurationTicks);
        }

        public void RenewLease(ConnectedDeploymentIntent deployment)
        {
            if (deployment == null || !deployment.IsLive) { return; }
            deployment.RenewLease(Find.TickManager.TicksGame, LeaseDurationTicks);
        }

        /// <summary>
        /// Close a deployment. Nothing physical happens, and in particular the worker is
        /// not moved: it stays exactly where it is standing, with its own needs and
        /// whatever local work it finds. Closing only ends this company's claim on its
        /// attention.
        /// </summary>
        public void Close(ConnectedDeploymentIntent deployment, ConnectedDeploymentPhase terminalPhase,
            string failureKey)
        {
            if (deployment == null || !deployment.IsLive) { return; }
            if (terminalPhase != ConnectedDeploymentPhase.Completed &&
                terminalPhase != ConnectedDeploymentPhase.Cancelled &&
                terminalPhase != ConnectedDeploymentPhase.Failed)
            { terminalPhase = ConnectedDeploymentPhase.Failed; }
            deployment.Close(terminalPhase, failureKey);
            if (terminalPhase == ConnectedDeploymentPhase.Failed && !string.IsNullOrEmpty(failureKey))
            {
                RimroomsCampaignComponent campaign = Campaign;
                if (campaign != null && campaign.CanOperate)
                {
                    campaign.RecordEvent("RR_Event_ConnectedWorkFailed", deployment.Id,
                        failureKey.Translate().ToString());
                }
            }
        }

        /// <summary>
        /// Record what was actually picked up. The observed object and count are read
        /// from the carry owner, never from the requested quantity, because a partial
        /// pickup legitimately splits the stack into a different object.
        /// </summary>
        public void NotePickup(ConnectedWorkIntent intent, Thing carried, int observedCount)
        {
            if (intent == null || !intent.IsLive || carried == null || observedCount < 1) { return; }
            intent.RecordPickup(carried, observedCount, Find.TickManager.TicksGame, LeaseDurationTicks);
        }

        public void NoteCrossAttempt(ConnectedWorkIntent intent)
        {
            if (intent == null || !intent.IsLive) { return; }
            intent.NoteCrossAttempt();
            intent.RenewLease(Find.TickManager.TicksGame, LeaseDurationTicks);
        }

        public void RenewLease(ConnectedWorkIntent intent)
        {
            if (intent == null || !intent.IsLive) { return; }
            intent.RenewLease(Find.TickManager.TicksGame, LeaseDurationTicks);
        }

        /// <summary>
        /// Close an intent. Nothing physical happens here: an object already picked up
        /// stays exactly where it is, in whatever hands or on whatever floor it is
        /// actually on. Closing only releases the planning lease and the continuation.
        /// </summary>
        public void Close(ConnectedWorkIntent intent, ConnectedWorkPhase terminalPhase, string failureKey)
        {
            if (intent == null || !intent.IsLive) { return; }
            if (terminalPhase != ConnectedWorkPhase.Completed && terminalPhase != ConnectedWorkPhase.Cancelled &&
                terminalPhase != ConnectedWorkPhase.Failed)
            { terminalPhase = ConnectedWorkPhase.Failed; }
            intent.Close(terminalPhase, failureKey);
            // A cancellation is ordinary replanning and is not worth the player's
            // attention. A failure means a committed trip did not finish, which is.
            if (terminalPhase == ConnectedWorkPhase.Failed && !string.IsNullOrEmpty(failureKey))
            {
                RimroomsCampaignComponent campaign = Campaign;
                if (campaign != null && campaign.CanOperate)
                { campaign.RecordEvent("RR_Event_ConnectedWorkFailed", intent.Id, failureKey.Translate().ToString()); }
            }
        }

        // ----- maintenance -----

        /// <summary>
        /// Push the player's work-giver priority preferences into the defs for this session.
        /// The startup pass already did this once, but a pawn caches its own giver order and
        /// the pawns of a loaded save did not exist then, so it is done again here where
        /// every pawn is present.
        /// </summary>
        public override void FinalizeInit()
        {
            base.FinalizeInit();
            ConnectedWorkPriorities.Apply(RimroomsMod.Settings);
        }

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            if (Find.TickManager.TicksGame % MaintenanceInterval != 0) { return; }
            if (stateFaultKey != null || schema != CurrentSchema) { return; }
            routes.DropStaleCursors();

            // Bounded by construction: the live sets can never exceed their caps, so one
            // full sweep per interval is a fixed cost, not a growing one.
            for (int index = 0; index < intents.Count; index++)
            {
                ConnectedWorkIntent intent = intents[index];
                if (intent == null || !intent.IsLive) { continue; }
                string failure = LiveFailureKey(intent);
                if (failure == null) { continue; }
                Close(intent, LifecyclePhaseFor(failure), failure);
            }
            if (intents.Count > 0)
            { intents.RemoveAll(intent => intent == null || !intent.IsLive); }

            // Deployments are swept the same way and for the same reason: a worker who
            // died, was captured, left the map or lost its provider must not leave a
            // record behind that silently blocks it from ever being planned again. This
            // sweep never asks a provider whether work remains — that question belongs to
            // the work giver, on the worker's own map, and asking it here for every
            // deployment every interval would be a real cost for no gain.
            for (int index = 0; index < deployments.Count; index++)
            {
                ConnectedDeploymentIntent deployment = deployments[index];
                if (deployment == null || !deployment.IsLive) { continue; }
                string failure = LiveFailureKey(deployment);
                if (failure == null) { continue; }
                Close(deployment, DeploymentPhaseFor(failure), failure);
            }
            if (deployments.Count > 0)
            { deployments.RemoveAll(deployment => deployment == null || !deployment.IsLive); }
        }

        /// <summary>
        /// A routine replan is a cancellation; a committed trip that broke is a
        /// failure. Only the second is worth telling the player about.
        /// </summary>
        internal static ConnectedWorkPhase LifecyclePhaseFor(string failureKey)
        {
            switch (failureKey)
            {
                case "RR_ConnectedWork_ObjectGone":
                case "RR_ConnectedWork_ObjectMoved":
                case "RR_ConnectedWork_WorkerUnavailable":
                case "RR_ConnectedWork_AdapterRetired":
                    return ConnectedWorkPhase.Cancelled;
                default:
                    return ConnectedWorkPhase.Failed;
            }
        }

        /// <summary>
        /// How a deployment ends. Almost nothing here is a failure, and that is honest
        /// rather than lenient: a deployment carries nothing, so a worker that went home,
        /// was drafted, or simply outlived its lease has lost nobody and dropped nothing.
        /// A route that kept being refused is the exception — that is a broken connection
        /// the player may want to know about.
        /// </summary>
        internal static ConnectedDeploymentPhase DeploymentPhaseFor(string failureKey)
        {
            switch (failureKey)
            {
                case "RR_ConnectedWork_RouteExhausted":
                case "RR_ConnectedWork_InvalidState":
                    return ConnectedDeploymentPhase.Failed;
                default:
                    return ConnectedDeploymentPhase.Cancelled;
            }
        }

        /// <summary>
        /// Why this live deployment can no longer be honoured, or null while it still can.
        /// A worker inside an unresolved crossing is deliberately left alone: the crossing
        /// service owns that person until its receipt is reconciled.
        /// </summary>
        public string LiveFailureKey(ConnectedDeploymentIntent deployment)
        {
            RimroomsCampaignComponent campaign = Campaign;
            if (deployment == null || !CanOperate || campaign == null ||
                deployment.BranchId != campaign.BranchId)
            { return "RR_ConnectedWork_InvalidState"; }

            ConnectedDeploymentProvider provider = ConnectedDeploymentProviders.Get(deployment.ProviderId);
            if (provider == null || provider.ProviderVersion != deployment.ProviderVersion)
            { return "RR_ConnectedWork_AdapterRetired"; }

            Pawn pawn = deployment.Pawn;
            if (pawn == null || pawn.Destroyed || pawn.Dead ||
                pawn.GetUniqueLoadID() != deployment.PawnLoadId)
            { return "RR_ConnectedWork_WorkerLost"; }
            if (!pawn.Spawned)
            {
                RimroomsPortalCrossingService crossings = Crossings;
                if (crossings != null && crossings.HasUnresolvedCrossing(pawn)) { return null; }
                return "RR_ConnectedWork_WorkerLost";
            }
            if (!campaign.OwnsMap(deployment.DestinationMap) || !campaign.OwnsMap(pawn.Map))
            { return "RR_ConnectedWork_MapUnavailable"; }
            if (deployment.CrossAttempts > MaximumCrossAttempts)
            { return "RR_ConnectedWork_RouteExhausted"; }

            if (deployment.Phase == ConnectedDeploymentPhase.Travelling)
            {
                if (Find.TickManager.TicksGame > deployment.LeaseExpiryTick)
                { return "RR_ConnectedWork_LeaseExpired"; }
                // Drafting, a mental state or being downed end a journey that has not
                // arrived yet. Nothing is lost by dropping it.
                if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null)
                { return "RR_ConnectedWork_WorkerUnavailable"; }
                return null;
            }

            // Deployed. A worker standing where it was sent needs no countdown, because
            // its being there is the whole point of the record — and a countdown would
            // expire it overnight while it slept beside an unfinished wall. What ends it
            // is leaving: if this person is no longer on that map, it went somewhere of
            // its own accord or was taken, and either way the deployment is over.
            if (pawn.Map != deployment.DestinationMap)
            { return "RR_ConnectedWork_WorkerDeparted"; }
            return null;
        }

        /// <summary>
        /// Why this live intent can no longer be honoured, or null while it still can.
        /// A worker inside an unresolved crossing is deliberately left alone: the
        /// crossing service owns that person until its receipt is reconciled.
        /// </summary>
        public string LiveFailureKey(ConnectedWorkIntent intent)
        {
            RimroomsCampaignComponent campaign = Campaign;
            if (intent == null || !CanOperate || campaign == null || intent.BranchId != campaign.BranchId)
            { return "RR_ConnectedWork_InvalidState"; }

            ConnectedWorkAdapter adapter = ConnectedWorkAdapters.Get(intent.AdapterId);
            if (adapter == null || adapter.AdapterVersion != intent.AdapterVersion)
            { return "RR_ConnectedWork_AdapterRetired"; }

            Pawn pawn = intent.Pawn;
            if (pawn == null || pawn.Destroyed || pawn.Dead || pawn.GetUniqueLoadID() != intent.PawnLoadId)
            { return "RR_ConnectedWork_WorkerLost"; }
            if (!pawn.Spawned)
            {
                RimroomsPortalCrossingService crossings = Crossings;
                if (crossings != null && crossings.HasUnresolvedCrossing(pawn)) { return null; }
                return "RR_ConnectedWork_WorkerLost";
            }
            if (!campaign.OwnsMap(intent.FetchMap) || !campaign.OwnsMap(intent.StoreMap) ||
                !campaign.OwnsMap(pawn.Map))
            { return "RR_ConnectedWork_MapUnavailable"; }
            if (Find.TickManager.TicksGame > intent.LeaseExpiryTick)
            { return "RR_ConnectedWork_LeaseExpired"; }
            if (intent.CrossAttempts > MaximumCrossAttempts)
            { return "RR_ConnectedWork_RouteExhausted"; }

            if (intent.Phase == ConnectedWorkPhase.Planned)
            {
                Thing source = intent.SourceThing;
                if (source == null || source.Destroyed || source.GetUniqueLoadID() != intent.SourceThingLoadId)
                { return "RR_ConnectedWork_ObjectGone"; }
                if (!source.Spawned || source.Map != intent.FetchMap)
                { return "RR_ConnectedWork_ObjectMoved"; }
                if (source.stackCount < 1) { return "RR_ConnectedWork_ObjectGone"; }
                // Drafting, a mental state or being downed ends a plan that has not
                // taken hold of anything yet. Nothing is lost by dropping it.
                if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null)
                { return "RR_ConnectedWork_WorkerUnavailable"; }
                return null;
            }

            Thing cargo = intent.Cargo;
            if (cargo == null || cargo.Destroyed || cargo.GetUniqueLoadID() != intent.CargoLoadId)
            { return "RR_ConnectedWork_CargoGone"; }
            // Once something is in hand the trip is only abandoned if the hands let
            // go. A drafted carrier is not a failure; the lease window bounds it.
            if (pawn.carryTracker == null || pawn.carryTracker.innerContainer == null ||
                !pawn.carryTracker.innerContainer.Contains(cargo))
            { return "RR_ConnectedWork_CargoDropped"; }
            return null;
        }

        private void ValidateSavedState()
        {
            stateFaultKey = null;
            if (schema != CurrentSchema || nextSequence < 1 || intents == null || deployments == null)
            { Fault(); return; }
            var ids = new HashSet<string>(StringComparer.Ordinal);
            var liveWorkers = new HashSet<string>(StringComparer.Ordinal);
            foreach (ConnectedWorkIntent intent in intents)
            {
                if (intent == null || string.IsNullOrWhiteSpace(intent.Id) || intent.Id.Length > 256 ||
                    !ids.Add(intent.Id) || string.IsNullOrEmpty(intent.BranchId) ||
                    string.IsNullOrEmpty(intent.AdapterId) || intent.AdapterVersion < 1 ||
                    !Enum.IsDefined(typeof(ConnectedWorkPhase), intent.Phase) || intent.RequestedCount < 1)
                { Fault(); return; }
                if (!intent.IsLive) { continue; }
                // A live intent must still name its worker, and one worker may never
                // own two of them; either would make the continuation ambiguous.
                if (intent.Pawn == null || string.IsNullOrEmpty(intent.PawnLoadId) ||
                    intent.Pawn.GetUniqueLoadID() != intent.PawnLoadId ||
                    !liveWorkers.Add(intent.PawnLoadId))
                { Fault(); return; }
                if (intent.Phase == ConnectedWorkPhase.Planned &&
                    (intent.SourceThing == null || string.IsNullOrEmpty(intent.SourceThingLoadId)))
                { Fault(); return; }
                if (intent.Phase == ConnectedWorkPhase.Carrying &&
                    (intent.Cargo == null || string.IsNullOrEmpty(intent.CargoLoadId) || intent.ObservedCount < 1))
                { Fault(); return; }
            }
            // Deployments share both sets with the intents above, deliberately. Ids must be
            // unique across everything this branch saved, and the one-live-commitment rule
            // has to hold *across* the two record kinds or a worker could load owing a
            // carry trip and a deployment at once, with no defined answer for which wins.
            foreach (ConnectedDeploymentIntent deployment in deployments)
            {
                if (deployment == null || string.IsNullOrWhiteSpace(deployment.Id) ||
                    deployment.Id.Length > 256 || !ids.Add(deployment.Id) ||
                    string.IsNullOrEmpty(deployment.BranchId) ||
                    string.IsNullOrEmpty(deployment.ProviderId) || deployment.ProviderVersion < 1 ||
                    !Enum.IsDefined(typeof(ConnectedDeploymentPhase), deployment.Phase))
                { Fault(); return; }
                if (!deployment.IsLive) { continue; }
                // A live deployment must still name its worker and the map it was sent to.
                // Note what is deliberately *not* required: a source object. That is the
                // whole reason this is a separate record instead of an exemption carved
                // into the intent check above, where a missing source object is a fault.
                if (deployment.Pawn == null || string.IsNullOrEmpty(deployment.PawnLoadId) ||
                    deployment.Pawn.GetUniqueLoadID() != deployment.PawnLoadId ||
                    !liveWorkers.Add(deployment.PawnLoadId) || deployment.DestinationMap == null)
                { Fault(); return; }
            }
        }

        private void Fault()
        {
            stateFaultKey = "RR_ConnectedWork_InvalidSave";
            Log.Error("[Rimrooms][ConnectedWork] Saved work intents failed integrity; " +
                "cross-map work is disabled. Preserve the original save.");
        }
    }
}
