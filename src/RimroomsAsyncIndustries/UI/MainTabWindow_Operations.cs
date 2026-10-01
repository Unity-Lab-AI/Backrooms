using System.Globalization;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Investigation;
using RimroomsAsyncIndustries.Scenario;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>RR-UI: views read campaign state; commands call its services.</summary>
    public sealed partial class MainTabWindow_Operations : MainTabWindow
    {
        private Vector2 scrollPosition;
        private float contentHeight = 420f;
        private int selectedPane;
        private static readonly string[] PaneKeys = { "RR_UI_Overview", "RR_UI_Personnel", "RR_UI_Contracts", "RR_UI_Ledger", "RR_UI_Atlas", "RR_UI_Activity", "RR_UI_Investigation", "RR_UI_Machine", "RR_UI_Expedition", "RR_UI_Facilities", "RR_UI_Procurement", "RR_UI_Sites", "RR_UI_Places", "RR_UI_Help" };

        /// <summary>
        /// The help pane is the one pane that does not read company state, so it is drawn
        /// beside the campaign block rather than inside it. A glossary that needs a running
        /// company before it will open is not help.
        /// </summary>
        private const int HelpPane = 13;

        public override Vector2 RequestedTabSize { get { return new Vector2(820f, 580f); } }

        public override void DoWindowContents(Rect inRect)
        {
            // Known-good IMGUI state for this draw, restored on the way out.
            // Unity's draw state is process-wide and every mod's OnGUI shares
            // it; a mod that leaves GUI.color set paints every window after it.
            // See RimroomsWindowState -- this is the fix for the first bug a
            // real launch found.
            using (RimroomsWindowState.Clean())
            using (Core.RimroomsDiagnostics.Measure("operations-draw"))
            { DrawOperations(inRect); }
        }

        private void DrawOperations(Rect inRect)
        {
            GameFont previousFont = Text.Font;
            Rect viewport = inRect.ContractedBy(12f);
            const int columns = 5;
            float tabWidth = viewport.width / columns;
            for (int i = 0; i < PaneKeys.Length; i++)
            {
                if (Widgets.ButtonText(new Rect(viewport.x + (i % columns) * tabWidth, viewport.y + (i / columns) * 36f, tabWidth - 4f, 32f), PaneKeys[i].Translate()))
                {
                    selectedPane = i;
                    scrollPosition = Vector2.zero;
                    contentHeight = 420f;
                }
            }
            viewport.yMin += ((PaneKeys.Length + columns - 1) / columns) * 36f + 8f;
            Rect content = new Rect(0f, 0f, Mathf.Max(120f, viewport.width - 20f), contentHeight);
            Widgets.BeginScrollView(viewport, ref scrollPosition, content);
            Listing_Standard listing = new Listing_Standard();
            // One column. Core's Listing silently wraps a full column-width to the RIGHT when content
            // outgrows the rect, outside the group it clips to, and resets CurHeight doing it -- so the
            // page loses its tail AND under-reports its height, which shrinks the rect again.
            listing.maxOneColumn = true;
            listing.Begin(content);
            try
            {
                Text.Font = GameFont.Medium;
                listing.Label("RR_Operations_Title".Translate());
                Text.Font = GameFont.Small;
                listing.Gap(12f);

                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                if (selectedPane == HelpPane)
                {
                    DrawHelp(listing);
                }
                else if (campaign == null)
                {
                    listing.Label("RR_Operations_NoGame".Translate());
                }
                else if (!campaign.HasSupportedSchema)
                {
                    listing.Label("RR_Operations_UnsupportedSave".Translate());
                }
                else if (campaign.StateFaultKey != null)
                {
                    listing.Label(campaign.StateFaultKey.Translate());
                }
                else if (!campaign.HasBranch)
                {
                    listing.Label("RR_Operations_Inactive".Translate());
                    listing.Gap(8f);
                    listing.Label("RR_Company_Inactive".Translate());
                    if (ScenPart_RimroomsStart.Current != null && Find.CurrentMap != null &&
                        listing.ButtonText("RR_UI_RetryCompanyRegistration".Translate()))
                    { ShowResult(ScenPart_RimroomsStart.Current.TryInitializeExistingHeadquarters(Find.CurrentMap)); }
                }
                else
                {
                    DrawCompany(listing, campaign);
                }

                listing.Gap(20f);
                listing.Label("RR_Operations_NativeControls".Translate());

                // Row 821 names the surfaces that must stay reachable: *"every relevant
                // Architect, Work, Assign, Research, World, map, building, and pawn action"*.
                // Until 0.12.40-dev this block held two of them, and **Architect -- the first
                // one the row names, and the one every building action goes through -- was not
                // opened from anywhere in this package.** Assign and World were reachable, but
                // only from inside the personnel and facilities panes, which is reachable and
                // not findable. All five are here now, in the order the row lists them.
                //
                // Each is `MainButtonDef.Worker.InterfaceTryActivate()`: the game's own button,
                // pressed on the player's behalf. Nothing about Core's tab bar is replaced,
                // reordered or patched, which is the part of row 821 that stays unbuilt on
                // purpose -- see the closure note.
                if (listing.ButtonText("RR_Operations_OpenArchitect".Translate()))
                {
                    OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Architect"));
                }
                if (listing.ButtonText("RR_Operations_OpenWork".Translate()))
                {
                    OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Work"));
                }
                if (listing.ButtonText("RR_Operations_OpenAssign".Translate()))
                {
                    OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign"));
                }
                if (listing.ButtonText("RR_Operations_OpenResearch".Translate()))
                {
                    OpenNativeTab(MainButtonDefOf.Research);
                }
                if (listing.ButtonText("RR_Operations_OpenWorld".Translate()))
                {
                    OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("World"));
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

        private void DrawCompany(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            // The company's own name, on every pane. Every start builds a company and
            // names it their own, so this is identity rather than decoration.
            listing.Label("RR_Company_NameHeading".Translate(campaign.CompanyName));
            if (listing.ButtonText("RR_Company_RenameButton".Translate()))
            { Find.WindowStack.Add(new Dialog_RenameCompany(campaign)); }
            listing.Label("RR_Company_Balance".Translate(Money(campaign.BalanceUsd)));
            listing.GapLine();
            switch (selectedPane)
            {
                case 7: DrawMachine(listing, campaign); break;
                case 8: DrawExpedition(listing, campaign); break;
                case 9: DrawFacilities(listing, campaign); break;
                case 10: DrawProcurement(listing, campaign); break;
                case 11: DrawRemoteSites(listing, campaign); break;
                case 12: DrawHeldPlaces(listing, campaign); break;
                case 1:
                    DrawPersonnel(listing, campaign);
                    break;
                case 2:
                    // The corporation's requests come first: they are the campaign, and the
                    // contracts below them are the survey and odd-supply paperwork the requests
                    // generate. A player looking at this pane is looking for what to do next.
                    DrawRequests(listing, campaign);
                    foreach (ContractRecord contract in campaign.Contracts)
                    {
                        listing.Label("RR_UI_ContractRow".Translate(contract.TitleKey.Translate(), ("RR_Contract_" + contract.Status).Translate()));
                        listing.Label("RR_UI_ContractValue".Translate(Money(contract.BasePaymentUsd), Money(contract.BonusUsd)));
                        DrawContractTerms(listing, campaign, contract);
                        listing.GapLine();
                    }
                    break;
                case 3:
                    listing.Label("RR_Company_CashExplanation".Translate());
                    listing.Label("RR_UI_LedgerRecent".Translate());
                    listing.Gap(8f);
                    foreach (LedgerEntry entry in campaign.Ledger.Reverse().Take(60))
                    {
                        listing.Label("RR_UI_LedgerRow".Translate(Day(entry.Tick), entry.ReasonKey.Translate(), Money(entry.AmountUsd), Money(entry.BalanceAfterUsd)));
                        listing.Gap(4f);
                    }
                    break;
                case 4:
                    foreach (CoordinateRecord coordinate in campaign.Coordinates.ToList())
                    {
                        listing.Label("RR_UI_CoordinateRow".Translate(coordinate.Label, ("RR_Coordinate_" + coordinate.Status).Translate()));
                        // How hostile the space currently is. The pressure ladder has decided
                        // this since 0.8.4-dev and drives anomaly events and incursion, and it
                        // had never been shown to anybody -- inferable only by being hurt by it,
                        // which is the opposite of invariant 28’s learnable rule.
                        listing.Label("RR_UI_CoordinateBand".Translate(
                            Threats.CoordinatePressureLadder.BandLabelKey(
                                Threats.CoordinatePressureLadder.BandFor(coordinate,
                                    Threats.CoordinatePressureLadder.ColonyWealth())).Translate()));
                        listing.Label("RR_UI_SurveyedRooms".Translate(coordinate.Rooms.Count(r => r.Surveyed)));
                        if (campaign.HasRouteTelemetry)
                        {
                            foreach (RoomRecord room in coordinate.Rooms.Where(r => r.Surveyed))
                            {
                                string knownLinks = string.Join(", ", room.Links.Where(index => coordinate.Rooms.Any(r => r.Index == index && r.Surveyed))
                                    .Select(index => (index + 1).ToString()).ToArray());
                                listing.Label("RR_UI_TelemetryRoom".Translate(room.Index + 1, ("RR_Room_" + room.FamilyId).Translate(), knownLinks));
                            }
                        }
                        else { listing.Label("RR_UI_TelemetryLocked".Translate()); }
                        DrawKnownRoomClues(listing, coordinate);
                        if (coordinate.Status == CoordinateStatus.Unavailable)
                        {
                            string failure = (coordinate.Site as Generation.RimroomsDestinationMapParent)?.GenerationFailureKey;
                            if (!string.IsNullOrEmpty(failure)) { listing.Label(failure.Translate()); }
                            listing.Label("RR_UI_FailedSiteRecoveryExplanation".Translate());
                            if (listing.ButtonText("RR_UI_FailedSiteRecovery".Translate()))
                            {
                                string failedId = coordinate.Id;
                                Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation("RR_UI_FailedSiteRecoveryConfirm".Translate(), () =>
                                {
                                    CompanyActionResult result = campaign.ReaddressPristineInitialSurvey(failedId);
                                    ShowResult(result);
                                    if (result.Success)
                                    { selectedCoordinateId = failedId + ":fallback:1"; selectedPane = 8; scrollPosition = Vector2.zero; }
                                }));
                            }
                        }
                        listing.GapLine();
                    }
                    break;
                case 6:
                    DrawEvidenceCreationRecovery(listing, campaign);
                    DrawLaboratoryBinding(listing, campaign);
                    listing.GapLine();
                    listing.Label("RR_UI_LabInstructions".Translate());
                    listing.Label("RR_Company_Insights".Translate(campaign.ResearchInsights));
                    listing.GapLine();
                    foreach (EvidenceRecord record in campaign.Evidence)
                    {
                        CoordinateRecord coordinate = campaign.Coordinates.FirstOrDefault(c => c.Id == record.CoordinateId);
                        float required = record.Item?.TryGetComp<CompRouteEvidence>()?.WorkRequired ?? 3000f;
                        listing.Label("RR_UI_EvidenceRow".Translate(coordinate == null ? record.CoordinateId : coordinate.Label,
                            ("RR_EvidenceStatus_" + record.Status).Translate(), (record.AnalysisWork / required).ToString("P0")));
                        listing.Label("RR_UI_EvidenceChecklist".Translate(Observation(record.RouteRecorded),
                            Observation(record.DistortionRecorded), Observation(record.EntityRecorded)));
                        if (record.Item != null && record.Item.Spawned && !record.Item.Position.Fogged(record.Item.Map) &&
                            listing.ButtonText("RR_UI_LocateRecording".Translate()))
                        { CameraJumper.TryJumpAndSelect(record.Item); }
                        if (!record.RouteRecorded || !record.DistortionRecorded)
                        { listing.Label("RR_UI_EvidenceFieldWorkRemaining".Translate()); }
                        DrawEvidenceDetails(listing, record);
                        listing.Gap(8f);
                    }
                    listing.GapLine();
                    foreach (ProjectRecord project in campaign.Projects)
                    {
                        RimroomsProjectDef definition = DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(project.ResearchDefName);
                        if (definition == null) { listing.Label("RR_Research_MissingProject".Translate()); continue; }
                        string status = project.Completed ? "RR_UI_ProjectCompleted".Translate().ToString()
                            : project.InsightCommitted ? "RR_UI_ProjectWorking".Translate((project.WorkDone / definition.workRequired).ToString("P0")).ToString()
                            : "RR_UI_ProjectUnstarted".Translate().ToString();
                        listing.Label("RR_UI_ProjectRow".Translate(definition.LabelCap, status));
                        listing.Label(definition.description);
                        if (!project.InsightCommitted && !project.Completed && listing.ButtonText("RR_UI_ProjectStart".Translate(definition.LabelCap)))
                        { ShowResult(campaign.BeginCompanyProject(project.Id)); }
                        listing.Gap(8f);
                    }
                    break;
                case 5:
                    if (Prefs.DevMode)
                    {
                        listing.Label("RR_Debug_CounterNote".Translate());
                        if (listing.ButtonText("RR_Debug_CounterStart".Translate())) { Core.RimroomsDiagnostics.Start(); }
                        if (listing.ButtonText("RR_Debug_CounterStop".Translate())) { Core.RimroomsDiagnostics.Stop(); }
                        if (listing.ButtonText("RR_Debug_CounterLog".Translate())) { Core.RimroomsDiagnostics.WriteSnapshot(); }
                        if (listing.ButtonText("RR_Debug_RuntimeIdentity".Translate())) { Core.RimroomsDiagnostics.WriteRuntimeIdentity(); }
                        listing.GapLine();
                    }
                    if (campaign.Events.Count == 0) { listing.Label("RR_UI_NoRecords".Translate()); }
                    foreach (CompanyEventRecord activity in campaign.Events.Reverse())
                    {
                        string message = activity.MessageKey.Translate().ToString();
                        if (activity.Arguments.Count > 0)
                        {
                            message = string.Format(CultureInfo.CurrentCulture, message, activity.Arguments.Cast<object>().ToArray());
                        }
                        listing.Label("RR_UI_ActivityRow".Translate(Day(activity.Tick), message));
                        listing.Gap(4f);
                    }
                    break;
                default:
                    DrawOpeningObjective(listing, campaign);
                    listing.Label("RR_Company_CashExplanation".Translate());
                    listing.Label("RR_Company_StaffCount".Translate(campaign.Staff.Count));
                    listing.Label("RR_Company_Insights".Translate(campaign.ResearchInsights));
                    long outstanding = campaign.Obligations.Where(o => !o.Paid).Sum(o => o.AmountUsd);
                    listing.Label("RR_Company_Outstanding".Translate(Money(outstanding)));
                    if (outstanding > 0 && listing.ButtonText("RR_Company_PayOutstanding".Translate()))
                    {
                        CompanyActionResult result = campaign.PayOutstandingObligations();
                        if (!result.Success) { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
                    }
                    listing.Gap(12f);
                    listing.Label("RR_Company_OpeningObjective".Translate());
                    if (campaign.Headquarters != null)
                    {
                        if (listing.ButtonText("RR_Company_OpenHeadquarters".Translate()))
                        {
                            CameraJumper.TryJump(campaign.Headquarters.Center, campaign.Headquarters);
                        }
                    }
                    else { listing.Label("RR_Company_MapUnavailable".Translate()); }
                    break;
            }
        }

        private static string Money(long amount) { return amount.ToString("N0", CultureInfo.CurrentCulture); }
        private static string Observation(bool recorded) { return (recorded ? "RR_UI_ObservationRecorded" : "RR_UI_ObservationMissing").Translate().ToString(); }
        private static int Day(int tick) { return tick / GenDate.TicksPerDay + 1; }
        private static void ShowResult(CompanyActionResult result)
        {
            if (!result.Success) { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
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
