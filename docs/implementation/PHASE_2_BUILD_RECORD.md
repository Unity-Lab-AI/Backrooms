# Phase 2 development build: 0.2.0

**Date:** 2026-09-28. **Status:** first-expedition implementation in development. Gate 2 has not passed. The full mod goal remains active. No RimWorld launch or gameplay test has been performed for this build.

## Source and feature routes

Start with the [task record](PHASE_2_VERTICAL_SLICE_TASK.md), [first playable contract](../FIRST_PLAYABLE_CONTRACT.md), [content inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [action contracts](../OPERATIONS_ACTION_CONTRACTS.md), and [save policy](../SAVE_MIGRATION_POLICY.md). Every current game API comes from Core row 4, package `Ludeon.RimWorld`, reviewed DLL SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. Optional profile APIs are not referenced by this assembly.

| Feature IDs | Actual source and player route | Source / implementation evidence |
| --- | --- | --- |
| RR-SCEN, RR-FAC, RR-STA | [Scenario](../../src/RimroomsAsyncIndustries/Scenario/): choose Async Industries; five staff, 60×60 facility and physical stock; separate physical setup and branch registration receipts | [Scenario API review](PHASE_2_SCENARIO_SOURCE_REVIEW.md), [scenario implementation](PHASE_2_SCENARIO_IMPLEMENTATION.md) |
| RR-ECO, RR-MSN, RR-EVD | [Company](../../src/RimroomsAsyncIndustries/Company/): $50m branch account, daily wages/overhead, explicit arrears, original $5m survey and optional $1m bonus, saved cases and evidence | [Company source review](PHASE_2_COMPANY_SOURCE_REVIEW.md), [investigation implementation](PHASE_2_INVESTIGATION_IMPLEMENTATION.md) |
| RR-GATE | [Gate](../../src/RimroomsAsyncIndustries/Gate/): physical assembly bill, calibration, qualified staffed console, accounted power/reserve, bounded opening, warnings, cutoff and paid recovery activation | [Work/power API review](PHASE_2_WORK_POWER_SOURCE_REVIEW.md), [gate implementation](PHASE_2_GATE_IMPLEMENTATION.md) |
| RR-SPACE | [Generation](../../src/RimroomsAsyncIndustries/Generation/): stable coordinate, 6–8 rooms, retained 60×60 map, native doors/roof/light, saved threshold/evidence cells | [Destination API review](PHASE_2_DESTINATION_SOURCE_REVIEW.md), [destination implementation and limitations](PHASE_2_DESTINATION_IMPLEMENTATION.md) |
| RR-EXP | [Expedition](../../src/RimroomsAsyncIndustries/Expedition/): actual inventory pickup, approach jobs, same-pawn transfer, recall, casualty carry, stranded recovery, abandonment history and cargo declarations | [Expedition implementation](PHASE_2_EXPEDITION_IMPLEMENTATION.md) |
| RR-EVD, RR-GATE | [Investigation](../../src/RimroomsAsyncIndustries/Investigation/): physical recording and case, staffed analysis work, once-only insight, company research and surveyed-route telemetry | [Investigation implementation](PHASE_2_INVESTIGATION_IMPLEMENTATION.md) |
| RR-THREAT, RR-SPACE | [Threats](../../src/RimroomsAsyncIndustries/Threats/): numbered physical route aids, observable corridor mismatch and bounded attackable encounter | [Threat implementation](PHASE_2_THREAT_IMPLEMENTATION.md), [initial source review](PHASE_2_INVESTIGATION_THREAT_REVIEW.md) |
| RR-UI, RR-STYLE | [UI](../../src/RimroomsAsyncIndustries/UI/): nine Operations panes, next objective, real pawn/building/item links, written observations, closure/declaration dialogs; original equipment and creature sprites | [Original art prompts and paths](assets/phase2-original-art.json), [provenance register](../research/provenance-register.csv) |
| RR-STYLE, RR-SPACE, RR-GATE | [Audio](../../src/RimroomsAsyncIndustries/Audio/) and native user settings: four original quiet event cues, separate gate/field mute and volume; original carpet with native room-wall paint | [Audio source review](PHASE_2_AUDIO_SOURCE_REVIEW.md), [audio implementation](PHASE_2_AUDIO_IMPLEMENTATION.md), [interior presentation](PHASE_2_INTERIOR_PRESENTATION.md) |

The inventory uses native definitions at runtime; proprietary source or images are not copied into the package. Project masters live in `assets/source/phase2/`; only approved PNGs and game-loadable files enter the mod. Native-resolution image exports are temporary development assets; normal-zoom readability and memory sizing remain acceptance work.

## Concrete behavior refinements

- A relief pawn is separate from the original three-person survey crew. The safety bonus follows the original crew, including later live rescue, and cannot be earned with replacement staff.
- Recovery reuses the saved expedition/site and has its own monotonic operation receipt. Charging and activation have actual power costs; replaying a receipt does not refill a window or capacitor.
- Abandonment closes the operation record and gate, preserving the map, people, bodies, equipment and evidence in place. A later run can physically recover historical crew. Closure snapshots and cargo declarations remain auditable after recovery.
- Company research uses `RimroomsProjectDef` and the native Research work schedule at the field analysis bench. This implements the required insight gate without changing Core's research system or adding Harmony. Gate Telemetry reveals connections between surveyed rooms only.
- The case and recording are separate physical items. Their shared expedition manifest and presence at headquarters establish first-slice custody; the case is not a hidden container. Analysis checks both still exist at headquarters. A destroyed unique recording stays lost; revisiting never grants a copy.
- Field observations preserve actual room and marker IDs, tick, witness and recorder carrier. Completed analysis freezes that record for the Investigation panel. Earlier records with only checklist flags are explicitly labeled as lacking detail.
- Generation tries three deterministic room plans and a six-room fallback before committing a map. Existing saved layouts are retained. Original furnishing arrangements, native closed/hold-open doors, observed clues and physical salvage now occupy the room families. Atlas text reveals only observed landmarks.
- [Initial-site recovery](PHASE_2_GENERATION_RECOVERY.md) permits one explicit replacement coordinate for a pristine first-generation geometry failure. The failed map remains saved, the original unpaid case/contract follow the replacement, and a stable receipt prevents repeated replacement. Missing content, prior activity and unknown failures refuse. The bounded slice retains at most the failed site plus one replacement.
- The pursuer requires a real open approach two graph rooms from the crew. An unopened route delays the encounter; it does not grant a sighting or instantly counter an invisible creature. Successful native spawn is verified before any observation is recorded.
- Opt-in development counters measure component, generation, route-validation and Operations costs without modifying campaign saves. No performance measurements have been collected.
- The post-analysis choice now offers Gate Telemetry or preparation for an AI-01 resurvey. This reconciles the tutorial with the first-slice inventory's one coordinate and one paid survey. It preserves the full Phase 3 requirement for generated paid follow-on contracts; the repeat first-site visit cannot repay onboarding or regenerate unique evidence.
- The accepted 20 **in-game** minute opening remains 833 ticks while an owner timing clarification is pending. This is roughly 14 seconds at normal game speed and is a known usability/balance risk. No answer is inferred. Threat timings also remain their accepted in-game units.

## Build evidence and limits

The final integrated `tools/build.ps1 -NoRestore` run compiled net472/C# 7.3 with **zero warnings and zero errors** and packaged **61 explicit files**. Assembly SHA-256 is `EB542B4D4F5E27CB08F3FA8AA673B64B9CA89D58568175A8A7B3F6E75B2D6575`. The current assembly adds the locally referenced `UnityEngine.TextRenderingModule`; all game/Unity references remain `Private=false`. The authoritative current file allowlist is [tools/package-files.json](../../tools/package-files.json).

Saved receipts: [compiler output](evidence/phase2-first-expedition-2026-09-28/compiler-output.txt), [package manifest](evidence/phase2-first-expedition-2026-09-28/package-manifest.json), [reference manifest](evidence/phase2-first-expedition-2026-09-28/reference-manifest.json), and [staging receipt](evidence/phase2-first-expedition-2026-09-28/staging-receipt.json). All 61 installed files were hash-compared with the package. The prior 0.1.0 installation was preserved at the backup path in the staging receipt. A build hash is evidence for those exact files, not for later edits.

The [source manifest](evidence/phase2-first-expedition-2026-09-28/source-manifest.json) records the 45 C# file hashes present at compilation. The saved-document audit also passes: 294 reviewed rows, 914 relationship records, 23 indexed story records and zero open Gate 0 boxes. Six new line-fragment links were corrected to stable document headings before the passing audit; this checks saved references and register agreement only.

RimBridgeServer 2.1.1 is separately staged, with its publisher archive digest and 17 installed file hashes recorded in the [QA receipt](evidence/phase2-first-expedition-2026-09-28/rimbridge-staging-receipt.json). It is not enabled or a Rimrooms dependency. Follow the [owner launch sheet](PHASE_2_OWNER_LAUNCH.md) and [direct-attach review](PHASE_2_BRIDGE_SETUP_REVIEW.md). No profile was changed, game launched or bridge connected. Compilation/staging is not a Def-load, save/load, gameplay, performance, full-profile, or co-op result.

## Remaining Phase 2 work before promotion

1. The recorded Company/field, XML and bounded feature-coverage source findings have implementation follow-ups; final compiler/package/staging records are saved above. Fix any further issue exposed by the owner-launched session and preserve its evidence.
2. Inspect interior materials, furnishing/clue placement, native doors and quiet audio cues at actual game zoom and listening levels. Their source and original assets exist; rendered quality, subjective mix, runtime reachability and export sizing remain unobserved.
3. Observe failed-generation recovery against the implemented bounded selection and retained partial-map policy. Partial maps fail closed and remain retained; they are never deleted or rerolled after a visit.
4. Resolve the opening-time choice and tune the readable warning/contact windows. No runtime timing conclusion is available.
5. Collect the implemented diagnostics and complete the finite retained-map policy before expanding to more coordinates.
6. After the owner's first full 295-target RimSort launch (bridge overlay counted separately), collect Def-load, startup, fresh scenario, one-time grants, power/work, fog/path, field gear, rescue, analysis, payment, save/reload/revisit, UI and performance observations. Fix observed failures before claiming Gate 2.

Full campaign hiring/training, procurement/shipments, dynamic contract families, broader research, outposts, alternate starts, town cases, containment, optional integrations/co-op, menu slideshow, balance and release work remain in the [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md). This checkpoint does not close those tasks.

## Publication and independent follow-up

Source/asset commit `616321afe8cc58402b33fa1eb9988dacb4752705` was pushed and read back through all four branches on both Forgejo and GitHub; see the [publication receipt](evidence/phase2-first-expedition-2026-09-28/publication-receipt.json). This is a development checkpoint, not a release tag or gameplay pass.

While the owner's launch remains pending, [personnel/facility source preparation](PHASE_3_PERSONNEL_FACILITIES_TASK.md), [physical procurement source preparation](PHASE_3_PROCUREMENT_TASK.md), the [bounded direct-attach client](PHASE_2_BRIDGE_CLIENT_SOURCE.md) and [two original menu-art candidates](PHASE_5_MENU_ART_PREPARATION.md) were prepared outside the 61-file mod package. None changes the compiled 0.2.0 DLL, installed target/profile or pending acceptance status.

The attach client's second source-reviewed revision adds opt-in game state, configured/loaded mod identity, and recent warning/error capture. Its 512-entry array limit accommodates the full QA profile, and any sanitizer truncation yields incomplete evidence with a nonzero exit. Source inspection and syntax parsing are recorded in the linked client review; no connection, profile change, game launch or runtime acceptance occurred.
