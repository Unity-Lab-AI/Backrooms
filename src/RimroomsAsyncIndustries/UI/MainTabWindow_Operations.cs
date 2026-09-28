using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>RR-UI: read-only foundation view. Never owns or initializes company state.</summary>
    public sealed class MainTabWindow_Operations : MainTabWindow
    {
        private Vector2 scrollPosition;
        private float contentHeight = 420f;

        public override Vector2 RequestedTabSize { get { return new Vector2(660f, 480f); } }

        public override void DoWindowContents(Rect inRect)
        {
            GameFont previousFont = Text.Font;
            Rect viewport = inRect.ContractedBy(12f);
            Rect content = new Rect(0f, 0f, Mathf.Max(120f, viewport.width - 20f), contentHeight);
            Widgets.BeginScrollView(viewport, ref scrollPosition, content);
            Listing_Standard listing = new Listing_Standard();
            listing.Begin(content);
            try
            {
                Text.Font = GameFont.Medium;
                listing.Label("RR_Operations_Title".Translate());
                Text.Font = GameFont.Small;
                listing.Gap(12f);

                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                if (campaign == null)
                {
                    listing.Label("RR_Operations_NoGame".Translate());
                }
                else if (!campaign.HasSupportedSchema)
                {
                    listing.Label("RR_Operations_UnsupportedSave".Translate());
                }
                else if (!campaign.HasBranch)
                {
                    listing.Label("RR_Operations_Inactive".Translate());
                    listing.Gap(8f);
                    listing.Label("RR_Operations_Foundation".Translate());
                }
                else
                {
                    listing.Label("RR_Operations_Branch".Translate(campaign.BranchId));
                    listing.Label("RR_Operations_Scenario".Translate(campaign.ScenarioId ?? string.Empty));
                    listing.Label("RR_Operations_Foundation".Translate());
                }

                listing.Gap(20f);
                listing.Label("RR_Operations_NativeControls".Translate());
                if (listing.ButtonText("RR_Operations_OpenWork".Translate()))
                {
                    OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Work"));
                }
                if (listing.ButtonText("RR_Operations_OpenResearch".Translate()))
                {
                    OpenNativeTab(MainButtonDefOf.Research);
                }
                contentHeight = Mathf.Max(420f, listing.CurHeight + 20f);
            }
            finally
            {
                listing.End();
                Widgets.EndScrollView();
                Text.Font = previousFont;
            }
        }

        private static void OpenNativeTab(MainButtonDef target)
        {
            if (target == null || !target.Worker.Visible || target.Worker.Disabled)
            {
                Messages.Message("RR_Operations_TabUnavailable".Translate(), MessageTypeDefOf.RejectInput, false);
                return;
            }

            // Preserve native research/tutorial/world-selection behavior via its worker.
            target.Worker.InterfaceTryActivate();
        }
    }
}
