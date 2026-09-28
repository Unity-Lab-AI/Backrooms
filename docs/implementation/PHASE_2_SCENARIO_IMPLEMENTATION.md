# Phase 2: Async Industries start implementation

**Date:** 2026-09-28. **State:** source and package data written; lead compilation/integration and owner-launched runtime acceptance are separate evidence. No game, profile change, build, or tests were run by this assignment.

## Task and authority

- TODO: [Phase 2 vertical slice](PHASE_2_VERTICAL_SLICE_TASK.md); feature IDs **RR-SCEN, RR-FAC, RR-STA, RR-ECO, RR-MSN, RR-COMPAT**.
- Canonical inputs: [Async start](../SCENARIOS.md#async_industries--first-vertical-slice), [opening inventory](../FIRST_SLICE_CONTENT_INVENTORY.md#opening-site-and-company), [state ownership](../CAMPAIGN_STATE_DICTIONARY.md), and [action contracts](../OPERATIONS_ACTION_CONTRACTS.md).
- Exact integration row: **4**, package **`Ludeon.RimWorld`**. Pinned Assembly-CSharp SHA-256 **`5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`**. [Scenario source review](PHASE_2_SCENARIO_SOURCE_REVIEW.md) records APIs, native XML references, local inspection commands and tool version **9.1.0.7988**. [Destination review](PHASE_2_DESTINATION_SOURCE_REVIEW.md) records shared MapGenerator limits.
- This assignment owns the scenario directory, four startup Def files, scenario English text, and this record. The lead owns campaign state/services, gate/equipment Defs, company UI, build/staging, canonical contract updates and compilation evidence.
- Scope is the approved opening. Furniture Store, Lone Survivor, hiring after startup, later facilities, multiplayer and optional integration adapters are outside this increment.

## Created files and routes

| Actual file | Responsibility |
| --- | --- |
| [RimroomsStartDef.cs](../../src/RimroomsAsyncIndustries/Scenario/RimroomsStartDef.cs) | Data schema for scenario identity, size/generator, terrain/materials, rooms/doors/furniture/conduits/stock, initial role requirements and branch financial terms. |
| [ScenPart_RimroomsStart.cs](../../src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsStart.cs) | Final roster validation, fixed HQ generator selection, role work preferences, registration after arrival, ordinary eligible faction neutrality, visible startup messages and registration-only recovery API. Includes the native pawn-page subclass. |
| [HeadquartersSetupComponent.cs](../../src/RimroomsAsyncIndustries/Scenario/HeadquartersSetupComponent.cs) | Map-owned physical setup receipt, retained partial-failure state, original staff references, registration receipt and placement records. |
| [GenStep_Headquarters.cs](../../src/RimroomsAsyncIndustries/Scenario/GenStep_Headquarters.cs) | HQ terrain and original facility layout; owned native buildings, doors/roof/home area, effective-limit stock splitting, starter power and native arrival roots. |
| [RR_Scenarios.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/ScenarioDefs/RR_Scenarios.xml) | Selectable `RR_AsyncIndustries`, native five-kind configuration, no extra pocket possessions, one Standing arrival, `RR_Headquarters` and two owned GenSteps. |
| [RR_ScenarioParts.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/ScenPartDefs/RR_ScenarioParts.xml) | Fixed company-start and staff-page registration; these parts cannot be randomly added to ordinary scenarios. |
| [RR_Staff.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/PawnKindDefs/RR_Staff.xml) | Five original staff kinds using Core pawn generation, apparel and work/skill constraints. |
| [RR_Starts.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/RimroomsStartDefs/RR_Starts.xml) | `RR_AsyncIndustriesStart`: the complete initial facility arrangement, quantities, role floors and financial values. |
| [RR_Scenario.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_Scenario.xml) | Welcome, validation, setup-failure and recovery text. Scenario and kind labels/descriptions are ordinary translatable Def fields. |

All source, layout, text and configuration in this increment are original. Native ThingDef/PawnKindDef base references use the installed game's behavior. No third-party code, binary, texture or dialogue was added by this assignment.

## Player route and startup ordering

Select **Async Industries**, choose ordinary storyteller/world/site options, configure the five named capability groups through the native starting-pawn page, and start. The description explicitly states the fixed **60×60** headquarters; the scenario's late map-size override takes precedence over the native advanced size choice. Temperate sites are recommended in this first start's description. Selected world climate still applies.

1. The native scenario faction/layer parts create the ordinary player faction and settlement. Custom parts do not create a second faction or replace the main menu.
2. The native `ScenPart_ConfigPage_ConfigureStartingPawns_KindDefs` generates one required member of each original kind. All five are still normal RimWorld pawns, individually configurable and controllable. The custom page rejects a final roster with missing roles, disabled required work/skills, inadequate role levels, dead/downed pawns or missing movement/manipulation.
3. After native `PrepForMapGen`, the custom `PreMapGenerate` validates again, selects `RR_Headquarters` and size 60, and sets each role's initial work preferences. It does not generate new pawns or add funds.
4. HQ terrain runs at order 5, lays soil, reserves room footprints and sets the arrival point. Facility generation runs at order 800 and records `setupStarted` before placing any buildings or stock.
5. The facility builds perimeter/rooms, doors, concrete interior floors, roofs, furniture, power and receiving stock. Stock splits using each installed Def's effective `stackLimit`; Core/OgreStack behavior remains authoritative.
6. Exactly one native `ScenParts` step and one native **Standing** arrival place the existing selected staff. No crash pods or crash thought are requested. `NoPossessions` suppresses native bonus starting pocket supplies, keeping the physical manifest auditable; normal generated apparel remains.
7. After native arrival/map initialization, `PostGameStart` calls `InitializeBranch` using the saved physical receipt's staff and actual map. The campaign service verifies spawned player-owned staff, owns the initial account/records, and makes registration idempotent. Eligible ordinary human factions are adjusted toward neutral through native goodwill APIs once. Native restrictions, permanent enemies and special factions remain effective.

The scenario part keeps no per-game runtime flags on its Def-backed object. A second new game receives new map/component receipts. Destination maps have no HQ GenSteps, and the guards additionally require the initial game data, expected tile/size, selected custom start and an inactive branch. Ordinary saves receive only inert empty MapComponents.

## Original HQ arrangement

Coordinates below are map `x,z`, with north increasing z. The complete authoritative coordinates are editable in `RR_Starts.xml`.

| Space | Bounds / contents |
| --- | --- |
| Perimeter | x 8–51, z 8–51; granite walls and a steel south entrance. Soil yard remains available for crops/building. |
| Dormitory | x 10–22, z 10–19; five wooden beds, lighting and heat. |
| Mess | x 24–33, z 10–19; electric stove, dining table and five stools, lighting and heat. |
| Infirmary | x 35–48, z 10–19; two medical-use beds, shelf, lighting and heat. |
| Receiving | x 10–23, z 21–32; shelves and the starting stock placement center at 17,27. |
| Workshop | x 10–23, z 34–48; electric smithy, light and heat. |
| Gate chamber | x 25–33, z 26–39; `RR_MachineGate` centered 29,33, console 27,28, cutoff 31,28 and light. The gate's south entry/interaction cell is free. |
| Power | x 35–48, z 21–32; `RR_UtilityGenerator` at 40,26 and Core battery at 44,26, plus light. |
| Research | x 35–48, z 34–48; native simple research bench at 41,42 and `RR_FieldAnalysisBench` at 39,37, with free south access, lighting and heat. |
| Yard | Arrival point 30,23; recreation horseshoes at 28,44; connected paths between room doors. |

Six conduit runs connect the gate, workshop, lab, power and living areas. The custom generator starts at half fuel capacity; **150 wood** is additional starter fuel. The Core battery starts at **50% stored charge**, through `SetStoredEnergyPct` rather than efficiency-adjusted charging. The native battery is shared electricity storage. The lead's gate implementation owns its separately reserved return-energy rule.

The lead supplies the actual 3×3 gate, 1×1 console/cutoff, 2×2 generator and 2×1 analysis bench Defs and their behavior. Prebuilt walls/furniture represent the existing facility and do not subtract the separate assembly stock. Automatic bedroom assignment, stockpile zone creation or growth plots are not simulated by hidden startup grants; the player can use native controls to designate and expand them.

## Starting tuning and stock

These numeric choices implement previously qualitative opening requirements. They are editable first-slice tuning, not canon or observed balance.

| Role | Minimum skill levels | Initially favored native work |
| --- | --- | --- |
| Operations | Social 6, Intellectual 4 | Warden, Hauling |
| Research | Intellectual 8, Crafting 4 | Research |
| Engineering | Construction 8, Crafting 6 | Construction, Smithing, Crafting |
| Security | Shooting 8, Melee 4; violence enabled | Hauling between assignments; player equipment/draft controls remain native |
| Medical/logistics | Medicine 8, Cooking 6, Plants 4 | Doctor, Cooking, Growing |

Kind generation additionally requires hauling, cleaning and firefighting. Role assignment is not a permanent class lock. All numeric floors and preferred work live in `RR_Starts.xml`, with matching generation ranges in `RR_Staff.xml`.

Physical manifest: **250 steel; 18 industrial components; 2 advanced components; 150 silver; 50 survival meals; 6 industrial medicine; one normal-quality bolt-action rifle and revolver; one normal-quality flak vest; 150 wood; one field recorder; six survey tags; one return beacon; one sealed evidence case**. The 50 meals budget assumes two meals per staff member per day for five days; actual needs, eating waste and selected pawn traits are native game behavior. Six medicines are the initial allowance toward two serious treatments; actual wounds/tending requirements remain native. These quantities need owner-session balance observation.

The recorder/tags/beacon/case and medical/firearm/vest items are one initial allocation, not a second expedition grant. They begin as physical receiving stock for assignment, hauling and loading. Dollars stay in the branch account: **$50,000,000 opening funds, $5,000 wage per staff per day, $25,000 daily overhead, $5,000,000 survey reward and $1,000,000 optional bonus**, passed once to the campaign service. No dollar value is converted into a silver pile.

## Saved receipt and recovery

`HeadquartersSetupComponent` saves `rr_startDefName`, `rr_setupStarted`, `rr_setupComplete`, `rr_branchInitialized`, `rr_setupFailure`, original pawn references (`rr_startStaff`), parallel role values (`rr_startRoles`) and building/stock placement records (`rr_placedRecords`). No runtime Def object owns these receipts. List references use Scribe reference/value modes and retain valid empty collections on load.

- **Physical failure:** setup is marked started before mutation. Collisions, missing Defs, invalid rectangles and placement failures retain existing objects, save a failure reason, log the specific error, and block another physical grant. The start displays a failure letter. Partial structures are not automatically demolished or reconstructed. For this pre-runtime increment, the player retains the log and returns to scenario setup; automated repair of a partial physical facility is not implemented.
- **Registration failure after complete physical setup:** the existing HQ/staff/stock remain. `ScenPart_RimroomsStart.Current.TryInitializeExistingHeadquarters(map)` provides an explicit retry path after the cause is fixed, calls only the idempotent company registration service, and issues no objects. The lead owns wiring this action into the recovery UI. No startup retry runs automatically on load or tick.
- **Repeated registration:** the map receipt returns `Existing`; the company service also owns its separate branch initialization receipt. A view redraw never grants money or stock.
- **Ordinary colony:** no selected company start or completed HQ receipt means refusal. There is no conversion of an existing colony into a company branch.

## Remaining acceptance and limits

This assignment read the pinned exact types/native XML, wrote the original source/data and manually compared the consumed signatures. The lead owns compile, XML/reference/package validation and updated status evidence; no pass for these is claimed here.

Owner RimSort launch must observe: scenario listing; native configuration/rerolls; actual five-member capability coverage; exact 60×60 dimensions; standing arrival without crash narrative; roof/door access; one usable bed per staff; power connections, battery/fuel and free interaction cells; correct physical stock quantities under Core and the full profile; initial account/contract once; neutral eligible neighbors; ordinary-save inactivity; second new game; save/reload; failed/duplicate registration; destination generation without HQ grants; and the full facility-to-survey return loop with the lead's gate/destination work.

Custom generators still receive native biome/tile-mutator extra GenSteps. `UsedRects` is advisory to cooperating steps. Unusual sites or optional content may place structures or alter terrain; the current builder detects occupied planned structure footprints and refuses partial startup rather than erasing arbitrary generated content. The 60×60 size, selected climate, small food/fuel allowance, expansion space, staffing priorities and native raid/pathing assumptions remain balance/runtime acceptance work. No profile compatibility or completed playable gate is implied by these files.

### Source comparison after lead compiler feedback

The lead reported two C# 7.3 diagnostics in `ScenPart_RimroomsStart.cs`. Both were corrected: roster selection uses an explicit loop instead of capturing an `out` parameter in a lambda, and the missing-setup message conditional explicitly converts `TaggedString` to `string`. This assignment did not invoke the compiler; the lead owns the subsequent result.

The additional bounded read of pinned `Game.InitNewGame`, `GameInitData.PrepForMapGen`, `StartingPawnUtility`, scenario dispatch and native Standing arrival found no further concrete startup-order mismatch. Native initialization assigns `CurrentMap` before custom `PostGameStart`, retains `GameInitData` until after that call, and clears only its player-faction field earlier. The implementation correctly obtains `Faction.OfPlayer`. Default starting-pawn requests use the Adult development stage. Standing arrival places the existing selected pawns directly; the company service checks their actual spawned map/faction before awarding its account.

Source-known limitations remain explicit: native arrival ignores the return value of individual placement attempts, so the company's spawned-pawn check is essential; generation catches/logs failed GenSteps and continues, so a returned Map alone cannot prove physical setup; biome/mutator steps can alter a completed facility after order 800, so final gate/facility availability must still be observed and checked by operations. The physical receipt prevents duplicate grants and reports partial failure, but does not claim to reconstruct partially generated facilities or validate arbitrary optional-mod mutations. No runtime result is implied by this source comparison.
