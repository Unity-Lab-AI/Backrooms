# RimWorld 1.6 package and room-generation findings

**Checked:** 2026-09-27  
**State:** Gate 0 research only. No Rimrooms package or gameplay implementation was created.

## What the 1.6 sources establish

Ludeon's [1.6 Modder Primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub) documents reusable room layouts, room parts, prefabs, map-generation stages, and variable tick rates. The current [mod-folder guide](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_Folder_Structure) describes `About/About.xml`, version folders, and conditional `LoadFolders.xml` entries. The guide is community-maintained; its folder rules were compared with the installed 1.6 game data and all 294 active profile entries rather than taken on trust.

The official [1.6/Odyssey announcement](https://store.steampowered.com/news/posts/?appgroupname=RimWorld&appids=294100&enddate=1753200027&feed=steam_community_announcements) confirms that 1.6 is a free base-game update and Odyssey is separate DLC. The mod must therefore remain complete on Core, with Odyssey-specific content isolated behind its package ID.

For this project, the 1.6 generation features support a simple design direction:

- Keep each Backrooms coordinate finite and seeded, and save its map for revisits. “Endless” play comes from finding more coordinates over time, not from one huge map.
- Use RimWorld's room-layout and prefab content for reusable room shapes and furnishings. Use project-owned coordinate and route records to connect rooms, control variation, and preserve discoveries.
- Let normal map generation place terrain and required structures, then validate routes and return clues before an expedition becomes playable. Keep generation limits and a recovery path visible in the design.
- Use delta-based ticks where a future system does not need work every game tick. The exact hook, room-layout types, and save behavior still need a small post-Gate-0 prototype against the pinned assemblies.

These are feasibility findings, not confirmed implementation APIs. Exact signatures, map persistence, coordinate transitions, deterministic replay, and performance have not yet been proved in a Rimrooms prototype.

## Installed package and load-folder audit

The [repeatable audit script](../../tools/research/audit-installed-mod-metadata.ps1) read only the selected profile's installed `About/About.xml` and optional `LoadFolders.xml` files. It does not copy mod files into Rimrooms. Its dated outputs are the [294-row metadata snapshot](installed-mod-metadata-2026-09-27.csv) and the [declared relationship graph](installed-mod-relationships-2026-09-27.csv).

Results for the pinned local profile:

- All 294 rows have parseable local metadata: 288 installed Workshop entries and Core plus the five installed DLC packages.
- The 288 Workshop entries have 286 local `About.xml` declarations that include RimWorld 1.6. Two do not: **SF Grim Reality** lists through 1.4; **Bo's Milkable Animals** lists through 1.5. Their current publisher pages have been checked separately in their review records. A local declaration is version evidence, not a guarantee that a mod will or will not run.
- The 294 records contain 226 hard-dependency declarations. Every target package ID is present in this selected profile. No two rows declare the same package ID.
- The metadata declares 616 `loadAfter` and 12 `loadBefore` references. Of these 252 point outside the active 294-entry profile; keep those as ordering clues, not as proof those other packages are installed.
- There are 60 declared `incompatibleWith` references, and none targets another active package in this snapshot. This checks declared metadata only; it cannot rule out undocumented conflicts.
- 106 packages have a `LoadFolders.xml`. The audit found absent folder paths in two packages: Vehicle Framework refers to `1.6/Compatibility/Anomaly` and `1.4/_Biotech`; Prison Labor refers to `1.6/Biotech` and `1.5/Biotech`. Their pages or public source trees also need review; the missing folders do not by themselves establish a startup failure.

The exact game and profile paths, build numbers, and input configuration hashes are in the [RWT and gravship feasibility audit](RWT_AND_GRAVSHIP_FEASIBILITY.md). Each row in the metadata snapshot includes the local source path, `About.xml` SHA-256, version declarations, dependencies, ordering declarations, and missing conditional folder paths. The audit can be repeated with the same inventory and local Steam/RimWorld roots.

## What remains open

This audit does not review every Workshop description or update date, source code/API, license, asset terms, patch interaction, or runtime behavior. It is not a compatibility certification. The remaining page-by-page and high-risk source review is still required for all 294 profile entries. See the [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md), [mod reviews](reviews/mods/), [source register](../SOURCE_REGISTER.md), and [feature traceability map](../FEATURE_TRACEABILITY.md).

The only named absence checks here are the two packages above. The full load-order graph, patch behavior, inactive/optional references, game logs, and cross-mod results still need review. RWT, the two gravship chapters, and the world/map, storage, prisoner, power, research, work, and quest systems remain the highest-priority API/runtime targets.
