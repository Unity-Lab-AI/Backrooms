# Phase 2 gate and console implementation

**Status:** Gate module implementation draft; code and XML are present, but no RimWorld build or in-game acceptance has been run. Values called provisional below remain tuning hypotheses.

This slice creates a powered, staffed machine gate as the physical opening into a branch-owned expedition. It deliberately stops at gate status and operation receipts: expedition manifests, crew movement, maps/sites, recall, stranded outcomes, and trade are owned by the expedition/company systems.

## Included content

| Def / component | Shape and role | Current setup |
| --- | --- | --- |
| `RR_MachineGate` | 3x3 gate; south interaction cell is `GateEntryCell` | Original texture `1.6/Textures/Buildings/Gate/RR_MachineGate.png`; powered `CompRimroomsGate`; Core flickable and breakdownable comps |
| `RR_GateConsole` | 1x1 powered Core worktable and bill giver | Original console texture; 100 Steel + 8 ComponentIndustrial recipe; staffed assembly and calibration; real operator job |
| `RR_EmergencyCutoff` | 1x1 player control | Original cutoff texture; requests an emergency state on its nearest gate |
| `RR_UtilityGenerator` | 2x2 wood-fueled Core generator | Original generator texture; configured for 6,000 W; fuel is WoodLog |
| `RR_AssembleMachineGate` | One-shot console recipe | Carries and consumes 100 Steel + 8 industrial components through Core's bill/work lifecycle; 6,000 work is provisional |
| `RR_CalibrateGate` | Staffed intellectual-work job | Completes a saved calibration work requirement; current 2,500 work is provisional |
| `RR_OperateGate` | Long-running station job | Reserves the console and interaction cell; loss of job/pawn readiness is visible to the gate |

Construction costs, power ratings, reserve capacity/cost, work values, and the default 833-tick opening (20 in-game minutes) are initial tuning values. The opening duration is 833 ticks because Core runs at 2,500 ticks per hour. These values still require owner review where pending and in-game balancing.

## Gate lifecycle

1. Construct gate, console, cutoff, and generator through ordinary Core construction and hauling. The scenario may provide the specified starting generator fuel/wood separately.
2. Assign one employed staff pawn through `AssignOperator(Pawn)`. The pawn uses the actual console job to calibrate, then a separate long-running console job to staff the opening.
3. The console's one-shot bill makes the final gate assembly physical. Core carries ingredients and advances staffed bill work; only the completion callback marks the gate assembled. Calibration is separate and also advances from staffed work.
4. The operator must be the saved `AssignedOperator`, employed, alive and capable, on the gate's map, at the powered console interaction cell, and actively running `RR_OperateGate` against that console. The gate and console must both have live powered connections; a valid employee elsewhere does not satisfy readiness. After the run is closed as stranded, the company may reassign the gate to another eligible employed pawn.
5. `CanOpen` checks the assigned/operator identity, station job and position, assembly/calibration, stable live power/headroom, a nonempty expedition ID, and the emergency reserve cost. It also projects the switch from the current idle/charge draw to the configured 3,500 W opening draw and requires the configured minimum aggregate headroom after that change. `BeginOpening` repeats the checks before starting the configured normal window. The gate draws its configured opening load while open.
6. Power loss, operator/job loss, cutoff, time cost exhausting the normal window, or normal timer expiry enters a bounded emergency-return window. Saved warning flags trigger once per opening at about 10, 5, and 2 in-game minutes remaining (417, 208, and 83 ticks); a paid recovery opening resets those flags. `FailureKey`, `ActiveExpeditionId`, and the timer remain saved and visible while open. The gate does not teleport pawns or destroy a map.
7. `TrySpendEmergencyReturnReserve` spends its one configured cost only for the matching active expedition and live emergency window. A repeated request is idempotent. The expedition service must record who returned/stranded before calling `CloseOpening()`.
8. `CloseOpening()` clears the active ID and timers and saves the exact `lastClosedExpeditionId`. This lets the company recover a stranded run even though `Strand()` has closed its gate state. A new recovery attempt requires the assigned operator actively staffing, stable live power/headroom, and the separate gate-owned capacitor fully recharged. `BeginRecoveryOpening` accepts either an active run whose bounded emergency window has expired or the most recently closed run ID; it uses a new stable recovery operation ID, deducts the configured recovery activation charge (currently provisionally 1 watt-day), reactivates that expedition ID, and starts a fresh configured normal window with the configured emergency-return charge still available. It preserves all environmental time-cost receipts for the expedition. Failed preflight writes no receipt; a retry of an accepted recovery receipt returns Existing and never resets its timers or reserve or deducts twice. The Gate component knows only its latest closed ID; the expedition controller must enforce that only `Stranded` runs can recover and that `Completed`/`Abandoned` runs remain terminal.
9. `CloseOpening()` also remembers the last closed expedition ID for safe idempotent handling. A retry of `BeginOpening` with that ID cannot reopen or restore its timer; recovery requires its distinct recovery operation API and receipt.

