# Phase 2 first-survey generation recovery

**Status:** bounded source implementation for development slice 0.2.0; no RimWorld runtime, save/reload, or owner acceptance evidence is claimed. This action exists only to recover the untouched Async Industries opening survey after a narrow first-site generation failure.

**Feature route:** `RR-SPACE` owns coordinate identity and generation, `RR-EVD` owns the still-empty case/evidence links, `RR-EXP` supplies custody checks, and `RR-UI` exposes the player action. See the [first-playable contract](../FIRST_PLAYABLE_CONTRACT.md), [first-slice inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [procedural-space contract](../PROCEDURAL_SPACE_CONTRACT.md), [state dictionary](../CAMPAIGN_STATE_DICTIONARY.md), [save policy](../SAVE_MIGRATION_POLICY.md), and [Operations action contract](../OPERATIONS_ACTION_CONTRACTS.md).

## Player route and API

Atlas → **Review a replacement coordinate** opens a confirmation dialog. Confirmation calls:

```text
RimroomsCampaignComponent.ReaddressPristineInitialSurvey(string failedCoordinateId)
```

The service is in [`FailedSiteRecovery.cs`](../../src/RimroomsAsyncIndustries/Generation/FailedSiteRecovery.cs). It returns the standard `CompanyActionResult`:

| Result | Meaning |
| --- | --- |
| `Applied` | A single replacement coordinate was committed after every guard and fallback preflight passed. |
| `Existing` | The deterministic replacement receipt already exists and its stable identity, seed, room geometry/topology, and contract/case links still match. Survey flags and a valid generated site owner may have progressed; no new mutation occurs. |
| `Refused(key)` | Eligibility, custody, content, integrity, cap, or fallback checks failed. Nothing is deleted, moved, granted, or paid by this operation. |

The stable receipt and replacement coordinate ID is `<failedCoordinateId>:fallback:1`. The replacement label is `AI-01R`; its seed is derived from the branch campaign seed and that stable ID. The replacement receives a planner-validated six-room safe fallback graph. The old map owner, map, graph, objects, and failure data remain in place. The initial unpaid survey contract and empty case are rebound to the replacement only after preflight completes.

The adjacent [`RoomLayoutPlanner.TryBuildSafeFallback`](../../src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs) builds and validates the fixed graph without mutating the input coordinate. It is a geometry preflight; successful preflight does not prove that the map or Defs load in RimWorld.

## Eligibility and fail-closed checks

The service accepts only the `async_industries` scenario's unique onboarding survey (`rr.survey.onboarding.v1`) and initial empty case. For a new readdress, the original survey must still be accepted and unpaid, its case open and empty, and the failed coordinate must be its current link. No other contract, case, evidence record, or settlement receipt may refer to the failed coordinate.

Recovery is restricted to a single initial coordinate and one replacement. It requires a retained, registered `RR_BackroomsSite` owner, an attempted but incomplete generation, the expected map ownership, and one of the source allowlisted placement/geometry failure keys. Required current map, thing, and terrain Defs are checked before creating the replacement. Missing definitions, unknown/source failure keys, or failed dependency preflight return `RR_Generation_ReaddressContentRestore`: package/source diagnosis is required, replacement is unavailable for this record, and the failed site is retained. Readdressing a coordinate does not repair a missing definition or arbitrary source error.

The site must remain pristine for the initial readdress: no surveyed rooms; no expedition or interrupted transfer linked to the coordinate/map; no map pawns or corpses, including nested holders; no evidence record or physical `RR_RouteRecording`; and no case activity. Any uncertainty while scanning custody holders refuses recovery. The service never cleans up or archives a failed map, reuses a map, moves pawns/items, spends funds, pays the contract, or removes evidence.

After creation, the stable `:fallback:1` receipt stays idempotent as the campaign progresses. A repeated request returns `Existing` if the failed-site owner is still retained and the replacement ID, seed, generator/library versions, room geometry/topology, and initial contract/case links remain consistent. Room surveyed flags may change; an assigned replacement site is accepted only when it is the registered `RR_BackroomsSite` owner for that replacement coordinate, with any loaded map still owned and registered correctly. Other coordinates added later do not invalidate the receipt. A conflicting record refuses rather than being overwritten.

The exact allowlisted failure keys and required Def names are maintained in `FailedSiteRecovery.cs`. Adding a new failure key or dependency requires source review and an explicit update to this contract; unknown errors remain ineligible.

## Player feedback keys

The corresponding English keyed entries are in [`RR_Generation.xml`](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_Generation.xml):

- `RR_Generation_ReaddressContentRestore` — package/source diagnosis required; replacement cannot repair this record; site retained.
- `RR_Generation_ReaddressFailureNotEligible` — not an eligible initial failed survey.
- `RR_Generation_ReaddressSiteNotPristine` — activity, people, evidence, or linked expedition state prevents readdressing.
- `RR_Generation_ReaddressReplacementExistsMismatch` — conflicting deterministic replacement exists; records are preserved for diagnosis.
- `RR_Generation_ReaddressSiteCapReached` — one failed site plus one replacement is the hard cap for this recovery path.
- `RR_Generation_ReaddressFallbackInvalid` — fixed fallback graph failed preflight; no links or items changed.
- `RR_Event_SiteReaddressed` — activity event records old and new coordinate labels; the failed map is retained and the initial contract remains unpaid.

The Atlas control, confirmation, and common result rendering are in [`MainTabWindow_Operations.cs`](../../src/RimroomsAsyncIndustries/UI/MainTabWindow_Operations.cs). The action is a player-invoked recovery, not an automatic retry or silent reroll.

## Verification still required

Source-level implementation and deterministic guards are present. The following remain unverified and are acceptance work, not evidence inferred from source:

1. Lead compilation/package validation passed for the pinned Core references: zero warnings/errors, 61 packaged/staged files. See the [build record and receipts](PHASE_2_BUILD_RECORD.md). Actual Def loading in a Core-only session is still required.
2. A controlled generation failure for each allowlisted category; verify the failed owner/map/content remain visible and unchanged.
3. Refusal checks for missing required Defs, unknown/source failure, evidence, route recording, pawns/corpses/holders, interrupted transfers, unrelated expedition links, non-initial scenarios, prior replacement, and site cap.
4. Successful readdress creates one AI-01R coordinate with six rooms, preserves the old failed map and objects, rebinds only the initial contract/case, and grants/spends/transfers nothing.
5. Save, reload, and repeat action: exactly one replacement remains; exact retry returns `Existing`; conflicting records refuse without mutation.
6. Atlas labels, confirmation, refusal text, activity-feed formatting, and keyboard/accessibility behavior in game.

The delegated author performed no game, compile, test or save/reload run. The lead subsequently recorded the integrated compiler/package/staging result above. All gameplay and persistence cases remain unobserved.
