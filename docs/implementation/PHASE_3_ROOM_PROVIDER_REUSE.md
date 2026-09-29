# Native providers for generated Backrooms rooms

**Status:** source implemented against pinned RimWorld 1.6 Core definitions; integrated compile and all runtime acceptance remain pending. This record covers only new destination-map fixtures, floor variation, and failed-site recovery prerequisites.

## Task record

- **Features:** RR-SPACE, RR-EXP, RR-FAC, RR-STYLE, RR-GATE.
- **Baseline:** published checkpoint `5e8215cb4fb955bb329e64b7d0e3a8b6217f5886`, mod source/package `0.3.1-dev` per the [native provider task](PHASE_3_NATIVE_PROVIDER_TASK.md).
- **Owned source paths:** `src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs`, `src/RimroomsAsyncIndustries/Generation/FailedSiteRecovery.cs`, and `src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs`. This record is the sole owned document.
- **Affected callers:** `DestinationService.EnsureSite` records the current `RoomContentBuilder.ContentVersion` when it creates a new site (`DestinationService.cs:118`); the destination GenStep builds first-time maps; failed-site replacement preflight calls `RequiredRecoveryContentAvailable` (`FailedSiteRecovery.cs:80,284`).
- **Saved state:** no field, enum, coordinate identity, seed, graph, evidence ID, return cell, or map-owner schema changed. Existing `RoomContentMapComponent` version and clue references remain saved as before. The content recipe constant advances from 2 to 3 for newly generated arrangements.
- **Changed behavior:** future first-generation sites use real Core power, lighting and heating plus direct Core floor definitions. Power is consumable and can fail; the previous always-lit/free-warming custom fixtures are no longer placed on new maps.
- **Preserved behavior:** established maps are loaded as-is; `DestinationService` returns an existing owned map, and `TryBeginLayout` refuses rebuilding a ready or already-started layout. Existing custom Defs remain in the package so old saved maps can resolve them. New saved coordinate graphs without a site receive the current content recipe when their first site is created; an attempted-but-missing map remains under the existing refusal/recovery path rather than being silently rerolled.
- **Checks performed here:** static comparison of source and local Core XML/decompilation only. No build, game launch, runtime test, profile change, or save test was run by this task.
- **TODO status:** this source-level replacement is implemented. The broader generation/provider item and all runtime gates remain open; the integration lead owns the master TODO and final build record.

## Provider bindings

| Previous new-map use | Current existing provider | Implemented treatment and boundary |
| --- | --- | --- |
| `RR_SiteFluorescent` | Core `StandingLamp` | One native powered lamp in every saved room, plus the existing room-content lamp in each `service_passage` and `utility_room`. They use the live Core `CompPowerTrader`/`CompGlower`; there is no forced `PowerOn`. |
| `RR_SiteClimateUnit` | Core `Heater` | One native powered heater in the utility room, falling back to service passage when the graph has no utility room. The map starts indoor rooms at 20°C in `PostMapInitialized`; native heater regulation thereafter is subject to its power, weather and temperature simulation. It does not provide cooling. |
| `RR_FadedInstitutionalCarpet` | Core `PavedTile`, `Concrete`, `MetalTile` | Regular rooms use PavedTile with deterministic Concrete stripes; service/utility rooms use Concrete with deterministic MetalTile stripes. All are direct TerrainDefs. The Core `Carpet` entry is a terrain template and is deliberately not used as a direct terrain. |
| No former finite site supply | Core `ChemfuelPoweredGenerator`, `Chemfuel`, `HiddenConduit` | A native player-faction generator is fully loaded from actual spawned Chemfuel. Its capacity is finite and its output depends on its native fuel/flick/breakdown state. Hidden conduits are actual Core transmitters and are not placed on the generator's own occupied transmitter cells. |

No Core files or third-party mod assets are copied. Legacy `RR_SiteFluorescent`, `RR_SiteClimateUnit`, and `RR_FadedInstitutionalCarpet` Defs are deliberately retained for old saves; removal requires a separate migration boundary. The broader historical-to-native inventory remains in [the content replacement map](EXISTING_CONTENT_REPLACEMENT_MAP.md).

## Native power layout and bounds

