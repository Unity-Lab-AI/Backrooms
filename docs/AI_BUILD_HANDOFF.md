# AI build handoff and document map

**Project:** Rimrooms - Async Industries  
**Purpose:** make the authoritative context, source material, and implementation path discoverable to a future coding agent without relying on chat history.

## Required reading order

Read these files in this order before implementation:

1. [`../README.md`](../README.md) — project purpose, scope, and linked artifact list.
2. [`../AGENTS.md`](../AGENTS.md) — mandatory project instructions for coding agents.
3. [`SOURCE_REGISTER.md`](SOURCE_REGISTER.md) — canonical document map, direct source URLs, local profile inputs, review locations, and evidence state.
4. [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) — owner decisions, blockers, code/package file map, phase sequence, gates, and acceptance work.
5. [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) and [`FEATURE_TRACEABILITY.md`](FEATURE_TRACEABILITY.md) — settled owner decisions and the feature-by-feature route through lore, the 294-mod profile, style, package surfaces, and acceptance evidence.
6. [`GAME_DESIGN.md`](GAME_DESIGN.md) and [`SCENARIOS.md`](SCENARIOS.md) — core experience, campaign loop, and complete opening-scenario contracts.
7. [`SYSTEMS_CATALOG.md`](SYSTEMS_CATALOG.md) — complete system/content inventory.
8. [`TECHNICAL_ARCHITECTURE.md`](TECHNICAL_ARCHITECTURE.md) — proposed assemblies, ownership of save state, extension boundaries, and system contracts.
9. [`MOD_INTEGRATION_PLAN.md`](MOD_INTEGRATION_PLAN.md) and [`COMPATIBILITY.md`](COMPATIBILITY.md) — interaction model, DLC policy, RWT constraints, and the exact profile boundary.
10. [`research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) and [`research/reviews/mods/3005289691-nova.rimworldtogether.md`](research/reviews/mods/3005289691-nova.rimworldtogether.md) — local profile comparison, story-facing co-op translation, and sourced RWT/VGE findings.
11. [`RESEARCH.md`](RESEARCH.md) and [`UNIVERSE_ADAPTATION.md`](UNIVERSE_ADAPTATION.md) — source provenance, source-to-design translation, and what remains unreviewed.
12. [`research/PREPRODUCTION_ACCEPTANCE_STANDARD.md`](research/PREPRODUCTION_ACCEPTANCE_STANDARD.md), [`research/OPTIONAL_MOD_SUPPORT_POLICY.md`](research/OPTIONAL_MOD_SUPPORT_POLICY.md), [`research/CONTENT_ACCESSIBILITY_BRIEF.md`](research/CONTENT_ACCESSIBILITY_BRIEF.md), and [`research/provenance-register.csv`](research/provenance-register.csv) — measurable quality bar, optional-mod boundary, content/accessibility requirements, and source/asset tracking.
13. [`research/FAN_SUMMARY_GUIDE.md`](research/FAN_SUMMARY_GUIDE.md), [`research/KANE_PIXELS_FAN_CLIFF_NOTES.md`](research/KANE_PIXELS_FAN_CLIFF_NOTES.md), [`research/KANE_PIXELS_LORE_STORY_MAP.md`](research/KANE_PIXELS_LORE_STORY_MAP.md), [`research/kane-pixels-video-index.csv`](research/kane-pixels-video-index.csv), and [`research/reviews/README.md`](research/reviews/README.md) — owner-approved fan-summary route, official series scope, concise story notes for all 23 playlist uploads, and direct-review records. Keep fan interpretation labeled and do not infer story order from playlist order. The A24 feature has a separate first-pass fan-summary story note in [`research/reviews/a24-feature/feature-review.md`](research/reviews/a24-feature/feature-review.md); it is not a direct viewing. Keep both tracks short and story-focused: people, events, memorable spaces, mysteries, and useful scenario or quest ideas. Full video or feature viewing is optional when the fan summary answers the design question.
14. [`research/rimworld-server-mod-inventory.csv`](research/rimworld-server-mod-inventory.csv) and the [294-mod workbook](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx) — source/profile row data. Do not treat a preliminary workbook description as a verified mod-page audit.

## Feature-to-document route

Every planned feature must have a stable ID in [`FEATURE_TRACEABILITY.md`](FEATURE_TRACEABILITY.md), with its design, lore/source, exact 294 profile rows, DLC/RWT boundary, presentation guidance, planned files, and acceptance proof linked there. A preliminary inventory mapping is not a verified integration.

| Work area | Read first | Cross-check before coding |
| --- | --- | --- |
| New-game start, corporate progression, objective loop | `GAME_DESIGN.md` | `ROADMAP.md`, TODO Phase 2 |
| Scenario framework and alternate starts | `SCENARIOS.md` | `GAME_DESIGN.md`, `SYSTEMS_CATALOG.md`, `MOD_INTEGRATION_PLAN.md`, RWT audit, TODO Phases 0.5, 2, 3, and 6 |
| Rooms, staff jobs, hiring, training, morale, security | `SYSTEMS_CATALOG.md` | `GAME_DESIGN.md`, `MOD_INTEGRATION_PLAN.md` |
| Gate machine, power, opening window, recall, extraction | `GAME_DESIGN.md` | `TECHNICAL_ARCHITECTURE.md`, TODO Phase 2–3 |
| Procedural space, coordinates, map persistence, propagation, return clues | `UNIVERSE_ADAPTATION.md` | `TECHNICAL_ARCHITECTURE.md`, TODO Phase 3 |
| Expeditions, contracts, cargo, recovery, payment, evidence, sale/detention | `SYSTEMS_CATALOG.md` | `MOD_INTEGRATION_PLAN.md`, TODO Phase 3 |
| Entities, anomalies, investigation, containment | `UNIVERSE_ADAPTATION.md` | `RESEARCH.md`, `SYSTEMS_CATALOG.md`, TODO Phase 3 |
| RWT branches, visiting, trade/aid, research dossiers | `research/reviews/mods/3005289691-nova.rimworldtogether.md` | `research/RWT_AND_GRAVSHIP_FEASIBILITY.md`, `COMPATIBILITY.md`, `MOD_INTEGRATION_PLAN.md`, TODO Phase 4 |
| Gravship/off-world extension | `research/RWT_AND_GRAVSHIP_FEASIBILITY.md` | `MOD_INTEGRATION_PLAN.md`, `COMPATIBILITY.md` |
| DLC support | `COMPATIBILITY.md` | TODO Phase 4 and the selected DLC's installed Defs |
| Existing profile mod interaction | `research/rimworld-server-mod-inventory.csv` + workbook | `SOURCE_REGISTER.md`, review template, `COMPATIBILITY.md`; verify exact package page/source before patching |
| Full-company interface, accessibility, localization | `SYSTEMS_CATALOG.md` | `GAME_DESIGN.md`, TODO Phase 5 |
| Build/package/release | `TECHNICAL_ARCHITECTURE.md` | TODO Phases 1 and 6 |

## Evidence and status vocabulary

- **Verified local snapshot:** read directly from a named local configuration/file on the recorded date. This does not mean runtime behavior was tested.
- **Verified upstream statement:** stated on an official publisher/project page or release note; include the direct URL and check date.
- **Preliminary design mapping:** an intended use inferred from a mod name/category or broad feature; it is not a compatibility result.
- **Inferred behavior:** a design conclusion drawn from sources; label the reasoning and do not present it as an upstream promise.
- **Pending:** exact source review, owner decision, code, or runtime evidence is missing.

Update the file that owns the decision first, then add a link from its navigation parent. Keep one canonical detailed record for each topic; use links instead of copying large mutable specifications into multiple files.

## Current gate

The exact local server/client mod ID set and order match at 294 entries. The local RimWorld build and exact server archive are identified; the client artifact is separately pinned by hash. The server does not enforce the mod list, and no compatibility run has been performed for this mod. Seventeen profile rows now have individual source-fact notes; the other 277 still need review, and none has combined-profile runtime clearance. All 23 indexed uploads have concise secondary story summaries in `research/KANE_PIXELS_FAN_CLIFF_NOTES.md`, and the separate A24 fan-summary story note is linked in `research/reviews/a24-feature/feature-review.md`. The four existing video notes are partial direct reviews; full viewing is optional unless an important design question remains unresolved. `Faultline.mov` stays a supplemental lead with its cause unresolved; `Simpsons` is outside the selected Kane creator scope. Keep the source work story-first: people, events, spaces, mysteries, and useful scenario ideas. D1–D9 are recorded; do not reopen them unless the owner changes direction. Complete every remaining Gate 0 research, design, and runtime-evidence item in the TODO before creating the source project or claiming the profile is supported. The displayed title is exactly `Rimrooms - Async Industries`; leave author/publisher metadata blank until assigned.
