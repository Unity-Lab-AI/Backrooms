# Scenario setup and native-provider replacement task

**Baseline:** source/document commit `9de5e73cd2443621af47abe91cfb62e2e21390d8`; compiled/staged `0.3.0-dev`, 68 package files, DLL `22DA7E237C79E8DABF5F5DCFE6049F283BCE001CCADB9D241FB41A950C1AAAF1`. Previous goal turn made progress through implementation, successful compilation/staging and verified publication. The full mod goal remains active.

## Scope and requirements

Read [scenario and portal direction](../SCENARIO_SETUP_AND_PORTAL_NETWORK.md), [installed-provider source review](SCENARIO_AND_DOOR_PROVIDER_SOURCE.md), [regression containment](../REGRESSION_CONTAINMENT.md), [content reuse](../CONTENT_REUSE_POLICY.md), [save policy](../SAVE_MIGRATION_POLICY.md) and the [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md). Features: RR-SCEN, RR-STA, RR-FAC, RR-GATE, RR-EXP, RR-SPACE, RR-EVD, RR-STYLE, RR-COMPAT.

| Work | Exclusive ownership | Preserved behavior / deliberate change |
| --- | --- | --- |
| Company customization | Agent core_build_source_review: `Scenario/`, start/scenario/ScenPart XML, new startup keyed text, own implementation record | Replace fixed custom-kind roster enforcement with final actual-pawn role/setup review reachable after native/EdB customization. Preserve selected tile, edited identities/relationships/gear, native one-time arrival/supplies, existing setup receipts and company ledger initialization. Core row 4; optional Prepare Carefully row 85. |
| Native generated room providers | Agent edge_graph_audit: `GenStep_BackroomsDestination.cs`, `FailedSiteRecovery.cs`, relevant legacy fixture/terrain XML only, own record | Replace new-map custom fixtures/carpet with actual Core providers and real physical power; preserve saved old maps, graph identities, fog, route clues, salvage, evidence locations and recovery checks. No new gameplay assets. |
| Gate migration impact | Agent gate0_readiness_audit: read-only code/provider review and `NATIVE_GATE_MIGRATION_IMPACT.md` | Inventory existing gate state/callers and native-door power/endpoint migration route before changing it. No claim that the migration is implemented. Preserve dispatch/recall/emergency/recovery/abandonment/receipt behavior. |
| Integration and completion | Lead: shared company/UI integration, contracts/TODO, version/allowlist, compile/evidence, staging and publication | Review changed callers and serialized fields; merge exclusive scopes, correct any compiler/source findings, check only evidenced source/build increments. Publish both cascades once at a meaningful completed milestone. |

No game, tests or runtime compatibility claim is authorized by this task record. The owner alone launches through RimSort when ready. Independent code work continues while that acceptance remains deferred.

## Regression impact checklist

- [x] Actual customized pawns survive final setup, Back/reopen and new-game initialization; no hidden replacement or skill/priority rewrite.
- [x] Native starting possessions/scenario supply parts have one owner; facility stock does not duplicate edited supplies.
- [x] Existing `HeadquartersSetupComponent` and company initialization receipts remain readable and do not replay grants.
- [x] Selected company tile remains unchanged; alternate-start logic does not accidentally invoke company funding or facility generation.
- [ ] New native fixtures have valid physical power/placement without blocking saved paths or wiping existing objects.
- [ ] Existing generated maps, discovery/evidence IDs and paid rewards are retained; replacement eligibility still refuses touched/occupied sites.
- [x] Gate impact review accounts for every existing consumer, saved field and recovery action before native-door migration begins.
- [x] Integrated compilation and package evidence are saved; TODO source/build checkboxes and remaining runtime cases match the result.

These items are an impact review queue, not runtime test results. The owning implementation records must explain which were source-reviewed, compiled, or still need owner-launched observation. Prior native menu, hiring, procurement, laboratory and evidence behavior must remain reachable while these systems change.

## Future owner-launched cases

Core and Prepare Carefully company setup with default/edited rosters, count changes, Back/cancel and equipment edits; existing development saves and same-version reload; repeated registration; chosen-tile fidelity; new-map room lighting/power/climate and clear routes; old-map revisit; evidence loss/no-remint and failed-site refusal; ordinary native research; personnel/shipments and the existing first-survey dispatch → return → analysis → payment loop. Gate migration adds its own connected battery, interruption and endpoint tests after implementation.

Source review completed for the company setup and gate-impact items above; see [scenario evidence](PHASE_3_SCENARIO_SETUP_IMPLEMENTATION.md) and [native-gate impact map](NATIVE_GATE_MIGRATION_IMPACT.md). These checkmarks record source/caller inspection, not observed gameplay behavior. The initial company-only integration compiled with zero warnings/errors; the final combined checkpoint remains in [the build record](PHASE_3_SCENARIO_PROVIDER_BUILD.md).

Publication boundary: company setup source and both provider reviews are included in 0.3.1. Native room source changes were not started before this checkpoint; the two room implementation checks remain open for the next milestone. No in-progress project edits are deliberately withheld from publication.
