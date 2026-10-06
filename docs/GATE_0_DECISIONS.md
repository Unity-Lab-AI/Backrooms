# Rimrooms - Async Industries: Gate 0 decisions

> **This file is the authority on owner decisions, and decisions change.** Read the
> [decision log](#decision-log) rather than a remembered answer: **D1 changed 2026-09-29** (public
> Workshop is the first distribution target) and **D3 and D4 changed 2026-10-01** (the five
> expansions and the collection are declared requirements). The ballots in the sections below keep
> their original wording with a supersession note, because a decision record that is edited to
> match the present loses the thing it exists to hold.

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

## Completion tracking, regression containment and publication cadence

### Gate traversal, who may cross, and escalation pacing

**Owner clarification, 2026-09-28.** People and monstrosities further in must not all run for a gate to exit or attack when it opens, and must not cross a machine door or a natural portal; they stay in the Backrooms. They reach the near side only when the player uses ordinary game mechanics, pawn controls and normal pawn tasks to carry things back, and a pawn can carry essentially anything found — furniture, production equipment, resources, and people and monstrosities themselves. Nothing on the far side may rush a gate as soon as it connects; things must get crazier, but not all at once, with balance across the whole design.

The owner also fixed the vocabulary: **gate, gates, machine door and portal all mean the same thing**; only the connection kind (laboratory versus permanently open natural) differs. And **all three starts — company, solo-or-group inside, and furniture store — can eventually have multiple gates**, so no design or code may assume one gate per branch, map or coordinate.

Recorded in full, with the source chokepoint that enforces it, in [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side). This does not approve any previously deferred named threat, and it does not change the asynchronous RimWorld Together boundary.

### Connected colony travel, permanent natural portals and procedural inhabitants

The owner clarified that open laboratory/natural portals must unify local-branch work, labor and physical material access across maps. Pawns cross freely to carry materials and perform jobs on either side; mandatory expedition manifests and separate job pools are superseded. Natural portals stay permanently open. Coordinates select persistent seeds/saved spaces; advancement enables recall and increasingly complex/dangerous procedural architecture, events and people in native mental/health/life states, with rare monstrosities. The [binding implementation contract and backlog](CONNECTED_COLONY_PORTALS.md) records the full direction. This requires substantial new cross-map job/path/reservation work; the existing source does not prove it implemented. It does not change the separate-player asynchronous RWT boundary or approve previously deferred named threat sketches.

On 2026-09-28 the owner required completed work to be checked in the TODO with evidence and explicit regression containment while extending existing implementation. Follow [REGRESSION_CONTAINMENT.md](REGRESSION_CONTAINMENT.md). The owner also reaffirmed both remote cascades but requested publication only at meaningful completed milestones, not every edit. Batch code, contracts, checked tasks and evidence before the cascade. The owner clarified that every publication must include all current project changes, with no separate unpublished batch. Finish and integrate active work first; verify the final remote refs in tool output without creating a new local-only receipt. Existing signed-in browser access remains available, but verify the actual Git transport result.

## Owner choices and recorded answers

The marked boxes below are recorded as owner selections. Where multiple compatible options are marked, they are combined and explained in the decision log. D2's proposal is accepted. The suggested answer is a proposal unless it is marked by the owner.

### D1. First distribution target

