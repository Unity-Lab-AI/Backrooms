using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Investigation;
using RimroomsAsyncIndustries.Threats;
using Verse;

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
            string key;
            int pane;
            if (gate == null || !gate.AssemblyComplete) { key = "RR_UI_NextAssembly"; pane = 7; }
            else if (!gate.Calibrated) { key = "RR_UI_NextCalibration"; pane = 7; }
            else if (trips.Active?.Status == ExpeditionStatus.Stranded) { key = "RR_UI_NextRecovery"; pane = 8; }
            else if (trips.Active != null) { key = "RR_UI_NextFieldSurvey"; pane = 8; }
            else if (record == null || !record.RouteRecorded || !record.DistortionRecorded)
            { key = "RR_UI_NextDispatch"; pane = 8; }
            else if (record.Status != EvidenceStatus.Secured && record.Status != EvidenceStatus.Analyzed)
            { key = "RR_UI_NextRecoverEvidence"; pane = 8; }
            else if (record.Status != EvidenceStatus.Analyzed) { key = "RR_UI_NextAnalysis"; pane = 6; }
            else if (!campaign.HasRouteTelemetry) { key = "RR_UI_NextTelemetry"; pane = 6; }
            else { key = "RR_UI_NextRevisit"; pane = 8; }
            listing.Label("RR_UI_CurrentObjective".Translate());
            listing.Label(key.Translate());
            if (listing.ButtonText("RR_UI_OpenObjective".Translate()))
            { selectedPane = pane; scrollPosition = UnityEngine.Vector2.zero; }
            if (record?.Status == EvidenceStatus.Analyzed && trips.Active == null)
            {
                listing.Label("RR_UI_NextLeadChoice".Translate());
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
            { selectedGate = null; return null; }
            return selectedGate?.TryGetComp<CompRimroomsGate>();
        }

        private void DrawMachine(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            DrawNativeGateBinding(listing, campaign);
            DrawPortalNetwork(listing, campaign);
            CompRimroomsGate gate = CurrentGate(campaign);
            listing.Label((gate != null
                ? "RR_NativeGate_MachineInstructions" : "RR_UI_MachineInstructions").Translate());
            if (gate == null) { listing.Label("RR_NativeGate_NoSelectedGate".Translate()); return; }
            if (!gate.IsDesignated) { listing.Label("RR_NativeGate_BindBeforeOperation".Translate()); return; }
            if (listing.ButtonText("RR_UI_SelectMachine".Translate())) { CameraJumper.TryJumpAndSelect(gate.parent); }
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
            listing.Label("RR_UI_FieldObjectives".Translate());
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
                        listing.Label(fieldState.PursuerWithdrawn ? "RR_UI_EntityWithdrawn".Translate()
                            : "RR_UI_EntityLastRoom".Translate(fieldState.LastSeenPursuerRoom + 1));
                    }
                }
                if (!string.IsNullOrEmpty(run.FailureKey)) { listing.Label(run.FailureKey.Translate()); }
                if (run.Status == ExpeditionStatus.Staging && listing.ButtonText("RR_UI_AbortStaging".Translate())) { ShowResult(trips.AbortStaging()); }
                if ((run.Status == ExpeditionStatus.OnSite || run.Status == ExpeditionStatus.Returning) && listing.ButtonText("RR_UI_RecallCrew".Translate())) { ShowResult(trips.Recall()); }
                if (run.Status == ExpeditionStatus.Stranded)
                {
                    listing.Label("RR_UI_StrandedInstructions".Translate());
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
                    if (listing.ButtonText("RR_UI_PlaceTag".Translate(selected.LabelShortCap))) { ShowResult(site.QueueDeployAid(selected)); }
                    foreach (EvidenceRecord record in campaign.Evidence.Where(e => e.CoordinateId == run.CoordinateId && e.Item != null && e.Item.Spawned && e.Item.Map == selected.Map && !e.Item.Position.Fogged(selected.Map)))
                    {
                        if (listing.ButtonText("RR_UI_RecoverEvidence".Translate(selected.LabelShortCap)))
                        { ShowResult(ExpeditionCargo.QueuePickup(selected, record.Item, 1)); }
                    }
                    DrawRouteAidRecovery(listing, selected);
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
            { listing.Label("RR_UI_ResurveyPurpose".Translate()); }
            if (listing.ButtonText("RR_UI_SelectCoordinate".Translate(coordinate.Label)))
            {
                var options = new List<FloatMenuOption>();
                foreach (CoordinateRecord choice in campaign.Coordinates)
                { CoordinateRecord captured = choice; options.Add(new FloatMenuOption(choice.Label, () => selectedCoordinateId = captured.Id)); }
                Find.WindowStack.Add(new FloatMenu(options));
            }
            listing.Label("RR_UI_DispatchInstructions".Translate());
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
            if (gate == null || !gate.IsDesignated)
            { listing.Label("RR_NativeGate_DispatchNeedsBoundGate".Translate()); }
            else if (listing.ButtonText("RR_UI_DispatchCrew".Translate()))
            { ShowResult(trips.Dispatch(gate, coordinate, new List<Pawn>(selectedCrew))); }
        }

        private static void DrawRouteAidRecovery(Listing_Standard listing, Pawn pawn)
        {
            // One kind of route aid since the beacon was retired in 0.9.9-dev.
            foreach (string defName in new[] { "RR_SurveyTag" })
            {
                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                if (definition == null) { continue; }
                foreach (Thing item in pawn.Map.listerThings.ThingsOfDef(definition).Where(t => t.TryGetComp<CompRouteAid>()?.Deployed == true).ToList())
                {
                    if (!listing.ButtonText("RR_UI_RecoverRouteAid".Translate(pawn.LabelShortCap, item.LabelCap))) { continue; }
                    bool forbidden = item.IsForbidden(pawn);
                    item.SetForbidden(false, false);
                    CompanyActionResult result = ExpeditionCargo.QueuePickup(pawn, item, 1);
                    if (!result.Success) { item.SetForbidden(forbidden, false); }
                    ShowResult(result);
                }
            }
        }
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
