# DECOMPOSED — Decomposed Task List (Highly Broken-Down Tasks)

**Tier 3 of 3 — the DECOMPOSED task list.** The lowest-level execution-grain task list. Every minor task in `docs/TODO.md` decomposes into one or more decomposed tasks here when YOLO mode picks it up (or when Unity decomposes proactively).

A decomposed task is the **smallest meaningful unit of work** — one file edit, one command, one verification step. If a decomposed task takes more than 15 minutes or touches more than one logical unit, it should be broken down further.

Status markers (same scheme as TODO.md / ROADMAP.md):
- `[ ]` pending
- `[~]` in_progress
- `[x]` complete (move to FINALIZED.md immediately, never leave here)

LAW #0 reminder: every decomposed task preserves the source minor task's verbatim text in its parent reference, AND preserves any user-stated specifics in the decomposition itself.

---

## How the three tiers cascade

```
ROADMAP.md (major)         "<major milestone — multi-session / multi-PR goal>"
       ↓ decomposed into
TODO.md (minor)            "<minor task 1 — day-to-day work grain>"
                           "<minor task 2>"
                           "<minor task 3>"
       ↓ decomposed into
DECOMPOSED.md (this file)  "<smallest unit 1 — single file edit / command / verify step>"
                           "<smallest unit 2>"
                           "<smallest unit 3>"
                           "<smallest unit 4>"
```

YOLO mode picks the next decomposed task in cascade order — current minor's pending decomposed → next decomposed → escalate to next minor when current minor's decomposed list is empty → escalate to next major when current minor list is empty.

---

## In progress

_(none — the resume step 1, 2 and 3 slices below all closed in 0.4.2-dev and are archived in `FINALIZED.md`. Step 4 slices are added when it is picked up.)_

---

## Complete — moved to FINALIZED, descriptions retained per LAW

### Parent minor task: Resume step 1 — CLOSED 2026-09-28 (0.4.2-dev) — connected-colony crossing service review

**Parent minor task (from `docs/TODO.md`, verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`):**
> Review the crossing service's documented permission, recovery and state boundaries before connecting callers. Finish unresolved constraints rather than weakening checks. Preserve original pawns/cargo and no-wipe landings.

Decomposed proactively on 2026-09-28 from the crossing record (`implementation/CONNECTED_CROSSING_IMPLEMENTATION.md`) so the next session can start without re-deriving the slice. Each entry is one file read, one review, or one bounded edit.

#### [x] Read the crossing service and its receipt records in full

**Decomposition rationale:** the 800-line read LAW applies before any edit; the service is 535 lines and the records 207, so this is one read pass.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs`, `src/RimroomsAsyncIndustries/Portals/PortalCrossingRecords.cs` (read only)

**Verification step:** the six documented boundaries from the crossing record are located in source by line: eligibility filter (player-faction humanlike colonists; rejects prisoners, slaves, quest lodgers, drafted, downed, dead, mental-state), source door/cell permission, nonmerging carry transfer, post-despawn graph recheck, post-spawn destination door/area check with rollback, 256-unresolved-crossing bound.

#### [x] Enumerate the unresolved constraints the crossing record left open

**Decomposition rationale:** the record names limits that are "still open"; step 1 says finish them rather than weaken checks, so they need a list before any caller is wired.

**Files to touch:** new task record `docs/implementation/CONNECTED_CROSSING_CALLER_REVIEW.md` (written 2026-09-28)

**Verification step:** the record lists at minimum: player-facing localization of API failure keys (`1.6/Languages/English/Keyed/`), the emergency-return route for portal sessions, the legacy saved-endpoint repair route (content versions 0–3 custom return anchor), receipt compaction policy, and mech/subhuman/optional-door support as explicitly out of scope.

#### [x] Decide each open constraint: finish now, defer with reason, or hand to a later resume step

**Decomposition rationale:** localization and emergency return belong to step 3 (crossing jobs + player controls); legacy endpoint repair belongs to step 2 (address registration). Step 1 should close only what callers need to be safe.

**Files to touch:** `docs/implementation/CONNECTED_CROSSING_CALLER_REVIEW.md` (planned), `docs/TODO.md` (status notes alongside, never replacing, the step text)

**Verification step:** every constraint has exactly one disposition and a pointer to the resume step that owns it.

#### [x] Apply any source changes step 1 requires and compile

**Decomposition rationale:** if the review finds a check that must be tightened before callers exist, the fix ships with compiler evidence; if none, this entry is closed as "no source change" and says so.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs` (only if a boundary must be tightened); `./tools/build.ps1 -NoRestore`

**Verification step:** zero warnings/errors against the pinned Core references; compiler output saved under a new `docs/implementation/evidence/` folder only when a milestone checkpoint is being cut. No game launch.

### Parent minor task: Resume step 2 — CLOSED 2026-09-28 (0.4.2-dev) — address registration, discovery and legacy endpoint repair

**Parent minor task (from `docs/TODO.md`, verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`):**
> Add explicit address registration and discovery using the existing campaign coordinate/site owner. Preserve seeds and visited maps; provide an explicit legacy saved-endpoint repair path. No auto-conversion of active legacy missions.

