# Connected-colony travel — addresses, legacy repair, ordinary crossing and the gate traversal rule (0.4.2-dev, 0.4.3-dev)

**TODO / feature IDs:** master TODO §Native-provider foundation — "Finish resumable route scheduling, same-pawn/cargo crossing recovery and player-facing connection controls"; RR-GATE, RR-EXP, RR-SPACE, RR-UI. Resume steps 1–3 of [`CONNECTED_COLONY_CHECKPOINT.md`](CONNECTED_COLONY_CHECKPOINT.md), quoted verbatim in [`../TODO.md`](../TODO.md).

**Baseline build/commit:** `48a8418` (0.4.1-dev source, 75 C# files, 71 package files).

**Checkpoint A — 0.4.2-dev** (addresses, legacy repair, ordinary crossing): **78 C# source files**, **73 approved package files**, zero warnings and errors, SDK 9.0.308, Release/net472. Assembly SHA-256 `986151ED0F1F3F319CED08A960A85B8AC57880F1E31302A334E3DE496A90F6BD`. Evidence: [`evidence/connected-travel-2026-09-28/`](evidence/connected-travel-2026-09-28/).

**Checkpoint B — 0.4.3-dev** (the owner's gate traversal rule): **79 C# source files**, **73 approved package files**, zero warnings and errors, same toolchain. Assembly SHA-256 `EC09DF40D3007CE1...` (full value in the manifest). Evidence: [`evidence/connected-traversal-2026-09-28/`](evidence/connected-traversal-2026-09-28/).

Each folder holds compiler output plus source, package and reference manifests. **No game was launched and no test was run for either checkpoint.**

**Owned paths:** `src/RimroomsAsyncIndustries/Portals/PortalAddressService.cs` (new), `Portals/PortalTravelService.cs` (new, includes `JobDriver_CrossPortal`), `Portals/PortalTraversalPolicy.cs` (new), `Portals/PortalCrossingService.cs` (two additive members plus the policy calls), `Generation/RimroomsDestinationMapParent.cs` (threshold repair), `Company/CampaignServices.cs` + `RimroomsCampaignComponent.cs` (discovered-coordinate API and record bound), `UI/OperationsPortalNetwork.cs` (new pane), `UI/OperationsExpeditions.cs` (one call), `Mod/.../1.6/Defs/JobDefs/RR_PortalJobs.xml` (new), `Mod/.../1.6/Languages/English/Keyed/RR_Portals.xml` (new), `tools/package-files.json` (two entries).

## Step 1 — crossing-service boundary review

Closed with no source change and no weakened check. The located boundaries, the direction/identity proofs and the disposition of every open constraint are in [`CONNECTED_CROSSING_CALLER_REVIEW.md`](CONNECTED_CROSSING_CALLER_REVIEW.md). Two additive members came out of it, both so callers refuse for the same reason the crossing itself would:

- `RimroomsPortalCrossingService.EligibilityFailureKey(Pawn)` — the single eligibility rule, now called by `ValidateRouteAndPawn` instead of being duplicated in the caller.
- `RimroomsPortalCrossingService.HasUnresolvedCrossing(Pawn)` — read-only query over non-terminal receipts.

## Step 2 — address registration, discovery and legacy repair

**`PortalAddressService`** turns a branch-owned coordinate into a saved address. It is the first caller of `RimroomsPortalNetwork.Register` in the project's history.

- `AddressId(campaign, coordinate, threshold)` = `<branchId>:portal:<coordinateId>:<threshold unique load id>`. Derived, never counted, so a replay produces the same id and `Register` answers `Existing`.
- `RegisterLaboratoryAddress(gate, coordinate)` requires a designated native gate with no binding failure and no portal-owner fault, on the headquarters map, with a valid standable `GateEntryCell`. It ensures the site through the existing coordinate owner (`DestinationService.EnsureSite`), so a saved space is recalled and never rebuilt, then registers `Laboratory` with the site's `ReturnAnchor` and `ReturnCell` as the far endpoint.
- `RegisterNaturalAddress(localThreshold, localApproach, coordinate)` registers `Natural`. No gate, timer, operator or battery is consulted for this kind, now or later. The caller supplies the approach cell explicitly; it is never derived from a door's drawn rotation.
- Both refuse with a keyed reason for every failure path; `PortalNetworkResult` is translated one-to-one into `RR_PortalAddress_*`.

**Geometry verified against generation source.** `GenStep_BackroomsDestination` places the site's return anchor as a Core steel `Door` (content version 4) and derives `returnCell` through `FindAdjacentSafeCell`, which returns a standable cell at Manhattan distance 1 from the one-cell anchor footprint. That satisfies `RimroomsPortalNetwork.ValidDoor`'s cardinal-adjacency requirement, so a v4 site's saved return threshold is directly registrable.

**Legacy repair.** Sites at content versions 0–3 use `RR_ReturnAnchor`, which is not a `Building_Door`, so they cannot hold an endpoint. `RimroomsDestinationMapParent` gained:

- `public const int DoorThresholdContentVersion = 4` — the first content version whose threshold is an actual door, kept separate from `RoomContentBuilder.ContentVersion` so a future content bump cannot make v4 sites look broken.
- `NeedsThresholdRepair` — layout ready, content below that version, and the saved anchor is not a door.
- `TryRepairReturnThreshold(replacement, operationId)` — additive, once per site, receipt-guarded (`rr_thresholdRepairReceipt`). It accepts only a spawned one-cell Core `Door` on this map, cardinal-adjacent to the **unchanged** saved `returnCell`. It sets the anchor and the content version and clears a stale generation failure key. It does not touch the room graph, the layout fingerprint, the entry cell, the evidence cell, player construction or discoveries.

`PortalAddressService.RepairLegacyThreshold(coordinate)` preflights everything (branch, coordinate membership, site loaded, legacy anchor present and one-cell, saved return cell still valid/standable/adjacent, Core `Door` def present and one-cell, **no unresolved crossing referencing this map**), then destroys the historical anchor with `DestroyMode.Vanish` and spawns a steel Core `Door` at exactly its cell and rotation in the same action, then records the repair. The operation id is `<coordinateId>:threshold-repair:1`, so a replay is refused as already recorded rather than repeated.

**Discovered coordinates.** `RimroomsCampaignComponent.CreateDiscoveredCoordinate(discoveryId, out coordinate)` is the additive API the state-migration review asked for. The id is `<branchId>:coordinate:discovery:<discoveryId>` and the seed is `CampaignSeed.Derive(campaignSeed, "coordinate:discovery:<discoveryId>", 1)`, so both are deterministic from the branch seed and a caller-stable discovery id; a replay returns the existing record. Growth is bounded by `MaximumCoordinates = 512` and **no visited coordinate is ever removed to make room**. If the added record would fault save integrity the record is withdrawn and the branch is left exactly as it was.

## Step 3 — ordinary crossing jobs, controls and the emergency route

**`PortalTravelService`** owns ordinary travel. There is no crew list, manifest or dispatch on this path.

- `StepFrom(connection, map)` gives the directed step as seen from a map. `Register` forbids same-map edges, so the near side is unambiguous.
- `LocalAddresses(map)` lists remembered addresses whose near side is that map, ordered by coordinate then id.
- `OrderCrossing(pawn, connection)` refuses early with the crossing service's own eligibility key, refuses a pawn already in an unresolved crossing, revalidates the edge through `ValidateRouteStep`, checks the approach cell is standable and reachable at `Danger.Deadly`, then issues `RR_CrossPortal` as a player-ordered job with `targetA` = the near threshold door and `targetB` = the saved approach cell.
- `OrderEmergencyReturn(gate)` is the emergency route home: it requires an actual saved portal session awaiting recovery and calls `RecoverPortalOpening` with operation id `<connectionId>:emergency-return:<portalOpeningId>`. The gate's existing receipt rules debit the physical recovery cost exactly once per operation id, a retry cannot restore duration, and **nobody is teleported** — people who are across walk back through the reopened session.
- `CloseSession(gate)` closes a laboratory session deliberately; the gate already refuses to close during an emergency so close/reopen cannot bypass the recovery debit. People already across stay where they are with everything they carry.
- `RecoverCrossing(operationId)` forwards to the crossing service's `Recover`.

**`JobDriver_CrossPortal`** walks to `targetB` with native pathing, then performs exactly one crossing.

- The connection is resolved at execution time from the near door and the saved approach cell, then filtered to the edges that are currently available. A laboratory door may remember several addresses but only its open session is available, so exactly one candidate survives; **an ambiguous order is refused rather than guessed**.
- The operation id is `<connectionId>:crossing:<pawn unique load id>:<job.loadID>` and is saved on the driver (`rr_portalCrossingOperation`), so a save/reload mid-job keeps the same idempotent identity and cannot double-cross.
- The JobDef mirrors the project's existing transfer jobs: `carryThingAfterJob` true, `dropThingBeforeJob` false, `casualInterruptible` false, `checkOverrideOnDamage` Never — the carried stack travels with its owner.
- Failure keys are surfaced to the player at the point of use through `Messages.Message`. The job ends itself only when it is still the pawn's current job, because a completed crossing despawns and respawns the same person and Core already ends jobs for that.

**Operations pane.** `DrawPortalNetwork` is drawn under the Machine pane and shows remembered addresses with live availability, the coordinate picker, the legacy-repair action with its explanation, laboratory open/close and emergency-return controls, the per-address crossing order for the selected colonist, and the list of unresolved crossings with a reconcile action each. That last list exists so a person held for recovery is never invisible.

The crossing order follows this project's established selection idiom (select the colonist, act in Operations), which is the same route the first-slice route-aid and salvage actions use. A door float-menu or pawn gizmo would be nicer and is recorded in [`../DEFERRED.md`](../DEFERRED.md) under M5; it is a presentation improvement, not a missing capability.

## Gate traversal policy (owner rule, same wave)

The owner's [gate traversal and pacing rule](../CONNECTED_COLONY_PORTALS.md#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side) arrived while this wave was open and its traversal half is implemented here. `Portals/PortalTraversalPolicy.cs` is the single chokepoint every crossing path asks:

- `TravellerFailureKey(Pawn)` — only this company's own colonists walk through, and only when the existing eligibility rule also passes. A non-player pawn is refused with `RR_PortalTraversal_NotOurPerson`.
- `CargoFailureKey(Thing, Pawn carrier)` — anything genuinely in the carrier's hands may ride: materials, tools, equipment, resources, minified furniture and production benches, corpses, and people or monstrosities that are downed, dead or held as prisoners. A pawn still on its own feet is refused with `RR_PortalTraversal_PassengerNotHeld`, because letting it walk through would be traversal. An object not actually carried is refused with `RR_PortalTraversal_CargoNotCarried`.
- `AutonomousNonPlayerTraversalPermitted` is a constant `false` and `MayApproachThresholdForTraversal` returns an unconditional `false`, so a later work adapter, scheduler, generator or threat cannot reintroduce the behaviour by accident. These exist to be read by future code, not configured.

`RimroomsPortalCrossingService.Cross` consults the policy inside `ValidateRouteAndPawn` and again immediately before the carry transfer, so both the planning check and the execution check go through the same rule.

**Scope confirmed with the owner:** gate, gates, machine door and portal all mean one thing; only the connection kind differs (laboratory versus permanently open natural). The rule is per connection and holds for every gate simultaneously, and all three starts — company, solo-or-group inside, and furniture store — can eventually run several gates, so nothing assumes one gate per branch, map or coordinate.

**Verified, not assumed:** nothing in the current source gives a far-side pawn a route, destination or trigger toward a threshold, and RimWorld's own pathing cannot route a pawn between `Map` instances, so no existing behaviour had to be removed. The policy is the standing guard against building one.

**The pacing half is not implemented and is not silently dropped.** The saved, bounded escalation ladder is specified in the contract and carries a concrete spec with a named owner step in [`../DEFERRED.md`](../DEFERRED.md) (resume step 5, before any inhabitant generation ships).

## Saved state added

| Owner | Key | Rule |
|---|---|---|
| `RimroomsDestinationMapParent` | `rr_thresholdRepairReceipt` | Additive; absent on saves that never needed a repair. Once set, a second repair is refused. |
| `JobDriver_CrossPortal` | `rr_portalCrossingOperation` | Additive on the job; keeps one crossing idempotent across save/reload. |

No existing key changed meaning. No schema version was bumped: the portal network, crossing service and campaign schemas are unchanged, and the new campaign API only appends a `CoordinateRecord` of the existing shape.

## Preserved behaviour

Legacy expeditions keep their own gate, receipts and recovery; `rr_gateActiveExpeditionId` is never adopted or converted, and `BeginPortalOpening` still refuses while a legacy or unresolved native trip exists. The physical gate remains the single timer and energy owner for both modes. Visited maps are never rebuilt, rerolled or retargeted. Natural connections still ignore every timer, operator, battery and mission. Ordinary door use still moves nobody.

## Remaining work and regression cases

Open items are tracked in [`../DEFERRED.md`](../DEFERRED.md) with a named owner step: cross-map work intents, quantity leases and the seven adapter families (step 4); natural-portal discovery trigger, optional providers, procedural inhabitants (step 5); receipt compaction and streaming (step 6); the legacy gate/gear/fixture replacements (M2, which shares the migration decision with this repair).

Owner-launched acceptance for this increment, deferred: crossing both directions on a laboratory edge and a natural edge; carrying a partial stack, a full stack and a unique evidence book; the session closing between despawn and spawn; an occupied or forbidden arrival cell; save/reload with an unresolved receipt then reconcile; the 256-pending bound; a replayed operation id; the legacy repair on a visited v0–3 site with and without the Core door def present; open/close/emergency-return with the real battery debit observed once.
