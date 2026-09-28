using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Procurement;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private string procurementCatalogDefName;
        private string procurementQuantityBuffer = "100";
        private int procurementReceivingZoneId = -1;
        private int procurementOrderPage;

        private void DrawProcurement(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Procurement_Title".Translate());
            listing.Label("RR_Procurement_BranchBalance".Translate(Money(campaign.BalanceUsd)));
            listing.Label("RR_Procurement_EstimateNotice".Translate());
            listing.GapLine();

            RimroomsProcurementComponent procurement = Current.Game == null ? null : Current.Game.GetComponent<RimroomsProcurementComponent>();
            if (procurement == null) { listing.Label("RR_Procurement_ComponentUnavailable".Translate()); return; }
            if (procurement.StateFaultKey != null) { listing.Label(procurement.StateFaultKey.Translate()); return; }
            if (campaign.Headquarters == null || campaign.Headquarters.Disposed)
            { listing.Label("RR_Proc_HeadquartersUnavailable".Translate()); return; }

            IReadOnlyList<RimroomsProcurementCatalogDef> catalog = procurement.AvailableCatalog();
            List<Zone_Stockpile> zones = HeadquartersStockpiles(campaign);
            RimroomsProcurementCatalogDef selectedCatalog = SelectedCatalog(catalog);
            Zone_Stockpile selectedZone = zones.FirstOrDefault(zone => zone.ID == procurementReceivingZoneId);
            if (selectedZone == null && zones.Count > 0)
            { selectedZone = zones[0]; procurementReceivingZoneId = selectedZone.ID; }

            listing.Label("RR_Procurement_OrderInstructions".Translate());
            if (catalog.Count == 0) { listing.Label("RR_Proc_CatalogUnavailable".Translate()); }
            else if (listing.ButtonText("RR_Procurement_SelectItem".Translate(selectedCatalog.LabelCap)))
            { OpenCatalogMenu(catalog); }

            if (zones.Count == 0) { listing.Label("RR_Proc_NoStockpiles".Translate()); }
            else if (listing.ButtonText("RR_Procurement_SelectStockpile".Translate(selectedZone == null ? "" : selectedZone.label)))
            { OpenReceivingZoneMenu(zones, selectedCatalog == null ? null : selectedCatalog.ItemDef); }

            listing.Label("RR_Procurement_Quantity".Translate());
            procurementQuantityBuffer = Widgets.TextField(listing.GetRect(30f), procurementQuantityBuffer ?? "");
            int quantity;
            bool quantityValid = int.TryParse(procurementQuantityBuffer, NumberStyles.Integer, CultureInfo.InvariantCulture, out quantity) && quantity > 0;
            if (selectedCatalog != null && quantityValid)
            {
                ThingDef itemDef = selectedCatalog.ItemDef;
                long estimatedTotal = 0;
                try { estimatedTotal = checked(selectedCatalog.unitPriceUsd * quantity); }
                catch (OverflowException) { quantityValid = false; }
                if (quantity > selectedCatalog.maxOrderQuantity)
                { listing.Label("RR_Proc_QuantityLimit".Translate(selectedCatalog.maxOrderQuantity)); quantityValid = false; }
                else if (itemDef != null && quantity > procurement.MaximumOrderQuantityFor(itemDef))
                { listing.Label("RR_Proc_QuantityLogisticsLimit".Translate(procurement.MaximumOrderQuantityFor(itemDef))); quantityValid = false; }
                else if (itemDef != null && selectedZone != null)
                {
                    int limit = itemDef.stackLimit < 1 ? 1 : itemDef.stackLimit;
                    long stackCount = ((long)quantity + limit - 1L) / limit;
                    float mass = itemDef.GetStatValueAbstract(StatDefOf.Mass) * quantity;
                    listing.Label("RR_Procurement_Preview".Translate(quantity, estimatedTotal.ToString("N0", CultureInfo.CurrentCulture),
                        stackCount.ToString("N0", CultureInfo.CurrentCulture), mass.ToString("N1", CultureInfo.CurrentCulture)));
                    listing.Label("RR_Procurement_ReceivingTarget".Translate(selectedZone.label));
                }
            }
            else if (!string.IsNullOrWhiteSpace(procurementQuantityBuffer))
            { listing.Label("RR_Proc_InvalidQuantity".Translate()); }

            if (selectedCatalog != null && selectedZone != null && quantityValid && listing.ButtonText("RR_Procurement_GetQuote".Translate()))
            {
                ProcurementQuoteRecord quote;
                CompanyActionResult result = procurement.CreateQuote(campaign, selectedCatalog.defName, quantity, selectedZone, out quote);
                ShowResult(result);
            }

            listing.GapLine();
            listing.Label("RR_Procurement_QuotesHeading".Translate());
            int now = Find.TickManager.TicksGame;
            List<ProcurementQuoteRecord> liveQuotes = procurement.Quotes.Reverse()
                .Where(quote => quote != null && !quote.Accepted && quote.ExpiresTick >= now).Take(8).ToList();
            if (liveQuotes.Count == 0) { listing.Label("RR_Proc_NoOpenQuotes".Translate()); }
            foreach (ProcurementQuoteRecord quote in liveQuotes)
            {
                ThingDef itemDef = DefDatabase<ThingDef>.GetNamedSilentFail(quote.ThingDefName);
                int currentLimit = itemDef == null || itemDef.stackLimit < 1 ? 1 : itemDef.stackLimit;
                long currentStacks = ((long)quote.Quantity + currentLimit - 1L) / currentLimit;
                listing.Label("RR_Proc_QuoteLine".Translate(quote.ThingLabel, quote.Quantity,
                    quote.TotalPriceUsd.ToString("N0", CultureInfo.CurrentCulture), quote.ReceivingZoneLabel));
                listing.Label("RR_Proc_QuoteBurden".Translate(quote.StackCountAtQuote,
                    currentStacks.ToString("N0", CultureInfo.CurrentCulture), quote.EstimatedMassKg.ToString("N1", CultureInfo.CurrentCulture)));
                listing.Label("RR_Proc_QuoteTiming".Translate(DaysUntil(quote.DispatchTick, now), DaysUntil(quote.ArrivalTick, now),
                    DaysUntil(quote.ExpiresTick, now)));
                if (listing.ButtonText("RR_Procurement_AcceptQuote".Translate(quote.TotalPriceUsd.ToString("N0", CultureInfo.CurrentCulture))))
                {
                    ProcurementQuoteRecord captured = quote;
                    Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                        "RR_Proc_ConfirmPurchase".Translate(captured.ThingLabel, captured.Quantity,
                            captured.TotalPriceUsd.ToString("N0", CultureInfo.CurrentCulture), captured.ReceivingZoneLabel),
                        delegate
                        {
                            ShowResult(procurement.AcceptQuote(campaign, captured.Id));
                        }));
                }
                listing.Gap(8f);
            }

            listing.GapLine();
            listing.Label("RR_Procurement_OrderHistoryHeading".Translate());
            listing.Label("RR_Proc_ArchiveSummary".Translate(
                procurement.ArchivedOrderCount.ToString("N0", CultureInfo.CurrentCulture),
                procurement.ArchivedDeliveredOrderCount.ToString("N0", CultureInfo.CurrentCulture),
                procurement.ArchivedCancelledOrderCount.ToString("N0", CultureInfo.CurrentCulture),
                procurement.ArchivedDeliveredQuantity.ToString("N0", CultureInfo.CurrentCulture)));
            const int pageSize = 12;
            List<ProcurementOrderRecord> allOrders = procurement.Orders.Reverse().ToList();
            int pageCount = Math.Max(1, (allOrders.Count + pageSize - 1) / pageSize);
            procurementOrderPage = Mathf.Clamp(procurementOrderPage, 0, pageCount - 1);
            listing.Label("RR_Procurement_OrderPage".Translate(procurementOrderPage + 1, pageCount));
            if (procurementOrderPage > 0 && listing.ButtonText("RR_Procurement_PreviousOrders".Translate()))
            { procurementOrderPage--; }
            if (procurementOrderPage + 1 < pageCount && listing.ButtonText("RR_Procurement_NextOrders".Translate()))
            { procurementOrderPage++; }
            foreach (ProcurementOrderRecord order in allOrders.Skip(procurementOrderPage * pageSize).Take(pageSize))
            { DrawProcurementOrder(listing, campaign, procurement, order, zones, now); }
        }

        private void DrawProcurementOrder(Listing_Standard listing, RimroomsCampaignComponent campaign,
            RimroomsProcurementComponent procurement, ProcurementOrderRecord order, List<Zone_Stockpile> zones, int now)
        {
            if (order == null) { return; }
            listing.Label("RR_Proc_OrderLine".Translate(order.Id, order.ThingLabel,
                order.Quantity.ToString("N0", CultureInfo.CurrentCulture),
                order.DeliveredQuantity.ToString("N0", CultureInfo.CurrentCulture),
                order.RemainingQuantity.ToString("N0", CultureInfo.CurrentCulture),
                ("RR_Proc_Status_" + order.Status).Translate()));
            listing.Label("RR_Proc_OrderTerms".Translate(order.TotalPriceUsd.ToString("N0", CultureInfo.CurrentCulture),
                order.ReceivingZoneLabel, DaysUntil(order.DispatchTick, now), DaysUntil(order.ArrivalTick, now)));
            ThingDef itemDef = DefDatabase<ThingDef>.GetNamedSilentFail(order.ThingDefName);
            if (itemDef != null)
            {
                int limit = itemDef.stackLimit < 1 ? 1 : itemDef.stackLimit;
                long currentStacks = ((long)order.RemainingQuantity + limit - 1L) / limit;
                listing.Label("RR_Proc_OrderCurrentStacks".Translate(currentStacks.ToString("N0", CultureInfo.CurrentCulture), limit));
            }
            if (!string.IsNullOrEmpty(order.FailureKey)) { listing.Label(order.FailureKey.Translate()); }
            if (order.Receipts.Count > 0)
            {
                ProcurementDeliveryReceipt receipt = order.Receipts[order.Receipts.Count - 1];
                listing.Label("RR_Proc_LatestReceipt".Translate(receipt.Id, receipt.QuantityDelivered, receipt.RemainingHeld,
                    receipt.ResultingThingLoadIds.Count));
            }
            if (order.ArchivedDeliveryReceiptCount > 0)
            {
                listing.Label("RR_Proc_ArchivedReceiptSummary".Translate(
                    order.ArchivedDeliveryReceiptCount.ToString("N0", CultureInfo.CurrentCulture),
                    order.ArchivedDeliveryQuantity.ToString("N0", CultureInfo.CurrentCulture),
                    order.FirstArchivedReceiptSequence.ToString("N0", CultureInfo.CurrentCulture),
                    order.LastArchivedReceiptSequence.ToString("N0", CultureInfo.CurrentCulture)));
            }
            foreach (ProcurementRouteChangeRecord change in order.RouteChanges.Skip(Math.Max(0, order.RouteChanges.Count - 3)))
            { listing.Label("RR_Proc_RouteChange".Translate(change.OldZoneLabel, change.NewZoneLabel, Day(change.Tick))); }

            if (order.Status == ProcurementOrderStatus.PaymentPending && listing.ButtonText("RR_Procurement_RetryPayment".Translate()))
            { ShowResult(procurement.AcceptQuote(campaign, order.Id)); }
            if ((order.Status == ProcurementOrderStatus.PartiallyDelivered || order.Status == ProcurementOrderStatus.AwaitingReceivingSpace) &&
                listing.ButtonText("RR_Procurement_RetryDelivery".Translate()))
            { ShowResult(procurement.RetryDelivery(campaign, order.Id)); }
            if (order.Status != ProcurementOrderStatus.Delivered && order.Status != ProcurementOrderStatus.Cancelled &&
                order.Status != ProcurementOrderStatus.CancelPending && order.Status != ProcurementOrderStatus.RecoveryRequired && zones.Count > 0 &&
                listing.ButtonText("RR_Procurement_ChangeReceiving".Translate()))
            { OpenOrderReceivingZoneMenu(procurement, campaign, order, zones); }
            if (order.Status == ProcurementOrderStatus.Scheduled && now < order.DispatchTick && listing.ButtonText("RR_Procurement_CancelOrder".Translate()))
            {
                Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation("RR_Proc_ConfirmCancellation".Translate(order.Id,
                    order.TotalPriceUsd.ToString("N0", CultureInfo.CurrentCulture)), delegate
                    { ShowResult(procurement.CancelOrder(campaign, order.Id)); }));
            }
            if (listing.ButtonText("RR_Procurement_InspectOrder".Translate())) { ShowOrderDetails(order); }
            listing.GapLine();
        }

        private RimroomsProcurementCatalogDef SelectedCatalog(IReadOnlyList<RimroomsProcurementCatalogDef> catalog)
        {
            RimroomsProcurementCatalogDef selected = catalog.FirstOrDefault(def => def.defName == procurementCatalogDefName);
            if (selected == null && catalog.Count > 0)
            { selected = catalog[0]; procurementCatalogDefName = selected.defName; }
            return selected;
        }

        private static List<Zone_Stockpile> HeadquartersStockpiles(RimroomsCampaignComponent campaign)
        {
            if (campaign.Headquarters == null || campaign.Headquarters.zoneManager == null) { return new List<Zone_Stockpile>(); }
            return campaign.Headquarters.zoneManager.AllZones.OfType<Zone_Stockpile>()
                .Where(zone => zone != null && zone.Map == campaign.Headquarters)
                .OrderBy(zone => zone.label, StringComparer.CurrentCultureIgnoreCase).ThenBy(zone => zone.ID).ToList();
        }

        private void OpenCatalogMenu(IReadOnlyList<RimroomsProcurementCatalogDef> catalog)
        {
            var options = new List<FloatMenuOption>();
            foreach (RimroomsProcurementCatalogDef entry in catalog)
            {
                RimroomsProcurementCatalogDef captured = entry;
                options.Add(new FloatMenuOption(captured.LabelCap + " - " + captured.thingDefName, delegate
                { procurementCatalogDefName = captured.defName; }));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private void OpenReceivingZoneMenu(List<Zone_Stockpile> zones, ThingDef itemDef)
        {
            var options = new List<FloatMenuOption>();
            foreach (Zone_Stockpile zone in zones)
            {
                Zone_Stockpile captured = zone;
                bool accepts = itemDef == null || (captured.settings != null && captured.settings.AllowedToAccept(itemDef));
                string label = captured.label + (accepts ? "" : " - " + "RR_Proc_ZoneFilterRejects".Translate().ToString());
                options.Add(new FloatMenuOption(label, accepts ? (Action)delegate { procurementReceivingZoneId = captured.ID; } : null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private static void OpenOrderReceivingZoneMenu(RimroomsProcurementComponent procurement, RimroomsCampaignComponent campaign,
            ProcurementOrderRecord order, List<Zone_Stockpile> zones)
        {
            ThingDef itemDef = DefDatabase<ThingDef>.GetNamedSilentFail(order.ThingDefName);
            var options = new List<FloatMenuOption>();
            foreach (Zone_Stockpile zone in zones)
            {
                Zone_Stockpile captured = zone;
                bool accepts = itemDef != null && captured.settings != null && captured.settings.AllowedToAccept(itemDef);
                string label = captured.label + (accepts ? "" : " - " + "RR_Proc_ZoneFilterRejects".Translate().ToString());
                options.Add(new FloatMenuOption(label, accepts ? (Action)delegate
                { ShowResult(procurement.ChangeReceivingZone(campaign, order.Id, captured)); } : null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private static void ShowOrderDetails(ProcurementOrderRecord order)
        {
            List<ProcurementDeliveryReceipt> recentReceipts = order.Receipts.Skip(Math.Max(0, order.Receipts.Count - 12)).ToList();
            string receipts = order.Receipts.Count == 0 ? "RR_Proc_NoReceipts".Translate().ToString()
                : string.Join("\n", recentReceipts.Select(receipt => receipt.Id + "  " + receipt.QuantityDelivered.ToString("N0", CultureInfo.CurrentCulture) +
                    " delivered / " + receipt.RemainingHeld.ToString("N0", CultureInfo.CurrentCulture) + " held"));
            if (order.Receipts.Count > recentReceipts.Count)
            { receipts = "RR_Proc_ReceiptsOmitted".Translate(order.Receipts.Count - recentReceipts.Count) + "\n" + receipts; }
            if (order.ArchivedDeliveryReceiptCount > 0)
            {
                receipts = "RR_Proc_ArchivedReceiptSummary".Translate(
                    order.ArchivedDeliveryReceiptCount.ToString("N0", CultureInfo.CurrentCulture),
                    order.ArchivedDeliveryQuantity.ToString("N0", CultureInfo.CurrentCulture),
                    order.FirstArchivedReceiptSequence.ToString("N0", CultureInfo.CurrentCulture),
                    order.LastArchivedReceiptSequence.ToString("N0", CultureInfo.CurrentCulture)) + "\n" + receipts;
            }
            string details = "RR_Proc_OrderDetails".Translate(order.Id, order.QuoteId, order.ThingLabel, order.ThingDefName,
                order.Quantity.ToString("N0", CultureInfo.CurrentCulture), order.DeliveredQuantity.ToString("N0", CultureInfo.CurrentCulture),
                order.RemainingQuantity.ToString("N0", CultureInfo.CurrentCulture), order.TotalPriceUsd.ToString("N0", CultureInfo.CurrentCulture),
                order.Status.ToString(), order.ReceivingZoneLabel, order.PaymentVerified.ToString(), order.CancelIntent.ToString(), receipts);
            Find.WindowStack.Add(new Dialog_MessageBox(details));
        }

        private static int DaysUntil(int targetTick, int now)
        { return Math.Max(0, (targetTick - now + GenDate.TicksPerDay - 1) / GenDate.TicksPerDay); }
    }
}
