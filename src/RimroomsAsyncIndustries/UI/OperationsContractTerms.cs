using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// RR-UI: what a contract actually wants, said on the card.
    ///
    /// **Row 1033, in its own words:** *"A player-facing surface for open odd demands. Offers and
    /// settlements are recorded events today; the Operations pane does not list them."*
    ///
    /// The row understates it. The pane did list them — and printed **`RR_UI_ContractTerms` on
    /// every contract**, which is the *survey* contract's terms, written for a completely
    /// different job. So an odd-goods demand for two hundred odd cotton displayed *"Survey the
    /// route, record the distortion, recover the record book and analyse it at headquarters"*.
    /// The pane was not silent about odd demands, it was **wrong** about them, which is worse:
    /// silence makes a player go looking, and a confident wrong answer stops them.
    ///
    /// Meanwhile `requiredThingDefName`, `requiredCount` and `deliveredCount` were saved, given
    /// public accessors, and **read by nothing but the settlement code** — the exact shape
    /// `check-wiring.py` exists to catch, in C# rather than in XML where it can see it.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        private static void DrawContractTerms(Listing_Standard listing,
            RimroomsCampaignComponent campaign, ContractRecord contract)
        {
            if (contract == null) { return; }

            // Not a demand: the survey terms are this contract's real terms.
            if (!contract.IsOddSupply)
            {
                DrawHeading(listing, heading: "RR_UI_ContractTermsBrief".Translate(),
                    detail: "RR_UI_ContractTerms".Translate());
                return;
            }

            ThingDef wanted = DefDatabase<ThingDef>
                .GetNamedSilentFail(contract.RequiredThingDefName);
            string label = wanted == null
                ? "RR_UI_DemandUnknownThing".Translate().ToString()
                : wanted.LabelCap.ToString();

            listing.Label("RR_UI_DemandWanted".Translate(
                contract.RequiredCount.ToString("N0"), label));
            // What counts toward the delivery, on the delivery count.
            DrawHeading(listing,
                heading: "RR_UI_DemandDelivered".Translate(
                    contract.DeliveredCount.ToString("N0"),
                    contract.RequiredCount.ToString("N0")),
                detail: "RR_UI_DemandOddOnly".Translate());

            if (!contract.IsOddConsignment) { return; }

            // A consignment mission also wants a space worked, and that half is the reason it
            // pays double. Stated as progress rather than as a yes or a no, because a player
            // who cannot see how far along they are cannot decide whether to push on.
            CoordinateRecord named = campaign.Coordinates
                .FirstOrDefault(c => c != null && c.Id == contract.CoordinateId);
            listing.Label("RR_UI_ConsignmentOrigin".Translate(
                named == null ? contract.CoordinateId : named.Label,
                contract.RequiredDepth.ToString("N0")));
            listing.Label("RR_UI_ConsignmentSurvey".Translate(
                campaign.FieldConditionProgress(contract).ToString("N0"),
                contract.RequiredSurveyedRooms.ToString("N0"),
                contract.RequiredDepth.ToString("N0")));
            listing.Label(campaign.FieldConditionMet(contract)
                ? "RR_UI_ConsignmentFieldMet".Translate()
                : "RR_UI_ConsignmentFieldUnmet".Translate());
        }
    }
}
