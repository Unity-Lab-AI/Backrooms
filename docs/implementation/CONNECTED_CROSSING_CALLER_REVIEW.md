# Connected-colony crossing service — caller review (resume step 1)

**TODO / feature IDs:** master TODO §Native-provider foundation — "Finish resumable route scheduling, same-pawn/cargo crossing recovery and player-facing connection controls"; RR-GATE, RR-EXP, RR-SPACE. Resume step 1 of [`CONNECTED_COLONY_CHECKPOINT.md`](CONNECTED_COLONY_CHECKPOINT.md): *"Review the crossing service's documented permission, recovery and state boundaries before connecting callers. Finish unresolved constraints rather than weakening checks. Preserve original pawns/cargo and no-wipe landings."*

**Baseline build/commit:** `48a8418` on `feature/connected-colony-portals` (source identical to 0.4.1-dev `8ed4e32`; 75 C# files, 71 package files, zero warnings/errors).

**Owned paths (read in full for this review):** `src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs` (535 lines), `PortalCrossingRecords.cs` (207), `RimroomsPortalNetwork.cs` (234), `PortalConnectionRecord.cs` (85), `PortalRouteSearch.cs` (246), `Gate/PortalGateOpening.cs` (167). No file was modified by this review.

**Affected callers and saved fields:** there are no callers today. Saved fields observed: `rr_portalCrossingSchema`, `rr_portalCrossingNextSequence`, `rr_portalCrossingReceipts`, `rr_portalCrossingHeldThings`; `rr_portalNetworkSchema`, `rr_portalConnections`; `rr_gatePortalConnectionId`, `rr_gatePortalOpeningId`, `rr_gatePortalOpeningSequence`, `rr_gatePortalRecoveryReceipts`. None change in step 1.

**Deliberate changes:** none. **Preserved behaviour:** everything below.

## 1. The documented boundaries, located in source

| Boundary (from `CONNECTED_CROSSING_IMPLEMENTATION.md`) | Where | What it actually does |
|---|---|---|
| Eligibility filter | `ValidateRouteAndPawn`, lines 391–393 | Refuses unless `Spawned && !Dead && !Downed && !Drafted && !InMentalState && Faction == OfPlayer && IsColonist && !IsPrisoner && !IsSlave && !IsQuestLodger()`. Key `RR_PortalCrossing_PawnNotEligible`. |
| Source threshold + door/cell permission | lines 385–390, `CanUseEndpointNow` 430–438 | Anchor must be a spawned `Building_Door` at its saved cell on its saved map; pawn must stand on the saved approach cell; anchor and cell not forbidden to the pawn; `door.CanPhysicallyPass(pawn)` (delegates to `PawnCanOpen`, which Locks-type mods patch). |
| Nonmerging carry transfer | lines 98–111 | Whole carried stack moved into the service's `ThingOwner` with `canMergeWithExistingStacks: false`; count, reference and stack size verified; on mismatch `FailBeforeDespawn` restores and rolls back. |
| Post-despawn graph recheck | lines 113–129 | `pawn.DeSpawn()` (Core clears jobs/reservations across maps), pawn taken into custody, then the live edge is re-found and `Availability` re-run; a closed edge → `NeedsRecovery` + `TryRecoverToSource`. |
| Same-object spawn | `TrySpawnOwnedPawn` 350–356 | `GenSpawn.Spawn(pawn, cell, map, rot, WipeMode.Vanish)` on the held pawn only; result identity checked. Never a Def overload. |
| Post-spawn destination check + rollback | lines 136–140 | `CanUseEndpointNow` on the destination (this is where allowed-area membership is evaluated, because Core stores areas per map); denial → `TryRecoverToSource`. |
| 256 pending bound | line 81 | Counts non-terminal receipts; `RR_PortalCrossing_PendingLimit`. |
| One crossing per pawn | line 83 | `RR_PortalCrossing_PawnInTransit`. |
| Idempotency | lines 73–80, `MatchesRequest` | Same operation id + same pawn/edge/endpoints → returns the recorded outcome; different request → `IdentityConflict`. Receipts are never deleted. |
| Recovery | `Recover` → `ReconcileAndRecover` 181–226 | Only the saved source (`OriginalPawnCell`) or destination approach cell are candidate locations; a pawn found elsewhere on an owned map has its cargo restored and is marked `RecoveredAtActualLocation`; otherwise `PawnLocationUnresolved`. |
| Load validation | `ValidateSavedState` 454–496 | Duplicate ids, bad sequence, unowned non-terminal pawn/cargo, orphaned held things → `stateFaultKey`, which disables both `Cross` and `Recover` while retaining evidence. |
| Reentrancy | `busy` flag | `Cross` and `Recover` refuse while another operation is executing. |

Route search: `PortalRouteSearch` is transient, budgeted (≤ 1024 operations per `Advance`), rechecks captured availability on every completion, and `ValidateStepForTraversal` re-runs `Availability` for the selected edge immediately before a crossing. Topology only; it never claims pawn reachability.

Gate session: `HasUsablePortalWindow(connectionId, openingId)` requires the matching saved ids, no legacy `activeExpeditionId`, not emergency, `openingTicksRemaining > 0`, native provider, station readiness, and at least one tick of energy in the bound battery. `BeginPortalOpening` refuses while a legacy trip or unresolved native trip exists; `ClosePortalOpening` refuses during emergency (no close/reopen cost bypass); `RecoverPortalOpening` debits the physical recovery cost once per operation id.

## 2. Direction and identity checks verified by hand

- `ValidateRouteAndPawn` line 377–382: with `source == First` the destination must be `Second`; with `source == Second` the destination must be `First` (enforced by the endpoint-membership and `source == destination` checks). Correct for both directions.
- `ConnectionMatchesReceipt` compares id, branch, coordinate, kind, opening id, both anchors by reference and load id, both anchor cells and both approach cells. A moved or replaced door invalidates the match; nothing is retargeted.
- `Register` refuses same-map edges, requires the second endpoint to be a generated (`LayoutReady`) destination site owned by the branch, and for `Laboratory` edges requires the first anchor to be a designated native gate whose `GateEntryCell` equals the first approach cell. A natural threshold can never be reassigned to another site; a laboratory door may hold several addresses but only the current opening id activates one.
- `Availability` for `Natural` edges consults no timer, operator, battery or mission; only endpoint presence and standable approach cells. This is the permanent-natural lifetime the owner requires.

## 3. Unresolved constraints and their dispositions

| Constraint | Disposition | Owner |
|---|---|---|
| 32 crossing failure keys (`RR_PortalCrossing_*`, listed below) and the network/gate refusal keys have no `Keyed/` entries | Finish in step 3 together with job/gizmo text in a new `Keyed/RR_Portals.xml` (+ `tools/package-files.json` allowlist), so the first reachable failure already has player text | Step 3 |
| Emergency-return route for a laboratory session that closes with pawns remote | Define in step 3: pawns stay where they are with their real inventory; return only by physically crossing a reopened edge (`RecoverPortalOpening` debits once per operation id) or by the receipt recovery path; never teleport | Step 3 |
| Legacy saved sites (content versions 0–3) use `RR_ReturnAnchor`, which is not a `Building_Door`; `Register` refuses them | Explicit repair route in step 2: a company action that places/binds a real Core door as the site's return threshold, records a receipt, and never rebuilds the visited map | Step 2 |
| No caller creates a `PortalConnectionRecord`; registration needs a generated site first (`LayoutReady`) | Step 2 registration helper: ensure the site through `DestinationService.EnsureSite`, then `Register` | Step 2 |
| Natural-portal discovery leading to a **new** coordinate needs a deterministic coordinate creation API (`CreateDiscoveredCoordinate` proposed in `CONNECTED_PORTAL_STATE_MIGRATION.md`, absent) | Step 2 adds it on the campaign component, additive, replay returns the existing record | Step 2 |
| Drafted pawns are refused by the eligibility filter | Keep. A deliberate cross gizmo (step 3) is shown only for eligible pawns and names the reason otherwise; automatic work never targets drafted pawns anyway | Step 3 |
| Held pawns in a `NeedsRecovery` receipt do not tick while in the service's `ThingOwner` (no needs decay, no healing) | Keep; document as intended: recovery is the only exit and it is explicit. Surface unresolved receipts in the Operations network view so they are never invisible | Step 3 (UI) |
| Receipt history is retained without compaction | Keep for now; add a bounded-archive policy only after receipts are reachable in play | Later (M1 step 6 / debt list) |
| Mechs, subhumans, non-`Building_Door` anchors, optional-provider doors are unsupported | Keep; documented boundary, not a defect | — |
| `ValidDoor` accepts any `Building_Door` with a cardinal-adjacent approach; natural anchors do not save the door's original rotation, so "which side" the approach represents is only the saved approach cell | Keep; the approach cell is the contract. Step 2 registration always records the approach cell from the caller, never derives it from door rotation | Step 2 |

**Result of step 1:** zero source changes required; no check weakened; every open constraint has exactly one owner. Compilation evidence is therefore unchanged from the 0.4.1-dev checkpoint.

## 4. The 32 crossing failure keys that need text

`Busy`, `InvalidState`, `InvalidRequest`, `SequenceExhausted`, `IdentityConflict`, `PendingLimit`, `PawnInTransit`, `DestinationUnsafe`, `CarryOwnerChanged`, `CargoCustodyFailed`, `PawnCustodyFailed`, `PawnCustodyMissing`, `EdgeClosedDuringCleanup`, `DestinationSpawnFailed`, `DestinationAccessDenied`, `ReceiptMissing`, `RecoveryException`, `ReceiptIdentityChanged`, `RecoveredAtChangedLocation`, `PawnLocationUnresolved`, `SourceRecoveryBlocked`, `EndpointMismatch`, `CargoRestoreFailed`, `EdgeUnavailable`, `WrongBranch`, `NotAtSourceThreshold`, `SourceAccessDenied`, `PawnNotEligible`, `InvalidSave`, `UnownedPawn`, `UnownedCargo`, `OrphanedHeldThing` — all prefixed `RR_PortalCrossing_`.

## 5. Remaining regression cases (owner-launched, deferred)

Both directions across a laboratory edge and a natural edge; crossing while carrying a partial stack, a full stack, a unique evidence book; laboratory closed between despawn and spawn; destination approach cell occupied; destination door locked/forbidden; save/reload with a `NeedsRecovery` receipt then `Recover`; 256 pending receipts; the same operation id replayed. None of these can run before the owner launches.

**TODO updates:** `docs/TODO.md` resume step 1 → closed; master TODO gets a bounded checked subitem naming this record; `docs/FINALIZED.md` entry appended when the milestone is cut.
