# Rimrooms - Async Industries

**Rimrooms - Async Industries** is a RimWorld 1.6 company-management campaign about building and operating an organization that investigates, contains, and profits from unstable spaces beyond a machine gate.

The default campaign begins with a small facility, limited supplies, and an unreliable gate. Players can instead choose a furniture-and-knickknack store breach or begin as a lone survivor already inside a seeded Backrooms coordinate. The openings differ, then feed into shared systems for exploration, evidence, threats, recovery, and expansion. See the [scenario framework](docs/SCENARIOS.md).

The target is RimWorld 1.6. The campaign works with Core alone for solo play; Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional. Co-op uses RimWorld Together and Harmony; the other entries in the 294-mod profile are optional, while the full list remains the research/test target. The displayed title is exactly **Rimrooms - Async Industries**; the author/publisher field is intentionally blank. Shipped Backrooms inspiration is limited to Kane Pixels' continuity and the A24 feature, adapted indirectly. See the [source register](docs/SOURCE_REGISTER.md) for research status and the [feature traceability map](docs/FEATURE_TRACEABILITY.md) for links between systems, sources, mods, visual direction, and build evidence.

The detailed, build-ready start contracts live in [`docs/SCENARIOS.md`](docs/SCENARIOS.md). Future build agents should start from [`AGENTS.md`](AGENTS.md), [`docs/AI_BUILD_HANDOFF.md`](docs/AI_BUILD_HANDOFF.md), and the [source register](docs/SOURCE_REGISTER.md), which maps local inputs and primary source URLs to their review status.

## Project documents

- [Game design brief](docs/GAME_DESIGN.md) — player experience, campaign loop, systems, and scope.
- [Systems catalog](docs/SYSTEMS_CATALOG.md) — staff, facilities, interface, research, missions, and economy inventory.
- [Technical architecture](docs/TECHNICAL_ARCHITECTURE.md) — proposed RimWorld implementation and multiplayer constraints.
- [AI build handoff and document map](docs/AI_BUILD_HANDOFF.md) — required reading order, feature-to-source paths, and evidence/status rules for future coding agents.
- [Gate 0 owner decisions](docs/GATE_0_DECISIONS.md) — recorded release, dependency, canon, transfer, identity, language, content, and license decisions.
- [Feature traceability map](docs/FEATURE_TRACEABILITY.md) — stable system IDs connecting player contracts to research, the 294-mod profile, presentation, code/file surfaces and acceptance evidence.
- [Source and document register](docs/SOURCE_REGISTER.md) — canonical file map, direct research URLs, local profile paths, review templates, and unresolved evidence.
- [Campaign scenario contracts](docs/SCENARIOS.md) — Async Industries, Furniture & Knickknack Store, Lone Survivor, and later opening candidates with shared start-state requirements.
- [Build-agent instructions](AGENTS.md) — project invariants and documentation workflow for implementation.
- [DLC and multiplayer compatibility](docs/COMPATIBILITY.md) — support policy and the local server profile.
- [Complete systems and mod integration plan](docs/MOD_INTEGRATION_PLAN.md) — top-to-bottom company loop, RWT branch-sharing model, both gravship chapters, every profile integration family, and implementation gates.
- [Pre-production and implementation TODO](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) — owner decisions, coding-start gate, full file creation list, interconnected build phases, every-profile integration, QA, and release acceptance.
- [Research and references](docs/RESEARCH.md) — source register, inspiration notes, and licensing provenance.
- [RWT and gravship feasibility audit](docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md) — exact local 294-entry client/server profile comparison, RWT build identity gap, and the two gravship chapter findings.
- [Universe adaptation notes](docs/UNIVERSE_ADAPTATION.md) — Kane Pixels/A-Sync continuity translated into the RimWorld company campaign.
- [Kane Pixels video index](docs/research/kane-pixels-video-index.csv) — all 23 entries in the official “The Backrooms” playlist, with direct watch URLs, IDs, runtime, and review status.
- [Development roadmap](docs/ROADMAP.md) — staged implementation from first playable build to the long campaign.
- [Local server mod inventory](docs/research/rimworld-server-mod-inventory.csv) — 294 name/ID/order records exported from the server's `ModConfig.json` on 2026-09-27, with direct Workshop URLs for 288 Workshop entries. It does not include private settings.
- [294-mod integration workbook](outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx) — filterable per-mod role, dependency, use, conflict watch, and review status.

## Design rule

Make the company loop work before building an endless content catalog. Each new room, entity, tool, contract, or research branch should give the player a useful decision, create a risk, or improve how the company handles risk.

## Current status

This is a design and research workspace, not a functioning mod yet. No C# assemblies, XML definitions, art, sounds, or released Backrooms assets have been added. The 294-row workbook is a complete profile inventory and design mapping, but most individual Workshop metadata and compatibility have not been independently verified. The full episode-by-episode video and feature-film review is still an open research task; current source notes are a first pass based on official public pages and materials.
