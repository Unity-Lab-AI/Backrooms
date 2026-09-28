# Phase 2 row 4: gate, work, power, and research source review

**Checked:** 2026-09-28
**Status:** source review complete; implementation-facing routes below. No game launch, build, gameplay test, or profile change was performed.

## Scope and pinned source

This review covers the [Phase 2 vertical slice](PHASE_2_VERTICAL_SLICE_TASK.md), the [first-playable contract](../FIRST_PLAYABLE_CONTRACT.md), and the [power/gate source audit](../research/POWER_GATE_AND_TURRET_SOURCE_AUDIT.md). It inspected the installed RimWorld Core assembly only:

- `Assembly-CSharp.dll`: version `1.6.9676.17735`, SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`.
- Local assembly path: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`.
- Decompiler: `.local/tools/ilspycmd.exe`, ILSpy `9.1.0.7988`. Decompiled inspection files are in ignored `.local/inspection-work`; they are reference notes and are not project source or redistributed game code.

Claims below are exact API/source observations or explicitly labeled design proposals. They are not in-game behavior evidence.

## First-slice implementation route

### Native bill for the final physical assembly

Use the 1×1 `RR_GateConsole` as a powered Core `Building_WorkTable` bill giver, with a custom Rimrooms component and a one-shot `RR_AssembleMachineGate` recipe. The recipe ingredient list is exactly 100 Steel and 8 ComponentIndustrial, its work amount remains a tunable Def value, and a custom `RecipeWorker` handles the completion callback. This uses Core's normal bill/material/work lifecycle instead of an instant-consumption gizmo.

The inspected route is:

1. `RimWorld.WorkGiver_DoBill.JobOnThing(Pawn, Thing, bool)` checks that the bill giver is usable, has work to do, can be reserved, and has the ingredients; `TryStartNewDoBillJob(Pawn, Bill, IBillGiver, List<ThingCount>, out Job, bool)` creates `JobDefOf.DoBill` and queues the real ingredient Things and requested counts.
2. `Verse.AI.JobDriver_DoBill.TryMakePreToilReservations(bool)` reserves the bill giver and interaction cell. `MakeNewToils()` routes the pawn through `CollectIngredientsToils(...)`, which reserves/carries the queued materials, returns to the bill giver, then runs `Toils_Recipe.DoRecipeWork()`.
3. `DoRecipeWork()` advances `workLeft` in `tickIntervalAction(int delta)` using the recipe's work amount and configured work-speed stat. It reports progress and only proceeds when work reaches zero.
4. `Toils_Recipe.FinishRecipeAndStartStoringProduct(TargetIndex)` calculates ingredients, creates any products, consumes the physical ingredients, and calls `Bill.Notify_IterationCompleted(Pawn, List<Thing>)`. A Gate `RecipeWorker.Notify_IterationCompleted(Pawn, List<Thing>)` can then set the linked gate's assembly state once. A no-product assembly recipe is supported by this lifecycle: the bill job ends successfully when no product Thing is returned.
5. The completion callback must be idempotent and suspend/remove the gate's one-shot bill after success. It must check that the current DoBill target is the correct console and the matching recipe before changing gate state. The callback runs after Core consumes the inputs; do not report success if that commit did not occur.

Relevant inspected types/signatures: `Verse.RecipeDef` exposes `workAmount`, `ingredients`, `fixedIngredientFilter`, `products`, `skillRequirements`, `workSkill`, and `recipeUsers`; `RimWorld.Building_WorkTable` exposes `BillStack`, `BillInteractionCell`, `CurrentlyUsableForBills()`, and `UsableForBillsAfterFueling()`. Core work tables check `CompPowerTrader.PowerOn` unless `CanWorkWithoutPower` is true.

### Calibration and the assigned operator

Assembly and calibration are separate progress states. Calibration is staffed work at the console; opening also requires the assigned operator to be physically staffing the station in a real reserving job.

