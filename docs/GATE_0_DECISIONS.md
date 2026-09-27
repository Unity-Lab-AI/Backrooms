# Rimrooms - Async Industries: Gate 0 decisions

**Purpose:** record the product choices that must be fixed before any Rimrooms game code, XML Defs, source-specific content, or production art/audio is created. This is the owner decision sheet for the [master preparation TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md). Research and feasibility tasks that do not need an owner choice remain in that TODO.

## Decisions already supplied by the owner

These are treated as project direction from the conversation. A change must be recorded here and propagated to the canonical design documents.

- **Title:** Rimrooms - Async Industries.
- **Game/build target:** RimWorld 1.6.
- **Core premise:** begin from a small facility with limited resources; hire and train staff; build, power, calibrate, secure, and operate the machine gate; investigate, extract, study, contain, trade, sell, and expand.
- **Scenario set:** Async Industries facility first; Furniture & Knickknack Store breach and Lone Survivor as distinct selectable starts using shared campaign and coordinate systems. Later starts can include outposts, town distortions, and company crises.
- **Mod profile:** the dated 294-entry local server profile is the required research and integration target. It is not yet individually reviewed or compatibility-certified.
- **Multiplayer experience:** asynchronous cooperation through RimWorld Together; each player owns a separate facility/branch and can exchange resources, items, and technology and visit another player's facility. No live shared-map control is intended.
- **Space expansion:** Vanilla Gravship Expanded Chapters 1 and 2 are intended as a later company/space layer, not a replacement for gate exploration.
- **Creative references:** Kane Pixels' Backrooms series and the A24 Backrooms feature are required primary references. Wider Backrooms material is in scope for research; the exact canon layers used in shipped content still needs selection below.
- **Preparation rule:** finish the research, profile mapping, feature contracts, and Gate 0 decisions before starting implementation. Do not begin code while this gate is open.

## Owner choices still required

Reply with the option letter or provide a replacement. The suggested answer is a proposal, not an approval. If an option is accepted, record it in the decision log below and update the linked canonical documents.

### D1. First distribution target

- [ ] **A — Suggested:** private RimWorld Together test build first; consider public Steam Workshop release only after the named profile and multiplayer flows pass.
- [ ] **B:** public Steam Workshop release is the first distribution target; do not announce compatibility until validation is complete.
- [ ] **C:** private server use only; no public Workshop release planned.

### D2. Public identity, package identity, and versioning

Fill the exact values, or accept the proposal. The repository org is `Unity-Lab-AI`, but that does not by itself decide the public author name.

- Public author/display name: `____________________`
- Package ID / namespace: `____________________`
- Version policy: [ ] Suggested: semantic versions, `0.x` while pre-release and `1.0.0` at the first stable public release. [ ] Other: `____________________`

### D3. What the 294-mod profile means at launch

- [ ] **A — Suggested:** keep a Core-only solo/dev path; define the exact ordered 294-entry profile as the supported RWT co-op profile and require matching that profile to join that co-op server. Review every row before code, then implement native-feature support or a narrow adapter where justified.
- [ ] **B:** keep the 294 entries as a full test target, but require only RimWorld Core plus Harmony/RWT; every other profile mod stays optional for players.
- [ ] **C:** ship a Core package plus separate optional integration packages; do not define the 294 list as one required launch profile.

### D4. DLC support contract

- [ ] **A — Suggested:** Core-only campaign remains playable; Royalty, Ideology, Biotech, Anomaly, and Odyssey each add optional detected content. Validate the all-five local profile and test every DLC interaction identified by the feature map.
- [ ] **B:** require the full five-DLC set for the supported campaign.
- [ ] **C:** select a smaller explicit DLC support list: `____________________`.

### D5. Backrooms canon and adaptation depth

- [ ] **A — Suggested:** review the complete Kane Pixels series and A24 feature, plus clearly identified wider-canon sources; use those as the broad content reference pool and label source-derived versus original content in every feature record.
- [ ] **B:** use only the Kane Pixels continuity and A24 feature; leave wider community canon out of shipped content.
- [ ] **C:** treat all reviewed material as high-level inspiration and make nearly all named characters, events, dialogue, and storylines original.
- [ ] **D:** adapt specific named characters, locations, scenes, and equipment directly; list the exact elements to prioritize: `____________________`.

The owner's stated MIT/court-case rights premise is retained as an owner-provided assertion, not as a verified legal finding. Before distribution, Gate 0 still records the source and license/provenance for each borrowed or recreated name, text, design, image, sound, and other asset. This research check is not an invitation to silently narrow the requested creative scope.

### D6. How players exchange technology

- [ ] **A — Suggested:** exchange research as physical, tradeable Research Dossier items. The receiving branch studies/consumes a dossier locally; no global research state is assumed. This fits the stated trade/visit model and can be tested against RWT's actual item-transfer path.
- [ ] **B:** instantly share unlocked research between branches through a shared ledger, but only if the pinned RWT build exposes a supported extension point.
- [ ] **C:** support both transferable dossiers and direct shared unlocks when feasible.

The stated gameplay requirement is already clear: players should be able to share technology. The choice above is only the implementation contract; RWT feasibility remains a research/test task.

### D7. First-release language and standalone play

- [ ] **A — Suggested:** English player-facing text at first release; build every label through localization keys so translations can follow. Keep a Core-only solo development/play path, with RWT used for the co-op campaign.
- [ ] **B:** English only, with no localization structure required for the first release.
- [ ] **C:** launch with these languages: `____________________`; make RWT required for every supported mode.

### D8. Project code license

- [ ] **A — Suggested:** license original source code as MIT; record the art/audio license separately and never assume an outside asset is covered by the code license.
- [ ] **B:** license original source code as GPL-3.0-or-later.
- [ ] **C:** keep the code private/all-rights-reserved.
- [ ] **D:** use another license: `____________________`.

### D9. Audience and horror presentation

- [ ] **A — Suggested:** market it as mature psychological horror/management; include missing-person cases, hazardous exploration, containment, detention/interviews and difficult company decisions as gameplay systems, while presenting violence and harm through RimWorld-scale/stylized feedback rather than graphic cutscenes.
- [ ] **B:** keep it closer to broad-audience RimWorld presentation; threat, custody and injury outcomes are abstracted and low-detail.
- [ ] **C:** use a stronger horror presentation; define the desired limits for violence, body horror, captivity, and distressing events here: `____________________`.
- [ ] **D:** other audience/content target: `____________________`.

## Choices not delegated to the owner

These are execution work, not questions: identify the exact RimWorld/RWT/Harmony builds; inspect all 294 exact mod pages, installed metadata and available source/API; verify RWT transfer/visit/scenario/save behavior; review all 23 indexed videos and the full feature; complete the feature/mod/lore/style/file traceability map; record DLC and gravship dependencies; and produce reproducible evidence. They are tracked in [Phase 0 of the master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-0--pre-code-blockers-and-research).

## Decision log

| ID | Final answer | Date | Documents updated |
| --- | --- | --- | --- |
| D1 | Pending | — | — |
| D2 | Pending | — | — |
| D3 | Pending | — | — |
| D4 | Pending | — | — |
| D5 | Pending | — | — |
| D6 | Pending | — | — |
| D7 | Pending | — | — |
| D8 | Pending | — | — |
| D9 | Pending | — | — |
