# Rimrooms - Async Industries: source and document register

This file is the navigation index for the research and design materials a future implementation agent must consult. Read it alongside [`AGENTS.md`](../AGENTS.md) and [`AI_BUILD_HANDOFF.md`](AI_BUILD_HANDOFF.md). Source observations, design interpretations, and unverified runtime behavior must stay clearly distinguished.

## Project source-of-truth documents

| Topic | Canonical document | Supporting documents |
| --- | --- | --- |
| Work sequence and coding-start gate | [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) | [`ROADMAP.md`](ROADMAP.md), [`AI_BUILD_HANDOFF.md`](AI_BUILD_HANDOFF.md) |
| Player campaign and primary loop | [`GAME_DESIGN.md`](GAME_DESIGN.md) | [`SYSTEMS_CATALOG.md`](SYSTEMS_CATALOG.md), [`ROADMAP.md`](ROADMAP.md) |
| Starting campaign scenarios | [`SCENARIOS.md`](SCENARIOS.md) | [`GAME_DESIGN.md`](GAME_DESIGN.md), [`SYSTEMS_CATALOG.md`](SYSTEMS_CATALOG.md), [`MOD_INTEGRATION_PLAN.md`](MOD_INTEGRATION_PLAN.md) |
| Proposed code and save boundaries | [`TECHNICAL_ARCHITECTURE.md`](TECHNICAL_ARCHITECTURE.md) | TODO, compatibility plan |
| Existing-mod integration | [`MOD_INTEGRATION_PLAN.md`](MOD_INTEGRATION_PLAN.md) | [`COMPATIBILITY.md`](COMPATIBILITY.md), profile CSV/workbook |
| Local RWT server/client snapshot and VGE feasibility | [`research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) | [`COMPATIBILITY.md`](COMPATIBILITY.md), RWT source URLs below |
| Universe observations and design adaptation | [`UNIVERSE_ADAPTATION.md`](UNIVERSE_ADAPTATION.md) | [`RESEARCH.md`](RESEARCH.md), source review records below |

## Primary creative references

| Source | Direct reference | Local index/review location | Research status |
| --- | --- | --- | --- |
| Kane Pixels official Backrooms playlist | [Official playlist](https://www.youtube.com/playlist?list=PLVAh-MgDVqvDUEq6qDXqORBioE4Yhol_z) | [`research/kane-pixels-video-index.csv`](research/kane-pixels-video-index.csv); each row now has a direct `source_url` | 23 entries indexed; timestamped video-by-video analysis is pending. |
| Individual Kane Pixels official uploads | Open each row's `source_url`; it points to the official YouTube watch page for that video ID. | Save `docs/research/reviews/kane-pixels/<video_id>.md` using the [video review template](research/reviews/templates/kane-video-review-template.md); see [review-folder instructions](research/reviews/README.md). | First video's transcript export was unavailable in the inspected player. Do not infer transcript text; review the video directly and record timestamps. |
| A24 Backrooms feature | [Official film page and synopsis](https://a24films.com/films/backrooms) | [`RESEARCH.md`](RESEARCH.md); save `docs/research/reviews/a24-feature/feature-review.md` using the [feature review template](research/reviews/templates/a24-feature-review-template.md). | Official synopsis/interview/home-video sources were reviewed for high-level context. Full feature viewing and timestamped analysis are pending. |
| A24 creator interview | [“Thirty Thousand Square Feet with Kane Parsons & James Wan”](https://a24films.com/notes/2026/05/thirty-thousand-square-feet-with-kane-parsons-james-wan) | [`RESEARCH.md`](RESEARCH.md) | Source-based high-level notes exist; distinguish the interview's statements from game design interpretation. |
| A24 home-video extras | [Official A24 Blu-ray listing](https://shop.a24films.com/products/backrooms-blu-ray) | [`RESEARCH.md`](RESEARCH.md) | Listing reviewed to identify available production extras; it is not a substitute for viewing the feature. |

The project direction names Kane Pixels' continuity and the A24 feature as primary creative references. Keep the wider community Backrooms corpus separate and label it when used. See the provenance and uncertainty rules in [`RESEARCH.md`](RESEARCH.md).

## RimWorld, multiplayer, and mod references

| Source | Direct reference / local path | Purpose and status |
| --- | --- | --- |
| Local 294-entry server profile export | [`research/rimworld-server-mod-inventory.csv`](research/rimworld-server-mod-inventory.csv) | Snapshot of the selected profile with load order, name, Workshop ID, and a direct Workshop URL where the ID is numeric. It is not proof that every mod was researched or tested. |
| Original local configuration/source locations | See [RWT and gravship feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) for exact paths to the server `ModConfig.json`/executable, client `ModsConfig.xml`, and installed Workshop `About.xml` files. | These are machine-local research inputs; the repository CSV/audit preserve the derived snapshot. They are not copied or redistributed as mod content. |
| 294-row integration register | [`../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx`](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx) | Preliminary use, dependency, and compatibility mapping; most per-mod rows still need exact page/API review. |
| Mod review procedure | [`research/reviews/README.md`](research/reviews/README.md) and [mod review template](research/reviews/templates/mod-review-template.md) | Save each verified Workshop/source review as `docs/research/reviews/mods/<workshop_id>-<package_id>.md`. |
| RWT official Workshop description | [RimWorld Together Workshop page, ID 3005289691](https://steamcommunity.com/sharedfiles/filedetails/?id=3005289691) | Describes separate colonies and advertised co-op activities. Detailed visit, item, scenario, and transfer behavior must be checked against the exact pinned build. |
| RWT upstream repository and releases | [Repository](https://github.com/RimWorld-Together/Rimworld-Together); [release 26.8.31.1](https://github.com/RimWorld-Together/Rimworld-Together/releases/tag/26.8.31.1) | Source and release notes; the local server hash is not yet identified as that release. |
| Local RWT/profile audit | [`research/RWT_AND_GRAVSHIP_FEASIBILITY.md`](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) | Client/server profile IDs and order match in the dated snapshot; enforcement is disabled; runtime behavior and exact local RWT build remain unresolved. |
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
