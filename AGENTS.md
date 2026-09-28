# Rimrooms - Async Industries: build-agent guide

This file is the operating guide for anyone preparing, designing, implementing, or documenting the complete RimWorld mod. It points to the detailed project contracts; it does not replace them. Use saved project documents and evidence rather than reconstructing requirements from chat history.

## Project state and next gate

- Gate 0 documentation/source preparation **passed on 2026-09-28**. The owner decisions D1–D9 and supplemental S1/B are recorded; the master TODO has no open Gate 0 checklist items.
- Phase 1 has a compiled **0.1.0 foundation**: C# project, logging entry point, inactive campaign component, localized Operations tab, original identity card, copyable package and build/staging tools. Read the [build record](docs/implementation/PHASE_1_BUILD_RECORD.md), [build instructions](docs/BUILDING.md), [Core source review](docs/implementation/PHASE_1_CORE_SOURCE_REVIEW.md) and [migration policy](docs/SAVE_MIGRATION_POLICY.md). No company scenario, gate loop or playable campaign exists yet; no in-game Rimrooms result is recorded.
- Gate 0 passing is not a compatibility, playability, balance, or release claim. All game/runtime checks remain future acceptance work after a Rimrooms build exists.
- Read the [AI build handoff](docs/AI_BUILD_HANDOFF.md), [Gate 0 decisions](docs/GATE_0_DECISIONS.md), [feature traceability map](docs/FEATURE_TRACEABILITY.md), [source register](docs/SOURCE_REGISTER.md), and [master TODO](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) before implementation. Follow their required-reading order and begin with the next unblocked TODO phase.

## Authority and document map

If documents appear to conflict, use this order and update every affected contract in the same change:

1. The owner's latest explicit direction, recorded in [GATE_0_DECISIONS.md](docs/GATE_0_DECISIONS.md). D1–D9 remain binding. S1/B freezes broad later threat/anomaly families and defers the five named threat sketches; do not promote those names to planned content without later owner approval.
2. [PREPRODUCTION_AND_IMPLEMENTATION_TODO.md](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) for work order, phase gates, evidence requirements, and the complete file/task backlog.
3. Canonical player/design contracts: [GAME_DESIGN.md](docs/GAME_DESIGN.md), [SCENARIOS.md](docs/SCENARIOS.md), [FIRST_PLAYABLE_CONTRACT.md](docs/FIRST_PLAYABLE_CONTRACT.md), [FIRST_SLICE_CONTENT_INVENTORY.md](docs/FIRST_SLICE_CONTENT_INVENTORY.md), [CAMPAIGN_CONTENT_CATALOG.md](docs/CAMPAIGN_CONTENT_CATALOG.md), [CAMPAIGN_ROSTER_FREEZE.md](docs/CAMPAIGN_ROSTER_FREEZE.md), [THREAT_DESIGN_SHEETS.md](docs/THREAT_DESIGN_SHEETS.md), [PROCEDURAL_SPACE_CONTRACT.md](docs/PROCEDURAL_SPACE_CONTRACT.md), [CAMPAIGN_ECONOMY_MODEL.md](docs/CAMPAIGN_ECONOMY_MODEL.md), [CAMPAIGN_ECONOMY_PROGRESSION.md](docs/CAMPAIGN_ECONOMY_PROGRESSION.md), [OPERATIONS_ACTION_CONTRACTS.md](docs/OPERATIONS_ACTION_CONTRACTS.md), [CAMPAIGN_STATE_DICTIONARY.md](docs/CAMPAIGN_STATE_DICTIONARY.md), and [TUTORIAL_SCRIPT.md](docs/TUTORIAL_SCRIPT.md).
4. Technical/integration contracts: [TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md), [SYSTEMS_CATALOG.md](docs/SYSTEMS_CATALOG.md), [MOD_INTEGRATION_PLAN.md](docs/MOD_INTEGRATION_PLAN.md), [COMPATIBILITY.md](docs/COMPATIBILITY.md), [FEATURE_TRACEABILITY.md](docs/FEATURE_TRACEABILITY.md), and the applicable first-slice and post-build acceptance plans.
5. Source facts: the [source register](docs/SOURCE_REGISTER.md), the dated 294-row CSV/workbook, each linked per-mod review, and primary publisher/official sources. Local metadata, fan summaries, and proposed treatments are clearly labeled; none alone proves runtime compatibility.

Do not revive an older proposal just because it appears in a draft. D1–D9, S1/B, and the canonical contracts take precedence. When a new owner decision changes scope, record it and propagate it across the TODO, design, technical, traceability, and test documents before relying on it.