The gate-owned reserve is a serialized watt-day value charged only while its own configured negative `CompPowerTrader.PowerOutput` is online, connected, and the measured aggregate network headroom meets the configured threshold. It adds the same accepted load energy per tick to the local store; it does not claim or debit shared facility battery contents. A later recovery waits for the stored amount to refill fully under power, then pays a separate activation charge. The recovery therefore costs powered game time before the new powered opening and consumes a configured reserve fee; the emergency-return charge remains available for that new opening. Capacity must cover both configured costs.

Core reports aggregate PowerNet state, not energy delivered to an individual consumer. Dynamic load accounting and brownout ordering are therefore design-level accounting until a live profile verifies them. Do not treat the capacitor as a runtime-proven power guarantee.

## Saved gate activity cues

The gate writes meaningful state transitions to the branch-owned recent activity feed through `RimroomsCampaignComponent.RecordEvent` in [CompRimroomsGate](../../src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs). Transition guards and saved warning flags make these single events rather than per-tick entries. Existing warning toasts remain and now have matching saved activity rows. The activity feed itself is a saved recent-history list capped by the company component at 256 rows.

| Gate transition | Activity message key | Arguments |
| --- | --- | --- |
| Native assembly bill completes and first sets assembled | `RR_Event_GateAssemblyCompleted` | none |
| Staffed calibration completes | `RR_Event_GateCalibrationCompleted` | none |
| Normal opening begins | `RR_Event_GateOpeningStarted` | none; expedition ID is the related record ID |
| Opening closes | `RR_Event_GateOpeningClosed` | none; expedition ID is the related record ID |
| 10/5/2-minute warning threshold is crossed | Existing `RR_Gate_WarningTenMinutes`, `RR_Gate_WarningFiveMinutes`, `RR_Gate_WarningTwoMinutes` | none; each serialized flag is set once per opening |
| Power/operator loss, normal-window expiry, or cutoff enters emergency state | Existing `RR_Gate_PowerLost`, `RR_Gate_OperatorLost`, `RR_Gate_WindowExpired`, `RR_Gate_EmergencyCutoff` | none; active expedition ID is related |
| Environmental time cost exhausts the normal window | `RR_Gate_TimeCostWindowExhausted` | none; active expedition ID is related |
| Emergency-return window expires | Existing `RR_Gate_EmergencyWindowExpired` | none; active expedition ID is related |
| Emergency-return reserve is spent | `RR_Event_GateEmergencyReturnPaid` | `{0}` = configured watt-day cost to two decimal places |
| A paid recovery opening starts | `RR_Event_GateRecoveryOpeningStarted` | `{0}` = configured watt-day activation cost to two decimal places |

Assembly/calibration/opening/close events are emitted only on first state change; repeated receipt requests do not replay paid events. The time-cost failure key also appears in the gate status readout, so its translation is needed in addition to the new event translations for assembly, calibration, opening, closure, return payment, and recovery start. A UI cue or audio cue may be added after the shared presentation service is available; this gate source currently records activity only.

## Public integration surface

`RimroomsAsyncIndustries.Gate.CompRimroomsGate` is the gate state owner. The public expedition/Operations methods are:

