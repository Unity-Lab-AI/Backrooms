using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// How a further natural gate is actually found in play.
    ///
    /// Everything this needs already existed: the deterministic discovered-coordinate
    /// API, natural-edge registration, and the coordinate/seed owner that recalls a
    /// saved space instead of rebuilding it. What was missing was the trigger — the
    /// moment in the game where one of this company's people looks at a doorway deeper
    /// in and records that it leads somewhere new. Without it the permanently-open
    /// natural half of the design was unreachable except by the player wiring an
    /// address by hand, and a deterministic coordinate API sat with no caller at all.
    ///
    /// Bounded, and deliberately so. A frontier is a property of the doorway's own
    /// position under the coordinate's own saved seed, so the same doorway is always
    /// the same answer: reopening a known space never rerolls what it leads to. At
    /// most <see cref="MaximumFrontiersPerCoordinate"/> gates are ever found on one
    /// coordinate, and the campaign's own coordinate cap bounds the whole graph. This
    /// propagates further spaces without preallocating infinity, which is exactly what
    /// the contract asks for.
    ///
    /// This finds a *way through*. It does not generate inhabitants, encounters or
    /// pressure; what waits on the other side is the escalation ladder's business.
    /// </summary>
    public static class NaturalFrontierService
    {
        public const string SurveyJobDefName = "RR_SurveyFrontier";

        /// <summary>
        /// How many natural gates may ever be found on one coordinate. Raising this is
        /// a design decision, not a tuning knob; the cap is what keeps a chain of
        /// spaces finite.
        /// </summary>
        internal const int MaximumFrontiersPerCoordinate = 2;

        /// <summary>
        /// Roughly one doorway in this many is a frontier. Combined with the cap above,
        /// a space with many doors still yields at most two ways onward.
        /// </summary>
        internal const int FrontierRarity = 12;

        /// <summary>
        /// Whether this doorway is one that leads onward and has not been recorded yet.
        /// Pure and side-effect free: it generates nothing and records nothing, so it
        /// is safe to ask about every door on a map during work scanning.
        /// </summary>
        public static bool IsFrontierCandidate(Thing door)
        {
            CoordinateRecord source;
            return Evaluate(door, out source) == null;
        }

        /// <summary>
        /// Record this doorway as a permanently open natural gate to a further space.
        /// Idempotent: the coordinate id and seed are derived, and both the campaign
        /// record and the graph edge answer "already exists" on a replay rather than
        /// creating a second one.
        /// </summary>
        public static CompanyActionResult Discover(Thing door)
        {
            CoordinateRecord source;
            string refusal = Evaluate(door, out source);
            if (refusal != null) { return CompanyActionResult.Refused(refusal); }
            RimroomsCampaignComponent campaign = Campaign();

            // Derived from the source coordinate and the doorway's own position, so a
            // replay of the same discovery resolves to the same space with the same
            // seed rather than inventing another one.
            string discoveryId = source.Id + ":frontier:" + door.Position.x + "," + door.Position.z;
            CoordinateRecord discovered;
            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, out discovered);
            if (!created.Success || discovered == null) { return created; }

            CompanyActionResult registered = PortalAddressService.RegisterNaturalAddress(
                door, PortalAddressService.ApproachCellFor(door), discovered);
            if (registered.Success && !registered.AlreadyApplied)
            { campaign.RecordEvent("RR_Event_FrontierDiscovered", discovered.Id, source.Id); }
            return registered;
        }

        /// <summary>The label of the space a recorded frontier leads to, for player text.</summary>
        public static string DiscoveredLabelFor(CoordinateRecord discovered)
        {
            if (discovered == null) { return string.Empty; }
            return string.IsNullOrEmpty(discovered.Label) ? discovered.Id : discovered.Label;
        }

        /// <summary>
        /// One evaluation used by both the predicate and the action, so the thing a
        /// worker was sent to survey cannot differ from the thing that gets recorded.
        /// Returns a keyed refusal, or null when the doorway is a live candidate.
        /// </summary>
        private static string Evaluate(Thing door, out CoordinateRecord source)
        {
            source = null;
            RimroomsCampaignComponent campaign = Campaign();
            RimroomsPortalNetwork network = Network();
            if (campaign == null || !campaign.CanOperate || network == null || network.HasStateFault)
            { return "RR_Frontier_Unavailable"; }
            if (!(door is Building_Door) || !door.Spawned || door.Destroyed || door.Map == null ||
                !campaign.OwnsMap(door.Map))
            { return "RR_Frontier_NotADoorway"; }

            // Only deeper in. Headquarters has a machine for this; the Backrooms is
            // where a doorway can simply lead somewhere else.
            RimroomsDestinationMapParent site = door.Map.Parent as RimroomsDestinationMapParent;
            if (site == null || !site.LayoutReady) { return "RR_Frontier_NotInTheBackrooms"; }
            CoordinateRecord record = campaign.Coordinates.FirstOrDefault(candidate => candidate != null &&
                candidate.Site == site && candidate.Id == site.CoordinateId);
            if (record == null) { return "RR_Frontier_NotInTheBackrooms"; }
            // The way home is never a frontier.
            if (door == site.ReturnAnchor) { return "RR_Frontier_IsTheWayBack"; }

            IntVec3 approach = PortalAddressService.ApproachCellFor(door);
            if (!PortalAddressService.UsableThreshold(door, approach, door.Map))
            { return "RR_Frontier_Obstructed"; }

            IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
            int foundHere = 0;
            for (int index = 0; index < edges.Count; index++)
            {
                PortalConnectionRecord edge = edges[index];
                if (edge == null || edge.First == null || edge.Second == null) { continue; }
                if (edge.First.Anchor == door || edge.Second.Anchor == door)
                { return "RR_Frontier_AlreadyRecorded"; }
                if (edge.Kind == PortalConnectionKind.Natural && edge.First.Map == door.Map) { foundHere++; }
            }
            if (foundHere >= MaximumFrontiersPerCoordinate) { return "RR_Frontier_NoneLeftHere"; }

            // The draw is over the doorway's position under this coordinate's own saved
            // seed. Position is stable for the life of the space, so the answer never
            // changes on a reload or a revisit.
            int draw = CampaignSeed.Derive(record.Seed,
                "frontier:" + door.Position.x + "," + door.Position.z, 1);
            if (draw % FrontierRarity != 0) { return "RR_Frontier_LeadsNowhere"; }

            source = record;
            return null;
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }
    }

    /// <summary>
    /// Offers the survey as ordinary work, so a doorway that leads onward is found by
    /// someone actually walking up to it and looking, in their own work order.
    /// </summary>
    public sealed class WorkGiver_SurveyFrontier : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        { get { return ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial); } }

        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }

        public override Danger MaxPathDanger(Pawn pawn) { return Danger.Some; }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            // Free on headquarters and on any map that has already given up all the
            // ways onward it has, which is the overwhelmingly common case.
            if (pawn == null || !pawn.Spawned || pawn.Map == null) { return true; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate || !campaign.OwnsMap(pawn.Map)) { return true; }
            RimroomsDestinationMapParent site = pawn.Map.Parent as RimroomsDestinationMapParent;
            if (site == null || !site.LayoutReady) { return true; }
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault) { return true; }
            int foundHere = network.Connections.Count(edge => edge != null && edge.First != null &&
                edge.Kind == PortalConnectionKind.Natural && edge.First.Map == pawn.Map);
            return foundHere >= NaturalFrontierService.MaximumFrontiersPerCoordinate;
        }

        private Job SurveyJob(Pawn pawn, Thing thing, bool forced)
        {
            if (!NaturalFrontierService.IsFrontierCandidate(thing)) { return null; }
            if (!pawn.CanReserveAndReach(thing, PathEndMode.Touch, pawn.NormalMaxDanger(), 1, -1, null, forced))
            { return null; }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(NaturalFrontierService.SurveyJobDefName);
            return definition == null ? null : JobMaker.MakeJob(definition, thing);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return SurveyJob(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return SurveyJob(pawn, t, forced); }
    }

    /// <summary>
    /// Walk to the doorway, study it, and record where it leads. The candidate check
    /// is re-asked throughout, so a doorway that stops qualifying mid-survey ends the
    /// job instead of recording something that is no longer true.
    /// </summary>
    public sealed class JobDriver_SurveyFrontier : JobDriver
    {
        private const int SurveyTicks = 600;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        { return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed); }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !NaturalFrontierService.IsFrontierCandidate(job.targetA.Thing));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil survey = Toils_General.Wait(SurveyTicks, TargetIndex.A);
            survey.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            survey.WithProgressBarToilDelay(TargetIndex.A);
            yield return survey;
            Toil record = ToilMaker.MakeToil("RR_SurveyFrontier");
            record.initAction = RecordDiscovery;
            record.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return record;
        }

        private void RecordDiscovery()
        {
            Thing door = job.targetA.Thing;
            CompanyActionResult result = NaturalFrontierService.Discover(door);
            if (result.Success && !result.AlreadyApplied)
            {
                Messages.Message("RR_Frontier_Discovered".Translate(pawn.LabelShortCap),
                    door, MessageTypeDefOf.PositiveEvent, false);
                return;
            }
            if (!result.Success && !string.IsNullOrEmpty(result.MessageKey))
            { Messages.Message(result.MessageKey.Translate(), door, MessageTypeDefOf.RejectInput, false); }
        }
    }
}