Decomposed 2026-09-28 from the network record, the state-migration review and the destination service. Nothing in the repo calls `RimroomsPortalNetwork.Register` today; this step creates the first caller.

#### [x] Read the network, connection record, destination service and map parent in full

**Decomposition rationale:** four files own the pieces being joined (graph, edge record, coordinate/site owner, world-object anchors); the 800-line read LAW applies before wiring them.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/RimroomsPortalNetwork.cs`, `PortalConnectionRecord.cs`, `Generation/DestinationService.cs`, `Generation/RimroomsDestinationMapParent.cs`, `Gate/PortalGateOpening.cs` (read only); `docs/implementation/CONNECTED_PORTAL_STATE_MIGRATION.md`

**Verification step:** the registration preconditions in `Register(...)` are listed (actual door, branch-owned coordinate/site, distinct loaded maps, fixed approach cell, provider role, identity collision refusal), and the content-version gate in `DestinationService` (v4 Core door vs v0–3 `RR_ReturnAnchor`) is located by line.

#### [x] Write the task record for step 2

**Decomposition rationale:** `REGRESSION_CONTAINMENT.md` requires baseline, owned paths, affected callers/saved fields, deliberate changes, preserved behaviour and remaining runtime cases before a working path changes.

**Files to touch:** `docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md` (written 2026-09-28; steps 2 and 3 share one record because they shipped in one checkpoint)

**Verification step:** the record names `rr_portalConnections`, `rr_gatePortalConnectionId`, `rr_gatePortalOpeningId`, `rr_contentVersion` and the coordinate record fields as the saved surfaces, and states that active legacy expeditions (`rr_gateActiveExpeditionId`) are never converted.

#### [x] Register a laboratory address from an existing coordinate/site

**Decomposition rationale:** the first real edge: when the campaign already owns a coordinate with a generated v4 site, a designated Core door on the HQ map plus the site's Core steel-door threshold become a `Laboratory` connection through `Register`.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/RimroomsPortalNetwork.cs` (registration helper), `Generation/DestinationService.cs` (expose the saved threshold + approach for v4 sites), `Company/CampaignRecords.cs` (only if a coordinate needs a saved connection id; append, never renumber)

**Verification step:** compiles; a repeated registration of the same address returns the existing record (idempotent); a v0–3 site is refused with a diagnosable key instead of being retargeted.

#### [x] Add the explicit legacy saved-endpoint repair route

**Decomposition rationale:** the checkpoint requires a repair path for sites whose return threshold is the historical `RR_ReturnAnchor`; registration accepts actual doors only and must not silently replace the anchor.

**Files to touch:** `src/RimroomsAsyncIndustries/Generation/DestinationService.cs` and `Portals/PortalAddressService.cs`, `1.6/Languages/English/Keyed/RR_Portals.xml`

**Verification step:** the repair is an explicit player/company action with its own receipt; it never rebuilds a visited map; on success the site can be registered; on failure the reason is keyed and the site stays readable under its old version.

#### [x] Register natural (permanent) connections from discovery

**Decomposition rationale:** natural portals have no timer and no close operation; the graph kind exists but nothing creates one. Discovery source for the first slice is a generated site's further doors/frontiers or a scenario opening.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/RimroomsPortalNetwork.cs`, `Generation/GenStep_BackroomsDestination.cs` (frontier records), `Threats/FirstSliceSiteComponent.cs` (only if discovery is observed there)

**Verification step:** a `Natural` edge registers without an opening id, `Availability` never consults gate timers for it, and a physically blocked doorway reports obstruction without removing the edge.

