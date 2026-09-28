# Pre-production acceptance standard

This standard turns the project's “AAA-grade” quality goal into observable pass conditions. It is a target for a RimWorld mod team, not a claim that the project has studio-scale resources. A criterion is complete only when the evidence is saved and linked from [FEATURE_TRACEABILITY.md](../FEATURE_TRACEABILITY.md) or the relevant release report.

## Gate 0 evidence acceptance

- All D1–D9 choices remain recorded in [GATE_0_DECISIONS.md](../GATE_0_DECISIONS.md); the mod title is exact and author/publisher metadata is `Operator`.
- Every source-derived design claim links to a reviewed source record. All 23 indexed Kane Pixels uploads and the A24 feature receive separate saved review records before source-specific production begins.
- Every one of the 294 profile rows has a verified package identity, source/version review, required-dependency and license notes, feature IDs, final disposition, and a review record. “Verified alongside” counts only after the named profile is tested.
- RimWorld, DLC, Harmony, and RWT client/server builds are pinned. Before code, run the disposable two-client cases in the [RWT baseline test plan](RWT_BASELINE_TEST_PLAN.md): separate vanilla-started branches, supported visits, ordinary cargo/aid exchange, reconnect, and save recovery. Include optional profile rows 182 and 274 because the owner selected them for testing despite publisher warnings. Record failures without claiming compatibility. Custom Rimrooms dossier transfer and conditional shared-ledger behavior are post-code acceptance tests and stay disabled until implemented and verified.
- The scenario, system, visual, accessibility, persistence, performance, and release contracts have owners, acceptance evidence locations, and no unresolved dependency decisions.

## Playable campaign acceptance

- **Core solo route:** a fresh Core-only save can start Async Industries, finish the first gate repair/calibration, dispatch and return a crew, analyze evidence, receive a payment/research outcome, save, quit, reload, and continue without DLC or optional profile mods.
- **Scenario coverage:** the facility start is the first playable target. Store and Lone Survivor starts each receive unique setup tests and converge into shared campaign/coordinate systems before broad release.
- **Expedition safety:** every generated destination provides a visible dispatch condition, a return/extraction rule, and a recoverable failure path. No required campaign objective can generate an unrecoverable softlock.
- **Procedural repeatability:** for 1,000 recorded seed/coordinate cases per generator release, identical inputs produce identical room graphs; every generated graph passes route validation and has a reachable extraction path. Changed generator versions preserve saved visited sites or use a reviewed migration.
- **Persistence:** a scripted suite performs at least 100 save/load cycles across representative Core and all-five-DLC saves, plus migration tests from each supported prior schema. No duplicated starting grants, lost pawns/items, reset discoveries, or unrecoverable load errors are accepted.
- **Co-op transactions:** in the pinned two-client profile, exercise at least 100 item/dossier transfers and 20 interrupted/reconnected transfers. There must be zero duplicate company-ledger postings, silently lost cargo, or cross-branch writes to state that remains branch-owned. Shared research is enabled only after equivalent ledger-sync tests pass.

## Integration and compatibility acceptance

- Maintain two distinct claims: **required dependency** and **tested compatibility**. Only Core is required for solo; Harmony and RimWorld Together are additionally required for co-op. All other 294-profile entries and all five DLC remain optional.
- Run the complete ordered 294 profile at the pinned versions after a clean Core baseline. Record startup/save errors, warnings, load order, settings, relevant feature interactions, and disposition for every entry. Publish only the configurations actually tested.
- Verify a Core-only run and an all-five-DLC run. Test each DLC-specific feature in the feature map with the relevant DLC present and absent; absent optional content must leave the base campaign playable.
- Re-run the smoke and save/load suite after any game, DLC, RWT, required dependency, or Rimrooms version change.

## Quality and accessibility acceptance

- **Content:** no placeholder text, art, sound, or scenario rewards in a release candidate. Every shipped asset has a provenance record and distribution permission/license record; original source code carries the selected MIT license. Do not infer an author name from the license.
- **Language:** 100% of player-facing text is supplied through localization keys; a test locale with deliberately long strings has no clipped critical controls or missing-key output.
- **Usability:** every company operation has an understandable name, visible preconditions, result, and failure/recovery message. A new player can complete the first operation using the tutorial and UI alone, without external notes.
- **Accessible cues:** no essential warning or status relies only on color, audio, animation, or screen shake. Provide text/caption equivalents for radio and threat cues, non-color state indicators, reduced-flash/reduced-shake options where the engine allows, readable UI scaling, and keyboard/controller focus checks for custom panes.
- **Performance:** benchmark the same named machine and exact profiles against a vanilla/profile baseline. Record map generation p50/p95, idle and active tick cost, memory growth across repeated expeditions, and UI draw cost. Before implementation, set ceilings in the benchmark plan; reject regressions that exceed the agreed budget or grow without bound.
- **Stability:** no uncaught errors in the representative campaign smoke suite; no new save/load exception or broken reference in the release log. Every known compatibility limitation is documented instead of hidden.

## Release decision

The private RWT prototype must meet the Core-only solo path and the pinned co-op acceptance tests. Public release additionally requires the chosen platform's current content questionnaire to be completed accurately, source/asset credits to be finalized, install and migration instructions, and a compatibility table that matches saved test evidence. No age classification or author/publisher name is preselected here.
