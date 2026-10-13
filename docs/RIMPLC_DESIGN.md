# RimPLC: design

> **Current game target — 2026-10-12:** prepare for **RimWorld 1.7 unstable / Waylith**, retaining **1.6**. Both loader versions use the shared `1.7/` content folder. [The migration record](implementation/RIMWORLD_1_7_MIGRATION.md) owns the current target and remaining checks. Earlier 1.6 source, build and play observations remain historical; no 1.7 runtime or full-profile acceptance is recorded.

Owner, verbatim: *"i think this is the whoole PLC like logic chain if this then this if heath level reaches then this type of thing for the whole game properly layed out into a PLC that we will call RimPLC as a seperate mod idea we will build inot the backrooms folder and rimrooms and make a stand alone version thats fully integrated with the game for use with any mod and any dlc with not depandancies"*

Owner decisions, verbatim:

- *"Both: player UI + AI API"*
- *"we need to build it tho before we train everything the three pods training together our lora and vocie"*

This is a design only. Nothing is built, staged, copied or deployed by this document, and the running game and its `Mods` folder are not touched.

## Contents

0. What RimPLC is, and the sources
1. Register check (LAW: check the mod register before building)
2. The two shapes: standalone mod, and the Rimrooms soft link
3. Core model: sensors, tags, marks, rungs, scan cycle
4. Sensor catalogue (each mapped to a real API)
5. Action set (each mapped to a real API)
6. Player UI
7. Save, presets, export and import
8. AI API (RimBridge companion tools, plus a file fallback)
9. Migration from `gates.py` and the brain training
10. Build phases and the minimum shippable version
11. Risks
12. Open questions for the owner

---

## 0. What RimPLC is, and the sources

RimPLC is the in-game home of the Ladder v2 logic. Today that logic lives outside the game: `.local/autopilot/gates.py` reads the colony through the RimBridge socket, walks `docs/playbook.gates.json` (31 rungs, 12 disabled, 9 constants and 7 computed variables), and hands the autopilot one live rung. RimPLC moves the same thing into a C# mod. It reads the game directly, scans the rungs every few hundred ticks, shows the result in a ladder window a player can edit, and exposes the same state and edits to Unity.

Sources read for this design:

