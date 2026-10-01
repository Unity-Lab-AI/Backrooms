using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Ordinary travel through a remembered address. A person walks to the saved
    /// threshold and crosses; there is no crew list, manifest or dispatch. Opening
    /// a doorway normally never moves anyone.
    /// </summary>
    public static class PortalTravelService
    {
        public const string CrossJobDefName = "RR_CrossPortal";

        /// <summary>
        /// The directed step for one remembered address as seen from this map. Both
        /// endpoints can never be on one map, so the source side is unambiguous.
        /// </summary>
        public static PortalRouteStep StepFrom(PortalConnectionRecord connection, Map from)
        {
            if (connection == null || from == null || connection.First == null || connection.Second == null)
            { return null; }
            if (connection.First.Map == from && connection.Second.Map != from) { return new PortalRouteStep(connection, true); }
            if (connection.Second.Map == from && connection.First.Map != from) { return new PortalRouteStep(connection, false); }
            return null;
        }

        /// <summary>Remembered addresses whose near side is this map, in a stable order.</summary>
        public static List<PortalConnectionRecord> LocalAddresses(Map from)
        {
            RimroomsPortalNetwork network = Network();
            if (network == null || network.HasStateFault || from == null) { return new List<PortalConnectionRecord>(); }
            return network.Connections.Where(edge => edge != null && StepFrom(edge, from) != null)
                .OrderBy(edge => edge.CoordinateId).ThenBy(edge => edge.Id).ToList();
        }

        /// <summary>
        /// Order one person to walk to the saved threshold and cross. The crossing
        /// itself revalidates everything; this refuses early with the same reason.
        /// </summary>
        public static CompanyActionResult OrderCrossing(Pawn pawn, PortalConnectionRecord connection)
        {
            RimroomsCampaignComponent campaign = Campaign();
            RimroomsPortalNetwork network = Network();
            RimroomsPortalCrossingService crossings = Crossings();
            if (campaign == null || !campaign.CanOperate || network == null || network.HasStateFault ||
                crossings == null || crossings.StateFaultKey != null)
            { return CompanyActionResult.Refused("RR_PortalTravel_InvalidState"); }
            if (pawn == null || pawn.Map == null) { return CompanyActionResult.Refused("RR_PortalTravel_NoPerson"); }
            string eligibility = RimroomsPortalCrossingService.EligibilityFailureKey(pawn);
            if (eligibility != null) { return CompanyActionResult.Refused(eligibility); }
            if (crossings.HasUnresolvedCrossing(pawn))
            { return CompanyActionResult.Refused("RR_PortalCrossing_PawnInTransit"); }
            string fit = PortalTraversalPolicy.FitFailureKey(pawn, DoorwayWidth(connection));
            if (fit != null) { return CompanyActionResult.Refused(fit); }

            PortalRouteStep step = StepFrom(connection, pawn.Map);
            if (step == null || network.Find(connection.Id) != connection)
            { return CompanyActionResult.Refused("RR_PortalTravel_AddressUnavailable"); }
            PortalNetworkResult availability = network.ValidateRouteStep(step);
            if (availability != PortalNetworkResult.Success)
            {
                // **Ask the gate why before falling back to the generic text.** `Closed` covers
                // seven conditions, and the one the owner hit -- no stored charge -- read as an
                // address fault. A refusal that names the wrong thing is worse than a vague one,
                // because it sends somebody to fix something that is not broken.
                CompRimroomsGate blocked = connection.First == null || connection.First.Anchor == null
                    ? null : connection.First.Anchor.TryGetComp<CompRimroomsGate>();
                if (availability == PortalNetworkResult.Closed && blocked != null)
                {
                    string why = blocked.PortalWindowBlockerKey(connection.Id, connection.OpeningId);
                    if (why != null) { return CompanyActionResult.Refused(why); }
                }
                return CompanyActionResult.Refused(AvailabilityKey(availability));
            }
            if (!step.Source.ApproachCell.IsValid || !step.Source.ApproachCell.Standable(pawn.Map))
            { return CompanyActionResult.Refused("RR_PortalTravel_ApproachBlocked"); }
            if (!pawn.CanReach(step.Source.ApproachCell, PathEndMode.OnCell, Danger.Deadly))
            { return CompanyActionResult.Refused("RR_PortalTravel_Unreachable"); }

            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(CrossJobDefName);
            if (definition == null) { return CompanyActionResult.Refused("RR_PortalTravel_JobDefMissing"); }
            Job job = JobMaker.MakeJob(definition, step.Source.Anchor, step.Source.ApproachCell);
            job.count = 1;
            if (!pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc))
            { return CompanyActionResult.Refused("RR_PortalTravel_OrderRefused"); }
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// How wide the doorway of a connection is, in cells.
        ///
        /// Taken from the connection's **first** endpoint for every kind, which for a
        /// laboratory connection is the gate. A connection has one width in both directions:
        /// the gate is the machine that forms the aperture, and the doorway on the Backrooms
        /// side is just where you arrive. Measuring each end separately would let a pack
        /// animal walk in through a wide gate and then be unable to come home, because a
        /// generated return threshold is always an ordinary one-cell door.
        /// </summary>
        public static int DoorwayWidth(PortalConnectionRecord connection)
        {
            Thing anchor = connection == null || connection.First == null ? null : connection.First.Anchor;
            if (anchor == null) { return 1; }
            CompRimroomsGate gate = anchor.TryGetComp<CompRimroomsGate>();
            if (gate != null && gate.IsDesignated) { return gate.GateWidth; }
            if (anchor.def == null) { return 1; }
            int span = anchor.def.size.x > anchor.def.size.z ? anchor.def.size.x : anchor.def.size.z;
            return span < 1 ? 1 : span;
        }

        /// <summary>Reconcile one interrupted crossing. Never invents a person or item.</summary>
        public static CompanyActionResult RecoverCrossing(string operationId)
        {
            RimroomsPortalCrossingService crossings = Crossings();
            if (crossings == null) { return CompanyActionResult.Refused("RR_PortalTravel_InvalidState"); }
            PortalCrossingResult result = crossings.Recover(operationId);
            if (result.Success || result.AlreadyApplied) { return CompanyActionResult.Existing(); }
            return CompanyActionResult.Refused(result.FailureKey ?? "RR_PortalCrossing_InvalidState");
        }

        /// <summary>
        /// The emergency route home for a laboratory session: pay the physical
        /// recovery debit once and reopen the same saved session so people who are
        /// across can walk back. Nobody is teleported and no debit is duplicated.
        /// </summary>
        public static CompanyActionResult OrderEmergencyReturn(CompRimroomsGate gate)
        {
            if (gate == null || gate.HasPortalOwnerFault || string.IsNullOrEmpty(gate.PortalConnectionId) ||
                string.IsNullOrEmpty(gate.PortalOpeningId))
            { return CompanyActionResult.Refused("RR_PortalTravel_NoSession"); }
            if (!gate.IsAwaitingRecovery) { return CompanyActionResult.Refused("RR_Gate_RecoveryWindowStillActive"); }
            string operationId = gate.PortalConnectionId + ":emergency-return:" + gate.PortalOpeningId;
            return gate.RecoverPortalOpening(gate.PortalConnectionId, operationId);
        }

        /// <summary>Close a laboratory session deliberately. People already across stay there.</summary>
        public static CompanyActionResult CloseSession(CompRimroomsGate gate)
        {
            if (gate == null || string.IsNullOrEmpty(gate.PortalConnectionId))
            { return CompanyActionResult.Refused("RR_PortalTravel_NoSession"); }
            return gate.ClosePortalOpening(gate.PortalConnectionId);
        }

        internal static string AvailabilityKey(PortalNetworkResult result)
        {
            switch (result)
            {
                case PortalNetworkResult.Closed: return "RR_PortalTravel_SessionClosed";
                case PortalNetworkResult.Obstructed: return "RR_PortalTravel_ApproachBlocked";
                case PortalNetworkResult.InvalidEndpoint: return "RR_PortalTravel_EndpointMissing";
                case PortalNetworkResult.WrongBranch: return "RR_PortalCrossing_WrongBranch";
                default: return "RR_PortalTravel_AddressUnavailable";
            }
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }
        private static RimroomsPortalCrossingService Crossings()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalCrossingService>(); }
    }

    /// <summary>
    /// Walks the ordered person to the saved threshold cell, then performs exactly
    /// one crossing of the live edge. The edge is re-validated immediately before
    /// the move; a closed session ends the job instead of moving anyone.
    /// </summary>
    public sealed class JobDriver_CrossPortal : JobDriver
    {
        private string operationId;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref operationId, "rr_portalCrossingOperation");
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // The threshold cell is shared passage, not a reservable work spot.
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => CurrentStep() == null);
            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            Toil cross = ToilMaker.MakeToil("RR_CrossPortal");
            cross.initAction = delegate { PerformCrossing(); };
            cross.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return cross;
        }

        private PortalRouteStep CurrentStep()
        {
            Thing anchor = job.targetA.Thing;
            if (anchor == null || pawn.Map == null) { return null; }
            List<PortalRouteStep> candidates = PortalTravelService.LocalAddresses(pawn.Map)
                .Select(edge => PortalTravelService.StepFrom(edge, pawn.Map))
                .Where(step => step != null && step.Source.Anchor == anchor &&
                    step.Source.ApproachCell == job.targetB.Cell)
                .ToList();
            if (candidates.Count == 0) { return null; }
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null) { return null; }
            List<PortalRouteStep> available = candidates
                .Where(step => network.ValidateRouteStep(step) == PortalNetworkResult.Success).ToList();
            // Several remembered addresses may share one doorway; exactly one of
            // them can be open at a time, so an ambiguous order is refused.
            return available.Count == 1 ? available[0] : null;
        }

        private void PerformCrossing()
        {
            PortalRouteStep step = CurrentStep();
            RimroomsPortalCrossingService crossings = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalCrossingService>();
            if (step == null || crossings == null)
            {
                Report("RR_PortalTravel_AddressUnavailable");
                EndSafely();
                return;
            }
            if (string.IsNullOrEmpty(operationId))
            {
                operationId = step.Connection.Id + ":crossing:" + pawn.GetUniqueLoadID() + ":" + job.loadID;
            }
            PortalCrossingResult result = crossings.Cross(pawn, step, operationId);
            if (!result.Success && !string.IsNullOrEmpty(result.FailureKey)) { Report(result.FailureKey); }
            EndSafely();
        }

        private void Report(string key)
        {
            Messages.Message(key.Translate(), pawn, MessageTypeDefOf.RejectInput, false);
        }

        private void EndSafely()
        {
            // A completed crossing despawns and respawns the same person, which Core
            // already ends jobs for. Only end this job if it is still the current one.
            if (pawn.CurJob == job) { EndJobWith(JobCondition.Succeeded); }
        }
    }
}
