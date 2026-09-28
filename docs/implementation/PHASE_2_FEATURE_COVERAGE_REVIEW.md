# Phase 2 first-playable feature coverage review

**Date:** 2026-09-28. **Scope:** static comparison of the first-playable contract, first-slice inventory, tutorial script, current source and Phase 2 build record. Read-only except for this report. No build, tests or RimWorld session were run. Feature presence here means source paths exist; it does not establish Def loading, gameplay success, save/load behavior, balance or usability.

## Assessment

The bounded Async Industries loop has source routes for branch setup, gate assembly and staffed operation, one saved AI-01 destination, physical expedition cargo, route/threat observations, evidence analysis, one-time settlement, Gate Telemetry and a revisit. The starting roster, facility, account and physical stock are authored in the start Def. The room planner has three deterministic candidates plus a six-room precommit fallback; the content builder places native furnishings, the original carpet treatment, clue landmarks and optional physical salvage. These are implemented-source findings, not runtime acceptance.

This review initially identified two concrete gaps in the bounded player loop; the lead's implementation follow-up below closes their source work while retaining runtime acceptance:

1. The promised next-lead choice conflicts with the one-coordinate first-slice scope and has no follow-on-contract implementation.
2. A failure after destination-map generation starts leaves the coordinate permanently unavailable; the existing planner fallback does not cover that post-commit failure path.

Narrative tutorial delivery and final in-game presentation remain polish/acceptance work. They do not block the implemented first expedition source path.

## Findings recorded before the integration fixes

The following preserves the source situation at the initial review. The current source and contracts have the fixes described in the closure follow-up below.

### 1. The next-lead instructions promise a contract that the first slice does not contain