- A custom `WorkGiver_Scanner` uses the Core pattern `PotentialWorkThingRequest`, `HasJobOnThing(Pawn, Thing, bool)`, and `JobOnThing(Pawn, Thing, bool)` to offer calibration only for a spawned, assembled, uncalibrated gate/console pair and a capable assigned staff pawn.
- `JobDriver_RRCalibrateGate.TryMakePreToilReservations(bool)` reserves the console and its interaction spot. `MakeNewToils()` moves to the interaction cell and advances calibration through a `Toil.tickIntervalAction(int delta)`; only work completion sets `Calibrated=true`. Refusal or interruption leaves progress/state recoverable.
- A separate `RR_OperateGate` job reserves the console and remains there in a never-ending station toil. `IsOperatorOnStation` is true only when the saved `AssignedOperator` is still employed, alive, spawned on the gate map, not downed/in a mental state, has the operator job targeting this console, is at its interaction cell, and the console's native power/flick/breakdown state is usable. Assignment validates the pawn is eligible and present on the facility map; after a stranded run closes its gate state, the player can replace a dead/invalid operator. The assignment gizmo offers eligible employed branch staff from the saved staff records; a second command starts the actual operator job through `Pawn.jobs.TryTakeOrderedJob(...)`. During an emergency, the player may restart the assigned operator job so the gate can be staffed for recovery; assignment remains locked while an expedition is active.
- `CanOpen(Pawn gateOperator, string expeditionId)` requires the passed pawn to be the saved `AssignedOperator` and `IsOperatorOnStation` to be true at the moment of opening. It also projects the change from the current gate draw to the configured 3,500 W opening draw: current `PowerNet.CurrentEnergyGainRate()` is converted to watts, the additional gate load is subtracted, and the configured minimum network headroom must remain. While open, loss of power, loss/interruption of the station job, or timer expiry sets a visible emergency/failure state. The gate retains the active expedition ID and zero/remaining ticks until the expedition service consumes the status and calls `CloseOpening()`; it does not destroy a site or move pawns.
- The default 833-tick normal window saves three per-opening warning flags and notifies once as remaining time crosses 417, 208, and 83 ticks (about 10, 5, and 2 in-game minutes). Initial opening retries do not reset these flags; accepted paid recovery resets them for its fresh window.

The vanilla patterns inspected for these jobs are `Verse.AI.JobDriver.TryMakePreToilReservations(bool)`/`MakeNewToils()`, `Verse.ReservationManager.Reserve(Pawn, Job, LocalTargetInfo, int, int, ReservationLayerDef, bool, bool, bool)`, `Toils_Reserve.Reserve(TargetIndex, int, int, ReservationLayerDef, bool)`, and `Toils_Goto.GotoThing(TargetIndex, PathEndMode)`. A successful workgiver result is not station readiness; readiness is checked against the active job, assigned identity, and current interaction-cell position.

### Physical construction remains available

Core's alternative construction route is `Frame.TotalMaterialCost()`, `Frame.ThingCountNeeded(ThingDef)`, `Frame.IsCompleted()`, and `Frame.CompleteConstruction(Pawn)`. `WorkGiver_ConstructDeliverResourcesToFrames` selects reachable material stacks and produces `JobDefOf.HaulToContainer`; `JobDriver_HaulToContainer` reserves, carries, and deposits them into the frame. `WorkGiver_ConstructFinishFrames` issues `JobDefOf.FinishFrame`; `JobDriver_ConstructFinishFrame` reserves the frame and adds construction work before completion.

That route is appropriate for building the physical gate shell, but the 100 Steel + 8 ComponentIndustrial final assembly/calibration step is assigned to the staffed console bill above so it has an explicit, one-time completion boundary.

## Power and emergency return reserve

### Verified Core behavior

- `CompPowerTrader.PowerOutput` is writable. Its setter updates the signed watt draw/output field and output display state; it does not itself debit a battery or transfer energy to another component.
- `CompPowerTrader.EnergyOutputPerTick` is `PowerOutput * CompPower.WattsToWattDaysPerTick`. `SetUpPowerVars()` resets the output from the Def's idle/normal consumption values. `PostExposeData()` saves `PowerOn`, not a custom runtime `PowerOutput` value, so dynamic loads must be recalculated after load/spawn.
- `PowerNet.CurrentEnergyGainRate()` sums online traders' `EnergyOutputPerTick`; `CurrentStoredEnergy()` sums the `StoredEnergy` of every non-EMP-stunned battery on that net. `PowerNetTick()` evaluates this aggregate, changes shared battery charge, and may switch consumers off during a deficit. There is no per-consumer delivered-energy meter, battery reservation, or load-priority guarantee.
- `PowerNet.CanPowerNow(CompPowerTrader)` is a current aggregate estimate. It is not an atomic reservation or a promise that a shared facility battery is held for the gate.
- `CompPowerBattery.StoredEnergy`, `DrawPower(float)`, and `AddEnergy(float)` expose actual battery storage operations; `DrawPower` subtracts from the shared battery and logs/clamps if asked for more energy than it contains. A battery attached to the ordinary facility net is therefore not an exclusive gate reserve.

