# Company systems implementation wave

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Started:** 2026-09-28. **Status:** 0.3.0-dev source compiled and staged; full-mod implementation continues. Follow the [owner's instruction to continue building while testing is deferred](../GATE_0_DECISIONS.md#build-continuation-and-deferred-game-testing). No runtime gate is closed by this work.

## Task scope and ownership

| Work | Features and source contracts | Exclusive implementation scope | State/action/recovery |
| --- | --- | --- | --- |
| Voluntary applicants, hire and staff detail | RR-STA/RR-ECO/RR-UI; [personnel source task](PHASE_3_PERSONNEL_FACILITIES_TASK.md), Core row 4 `Ludeon.RimWorld` | Personnel/, Company/PersonnelServices.cs, UI/OperationsPersonnel.cs, personnel Defs/keyed XML; agent core_build_source_review | Saved branch-owned candidate holder, stable quotes and hire receipts, one ledger debit, same pawn arrival, native recruitment, payroll registration; retained interrupted hire and refund rules |
| Physical procurement | RR-ECO/RR-FAC/RR-UI; [procurement source task](PHASE_3_PROCUREMENT_TASK.md), Core row 4; OgreStack 157, storage 122/259 optional | Procurement/, UI/OperationsProcurement.cs, procurement Defs/keyed XML; agent gate0_readiness_audit | Saved order/quote and actual held cargo, one charge, bounded receiving, exact partial receipts and retained remainder; no virtual inventory |
| Physical facilities | RR-FAC/RR-STA/RR-UI; personnel task and [company roster](../CAMPAIGN_ROSTER_FREEZE.md) | Facilities/, UI/OperationsFacilities.cs, facilities keyed XML; lead | Read actual HQ buildings, bed categories and needs; cached view with revalidated inspection, no hidden room gates or changed needs |
| Approved original menu slideshow | RR-UI/RR-STYLE; [menu source review](PHASE_5_MENU_CONTROLLER_SOURCE.md), [original art candidates](PHASE_5_MENU_ART_PREPARATION.md), [style brief](../research/VISUAL_AUDIO_STYLE_BRIEF.md) | Presentation/, Core/RimroomsSettings.cs and RimroomsMod.cs, menu keyed XML and original menu image copies; agent edge_graph_audit | Top-left mod title/loaded version, user settings, quiet dwell/fade, reduced-motion still, native fallback/disable, respect other background owners; no campaign save ownership |
| Existing research-bench role | RR-FAC/RR-EVD/RR-UI; [laboratory implementation](PHASE_3_LABORATORY_REUSE_IMPLEMENTATION.md), Core row 4 | Investigation laboratory component/utility/workgiver, UI binding partial, keyed text; agent core_build_source_review, root integrates job/scenario | Explicit saved designation of actual SimpleResearchBench or HiTechResearchBench; native speed/power and work remain; no automatic capture of every bench |
| Native gameplay sound reuse | RR-STYLE/RR-GATE/RR-THREAT; [native audio implementation](PHASE_3_NATIVE_AUDIO_REUSE.md), Core row 4 | Audio/RimroomsAudio.cs, existing cue text, package archival/allowlist; lead | Existing Core cues referenced at runtime, original sound files outside package; text/mute/visibility preserved, no saved sound state |
| Existing physical evidence book | RR-EVD/RR-SPACE/RR-UI; [book implementation](PHASE_3_EVIDENCE_BOOK_REUSE_IMPLEMENTATION.md), Core row 4 | Evidence creation holder, dormant native-book comp, XML patch, company registration and recovery UI; agent core_build_source_review with lead recovery integration | Once-only native TextBook creation, deep-held unfinished original, quality/placement journal, actual item identity and no remint after loss |

The lead owns MainTabWindow_Operations.cs, shared campaign integration, package allowlist, version/build receipts, canonical documentation, Git and publication. Agents must not edit those files, run concurrent builds, launch the game or touch the owner's profile. Each agent returns changed paths, callable integration entry points, source evidence, remaining limits and checks actually performed. Optional-mod behavior is retained through native Core APIs; no optional assembly becomes required.

## Save and integration contract

Keep the existing campaign component as the only company ledger/payroll owner. New personnel/procurement GameComponents may own their bounded branch-local records and ThingOwner custody with explicit independent schema versions; they remain inactive without a valid campaign. Use original branch IDs and actual object references. Do not duplicate company money, replace normal Work/Assign/needs, or generate offers/orders during constructors, drawing or load initialization. Old schema-2 company saves acquire empty new components with no grants or charges. Unknown/corrupt new component states disable their actions and retain recoverable owned objects.

## Evidence and remaining work

### Implemented source routes

- [Personnel](PHASE_3_PERSONNEL_IMPLEMENTATION.md): native applicant inspection/hire/retry/refund/release, staff roles and payroll registration. A safely dismissed unavailable offer keeps its historical identity without touching a foreign pawn.
- [Procurement](PHASE_3_PROCUREMENT_IMPLEMENTATION.md): physical Core cargo, explicit supplier prices, exact ledger reconciliation, stockpile receiving, bounded partial delivery, rerouting and retained/archived history. Live stack limits govern creation and later splitting; no oversized OgreStack assumption is embedded.
- [Facilities](PHASE_3_FACILITIES_IMPLEMENTATION.md): cached HQ building/room/power/bed observations, staff needs and native inspection/Assign links.
- [Laboratory](PHASE_3_LABORATORY_REUSE_IMPLEMENTATION.md) and [evidence books](PHASE_3_EVIDENCE_BOOK_REUSE_IMPLEMENTATION.md): existing Core objects with explicit saved roles/custody.
- [Native audio](PHASE_3_NATIVE_AUDIO_REUSE.md), [menu controller](PHASE_5_MENU_IMPLEMENTATION.md) and [painted v2 menu art](PHASE_5_MENU_ART_V2.md): source/provenance and clear runtime boundaries.

The [scenario and door-network refinement](../SCENARIO_SETUP_AND_PORTAL_NETWORK.md) is the latest next-stage design input. This wave does not implement its three customized setup flows or the conversion to native portal doors. Existing custom gate/equipment/threat/terrain/start-kind content still requires the [replacement map](EXISTING_CONTENT_REPLACEMENT_MAP.md).

Planned files remain planned until present. Compile the integrated source only after agents finish; save actual compiler/package receipts. Runtime cases in the personnel/procurement plans, slideshow native-overlay/other-mod behavior, save/load, economy and full-profile acceptance remain deferred to an owner-launched disposable session. This wave does not complete the broad Phase 3 or Phase 5 checklist. The [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) continues through training, broader facility capabilities, procedural campaign, missions, research, containment, outposts, alternate starts, optional integrations and release.

The owner subsequently required existing gameplay content only. Personnel/procurement/facility code in this wave uses native pawns, items and buildings. Agent edge_graph_audit was redirected to the [complete replacement map](EXISTING_CONTENT_REPLACEMENT_MAP.md); its menu work resumed after the owner approved the original-background exception and required top-left mod title/current-version text. No gameplay asset creation is authorized.

## Integrated build checkpoint — 2026-09-28

- Command: `./tools/build.ps1 -NoRestore`; .NET SDK **9.0.308**, Release, C# 7.3, net472, pinned Core assembly **1.6.9676.17735**. Successful compile: **0 warnings, 0 errors**. The first integration attempt found namespace collisions and C# 7.3 local/conditional-expression errors; those were corrected before this recorded successful output.
- **63 C# source files**, **68 explicitly approved package files**. Package DLL SHA-256: `22DA7E237C79E8DABF5F5DCFE6049F283BCE001CCADB9D241FB41A950C1AAAF1`.
- [Compiler output](evidence/phase3-company-2026-09-28/build-output.txt), [package manifest](evidence/phase3-company-2026-09-28/package-manifest.json), [reference manifest](evidence/phase3-company-2026-09-28/reference-manifest.json), and [source hashes](evidence/phase3-company-2026-09-28/source-manifest.json).
- Staged through `./tools/stage-mod.ps1 -UpdateExisting` to the Local Mods directory read from RimSort. **All 68 copied hashes matched**; the prior installation was preserved in the local backup path recorded in the [staging receipt](evidence/phase3-company-2026-09-28/staging-receipt.json). No profile selection/order was changed and no game was launched.
- The saved-reference audit passed during integration: 422 Markdown files, 2,323 local link occurrences, 166 fragments, 294 mod rows/reviews, 3,234 workbook cells, 914 relationship records, 23 story records and zero open Gate 0 boxes. Later documentation additions require the final saved audit below; this is reference integrity only, not gameplay acceptance.

The package remains a private development checkpoint. It includes legacy/custom gameplay objects still awaiting native-provider conversion. No save/load, menu, procurement, hiring, profile, RWT or gameplay test is claimed. Continue the complete master TODO, starting with native-door/field-content replacement and the newly clarified scenario setup while owner-launched testing remains deferred.

Final saved-reference result: [document audit](evidence/phase3-company-2026-09-28/document-audit.json). This checks local links, recorded register agreement and existing Gate 0 boxes only; it starts no game and is not an implementation test.
