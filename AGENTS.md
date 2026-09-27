# Rimrooms - Async Industries: build-agent instructions

Before changing or creating code, read [`docs/AI_BUILD_HANDOFF.md`](docs/AI_BUILD_HANDOFF.md), then [`docs/SOURCE_REGISTER.md`](docs/SOURCE_REGISTER.md). Together they give the implementation order, canonical design paths, source URLs, review locations, and evidence limits.

## Source-of-truth rules

- Treat [`docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) as the ordered work plan and implementation gate. Do not mark work complete without a saved artifact or reproducible evidence.
- Treat [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md) as the player-experience and campaign-loop contract; [`docs/SYSTEMS_CATALOG.md`](docs/SYSTEMS_CATALOG.md) as the breadth inventory; and [`docs/TECHNICAL_ARCHITECTURE.md`](docs/TECHNICAL_ARCHITECTURE.md) as the proposed code/save/network boundary.
- Use [`docs/MOD_INTEGRATION_PLAN.md`](docs/MOD_INTEGRATION_PLAN.md), [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md), [`docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md), the CSV inventory, and the workbook for third-party mod boundaries. The workbook's preliminary mappings are not proof of compatibility.
- Use [`docs/RESEARCH.md`](docs/RESEARCH.md), [`docs/UNIVERSE_ADAPTATION.md`](docs/UNIVERSE_ADAPTATION.md), and the indexed source/review files for creative references. Label a claim as source fact, interpretation, or original game design.
- Use [`docs/SCENARIOS.md`](docs/SCENARIOS.md) as the canonical contract for Async Industries, Furniture & Knickknack Store, Lone Survivor, and future openings; do not implement scenario details from chat summaries alone.
- Preserve RimWorld Core as the only mandatory game-content dependency. Detect DLC and third-party mod integrations and isolate them behind optional patches/adapters unless the owner changes that decision.
- Do not copy or redistribute files from other RimWorld mods. Integrate their installed behavior through documented public extension points and record a source link for each external claim.

## Required implementation discipline

- Keep feature IDs stable and namespaced `RimroomsAsyncIndustries`; do not guess an author namespace or publish metadata while owner decisions remain open.
- Every feature must identify its owning save state, player-facing route, preconditions, failure state, DLC/mod dependency, and acceptance evidence before implementation.
- Keep each player's facility, ledger, research, coordinate discoveries, and local maps branch-owned. Cross-branch effects must be explicit, idempotent, and supported by the pinned RimWorld Together build; do not assume server-side shared state.
- Generated spaces need stable coordinate/seed identity, bounded generation, route validation, saved discoveries, and a recoverable return path.
- Optional DLC and integrations must leave a complete Core-only start and campaign path.
- Update the relevant design/technical/research documents in the same change as any decision that changes their contract. Keep project links relative to this repository root and verify each local target exists.
- For implementation work, build and run the relevant RimWorld profile and record game build, DLC, mod order, RWT client/server build, save, logs, and observed result. Never describe a profile as supported merely because it loads.

## Current project state

This folder contains design and research documents only. There is no Rimrooms C# source, XML Def package, asset package, runnable build, or in-game implementation yet. Gate 0 in the master TODO must be completed before full implementation starts.
