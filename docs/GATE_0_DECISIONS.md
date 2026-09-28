# Rimrooms - Async Industries: Gate 0 decisions

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Purpose:** record the product choices that control Rimrooms preparation and implementation. All recorded selections are binding project direction. Research and feasibility tasks that do not need an owner choice remain in the [master preparation TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

## Decisions already supplied by the owner

These are treated as project direction from the conversation. A change must be recorded here and propagated to the canonical design documents.

- **Title:** Rimrooms - Async Industries.
- **Game/build target:** RimWorld 1.6.
- **Core premise:** begin from a small facility with limited resources; hire and train staff; build, power, calibrate, secure, and operate the machine gate; investigate, extract, study, contain, trade, sell, and expand.
- **Scenario set:** Async Industries facility first; Furniture & Knickknack Store breach and Lone Survivor as distinct selectable starts using shared campaign and coordinate systems. Later starts can include outposts, town distortions, and company crises.
- **Mod profile:** the dated 294-entry local server profile is the required research and integration target. All 294 rows now have accepted source-fact reviews; that is not a runtime compatibility certificate.
- **Multiplayer experience:** asynchronous cooperation through RimWorld Together; each player owns a separate facility/branch and can exchange resources, items, and technology and visit another player's facility. No live shared-map control is intended.
- **Space expansion:** Vanilla Gravship Expanded Chapters 1 and 2 are intended as a later company/space layer, not a replacement for gate exploration.
- **Creative references:** Kane Pixels' Backrooms series and the A24 Backrooms feature are the selected references. Adapt indirectly; broader community canon is excluded from shipped content.
- **Preparation rule:** finish the research, profile mapping, feature contracts, and Gate 0 decisions before starting implementation. Do not begin code while this gate is open.

## Supplemental owner direction captured during preparation

These product requirements supplement D1–D9; they do not change those answers or create new owner decisions.

- **Company scale and economy:** the parent corporation operates at multi-trillion-dollar scale. Company contracts, discoveries, research, salvage, and services can reach millions or more when the buyer, deliverable, risk, and rights support that value; events do not pay a universal token amount just for happening. Company USD stays in an auditable branch ledger, separate from physical silver and goods. The colony still uses RimWorld's ordinary pawn work, growing, cooking, crafting, harvesting, research, storage, and hauling. Meals are physical food, not an automatic cash fee.
- **Capacity and logistics:** use the owner's selected 294-profile with OgreStack's default behavior as the planning baseline, without making OgreStack required or overriding its settings. One million physical silver is therefore modeled as 67 stacks under the published default small-volume multiplier, compared with 2,000 stacks at Core's 500-item limit. Runtime estimates must use the actual save's effective item limit, pawn carry, storage, and hauling throughput; account balances never spawn as silver.
- **Company interface:** the completed mod should remap RimWorld's menus, tabs, and campaign views into a company-first command layout for facilities, staff, research, the gate, expeditions, evidence, cases, contracts, finance, sites, and outposts. The first playable starts with Operations; the full layout grows from it while keeping underlying RimWorld actions accessible.
- **Main-menu showcase:** create an original Backrooms background rotation that previews the shipped scenarios and campaign systems, with readable menu controls, disable/reduced-motion behavior, fallback, and per-asset provenance. The source/API research is recorded in the [menu extension audit](research/MENU_BACKGROUND_EXTENSION_AUDIT.md); the actual slideshow implementation and images remain later work.
- **Profile-wide treatment:** all 294 installed profile entries are in scope for source review and interaction mapping. Use their native behavior, adapt a public extension point, add a narrow integration, or mark a row optional/no-touch/unsupported based on evidence. D3 remains controlling: only Core plus Harmony/RWT are required for co-op, while every other profile mod is optional. Do not copy or redistribute mod files.

## Scenario setup and doorway direction

On 2026-09-28 the owner reaffirmed three custom scenario openings, Prepare Carefully support for their starting people, and ordinary world-site choice for Async Industries. Portals must be existing doors recolored with a native aura, with different supported sizes and real connected batteries, generation, control/research equipment, upgrades, longer operating windows and saved-map recall. The inside start was proposed as configurable solo/group with automatic Backrooms placement until a reliable exit is discovered; the party/exit choices are awaiting the two grouped answers. See [the complete refinement](SCENARIO_SETUP_AND_PORTAL_NETWORK.md). This is continued build direction, not a new Gate 0 blocker. The lead is provisionally proceeding with configurable solo/group, automatic Backrooms entry and a fixed discovered exit after allowing time for answers; these defaults remain explicitly revisable, not recorded owner selections.

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

The owner's stated MIT/court-case rights premise is retained as an owner-provided assertion, not as a verified legal finding. The source/provenance register and feature-source routes are part of Gate 0; complete per-asset source and license records for any future borrowed or recreated name, text, design, image, sound, or other asset before distribution. Asset creation and release permissions are later production/release work, not an open Gate 0 item. This research check is not an invitation to silently narrow the requested creative scope.

### D6. How players exchange technology

- [x] **A — Selected:** exchange research as physical, tradeable Research Dossier items. The receiving branch studies/consumes a dossier locally; no global research state is assumed. This fits the stated trade/visit model and can be tested against RWT's actual item-transfer path.
- [x] **B — Selected:** also share unlocked research through a shared ledger, but only if the pinned RWT build exposes a supported extension point and testing confirms safe synchronization.
- [ ] **C:** support both transferable dossiers and direct shared unlocks when feasible.

**Combined owner answer:** support both tradeable dossiers and direct shared research when RWT has a supported extension point and synchronization is demonstrated safe. If shared-ledger synchronization is unsupported or unsafe, retain dossier exchange and leave direct sharing disabled. Gate 0 records the source/configuration research and prepares the acceptance plan; run multiplayer workflow tests only after a Rimrooms build exists.

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

## Owner direction on publisher-warned mods

- **Questionable Ethics Enhanced (profile row 182):** its publisher warns that RimWorld multiplayer will not work properly. The owner replied on 2026-09-27, “use it it'll be fine.” Record the mod as optional and include it in the RWT candidate test profile; do not exclude it solely because of the warning. This direction is not a compatibility result or a promise that desyncs will not occur. See the [row 182 review](research/reviews/mods/2850854272-Mlie.QuestionableEthicsEnhanced.md) and [interaction check](research/PRIORITY_PROFILE_INTERACTIONS.md).
- **Medical Dissection (profile row 274):** its publisher warns that multiplayer is unsupported and may desynchronize; the local manifest declares no incompatibility. The owner gave the same direction on 2026-09-27: keep it in the optional 294-entry candidate test profile despite the warning. Do not advertise it as RWT-compatible until the exact test is recorded. See the [row 274 review](research/reviews/mods/1328216966-Heremeus.MedicalDissection.md) and [interaction check](research/PRIORITY_PROFILE_INTERACTIONS.md).
- **Scope:** both mods remain optional under D3. The owner wants them included in co-op feasibility testing; their publisher warnings remain in the evidence, and no technical outcome is assumed.

## Research-method clarification from the owner

On 2026-09-27, the owner approved fan-made episode summaries and movie plot summaries as the first-pass story sources. A fan-maintained movie summary is now recorded; the chaptered video recap remains optional. Full video or feature viewing is not required by default. Keep fan interpretation labeled, keep the series and film separate, and only go back to the official source when a detail remains unclear and matters to a planned feature. See [`research/FAN_SUMMARY_GUIDE.md`](research/FAN_SUMMARY_GUIDE.md). This changes the research method, not the selected story scope in D5.

## Choices not delegated to the owner

These are execution work, not owner questions: the exact RimWorld/RWT/Harmony builds, 294 source reviews, 23-entry fan-summary notes, separate first-pass fan movie note, supplemental-clip scope, feature/mod/lore/style/file traceability, DLC and gravship dependencies, source maps, and post-build acceptance plans are recorded. Runtime RWT transfer/visit/scenario/save behavior and reproducible gameplay evidence are deliberately scheduled only after a Rimrooms build exists. Direct viewing is needed only for unresolved, design-critical story details. Gate 0 completion and the Phase 1+ follow-up work are tracked in [the master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

## Build continuation and deferred game testing

**Owner reaffirmation:** the objective is completion of **all TODO work for Rimrooms - Async Industries**. The work is active. A stale application goal-status label is not a project gate and does not prevent implementation. Preserve the owner's RimSort launch control and pending runtime-evidence boundaries.

**Owner direction, 2026-09-28:** after reviewing the unfinished full-mod TODO, the owner deferred the first game test and explicitly instructed work to continue until the full mod is built. Continue source/content implementation across the planned phases without making an owner-launched Gate 2 run a prerequisite for further coding. Keep the existing dependency order between systems. Runtime gates remain pending acceptance requirements; this changes development sequencing, not evidence standards, feature scope or release criteria. Only the owner launches through RimSort. Do not request another launch merely to resume implementation. The opening-duration clarification remains unanswered; preserve the accepted value until directed otherwise.

## Decision log

**Latest content decision:** the owner's [existing-content-only gameplay policy](CONTENT_REUSE_POLICY.md) supersedes prior original gameplay asset/item/bench creation plans. Repurpose existing Core/DLC/profile definitions and assets in place; implement new company/generation/quest logic around them. Prior 0.2.0 custom physical content is a replacement/migration task. The owner confirmed original RimWorld-style Backrooms main-menu images as the sole visual exception, with the exact mod title and current version shown beside native top-left version information.

| ID | Final answer | Date | Documents updated |
| --- | --- | --- | --- |
| D1 | A — private RWT test first; public Workshop only after validation is considered | 2026-09-27 | TODO, roadmap, release plan |
| D2 | Exact title; author/publisher metadata `Operator`; package ID `UnityLabAI.RimroomsAsyncIndustries`; namespace `RimroomsAsyncIndustries`; semantic versions | 2026-09-27 | TODO, About.xml/package metadata, technical architecture |
| D3 | B — all 294 are the research/test target; only Core + Harmony/RWT required; other profile mods optional. Owner says test rows 182 and 274 in the co-op candidate despite publisher warnings; no support claim before results. | 2026-09-27 | TODO, compatibility, mod plan, technical architecture, interaction map |
| D4 | A — all five DLC optional; Core-only campaign; validate all-five profile | 2026-09-27 | TODO, compatibility, scenario, mod plan, systems catalog |
| D5 | B + customized D — Kane Pixels and A24 only; indirect use of canon/lore/themes/styles | 2026-09-27 | TODO, source register, research, universe adaptation, feature map |
| D6 | A + B — tradeable dossiers plus shared research ledger only if supported and safely tested | 2026-09-27 | TODO, technical architecture, mod plan, roadmap |
| D7 | A — English first/localization-ready; solo Core path; RWT co-op | 2026-09-27 | TODO, technical architecture, build plan |
| D8 | A — MIT for original source code; assets tracked/licensed separately | 2026-09-27 | TODO, provenance plan, package checklist |
| D9 | A + customized C — mature psychological horror; strongest presentation the game/profile supports | 2026-09-27 | TODO, game design, style and content briefs |
| S1 — supplemental content scope | B — freeze broad later threat/anomaly families; defer the five names in the roster to later content reviews. The names are not approved roadmap or release commitments. | 2026-09-28 | TODO, campaign roster, content catalog |

**S1 detail:** the owner selected option B for the later threat roster. Freeze the broad threat/anomaly families only; treat the five named entries in `CAMPAIGN_ROSTER_FREEZE.md` as deferred sketches. Revisit a named threat for owner approval and complete its feature sheet before adding it to a later implementation scope. This does not alter the authored first-slice route distortion or hostile encounter.
