# RimWorld 1.6 package and room-generation findings

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


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

## 1.6 generation and world-system candidates

The official [Ludeon 1.6 Modder Primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub) provides candidate names and concepts. These are investigation paths, not a frozen implementation design:

| Primer section | Documented names or guidance | Rimrooms use to investigate | Boundary |
| --- | --- | --- | --- |
| Structure layouts and Prefabs (Primer sections 78–92) | `LayoutRoomDef`, `RoomContentsWorker`, `RoomPartDef`; reusable room parts and XML-defined layouts/prefabs. | Author reusable Backrooms room families and furnishings. | The Primer gives no constructor or full method signature. Validate placement, tags, and save behavior in a small prototype. |
| Map generation (Primer sections 40–77) | `TileMutatorDef`, `WorldGenStep_Mutators`, `MapComponent`; mutator workers should not hold state, so stateful behavior belongs in a component. `MapGenUtility.GetClearRects`, `TryGetRandomClearRect`, `TryGetLargestClearRect`, and `TryGetClosestClearRectTo` are named helpers. | Build finite seeded sites, add bounded spatial variations, and retain site-specific state. | The Primer does not certify map unload/reload persistence or signatures for these methods. Prototype and inspect installed 1.6 assemblies before depending on them. |
| Map-generation ordering | 10–100 base grids; 200–300 natural terrain; 400–500 critical large structures; 600 gravship reservation; 700–800 noncritical large structures; 850 player start; 900–1200 noncritical generation; 1500 fog; 1600+ features that must be unfogged; 1700 gravship marker. Edifices added at 1600+ may require manual fog-grid updates. | Place required room structures, exits, and return clues at deliberate stages while preserving visibility/fog rules. | Treat this as 1.6 ordering guidance. Confirm exact interaction with each generated site, Odyssey, and the active mod profile. |
| Pathfinding refactor (Primer sections 93–99) | `PathRequest`; submit a request rather than make an immediate synchronous path query. | Validate pawn routes to exits, mission objectives, and return points without blocking map generation. | No request-construction signature is supplied. Do not assume a particular callback/lifecycle until the prototype. |
| Planet layers (Primer sections 19–32) | `PlanetLayerDef`, `PlanetLayer`, `PlanetTile`, `WorldGrid.RegisterPlanetLayer`, `WorldGenSteps`, `WorldDrawLayers`, `WorldTabs`, `PlanetLayerSettingsDef`, and `ScenPart_PlanetLayerFixed`. | Consider a separate layer only if the Backrooms needs a world-scale view that ordinary sites/maps cannot support. | The Primer names these but gives no formal `RegisterPlanetLayer` signature. A custom planet layer is optional and not a gate foundation. |
| Map state / used cells | The literal example `MapGenerator.GetOrGenerateVar<List<CellRect>>(MapGenerator.UsedRectsName)`. | Avoid overlap with occupied/generated cells in a map pass. | This is the exact invocation shown in the Primer; it is not proof of whole-site persistence. |

The Primer’s named identifiers are documented 1.6 investigation targets, not complete API signatures. Its exact example is `MapGenerator.GetOrGenerateVar<List<CellRect>>(MapGenerator.UsedRectsName)`; it supplies no constructor/signature for `WorldGrid.RegisterPlanetLayer`, the map helper methods, or `PathRequest`.

The installed Core XML was also inspected on the pinned 1.6 build. `CommonMapGenerator.xml` contains the `MapGeneratorDef`, `genSteps`, `GenStepDef`, `order`, and `genStep Class` Def shapes and repeats the stage ordering. `AmbushHidden.xml` links a `SitePartDef` to a `GenStepDef` at order 1600. Core world-object definitions use `Site` and `PocketMapParent`. These observations confirm installed data/Def patterns only; they do not prove that Rimrooms should subclass a particular type or rely on its save lifecycle.

The exploration recommendation is a Rimrooms-owned coordinate/room graph with finite on-demand maps, explicit exits and recovery cues, and saved site history. Keep a custom planet layer optional. Extend the atlas by revealing additional seeded coordinates and preserve each visited location. A map component or a world/site object can be evaluated as a persistence owner, but deterministic replay, unload/reload, migration, multiplayer branch ownership, and return-path validation remain prototype work.

The 294-profile source review identifies relevant existing-mod research leads including Move Your Monolith, Stargates!, Go Explore, No Quests Without Comms, Anomaly Research Asteroid, Sparkling Worlds, Buildable Terrain, Permeable Terrain, More Vanilla Biomes, Change Map Edge, Dubs Mint Minimap, Map Preview, and both VGE chapters. They are examples and interaction risks, not code or art to copy. See their exact row IDs and test hypotheses in the [priority interaction map](PRIORITY_PROFILE_INTERACTIONS.md) and the [gravship profile review](GRAVSHIP_PROFILE_INTERACTIONS.md).
