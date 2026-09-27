# Rimrooms - Async Industries: source and document register

This file is the navigation index for the research and design materials a future implementation agent must consult. Read it alongside [`AGENTS.md`](../AGENTS.md) and [`AI_BUILD_HANDOFF.md`](AI_BUILD_HANDOFF.md). Source observations, design interpretations, and unverified runtime behavior must stay clearly distinguished.

## Project source-of-truth documents

| Topic | Canonical document | Supporting documents |
| --- | --- | --- |
| Work sequence and coding-start gate | [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) | [`ROADMAP.md`](ROADMAP.md), [`AI_BUILD_HANDOFF.md`](AI_BUILD_HANDOFF.md) |
| Settled owner choices for implementation | [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) | TODO Phase 0 and `AI_BUILD_HANDOFF.md` |
| Measurable acceptance, optional-mod policy, content/accessibility, provenance register | [`research/PREPRODUCTION_ACCEPTANCE_STANDARD.md`](research/PREPRODUCTION_ACCEPTANCE_STANDARD.md); [`research/OPTIONAL_MOD_SUPPORT_POLICY.md`](research/OPTIONAL_MOD_SUPPORT_POLICY.md); [`research/CONTENT_ACCESSIBILITY_BRIEF.md`](research/CONTENT_ACCESSIBILITY_BRIEF.md); [`research/provenance-register.csv`](research/provenance-register.csv) | TODO Phase 0.1; feature map and release evidence |
| Kane Pixels official series continuity and story review | [`research/KANE_PIXELS_LORE_STORY_MAP.md`](research/KANE_PIXELS_LORE_STORY_MAP.md); [`research/kane-pixels-video-index.csv`](research/kane-pixels-video-index.csv); [`research/reviews/kane-pixels/`](research/reviews/kane-pixels/) | TODO Phase 0.2; source-backed lore and quest/feature traceability |
| Feature/source/mod/style/file traceability | [`FEATURE_TRACEABILITY.md`](FEATURE_TRACEABILITY.md) | `SYSTEMS_CATALOG.md`, `MOD_INTEGRATION_PLAN.md`, the 294-row register |
| Player campaign and primary loop | [`GAME_DESIGN.md`](GAME_DESIGN.md) | [`SYSTEMS_CATALOG.md`](SYSTEMS_CATALOG.md), [`ROADMAP.md`](ROADMAP.md) |
| Starting campaign scenarios | [`SCENARIOS.md`](SCENARIOS.md) | [`GAME_DESIGN.md`](GAME_DESIGN.md), [`SYSTEMS_CATALOG.md`](SYSTEMS_CATALOG.md), [`MOD_INTEGRATION_PLAN.md`](MOD_INTEGRATION_PLAN.md) |
| Proposed code and save boundaries | [`TECHNICAL_ARCHITECTURE.md`](TECHNICAL_ARCHITECTURE.md) | TODO, compatibility plan |
| Existing-mod integration | [`MOD_INTEGRATION_PLAN.md`](MOD_INTEGRATION_PLAN.md) | [`COMPATIBILITY.md`](COMPATIBILITY.md), profile CSV/workbook |
| Local RWT server/client snapshot and VGE feasibility | [`research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) | [`COMPATIBILITY.md`](COMPATIBILITY.md), RWT source URLs below |
| Universe observations and design adaptation | [`UNIVERSE_ADAPTATION.md`](UNIVERSE_ADAPTATION.md) | [`RESEARCH.md`](RESEARCH.md), source review records below |

## Primary creative references

| Source | Direct reference | Local index/review location | Research status |
| --- | --- | --- | --- |
| Kane Pixels official Backrooms playlist | [Official playlist](https://www.youtube.com/playlist?list=PLVAh-MgDVqvDUEq6qDXqORBioE4Yhol_z) | [`research/kane-pixels-video-index.csv`](research/kane-pixels-video-index.csv); each row links to its official video and local note | 23 entries indexed; full story reviews remain pending. |
| Individual Kane Pixels official uploads | Open each row's `source_url`; it points to the official YouTube watch page for that video ID. | Each row links to `docs/research/reviews/kane-pixels/<video_id>.md`; see [review-folder instructions](research/reviews/README.md). | First four notes are partial; remaining notes are placeholders. Captions/transcripts are supporting material only when actually available. |
| A24 Backrooms feature | [Official film page, synopsis, and current Watch Now links](https://a24films.com/films/backrooms) | [`research/reviews/a24-feature/feature-review.md`](research/reviews/a24-feature/feature-review.md); use the [feature review template](research/reviews/templates/a24-feature-review-template.md). | Official viewing options are linked from the film page as of 2026-09-27. Full feature review is pending and remains separate from the Kane Pixels series. |
| A24 creator interview | [“Thirty Thousand Square Feet with Kane Parsons & James Wan”](https://a24films.com/notes/2026/05/thirty-thousand-square-feet-with-kane-parsons-james-wan) | [`RESEARCH.md`](RESEARCH.md) | Source-based high-level notes exist; distinguish the interview's statements from game design interpretation. |
| A24 home-video extras | [Official A24 Blu-ray listing](https://shop.a24films.com/products/backrooms-blu-ray) | [`RESEARCH.md`](RESEARCH.md) | Listing reviewed to identify available production extras; it is not a substitute for viewing the feature. |

The selected creative references are Kane Pixels' continuity and the A24 feature, adapted indirectly. Broader community Backrooms canon is excluded from shipped content. If it is consulted for identification or provenance research, keep it clearly separated from the selected references. See the provenance and uncertainty rules in [`RESEARCH.md`](RESEARCH.md).

## RimWorld, multiplayer, and mod references

| Source | Direct reference / local path | Purpose and status |
| --- | --- | --- |
| Local 294-entry server profile export | [`research/rimworld-server-mod-inventory.csv`](research/rimworld-server-mod-inventory.csv) | Snapshot of the selected profile with load order, name, Workshop ID, and a direct Workshop URL where the ID is numeric. It is not proof that every mod was researched or tested. |
| Original local configuration/source locations | See [RWT and gravship feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) for exact paths to the server `ModConfig.json`/executable, client `ModsConfig.xml`, and installed Workshop `About.xml` files. | These are machine-local research inputs; the repository CSV/audit preserve the derived snapshot. They are not copied or redistributed as mod content. |
| 294-row integration register | [`../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx`](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx) | Preliminary use, dependency, and compatibility mapping; most per-mod rows still need exact page/API review. |
| Mod review procedure | [`research/reviews/README.md`](research/reviews/README.md) and [mod review template](research/reviews/templates/mod-review-template.md) | Save each verified Workshop/source review as `docs/research/reviews/mods/<workshop_id>-<package_id>.md`. |
| RWT official Workshop description | [RimWorld Together Workshop page, ID 3005289691](https://steamcommunity.com/sharedfiles/filedetails/?id=3005289691) | Describes separate colonies and advertised co-op activities. Detailed visit, item, scenario, and transfer behavior must be checked against the exact pinned build. |
| RWT upstream repository and releases | [Repository](https://github.com/RimWorld-Together/Rimworld-Together); [release 26.8.31.1](https://github.com/RimWorld-Together/Rimworld-Together/releases/tag/26.8.31.1) | Source and release notes; the local server archive digest matches this release's published Windows asset. Client behavior and API support still need review. |
| Local RWT/profile audit | [`research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) | Client/server profile IDs and order match; the local RimWorld build, server release asset, client DLL, and profile snapshots are pinned by version and hash. Runtime behavior remains untested; server enforcement is disabled. |
| Vanilla Gravship Expanded Chapter 1 | [Steam Workshop page, ID 3609835606](https://steamcommunity.com/sharedfiles/filedetails/?id=3609835606) | Optional Odyssey/VEF integration; retain native gravship systems and heed its compatibility warning. |
| Vanilla Gravship Expanded Chapter 2 | [Steam Workshop page, ID 3799737423](https://steamcommunity.com/sharedfiles/filedetails/?id=3799737423) | Optional Chapter 1 continuation; preserve its dependency chain and test the selected vehicle/space stack. |
| Vanilla Expanded Framework | [Steam Workshop page, ID 2023507013](https://steamcommunity.com/sharedfiles/filedetails/?id=2023507013) | Dependency/API reference for the selected VGE stack; not a Rimrooms core dependency. |
| RimWorld mod package/build guidance | [Ludeon modding tutorial](https://ludeon.com/forums/index.php?topic=33219.0); [1.6 update guidance](https://rimworldwiki.com/wiki/Modding_Tutorials/RimWorld_1.6_Mod_Updates); [`About.xml`](https://www.rimworldwiki.com/wiki/Modding_Tutorials/About.xml); [folder structure](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_folder_structure) | Recheck against installed RimWorld 1.6 files before locking package folders, load folders, compiler targets, and metadata. |
| RimWorld 1.6 and Odyssey | [Official Steam announcement](https://store.steampowered.com/news/posts/?appgroupname=RimWorld&appids=294100&enddate=1753200027&feed=steam_community_announcements) | Distinguishes the free 1.6 update from the optional Odyssey DLC. Record actual installed build/DLC evidence before implementation. |

RWT wiki pages returned HTTP 403 during the 2026-09-27 research snapshot. Their existence in older notes must not be presented as successful verification. Use the official Workshop description and upstream release/source, then verify exact visit, aid, transfer, settings, scenario-join, and save/reconnect semantics in the pinned environment. Avoid importing assumptions from the separate `rwmt/Multiplayer` project.

## Evidence records and naming

- Store reviewed source notes under `docs/research/reviews/` and include the source URL, access/review date, exact version/build, timestamps or page section, observations, uncertainties, and a separate game-design translation.
- Use `kane-pixels/<video_id>.md` for each video, `a24-feature/feature-review.md` for the film, and `mods/<workshop_id>-<package_id>.md` for each mod. Templates and field guidance are in [`research/reviews/README.md`](research/reviews/README.md).
- Change index status only after the matching review record exists. Use `Pending`, `Reviewed—source facts recorded`, or `Runtime tested—profile details recorded`; a workshop-page review alone is never a compatibility test.
- For a new feature, link from its canonical design document to its specific research record. Do not paste mutable source logs into multiple summaries.
- Label statements as **source fact**, **local snapshot**, **interpretation**, **design decision**, or **runtime result**. Add a direct URL or a repository-relative file path for each substantive claim.
