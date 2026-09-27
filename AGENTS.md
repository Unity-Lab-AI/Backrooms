# Rimrooms - Async Industries: build-agent instructions

Before any implementation, read [`docs/AI_BUILD_HANDOFF.md`](docs/AI_BUILD_HANDOFF.md), [`docs/GATE_0_DECISIONS.md`](docs/GATE_0_DECISIONS.md), [`docs/FEATURE_TRACEABILITY.md`](docs/FEATURE_TRACEABILITY.md), and [`docs/SOURCE_REGISTER.md`](docs/SOURCE_REGISTER.md). The strict Gate 0 must pass before a Rimrooms code project, XML Defs, or source-specific production content begins.

## Source-of-truth rules

- Treat [`docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) as the ordered work plan and implementation gate. Do not mark work complete without a saved artifact or reproducible evidence.
- Treat [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md) as the player-experience and campaign-loop contract; [`docs/SYSTEMS_CATALOG.md`](docs/SYSTEMS_CATALOG.md) as the breadth inventory; and [`docs/TECHNICAL_ARCHITECTURE.md`](docs/TECHNICAL_ARCHITECTURE.md) as the proposed code/save/network boundary.
- Use [`docs/MOD_INTEGRATION_PLAN.md`](docs/MOD_INTEGRATION_PLAN.md), [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md), [`docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md), the CSV inventory, and the workbook for third-party mod boundaries. The workbook's preliminary mappings are not proof of compatibility.
- Use [`docs/RESEARCH.md`](docs/RESEARCH.md), [`docs/UNIVERSE_ADAPTATION.md`](docs/UNIVERSE_ADAPTATION.md), and the indexed source/review files for creative references. Label a claim as source fact, interpretation, or original game design.
- Use [`docs/SCENARIOS.md`](docs/SCENARIOS.md) as the canonical contract for Async Industries, Furniture & Knickknack Store, Lone Survivor, and future openings; do not implement scenario details from chat summaries alone.
- Treat dependency, DLC, distribution, canon, project-license, language, and RWT technology-transfer choices as open until they are recorded in `docs/GATE_0_DECISIONS.md`. Do not silently promote a suggested answer to an owner decision.
- Do not copy or redistribute files from other RimWorld mods. Integrate their installed behavior through documented public extension points and record a source link for each external claim.

## Required implementation discipline

- Keep feature IDs stable and namespaced `RimroomsAsyncIndustries`; do not guess an author namespace or publish metadata while owner decisions remain open.
- Every feature must use a stable ID from `docs/FEATURE_TRACEABILITY.md` and link its exact lore/source notes, mod-profile rows, style rules, implementation files, state owner, player-facing route, failure state, DLC/mod dependency, and acceptance evidence before implementation.
- Keep each player's facility, ledger, research, coordinate discoveries, and local maps branch-owned. Cross-branch effects must be explicit, idempotent, and supported by the pinned RimWorld Together build; do not assume server-side shared state.
- Generated spaces need stable coordinate/seed identity, bounded generation, route validation, saved discoveries, and a recoverable return path.
- Do not assume the DLC or 294-mod requirement policy. Follow the owner decision recorded in `docs/GATE_0_DECISIONS.md`; if the owner selects optional-DLC support, preserve a complete Core-only campaign.
- Update the relevant design/technical/research documents in the same change as any decision that changes their contract. Keep project links relative to this repository root and verify each local target exists.
- For implementation work, build and run the relevant RimWorld profile and record game build, DLC, mod order, RWT client/server build, save, logs, and observed result. Never describe a profile as supported merely because it loads.

## Current project state

This folder contains design and research documents only. There is no Rimrooms C# source, XML Def package, asset package, runnable build, or in-game implementation yet. Gate 0 in the master TODO must be completed before full implementation starts.
