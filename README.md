# Rimrooms - Async Industries

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](docs/CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Rimrooms - Async Industries** is a RimWorld 1.6 company-management campaign about building and operating an organization that investigates, contains, and profits from unstable spaces beyond a machine gate.

The planned default campaign begins with a small facility, limited supplies, and an unreliable gate. Later planned openings let players choose a furniture-and-knickknack store breach or begin as a lone survivor already inside a seeded Backrooms coordinate. The openings differ, then feed into shared systems for exploration, evidence, threats, recovery, and expansion. See the [scenario framework](docs/SCENARIOS.md).

The target is RimWorld 1.6. The campaign is designed to work with Core alone for solo play; Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional. Co-op uses RimWorld Together and Harmony; the other entries in the 294-mod profile are optional, while the full list remains the research/test target. The displayed title is exactly **Rimrooms - Async Industries**; the author/publisher value is `Operator`. Shipped Backrooms inspiration is limited to Kane Pixels' continuity and the A24 feature, adapted indirectly. See the [source register](docs/SOURCE_REGISTER.md) for research status and the [feature traceability map](docs/FEATURE_TRACEABILITY.md) for links between systems, sources, mods, visual direction, and build evidence.

The scenario opening cards live in [`docs/SCENARIOS.md`](docs/SCENARIOS.md); the named first-slice roster, starter threats, and provisional economy are in [`docs/FIRST_SLICE_CONTENT_INVENTORY.md`](docs/FIRST_SLICE_CONTENT_INVENTORY.md), [`docs/THREAT_DESIGN_SHEETS.md`](docs/THREAT_DESIGN_SHEETS.md), and [`docs/CAMPAIGN_ECONOMY_MODEL.md`](docs/CAMPAIGN_ECONOMY_MODEL.md). Future build agents should start from [`AGENTS.md`](AGENTS.md), [`docs/AI_BUILD_HANDOFF.md`](docs/AI_BUILD_HANDOFF.md), and the [source register](docs/SOURCE_REGISTER.md), which maps local inputs and primary source URLs to their review status. All 294 profile rows now have accepted source-fact reviews and linked records; zero rows have combined-profile runtime clearance. The [agent roadmap](docs/research/MOD_REVIEW_AGENT_ROADMAP.md) records the completed source-review intake and gives the workflow for new evidence.

## Build and installation

**Current development version: 0.10.4-dev.** Every checkpoint has its own record under [`docs/implementation/`](docs/implementation/), and [`docs/NOW.md`](docs/NOW.md) is the single page that says what is true right now: the published commit, the build counts, the reproduced assembly hash, and what is open in order.

What works in source today, briefly: a gate is an **ordinary door you designate** rather than a custom machine, at sizes from 1x1 to 2x3; **bringing a connection up is work** an operator does at a console, faster on a route the crew has run before; each gate keeps its own **address book** of everywhere it has dialled; colonists and animals cross, with the gate's width deciding what fits through; coordinates generate as rooms, corridors and **facilities** that span several rooms at once; what lives there **follows a crew to the doorway** in the worst spaces and, on an advanced machine, can come through behind them; and an **odd-origin economy**, company bonds, a corporate trader and a credits ladder sit on top of it.

Six checkers run without the game and gate every checkpoint: package integrity, keyed strings, DLC gating, info cards, documentation conformance, and the Gate 0 documentation audit. The build is **deterministic** and proved so by recompiling twice from clean and comparing the assembly hash. **Existing-content replacement, the remaining scenarios and all runtime acceptance are still open**, and no game launch is required to continue implementation.

- [Build and staging instructions](docs/BUILDING.md) — pinned local references, locked restore, copyable package, safe updates and RimSort discovery.
- [First owner-launched session](docs/implementation/PHASE_2_OWNER_LAUNCH.md) — staged package identities, separate QA bridge and RimSort launch steps.
- [Current build evidence and next work](docs/implementation/PHASE_3_BUILD_RECORD.md) — company operations, content reuse and menu implementation; [earlier expedition slice](docs/implementation/PHASE_2_BUILD_RECORD.md) and [historical foundation](docs/implementation/PHASE_1_BUILD_RECORD.md).
- [Public release plan](docs/PUBLIC_RELEASE_PLAN.md) — the documentation site, the Steam Workshop page and the collection, and the order they have to happen in.
- [Contributor guide](CONTRIBUTING.md), [changelog](CHANGELOG.md), [credits](docs/CREDITS.md), [save policy](docs/SAVE_MIGRATION_POLICY.md), and [bug report form](.github/ISSUE_TEMPLATE/bug_report.yml).

Build a clone before copying `Mod/Rimrooms - Async Industries/`; generated DLLs are not committed. This development package needs Core only. Future co-op requires the documented Harmony/RWT stack; no optional integration is yet cleared. The owner alone activates, sorts and launches through RimSort. Preserve the full 295-entry product target and count the QA bridge separately.

## Project documents

- [Gate 0 completion audit](docs/research/GATE_0_COMPLETION_AUDIT.md) — requirement-by-requirement closure evidence, reproducible document/register/pin checks, and the post-build work boundary.
- [Performance benchmark plan](docs/research/PERFORMANCE_BENCHMARK_PLAN.md) — named reference machine, initial budgets and measurements scheduled after the owner's first RimSort launch.
- [2026-09-28 profile delta](docs/research/profile-deltas-2026-09-28.json) — reviewed Hospitality update to read alongside the historical 294-mod register.
- [Rimrooms mod overview](docs/RIMROOMS_MOD_OVERVIEW.md) — compact player-facing summary of the scenarios, campaign, company scale, exploration, multiplayer direction, interface, and menu showcase.
- [Game design brief](docs/GAME_DESIGN.md) — player experience, campaign loop, systems, and scope.
- [Systems catalog](docs/SYSTEMS_CATALOG.md) — staff, facilities, interface, research, missions, and economy inventory.
- [Campaign content catalog](docs/CAMPAIGN_CONTENT_CATALOG.md) — full progression arcs, research branches, evidence, incidents, threats, room families, outposts, and later space content; future details remain candidates.
- [Technical architecture](docs/TECHNICAL_ARCHITECTURE.md) — proposed RimWorld implementation and multiplayer constraints.
- [AI build handoff and document map](docs/AI_BUILD_HANDOFF.md) — required reading order, feature-to-source paths, and evidence/status rules for future coding agents.
- [Gate 0 owner decisions](docs/GATE_0_DECISIONS.md) — recorded release, dependency, canon, transfer, identity, language, content, and license decisions.
- [Feature traceability map](docs/FEATURE_TRACEABILITY.md) — stable system IDs connecting player contracts to research, the 294-mod profile, presentation, code/file surfaces and acceptance evidence.
- [Source and document register](docs/SOURCE_REGISTER.md) — canonical file map, direct research URLs, local profile paths, review templates, and unresolved evidence.
- [294-mod review roadmap](docs/research/MOD_REVIEW_AGENT_ROADMAP.md) — agent batch assignments, evidence rules, and lead-agent intake steps for the complete profile review.
- [Priority mod interactions](docs/research/PRIORITY_PROFILE_INTERACTIONS.md) — source-backed overlaps and test candidates; not a compatibility certificate.
- [Pre-production acceptance standard](docs/research/PREPRODUCTION_ACCEPTANCE_STANDARD.md), [optional-mod support policy](docs/research/OPTIONAL_MOD_SUPPORT_POLICY.md), [content/accessibility brief](docs/research/CONTENT_ACCESSIBILITY_BRIEF.md), and [provenance register](docs/research/provenance-register.csv) — quality criteria and the scope records future reviewers should use.
- [Visual and audio style brief](docs/research/VISUAL_AUDIO_STYLE_BRIEF.md) — original presentation direction for the company, gate, Backrooms spaces, scenarios, the Backrooms main-menu slideshow, interface, sound, and accessibility.
- [Kane Pixels fan cliff notes](docs/research/KANE_PIXELS_FAN_CLIFF_NOTES.md) — 23 concise fan-summary story notes with links to their source pages and original RimWorld inspiration hooks.
- [Fan summary guide](docs/research/FAN_SUMMARY_GUIDE.md) — approved first-pass route for the series and film; direct viewing is only needed to answer a specific story or visual question left open by the summaries.
- [Kane Pixels lore/story map](docs/research/KANE_PIXELS_LORE_STORY_MAP.md) — the 23-upload review queue, continuity evidence rules, and story-to-game synthesis path; direct-upload reviews remain in progress where needed.
- [Campaign scenario contracts](docs/SCENARIOS.md) — Async Industries, Furniture & Knickknack Store, Lone Survivor, and later opening candidates with shared start-state requirements.
- [First playable contract](docs/FIRST_PLAYABLE_CONTRACT.md) — provisional starting values and acceptance target for the Async Industries vertical slice.
- [First-slice content inventory](docs/FIRST_SLICE_CONTENT_INVENTORY.md) — named staff, facility rooms, field gear, coordinate room families, evidence, objectives, reward, and teaching order.
- [First-slice mod interaction map](docs/research/FIRST_SLICE_MOD_INTERACTION_MAP.md) — the first playable's state owners, relevant reviewed mods, provisional treatments, post-build acceptance cases, and explicit deferrals.
- [First-slice Core API source map](docs/research/FIRST_SLICE_CORE_API_SOURCE_MAP.md) — verified local Core XML/metadata entry points and the source-inspection work required before implementing each route.
- [RimSort package and launch plan](docs/research/RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md) — repository/package separation, RimSort Local Mods staging, and the owner-operated 295-entry product target. RimBridgeServer is a separate test-only overlay, normally making 296 loaded entries.
- [Tutorial script](docs/TUTORIAL_SCRIPT.md) — provisional player-facing first-session sequence, recovery messages, and accessibility cues; in-game UX review remains open.
- [Procedural space contract](docs/PROCEDURAL_SPACE_CONTRACT.md) — finite seeded destinations, room tags, route safety, distortion propagation, revisit state, and migration rules.
- [Threat design sheets](docs/THREAT_DESIGN_SHEETS.md) — original starter route distortion and entity rules, counterplay, evidence, accessibility cues, and the template for later threats.
- [Campaign economy model](docs/CAMPAIGN_ECONOMY_MODEL.md) and [campaign economy progression](docs/CAMPAIGN_ECONOMY_PROGRESSION.md) — provisional opening values plus later income/cost stages, quote rules, logistics, and remaining balance cases; the linked workbook includes the opening example and editable 30-day planning/downside cases for later stages.
- [Operations action contracts](docs/OPERATIONS_ACTION_CONTRACTS.md) — planned panes, action requirements, results, failures, recovery, and state owners.
- [Campaign state dictionary](docs/CAMPAIGN_STATE_DICTIONARY.md) — branch/save ownership, stable ID categories, transfers, and migration rules.
- [Build-agent instructions](AGENTS.md) — project invariants and documentation workflow for implementation.
- [DLC and multiplayer compatibility](docs/COMPATIBILITY.md) — support policy and the local server profile.
- [Complete systems and mod integration plan](docs/MOD_INTEGRATION_PLAN.md) — top-to-bottom company loop, RWT branch-sharing model, both gravship chapters, every profile integration family, and implementation gates.
- [Pre-production and implementation TODO](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) — owner decisions, coding-start gate, full file creation list, interconnected build phases, every-profile integration, QA, and release acceptance.
- [Research and references](docs/RESEARCH.md) — source register, inspiration notes, and licensing provenance.
- [RWT and gravship feasibility audit](docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md) — exact local 294-entry client/server profile comparison, pinned RWT artifacts, unresolved RimWorld build identity, open runtime/API checks, and the two gravship chapter findings.
- [RWT post-build acceptance plan](docs/research/RWT_BASELINE_TEST_PLAN.md) — separate client branches, offline-visit availability, online trade/gift, candidate offline drop-pod cargo, aid/recovery cases, and the owner-selected test scope for rows 182 and 274. Run only after a Rimrooms build exists, using the [RimBridgeServer test plan](docs/research/RIMBRIDGE_TEST_HARNESS.md); this run sheet is not a test result.
- [RimBridgeServer test harness plan](docs/research/RIMBRIDGE_TEST_HARNESS.md) — attach after the owner starts the isolated session through RimSort; optional test tooling, never a player dependency.
- [Gravship, vehicle, cargo, and orbital profile interactions](docs/research/GRAVSHIP_PROFILE_INTERACTIONS.md) — source-backed review of the selected profile families that may interact with the two VGE chapters, plus a staged check plan. No compatibility pass is claimed.
- [RimWorld 1.6 package and generation findings](docs/research/RIMWORLD_1_6_PACKAGE_AND_GENERATION.md) — official 1.6 primer, named room/map/path/planet-layer candidates, local package metadata counts, dependency/order graph, and unresolved prototype boundaries.
- [Installed metadata snapshot](docs/research/installed-mod-metadata-2026-09-27.csv) and [declared mod relationship graph](docs/research/installed-mod-relationships-2026-09-27.csv) — repeatable local 294-row input facts; not compatibility certification.
- [Universe adaptation notes](docs/UNIVERSE_ADAPTATION.md) — Kane Pixels/A-Sync continuity translated into the RimWorld company campaign.
- [Kane Pixels video index](docs/research/kane-pixels-video-index.csv) — all 23 entries in the official “The Backrooms” playlist, with direct watch URLs, IDs, runtime, and review status.
- [Development roadmap](docs/ROADMAP.md) — staged implementation from first playable build to the long campaign.
- [Local server mod inventory](docs/research/rimworld-server-mod-inventory.csv) — 294 name/ID/order records exported from the server's `ModConfig.json` on 2026-09-27, with direct Workshop URLs for 288 Workshop entries. It does not include private settings.
- [294-mod integration workbook](outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.html) — filterable per-mod role, dependency, use, conflict watch, and review status.

## Working on the mod with the Claude Code workflow

Development continues under the Unity AI Lab `.claude/` workflow from 2026-09-28. Start with [`docs/HOWTO.md`](docs/HOWTO.md): it explains how the workflow ledger sits on top of the project contracts above, the daily task ceremony, the build/stage/publish commands, and the rules a build agent must never break (existing content only, the owner alone launches RimWorld, connected colony portals supersede dispatch-only travel). The ledger files are:

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — major milestones layered on the Stage 0–6 roadmap; [`docs/TODO.md`](docs/TODO.md) — the working queue; [`docs/DECOMPOSED.md`](docs/DECOMPOSED.md) — single-edit slices of the active task; [`docs/NOW.md`](docs/NOW.md) — the one task in motion.
- [`docs/FINALIZED.md`](docs/FINALIZED.md) — permanent archive of completed work, including the inherited pre-workflow history.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — as-built map of the source, package, tools and save owners plus the whole-project design system map; [`docs/SKILL_TREE.md`](docs/SKILL_TREE.md) — capability inventory with implementation status.
- [`docs/PUBLISHING.md`](docs/PUBLISHING.md) — the exact push and cascade procedure for both remotes.

The complete mod backlog remains [`docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md); the ledger mirrors its active slice and never replaces it.

## Design rule

Make the company loop work before building an endless content catalog. Each new room, entity, tool, contract, or research branch should give the player a useful decision, create a risk, or improve how the company handles risk.

## Current status

Gate 0 documentation/source criteria passed. The [0.2.0 build record](docs/implementation/PHASE_2_BUILD_RECORD.md) now maps the implemented first-expedition slice, original sprites, compiler evidence and remaining work. Gate 2 gameplay acceptance, full campaign content, final audio and the main-menu slideshow remain open. Fan-summary story coverage is complete for the 23 indexed Kane Pixels uploads and the separate A24 feature note; the notes clearly mark secondary-source claims, and watching every video or the full film is not a Gate 0 requirement. Check creator or official film sources only when a planned feature depends on an unresolved detail. All 294 profile rows have accepted source-fact notes and linked review records, including direct publisher-source follow-up for rows 96, 237, and 278. No gameplay or multiplayer workflow tests were run for Rimrooms before a build; the two-client RWT baseline and combined-profile compatibility remain pending post-build acceptance through the [RimBridgeServer harness plan](docs/research/RIMBRIDGE_TEST_HARNESS.md). The product test target is 295 entries (the current 294 plus Rimrooms); a separately loaded RimBridgeServer QA overlay normally makes the test session 296 entries. The staging tool copies the mod into RimSort's configured Local Mods directory; the owner alone activates, sorts and launches it.

The latest required direction is [one connected local colony through open portals](docs/CONNECTED_COLONY_PORTALS.md): shared work/material access, permanent natural portals and persistent procedural inhabitants. This unified work network is not yet implemented by the native-provider foundation.
