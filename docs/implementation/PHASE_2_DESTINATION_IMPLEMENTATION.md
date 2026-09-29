# Phase 2: destination generation implementation

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** implemented source for the bounded first destination; owner-launched runtime acceptance remains pending. The lead owns compilation and the [current build record](PHASE_2_BUILD_RECORD.md). This agent performed source inspection and edits only: no build, tests, game launch, profile change or compatibility claim.

## Task and source record

**Assigned 2026-09-28.** The lead assigned `Generation/*` and this record to the Core source-review agent, then explicitly added the `RR_BackroomsSite` launch-target flag. The prior generation owner confirmed its last edit was confined to fixture XML. Features: **RR-SPACE, RR-EXP, RR-EVD, RR-THREAT, RR-STYLE**. The [Phase 2 task](PHASE_2_VERTICAL_SLICE_TASK.md), [AI-01 room inventory](../FIRST_SLICE_CONTENT_INVENTORY.md#first-destination-ai-01), [generation/failure order](../PROCEDURAL_SPACE_CONTRACT.md#building-a-destination), [first playable](../FIRST_PLAYABLE_CONTRACT.md) and [state dictionary](../CAMPAIGN_STATE_DICTIONARY.md) control the scope.

Exact source: profile row **4**, package **`Ludeon.RimWorld`**, local `Assembly-CSharp.dll` SHA-256 **`5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`**, ILSpy **9.1.0.7988**. This work adds original arrangements of native runtime Defs; no Core code, XML, textures or other proprietary files are copied into the mod. All DLC and optional mods remain outside this source-backed baseline.

**Result:** deterministic bounded graph candidates and explicit precommit fallback; six required room families and up to two optional dead ends; native furnishings, readable clue records and physical salvage; reserved routes/objective cells; saved generation/content receipts; normal native world-travel guards. The lead owns English text, UI pickup integration, canonical contracts, package art/version and compilation. Gate 2 remains open until its acceptance evidence exists.

## Implementation ownership and callers

| File | Responsibility |
| --- | --- |
| [DestinationService.cs](../../src/RimroomsAsyncIndustries/Generation/DestinationService.cs) | Validate coordinate/graph/owner, select a bounded engine tile, create or reuse one saved map, return its stable entry. |
| [RoomLayoutPlanner.cs](../../src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs) | Pure deterministic candidate planning and projected route checks before graph commitment. |
| [RimroomsDestinationMapParent.cs](../../src/RimroomsAsyncIndustries/Generation/RimroomsDestinationMapParent.cs) | Persist identity, versions, fingerprint, generation/layout receipts, candidate, cells, anchor and failure; reject ordinary travel/automatic removal. |
| [GenStep_BackroomsDestination.cs](../../src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs) | Place shells, corridors, native doors, fixtures, contents and fog roots; verify placed routes and clue access. |
| [RoomContentBuilder.cs](../../src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs) | Arrange native furniture/floor accents and one actual salvage object in optional storage. |
| [RoomContentMapComponent.cs](../../src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs) | Save clue IDs, actual landmarks and observation flags; draw visible-landmark labels/tooltips. |
| [RR_BackroomsSites.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/WorldObjectDefs/RR_BackroomsSites.xml) | Register the saved custom owner/generator and `validLaunchTarget=false`. |

Related lead-owned package files are [generation registration](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/MapGeneratorDefs/RR_BackroomsGeneration.xml), [fixture Defs](historical-content/0.2.0/1.6/Defs/ThingDefs_Buildings/RR_BackroomsFixtures.xml), and [English text](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_Generation.xml).

The expedition caller preflights crew, cargo, capacity and gate readiness before `DestinationService.EnsureSite(campaign, coordinate, out map, out entry)`. Generation never transfers crew/items. Investigation owns the physical route recording at `OfficeEvidenceCell`; this generator does not mint it. `RoomContentMapComponent.Clues` exposes `Id`, `RoomIndex`, `Landmark`, `Salvage`, `Observed`, `Label` and `Description`. UI pickup uses the actual observed salvage Thing and the normal capacity/reservation/pickup job, never a remote inventory copy. The lead reports Atlas clue listings and expedition salvage pickup are wired to this API.

## Deterministic planning and commitment

1. Require a positive-version coordinate owned exactly once by the operating branch. A missing site reference with a Ready/surveyed record, matching registered owner or matching loaded map fails before graph mutation.
2. Generate rooms only when the list is empty, status is `Discovered`, and there is no owner. A nonempty saved graph is validated and preserved, including the earlier 14x14 graph format.
3. Planner version **2** examines **three** candidates in fixed order, derived from coordinate ID/seed, generator/library versions, planner version and candidate number. No global random state is consumed. Candidates vary rotation/mirroring, 6-8 room count, proportions, spine versus one return loop, and optional-family placement. The required family sequence stays readable in this first slice.
4. Candidates require exactly six mandatory families, unique contiguous IDs, reciprocal cardinal links, even room dimensions **10-16 cells**, no overlap, connectivity and at most one loop. New optional rooms are leaves. A pure **60x60** floor projection checks all room centers through planned one-cell doors, three-cell corridors and center supports.
5. After three rejected candidates, examine one explicit **six-room, 14x14, unrotated loop**. If it fails, refuse with `RR_Generation_NoSafeCandidate`. No graph, map, owner, crew or cargo is committed during candidate/fallback checks. Fallback never applies to an existing graph/map.
6. Commit the selected graph once. Its fingerprint covers ID/seed/versions, room families/indexes, dimensions/positions and sorted links. Any later failure retains it; no alternate candidate is selected.
7. Examine at most **512** spread-out surface tiles, accepting only Core-valid, unoccupied, map-free land. Prefer a temperate forest/swamp; otherwise retain the first other valid tile in the sample. This is an engine address, not an ordinary travel destination.
8. Register one MapParent, save candidate/planner/content provenance and the generation-attempt receipt, then request one Core **60x60** map. The GenStep has its own layout-start receipt so retry cannot clear a partial map.
9. Set `LayoutReady` only after the actual anchor, entry/return/office cells, every room and every clue/salvage landmark are reachable. Only then can the caller enter.

`candidateIndex=-1` means an existing graph did not match a current candidate; it is not relabeled or rerolled. Planner/content versions are extra provenance, not permission to reinterpret saved coordinate generator/library versions.

## Physical room content

All arrangements and clue text are original Rimrooms material. Native Defs are looked up at runtime. Rooms have stable content seeds and three floor/placement variants. `Rand.PushState`/`PopState` bounds incidental native Thing-creation randomness. Quality is Normal where supported; condition varies deterministically from 65% to 89%. Revisit never restocks.

| Family | Physical content | Purpose |
| --- | --- | --- |
| Threshold | Two stools, saved return anchor and separate arrival/return cells | Arrival and physical extraction point. |
| Survey Lobby | Small table, chair and plant pot | Survey station and clue directing the player to coordinate/mission information in Operations. |
| Office Copy | Two tables, two chairs, optional pot; clear evidence slot | Repeated workstations and the separately owned route recording. |
| Service Passage | Shelf and disconnected standing lamp | Route-tag teaching junction. |
| Borrowed Corridor | Paired pots in a narrow/wide room | Ordinary landmarks around the separately owned distortion. |
| Storage Nook, optional | Shelf plus 12 steel, one minified stool or one minified dining chair | One actual capacity-bound salvage object; native minification keeps the original furniture inside its holder. |
| Utility Room, optional | Disconnected standing lamp and stool | A dead-end environmental clue, with no mandatory control puzzle. |
| Return Gallery | Paired stools, sometimes a pot | A text-readable return-route landmark. |

Shells use concrete with paved/metal stripes or insets, steel walls, constructed roofs and a center support. Core deep water remains an impassable exterior placeholder. Props avoid a reserved three-cell route cross and the saved objective/anchor cells; footprints require a clear margin. Post-placement validation checks a reachable standing/adjacent cell for each landmark, beyond graph connectivity alone.

Each room retains one `RR_SiteFluorescent` with radius-six no-grid lighting; one capped passive `RR_SiteClimateUnit` sits in utility or service. Enclosed rooms start at 20 degrees C. This heater is not active cooling. Native standing lamps have no supplied power and do not substitute for the fluorescent fixtures.

Clues save stable IDs (`coordinate:room:index:clue`), the actual Thing, origin cell, family, variant and observed flag. A clue becomes observed when its room is surveyed and the physical landmark is unfogged. Labels/tooltips follow still-spawned landmarks; no fog reveal, destroyed-object recreation or phantom label after pickup. Descriptive clues do not independently grant evidence or research rewards.

## Door, fog and threat boundary

Linked room boundaries have native steel doors, initially **closed**, player-accessible and un-forbidden. Generation invokes the public native hold-open command from `Building_Door.GetGizmos`; this sets the native saved hold flag without opening the door. First pawn approach opens it normally; hold-open then leaves that surveyed route open. The player can disable hold-open and deliberately close a route during pursuit. If an optional mod removes/replaces the command, a warning records the unavailable setup and native behavior remains in effect.

Only threshold entry/return are initial fog roots. Office Copy is not pre-revealed. Core `FloodFillerFog` stops at edifices with `MakeFog`; native doors supply that boundary. Structural validation accepts an un-forbidden player/factionless native door as openable, since `Standable` rejects a closed door that a pawn can normally open. Real expedition jobs still enforce their pawn-specific reachability.

The threat controller is lead-owned. A loop permits reaching Borrowed Corridor via Return Gallery before opening Office Copy doors. The lead reports that pursuit now selects a valid two-graph-room spawn with an actual `NoPassClosedDoors` route to the live crew; if no route exists, it retries after exploration rather than spawning and immediately withdrawing. This closes the source-level timing issue; runtime door/counterplay acceptance remains pending.

## Save, failure and access behavior

- Saved graph/map identity wins over current templates. Old maps receive no automatic furnishing/door retrofit. Additional receipts default for older saves; existing maps are reused only if identity/required-cell validation succeeds.
- Generation-attempt/layout-start flags survive partial failure. A missing map after Ready, survey, layout completion or an attempted generation refuses recreation. Core can catch a GenStep exception and return a partial map; it is retained and rejected as incomplete.
- Missing/changed Defs, incompatible footprints, unreachable landmarks, blocked objectives or invalid owners fail visibly. No postcommit fallback, reseed, map deletion, free stock or crew transfer occurs.
- The initial layout clears prior biome/content Things once on a new destination. It never clears headquarters or an existing destination. Profile acceptance must examine optional content inserted by earlier GenSteps.
- `ShouldRemoveMapNow` retains the owner/map. This one-site slice does not solve unlimited loaded-map capacity; see the finite Core ceiling and future unload/cache work in the [source review](PHASE_2_DESTINATION_SOURCE_REVIEW.md).
- `CanBeSettled=false`, `UseGenericEnterMapFloatMenuOption=false`, disabled caravan/transporter/shuttle menu overrides, `GravShipCanLandOn=false` and `validLaunchTarget=false` reject inspected normal Core entry/launch routes. Generic transport code is not patched. Third-party transports/direct arrival APIs that ignore these hooks require separate adapter review.
- Opt-in diagnostics measure actual map generation as `destination-generate` and placed/revisited route validation as `route-validation`. No performance results are claimed.

## Source facts and reproduction

Begin with [PHASE_2_DESTINATION_SOURCE_REVIEW.md](PHASE_2_DESTINATION_SOURCE_REVIEW.md). Additional bounded inspections:

| Source | Fact used |
| --- | --- |
| `Verse.MapComponent` | Public saved map tick/GUI lifecycle. |
| `Verse.TooltipHandler` | `TipRegion(Rect, Func<string>, int)` supports original clue tooltips. |
| `RimWorld.MinifyUtility` | `MakeMinified(Thing, DestroyMode)` preserves the original unowned Thing as `InnerThing`. |
| `RimWorld.CompQuality` | `SetQuality(QualityCategory, ArtGenerationContext?)`. |
| `Verse.GenGrid` | Standable/Walkable distinction requires a native openable-door case. |
| `RimWorld.GenStep_Fog`, `Verse.FloodFillerFog` | All-fog initialization, explicit roots and MakeFog flood boundaries. |
| `RimWorld.Building_Door` | Native hold-open command, saved flags, and no forced open when toggled. |
| `RimWorld.Planet.MapParent` | Public virtual caravan/transport/shuttle menu entry points. |
| `RimWorld.Planet.TileFinder` | Normal occupied-map gravship targeting requires `GravShipCanLandOn`. |
| `RimWorld.Planet.WorldObjectsHolder` | `AllWorldObjects` enables orphan-owner detection. |
| Core furniture/floor XML | Runtime names/sizes/stuff for the selected furniture and Concrete/PavedTile/MetalTile. |
| Core `WorldObjects.xml` lines 135 and 237 | Native `validLaunchTarget=false` examples, also confirmed by the separate read-only Def reviewer. |

Reproduce from the repo root, substituting an exact type above. Local inputs/output are not shipped:

```powershell
$rrManaged = 'C:/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed'
& .local/tools/ilspycmd.exe --version
Get-FileHash -Algorithm SHA256 -LiteralPath "$rrManaged/Assembly-CSharp.dll"
& .local/tools/ilspycmd.exe -t RimWorld.Building_Door -r $rrManaged -o .local/inspection-room-content "$rrManaged/Assembly-CSharp.dll"
```

Ignored output is in `.local/inspection-room-content/` and `.local/inspection-destination/`. This document is an original interface/control-flow summary. Source inspection cannot establish rendering, profile lifecycle behavior, balance or playability.

## Remaining work and acceptance

The slice now has native furnishings, limited meaningful graph/room variation, original clue records and optional salvage. Final architecture/terrain/fixture art, audio, broader template/modifier libraries, outposts and the later coordinate campaign remain separate work. Current content is not the final aesthetic or full procedural system.

After the owner launches through RimSort, record exact build/profile/save/seed/logs for these cases:

| Case | Required observation |
| --- | --- |
| Generation/variation | One owner/map; 6-8 rooms; shape/orientation/spine/loop/leaf results agree with seed and provenance. |
| Candidate failure | Bounded rejection reaches safe fallback only before commitment; saved/partial state is preserved. |
| Furniture/salvage | All props/clues fit and are reachable; storage pickup consumes real capacity and returns the actual item. |
| Door/fog | Only threshold initially visible; first crossing reveals rooms; hold-open and deliberate closing work during actual pursuit. |
| Routes/evidence | All rooms/anchor/objective remain usable; investigation creates exactly one recording; descriptive clues grant no duplicate reward. |
| Save/revisit | Map, doors, furniture, clue references, removed salvage and receipts persist without restock/regeneration. |
| Corruption/recovery | Invalid/missing owner/map/graph, changed Def, interrupted generation or destroyed anchor refuses while preserving contents. |
| World access | Caravan entry, transport/shuttle landing, launch targeting and native gravship selection cannot bypass the machine. |
| Environment/profile | Temperature, roofs, fixture damage, earlier GenSteps and optional transports have explicit observations. |
| Performance/capacity | Opt-in generation/route duration and retained-map growth are measured against the documented budget. |

No case is marked passed by source inspection or compilation.
