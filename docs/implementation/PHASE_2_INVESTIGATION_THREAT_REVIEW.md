# Phase 2: investigation and threat source review

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Date:** 2026-09-28. **Evidence:** bounded read-only source comparison, not runtime acceptance. The lead was changing the reviewed files concurrently; the locations below identify the reviewed methods and initial line positions. Fix status is stated explicitly. This reviewer changed only this report and ignored local inspection output. No game, build, tests, profile changes, or third-party source distribution occurred.

## Task and authority

- Parent task: [Phase 2 vertical slice](PHASE_2_VERTICAL_SLICE_TASK.md); features **RR-EVD, RR-THREAT, RR-EXP, RR-UI, RR-COMPAT**.
- Inputs: [first playable](../FIRST_PLAYABLE_CONTRACT.md), [first-slice inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [threat sheets](../THREAT_DESIGN_SHEETS.md), [state ownership](../CAMPAIGN_STATE_DICTIONARY.md), [action contracts](../OPERATIONS_ACTION_CONTRACTS.md).
- Reviewed scope: `src/RimroomsAsyncIndustries/Investigation/`, `Threats/`, and Company `InvestigationServices.cs` / `EvidenceSettlement.cs`; related Defs and expedition/generation interfaces were read only to establish call context.
- Source pin: profile **row 4**, package **`Ludeon.RimWorld`**, installed `Assembly-CSharp.dll` SHA-256 **`5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`**. Inspector: **ILSpy command line 9.1.0.7988**. Core-only scope; no optional mod behavior is certified.
- Saved owners: site `MapComponent` owns encounter/observations and physical marker references; the branch owns case, analysis, project and contract receipts; native item/pawn holders own actual custody. The lead clarified that the encounter opening ID is the expedition run ID: recovery openings retain the same encounter rather than resetting it.

## Concrete findings sent to the lead

### 1. Closed-door counterplay was checked after same-room damage

**Priority: medium.** [FirstSlicePursuer.cs](../../src/RimroomsAsyncIndustries/Threats/FirstSlicePursuer.cs), `AdvancePursuer`, initially lines 50–69 and 86–88.

The contact branch used the authored `RoomRecord` bounds and returned before the native `NoPassClosedDoors` reachability check. A wall or closed door built inside one authored room could therefore separate pawn and pursuer while the contact timer still inflicted damage. Authored procedural room bounds are not proof of current native path connectivity.

**Required correction:** evaluate the physical closed-door path before the contact branch, and retain that requirement when applying the bounded strike. The lead has now moved a native path guard before contact in the source; this was re-read, but not exercised in game.

### 2. A replacement target inherited another pawn's contact warning

**Priority: medium.** Same method, initially lines 50–65; site fields/`ExposeData` in [FirstSliceSiteComponent.cs](../../src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs).

Only a shared `contactWarningTick` was saved. When the initially warned pawn left that room and another crew member became the closest target in the same room, the second pawn could receive the strike immediately using the first pawn's elapsed warning. This did not provide that target the promised further one-minute warning.

**Required correction:** save the warned pawn reference; reset the timer on target change, withdrawal, room separation or blocked path. The lead added a target comparison/reference while this review was running. Runtime warning continuity remains unverified.

### 3. A split team could fail to trigger the required distortion

**Priority: medium.** `FirstSliceSiteComponent.MapComponentTick`, initially lines 112–128.

The method chose `present.FirstOrDefault(p => !p.Downed)` and tested only that pawn's room. If that first crew member remained at the threshold while a different crew member traversed Borrowed Corridor, no distortion activated. Survey flags could still accumulate for the other members, leaving a required observation blocked by list order rather than actual traversal.

**Required correction:** observe actual eligible crossing pawns and their saved previous rooms; associate the warning/junction with the triggering pawn. The lead accepted this correction and is implementing it. The same inspection identified leader-driven movement timing in `AdvancePursuer`; keep its observed-room state tied to the actual tracked crew/target when implementing split-team counterplay.

### 4. Deploying a marker could move or destroy unrelated physical stock

**Priority: medium.** `FirstSliceSiteComponent.DeployAid`, initially lines 195–218.

The method removed one real item from inventory and called `GenSpawn.Spawn(unit, pawn.Position, map)` without checking the existing item occupancy. Native `GenSpawn` makes room when an item cell is full: it despawns an existing item, tries nearby placement, and destroys that existing item if placement fails. Even successful displacement can clear a deployed marker's identity through `CompRouteAid.PostDeSpawn`. A route command must not unexpectedly relocate another marker or destroy physical cargo.

**Required correction:** before taking the unit, choose/recheck an unoccupied safe target cell; reserve it through the real job; refuse if its occupancy changes. After spawning, verify the actual unit is spawned on that map before recording deployment. Failed placement must restore the exact unit to its original inventory or a saved recovery holder; do not discard the return value of a fallback placement operation. The lead was informed; changes were in progress at report creation.

### 5. A refused deployment order was reported as successful

**Priority: low.** `FirstSliceSiteComponent.QueueDeployAid`, initially lines 191–193.

The method ignored the `bool` from `pawn.jobs.TryTakeOrderedJob` and returned `Applied` unconditionally. Native job assignment can refuse, including reservation failure. This creates a false action result and no useful next step.

**Required correction:** return refusal when native ordered-job assignment rejects the job. This is a distinct command-result issue from physical placement after a job starts.

### 6. Reopening could overwrite completed analysis with a missing-item status

**Priority: low.** [InvestigationServices.cs](../../src/RimroomsAsyncIndustries/Company/InvestigationServices.cs), `EnsureRouteRecording`, initially line 27.

The existing-record branch assigned `Missing` whenever its physical item was null/destroyed, even after `analyzedTick` recorded completed analysis. Reopening after a later loss could therefore replace the displayed completed state and allow the site's `status != Analyzed` observation branch to modify the already-analyzed record. The new receipt guard prevents another insight award, but the historical analysis state should remain intact.

**Required correction:** restrict the missing-status assignment to `analyzedTick < 0`, consistent with `EvidenceSettlement`; preserve the completed receipt and record later custody loss separately. The lead was informed.

## Previously known issues and reviewed fixes

The following were supplied by the lead as already known, not discovered by this review:

- `CanAnalyze` now requires both route and distortion observations before analysis work can award the insight.
- `CanAnalyze` now checks `analyzedTick < 0`; completion writes the tick and analyzed status before incrementing the insight and attempting settlement.
- `EvidenceSettlement` now continues settling an analyzed record after its physical item has become missing. It retains the saved expedition source and can award a later earned original-three-person return bonus.

These source guards were present in the reviewed live code. Base payment and bonus use separate stable transaction IDs; no new duplicate-payment path was identified within this bounded review. This is not a save/load or multiplayer result.

## Physical distortion tell: safe implementation route

The original alert described a repeated label and conflicting tag without a corresponding physical change. The lead is replacing that text-only tell with the following original implementation:

1. Require an actual deployed, numbered tag at the crew's validated junction before awarding full mismatch evidence. With no tag, provide an honest route-oddity hint and allow tagging/revisiting; do not invent a physical tag.
2. Store the real tag reference and its recorded junction/number. Choose a revealed, in-bounds, standable, empty cell across the relevant connection, excluding the return anchor/entry and preserving the accessible return path.
3. Relocate **that same spawned Thing on the same map** through its public `Position` setter, after checking `!tag.def.AffectsRegions`. Do not clone it, split it, renumber it, or call `DeSpawn` for the visual mismatch.
4. Retain the original `CompRouteAid.RoomIndex` and number while the physical position disagrees. Save the tell receipt/reference so loading or a same-run recovery does not move it again.
5. `CompRouteAid.DrawGUIOverlay()` can call `GenMapUI.DrawThingLabel(parent, text)` with the repeated/recorded room label and marker number. Its inspect text can show recorded room versus actual `RoomAt(parent.Position)`. Guard current map, spawned state and fog visibility; the overlay must not disclose unexplored rooms.
6. Counterplay must compare **actual marker position** with the recorded junction. Merely finding a tag whose saved `RoomIndex` matches is insufficient after it has been displaced. A deliberate physical recovery/redeployment path may revalidate it; no replacement grant is necessary.

**Pinned Core facts supporting this route:** `Thing.Position` updates thing/cover/region registration and dirties the map mesh for a same-map move, without running `DeSpawn`; it warns against moving region-affecting things this way. `ThingWithComps.DrawGUIOverlay` invokes each comp's `DrawGUIOverlay`, and `ThingComp` provides that virtual method. `GenMapUI.DrawThingLabel(Thing, string)` is a public native label helper. The existing route-aid `PostDeSpawn` clears coordinate/room/number, which is why despawn/respawn is inappropriate for retaining this deployed marker identity.

## Additional source observations

- The site saves encounter-started/withdrawn flags, movement count, pending distortion debit, warning time, entity reference and crew references. The intended limits are explicit: at most three pursuit advances, one attempted strike, threshold exclusion, and an idempotent run ID.
- `Thing.SpawnSetup` notifies the map attack-target cache. `Verse.AI.AttackTargetsCache.Notify_ThingSpawned` registers any `IAttackTarget`; it does not require a native `Pawn`. No concrete registration mismatch was found for the current ethereal `Thing_QuietPursuer` implementation. Actual firearm targeting/hits still need owner-launched acceptance.
- Laboratory work checks the physical recording in the analyst's carry tracker, the HQ map, bench power, position, work capability and skill. The work giver selects a real spawned item and reserves it. Inventory-to-floor delivery and interruption behavior still need runtime acceptance; no fabricated evidence item is used by the laboratory service.

## Reproducible inspection

From the repository root, using the ignored local tool and output directory:

```powershell
$managedPath = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
$assemblyPath = Join-Path $managedPath 'Assembly-CSharp.dll'
& .local/tools/ilspycmd.exe --version
New-Item -ItemType Directory -Force .local/inspection-investigation | Out-Null
foreach ($reviewType in @('Verse.Thing','Verse.ThingComp','Verse.ThingWithComps','Verse.GenMapUI','Verse.AI.AttackTargetsCache','Verse.GenSpawn','Verse.AI.Pawn_JobTracker')) {
    & .local/tools/ilspycmd.exe -r $managedPath -t $reviewType $assemblyPath |
        Set-Content -Encoding utf8 ('.local/inspection-investigation/' + $reviewType + '.cs')
}
```

This review inspected `GenSpawn` and `Pawn_JobTracker` from the existing ignored `.local/inspection-expedition/` output; the command above recreates those exact type inspections in one directory. The initial lookup of `Verse.AttackTargetsCache` failed because the actual type is `Verse.AI.AttackTargetsCache`; the corrected type was inspected successfully. No whole-assembly source tree was generated or committed.

## Remaining acceptance

After lead integration and the owner's RimSort launch: verify split-crew distortion triggering; real marker identity/location before and after save/load; blocked/full-cell deployment without stock loss; refused-order feedback; closed-door and changing-target contact warnings; movement/firearm retreat; bounded same-run rescue encounters; laboratory interruption; destroyed evidence before versus after analysis; base/bonus settlement retry; and pending distortion cost across save/load. These are planned cases, not tests performed by this review.
