# Phase 2: company, investigation, and threat integration review

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Date:** 2026-09-28. **Scope:** bounded source and Def comparison against the first-playable contracts. This is a static review, not runtime acceptance. No game, build, or tests were run. After the initial review, the evidence payload finding was implemented in Company source and described in the linked investigation implementation note; root also wired current field events to that API. This follow-up does not establish runtime acceptance. The adjacent generation edit replaced unregistered localization-key literals with English fixture labels/descriptions in `RR_BackroomsFixtures.xml`.

## Inputs and boundaries

- Player contract: [first playable](../FIRST_PLAYABLE_CONTRACT.md), [first-slice inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [threat sheets](../THREAT_DESIGN_SHEETS.md), [tutorial](../TUTORIAL_SCRIPT.md), [state ownership](../CAMPAIGN_STATE_DICTIONARY.md), and [operation actions](../OPERATIONS_ACTION_CONTRACTS.md).
- Implementation reviewed: `src/RimroomsAsyncIndustries/Company/`, `Investigation/`, and `Threats/`, with the associated first-slice Thing, Job, WorkGiver, RimroomsProject, building, and English-language definitions. Relevant Operations UI and expedition call sites were read to establish player routes.
- Prior source review: [investigation/threat review](PHASE_2_INVESTIGATION_THREAT_REVIEW.md). Its listed corrections for closed-door contact, target-specific contact warning, split-crew distortion selection, marker placement, rejected deployment jobs, and analyzed-evidence status were present in the current files. This does not establish they work in game.
- Implementation summaries: [investigation implementation](PHASE_2_INVESTIGATION_IMPLEMENTATION.md) and [threat implementation](PHASE_2_THREAT_IMPLEMENTATION.md). Those are design/source summaries, not runtime evidence.

## Findings

### RR-FIELD-01 — Durable field observation payload

**Source status: implemented; runtime acceptance remains open.**

The first review found that the physical AI-01 recording retained only checklist booleans, despite the first-slice contract and tutorial promising specific observations. The source follow-up adds typed, saved observation records and a frozen post-analysis report in [EvidenceObservations.cs](../../src/RimroomsAsyncIndustries/Company/EvidenceObservations.cs), with report ownership and additive serialization in [CampaignRecords.cs](../../src/RimroomsAsyncIndustries/Company/CampaignRecords.cs) and analysis completion capture in [InvestigationServices.cs](../../src/RimroomsAsyncIndustries/Company/InvestigationServices.cs). The site event code now calls the service for surveyed rooms, displaced tags, a recorder-gap follow-up, and a live entity. The Operations panel renders the frozen report after analysis.

The API validates a live expedition witness physically present in the observed room plus a physical recorder carried on the same active expedition at that site. Each row stores stable ID, event kind, observed/referenced room, marker number, witness identity/room, recorder and carrier identity, and game tick. Route coverage is derived from stored observations for all six required room families. It does not treat the map's `surveyed` flags as a recording. A true route flag from an older schema is preserved as an explicitly marked legacy summary only; no observation rows are fabricated from the old flags. Campaign load validation rejects malformed observation collections or report snapshots.

An analyzed legacy row with no typed data produces a report explicitly labelled as legacy details unavailable. New analysis freezes a copy of currently stored rows with analyst and completion tick. Source review establishes that these paths exist, not that gameplay captures every intended observation or that report data survives the game's actual save/load lifecycle.

**Required checks:** save/load before and after analysis; inspect the frozen report after more than 256 subsequent activity events; exercise duplicate survey/events; refuse remote, nonmember, missing-recorder, and failed-spawn facts; verify six-family route completion is impossible until six actual survey observations exist; confirm a later map survey without a valid recorder does not retroactively count as recorded.

### RR-FIELD-02 — Evidence case tutorial wording

**Source status: addressed; runtime acceptance remains open.**

The initial review found that the [tutorial](../TUTORIAL_SCRIPT.md#5-return-seal-and-report) described putting the recording inside a case that is not a container. The current tutorial correctly tells players to return the **AI-01 Route Recording** and physical case together as separate items; the case record links them through the expedition manifest. This matches the actual custody model.

**Required check:** follow the revised in-game instructions using normal hauling and verify that both separate items are required, moving either item away pauses analysis, and returning it resumes the same evidence record.

### RR-FIELD-03 — Quiet Pursuer spawn result

**Source status: addressed; runtime acceptance remains open.**

The initial review found that the encounter treated a requested spawn as a sighting without checking the result. The current [StartPursuer](../../src/RimroomsAsyncIndustries/Threats/FirstSlicePursuer.cs) verifies the returned Thing, `Spawned`, and map ownership before setting encounter state or exposing a sighting; failure removes the unspawned Thing, leaves the attempt retryable, and records no sighting. The observation service independently requires an actual live spawned entity at the recorded room.

**Required check:** force or simulate a rejected spawn; confirm no sighting, entity evidence, or bonus eligibility is recorded; then verify a later successful attempt records once.

### RR-FIELD-04 — Deployment item recovery

**Source status: addressed; runtime acceptance remains open.**

The initial review found that recovery attempted to drop multiple retained deployment items at one occupied cell. The current [RecoverDeploymentItems](../../src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs) selects a reachable, standable, unoccupied cell separately for each item and returns a refusal without discarding any remaining items when a safe drop cannot be found.

**Required checks:** with two held recovery items, confirm both can be recovered in one supported interaction; confirm a full/blocked site keeps undropped items in the holder.

## Reviewed behavior that matches the current contract

- Company insight/project state is branch-owned; Gate Telemetry is a local `RimroomsProjectDef`, not a native global Core research project. It uses a powered field analysis bench and Research work priority. This is consistent with the first-slice contract for a local project and should keep being labeled as company research in player-facing UI.
- The custody rule uses separate physical case and recording items, stable evidence IDs, a real HQ analysis bench, and native pawn carry/work. Missing or destroyed unanalysed evidence is retained as missing rather than recreated; case custody is rechecked before work and is revoked when an item leaves HQ.
- Root-provided fixes were present for the prior review's marker placement, job rejection, contact warning, closed-door pathing, and split-crew selection findings. The current distortion clue also has an explicit recovery message: if the crew crosses before placing a marker, it instructs them to place one at the known junction and approach again. This is an authored recovery path, but it still needs the skip-tag/revisit acceptance case below.
- The destination fixture Defs now use literal English labels/descriptions rather than untranslated `RR_Generation_*` strings. The world-object label/description are literal already.

## Runtime evidence still required

No source inspection establishes the feature as compatible or playable. Keep these Gate 0 / first-playable checks open: full AI-01 dispatch-to-return loop; no-tag crossing followed by the written backtrack/reapproach path; structured evidence survives save/load and remains available after long activity history; evidence/case item movement, destruction and recovery; rejected pursuer spawn; marker deployment/recovery after interruption; warning and counterplay timing; one-time base/bonus payments and insight; native research work interruption; repeat visit to the same saved coordinate; and optional-content-absent Core behavior. Record exact game build/profile, save, logs, and observed result when the owner performs those runs.
