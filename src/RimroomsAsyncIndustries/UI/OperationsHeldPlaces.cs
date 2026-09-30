using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// The places pane: what this company is holding open, and what it costs to keep holding it.
    ///
    /// ## Owner direction, 2026-09-30
    ///
    /// *"yeah so if the player discovers and goes through a natural gate how do they turn them off
    /// to use the machine gates for more controll and aiming deeper?"*, and the trap named:
    /// *"get 5 natural gates u cant use a machine gate"*. Asked how, they chose **an Operations
    /// held-places list with a Release button**, over a gizmo alone, over both, and over an
    /// automatic timer.
    ///
    /// **The reason that was the right choice is scatter.** A gizmo acts on the door in front of
    /// you; the gates that fill a budget are spread across levels you may not be standing on. A
    /// player at their limit needs to see all of it in one place and choose. The door gizmo exists
    /// too — see `CompRimroomsEmergence` — but it is the convenience, not the answer.
    ///
    /// ## The count is shown even when nothing can be released
    ///
    /// Same principle as the sites pane: *a costly responsibility rather than free map ownership*
    /// means the bill has to be visible next to the list. A player who cannot work out why a gate
    /// refused has been told nothing useful.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        private void DrawHeldPlaces(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Release_Heading".Translate());
            listing.Gap(6f);
            listing.Label("RR_Release_Budget".Translate(OpenMapBudget.Held, OpenMapBudget.Budget));
            listing.Label("RR_Release_Explanation".Translate());
            listing.Gap(8f);

            // Colonies first, because they are the other half of the budget and a player counting
            // slots needs to see why three of five are gone before they blame the Backrooms.
            var colonies = Find.Maps.Where(map => map != null && map.IsPlayerHome &&
                map.Parent is Settlement).ToList();
            for (int index = 0; index < colonies.Count; index++)
            {
                listing.Label("RR_Release_ColonyRow".Translate(colonies[index].Parent.Label));
            }

            IReadOnlyList<CoordinateRecord> coordinates = campaign.Coordinates;
            var held = new List<CoordinateRecord>();
            var shelved = new List<CoordinateRecord>();
            for (int index = 0; index < coordinates.Count; index++)
            {
                CoordinateRecord record = coordinates[index];
                if (record == null) { continue; }
                RimroomsDestinationMapParent parent = record.Site as RimroomsDestinationMapParent;
                if (parent != null && parent.Map != null) { held.Add(record); }
                else if (record.ReleasedByPlayer) { shelved.Add(record); }
            }

            listing.GapLine();
            if (held.Count == 0)
            {
                listing.Label("RR_Release_NoneHeld".Translate());
            }
            for (int index = 0; index < held.Count; index++)
            {
                CoordinateRecord record = held[index];
                listing.Label("RR_Release_PlaceRow".Translate(
                    NaturalFrontierService.DiscoveredLabelFor(record), record.Depth));
                string refusal = CoordinateRelease.RefusalFor(campaign, record);
                if (refusal != null)
                {
                    // A refusal is shown as the row's own state rather than as a disabled button
                    // with no explanation. The player asked a reasonable question and gets an
                    // answer: who is inside, or that it is the headquarters.
                    listing.Label("RR_Release_Blocked".Translate(refusal.Translate()));
                }
                else
                {
                    int items = CoordinateRelease.ItemsLeftBehind(record);
                    listing.Label("RR_Release_LeftBehind".Translate(items));
                    CoordinateRecord subject = record;
                    if (listing.ButtonText("RR_Release_Button".Translate()))
                    {
                        Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                            "RR_Release_Confirm".Translate(
                                NaturalFrontierService.DiscoveredLabelFor(subject), items),
                            delegate { Release(campaign, subject); },
                            destructive: true,
                            title: "RR_Release_ConfirmTitle".Translate()));
                    }
                }
                listing.GapLine();
            }

            if (shelved.Count > 0)
            {
                listing.Label("RR_Release_ShelvedHeading".Translate());
                for (int index = 0; index < shelved.Count; index++)
                {
                    listing.Label("RR_Release_ShelvedRow".Translate(
                        NaturalFrontierService.DiscoveredLabelFor(shelved[index]), shelved[index].Depth));
                }
                listing.Label("RR_Release_ShelvedHint".Translate());
            }
        }

        /// <summary>
        /// Release one place, and say what happened either way.
        ///
        /// A silent refusal here would be the worst possible outcome: the player pressed a button
        /// to free a slot, and a slot either was or was not freed.
        /// </summary>
        private static void Release(RimroomsCampaignComponent campaign, CoordinateRecord record)
        {
            string label = NaturalFrontierService.DiscoveredLabelFor(record);
            string refusal = CoordinateRelease.TryRelease(campaign, record);
            if (refusal != null)
            {
                Messages.Message("RR_Release_Failed".Translate(label, refusal.Translate()),
                    MessageTypeDefOf.RejectInput, false);
                return;
            }
            Messages.Message("RR_Release_Done".Translate(label, OpenMapBudget.Describe()),
                MessageTypeDefOf.PositiveEvent, false);
        }
    }
}