## The mod we are building

RimWorld remains the game. Rimrooms adds an open-ended company investigation and expansion campaign. The company can keep discovering new coordinates and expanding across the Backrooms; active maps and generation work must have practical limits.

- **Company start and daily operation:** begin with a small Async Industries research/security facility; hire and train scientists, guards, engineers, analysts, and support staff; assign work; build and power labs, gate control, storage, medical/quarantine, armory, workshops, quarters, cafeterias, recreation, radio, receiving, and security spaces as the company expands.
- **Gate and expeditions:** assemble, power, calibrate, secure, maintain, and upgrade the machine. Begin with short opening windows and earn longer operations through research, equipment, staffing, and infrastructure. Prepare a crew, gear, cargo, objective, budget, and return plan; dispatch, communicate, recall, extract, and recover.
- **Backrooms sites:** use stable coordinate identities and seeds, fog-of-war, readable route clues, saved map/discovery state, bounded procedural room graphs, revisits, changing architecture, investigation, salvage, threats, and a recoverable way back. Discover new coordinates throughout the campaign without preallocating an infinite map. Keep each generation operation and active-map budget bounded; preserve visited sites and allow further exploration through additional coordinates. Strange or dreamlike spaces must remain understandable enough to explore and play.
- **Cases and campaign stories:** support irregular openings in real-world settlements, missing or delayed crews, conflicting records, reappearing people, deaths, witness accounts, investigations, quests, contracts, emergencies, and recoveries. Treat candidate names and mechanics according to S1/B and the content catalog; source-derived ideas remain separate from interpretation and original Rimrooms design.
- **Research and expansion:** turn recovered records, samples, equipment, furniture, and observations into local research, new technology, safer operations, new facility functions, guarded outposts, resource collection, procurement, shipment, and eventually optional space/gravship logistics. The two selected VGE chapters are optional late-game integrations, not the foundation of the gate.
- **Company economy and physical logistics:** the parent company is multi-trillion-dollar scale, while a scenario controls its own authorized branch budget. Company USD entries are separate from RimWorld silver and physical stock. Contracts show quoted scope, payment, deadlines, delivery, risks, and penalties; discoveries and missions can produce major, million-scale company value rather than token event payouts. Materials, equipment, furniture, food, evidence, and silver still require real hauling, pawn capacity, storage, and delivery. Cross-reference the active OgreStack setting and the Core-only baseline; the million-silver case is a logistics case, not a reason to spawn impossible stacks.
- **Scenarios:** Async Industries is the first playable opening. Furniture & Knickknack Store and Lone Survivor are distinct planned starts on the shared scenario/coordinate/evidence model. Further starts remain candidates and need their own approved brief before implementation.
- **Company interface and presentation:** grow the Operations/Company Command layout to manage staff, facilities, gate, expeditions, atlas, evidence/research, contracts, and ledger while preserving useful native RimWorld controls. Create an original, quiet Backrooms main-menu background slideshow that showcases features actually present in the release, with fallback, readability, disable, and reduced-motion behavior.
- **Multiplayer target:** use RimWorld Together for asynchronous cooperation between separate company branches, including facility visits and resource/item exchanges. Custom research dossiers are planned Rimrooms items; their transfer and study behavior still need implementation and testing. Follow the documented online requirement for direct trade/gifts; offline delivery and visits need their own results. Do not add live shared-map control. Facilities, ledgers, maps, cases, discoveries, and research remain branch-owned by default. Enable shared research only through a supported and safely verified extension; otherwise retain the planned dossier route.

Keep the first playable bounded to the contracts above. The complete breadth map is a long-term target, not permission to implement every late-campaign idea before the vertical slice works.

## RimWorld, DLC, and the 294-mod profile

- Target RimWorld 1.6. Preserve a complete Core-only solo campaign. All five DLC are optional. Only Core plus the Harmony/RWT stack is required for co-op; all 294 entries in the local server profile are research and compatibility targets, not mandatory player dependencies.
- Account for every profile row in the CSV/workbook and use the mod's useful behavior where a verified, safe route fits. A row may be native support, configuration, a narrow optional adapter, explicit no-touch, or an explicit conflict/defer. Do not add a dependency merely to claim integration, and do not infer compatibility from load order.
- Read dated profile updates alongside the historical register. The [2026-09-28 delta](docs/research/profile-deltas-2026-09-28.json) records Hospitality row 270 at installed 1.1.5; its original 1.1.4 review stays historical. Run the local read-only `tools/research/audit-pinned-targets.ps1` on this workstation before relying on those pins. Record new changes and inspect affected interfaces before using a changed mod; do not label source review as a runtime result.
- Do not copy another mod's source, assets, or bundled files. Integrate installed behavior only through documented public extension points, declared dependencies, or tested interoperability. Preserve native features and QoL behavior where possible.
- Use the two gravship chapters only within their recorded Odyssey/VEF/dependency boundaries. Do not promise custom boarding, stations, moon maps, or orbital campaigns without a separate approved design and proven API.
- Keep physical item stacks and cargo grounded in the selected profile's actual settings. The workbook's 67-stack OgreStack and 2,000-stack Core calculations are stated assumptions to validate after a build; they are not permission to bypass hauling or storage constraints.

