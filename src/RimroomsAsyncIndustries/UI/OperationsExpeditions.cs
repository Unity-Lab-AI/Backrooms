using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Investigation;
using RimroomsAsyncIndustries.Threats;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private Thing selectedGate;
        private string selectedCoordinateId;
        private readonly List<Pawn> selectedCrew = new List<Pawn>();
        private Pawn selectedFieldWorker;

        private void DrawOpeningObjective(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            CompRimroomsGate gate = CurrentGate(campaign);
            RimroomsExpeditionComponent trips = Current.Game.GetComponent<RimroomsExpeditionComponent>();
            ContractRecord survey = campaign.Contracts.FirstOrDefault(c => c.TemplateId == "rr.survey.onboarding.v1");
            EvidenceRecord record = survey == null ? null : campaign.Evidence.FirstOrDefault(e => e.CoordinateId == survey.CoordinateId);
            // **TWO KEYS PER OBJECTIVE, AND THAT IS THE WHOLE REWRITE OF THIS LINE.** Owner:
            // *"things can be shortend and more concise and dirrect  with tools tips would less
            // cluter it"*. `brief` is the three or four words that say which objective this is;
            // `key` is the same instruction as before, every word of it, on the hover. The
            // objective line was between seventeen and thirty-five words of prose depending on
            // the branch, drawn as a paragraph above a button.
            string key;
            string brief;
            int pane;
            if (gate == null || !gate.AssemblyComplete)
            { key = "RR_UI_NextAssembly"; brief = "RR_UI_NextAssemblyBrief"; pane = 7; }
            else if (!gate.Calibrated)
            { key = "RR_UI_NextCalibration"; brief = "RR_UI_NextCalibrationBrief"; pane = 7; }
            else if (trips.Active?.Status == ExpeditionStatus.Stranded)
            { key = "RR_UI_NextRecovery"; brief = "RR_UI_NextRecoveryBrief"; pane = 8; }
            else if (trips.Active != null)
            { key = "RR_UI_NextFieldSurvey"; brief = "RR_UI_NextFieldSurveyBrief"; pane = 8; }
            else if (record == null || !record.RouteRecorded || !record.DistortionRecorded)
            { key = "RR_UI_NextDispatch"; brief = "RR_UI_NextDispatchBrief"; pane = 8; }
            else if (record.Status != EvidenceStatus.Secured && record.Status != EvidenceStatus.Analyzed)
            { key = "RR_UI_NextRecoverEvidence"; brief = "RR_UI_NextRecoverEvidenceBrief"; pane = 8; }
            else if (record.Status != EvidenceStatus.Analyzed)
            { key = "RR_UI_NextAnalysis"; brief = "RR_UI_NextAnalysisBrief"; pane = 6; }
            // **Review is the step between a finished report and the next lead**, and the
            // objective line is how the player learns the step exists at all.
            else if (campaign.AwaitsReview(record))
            { key = "RR_UI_NextReview"; brief = "RR_UI_NextReviewBrief"; pane = 6; }
            else if (!campaign.HasRouteTelemetry)
            { key = "RR_UI_NextTelemetry"; brief = "RR_UI_NextTelemetryBrief"; pane = 6; }
            else { key = "RR_UI_NextRevisit"; brief = "RR_UI_NextRevisitBrief"; pane = 8; }
            DrawHeading(listing, heading: "RR_UI_CurrentObjective".Translate(brief.Translate()),
                detail: key.Translate());
            if (listing.ButtonText("RR_UI_OpenObjective".Translate()))
            { selectedPane = pane; scrollPosition = UnityEngine.Vector2.zero; }
            if (record?.Status == EvidenceStatus.Analyzed && trips.Active == null)
            {
                DrawHeading(listing, heading: "RR_UI_NextLeadTitle".Translate(),
                    detail: "RR_UI_NextLeadChoice".Translate());
                if (!campaign.HasRouteTelemetry && listing.ButtonText("RR_UI_ReviewTelemetry".Translate()))
                { selectedPane = 6; scrollPosition = UnityEngine.Vector2.zero; }
                if (listing.ButtonText("RR_UI_PrepareResurvey".Translate()))
                { selectedCoordinateId = record.CoordinateId; selectedPane = 8; scrollPosition = UnityEngine.Vector2.zero; }
            }
            listing.GapLine();
        }

        private CompRimroomsGate CurrentGate(RimroomsCampaignComponent campaign)
        {
            RimroomsExpeditionComponent trips = Current.Game == null ? null : Current.Game.GetComponent<RimroomsExpeditionComponent>();
            ExpeditionRecord activeRun = trips == null ? null : trips.Active;
            if (activeRun != null)
            {
                // An active or stranded record owns its saved gate reference. Never retarget it to another door.
                return activeRun.Gate == null ? null : activeRun.Gate.TryGetComp<CompRimroomsGate>();
            }

            if (campaign == null || campaign.Headquarters == null || selectedGate == null || selectedGate.Destroyed ||
                !selectedGate.Spawned || selectedGate.Map != campaign.Headquarters || selectedGate.Faction != Faction.OfPlayer ||
                selectedGate.TryGetComp<CompRimroomsGate>() == null)
            {
                // **A BRANCH THAT HAS A GATE HAS A GATE, WHETHER OR NOT THIS WINDOW WAS TOLD.**
                // `selectedGate` is only ever assigned by *Select a door* in this pane, so a player
                // who designates the door from the door's own button -- which is the one-click path
                // this mod advertises, and the first thing anybody tries -- left this null. Every
                // reader of `CurrentGate` then behaved as though no gate existed: **the eleven-step
                // board read `0 of 11 complete` on a commissioned gate that was already paying out
                // its start-up goals**, and the objective line above sent the player to assemble a
                // gate they had built. Found by playing, 2026-10-07.
                //
                // The fallback asks the branch instead of the window: the headquarters' own
                // designated gate, from `AvailableNativeDoors`, which is already ordered
                // deterministically so a branch with two gates picks the same one every frame
                // rather than flickering between them. **It is a fallback and not a replacement** --
                // an explicit selection still wins, which is what lets a player with two gates
                // choose the other one.
                selectedGate = null;
                CompRimroomsGate designated = DesignatedGate(campaign);
                if (designated != null) { selectedGate = designated.parent; }
                return designated;
            }
            return selectedGate?.TryGetComp<CompRimroomsGate>();
        }

        /// <summary>
        /// The headquarters' own designated gate, or null when the branch has not made one yet.
        ///
        /// Asked of the same enumeration the *Select a door* menu offers, so this cannot drift from
        /// what that menu would have let the player pick.
        /// </summary>
        private static CompRimroomsGate DesignatedGate(RimroomsCampaignComponent campaign)
        {
            foreach (Building_Door door in AvailableNativeDoors(campaign))
            {
                CompRimroomsGate candidate = door.TryGetComp<CompRimroomsGate>();
                if (candidate != null && candidate.IsDesignated) { return candidate; }
            }
            return null;
        }

        private void DrawMachine(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            // **THE NUMBERED CHECKS FIRST.** Owner: *"the whole machine  tab needs to be numbered
            // and everything step 1 step 2... ect ect so fucking simple a 6 yr old chimp can do
            // it"*. Drawn above the binding and network panels because it is the thing that says
            // which of them to go and use, and in which order.
            DrawGateStartupChecks(listing, campaign);
            DrawNativeGateBinding(listing, campaign);
            DrawPortalNetwork(listing, campaign);
            CompRimroomsGate gate = CurrentGate(campaign);
            // **THE BOARD ABOVE ALREADY SAYS WHAT TO DO NEXT.** Owner: *"not every step having
            // its own type up of whats next"*. So this stops being a second set of
            // instructions and becomes the machine's controls, with the fifty-seven-word
            // version on the hover for anybody who wants the whole thing.
            DrawHeading(listing, heading: "RR_UI_MachineControlsTitle".Translate(),
                detail: (gate != null
                    ? "RR_NativeGate_MachineInstructions" : "RR_UI_MachineInstructions").Translate());
            // **THE CONTROLS STAY VISIBLE AND SAY WHY THEY ARE OFF**, rather than the pane
            // printing a sentence where a button would have been. A player who cannot find the
            // button cannot tell whether the sentence is about the button or about the game.
            if (gate == null)
            {
                DrawAction(listing, label: "RR_UI_SelectMachine".Translate(),
                    refusal: "RR_NativeGate_NoSelectedGate".Translate());
                return;
            }
            // Jumping to the door comes before the designation check now. The gate exists, so
            // the one control that always works should work -- and finding the thing on the map
            // is how a player answers *"which door did I pick"* for themselves.
            if (listing.ButtonText("RR_UI_SelectMachine".Translate())) { CameraJumper.TryJumpAndSelect(gate.parent); }
            if (!gate.IsDesignated)
            {
                DrawAction(listing, label: "RR_UI_CalibrateMachine".Translate(),
                    refusal: "RR_NativeGate_BindBeforeOperation".Translate());
                return;
            }
            listing.Label(gate.CompInspectStringExtra());
            listing.GapLine();
            foreach (StaffRecord member in campaign.Staff.Where(s => s.Employed && s.Pawn != null && s.Pawn.Spawned && s.Pawn.Map == campaign.Headquarters))
            {
                if (listing.ButtonText("RR_UI_AssignGateOperator".Translate(member.Name))) { ShowResult(gate.AssignOperator(member.Pawn)); }
            }
            if (listing.ButtonText("RR_UI_CalibrateMachine".Translate())) { ShowResult(gate.OrderCalibration()); }
            if (listing.ButtonText("RR_UI_StaffMachine".Translate())) { ShowResult(gate.OrderStaffConsole()); }
        }

        private void DrawExpedition(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            RimroomsExpeditionComponent trips = Current.Game.GetComponent<RimroomsExpeditionComponent>();
            ExpeditionRecord run = trips.Active;
            // Fifty-six words of what the contract wants, which a player needs once and then
            // never again. On the hover, in full, where it is available on the visit they do
            // need it.
            DrawHeading(listing, heading: "RR_UI_FieldObjectivesTitle".Translate(),
                detail: "RR_UI_FieldObjectives".Translate());
            if (trips.InterruptedTransfers.Count > 0 && listing.ButtonText("RR_UI_RecoverTransfers".Translate()))
            { ShowResult(trips.RecoverInterruptedTransfers()); }
            if (run == null)
            {
                DrawDispatch(listing, campaign, trips);
            }
            else
            {
                listing.Label("RR_UI_TripState".Translate(("RR_Exp_Status_" + run.Status).Translate()));
                FirstSliceSiteComponent fieldState = run.Destination?.GetComponent<FirstSliceSiteComponent>();
                if (fieldState != null && fieldState.OpeningId == run.ExpeditionId)
                {
                    listing.Label("RR_UI_FieldRuleState".Translate(Observation(fieldState.DistortionObserved)));
                    if (fieldState.EntityObserved)
                    {
                        // The room number is the readout; what to do about the thing in it is
                        // advice, and advice that repeats every frame stops being read.
                        if (fieldState.PursuerWithdrawn)
                        { listing.Label("RR_UI_EntityWithdrawn".Translate()); }
                        else
                        {
                            DrawHeading(listing,
                                heading: "RR_UI_EntityRoomBrief".Translate(fieldState.LastSeenPursuerRoom + 1),
                                detail: "RR_UI_EntityLastRoom".Translate(fieldState.LastSeenPursuerRoom + 1));
                        }
                    }
                }
                if (!string.IsNullOrEmpty(run.FailureKey)) { listing.Label(run.FailureKey.Translate()); }
                if (run.Status == ExpeditionStatus.Staging && listing.ButtonText("RR_UI_AbortStaging".Translate())) { ShowResult(trips.AbortStaging()); }
                if ((run.Status == ExpeditionStatus.OnSite || run.Status == ExpeditionStatus.Returning) && listing.ButtonText("RR_UI_RecallCrew".Translate())) { ShowResult(trips.Recall()); }
                if (run.Status == ExpeditionStatus.Stranded)
                {
                    DrawHeading(listing, heading: "RR_UI_StrandedTitle".Translate(),
                        detail: "RR_UI_StrandedInstructions".Translate());
                    if (listing.ButtonText("RR_UI_ReopenRecovery".Translate())) { ShowResult(trips.ReopenReturnRoute()); }
                    foreach (StaffRecord member in campaign.Staff.Where(s => s.Employed && s.Pawn != null && s.Pawn.Spawned && s.Pawn.Map == campaign.Headquarters && !run.InitialCrew.Contains(s.Pawn)))
                    {
                        if (listing.ButtonText("RR_UI_LoadRelief".Translate(member.Name))) { ShowResult(trips.QueueReliefLoadout(member.Pawn)); }
                        if (listing.ButtonText("RR_UI_SendRelief".Translate(member.Name))) { ShowResult(trips.SendRelief(member.Pawn)); }
                    }
                }
                listing.GapLine();
                List<Pawn> members = run.InitialCrew.Concat(run.RescueCrew).Concat(run.RecoveryPassengers).Where(p => p != null).Distinct().ToList();
                foreach (Pawn pawn in members)
                {
                    string location = pawn.Dead ? "RR_UI_CrewDead" : pawn.MapHeld == campaign.Headquarters ? "RR_UI_CrewHome"
                        : pawn.MapHeld == run.Destination ? "RR_UI_CrewOnSite" : "RR_UI_CrewUnknown";
                    listing.Label("RR_UI_CrewRow".Translate(pawn.LabelShortCap, location.Translate()));
                    if (pawn.Spawned && listing.ButtonText("RR_UI_SelectFieldWorker".Translate(pawn.LabelShortCap)))
                    { selectedFieldWorker = pawn; CameraJumper.TryJumpAndSelect(pawn); }
                }
                Pawn selected = selectedFieldWorker;
                if (selected != null && members.Contains(selected) && selected.Spawned && selected.Map == run.Destination && !selected.Dead && !selected.Downed)
                {
                    FirstSliceSiteComponent site = selected.Map.GetComponent<FirstSliceSiteComponent>();
                    if (site.DeploymentRecoveryCount > 0 && listing.ButtonText("RR_UI_RecoverRoutePlacement".Translate()))
                    { ShowResult(site.RecoverDeploymentItems(selected)); }
                    foreach (EvidenceRecord record in campaign.Evidence.Where(e => e.CoordinateId == run.CoordinateId && e.Item != null && e.Item.Spawned && e.Item.Map == selected.Map && !e.Item.Position.Fogged(selected.Map)))
                    {
                        if (listing.ButtonText("RR_UI_RecoverEvidence".Translate(selected.LabelShortCap)))
                        { ShowResult(ExpeditionCargo.QueuePickup(selected, record.Item, 1)); }
                    }
                    DrawSalvageRecovery(listing, selected);
                    foreach (Pawn casualty in members.Concat(trips.RecoverableCrewAtActiveSite()).Distinct().Where(p => p != selected && (p.Downed || p.Dead) && (p.Dead ? p.Corpse?.MapHeld : p.MapHeld) == run.Destination))
                    {
                        if (listing.ButtonText("RR_UI_CarryCasualty".Translate(selected.LabelShortCap, casualty.LabelShortCap)))
                        { ShowResult(trips.QueueCasualtyReturn(selected, casualty)); }
                    }
                }
                foreach (Pawn survivor in trips.RecoverableCrewAtActiveSite().Where(p => !p.Dead && !p.Downed))
                {
                    if (listing.ButtonText("RR_UI_RecoverHistoricalSurvivor".Translate(survivor.LabelShortCap)))
                    { ShowResult(trips.QueueRecoveredCrewReturn(survivor)); }
                }
                if (trips.CanAbandonExpedition(run.ExpeditionId).Success && listing.ButtonText("RR_UI_ReviewAbandon".Translate()))
                { Find.WindowStack.Add(new Dialog_ExpeditionClosure(run)); }
                listing.GapLine();
                DrawManifest(listing, run);
            }
            listing.GapLine();
            foreach (ExpeditionRecord past in trips.Records.Where(r => r.Closed).Reverse().Take(5))
            {
                listing.Label("RR_UI_TripHistory".Translate(past.ExpeditionId, ("RR_Exp_Status_" + past.Status).Translate(), past.ReturnedCrew.Count, past.InitialCrew.Count));
                if (past.Status == ExpeditionStatus.Abandoned && trips.Active == null && listing.ButtonText("RR_UI_ResumeRecovery".Translate()))
                { ShowResult(trips.ResumeAbandonedExpedition(past.ExpeditionId)); }
                foreach (ExpeditionClosureRecord closure in past.ClosureHistory.Reverse().Take(3))
                { listing.Label("RR_UI_ClosureHistory".Translate(closure.Reason)); }
                DrawManifest(listing, past);
            }
        }

        private void DrawDispatch(Listing_Standard listing, RimroomsCampaignComponent campaign, RimroomsExpeditionComponent trips)
        {
            CoordinateRecord coordinate = campaign.Coordinates.FirstOrDefault(c => c.Id == selectedCoordinateId) ?? campaign.Coordinates.FirstOrDefault();
            if (coordinate == null) { listing.Label("RR_UI_NoCoordinate".Translate()); return; }
            selectedCoordinateId = coordinate.Id;
            if (campaign.Evidence.Any(e => e.CoordinateId == coordinate.Id && e.Status == EvidenceStatus.Analyzed))
            {
                // **The short line keeps the part a player can be caught out by** -- that the
                // survey payment does not come twice. The rest of the forty words is what
                // persists and what can still be done there, which is reference, not a warning.
                DrawHeading(listing, heading: "RR_UI_ResurveyTitle".Translate(),
                    detail: "RR_UI_ResurveyPurpose".Translate());
            }
            if (listing.ButtonText("RR_UI_SelectCoordinate".Translate(coordinate.Label)))
            {
                var options = new List<FloatMenuOption>();
                foreach (CoordinateRecord choice in campaign.Coordinates)
                { CoordinateRecord captured = choice; options.Add(new FloatMenuOption(choice.Label, () => selectedCoordinateId = captured.Id)); }
                Find.WindowStack.Add(new FloatMenu(options));
            }
            DrawHeading(listing, heading: "RR_UI_DispatchTitle".Translate(),
                detail: "RR_UI_DispatchInstructions".Translate());
            selectedCrew.RemoveAll(p => p == null || !p.Spawned || p.Map != campaign.Headquarters || p.Dead || !campaign.Staff.Any(s => s.Pawn == p && s.Employed));
            foreach (StaffRecord member in campaign.Staff.Where(s => s.Employed && s.Pawn != null && s.Pawn.Spawned && s.Pawn.Map == campaign.Headquarters && !s.Pawn.Dead))
            {
                bool selected = selectedCrew.Contains(member.Pawn);
                listing.CheckboxLabeled(member.Name + " — " + ("RR_Role_" + member.Role).Translate(), ref selected);
                if (selected && !selectedCrew.Contains(member.Pawn)) { selectedCrew.Add(member.Pawn); }
                else if (!selected) { selectedCrew.Remove(member.Pawn); }
            }
            if (listing.ButtonText("RR_UI_LoadSharedKit".Translate())) { ShowResult(trips.QueueLoadout(new List<Pawn>(selectedCrew))); }
            CompanyActionResult kit = ExpeditionCargo.CheckKit(selectedCrew);
            listing.Label(kit.Success ? "RR_UI_KitReady".Translate() : kit.MessageKey.Translate());
            CompRimroomsGate gate = CurrentGate(campaign);
            // Row 728. Drawn before the dispatch button on purpose: the whole value of it is
            // being able to read why somebody is unready *instead of* pressing the button and
            // being told "invalid crew".
            listing.GapLine();
            DrawCrewPlanner(listing, campaign, gate);
            listing.GapLine();
            // **THE DISPATCH BUTTON IS ALWAYS THERE.** It used to be replaced by a sentence
            // explaining its absence, which is the worst version of both: the player loses the
            // control AND reads a paragraph. Disabled with the reason on it instead.
            if (DrawAction(listing, label: "RR_UI_DispatchCrew".Translate(),
                    refusal: gate == null || !gate.IsDesignated
                        ? "RR_NativeGate_DispatchNeedsBoundGate".Translate()
                        : TaggedString.Empty))
            {
                // **ANNOUNCED, because dispatching to an unresolved coordinate builds its map.**
                //
                // `Dispatch` reaches `EnsureSite`, and this path was recorded as exempt from the
                // freeze notice because *the result is read by its caller*. That reason described
                // the method and not the call: **this is a button**, the result is read inside the
                // callback, and moving the whole `ShowResult(Dispatch(...))` into the notice's
                // continuation is exactly the shape `OperationsPortalNetwork` already uses for its
                // two openings. A long event is legal wherever nothing *outside* the callback is
                // waiting, which is here.
                //
                // The crew list is copied before the lambda for the reason it was already being
                // copied: `selectedCrew` is pane state the player can change, and the dispatch
                // now happens a frame or more later.
                var dispatching = new List<Pawn>(selectedCrew);
                Presentation.RimroomsGenerationNotice.Announce(coordinate, delegate
                { ShowResult(trips.Dispatch(gate, coordinate, dispatching)); });
            }
        }

        // Recovering a marker is an ordinary uninstall order on an ordinary Core building
        // now, so the panel that used to list every deployed survey tag and offer to pick it
        // up has nothing left to do. Removed rather than left showing an empty list.
        private static void DrawManifest(Listing_Standard listing, ExpeditionRecord run)
        {
            listing.Label("RR_UI_CargoManifest".Translate());
            if (listing.ButtonText("RR_UI_RefreshCargo".Translate()))
            { ShowResult(Current.Game.GetComponent<RimroomsExpeditionComponent>().RefreshManifest(run.ExpeditionId)); }
            foreach (CargoManifestEntry entry in run.Cargo)
            {
                listing.Label("RR_UI_CargoRow".Translate(entry.Label, entry.OriginalCount, entry.ObservedCount,
                    ("RR_Cargo_Location_" + entry.Location).Translate(), entry.Damaged ? "RR_UI_Damaged".Translate().ToString() : ""));
                if (entry.Declaration != CargoDisposition.Unspecified)
                {
                    listing.Label("RR_UI_CargoDeclaration".Translate(("RR_Cargo_" + entry.Declaration).Translate(), entry.DeclaredCount, entry.Note));
                    if (entry.DeclarationNeedsReview) { listing.Label("RR_UI_DeclarationNeedsReview".Translate()); }
                }
                if (listing.ButtonText("RR_UI_DeclareCargo".Translate(entry.Label)))
                { Find.WindowStack.Add(new Dialog_CargoDeclaration(entry)); }
            }
        }
    }
}