**Changed by the owner on 2026-09-29. B is now the selection; A is superseded.** The original answer was recorded 2026-09-27, before any of the mod existed. See [the superseding direction](#d1-superseded-2026-09-29--public-workshop-is-the-first-distribution-target) below for the owner's verbatim words and what the change costs.

- [ ] ~~**A — selected 2026-09-27, superseded 2026-09-29:** private RimWorld Together test build first; consider public Steam Workshop release only after the named profile and multiplayer flows pass.~~
- [x] **B — Selected 2026-09-29:** public Steam Workshop release is the first distribution target; do not announce compatibility until validation is complete.
- [ ] **C:** private server use only; no public Workshop release planned.

#### D1 superseded 2026-09-29 — public Workshop is the first distribution target

**Verbatim owner direction (2026-09-29), answering the M6 release question:**

> *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*

Option 3 as presented was *"Public Workshop directly once complete — skip the private-prototype stage."* The owner's reason is the load-bearing half and is recorded because it answers the objection that was put to them: the risk raised against B was that first real-world profile validation would happen in public, against other players' saves. **There are no other players' saves.** Nothing has shipped, there is no installed base, and there is therefore no save to break. The owner's model is publish, then iterate in public — *"we just publish it all and update it as we go fixing bugs"*.

Consequences, propagated in the same change:

- The private RWT prototype stage is **no longer a release prerequisite**. It remains available as a test route and the [RWT run sheet](research/RWT_BASELINE_TEST_PLAN.md) and [RimBridgeServer harness](research/RIMBRIDGE_TEST_HARNESS.md) are unaffected.
- **M6's exit condition changes.** It previously read "private RWT prototype passes the Core-only solo path and the pinned co-op tests". It is now the solo path passing against the declared profile, with co-op validation no longer gating the first publication.
- **The no-compatibility-claim rule survives intact and is now the main protection.** B's own text — *"do not announce compatibility until validation is complete"* — stays binding. Publishing early makes this stricter, not looser. **And the D3/D4 change on 2026-10-01 narrowed what the mod page may say even further:** it may state what the package *declares as requirements*, read from `About.xml`, and it may state that the solo loop is reachable on Core content. It must not claim that any declared row has been **validated together** — not a profile row, not a DLC interaction, not RWT co-op — until that row has a recorded result. Declaring a dependency is a requirement, never evidence of compatibility, and conflating the two is exactly the claim this rule exists to stop. 200 of the dispositions are still provisional.
- **Update-and-fix becomes a supported path rather than an afterthought.** Save migration stops being a release-day checkbox and becomes an ongoing obligation from the first published version, since from publication onward there *are* other people's saves. [`SAVE_MIGRATION_POLICY.md`](SAVE_MIGRATION_POLICY.md) owns that, and the version policy in D2 is unchanged: `0.x` while pre-release, `1.0.0` at the first stable public release.

This changes the release gate only. It does not change evidence standards, feature scope, the existing-content rule, or the rule that only the owner launches the game.

### D2. Public identity, package identity, and versioning

**Proposal accepted with the owner's correction.** Keep the displayed mod title exactly **Rimrooms - Async Industries**. Set the author/publisher value to `Operator`; the MIT license does not supply or change that value.

- Displayed mod title: `Rimrooms - Async Industries`
- Public author/publisher metadata: `Operator`
- RimWorld package ID: `Rimrooms.AsyncIndustries`
- Internal C# namespace: `RimroomsAsyncIndustries`
- Version policy: semantic versions; `0.x` while pre-release and `1.0.0` at the first stable public release.

### D3. What the 294-mod profile means at launch

- [ ] **A — Suggested, not selected.** *(Worth noting in hindsight: this unselected option was the closest of the three to where the project actually landed on 2026-10-01, since it treated the exact ordered profile as a thing to match rather than a loose test target.)* Keep a Core-only solo/dev path (that clause superseded 2026-10-01); define the exact ordered 294-entry profile as the supported RWT co-op profile and require matching that profile to join that co-op server. Review every row before code, then implement native-feature support or a narrow adapter where justified.
- [x] **B — Selected, then SUPERSEDED 2026-10-01:** keep the 294 entries as a full test target, but require only RimWorld Core plus Harmony/RWT; every other profile mod stays optional for players. *(Original wording kept. The owner has since made every collection member a declared requirement — see the D3 row in the [decision log](#decision-log).)*
- [ ] **C:** ship a Core package plus separate optional integration packages; do not define the 294 list as one required launch profile.

### D4. DLC support contract

- [x] **A — Selected, then SUPERSEDED 2026-10-01:** Core-only campaign remains playable; Royalty, Ideology, Biotech, Anomaly, and Odyssey each add optional detected content. Validate the all-five local profile and test every DLC interaction identified by the feature map. *(Original wording kept. All five are now declared requirements — see the D4 row in the [decision log](#decision-log). The all-five validation and the per-interaction tests still stand.)*
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

- [x] **A — Selected:** English player-facing text at first release; build every label through localization keys so translations can follow. Keep a Core-only solo development/play path (that clause superseded 2026-10-01), with RWT used for the co-op campaign. *(The language half stands unchanged. The dependency clause was superseded on 2026-10-01 by the D3 and D4 changes: the solo path must still work on Core content, as degradation rather than as a supported configuration.)*
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

**Latest content decision, 2026-10-06: the existing-content-only policy is REVERSED IN PART.** The owner asked *"are we making our own items and benches and gates? becasue if so i fucking love it!"* and chose a full reversal, adding *"remember things rotate"*. Original gameplay art, audio, items, benches and terrain ship again. **What did not reverse:** reuse stays the default, no door def is ever cloned, and original content is added beside every reuse binding so a branch that builds none of it still works. The paragraph below is the 2026-09-28 decision it supersedes, kept because every retirement record cites it.

**Superseded content decision (2026-09-28):** the owner's [existing-content-only gameplay policy](CONTENT_REUSE_POLICY.md) supersedes prior original gameplay asset/item/bench creation plans. Repurpose existing Core/DLC/profile definitions and assets in place; implement new company/generation/quest logic around them. Prior 0.2.0 custom physical content is a replacement/migration task. The owner confirmed original RimWorld-style Backrooms main-menu images as the sole visual exception, with the exact mod title and current version shown beside native top-left version information.

| ID | Final answer | Date | Documents updated |
| --- | --- | --- | --- |
| D1 | **B — public Steam Workshop is the first distribution target; do not announce compatibility until validation is complete.** Changed by the owner 2026-09-29: *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*. Supersedes A (private RWT test first), recorded 2026-09-27 before the mod existed. The private RWT prototype is no longer a release prerequisite; the no-compatibility-claim rule is now the main protection. | 2026-09-27, **changed 2026-09-29** | TODO, roadmap, release plan, ARCHITECTURE, SKILL_TREE, AGENTS, CONTRIBUTING |
| D2 | Exact title; author/publisher metadata `Operator`; package ID `Rimrooms.AsyncIndustries`; namespace `RimroomsAsyncIndustries`; semantic versions | 2026-09-27 | TODO, About.xml/package metadata, technical architecture |
| D3 | **SUPERSEDED BY THE OWNER 2026-10-03: the package declares no hard dependencies at all.** *"and something i dont like that is going to take major major work and should be added to the todo : rework mod to not need any depeancie mods"*, and the same day *"and im reiterating the fact that we need to fix the depancy list so that its accurate to what is required and we hope to have the mod as a complete stand alone"*. `About.xml`'s `modDependencies` block is gone as of 0.12.86-dev; **all 293 entries were already in `loadAfter`**, so the load order is unchanged and only the requirement wall went. **The earlier reading is kept below rather than deleted.** ~~CHANGED by the owner 2026-10-01: every mod in the collection is a hard dependency.~~ *"there are alot more depeandacies than just the DLC we have alkinds of mods in the 274 mod list WE ARE USING ALL OF THEM!!!!"*. `About.xml` declares the collection plus the five expansions, each with a display name and a link, and every one also as a load-order constraint. **Read the count from `About.xml`, never from here** — this row said *289 mods* and went stale within two days, when attach-only QA tooling was excluded by name at 0.12.79-dev because declaring a debug server as a player requirement tells a player something false. Supersedes B (all 294 are the research/test target; only Core + Harmony/RWT required; other profile mods optional), recorded 2026-09-27. | 2026-09-27, **changed 2026-10-01** | About.xml, compatibility, mod plan, technical architecture, the wiki |
| D4 | **SUPERSEDED BY THE OWNER 2026-10-03, by the same direction as D3: the five expansions are not declared requirements either.** They came out of `modDependencies` with the other 288 and remain in `loadAfter`. This returns the five to the position D4 held when it was first recorded on 2026-09-27 — *"Core-only campaign; all five DLC optional detected content"* — which the 2026-10-01 amendment had reversed. **The graceful guards still stay**, and the conditional-layer work in Major M4 is what makes declaring nothing honest rather than merely quiet. **The earlier reading is kept below rather than deleted.** ~~CHANGED by the owner 2026-10-01: all five expansions are hard dependencies.~~ *"the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*. Supersedes A (all five DLC optional; a Core-only campaign, now retired), recorded 2026-09-27. **The graceful guards stay** — the owner chose to declare the requirement and still look content up by name, so a player who ignores the warning degrades rather than crashes. | 2026-09-27, **changed 2026-10-01** | About.xml, compatibility, scenario, mod plan, systems catalog, the wiki |
| D5 | B + customized D — Kane Pixels and A24 only; indirect use of canon/lore/themes/styles | 2026-09-27 | TODO, source register, research, universe adaptation, feature map |
| D6 | A + B — tradeable dossiers plus shared research ledger only if supported and safely tested | 2026-09-27 | TODO, technical architecture, mod plan, roadmap |
| D7 | A — English first/localization-ready; solo Core path; RWT co-op | 2026-09-27 | TODO, technical architecture, build plan |
| D8 | A — MIT for original source code; assets tracked/licensed separately | 2026-09-27 | TODO, provenance plan, package checklist |
| D9 | A + customized C — mature psychological horror; strongest presentation the game/profile supports | 2026-09-27 | TODO, game design, style and content briefs |
| S1 — supplemental content scope | B — freeze broad later threat/anomaly families; defer the five names in the roster to later content reviews. The names are not approved roadmap or release commitments. | 2026-09-28 | TODO, campaign roster, content catalog |

**S1 detail:** the owner selected option B for the later threat roster. Freeze the broad threat/anomaly families only; treat the five named entries in `CAMPAIGN_ROSTER_FREEZE.md` as deferred sketches. Revisit a named threat for owner approval and complete its feature sheet before adding it to a later implementation scope. This does not alter the authored first-slice route distortion or hostile encounter.


## Owner decisions — 2026-09-28 — gate duration, scenario parity, company identity

Recorded verbatim, then their consequences. Implemented in 0.5.4-dev; record: [`implementation/GATE_DURATION_AND_COMPANY_NAMING.md`](implementation/GATE_DURATION_AND_COMPANY_NAMING.md).

> on gate duration question you should have the first opening be like 30 minutes of real time not game time there has to be time to acually do shit and it only greatly increases from there once u can re call seeds and better tech and levels to being able to open it indefintality at higherr tech and research and staff and power supplies

> but remember natural portals like in the not corporation secerio stay open indefinately as the player doesnt have a way to build a lab portal of their own yet

> hold up every scerio gets the same tech tree to research so each scernioro will be able to build a full corporation if they want

> and name it their own

**Decided, and binding:**

1. **Laboratory duration is a ladder, measured in real time at normal speed.** First opening 108,000 ticks ≈ 30 real minutes. Each earned tier multiplies it. The top of the ladder removes the countdown entirely. The previously accepted 833 ticks is superseded for portal sessions and retained only for legacy expeditions.
2. **Indefinite means "while supported".** Power, operator and energy are still required every tick. This is the mechanism, not a description: running the energy supply dry ends a sustained opening exactly as cutting power does.
3. **Duration advances on completed research, never on spendable insight.** Insight is a currency that is consumed; gating duration on it would have made advancement reduce capability.
4. **Natural gates are permanently open and must stay so.** No timer, operator, power, mission or close command may ever apply to a natural connection. The non-corporation starts depend on this, because they begin with no way to build a laboratory gate.
5. **One research tree for every scenario.** No research, project, duration or capability rule may be gated on scenario identity. Every start must be able to reach a self-built laboratory gate and a full company. M3's tree must be authored as a single tree available to all starts.
6. **Every company is named by its player, on every start.** The scenario supplies a suggestion only. The name is saved on the branch and renameable at any time.

**Also decided the same day, closing two Gate 0 questions:**

7. **Inside start party:** configurable — solo or a small group, the player's choice.
8. **Inside start first exit:** **the player chooses the destination settlement.** This supersedes the earlier provisional assumption of a fixed discovered destination.

**Also directed:** continue building and defer the first in-game validation pass; build travel-to-work intents next.

---

## Owner decisions — 2026-09-28 — the universe period and its factions

Recorded verbatim, then their consequences. Captured in `TODO.md` as ten rows, one per item in the owner's list. The faction layer itself is queued after the remaining cross-map work families by the owner's own sequencing decision; the rows and that reason are in [`DEFERRED.md`](DEFERRED.md) under M3.

> and i havent talked about it but this is 1990's when this all starts and the factions should be the factions of the universe, so US government, other corporations trying to get propietary tech, ex employes disgruntleed, high tech theives, corporate spys and sbaatosh, concerned citizens.. and anything other type of factions along these lines that will increses the backrromms universe feeling as all this needs to be defgault set in the game settup for the differernt scenerios tailored to their scenrerio

**Decided, and binding:**

7. **The campaign opens in the 1990s.** This is the period for faction framing, naming and in-world language across every scenario.
8. **The world's factions are the universe's own**, not RimWorld's default rimworld factions: US government, rival corporations after proprietary technology, disgruntled ex-employees, high-tech thieves, corporate espionage and sabotage, concerned citizens, and further factions in the same vein wherever they increase the Backrooms universe feeling.
9. **Factions are authored as new `FactionDef`s that reuse existing pawn kinds.** A `FactionDef` is world configuration, not a physical gameplay Def, so it is inside [`CONTENT_REUSE_POLICY.md`](CONTENT_REUSE_POLICY.md). Each faction's `pawnGroupMakers` point at existing Core or profile `PawnKindDef`s, and faction icons reuse existing icon paths. **No new `PawnKindDef`, no new texture, no new item** — which is what keeps this layer clear of M2's removal of the five `RR_*Staff` PawnKinds. A new pawn kind here would reopen exactly the category M2 is deleting and would need an explicit policy amendment first.
10. **Every faction starts neutral.** Hostility is earned from what the company actually does, driven by the same saved observable causes as the bounded escalation ladder rather than by a second, unrelated hostility system. No faction is a raider on tick one.
11. **The 1990s also constrains starting grants.** Scenario starting equipment and buildings are period-plausible. Research is **not** period-gated, because decision 5 above makes one full tree available to every start and a period-gated tree would dead-end progression. The period shapes where a start begins, never where it can end up.
12. **Faction setup is default-set per scenario, tailored to that scenario**, and must be threaded through the existing versioned start contract (`RimroomsStartDef` → `BranchStartRequest` → `InitializeBranch`). It may **not** be a scenario-identity branch in code, which decision 5 already forbids for research and capability rules.

**Sequencing decided the same day:** finish the remaining cross-map work families first — bills and unfinished work, research, tending across a gate, food, rest — then author the faction and period layer as one clean content checkpoint.

---

## Owner decisions — 2026-09-28 — nothing is blocked on the owner, and the test phase

Recorded verbatim, then their consequences. Implemented in 0.5.6-dev; record: [`implementation/TUNABLE_PRIORITIES_AND_TEST_PHASE.md`](implementation/TUNABLE_PRIORITIES_AND_TEST_PHASE.md).

> whats blocked by me nothing should ever be blocked by me use ask me question and make sure there is a write in option multile choice to select and fill out my own because not all your recommendations listed are the only options

> option 1 and once again we should not be worriying about this as the mod is NOT completed yet only once we confirm everything in intirety with the mod and its workings with the game dlc, core, and mods is 100% do we ever test it(which i have to set up first, then u add the rim api mod, then we test(me running through the game asnd telling you the problems, LIVE fixes to the extent we can without a restart and reload of the mod)

> make sure we are foillowing all rimworld and steam TOS and requirments when it comes to issues similar and the issue of factions and pawn heduffs and the like this mod has to be working with official versions

**Decided, and binding:**

13. **There is no blocked-on-owner status.** The `[!]` marker is removed from `TODO.md` and `DEFERRED.md` and must not be reintroduced. Nothing in this project has ever been blocked on the owner; the standing instruction was to keep building and launch later, and every checkpoint from 0.4.2 onward was built without waiting. A row that cannot be *closed* without the game running is `[T]` and gates no work.
14. **Testing is one phase, after completion, in a fixed order.** The mod is confirmed complete in its entirety — its own workings and its workings with the game, Core, the DLC and the mods — at 100%. Then the **owner** sets up the test environment. Then the rim api mod is added. Then the owner plays and reports problems, and fixes land **live, to whatever extent is possible without a restart and reload of the mod.**
15. **Prefer settings and data over constants, as a consequence of 14.** Anything hardcoded is something the live test session cannot fix. Any value that is a matter of feel or tuning belongs in the settings window or in a def. The eight cross-gate work-giver priorities were moved for exactly this reason in 0.5.6-dev; hold every future tuning value to the same test.
16. **Never ask the owner to launch in order to continue building.** No source work ever waits on a launch. The launch rule itself is unchanged: only the owner launches RimWorld, through RimSort, and the agent never touches the active mod list or attaches the QA overlay outside the saved plan.
17. **At a fork, ask immediately and keep building around it.** Fire a multiple-choice question the moment a real fork appears, and meanwhile finish everything that does not depend on the answer. **Every question carries a write-in option, and the listed suggestions are never the whole option space** — the owner's own wording. Do not treat a menu as exhaustive.
18. **RimWorld and Steam terms are a release requirement, verified rather than asserted.** The mod targets official RimWorld and official DLC only. Add definitions; never redistribute a game, DLC or third-party asset. Reference icons and pawn kinds by path and defName instead of copying files. No `PatchOperationReplace` or `PatchOperationRemove` on a Core or DLC def. Gate DLC-conditional content with `MayRequire`. No modified game build, no bundled game file, no shipped QA overlay, and upload only what we own. This governs the faction layer, pawn hediffs, and every def class added later. Position, verification and the mechanical checks: [`COMPLIANCE_AND_OFFICIAL_VERSIONS.md`](COMPLIANCE_AND_OFFICIAL_VERSIONS.md).

---

## Owner decisions — 2026-09-29 — the M6 release gate

Recorded verbatim, then their consequences. Three answers to one question set, asked because M6 is the only major that cannot be closed by building.

> option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs

> option 2 and option 3

**Decided, and binding:**

19. **M6 splits into M6a and M6b.** M6a is the four rows that can be closed without the game running: package and def validation, the fresh-start checklist, the mod page and provenance, and the tag-and-archive ritual. M6b is the six rows that structurally cannot: scenario acceptance per opening, the invalid-state matrix, performance, economy balance, the release report and the install/uninstall/server tests. The split is bookkeeping, not scope: no row is dropped, reworded or moved out of Phase 6. It exists because one major reading 0% hid the fact that nearly half of it was buildable today.
20. **The no-tests rule gains one scoped exception, and it is deferred.** The owner selected *both* the automated-fixtures option and the defer option for the Phase 6 fixtures row. Read together: **automated fixtures are authorised**, replacing the manual-checklist-only reading, **and they are not written until after the first launch**, so their content is shaped by observed failures rather than guessed ones. The exception is **narrow and belongs to that row alone**: deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration. It is **not** permission for a general test suite, and `CONTRIBUTING.md`'s rule stands everywhere else. Nothing about it may be built before the owner has launched the game once.
21. **Publication no longer waits on validation, but claims still do.** See [D1 superseded](#d1-superseded-2026-09-29--public-workshop-is-the-first-distribution-target). The mod page may state what `About.xml` declares as requirements, and that the solo loop runs on Core content; it must not claim a profile row, a DLC interaction or RWT co-op has been validated until that row has a recorded result. Publishing early makes the no-compatibility-claim rule the main protection rather than a formality, and makes save migration a standing obligation from the first published version.

---

## Owner decisions — 2026-09-29 — undeferring, and what the Backrooms is *for*

Recorded verbatim, then their consequences. Asked because `DEFERRED.md` was being emptied into `TODO.md` and three of its rows were genuine forks rather than queued work.

> un deffer everything in defferments.md and put it all back in the todod properly LIKE I SAID NOTHING SHALL BE DEFFERED SO USE ASK ME FUCKIGN QUESTION OR FUCKING RE MAKE IT IN THE TODO CORRECTLY AS MOST ARE TEST SHIT THAT IVE BEEN SAYING SINCE THE START WE DO WHEN ITS ALL COMPLETE AND 100% FINISHED!!!! DO YOU UNDERSTAND THIS!!!!!

> ik think option one can work and we can add a flag to item from the back rooms like (odd) or something like that and have quests and missions and contracts and stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd) and the such for all things materials and resources ect ect that can give reason for the players to have to advance and excplore and haul and use the spaces iin the backrooms

> option 1 weve never made a save and the rimworld together server ands saves you may have been used in prep have nothing to do with how our mod will work as it was all pre build and we havent tested as the build is not complete

**Decided, and binding:**

22. **Nothing is deferred, and `DEFERRED.md` is closed.** All 43 open rows moved into `TODO.md` byte-for-byte — 38 as ordinary open work under the major that owns it, 5 as `[T]`. **No row may ever be added to that file again.** Work that is not being done right now has exactly three legitimate homes: build it, put it in `TODO.md` under its major (`[T]` if it cannot close without the game running), or ask the owner immediately with multiple choice and a write-in. A genuine fork is a question, never a deferment.

23. **Odd origin — the Backrooms marks what comes out of it, and the economy asks for it.** This is the owner's own design and it is the answer to *why a player goes back in*. Floors recovered when lifted is scoped to **Rimrooms floors only** (option 1), so installing the mod never changes an existing colony's vanilla floors — and on top of that, **anything brought out of a Backrooms coordinate carries an "(odd)" marker**, and contracts, quests and missions demand quantities of *odd* goods specifically: *"1000 (odd) cotton"*, *"10 uninstalled electic stoves(odd)"*, and so on across every material and resource. The purpose in the owner's words: *"give reason for the players to have to advance and excplore and haul and use the spaces iin the backrooms"*.

    Why this is a strong shape and not just flavour: it converts the entire existing cross-map work engine into an **economy**. Thirty-one work families already move real goods through a gate; until now nothing in the game asked for those goods *by origin*. An odd-only contract cannot be satisfied by the colony's own stockpile at any price, so it can only be filled by going in, working the space, and hauling it out — which is the loop the whole mod was built to support. It also gives ordinary Core resources a second tier of value without inventing a single new item.

    **It stays inside [`CONTENT_REUSE_POLICY.md`](CONTENT_REUSE_POLICY.md):** the marker is a comp added to existing Core things and a saved flag set at the moment a thing leaves a coordinate. **No new item, no new texture, no new resource.** Adding a comp is a `PatchOperationAdd`, which is permitted; `PatchOperationReplace` and `PatchOperationRemove` on a Core def remain forbidden. The label decoration is a keyed string, so "(odd)" is translatable and its exact wording is not frozen by this decision.

24. **A clean development-save break is declared, and the reason is stated plainly.** In the owner's words: *"weve never made a save and the rimworld together server ands saves you may have been used in prep have nothing to do with how our mod will work as it was all pre build and we havent tested as the build is not complete"*. So M2 may remove any custom Def a saved `Thing` would reference — the gate objects, the field gear, the five `RR_*Staff` PawnKinds, the five recipes — **without writing a migration for any of them**. The old build stays archived. This is correct on its own terms too: `0.x` explicitly promises no save compatibility under D2. **Note the boundary — decision 21 made save migration a standing obligation from the first *published* version onward.** This break is the last free one.

25. **The Quiet Pursuer keeps its rules and loses its art.** Rebind the encounter to an existing Core pawn presentation, preserving the readable warning, the learnable rule and the countermeasure exactly as authored in [`THREAT_DESIGN_SHEETS.md`](THREAT_DESIGN_SHEETS.md). The custom sprite leaves the package. No new art exception is opened; the main-menu images remain the sole visual exception.
    - **SUPERSEDED 2026-10-06, AND ONLY HALF OF IT.** The art ban is lifted: the owner reversed the existing-content-only direction in full, so the custom sprite may come back. **The rules half still stands and is the harder half** — the readable warning, the learnable rule and the countermeasure are authored behaviour, and `THREAT_DESIGN_SHEETS.md` still forbids colour or sound being the only way to notice a tell. Our own sprite may give the Pursuer a face; it may not become how a player is warned.
    - **It is NOT shipped yet, and the reason is scope rather than permission.** A creature presentation of our own needs a race `ThingDef` with `lifeStages` and body graphics, not a texture — and a malformed race def on a 296-mod profile is the kind of thing that breaks somebody else's pawn rendering. `RR_QuietPursuer.png` is cut and deliberately held out of the package by `tools/cut-phase2-art.py`, which ships no texture no def or source file names.
