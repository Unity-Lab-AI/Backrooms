# -*- coding: utf-8 -*-
"""Give review a button. A readout and an objective line are not a workflow.

The previous edit made review visible and told the player it was the next step. **Neither of
those lets anybody do it.** `ReviewAnalysis` would have been `RedeemBondsInRadius` all over
again: correct, saved, surfaced, and with no caller the player could reach -- the shape that
accounts for four of five bond defects and seven before them.

`DrawReview` follows `DrawInterview` exactly, including how it finds the campaign, because that
is the one pattern in this pane already proven to work.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UI = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI", "OperationsEvidence.cs")

OLD_READOUT = u"""                else { listing.Label("RR_UI_ReviewAwaiting".Translate()); }"""

NEW_READOUT = u"""                else { DrawReview(listing, record); }"""

ANCHOR = u"""        private static void DrawInterview(Listing_Standard listing, EvidenceRecord record,"""

ADDITION = u'''        /// <summary>
        /// The sign-off, and the button that performs it.
        ///
        /// **Review is the fourth of the owner's four workflows** -- *"Add
        /// analyze/interview/compare/review workflows"* -- and the last to ship. Analyse, compare
        /// and interview were already here.
        ///
        /// Every refusal `ReviewAnalysis` can return is a named key the player is shown, because
        /// a control that refuses in silence is how somebody concludes a button is broken. That
        /// cost the owner an afternoon on the gate at 0.12.73-dev.
        /// </summary>
        private static void DrawReview(Listing_Standard listing, EvidenceRecord record)
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return; }
            if (!campaign.AwaitsReview(record)) { return; }

            listing.Label("RR_UI_ReviewAwaiting".Translate());

            // An outstanding dispute is two of the branch's own people contradicting each other
            // on the record. The interview is what clears it, and saying so is more use than a
            // greyed-out button: it names the step that unblocks this one.
            int disputes = campaign.UnsettledDisputes(record).Count();
            if (disputes > 0)
            {
                listing.Label("RR_Review_DisputesOutstanding".Translate(disputes));
                return;
            }

            Pawn reviewer = campaign.ReviewerFor(record);
            if (reviewer == null)
            {
                listing.Label("RR_Review_NoReviewer".Translate(
                    RimroomsCampaignComponent.MinimumReviewerIntellectual));
                return;
            }

            listing.Label("RR_UI_ReviewPrompt".Translate(reviewer.LabelShortCap));
            if (listing.ButtonText("RR_UI_SignOffReport".Translate()))
            { ShowResult(campaign.ReviewAnalysis(record, reviewer)); }
        }

'''

text = io.open(UI, encoding="utf-8-sig").read()
problems = []
if text.count(OLD_READOUT) != 1:
    problems.append("readout anchor %d" % text.count(OLD_READOUT))
if text.count(ANCHOR) != 1:
    problems.append("method anchor %d" % text.count(ANCHOR))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(OLD_READOUT, NEW_READOUT, 1)
text = text.replace(ANCHOR, ADDITION + ANCHOR, 1)
io.open(UI, "w", encoding="utf-8-sig", newline="").write(text)

after = io.open(UI, encoding="utf-8-sig").read()
failures = []
if u"ShowResult(campaign.ReviewAnalysis(record, reviewer))" not in after:
    failures.append("THE BUTTON DOES NOT CALL ReviewAnalysis -- the workflow is unreachable")
if u"private static void DrawReview(" not in after:
    failures.append("DrawReview was not written")
if u"else { DrawReview(listing, record); }" not in after:
    failures.append("DrawReview is never called from the readout")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("review has a button, and the button calls the service")
