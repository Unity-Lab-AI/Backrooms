# Phase 2: expedition dispatch, return and physical cargo

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Date:** 2026-09-28. **State:** original source/package records written for lead integration; runtime unverified. No game launch, tests, build, mod-profile changes or external-mod changes were performed by this assignment.

## Task record and boundaries

- Parent task: [Phase 2 vertical slice](PHASE_2_VERTICAL_SLICE_TASK.md). Features **RR-EXP, RR-GATE, RR-SPACE, RR-EVD, RR-STA, RR-COMPAT**.
- Canonical inputs: [first playable](../FIRST_PLAYABLE_CONTRACT.md#gate-and-expedition-rules-for-the-prototype), [Operations action map](../OPERATIONS_ACTION_CONTRACTS.md#action-map), [saved ownership](../CAMPAIGN_STATE_DICTIONARY.md#ownership-rule), [first-slice inventory](../FIRST_SLICE_CONTENT_INVENTORY.md#expedition-content).
- Exact source row: **4**, package **`Ludeon.RimWorld`**, installed `Assembly-CSharp.dll` SHA-256 **`5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`**. No Harmony or DLC assembly is referenced by this implementation.
- Exclusive files: `src/RimroomsAsyncIndustries/Expedition/*`, the expedition JobDefs/English text below, and this record. The lead owns existing Company/UI, evidence, threat hooks, package integration and acceptance evidence. Separate agents own Gate and Generation. This assignment made no Company partial/file changes.
- Normal dispatch is one to three original staff plus a separate HQ operator. The lead approved one **additional relief person per saved run**, kept in a separate list, as recovery for incapacitated or stranded teams. Further trips may reuse that same relief person; the original crew and bonus identity never change.

## Actual created files

| File | Responsibility |
| --- | --- |
| [ExpeditionRecords.cs](../../src/RimroomsAsyncIndustries/Expedition/ExpeditionRecords.cs) | Saved run/crew/relief/entry-return/cargo and transfer-recovery records; fixed enum values. |
| [ExpeditionCargo.cs](../../src/RimroomsAsyncIndustries/Expedition/ExpeditionCargo.cs) | Physical shared-kit checks, native carry-capacity checks, real pickup-job planning, departure manifest and observed return locations/quantities. |
| [RimroomsExpeditionComponent.cs](../../src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs) | Branch-local saved controller, guarded dispatch/reopen/recall/relief actions, anchor checks, identity-preserving transfer and failure recovery. |
| [ExpeditionClosure.cs](../../src/RimroomsAsyncIndustries/Expedition/ExpeditionClosure.cs) | Explicit operation closure, historical crew recovery, observed cargo declarations and additive expedition-schema migration. |
| [JobDriver_ExpeditionApproach.cs](../../src/RimroomsAsyncIndustries/Expedition/JobDriver_ExpeditionApproach.cs) | Real native path/reservation jobs to the gate or saved return anchor; a carrying route for downed crew or remains. |
| [RR_ExpeditionJobs.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/JobDefs/RR_ExpeditionJobs.xml) | `RR_ApproachGate`, `RR_ReturnThroughGate`, `RR_CarryToReturnAnchor`; all preserve a carried thing during job cleanup and do not drop it before starting. |
| [RR_Expedition.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_Expedition.xml) | Readiness, loadout, return, emergency, casualty, recovery and cargo-report text. Native report strings remain translatable JobDef fields. |

## API for the lead's Operations and evidence flows

Namespace: `RimroomsAsyncIndustries.Expedition`. Retrieve the native-created `RimroomsExpeditionComponent` from the current Game.

| API | Effect |
| --- | --- |
| `Records`, `Active`, `InterruptedTransfers` | Read-only list views. Each run exposes `ExpeditionId`, `CoordinateId`, `InitialCrew`, `ReturnedCrew`, `RescueCrew`, `Status`, `Headquarters`, `Destination`, `ReturnCell`, `Gate`, `Cargo`, `FailureKey`, `Emergency`, `Closed`. |
| `QueueLoadout(List<Pawn>)` | Preflights all missing shared-kit items/capacity/reservations at HQ, then orders real native inventory-pickup jobs. No items are spawned or instantly moved. |
| `Dispatch(CompRimroomsGate, CoordinateRecord, List<Pawn>)` | Validates branch/staff/operator/kit/capacity/gate; generates the saved destination and ensures its unique recording before ordering crew approach. The clock begins after all selected staff reach the physical gate area. |
| `AbortStaging()` | Cancels approach before the crossing. Physical kit already picked up stays with its actual owners. Aborting a relief approach retains the original stranded run. |
| `Recall()` | Orders mobile field members to the saved threshold. Each crosses only after actually arriving and passing current gate/return/carry checks. |
| `ReopenReturnRoute()` | Uses the same run, coordinate and existing map after restored HQ readiness. It does not reroll the map, remake evidence or replace people/items. |
| `SendRelief(Pawn)` | Stages the one saved relief staff member at HQ. The original operator stays at the console. The shared kit is checked across actual original field inventories plus the relief member's HQ inventory. |
| `QueueReliefLoadout(Pawn)` | Orders pickup of physically available HQ replacements for missing shared-kit items during a stranded run. Actual original field inventories and correctly deployed aids count toward the existing shared kit. |
| `QueueCasualtyReturn(Pawn carrier, Pawn casualty)` | Orders a real approach/pickup/carry to the threshold for a downed original or relief crew member, or their actual corpse. No arbitrary remote rescue. |
| `RecoverInterruptedTransfers()` | Attempts to put a deep-held failed transfer back on its recorded **source** map near the original source cell. It never grants a second pawn or bypasses the gate to a new target. |
| `RecordCargoDisposition(string entryId, CargoDisposition, string note)` | Saves a bounded player declaration about consumption, loss or leaving cargo. Does not remove/create items or change payment. |
| `CheckCargoDisposition(string entryId, CargoDisposition, int count)` | Refreshes physical observations and refuses a report contradicted by the actual item/location/count. |
| `RecordCargoDisposition(string entryId, CargoDisposition, int count, string note)` | Saves a quantity-specific, explained declaration and its observation snapshot. A repeat of the current identical report returns Existing. |
| `RefreshManifest(string expeditionId)` | Refreshes a selected active or historical record's actual cargo and living original returns; creates no physical transfer. |
| `CanAbandonExpedition(string expeditionId)` / `PreviewAbandonment(string expeditionId)` | Validate closure and return a non-persisted people/cargo snapshot for the player's confirmation, including pending-transfer and deep-held-person counts. |
| `AbandonExpedition(string expeditionId, string reason)` | On explicit player confirmation, closes the operation as Abandoned, records its reason and immutable snapshot, closes only its matching gate, and cancels its transit jobs. Nothing is deleted or remotely reclaimed. |
| `ResumeAbandonedExpedition(string expeditionId)` | Restores recovery planning on the same record only when no run is active and the original gate accepts it as its recoverable most recently closed operation. Readiness is checked; this action does not open the gate or spend reserve. |
| `RecoverableCrewAtActiveSite()` / `QueueRecoveredCrewReturn(Pawn)` | List historical abandoned-run people physically at the active saved site, then issue a native threshold approach for a mobile survivor. Downed people/remains use `QueueCasualtyReturn` with an actual carrier. |
| `ExpeditionCargo.QueuePickup(Pawn, Thing, int)` | Public native inventory pickup route for the lead's clicked evidence/item interactions. Requires real same-map item, route, reservation and capacity. |

`ReturnedCrew` contains only living **original** crew who actually entered this run and are now physically at HQ, including a living downed member carried back. Relief members never replace the initial roster or increase that original-three bonus count. Recovered remains can close the physical run but do not count as living returned crew. The lead polls these records for evidence custody and settlement; this component never grants a financial reward or research insight.

## Integration call order

1. `Dispatch` checks `Campaign.CanOperate`, selected employed pawns, one to three distinct crew, actual HQ location, movement/health/mental state, carried-hand conflicts and native mass capacity. The assigned operator cannot be in this list.
2. The exact shared physical kit must be in crew inventories: recorder 1, survey tags 6, return beacon 1, sealed case 1. Native medicines, weapons, apparel and other cargo remain actual optional carried items. The loadout action uses effective ThingDefs/stack counts and native mass, so OgreStack or another stack setting does not create free carrying capacity.
3. `Gate.CanOpen(operator, runId)` checks staffing/power/assembly/calibration. `DestinationService.EnsureSite(campaign, coordinate, out map, out entry)` generates or reuses the existing site. `Campaign.EnsureRouteRecording(coordinate)` must succeed before any crew move. The saved destination parent supplies `ReturnCell`.
4. Three distinct reachable staging cells at most 2.9 cells from the gate entry are selected; the component creates a new stable branch/run ID and orders native reserving/pathing jobs. It rechecks the actual job, physical location, kit and capacity when everyone arrives.
5. Gate `BeginOpening(runId)` succeeds before crossing. The destination's `FirstSliceSiteComponent.BeginOpening(runId, originalCrew)` is called idempotently; relief receives `AddReliefPawn`. Site observation logic remains in that component.
6. Each original Pawn is despawned and respawned at a validated clear destination cell, retaining the native inventory, equipment, apparel and carried-object owners. No alternate Pawn generation, stock recreation, deep-copy transfer or arbitrary inventory sweep occurs.
7. Recall orders a real path to the persisted return cell. At arrival, the controller rechecks the gate ID/window, capacity and a clear HQ landing cell. The same Pawn and its carried inventory cross back. Carried casualties/remains are placed nearby at HQ for ordinary care/storage.
8. Complete physical return closes the gate and reconciles the cargo report. The lead's evidence/case/contract logic checks actual evidence at HQ and records settlement separately.

The component checks active movement/state every ten game ticks and refreshes the live cargo record every sixty ticks. It does not create another clock. Normal and emergency time remaining are read from the gate; the duration choice stays in gate Def tuning, including any owner decision replacing the initial short-window hypothesis.

For the Borrowed Corridor, a matching site's `PendingDistortionCost` is submitted to `Gate.SpendOpeningTicks(runId, ticks, runId + ":borrowed-corridor")`. The site acknowledges that pending cost only after a successful or already-applied gate result. The gate owns the time debit and its idempotency receipt; the expedition controller does not subtract an independent timer or hide a refused debit.

## Timeout, power loss and recovery

The gate exposes `ActiveExpeditionId`, `OpeningTicksRemaining`, `FailureKey`, `EmergencyReturnTicksRemaining` and the spent-reserve receipt. Gate support failure or normal expiry switches the expedition to return and immediately issues route jobs to mobile members. At the first actual threshold crossing, `TrySpendEmergencyReturnReserve(runId)` spends once. Further members may cross only within that same bounded gate-owned emergency window. No permanent reserve authorization or infinite return grace is created.

After expiry, `Stranded` retains the original map, pawns, loose items, case/coordinate links, cargo references and run ID. Closing the gate does not delete a site. Restore the operator/power/reserve and explicitly reopen the saved return route, or send the one approved relief member. Relief readiness counts only real inventory owners located at the saved site or the specified HQ rescuer. Missing kit must be found or physically replaced through the lead's equipment systems; destroyed unique route evidence is never regenerated by this controller.

For relief only, actually spawned tags/beacon with `CompRouteAid.Deployed` and the same saved coordinate ID also count toward the one shared kit. Unrelated loose or unknown cargo never counts. Normal fresh dispatch still requires its full inventory kit. The relief loadout action subtracts these real existing quantities before requesting any replacement pickup.

Recovery openings use `CanRecover` / `BeginRecoveryOpening` rather than recycling initial `BeginOpening`. Each explicit return-reopen or relief attempt receives a saved monotonically numbered `currentRecoveryOperationId`; its staging/retry uses that same ID. Only a newly authorized attempt after real gate readiness/recharge can receive a fresh bounded window. The original expedition/site/crew IDs remain unchanged, and idempotency prevents a repeated begin call resetting its time or reserve spend.

The gate integration supports recovery of either its current expired operation or its **most recently closed** operation. `Strand` may close the gate and retain the run; this must not permanently disqualify that run from powered recovery. Opening a recovery still needs the gate's actual station, full reserve and readiness checks. A completed or abandoned record is not automatically reopened by this controller.

### Explicit abandonment and later recovery

The player can close an unrecoverable operation through a confirmation showing all original crew, relief members, recovery passengers and manifest observations. A nonblank reason is required. Initial unlaunched staging uses Abort staging instead. The preview explicitly includes pending-transfer and deep-held-person counts. Closure retains those original journals and held pawns; it does not conceal or discard them. This allows an explicitly abandoned run with a permanently missing source map to stop blocking company operations while preserving every recoverable object.

Closure appends a saved `ExpeditionClosureRecord`: stable closure ID, reason, tick, pending-transfer and held-person counts, crew reference plus preserved ID/label, known death versus unknown whereabouts, observed map/location, and each cargo entry's Thing ID, observed count/location, known destruction and current declaration. The snapshot remains unchanged as later recoveries update the live manifest. Missing references are labeled unresolved; they are never silently declared dead or destroyed. The record remains in history with `ExpeditionStatus.Abandoned` and no longer occupies `Active`.

Abandonment does not delete the destination, move crew, dispose of corpses, replace evidence, or alter faction/colonist control. Existing native tending, hauling and rescue work continues; only this operation's approach/return jobs are canceled. A new dispatch can use the same saved coordinate through the ordinary gate/kit/path checks. It does not replenish the lost field kit or the unique route recording.

New dispatch/recovery may ignore pending transfer journals **only** when their saved owner run is explicitly Abandoned in the current branch. Journals for an active, unknown or foreign owner and held pawns without a journal still block dispatch. `RecoverInterruptedTransfers` remains available for the abandoned operation and still restores the exact original person only to their recorded source, never to an invented HQ arrival. Resuming that same old operation requires its pending transfers to be resolved first.

Two explicit recovery routes remain:

- If the old operation is still the gate's most recently closed operation, `ResumeAbandonedExpedition` can restore it to Stranded after readiness succeeds. Its prior closure snapshot and one-person relief identity remain intact. The player then uses the normal reopen/relief commands.
- After a newer operation has used that gate, dispatch another crew to the same saved site. `QueueRecoveredCrewReturn` orders a physically present mobile historical survivor to the actual threshold. `QueueCasualtyReturn` can carry a historical downed person or their actual corpse there. Both use the current gate window, capacity and original identity-preserving transfer. They cannot remotely claim people elsewhere.

Historical people are added to `RecoveryPassengers`, separate from the new run's `InitialCrew` and one-person `RescueCrew`. They do not substitute for the original-three bonus or create new pawns. Their actual return can update the old run's living-return record. The background controller refreshes at most one historical record every sixty game ticks; the UI may explicitly refresh its selected record. A newly completed run waits for its explicitly enrolled recovery passengers too; if rescue fails, that operation can again be explicitly closed without deleting them.

Native pickup jobs can be interrupted or another actor can change reservations/stock after preflight. A partially queued load reports that accepted jobs remain; retry checks the actual inventory and only requests missing kit. A staging interruption aborts the initial approach without spending/opening. A path-blocked recall preserves the location and reason; another recall or casualty order remains explicit.

Every cross-map mutation first saves a transfer journal reference with source map/cell. On failure, the controller attempts to respawn the same Pawn on that source map. If it remains unspawned, a component-owned `ThingOwner<Pawn>` deep-saves that original Pawn and its normal child containers for explicit recovery. This exceptional holder is not a working destination and does not run normal field gameplay. Pending transfers block another trip unless the player explicitly abandons their owner operation with those retained people/journals shown in the closure preview. Missing source maps or blocked recovery cells retain the journal/holder rather than deleting a person. The observed runtime behavior of this last-resort path remains an acceptance requirement.

## Saved fields and manifest limits

The component now writes **`rr_expeditionSchema=2`**, deep run records, deep transfer-recovery records and a deep recovery holder. Runs save stable run/branch/coordinate IDs; gate/HQ/destination references; entry/return cells; original, entered, living-returned, relief and historical recovery-passenger Pawn references; relief-staging flag; status/ticks/emergency/failure; cargo records; and deep closure snapshots. Native jobs and their target reservations/queues follow RimWorld's existing save route. An unsupported schema disables actions rather than issuing new trips.

Schema 1 migrates additively at `PostLoadInit`: existing enum numeric values, run IDs, physical references, transfer journals and gate receipt IDs are unchanged. New lists default empty. Legacy cargo declarations lacked checked quantities/provenance, so their original value/note/observation are retained as a history row with unknown report tick (`-1`) and a visible review-required flag. No historical consumption, death, transfer or closure is invented. The migrated schema is then 2. Existing enum values remain stable; new values are `ExpeditionStatus.Abandoned=6`, `CargoLocation.AtSiteInContainer=5`, and `CargoDisposition.Used=4`. The lead owns propagation into the central save policy and owner-launched migration acceptance.

Runs also save the recovery-attempt counter and current recovery operation ID. These are branch/run-local receipt keys, not an alternate gate timer.

Each cargo entry saves the actual Thing reference and original load ID/Def name/label/carrier/count/hit points, observed count/location/damage, and an optional explicit player disposition/note. It additionally saves declared count, review-needed flag, and declaration history containing the report tick and the count/location observed when the report was submitted. Departure captures inventory, equipment and apparel; returning capture also registers newly recovered carried items. It does not infer a physical shipment from account dollars.

Item references do not prove the history of a consumed, destroyed, split or merged stack. The report deliberately retains **unresolved** IDs/count changes instead of inventing a delivery or claiming every missing item was consumed. Player declarations are labeled declarations and change no physical stock. Items seen on the destination floor are listed left at site; items on another map remain elsewhere; damaged surviving objects retain their live reference. This is a traceable physical report, not a global Harmony hook over every item mutation. A complete UI must show unresolved counts and provide the disposition controls; the lead owns that UI wiring.

Declaration rules distinguish observed whereabouts from a player's explanation:

| Report | Current physical check |
| --- | --- |
| Consumed / Lost | Positive quantity cannot exceed `max(0, originalCount - observedCount)`. An intact original quantity cannot be reported missing. A missing reference or reduced/split stack is an unresolved identity/quantity, not automatic proof of consumption. |
| LeftBehind | A real surviving item must currently be on the saved destination, either loose or held there after that run is closed. Equipment carried by the still-operating crew is shown as carried, not automatically abandoned. |
| Used | A real surviving object and an opened run are required; this reports use of reusable equipment without claiming its removal. |
| Unspecified | Clears the current declaration with quantity zero; previous report history remains. |

Nonempty reports require a short explanation. A new report replaces the current classification, rather than summing history as extra loss. Reconciliation flags a report for review if later physical evidence disagrees, such as a declared left-site object arriving at HQ. It preserves the historical report and never hides the known current item. Objects inside another site holder are distinguished from crew inventories. No disposition changes research, financial settlement, stack counts, damage or ownership.

## Pinned Core source evidence and reproduction

Tool: `.local/tools/ilspycmd.exe` / ICSharpCode.Decompiler **9.1.0.7988**. Ignored inspection location `.local/inspection-expedition/`. No proprietary source text or assembly was added to tracked files.

```powershell
$managed = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
$assemblyPath = Join-Path $managed 'Assembly-CSharp.dll'
Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256
& .local/tools/ilspycmd.exe --version
New-Item -ItemType Directory -Force .local/inspection-expedition | Out-Null
$types = @(
  'RimWorld.JobDriver_EnterPortal', 'Verse.AI.JobDriver_TakeInventory',
  'RimWorld.JobDriver_CarryDownedPawn', 'RimWorld.JobDriver_TakeAndEnterPortal',
  'RimWorld.MassUtility', 'Verse.AI.Pawn_JobTracker', 'Verse.Pawn',
  'Verse.GenSpawn', 'Verse.Pawn_InventoryTracker', 'Verse.AI.Toils_General',
  'Verse.AI.Toils_Haul', 'Verse.AI.JobQueue', 'Verse.AI.JobDriver',
  'Verse.IThingHolder', 'Verse.ThingOwner`1'
)
foreach ($type in $types) {
  & .local/tools/ilspycmd.exe -r $managed -t $type $assemblyPath |
    Set-Content -Encoding utf8 ".local/inspection-expedition/$type.cs"
  if ($LASTEXITCODE -ne 0) { throw "Inspection failed: $type" }
}
```

| Source fact | Implementation consequence |
| --- | --- |
| Native `JobDriver_EnterPortal` paths to a portal, uses `DeSpawnOrDeselect` and `GenSpawn.Spawn` on the **same** Pawn, then restores draft/fire behavior. | Direct Core map transition is available; Rimrooms pre-generates the destination and additionally requires saved-run/anchor checks and failure recovery. |
| `Pawn.DeSpawn` calls `jobs.StopAll`, releases reservations and removes map-specific components. Job-tracker cleanup drops a carried object unless the JobDef's `carryThingAfterJob` says to preserve it. Starting a job can separately drop it according to `dropThingBeforeJob`. | Both flags are explicitly set on Rimrooms transit jobs. Native owned inventory/equipment are retained. No teleport is issued before the path job reaches the threshold. |
| `GenSpawn.Spawn(Thing, IntVec3, Map, Rot4, ...)` can log/return without successfully spawning; it can also return an already-spawned object. | The controller checks actual `pawn.Spawned` and target Map after the call, with source rollback and a deep recovery owner. A returned reference alone is not success. |
| `Verse.AI.JobDriver_TakeInventory` reserves count, walks to the item and uses `Toils_Haul.TakeToInventory`; `job.checkEncumbrance` caps actual pickup using native free space. | Preflight plus queued native pickup is used, then dispatch rechecks actual inventory. The initially guessed RimWorld namespace for this type was absent; the inspected working type is `Verse.AI.JobDriver_TakeInventory`. |
| `MassUtility` exposes `GearAndInventoryMass`, `Capacity`, `FreeSpace`, `WillBeOverEncumberedAfterPickingUp`, and `CanEverCarryAnything`. Mass includes equipped/worn gear and inventory counts. | No fixed cargo capacity or stack-count exemption is hard-coded. Loose carried objects are additionally counted; native body-carry behavior is retained for a carried casualty/corpse. |
| `Pawn_JobTracker.TryTakeOrderedJob(Job, JobTag? = Misc, bool requestQueueing = false)` returns success and reserves before queuing. JobQueue is saved as deep queued jobs. | Real player-order jobs are queued and partial refusal is reported; a UI redraw never moves stock. |
| Native casualty/portal carrying paths use `Toils_Haul.StartCarryThing` after approach/reservation. `ThingOwner<T>` supports an explicit holder and deep serialization; `IThingHolder` exposes parent, direct owner and child-holder traversal. | The casualty job carries the original Pawn/corpse. Only interrupted transfers use the exceptional deep holder, with Pawn references linked back into the original run. |

Shared source limits remain those in the [destination source review](PHASE_2_DESTINATION_SOURCE_REVIEW.md): maps persist, a generated Map alone is not proof every GenStep succeeded, and the expedition layer must preserve references to stranded sites. The scenario startup review still governs one-time headquarters grants.

## Remaining integration and runtime acceptance

The lead must compile these files against the pinned Core references, bind Operations controls, reconcile any diagnostics, validate Def/key/package references and save the build evidence. Compilation does not establish transfer atomicity or compatibility. No tests were executed by this assignment.

Owner-launched RimSort acceptance must include: real loadout pickup/interrupt/retry; exactly one physical shared kit under Core and active OgreStack; capacity and reserved-item refusal; withheld operator; blocked staging/landing; abort before entry; same Pawn/Thing IDs across outward/return transfers; path-based recall; ordinary expiry and operator/power loss; one emergency spend within the bounded window; save/reload during staging/on-site/return/stranding; original-coordinate revisit; downed and corpse carrying; one-person relief and repeat use of the same relief member; no original-three bonus substitution; partial transfer/rollback/deep-holder recovery; manifest split/merge/consumption/damage reporting; missing gate/site; recording destruction without replacement; and financial settlement exactly once only through the lead's evidence/contract logic.

The closure follow-up additionally requires: confirmation/cancel and repeat closure; auditable snapshots for unknown/dead/stranded crew and cargo; new dispatch to an abandoned run's unchanged coordinate; no evidence or gear replacement; last-closed-only resume versus later-run physical rescue; historical mobile/downed/corpse return; failed rescue followed by re-closure; schema-1 declaration migration without invented proof; changed physical whereabouts flagged for review; contradictory intact-item and excessive-quantity declarations refused; active/orphaned transfer journals blocking dispatch; and explicitly abandoned journals/held people remaining saved, visible and source-only recoverable while newer operations proceed. Source inspection and edits were performed for this follow-up; no build, tests or game launch were performed by the assigned agent.

Runtime limitations to observe directly include party movement taking part of the opening window, native path/reservation interactions, inventory unloading/consumption by ordinary jobs or optional mods, carried-body cleanup during cross-map jobs, and custody resolution after save/load. The first slice retains maps rather than implementing a map archive or parallel live-player control. No full-profile, save, gameplay or release pass is claimed by the source written here.