### Gate-owned reserve design

Keep emergency-return watt-days in a separately serialized gate-owned value with visible current/capacity readouts, not in the shared facility battery total. While its `CompPowerTrader` is online and connected, the gate's charging mode sets a configured negative `PowerOutput`; add exactly the corresponding `-EnergyOutputPerTick` to the gate-owned watt-day store per accepted powered tick. This accounts for the same native load in the PowerNet aggregate and avoids claiming any part of another battery's charge. Recompute dynamic output from component state on spawn/load.

Open readiness checks the calibrated gate, an operator physically on station, the powered state/stability window, the configured minimum return charge, and reserve capacity. One emergency use subtracts one fixed Def-configured cost and records the active expedition identity before reporting success. Repeating the spend for that active expedition returns `CompanyActionResult.Existing()` and never subtracts twice. No facility battery count is treated as gate-owned reserve.

The PowerNet source is aggregate rather than metered. Therefore, this is load-accounted gate storage; actual behavior through brownouts, outages, tick order, and save/load remains post-code acceptance work. Do not present the reserve as runtime-proven before that acceptance.

## Core-only company research decision

Do not create `RR_RouteInsight` or use a `ResearchProjectDef` prerequisite as the company insight gate. Core `ResearchProjectDef.CanStartNow` is a concrete non-virtual property; it checks its built-in prerequisites, bench, techprints, mechanitor, analyzed-things, and hidden state. `hideWhen` describes storyteller difficulty conditions, not campaign data. `requiredAnalyzed` resolves through `Find.AnalysisManager` and Core clears it when Biotech is inactive. `knowledgeCategory`/`knowledgeCost` are Anomaly paths. `ResearchManager.SetCurrentProject(ResearchProjectDef)` does not itself enforce `CanStartNow`, and `ResearchManager.FinishProject(ResearchProjectDef, bool, Pawn, bool)` recursively finishes native prerequisites.

The approved Core-only route is the custom Rimrooms company project: validated analysis commits its earned insight to the branch-owned `ProjectRecord` (whose pre-release `researchDefName` remains `RR_GateTelemetry`), and an Investigation-owned `RimroomsProjectDef` plus staffed research job controls company progress. Keep vanilla `ResearchProjectDef`/`ResearchManager` completely separate and untouched. Never manually finish or instantly complete Gate Telemetry through Core research APIs. The lead owns the custom project Def and staffed analysis/research implementation; the Gate module only exposes gate-side readiness/state and does not change `ProjectRecord`.

The native research route inspected for contrast is `WorkGiver_Researcher.HasJobOnThing(Pawn, Thing, bool)` / `JobOnThing(Pawn, Thing, bool)` followed by `JobDriver_Research.TryMakePreToilReservations(bool)` and `MakeNewToils()`. The driver reserves the bench and interaction cell, then its staffed work toil calls `ResearchManager.ResearchPerformed(float, Pawn)` over time. `ResearchProjectDef.CanBeResearchedAt(Building_ResearchBench, bool)` checks the required bench, power, and required facilities. Those native routes remain intact for ordinary colony research.

## Public Gate API for the expedition service

Gate state is owned by the `RR_MachineGate` component. The expedition/Operations services may call these public members after their branch-state guard:

