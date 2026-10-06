using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// The requests half of the contracts pane: what the corporation is asking for, the ways
    /// through it, and what the branch has already done.
    ///
    /// **This is the surface that was missing.** The request shape and all seven authored
    /// requests shipped in 0.11.1-dev and 0.11.2-dev and no player could ever see one, because
    /// nothing read them. A card nobody can look at is content in a file.
    ///
    /// ## Why the routes are shown in full, always
    ///
    /// Owner decision, 2026-09-29: ***"filter picks the family, card never shrinks"***. Every
    /// authored route is drawn whether or not the branch can currently take it, because a route
    /// you cannot take yet is a route you can **work toward** — which is the whole reason the
    /// chart promises more than one. Capability decides which requests get **offered**; it never
    /// decides what a card that is already on the table admits to.
    ///
    /// ## Why satisfaction is read rather than computed here
    ///
    /// The tick that evaluates the routes records which ones are true, and this pane reads that.
    /// A panel redraws sixty times a second and two of the route checks scan every map the branch
    /// runs; computing it here would be the same answer, worked out a second time, more
    /// expensively, with somewhere new to drift.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        private void DrawRequests(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Requests_Heading".Translate());
            listing.Gap(6f);

            // Two of the three starts open in silence, and the silence is the design. Saying so
            // is better than an empty panel, which reads as a bug.
            if (!campaign.CorporationContact)
            {
                DrawHeading(listing, heading: "RR_Requests_NoContactBrief".Translate(),
                    detail: "RR_Requests_NoContact".Translate());
                listing.GapLine();
                return;
            }

            // **THE OFFER AND THE OBLIGATIONS ARE TWO LISTS NOW, and before this they could not be
            // more than one thing between them.** Accepting a job used to stop the company offering
            // anything else, so this pane never had a second request to draw. Owner: *"with ability
            // to accept more than one quests at a time"*.
            //
            // The offer comes first because it is the only one asking the player a question. Every
            // accepted job follows in acceptance order, drawn by the same method: it already shows
            // the Accept button only on an offer, so one routine serves both and the two cannot
            // disagree about how a request reads.
            RequestRecord offered = campaign.OfferedRequest;
            List<RequestRecord> accepted = campaign.AcceptedRequests;
            if (offered == null && accepted.Count == 0)
            {
                if (campaign.PastTheHinge)
                {
                    DrawHeading(listing, heading: "RR_Requests_PastTheHingeBrief".Translate(),
                        detail: "RR_Requests_PastTheHinge".Translate());
                }
                else { listing.Label("RR_Requests_NoneOpen".Translate()); }
            }
            if (offered != null) { DrawOpenRequest(listing, campaign, offered); }
            for (int index = 0; index < accepted.Count; index++)
            {
                listing.GapLine();
                DrawOpenRequest(listing, campaign, accepted[index]);
            }

            DrawPaperworkLedger(listing, campaign);
            DrawRequestHistory(listing, campaign);
            listing.GapLine();
        }

        /// <summary>
        /// The branch ledger: every accepted quest, its paperwork, and its light.
        ///
        /// **Owner direction, 2026-10-06, verbatim:** *"its almost like every book recieved needs to
        /// be tuned to or capable of listing the current quests its needed for that has been
        /// acceptred, with ability to accept more than one quests at a time"*.
        ///
        /// **Nothing ever prevented several at once** — `requests` is a list, and the tutorial line
        /// simply hands out one at a time. **What was missing is the index**, which is this.
        ///
        /// ## Accepted quests only, which is what makes it a ledger
        ///
        /// A ledger that also listed offers would be an offer board, and the pane above is already
        /// that. This answers one question: *what has this branch taken on, and what does each one
        /// still need from me.*
        ///
        /// ## And it is silent when there is nothing to say
        ///
        /// No accepted quest wants paperwork, no section. A heading over an empty list is the kind of
        /// permanent furniture that teaches a player to stop reading a pane.
        /// </summary>
        private void DrawPaperworkLedger(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            IReadOnlyList<RequestRecord> line = campaign.Requests;
            if (line == null) { return; }
            var rows = new List<RequestRecord>();
            for (int index = 0; index < line.Count; index++)
            {
                RequestRecord record = line[index];
                if (record == null || record.Status != RequestStatus.Accepted) { continue; }
                if (campaign.WriteUpsWanted(record).Count == 0) { continue; }
                rows.Add(record);
            }
            if (rows.Count == 0) { return; }

            listing.GapLine();
            listing.Label("RR_Ledger_PaperworkHeading".Translate(rows.Count));
            for (int index = 0; index < rows.Count; index++)
            {
                RequestRecord record = rows[index];
                RimroomsRequestDef definition = record.Definition;
                List<RimroomsWriteUpDef> wanted = campaign.WriteUpsWanted(record);
                int filed = 0;
                for (int item = 0; item < wanted.Count; item++)
                {
                    if (record.WriteUpsFiled.Contains(wanted[item].defName)) { filed++; }
                }
                QuestLight light = campaign.LightFor(record);
                listing.Label("RR_Ledger_PaperworkRow".Translate(
                    definition == null ? record.RequestDefName : definition.LabelCap.ToString(),
                    filed, wanted.Count, LightLabel(light)));

                // **The next step, not just the state.** A status line only helps somebody who
                // already knows the procedure exists, which is the lesson the record book's own
                // inspect card learned the hard way.
                //
                // **ONE DRAW CALL FOR FOUR MUTUALLY EXCLUSIVE LINES, and the shape is the point.**
                // This was four separate `listing.Label` statements, which `check-operations-density`
                // charges as the SUM of all four -- 56 words a player can never see together, since
                // exactly one branch draws per frame. The honest figure is the worst line the pane
                // can show, and the tool measures a key picked into a variable and translated once
                // at the maximum of its group. That is what `indirect_groups` exists for, and the
                // expedition pane's objective line is the same shape for the same reason.
                //
                // The argument rides along unconditionally: `Translate` ignores an extra argument a
                // string has no placeholder for, so the three with no `{0}` read exactly as they
                // did and the fourth keeps the name of the write-up it is asking for.
                RimroomsWriteUpDef next = campaign.NextWriteUp(record);
                string nextKey;
                if (light == QuestLight.Green) { nextKey = "RR_Ledger_PaperworkNextSend"; }
                else if (light == QuestLight.Amber) { nextKey = "RR_Ledger_PaperworkNextBook"; }
                else if (next == null) { nextKey = "RR_Ledger_PaperworkNextWaiting"; }
                else { nextKey = "RR_Ledger_PaperworkNextWrite"; }
                listing.Label(nextKey.Translate(next == null ? "" : next.label));
                listing.Gap(4f);
            }
        }

        /// <summary>One word for the light, so the row stays one line.</summary>
        private static string LightLabel(QuestLight light)
        {
            switch (light)
            {
                case QuestLight.Green: return "RR_Ledger_LightGreen".Translate().ToString();
                case QuestLight.Amber: return "RR_Ledger_LightAmber".Translate().ToString();
                default: return "RR_Ledger_LightDark".Translate().ToString();
            }
        }

        private void DrawOpenRequest(Listing_Standard listing, RimroomsCampaignComponent campaign,
            RequestRecord record)
        {
            RimroomsRequestDef definition = record.Definition;
            if (definition == null)
            {
                // The def went away with a mod list change. Say so rather than drawing a blank
                // row: the record is still in the save and still resolvable.
                listing.Label("RR_Requests_DefMissing".Translate(record.RequestDefName));
                return;
            }

            listing.Label("RR_Requests_OpenRow".Translate(definition.LabelCap,
                StatusLabel(record.Status)));
            listing.Label(definition.description);
            listing.Gap(4f);
            listing.Label("RR_Requests_Payment".Translate(Money(definition.paymentUsd)));
            if (definition.bonusUsd > 0)
            { listing.Label("RR_Requests_Bonus".Translate(Money(definition.bonusUsd))); }

            // There is no field to print an expiry from. Chart §1.1, enforced by absence: the
            // shape has nowhere to put a clock, so this line can only ever say so.
            listing.Label("RR_Requests_NoTimeLimit".Translate());
            listing.Gap(6f);

            listing.Label("RR_Requests_RoutesHeading".Translate());
            IReadOnlyList<string> satisfied = record.SatisfiedRouteLabelKeys;
            List<RimroomsSuccessRoute> routes = RequestRoutes.Available(definition, campaign);
            for (int index = 0; index < routes.Count; index++)
            {
                RimroomsSuccessRoute route = routes[index];
                if (route == null || string.IsNullOrEmpty(route.labelKey)) { continue; }
                // Three things a player needs off one line: what the route is, whether the branch
                // has already done it, and whether it is one the company authored or one this
                // branch earned by building something.
                string marker = satisfied.Contains(route.labelKey)
                    ? "RR_Requests_RouteDone".Translate().ToString()
                    : "RR_Requests_RouteOpen".Translate().ToString();
                string label = route.derived
                    ? "RR_Requests_RouteRowDerived".Translate(marker, route.labelKey.Translate()).ToString()
                    : "RR_Requests_RouteRow".Translate(marker, route.labelKey.Translate()).ToString();
                listing.Label(label);
                if (!string.IsNullOrEmpty(route.descriptionKey))
                { listing.Label("RR_Requests_RouteDesc".Translate(route.descriptionKey.Translate())); }
                listing.Gap(4f);
            }

            listing.Gap(4f);
            if (record.Status == RequestStatus.Offered &&
                listing.ButtonText("RR_Requests_Accept".Translate()))
            { ShowResult(campaign.AcceptRequest(record.RequestDefName)); }

            // Cancellation is a right the chart grants the player and denies the corporation, so
            // the button is always there while the request is open.
            if (listing.ButtonText("RR_Requests_Cancel".Translate()))
            { ShowResult(campaign.CancelRequest(record.RequestDefName)); }
        }

        /// <summary>
        /// The status word, from a literal key per branch.
        ///
        /// **Built by hand rather than by concatenating the enum name onto a prefix.** A key
        /// assembled at runtime cannot be checked: `check-keyed-strings.py` sees the prefix and
        /// nothing else, which is how an invented key got shipped once before. Every key this mod
        /// uses appears in full in a source file.
        ///
        /// Only the two open states are reachable here — this is drawn for an open request.
        /// </summary>
        private static string StatusLabel(RequestStatus status)
        {
            return (status == RequestStatus.Accepted
                ? "RR_Requests_StatusAccepted".Translate()
                : "RR_Requests_StatusOffered".Translate()).ToString();
        }

        private void DrawRequestHistory(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            IReadOnlyList<RequestRecord> all = campaign.Requests;
            bool any = false;
            for (int index = 0; index < all.Count; index++)
            {
                RequestRecord record = all[index];
                if (record == null || !record.Resolved) { continue; }
                if (!any)
                {
                    listing.GapLine();
                    listing.Label("RR_Requests_HistoryHeading".Translate());
                    any = true;
                }
                RimroomsRequestDef definition = record.Definition;
                string label = definition == null ? record.RequestDefName : definition.LabelCap.ToString();
                if (record.Status == RequestStatus.Cancelled)
                {
                    listing.Label("RR_Requests_HistoryCancelled".Translate(label));
                    continue;
                }
                // Which route actually did it. This is the part a player cannot reconstruct
                // afterwards, and it is the interesting half of the history.
                string route = (string.IsNullOrEmpty(record.SatisfiedRouteLabelKey)
                    ? "RR_Requests_RouteUnrecorded".Translate()
                    : record.SatisfiedRouteLabelKey.Translate()).ToString();
                listing.Label(record.BonusPaid
                    ? "RR_Requests_HistoryCompletedWithBonus".Translate(label, route, Day(record.CompletedTick)).ToString()
                    : "RR_Requests_HistoryCompleted".Translate(label, route, Day(record.CompletedTick)).ToString());
            }
        }
    }
}
