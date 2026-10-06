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

        /// <summary>
        /// Which report this session is writing, claimed once when work starts.
        ///
        /// **THIS IS THE FIX FOR THE BUG THE PARALLELISM SHIPPED WITH, and the previous comment here
        /// argued against it.** It said the target must be *"derived, never carried on the job"*,
        /// because carrying it would be *"a second copy of a decision the record already owns"*. That
        /// reasoning is right about a decision and wrong about an **identity**: re-deriving the
        /// target every tick meant a pawn's accumulated progress silently moved to whatever report
        /// was outstanding next, so a writer 900 ticks into a 1000-tick report would instantly
        /// complete a 600-tick one the moment somebody else filed the first. **One session of work,
        /// two reports filed.**
        ///
        /// So the job claims a report and keeps it. The record still owns whether it is outstanding;
        /// this owns only *which one I sat down to write*, which is a fact about the pawn and cannot
        /// live anywhere else. Scribed, so a save mid-session resumes the same report rather than
        /// silently switching.
        /// </summary>
        private string claimedRequestId;
        private string claimedKindName;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref progress, "rr_writeUpProgress", 0f);
            Scribe_Values.Look(ref claimedRequestId, "rr_writeUpClaimedRequest");
            Scribe_Values.Look(ref claimedKindName, "rr_writeUpClaimedKind");
        }

        /// <summary>
        /// Whether this session is writing that exact report. Read by the work giver's scan, so two
        /// desks never put two people on the same page.
        /// </summary>
        public bool IsWriting(RequestRecord request, RimroomsWriteUpDef kind)
        {
            return request != null && kind != null
                && !string.IsNullOrEmpty(claimedRequestId)
                && claimedRequestId == request.Id
                && claimedKindName == kind.defName;
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
                // **THE CLAIM IS TAKEN HERE, at the moment work starts rather than when the job was
                // offered.** A pawn walks for a while, and in that time somebody else may have filed
                // this or sat down to write it; claiming at the desk means the claim describes
                // somebody who is actually writing.
                WriteUpTarget chosen = Choose();
                if (chosen == null) { EndJobWith(JobCondition.Incompletable); return; }
                claimedRequestId = chosen.Request.Id;
                claimedKindName = chosen.Kind.defName;
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
        /// Whether this report is already filed against this quest.
        ///
        /// Walked rather than asked with `Contains`, because `WriteUpsFiled` is an
        /// `IReadOnlyList&lt;string&gt;` -- deliberately, so nothing outside `RequestRecord` can add to
        /// it. The interface has no `Contains`, and reaching for LINQ here would pull an allocation
        /// into a per-tick path for a list that is four entries long.
        /// </summary>
        private static bool HasFiled(RequestRecord request, string kindName)
        {
            IReadOnlyList<string> filed = request.WriteUpsFiled;
            if (filed == null) { return false; }
            for (int index = 0; index < filed.Count; index++)
            {
                if (filed[index] == kindName) { return true; }
            }
            return false;
        }

        /// <summary>
        /// What to sit down and write: the first report nobody else is already writing.
        ///
        /// Asked **once**, at the desk, by <see cref="MakeNewToils"/>. Everything afterwards reads
        /// <see cref="Resolve"/>, which only ever answers with the claim.
        /// </summary>
        private WriteUpTarget Choose()
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return null; }
            RequestRecord request;
            RimroomsWriteUpDef kind;
            if (!campaign.TryFindWriteUpWork(pawn, out request, out kind)) { return null; }
            if (request == null || kind == null || string.IsNullOrEmpty(request.Id)) { return null; }
            return new WriteUpTarget { Campaign = campaign, Request = request, Kind = kind };
        }

        /// <summary>
        /// The claimed report, or null once it is filed, cancelled or otherwise gone.
        ///
        /// **It answers with the claim and never with a substitute**, which is the whole repair.
        /// Returning the next outstanding report instead is what let one session's progress land on
        /// a different one. If somebody else filed this while the pawn was writing it, the honest
        /// outcome is that this session ends with nothing to show -- visible, and a consequence of
        /// two people having been sent at the same instant rather than of the record being wrong.
        /// </summary>
        private WriteUpTarget Resolve()
        {
            if (string.IsNullOrEmpty(claimedRequestId) || string.IsNullOrEmpty(claimedKindName))
            { return null; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return null; }
            RequestRecord request = campaign.RequestById(claimedRequestId);
            if (request == null || request.Status != RequestStatus.Accepted) { return null; }
            if (HasFiled(request, claimedKindName)) { return null; }
            RimroomsWriteUpDef kind = null;
            foreach (RimroomsWriteUpDef candidate in campaign.WriteUpsWanted(request))
            {
                if (candidate != null && candidate.defName == claimedKindName)
                { kind = candidate; break; }
            }
            if (kind == null || !campaign.WriteUpPreconditionMet(kind, request)) { return null; }
            return new WriteUpTarget { Campaign = campaign, Request = request, Kind = kind };
        }
    }
}
