# Phase 2: Async Industries scenario and headquarters source review

**Date:** 2026-09-28. **Evidence state:** pinned Core source inspection only; no game launch, profile change, gameplay test, or compatibility result.
**Task:** [Phase 2 vertical slice](PHASE_2_VERTICAL_SLICE_TASK.md). **Profile:** row 4, `Ludeon.RimWorld`. **Features:** RR-SCEN, RR-FAC, RR-STA, RR-ECO, RR-MSN, RR-COMPAT.

## Contract and owned scope

Implement the [`async_industries` opening](../SCENARIOS.md#async_industries--first-vertical-slice) and [first-slice stock/facility contract](../FIRST_SLICE_CONTENT_INVENTORY.md#opening-site-and-company): selectable company start, 60×60 headquarters, five generated capable staff, prebuilt ordinary facility, incomplete gate, exactly one stock allocation, and exactly one branch initialization. The start uses Core without Harmony or DLC. Roles remain assignments that can change after startup.

This assignment owns this review only. The lead owns campaign state/services and assigns implementation file ownership separately. The [Phase 1 source review](PHASE_1_CORE_SOURCE_REVIEW.md) still governs component construction and saves. The scenario supplies starting conditions; the campaign service owns branch identity, money, receipts, contracts, and ongoing progression.

## Evidence and reproduction

Input rechecked: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`, SHA-256 **`5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`**. Tool: local **ilspycmd / ICSharpCode.Decompiler 9.1.0.7988**. Decompiled reference text is ignored under `.local/inspection-scenario/`; no game source or binary is included in tracked source/package files.

Read Core XML from the same install:

- `Data/Core/Defs/Scenarios/Scenarios_Classic.xml`: abstract `ScenarioBase`, starting-person part, arrival part, and ordinary starting-stock shape.
- `Data/Core/Defs/Scenarios/ScenParts_Fixed.xml`: fixed-part metadata and normal pawn-configuration page.
- `Data/Core/Defs/MapGeneration/CommonMapGenerator.xml`: `FindPlayerStartSpot` order 850, `ScenParts` order 875, and later fog generation.
- `Data/Core/Defs/PawnKindDefs_Humanlikes/PawnKinds_Player.xml`: abstract `BasePlayerPawnKind`, `Colonist`, and `Tribesperson`.
- `Data/Core/Defs/PawnKindDefs_Humanlikes/PawnKinds_Mercenary.xml`: native skill-range XML structure (`skills` → `li` → `skill` / `range`). This is a data-format reference, not content to copy.

Reproduce the successful type inspections from the repository root:

```powershell
$managed = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
$assemblyPath = Join-Path $managed 'Assembly-CSharp.dll'
Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256
& .local/tools/ilspycmd.exe --version
New-Item -ItemType Directory -Force .local/inspection-scenario | Out-Null
$types = @(
  'RimWorld.ScenPart', 'RimWorld.Scenario', 'RimWorld.ScenarioDef',
  'RimWorld.ScenarioLister', 'RimWorld.Page_SelectScenario', 'RimWorld.PageUtility',
  'RimWorld.ScenPart_PlayerFaction', 'RimWorld.ScenPart_ForcedMap',
  'RimWorld.ScenPart_ConfigPage_ConfigureStartingPawns',
  'RimWorld.ScenPart_ConfigPage_ConfigureStartingPawnsBase',
  'RimWorld.ScenPart_ConfigPage_ConfigureStartingPawns_KindDefs',
  'RimWorld.ScenPart_PlayerPawnsArriveMethod',
  'RimWorld.ScenPart_StartingThing_Defined', 'RimWorld.DropPodUtility',
  'RimWorld.GenStep_ScenParts', 'Verse.GenStep', 'Verse.GameInitData',
  'Verse.StartingPawnUtility', 'Verse.PawnGenerator', 'Verse.PawnGenerationRequest',
  'Verse.SkillRange', 'RimWorld.SkillRecord', 'RimWorld.PawnKindDefOf',
  'RimWorld.Faction', 'RimWorld.FactionRelation',
  'RimWorld.Page_ConfigureStartingPawns', 'Verse.SkillRequirement',
  'RimWorld.CompPowerBattery', 'Verse.CellRect'
)
foreach ($type in $types) {
  & .local/tools/ilspycmd.exe -r $managed -t $type $assemblyPath |
    Set-Content -Encoding utf8 ".local/inspection-scenario/$type.cs"
  if ($LASTEXITCODE -ne 0) { throw "Inspection failed: $type" }
}
```

Two preliminary candidate names, `Verse.GameStarter` and `RimWorld.ScenPart_FactionRelation`, were absent from the pinned type table. They are not implementation routes. The verified entry route is `PageUtility.InitGameStart`; faction initialization uses `Faction` APIs. The earlier Core source map's `GameStarter` wording was an inspection lead, not a verified API.

## Selectable scenario and exact lifecycle

`ScenarioDef.scenario` is public. `ScenarioDef.PostLoad()` fills missing scenario name/description from the Def and marks it `ScenarioCategory.FromDef`. `ScenarioLister` enumerates `DefDatabase<ScenarioDef>`, and `Page_SelectScenario` displays scenarios with `showInUI`. Add an original `ScenarioDef` with a unique Def name; no menu patch or external scenario file is required.

Use **`ParentName="ScenarioBase"`**, not Crashlanded. The base supplies `PlayerColony`, the required surface layer, and optional Odyssey orbit metadata. Inheriting Crashlanded would also inherit its crash narrative, illness, scattered resources, animals, and equipment. Keep any inherited optional planet-layer entries guarded; they are not requirements for the Core start.

`Scenario.AllParts` always enumerates **player faction → surface layer → parts in list/XML order**. Exact hook order for the native new-game route:

| Stage | Verified caller and behavior | Rimrooms use |
| --- | --- | --- |
| Scenario selection | `Page_SelectScenario.BeginScenarioConfiguration(Scenario, Page)` creates a new `Game`, sets a new `GameInitData`, assigns the selected scenario, calls `Scenario.PreConfigure()`, then obtains configuration pages. | Reset transient part fields here. The branch component already exists but must remain inactive. |
| Configuration | `Scenario.GetFirstConfigPage()` stitches storyteller, world creation, starting-site selection unless a forced-map part exists, optional ideology setup, then each part's `GetConfigPages()`. The last page runs `PageUtility.InitGameStart`. | Keep native configuration/pawn controls. There is **no `ScenPart.Configure()` method**. |
| World ready | `ScenPart_PlayerFaction.PostWorldGenerate()` creates/adds the player's faction. `Scenario` dispatches `PostWorldGenerate()` in AllParts order. | A later custom part can inspect the player faction and initialize ordinary starting faction relations. |
| Starting people | `ScenPart_ConfigPage_ConfigureStartingPawnsBase.PostIdeoChosen()` sets the starting count, generates starting candidates, and fills the candidate pool to `pawnChoiceCount`. | Use one native starting-person part. Do not independently generate a second roster in map generation. |
| Final preparation | `PageUtility.InitGameStart()` queues a pre-load action: first `GameInitData.PrepForMapGen()`, then `Scenario.PreMapGenerate()`. | By custom PreMapGenerate, optional candidates are already trimmed and generic work priorities assigned. Validate the final five, select roles, and set startup map size/generator here. |
| Starting settlement | The faction part's `PreMapGenerate()` creates a player-owned settlement at the selected tile. | Keep this normal ownership. Custom part need not create a second headquarters settlement. |
| Map generation | `Game.InitNewGame()` reads `initData.mapSize`, creates the map with `initData.mapGeneratorDef` when supplied, and runs the generation pipeline. `GenStep_ScenParts.Generate(Map, GenStepParams)` dispatches `Scenario.GenerateIntoMap(map)`. | A custom HQ generator prepares terrain/facility/start cell, and exactly one arrival part places the existing staff. |
| Map completion | MapGenerator's `Scenario.PostMapGenerate(map)` hook also runs on later generated maps, not only the first map. | Any custom hook must check the designated headquarters/start receipt. Never award stock on arbitrary later maps. |
| Start completion | `Game.InitNewGame()` finalizes, sets current map, calls `Scenario.PostGameStart()`, applies starting research, and finally dispatches `GameComponent.StartedNewGame()`. | Custom PostGameStart verifies actual HQ/staff/stock, then calls the one-time campaign initializer. |

All ScenPart lifecycle hooks above are public virtual `void` methods; `GenerateIntoMap` and `PostMapGenerate` take `Map`. `GetConfigPages()` returns `IEnumerable<Page>`. `PlayerStartingThings()` returns `IEnumerable<Thing>`. `AllowPlayerStartingPawn(Pawn pawn, bool tryingToRedress, PawnGenerationRequest req)` returns `bool`. There is no separate Configure override to implement.

**Faction reference timing:** `ScenPart_PlayerFaction.PostGameStart()` clears `Find.GameInitData.playerFaction` before later custom parts execute. Read `Faction.OfPlayer` and the actual spawned pawns, not that cleared initialization field.

**Second-new-game pitfall:** the scenario-selection method assigns the selected `Scenario` object directly, without cloning it at this point. A mutable `generated = true` flag on a Def-backed part can survive into another new game in the same process. Reset transient part state in `PreConfigure`, and use the new game's campaign/map receipt for authoritative idempotency. `ScenPart.CopyForEditing()` defaults to a memberwise copy; mutable lists also need care if a custom part participates in scenario editing.

## Headquarters size and generation route

`GameInitData` exposes public `int mapSize` (default 250) and `MapGeneratorDef mapGeneratorDef`. A custom **PreMapGenerate** may set the approved 60×60 size and select the original HQ generator immediately before `Game.InitNewGame` consumes them. Display the fixed size in the scenario description/configuration summary; do not silently suggest the starting-site advanced size option controls this scenario if the custom part will override it.

The native `ScenPart_ForcedMap` is not necessary merely to choose a generator. It removes normal starting-site selection, chooses a random starting tile/layer in `PostWorldGenerate`, and sets the generator then. Preserve ordinary site choice by assigning `GameInitData.mapGeneratorDef` in the custom PreMapGenerate instead.

Use a narrowly scoped original `MapGeneratorDef`/`GenStep` for the HQ rather than assuming the full default wilderness stack works at 60×60. A dedicated HQ step can lay valid terrain, the perimeter/rooms, roofed sleeping/research/storage areas, ordinary power/work furnishings, and the unfinished gate; its generated footprint must leave a valid walkable arrival area and perimeter access. Do not mutate `Base_Player` globally.

Verified `Verse.GenStep` requirements:

- `public abstract int SeedPart { get; }` — give the original step a stable seed contribution.
- `public abstract void Generate(Map map, GenStepParams parms)`.
- `public virtual void PostMapInitialized(Map map, GenStepParams parms)`.
- A public `GenStepDef def` is provided by the generation system.

Core XML puts `FindPlayerStartSpot` at 850 and `ScenParts` at 875. If the HQ step sets an explicit safe `MapGenerator.PlayerStartSpot`, do not subsequently overwrite it with an inappropriate generic start-finder step. Keep ScenParts exactly once in the startup generator, after walkable terrain/start position exists. Do not have both a custom pawn spawner and native arrival. World-object/site generation remains the separate destination assignment.

The [destination source review](PHASE_2_DESTINATION_SOURCE_REVIEW.md) confirms the same assembly's `MapGenerator.PlayerStartSpot` has a public setter, map size is assigned before component construction/GenSteps, and `Scenario.PostMapGenerate(map)` runs before `map.FinalizeInit()` on every generated map. This reviewer also read that bounded ignored MapGenerator excerpt. MapGenerator appends biome and tile-mutator extra GenSteps even for a custom generator; reserving `UsedRects` only protects against steps that respect that convention. Site-specific interference remains a runtime acceptance case. These are source facts, not a runtime result.

At 60×60, room fit, crop/food sustainability, colony expansion space, pathing, raids, and optional-mod assumptions remain acceptance work. The documented size is a tuning hypothesis, not proof of a playable map.

## Five capable staff with normal pawn configuration

Two native routes are present. A generic `ScenPart_ConfigPage_ConfigureStartingPawns` accepts `pawnCount`, inherited `pawnChoiceCount`, `allowedDevelopmentalStages`, and `requiredSkills`. It sets `GameInitData.startingSkillsRequired`, but the inspected general work-coverage check does not itself establish Rimrooms role-specific skill floors. Do not equate five generic colonists with five qualified staff.

The more explicit route is **`ScenPart_ConfigPage_ConfigureStartingPawns_KindDefs`**, with:

- `public List<PawnKindCount> kindCounts`.
- Inherited `public int pawnChoiceCount`.
- Each entry uses `kindDef`, `count`, and `requiredAtStart`.
- Total starting count is the sum of entry counts. The part generates each entry through `StartingPawnUtility.GetGenerationRequest(index)`, sets its KindDef, stores the request, and calls `AddNewPawn(index)`.
- `PostIdeoChosen()` records required kinds before invoking its base. Native page configuration remains available; candidates can be rerolled through the existing starting-pawn path.

A practical original-data design is five Rimrooms staff PawnKindDefs derived from Core's abstract `BasePlayerPawnKind`, one per initial capability focus, with `defaultFactionDef=PlayerColony`, appropriate ordinary apparel, and explicit skill ranges/required work tags. Add an original ScenPartDef using the native KindDefs class and `Page_ConfigureStartingPawns`; use one required pawn of each kind and five total candidates for the bounded opening. Initial pawn kind does not lock a future company role.

`PawnGenerator` supports `PawnKindDef.skills` as a list of `SkillRange`; XML entries specify `skill` and integer `range`. Generation brings that skill into the requested range and rejects a pawn whose required skill is totally disabled. Required kind work tags are also checked. These checks occur before the fallback that relaxes scenario predicates. Select original role floors in scenario data and match them to the actual operator, construction, research, guard, and treatment requirements. The design contracts do not establish exact numeric floors yet; label chosen values as tuning data rather than source facts.

**Predicate limit:** `PawnGenerator.GenerateNewPawnInternal` tries at most 120 times, stops enforcing scenario requirements after attempt 70, and stops enforcing request validators after attempt 100. `AllowPlayerStartingPawn` or `validatorPreGear` alone is therefore not a guarantee. Kind skill/work constraints remain separate checks, but a failed generation can still return null. Validate all five final selected pawns and team coverage before granting objects or money. Refuse a broken start with a useful reason; never silently accept an incapable operator because generation exhausted retries.

Relevant verified public APIs:

| API | Use and caution |
| --- | --- |
| `PawnGenerator.GeneratePawn(PawnGenerationRequest request)` | Generates a pawn; not needed for a second custom roster when native starting-pawn generation already ran. |
| `PawnGenerationRequest(PawnKindDef kind, Faction faction = null, PawnGenerationContext context = NonPlayer, PlanetTile? tile = null, ...)` | Use named arguments for the long constructor. Relevant options include `forceGenerateNewPawn`, `allowDead`, `allowDowned`, `mustBeCapableOfViolence`, `validatorPreGear`, `validatorPostGear`, and `developmentalStages`. Do not use a default struct instead of its proper constructor. |
| `StartingPawnUtility.GetGenerationRequest(int)` / `SetGenerationRequest(int, PawnGenerationRequest)` | Preserve native candidate-generation bookkeeping when customizing requests. |
| `StartingPawnUtility.AddNewPawn(int index = -1)` / `RandomizeInPlace(Pawn)` | Native roster/possession lifecycle; do not manually discard a candidate without updating the native lists and family/relations handling. |
| `StartingPawnUtility.WorkTypeRequirementsSatisfied()` | Checks native work types marked `requireCapableColonist` across the selected starting count. It is a baseline, not the entire Rimrooms roster contract. |
| `SkillRecord.Level` setter | Clamps the base value to 0–20. Raising it does not remove disabled skills, backstories, traits, or work restrictions. Prefer data-driven generation floors; validate final capability regardless. |

Additional implementation bindings: `Page_ConfigureStartingPawns.CanDoNext()` is protected virtual through its override and can be extended to reject an invalid final staff roster. `Verse.SkillRequirement.PawnSatisfies(Pawn)` checks level but does not independently check `SkillRecord.TotallyDisabled`; perform both checks. SkillRequirement's custom XML loader uses the skill Def name as the element name and integer content, for example `<Intellectual>8</Intellectual>`, unlike PawnKindDef's `SkillRange` list. `CompPowerBattery.SetStoredEnergyPct(float)` sets a clamped fraction directly; `AddEnergy(float)` first applies efficiency and cannot be used as a direct stored-fraction assignment. `CellRect.Min` / `Max` are public IntVec3 corners.

`GameInitData.PrepForMapGen()` already trims optional pawns, passes leftovers to the world, sets the selected pawns to the player faction, adds dynamic components, disables all priorities, and then assigns normal priorities. Any explicit opening role/work settings must run afterward. Keep normal pawn needs, skills, health, apparel, equipment and native Work controls authoritative.

## Arrival, stock, and once-only grants

Native `ScenPart_PlayerPawnsArriveMethod` with **`method=Standing`** uses the normal starting-pawn list and `DropThingGroupsNear(..., instaDrop: true, ...)`. The `instaDrop` branch uses `GenPlace.TryPlaceThing` directly, without creating an incoming skyfaller or active transport pod. The native `CrashedTogether` thought is only applied for `DropPods`. This route satisfies a standing company start without replacing the pawn spawn pipeline.

The arrival part enumerates **every** scenario part's `PlayerStartingThings()` and the selected pawns' generated starting possessions, then places the pawns and those things. Starting things are normally forbidden. Therefore:

1. Include exactly one arrival part and one starting-person part.
2. Choose one owner for each startup resource: either native starting-things definitions or the custom HQ stock placement, never both.
3. If using custom shelves/storage placement, generate the specified stock there and do not return the same goods again through `PlayerStartingThings()`.
4. Handle effective stack limits from installed Defs. Preserve the total while splitting into valid physical stacks; do not assume default Core/OgreStack numbers in spawn code.
5. Unforbid only the intended startup goods, rather than sweeping unrelated map items. Account for ordinary pawn-generated possessions explicitly; an exact audited manifest may use a separately reviewed no-possessions policy.
6. Validate all intended staff actually spawned. `GenPlace.TryPlaceThing` can fail; source inspection does not guarantee arrival cells or crowded storage will work.

Use an HQ/setup receipt and component branch/start receipt **before** physical grants. The HQ setup step must record successful placement and retain failure details; partial failed setup must not be replayed into another full stock grant. `Find.GameInitData != null` alone is insufficient because a startup routine could generate more than one map. Also check expected HQ map/tile, scenario identity, and completed setup state.

After native placement, custom `PostGameStart()` can call the lead's planned `RimroomsCampaignComponent.InitializeBranch(BranchStartRequest)` once. The agreed request contains `ScenarioId="async_industries"`, `ScenarioVersion=1`, seed, headquarters map, five existing pawn references, roles in matching order (`operations`, `research`, `engineering`, `security`, `medical_logistics`), initial USD funding, payroll/overhead and quoted survey amounts. `CompanyActionResult.Success`, `AlreadyApplied`, and `MessageKey` describe the result. Read this API from the actual source before implementing; this review records the lead's integration contract, not evidence that the method has shipped.

The initializer must be idempotent; a repeated result must not rerun stock, roster, buildings, or money. An initialization failure should leave a visible recovery/report state and preserve what exists. No campaign initialization belongs in generic component constructors, UI drawing, load hooks, or all-map callbacks.

## Ordinary faction relations

The Core player faction part already creates and adds the company-owned player faction. Reuse it; do not generate a second player faction. The player's displayed faction name can be assigned through public `Faction.Name` if required by the scenario presentation.

For ordinary eligible human factions at startup, use `Faction.TryAffectGoodwillWith(Faction other, int goodwillChange, bool canSendMessage = true, bool canSendHostilityLetter = true, HistoryEventDef reason = null, GlobalTargetInfo? lookTarget = null)`, suppressing startup notifications. It checks native restrictions and mirrors goodwill/relation state to the other side. A delta toward zero may be adjusted by the natural-goodwill logic; verify the resulting relation is Neutral rather than promising exact zero from that call.

Preserve permanent enemies, hidden/special factions, defeated factions, nonhuman threats, and native restrictions. “Ordinary neighboring factions start neutral” is not permission to turn mechanoids, insects, or every optional hostile faction into company friends. Apply the start adjustment once, not repeatedly each tick/load.

Avoid these traps:

- `SetRelationDirect` explicitly rejects pairs that both use goodwill.
- `SetRelation(FactionRelation)` recreates the reciprocal relation but does not copy its supplied `baseGoodwill`; `FactionRelation` defaults that value to 100. It is not a safe shortcut for symmetric zero-goodwill initialization.
- `GoodwillWith` includes situation caps, and `CanChangeGoodwillFor` may reject an adjustment. Respect a refusal and record the exception; do not write private fields or patch the entire faction system to force it.

## Acceptance still required

Compilation and XML checks can establish signatures and data structure. The owner-launched RimSort session must still prove scenario listing/configuration, exact map dimensions, five capable controllable staff, no duplicate/omitted stock, standing arrival without crash content, valid doors/roof/power/storage, neutral eligible neighbors, one-time branch/contract/funds setup, another new game in the same session, save/reload, and later destination generation without reapplying HQ setup. The 295-entry target and Core-only focused cases remain separate observations; RimBridgeServer is an attach-only QA overlay after launch.

**Result:** native Core extension routes are identified and their important ordering/pitfalls are recorded. No scenario implementation or runtime pass is claimed by this review.
