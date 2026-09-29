using System.Collections.Generic;
using System;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Procurement
{
    public enum ProcurementOrderStatus
    {
        PaymentPending = 0,
        Scheduled = 1,
        InTransit = 2,
        PartiallyDelivered = 3,
        AwaitingReceivingSpace = 4,
        Delivered = 5,
        CancelPending = 6,
        Cancelled = 7,
        RecoveryRequired = 8
    }

    public sealed class ProcurementQuoteRecord : IExposable
    {
        internal string id;
        internal string branchId;
        internal string thingDefName;
        internal string thingLabel;
        internal string receivingZoneLabel;
        internal int receivingZoneId = -1;
        internal Map receivingMap;
        internal Zone_Stockpile receivingZone;
        internal int quantity;
        internal long unitPriceUsd;
        internal long totalPriceUsd;
        internal int stackCountAtQuote;
        internal float estimatedMassKg;
        internal int createdTick;
        /// <summary>
        /// **Legacy since 0.11.0-dev: set by nothing, read by nothing.** A quote no longer
        /// expires. Kept scribed so a save written before that checkpoint still loads.
        /// Archived in full: docs/implementation/historical-content/0.11.0-dev/RETIRED_OFFER_CLOCKS.md
        /// </summary>
        internal int expiresTick;
        internal int dispatchTick;
        internal int arrivalTick;
        internal bool accepted;

        public string Id { get { return id; } }
        public string ThingDefName { get { return thingDefName; } }
        public string ThingLabel { get { return thingLabel; } }
        public string ReceivingZoneLabel { get { return receivingZoneLabel; } }
        public int ReceivingZoneId { get { return receivingZoneId; } }
        public int Quantity { get { return quantity; } }
        public long UnitPriceUsd { get { return unitPriceUsd; } }
        public long TotalPriceUsd { get { return totalPriceUsd; } }
        public int StackCountAtQuote { get { return stackCountAtQuote; } }
        public float EstimatedMassKg { get { return estimatedMassKg; } }
        public int ExpiresTick { get { return expiresTick; } }
        public int DispatchTick { get { return dispatchTick; } }
        public int ArrivalTick { get { return arrivalTick; } }
        public bool Accepted { get { return accepted; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_procQuoteId");
            Scribe_Values.Look(ref branchId, "rr_procBranchId");
            Scribe_Values.Look(ref thingDefName, "rr_procThingDefName");
            Scribe_Values.Look(ref thingLabel, "rr_procThingLabel");
            Scribe_Values.Look(ref receivingZoneLabel, "rr_procZoneLabel");
            Scribe_Values.Look(ref receivingZoneId, "rr_procZoneId", -1);
            Scribe_References.Look(ref receivingMap, "rr_procReceivingMap");
            Scribe_References.Look(ref receivingZone, "rr_procReceivingZone");
            Scribe_Values.Look(ref quantity, "rr_procQuantity");
            Scribe_Values.Look(ref unitPriceUsd, "rr_procUnitPriceUsd");
            Scribe_Values.Look(ref totalPriceUsd, "rr_procTotalPriceUsd");
            Scribe_Values.Look(ref stackCountAtQuote, "rr_procStackCountAtQuote");
            Scribe_Values.Look(ref estimatedMassKg, "rr_procEstimatedMassKg");
            Scribe_Values.Look(ref createdTick, "rr_procCreatedTick");
            Scribe_Values.Look(ref expiresTick, "rr_procExpiresTick");
            Scribe_Values.Look(ref dispatchTick, "rr_procDispatchTick");
            Scribe_Values.Look(ref arrivalTick, "rr_procArrivalTick");
            Scribe_Values.Look(ref accepted, "rr_procAccepted");
        }
    }

    public sealed class ProcurementOrderRecord : IExposable
    {
        internal string id;
        internal string quoteId;
        internal string branchId;
        internal string thingDefName;
        internal string thingLabel;
        internal string receivingZoneLabel;
        internal int receivingZoneId = -1;
        internal Map receivingMap;
        internal Zone_Stockpile receivingZone;
        internal int quantity;
        internal int deliveredQuantity;
        internal long unitPriceUsd;
        internal long totalPriceUsd;
        internal int stackCountAtQuote;
        internal float estimatedMassKg;
        internal int acceptedTick;
        internal int dispatchTick;
        internal int dispatchedTick = -1;
        internal int arrivalTick;
        internal int nextAttemptTick;
        internal long deliveryReceiptSequence;
        internal long archivedDeliveryReceiptCount;
        internal long archivedDeliveryQuantity;
        internal long firstArchivedReceiptSequence;
        internal long lastArchivedReceiptSequence;
        internal long settledDeliveredStackQuantity;
        internal ProcurementOrderStatus status;
        internal bool paymentVerified;
        internal bool cancelIntent;
        internal int routeChangeSequence;
        internal string failureKey;
        internal List<Thing> heldCargo = new List<Thing>();
        internal List<ProcurementDeliveryStack> deliveredStacks = new List<ProcurementDeliveryStack>();
        internal List<ProcurementDeliveryReceipt> receipts = new List<ProcurementDeliveryReceipt>();
        internal List<ProcurementRouteChangeRecord> routeChanges = new List<ProcurementRouteChangeRecord>();

        public string Id { get { return id; } }
        public string QuoteId { get { return quoteId; } }
        public string ThingDefName { get { return thingDefName; } }
        public string ThingLabel { get { return thingLabel; } }
        public string ReceivingZoneLabel { get { return receivingZoneLabel; } }
        public int ReceivingZoneId { get { return receivingZoneId; } }
        public int Quantity { get { return quantity; } }
        public int DeliveredQuantity { get { return deliveredQuantity; } }
        public int RemainingQuantity { get { return MathMaxZero(quantity - deliveredQuantity); } }
        public long UnitPriceUsd { get { return unitPriceUsd; } }
        public long TotalPriceUsd { get { return totalPriceUsd; } }
        public int StackCountAtQuote { get { return stackCountAtQuote; } }
        public float EstimatedMassKg { get { return estimatedMassKg; } }
        public int DispatchTick { get { return dispatchTick; } }
        public int ArrivalTick { get { return arrivalTick; } }
        public ProcurementOrderStatus Status { get { return status; } }
        public long ArchivedDeliveryReceiptCount { get { return archivedDeliveryReceiptCount; } }
        public long ArchivedDeliveryQuantity { get { return archivedDeliveryQuantity; } }
        public long FirstArchivedReceiptSequence { get { return firstArchivedReceiptSequence; } }
        public long LastArchivedReceiptSequence { get { return lastArchivedReceiptSequence; } }
        public bool PaymentVerified { get { return paymentVerified; } }
        public bool CancelIntent { get { return cancelIntent; } }
        public string FailureKey { get { return failureKey; } }
        public IReadOnlyList<ProcurementDeliveryReceipt> Receipts { get { return receipts; } }
        public IReadOnlyList<ProcurementRouteChangeRecord> RouteChanges { get { return routeChanges; } }

        private static int MathMaxZero(int value) { return value < 0 ? 0 : value; }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_procOrderId");
            Scribe_Values.Look(ref quoteId, "rr_procOrderQuoteId");
            Scribe_Values.Look(ref branchId, "rr_procOrderBranchId");
            Scribe_Values.Look(ref thingDefName, "rr_procOrderThingDefName");
            Scribe_Values.Look(ref thingLabel, "rr_procOrderThingLabel");
            Scribe_Values.Look(ref receivingZoneLabel, "rr_procOrderZoneLabel");
            Scribe_Values.Look(ref receivingZoneId, "rr_procOrderZoneId", -1);
            Scribe_References.Look(ref receivingMap, "rr_procOrderMap");
            Scribe_References.Look(ref receivingZone, "rr_procOrderZone");
            Scribe_Values.Look(ref quantity, "rr_procOrderQuantity");
            Scribe_Values.Look(ref deliveredQuantity, "rr_procDeliveredQuantity");
            Scribe_Values.Look(ref unitPriceUsd, "rr_procOrderUnitPriceUsd");
            Scribe_Values.Look(ref totalPriceUsd, "rr_procOrderTotalPriceUsd");
            Scribe_Values.Look(ref stackCountAtQuote, "rr_procOrderStackCountAtQuote");
            Scribe_Values.Look(ref estimatedMassKg, "rr_procOrderEstimatedMassKg");
            Scribe_Values.Look(ref acceptedTick, "rr_procAcceptedTick");
            Scribe_Values.Look(ref dispatchTick, "rr_procOrderDispatchTick");
            Scribe_Values.Look(ref dispatchedTick, "rr_procDispatchedTick", -1);
            Scribe_Values.Look(ref arrivalTick, "rr_procOrderArrivalTick");
            Scribe_Values.Look(ref nextAttemptTick, "rr_procNextAttemptTick");
            Scribe_Values.Look(ref deliveryReceiptSequence, "rr_procReceiptSequence");
            Scribe_Values.Look(ref archivedDeliveryReceiptCount, "rr_procArchivedReceiptCount");
            Scribe_Values.Look(ref archivedDeliveryQuantity, "rr_procArchivedDeliveryQuantity");
            Scribe_Values.Look(ref firstArchivedReceiptSequence, "rr_procFirstArchivedReceiptSequence");
            Scribe_Values.Look(ref lastArchivedReceiptSequence, "rr_procLastArchivedReceiptSequence");
            Scribe_Values.Look(ref settledDeliveredStackQuantity, "rr_procSettledDeliveredStackQuantity");
            Scribe_Values.Look(ref status, "rr_procOrderStatus");
            Scribe_Values.Look(ref paymentVerified, "rr_procPaymentVerified");
            Scribe_Values.Look(ref cancelIntent, "rr_procCancelIntent");
            Scribe_Values.Look(ref routeChangeSequence, "rr_procRouteChangeSequence");
            Scribe_Values.Look(ref failureKey, "rr_procFailureKey");
            Scribe_Collections.Look(ref heldCargo, "rr_procHeldCargo", LookMode.Reference);
            Scribe_Collections.Look(ref deliveredStacks, "rr_procDeliveredStacks", LookMode.Deep);
            Scribe_Collections.Look(ref receipts, "rr_procDeliveryReceipts", LookMode.Deep);
            Scribe_Collections.Look(ref routeChanges, "rr_procRouteChanges", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                heldCargo = heldCargo ?? new List<Thing>();
                deliveredStacks = deliveredStacks ?? new List<ProcurementDeliveryStack>();
                receipts = receipts ?? new List<ProcurementDeliveryReceipt>();
                routeChanges = routeChanges ?? new List<ProcurementRouteChangeRecord>();
            }
        }
    }

    public sealed class ProcurementRouteChangeRecord : IExposable
    {
        internal string id;
        internal int tick;
        internal int oldZoneId = -1;
        internal int newZoneId = -1;
        internal string oldZoneLabel;
        internal string newZoneLabel;

        public string Id { get { return id; } }
        public int Tick { get { return tick; } }
        public string OldZoneLabel { get { return oldZoneLabel; } }
        public string NewZoneLabel { get { return newZoneLabel; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_procRouteChangeId");
            Scribe_Values.Look(ref tick, "rr_procRouteChangeTick");
            Scribe_Values.Look(ref oldZoneId, "rr_procRouteChangeOldZoneId", -1);
            Scribe_Values.Look(ref newZoneId, "rr_procRouteChangeNewZoneId", -1);
            Scribe_Values.Look(ref oldZoneLabel, "rr_procRouteChangeOldZoneLabel");
            Scribe_Values.Look(ref newZoneLabel, "rr_procRouteChangeNewZoneLabel");
        }
    }

    public sealed class ProcurementDeliveryStack : IExposable
    {
        internal Thing thing;
        internal int quantity;
        internal int receivingZoneId = -1;
        internal string loadId;
        internal IntVec3 stagedCell;

        public Thing Thing { get { return thing; } }
        public int Quantity { get { return quantity; } }
        public int ReceivingZoneId { get { return receivingZoneId; } }
        public string LoadId { get { return loadId; } }

        public void ExposeData()
        {
            Scribe_References.Look(ref thing, "rr_procDeliveredStackThing");
            Scribe_Values.Look(ref quantity, "rr_procDeliveredStackQuantity");
            Scribe_Values.Look(ref receivingZoneId, "rr_procDeliveredStackZoneId", -1);
            Scribe_Values.Look(ref loadId, "rr_procDeliveredStackLoadId");
            Scribe_Values.Look(ref stagedCell, "rr_procDeliveredStackStagedCell");
        }
    }

    public sealed class ProcurementDeliveryReceipt : IExposable
    {
        internal string id;
        internal string orderId;
        internal long sequence;
        internal int tick;
        internal int quantityDelivered;
        internal int remainingHeld;
        internal int receivingZoneId = -1;
        internal string receivingZoneLabel;
        internal List<ProcurementDeliveryStack> deliveredStacks = new List<ProcurementDeliveryStack>();
        internal List<string> resultingThingLoadIds = new List<string>();

        public string Id { get { return id; } }
        public string OrderId { get { return orderId; } }
        public long Sequence { get { return sequence; } }
        public int Tick { get { return tick; } }
        public int QuantityDelivered { get { return quantityDelivered; } }
        public int RemainingHeld { get { return remainingHeld; } }
        public string ReceivingZoneLabel { get { return receivingZoneLabel; } }
        public IReadOnlyList<string> ResultingThingLoadIds { get { return resultingThingLoadIds; } }
        public IReadOnlyList<ProcurementDeliveryStack> DeliveredStacks { get { return deliveredStacks; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_procReceiptId");
            Scribe_Values.Look(ref orderId, "rr_procReceiptOrderId");
            Scribe_Values.Look(ref sequence, "rr_procReceiptSequenceNumber");
            Scribe_Values.Look(ref tick, "rr_procReceiptTick");
            Scribe_Values.Look(ref quantityDelivered, "rr_procReceiptQuantity");
            Scribe_Values.Look(ref remainingHeld, "rr_procReceiptRemaining");
            Scribe_Values.Look(ref receivingZoneId, "rr_procReceiptZoneId", -1);
            Scribe_Values.Look(ref receivingZoneLabel, "rr_procReceiptZoneLabel");
            Scribe_Collections.Look(ref deliveredStacks, "rr_procReceiptStacks", LookMode.Deep);
            Scribe_Collections.Look(ref resultingThingLoadIds, "rr_procReceiptThings", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                deliveredStacks = deliveredStacks ?? new List<ProcurementDeliveryStack>();
                resultingThingLoadIds = resultingThingLoadIds ?? new List<string>();
            }
        }
    }
}