| Member | Contract |
| --- | --- |
| `Pawn AssignedOperator { get; }` | Saved pawn reference assigned from employed staff through the gate command. |
| `bool IsOperatorOnStation { get; }` | Requires identity, presence, active operator job targeting the paired console, interaction-cell position, and a capable/non-interrupted pawn. |
| `bool AssemblyComplete { get; }`, `bool Calibrated { get; }` | Persisted stage state, changed only by completed staffed work. |
| `bool IsOpening { get; }`, `string ActiveExpeditionId { get; }`, `int OpeningTicksRemaining { get; }` | Persisted active window; expiry leaves status for the branch service to process. |
| `bool EmergencyReturnSpentForActiveExpedition { get; }`, `string FailureKey { get; }` | Visible, saved emergency/failure state. Power/assignment/job interruptions and timer expiry do not erase the expedition ID. |
| `float ReturnReserveStoredWattDays { get; }`, `float ReturnReserveCapacityWattDays { get; }` | Gate-owned, serialized and visible charged-return reserve. |
| `float RecoveryOpeningCostWattDays { get; }` | Def-configured recovery activation fee, deducted once after successful recovery preflight. |
| `CompanyActionResult CanOpen(Pawn gateOperator, string expeditionId)` | Pure preflight. It requires `gateOperator == AssignedOperator`, `IsOperatorOnStation`, calibrated/assembled state, unique nonempty ID, stable power, no active window, and sufficient stored return energy. |
| `CompanyActionResult BeginOpening(string expeditionId)` | Rechecks gate-local conditions and atomically starts the configured opening window. No crew/map transfer. |
| `CompanyActionResult SpendOpeningTicks(string expeditionId, int ticks, string operationId)` | Applies a positive, idempotent environmental time debit to the matching normal window. It records requested and effective ticks; a cost greater than remaining time reduces the window to zero and starts emergency. |
| `bool TryGetOpeningTicksSpendReceipt(string operationId, out int requestedTicks, out int appliedTicks)` | Reads the saved cost receipt for controller reconciliation. |
| `CompanyActionResult CanRecover(Pawn gateOperator, string expeditionId, string recoveryOperationId)` | Preflights a new opening either for the same active expedition after its emergency-return window expires, or for the exact most recently closed ID saved by `CloseOpening()`. Requires staffing, stable power, projected opening headroom, and a fully charged separate reserve. The expedition controller must allow this only for `Stranded` status; `Completed` and `Abandoned` are terminal there. |
| `CompanyActionResult BeginRecoveryOpening(string expeditionId, string recoveryOperationId)` | Records a distinct stable recovery receipt; reactivates the same active/latest-closed expedition ID, deducts the configured recovery activation cost once, and grants a fresh configured opening/emergency window. It retains prior environmental cost receipts. A matching retry returns `Existing()` without resetting or deducting again. |
| `void CloseOpening()` | Clears active-window state, saves `lastClosedExpeditionId` for a stranded-run recovery path, and leaves run status/result ownership with the branch expedition service. It does not move pawns or destroy the destination. |
| `CompanyActionResult TrySpendEmergencyReturnReserve(string expeditionId)` | Only spends for the matching active ID, one fixed configured cost once; repeated call for that active ID returns `Existing()`. |
| `CompanyActionResult OrderCalibration()` / `OrderStaffConsole()` | Player-facing job-order methods for the Operations interface; ordinary gate gizmos call the same paths. |

The current normal opening default is 833 ticks (20 in-game minutes at 2,500 Core ticks per hour). Opening/power values remain Def-tuned hypotheses until gameplay acceptance measures them. Recovery is a separate operation: for an active gate ID, its bounded emergency-return window must expire; after `CloseOpening`, only its saved most-recently-closed ID is eligible. The operator must be staffing, the network live and stable, and projected opening headroom available; the gate-owned reserve must be fully recharged over powered ticks. A new stable recovery receipt then deducts the separate Def-configured recovery activation fee (currently provisionally 1 watt-day, leaving the configured 1 watt-day emergency-return fee available from the 2 watt-day capacity) and starts a fresh configured normal/emergency window for the same expedition ID. This pays recovery through actual charged-power time and an explicit reserve cost, retains prior environmental time-cost receipts, and never directly allocates a shared facility battery. A failed preflight does not store a receipt; a same-receipt retry does not refill the reserve or reset time or deduct twice. `BeginOpening` with the same active normal ID or most recently closed ID is idempotent and never restores the window. The API deliberately leaves expedition creation, crew manifests, map generation, dispatch, recall, stranded status, and site destruction outside `Gate/`.

## Remaining acceptance and integration checks

- No source observation verifies a configured powered console or generator runs correctly in a live map. Confirm placement/interaction cells, bill creation, physical 100 + 8 material sourcing, one-time recipe completion, calibration work, operator reservation/position, station interruption, dynamic charge accounting, opening timer, failure visibility, and save/load after a later build.
- Confirm the gate-owned reserve increases only by its configured PowerNet load and cannot be read/spent as shared `CompPowerBattery` energy; test power shortage, EMP, breakdown, brownout, and restored power.
- Confirm the expedition service's `Strand()` closure can recover using the saved latest-closed ID, while it rejects Completed/Abandoned records; confirm it—not the gate—records crew/map recovery.
- Confirm the custom company research job consumes only the validated branch insight and advances only through staffed work; normal RimWorld research must remain unchanged.
