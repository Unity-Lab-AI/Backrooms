# Connected-colony work — intents, planning leases and the first adapter family (0.5.0-dev)

**TODO / feature IDs:** master TODO §Native-provider foundation, resume step 4 of [`CONNECTED_COLONY_CHECKPOINT.md`](CONNECTED_COLONY_CHECKPOINT.md), quoted verbatim in [`../TODO.md`](../TODO.md). RR-GATE, RR-EXP, RR-SPACE, RR-FAC, RR-UI, RR-COMPAT.

**Baseline:** `9430dee` (0.4.3-dev, 79 C# files, 73 package files).

**This checkpoint — 0.5.0-dev:** **87 C# source files**, **76 approved package files**, zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `E5426A967402B70D709536F8C1809C9A2B9158492091768B31984E0003205AAF`. Evidence: [`evidence/connected-work-2026-09-28/`](evidence/connected-work-2026-09-28/) — compiler output plus source, package and recomputed reference manifests. Reference assembly hashes were recomputed rather than copied forward, and show no drift from the previous checkpoint.

**No game was launched, no test was run, and no RimSort mod list was changed.** Nothing below claims a gameplay, balance, performance or compatibility result.

**Owned paths.** New: `ConnectedWork/ConnectedWorkRecords.cs`, `ConnectedWork/ConnectedRouteService.cs`, `ConnectedWork/ConnectedWorkAdapter.cs`, `ConnectedWork/RimroomsConnectedWorkComponent.cs`, `ConnectedWork/WorkGiver_ConnectedWork.cs`, `ConnectedWork/JobDriver_ConnectedHauling.cs`, `ConnectedWork/Adapters/ConnectedHaulingAdapter.cs`, `UI/OperationsConnectedWork.cs`, `Defs/JobDefs/RR_ConnectedWorkJobs.xml`, `Defs/WorkGiverDefs/RR_ConnectedWork.xml`, `Languages/English/Keyed/RR_ConnectedWork.xml`. Modified, additively: `Company/CampaignServices.cs` (one new public accessor), `UI/OperationsPortalNetwork.cs` (one added call), `tools/package-files.json` (three entries), `About/About.xml` and the csproj (version).

---

## What this adds

A colonist can now do work whose object is on the other side of a gate, as ordinary work, with no dispatch, no crew list and no cargo manifest. The first family is **storage hauling, in both directions**: fetch an actual object from the map that holds it, carry it through in real hands under native mass and stack limits, and place it in storage the destination map's own settings accept.

Nothing is counted, cloned, teleported or consumed remotely. The object that arrives is the object that left, or the legitimate split of the stack that a partial pickup produced.

## Why a native WorkGiver and not a scheduler

The whole layer reaches pawns through Core's own `JobGiver_Work`, as two ordinary `WorkGiverDef`s. Verified from the pinned decompile: `JobGiver_Work.TryIssueJobPackage` calls `WorkGiver.NonScanJob(pawn)` for every giver in `pawn.workSettings.WorkGiversInOrderNormal`, in `priorityInType` order, and `PawnCanUseWorkGiver` first checks `nonColonistsCanDo`, `WorkTagIsDisabled`, `WorkTypeIsDisabled`, `ShouldSkip` and `MissingRequiredCapacity`.

Riding that path rather than ticking a component is what preserves the things the contract requires preserved, without a single extra line: per-pawn work priorities, within-type order, schedules, disabled work types, required capacities, and the precedence of the constant and emergency think trees over routine work. Hunger, sleep, danger, drafting and mental states keep winning because they always did. **No job this layer produces is ever marked `playerForced`**, so nothing here can bypass a policy the player set.

## The pieces

### Saved work intent

`ConnectedWorkIntent` is the continuation state for a whole trip. A native job only ever owns one local segment of one. It records the fields the pinned API review required: stable branch/intent ids, adapter id **and version**, the worker and its load id, the original object with its load id and owning map, the requested quantity, the observed object and count after an actual pickup, the destination map and cell, the final work target, the connection id, opening id and graph revision the plan was made against, the phase, the lease expiry and a failure key.

The final-target field is present and unused by hauling. It exists from schema 1 deliberately so the bill, frame and patient families need no migration to record theirs.

**The phase does not encode which segment comes next.** There are only two live phases, `Planned` and `Carrying`, and the next physical segment is derived from the phase plus the worker's *actual current map* every time it is needed. That is what makes a reload mid-route, an interrupted job, or a worker who ended up somewhere unexpected all resolve through one rule instead of a saved step index that can disagree with reality.

### The planning lease

The intent owns its own lease, so the two can never desync. A lease is bounded, expiring, and keyed by the actual `Thing` plus a quantity, exactly as the review specified — and it is **not** a native reservation. It excludes no native pawn, grants no claim, and never travels to another map as a claim. Its only job is to stop two of this company's own planners from promising the same stack. `LeasedCount(thing)` is the whole mechanism.

The lease is held only while the worker is still on its way. Once a quantity is physically in hand, the carry owner holds it and the remaining source stack is free for anyone again.

Native availability is rechecked definitively on arrival. If another pawn took or moved the object in the meantime, the intent closes and a replacement is planned later; nothing is consumed remotely to compensate.

### Two halves of validation, and why they are separate

This is the distinction the review insisted on, and it is enforced by the adapter contract's shape rather than by comment:

* **Candidate half** (`TryPlan`) runs against an explicit `Map`. It may read that map's own listers and storage settings. It uses `map.listerHaulables.ThingsPotentiallyNeedingHauling()`, `map.haulDestinationManager.AllGroupsListInPriorityOrder`, `StorageSettings.Priority`, `StorageSettings.AllowedToAccept`, `StoreUtility.CurrentStoragePriorityOf` and `IntVec3.IsValidStorageFor(cell, map, thing)`. That last one is the single storage predicate Core genuinely parameterises by `Map` — Core's own `JobDriver_HaulToCell` uses it that way — so it answers about the other side instead of quietly answering about the worker's side.
* **Definitive half** (`RevalidateAtFetchSide`, `RevalidateAtStoreSide`, and the job builders) runs only once the worker is physically standing on the map in question. That is where `HaulAIUtility.PawnCanAutomaticallyHaul`, `pawn.CanReserveAndReach`, `StoreUtility.TryFindBestBetterStoreCellFor` and the real native reservation happen, because only there do those calls mean what they say.

No native `HasJobOnThing`/`JobOnThing` is ever called against a remote map. The review recorded that Core's default `HasJob` implementations can invoke their `JobOn` counterparts, so a speculative remote probe can have side effects; the candidate half is therefore written from scratch rather than borrowed.

**Honest limit on allowed areas.** `Pawn_PlayerSettings` exposes no public arbitrary-map area accessor, so this build makes **no claim** of remote allowed-area compliance. The candidate half checks only faction-level forbidding, which is a property of the object. Per-pawn forbidding and allowed areas are checked definitively on arrival, and a refusal there closes the trip with a keyed reason instead of stranding anyone.

### Bounded search, and a real defect found and fixed in review

Routing uses the existing resumable `PortalRouteSearch` through a new `ConnectedRouteService` that retains one cursor per ordered map pair and advances it 96 operations at a time, capped at 32 cursors. The rule the service exists to enforce: **a search that ran out of budget is pending, never "no route."** Only a genuinely exhausted search closes a trip. Cursors are transient, own no game object, and are rebuilt after load.

Every candidate scan is capped too — four connected maps, twenty-four loose objects, twenty-four stored objects, eight storage groups, twenty-four cells per group. The first version of those caps examined a fixed **prefix**, which was a genuine defect against the owner's rule that no code path may assume one gate per branch: with five or six sites open, the fifth and sixth would have been starved forever. Every cap is now a **rotating window** (`RotationOffset`, `WindowStart`), deterministic with no randomness so a reload cannot change what a pass sees, and sized so a pass always spends its whole budget while still reaching every position across successive passes.

### Segments, and how a trip survives a job boundary

```
Planned   + worker not on the fetch map  -> RR_CrossPortal toward the fetch map
Planned   + worker on the fetch map      -> RR_ConnectedFetch   (native reserve, real pickup)
Carrying  + worker not on the store map  -> RR_CrossPortal toward the store map
Carrying  + worker on the store map      -> RR_ConnectedDeliver (Core's own hauling toils)
```

Crossing reuses `RR_CrossPortal` and `RimroomsPortalCrossingService` unchanged, so there is exactly one implementation of stepping through a gate with one set of rules, and the automatic path inherits every check the player-ordered path already had. The one difference is deliberate: a player order may path at `Danger.Deadly`; automatic work uses `pawn.NormalMaxDanger()` and also refuses a forbidden threshold or approach cell.

Delivery uses Core's `Toils_Haul.CarryHauledThingToCell` and `Toils_Haul.PlaceHauledThingInCell`, with `job.haulMode = HaulMode.ToCellStorage` so Core's own fail condition revalidates the cell against the worker's map mid-carry, and with Core's jump-back behaviour intact for a cell that cannot take the whole stack.

**Carry-between-jobs was verified, not assumed.** `Pawn_JobTracker` drops a carried thing on job start when `dropThingBeforeJob` is true, and on job cleanup when `carryThingAfterJob` is false. The fetch job therefore sets `dropThingBeforeJob` true (put down anything unrelated) and `carryThingAfterJob` true (keep what was picked up). The deliver job sets `dropThingBeforeJob` **false** — the whole point of that segment is that the worker arrives holding the cargo — and `carryThingAfterJob` true so a retried placement still has it.

Outcomes are recorded from `JobDriver.AddFinishAction`, a global finish action that Core runs on cleanup regardless of which toil was current, rather than from a final toil that a failure would skip. This is also what makes a merged delivery correct: placing a stack into an existing one destroys the original object, and the finish action reads "no longer in hand" as a completed delivery rather than a lost item.

### Two givers per family, and why

Each family is registered twice, because starting a trip and finishing one need opposite priorities.

| Def | `priorityInType` | Role | Neighbours in Core's `Hauling` |
|---|---|---|---|
| `RR_ConnectedHaulingContinue` | 95 | only finishes a committed trip | below `Strip` (100) and `HaulToPortal` (105), above `HaulCorpses` (90) |
| `RR_ConnectedHauling` | 14 | only starts a new trip | directly below `HaulGeneral` (15) |

Starting sits below its native counterpart so ordinary local hauling is always preferred and a trip through a gate only happens when there is nothing closer to do. Finishing sits high so a worker standing on the far side holding leased cargo does not lose to routine local hauling and abandon the delivery. One giver cannot be both, so there are two. **Both numbers are balance decisions**, recorded as such, and subject to the owner's runtime acceptance.

Independently of priority, an abandoned trip is still safe: the lease expires, the intent closes, and the object stays physically wherever it actually is. Nothing is duplicated and nothing is lost.

### Direction, decided by cost rather than by favour

A planning pass tries to collect **where the worker already stands** before sending it through a gate to collect. A trip that starts here costs one crossing; a trip that starts across costs two. That rule also produces the behaviour the design wants without hard-coding a favoured direction: a worker inside the Backrooms takes what it finds home, and a worker at headquarters only carries goods inward when the player deliberately built better storage there to carry them to.

### Candidate source two, without which "bring it home" would silently not work

Core's `ListerHaulables.ShouldBeHaulable` excludes anything already in its best storage **on its own map**. So a crate sitting in a perfectly good far-side stockpile is invisible to that map's own lister even when the player has built strictly better storage on this side. A hauling adapter built only on `listerHaulables` would therefore appear to work on loose salvage and silently fail on anything stored. The adapter adds a second bounded candidate source that walks the fetch map's own storage groups for exactly that case.

### The gate rule, asked on every path

`PortalTraversalPolicy` is consulted in `WorkGiver_ConnectedWork.NonScanJob` and again in `ConnectedHaulingAdapter.TryPlan`, before any planning, not only at the threshold. A colonist may decide to cross in order to work; nothing else may ever decide anything about a gate. The adapter additionally refuses `Pawn` and `Corpse` as storage cargo outright: carrying someone downed, dead or imprisoned back through a gate is allowed by the policy, but it is rescue, capture or burial work, and those families own their own custody, bed and grave rules.

A worker held inside an unresolved crossing is never handed a job; it belongs to the crossing service until its receipt is reconciled.

### Visibility

`DrawConnectedWork` lists every live trip in the Operations portal pane — who is on it, which object, which way, and which stage. This exists for the same reason the unresolved-crossing list does: saved state that moves the player's people and goods must never be invisible.

---

## Saved state added

| Owner | Key | Rule |
|---|---|---|
| `RimroomsConnectedWorkComponent` | `rr_connectedWorkSchema` | New component, schema 1, always written. |
| Same | `rr_connectedWorkNextSequence` | Monotonic intent id source. |
| Same | `rr_connectedWorkIntents` | Deep list, capped at 64 live and 128 total. |

No existing key changed meaning and no existing schema was bumped. A save from 0.4.3-dev loads with no intents, which is the correct empty state. On load the component validates its own records and, on any inconsistency, sets a fault, logs it, disables the whole layer and leaves the save untouched — the same discipline the campaign and crossing services already use. A live intent must still name its worker, and one worker may never own two; either would make the continuation ambiguous, so either faults.

An intent whose recorded `adapterVersion` is not the current one is cancelled rather than executed under changed rules.

## Preserved behaviour

The portal network, crossing service, crossing receipts, gate timers and energy rules, expedition records and the traversal policy are all unchanged. Legacy expeditions keep their own gate and recovery. Natural connections still ignore every timer, operator, battery and mission. Ordinary door use still moves nobody. The only change to an existing source file beyond one call site is one new public accessor on the campaign component.

---

## Bounded costs

| Cap | Value | What it bounds |
|---|---|---|
| Live intents | 64 | saved growth |
| Total intent rows | 128 | growth between maintenance sweeps |
| Lease duration | 7,500 ticks | how long a stale plan can sit |
| Crossing attempts per intent | 8 | the retry loop guard, not the hop count |
| Planning pass per worker | every 180 ticks | how often the expensive search runs |
| Route operations per advance | 96 | topology work per query per pass |
| Retained route cursors | 32 | transient memory |
| Maintenance | full sweep every 60 ticks | fixed cost, since the live set is capped |

These are source-level bounds. **No performance measurement is claimed**; measurement remains owner-blocked behind a RimSort launch.

---

## Deliberate limits in this checkpoint

- **One family.** Storage hauling only. Construction supply and finishing, bills and unfinished work, research, tend and rescue, food, rest and every remaining family are not implemented and are not claimed. They are tracked with named owner steps in [`../DEFERRED.md`](../DEFERRED.md).
- **Cell storage destinations only.** A delivery resolves to a storage *cell*. A container or provider haul destination is not handled; that is where the Adaptive Storage, LWM Deep Storage, Warehouse and RimFridge cases belong, each needing its own reviewed adapter.
- **No optional provider adapters.** The Core-only path is the only path here. Pick Up And Haul, Haul To Stack and the rest keep their normal single-map behaviour and are untested in combination.
- **People and corpses are out of scope for this family**, by design, as above.
- **No allowed-area claim for a remote map**, as above.
- **Two `OwnsMap` copies remain** private inside `RimroomsPortalNetwork` and `RimroomsPortalCrossingService`. The canonical accessor now lives on the campaign component and new code uses it; converging those two finalized copies is deliberately not done mid-feature and is recorded as a deferment.

## Owner-launched acceptance, deferred

Hauling a loose object from a site to headquarters storage and the reverse; a partial stack pickup where the split object is what travels; a full stack pickup where the original object travels; a delivery that merges into an existing stack; a delivery whose cell fills mid-carry; the storage being deleted while the worker is across; the gate session closing while the worker is across carrying cargo; save and reload at each of the four segments; the worker drafted, downed, or sent into a mental break at each segment; two workers offered the same stack; an object forbidden or outside the allowed area on the far side; a site with more than four connected maps open, confirming the rotating window reaches all of them; the lease expiring with cargo in hand; and the interaction with each optional hauling provider in the 294-row profile, one row at a time.

## Reference material

Read together with the [pinned Core work API](CONNECTED_WORK_CORE_API.md) — including its appendix on Core's own map-portal system — the [profile boundaries](CONNECTED_WORK_PROFILE_BOUNDARIES.md), the [travel record](CONNECTED_TRAVEL_IMPLEMENTATION.md) and the governing [connected colony contract](../CONNECTED_COLONY_PORTALS.md).
