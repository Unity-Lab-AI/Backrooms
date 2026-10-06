using System.Collections.Generic;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// A colonist sitting at a records desk writing one piece of the company's paperwork.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"the journals are taken to a table and written out
    /// but these tasks are auto in the pawns work jobs"*.
    ///
    /// ## It is ordinary work, with every consequence of that
    ///
    /// It competes with cooking and hauling on the same work tab, so a branch that assigns nobody to
    /// it never files anything — **which is a decision the player made rather than a defect.** It is
    /// interruptible and resumable, because the tally lives on the company record and the desk holds
    /// nothing: a pawn pulled off halfway has lost that session's progress and nothing else.
    ///
    /// ## And the pawn is never trapped here
    ///
    /// <see cref="GateWatch.MustLeave"/> is the absolute floor, asked in the `FailOn` **and** again
    /// every tick, exactly as it is at the gate console. That floor exists because a pawn starved to
    /// death at a comms console, and **a starved pawn at a desk would be the same defect one
    /// subsystem over** — the owner's words were *"we cant have them not going to eat or finding
    /// saftey"*, and nothing about paperwork earns an exception to them.
    ///
    /// There is deliberately no posture setting here. A gate window is a scarce thing somebody might
    /// reasonably want held through discomfort; a report is not, so the floor is the whole rule.
    /// </summary>
    public sealed class JobDriver_RRWriteUp : JobDriver
    {
        /// <summary>How much of the write-up is done. Reset per job, because the record keeps score.</summary>
        private float progress;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref progress, "rr_writeUpProgress", 0f);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed)
                && pawn.ReserveSittableOrSpot(job.targetA.Thing.InteractionCell, job, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOnBurningImmobile(TargetIndex.A);
            // **The need floor, before anything else.** Same call the gate console job makes, so
            // there is one derivation of "this pawn must stop working" and not two.
            this.FailOn(() => GateWatch.MustLeave(pawn));
            this.FailOn(() => Current.Game == null
                || Current.Game.GetComponent<RimroomsCampaignComponent>() == null
                || !Current.Game.GetComponent<RimroomsCampaignComponent>().CanOperate);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

            Toil write = ToilMaker.MakeToil("RR_WriteUp");
            write.initAction = delegate
            {
                // Re-read at the moment work starts rather than trusting the giver's decision: a
                // pawn walks for a while, and in that time somebody else may have filed this.
                if (Resolve() == null) { EndJobWith(JobCondition.Incompletable); }
            };
            write.tickAction = delegate
            {
                // Asked every tick as well as in the FailOn, because a need crosses its threshold
                // mid-job and a FailOn alone is only consulted when the job is re-checked.
                if (GateWatch.MustLeave(pawn))
                { EndJobWith(JobCondition.InterruptForced); return; }

                WriteUpTarget target = Resolve();
                if (target == null) { EndJobWith(JobCondition.Incompletable); return; }

                // Intellectual, like analysis and calibration: the work is reading records and
                // writing prose, and the branch's researchers are the people with that skill.
                float speed = pawn.GetStatValue(StatDefOf.ResearchSpeed);
                progress += speed <= 0f ? 1f : speed;
                if (pawn.skills != null)
                { pawn.skills.Learn(SkillDefOf.Intellectual, 0.07f); }

                if (progress < target.Kind.workRequired) { return; }
                // **One call advances the record and stamps the book.** Not two operations, so the
                // two cannot disagree; see RimroomsCampaignComponent.FileWriteUpAndStamp.
                target.Campaign.FileWriteUpAndStamp(target.Request, target.Kind);
                ReadyForNextToil();
            };
            write.defaultCompleteMode = ToilCompleteMode.Never;
            write.WithProgressBar(TargetIndex.A, () =>
            {
                WriteUpTarget target = Resolve();
                return target == null ? 0f : progress / target.Kind.workRequired;
            });
            write.activeSkill = () => SkillDefOf.Intellectual;
            write.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            yield return write;
        }

        /// <summary>
        /// What this job is actually writing, resolved fresh every time it is asked.
        ///
        /// A class rather than a struct so "nothing to write" is a plain null. A nullable struct
        /// said the same thing in more words and every reader had to unwrap it.
        /// </summary>
        private sealed class WriteUpTarget
        {
            public RimroomsCampaignComponent Campaign;
            public RequestRecord Request;
            public RimroomsWriteUpDef Kind;
        }

        /// <summary>
        /// The quest and kind this pawn should be writing, or null if there is nothing left.
        ///
        /// **Derived, never carried on the job.** Storing the chosen quest in the job would be a
        /// second copy of a decision the record already owns, and a save/reload between the giver
        /// and the toil would make them disagree.
        /// </summary>
        private WriteUpTarget Resolve()
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return null; }
            RequestRecord request;
            RimroomsWriteUpDef kind;
            if (!campaign.TryFindWriteUpWork(out request, out kind)) { return null; }
            return new WriteUpTarget { Campaign = campaign, Request = request, Kind = kind };
        }
    }
}
