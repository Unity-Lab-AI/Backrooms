using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Investigation
{
    /// <summary>
    /// The three things a colonist can be told to do with a quest book.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"with a pawn click actions with sterp by step
    /// instructions how to use the journal but not wordy keep it very concise asnd to the point"*.
    ///
    /// The instruction block is a separate option and is always present; these three are the actions,
    /// and **each appears only when it can actually be taken.** An option that shows up greyed out
    /// with an explanation is a sentence the player reads on every right-click for the rest of the
    /// campaign, which is the opposite of *concise and to the point*.
    ///
    /// ## None of them invents a job
    ///
    /// *Write up here* is the same work giver's job, ordered rather than scheduled. *File in archive*
    /// and *Send to company* are Core hauling to a cell. **There is no fourth mechanism**, so a
    /// player who prefers to let work priorities handle everything gets the identical outcome more
    /// slowly, and nothing behaves differently because it was clicked.
    /// </summary>
    public sealed partial class CompRouteEvidence
    {
        private IEnumerable<FloatMenuOption> QuestBookOptions(Pawn selPawn)
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { yield break; }
            RequestRecord request = campaign.RequestById(stampedQuestId);
            if (request == null || request.Status != RequestStatus.Accepted) { yield break; }

            // ---------------------------------------------------------------- write up here
            RimroomsWriteUpDef next = campaign.NextWriteUp(request);
            ThingDef deskDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_RecordsDesk");
            if (next != null && deskDef != null && parent.Map != null)
            {
                Thing desk = NearestFreeDesk(selPawn, deskDef);
                JobDef writeUp = DefDatabase<JobDef>.GetNamedSilentFail("RR_WriteUp");
                if (desk != null && writeUp != null)
                {
                    Pawn worker = selPawn;
                    Thing chosen = desk;
                    yield return new FloatMenuOption(
                        "RR_UI_JournalWriteUpHere".Translate(next.label),
                        delegate
                        {
                            // Forced, because the player asked for it by name. The job's own need
                            // floor still applies: a starving pawn ordered to a desk leaves it, and
                            // that is deliberate rather than a failure of the order.
                            worker.jobs.TryTakeOrderedJob(JobMaker.MakeJob(writeUp, chosen),
                                JobTag.Misc);
                        });
                }
            }

            // ---------------------------------------------------------------- file in archive
            if (!campaign.HasArchivedCustody(parent))
            {
                Thing archive = campaign.NearestArchiveStore(parent);
                if (archive != null)
                {
                    Pawn hauler = selPawn;
                    Thing book = parent;
                    Thing target = archive;
                    yield return new FloatMenuOption("RR_UI_JournalFile".Translate(), delegate
                    {
                        Job haul = HaulAIUtility.HaulToContainerJob(hauler, book, target);
                        if (haul != null) { hauler.jobs.TryTakeOrderedJob(haul, JobTag.Misc); }
                    });
                }
            }

            // ---------------------------------------------------------------- send to company
            // **Only while the light is actually green.** Sending is the one action with a
            // consequence the player cannot undo, so it is offered exactly when it will work rather
            // than offered always and refused on arrival.
            if (campaign.LightFor(request) == QuestLight.Green)
            {
                IntVec3 cell = campaign.NearestCreditBeaconCell(parent);
                if (cell.IsValid)
                {
                    Pawn hauler = selPawn;
                    Thing book = parent;
                    IntVec3 destination = cell;
                    yield return new FloatMenuOption("RR_UI_JournalSend".Translate(), delegate
                    {
                        Job haul = JobMaker.MakeJob(JobDefOf.HaulToCell, book, destination);
                        haul.count = 1;
                        haul.haulMode = HaulMode.ToCellNonStorage;
                        hauler.jobs.TryTakeOrderedJob(haul, JobTag.Misc);
                    });
                }
            }
        }

        /// <summary>
        /// The closest records desk this pawn could reserve, or null.
        ///
        /// Reservation is checked here rather than after the walk, so the option is absent when every
        /// desk is taken instead of present and futile.
        /// </summary>
        private Thing NearestFreeDesk(Pawn selPawn, ThingDef deskDef)
        {
            List<Thing> desks = parent.Map.listerThings.ThingsOfDef(deskDef);
            Thing best = null;
            int bestDistance = int.MaxValue;
            for (int index = 0; index < desks.Count; index++)
            {
                Thing desk = desks[index];
                if (desk == null || !desk.Spawned) { continue; }
                if (!selPawn.CanReserveAndReach(desk, PathEndMode.InteractionCell, Danger.Some)) { continue; }
                if (!selPawn.CanReserveSittableOrSpot(desk.InteractionCell, false)) { continue; }
                int distance = selPawn.Position.DistanceToSquared(desk.Position);
                if (distance >= bestDistance) { continue; }
                best = desk;
                bestDistance = distance;
            }
            return best;
        }
    }
}