| Source | What it gave |
|---|---|
| `training/ladder-v2/DESIGN.md` | The 40 new sensor keys, the marks that cannot be measured from the bridge, rung families and priority bands, the tag table, the training episode families A–F, and the six engine changes v2 needs |
| `docs/playbook.gates.json` | The current rung and tag format (`id`, `priority`, `when`, `then`, `why`, `never`, `disabled`; `tags.constants`, `tags.variables` with `min`/`max`) |
| `.local/autopilot/gates.py` | `state()`, `tags()`, `_bound()`, `_holds()`, `decide()` semantics, including "a missing key never fires" and "first match plus `always`" |
| `.local/autopilot/tools.py` | `t_ladder` output shape (`live_rungs`, `tags`, `my_marks`, `my_rungs`) and `t_ladder_set` ops (`mark`, `tag`, `add_rung`, `remove_rung`) with their name rules |
| `src/RimroomsAsyncIndustries/` | Build model (`net472`, C# 7.3, `TreatWarningsAsErrors`, deterministic, references only `Assembly-CSharp` and three `UnityEngine` modules, **no Harmony anywhere**), `GameComponent` pattern, the `RimroomsAutomationComponent` inbox/outbox command file, and calls already proven in this repo (`SetPriority`, `Bill_Production` + `BillStack.AddBill`, `Zone_Growing.SetPlantDefToGrow`, `allowSow`, `AreaRestrictionInPawnCurrentMap`, `ModsConfig.OdysseyActive`) |
| `Mods/RimBridgeServer/README.md` (installed copy, read only) | The **Third-Party Extension Tools** section: companion DLLs referencing `RimBridgeServer.Sdk`, `[Tool]` methods, `BridgeTools` folder layout, global tool names, collision rejection |
| `.local/decomp/roofscan/` (decompiled `Assembly-CSharp` for 1.6) | Every API marked **verified** below was found there by name and signature |
| The 294-row register HTML and the per-mod reviews | §1 |

Marking rule for this document:

- **verified (decomp)**: the member was found by name and signature in `.local/decomp/roofscan`.
- **verified (repo)**: Rimrooms already calls it in shipped source.
- **UNVERIFIED**: from general knowledge only. It has to be confirmed against the decomp before code relies on it.

---

## 1. Register check

Per `.claude/CONSTRAINTS.md` §CHECK THE MOD REGISTER BEFORE BUILDING. The register HTML (`outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.html`) was filtered by these `System family` values: *Staff jobs, policies, and social systems*, *Staff work-flow quality of life*, *Interface, scenario setup, and quality of life*, *Interface and startup quality of life*, *Mod framework* and *Performance and simulation controls*. It was also searched by name for manager, work tab, pawn control, animal tab/controls, policy, automatic/auto, and Harmony.

**Not in the profile:** Colony Manager, Fluffy's Work Tab, Better Pawn Control, and any general "auto-anything" colony automation mod. The Compact Work Tab review says so explicitly: *"The inventory does not contain Fluffy's Work Tab."* So RimPLC reinvents nothing that the profile already provides. No mod in the profile is a rule engine.

Rows that apply, with the review read for each:

| Row | Mod | Stance / firmness | What the review says | What it changes in RimPLC |
|---|---|---|---|---|
| 1 | Harmony | Optional / Provisional | *"Add no Harmony patch unless a specific Rimrooms feature needs it and the patch is isolated."* | RimPLC uses **no Harmony**. That is the standalone answer (§2.1). |
| 13 | HugsLib | No integration | none | RimPLC does not use HugsLib settings or ticks. |
| 67 | Compact Work Tab | Optional / Settled | UI-only. Overrides the work tab drawing. Check *"manual priorities on/off ... save/reload of priorities"*. | The `set_work_priority` action writes `Pawn_WorkSettings` only, never the tab. It must respect the manual-priorities toggle (§5, UNVERIFIED field). It works the same with or without CWT. |
| 155 | Numbers | Optional / Provisional | A workforce dashboard with no data ownership | No conflict. RimPLC does not add Numbers columns in v1. |
| 30 | Allow Tool | Optional / Settled | *"no Rimrooms dependency ... keep actions understandable when this tool is absent"* | Designation actions use Core `DesignationDef`s only, never Allow Tool's custom ones. Allow Tool's own designations (for example haul-urgently) can be read as sensors through `DefDatabase` when present, never assumed. |
| 264 | Zone To Schedule | Optional / Provisional | *"drafted/uncontrollable pawns do not switch; manual area changes persist until the next schedule transition"* | **Real interaction.** A RimPLC `set_area` action is overwritten by ZtS at the next schedule hour. RimPLC must not fight it: a `set_area` coil is edge-triggered (it fires once on the rising edge), never re-asserted every scan. If `ModsConfig.IsActive("Mlie.ZoneToSchedule")`, the editor shows a warning on `set_area` and `set_schedule` rungs. |
| 239 | Undraft After Tucking | Optional / Provisional | Auto-undrafts a rescuer after tucking | **Real interaction.** A latched `draft` coil would re-draft the rescuer. Draft coils are edge-triggered and never latched. |
| 19 | Automatic Power Switch | Optional / Provisional | *"do not replace or silently automate its controls"* | RimPLC v1 has **no power-switch action**. Reading flick state as a sensor is allowed. |
| 212 | Smarter Construction | No integration | Changes build ordering | None. RimPLC only places designations and blueprints through Core designators. |
| 168 | Priority Treatment | Optional / Settled | Medical job ordering | None. `set_medical_care` writes `playerSettings.medCare` only. |
| 15, 44, 260 | Automatic Stump Chopping, Auto-Cut Blight, While You Are Nearby | Optional | Each already automates one narrow job | RimPLC does not duplicate these. The preset ladder ships no stump-chop or blight rung. |
| 33, 36 | Animal Controls, Animal Tab | Optional / Settled | Animal training and controls UI | The training/mount marks from Ladder v2 §1.3 become sensors read from Core training records (UNVERIFIED API, §4) and are not taken from these mods. |
| 95 | FrameRateControl | Optional / Provisional | Changes the tick rate | The scan cadence is counted in **game ticks**, not frames or real time, so a changed tick rate scales correctly. |

Retroactive note: the existing `RimroomsAutomationComponent` (`set_work_priority`, `set_area`, `add_bill`) predates this LAW. The ZtS and Undraft-After-Tucking interactions above also apply to it. That should be recorded as a task in `docs/TODO.md` by whoever owns that file. This document does not edit TODO.

---

## 2. The two shapes

### 2.1 (a) Standalone RimPLC: zero dependencies

| Item | Value |
|---|---|
| Display name | `RimPLC` |
| packageId | `Operator.RimPLC` (proposal, matching Rimrooms' author value `Operator`) |
| supportedVersions | `1.6` and `1.7`; both load the shared `1.7/` content folder. A declaration is not 1.7 runtime acceptance |
| `modDependencies` | **none** |
| `loadAfter` | `Ludeon.RimWorld` and the five DLC ids only. It is ordering, not a requirement. |
| Assembly references | `Assembly-CSharp`, `UnityEngine.CoreModule`, `UnityEngine.IMGUIModule`, `UnityEngine.TextRenderingModule`. Same as Rimrooms, `Private=false`. |
| Source location | `RimPLC/Source/RimPLC/RimPLC.csproj`, following the Rimrooms csproj settings (`net472`, `LangVersion 7.3`, `Deterministic`, `TreatWarningsAsErrors`, `IncludeSourceRevisionInInformationalVersion=false`, `RIMWORLD_PATH`, and the same `RequireLocalGameReferences` guard) |
| Package location | `RimPLC/` (`About/`, `LoadFolders.xml`, `1.7/Assemblies/RimPLC.dll`, `1.7/Defs/`, `Languages/`) |

**Why no Harmony.** RimPLC reads state and calls player-level setters. It never needs to change Core behaviour. Every sensor and action in §4 and §5 is a public member, and Rimrooms has already shown, across seven components, that this profile can be served with public API only. The only private member RimPLC wants is the alert list (`AlertsReadout.activeAlerts` is `private`, verified (decomp)). §4.4 reads alerts without it. Harmony is not needed, so the "bundled-safe" question does not arise. If a future feature truly needs a patch, it goes into a separate optional assembly loaded through `LoadFolders.xml` `IfModActive="brrainz.harmony"` (the attribute is verified (decomp), `Verse/ModLoadFolders.cs`), so the core mod stays dependency-free.

**Any mod, any DLC.**

- **Defs are resolved at runtime by name**, never compiled in. A rung that names `ThingDef Steel`, `WorkTypeDef Research` or `RecipeDef CookMealSimple` resolves through `DefDatabase<T>.GetNamedSilentFail` (verified (repo)). A name that does not resolve leaves that condition **unmeasured**, so the rung does not fire (§3.2). The rung shows a red "unresolved def" badge in the editor. It is never a crash, and never a guess.
- **DLC rungs are gated.** Each rung can carry `requires: ["Royalty", "mod:vanillaexpanded.gravship"]`. The DLC flags come from `ModsConfig.RoyaltyActive`, `IdeologyActive`, `BiotechActive`, `AnomalyActive` and `OdysseyActive`, all verified (decomp, `Verse/ModsConfig.cs:81-89`). Mod ids use `ModsConfig.IsActive(string id)`, verified (decomp, line 395). A rung whose requirement is missing is shown greyed out as "not applicable", is never scanned, and is never deleted, so the same ladder file works on every profile.
- **DLC sensors are gated the same way.** For example, `title_rank` only exists when `RoyaltyActive` is true, so the key is absent otherwise.
- **Adding RimPLC to an existing save** works the way Rimrooms' `GameComponent(Game game)` constructors already work. Removing it from a save will log the missing component class on load. That is UNVERIFIED for whether it is harmless. It has to be checked on a disposable save before release (§11).

### 2.2 (b) Rimrooms / Backrooms integration: an optional soft link

Rimrooms must keep working with RimPLC absent, and RimPLC must keep working with Rimrooms absent. Neither declares the other as a dependency.

1. **The preset ships in RimPLC, gated.** The full-run Ladder v2 preset includes the Backrooms gate family (bands 80–86) with `requires: ["mod:Rimrooms.AsyncIndustries"]`. Without Rimrooms those rungs are greyed out.
2. **Rimrooms sensors come from a registration API in RimPLC**, called from a small extra Rimrooms assembly that only loads when RimPLC is active:
   - `Mod/Rimrooms - Async Industries/LoadFolders.xml` gains `<li IfModActive="Operator.RimPLC">RimPLCLink</li>`. `IfModActive` is verified (decomp). The shared content entry is `<li>1.7</li>` for both loader versions; keep this folder name when adding an optional link.
   - `RimroomsRimPLCLink.dll` references `RimPLC.dll` (`Private=false`) and calls `RimPLC.Api.RegisterSensor("gate_online", map => ...)` and similar from a `StaticConstructorOnStartup` class (UNVERIFIED as the right hook; a `GameComponent` constructor is the proven fallback).
   - The Rimrooms core assembly does not change its references. Its "no dependency" stance (owner, 2026-10-03: *"rework mod to not need any depeancie mods"*) holds.
3. **Rimrooms-owned sensors** turn the Ladder v2 §1.3 marks that came from the machine pane into measured keys: `gate_online`, `gate_open`, `operator_on_station`, `gate_sections_done`. They are read straight from `RimroomsCampaignComponent` / the gate comps, with the exact members picked when the link is written (UNVERIFIED until then).
4. **Rimrooms-owned actions**, registered the same way, are limited to what `RimroomsAutomationComponent` already does. Gate start/recall actions are **not** exposed in v1; the gate stays a player/owner decision.
5. **Overlap with `RimroomsAutomationComponent`.** Its inbox/outbox file is the model for RimPLC's file fallback (§8.3). Once RimPLC has the same actions, the Rimrooms inbox stays as it is (it is used live). Merging or retiring it is a later owner call, not part of this design.

---

## 3. Core model

### 3.1 Objects

| Object | PLC term | Shape |
|---|---|---|
| **Sensor** | Input image | A named key, computed in C# from game state. Type `bool`, `int`, `float` or `string[]` (labels). It can be **absent** (unmeasured). Each sensor has a cadence class (§3.4) and an optional `requires`. |
| **Tag** | Constant or variable | `UPPER_CASE` name. A **constant** has a value and `min`/`max`. A **variable** has a formula over sensors (the 7 in `gates.py` `tags()`: `FOOD_MIN_DAYS = 2 + 0.4*n` and so on) plus clamps, and an optional override. The override wins, as in `gates.py`. List tags (for example `NEVER_HUNT`, `RESEARCH_ORDER`) are allowed in RimPLC. That closes Ladder v2 engine change 5. |
| **Mark** | Internal bit/word | `lower_case` name. It holds a **bool or a number** (closes Ladder v2 engine change 1: `title_rank 4` stays 4). Exposed to conditions as `mark_<name>`, exactly as `gates.py` does today. |
| **Rung** | Rung | `id`, `priority` (float, lower runs first), `enabled`, `source` (`book`, `player`, `unity`), `requires`, `when` (condition), `then` (advice steps), `coils` (executable outputs), `why`, `never`, `mode`. |
| **Timer / counter** | TON, TOF, CTU | Named instructions that live inside a rung condition (§3.3), with their state saved |

### 3.2 Condition language

It is a **strict superset of today's `when`**, so every rung in `docs/playbook.gates.json` loads unchanged:

- `key: bool`, `key: number` (equality), `key: "<X"`, `key: ">X"` with X a number, a `{TAG}` or another key: **identical** to `_holds` / `_bound`.
- `letter_matches: "substr"`: identical.
- **Missing key means the condition fails**, and an unresolved bound means the condition fails and is recorded in `unresolved_conditions`. Both are identical to `gates.py` and are load-bearing for training family C.

Added operators (closing Ladder v2 engine change 2):

- `">=X"`, `"<=X"`, `"!=X"`, `"==X"` string forms.
- `{"any": [cond, cond]}` for OR (one rung instead of two).
- `{"not": cond}`.
- `{"ton": {"id": "cold_5m", "in": cond, "ticks": 2500}}` true when `in` has held for that many ticks. `tof` is the off-delay. `{"ctu": {"id": "raids", "in": cond, "preset": 2, "reset": cond}}` counts rising edges. `{"ons": cond}` is true for one scan on a rising edge.
- `{"label": "alert", "contains": "starv"}` for label lists.

The engine keeps both shapes. `when` as a flat dict is the AND form, which the training data already uses. Nested objects are only used when needed.

### 3.3 Outputs: advice and coils

Today a rung's `then` is a list of sentences for the AI to carry out. That has to stay, because the brain is trained on it. RimPLC adds executable outputs next to it:

- **`then` (advice)**: text steps. They are shown to the player in the editor and returned to Unity as the live rung, exactly like `t_ladder`.
- **`coils` (actions)**: typed actions from §5, for example `{"do":"set_work_priority","pawn":"*","work":"Cooking","level":1}`. Each coil has a type:
  - `OTE` (default): the action runs on the **rising edge** of the rung (false to true), once.
  - `OTL` / `OTU`: latch and unlatch **marks only**, never game state. Latching game state would fight the player and the mods in §1.
  - `pulse`: the action re-runs every N scans while the rung is true, with a minimum period. It is only allowed on idempotent actions (`message`, `set_mark`).

**`mode`** per rung:

- `advise`: never executes coils. This is the default for every `book` rung.
- `auto`: executes coils.
- `off`: same as disabled.

A player flips a rung to `auto` in the UI. Unity can only propose `auto`; it needs the owner (§8.4).

### 3.4 Scan cycle

Real PLCs evaluate every rung each scan. `decide()` returns only the first match. RimPLC does both:

1. **Input scan.** Sensors refresh by cadence class:
   - **fast**: every scan (pawn flags, hostiles, alerts cache, ticks)
   - **normal**: every 4th scan (resources, zones, counts)
   - **slow**: every 16th scan (wealth, research, faction goodwill, sweeps of things by def)
2. **Logic scan.** Every enabled, applicable rung is evaluated in priority order. Each rung's truth, the keys that matched, and timer/counter state are recorded.
3. **Output scan.** For `auto` rungs, coils fire on their edges. **Arbitration:** if two true rungs write the same target (the same pawn and work type, the same bill table, the same area), the lower priority number wins and the other is reported as "suppressed by `<id>`".
4. **Live rung.** The first true `advise` rung in priority order, plus `always`. This is exactly the `decide()` contract, and it is what Unity reads.

**Cadence.** `GameComponent.GameComponentTick` (verified (decomp, `Verse/GameComponent.cs:11`)) runs the scan every `SCAN_TICKS` game ticks. The default is 250 (one rare tick); the player can set 60–2500. When the game is paused, ticks stop. Rimrooms solved the same problem by also running once a second from the GUI update. RimPLC does the same, as an **input + logic only** scan while paused, with **no output**. That way the editor stays live, and nothing acts while the player has paused.

**Performance budget.**

- Target: **under 3 ms per scan on the main thread**. Measured live 2026-10-12 with ~300 mods and 127 rungs: 1.31 ms per scan, every 250 ticks (about 0.005 ms per tick). The first 1 ms target skipped the slow sensors on every scan for no real saving, so it was raised.
- Sensors never iterate every cell on the map. Counts use `map.resourceCounter` (stockpiled resources), `map.listerThings.ThingsOfDef` (verified (decomp)) and `map.mapPawns` lists.
- A scan that goes over budget finishes its logic but skips the slow-class sensors next time and shows "over budget" in the window.
- Multiple maps: each sensor is computed for the **home map** (`Find.Maps` filtered by `IsPlayerHome`, verified (repo)), and per map only where a rung asks for `map:` scope (Phase 3).

### 3.5 Determinism and multiplayer

RWT runs separate colonies, so there is no lockstep. Still, RimPLC uses no `UnityEngine.Random` and no wall clock inside logic, so a scan is a pure function of game state plus saved PLC state.

---

## 4. Sensor catalogue

These are the Ladder v2 keys, **under the same names**, so the existing training data and rungs carry over. The source changes from bridge sweeps to direct reads. Where the value's meaning shifts, the table says so.

### 4.1 Time, colony, pawns

| Key | API | Status | Note |
|---|---|---|---|
| `day` | `Find.TickManager.TicksGame / 60000f` | verified (decomp, `Verse/TickManager.cs`) | |
| `paused` | `Find.TickManager.Paused` | UNVERIFIED property name (`Pause()` is verified (decomp, line 237)) | |
| `map_count` | `Find.Maps.Count` | verified (repo) | |
| `colonists` | `map.mapPawns.FreeColonists.Count` | verified (decomp, `Verse/MapPawns.cs:144`) | Home map. A colony-wide count over all maps is a second key, `colonists_all`. |
| `downed_count` | `pawn.Downed` | UNVERIFIED member name | |
| `mental_break` | `pawn.InMentalState` | verified (decomp, `Verse/Pawn.cs:277`) | |
| `drafted_count` | `pawn.drafter.Drafted` | verified (decomp, `Pawn_DraftController.cs:19`, with a setter) | |
| `lowest_health_pct` | `pawn.health.summaryHealth.SummaryHealthPercent` | verified (decomp, `SummaryHealthHandler.cs:14`) | This is the owner's *"if heath level reaches then this"*. |
| `lowest_mood` | `pawn.needs.mood.CurLevel` | `Need_Mood` verified (decomp); `CurLevel` UNVERIFIED | Replaces the `mood_low` judgement mark. |
| `colony_animals`, `colony_mechs` | `map.mapPawns` filtered by `Faction.OfPlayer` and `RaceProps.Animal` / `IsColonyMech` | UNVERIFIED member names | Direct reads, which removes the Ladder v2 caveat about tamed versus wild in cell sweeps |

### 4.2 Threat and environment

| Key | API | Status |
|---|---|---|
| `hostiles_on_map` (bool form `hostile_threat`) | `GenHostility.AnyHostileActiveThreatToPlayer(map)` | verified (decomp, `GenHostility.cs:227`). This **replaces** the "letter says raid" heuristic and the Ladder v2 `threat_letter` correction. The count form is UNVERIFIED (`map.attackTargetsCache`). |
| `outdoor_temp` | `map.mapTemperature.OutdoorTemp` | verified (decomp, `Verse/MapTemperature.cs:25`). Replaces the `outdoor_cold` / `outdoor_hot` marks with a number and a tag threshold. |
| `condition_<defName>` | `map.gameConditionManager.ConditionIsActive(def)` / `ActiveConditions` | verified (decomp, `GameConditionManager.cs:75, 271`). Cold snap, heat wave, toxic fallout and so on, by def name. |
| `fire_cells` | `map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count` | `ThingsOfDef` verified (decomp); `ThingDefOf.Fire` UNVERIFIED |
| `letters`, `threat_letter`, `quest_letter`, `empire_letter` | `Find.LetterStack.LettersListForReading`, `letter.def` | verified (decomp, used in `Dialog_ChooseNewWanderers.cs:93`) |

### 4.3 Economy

| Key | API | Status | Note |
|---|---|---|---|
| `steel`, `components`, `plasteel`, `uranium`, `gold`, `silver`, `chemfuel`, `wood`, `medicine`, `meals`, `raw_food` | `map.resourceCounter.GetCount(ThingDef)` | verified (decomp, `ResourceCounter.cs:75`) | **Semantics change:** ResourceCounter counts what is in storage, not everything inside the camp rectangle. It is closer to what the rungs mean. Flag it in the migration parity read (§9). |
| `days_of_food` | `map.resourceCounter.TotalHumanEdibleNutrition / (colonists * 1.6)` | `TotalHumanEdibleNutrition` verified (decomp, `ResourceCounter.cs:19`); the 1.7/day constant is from `gates.py` | Core's own `Alert_LowFood` uses the same total |
| `wealth` | `map.wealthWatcher.WealthTotal` | verified (decomp, `WealthWatcher.cs:42`) | Replaces the `wealth_band` mark |
| `growing_cells`, `stockpile_cells`, `home_cells` | `map.zoneManager.AllZones`, `map.areaManager.Home` | verified (decomp, `ZoneManager.cs:13`, `AreaManager.cs:17`) | Cell count members UNVERIFIED |
| `count_<defName>` (generic) | `map.listerThings.ThingsOfDef(def).Count` | verified (decomp) | Covers `stoves`, `turrets`, `beds`, `research_benches`, `comms_console`, `pod_launchers`, `ship_parts` and any **mod** building, by def name at runtime |
| `count_group_<ThingRequestGroup>` | `map.listerThings.ThingsInGroup` | UNVERIFIED | Corpses, plants and so on |

### 4.4 Alerts

`AlertsReadout.activeAlerts` is private (verified (decomp)). `Find.Alerts` is public (verified (decomp, `Verse/Find.cs:60`)). `Alert.Active` and `Alert.GetReport()` are public (verified (decomp, `Alert.cs:52, 101`)).

Design: RimPLC builds its own instances of the alert types a ladder names (by class name, for example `RimWorld.Alert_LowFood`) and calls `GetReport().active` on the slow cadence. That gives `alert_<ClassName>` keys that are **language-independent**. This fixes the Ladder v2 problem that *"exact English labels are UNVERIFIED"*. It is UNVERIFIED that constructing a second instance of every alert type is side-effect free; Rimrooms' `RimroomsAlerts` notes that Core's `AlertsReadout` constructor walks the types, which suggests it is. The fallback is reflection on the private list, read only, which still needs no Harmony.

### 4.5 Research, factions, DLC (the Ladder v2 "impossible" marks become sensors)

As built (2026-10-13). Every key here is read straight from the game; a key whose DLC, def or faction is absent is left out, never a fake value.

| Key | Code | API | Status |
|---|---|---|---|
| `research_<defName>` (lower case) | `Sensors.ReadSlow` | `ResearchProjectDef.IsFinished` over every loaded project | verified (decomp) |
| `research_current` (string), `research_queue_empty`, `ship_research_done` | `Sensors.ReadSlow` | `Find.ResearchManager.GetProject()`; `ShipBasics.IsFinished` | verified (decomp) |
| `title_seniority` | `Sensors.ReadSlow` | max over colonists of `royalty.MostSeniorTitle.def.seniority`; Royalty only | verified (decomp). Raw seniority, **not** the 0-7 rank: `mark_title_rank` stays a mark she sets |
| `empire_hostile` | `SensorsWorld.Factions` | `Find.FactionManager.OfEmpire.HostileTo(Faction.OfPlayer)`; left out with no Empire | verified (decomp). `goodwill_<factionDef>` was planned and is **not built** |
| `caravan_out` / `caravans_out`, `caravan_pawns_out` | `Sensors.ReadSlow` / `SensorsWorld.Caravans` | `Find.WorldObjects.Caravans`, player-controlled | verified (decomp) |
| `ideo_roles`, `ideo_roles_unassigned`, `ideo_leader_assigned`, `ritual_spots`, `ideo_rituals` | `SensorsWorld.Ideology` | the player's primary ideo: `RolesListForReading`, `ChosenPawnSingle()`, `Precept_Ritual`; Ideology only | verified (decomp). `mark_ideo_roles_set` is still the done-mark the rungs set |
| `monolith`, `monolith_level` | `SensorsBuild.Buildings` | `VoidMonolith` on the map; `Find.Anomaly.Level`; Anomaly only | verified (decomp) |
| `mount_candidates` | `Sensors.ReadNormal` | mount-capable animals on the home map by def name | heuristic def list from `gates.py` |
| `toxic_buildup_max`, `worst_disease_margin`, `battery_days_stored` | `SensorsWorld.Toxic` / `Disease` / `Batteries` | `HediffDefOf.ToxicBuildup` severity; `HediffComp_Immunizable.Immunity` - severity; `CompPowerBattery.StoredEnergy` / draw | verified (decomp) |
| `psylink_level`, `mechlink_installed`, `gravship_ready`, `mounts_trained`, `mounted_ready` | -- | -- | **not sensors**: they stay marks (`mark_*`) she or the player sets, as in Ladder v2 |

### 4.6 Sensors that stay marks

These are judgement states: `mountain_base_done`, `production_running`, `fields_set`, `bills_set`, `start_kind` (the scenario could be read from `Find.Scenario`, UNVERIFIED), and every `<rung>_done` growth mark. These need no change from Ladder v2. They are set by the rung's own `then` (advice) or by an `OTL` coil.

---

## 5. Action set

Each action is something a player can do from the normal UI. RimPLC calls the same setter that UI would call, never a def edit and never a spawn. Refusal rule (copied from `RimroomsAutomationComponent`): *"it refuses any command naming something it cannot find rather than guessing a near match."*

| Action | Arguments | API | Status |
|---|---|---|---|
| `message` | text, type | `Messages.Message(string, MessageTypeDef, bool)` | verified (decomp, `Verse/Messages.cs:47`) |
| `letter` | label, text, def | `Find.LetterStack.ReceiveLetter(TaggedString, TaggedString, LetterDef, LookTargets, ...)` | verified (decomp, `LetterStack.cs:44`) |
| `set_mark` / `set_tag` | name, value | RimPLC internal | |
| `set_work_priority` | pawn or `*`, workType, level 0–4 | `pawn.workSettings.SetPriority(WorkTypeDef, int)` | verified (decomp, `Pawn_WorkSettings.cs:140`) and (repo). It has to check the colony "manual priorities" setting (UNVERIFIED member); see Compact Work Tab in §1. |
| `add_bill` | table (def or cell), recipe, count or forever | `new Bill_Production(recipe)`, `repeatMode`, `targetCount`, `table.BillStack.AddBill` | verified (repo) and (decomp, `BillStack.cs:69`). It must check for an existing equal bill first, so an edge re-fire after load does not duplicate it. |
| `set_bill_count` | table, recipe, count | `bill.targetCount` | verified (repo) |
| `set_zone_plant` / `set_zone_sowing` | zone label or cell, plant | `Zone_Growing.SetPlantDefToGrow`, `allowSow` | verified (repo) |
| `set_area` | pawn, area label | `pawn.playerSettings.AreaRestrictionInPawnCurrentMap` | verified (repo). Zone To Schedule warning, §1. |
| `set_schedule` | pawn, hour, assignment | `pawn.timetable.SetAssignment(int, TimeAssignmentDef)` | verified (decomp, `Pawn_TimetableTracker.cs:56`) |
| `set_medical_care` | pawn, category | `pawn.playerSettings.medCare` | verified (decomp, `Pawn_PlayerSettings.cs:27`) |
| `set_hostility_response` | pawn, mode | `pawn.playerSettings.hostilityResponse` | field verified (decomp); enum values UNVERIFIED |
| `draft` / `undraft` | pawn or `*` | `pawn.drafter.Drafted = bool` | verified (decomp, setter exists). Edge only, never latched (Undraft After Tucking, §1). |
| `designate` | designation def (Hunt, Tame, Harvest, Mine, Cut...), target thing/cell/rect, filter | `map.designationManager.AddDesignation(new Designation(LocalTargetInfo, DesignationDef))` | verified (decomp, `DesignationManager.cs:167`, `Designation.cs:49`; `DesignationDefOf.Hunt` and `.Tame` verified). Validity checks (can this thing be hunted?) should go through the matching Core `Designator.CanDesignateThing` (UNVERIFIED) rather than RimPLC's own rules. `NEVER_HUNT` stays a tag filter. |
| `forbid` / `unforbid` | things in an area | `Thing.SetForbidden(bool, bool)` | verified (decomp, `ForbidUtility.cs:16`) |
| `set_research` | project def | `Find.ResearchManager.SetCurrentProject(def)` | verified (decomp, `ResearchManager.cs:110`) |
| `pause` / `set_speed` | speed | `Find.TickManager.Pause()`; `CurTimeSpeed` setter | `Pause()` verified (decomp). `CurTimeSpeed` setter UNVERIFIED. |
| `set_drug_policy` / `set_apparel_policy` / `set_food_policy` | pawn, policy label | `pawn.drugs.CurrentPolicy`, outfits / food restriction trackers | `CurrentPolicy` read seen (decomp, `DrugAIUtility.cs:13`); setters and 1.6 tracker names UNVERIFIED |
| `place_blueprint` | def, stuff, cell, rotation | Core designator `Designator_Build` | **UNVERIFIED, Phase 4 only.** Layout is the AI's job (`then` advice), not a coil, in v1. |

Not in the action set, on purpose: anything that spawns, destroys, edits defs, moves things between maps, launches pods or gravships, starts or recalls the Backrooms gate, accepts or pays a demand, or touches files outside RimPLC's own export folder. Those stay advice steps, so a person or Unity decides.

---

## 6. Player UI

**Entry point.** A `MainButtonDef` (XML) with `MainButtonWorker_ToggleTab` (verified (decomp)) opens `MainTabWindow_RimPLC`. Also a keybinding (UNVERIFIED `KeyBindingDef` hookup). Defs are XML in `1.7/Defs/`, so nothing is patched.

**Window layout:**

```
+-- RimPLC ------------------------------------------- [scan 250t | 0.42 ms | live: starving] --+
| Ladder | Tags | Marks | Sensors | Log                                         [Preset v] [Import][Export] |
+---------------------------------------------------------------------------------------------+
|  pri   id                 when (contacts)                         coils / then        mode   |
|  2.00  hostile-on-map    [hostile_threat]                          pause; draft all   advise |  <- green = true
|  2.20  starving          [days_of_food < {FOOD_PANIC_DAYS}]         harvest berries    auto   |
|  4.10  meal-bill         [meals < {MEAL_BILL_TARGET}][stoves>0]     add_bill ...       auto   |  <- grey  = false
|  41.0  title-knight      (requires Royalty - not active)                               -      |  <- hatched = n/a
+---------------------------------------------------------------------------------------------+
```

- **Live highlighting** per contact: green means true, dark means false, amber means **unmeasured** (key missing), and red means an unresolved def or tag. The amber state is the visual form of training family C.
- **Ladder tab:** add, duplicate, edit, enable/disable, set the mode, and reorder by editing the priority. The rung editor is a form: a key picker filled from the live sensor catalogue (so a player can only pick keys that exist), an operator dropdown, a value field that also accepts a `{TAG}` picker, a coil list built from §5 with per-argument pickers drawn from `DefDatabase` (work types, recipes, plants from every loaded mod), and `then` as free text lines.
- **Book rungs** (`source: book`) can be disabled or switched to `auto`, but not deleted or edited in place. "Edit" makes a player copy with the same id that overrides the book rung. This is the same rule `gates.py` uses for her rungs: *"hers replace a book rung of the same id"*. "Revert" removes the copy.
- **Tags tab:** constants and variables, value, min/max, the formula for variables (read only in v1), and override with a clear button. Values outside min/max are refused in the UI.
- **Marks tab:** list, set, clear.
- **Sensors tab:** every key, its current value, its cadence class, its API source line (from §4), and "absent" with the reason.
- **Log tab:** the last 200 coil firings and suppressions, with tick, rung, action, result string (the `RimroomsAutomationComponent` result style) and who caused it (`scan`, `player`, `unity`).
- A **global "outputs armed" switch** that defaults to off for a new game. With it off, RimPLC is an advisor only. This is the safety default for any mod and any profile.

Text goes through `Languages/English/Keyed/RimPLC.xml` keys, as Rimrooms does.

---

## 7. Save, presets, export and import

**Per-game save.** `RimPLCGameComponent : GameComponent` holds the ladder (player and Unity rungs plus overrides), tag overrides, marks, timer/counter state, edge memory, the outputs-armed flag and the scan settings. It uses `ExposeData` with `Scribe_Values` (verified (repo)) and `Scribe_Collections.Look` over `IExposable` rung classes (UNVERIFIED call shape; it is standard, but check against the decomp). **Book rungs are not saved**; only the preset id and version are. Updating the mod updates the book, and player overrides survive by id.

**Presets.** These are JSON files in `Mod/RimPLC/Presets/`:

- `LadderV2.json`: the default full-run ladder (§9). Loaded as the book on a new game.
- `Advisor-Minimal.json`: survival and threat rungs only, all `advise`.
- Mod-supplied presets: any mod may ship `Presets/*.rimplc.json`. RimPLC scans `ModLister`/active mod folders for that folder name (UNVERIFIED enumeration API).

**Export and import.** The format is the **same JSON shape as `docs/playbook.gates.json`** (`version`, `gates[]`, `tags.constants`, `tags.variables`) plus the new optional fields (`coils`, `mode`, `requires`, `source`, nested conditions). Export writes to `GenFilePaths.ConfigFolderPath/RimPLC/` (UNVERIFIED member name). Import validates every rung: id rules, priority is a number, keys exist in the catalogue or are `mark_*`, coil arguments resolve, and `then` has at most 8 lines of at most 300 characters (the `t_ladder_set` limits). Import shows a diff and the player confirms. **JSON parsing needs no extra library:** RimWorld does not ship Newtonsoft in Core, and RimBridgeServer's copy cannot be referenced without a dependency. So RimPLC carries a small hand-written JSON reader/writer (about 300 lines). The alternative is presets as XML through `Scribe`, with a converter script outside the game.

---

## 8. AI API

### 8.1 Primary: RimBridge companion tools

RimBridgeServer supports third-party tools (installed README, *Third-Party Extension Tools*): a companion DLL references `RimBridgeServer.Sdk`, marks methods `[Tool("name")]`, and is placed in the `BridgeTools` root. **RimPLC core never references the SDK.** The companion is a separate assembly, `RimPLC.BridgeTools.dll`, deployed to `<RimWorld>/BridgeTools/RimPLC/`. That fits the README's paired-deploy rule: the mod in `Mods/RimPLC`, the companion in the sibling `BridgeTools/RimPLC`. Without RimBridgeServer, nothing loads it and nothing breaks.

| Tool | Args | Returns |
|---|---|---|
| `rimplc/read_ladder` | `top` (default 4), `all` | Exactly the `t_ladder` shape: `live_rungs[{id, priority, then, matched}]`, `tags`, `my_marks`, `my_rungs`, plus `unresolved_conditions`, `disabled_rungs`, `scan_tick`. `matched` closes Ladder v2 engine change 6. |
| `rimplc/read_state` | `keys` (optional filter) | The sensor dict, the same keys `gates.py state()` returns, with absent keys omitted |
| `rimplc/set_tag` | name, value | Same rules as `t_ladder_set tag` (`[A-Z0-9_]{1,40}`), clamped to min/max, refused for owner-only constants (§8.4) |
| `rimplc/set_mark` | name, value (bool or number) | `[a-z0-9_]{1,40}` |
| `rimplc/upsert_rung` | rung | Same validation as `t_ladder_set add_rung`, including the `unity-` id prefix and the 8x300 `then` cap. `mode` is forced to `advise` (§8.4). |
| `rimplc/remove_rung` | id | Only `unity-*` and `player-*` copies; book rungs are refused |
| `rimplc/enable_rung` | id, enabled | Book rungs: disable needs the owner (§8.4) |
| `rimplc/fire_rung` | id, `dry_run` | **Fire-and-report.** Evaluates the rung now, runs its coils once if it is true and outputs are armed (or reports what it would do when `dry_run`), and returns per-coil results, then the re-read of the sensors the rung's `when` names. This is the training family B "act, then verify by re-reading" loop in one call. |
| `rimplc/export` / `rimplc/import` | path / json | As §7 |

**Main-thread rule.** Game state can only be touched on the main thread. It is UNVERIFIED whether `[Tool]` methods are called on it. The SDK offers `ctx.Game.NextFrameAsync()` (README), so every RimPLC tool awaits one frame before touching state, unless the decomp of the SDK shows that calls are already main-thread.

`list_capabilities` will then show `rimplc/*` dynamically, and `tools.py` picks the tools up by name (§9).

### 8.2 Name collision

Tool names are global, and collisions are rejected and reported (README). The prefix `rimplc/` is reserved.

### 8.3 Fallback: file inbox

This is for when no RimBridgeServer is loaded (the shipped product has no bridge; `docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md`: *"the rim api / RimBridgeServer overlay is not in the package"*). It uses the `RimroomsAutomationComponent` pattern: `<config>/RimPLC/inbox.jsonl` with one command per line using the same names and arguments as §8.1, results in `outbox.jsonl` with `id` echoed, and a per-pass cap of `MAX_COMMANDS_PER_PASS` (already a constant in the playbook). This is how the open-source autopilot (`project_open_source_autopilot`) can drive RimPLC with no bridge at all.

### 8.4 Who may change what (LAWs)

- **CHAT NEVER COMMANDS ANYTHING BUT THE GAME** and training family F. Unity's edits come through the AI API. Some edits need the owner, which means a field in the request that only the CLI side sets, never chat. These are: turning a rung to `auto`, arming outputs, disabling a book rung, and changing a constant flagged `owner_only`. Without the owner flag, the API returns `refused: owner only`, and that refusal is itself training data.
- **THE STREAM IS CLEAN.** `message` and `letter` coils display on stream. Their text comes from rungs, so the import/upsert validator runs the same clean-word filter the stream speech uses (that filter's location is UNVERIFIED in this design; reuse it rather than writing a new one).

---

## 9. Migration: `gates.py` and brain training move to RimPLC

The owner's order is that RimPLC exists **before** the three pods train. The brain has to learn RimPLC's ladder and tool shapes, not the Python ones.

**Step 1: freeze the schema first (it gates data generation).** Lock the rung JSON (§3, §7), the sensor key catalogue (§4), the tool names and result shapes (§8.1). Once frozen, the Ladder v2 episode generator can produce data even before the C# is finished, because it scripts states and gold answers from the schema.

**Step 2: convert the playbook.** A one-off converter (Python, under `.local/autopilot/`) reads `docs/playbook.gates.json` plus the Ladder v2 families and writes `Mod/RimPLC/Presets/LadderV2.json`:

- `when` and `then` are copied unchanged. Every `book` rung is `mode: advise`, so behaviour equals today's.
- `disabled` rungs stay disabled, with the reason kept.
- Sensors that are now measured (`research_*`, `title_rank`, `outdoor_temp`, `wealth`, `caravan_out`, `lowest_mood`) turn their old `mark_*` conditions into sensor conditions. The converter logs each rewrite.
- DLC families get `requires`.
- `tags` copies across. The 7 computed variable formulas become formula strings.

`docs/playbook.gates.json` stays as the source of record until the owner retires it.

**Step 3: `gates.py` becomes a thin client.** `decide()` and `state()` call `rimplc/read_ladder` and `rimplc/read_state` when the tools exist (checked once with `rimbridge/list_capabilities`), and fall back to today's code otherwise. `t_ladder` and `t_ladder_set` in `tools.py` map one to one onto `rimplc/read_ladder`, `set_mark`, `set_tag`, `upsert_rung` and `remove_rung`. Her existing `scratch/ladder.json` (marks, tags, her `unity-*` rungs, `letters_seen`) is imported once through `rimplc/import`.

**Step 4: parity read (a manual verification, not a test suite, per the NO TESTS LAW).** On one save, run `gates.py --all` the old way and RimPLC `read_ladder all=true`. Compare which rungs are live and the key values. Expected differences, written down beforehand:

- resource counts: storage versus camp sweep
- `hostiles_on_map`: the threat API versus the "raid" letter
- keys that now exist on maps away from home

Every other difference is a bug to fix before training.

**Step 5: training data in RimPLC's shape.**

- The tool result the brain sees in families A–F is the `rimplc/read_ladder` JSON. Because it keeps the `t_ladder` field names, the existing `brain-life` and admin/pacing sets stay valid; only new fields are added.
- The tool names the brain calls switch from `ladder` / `ladder_set` to the `rimplc/*` names, or keep the old names as `tools.py` aliases. **Owner decision needed** (§12); keeping the aliases means no existing training data has to be re-labelled.
- Add a family **G: fire-and-report** (`rimplc/fire_rung` with `dry_run`, then for real, then read the re-read sensors).
- The generator's validator checks every `when` key against the frozen RimPLC catalogue instead of the Ladder v2 §1 table.

**Step 6: the pods train** on that data. RimPLC phases 3–4 can keep shipping after training, because they add actions and UI, not new shapes the brain needs.

---

## 10. Build phases

| Phase | Contents | Done when |
|---|---|---|
| **P0: schema freeze** | Rung/tag/mark JSON v1; sensor catalogue (§4 names and types); tool names and result shapes (§8.1); the converter (§9 step 2) producing `LadderV2.json` | The converter output loads in a stand-alone Python checker that applies the §7 import rules. Data generation for the pods can start here. |
| **P1: MVP (first shippable)** | `src/RimPLC` project; `RimPLCGameComponent` with the scan cycle (§3.4), the **existing operators plus `>=`, `<=`, `!=`**, numeric marks, the 7 variable formulas; about 45 sensors (all of §4.1–4.3 plus `research_*` and `alert_*`); the `LadderV2` book preset; save in the game file; the window with the **Ladder** (read, enable/disable, live highlight including amber for unmeasured), **Tags** (override) and **Marks** tabs; **advise mode only**, the only coils being `message`, `set_mark` and `set_tag`; the companion tools `read_ladder`, `read_state`, `set_tag`, `set_mark`, `upsert_rung`, `remove_rung`, `enable_rung`; the `gates.py` thin-client switch; the parity read | The parity read passes, on the owner's say-so, on one live save. **This is what must exist before the pods train.** |
| **P2: full editor** | Rung editor form with def pickers; `any` / `not` / `ton` / `tof` / `ctu` / `ons`; export/import with diff; file inbox fallback (§8.3); the Sensors and Log tabs; performance readout and budget skip | A player can build a new rung from scratch in the UI and see it fire |
| **P3: actions** | `auto` mode, outputs-armed switch, arbitration, all §5 actions marked verified; `fire_rung` with real execution; owner-only gates (§8.4); register warnings (ZtS, Undraft After Tucking) in the editor | Each action has been fired once on a disposable save, with the result in the Log tab |
| **P4: integration and breadth** | Rimrooms link assembly (§2.2) with gate sensors; DLC sensors from §4.5 one at a time; mod-supplied presets; multi-map scope; `place_blueprint` if verified | Rimrooms present and absent both load clean; each DLC on and off loads clean |

Build and deploy steps follow `docs/BUILDING.md`. The owner stages and launches, as for Rimrooms. Agents do not launch the game.

---

## 11. Risks

1. **Timeline versus the pods.** P1 is a real C# mod plus a bridge companion. If it slips, training waits. Mitigation: P0 alone unblocks data generation, and the brain's tool shape equals `t_ladder`'s, so data made against P0 stays valid after P1 lands.
2. **Semantics drift between Python and C# sensors** (storage counts versus sweep counts, threat API versus letter). The brain learned the old numbers. Mitigation: the parity read (§9 step 4), with the expected differences written down beforehand, and the training data regenerated from RimPLC reads.
3. **Bridge thread and SDK version.** It is UNVERIFIED whether `[Tool]` calls run on the main thread, and an SDK version mismatch means the companion is skipped (the README tells you to check `get_bridge_status`). Mitigation: always await a frame; fall back to the file inbox.
4. **Automation fighting the player and mods** (Zone To Schedule, Undraft After Tucking, Compact Work Tab manual priorities, Automatic Power Switch). Mitigation: edge-only coils, no latched game state, outputs off by default, no power actions, and register warnings in the editor.
5. **Save-removal safety.** Removing a mod with a `GameComponent` from a save is UNVERIFIED as clean. Mitigation: check on a disposable save before release, and document it.
6. **Alert reading.** Building duplicate `Alert` instances may have side effects (UNVERIFIED). Mitigation: read-only reflection on the private list as a fallback, still with no Harmony.
7. **Performance at scale** (300 rungs, 294 mods, multiple maps). Mitigation: cadence classes, no cell sweeps, budget skip, and a measured readout.
8. **Duplicate bills or designations after load.** Edge memory is saved, but a load between edge and action could re-fire. Mitigation: each action is idempotent (it checks for an equal bill or designation first).
9. **Hand-written JSON parser bugs** on import. Mitigation: a strict, small grammar; refuse on any error; never partial-apply.
10. **Chat safety.** An `upsert_rung` path open to the brain could be steered by chat. Mitigation: owner-only gates (§8.4), forced `advise` for Unity rungs, and family F training.
11. **UNVERIFIED APIs** listed in §4 and §5. Each must be checked in `.local/decomp/roofscan` before the code uses it. None of them blocks P1 except `Downed` and `Paused`, which are trivial to confirm.

---

## 12. Open questions for the owner

These are asked, not flagged (per *ask, never flag*). The coordinator should put them to the owner:

1. **packageId and display name:** `Operator.RimPLC` / `RimPLC`?
2. **Brain tool names:** keep the `ladder` / `ladder_set` aliases (no relabelling of existing data), or switch the training data to `rimplc/*` names?
3. **Default for a new game:** outputs armed off, advisor only (proposed), or on?
4. **Is the Rimrooms automation inbox retired** once RimPLC covers its six commands, or kept as is?

## Owner decisions (2026-10-12, verbatim)

1. **Package id:** "no unity ai lab shit  option 2" -> `Operator.RimPLC`. No lab branding anywhere in the mod.
2. **Brain tool names:** "Keep ladder/ladder_set (Recommended)" -> the brain keeps calling `ladder` / `ladder_set`; they map onto RimPLC underneath, existing training rows stay valid.
3. **Default mode:** "option one its what the ai checks or human is notified to their game like a auto updating checkl ist of controls and switchs and replays and contactors for signaling and control like a electrical mechanic would do ie float switch for healt bars and colonist has taken damage pausing and liek can she handle this fight if yes unpasue if no plan help o can help get there soon? no then run keep range too many get help like all this type of shit for everything from low food to low ship fuel to too many junk wepons needed to sell, not enough steel supply shortage needed supplies at level, ect ect defenses secure if so then if no then, buildings damaged? set repairs if pawns safe, ppawn bnleeding is there enemy on map if so daft all kill thing, save pawns field tend before carry to hospiital ectect ect you know what i mean"
   -> Advise-only by default. The ladder is an **auto-updating checklist of controls, switches, relays and contactors** the AI checks or the human is notified by, wired like an electrician would: a float switch on health bars; colonist took damage -> pause -> can she handle this fight? yes -> unpause; no -> can help get there soon? no -> keep range; too many -> get help. The same pattern covers everything: low food, low ship fuel, too many junk weapons to sell, steel / supply shortage against set levels, defenses secure? yes/no branches, buildings damaged -> set repairs if pawns safe, pawn bleeding -> enemy on map? draft all, kill the threat, field tend before carrying to hospital.
   -> Built in the ladder (2026-10-12) as five linked-rung chains (combat, medical, repairs, defense, supply), advise-only, each rung with `chain`, `check` and `notice`: see `training/ladder-v2/DESIGN.md` §6.1. RimPLC's book preset carries them across unchanged (§9 step 2).
4. **Old Rimrooms automation inbox:** "Keep both" -> the inbox stays as a fallback when RimPLC isn't installed; both paths fire one-shot on a rung's rising edge so they never double-act.

**Package layout update — 2026-10-12:** current RimPLC content and build output now use `RimPLC/1.7/`. `LoadFolders.xml` maps both game 1.6 and 1.7 to that one folder. The dated P1/P2 receipts below preserve the original `1.6/` output paths used for those builds; they do not describe the current copyable layout.

## Built status (2026-10-12): P0 and P1 built, compiled, not staged

Owner, verbatim: *"get to that PLC work to finish it"*. Built in the repo only. Nothing was copied into a `Mods` folder or the game install, nothing staged, nothing deployed, the running game was not touched. **Location differs from §2.1:** the mod lives in `RimPLC/` at the repo root (source in `RimPLC/Source/`), not `src/RimPLC` + `Mod/RimPLC`, so its build output stays inside its own folder.

**P0, schema freeze: done.**

- `docs/rimplc/schema/`: `ladder.schema.json` (top level), `rung.schema.json`, `sensor.schema.json`, `tag.schema.json`, `mark.schema.json`, `tools.schema.json` (every `rimplc/*` tool's args and result, the inbox/outbox line).
- `tools/rimplc-check.py`: validates a ladder against the schemas plus the §7 import rules; `--emit` writes `RimPLC/Presets/LadderV2.json` (the playbook unchanged plus `preset`, per rung `source: book`, `mode: advise`, and `requires` on 23 DLC/Backrooms rungs). `docs/playbook.gates.json` itself is unchanged and valid (127 rungs, 81 sensors, 17 constants, 27 variables); six keys used only by disabled rungs are reported as notes. `gates.py decide()` loads both the playbook and the preset and gives the same answer.

**P1, the mod: done, compiles clean** (`dotnet build -c Release`, 0 warnings, 0 errors, warnings are errors) to `RimPLC/1.6/Assemblies/RimPLC.dll` and `RimPLC/BridgeTools/RimPLC.BridgeTools.dll`.

| Part | File | State |
|---|---|---|
| About | `RimPLC/About/About.xml` | `Operator.RimPLC`, no `modDependencies`, no lab branding |
| Engine | `Engine.cs`, `Rung.cs` | Port of `gates.py` `tags`/`_bound`/`_holds`/`explain`/`rungs`/`decide`, latch, grace, numeric marks, `>= <= !=`, POD_FUEL from POD_SQUAD, unresolved and unknown keys. Adds `requires` gating and the player's switch. |
| Sensors | `Sensors.cs` | 79 of the 80 named book sensors plus the `alert_<x>` family, read from the game; `wall_gaps` stays not measured. New keys: `lowest_health_pct`, `bleeding_count`, `needs_tend_count`, `able_shooters_armed`, `hostile_threat`, `outdoor_temp`, `wealth`, `lowest_mood`, `research_<def>`, `research_current`, `research_queue_empty`, `title_seniority`, `caravan_out`, `alert_classes`. Health and bleeding come from the game's own `HediffSet.BleedRateTotal`, `HasTendableHediff`, `SummaryHealthPercent`, closing the gap that the bridge cannot see pawn health. |
| Scan cycle | `RimPLCGameComponent.cs` | Every 250 ticks (60-2500 in the window); fast / normal / slow cadence; 3 ms budget with slow-skip (measured 1.31 ms live); paused = once a real second, no output |
| Outputs | same | Advise only: rising-edge `notice` messages (book and player rungs), coils `message` / `set_mark` / `set_tag` only on `auto` rungs, every other action refused and logged |
| Save | same | `ExposeData`: marks, tag overrides, player/Unity rungs (as JSON), switches, modes, edge memory, seen letters, scan settings. The book is not saved. |
| Window | `MainTabWindow_RimPLC.cs`, `1.6/Defs/MainButtonDefs/` | Ladder (live highlight per contact, on/off, advise/auto, detail panel), Tags, Marks, Sensors, Log |
| AI API | `Api.cs`, `RimPLC.BridgeTools/` | `rimplc/read_ladder` (keeps `live_rungs`, `tags`, `my_marks`, `my_rungs`, `unknown_keys`), `read_state`, `set_tag`, `set_mark`, `upsert_rung`, `remove_rung`, `enable_rung`; main thread through the SDK's `IRimBridgeContext.MainThread.InvokeAsync` |
| File fallback | `Inbox.cs` | `<config>/RimPLC/inbox.jsonl` -> `outbox.jsonl`, claim by rename, `MAX_COMMANDS_PER_PASS` per pass, works while paused |

Expected parity differences against `gates.py` (for the §9 step 4 read): stores count storage (`ResourceCounter`) not the camp sweep; `days_of_food` uses `TotalHumanEdibleNutrition`; `hostiles_on_map` is the threat API count, not the letter-vouched crowd; buildings are counted per object, plants/animals/weapons over the whole home map; `colony_animals` / `colony_mechs` read 0 when there are none (the bridge left them absent); `ticks_moving` is `!Paused`; `explore_done` is the mark `explore_done`; `loose_weapons` counts every weapon on the ground, not only `Gun_`/`MeleeWeapon_`/`Bow_`.

UNVERIFIED in the code (marked in comments): `UnityEngine.Application.isFocused` for `game_foreground` (Unity, not in the Assembly-CSharp decomp); `alert_food_rot` (label substring, no Core class found); reading `AlertsReadout.activeAlerts` by reflection (field verified, timing not); the building def-name heuristics carried over from `gates.py` (`Embrasure`, `Grav`, `Throne`, `Ship_`); whether removing RimPLC from a save is clean (§11.5); the scan cost at 300 rungs (127 measured live at 1.31 ms). Staged and run live 2026-10-12 on a fresh test colony: bridge tools registered, ladder window renders, parity read done (see docs/TODO.md).

**Not in P1, left for P2 and later:** the `gates.py` thin-client switch and `tools.py` mapping of `ladder`/`ladder_set` onto `rimplc/*`; the parity read on a live save (owner's step); the rung editor form with def pickers; `any`/`not`/`ton`/`tof`/`ctu`/`ons`; export/import with diff; the clean-word filter for Unity rungs' notices (until then they are not shown); converting the measured `mark_research_*` / `outdoor_*` / `caravan_out` conditions to sensor conditions in the preset; P3 game actions, arbitration and the outputs-armed switch; P4 Rimrooms link and DLC sensors.

## Built status (2026-10-12): P2, everything that needs no live game

Owner, verbatim: *"get to that PLC work to finish it"*. As with P1, this was built in the repo only. Nothing was copied into a `Mods` folder, the game install or a save, nothing was staged, and the running game was not touched. Both projects compile with `dotnet build -c Release`: 0 warnings and 0 errors, warnings are errors, and the output goes to `RimPLC/1.6/Assemblies/` and `RimPLC/BridgeTools/` only.

**1. Thin client: `gates.py` / `tools.py`.** The brain keeps `ladder` / `ladder_set` (owner decision 2). Their names, arguments and result text are unchanged. Underneath:

| Brain tool | RimPLC (bridge `rimplc/<cmd>`, else `<config>/RimPLC/inbox.jsonl` `cmd`) | When RimPLC does not answer |
|---|---|---|
| `ladder` | `read_ladder {top: 4}`. `gates.format_rimplc_ladder` keeps exactly `live_rungs[{id, priority, matched, then}]`, `tags`, `my_marks`, `my_rungs`, `unknown_keys`, cut at 5000 characters | `gates.decide(every=True)` + `format_ladder` (the old `t_ladder` text) |
| `ladder_set mark` | `set_mark {name, value}` | `scratch/ladder.json` |
| `ladder_set tag` | `set_tag {name, value}` (never the owner flag) | same |
| `ladder_set add_rung` | `upsert_rung {rung}` | same |
| `ladder_set remove_rung` | `remove_rung {id}` | same |
| (letters looked at) | `letters_seen {}` | `letters_seen` in `scratch/ladder.json` |

- **Number forms.** RimPLC's numbers are doubles. They are given back their Python form, so the text matches. A count of 4 comes back as `4`. The float keys (`day`, `days_of_food`, `fight_ratio`, ...) stay floats, including a `0` from the command file. Tags take the type `gates.tags()` gives. A book rung's priority takes its book value.
- **Mirroring.** An edit RimPLC accepts is also written to `scratch/ladder.json`, so the Python fallback keeps her marks and rungs. A refusal is raised as `REFUSED BY GUARD: <reason>`.
- **Retry.** After a miss, RimPLC is not asked again for 60 s (`RIMPLC_RETRY_S`). The command file is only used when `<config>/RimPLC/` exists (`RIMPLC_DIR` overrides the path).
- **Known text differences when RimPLC answers.**
  - `remove_rung` of an id she has no rung for is refused (`no rung <id>`), where the local file silently succeeds.
  - RimPLC also refuses an `add_rung` that breaks a checker rule the local file never checked: a `{TAG}` that does not exist, a malformed instruction, or a notice that is not clean.

**2. Engine operators** in `Engine.cs`, `gates.py`, `rung.schema.json` (`$defs.instruction`) and `rimplc-check.py`. A `when` value that is an object is an instruction, and its key is its label and the name of its memory:

- `any` (OR of AND-branches) and `not`. An unmeasured input stays unmeasured, so a missing key never fires.
- `ton` / `tof` with `ticks` or `hours` (2500 ticks per hour).
- `ctu` with `preset` and an optional `reset`.
- `ons`.

How they run:

- An instruction pass runs before the rungs are tested, so every timer sees its input every scan, even when an earlier condition already failed.
- Memory moves only on a committed scan: a tick scan in game, or `decide(write=True)`. A paused scan or an API read only looks.
- `matched` for an instruction shows the measured values of the conditions inside it.
- The in-game timers count `TicksGame`. `gates.py` counts `day * 60000` because the bridge state has no tick key, a difference of under 600 ticks.
- Memory is saved with the game (`instructionMemory`) and in `scratch/plc_memory.json`.

**3. Rung editor** (`Dialogs.cs`, Ladder tab: New rung / Edit / Remove or Revert):

- **Fields.** id, priority and requires. Conditions are key + operator + value, with a `{TAG}` picker and a compare-with-key picker. Nested instructions are edited as JSON, with templates for all six. Then lines, notice and why.
- **Key pickers** (a searchable list):
  - sensors: the catalogue and what is measured now
  - marks
  - tags
  - things: items in store, `count_<def>`
  - buildings: buildable, `count_<def>`
  - research: `research_<def>`
  - alerts: every `Alert` subclass, `alert_<class>`
- **Pickers use runtime defs.** Anything in `DefDatabase`, so every loaded mod and DLC shows up. Picking a DLC def adds its DLC to `requires`, and another mod's def adds `mod:<packageId>`.
- **On-demand sensors.** `count_<def>` and `alert_<class>` keys are measured only when a rung names them (`Sensors.ReadDemand`). A def that is not loaded stays unmeasured.
- **Checks.** Check / Save run `Validate.cs`, the same rules as `rimplc-check.py`. Unknown keys are errors in the editor. Through the AI API they stay a note, as `ladder_set` always said.
- **Book rungs.** "Edit" on a book rung saves a player copy under the book id. "Revert" removes it.

**4. Export / import with a diff** (`Transfer.cs`):

- **Export** writes `<config>/RimPLC/exports/ladder-<tick>.json` in the ladder shape. `gates` holds the player's and Unity's rungs. The new optional `rimplc_state` holds marks, tag overrides, switched-off ids and modes.
- **Import** is a merge, never a wipe. Every rung goes through the same upsert path and checks. The diff shows `+` new, `~` changed (with the fields), `=` unchanged (or same as the book) and `!` refused. Nothing applies until Apply.
- **API.** `rimplc/export` and `rimplc/import` (`dry_run` defaults to true) on the bridge, and `export` / `import` in the command file. Through the API, rungs become `unity-` rungs in advise mode. Switching off a book rung, turning a rung to `auto` and changing a constant need the owner flag.

**5. Clean-word filter** (`CleanText.cs`). This is a port of `guards.clean_for_stream`: the SOFTEN and CLEAN_BLOCK rules from `unity-voice.py`, plus EXTRA_BLOCK and TECH_BLOCK.

- **Shown.** Unity rungs' notices and their `message` coils are shown through it. A line it rejects is not shown, and the Log tab says so.
- **Refused.** `upsert_rung`, the checker and the local `ladder_set add_rung` refuse a unity notice the filter rejects.
- **Not ported.** The owner-only secret words list stays out of the mod.
- **Differences from Python.** Links are dropped, not spoken.

**6. Measured sensors replace marks** in the preset. `rimplc-check.py --emit` rewrites 7 conditions in 6 rungs:

| Old mark | Sensor | Rungs |
|---|---|---|
| `mark_research_microelectronics` | `research_microelectronicsbasics` (defName verified) | comms, hitech-bench |
| `mark_research_transport_pod` | `research_transportpod` (defName UNVERIFIED) | caravan-raid, pod-assault |
| `mark_research_xenogenetics` | `research_xenogenetics` (defName UNVERIFIED) | genes |
| `mark_caravan_out` | `caravan_out` | caravan-raid, settlement-down |

- **Fallback.** Each new sensor entry names the old mark as `fallback` (`sensor.schema.json`). `gates.py` cannot measure these keys, so it reads the mark, or false when the mark is unset. RimPLC does the same while a def is not loaded. A wrong defName therefore falls back to the old behaviour instead of breaking.
- **Not converted.** `mark_title_rank` (`title_seniority` is raw seniority, not the 0-7 rank) and `mark_empire_hostile` (not measured yet).
- **The playbook** `docs/playbook.gates.json` is unchanged.

**Verification** (a throwaway script and a C# harness in `%TEMP%`, no game, no bridge; the harness runs `Engine.Scan` from the built `RimPLC.dll`). All passed:

| Check | What it compared |
|---|---|
| `ladder` text unchanged | Old `gates.py` (HEAD) vs the new fallback path, on 400 states derived from the captured `.local/qa` replies x 3 ladders (1,200 cases), byte for byte |
| Preset vs playbook | The same live rungs in `gates.py`, with the research/caravan marks set and unset |
| C# vs Python | The same hits, `unresolved_conditions` and `unknown_keys` on 750 cases, for both the playbook and the converted preset. The thin client's text from the C# result equals the Python text |
| The six instructions | A hand-worked 12-scan sequence, including a non-committing scan, in both engines. `not` of an unmeasured key never fired |
| Thin client | Miss, then fallback, then the retry timer; a bridge reply as JSON text; a command-file round trip; `ladder_set` mapping, text and refusals; mirroring; the local fallback text |
| Clean filter | The C# port equals `clean_for_stream` on 12 lines |
| Validator | `Validate.cs` accepts and refuses the same 10 rungs as `rimplc-check.py` |

**Still needs a live game** (the owner's steps; none was done):

- **Staging and parity.** Staging, and the §9 step 4 parity read on one save.
- **Bridge result shape.** Whether the bridge returns a tool's `Dictionary` result as `structuredContent` or as text. The client handles both, but this is UNVERIFIED live.
- **The window.** How the editor, picker and diff windows look and feel. Whether `AllSubclassesNonAbstract` over `Alert` lists cleanly with 294 mods.
- **Timers and counters.** Whether they behave the same across a save and load.
- **Unverified defNames.** `TransportPod` and `Xenogenetics` (otherwise the mark fallback answers).
- **Export / import.** That it round-trips on a real colony.
- **Performance.** The cost of `count_<def>` sensors at scale (the 1 ms budget).
- **Already pending from P1.** P3 game actions and P4 links.

## Built status (2026-10-13): the full rebuild, remote I/O, warnings

Owner, verbatim: *"i daubt you fully redid the RimPLC for everything ive evr toldd you and the condencment and distillation of all walkthroughs and all the 100s of meta prompts that will be needed for the 100s of levers swtichs and sensorse and variables in the RimPLC being fully complete"* / *"pawn with out a wepaon is a very high rankeing need to fix just like the other hundred and hundreds of sensores need to wewarn properly and be diplayed well organized and formated with in game tool tip explinations"*.

**The ladder** (`docs/playbook.gates.json`, preset `RimPLC/Presets/LadderV2.json`): 380 rungs in 16 families, rebuilt by a multi-agent pass from 880 owner orders (playbooks, every doc, 7 session transcripts) and ~350 walkthrough rules, then a repair-and-merge pass. Mechanical checks are clean (`.local/plc-rebuild/check.py`): valid, no duplicate ids, no priority ties, no mark read but never set, no unknown `when` key, every rung has a meta prompt. The pre-rebuild ladder is kept at `.local/plc-rebuild/playbook.live-before-swap.json`; all working files (owner rules, walkthrough sheets, inventory, critics) are in `.local/plc-rebuild/`.

**Meta prompts** (`.local/autopilot/rung-prompts.json`): one per rung, <=12 lines -- what to look at, the tools in order, the fallback, the done-mark, the owner's key words. Only the live top rung's prompt reaches the model (the brief and the `ladder` tool both append `HOW TO DO [id] NOW`). The system prompt carries only the situation module of the top rung's family (`.local/autopilot/modules/`, built by `tools/build-prompt-modules.py`); the conversation cap is 18,000 tokens inside the 32,768 context so the prompt is never cut from the front.

**Sensors.** `Sensors.cs` plus `SensorsBuild.cs` (normal cadence, each block guarded): crew (unarmed, sidearm, armour, flee, bedroom, children, lovers, plants skill, research-only, prisoners), buildings (benches, multi-analyzers, torch lamps, monolith), power (unconnected consumers, unpowered buildings and embrasures, margin %), rooms (out of 10-35 C, unfloored cells, roof holes, lab light), storage (loose and forbidden items), camp water/marsh, wall blueprints against rock, perimeter gaps, screen state; plus `explore_done`, `bill_rows`, `grid_matches_plan`, `fields_all_default_crop`, `ship_research_done`, letter body text and `condition_<def>` for every active condition. `pawns_unconfigured` and inventory section D are read by `SensorsWorld.cs` (below).

**Remote I/O** (`rimplc/set_host`, `Api.SetHost`): the stream PC's readings -- `seconds_since_spoken`, `chat_unanswered`, `new_joiners`, `chat_asks_mod`, `seconds_since_webcam`, `seconds_since_tool`, `voice_playing`, `owner_input_active`, `prompt_version_changed`, `owner_unread` (added by the desk review below) -- computed by `gates.host_inputs()` and pushed before every ladder read. Merged first (a game reading of the same name wins), no log line, dropped after 120 s.

**Warnings and display.** Every sensor in the catalogue carries `label`, `group`, `tip` and `severity`, and a `warn` rule where the reading can be a problem (123 of the playbook's 165; schema extended; written by `tools/annotate-sensors.py`, and for the preset-only measured sensors by `MEASURED` in `tools/rimplc-check.py`). The Sensors tab shows a warnings panel (critical red, warning amber) and then every reading by group with a formatted value and a tooltip (what it means, when it warns, the key). Generic `alert_*` and `condition_*` readings warn when true. Critical warnings also raise `Alert_RimPLC` in RimWorld's own alert column. An unarmed colonist is critical and has its own rungs: `unarmed-pawn` (2.6, empire_pass while a gun is on the map) and `unarmed-no-gun` (2.65).

**Commands built for the rungs** (Rimrooms `SetupTools3/4.cs`, all in her `game_set` tool with a read-back): `unforbid`, `chop`, `shelter`, `stockpile_camp`, `build` (any architect def, checked per cell), `build_room`, `deconstruct`, `harvest`, `tame`, `slaughter`, `allow_area`, `self_tend`, `schedule`, `drug_policy`, `research`, `bed_medical`, `bed_prisoner`, `cooler_temp`, and (`SetupTools5/6.cs`) `equip`, `capture`, `bill_count`, `zone_create`, `roof_area`, `firebreak`, `pen`, `bury`, `ideo_role`, `save_game`, `stockpile_priority`, `stockpile_copy`, `crew_setup`. **Window:** a family filter on the Ladder tab; the Sensors tab also lists every input a rung asks for with no reading yet (host inputs marked).

**Section D and pawn setup (2026-10-13, second pass).** Owner, verbatim: *"kill em,, we have to finishe the RimPLC and the prep for the vocie repase multipass run"*.
- `pawns_unconfigured` (critical): a colonist counts as set up when, at one scan, it has a gun primary and a melee sidearm (violent pawns), hostility Attack (violent pawns), self-tend (if it can doctor), at least one job, and the "No drugs" policy. Set-up pawns are remembered in the save (`RimPLCGameComponent.ConfiguredPawns`, `configuredPawns`), so a weapon dropped later is the unarmed rung's job, not a "never configured" warning. Fixed by the new `crew_setup` command plus `empire_pass`.
- `SensorsWorld.cs` reads (normal cadence, each block guarded): trade (`trade_ships_in_orbit`, `trade_beacons`, `comms_consoles`, `silver`), caravans (`caravans_out`, `caravan_pawns_out`), pods (`transport_pods`, `pod_launchers`), quests (`quests_active`, `quests_offered`), pens (`pen_markers`, `pen_animals_unpenned`), conduit routing (`power_nets`, `power_nets_dead`), storage (`stockpiles`, `storage_buildings`, `stockpiles_default_priority`), ideology (`ideo_roles`, `ideo_roles_unassigned`, `ideo_leader_assigned`, `ritual_spots`, `ideo_rituals`), visitors (`visitors`, `hospitality_guests`, `guest_beds` -- the guest-bed class name is UNVERIFIED, no Hospitality reference is compiled in). 22 new catalogue entries, all annotated with label, group, tip, warn and severity. 37 catalogue entries that the C# (or the host push) already read were still marked `not-measured`; they are now `verified` with their real source.
- 11 new rungs with meta prompts: `crew-not-set-up` (3.49), `caravan-home-thin` (2.66), `power-net-dead` (17.03), `stockpile-priorities` (17.63, latched), `trade-ship-orbit` (20.02), `trade-beacon-missing` (24.09), `guests-no-beds` (24.21), `pen-animals-loose` (24.57), `pen-animals-roping` (24.58), `quest-offered` (25.02), `ritual-spot-missing` (33.21). The pre-existing priority tie at 2.6 is resolved: `unarmed-pawn` keeps 2.6, `war-manhunter-butcher` moves to 2.61.
- New Rimrooms commands (`SetupTools6.cs`, also in her `game_set` tool and the window's known-command list): `stockpile_priority`, `stockpile_copy` (filter + priority copied from one stockpile to another), `crew_setup`.
- Mod register checked first (`docs/research/mod-register-integration-fields-2026-09-29.csv`): Simple sidearms (sidearms sit in the inventory; the setup check reads both), Wall Orbital Trade Beacon (beacons counted by class), No Quests Without Comms (comms consoles read next to quests), Hospitality (Continued) / Invite to Stay / Storefront / Real Faction Guest (vanilla guest state; guest beds by class name), the storage family -- Adaptive, LWM, Warehouse, RimFridge (`Building_Storage` and vanilla `StorageSettings`, so `stockpile_copy` works on their zones), More filters for animals' pen (vanilla pen marker). Everything is read-only or uses vanilla settings; nothing patches another mod.
- Checks: `rimplc-check.py --emit` valid (391 rungs, 166 sensors in the preset); the merge checker reported CLEAN (no duplicate ids, no priority ties, no mark read but never set, no unknown key, every rung has a prompt) -- but it read the merge round's candidate files (378 rungs), not the live ones; since the desk review below it reads the live files. Both DLLs built against the Krafs refs and copied to `Mod/` and the game's Mods folder.
- **Window items E1-E3, E5, E6 were already built** (`MainTabWindow_RimPLC.cs`: instruction memory, coloured operand contacts, unresolved reasons, mark defaults, MISSING TOOL flags); the earlier "still open" line was stale.

**Still open:** none of the 2026-10-13 work has run in a live game yet; a trade dialog tool (sell/buy by item) and quest accept/decline as commands (the rungs use the UI tools for now); Hospitality's guest-bed class name and bed price; the standalone RimPLC repositories (GitHub `G-Fourteen/RimPLC`, Forgejo `GFourteen/RimPLC`) are not synced with this work (needs the owner's go).

## Built status (2026-10-13): desk review before the first live game

The ladder, the meta prompts and the sensor catalogue were checked against the code that feeds and answers them, the defects fixed, and the checker extended so each class stays caught. Nothing was staged or copied to a `Mods` folder, the game was not launched, and nothing ran on the GPU. `RimPLC.dll` was rebuilt (`dotnet build RimPLC/Source/RimPLC/RimPLC.csproj -c Release -p:RimWorldManagedPath=<Krafs.Rimworld.Ref 1.6.4871>/ref/net472`, 0 warnings, 0 errors) into `RimPLC/1.7/Assemblies/` only; the Rimrooms DLL and `RimPLC.BridgeTools.dll` were not touched.

**Found and fixed** (the new checker on the files before the fix: 61 defects on the playbook, 3 more on the preset):

| Class | Found | Fix |
|---|---|---|
| Rung input nothing writes | 3: `empire_hostile` (empire-hostile), `hud_visible` (config-hud-restore), `owner_unread` (owner-message) -- catalogued `not-measured`, so the three rungs could never fire | `empire_hostile`: `SensorsWorld.Factions`, `Find.FactionManager.OfEmpire.HostileTo(player)` (verified, decomp `FactionManager.cs`), left out with no Empire. `hud_visible`: `Sensors.ReadFast`, `!Find.ScreenshotModeHandler.Active` (verified, decomp `Find.cs` / `UIRoot.cs`; F11 hides the HUD). `owner_unread`: a host input in `gates.host_inputs()` (private studio-inbox lines no `replyTo` answers, newer than the newest answered one, at most an hour old). All three now `verified` |
| Condition that can never hold | 5: `comms_console: ">0"` (br-contact-company, config-post-strictness) and `defences_built: ">0"` (br-sustainable) compare a boolean reading with a number; `embrasure_gaps` was catalogued bool and `monolith` int against what the C# writes | `comms_console: true`, `defences_built: true`; `embrasure_gaps` type int, `monolith` type bool. Two steps/prompts that read `defences_built >= 2` now read "true" |
| Warning rule that never trips / no display entry | 3: `owner_unread` (critical) had a boolean rule on a number, `embrasure_gaps` a number rule on a bool, the preset's `caravan_out` had no label, group, tip or severity | `owner_unread` warns at `>0`; types fixed; `MEASURED` entries in `rimplc-check.py` carry their display fields |
| Catalogue status the code contradicts | 4: `simple_benches`, `hitech_benches`, `multi_analyzers`, `torch_lamps` marked `not-measured` but read by `SensorsBuild` | `verified`, real source |
| Step naming a `game_set` command no handler answers | `campfire/torch`, `barricades` (setup-4b-shelter, setup-7-camp-defence); `schedule` and `drug_policy` declared missing in setup-3-assign though handlers exist; `game_set cmd=unforbid` (unforbid-constant) | `game_set cmd build def Campfire / TorchLamp / Barricade x z`, `schedule assignment Anything hours 6-21`, `drug_policy policy 'No drugs'`; `game_set cmd unforbid`. `terraform` stays declared missing (no handler; the steps carry the designator fallback) |
| Step or prompt calling a tool missing that now exists | 40 (33 rung steps, 7 meta prompts): `set_self_tend`, `set_schedule`, `set_drug_policy`, `set_bill_count`, `zone_create`, `set_ideo_role`, `place_building` / `build_furniture` / the `build` tool, `deconstruct`, `tame_animal`, `build_pen`, `queue_research` / `research_queue` / `set_research`, `set_bed_medical`, `set_cooler_target`, the self-tend toggle, `build_room` | Each rewritten to the `game_set cmd` that answers it, with the UI path kept as the refusal fallback (Penoxycyline queues as `project=PenoxycylineProduction`, UNVERIFIED defName; `research` also matches the label). Still-missing tools stay named (trade dialog, call trader, quest accept, prisoner interaction, marriage, apparel equip, door lock, bed price, form caravan, stockpile filter modes medicine/drugs/valuables/dump) |
| Notes the code contradicts | `empire-hostile` note "empire_hostile is TO_BUILD"; a `why` tail "monolith_level (TO_BUILD)" | measured (`SensorsWorld`; `Find.Anomaly.Level`) |
| Built-status text | the 2026-10-13 section said the merge checker ran "on the live files" (it read the 378-rung candidates) and that every sensor carries `warn` | corrected above |

Clean on review, no change needed: duplicate rung ids 0, duplicate meta prompt ids 0, prompts with no rung 0, rungs with no prompt 0, priority ties 0, marks read but never set 0, the window's known-command list equals the 49 Rimrooms handlers. The P2 note "`mark_empire_hostile` (not measured yet)" and §4.5's `empire_hostile` / `monolith_level` rows are superseded by the sensors above.

**The checker now catches every class.** `tools/rimplc-check.py` runs a wiring pass on the playbook and on the emitted preset (classes W1-W10 in its header): an input with no writer (RimPLC C#, host inputs, fallback marks), a catalogued sensor nothing writes or one marked `not-measured` that is written, a host input not catalogued, a mark nothing sets, a `game_set` command with no handler or a declared-missing one that has a handler, a missing-tool claim for a tool that exists, a window/handler command-list drift, prompt/rung parity, duplicate prompt ids and priority ties, display entries (group from `SensorView.GroupOrder`, label, tip, severity, warn rule form and type), a sensor nothing reads (13 display-only readings are listed by name in `DISPLAY_ONLY`; one that starts being read must leave the list), and C#-vs-catalogue types plus boolean/number comparisons in conditions. `.local/plc-rebuild/check.py` now reads the live files by default (`--candidate` for the merge round), runs that wiring pass, and adds prompts-without-a-rung and duplicate prompt ids. Both report CLEAN; on the pre-fix files the wiring pass reports 61.

**Still open after the review:** none of it has run in a live game; `terraform` has no command; the notes on toxic-fallout, disease and eclipse-battery name sensors not built (`toxic_buildup_max`, `worst_disease_margin`, `battery_days_stored`); `config-post-strictness` stays disabled (no setting); `PenoxycylineProduction` and Hospitality's guest-bed class name are UNVERIFIED.

## Built status (2026-10-13): loose ends closed

Everything "still open after the review" above that can be settled without a live game is settled. Nothing was staged, copied to `Mods`, launched or run on the GPU.

- **Three new sensors** (`SensorsWorld.cs`, normal cadence, each block guarded, each catalogued with label, group, tip, warn and severity by `tools/annotate-sensors.py`):
  - `toxic_buildup_max` (Health, critical at `>=0.4`): the worst colonist's `ToxicBuildup` severity. Read by the new rung `toxic-buildup-high` (2.27, `>={TOXIC_PULL_IN}`: that pawn rests indoors) and named in `toxic-fallout`'s step.
  - `worst_disease_margin` (Health, critical at `<0.1`): immunity minus severity of the worst visible disease a colonist is still racing (1 when none; toxic buildup left out). Read by the new rung `disease-losing-race` (5.45: Medical bed, best medicine, best doctor).
  - `battery_days_stored` (Power, warning at `<1`): stored battery Wd over the current draw in W, left out when nothing draws. `eclipse-battery` now fires only when it is under one day.
  - The three "sensor ... needed" notes are gone. Both new rungs have meta prompts. The ladder was then 393 rungs and 168 sensors (see the next paragraph for the final count).
- **`terraform` command** (Rimrooms `SetupTools6.Terraform`, in her `game_set` enum and the window's command list): `mode bridge` puts a Core `Bridge` blueprint on every cell of `x,z,w,h` that takes one (water, marsh). `mode smooth` and `mode remove_floor` run Core's own `Designator_SmoothSurface` / `Designator_RemoveFloor` cell by cell with their own checks; those designators act on `Find.CurrentMap`, so they are refused unless that map is on screen. **Core has no mud/sand/water-to-soil operation**, and no mod in the profile adds one. So the steps that asked to "terraform to soil" now bridge what is wet and keep fields and builds off what cannot be converted (setup-4b-shelter, setup-6b-crops, setup-7-camp-defence, terraform-water-first, animals-pen-soil). The Rimrooms DLL compiles clean against the Krafs refs; it was built to a scratch folder only, not into `Mod/` (the `src/` tree holds other uncommitted work).
- **Antibiotics research defName confirmed:** `PenoxycylineProduction` (`Data/Core/Defs/ResearchProjectDefs/ResearchProjects_1.xml`, label "penoxycyline production"). No change needed.
- **Hospitality guest bed confirmed:** `Hospitality.Building_GuestBed` in Hospitality (Continued)'s `1.7/Assemblies/Hospitality.dll` (workshop 3509486825, `Orion.Hospitality`). The `guest_beds` match on a thing class whose name contains `GuestBed` is correct; the comment and catalogue entry are now marked verified.
- **§4.5 rewritten** to match the code (what each key reads, where, and which stay marks; `goodwill_<factionDef>` is not built).
- **`config-post-strictness` stayed disabled at this point** (enabled below). The setting that would drive it already exists: the gate's **watch posture**, `CompRimroomsGate.watchPosture` (enum `GateWatchPosture`: `Mild`, `Balanced`, `Strict`; default `Balanced`, the owner's "default in between"; saved as `rr_gateWatchPosture`; changed only by the gate's watch-posture gizmo). The eat/safety floor (`GateWatch.MustLeave`) holds in every posture. Before the rung can run, two things are needed: a `gate_watch_posture` sensor (the Rimrooms link of §2.2) and a `game_set` command to set it. The rung's reason, step and meta prompt now say this.
- **Checker:** W6 also compares her `game_set` tool's `cmd` enum in `tools.py` with the handlers (the mod-internal `sensors` dump excepted). `rimplc-check.py --emit` and `.local/plc-rebuild/check.py` are both CLEAN. `RimPLC.dll` was rebuilt, 0 warnings, 0 errors.

**Commands added in the same pass, wired into the ladder** (the Rimrooms commands `freezer`, `butcher`, `kitchen`, `arm`, `draft`, `hold`, `tower`, `power` and `hall`, from `SetupTools7/8/9.cs`). All of them are in the window's known-command list and in her `game_set` tool enum (`tools.py`, which also gained the `size`, `x1`, `z1`, `x2`, `z2` and `width` arguments); the checker's W6 compares both lists with the handlers.

- **New sensors** (`SensorsWorld.cs`, guarded, annotated). Each is computed with the matching command's own test:
  - `kitchen_tables_no_bill` and `butcher_tables`.
  - `freezer_coolers` (built coolers whose cold side is an indoor room), `freezer_coolers_warm` (of those, set above 0 C) and `cooler_planned`.
  - `corner_<ne|nw|se|sw>_x` / `_z`: the Home area's bounding-box corners, so corners come from the colony's own layout, never the Store's fixed coordinates.
  - `tower_<corner>`: an embrasure built, framed or planned within 8 cells of that corner.
  - `stone_blocks`.
  - The ladder was then 400 rungs and 186 sensors (187 in the preset).
- **Kitchen and food rungs:**
  - `kitchen-bills` (4.85, new) runs `kitchen` while `kitchen_tables_no_bill > 0`.
  - `butcher-table` (5.0) now fires on a built stove, no butcher table, and meat coming in (`corpses > 0` or `designations_hunt > 0`). It runs `butcher`, then `kitchen`.
  - `freezer-cooler` (6.45, new) runs `freezer` when there is a food store, no freezer cooler and none planned.
  - `freezer-set-cold` (6.46, new) runs `freezer` again once the cooler is built and still warm, so -5 C gets set. If the reply says NOT POWERED, it runs `power x z` at the cooler first.
- **Defence rungs:**
  - `unarmed-pawn` (2.6) calls `arm` first, with `empire_pass` behind it. `unarmed-no-gun` (2.65) calls `arm` (it queues the craft bill for the shortfall) and keeps its melee and trader fallback.
  - `war-mobilize` (the raid alert) runs `arm`, then `hold`, with `order_pawn` as the fallback.
  - `war-stand-down` and `combat-0-reset` release with `draft pawn all on false` once no hostiles are left.
  - `tower-ne` / `-nw` / `-se` / `-sw` (27.91-27.94, new, one per corner) run `tower x <corner_x> z <corner_z> size 3`. They fire when there are no hostiles, the corner has no tower, and steel or stone blocks are at 150 or more. `war-bastions-towers` hands the corners to them.
- **Power rungs:**
  - `power-every-consumer` (16.9) now fires whenever a built consumer is on no grid and the colony has power (the camp-stable gate was dropped). It runs `power`, with the conduit designator as the fallback.
  - `power-net-dead` runs `power` first.
- **`hall`:** listed in both command lists. No rung asks for a hall yet.
- **Builds:** `RimPLC.dll` 0 warnings / 0 errors. The Rimrooms project, with `terraform`, compiles 0 / 0 to a scratch folder.
- **Research (`research_next`):**
  - `research-pick-next` (12.9, new) runs `research_next` whenever `research_queue_empty` is true, which is both "none chosen" and "the last one finished", since `GetProject()` is empty in both cases. `research-idle` stays as the by-hand fallback.
  - New sensors `research_upgrades_unbuilt` / `research_upgrades_missing` apply the command's own upgrade list and test: researched and neither built nor planned on the home map.
  - `research-build-upgrades` (14.15, new) builds each name in that list (`build def <name>`, then `power`).
  - The ladder was then 402 rungs and 188 sensors.
- **Generator and prisoners (`generator`, `prisoner`):**
  - `power-no-grid` (15.9, new) fires on no grid at all (`has_power` false, Electricity researched, no hostiles). It runs `generator kind wood` (solar when researched and wood is short), then `power`.
  - `prisoner-new-recruit` (3.55, new) runs `prisoner mode recruit pawn <name>` for each name in the new sensor `prisoners_new_names`. `prisoners_new` counts prisoners still on the initial Maintain-only mode that RimPLC has never seen with a stance of their own. A prisoner seen with any other mode is remembered in the save (`RimPLCGameComponent.PrisonersSeen`, `prisonersSeen`), so a stance the playbook or the player sets (enslave, convert, or maintain later) is kept, and the rung never uses `pawn all`.
  - `growth-prisoner-keep` and `recruit-past-three` now name the `prisoner` command where they said `set_prisoner_interaction` was missing (that name is in the checker's retired list).
  - The ladder was then 404 rungs and 190 sensors. Both commands are in the window list and her `game_set` enum.

- **Trade (`trade`):**
  - `trade-in-reach` (20.01, new) fires when a trader caravan is on the map (new sensor `trader_caravans_on_map`), or a ship is in orbit and a comms console stands. It lists first.
  - It then sells cash crops and refined goods above the new tag `TRADE_KEEP` (50 of each, 10-2000), and buys steel below `STEEL_RESERVE` and components below `COMPONENT_RESERVE`. The negotiator walks there first and the deal runs on the second call. It never sells spacer tech.
  - The visit is marked `trade_visit_done`; `trade-visit-reset` (20.015) clears the mark when the trader leaves.
  - `trade-ship-orbit`, `econ-trader-arrived`, `supply-steel-1-buy`, `supply-weapons-1-sell` and `trade-run` now name `trade` where they said `trade_dialog` was missing. Calling a trader in (`call_trader`) is still missing.
- **Gate watch posture (`gate_posture`):**
  - New Rimrooms `SetupTools12.GatePosture` (`posture=Mild|Balanced|Strict`) writes `CompRimroomsGate.watchPosture`, the field the gizmo writes, by reflection on every gate on the map.
  - The new RimPLC sensor `gate_watch_posture` (0/1/2) reads it by reflection on the comp named `CompRimroomsGate`, so RimPLC still has no Rimrooms reference.
  - `config-post-strictness` is **enabled**: when `gate_watch_posture != 1` it runs `gate_posture posture Balanced` (latched). The eat/safety floor holds in every posture.
- **Hall (`hall`):** the playbook calls for 3-wide halls in `rung-5-the-mountain-base` (the spine and the prison and guest wing halls) and `walls-halls-roofs`. Their steps now use `hall x1 z1 x2 z2 width 3`. They are layout-time steps inside those rungs, with no hall rung of their own.
- **Guest beds (`guest_beds`):** `guest-bed-fees` (24.22, new, latched) lists the guest beds and their fee once `guest_beds > 0`. The playbook gives no fee order (the "$20" the owner quoted was what he saw), so the mod default stays. `guest-wing` and `econ-guest-beds-full` use the list where they said `set_bed_price` was missing.
- **Security rooms (`security_room`):** `security-room-ne` / `-nw` / `-se` / `-sw` (27.95-27.98, new) run `security_room x <corner_x> z <corner_z> size 3` once that corner's tower stands (new sensors `tower_<corner>_built`: a built embrasure within 8 cells), then set `mark_security_room_<corner>`.
- All of these commands are in the window list and her `game_set` enum. `trade_dialog`, `set_bed_price` and `set_prisoner_interaction` are in the checker's retired-name list.
- The ladder is now 411 rungs and 196 sensors. Both checkers are CLEAN. `RimPLC.dll` builds 0/0; Rimrooms compiles 0/0 to a scratch folder.

**Still open:** none of this has run in a live game; calling a trader in (`call_trader`) has no command.