| Member | Use |
| --- | --- |
| `Pawn AssignedOperator`, `bool IsOperatorOnStation`, `bool AssemblyComplete`, `bool Calibrated` | Read saved operator and readiness stages. |
| `IntVec3 GateEntryCell` | Physical south-side gate approach anchor for branch-owned crew routing. |
| `bool IsOpening`, `string ActiveExpeditionId`, `int OpeningTicksRemaining`, `int EmergencyReturnTicksRemaining`, `bool IsEmergency`, `bool IsAwaitingRecovery`, `string FailureKey` | Read saved gate window state without moving crew or changing sites. |
| `float ReturnReserveStoredWattDays`, `float ReturnReserveCapacityWattDays` | Read gate-local emergency/recovery charge. |
| `CompanyActionResult AssignOperator(Pawn)` | Assign or unassign an employed staff pawn. |
| `CompanyActionResult OrderCalibration()` / `OrderStaffConsole()` | Player-facing order routes for the Operations interface; native gate gizmos remain available too. |
| `CompanyActionResult CanOpen(Pawn gateOperator, string expeditionId)` | Preflight an initial opening. The passed pawn must match `AssignedOperator` and be staffing now; projected 3,500 W opening load must leave the configured aggregate headroom. |
| `CompanyActionResult BeginOpening(string expeditionId)` | Recheck local readiness and begin once. Same active or last-closed ID retries do not reset/reopen. |
| `CompanyActionResult SpendOpeningTicks(string expeditionId, int ticks, string operationId)` | Idempotently subtract a positive environmental cost from the matching normal window. If requested ticks exceed remaining time, it applies only the remaining amount, records requested/applied ticks, and enters emergency at zero. |
| `bool TryGetOpeningTicksSpendReceipt(string operationId, out int requestedTicks, out int appliedTicks)` | Read back the saved requested/effective time debit for controller reconciliation. |
| `CompanyActionResult TrySpendEmergencyReturnReserve(string expeditionId)` | Spend the one return cost during the matching live emergency window. |
| `CompanyActionResult CanRecover(Pawn gateOperator, string expeditionId, string recoveryOperationId)` | Preflight recovery after an active emergency window expires, or for the exact latest ID saved by `CloseOpening()`. Requires full reserve recharge, staffed operator, and projected opening power. The company controller must gate this to a stranded run. |
| `CompanyActionResult BeginRecoveryOpening(string expeditionId, string recoveryOperationId)` | Record a new recovery receipt, reactivate the same active/latest-closed expedition ID, deduct its configured activation cost, and open a fresh configured window; duplicate receipt never refills/reopens/deducts again. |
| `void CloseOpening()` | Clear active gate state and save the last closed expedition ID; the caller still owns the run's Completed/Stranded/Abandoned status. |

Time-cost and recovery receipts are saved by the gate component. Receipt IDs are stable caller-owned operation IDs. Reusing an ID for different parameters is refused. The expedition service owns its own retry/result ledger and must not use gate callbacks as a substitute for its transaction.

## Boundaries and acceptance work

- Company staff assignment is checked against saved campaign staff. The operations/UI caller owns appropriate command presentation and transaction ordering.
- The company research project remains outside Core's ordinary `ResearchProjectDef`/`ResearchManager`; gate calibration is not company research completion and does not grant insight.
- Other mod/DLC integrations, multiplayer transfer, expedition/site creation, and generated Backrooms spaces are not implemented by this module.
- Future acceptance must verify physical material delivery, one-shot bill completion and save/load, calibration interruptions, operator replacement after death/stranding, operator identity/job interruptions, 3,500 W projected headroom and subsequent opening draw, saved one-time 10/5/2 minute warnings, emergency timer and reserve idempotency, overlarge environmental time debits, full recharge and new recovery receipt semantics for active and last-closed stranded IDs, generator fuel exhaustion, power restoration/breakdown/EMP/brownout, UI command routing, and duplicate operation calls.
- Required evidence for supported status: exact RimWorld build, Core/DLC profile, mod order, multiplayer client/server build if applicable, save, logs, and observed result. This draft does not claim that any of those runtime checks passed.
