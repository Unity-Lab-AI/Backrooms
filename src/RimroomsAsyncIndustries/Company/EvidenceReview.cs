using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Review: the fourth workflow, and the one that was still missing.
    ///
    /// **Owner direction, verbatim:** *"Add analyze/interview/compare/review workflows for
    /// equipment, furniture, people, entity remains, recordings, transcripts, route notes, and
    /// recovered documents"*, and on 2026-10-01: *"andf yes do those three things you listed as
    /// well"*.
    ///
    /// Analyse shipped first, compare at 0.12.25-dev, interview at 0.12.28-dev. **Review is the
    /// last of the four.**
    ///
    /// ## What a review is, and what it is not
    ///
    /// A review is **a second person checking a finished report**. It is not more analysis and it
    /// produces no new facts: `EvidenceAnalysisReport` is frozen the moment analysis completes
    /// and nothing here writes to it. What a review decides is whether the branch will **stand
    /// behind** what the report says.
    ///
    /// So it can **endorse**, or it can **return the record** — and returning it is the half that
    /// makes the workflow worth having. A report whose observation detail never existed, or whose
    /// accounts are still in dispute, is one the company cannot sign off, and saying so is more
    /// use to the player than a rubber stamp.
    ///
    /// ## Why this is additive fields and not a new EvidenceStatus
    ///
    /// `EvidenceStatus` is `{ Located, Recovered, Secured, Analyzed, Missing }` and
    /// **`Analyzed` is the terminal state eight separate places test for** — the laboratory job
    /// driver, the first-slice site component, the objective hint, the resurvey gate. A sixth
    /// value would silently change every one of those comparisons and break every existing save
    /// that stores the enum by value.
    ///
    /// So review is **recorded beside the status, never instead of it**, which is the same
    /// additive-schema discipline `observationSchemaVersion` already uses in the same record for
    /// the same reason.
    ///
    /// ## And it is reachable, which is the part that usually fails here
    ///
    /// Four of five bond defects, and seven before them, were **built, correct and unreachable**.
    /// So this ships with two consumers in the same checkpoint: the evidence readout names the
    /// reviewer, and the objective hint tells the player a reviewed sign-off is the next step
    /// once analysis is done. A workflow with no surface is a workflow nobody can run.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// The Intellectual a reviewer needs. Lower than the interviewer's Social 4, because
        /// reading somebody else's report is a smaller ask than getting two people who disagree
        /// to settle it.
        /// </summary>
        public const int MinimumReviewerIntellectual = 3;

        /// <summary>
        /// Somebody on the payroll who could review this record, or null.
        ///
        /// **Never the analyst.** A second pair of eyes that belongs to the same head is not a
        /// second pair of eyes, and that is the entire mechanism.
        /// </summary>
        public Pawn ReviewerFor(EvidenceRecord record)
        {
            if (record == null) { return null; }
            Pawn analyst = record.AnalysisReport == null ? null : record.Analyst;
            Pawn best = null;
            int bestSkill = -1;
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn pawn = member.pawn;
                if (pawn == null || pawn.Dead || pawn.Destroyed || pawn.Downed) { continue; }
                if (analyst != null && pawn == analyst) { continue; }
                if (pawn.skills == null) { continue; }
                int skill = pawn.skills.GetSkill(SkillDefOf.Intellectual).Level;
                if (skill < MinimumReviewerIntellectual) { continue; }
                if (skill <= bestSkill) { continue; }
                best = pawn;
                bestSkill = skill;
            }
            return best;
        }

        /// <summary>
        /// Whether this record is waiting for a sign-off: analysed, and not yet reviewed.
        /// This is what the objective hint reads, so the player is told the step exists.
        /// </summary>
        public bool AwaitsReview(EvidenceRecord record)
        {
            return record != null
                && record.Status == EvidenceStatus.Analyzed
                && record.AnalysisReport != null
                && !record.Reviewed;
        }

        /// <summary>
        /// Every analysed record this branch has not signed off yet, so the readout can count
        /// them rather than the player hunting for them one at a time.
        /// </summary>
        public IEnumerable<EvidenceRecord> RecordsAwaitingReview()
        {
            return evidence.Where(AwaitsReview);
        }

        /// <summary>
        /// Signs a finished report off, or returns it.
        ///
        /// Every refusal names its own cause. **A gizmo that refuses in silence is the thing that
        /// cost the owner an afternoon on the gate** at 0.12.73-dev, and this follows
        /// <c>SettleDisputedAccount</c>'s shape precisely for that reason.
        /// </summary>
        public CompanyActionResult ReviewAnalysis(EvidenceRecord record, Pawn reviewer)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Review_Inactive"); }
            if (record == null || !evidence.Contains(record))
            { return CompanyActionResult.Refused("RR_Review_RecordUnavailable"); }
            if (record.Status != EvidenceStatus.Analyzed)
            { return CompanyActionResult.Refused("RR_Review_NotAnalysed"); }
            if (record.AnalysisReport == null)
            { return CompanyActionResult.Refused("RR_Review_NoReport"); }
            if (record.Reviewed)
            { return CompanyActionResult.Refused("RR_Review_AlreadyReviewed"); }
            if (reviewer == null || reviewer.Dead || reviewer.Destroyed || reviewer.Downed)
            { return CompanyActionResult.Refused("RR_Review_ReviewerUnavailable"); }
            if (record.Analyst != null && reviewer == record.Analyst)
            { return CompanyActionResult.Refused("RR_Review_ReviewerIsAnalyst"); }
            if (reviewer.skills == null
                || reviewer.skills.GetSkill(SkillDefOf.Intellectual).Level < MinimumReviewerIntellectual)
            { return CompanyActionResult.Refused("RR_Review_ReviewerUnskilled"); }

            // **A review cannot sign off on a record the company has not settled.** An unsettled
            // dispute is two of its own people contradicting each other on the record, and
            // endorsing that would make the sign-off worthless. The interview is the step that
            // clears it, which is how the four workflows chain rather than sit side by side.
            if (UnsettledDisputes(record).Any())
            { return CompanyActionResult.Refused("RR_Review_DisputesOutstanding"); }

            // The one case that is returned rather than endorsed, and it is a real one: an older
            // save's report kept its analyst and its timestamp and lost its observation detail.
            // There is nothing there to stand behind.
            bool endorsed = !record.AnalysisReport.DetailsUnavailable;

            record.MarkReviewed(reviewer, Find.TickManager.TicksGame, endorsed);
            RecordEvent(endorsed ? "RR_Event_ReviewEndorsed" : "RR_Event_ReviewReturned",
                record.Id, reviewer.LabelShortCap.ToString());
            Messages.Message(
                (endorsed ? "RR_Review_Endorsed" : "RR_Review_Returned")
                    .Translate(reviewer.LabelShortCap),
                record.Item ?? (Thing)reviewer, MessageTypeDefOf.TaskCompletion, false);
            return CompanyActionResult.Applied();
        }
    }
}