## Lore, style, and assets

- Use Kane Pixels' series as the primary Backrooms story source and the A24 feature as a separate source. The approved first pass is the linked fan cliff notes and high-level feature note. Label them as secondary interpretation; consult official material only for an unresolved detail that matters to a feature entering development.
- Translate atmosphere, mystery, architecture, institutional investigation, missing crews, and uncertainty into original game content. Do not present a Rimrooms rule as canon, copy scenes/characters/dialogue, or import wider community lore into shipped content without a new owner decision.
- Create original in-game art and audio. Maintain per-asset source, permission, and license records before distribution. The selected MIT license covers original source code only; it does not silently license third-party art, audio, films, videos, or mod assets.
- Follow [VISUAL_AUDIO_STYLE_BRIEF.md](docs/research/VISUAL_AUDIO_STYLE_BRIEF.md) and [CONTENT_ACCESSIBILITY_BRIEF.md](docs/research/CONTENT_ACCESSIBILITY_BRIEF.md). Keep horror readable and bounded, provide non-audio/non-color warning cues, and follow the approved menu slideshow behavior.

## Repository and copyable mod package

Keep project materials out of the loadable package:

```text
Backrooms/
  AGENTS.md, README.md, docs/, outputs/       design, research, evidence, and workbooks
  src/                                         solution and C# source; never copied into Local Mods
  tools/                                       build and staging utilities; never shipped
  Mod/Rimrooms - Async Industries/             sole copyable/loadable RimWorld mod root
    About/
    LoadFolders.xml
    1.6/                                       Defs, Assemblies, Languages, Patches, Textures, Sounds
```

The package title must be `Rimrooms - Async Industries`, package ID `UnityLabAI.RimroomsAsyncIndustries`, author/publisher `Operator`, and internal namespace `RimroomsAsyncIndustries`. Put only finished game-loadable output in `Mod/Rimrooms - Async Industries/`. A staging tool copies only that directory into the **Local Mods location shown in RimSort**; do not assume a hard-coded Steam path, copy the repository root, or ship docs, source, workbook, logs, test tools, or third-party files.

## RimSort and test ownership

- RimSort is authoritative for mod discovery, dependency/order review, profile composition, saving mod lists, and launch. The product target is the existing 294 entries plus Rimrooms: **295 target entries**.
- The owner alone starts RimWorld through RimSort. Never start the game directly, launch from an IDE, create a parallel manager profile, or alter the owner's active RimSort list. Any previously opened or agent-started game instance is not an acceptable test environment.
- RimBridgeServer is post-build QA tooling. After the owner launches a disposable session through RimSort, attach the bridge to that running session and record it separately. It normally adds a test-only overlay for **296 loaded entries** (295 target plus bridge); it is not a player dependency and must not replace a target mod. Do not use GABS to start or reorder the session. Use attach-only GABS only if its no-profile-change behavior is verified and approved in the bridge plan.
- The current docs contain future acceptance plans, not test results. No in-game Rimrooms test can run before a Rimrooms build exists. A successful load is only a startup observation, never a compatibility pass.
- For each authorized post-build case, record RimWorld build, DLC, RimSort version, ordered package IDs/versions, Rimrooms build/commit, RWT and bridge versions where relevant, save/scenario/seed, logs, and observed pass/failure/recovery. Never claim a profile supported because it merely launches.

## Agent work and change discipline

