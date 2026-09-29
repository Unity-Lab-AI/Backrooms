using RimroomsAsyncIndustries.Portals;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// Where one cross-map deployment stands. Only Travelling and Deployed are live;
    /// the rest are terminal.
    ///
    /// Unlike a work intent's phases, these two are not two halves of a fetch. A
    /// deployment has no cargo and no delivery: it is one worker going somewhere
    /// because qualifying work exists there, and then simply being there.
    /// </summary>
    public enum ConnectedDeploymentPhase
    {
        Travelling = 0,
        Deployed = 1,
        Completed = 2,
        Cancelled = 3,
        Failed = 4
    }

    /// <summary>
    /// One saved travel-to-work deployment: a worker, the map it is going to, and the
    /// work type that justified sending it.
    ///
    /// Every work family built so far is fetch → carry → deliver, and each is an
    /// adapter over <see cref="ConnectedWorkIntent"/>. Work done *at* the far site with
    /// nothing carried — finishing a frame, and later research, tending in place and
    /// every other stationary family — is a different shape, so it gets a different
    /// record rather than an exemption carved into that one.
    ///
    /// This is deliberately a sibling record and not a new phase on the work intent.
    /// A work intent's integrity check requires a real source object while planning and
    /// a real carried object while carrying; those two rules are what protect the three
    /// shipped families from loading a half-formed trip. Exempting a deployment from
    /// them would weaken the guard for everyone, and the exemption would be invisible.
    /// Everything a deployment actually shares with a work intent — the planning
    /// cooldown, the destination refusal memory, the bounded route cursors, the single
    /// crossing job, the traversal policy — lives on the component and the work giver,
    /// not on the record, so a sibling duplicates nothing but an expiry tick.
    ///
    /// What the record is *for*: a worker that crossed a gate to build must not be
    /// planned into a haul back home on the very next job search. The deployment is the
    /// memory that says "this person is over there on purpose." It never issues the
    /// work itself — Core's own local work giver does that, on the map the worker is
    /// now standing on, where every native check means what it says.
    /// </summary>
    public sealed class ConnectedDeploymentIntent : IExposable
    {
        private string id;
        private string branchId;
        private string providerId;
        private int providerVersion;

        private Pawn pawn;
        private string pawnLoadId;

        // Where the worker was sent. There is deliberately no saved reference to the
        // one object that justified the trip: the deployment lasts as long as *any*
        // qualifying work remains there, so keying it to a single frame would end it
        // the moment that frame finished, which is the opposite of what is wanted.
        private Map destinationMap;
        private string workTypeDefName;

        private string connectionId;
        private string openingId;
        private long topologyRevision;

        private ConnectedDeploymentPhase phase;
        private string failureKey;
        private int openedTick;
        private int arrivedTick;
        private int leaseExpiryTick;
        private int crossAttempts;

        public string Id { get { return id; } }
        public string BranchId { get { return branchId; } }
        public string ProviderId { get { return providerId; } }
        public int ProviderVersion { get { return providerVersion; } }
        public Pawn Pawn { get { return pawn; } }
        public string PawnLoadId { get { return pawnLoadId; } }
        public Map DestinationMap { get { return destinationMap; } }
        public string WorkTypeDefName { get { return workTypeDefName; } }
        public string ConnectionId { get { return connectionId; } }
        public string OpeningId { get { return openingId; } }
        public long TopologyRevision { get { return topologyRevision; } }
        public ConnectedDeploymentPhase Phase { get { return phase; } }
        public string FailureKey { get { return failureKey; } }
        public int OpenedTick { get { return openedTick; } }
        public int ArrivedTick { get { return arrivedTick; } }
        public int LeaseExpiryTick { get { return leaseExpiryTick; } }
        public int CrossAttempts { get { return crossAttempts; } }

        public bool IsLive
        {
            get
            {
                return phase == ConnectedDeploymentPhase.Travelling ||
                    phase == ConnectedDeploymentPhase.Deployed;
            }
        }

        public ConnectedDeploymentIntent() { }

        internal ConnectedDeploymentIntent(string id, string branchId, ConnectedDeploymentProvider provider,
            Pawn pawn, Map destinationMap, PortalRouteStep plannedStep, long topologyRevision,
            int tick, int leaseTicks)
        {
            this.id = id;
            this.branchId = branchId;
            providerId = provider.ProviderId;
            providerVersion = provider.ProviderVersion;
            this.pawn = pawn;
            pawnLoadId = pawn.GetUniqueLoadID();
            this.destinationMap = destinationMap;
            WorkTypeDef workType = provider.WorkType;
            workTypeDefName = workType == null ? null : workType.defName;
            if (plannedStep != null && plannedStep.Connection != null)
            {
                connectionId = plannedStep.Connection.Id;
                openingId = plannedStep.Connection.OpeningId;
            }
            this.topologyRevision = topologyRevision;
            phase = ConnectedDeploymentPhase.Travelling;
            openedTick = tick;
            leaseExpiryTick = tick + leaseTicks;
        }

        internal void RenewLease(int tick, int leaseTicks) { leaseExpiryTick = tick + leaseTicks; }

        /// <summary>
        /// The worker is standing on the map it was sent to. From here the deployment
        /// issues nothing at all: it only keeps this person from being planned into
        /// another cross-map trip while there is still work here to do.
        /// </summary>
        internal void RecordArrival(int tick, int leaseTicks)
        {
            phase = ConnectedDeploymentPhase.Deployed;
            arrivedTick = tick;
            RenewLease(tick, leaseTicks);
        }

        internal void NoteCrossAttempt() { crossAttempts++; }

        internal void Close(ConnectedDeploymentPhase terminalPhase, string key)
        {
            phase = terminalPhase;
            failureKey = key;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "id");
            Scribe_Values.Look(ref branchId, "branchId");
            Scribe_Values.Look(ref providerId, "providerId");
            Scribe_Values.Look(ref providerVersion, "providerVersion", 0);
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_Values.Look(ref pawnLoadId, "pawnLoadId");
            Scribe_References.Look(ref destinationMap, "destinationMap");
            Scribe_Values.Look(ref workTypeDefName, "workTypeDefName");
            Scribe_Values.Look(ref connectionId, "connectionId");
            Scribe_Values.Look(ref openingId, "openingId");
            Scribe_Values.Look(ref topologyRevision, "topologyRevision", 0L);
            Scribe_Values.Look(ref phase, "phase", ConnectedDeploymentPhase.Travelling);
            Scribe_Values.Look(ref failureKey, "failureKey");
            Scribe_Values.Look(ref openedTick, "openedTick", 0);
            Scribe_Values.Look(ref arrivedTick, "arrivedTick", 0);
            Scribe_Values.Look(ref leaseExpiryTick, "leaseExpiryTick", 0);
            Scribe_Values.Look(ref crossAttempts, "crossAttempts", 0);
        }
    }
}
