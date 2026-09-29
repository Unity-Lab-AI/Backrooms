using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Adapters
{
    /// <summary>
    /// Bringing one of our own people home through a gate when they go down on the
    /// far side.
    ///
    /// This is the capability the owner named explicitly — people carried back through
    /// the opening — and until now no route reached it. `PortalTraversalPolicy` already
    /// permitted a carried passenger who is downed, dead or held prisoner, and the
    /// crossing already preserved one; what was missing was the work that would order
    /// the carry, and the bed the person is put in at the other end.
    ///
    /// Only one direction exists here, deliberately. You carry a casualty *out* of the
    /// Backrooms to a bed; you never carry one in. The destination is whatever map the
    /// worker is standing on, and only if that map actually has a bed for them, so this
    /// works from headquarters and from a staffed forward space alike without assuming
    /// which is which.
    ///
    /// Capture is deliberately not here. Core makes taking a downed stranger prisoner a
    /// player order rather than automatic work, and the owner's rule is explicit that
    /// people and monstrosities come back because a player directed it. Automatic work
    /// rescues our own; anything else is the player's call, through the ordinary
    /// crossing order that already exists.
    /// </summary>
    public sealed class ConnectedCasualtyAdapter : ConnectedWorkAdapter
    {
        internal const string TakeToBedJobDefName = "RR_ConnectedTakeToBed";

        /// <summary>They reached a bed. The trip did what it was for.</summary>
        internal const string ArrivedHomeKey = "RR_ConnectedWork_CasualtyHome";

        /// <summary>They came round on the way. Still a finished trip: they are here.</summary>
        internal const string RecoveredEnRouteKey = "RR_ConnectedWork_CasualtyRecovered";

        private const int MaximumCasualtiesPerMap = 12;
        private const int MaximumBedsExamined = 32;

        public override string AdapterId { get { return ConnectedWorkAdapters.CasualtyRescue; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_RescueLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            // Arriving without a bed, or arriving with someone who woke up on the way,
            // are both finished trips: the person is physically on this side, which is
            // the whole point. Ordinary local rescue takes it from there.
            return failureKey == ArrivedHomeKey || failureKey == RecoveredEnRouteKey
                ? ConnectedWorkPhase.Completed : base.TerminalPhaseFor(failureKey);
        }

        public override ConnectedWorkIntent TryPlan(Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (work == null || !work.CanOperate || campaign == null || pawn == null || !pawn.Spawned ||
                pawn.Map == null || pawn.carryTracker == null || !campaign.OwnsMap(pawn.Map))
            { return null; }
            // The gate rule, before any planning.
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }

            Map home = pawn.Map;
            // No point planning a rescue to a map with nowhere to put anyone.
            if (!AnyCandidateBed(home, pawn)) { return null; }

            List<Map> connected = ConnectedWorkScan.ConnectedMaps(campaign, home, pawn);
            for (int index = 0; index < connected.Count; index++)
            {
                Map other = connected[index];
                if (work.DestinationRecentlyRefused(pawn, other)) { continue; }
                PortalRouteStep step;
                bool pending;
                if (!work.Routes.TryNextStep(home, other, out step, out pending)) { continue; }

                // That map's own downed list, read explicitly. Core keeps this per map,
                // so asking the far map about its own casualties is legitimate.
                IReadOnlyList<Pawn> downed = other.mapPawns.SpawnedDownedPawns;
                int windowStart = ConnectedWorkScan.WindowStart(downed.Count, MaximumCasualtiesPerMap, pawn);
                int examined = 0;
                for (int position = windowStart; position < downed.Count; position++)
                {
                    if (examined >= MaximumCasualtiesPerMap) { break; }
                    examined++;
                    Pawn patient = downed[position];
                    if (!CandidateCasualty(patient, pawn, other, work, step)) { continue; }
                    ConnectedWorkIntent opened = work.Open(this, pawn, patient, home,
                        IntVec3.Invalid, 1, null, step);
                    if (opened != null) { return opened; }
                }
            }
            return null;
        }

        public override string RevalidateAtFetchSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Pawn patient = intent == null ? null : intent.SourceThing as Pawn;
            if (patient == null || patient.Destroyed || patient.Dead || !patient.Spawned || pawn == null ||
                patient.Map != pawn.Map || patient.GetUniqueLoadID() != intent.SourceThingLoadId)
            { return "RR_ConnectedWork_CasualtyGone"; }
            // Core's own precondition, asked on the map that actually holds them: wants
            // rescue, not forbidden to this worker, no enemy close by, reservable and
            // reachable. It deliberately does not require a bed, which is why it is the
            // right question here and the bed is a separate question at the other end.
            if (!HealthAIUtility.CanRescueNow(pawn, patient, false))
            { return "RR_ConnectedWork_CasualtyUnavailable"; }
            return null;
        }

        public override Job FetchJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Pawn patient = intent == null ? null : intent.SourceThing as Pawn;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.FetchJobDefName);
            if (definition == null || patient == null) { return null; }
            // The same physical pickup the hauling family uses. Core carries a downed
            // pawn with the ordinary carry toil, exactly as it carries a crate.
            Job job = JobMaker.MakeJob(definition, patient);
            job.count = 1;
            return job;
        }

        public override string RevalidateAtStoreSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Pawn patient = intent == null ? null : intent.Cargo as Pawn;
            if (patient == null || patient.Destroyed || pawn == null || pawn.carryTracker == null ||
                patient != pawn.carryTracker.CarriedThing ||
                patient.GetUniqueLoadID() != intent.CargoLoadId)
            { return "RR_ConnectedWork_CasualtyGone"; }
            // They came round while being carried. Nothing went wrong; put them down
            // here and let them walk. This is a completed trip, not a failure.
            if (!patient.Downed && !patient.Dead) { return RecoveredEnRouteKey; }

            // Now that the worker is standing on this map carrying them, the patient's
            // MapHeld *is* this map, so Core's bed search finally answers about the beds
            // that are actually here. Before the crossing it would have answered about
            // the far side, which is precisely why this is asked here and not there.
            Building_Bed bed = RestUtility.FindBedFor(patient, pawn, checkSocialProperness: false,
                ignoreOtherReservations: false, patient.GuestStatus);
            if (bed == null || bed.Destroyed || !bed.Spawned || bed.Map != pawn.Map ||
                bed.IsForbidden(pawn) || !pawn.CanReach(bed, PathEndMode.Touch, pawn.NormalMaxDanger()))
            { return ArrivedHomeKey; }
            intent.RecordResolvedTarget(bed);
            return null;
        }

        public override Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Pawn patient = intent == null ? null : intent.Cargo as Pawn;
            var bed = intent == null ? null : intent.FinalTarget as Building_Bed;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(TakeToBedJobDefName);
            if (definition == null || patient == null || bed == null || bed.Destroyed || !bed.Spawned ||
                bed.Map != pawn.Map)
            { return null; }
            Job job = JobMaker.MakeJob(definition, patient, bed);
            job.count = 1;
            return job;
        }

        // ----- candidate predicates, explicit about which map they ask about -----

        private static bool CandidateCasualty(Pawn patient, Pawn worker, Map fetchMap,
            RimroomsConnectedWorkComponent work, PortalRouteStep step)
        {
            if (patient == null || patient == worker || patient.Destroyed || patient.Dead ||
                !patient.Spawned || patient.Map != fetchMap)
            { return false; }
            // Our own people only. Core automates rescuing your own faction and leaves
            // anyone else to a player order; the owner's rule says the same thing.
            if (patient.Faction != Faction.OfPlayer) { return false; }
            // Reads only the patient's own state, so it is a fair question about a map
            // nobody is standing on: downed, not already in a bed, not charging, not
            // deactivated.
            if (!HealthAIUtility.WantsToBeRescued(patient)) { return false; }
            if (patient.IsForbidden(Faction.OfPlayer)) { return false; }
            if (patient.Position.Fogged(fetchMap)) { return false; }
            // One worker per casualty: a lease on a person means the same thing it means
            // on a crate, and it excludes no native pawn from rescuing them locally.
            if (work.LeasedCount(patient) > 0) { return false; }
            if (!work.ObservedAreaAllows(worker, fetchMap, patient.Position)) { return false; }
            if (step != null && step.Destination != null &&
                !work.ObservedAreaAllows(worker, step.Destination.Map, step.Destination.ApproachCell))
            { return false; }
            return true;
        }

        /// <summary>
        /// Whether this map plausibly has a bed for a casualty. Explicit and local to the
        /// map asked about, because Core's own bed search answers about the sleeper's
        /// current map and would answer about the wrong side here. The real decision is
        /// made on arrival.
        /// </summary>
        private static bool AnyCandidateBed(Map map, Pawn worker)
        {
            if (map == null) { return false; }
            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            int examined = 0;
            for (int index = 0; index < buildings.Count; index++)
            {
                if (examined >= MaximumBedsExamined) { break; }
                var bed = buildings[index] as Building_Bed;
                if (bed == null) { continue; }
                examined++;
                if (bed.Destroyed || !bed.Spawned || bed.ForPrisoners || bed.IsBurning()) { continue; }
                if (!bed.AnyUnoccupiedSleepingSlot) { continue; }
                if (worker != null && bed.IsForbidden(worker)) { continue; }
                return true;
            }
            return false;
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