- Start each task from the relevant TODO phase and stable feature IDs in [FEATURE_TRACEABILITY.md](docs/FEATURE_TRACEABILITY.md). Read the canonical feature contract and exact source/review rows before touching implementation.
- A feature is not ready to code until its source/lore status, scope, player route, state owner, saved IDs, failure/recovery behavior, style/accessibility rules, optional DLC/mod boundary, file destinations, and acceptance evidence are traceable.
- Use [MOD_REVIEW_AGENT_ROADMAP.md](docs/research/MOD_REVIEW_AGENT_ROADMAP.md) for bounded mod-source review assignments. Give agents non-overlapping rows/questions; require direct source links and clearly labeled facts/inferences; send unresolved questions to the lead; the lead reconciles the source record, CSV, workbook, and canonical design.
- Keep changes focused. When a decision changes a contract, update all linked design, architecture, traceability, source, and test-plan documents in the same change. Keep links relative to this repository and verify their targets.
- Do not mark an item complete without a saved artifact or reproducible evidence. Distinguish source fact, fan interpretation, owner decision, original design, static metadata, planned test, and observed runtime result.
- Preserve uncommitted user work. Do not delete local evidence, mod files, saves, or settings to simplify a task. Do not publish or claim release readiness from preparation documents alone.

### Start and finish each build task

Use a short task record in the current phase's evidence folder. Record: TODO item; feature IDs; canonical section links; exact inventory row/package IDs; scope and file ownership; state/save owner; player action and failure/recovery path; optional dependencies and fallback; acceptance cases; result and remaining work. Planned file paths must be labeled **planned** until they exist.

| Work stage | Required input | Completion evidence |
| --- | --- | --- |
| Phase 1: foundations | Package/launch plan, pinned Core API map, naming and source rules | Local build instructions, clean copyable package, explicit references, source inspection record; owner-launched checks after a build exists |
| Phase 2: first playable | Scenario, inventory, threat sheets, state/action contracts, first-slice interaction map | Implemented facility-to-return-to-analysis loop, recovery/save results, keyed text and original assets |
| Phase 3: full company systems | Campaign catalog, staged economy, procedural and scenario contracts | Staffing, facility, quest, research, logistics, outpost and alternate-start features with their own behavior/recovery evidence |
| Phase 4: optional integration/co-op | Exact per-mod review, relationship/interaction records, RWT and DLC plans | Present/absent behavior, dependency checks, transfer/reconnect results and known limitations for each claimed integration |
| Phases 5–6: interface, polish and release | Company Command, economy, style/accessibility contracts, master phase lists | Implemented interface, measured balance/performance, provenance, migration and release evidence |

The [master TODO](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) owns the detailed order within those stages. The first full-profile startup and later focused cases follow the RimSort plan. Use the [performance benchmark plan](docs/research/PERFORMANCE_BENCHMARK_PLAN.md) for budgets and repeatable comparisons. Keep prototype results separate from release acceptance.

For delegated work, the lead supplies that task record and an exclusive file/row scope. Agents return findings, changed paths, direct evidence, unresolved questions, and checks actually performed. The lead resolves overlaps and updates canonical documents; an agent's “done” message alone never closes a gate. Do not create separate user chats or send messages outside the current agent team without the owner's authorization.

Resolve routine implementation choices from the accepted contracts. Ask a compact, grouped multiple-choice question only when missing direction would materially change the experience or scope. S1/B requires later approval for the five deferred named threat sketches; it does not require a new owner questionnaire for every routine task. Keep work moving on independent items while a question is pending.

When publishing authorized work, preserve the existing `feature/preproduction-handoff` → `Prep` → `Develop` → `Main` cascade separately on `forgejo` and `github`. Inspect remote state, use ordinary fast-forward/merge operations as appropriate, and verify every resulting remote ref. Never force-push to manufacture agreement. A signed-in Forgejo browser and Git transport authentication are separate paths; inspect the actual Git result before reporting success.

## Preparation audit and evidence limits

Read the [Gate 0 completion audit](docs/research/GATE_0_COMPLETION_AUDIT.md) for the evidence behind the preparation status and the explicit post-build queue. Run `python tools/research/audit-gate0.py` to check saved local links/anchors, mod-register agreement, relationship records, story routes, and Gate 0 boxes. This read-only script starts no game and changes no workbook/profile. It does not verify upstream claims, execute spreadsheet formulas, or prove gameplay compatibility. Read the relevant source record as well as running the check.

## Current implementation boundary

Gate 0 is complete. The 0.1.0 foundation compiles and is staged for RimSort discovery; this does not activate it in the owner's profile. Phase 1 still needs owner-managed profile capture and runtime/performance evidence. The next code work is the Core-first scenario initializer and complete campaign-state/transaction foundation, followed by the gate-to-return-to-analysis slice in the master TODO. Use [CONTRIBUTING.md](CONTRIBUTING.md) for identifiers, file ownership and change discipline. The documented full campaign—staffing, research, power and security, gate operation, generated Backrooms sites, cases/contracts, physical logistics, optional integrations, asynchronous cooperation, interface, assets, and expansion—remains the build target. Keep this file and the canonical contracts in sync as the project advances; update status only when the corresponding source or evidence exists.
