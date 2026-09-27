# Rimrooms - Async Industries: Gate 0 decisions

**Purpose:** record the product choices that control Rimrooms preparation and implementation. All recorded selections are binding project direction. Research and feasibility tasks that do not need an owner choice remain in the [master preparation TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

## Decisions already supplied by the owner

These are treated as project direction from the conversation. A change must be recorded here and propagated to the canonical design documents.

- **Title:** Rimrooms - Async Industries.
- **Game/build target:** RimWorld 1.6.
- **Core premise:** begin from a small facility with limited resources; hire and train staff; build, power, calibrate, secure, and operate the machine gate; investigate, extract, study, contain, trade, sell, and expand.
- **Scenario set:** Async Industries facility first; Furniture & Knickknack Store breach and Lone Survivor as distinct selectable starts using shared campaign and coordinate systems. Later starts can include outposts, town distortions, and company crises.
- **Mod profile:** the dated 294-entry local server profile is the required research and integration target. It is not yet individually reviewed or compatibility-certified.
- **Multiplayer experience:** asynchronous cooperation through RimWorld Together; each player owns a separate facility/branch and can exchange resources, items, and technology and visit another player's facility. No live shared-map control is intended.
- **Space expansion:** Vanilla Gravship Expanded Chapters 1 and 2 are intended as a later company/space layer, not a replacement for gate exploration.
- **Creative references:** Kane Pixels' Backrooms series and the A24 Backrooms feature are the selected references. Adapt indirectly; broader community canon is excluded from shipped content.
- **Preparation rule:** finish the research, profile mapping, feature contracts, and Gate 0 decisions before starting implementation. Do not begin code while this gate is open.

## Owner choices and recorded answers

The marked boxes below are recorded as owner selections. Where multiple compatible options are marked, they are combined and explained in the decision log. D2's proposal is accepted. The suggested answer is a proposal unless it is marked by the owner.

### D1. First distribution target

- [x] **A — Selected:** private RimWorld Together test build first; consider public Steam Workshop release only after the named profile and multiplayer flows pass.
- [ ] **B:** public Steam Workshop release is the first distribution target; do not announce compatibility until validation is complete.
- [ ] **C:** private server use only; no public Workshop release planned.

### D2. Public identity, package identity, and versioning

**Proposal accepted with the owner's correction.** Keep the displayed mod title exactly **Rimrooms - Async Industries**. Set the author/publisher value to `Operator`; the MIT license does not supply or change that value.

- Displayed mod title: `Rimrooms - Async Industries`
- Public author/publisher metadata: `Operator`
- RimWorld package ID: `UnityLabAI.RimroomsAsyncIndustries`
- Internal C# namespace: `RimroomsAsyncIndustries`
- Version policy: semantic versions; `0.x` while pre-release and `1.0.0` at the first stable public release.

### D3. What the 294-mod profile means at launch

- [ ] **A — Suggested:** keep a Core-only solo/dev path; define the exact ordered 294-entry profile as the supported RWT co-op profile and require matching that profile to join that co-op server. Review every row before code, then implement native-feature support or a narrow adapter where justified.
- [x] **B — Selected:** keep the 294 entries as a full test target, but require only RimWorld Core plus Harmony/RWT; every other profile mod stays optional for players.
- [ ] **C:** ship a Core package plus separate optional integration packages; do not define the 294 list as one required launch profile.

### D4. DLC support contract

- [x] **A — Selected:** Core-only campaign remains playable; Royalty, Ideology, Biotech, Anomaly, and Odyssey each add optional detected content. Validate the all-five local profile and test every DLC interaction identified by the feature map.
- [ ] **B:** require the full five-DLC set for the supported campaign.
- [ ] **C:** select a smaller explicit DLC support list: `____________________`.

### D5. Backrooms canon and adaptation depth

- [ ] **A — Suggested:** review the complete Kane Pixels series and A24 feature, plus clearly identified wider-canon sources; use those as the broad content reference pool and label source-derived versus original content in every feature record.
- [x] **B — Selected:** use only the Kane Pixels continuity and A24 feature; leave wider community canon out of shipped content.
- [ ] **C:** treat all reviewed material as high-level inspiration and make nearly all named characters, events, dialogue, and storylines original.
- [x] **D — Selected with owner clarification:** adapt the canon, lore, themes, and styles indirectly; do not directly recreate specific scenes or characters based on this selection.

The owner's stated MIT/court-case rights premise is retained as an owner-provided assertion, not as a verified legal finding. Before distribution, Gate 0 still records the source and license/provenance for each borrowed or recreated name, text, design, image, sound, and other asset. This research check is not an invitation to silently narrow the requested creative scope.

### D6. How players exchange technology

- [x] **A — Selected:** exchange research as physical, tradeable Research Dossier items. The receiving branch studies/consumes a dossier locally; no global research state is assumed. This fits the stated trade/visit model and can be tested against RWT's actual item-transfer path.
- [x] **B — Selected:** also share unlocked research through a shared ledger, but only if the pinned RWT build exposes a supported extension point and testing confirms safe synchronization.
- [ ] **C:** support both transferable dossiers and direct shared unlocks when feasible.

**Combined owner answer:** support both tradeable dossiers and direct shared research when RWT has a supported, tested extension point. If shared-ledger synchronization is unsupported or unsafe, retain dossier exchange and leave direct sharing disabled. RWT feasibility remains a Gate 0 research/test task.

### D7. First-release language and standalone play

- [x] **A — Selected:** English player-facing text at first release; build every label through localization keys so translations can follow. Keep a Core-only solo development/play path, with RWT used for the co-op campaign.
- [ ] **B:** English only, with no localization structure required for the first release.
- [ ] **C:** launch with these languages: `____________________`; make RWT required for every supported mode.

### D8. Project code license

- [x] **A — Selected:** license original source code as MIT; record the art/audio license separately and never assume an outside asset is covered by the code license.
- [ ] **B:** license original source code as GPL-3.0-or-later.
- [ ] **C:** keep the code private/all-rights-reserved.
- [ ] **D:** use another license: `____________________`.

### D9. Audience and horror presentation

- [x] **A — Selected:** mature psychological horror/management, including missing-person cases, hazardous exploration, containment, detention/interviews, and difficult company decisions; present effects through RimWorld-scale game systems.
- [ ] **B:** keep it closer to broad-audience RimWorld presentation; threat, custody and injury outcomes are abstracted and low-detail.
- [x] **C — Selected with owner clarification:** use the strongest horror, body-horror, captivity, and distressing-event presentation the game and selected mod profile can support, while respecting their technical limits.
- [ ] **D:** other audience/content target: `____________________`.

**Combined owner answer:** use the mature psychological-horror management direction in A and push the horror presentation to the limit expressed in C, within the capabilities of RimWorld and the selected mod profile.

## Research-method clarification from the owner

On 2026-09-27, the owner approved fan-made episode summaries and movie plot summaries as the first-pass story sources. A fan-maintained movie summary is now recorded; the chaptered video recap remains optional. Full video or feature viewing is not required by default. Keep fan interpretation labeled, keep the series and film separate, and only go back to the official source when a detail remains unclear and matters to a planned feature. See [`research/FAN_SUMMARY_GUIDE.md`](research/FAN_SUMMARY_GUIDE.md). This changes the research method, not the selected story scope in D5.

## Choices not delegated to the owner

These are execution work, not questions: identify the exact RimWorld/RWT/Harmony builds; inspect all 294 exact mod pages and relevant installed metadata/source; verify required RWT transfer/visit/scenario/save behavior; retain the completed 23-entry fan-summary notes and separate first-pass fan movie note; preserve the documented supplemental-clip scope boundary; complete the feature/mod/lore/style/file traceability map; record DLC and gravship dependencies; and produce reproducible evidence. Direct viewing is needed only for unresolved, design-critical story details. They are tracked in [Phase 0 of the master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-0--pre-code-blockers-and-research).

## Decision log

| ID | Final answer | Date | Documents updated |
| --- | --- | --- | --- |
| D1 | A — private RWT test first; public Workshop only after validation is considered | 2026-09-27 | TODO, roadmap, release plan |
| D2 | Exact title; author field unset; package ID proposal `UnityLabAI.RimroomsAsyncIndustries`; internal namespace `RimroomsAsyncIndustries`; semantic versions | 2026-09-27 | TODO, About.xml/package metadata, technical architecture |
| D3 | B — all 294 are the research/test target; only Core + Harmony/RWT required; other profile mods optional | 2026-09-27 | TODO, compatibility, mod plan, technical architecture |
| D4 | A — all five DLC optional; Core-only campaign; validate all-five profile | 2026-09-27 | TODO, compatibility, scenario, mod plan, systems catalog |
| D5 | B + customized D — Kane Pixels and A24 only; indirect use of canon/lore/themes/styles | 2026-09-27 | TODO, source register, research, universe adaptation, feature map |
| D6 | A + B — tradeable dossiers plus shared research ledger only if supported and safely tested | 2026-09-27 | TODO, technical architecture, mod plan, roadmap |
| D7 | A — English first/localization-ready; solo Core path; RWT co-op | 2026-09-27 | TODO, technical architecture, build plan |
| D8 | A — MIT for original source code; assets tracked/licensed separately | 2026-09-27 | TODO, provenance plan, package checklist |
| D9 | A + customized C — mature psychological horror; strongest presentation the game/profile supports | 2026-09-27 | TODO, game design, style and content briefs |
