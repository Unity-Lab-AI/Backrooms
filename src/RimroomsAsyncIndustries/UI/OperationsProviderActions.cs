using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        /// <summary>
        /// Company vehicles and the gravship, as buttons onto the providers' own surfaces. With a
        /// provider absent every action still draws, disabled, with the reason on it.
        /// </summary>
        private void DrawCompanyVehicles(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            Map map = Find.CurrentMap;
            List<Pawn> vehicles = CompanyVehicles.VehiclesOn(map);
            DrawHeading(listing, heading: "RR_Vehicle_Heading".Translate(vehicles.Count),
                detail: "RR_Vehicle_Detail".Translate());
            bool surface = CompanyVehicles.IsCompanySurface(campaign, map);
            TaggedString formRefusal = !CompanyVehicles.FrameworkAvailable ? "RR_Vehicle_FrameworkAbsent".Translate()
                : !surface ? "RR_Vehicle_NotCompanyMap".Translate()
                : vehicles.Count == 0 ? "RR_Vehicle_NoneHere".Translate() : TaggedString.Empty;
            if (DrawAction(listing, "RR_Vehicle_FormCaravan".Translate(), formRefusal))
            { Report(CompanyVehicles.OpenCaravanFormation(campaign, map)); }
            for (int index = 0; index < vehicles.Count && index < 6; index++)
            {
                Pawn vehicle = vehicles[index];
                TaggedString cargoRefusal = surface ? TaggedString.Empty : "RR_Vehicle_NotCompanyMap".Translate();
                if (DrawAction(listing, "RR_Vehicle_LoadCargo".Translate(vehicle.LabelShortCap,
                    CompanyVehicles.CarriedMass(vehicle).ToString("F1")), cargoRefusal))
                { Report(CompanyVehicles.OpenCargo(campaign, vehicle)); }
            }
            // Drawn refused every time, so the rule is visible rather than discovered.
            DrawAction(listing, "RR_Vehicle_ThroughGate".Translate(),
                CompanyVehicles.ThroughGate().MessageKey.Translate());

            TaggedString gravRefusal = !ModsConfig.OdysseyActive ? "RR_Gravship_OdysseyAbsent".Translate()
                : map != null && map.IsPocketMap ? "RR_Gravship_PocketMap".Translate()
                : !surface ? "RR_Vehicle_NotCompanyMap".Translate()
                : CompanyVehicles.GravEngineOn(map) == null ? "RR_Gravship_NoEngine".Translate() : TaggedString.Empty;
            if (DrawAction(listing, "RR_Gravship_SelectEngine".Translate(), gravRefusal,
                "RR_Gravship_Detail".Translate()))
            { Report(CompanyVehicles.SelectGravEngine(campaign, map)); }
        }

        /// <summary>
        /// Branch dossiers: write one, write a kept one again, accept files from the shared
        /// folder, and the provider route refused with its reason.
        /// </summary>
        private void DrawDossiers(Listing_Standard listing)
        {
            RimroomsDossierExchangeComponent exchange = Current.Game?.GetComponent<RimroomsDossierExchangeComponent>();
            if (exchange == null) { return; }
            DrawHeading(listing, heading: "RR_Dossier_Heading".Translate(exchange.Outbound.Count, exchange.Inbound.Count),
                detail: "RR_Dossier_Detail".Translate(RimroomsDossierExchangeComponent.Folder));
            TaggedString fault = exchange.FaultKey == null ? TaggedString.Empty : exchange.FaultKey.Translate();
            if (DrawAction(listing, "RR_Dossier_Export".Translate(), fault))
            {
                CompanyActionResult result = exchange.Export(out string written);
                if (result.Success)
                { Messages.Message("RR_Dossier_Exported".Translate(written), MessageTypeDefOf.TaskCompletion, false); }
                else { Report(result); }
            }
            DrawAction(listing, "RR_Dossier_SendProvider".Translate(),
                RimroomsDossierExchangeComponent.SendThroughProvider().MessageKey.Translate());
            IReadOnlyList<DossierOutbound> sent = exchange.Outbound;
            for (int index = sent.Count - 1; index >= 0 && index >= sent.Count - 3; index--)
            {
                DossierOutbound entry = sent[index];
                listing.Label(entry.Acknowledged
                    ? "RR_Dossier_SentAcknowledged".Translate(entry.Sequence, entry.AcknowledgedBy)
                    : "RR_Dossier_SentPending".Translate(entry.Sequence));
                if (DrawAction(listing, "RR_Dossier_Rewrite".Translate(entry.Sequence), TaggedString.Empty))
                { Report(exchange.Rewrite(entry)); }
            }
            List<string> pending = exchange.PendingFiles();
            for (int index = 0; index < pending.Count && index < 6; index++)
            {
                string name = pending[index];
                if (DrawAction(listing, "RR_Dossier_Import".Translate(name), fault))
                {
                    CompanyActionResult result = exchange.Import(name);
                    if (result.Success)
                    { Messages.Message("RR_Dossier_Imported".Translate(name), MessageTypeDefOf.TaskCompletion, false); }
                    else { Report(result); }
                }
            }
            IReadOnlyList<DossierInbound> received = exchange.Inbound;
            for (int index = received.Count - 1; index >= 0 && index >= received.Count - 3; index--)
            {
                DossierInbound entry = received[index];
                listing.Label("RR_Dossier_ReceivedRow".Translate(entry.SourceCompany, entry.Sequence, entry.BalanceUsd,
                    entry.CasesOpen, entry.CasesClosed, entry.EvidenceHeld, entry.EvidenceAnalyzed, entry.ResearchInsights));
            }
        }

        private static void Report(CompanyActionResult result)
        {
            if (result != null && !result.Success && result.MessageKey != null)
            { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
        }
    }
}