The pinned Core XML under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs` identifies the providers and values used here:

- `ThingDefs_Buildings/Buildings_Power.xml`: `HiddenConduit` line 78 inherits Core's native power transmitter; its parent description says conduit can be placed under walls/buildings (lines 4–54). `ChemfuelPoweredGenerator` begins at line 257, produces 1,000 W (line 296), consumes 4.5 Chemfuel/day, holds 30 fuel (lines 302–303), and contributes 6 heat/second (line 318).
- `ThingDefs_Buildings/Buildings_Furniture.xml`: `StandingLamp` line 1328 draws 30 W (line 1350) and has a native radius-12 glower (line 1360).
- `ThingDefs_Buildings/Buildings_Temperature.xml`: `Heater` line 198 draws 175 W (line 249).
- `ThingDefs_Items/Items_Resource_Manufactured.xml`: native `Chemfuel` starts at line 211.
- `TerrainDefs/Terrain_Floors.xml`: direct TerrainDefs `Concrete`, `PavedTile` and `MetalTile` are at lines 57, 81 and 139; `Carpet` at line 232 is a `TerrainTemplateDef`.
- The installed Core `Assembly-CSharp.dll` used for the local source review had SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. In reviewed `CompPowerTrader`, `PostSpawnSetup` does not itself force a power-on state; `PowerNet.PowerNetTick` handles eligible consumers. The generation code therefore calls the public `map.powerNetManager.UpdatePowerNetsAndConnections_First()` to process queued connection registration, not `PowerNetTick`, and does not set consumer `PowerOn` manually. The inspected methods are preserved locally under `.local/inspection-work/native-gate-review/RimWorld.CompPowerTrader.cs` and `.local/inspection-work/native-gate-review/RimWorld.PowerNet.cs`.

The site has 6–8 base lamps and at most two additional room-content lamps, plus one 175 W heater. The maximum named demand is therefore `10 × 30 W + 175 W = 475 W`, below the generator's 1,000 W nominal output. Thirty fuel units divided by 4.5/day is about 6.67 days at the listed rate; this is arithmetic from Core metadata, not an observed operating duration. Difficulty, fuel modifiers, downtime, breakdowns, lighting, and active-map simulation may alter actual behavior.

Generation wires the generator footprint as logical route roots but spawns no conduit there, avoiding two transmitters occupying a single cell. Deterministic bounded pathfinding routes actual conduits to each heater/lamp footprint. Full interior hidden-conduit coverage is added before room-content lamps spawn in service/utility rooms. The provider pass is capped at 512 conduit cells and up to 16 native fuel stacks; inability to reserve the required cells fails site generation with the existing retained-site failure path. After all actual loads have spawned, the native connection manager processes its queued registrations once; source checks require the generator, heater, and all room lamps to share its real `PowerNet` and require the generator to hold fuel. No artificial production tick is advanced.

## Recovery prerequisite update

`FailedSiteRecovery.RequiredRecoveryContentAvailable` now checks the generation providers (`ChemfuelPoweredGenerator`, `Chemfuel`, `HiddenConduit`, `StandingLamp`, `Heater`) and direct Core floors, as well as the native start providers introduced by the adjacent gate task: `Door`, `Autodoor`, `CommsConsole`, `TableMachining`, `Battery`, and `WoodFiredGenerator`. It no longer requires retired gate/console/cutoff/generator Defs as a prerequisite. Those old Defs have not been deleted or migrated, so previously saved layouts still resolve their original objects. This change only makes the new/replacement content preflight describe the current providers; it does not prove replacement or old-map recovery in the game.

The explicit generation-failure-code allowlist and pristine-site safeguards in `FailedSiteRecovery.cs:16-27,127-147` were not broadened or weakened. The new missing-provider error remains outside that geometry/content-placement replacement set, so a missing required Def does not trigger a blind alternate-seed retry.

## Remaining acceptance and regression cases

Keep these open under [regression containment](../REGRESSION_CONTAINMENT.md) and the [procedural-space contract](../PROCEDURAL_SPACE_CONTRACT.md):

1. Build and inspect new 6-room and 8-room graph variants with service-only, utility-only, and both room types. Confirm no duplicate generator/conduit transmitter warning, no extra conduit on generator cells, no overlap blocking movement, each lamp and heater is on the same active native net, and visual floors remain readable.
2. Confirm the actual generator starts on and fueled; light output, heater target, room temperature, fuel depletion, manual refueling, breakdown, flick-off, power loss, and recovery all follow vanilla 1.6 behavior. The 6.67-day estimate and 20°C initial value are not substitutes for these observations. Specifically inspect sealed utility-room heat accumulation from the chemfuel generator; this layout has no cooling device.
3. Verify route reachability, thresholds, entry, return anchor/cell, evidence cell, generated furniture/salvage, fog-of-war and clue identity after provider placement. Verify the 512-conduit/16-stack bounds fail visibly without consuming crew, evidence or coordinate identity.
4. Save/reload a newly generated site; revisit it and prove generation does not repaint its floors, replace furniture, duplicate fuel, move clues, or change map ownership. Confirm old v2 saved maps retain their custom fixture/floor Defs and state. Confirm a saved coordinate graph that has not yet had a site uses content v3 on its first generation; confirm an attempted site with its map missing stays on the existing explicit failure/replacement route.
5. Exercise failed-site replacement with the new native start requirements present and absent. Confirm absence refuses before mutation and does not remove the original coordinate, map, case, route recording or legacy objects.

This record is source implementation evidence only. The [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md), combined compilation/package receipt and runtime compatibility claims must be updated by the integration lead after review.
