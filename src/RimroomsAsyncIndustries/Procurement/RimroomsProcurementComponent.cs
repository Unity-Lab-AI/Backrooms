using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Procurement
{
    /// <summary>RR-ECO/RR-FAC: branch-local orders and physical supplier cargo.</summary>
    public sealed class RimroomsProcurementComponent : GameComponent, IThingHolder
    {
        private const int CurrentSchemaVersion = 1;
        private const int QuoteLifetimeTicks = 25000;
        private const int RetryDelayTicks = 2500;
        private const int ProcessingIntervalTicks = 250;
        private const int MaximumPhysicalStacksPerOrder = 4096;
        private const int MaximumStacksDeliveredPerTick = 4;
        private const int MaximumSavedQuotes = 100;
        private const int MaximumOpenOrders = 100;
        private const int MaximumSavedOrders = 512;
        private const int MaximumDetailedDeliveryReceiptsPerOrder = 64;
        private const int MaximumRouteChangesPerOrder = 128;
        private const int MaximumHeldStacksAcrossOrders = 8192;
        private const int MaximumActiveQuantity = 1000000;

        private int schemaVersion = CurrentSchemaVersion;
        private long nextOrderSequence = 1;
        private List<ProcurementQuoteRecord> quotes = new List<ProcurementQuoteRecord>();
        private List<ProcurementOrderRecord> orders = new List<ProcurementOrderRecord>();
        private long archivedOrderCount;
        private long archivedDeliveredOrderCount;
        private long archivedCancelledOrderCount;
        private long archivedDeliveredQuantity;
        private ThingOwner<Thing> heldCargo;
        private string stateFaultKey;
        private bool ledgerValidationPending;

        public RimroomsProcurementComponent(Game game)
        {
            heldCargo = new ThingOwner<Thing>(this);
        }

        public IReadOnlyList<ProcurementQuoteRecord> Quotes { get { return quotes; } }
        public IReadOnlyList<ProcurementOrderRecord> Orders { get { return orders; } }
        public long ArchivedOrderCount { get { return archivedOrderCount; } }
        public long ArchivedDeliveredOrderCount { get { return archivedDeliveredOrderCount; } }
        public long ArchivedCancelledOrderCount { get { return archivedCancelledOrderCount; } }
        public long ArchivedDeliveredQuantity { get { return archivedDeliveredQuantity; } }
        public string StateFaultKey { get { return stateFaultKey; } }
        public IThingHolder ParentHolder { get { return null; } }
        public ThingOwner GetDirectlyHeldThings() { return heldCargo; }
        public void GetChildHolders(List<IThingHolder> outChildren)
        { ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, heldCargo); }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_procurementSchema", CurrentSchemaVersion, forceSave: true);
            Scribe_Values.Look(ref nextOrderSequence, "rr_procurementNextOrder", 1L);
            Scribe_Collections.Look(ref quotes, "rr_procurementQuotes", LookMode.Deep);
            Scribe_Collections.Look(ref orders, "rr_procurementOrders", LookMode.Deep);
            Scribe_Values.Look(ref archivedOrderCount, "rr_procurementArchivedOrders");
            Scribe_Values.Look(ref archivedDeliveredOrderCount, "rr_procurementArchivedDeliveredOrders");
            Scribe_Values.Look(ref archivedCancelledOrderCount, "rr_procurementArchivedCancelledOrders");
            Scribe_Values.Look(ref archivedDeliveredQuantity, "rr_procurementArchivedDeliveredQuantity");
            Scribe_Deep.Look(ref heldCargo, "rr_procurementHeldCargo", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                quotes = quotes ?? new List<ProcurementQuoteRecord>();
                orders = orders ?? new List<ProcurementOrderRecord>();
                heldCargo = heldCargo ?? new ThingOwner<Thing>(this);
                ValidateSavedState();
                ledgerValidationPending = true;
            }
        }

        private void ValidateSavedState()
        {
            stateFaultKey = null;
            if (schemaVersion != CurrentSchemaVersion || nextOrderSequence < 1)
            { stateFaultKey = "RR_Proc_InvalidSave"; return; }
            long archivedCountSum;
            try { archivedCountSum = checked(archivedDeliveredOrderCount + archivedCancelledOrderCount); }
            catch (OverflowException) { stateFaultKey = "RR_Proc_InvalidSave"; return; }
            if (archivedOrderCount < 0 || archivedDeliveredOrderCount < 0 || archivedCancelledOrderCount < 0 ||
                archivedDeliveredQuantity < 0 || archivedCountSum != archivedOrderCount)
            { stateFaultKey = "RR_Proc_InvalidSave"; return; }
            if (quotes.Count > MaximumSavedQuotes || orders.Count > MaximumSavedOrders || heldCargo.Count > MaximumHeldStacksAcrossOrders)
            { stateFaultKey = "RR_Proc_InvalidSave"; return; }

            var ids = new HashSet<string>(StringComparer.Ordinal);
            var cargoReferences = new HashSet<Thing>();
            foreach (ProcurementOrderRecord order in orders)
            {
                if (order == null || string.IsNullOrEmpty(order.id) || !ids.Add(order.id) ||
                    order.quantity < 1 || order.deliveredQuantity < 0 || order.deliveredQuantity > order.quantity ||
                    order.heldCargo == null || order.deliveredStacks == null || order.receipts == null || order.routeChanges == null)
                { stateFaultKey = "RR_Proc_InvalidSave"; return; }

                bool cancelled = order.status == ProcurementOrderStatus.Cancelled;
                bool cancellationPending = order.status == ProcurementOrderStatus.CancelPending;
                if (order.status != ProcurementOrderStatus.RecoveryRequired &&
                    order.cancelIntent != (cancelled || cancellationPending))
                { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_InvalidSave"; }
                if (!order.paymentVerified && order.status != ProcurementOrderStatus.PaymentPending &&
                    order.status != ProcurementOrderStatus.RecoveryRequired)
                { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_PaymentUnverified"; }

                var orderCargo = new HashSet<Thing>();
                foreach (Thing item in order.heldCargo)
                {
                    if (item != null && (!orderCargo.Add(item) || !cargoReferences.Add(item)))
                    { stateFaultKey = "RR_Proc_InvalidSave"; return; }
                    if (item == null || item.Destroyed || !heldCargo.Contains(item))
                    { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; break; }
                }

                long receiptQuantity = 0;
                var receiptIds = new HashSet<string>(StringComparer.Ordinal);
                long expectedReceiptSequence = order.archivedDeliveryReceiptCount == 0
                    ? 1L : order.lastArchivedReceiptSequence + 1L;
                foreach (ProcurementDeliveryReceipt receipt in order.receipts)
                {
                    if (receipt == null || string.IsNullOrEmpty(receipt.id) || receipt.orderId != order.id ||
                        !receiptIds.Add(receipt.id) || receipt.quantityDelivered < 1 || receipt.remainingHeld < 0 ||
                        receipt.sequence != expectedReceiptSequence || receipt.id != order.id + ":delivery:" + receipt.sequence.ToString("D6") ||
                        !IsValidDeliveryStacks(receipt.deliveredStacks) || receipt.resultingThingLoadIds == null)
                    { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; break; }
                    long receiptStackQuantity = receipt.deliveredStacks.Sum(stack => (long)stack.quantity);
                    if (receiptStackQuantity != receipt.quantityDelivered)
                    { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; break; }
                    receiptQuantity += receipt.quantityDelivered;
                    expectedReceiptSequence++;
                }
                if (!IsValidDeliveryStacks(order.deliveredStacks) || order.settledDeliveredStackQuantity < 0 ||
                    order.routeChanges.Any(change => change == null || string.IsNullOrEmpty(change.id)))
                { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; }
                long deliveredStackQuantity;
                try { deliveredStackQuantity = checked(order.settledDeliveredStackQuantity + order.deliveredStacks.Where(stack => stack != null).Sum(stack => (long)stack.quantity)); }
                catch (OverflowException) { deliveredStackQuantity = long.MaxValue; order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; }
                long receiptCount;
                long allReceiptQuantity;
                bool receiptTotalsValid;
                try
                {
                    receiptCount = checked(order.archivedDeliveryReceiptCount + order.receipts.Count);
                    allReceiptQuantity = checked(order.archivedDeliveryQuantity + receiptQuantity);
                    receiptTotalsValid = order.archivedDeliveryReceiptCount >= 0 && order.archivedDeliveryQuantity >= 0 &&
                        (order.archivedDeliveryReceiptCount == 0
                            ? order.firstArchivedReceiptSequence == 0 && order.lastArchivedReceiptSequence == 0 && order.archivedDeliveryQuantity == 0
                            : order.firstArchivedReceiptSequence >= 1 && order.lastArchivedReceiptSequence >= order.firstArchivedReceiptSequence &&
                                order.lastArchivedReceiptSequence - order.firstArchivedReceiptSequence + 1 == order.archivedDeliveryReceiptCount &&
                                order.lastArchivedReceiptSequence <= order.deliveryReceiptSequence &&
                                (order.receipts.Count == 0 ? order.lastArchivedReceiptSequence == order.deliveryReceiptSequence
                                    : order.lastArchivedReceiptSequence < order.deliveryReceiptSequence));
                }
                catch (OverflowException) { receiptCount = long.MaxValue; allReceiptQuantity = long.MaxValue; receiptTotalsValid = false; }
                if (!receiptTotalsValid || receiptCount != order.deliveryReceiptSequence ||
                    order.routeChangeSequence != order.routeChanges.Count || allReceiptQuantity != order.deliveredQuantity ||
                    deliveredStackQuantity != order.deliveredQuantity)
                { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; }

                if (cancelled)
                {
                    if (order.heldCargo.Count != 0 || HeldQuantity(order) != 0 || order.deliveredQuantity != 0)
                    { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CancelledCargoRemains"; }
                }
                else if (order.status != ProcurementOrderStatus.RecoveryRequired &&
                    HeldQuantity(order) + order.deliveredQuantity != order.quantity)
                { order.status = ProcurementOrderStatus.RecoveryRequired; order.failureKey = "RR_Proc_CargoIntegrity"; }
            }
            foreach (Thing item in heldCargo)
            {
                if (item == null || !cargoReferences.Contains(item))
                { stateFaultKey = "RR_Proc_UnassignedCargo"; return; }
            }
        }

        public IReadOnlyList<RimroomsProcurementCatalogDef> AvailableCatalog()
        {
            return DefDatabase<RimroomsProcurementCatalogDef>.AllDefsListForReading
                .Where(def => def != null && IsUsableCatalogDef(def))
                .OrderBy(def => def.LabelCap.ToString(), StringComparer.CurrentCultureIgnoreCase).ToList();
        }

        public int MaximumOrderQuantityFor(ThingDef itemDef)
        {
            if (itemDef == null) { return 0; }
            return (int)Math.Min(MaximumActiveQuantity, (long)CurrentStackLimit(itemDef) * MaximumPhysicalStacksPerOrder);
        }

        public CompanyActionResult CreateQuote(RimroomsCampaignComponent campaign, string catalogDefName,
            int quantity, Zone_Stockpile receivingZone, out ProcurementQuoteRecord created)
        {
            created = null;
            CompanyActionResult available = CheckCampaign(campaign);
            if (!available.Success) { return available; }
            if (stateFaultKey != null) { return CompanyActionResult.Refused(stateFaultKey); }

            RimroomsProcurementCatalogDef catalog = string.IsNullOrEmpty(catalogDefName)
                ? null : DefDatabase<RimroomsProcurementCatalogDef>.GetNamedSilentFail(catalogDefName);
            if (catalog == null || !IsUsableCatalogDef(catalog)) { return CompanyActionResult.Refused("RR_Proc_CatalogUnavailable"); }
            ThingDef itemDef = catalog.ItemDef;
            if (quantity < 1 || quantity > catalog.maxOrderQuantity || quantity > MaximumActiveQuantity)
            { return CompanyActionResult.Refused("RR_Proc_InvalidQuantity"); }
            if (!IsReceivingZoneValid(campaign.Headquarters, receivingZone, itemDef))
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }

            int stackLimit = CurrentStackLimit(itemDef);
            long stackCount = ((long)quantity + stackLimit - 1L) / stackLimit;
            if (stackCount > MaximumPhysicalStacksPerOrder) { return CompanyActionResult.Refused("RR_Proc_StackCountLimit"); }
            long totalPrice;
            try { totalPrice = checked(catalog.unitPriceUsd * quantity); }
            catch (OverflowException) { return CompanyActionResult.Refused("RR_Proc_PriceOverflow"); }
            if (totalPrice <= 0) { return CompanyActionResult.Refused("RR_Proc_PriceOverflow"); }

            int now = Find.TickManager.TicksGame;
            int expiresTick;
            int dispatchTick;
            int arrivalTick;
            if (!TryAddTicks(now, QuoteLifetimeTicks, out expiresTick) ||
                !TryAddTicks(now, catalog.dispatchDelayTicks, out dispatchTick) ||
                !TryAddTicks(now, catalog.leadTimeTicks, out arrivalTick))
            { return CompanyActionResult.Refused("RR_Proc_TimeOverflow"); }
            if (nextOrderSequence == long.MaxValue) { return CompanyActionResult.Refused("RR_Proc_OrderLimit"); }
            if (orders.Count(o => o != null && !IsTerminal(o.status)) >= MaximumOpenOrders)
            { return CompanyActionResult.Refused("RR_Proc_TooManyOpenOrders"); }

            RemoveExpiredQuotes(now);
            quotes.RemoveAll(quote => quote != null && quote.accepted && orders.Any(order => order != null && order.id == quote.id));
            if (quotes.Count >= MaximumSavedQuotes) { return CompanyActionResult.Refused("RR_Proc_TooManyQuotes"); }
            float unitMass = itemDef.GetStatValueAbstract(StatDefOf.Mass);
            float totalMass = unitMass * quantity;
            if (float.IsNaN(totalMass) || float.IsInfinity(totalMass) || totalMass < 0f)
            { return CompanyActionResult.Refused("RR_Proc_MassUnavailable"); }

            string id = campaign.BranchId + ":procurement:" + nextOrderSequence.ToString("D6");
            nextOrderSequence++;
            created = new ProcurementQuoteRecord
            {
                id = id,
                branchId = campaign.BranchId,
                thingDefName = itemDef.defName,
                thingLabel = itemDef.LabelCap.ToString(),
                receivingZoneLabel = receivingZone.label,
                receivingZoneId = receivingZone.ID,
                receivingMap = campaign.Headquarters,
                receivingZone = receivingZone,
                quantity = quantity,
                unitPriceUsd = catalog.unitPriceUsd,
                totalPriceUsd = totalPrice,
                stackCountAtQuote = (int)stackCount,
                estimatedMassKg = totalMass,
                createdTick = now,
                expiresTick = expiresTick,
                dispatchTick = dispatchTick,
                arrivalTick = arrivalTick
            };
            quotes.Add(created);
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult AcceptQuote(RimroomsCampaignComponent campaign, string quoteId)
        {
            CompanyActionResult available = CheckCampaign(campaign);
            if (!available.Success) { return available; }
            if (stateFaultKey != null) { return CompanyActionResult.Refused(stateFaultKey); }
            ProcurementOrderRecord existingOrder = orders.FirstOrDefault(candidate => candidate != null && candidate.id == quoteId);
            if (existingOrder != null) { return RepairPendingPayment(campaign, existingOrder); }

            ProcurementQuoteRecord quote = quotes.FirstOrDefault(candidate => candidate != null && candidate.id == quoteId);
            if (quote == null || quote.accepted || quote.branchId != campaign.BranchId)
            { return CompanyActionResult.Refused("RR_Proc_QuoteUnavailable"); }
            if (orders.Count(candidate => candidate != null && !IsTerminal(candidate.status)) >= MaximumOpenOrders)
            { return CompanyActionResult.Refused("RR_Proc_TooManyOpenOrders"); }
            int now = Find.TickManager.TicksGame;
            if (now > quote.expiresTick) { return CompanyActionResult.Refused("RR_Proc_QuoteExpired"); }
            ThingDef itemDef = DefDatabase<ThingDef>.GetNamedSilentFail(quote.thingDefName);
            if (itemDef == null || itemDef.category != ThingCategory.Item || !itemDef.EverHaulable || itemDef.destroyOnDrop ||
                !IsReceivingZoneValid(campaign.Headquarters, quote.receivingZone, itemDef) ||
                quote.receivingMap != campaign.Headquarters || quote.receivingZoneId != quote.receivingZone.ID)
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }

            int activeStackLimit = CurrentStackLimit(itemDef);
            long currentStackCount = ((long)quote.quantity + activeStackLimit - 1L) / activeStackLimit;
            if (currentStackCount > MaximumPhysicalStacksPerOrder)
            { return CompanyActionResult.Refused("RR_Proc_StackCountLimit"); }
            if ((long)heldCargo.Count + currentStackCount > MaximumHeldStacksAcrossOrders)
            { return CompanyActionResult.Refused("RR_Proc_HeldStackBudget"); }
            LedgerEntry priorPayment = FindLedgerEntry(campaign, quote.id + ":purchase");
            if (priorPayment != null)
            { return CompanyActionResult.Refused(IsExpectedPurchase(priorPayment, quote) ? "RR_Proc_OrphanedPayment" : "RR_Proc_LedgerMismatch"); }
            if (orders.Count >= MaximumSavedOrders && !ArchiveSettledOrdersForRoom(campaign))
            { return CompanyActionResult.Refused("RR_Proc_OrderHistoryFull"); }

            ProcurementOrderRecord order = new ProcurementOrderRecord
            {
                id = quote.id,
                quoteId = quote.id,
                branchId = quote.branchId,
                thingDefName = quote.thingDefName,
                thingLabel = quote.thingLabel,
                receivingZoneLabel = quote.receivingZoneLabel,
                receivingZoneId = quote.receivingZoneId,
                receivingMap = quote.receivingMap,
                receivingZone = quote.receivingZone,
                quantity = quote.quantity,
                unitPriceUsd = quote.unitPriceUsd,
                totalPriceUsd = quote.totalPriceUsd,
                stackCountAtQuote = quote.stackCountAtQuote,
                estimatedMassKg = quote.estimatedMassKg,
                acceptedTick = now,
                dispatchTick = quote.dispatchTick,
                arrivalTick = quote.arrivalTick,
                nextAttemptTick = quote.arrivalTick,
                status = ProcurementOrderStatus.PaymentPending
            };

            CompanyActionResult cargoResult = CreateHeldCargo(order, itemDef);
            if (!cargoResult.Success) { return cargoResult; }
            orders.Add(order);
            CompanyActionResult payment;
            try
            {
                payment = campaign.PostTransaction(order.id + ":purchase", -order.totalPriceUsd,
                    "RR_Ledger_ProcurementPurchase", order.id);
            }
            catch (Exception exception)
            {
                order.failureKey = "RR_Proc_PaymentRetry";
                Log.Error("[Rimrooms][Procurement] Purchase receipt outcome is pending reconciliation for " + order.id + ": " + exception);
                return CompanyActionResult.Refused(order.failureKey);
            }

            LedgerEntry posted = FindLedgerEntry(campaign, order.id + ":purchase");
            if (payment.AlreadyApplied)
            {
                DestroyHeldCargo(order);
                order.status = ProcurementOrderStatus.RecoveryRequired;
                order.failureKey = "RR_Proc_OrphanedPayment";
                order.paymentVerified = false;
                return CompanyActionResult.Refused(order.failureKey);
            }
            if (!payment.Success)
            {
                if (posted == null)
                {
                    order.failureKey = payment.MessageKey ?? "RR_Proc_PaymentRetry";
                    return payment;
                }
                SetRecovery(order, IsExpectedPurchase(posted, order) ? "RR_Proc_OrphanedPayment" : "RR_Proc_LedgerMismatch");
                return CompanyActionResult.Refused(order.failureKey);
            }
            if (!IsExpectedPurchase(posted, order))
            { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }

            order.paymentVerified = true;
            order.status = ProcurementOrderStatus.Scheduled;
            quote.accepted = true;
            campaign.RecordEvent("RR_Event_ProcurementAccepted", order.id, order.thingLabel, order.quantity.ToString());
            return payment.AlreadyApplied ? CompanyActionResult.Existing() : CompanyActionResult.Applied();
        }

        public CompanyActionResult CancelOrder(RimroomsCampaignComponent campaign, string orderId)
        {
            CompanyActionResult available = CheckCampaign(campaign);
            if (!available.Success) { return available; }
            if (stateFaultKey != null) { return CompanyActionResult.Refused(stateFaultKey); }
            ProcurementOrderRecord order = FindOrder(orderId);
            if (order == null) { return CompanyActionResult.Refused("RR_Proc_OrderUnavailable"); }
            if (order.status == ProcurementOrderStatus.Cancelled)
            { return VerifyTerminalLedger(campaign, order) ? CompanyActionResult.Existing() : CompanyActionResult.Refused(order.failureKey); }
            int now = Find.TickManager.TicksGame;
            if (!VerifyPurchase(campaign, order)) { return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_PaymentUnverified"); }
            if (order.status != ProcurementOrderStatus.Scheduled || now >= order.dispatchTick ||
                order.deliveredQuantity != 0 || HeldQuantity(order) != order.quantity)
            { return CompanyActionResult.Refused("RR_Proc_CannotCancelAfterDispatch"); }
            if (long.MaxValue - campaign.BalanceUsd < order.totalPriceUsd)
            { return CompanyActionResult.Refused("RR_Proc_RefundOverflow"); }
            order.cancelIntent = true;
            order.status = ProcurementOrderStatus.CancelPending;
            order.failureKey = null;
            return CompleteCancellation(campaign, order);
        }

        public CompanyActionResult RetryDelivery(RimroomsCampaignComponent campaign, string orderId)
        {
            CompanyActionResult available = CheckCampaign(campaign);
            if (!available.Success) { return available; }
            if (stateFaultKey != null) { return CompanyActionResult.Refused(stateFaultKey); }
            ProcurementOrderRecord order = FindOrder(orderId);
            if (order == null) { return CompanyActionResult.Refused("RR_Proc_OrderUnavailable"); }
            if (order.status == ProcurementOrderStatus.Delivered || order.status == ProcurementOrderStatus.Cancelled)
            { return VerifyTerminalLedger(campaign, order) ? CompanyActionResult.Existing() : CompanyActionResult.Refused(order.failureKey); }
            if (order.status == ProcurementOrderStatus.RecoveryRequired)
            { return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_CargoIntegrity"); }
            if (order.cancelIntent || order.status == ProcurementOrderStatus.CancelPending)
            { return CompanyActionResult.Refused("RR_Proc_CancellationPending"); }
            if (!VerifyPurchase(campaign, order)) { return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_PaymentUnverified"); }
            int now = Find.TickManager.TicksGame;
            if (order.status == ProcurementOrderStatus.Scheduled || now < order.arrivalTick)
            { return CompanyActionResult.Refused("RR_Proc_NotArrived"); }
            order.nextAttemptTick = now;
            int moved = DeliverOrder(campaign, order, MaximumStacksDeliveredPerTick, now);
            if (moved > 0) { return CompanyActionResult.Applied(); }
            return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_ReceivingUnavailable");
        }

        public CompanyActionResult ChangeReceivingZone(RimroomsCampaignComponent campaign, string orderId, Zone_Stockpile receivingZone)
        {
            CompanyActionResult available = CheckCampaign(campaign);
            if (!available.Success) { return available; }
            if (stateFaultKey != null) { return CompanyActionResult.Refused(stateFaultKey); }
            ProcurementOrderRecord order = FindOrder(orderId);
            if (order == null) { return CompanyActionResult.Refused("RR_Proc_OrderUnavailable"); }
            if (order.status == ProcurementOrderStatus.Delivered || order.status == ProcurementOrderStatus.Cancelled)
            {
                VerifyTerminalLedger(campaign, order);
                return CompanyActionResult.Refused("RR_Proc_RedirectUnavailable");
            }
            if (order.cancelIntent || order.status == ProcurementOrderStatus.CancelPending)
            { return CompanyActionResult.Refused("RR_Proc_RedirectUnavailable"); }
            if (order.status == ProcurementOrderStatus.RecoveryRequired)
            { return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_CargoIntegrity"); }
            if (!VerifyPurchase(campaign, order)) { return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_PaymentUnverified"); }
            ThingDef itemDef = DefDatabase<ThingDef>.GetNamedSilentFail(order.thingDefName);
            if (!IsReceivingZoneValid(campaign.Headquarters, receivingZone, itemDef))
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }
            if (order.receivingZone == receivingZone) { return CompanyActionResult.Existing(); }
            if (order.routeChanges.Count >= MaximumRouteChangesPerOrder)
            { return CompanyActionResult.Refused("RR_Proc_RouteHistoryLimit"); }
            order.routeChangeSequence++;
            order.routeChanges.Add(new ProcurementRouteChangeRecord
            {
                id = order.id + ":route:" + order.routeChangeSequence.ToString("D4"),
                tick = Find.TickManager.TicksGame,
                oldZoneId = order.receivingZoneId,
                newZoneId = receivingZone.ID,
                oldZoneLabel = order.receivingZoneLabel,
                newZoneLabel = receivingZone.label
            });
            order.receivingZone = receivingZone;
            order.receivingZoneId = receivingZone.ID;
            order.receivingZoneLabel = receivingZone.label;
            order.nextAttemptTick = Find.TickManager.TicksGame;
            order.failureKey = null;
            campaign.RecordEvent("RR_Event_ProcurementRedirected", order.id, receivingZone.label);
            return CompanyActionResult.Applied();
        }

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            if (stateFaultKey != null) { return; }
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return; }

            int now = Find.TickManager.TicksGame;
            if (ledgerValidationPending)
            {
                ValidateLedgerAfterLoad(campaign);
                ledgerValidationPending = false;
            }
            if (now % ProcessingIntervalTicks != 0) { return; }
            int remainingStackBudget = MaximumStacksDeliveredPerTick;
            foreach (ProcurementOrderRecord order in orders.Where(candidate => candidate != null)
                .OrderBy(candidate => candidate.arrivalTick).ThenBy(candidate => candidate.id, StringComparer.Ordinal).ToList())
            {
                if (order == null) { continue; }
                if (order.status == ProcurementOrderStatus.Delivered)
                {
                    if (VerifyTerminalLedger(campaign, order)) { PruneSettledDeliveredStackReferences(order); }
                    continue;
                }
                if (order.status == ProcurementOrderStatus.Cancelled || order.status == ProcurementOrderStatus.RecoveryRequired) { continue; }
                if (order.cancelIntent || order.status == ProcurementOrderStatus.CancelPending)
                {
                    CompleteCancellation(campaign, order);
                    continue;
                }
                if (order.status == ProcurementOrderStatus.PaymentPending)
                {
                    // A crash/exception after the ledger write can be reconciled from the exact
                    // saved order and its existing holder without issuing a second shipment.
                    if (FindLedgerEntry(campaign, order.id + ":purchase") != null)
                    { RepairPendingPayment(campaign, order); }
                    continue;
                }
                if (!VerifyPurchase(campaign, order)) { continue; }
                if (!PruneSettledDeliveredStackReferences(order)) { continue; }
                if (remainingStackBudget <= 0) { continue; }
                if (order.status == ProcurementOrderStatus.Scheduled && now >= order.dispatchTick)
                {
                    order.status = ProcurementOrderStatus.InTransit;
                    order.dispatchedTick = now;
                    campaign.RecordEvent("RR_Event_ProcurementDispatched", order.id, order.thingLabel);
                }
                if (order.status == ProcurementOrderStatus.InTransit && now >= order.arrivalTick)
                {
                    order.nextAttemptTick = order.arrivalTick;
                }
                if ((order.status == ProcurementOrderStatus.InTransit || order.status == ProcurementOrderStatus.PartiallyDelivered ||
                    order.status == ProcurementOrderStatus.AwaitingReceivingSpace) && now >= order.arrivalTick && now >= order.nextAttemptTick)
                {
                    int used = DeliverOrder(campaign, order, remainingStackBudget, now);
                    remainingStackBudget -= used;
                }
            }
        }

        private void ValidateLedgerAfterLoad(RimroomsCampaignComponent campaign)
        {
            foreach (ProcurementOrderRecord order in orders.Where(candidate => candidate != null))
            {
                if (order.branchId != campaign.BranchId)
                { SetRecovery(order, "RR_Proc_BranchMismatch"); continue; }

                LedgerEntry purchase = FindLedgerEntry(campaign, order.id + ":purchase");
                LedgerEntry refund = FindLedgerEntry(campaign, order.id + ":cancel");
                if ((purchase != null && !IsExpectedPurchase(purchase, order)) ||
                    (refund != null && !IsExpectedRefund(refund, order)))
                { SetRecovery(order, "RR_Proc_LedgerMismatch"); continue; }

                if (order.status == ProcurementOrderStatus.RecoveryRequired) { continue; }
                if (order.status == ProcurementOrderStatus.Delivered || order.status == ProcurementOrderStatus.Cancelled)
                {
                    VerifyTerminalLedger(campaign, order);
                    continue;
                }
                if (order.status == ProcurementOrderStatus.PaymentPending)
                {
                    if (refund != null || order.cancelIntent)
                    { SetRecovery(order, "RR_Proc_LedgerMismatch"); continue; }
                    if (purchase == null)
                    {
                        order.paymentVerified = false;
                        if (string.IsNullOrEmpty(order.failureKey)) { order.failureKey = "RR_Proc_PaymentRetry"; }
                        continue;
                    }
                    if (HeldQuantity(order) != order.quantity || order.deliveredQuantity != 0)
                    { SetRecovery(order, "RR_Proc_CargoIntegrity"); continue; }

                    // The same saved order and its already-owned cargo survived a save between
                    // the ledger write and the state transition. Reconcile that receipt in place.
                    order.paymentVerified = true;
                    order.status = ProcurementOrderStatus.Scheduled;
                    order.failureKey = null;
                    ProcurementQuoteRecord savedQuote = quotes.FirstOrDefault(quote => quote != null && quote.id == order.quoteId);
                    if (savedQuote != null) { savedQuote.accepted = true; }
                    continue;
                }
                if (order.status == ProcurementOrderStatus.CancelPending)
                {
                    if (!order.cancelIntent || purchase == null || order.deliveredQuantity != 0 || HeldQuantity(order) != order.quantity)
                    { SetRecovery(order, purchase == null ? "RR_Proc_PaymentUnverified" : "RR_Proc_CargoIntegrity"); continue; }
                    order.paymentVerified = true;
                    if (refund != null) { CompleteCancellation(campaign, order); }
                    else if (string.IsNullOrEmpty(order.failureKey)) { order.failureKey = "RR_Proc_RefundRetry"; }
                    continue;
                }
                if (order.cancelIntent || refund != null)
                { SetRecovery(order, "RR_Proc_LedgerMismatch"); continue; }
                if (!VerifyPurchase(campaign, order)) { continue; }
                if (order.status != ProcurementOrderStatus.Scheduled && order.status != ProcurementOrderStatus.InTransit &&
                    order.status != ProcurementOrderStatus.PartiallyDelivered && order.status != ProcurementOrderStatus.AwaitingReceivingSpace)
                { SetRecovery(order, "RR_Proc_InvalidSave"); }
            }
        }

        private bool VerifyTerminalLedger(RimroomsCampaignComponent campaign, ProcurementOrderRecord order)
        {
            if (order == null) { return false; }
            if (campaign == null || order.branchId != campaign.BranchId)
            { SetRecovery(order, "RR_Proc_BranchMismatch"); return false; }

            LedgerEntry purchase = FindLedgerEntry(campaign, order.id + ":purchase");
            LedgerEntry refund = FindLedgerEntry(campaign, order.id + ":cancel");
            long receiptQuantity = order.receipts.Where(receipt => receipt != null).Sum(receipt => (long)receipt.quantityDelivered);
            long deliveredStackQuantity = 0;
            long allReceiptCount = 0;
            long allReceiptQuantity = 0;
            bool journalValid = false;
            try
            {
                allReceiptCount = checked(order.archivedDeliveryReceiptCount + order.receipts.Count);
                allReceiptQuantity = checked(order.archivedDeliveryQuantity + receiptQuantity);
                deliveredStackQuantity = checked(order.settledDeliveredStackQuantity +
                    order.deliveredStacks.Where(stack => stack != null).Sum(stack => (long)stack.quantity));
                long expectedSequence = order.archivedDeliveryReceiptCount == 0 ? 1L : order.lastArchivedReceiptSequence + 1L;
                bool recentSequenceValid = order.receipts.All(receipt => receipt != null && receipt.sequence == expectedSequence++);
                bool archivedSequenceValid = order.archivedDeliveryReceiptCount == 0
                    ? order.firstArchivedReceiptSequence == 0 && order.lastArchivedReceiptSequence == 0 && order.archivedDeliveryQuantity == 0
                    : order.firstArchivedReceiptSequence >= 1 && order.lastArchivedReceiptSequence >= order.firstArchivedReceiptSequence &&
                        order.lastArchivedReceiptSequence - order.firstArchivedReceiptSequence + 1 == order.archivedDeliveryReceiptCount;
                journalValid = order.archivedDeliveryReceiptCount >= 0 && order.archivedDeliveryQuantity >= 0 && archivedSequenceValid &&
                    recentSequenceValid && allReceiptCount == order.deliveryReceiptSequence &&
                    (order.receipts.Count == 0 ? order.lastArchivedReceiptSequence == order.deliveryReceiptSequence
                        : order.receipts[order.receipts.Count - 1].sequence == order.deliveryReceiptSequence) &&
                    allReceiptQuantity == order.deliveredQuantity && deliveredStackQuantity == order.deliveredQuantity &&
                    order.settledDeliveredStackQuantity >= 0 &&
                    IsValidDeliveryStacks(order.deliveredStacks) && order.receipts.Count <= MaximumDetailedDeliveryReceiptsPerOrder &&
                order.receipts.All(receipt => receipt != null && !string.IsNullOrEmpty(receipt.id) && receipt.orderId == order.id &&
                    receipt.quantityDelivered > 0 && receipt.remainingHeld >= 0 && IsValidDeliveryStacks(receipt.deliveredStacks) &&
                    receipt.resultingThingLoadIds != null && receipt.deliveredStacks.Sum(stack => (long)stack.quantity) == receipt.quantityDelivered) &&
                order.routeChanges.All(change => change != null && !string.IsNullOrEmpty(change.id));
            }
            catch (OverflowException) { journalValid = false; }
            catch (ArgumentOutOfRangeException) { journalValid = false; }

            if (order.status == ProcurementOrderStatus.Delivered)
            {
                if (!IsExpectedPurchase(purchase, order) || refund != null || order.cancelIntent ||
                    order.heldCargo.Count != 0 || HeldQuantity(order) != 0 || order.deliveredQuantity != order.quantity || !journalValid)
                { SetRecovery(order, purchase == null ? "RR_Proc_PaymentUnverified" : "RR_Proc_LedgerMismatch"); return false; }
            }
            else if (order.status == ProcurementOrderStatus.Cancelled)
            {
                if (!IsExpectedPurchase(purchase, order) || !IsExpectedRefund(refund, order) || !order.cancelIntent ||
                    order.heldCargo.Count != 0 || HeldQuantity(order) != 0 || order.deliveredQuantity != 0 || !journalValid)
                { SetRecovery(order, purchase == null || refund == null ? "RR_Proc_PaymentUnverified" : "RR_Proc_LedgerMismatch"); return false; }
            }
            else { return false; }

            order.paymentVerified = true;
            order.failureKey = null;
            return true;
        }

        private static bool IsValidDeliveryStacks(List<ProcurementDeliveryStack> stacks)
        {
            return stacks != null && stacks.All(stack => stack != null && stack.quantity > 0 && !string.IsNullOrEmpty(stack.loadId));
        }

        private int DeliverOrder(RimroomsCampaignComponent campaign, ProcurementOrderRecord order, int stackBudget, int now)
        {
            if (order == null || stackBudget <= 0 || IsTerminal(order.status) || order.cancelIntent || !order.paymentVerified)
            { return 0; }
            if (order.receipts.Count >= MaximumDetailedDeliveryReceiptsPerOrder && !CompactOldestReceipt(order))
            { SetRecovery(order, "RR_Proc_ReceiptHistoryLimit"); return 0; }
            if (order.deliveryReceiptSequence == long.MaxValue)
            { SetRecovery(order, "RR_Proc_ReceiptHistoryLimit"); return 0; }
            ThingDef itemDef = DefDatabase<ThingDef>.GetNamedSilentFail(order.thingDefName);
            if (itemDef == null || itemDef.category != ThingCategory.Item)
            { SetAwaiting(order, "RR_Proc_ItemDefMissing", now); return 0; }
            if (!IsReceivingZoneValid(order.receivingMap, order.receivingZone, itemDef) ||
                order.receivingZone.ID != order.receivingZoneId)
            { SetAwaiting(order, "RR_Proc_ReceivingZoneInvalid", now); return 0; }
            if (!Find.Maps.Contains(order.receivingMap))
            { SetAwaiting(order, "RR_Proc_HeadquartersUnavailable", now); return 0; }

            int newLimit = CurrentStackLimit(itemDef);
            long projectedOrderStacks;
            if (!TryGetProjectedStackCount(order, newLimit, out projectedOrderStacks))
            { SetRecovery(order, "RR_Proc_CargoIntegrity"); return 0; }
            long addedStacks = projectedOrderStacks - order.heldCargo.Count;
            long requiredAggregateStacks = (long)heldCargo.Count + addedStacks;
            if (projectedOrderStacks > MaximumPhysicalStacksPerOrder)
            { SetAwaiting(order, "RR_Proc_StackLimitChanged", now); return 0; }
            if (requiredAggregateStacks > MaximumHeldStacksAcrossOrders)
            { SetAwaiting(order, "RR_Proc_HeldStackBudget", now); return 0; }
            if (!NormalizeHeldStacks(order, newLimit))
            { SetRecovery(order, "RR_Proc_CargoIntegrity"); return 0; }

            Pawn carrier = FindAvailableCarrier(campaign, order.receivingMap);
            if (carrier == null) { SetAwaiting(order, "RR_Proc_NoReachableStaff", now); return 0; }
            SlotGroup targetGroup = order.receivingZone.GetSlotGroup();
            if (targetGroup == null || !order.receivingZone.settings.AllowedToAccept(itemDef))
            { SetAwaiting(order, "RR_Proc_FilterChanged", now); return 0; }

            int used = 0;
            int deliveredThisBatch = 0;
            var batchStacks = new List<ProcurementDeliveryStack>();
            var batchIds = new List<string>();
            string capacityFailure = null;
            HashSet<IntVec3> storageCells = new HashSet<IntVec3>(targetGroup.CellsList);
            foreach (Thing item in order.heldCargo.ToList())
            {
                if (used >= stackBudget) { break; }
                if (item == null || item.Destroyed || !heldCargo.Contains(item)) { continue; }
                if (item.stackCount <= 0 || item.stackCount > CurrentStackLimit(item.def))
                { SetRecovery(order, "RR_Proc_CargoIntegrity"); return used; }

                int targetCapacity = AvailableStorageFor(item, order.receivingZone, carrier, storageCells);
                int pendingAtTarget = PendingDeliveryQuantity(order.receivingMap, item.def, order.receivingZoneId, storageCells);
                int remainingReceivingCapacity = targetCapacity - pendingAtTarget - deliveredThisBatch;
                if (remainingReceivingCapacity <= 0)
                { capacityFailure = "RR_Proc_ReceivingStockpileFull"; break; }
                int requestedCount = Math.Min(item.stackCount, remainingReceivingCapacity);

                bool isPreferredTarget = StoreUtility.TryFindBestBetterStoreCellFor(item, carrier, order.receivingMap,
                    StoragePriority.Unstored, Faction.OfPlayer, out IntVec3 bestCell, needAccurateResult: false) &&
                    storageCells.Contains(bestCell);
                if (!isPreferredTarget)
                { capacityFailure = "RR_Proc_ReceivingStockpileNotPreferred"; break; }

                List<IntVec3> stagingCells = FindStagingCells(order.receivingMap, order.receivingZone, carrier, item.def);
                if (stagingCells.Count == 0)
                { capacityFailure = "RR_Proc_ReceivingStagingFull"; break; }
                var allowedStagingCells = new HashSet<IntVec3>(stagingCells);
                int before = item.stackCount;
                int placedForStack = 0;
                var stackResults = new List<ProcurementDeliveryStack>();
                var stackIds = new List<string>();
                bool dropped = false;
                foreach (IntVec3 center in SampleStagingCenters(stagingCells, 32))
                {
                    int candidatePlaced = 0;
                    var candidateResults = new List<ProcurementDeliveryStack>();
                    var candidateIds = new List<string>();
                    bool success = heldCargo.TryDrop(item, center, order.receivingMap, ThingPlaceMode.Near, requestedCount,
                        out Thing ignored,
                        delegate(Thing placed, int count)
                        {
                            if (placed == null || count < 1) { return; }
                            candidatePlaced += count;
                            string loadId = placed.GetUniqueLoadID();
                            candidateResults.Add(new ProcurementDeliveryStack
                            { thing = placed, quantity = count, receivingZoneId = order.receivingZoneId, loadId = loadId, stagedCell = placed.Position });
                            candidateIds.Add(loadId);
                        },
                        cell => allowedStagingCells.Contains(cell) && IsStagingCellUsable(order.receivingMap, order.receivingZone, carrier, cell));
                    if (candidatePlaced > 0)
                    {
                        placedForStack = candidatePlaced;
                        stackResults.AddRange(candidateResults);
                        stackIds.AddRange(candidateIds);
                        dropped = success || item.stackCount < before || !heldCargo.Contains(item);
                        break;
                    }
                    if (success) { dropped = true; break; }
                }
                if (!dropped && placedForStack == 0)
                { capacityFailure = "RR_Proc_ReceivingStagingFull"; break; }

                used++;
                if (placedForStack > 0)
                {
                    deliveredThisBatch += placedForStack;
                    batchStacks.AddRange(stackResults);
                    batchIds.AddRange(stackIds);
                    if (!heldCargo.Contains(item)) { order.heldCargo.Remove(item); }
                }
            }

            if (deliveredThisBatch > 0)
            {
                order.deliveredQuantity = checked(order.deliveredQuantity + deliveredThisBatch);
                order.deliveryReceiptSequence++;
                order.receipts.Add(new ProcurementDeliveryReceipt
                {
                    id = order.id + ":delivery:" + order.deliveryReceiptSequence.ToString("D6"),
                    orderId = order.id,
                    sequence = order.deliveryReceiptSequence,
                    tick = now,
                    quantityDelivered = deliveredThisBatch,
                    remainingHeld = HeldQuantity(order),
                    receivingZoneId = order.receivingZoneId,
                    receivingZoneLabel = order.receivingZoneLabel,
                    deliveredStacks = batchStacks,
                    resultingThingLoadIds = batchIds
                });
                order.deliveredStacks.AddRange(batchStacks);
                order.failureKey = null;
            }

            int remaining = HeldQuantity(order);
            if (order.deliveredQuantity + remaining != order.quantity)
            { SetRecovery(order, "RR_Proc_CargoIntegrity"); return used; }
            if (remaining == 0)
            {
                order.status = ProcurementOrderStatus.Delivered;
                order.failureKey = null;
                campaign.RecordEvent("RR_Event_ProcurementDelivered", order.id, order.thingLabel, order.quantity.ToString());
            }
            else if (capacityFailure != null)
            { SetAwaiting(order, capacityFailure, now); }
            else if (deliveredThisBatch > 0)
            {
                order.status = ProcurementOrderStatus.PartiallyDelivered;
                order.failureKey = null;
                order.nextAttemptTick = now + ProcessingIntervalTicks;
            }
            else
                    { SetAwaiting(order, "RR_Proc_ReceivingUnavailable", now); }
            return used;
        }

        private CompanyActionResult RepairPendingPayment(RimroomsCampaignComponent campaign, ProcurementOrderRecord order)
        {
            if (stateFaultKey != null) { return CompanyActionResult.Refused(stateFaultKey); }
            if (order == null) { return CompanyActionResult.Refused("RR_Proc_OrderUnavailable"); }
            if (order.branchId != campaign.BranchId)
            { SetRecovery(order, "RR_Proc_BranchMismatch"); return CompanyActionResult.Refused(order.failureKey); }
            if (order.status == ProcurementOrderStatus.RecoveryRequired)
            { return CompanyActionResult.Refused(order.failureKey ?? "RR_Proc_CargoIntegrity"); }
            if (order.status == ProcurementOrderStatus.Delivered || order.status == ProcurementOrderStatus.Cancelled)
            { return VerifyTerminalLedger(campaign, order) ? CompanyActionResult.Existing() : CompanyActionResult.Refused(order.failureKey); }
            if (order.cancelIntent || order.status == ProcurementOrderStatus.CancelPending)
            { return CompleteCancellation(campaign, order); }

            LedgerEntry entry = FindLedgerEntry(campaign, order.id + ":purchase");
            if (entry != null)
            {
                if (!IsExpectedPurchase(entry, order))
                { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }
                LedgerEntry refund = FindLedgerEntry(campaign, order.id + ":cancel");
                if (refund != null)
                { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }
                if (order.status == ProcurementOrderStatus.PaymentPending && HeldQuantity(order) != order.quantity)
                { SetRecovery(order, "RR_Proc_CargoIntegrity"); return CompanyActionResult.Refused(order.failureKey); }
                order.paymentVerified = true;
                if (order.status == ProcurementOrderStatus.PaymentPending)
                {
                    order.status = ProcurementOrderStatus.Scheduled;
                    order.failureKey = null;
                    ProcurementQuoteRecord quote = quotes.FirstOrDefault(candidate => candidate != null && candidate.id == order.quoteId);
                    if (quote != null) { quote.accepted = true; }
                }
                return CompanyActionResult.Existing();
            }

            if (order.status != ProcurementOrderStatus.PaymentPending || HeldQuantity(order) != order.quantity)
            { SetRecovery(order, "RR_Proc_PaymentUnverified"); return CompanyActionResult.Refused(order.failureKey); }
            CompanyActionResult payment;
            try
            {
                payment = campaign.PostTransaction(order.id + ":purchase", -order.totalPriceUsd,
                    "RR_Ledger_ProcurementPurchase", order.id);
            }
            catch (Exception exception)
            {
                order.failureKey = "RR_Proc_PaymentRetry";
                Log.Error("[Rimrooms][Procurement] Purchase retry outcome is pending reconciliation for " + order.id + ": " + exception);
                return CompanyActionResult.Refused(order.failureKey);
            }
            entry = FindLedgerEntry(campaign, order.id + ":purchase");
            if (!payment.Success)
            {
                if (entry == null)
                {
                    order.failureKey = payment.MessageKey ?? "RR_Proc_PaymentRetry";
                    return payment;
                }
                if (!IsExpectedPurchase(entry, order))
                { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }
            }
            if (!IsExpectedPurchase(entry, order))
            { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }
            order.paymentVerified = true;
            order.status = ProcurementOrderStatus.Scheduled;
            order.failureKey = null;
            ProcurementQuoteRecord savedQuote = quotes.FirstOrDefault(candidate => candidate != null && candidate.id == order.quoteId);
            if (savedQuote != null) { savedQuote.accepted = true; }
            return payment.AlreadyApplied || !payment.Success ? CompanyActionResult.Existing() : CompanyActionResult.Applied();
        }

        private CompanyActionResult CompleteCancellation(RimroomsCampaignComponent campaign, ProcurementOrderRecord order)
        {
            if (order == null || !order.cancelIntent || order.status != ProcurementOrderStatus.CancelPending)
            { return CompanyActionResult.Refused("RR_Proc_CancellationPending"); }
            if (campaign == null || order.branchId != campaign.BranchId)
            { SetRecovery(order, "RR_Proc_BranchMismatch"); return CompanyActionResult.Refused(order.failureKey); }
            LedgerEntry purchase = FindLedgerEntry(campaign, order.id + ":purchase");
            if (!IsExpectedPurchase(purchase, order))
            {
                if (purchase != null) { SetRecovery(order, "RR_Proc_LedgerMismatch"); }
                else { order.failureKey = "RR_Proc_PaymentUnverified"; }
                return CompanyActionResult.Refused(order.failureKey);
            }
            if (order.deliveredQuantity != 0 || HeldQuantity(order) != order.quantity)
            { SetRecovery(order, "RR_Proc_CargoIntegrity"); return CompanyActionResult.Refused(order.failureKey); }

            LedgerEntry refundEntry = FindLedgerEntry(campaign, order.id + ":cancel");
            bool refundWasAlreadyRecorded = refundEntry != null;
            if (refundEntry != null && !IsExpectedRefund(refundEntry, order))
            { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }
            if (refundEntry == null)
            {
                if (long.MaxValue - campaign.BalanceUsd < order.totalPriceUsd)
                { order.failureKey = "RR_Proc_RefundOverflow"; return CompanyActionResult.Refused(order.failureKey); }
                CompanyActionResult refund = null;
                try
                {
                    refund = campaign.PostTransaction(order.id + ":cancel", order.totalPriceUsd,
                        "RR_Ledger_ProcurementRefund", order.id);
                }
                catch (Exception exception)
                {
                    Log.Error("[Rimrooms][Procurement] Refund outcome is pending reconciliation for " + order.id + ": " + exception);
                }
                refundEntry = FindLedgerEntry(campaign, order.id + ":cancel");
                if (refundEntry == null)
                {
                    order.failureKey = refund == null ? "RR_Proc_RefundRetry" : refund.MessageKey ?? "RR_Proc_RefundRetry";
                    return refund ?? CompanyActionResult.Refused(order.failureKey);
                }
                if (!IsExpectedRefund(refundEntry, order))
                { SetRecovery(order, "RR_Proc_LedgerMismatch"); return CompanyActionResult.Refused(order.failureKey); }
            }

            DestroyHeldCargo(order);
            order.status = ProcurementOrderStatus.Cancelled;
            order.failureKey = null;
            campaign.RecordEvent("RR_Event_ProcurementCancelled", order.id, order.thingLabel);
            return refundWasAlreadyRecorded ? CompanyActionResult.Existing() : CompanyActionResult.Applied();
        }

        private bool VerifyPurchase(RimroomsCampaignComponent campaign, ProcurementOrderRecord order)
        {
            if (campaign == null || order == null || order.branchId != campaign.BranchId)
            { if (order != null) { SetRecovery(order, "RR_Proc_BranchMismatch"); } return false; }
            LedgerEntry purchase = FindLedgerEntry(campaign, order.id + ":purchase");
            if (purchase == null || !IsExpectedPurchase(purchase, order))
            {
                SetRecovery(order, purchase == null ? "RR_Proc_PaymentUnverified" : "RR_Proc_LedgerMismatch");
                return false;
            }
            LedgerEntry refund = FindLedgerEntry(campaign, order.id + ":cancel");
            if (refund != null && !order.cancelIntent)
            { SetRecovery(order, "RR_Proc_LedgerMismatch"); return false; }
            if (refund != null && !IsExpectedRefund(refund, order))
            { SetRecovery(order, "RR_Proc_LedgerMismatch"); return false; }
            order.paymentVerified = true;
            return true;
        }

        private static LedgerEntry FindLedgerEntry(RimroomsCampaignComponent campaign, string operationId)
        { return campaign.Ledger.FirstOrDefault(entry => entry != null && entry.OperationId == operationId); }

        private static bool IsExpectedPurchase(LedgerEntry entry, ProcurementOrderRecord order)
        {
            return entry != null && entry.OperationId == order.id + ":purchase" && entry.AmountUsd == -order.totalPriceUsd &&
                entry.ReasonKey == "RR_Ledger_ProcurementPurchase" && entry.RelatedId == order.id;
        }

        private static bool IsExpectedPurchase(LedgerEntry entry, ProcurementQuoteRecord quote)
        {
            return entry != null && entry.OperationId == quote.id + ":purchase" && entry.AmountUsd == -quote.totalPriceUsd &&
                entry.ReasonKey == "RR_Ledger_ProcurementPurchase" && entry.RelatedId == quote.id;
        }

        private static bool IsExpectedRefund(LedgerEntry entry, ProcurementOrderRecord order)
        {
            return entry != null && entry.OperationId == order.id + ":cancel" && entry.AmountUsd == order.totalPriceUsd &&
                entry.ReasonKey == "RR_Ledger_ProcurementRefund" && entry.RelatedId == order.id;
        }

        private bool NormalizeHeldStacks(ProcurementOrderRecord order, int stackLimit)
        {
            long stackCountAfter;
            if (!TryGetProjectedStackCount(order, stackLimit, out stackCountAfter) ||
                stackCountAfter > MaximumPhysicalStacksPerOrder ||
                (long)heldCargo.Count + stackCountAfter - order.heldCargo.Count > MaximumHeldStacksAcrossOrders)
            { return false; }
            foreach (Thing item in order.heldCargo.ToList())
            {
                if (item == null || item.Destroyed || !heldCargo.Contains(item)) { continue; }
                if (item.def.stackLimit < 1) { return false; }
                while (item.stackCount > stackLimit)
                {
                    Thing split = item.SplitOff(stackLimit);
                    if (split == null || !heldCargo.TryAdd(split, canMergeWithExistingStacks: false))
                    {
                        if (split != null && !split.Destroyed) { item.TryAbsorbStack(split, respectStackLimit: false); }
                        return false;
                    }
                    order.heldCargo.Add(split);
                }
            }
            order.heldCargo.RemoveAll(item => item == null || item.Destroyed || !heldCargo.Contains(item));
            return true;
        }

        private bool TryGetProjectedStackCount(ProcurementOrderRecord order, int stackLimit, out long projectedStackCount)
        {
            projectedStackCount = 0;
            if (order == null || order.heldCargo == null || stackLimit < 1) { return false; }
            foreach (Thing item in order.heldCargo)
            {
                if (item == null || item.Destroyed || !heldCargo.Contains(item) || item.stackCount < 1) { return false; }
                projectedStackCount += ((long)item.stackCount + stackLimit - 1L) / stackLimit;
                if (projectedStackCount > MaximumPhysicalStacksPerOrder) { return true; }
            }
            return true;
        }

        private int AvailableStorageFor(Thing item, Zone_Stockpile zone, Pawn carrier, HashSet<IntVec3> zoneCells)
        {
            long capacity = 0;
            int limit = CurrentStackLimit(item.def);
            foreach (IntVec3 cell in zoneCells)
            {
                if (!StoreUtility.IsGoodStoreCell(cell, zone.Map, item, carrier, Faction.OfPlayer)) { continue; }
                List<Thing> items = cell.GetThingList(zone.Map).Where(thing => thing.def.category == ThingCategory.Item).ToList();
                foreach (Thing existing in items)
                {
                    if (existing.CanStackWith(item)) { capacity += Math.Max(0, CurrentStackLimit(existing.def) - existing.stackCount); }
                }
                int openItemSlots = Math.Max(0, cell.GetMaxItemsAllowedInCell(zone.Map) - items.Count);
                capacity += (long)openItemSlots * limit;
                if (capacity >= MaximumActiveQuantity) { return MaximumActiveQuantity; }
            }
            return (int)Math.Min(MaximumActiveQuantity, capacity);
        }

        private bool PruneSettledDeliveredStackReferences(ProcurementOrderRecord order)
        {
            if (order == null || order.deliveredStacks == null) { return false; }
            foreach (ProcurementDeliveryStack stack in order.deliveredStacks.ToList())
            {
                Thing thing = stack == null ? null : stack.thing;
                bool remainsAtStaging = thing != null && !thing.Destroyed && thing.Spawned &&
                    thing.Map == order.receivingMap && thing.Position == stack.stagedCell;
                if (remainsAtStaging && order.receivingMap.zoneManager != null)
                {
                    Zone zoneAtStack = order.receivingMap.zoneManager.ZoneAt(thing.Position);
                    if (zoneAtStack is Zone_Stockpile) { remainsAtStaging = false; }
                }
                if (remainsAtStaging) { continue; }
                if (stack == null || stack.quantity < 1)
                { SetRecovery(order, "RR_Proc_CargoIntegrity"); return false; }
                try { order.settledDeliveredStackQuantity = checked(order.settledDeliveredStackQuantity + stack.quantity); }
                catch (OverflowException) { SetRecovery(order, "RR_Proc_CargoIntegrity"); return false; }
                order.deliveredStacks.Remove(stack);
            }
            return true;
        }

        private int PendingDeliveryQuantity(Map map, ThingDef itemDef, int receivingZoneId, HashSet<IntVec3> storageCells)
        {
            long pending = 0;
            foreach (ProcurementOrderRecord other in orders)
            {
                if (other == null || other.status == ProcurementOrderStatus.Cancelled || other.receivingMap != map || other.thingDefName != itemDef.defName)
                { continue; }
                foreach (ProcurementDeliveryStack stack in other.deliveredStacks)
                {
                    if (stack == null) { continue; }
                    Thing thing = stack.thing;
                    if (stack.receivingZoneId == receivingZoneId && thing != null && !thing.Destroyed && thing.Spawned && thing.Map == map &&
                        thing.Position == stack.stagedCell && !storageCells.Contains(thing.Position) && thing.def == itemDef)
                    { pending += stack.quantity; }
                }
            }
            return (int)Math.Min(MaximumActiveQuantity, pending);
        }

        private List<IntVec3> FindStagingCells(Map map, Zone_Stockpile zone, Pawn carrier, ThingDef itemDef)
        {
            var candidates = new HashSet<IntVec3>();
            SlotGroup group = zone.GetSlotGroup();
            if (group == null) { return new List<IntVec3>(); }
            foreach (IntVec3 storageCell in group.CellsList)
            {
                for (int dx = -3; dx <= 3; dx++)
                {
                    for (int dz = -3; dz <= 3; dz++)
                    {
                        if (Math.Abs(dx) + Math.Abs(dz) > 3) { continue; }
                        IntVec3 candidate = new IntVec3(storageCell.x + dx, 0, storageCell.z + dz);
                        if (IsStagingCellUsable(map, zone, carrier, candidate) && GenSpawn.CanSpawnAt(itemDef, candidate, map, itemDef.defaultPlacingRot))
                        { candidates.Add(candidate); }
                    }
                }
            }
            return candidates.OrderBy(cell => cell.DistanceToSquared(group.CellsList[0]))
                .ThenBy(cell => cell.x).ThenBy(cell => cell.z).ToList();
        }

        private static IEnumerable<IntVec3> SampleStagingCenters(List<IntVec3> stagingCells, int maximumCenters)
        {
            if (stagingCells == null || stagingCells.Count == 0) { yield break; }
            int samples = Math.Min(maximumCenters, stagingCells.Count);
            for (int index = 0; index < samples; index++)
            {
                int selectedIndex = samples == 1 ? 0 : (int)((long)index * (stagingCells.Count - 1) / (samples - 1));
                yield return stagingCells[selectedIndex];
            }
        }

        private static bool IsStagingCellUsable(Map map, Zone_Stockpile zone, Pawn carrier, IntVec3 cell)
        {
            return map != null && zone != null && carrier != null && cell.InBounds(map) && cell.Standable(map) &&
                map.areaManager.Home[cell] && map.zoneManager.ZoneAt(cell) == null &&
                cell.GetItemCount(map) == 0 && carrier.CanReach(cell, PathEndMode.OnCell, Danger.Some);
        }

        private static Pawn FindAvailableCarrier(RimroomsCampaignComponent campaign, Map map)
        {
            return campaign.Staff.Where(staff => staff != null && staff.Employed && staff.Pawn != null &&
                    staff.Pawn.Spawned && staff.Pawn.Map == map && !staff.Pawn.Dead && !staff.Pawn.Downed &&
                    staff.Pawn.Faction == Faction.OfPlayer)
                .Select(staff => staff.Pawn).FirstOrDefault();
        }

        private CompanyActionResult CreateHeldCargo(ProcurementOrderRecord order, ThingDef itemDef)
        {
            if (heldCargo == null) { return CompanyActionResult.Refused("RR_Proc_CargoOwnerUnavailable"); }
            int stackLimit = CurrentStackLimit(itemDef);
            int stacks = (int)(((long)order.quantity + stackLimit - 1L) / stackLimit);
            if (stacks > MaximumPhysicalStacksPerOrder) { return CompanyActionResult.Refused("RR_Proc_StackCountLimit"); }
            if ((long)heldCargo.Count + stacks > MaximumHeldStacksAcrossOrders)
            { return CompanyActionResult.Refused("RR_Proc_HeldStackBudget"); }
            int remaining = order.quantity;
            try
            {
                while (remaining > 0)
                {
                    int count = Math.Min(remaining, stackLimit);
                    Thing item = ThingMaker.MakeThing(itemDef);
                    if (item == null) { throw new InvalidOperationException("ThingMaker returned no item for " + itemDef.defName); }
                    item.stackCount = count;
                    if (item.stackCount < 1 || item.stackCount > item.def.stackLimit ||
                        !heldCargo.TryAdd(item, canMergeWithExistingStacks: false))
                    { item.Destroy(DestroyMode.Vanish); throw new InvalidOperationException("Shipment owner refused a bounded stack."); }
                    order.heldCargo.Add(item);
                    remaining -= count;
                }
            }
            catch (Exception exception)
            {
                DestroyHeldCargo(order);
                Log.Error("[Rimrooms][Procurement] Physical shipment creation failed: " + exception);
                return CompanyActionResult.Refused("RR_Proc_CargoCreateFailed");
            }
            return CompanyActionResult.Applied();
        }

        private void DestroyHeldCargo(ProcurementOrderRecord order)
        {
            foreach (Thing item in order.heldCargo.ToList())
            {
                if (item == null || item.Destroyed) { continue; }
                if (heldCargo.Contains(item)) { heldCargo.Remove(item); }
                item.Destroy(DestroyMode.Vanish);
            }
            order.heldCargo.Clear();
        }

        private int HeldQuantity(ProcurementOrderRecord order)
        {
            long total = 0;
            foreach (Thing item in order.heldCargo)
            {
                if (item != null && !item.Destroyed && heldCargo.Contains(item)) { total += item.stackCount; }
            }
            return (int)Math.Min(int.MaxValue, total);
        }

        private static bool IsReceivingZoneValid(Map map, Zone_Stockpile zone, ThingDef itemDef)
        {
            return map != null && zone != null && zone.Map == map && zone.GetSlotGroup() != null &&
                zone.GetSlotGroup().CellsList.Count > 0 && map.zoneManager != null &&
                map.zoneManager.AllZones.Contains(zone) && itemDef != null && zone.settings != null &&
                zone.settings.AllowedToAccept(itemDef);
        }

        private static bool IsUsableCatalogDef(RimroomsProcurementCatalogDef catalog)
        {
            ThingDef item = catalog == null ? null : catalog.ItemDef;
            return item != null && item.category == ThingCategory.Item && item.EverHaulable && !item.destroyOnDrop &&
                item.stackLimit > 0 && catalog.unitPriceUsd > 0 && catalog.maxOrderQuantity > 0 &&
                catalog.maxOrderQuantity <= MaximumActiveQuantity && catalog.dispatchDelayTicks >= 0 &&
                catalog.leadTimeTicks > catalog.dispatchDelayTicks;
        }

        private static int CurrentStackLimit(ThingDef itemDef)
        { return itemDef == null || itemDef.stackLimit < 1 ? 1 : itemDef.stackLimit; }

        private static bool TryAddTicks(int start, int delta, out int result)
        {
            long total = (long)start + delta;
            result = total > int.MaxValue ? 0 : (int)total;
            return total <= int.MaxValue && total >= 0;
        }

        private static CompanyActionResult CheckCampaign(RimroomsCampaignComponent campaign)
        {
            if (campaign == null || !campaign.CanOperate) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            if (campaign.Headquarters == null || campaign.Headquarters.Disposed) { return CompanyActionResult.Refused("RR_Proc_HeadquartersUnavailable"); }
            return CompanyActionResult.Applied();
        }

        private ProcurementOrderRecord FindOrder(string id)
        { return string.IsNullOrEmpty(id) ? null : orders.FirstOrDefault(order => order != null && order.id == id); }

        private static bool IsTerminal(ProcurementOrderStatus status)
        { return status == ProcurementOrderStatus.Delivered || status == ProcurementOrderStatus.Cancelled; }

        private bool ArchiveSettledOrdersForRoom(RimroomsCampaignComponent campaign)
        {
            while (orders.Count >= MaximumSavedOrders)
            {
                ProcurementOrderRecord candidate = orders.Where(order => order != null && IsTerminal(order.status))
                    .OrderBy(order => order.acceptedTick).ThenBy(order => order.id, StringComparer.Ordinal)
                    .FirstOrDefault(order => VerifyTerminalLedger(campaign, order) &&
                        (order.status != ProcurementOrderStatus.Delivered || PruneSettledDeliveredStackReferences(order)) &&
                        order.heldCargo.Count == 0 && HeldQuantity(order) == 0 && order.deliveredStacks.Count == 0);
                if (candidate == null) { return false; }

                long nextArchivedCount;
                long nextDeliveredCount = archivedDeliveredOrderCount;
                long nextCancelledCount = archivedCancelledOrderCount;
                long nextDeliveredQuantity = archivedDeliveredQuantity;
                try
                {
                    nextArchivedCount = checked(archivedOrderCount + 1L);
                    if (candidate.status == ProcurementOrderStatus.Delivered)
                    {
                        nextDeliveredCount = checked(archivedDeliveredOrderCount + 1L);
                        nextDeliveredQuantity = checked(archivedDeliveredQuantity + candidate.deliveredQuantity);
                    }
                    else { nextCancelledCount = checked(archivedCancelledOrderCount + 1L); }
                }
                catch (OverflowException) { return false; }

                archivedOrderCount = nextArchivedCount;
                archivedDeliveredOrderCount = nextDeliveredCount;
                archivedCancelledOrderCount = nextCancelledCount;
                archivedDeliveredQuantity = nextDeliveredQuantity;
                quotes.RemoveAll(quote => quote != null && quote.id == candidate.quoteId);
                orders.Remove(candidate);
            }
            return true;
        }

        private bool CompactOldestReceipt(ProcurementOrderRecord order)
        {
            if (order == null || order.receipts == null || order.receipts.Count == 0) { return false; }
            ProcurementDeliveryReceipt receipt = order.receipts[0];
            long expectedSequence = order.archivedDeliveryReceiptCount == 0
                ? 1L : order.lastArchivedReceiptSequence + 1L;
            if (receipt == null || receipt.sequence != expectedSequence || receipt.orderId != order.id ||
                receipt.quantityDelivered < 1 || !IsValidDeliveryStacks(receipt.deliveredStacks) ||
                receipt.deliveredStacks.Sum(stack => (long)stack.quantity) != receipt.quantityDelivered)
            { return false; }

            try
            {
                long nextReceiptCount = checked(order.archivedDeliveryReceiptCount + 1L);
                long nextDeliveredQuantity = checked(order.archivedDeliveryQuantity + receipt.quantityDelivered);
                if (order.archivedDeliveryReceiptCount == 0) { order.firstArchivedReceiptSequence = receipt.sequence; }
                order.archivedDeliveryReceiptCount = nextReceiptCount;
                order.archivedDeliveryQuantity = nextDeliveredQuantity;
                order.lastArchivedReceiptSequence = receipt.sequence;
                order.receipts.RemoveAt(0);
                return true;
            }
            catch (OverflowException) { return false; }
        }

        private void RemoveExpiredQuotes(int now)
        { quotes.RemoveAll(quote => quote == null || (!quote.accepted && now > quote.expiresTick)); }

        private void SetAwaiting(ProcurementOrderRecord order, string failureKey, int now)
        {
            order.status = ProcurementOrderStatus.AwaitingReceivingSpace;
            order.failureKey = failureKey;
            order.nextAttemptTick = now > int.MaxValue - RetryDelayTicks ? int.MaxValue : now + RetryDelayTicks;
        }

        private static void SetRecovery(ProcurementOrderRecord order, string failureKey)
        {
            order.status = ProcurementOrderStatus.RecoveryRequired;
            order.failureKey = failureKey;
        }
    }
}
