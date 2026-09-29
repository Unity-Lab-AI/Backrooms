using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// The sites pane: what the branch runs beyond its headquarters, and what it costs.
    ///
    /// **Arc 5's principle has to be visible or it is not a principle.** *"A remote base is a
    /// costly responsibility rather than free map ownership"* means the player must be able to see
    /// the bill next to the list, so the cost is a decision rather than a surprise on a ledger
    /// line they have to go looking for.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        private void DrawRemoteSites(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Sites_Heading".Translate());
            listing.Gap(6f);

            IReadOnlyList<RemoteSiteRecord> sites = campaign.RemoteSites;
            listing.Label("RR_Sites_Summary".Translate(
                campaign.LiveRemoteSiteCount, RimroomsCampaignComponent.MaximumRemoteSites,
                campaign.DailyRemoteSiteOverheadUsd.ToString("N0")));
            listing.Gap(8f);

            if (sites.Count == 0)
            {
                listing.Label("RR_Sites_None".Translate());
            }
            else
            {
                for (int index = 0; index < sites.Count; index++)
                {
                    RemoteSiteRecord record = sites[index];
                    if (record == null) { continue; }
                    // A record whose place is gone is shown rather than hidden: the player needs
                    // to know why a site stopped being billed, and silently dropping a row is how
                    // a UI teaches somebody not to trust it.
                    // Three states, not two. "Reachable but nobody there" is the one a player
                    // needs to see, because it is the one that quietly holds their shipments.
                    string row;
                    if (!record.Live) { row = "RR_Sites_RowUnreachable".Translate(record.Label).ToString(); }
                    else if (!campaign.IsSiteStaffed(record.Site.Map))
                    { row = "RR_Sites_RowUnstaffed".Translate(record.Label).ToString(); }
                    else { row = "RR_Sites_Row".Translate(record.Label).ToString(); }
                    listing.Label(row);
                    if (listing.ButtonText("RR_Sites_Release".Translate(record.Label)))
                    { ShowResult(campaign.ReleaseRemoteSite(record.Id)); }
                    listing.Gap(4f);
                }
            }

            listing.GapLine();
            Map current = Find.CurrentMap;
            if (current == null)
            {
                listing.Label("RR_Sites_NoCurrentMap".Translate());
                return;
            }

            // Registering the map you are looking at, rather than picking from a list. It is the
            // one place the intent is unambiguous, and it means the button's meaning never has to
            // be explained.
            string reason = RegistrationBlockedReason(campaign, current);
            if (reason != null)
            {
                listing.Label(reason.Translate());
                return;
            }
            if (listing.ButtonText("RR_Sites_RegisterCurrent".Translate(current.Parent.LabelCap)))
            { ShowResult(campaign.RegisterRemoteSite(current)); }
        }

        /// <summary>
        /// Why the map in view cannot be put on the books, or null when it can.
        ///
        /// **The same conditions the service enforces, said before the click instead of after.**
        /// A button that is offered and then refuses has taught the player nothing; the service
        /// still re-checks every one of these, because a UI that offered a button is not evidence
        /// that the conditions still hold.
        /// </summary>
        private static string RegistrationBlockedReason(RimroomsCampaignComponent campaign, Map map)
        {
            if (map == campaign.Headquarters) { return "RR_Sites_BlockedHeadquarters"; }
            if (map.Parent is RimroomsDestinationMapParent) { return "RR_Sites_BlockedCoordinate"; }
            if (map.Parent == null || map.Parent.Destroyed || map.Parent.Faction != Faction.OfPlayer)
            { return "RR_Sites_BlockedNotYours"; }
            if (campaign.IsRegisteredRemoteSite(map)) { return "RR_Sites_BlockedAlready"; }
            if (campaign.RemoteSites.Count >= RimroomsCampaignComponent.MaximumRemoteSites)
            { return "RR_Sites_BlockedTooMany"; }
            return null;
        }
    }
}
