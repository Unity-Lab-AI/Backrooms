using System.Collections.Generic;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Offers the company's paperwork as ordinary work at any records desk.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"these tasks are auto in the pawns work jobs"*.
    /// So it is a work giver and not an order: the player sets a priority and the branch files its
    /// reports, or does not.
    ///
    /// ## It finds nothing most of the time, and that is the design
    ///
    /// `TryFindWriteUpWork` is false unless an accepted quest has an outstanding write-up **whose
    /// precondition is already met**, so a branch between jobs offers no paperwork at all and this
    /// costs one scan of the request line per desk. Same discipline `WorkGiver_RRReconditionGate`
    /// states for itself: *"the owner's direction was that pawns must not always be doing this."*
    ///
    /// ## And the desk is the only thing it looks for
    ///
    /// **Uncapped by design.** The owner asked for more than one — *"u can have more than one to have
    /// more than one pawn doing it as u can have multiple quests going"* — and
    /// `CanReserveSittableOrSpot` is what stops two colonists being sent to the same chair. So the
    /// number of desks the player built **is** the number of pawns that can write at once, with no
    /// rule anywhere to tune.
    /// </summary>
    public sealed class WorkGiver_RRWriteUp : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        { get { return ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial); } }

        public override PathEndMode PathEndMode { get { return PathEndMode.InteractionCell; } }

        /// <summary>
        /// Every records desk on this pawn's map, and only while there is something to write.
        ///
        /// **The cheap question is asked first.** Whether the branch owes any paperwork is one scan
        /// of the request line; whether a desk is free is a reservation check per desk. Asking the
        /// branch-wide question before enumerating buildings means a colony with nothing outstanding
        /// never walks the building list at all.
        /// </summary>
        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            if (pawn == null || pawn.Map == null) { yield break; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { yield break; }
            RequestRecord request;
            RimroomsWriteUpDef kind;
            if (!campaign.TryFindWriteUpWork(out request, out kind)) { yield break; }
            ThingDef desk = DefDatabase<ThingDef>.GetNamedSilentFail("RR_RecordsDesk");
            if (desk == null) { yield break; }
            List<Thing> desks = pawn.Map.listerThings.ThingsOfDef(desk);
            for (int index = 0; index < desks.Count; index++)
            {
                if (desks[index] != null) { yield return desks[index]; }
            }
        }

        private Job FindWriteUpJob(Pawn pawn, Thing thing, bool forced)
        {
            if (pawn == null || thing == null || thing.def == null
                || thing.def.defName != "RR_RecordsDesk" || !thing.Spawned)
            { return null; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return null; }
            RequestRecord request;
            RimroomsWriteUpDef kind;
            if (!campaign.TryFindWriteUpWork(out request, out kind)) { return null; }
            if (!pawn.CanReserveAndReach(thing, PathEndMode.InteractionCell, Danger.Some, 1, -1,
                    null, forced)
                || !pawn.CanReserveSittableOrSpot(thing.InteractionCell, forced))
            { return null; }
            // **Asked before the job is offered, not only inside it.** A starving pawn would
            // otherwise take the job, fail out on its first tick and be offered it again, which
            // reads to a player as a colonist twitching at a desk. The job's own floor stays
            // exactly where it is; this stops the offer being made.
            if (GateWatch.MustLeave(pawn)) { return null; }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail("RR_WriteUp");
            return definition == null ? null : JobMaker.MakeJob(definition, thing);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return FindWriteUpJob(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return FindWriteUpJob(pawn, t, forced); }
    }
}
