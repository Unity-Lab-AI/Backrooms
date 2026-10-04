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
    /// Boarding up a natural portal: a pawn, some wood, and a map slot returned.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"and the closing of natural portals needs to be an option on the gate itself so pawns can
    /// close it with like 25 wood to board it up which makes it close its map freeing up a map
    /// from being open so others can be explored"*
    ///
    /// ## Why this is not a button
    ///
    /// Closing a place already existed — `CoordinateRelease.TryRelease`, reached from the
    /// Operations held-places pane. **The owner's complaint is where it lives**, and the same
    /// direction says so twice: *"everything that the machine needs to start up should be able to
    /// do in the worlkd from the devices themselfes with pawns controls and actrions not just in
    /// the opetaions tab"*. So this is a command on the door, a job a colonist walks over and
    /// does, and a real cost in material. A menu item that frees a map is bookkeeping; somebody
    /// nailing boards across a doorway is the game.
    ///
    /// ## Nothing here decides whether the place can close
    ///
    /// `CoordinateRelease.RefusalFor` is the authority on that and it already refuses a crew left
    /// inside, a crossing in flight and the headquarters. This asks it, adds the one condition
    /// that is its own — **is there the wood** — and then calls the same `TryRelease` the pane
    /// calls. Two derivations of one rule is the defect this project keeps meeting, and
    /// *"freeing up a map"* is far too consequential a place to meet it again.
    ///
    /// ## One way only
    ///
    /// There is no un-boarding, for the reason already recorded on `CompRimroomsEmergence`: owner,
    /// *"we do need to be able to close natural portals u just can not re open them"*, *"thats the
    /// whole 5 limit issue"*. A decision that can be undone is not a decision, and the budget it
    /// frees would mean nothing.
    /// </summary>
    internal static class PortalBoardUp
    {
        /// <summary>
        /// Wood a doorway takes to board up.
        ///
        /// Owner: *"with like 25 wood"*. Cheap on purpose — the cost is there so the act is a
        /// decision with a material consequence, not so it is an obstacle. A player who needs the
        /// map slot back should always be able to afford the slot back.
        /// </summary>
        internal const int WoodCost = 25;

        /// <summary>How long a colonist spends nailing it shut, at normal speed.</summary>
        internal const int BoardUpTicks = 420;

        internal const string JobDefName = "RR_BoardUpPortal";

        /// <summary>
        /// The coordinate this doorway currently leads to, or null.
        ///
        /// Read off the live portal network rather than from anything stored on the door, because
        /// the network is what `TryRelease` will walk to shelve the edges. A door that believed it
        /// led somewhere the network disagreed about is how a place becomes unreachable.
        /// </summary>
        internal static CoordinateRecord PlaceBehind(RimroomsCampaignComponent campaign, Thing door)
        {
            if (campaign == null || door == null) { return null; }
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault) { return null; }
            foreach (PortalConnectionRecord edge in network.Connections)
            {
                if (edge == null || string.IsNullOrEmpty(edge.CoordinateId)) { continue; }
                bool ours = (edge.First != null && edge.First.Anchor == door)
                    || (edge.Second != null && edge.Second.Anchor == door);
                if (!ours) { continue; }
                for (int index = 0; index < campaign.Coordinates.Count; index++)
                {
                    CoordinateRecord record = campaign.Coordinates[index];
                    if (record != null && record.Id == edge.CoordinateId) { return record; }
                }
            }
            return null;
        }

        /// <summary>
        /// Why this doorway cannot be boarded up, or null when it can.
        ///
        /// The release rules are asked, never restated. The wood is the one condition this owns.
        /// </summary>
        internal static string RefusalFor(RimroomsCampaignComponent campaign, Thing door)
        {
            CoordinateRecord place = PlaceBehind(campaign, door);
            if (place == null) { return "RR_BoardUp_LeadsNowhere"; }
            string refusal = CoordinateRelease.RefusalFor(campaign, place);
            if (refusal != null) { return refusal; }
            if (WoodOnMap(door.Map) < WoodCost) { return "RR_BoardUp_NoWood"; }
            return null;
        }

        /// <summary>Wood a colonist could actually fetch, which is not the same as wood present.</summary>
        internal static int WoodOnMap(Map map)
        {
            if (map == null) { return 0; }
            return map.resourceCounter == null
                ? 0 : map.resourceCounter.GetCount(ThingDefOf.WoodLog);
        }

        /// <summary>
        /// Send the nearest colonist who can reach both the wood and the doorway.
        ///
        /// **Ordered to somebody rather than queued as work.** The owner asked for it on the door,
        /// as a thing you tell somebody to do; a work giver would make it a background chore that
        /// closes a map when a hauler happens to get round to it, and closing a map is not a
        /// chore. `TryTakeOrderedJob` is the same route a player's right-click uses.
        /// </summary>
        internal static CompanyActionResult Order(RimroomsCampaignComponent campaign, Thing door)
        {
            string refusal = RefusalFor(campaign, door);
            if (refusal != null) { return CompanyActionResult.Refused(refusal); }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(JobDefName);
            if (definition == null) { return CompanyActionResult.Refused("RR_BoardUp_NoJobDef"); }

            Map map = door.Map;
            foreach (Pawn candidate in map.mapPawns.FreeColonistsSpawned
                .OrderBy(pawn => pawn.Position.DistanceToSquared(door.Position)))
            {
                if (candidate == null || candidate.Downed || candidate.Drafted) { continue; }
                if (candidate.WorkTagIsDisabled(WorkTags.ManualDumb)) { continue; }
                Thing wood = FindWood(candidate, map);
                if (wood == null) { continue; }
                if (!candidate.CanReach(door, PathEndMode.Touch, Danger.Deadly)) { continue; }
                var job = JobMaker.MakeJob(definition, door, wood);
                job.count = WoodCost;
                if (candidate.jobs.TryTakeOrderedJob(job, JobTag.Misc))
                { return CompanyActionResult.Applied(); }
            }
            return CompanyActionResult.Refused("RR_BoardUp_NobodyAvailable");
        }

        /// <summary>A reachable wood stack this pawn is allowed to take from.</summary>
        internal static Thing FindWood(Pawn pawn, Map map)
        {
            if (pawn == null || map == null) { return null; }
            return GenClosest.ClosestThingReachable(
                pawn.Position, map,
                ThingRequest.ForDef(ThingDefOf.WoodLog),
                PathEndMode.ClosestTouch,
                TraverseParms.For(pawn),
                9999f,
                candidate => candidate != null && !candidate.IsForbidden(pawn)
                    && pawn.CanReserve(candidate) && candidate.stackCount > 0);
        }

        /// <summary>
        /// Board it up: spend the carried wood and close the place.
        ///
        /// The wood goes **before** the release, so a refusal at the last moment cannot cost a
        /// player their material — and `TryRelease` is asked for its refusal first, so the
        /// ordinary case never gets that far.
        /// </summary>
        internal static CompanyActionResult Finish(RimroomsCampaignComponent campaign, Pawn pawn,
            Thing door)
        {
            string refusal = RefusalFor(campaign, door);
            if (refusal != null) { return CompanyActionResult.Refused(refusal); }
            CoordinateRecord place = PlaceBehind(campaign, door);
            if (place == null) { return CompanyActionResult.Refused("RR_BoardUp_LeadsNowhere"); }

            string released = CoordinateRelease.TryRelease(campaign, place);
            if (released != null) { return CompanyActionResult.Refused(released); }

            // Spent only once the place is actually closed. The other order would charge for a
            // refusal, and a player who paid twenty-five wood for nothing would be right to be
            // annoyed about it.
            Thing carried = pawn == null ? null : pawn.carryTracker.CarriedThing;
            if (carried != null && carried.def == ThingDefOf.WoodLog)
            {
                int spend = carried.stackCount < WoodCost ? carried.stackCount : WoodCost;
                carried.SplitOff(spend).Destroy(DestroyMode.Vanish);
            }
            return CompanyActionResult.Applied();
        }
    }

    /// <summary>
    /// Fetch the wood, walk to the doorway, and nail it shut.
    ///
    /// The release conditions are re-asked at the end rather than only at the start, because a
    /// crew can walk into the place while the boards are being carried across the map — and
    /// closing a map with somebody inside it is the one outcome this whole feature must never
    /// produce.
    /// </summary>
    public sealed class JobDriver_BoardUpPortal : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed)
                && pawn.Reserve(job.targetB, job, 1, PortalBoardUp.WoodCost, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOnDespawnedOrNull(TargetIndex.B);
            this.FailOnForbidden(TargetIndex.B);

            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil board = Toils_General.Wait(PortalBoardUp.BoardUpTicks, TargetIndex.A);
            board.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            board.WithProgressBarToilDelay(TargetIndex.A);
            yield return board;

            Toil close = ToilMaker.MakeToil("RR_BoardUpPortal");
            close.initAction = CloseThePlace;
            close.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return close;
        }

        private void CloseThePlace()
        {
            Thing door = job.targetA.Thing;
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            CompanyActionResult result = PortalBoardUp.Finish(campaign, pawn, door);
            if (result.Success)
            {
                Messages.Message("RR_BoardUp_Done".Translate(pawn.LabelShortCap),
                    door, MessageTypeDefOf.PositiveEvent, false);
                return;
            }
            if (!string.IsNullOrEmpty(result.MessageKey))
            {
                Messages.Message(result.MessageKey.Translate(), door,
                    MessageTypeDefOf.RejectInput, false);
            }
        }
    }
}