#### [x] Compile and record

**Decomposition rationale:** every resume step closes with compiler evidence and a master TODO bounded tick.

**Files to touch:** `./tools/build.ps1 -NoRestore`; `docs/implementation/CONNECTED_ADDRESS_REGISTRATION_TASK.md`; `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` (add a checked bounded subitem under the connected-colony item); `docs/TODO.md` (flip step 2); `docs/FINALIZED.md`

**Verification step:** zero warnings/errors; the bounded subitem names its evidence; no game launch.

### Parent minor task: Resume step 3 — CLOSED 2026-09-28 (0.4.2-dev) — ordinary crossing jobs, player controls, laboratory wiring, emergency return

**Parent minor task (from `docs/TODO.md`, verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`):**
> Implement ordinary local threshold approach/crossing jobs and player controls without crew/manifests. Wire laboratory open/close/recovery and permanent natural links. Define the remaining emergency-return route without duplicate debits or teleporting stranded workers home.

Decomposed 2026-09-28. This is the step that makes the substrate reachable in play: the first `JobDriver` that walks a pawn to a registered threshold and calls `PortalCrossingService.Cross`, plus gizmos that call `BeginPortalOpening` / `ClosePortalOpening` / `RecoverPortalOpening`.

#### [x] Read the existing approach/return job drivers and the gate job/work-giver pair

**Decomposition rationale:** the new crossing job must reuse the native pathing pattern already proven in `JobDriver_ExpeditionApproach` and the gate jobs rather than invent a second one.

**Files to touch:** `src/RimroomsAsyncIndustries/Expedition/JobDriver_ExpeditionApproach.cs`, `Gate/JobDriver_RimroomsGate.cs`, `Gate/WorkGiver_RimroomsGate.cs`, `Portals/PortalCrossingService.cs` (read only)

**Verification step:** the toil sequence the crossing job needs is written down: goto saved approach cell → recheck `ValidateStepForTraversal` → `Cross(pawn, step, operationId)` → end job on the destination map.

#### [x] Add `JobDef` + `JobDriver_CrossPortal` + keyed text

**Decomposition rationale:** one job, one Def, one keyed file; failure keys from the crossing service become player text here.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/PortalTravelService.cs` (holds `JobDriver_CrossPortal`), `Mod/Rimrooms - Async Industries/1.6/Defs/JobDefs/RR_PortalJobs.xml`, `1.6/Languages/English/Keyed/RR_Portals.xml`, `tools/package-files.json` (add the two XML files to the allowlist)

**Verification step:** compiles; package validation accepts the new files; every `FailureKey` string the crossing service can return has a keyed entry.

#### [x] Add player controls: deliberate cross gizmo on a registered threshold, open/close/recover gizmos on the gate

**Decomposition rationale:** the scenario/portal contract requires deliberate enter/return/recall/dial/close/emergency routes and forbids accidental teleport on ordinary door use.

**Files to touch:** `src/RimroomsAsyncIndustries/Gate/PortalGateOpening.cs` (gizmo surface), `Gate/CompRimroomsGate.cs` (`CompGetGizmosExtra` only), `UI/OperationsGateBinding.cs` (network view)

**Verification step:** compiles; opening a designated door normally never crosses; the gizmo calls the portal-session path (`BeginPortalOpening`) and never the legacy `BeginOpening`; refusal reasons surface through `CompanyActionResult`.

#### [x] Wire laboratory session lifecycle and permanent natural links into the job

**Decomposition rationale:** a laboratory edge is crossable only while `HasUsablePortalWindow(connectionId, openingId)`; a natural edge always is unless physically obstructed. The job must observe both.

**Files to touch:** `src/RimroomsAsyncIndustries/Portals/JobDriver_CrossPortal.cs`, `Portals/RimroomsPortalNetwork.cs` (`Availability`)

**Verification step:** closing a laboratory opening ends or suspends the job without moving anyone; a pawn already across stays there with its inventory; reopening the same address reconnects.

#### [x] Define the emergency-return route for portal sessions

**Decomposition rationale:** `RecoverPortalOpening` exists but the route home for stranded workers is undefined; the contract forbids teleporting everyone home and forbids double debits.

**Files to touch:** `src/RimroomsAsyncIndustries/Gate/PortalGateOpening.cs`, `Portals/PortalCrossingService.cs` (`Recover` path only), `docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md` (written 2026-09-28)

**Verification step:** an emergency session debits the physical battery once through the existing receipt rules; a retry cannot restore duration; workers return only by physically crossing a reopened edge or via the saved receipt recovery.

#### [x] Compile, record, tick, publish at milestone

**Decomposition rationale:** step 3 is the first player-visible portal milestone and is worth a checkpoint + cascade.

**Files to touch:** `./tools/build.ps1`; `docs/implementation/evidence/connected-travel-2026-09-28/`; `docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md`; `About.xml` + `CHANGELOG.md` version bump (0.4.2-dev); master TODO bounded ticks; `docs/TODO.md`, `docs/FINALIZED.md`; then `docs/PUBLISHING.md` procedure on both remotes

**Verification step:** zero warnings/errors; manifests saved; all eight remote refs read back at the new commit; no game launch.

---

### Parent minor task: Resume step 4 (wave 1) — CLOSED 2026-09-28 (0.5.0-dev) — work intents, planning leases and the storage-hauling family

> "Implement saved work intents, quantity leases and native destination job revalidation; then physical hauling, construction, bills, research, medical/food/bed and other work/needs families. Preserve priorities, schedules, areas, locks, custody and actual inventory. A generic graph does not implement these adapters."

**Decomposition rationale:** the step covers every work family. The engine plus exactly one family is the smallest increment that proves the design actually works end to end, and the remaining families are then additive against a settled contract rather than speculative.

- [x] **Slice 1 — close the reference gap before writing anything.** Inspect Core 1.6's own map-portal system and every API the adapters would stand on, against the pinned assembly hash. Files: `.local/inspection-connected-work/*` (evidence only). Verification: each signature read from the decompile, not memory; findings written up as an appendix to `implementation/CONNECTED_WORK_CORE_API.md`.
- [x] **Slice 2 — the saved intent.** Files: `ConnectedWork/ConnectedWorkRecords.cs`. Verification: every field the pinned review demanded is present, including adapter version and the unused final-target reference later families need.
- [x] **Slice 3 — bounded routing for automatic callers.** Files: `ConnectedWork/ConnectedRouteService.cs`. Verification: a budget-limited or invalidated status returns pending, never unreachable; cursors are transient and cleared on load.
- [x] **Slice 4 — the adapter contract.** Files: `ConnectedWork/ConnectedWorkAdapter.cs`. Verification: the candidate half and the definitive half are separate abstract members, so a future family cannot accidentally merge them.
- [x] **Slice 5 — the component, leases and maintenance.** Files: `ConnectedWork/RimroomsConnectedWorkComponent.cs`, plus one new public `OwnsMap` accessor on `Company/CampaignServices.cs`. Verification: withdraw-on-fault on open; one live intent per worker enforced in the save validator; full sweep bounded by the live cap.
- [x] **Slice 6 — the storage-hauling family.** Files: `ConnectedWork/Adapters/ConnectedHaulingAdapter.cs`. Verification: two candidate sources so stored objects are not silently invisible; rotating windows so no map or stockpile is starved; `Pawn` and `Corpse` refused by design.
- [x] **Slice 7 — work givers and segment drivers.** Files: `ConnectedWork/WorkGiver_ConnectedWork.cs`, `ConnectedWork/JobDriver_ConnectedHauling.cs`, `Defs/JobDefs/RR_ConnectedWorkJobs.xml`, `Defs/WorkGiverDefs/RR_ConnectedWork.xml`. Verification: plan/continue pair per family; carry-between-jobs flags set from the verified `Pawn_JobTracker` rules; outcomes recorded from a global finish action so a failure cannot skip them.
- [x] **Slice 8 — make it visible.** Files: `UI/OperationsConnectedWork.cs`, one added call in `UI/OperationsPortalNetwork.cs`, `Languages/English/Keyed/RR_ConnectedWork.xml`. Verification: every live trip is listed; all 31 referenced keys resolve.
- [x] **Slice 9 — checkpoint.** Files: `About.xml`, csproj, `tools/package-files.json`, `CHANGELOG.md`, the implementation record, the evidence folder, and the workflow ledger. Verification: clean build, XML parse sweep, key-coverage sweep, manifests recomputed.

### Parent minor task: Deferment audit — CLOSED 2026-09-28 (0.5.1-dev) — nine rows closed, natural gates findable

> lets get to work.. and try not to deffer anything you may need to properly bbuild other coded systems so that you can do the deffered items(I DONT WANT YOU JUST DEFFERING SHIT THAT WE NEED WORKING !!! WE CANT NOT BUILD SHIT THAT THE MOD DEPENDS ON AND JUST MARK IT DEFFERED BECAUSE SOMETHING WELSE NEEDS DONE FIRST!!! DO THE FIRST THING TO UNDEFER SHIT! I DONT WANT TO GET COMPLETED WITH THIS MOD AND HAVE 1000s of defferments, we need to critical solve these issues wirthin the confines of the mods and the game

**Decomposition rationale:** audit before building, because the register turned out to contain rows that had already shipped and rows blocked on nothing — and building the next feature on top of that would have inherited both.

- [x] **Slice 1 — audit the register and the source.** Ask of every row: is it still open, is it blocked on anything, does anything depend on it; and of the source: which public APIs have no callers. Verification: three rows verified as already-shipped against source; `CreateDiscoveredCoordinate` confirmed at zero callers.
- [x] **Slice 2 — one `OwnsMap`.** Files: `Portals/RimroomsPortalNetwork.cs`, `Portals/PortalCrossingService.cs`. Verification: both delegate to the campaign accessor, which is the strictest of the three.
- [x] **Slice 3 — bound the finished-receipt archive.** Files: `Portals/PortalCrossingService.cs`. Verification: unresolved receipts provably untouched; replay protection reasoned from how operation ids are derived.
- [x] **Slice 4 — container delivery destinations.** Files: `ConnectedWork/Adapters/ConnectedHaulingAdapter.cs`, `ConnectedWork/JobDriver_ConnectedHauling.cs`, `ConnectedWork/ConnectedWorkRecords.cs`, `Defs/JobDefs/RR_ConnectedWorkJobs.xml`. Verification: branch mirrors Core's `HaulToStorageJob` exactly; Core's own container toils used.
- [x] **Slice 5 — observed remote allowed areas.** Files: `ConnectedWork/ConnectedWorkRecords.cs`, `ConnectedWork/RimroomsConnectedWorkComponent.cs`, `ConnectedWork/Adapters/ConnectedHaulingAdapter.cs`, `ConnectedWork/WorkGiver_ConnectedWork.cs`. Verification: public API only; unobserved reads as unrestricted, matching Core's own default; arrival check still definitive.
- [x] **Slice 6 — natural-gate discovery.** Files: `Portals/NaturalFrontierService.cs` (new), `Portals/PortalAddressService.cs`, `UI/OperationsPortalNetwork.cs`, `Defs/JobDefs/RR_PortalJobs.xml`, `Defs/WorkGiverDefs/RR_InvestigationWork.xml`, `Languages/English/Keyed/RR_Portals.xml`. Verification: `CreateDiscoveredCoordinate` now has a caller; the draw is deterministic per doorway position under the coordinate seed; capped per coordinate; `Sight` and `Moving` confirmed as real capacity defNames before shipping the def.
- [x] **Slice 7 — the four missing keyed strings.** Files: `RR_Company.xml`, `RR_Procurement.xml`, `RR_Generation.xml`. Verification: sweep of every `RR_` identifier in source re-run; only concatenation prefixes remain, each family spot-checked.
- [x] **Slice 8 — checkpoint.** Files: `About.xml`, csproj, `CHANGELOG.md`, the audit record, the evidence folder, and the workflow ledger including the four audit questions now in `DEFERRED.md`'s header.

### Parent minor task: Casualties and remains — CLOSED 2026-09-28 (0.5.2-dev) — our own people and our dead come home

> okay lets get to it, whats logically next and/or needs finished already built or onto the next

**Decomposition rationale:** the owner's gate rule names people and monstrosities among what comes back through an opening, and no route reached it. A gap in a stated requirement is built before the next addition, so this went ahead of construction supply.

- [x] **Slice 1 — read Core's rescue path before writing.** Verification: `WorkGiver_RescueDowned`, `HealthAIUtility.CanRescueNow` (confirmed to have no bed requirement), `WorkGiver_TakeToBed.FindBed`, `JobDriver_TakeToBed` (confirmed it already jumps past goto and pickup when already carrying), `Toils_Bed`, `Building_Bed`, `WorkGiver_HaulCorpses`, and Core's `DoctorRescue` priority — all against the pinned assembly.
- [x] **Slice 2 — share the scan rules.** Files: `ConnectedWork/ConnectedWorkScan.cs` (new), `Adapters/ConnectedHaulingAdapter.cs`. Verification: the hauling adapter's private copies removed, not left alongside.
- [x] **Slice 3 — remains as ordinary hauling.** Files: `Adapters/ConnectedHaulingAdapter.cs`. Verification: `Corpse` exclusion removed with Core's feeding-animal guard added; category check relaxed for corpses only.
- [x] **Slice 4 — the cell-only candidate defect.** Files: `Adapters/ConnectedHaulingAdapter.cs`. Verification: a grave is reachable as a candidate destination, so the container delivery route is no longer unreachable for the case it was built for.
- [x] **Slice 5 — the casualty adapter.** Files: `Adapters/ConnectedCasualtyAdapter.cs` (new), `ConnectedWorkAdapter.cs` (registry). Verification: one direction only; destination is the map the worker stands on and only if it has a candidate bed; capture deliberately absent.
- [x] **Slice 6 — the bed handoff driver.** Files: `JobDriver_ConnectedCasualty.cs` (new), `Defs/JobDefs/RR_ConnectedWorkJobs.xml`. Verification: Core's own bed toils and reservation pattern; `carryThingAfterJob` false so a failed placement hands off to native rescue instead of stranding a carried person.
- [x] **Slice 7 — work givers and the shared fetch.** Files: `WorkGiver_ConnectedWork.cs`, `JobDriver_ConnectedHauling.cs`, `Defs/WorkGiverDefs/RR_ConnectedWork.xml`, `Languages/English/Keyed/RR_ConnectedWork.xml`. Verification: plan below and continue above Core's `DoctorRescue`; a person reserved whole rather than by quantity.
- [x] **Slice 8 — checkpoint.** Files: `About.xml`, csproj, `CHANGELOG.md`, the casualties record, the evidence folder, and the workflow ledger.

### Parent minor task: Construction supply and the dependency audit — CLOSED 2026-09-28 (0.5.3-dev)

> get to it we are doing great! make sure mods needed specifically for our mod as dependacies are properly handled with our single mod Rimrooms properly using them as needed to impliment all features of the mod properly

**Decomposition rationale:** the dependency audit ran first because if a feature genuinely needed another mod it would have changed what got built. It did not — and the audit instead dissolved a content blocker and found a factually wrong row.

- [x] **Slice 1 — audit what the mod actually requires.** Verification: twelve non-Rimrooms defs each traced to base Core in the game's own `Data` folders; both patch files confirmed guarded by parsing Core defs; stack-mod and modded-door compatibility confirmed from what the code does.
- [x] **Slice 2 — fix the throwing def lookups.** Files: `Expedition/RimroomsExpeditionComponent.cs`, `Gate/WorkGiver_RimroomsGate.cs`, `Threats/FirstSliceSiteComponent.cs`, `Languages/English/Keyed/RR_Expedition.xml`. Verification: zero `GetNamed` calls remain.
- [x] **Slice 3 — read Core's construction path before writing.** Verification: `IConstructible`, `IHaulEnroute`, `Frame`'s declaration and `resourceContainer`, `Toils_Construct`, `Toils_Goto.MoveOffTargetBlueprint`, `JobDriver_HaulToContainer`'s already-carrying jump, and Core's delivery giver priorities — all against the pinned assembly.
- [x] **Slice 4 — the construction adapter.** Files: `Adapters/ConnectedConstructionAdapter.cs` (new), `ConnectedWorkAdapter.cs`. Verification: quantity clamped by stack, carry capacity and the site's remaining need; site revalidated on the fetch side as well as on arrival.
- [x] **Slice 5 — the delivery driver.** Files: `JobDriver_ConnectedConstruction.cs` (new), `Defs/JobDefs/RR_ConnectedWorkJobs.xml`. Verification: blueprints included via Core's own conversion toil rather than excluded.
- [x] **Slice 6 — work givers.** Files: `WorkGiver_ConnectedWork.cs`, `Defs/WorkGiverDefs/RR_ConnectedWork.xml`. Verification: continue above and plan below Core's own delivery givers, with `prioritizeSustains` matching them.
- [x] **Slice 7 — record the capability-matching method and correct the register.** Files: `implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md` (new), `DEFERRED.md`. Verification: Core generator outputs extracted from `Buildings_Power.xml`; each M2 legacy object given a capability-based Core answer.
- [x] **Slice 8 — checkpoint.** Files: `About.xml`, csproj, `CHANGELOG.md`, the construction record, the evidence folder, and the workflow ledger.

### Parent minor task: Owner decisions round — CLOSED 2026-09-28 (0.5.4-dev) — duration ladder, scenario parity, company naming

> sound good, track the goal of completing todo work and anything else needed to make this mod work as layed out and use ask me questions with muliple choice suggestions and wwrite in options where you need guidance or blocked or holes needed filled or any guildance needed.

**Decomposition rationale:** the open forks were asked before building, because the duration answer determined whether the three work families already shipped were usable at all.

- [x] **Slice 1 — ask, with options and trade-offs.** Four questions: gate duration, validation timing, next build, inside start. All answered, including two rows owner-blocked since Gate 0.
- [x] **Slice 2 — verify the natural-gate exemption before touching any timer.** Verification: the window is consulted only for laboratory edges; a natural connection has no machine, operator or energy draw. No change needed.
- [x] **Slice 3 — pick a tier driver that cannot go backwards.** Verification: `researchInsights` is decremented on commit, so it was rejected in favour of completed projects.
- [x] **Slice 4 — the ladder.** Files: `Gate/CompRimroomsGate.cs` (props, config errors, tick, readout), `Gate/PortalGateOpening.cs` (tier, indefinite, ticks-for-tier, both session starts). Verification: legacy window untouched; sustained sessions still spend energy every tick.
- [x] **Slice 5 — company naming, end to end.** Files: `Scenario/RimroomsStartDef.cs`, `Scenario/RimroomsStartupComponent.cs`, `Scenario/Page_RimroomsCompanySetup.cs`, `Scenario/ScenPart_RimroomsStart.cs`, `Company/CompanyActionResult.cs`, `Company/RimroomsCampaignComponent.cs`, `Company/CampaignServices.cs`, `UI/Dialog_RenameCompany.cs` (new), `UI/MainTabWindow_Operations.cs`, `Defs/RimroomsStartDefs/RR_Starts.xml`. Verification: renames through Core's own dialog; blank and over-long names refused; additive save keys only.
- [x] **Slice 6 — record the decisions where decisions live.** Files: `GATE_0_DECISIONS.md`, `SCENARIO_SETUP_AND_PORTAL_NETWORK.md`, `CONNECTED_COLONY_PORTALS.md`, `DEFERRED.md`. Verification: three owner-blocked rows resolved; the unreachable top of the ladder recorded as a content gap with a named owner rather than left implied.
- [x] **Slice 7 — checkpoint.** Files: `About.xml`, csproj, `CHANGELOG.md`, the record, the evidence folder, the ledger.

## TOMBSTONES

_(none)_

---

## Decomposition rules

When a minor task arrives at the top of the YOLO queue:

1. **Read the minor task's verbatim text** from `docs/TODO.md`
2. **Read every file the minor task references** (full file, 800-line chunks per the LAW)
3. **Identify the smallest meaningful units of work** — each becomes a decomposed task
4. **Append decomposed entries here** with this header format:

```markdown
### [ ] <decomposed task title>

**Parent minor task (from `docs/TODO.md`, verbatim):**
> <verbatim minor task text>

**Decomposition rationale:** <one-sentence why this is the right slice>

**Files to touch:** `<path1>` `<path2>` ...

**Verification step:** <how to confirm this slice landed correctly>
```

5. **Flip status** to `[~]` when YOLO picks the task up
6. **Move to FINALIZED.md** when complete (per `§FINALIZED BEFORE DELETE` LAW)

## When NOT to decompose

- **Trivial one-line edits** — a typo fix doesn't need a DECOMPOSED entry; flip the minor task status and ship it
- **Pure-doc updates** that follow a clear template — bundle as a single decomposed task
- **Refactors with no behavior change** that touch <3 files — single decomposed task is fine
- **Tombstoning** — moving an obsolete task doesn't need decomposition

The decomposition tier exists to make multi-step work tractable in YOLO mode, NOT to bureaucratize every edit. Use judgment.