The first-playable contract says the player chooses Gate Telemetry or a follow-on survey contract after settlement and that either leads to a second expedition ([`FIRST_PLAYABLE_CONTRACT.md`, first-session step 6](../FIRST_PLAYABLE_CONTRACT.md#the-first-session)). The tutorial repeats that choice and says the new survey is for learning what AI-01 is hiding ([`TUTORIAL_SCRIPT.md`, section 6](../TUTORIAL_SCRIPT.md#6-choose-the-next-lead)). The inventory, however, defines only one coordinate, one accepted survey, and one reward path and defers broader campaign systems ([`FIRST_SLICE_CONTENT_INVENTORY.md`, included/deferred](../FIRST_SLICE_CONTENT_INVENTORY.md#included-and-deferred)).

The current source supports only the initial `rr.survey.onboarding.v1` contract and AI-01 coordinate: `InitializeBranch` creates and registers one coordinate, one case, one accepted contract and the Gate Telemetry project ([`CampaignServices.cs`](../../src/RimroomsAsyncIndustries/Company/CampaignServices.cs#L57-L91)); settlement filters specifically for the onboarding template ([`EvidenceSettlement.cs`](../../src/RimroomsAsyncIndustries/Company/EvidenceSettlement.cs#L44-L67)). No other source path creates a `CoordinateRecord` or adds a contract. The Operations contract pane is read-only ([`MainTabWindow_Operations.cs`](../../src/RimroomsAsyncIndustries/UI/MainTabWindow_Operations.cs#L122-L129)). After Telemetry, its actual objective is to review the surveyed route and revisit the saved coordinate ([`RR_OperationsExpeditions.xml`](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_OperationsExpeditions.xml#L58)); dispatch selects only from the coordinates already in the branch ([`OperationsExpeditions.cs`](../../src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs#L164-L190)).

**Bounded closure recommendation:** honor the inventory's one-coordinate / one-contract / one-reward first slice. Describe the second choice as an optional **AI-01 resurvey/revisit preparation objective**, not a new contract or coordinate. The Operations pane already permits dispatch back to the saved AI-01 map; make its objective and mission card explain that the repeat trip is for continued exploration, salvage or construction, with no second onboarding payment. Keep generated follow-on contracts and coordinates in the later dynamic-campaign phase. Update the first-playable contract and tutorial together so they no longer promise an unavailable contract. This recommendation adds no new generated coordinate and does not settle any broader campaign design.

Feature route: **RR-MSN, RR-SPACE, RR-ECO, RR-UI, RR-EXP**.

### 2. Post-commit destination-generation failure has no player recovery route

There is already a bounded *precommit* geometry fallback: [`RoomLayoutPlanner.TrySelect`](../../src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs#L18-L29) tries three plans and then a fixed six-room fallback. It would be inaccurate to list that graph fallback as missing.

The uncovered failure is later. [`DestinationService.EnsureSite`](../../src/RimroomsAsyncIndustries/Generation/DestinationService.cs#L111-L154) registers the coordinate's map owner and records `BeginGenerationAttempt` before asking Core to generate the map. If room placement/content throws, [`GenStep_BackroomsDestination.Generate`](../../src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs#L118-L125) records failure and retains the partial map. A later attempt is refused because `GenerationAttempted` is treated as an already-opened/missing-map case ([`DestinationService.cs`](../../src/RimroomsAsyncIndustries/Generation/DestinationService.cs#L87-L93)). There is no replacement-coordinate creator in the current source. Expedition dispatch calls `EnsureSite` before making the expedition record or transferring the crew ([`RimroomsExpeditionComponent.cs`](../../src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs#L58-L93)), so this failure preserves the crew and cargo but can strand the initial survey before it can begin.

**Minimal safe recovery proposal (design only):**

- Keep the failed coordinate, map, failure key and all placed objects as a quarantined historical record; never delete or silently reroll it.
- Permit exactly one deterministic replacement attempt for the unresolved initial survey only when the failed site is pristine: no expedition/entry, surveyed room, field observation, evidence item, player-built/placed object, moved crew or transferred cargo. A stable receipt must make the replacement idempotent, and the original contract/case linkage must move atomically to the replacement while the failed coordinate remains inspectable.
- Force the bounded six-room fallback layout on this single replacement. Set the first-slice retained destination-map cap to **two** (one quarantined failure plus one active replacement); do not mint a third site if the replacement fails.
- Do not use a replacement for missing required Core/Rimrooms Defs, missing owner/assembly, or installation mismatch: generating the same content again cannot repair a missing dependency. Give a specific refusal and preserve the record until the package/Def problem is corrected.
- If the site has been visited, surveyed, supplied with evidence, or touched by player activity, do not relink or replace it. Retain it and route the player to explicit diagnosis/recovery; preserving identity and belongings takes precedence over a fresh roll.

This is a source-identified recovery gap, not evidence that the normal generator currently fails. Feature route: **RR-SPACE, RR-EXP, RR-EVD, RR-UI**.

## Remaining work that is not a source omission

- **Narrative tutorial:** the tutorial document labels its dialogue as presentation target; current Operations has a next-objective board, equipment/action controls, written warnings and an evidence checklist. The full staged dialogue/quote sequence is not implemented in source, but the first-playable contract asks for a short explanation and an actionable board rather than that exact scripted sequence. Keep it as presentation work unless the owner makes staged dialogue an acceptance requirement ([`TUTORIAL_SCRIPT.md`](../TUTORIAL_SCRIPT.md); [`OperationsExpeditions.cs`](../../src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs#L20-L43)).
- **Visual/audio finish:** source now contains seeded room/furnishing variation, clue labels/tooltips and salvage ([`RoomContentBuilder.cs`](../../src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs#L30-L87); [`RoomContentMapComponent.cs`](../../src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs#L54-L65)). Build record still calls for checking presentation and quiet audio cues in game ([`PHASE_2_BUILD_RECORD.md`](PHASE_2_BUILD_RECORD.md#remaining-phase-2-work-before-promotion)). This is rendered-quality/accessibility acceptance, not proof that the code path is absent.
- **Runtime acceptance:** Def loading, fresh start, work/power, pathing, crew and cargo identity, threat response, evidence/settlement, save/reload/revisit, performance and the owner-prepared mod profiles remain unverified. These are acceptance observations, not static omissions; do not mark Gate 2 complete from this review.

## Build-record evidence note

The earlier audit found a stale 0.1.0 staging receipt. The final [0.2.0 compiler/package/reference/staging packet](evidence/phase2-first-expedition-2026-09-28/) now exists and is linked from the [build record](PHASE_2_BUILD_RECORD.md). Compilation passed with zero warnings/errors and all 61 staged files matched their manifest. This closes the artifact-trail gap; it does not establish a runtime result.

## Smallest closure sequence

Lead integration follow-up: the first-playable contract, tutorial, scenario and campaign catalog now consistently offer Gate Telemetry or **Prepare an AI-01 resurvey** for the bounded first slice. Operations exposes both choices after analysis and states that repeat visits preserve the same site without repaying onboarding. Generated paid follow-on contracts remain in the full Phase 3 scope. Finding 1 is resolved in source/documentation. Finding 2 has the [one-time pristine-site recovery implementation](PHASE_2_GENERATION_RECOVERY.md), stable repeat-call behavior, preserved failed map and two-site cap. Final package receipts are saved above. UI/gameplay/save behavior remains unobserved.

1. Resolve the one-coordinate/follow-on-contract text conflict by adopting the bounded AI-01 resurvey route or explicitly expanding first-slice scope; the bounded resurvey route is recommended above.
2. Implement the one-time pristine-site replacement/quarantine path and distinguish retryable generation faults from missing-Def faults; preserve the two-site cap.
3. Regenerate and link the integrated 0.2 build/staging receipts after the concurrent source work lands.
4. Keep Gate 2 closed until the separately owned, dated in-game acceptance observations are recorded.
