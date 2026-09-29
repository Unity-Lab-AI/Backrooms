using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
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

        private int schema = CurrentSchema;
        private long nextSequence = 1;
        private List<ConnectedWorkIntent> intents = new List<ConnectedWorkIntent>();
        private string stateFaultKey;

        // Transient. Planning throttles and topology cursors own no game object and
        // are deliberately not saved; they are rebuilt from nothing after a load.
        private readonly Dictionary<string, int> planningCooldown =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly ConnectedRouteService routes = new ConnectedRouteService();

        public RimroomsConnectedWorkComponent(Game game) { }

        public string StateFaultKey { get { return stateFaultKey; } }
        public IReadOnlyList<ConnectedWorkIntent> Intents { get { return intents.AsReadOnly(); } }
        public ConnectedRouteService Routes { get { return routes; } }
        public int LiveIntentCount { get { return intents.Count(intent => intent != null && intent.IsLive); } }

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
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                intents = intents ?? new List<ConnectedWorkIntent>();
                routes.Clear();
                planningCooldown.Clear();
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
            if (ActiveIntentFor(pawn) != null) { return null; }
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

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            if (Find.TickManager.TicksGame % MaintenanceInterval != 0) { return; }
            if (stateFaultKey != null || schema != CurrentSchema) { return; }
            routes.DropStaleCursors();
            if (intents.Count == 0) { return; }

            // Bounded by construction: the live set can never exceed MaximumIntents,
            // so one full sweep per interval is a fixed cost, not a growing one.
            for (int index = 0; index < intents.Count; index++)
            {
                ConnectedWorkIntent intent = intents[index];
                if (intent == null || !intent.IsLive) { continue; }
                string failure = LiveFailureKey(intent);
                if (failure == null) { continue; }
                Close(intent, LifecyclePhaseFor(failure), failure);
            }
            intents.RemoveAll(intent => intent == null || !intent.IsLive);
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
            if (schema != CurrentSchema || nextSequence < 1 || intents == null)
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
        }

        private void Fault()
        {
            stateFaultKey = "RR_ConnectedWork_InvalidSave";
            Log.Error("[Rimrooms][ConnectedWork] Saved work intents failed integrity; " +
                "cross-map work is disabled. Preserve the original save.");
        }
    }
}
