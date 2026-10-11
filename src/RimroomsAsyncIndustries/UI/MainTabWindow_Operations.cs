using System.Globalization;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Investigation;
using RimroomsAsyncIndustries.Scenario;
using RimWorld;
using UnityEngine;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

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
                    // Two paragraphs for one state. The short one says what is wrong, the longer
                    // one says what to do about it, and a player who already knows does not need
                    // to read it again every time they open the tab.
                    DrawHeading(listing, heading: "RR_Operations_Inactive".Translate(),
                        detail: "RR_Company_Inactive".Translate());
                    listing.Gap(8f);
                    if (ScenPart_RimroomsStart.Current != null && Find.CurrentMap != null &&
                        listing.ButtonText("RR_UI_RetryCompanyRegistration".Translate()))
                    { ShowResult(ScenPart_RimroomsStart.Current.TryInitializeExistingHeadquarters(Find.CurrentMap)); }
                    // A colony begun on any other scenario founds its branch here instead.
                    if (BranchFounding.Available(Find.CurrentMap))
                    {
                        listing.Label("RR_Founding_Desc".Translate());
                        if (listing.ButtonText("RR_Founding_Button".Translate()))
                        { ShowResult(BranchFounding.Found(Find.CurrentMap)); }
                    }
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
            // **THE BALANCE CARRIES ITS OWN EXPLANATION NOW, ON EVERY PANE.** The twenty-one
            // words about company USD being an accounting balance rather than physical silver
            // were a paragraph in the overview and again in the ledger; they belong on the
            // number they are about, where they are one hover away from wherever the player is.
            DrawHeading(listing, heading: "RR_Company_Balance".Translate(Money(campaign.BalanceUsd)),
                detail: "RR_Company_CashExplanation".Translate());
            listing.GapLine();
            DrawOpeningRetry(listing, campaign);
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
                    // The cash explanation moved onto the balance line above, which is on every
                    // pane including this one. What is left here is the one thing specific to
                    // the ledger: how far back the list goes.
                    DrawHeading(listing, heading: "RR_UI_LedgerTitle".Translate(),
                        detail: "RR_UI_LedgerRecent".Translate());
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
                            // The thirty words about when a replacement may be placed are the
                            // terms of this one offer, so they live on the offer.
                            if (DrawAction(listing, label: "RR_UI_FailedSiteRecovery".Translate(),
                                    refusal: TaggedString.Empty,
                                    detail: "RR_UI_FailedSiteRecoveryExplanation".Translate()))
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
                    DrawHeading(listing, heading: "RR_UI_LabTitle".Translate(),
                        detail: "RR_UI_LabInstructions".Translate());
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
                        {
                            // Fifty-seven words of field method, drawn once per unfinished
                            // record. Three records and it was the pane.
                            DrawHeading(listing,
                                heading: "RR_UI_EvidenceFieldWorkTitle".Translate(),
                                detail: "RR_UI_EvidenceFieldWorkRemaining".Translate());
                        }
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
                        DrawHeading(listing, heading: "RR_Debug_CounterTitle".Translate(),
                            detail: "RR_Debug_CounterNote".Translate());
                        if (listing.ButtonText("RR_Debug_CounterStart".Translate())) { Core.RimroomsDiagnostics.Start(); }
                        if (listing.ButtonText("RR_Debug_CounterStop".Translate())) { Core.RimroomsDiagnostics.Stop(); }
                        if (listing.ButtonText("RR_Debug_CounterLog".Translate())) { Core.RimroomsDiagnostics.WriteSnapshot(); }
                        if (listing.ButtonText("RR_Debug_RuntimeIdentity".Translate())) { Core.RimroomsDiagnostics.WriteRuntimeIdentity(); }
                        listing.GapLine();
                    }
                    if (campaign.Events.Count == 0) { listing.Label("RR_UI_NoRecords".Translate()); }
                    foreach (CompanyEventRecord activity in campaign.Events.Reverse())
                    {
                        string message = ActivityText(activity);
                        listing.Label("RR_UI_ActivityRow".Translate(Day(activity.Tick), message));
                        listing.Gap(4f);
                    }
                    break;
                default:
                    DrawOpeningObjective(listing, campaign);
                    // The cash explanation is on the balance line at the top of every pane now.
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
                    // **THE OBJECTIVE LINE ABOVE ALREADY SAYS WHICH STEP IS NEXT.** This is the
                    // standing opening brief, which is a different thing and was being read as a
                    // contradiction of it. Short title, brief on the hover, and the two no
                    // longer compete for the same slot.
                    DrawHeading(listing, heading: "RR_Company_OpeningBriefTitle".Translate(),
                        detail: "RR_Company_OpeningObjective".Translate());
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

        /// <summary>
        /// The branch is registered but the inside start never reached its opening, so the crew
        /// is still where it began. Offered on every pane until the opening completes.
        /// </summary>
        private static void DrawOpeningRetry(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            ScenPart_RimroomsStart start = ScenPart_RimroomsStart.Current;
            Map map = campaign.Headquarters ?? Find.CurrentMap;
            HeadquartersSetupComponent receipt = map == null ? null : map.GetComponent<HeadquartersSetupComponent>();
            if (start == null || receipt == null || !receipt.branchInitialized || receipt.openingComplete) { return; }
            DrawHeading(listing, heading: "RR_UI_OpeningIncomplete".Translate(),
                detail: string.IsNullOrEmpty(receipt.failure) ? TaggedString.Empty : receipt.failure.Translate());
            if (listing.ButtonText("RR_UI_RetryOpening".Translate()))
            { ShowResult(start.TryInitializeExistingHeadquarters(map)); }
            listing.GapLine();
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

        /// <summary>
        /// One activity row as text, and **never an exception.**
        ///
        /// Found playing, 2026-10-07: fifteen event keys were written as if the event's related id
        /// were their <c>{0}</c>, while `RecordEvent` stores that id apart from the format
        /// arguments. The first such row -- *"Finished paperwork collected for {0}. Company Account
        /// receipt: ${1} USD."* with one argument -- threw a FormatException on every frame the
        /// Activity pane drew, flooding the log and stalling the game's main thread. A row one
        /// argument short now takes the related id as its first; a row that still cannot be
        /// formatted shows its plain text rather than taking the window down.
        /// </summary>
        private static string ActivityText(CompanyEventRecord activity)
        {
            string format = activity.MessageKey.Translate().ToString();
            var values = activity.Arguments.Cast<object>().ToList();
            int wanted = 0;
            foreach (System.Text.RegularExpressions.Match match in
                System.Text.RegularExpressions.Regex.Matches(format, @"\{(\d+)"))
            { wanted = System.Math.Max(wanted, int.Parse(match.Groups[1].Value) + 1); }
            if (wanted == values.Count + 1) { values.Insert(0, activity.RelatedId ?? ""); }
            if (values.Count == 0) { return format; }
            try { return string.Format(CultureInfo.CurrentCulture, format, values.ToArray()); }
            catch (System.FormatException) { return format; }
        }
    }
}
