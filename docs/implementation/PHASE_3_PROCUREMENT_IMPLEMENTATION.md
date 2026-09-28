# Phase 3 procurement implementation record

**Scope:** the first local headquarters purchasing and physical receiving flow. This is a branch-local supplier order system, not shared RimTogether inventory or a finished company-wide economy.

**Verification status:** implementation source and Def/keyed content are present. The integrated source build and in-game acceptance have not been run by this work item; the parent is compiling the combined 0.3.0-dev package. Treat all interaction and save behavior as unverified until the owner-led profile run is recorded in the Phase 3 build record.

## Player flow

The Operations tab presents a small catalog of existing Core item definitions, quantity, an HQ stockpile selector, an estimated USD quote, live stack count, and mass. Accepting a quote snapshots those terms and a stable supplier schedule. The company ledger is the only currency source. Cargo is made from Core `ThingDef`s and held as real `Thing`s by the procurement `GameComponent`; there are no custom cargo items and no OgreStack assembly dependency. The Silver line is explicitly priced at a provisional supplier quote of USD 1,000 per physical Silver unit (so one million Silver would cost USD 1 billion); this is not an automatic silver-to-USD conversion and is not a final campaign balance decision.

On supplier arrival, the service checks the current HQ stockpile filter, available storage cells, vanilla storage preference, a reachable company pawn, and nearby empty Home cells. It places bounded stacks in the receiving area; RimWorld pawns then haul them with ordinary jobs. A partial delivery records only the quantities actually placed and keeps the remainder in supplier custody. The order can be retried or redirected to another accepting HQ stockpile without repricing or recharging. Cancellation is available only before dispatch and credits the original quote in full.

## Ownership and transaction safety

- `RimroomsCampaignComponent` owns the branch ID, USD balance, and stable ledger. Purchases use `<orderId>:purchase` with reason `RR_Ledger_ProcurementPurchase`; refunds use `<orderId>:cancel` with reason `RR_Ledger_ProcurementRefund`. Each receipt is rechecked for operation ID, amount, reason key, related order ID, and campaign branch before dispatch, refund completion, retry, or terminal verification.
- `RimroomsProcurementComponent` owns saved quotes, orders, one explicit `ThingOwner<Thing>` for in-transit/held shipment cargo, delivery and route receipts, and the stable order sequence. `ProcurementOrderRecord` carries the branch ID; ledger entries are campaign-owned and therefore validated against that same active branch.
- A payment failure leaves the same order in `PaymentPending`; held cargo cannot dispatch. An uncertain exception keeps the saved cargo and stable operation ID for reconciliation. A matching prior purchase with no trustworthy order is refused; a purchase call returning `AlreadyApplied` does not release duplicate cargo.
- Cancellation saves `cancelIntent` and `CancelPending` before refunding. Dispatch and delivery are blocked until the exact refund ledger receipt is verified and the held cargo can be destroyed once. Missing/ambiguous ledger state becomes a visible recovery state rather than an automatic second charge, refund, or shipment.
- Save-load reconciliation checks branch, purchase/refund ledger entries, holder ownership, receipt totals, stack references, and lifecycle state. Orders with mismatched state stop automatically. There is no cross-system atomic transaction between the company ledger, Thing holder, and map; stable receipts and fail-closed reconciliation are the recovery boundary.

## Bounded logistics and history

- Every quote and dispatch reads the live Core `ThingDef.stackLimit`; accepted quantity and USD total do not change if a stack mod later changes that value. No fixed OgreStack preset is assumed.
- A shipment is limited to 4,096 physical stacks and one million units per line. The component refuses acceptance before creating Things when the aggregate held-shipment owner would exceed 8,192 stack objects. If a later stack-limit change would exceed that concurrent limit, the paid order remains held and retryable.
- At most 100 open orders and 100 quotes are retained at once. Up to 512 detailed order records are retained; when more room is needed, only exact-ledger-verified `Delivered` or `Cancelled` orders with no held cargo and no unhauled receiving stacks can be archived. Their ledger entries remain intact, order IDs continue from the saved monotonic sequence, and aggregate delivered/cancelled counts remain visible. Ambiguous or active orders are never discarded.
- Each order retains up to 64 detailed recent delivery receipts. Older successful receipts are folded into a saved count, delivered-quantity total, and monotonic sequence range. The remaining physical cargo is separate from this receipt summary and still has to reconcile against the same order. Route-change receipts are capped at 128 and preserved.
- The Operations UI pages through all retained detailed orders and reports archived order and receipt summaries. Full receipt inspection shows the recent detailed batch list plus the archived count/quantity; older receipt detail is intentionally summarized.

## Files in this increment

- [RimroomsProcurementComponent.cs](../../src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementComponent.cs) — saved GameComponent/IThingHolder, quotes, idempotent charge/refund journal, shipping ticks, partial placement, retries, redirection, archive/receipt summaries, and save reconciliation.
- [ProcurementRecords.cs](../../src/RimroomsAsyncIndustries/Procurement/ProcurementRecords.cs) — saveable quote/order/receipt/route records and stable status values.
- [RimroomsProcurementCatalogDef.cs](../../src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementCatalogDef.cs) — policy catalog Def referencing existing items only.
- [OperationsProcurement.cs](../../src/RimroomsAsyncIndustries/UI/OperationsProcurement.cs) — quote, selection, acceptance, retry, redirect, cancellation, paged history, and receipt inspection controls. The Operations tab route itself was wired by the parent.
- [RR_ProcurementCatalog.xml](<../../Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsProcurementCatalogDefs/RR_ProcurementCatalog.xml>) — provisional prices/timing for Core Silver, Steel, Industrial Components, WoodLog, Cloth, MedicineIndustrial, and MealSurvivalPack.
- [RR_Procurement.xml](<../../Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Procurement.xml>) — UI, ledger, receipt, retry, and refusal text.

The APIs were checked against the pinned local Core source review in [PHASE_3_PROCUREMENT_TASK.md](PHASE_3_PROCUREMENT_TASK.md), including `ThingMaker.MakeThing`, live `ThingDef.stackLimit`, `ThingOwner.TryDrop`, `StoreUtility.TryFindBestBetterStoreCellFor`/`IsGoodStoreCell`, `StorageSettings.AllowedToAccept`, `SlotGroup.CellsList`, and Core Scribe ownership. The review describes source signatures; it does not establish in-game placement, active OgreStack values, save/load behavior, or native hauling results.

## Remaining acceptance work

The [parent build record](PHASE_3_BUILD_RECORD.md) now records successful integrated 0.3.0-dev compilation and staging. Future owner-led, disposable-save acceptance should verify Core-only and OgreStack active-setting profiles; affordable and unaffordable purchase; payment retry after a simulated interrupted result; pre-dispatch refund and refund retry; exact ledger operation IDs; one-time physical creation; partial and zero receiving capacity; route redirection; destroyed/filter-changed stockpiles; live stack-limit changes; held-stack budget behavior; delivery receipt compaction; order archiving; paged UI visibility; save/reload during `PaymentPending`, `CancelPending`, `InTransit`, partial delivery, and terminal states; and ordinary hauling into the selected stockpile. Test optional storage profiles separately. Do not mark runtime support until the observed game build, mod order, active stack setting, saved game, logs, and results are recorded.
