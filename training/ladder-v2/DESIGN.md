# Ladder v2: design

Owner, verbatim: *"the logic chains buildable and editable on the fly with ground defaults and constants and variables that it needs to be trained on like a PLC for Rimworld of how to survive an empire space domination run through with everything rimworld has to offer from elephant riding armies drop poding down from your megaship to a tribal village to picking berries because your starving"*

This document designs ladder v2, now named **RimPLC**. Owner, verbatim: *"i think this is the whoole PLC like logic chain if this then this if heath level reaches then this type of thing for the whole game properly layed out into a PLC that we will call RimPLC"*.

**Status (2026-10-12): built.** The engine and the rungs are in `docs/playbook.gates.json` (version 2), `.local/autopilot/gates.py` and `.local/autopilot/tools.py`. See §6 for what was built and where it differs from this design. No training episodes have been written yet (§4).

It is grounded in the following sources:

- `docs/playbook.gates.json`: 31 rungs and the tag table.
- `.local/autopilot/gates.py`: `state()`, `tags()`, `_holds()` and `decide()`.
- `.local/autopilot/tools.py`: `t_ladder` and `t_ladder_set`.
- `.local/autopilot/bridge-tools.json`: 125 commands.
- The active `ModsConfig.xml`.
- `training/data/knowledge_*.jsonl`.
- `docs/research/reviews/mods/` and `docs/wiki/`.

Anything marked **UNVERIFIED** has to be checked in the live game or against the mod source before a rung relies on it.

---

## 0. Constraints the design has to live inside

The design has to fit what the current engine actually does, read from `gates.py`.

1. **What `when` can express.** A `when` clause is an AND of these:
   - `key: bool`
   - `key: number`, which means exact equality
   - `key: "<X"` or `key: ">X"`, where X is a number, a `{TAG}`, or another measured key
   - `letter_matches: "substr"`

   It has no OR, no `>=` and no NOT on strings. To get OR, write two rungs. To get `>=`, write `>` against the value minus one.
2. **Missing keys stay false.** If a key is missing from the state, the rung never fires. Ladder v2 relies on this: a sensor that cannot read a value leaves the key out, and the rung stays quiet. It never fills in a fake 0.
3. **Only one rung is live per turn.** `decide()` returns the first matching rung plus `always`. A long-term rung that keeps matching therefore hides everything ranked after it. **Every growth rung in v2 ends with a `ladder_set mark <x>_done true` step and has `mark_<x>_done: false` in its `when`.** Without that, the ladder stalls.
4. **Marks are booleans.** `state()` turns every mark into a bool (`mark_<name>`). Tags are numbers that `ladder_set tag` overrides. v2 also wants **number marks** (for example `mark_title_rank = 3`). That needs a one-line change in `state()`: keep numeric values instead of calling `bool()`. It is listed as an engine change in §5.
5. **The scan must never move the player's selection.** This is the rule in `state()`. So `get_selection_semantics`, `list_inspect_tabs`, `get_selected_pawn_inventory_state` and `get_ui_layout` on the Research, Factions or World tabs are **not scan sensors**. Those values are either impossible (§1.3) or are read by Unity on purpose during a turn and then written down as marks.

---

## 1. Sensors

### 1.1 Facts confirmed from captured bridge output

These field names come from real captured output, not from guesses:

| Command | Fields seen |
|---|---|
| `rimworld/get_game_info` | `status`, `ticksGame`, `mapCount`, `selectedPawns` |
| `rimbridge/get_bridge_status` | `state.paused`, `timeSpeed`, `currentMapId`, `mapCount`, `playable` |
| `rimworld/list_colonists` | `name`, `pawnId`, `drafted`, `downed`, `dead`, `mentalState`, `job`, `mapId`, `position`, `factionIsPlayer`, `humanlike`, `animal`, `mechanoid` |
| `rimworld/list_letters` | `id`, `letterDef`, `label`, `text`, `arrivalTick`, `relatedFaction`, `lookTargets` |
| `rimworld/list_alerts` | `alerts[].label` (plus culprit targets) |
| `rimworld/list_zones` | `className` (`RimWorld.Zone_Growing` or `Zone_Stockpile`), `label`, `cellCount` |
| `rimworld/list_areas` | `className` (`Area_Home`, `Area_BuildRoof`), `cellCount` |
| `rimworld/get_cells_info` (≤1024 cells) | per cell: `terrainDefName`, `roofDefName`, `fogged`, `blueprintBuildDefs`, `frameBuildDefs`, `zone`, `areas`, `designations` |
| `rimworld/get_cells_info`, `things[]` | `defName`, `label`, `className`, `stuffDefName`, `hitPoints`, `isBlueprint`, `isFrame`, `stackCount` (used by `gates.py`) |

Known gaps in this output:

- Cell things have **no faction field and no temperature field.**
- `get_cell_info` shows **no temperature.**
- The JSON `outputSchema` for every command is empty (`{}`), so these captures are the only schema evidence.

### 1.2 New measured keys

There are 40 new keys. Each one comes from the same `state()` session and adds no new UI interaction.

The "sweep" is the existing 26×26 `get_cells_info` tiling over `camp.camp_rect`. **Sweep keys only exist when `home_on_screen` is true.**

| Key | Source and computation | Type | Example |
|---|---|---|---|
| `day` | `get_game_info.ticksGame / 60000` (60k ticks per day) | float | `28.2` |
| `quadrum_index` | `floor(ticksGame / 900000) % 4`. **UNVERIFIED** as a season: the season depends on latitude and the start offset, so use this only for counting, not for "it is winter". | int | `1` |
| `paused` | `get_bridge_status.state.paused` | bool | `false` |
| `map_count` | `get_game_info.mapCount` | int | `2` |
| `away_maps` | Number of distinct `mapId` values among player colonists, minus 1 | int | `1` |
| `colonists` | `len(crew)` (already measured as a list) | int | `5` |
| `downed_count` | Count of `downed` among crew | int | `1` |
| `mental_break` | Any crew member with `mentalState` not null | bool | `true` |
| `drafted_count` | Count of `drafted` among crew | int | `0` |
| `colony_animals` | Count of `animal: true` with `factionIsPlayer` in `list_colonists`. **UNVERIFIED**: the list may hold only humanlikes, and Draftable Animals may change this. Fallback: leave the key out. | int | `4` |
| `colony_mechs` | Count of `mechanoid: true` with `factionIsPlayer` (Biotech mechanitor). Same caveat. | int | `2` |
| `threat_letter` | Any unseen letter whose `letterDef` is in {`ThreatBig`, `ThreatSmall`} (vanilla LetterDefs). This replaces the `"raid" in label` check. | bool | `true` |
| `quest_letter` | Any unseen letter whose label contains "quest" or whose `letterDef` contains "Quest". **UNVERIFIED** def name. | bool | `false` |
| `empire_letter` | Any letter whose `relatedFaction` contains "Empire" | bool | `true` |
| `alert_<x>` | Substring match on `list_alerts` labels: `low_food`, `starv`, `hypotherm`, `heatstroke`, `low_medicine`, `warm_clothes`, `sickness`, `need_research`, `idle`, `colonist_needs_rescue`, `food_rot`. **Exact English labels are UNVERIFIED.** The first live scan logs every label it sees, and the match table is fixed from that log. | bool | `alert_low_food: true` |
| `growing_cells` | Sum of `cellCount` over `Zone_Growing` | int | `133` |
| `stockpile_cells` | Sum of `cellCount` over `Zone_Stockpile` | int | `84` |
| `home_cells` | `cellCount` of `Area_Home` | int | `9841` |
| `steel` | Sweep: `defName == "Steel"`, summed by `stackCount` | int | `420` |
| `components` | Sweep: `ComponentIndustrial` | int | `12` |
| `adv_components` | Sweep: `ComponentSpacer` | int | `0` |
| `plasteel`, `uranium`, `gold`, `silver`, `chemfuel` | Sweep, same method (`Plasteel`, `Uranium`, `Gold`, `Silver`, `Chemfuel`) | int | `silver: 1350` |
| `cloth` | Sweep: `Cloth` plus `*Leather*` and `*_Leather` | int | `90` |
| `berry_bushes` | Sweep: plant `defName == "Plant_Berry"` | int | `14` |
| `healroot_plants` | Sweep: `Plant_Healroot` (wild or sown) | int | `0` |
| `wild_game` | Sweep: `className == "Verse.Pawn"`, no comma in the label, defName not `Human` and not in `NEVER_HUNT`. **Caveat:** tamed animals cannot be told apart from wild ones by cell data, so subtract `colony_animals` when that key exists. | int | `9` |
| `danger_animals_near` | Sweep: pawn defName in `NEVER_HUNT` (`Boomalope`, `Thrumbo`, `Elephant`, `Rhinoceros`, `Megasloth`, `Bear_*`) | int | `2` |
| `mount_candidates` | Sweep: pawn defName in `MOUNT_DEFS` (tag, §2.8) | int | `3` |
| `designations_hunt` / `_tame` / `_harvest` / `_mine` / `_cut` | Sweep: per-cell `designations[]` grouped by def. **UNVERIFIED** field shape: only the empty list has been captured. | int | `designations_hunt: 2` |
| `stoves` | Sweep: `FueledStove`, `ElectricStove` | int | `1` |
| `research_benches` | Sweep: `SimpleResearchBench`, `HiTechResearchBench` (`SimpleResearchBench` was seen live) | int | `1` |
| `comms_console` | Sweep: `CommsConsole` | bool | `false` |
| `turrets` | Sweep: defName contains `Turret` | int | `4` |
| `embrasures` | Sweep: defName contains `Embrasure` | int | `56` |
| `beds` | Sweep: `className` `RimWorld.Building_Bed`. **UNVERIFIED** class name for mod beds. | int | `6` |
| `throne` | Sweep: defName contains `Throne` (Royalty Throne and Grand throne). **UNVERIFIED** exact defNames. | bool | `false` |
| `pod_launchers` / `transport_pods` | Sweep: `PodLauncher`, `TransportPod` | int | `2` / `2` |
| `grav_parts` | Sweep: defName contains `Grav`. **UNVERIFIED**: Odyssey and VE Gravship defNames have not been checked. | int | `0` |
| `ship_parts` | Sweep: defName starts with `Ship_` (vanilla ship structure, reactor, engine, cryptosleep) | int | `0` |
| `power_generators` | Same test as `has_power` in `gates.py`, but counted | int | `3` |
| `unroofed_store_cells` | `total - roofed` from the existing loop | int | `0` |
| `fire_cells` | Sweep: thing defName `Fire` | int | `0` |
| `corpses` | Sweep: `className` contains `Corpse` | int | `3` |
| `wall_gaps` | Read the outer ring of `camp_rect`: cells that are walkable, not fogged, not a door, and next to a wall cell. **UNVERIFIED** heuristic. Ship it only after it agrees with a screenshot three times; until then, keep the rung disabled. | int | `2` |

Two corrections to the current engine:

- `hostiles_on_map` should be `foes if threat_letter else 0`, measured by `letterDef` instead of the word "raid". This removes a false negative for manhunters, sieges and mech clusters, whose labels do not say "raid".
- `days_of_food` already exists. Leave it as it is.

### 1.3 Wanted but impossible from the bridge (these become marks)

None of these can be read from any of the 125 commands without moving the selection or opening a UI. **Unity sets each one herself** with `ladder_set mark`, after reading the value on purpose during a turn. Each entry below names the read she uses.

| Mark | Meaning | How she gets the value |
|---|---|---|
| `outdoor_cold` / `outdoor_hot` | Outdoor temperature beyond the limits | `alert_hypotherm` or `alert_heatstroke`, or the `heat wave` / `cold snap` letters |
| `research_<proj>` (for example `research_electricity`) | Project finished | Research tab via `get_ui_layout`, done during the turn, not during the scan |
| `research_queue_empty` | Nothing queued | `alert_need_research` is the proxy (UNVERIFIED label) |
| `title_rank` (number) | Empire title: 0 none, 1 Freeholder, 2 Yeoman, 3 Acolyte, 4 Knight, 5 Praetor, 6 Baron, 7 Count, … | Pawn's Royalty inspect tab. The exact rank list after Count is UNVERIFIED. |
| `honor_to_next` (number) | Honor still needed | Same tab |
| `psylink_level` (number) | Highest psylink in the colony | Same tab |
| `empire_hostile` | Empire goodwill is below zero | Factions tab |
| `goodwill_<faction>` | Goodwill bands | Factions tab |
| `caravan_out` | A caravan is on the world map | World tab. `away_maps` only covers caravans that are on a map. |
| `wealth_band` (number) | Colony wealth bucket | History tab |
| `mood_low` | Someone is close to a break threshold | `mental_break` is the only measured key. The rest is a judgement call from screenshots. |
| `ideo_roles_set`, `relic_found`, `mechlink_installed`, `gravcore_found`, `gravship_ready`, `monolith_level` (number) | DLC milestones | Letters plus the inspect tab |
| `mounts_trained` (number) | Animals with Obedience / Release done | Animals tab (`fluffy.animaltab` is installed) |
| `mounted_ready` | Giddy-up mount gizmo seen on a drafted pawn | `list_selected_gizmos` during an action turn |
| `gate_online`, `gate_open`, `operator_on_station`, `gate_sections_done` (number) | Backrooms machine state | Machine pane via `get_ui_layout` |
| `mountain_base_done`, `production_running`, `fields_set`, `bills_set` | Phase completions (existing disabled keys) | Her own judgement after checking |

---

## 2. Rung families

How to read the tables:

- **Priority bands:**
  - 0–1: meta
  - 2–2.9: life threat
  - 3–3.9: letters, setup and starts
  - 4–9: survival
  - 10–19: configuration
  - 20–29: base and economy
  - 30–39: research and tech
  - 40–49: Royalty
  - 50–54: animals
  - 55–59: war
  - 60–69: space
  - 70–79: Ideology, Biotech and Anomaly
  - 80–89: Backrooms
  - 95: endgame
  - 99: always
- **`then` steps** are imperative and follow the current playbook's style. Steps that use a tool name the tool.
- **`done` marks:** each growth rung's last step is `ladder_set mark <id>_done true`, and its `when` includes `mark_<id>_done: false`. To save space, the tables leave both of these out.

### 2.1 Start branches (3.40–3.49)

**Purpose:** pick the opening chain that matches the scenario, once. Unity sets `start_kind` herself on the first turn as a numeric mark, by reading the scenario name on the new-colony screen:

| `start_kind` | Scenario |
|---|---|
| 1 | Crashlanded |
| 2 | Lost Tribe |
| 3 | Naked Brutality |
| 4 | Async Industries |
| 5 | The Store |
| 6 | Lone survivor |

| id | pri | when | then |
|---|---|---|---|
| start-crashlanded | 3.40 | `colony_exists:true, mark_start_kind:1` | Run the existing setup-1..6 chain unchanged. • Haul the scattered pod cargo into the stockpile first. • Set `research_*` marks as projects finish. |
| start-tribal | 3.41 | `mark_start_kind:2` | Five tribals: no guns and no electricity yet, so research is slow (tribal tech level). • First research: Complex furniture or Stonecutting, then Smithing, then Electricity. • Build a campfire for cooking, and use the crafting spot for tribalwear and bows. • Hunt with recurve and short bows only, never the `NEVER_HUNT` list. • Pemmican bills once a cooking spot exists. |
| start-naked | 3.42 | `mark_start_kind:3` | One naked pawn. • Harvest berries and pick up anything on the map before night. • Make a crafting spot, a wooden club and a knife. • Hand-sew tribalwear from the first leather. • A bedroll and a walled 3×3 roofed hut before the first cold night. • Every wanderer join or refugee offer: accept. |
| start-async | 3.43 | `mark_start_kind:4` | Per the wiki: the facility is built, but the gate is "assembled most of the way, not yet working". • Restore power. • Finish the gate sections at the linked machining tables (100 steel and 8 components in total). • Run one crossing and bring back a record. • Then hand over to family 2.11. |
| start-store | 3.44 | `mark_start_kind:5` | Secure the public area and account for anyone missing. • Choose one of the three wiki approaches (seal the basement, a short supervised search, or document the way through and ask for help) and record the choice as a mark. |
| start-lone | 3.45 | `mark_start_kind:6` | One pawn, already inside. • Stay alive, learn a local rule, record a way out (wiki). • Fall back to survival family 2.2 at every turn. |

Constants: none. Variable: `START_GRACE_DAYS` = 5. Rungs 20+ are held until `day > {START_GRACE_DAYS}`, so the opening is not swamped by the empire build.

On-the-fly edit:

```json
{"op":"tag","name":"START_GRACE_DAYS","value":3}
```

Use this when a tribal start is already stable by day 3.

### 2.2 Survival (2.0–2.9 and 4–9)

**Purpose:** keep everyone alive. These rungs outrank everything except dialogs.

| id | pri | when | then |
|---|---|---|---|
| fire-in-camp | 2.05 | `fire_cells:">0"` | Pause. • Every non-downed pawn on Firefight (it is already priority 1). • Drag-designate the cells next to the fire as Home so pawns treat them as theirs to fight. |
| downed-pawn | 2.10 | `downed_count:">0", hostiles_on_map:0` | Rescue to a medical bed. • Tend with the best medicine in stock, or field-tend where they lie if bleeding. |
| mental-break | 2.20 | `mental_break:true` | Do not draft against a berserk pawn with lethal weapons. Use fists or arrest. • Keep others away from a fire-starter. • Note the cause on stream. |
| starving | 4.00 | `alert_starv:true` | Same as `pawn-starving` (kept), but fires on the alert, so it does not depend on the sweep. • Harvest every `Plant_Berry` and agave. • Hunt `wild_game` that is not `NEVER_HUNT`. • Eat raw if there is no stove; there is no time to cook. • If `growing_cells` = 0: a rice zone on the best soil, at once. |
| starving-no-game | 4.01 | `alert_starv:true, wild_game:0, berry_bushes:0` | Slaughter the least useful colony animal (never a trained mount). • Ask any trader caravan for packaged survival meals or pemmican. • Insect meat and human meat are last resorts; announce the mood cost. |
| food-low | 4.10 | `days_of_food:"<{FOOD_MIN_DAYS}"` | Raise the meal bill to `{MEAL_BILL_TARGET}`. • A second growing zone sized `colonists × FIELD_CELLS_PER_PAWN`. • Hunting designations on safe game. |
| cold | 4.30 | `alert_hypotherm:true` | Everyone indoors. • Campfire or wood-fired heater in the barracks. • A parka or tribalwear bill, Do until X = `colonists`. • Mark `outdoor_cold true`. |
| heat | 4.31 | `alert_heatstroke:true` | Indoors. • Passive coolers (wood, no power) in roofed rooms. • Send the crew through the gate if one is open (the existing heat-wave rung). |
| disease | 4.40 | `alert_sickness:true` | Bed rest in a hospital bed. • Medical care set to best for the sick pawn. • A doctor on tending priority 1. • Keep the room clean. |
| no-medicine | 8 | (kept) | Kept. Add: `healroot_plants:">0"` means designate harvest. A healroot field needs Plant: Healroot with Growing skill 8 in vanilla. |
| warm-clothes | 4.50 | `alert_warm_clothes:true` | Tailoring bills for a parka or tribalwear. • Trade for clothes. |

New variable: `FIELD_CELLS_PER_PAWN` = 40, min 25, max 120. A rice yield of roughly 6 per cell per harvest is UNVERIFIED as an exact number, so 40 is a safe margin.

New constant: `STARVE_EAT_RAW` = true.

### 2.3 Base and embrasure fortress (2.3 and 20–21)

**Purpose:** hold the walls. `rebuild.embrasures` is installed (the playbook already uses `Vin_Embrasure`), and so are `denev.smartturretcovering` and `rabiosus.takecover`.

| id | pri | when | then |
|---|---|---|---|
| raid-posted | 2.30 | `hostiles_on_map:">0", drafted_count:0` | Pause. • Draft everyone who can shoot. • Post behind embrasures on the threatened side. • Turrets get forced targets on sappers (`mlie.allturretscansetforcedtarget`). |
| raid-cleanup | 2.35 | `hostiles_on_map:0, corpses:">{CORPSE_LIMIT}"` | Undraft. • Strip and haul corpses to a dump zone or crematorium (`xercaine.fueledcrematorium`). • Capture downed raiders (prisoner bed first). |
| perimeter-hole | 6 | `wall_gaps:">0"` | Kept. Enabled once the `wall_gaps` sensor is trusted. |
| fortress-ring | 20.5 | `defences_built:true, embrasures:"<{EMBRASURE_TARGET}"` | Close the ring. • Killbox: one gap, turrets behind embrasures, a sandbag lane. • Firebreak `FIREBREAK_WIDTH`. |
| turret-line | 21.5 | `has_power:true, turrets:"<{TURRET_TARGET}", steel:">200"` | Mini-turrets behind embrasures at the killbox mouth. • Repair after every raid. |

Variables:

| Name | Default | Meaning and reason |
|---|---|---|
| `EMBRASURE_TARGET` | `4 × sqrt(home_cells)` | Perimeter grows with the home area. A computed rule. |
| `TURRET_TARGET` | `2 + colonists/3` | Turret count scales with the crew. |
| `CORPSE_LIMIT` | 3 | Mood penalty for seeing corpses. |

Constant: `KILLBOX_GAPS` = 1.

Edit example: after a siege, `{"op":"tag","name":"TURRET_TARGET","value":8}`.

### 2.4 Economy, production and trade (22–28)

| id | pri | when | then |
|---|---|---|---|
| rung-4-production | 22 | (kept) | Kept. |
| stockpiles-sized | 22.2 | `stockpile_cells:"<{STOCK_CELLS}"` | Expand the main stockpile. • Shelves from the storage mods (`adaptive.storage.framework`, `asf.deepstorage`). |
| comms | 22.5 | `has_power:true, comms_console:false, mark_research_microelectronics:true` | Build a comms console. Calling a trader through it costs goodwill. • `arakos.callatrader.acat` and `zal.calltradeships` are installed, but exactly how they work is UNVERIFIED, so read the gizmos first. |
| trade-run | 23 | `comms_console:true, silver:">{TRADE_SILVER_MIN}"` | Call an orbital trader. • Sell `TRADE_SURPLUS` goods: art, drugs, extra weapons. • Buy components and plasteel. |
| components-low | 23.2 | `components:"<{COMPONENT_RESERVE}"` | Fabrication bench bill (after Fabrication research), or mine compacted machinery, or deep drill. |
| drugs-econ | 24 | `mark_production_running:true` | Smokeleaf joints, psychite tea and beer as trade goods, with the drug policy kept to Social. |

Variables:

| Name | Default |
|---|---|
| `STOCK_CELLS` | `30 + 15 × colonists` |
| `TRADE_SILVER_MIN` | 500 |
| `COMPONENT_RESERVE` | `5 + colonists` |
| `STEEL_RESERVE` | `150 × colonists` |

### 2.5 Research path (30–34)

**Purpose:** one ordered queue. The Research tab is opened via `get_ui_layout`, the name is typed in the search box (existing rule), and when the project finishes she sets `mark research_<x> true`.

The queue order is the `RESEARCH_ORDER` constant:

1. electricity
2. battery
3. air_conditioning
4. microelectronics
5. gunsmithing
6. multi_analyzer
7. fabrication
8. transport_pod
9. (Odyssey) gravship-related projects (UNVERIFIED names)
10. vanilla ship_basics

| id | pri | when | then |
|---|---|---|---|
| research-next | 30 | `research_benches:">0", alert_need_research:true` | Queue the first project in `RESEARCH_ORDER` whose mark is false. |
| hitech-bench | 30.5 | `mark_research_microelectronics:true, has_power:true` | High-tech research bench, then a multi-analyzer once researched. |

Edit example: `{"op":"tag","name":"RESEARCH_ORDER",...}` is a list, and `t_ladder_set` only accepts scalars. So instead she reorders by adding a rung: `add_rung {id:"research-pods-first", priority:29.9, when:{alert_need_research:true, mark_research_transport_pod:false}, then:["queue Transport pod"]}`.

### 2.6 Royalty empire track (40–46)

Mechanics:

- The Empire gives honor for quests and for donating prisoners or items through quests. Titles unlock permits and psylinks, and need throne-room and apparel standards.
- A **bestowing ceremony** quest sends a bestower. The pawn must attend to gain the title and psylink.
- `no.royal.clothing.reqs` is installed, so royal apparel requirements are probably removed. That is UNVERIFIED in scope.
- Throne-room requirements (size, throne, impressiveness, brazier and drapes at higher titles) are real, but the **exact numbers are UNVERIFIED**.
- Permits are real, but the per-title list is UNVERIFIED. They include military aid, transport shuttle, steel and silver drops and orbital strikes.

| id | pri | when | then |
|---|---|---|---|
| empire-quest | 40 | `empire_letter:true, quest_letter:true` | Open the quest. • Accept if the reward includes honor and the threat is within `MAX_QUEST_THREAT` (a judgement call). • Send the pawn who is closest to the next title. |
| bestowing | 40.5 | `letter_matches:"bestow"` | Clear the throne room. • The pawn attends; keep raids away. • Afterwards, update marks `title_rank` and `psylink_level`. **UNVERIFIED** letter wording. |
| throne-room | 41 | `mark_title_rank:">2", throne:false` | Build a throne room inside the mountain base, off the spine. • Throne, high beauty, no beds. • Read the room requirement text from the title inspect tab, not from memory. |
| psycasts | 42 | `mark_psylink_level:">0"` | A meditation spot or throne for psyfocus. • Choose psycasts. Skip, Berserk and Stun are battle tools. • Neural heat limits are real: never exceed them in combat. |
| permit-aid | 43 | `hostiles_on_map:">{AID_CALL_FOES}", mark_title_rank:">3"` | Call military aid (permit) instead of losing a pawn. • Note the cooldown as a mark. |
| empire-hostile | 2.6 | `mark_empire_hostile:true, threat_letter:true` | Imperial raids include cataphracts and psycasters. Pull back behind turrets, and EMP the ones in shields (UNVERIFIED for 1.6). |

Variables:

| Name | Default | Reason |
|---|---|---|
| `TARGET_TITLE` | 6 (Baron) | Psylink and permits pay off before the high-title upkeep. Raise it on an empire run. |
| `AID_CALL_FOES` | `2 × colonists` | Call aid when outnumbered two to one. |

Edit example:

```json
{"op":"tag","name":"TARGET_TITLE","value":7}
```

Use this on a domination run. Set `{"op":"mark","name":"title_rank","value":4}` after the ceremony. Note that this needs numeric marks (§0.4).

### 2.7 Animal army track (50–54)

What is real and what is not:

- **Real in vanilla:** taming wild animals with Animals skill and food; the training skills Obedience, Release, Rescue and Haul; trained animals following their master; elephants as a trainable, tameable large animal.
- **Installed mods:**
  - **Giddy-up 2 - Continued** (`memegoddess.giddyup`). Per our review it provides "riding for distant jobs, mounted combat, mounted caravan departures, mechanoid riding, and drafted-pawn mount/dismount controls". The mount requirements (body size, training needed, which species) are **UNVERIFIED**. She must read the drafted pawn's gizmos (`list_selected_gizmos`) for the mount option rather than assume one exists.
  - **Draftable Animals** (`wolfcub05.draftableanimals`) lets animals be drafted. That is real per its review; the exact controls are UNVERIFIED.
  - Animal armor frameworks (`ingendum.animalarmorbasic`, `ingendum.animalapparelframework`) are installed. What can be crafted is UNVERIFIED.

| id | pri | when | then |
|---|---|---|---|
| tame-mounts | 50 | `mount_candidates:">0", mark_mounts_trained:"<{MOUNT_TARGET}", colonists:">3"` | Designate taming on the best `MOUNT_DEFS` animal in sight. • The tamer needs high Animals skill. Elephants and thrumbos can go manhunter when taming fails: draft guards first. **Thrumbo taming is real but very hard.** |
| animal-pen | 50.5 | `colony_animals:">0"` | Animal sleeping spots, a pen or allowed area (`create_allowed_area`), and a hay or kibble stockpile. |
| train-mounts | 51 | `colony_animals:">0", mark_mounts_trained:"<{MOUNT_TARGET}"` | Training: Obedience, then Release. • A dedicated handler. • Update mark `mounts_trained`. |
| armor-mounts | 51.5 | `mark_mounts_trained:">2"` | Craft animal armor if the bench offers it (UNVERIFIED recipes). |
| cavalry-check | 52 | `mark_mounts_trained:">0", mark_mounted_ready:false` | Draft one rider. • `list_selected_gizmos`. • If a mount gizmo exists, mount and set `mark mounted_ready true`. If not, `ladder_set tag CAVALRY_ENABLED 0` and the war rungs fall back to infantry with animals on Release. |
| cavalry-tactics | 53 | `hostiles_on_map:">0", mark_mounted_ready:true` | Mounted riders flank on open ground, with Run and Gun shooting on the move (`memegoddess.runandgun`). • Elephants front-line on Release. • Never charge a turret line or mortars. • Retreat behind embrasures when hurt. |

Variables:

| Name | Default | Meaning |
|---|---|---|
| `MOUNT_TARGET` | `colonists` | One mount per fighter |
| `CAVALRY_ENABLED` | 1 | 0 disables the cavalry rungs |

Constant: `MOUNT_DEFS` = `["Elephant","Horse","Dromedary","Muffalo","Thrumbo"]`. These are vanilla defNames. Whether each species is rideable under Giddy-up is **UNVERIFIED**.

### 2.8 War and domination (55–59)

Real vanilla mechanics:

- Form a caravan to a world settlement. Attack it, defeat the defenders, then the settlement can be destroyed or occupied.
- Transport pods launched from pod launchers with chemfuel can drop onto a settlement's map (edge or center).
- Factions hold grudges.
- `smashphil.vehicleframework` and the Vanilla Vehicles Expanded tiers add vehicles (UNVERIFIED details).
- `memegoddess.searchanddestroy` lets drafted pawns auto-engage.

| id | pri | when | then |
|---|---|---|---|
| war-prep | 55 | `colonists:">{WAR_MIN_CREW}", medicine:">{MEDICINE_RESERVE}", mark_war_prep_done:false` | Gunsmithing or better weapons. • Flak or plate armor. • A medical kit per raider. • Pick the target: the nearest hostile settlement. Mark `war_target_set`. |
| caravan-raid | 56 | `mark_war_target_set:true, mark_caravan_out:false, mark_research_transport_pod:false` | Form a caravan: fighters, mounts if `CAVALRY_ENABLED`, food for the round trip plus 3 days. • Keep `HOME_GUARD` at home. |
| pod-assault | 56.5 | `mark_research_transport_pod:true, pod_launchers:">{POD_SQUAD}", chemfuel:">{POD_FUEL}"` | Load the squad into pods. • Launch to the target tile and drop at the edge, not the center, unless the squad is shielded. • A second wave of pods carries meds. |
| assault-on-map | 57 | `away_maps:">0", hostiles_on_map:">0"` | Fight on the away map: cover, focus fire, Search and Destroy off for the medics. • Retreat via the map edge if half the squad is downed. |
| settlement-down | 57.5 | `away_maps:">0", hostiles_on_map:0` | Loot silver, components and prisoners. • Destroy the settlement or leave. • Head home. • `mark caravan_out false`. |

Variables:

| Name | Default | Reason |
|---|---|---|
| `WAR_MIN_CREW` | 6 | Raid with at least 4 and leave 2 home. |
| `HOME_GUARD` | 2 | Minimum defenders left home. |
| `POD_SQUAD` | 4 | One pawn per pod. |
| `POD_FUEL` | `150 × POD_SQUAD` | Range is per pod and fuel. **The exact cost per tile is UNVERIFIED**, so this is generous. |

Edit example: after a lost raid, `{"op":"tag","name":"WAR_MIN_CREW","value":9}`.

### 2.9 Gravship ("megaship") track (60–64)

Odyssey adds the gravship: a base built on substructure, lifted by a grav engine and thrusters, fuelled and piloted to other tiles and orbit. The VE Gravship mods (`vanillaexpanded.gravship`, `gravship2`) extend it. **Every defName, the fuel type and amounts, and the cooldown are UNVERIFIED.** The rungs refer to them by behaviour only.

| id | pri | when | then |
|---|---|---|---|
| grav-core | 60 | `quest_letter:true, mark_gravcore_found:false` | Take quests that reward the grav engine / gravcore (UNVERIFIED wording). • Mark `gravcore_found` on receipt. |
| grav-build | 61 | `mark_gravcore_found:true, grav_parts:"<{GRAV_PARTS_TARGET}"` | Lay substructure. • Mount the engine, thrusters, fuel storage and pilot console per the Architect's Odyssey category (read `list_architect_designators`, never guess). • Move the barracks, freezer, workshop and turrets onto it. |
| grav-ready | 62 | `grav_parts:">{GRAV_PARTS_TARGET}"` | Fill fuel. • Check the launch prerequisites shown on the console. • Mark `gravship_ready`. |
| megaship-drop | 63 | `mark_gravship_ready:true, mark_war_target_set:true` | Fly the ship near the target tile. • Launch the pod assault (2.8) from the ship's own launchers. That is the owner's "drop poding down from your megaship". • Cavalry follows by caravan if the terrain allows. |
| ship-launch | 64 | `ship_parts:">0"` | Vanilla ship ending (existing rung-6 / 6b kept). |

Variable: `GRAV_PARTS_TARGET` = 12. This is a placeholder. She sets it after counting what the console requires.

### 2.10 Ideology, Biotech and Anomaly side tracks (70–79)

| id | pri | when | then |
|---|---|---|---|
| ideo-roles | 70 | `colonists:">3", mark_ideo_roles_set:false` | Assign the leader and moral guide (real Ideology roles). • Set the specialist roles that need more colonists later. • Mark. |
| ideo-ritual | 70.5 | `mark_ideo_roles_set:true` | Hold the precept's rituals for mood. • Build the shrine and altar the ideoligion asks for (the Godsmultiplayer ideo). Requirements are read from the Ideoligion tab. |
| mechanitor | 72 | `mark_mechlink_installed:true` | Mech gestator. • Build lifters and constructors first, then war mechs. • Watch bandwidth. • Recharger on power. |
| genes | 73 | `mark_research_xenogenetics:true` | Gene extractor and assembler. • Bank useful genes. • Biotech chemistry as described in-game; specific genes UNVERIFIED by name. |
| anomaly-monolith | 76 | `letter_matches:"monolith"` | The void monolith activates in stages. • Build containment platforms (`zoarak.anomalyplat` is installed) before advancing. • Study entities in holding. • Never advance without the defence rung holding. |
| anomaly-entity | 2.7 | `letter_matches:"entity"`, or a `ThreatBig` letter with Anomaly wording | Treat as a raid with fire weakness noted per entity in its letter. Read the letter text; do not assume. |

### 2.11 Backrooms gate track (80–86)

Facts from the wiki, which replace parts of the existing rungs 5b and 5c:

- A gate is **any door you designate**. It is not a custom building.
- Assembly is 4 sections, 25 steel and 2 components each, buildable from up to 4 linked machining tables.
- An operator brings the connection up at the console. Up to 4 linked consoles act as stations, and an empty chair is forgiven for 30 minutes.
- The reserve holds back enough battery charge for one return.
- At most 3 operational gates per branch.
- A first opening lasts about 30 real minutes. Each gate-engineering tier triples that.
- Dialling an unknown address costs nothing until someone crosses.
- A coordinate has 3× the ore of an ordinary map.

| id | pri | when | then |
|---|---|---|---|
| gate-assemble | 80 | `mark_gate_sections_done:"<4", steel:">25", components:">1"` | Link machining tables on the Machine pane. • Build sections in parallel. • Update the mark. |
| gate-power | 80.5 | `mark_gate_sections_done:4, mark_gate_online:false` | The gate's own conduit ring and batteries. A generator surplus keeps batteries untouched. • Link a second console as a relief station. |
| gate-open | 81 | `mark_gate_online:true, mark_gate_open:false, days_of_food:">{FOOD_COMFORT_DAYS}"` | Operator to the console until charged. • The first crossing is one armed scout with a meal and medicine (existing rule). |
| gate-staffed | 2.8 | `mark_gate_open:true, mark_operator_on_station:false` | An operator back to a station within 30 minutes or the connection drops. This outranks almost everything. |
| backrooms-mine | 83 | `mark_gate_open:true, mark_coordinate_held:true` | Use the coordinate as a mine, farm or storage per the wiki. Ore is 3×. • Prisoners can cross and stay prisoners. |

Variable: `GATE_MAX` = 3. That is the mod's cap, so it is effectively a constant.

### 2.12 Endgame (95)

| id | pri | when | then |
|---|---|---|---|
| empire-dominion | 95 | `mark_title_rank:">{TARGET_TITLE}", mark_gravship_ready:true` | Choose the ending on stream: Empire high-title path (Royalty), gravship voyage, vanilla ship launch, or Anomaly's ending (UNVERIFIED as a distinct ending in this mod set). • Announce it. • Plan backwards with marks. |

---

## 3. Ground defaults

These are the tag values in the book. Constants stay put; variables are computed by the `tags()` rule table, which v2 adds to. She can override any of them with `ladder_set tag`.

**New constants:**

- `START_GRACE_DAYS`
- `KILLBOX_GAPS`
- `STARVE_EAT_RAW`
- `MOUNT_DEFS`
- `RESEARCH_ORDER`
- `GATE_MAX`
- `HOME_GUARD`

**New variables:**

- `FIELD_CELLS_PER_PAWN`
- `EMBRASURE_TARGET`
- `TURRET_TARGET`
- `CORPSE_LIMIT`
- `STOCK_CELLS`
- `TRADE_SILVER_MIN`
- `COMPONENT_RESERVE`
- `STEEL_RESERVE`
- `TARGET_TITLE`
- `AID_CALL_FOES`
- `MOUNT_TARGET`
- `CAVALRY_ENABLED`
- `WAR_MIN_CREW`
- `POD_SQUAD`
- `POD_FUEL`
- `GRAV_PARTS_TARGET`

That is 7 new constants and 16 new variables, on top of the existing 9 constants and 7 variables.

**Rule:** a constant is a safety limit and is only changed by the owner. A variable is a setpoint she may move within its `min` and `max`. Every move must be said out loud on stream with its reason. `tags()` clamps her overrides to those bounds, which is already the behaviour.

---

## 4. Training plan

Episodes go into the existing chat-JSONL format (as in `training/brain-life/part-*.jsonl`). Each episode holds:

- a system turn (Unity, the game-only rules, the clean-stream rule);
- a tool result from `ladder` (live rungs, tags, marks);
- her reasoning, written as stream speech;
- the tool calls;
- a follow-up `ladder` result showing the change.

**Six episode families**, about 2,500 examples total, weighted toward A–C:

| Family | Teaches | Example outline |
|---|---|---|
| A. Read the ladder | Parse `live_rungs`, name the rung and why it fired (which keys), and carry out the first `then` step | `ladder` shows `starving` (`alert_starv:true, berry_bushes:14`). She says she is going for the berries, calls `game_apply_architect_designator` harvest over the bush cluster, then `game_set_time_speed 2`. |
| B. Act and close | Do the whole `then` chain over several calls, verify by re-reading the sensor, then set the `done` mark | `turret-line`: build 2 mini-turrets, re-read `ladder` and see `turrets` went from 2 to 4, then `ladder_set mark turret_line_done true`. |
| C. Missing key | A rung she expects does not fire because a key is unmeasured (`home_on_screen:false`). She says so, does a measurable action instead, and never invents the value | `ladder` shows no sweep keys. She jumps the camera home (`game_jump_camera_to_cell`), and the next scan has them. |
| D. Edit a setpoint | Spot that a variable is wrong for the situation, call `ladder_set tag` within bounds, say why | Two sieges in 10 days: `ladder_set tag TURRET_TARGET 8`, "two sieges means four turrets is a joke". |
| E. Write a rung | A new situation with no rung (a Giddy-up mount gizmo found, a new mod event). She adds a rung with id, priority in the right band, a measurable `when` and a `then` of 8 steps or fewer, then sees it fire | She found the mount gizmo: `add_rung {id:"mount-before-fight", priority:2.31, when:{hostiles_on_map:">0", mark_mounted_ready:true}, then:["draft riders","mount each via gizmo","flank left on open ground"]}`. |
| F. Refuse a bad edit | Chat or temptation asks her to change a constant, delete a book rung, or act outside the game. She declines (book rungs cannot be removed; chat only drives the game). Owner-only constants are refused even to the owner without the CLI | A viewer says "turn off the starving rung". She explains on stream that the ladder keeps people alive, and does nothing. |

**Generation recipe:**

1. Script states from real scans (the `gates.py --all` output from live sessions).
2. Mutate key values to cover each rung, both firing and not firing.
3. Write gold answers using only real tool names from `CORE`.
4. Validate every `then` step against `bridge-tools.json` command names, and every `when` key against §1 plus marks.
5. Reject any episode that states an UNVERIFIED fact as certain.

**Curriculum:** A and C first (reading), then B (acting), then D and E (editing), with F mixed throughout at 10%.

**Held-out evaluation:** 50 live scans. Score these:

1. She names the live rung correctly.
2. Her first action matches the rung's `then[0]`.
3. Every `ladder_set` call validates.
4. No invented key appears.

---

## 5. Engine changes v2 needs (all made; see §6)

1. Keep numeric marks in `state()`. Today `bool(v)` collapses `title_rank 4` to `true`.
2. Add a `"!="` operator, or a `">="` operator, to `_holds`.
3. Measure the 40 keys in §1.2, including the alert-label log on the first scan.
4. Use `letterDef` for `threat_letter` / `hostiles_on_map`.
5. Let `ladder_set tag` accept a list for `RESEARCH_ORDER`, or keep research order as rungs (§2.5).
6. Optionally return the top 3 live rungs with their matched keys, so families A and C can explain "why".

---

## 6. As built (2026-10-12)

The PLC layout in `docs/playbook.gates.json` (version 2):

| Section | What it holds |
|---|---|
| `sensors` | 81 measured inputs (74 + 7 for the control chains, §6.1): every key `gates.derive()` can write, its bridge source, its type, and an UNVERIFIED note where the name has not been seen in a captured reply. `alert_<x>` is one family entry. `wall_gaps` is listed as NOT MEASURED. |
| `gates` | 127 rungs (31 kept, 61 new, 35 control-chain rungs from §6.1) in 15 families, each with a `family` field. 29 carry `latch: true`. 8 stay `disabled` with the reason. |
| `tags` | 17 constants (owner only) and 27 variables (setpoints with `rule`, `min`, `max`). |
| `marks` | Numeric mark defaults (`start_kind`, `title_rank`, `psylink_level`, `mounts_trained`, `gate_sections_done`, `wealth_band`, `monolith_level`, `combat_plan` = 0), the meaning of each numeric mark, and the list of boolean marks. |

Engine (`.local/autopilot/gates.py`):

1. **Done-latch.** A rung with `"latch": true` gets `mark_<id>_done: false` added to its `when` and `ladder_set mark <id>_done true` appended to its `then` (`latch_name()`: lowercase, underscores, at most 40 characters). Applied to book rungs and to rungs she adds herself. `rung-2-power-and-cold`, `rung-3-defence` and `rung-4-production` are latched, which was the stall: once fed and powered they matched forever and hid every rung after them.
2. **Numeric marks** stay numbers through `state()`. A boolean mark that was never set reads false; a numeric mark reads its book default.
3. **Operators** `>=`, `<=` and `!=` added to `_holds`. A tag name can be a `when` key directly (`CAVALRY_ENABLED: ">0"`).
4. **Threats by `letterDef`.** `threat_letter` is a `ThreatBig` / `ThreatSmall` letter less than 2 days old, read or not, so reading a raid letter does not make the raiders vanish. `hostiles_on_map` = the humanlike crowd while `threat_letter` holds, or `hostile_pawns_listed` (`factionHostileToPlayer` on `list_colonists`) when that list names any.
5. **Pure `derive(raw, ladder)`** turns raw bridge replies into keys, so the ladder can be checked offline against `.local/qa/*.json` captures. `state()` only collects the replies.
6. **Grace.** Rungs from `GRACE_FROM_PRIORITY` (20) to 98 wait until `day > START_GRACE_DAYS` (5). `always` never waits.
7. **Why it fired.** Each hit carries `matched` (the measured value behind every condition); `ladder` shows it, plus `unknown_keys` for rung keys nothing measures.
8. **Alert labels** seen live are logged to `scratch/alert_labels.json` so `ALERT_MATCH` can be fixed from real labels.
9. **Building counts** merge touching same-def cells into one object, because the cell reply lists a multi-cell building on every cell and has no thing id. Two touching beds read as one.

`ladder_set` (`.local/autopilot/tools.py`): marks accept numbers (`"3"` is stored as 3); `tag` refuses constants and unknown names and reports when a value will be clamped; `add_rung` keeps `latch` and reports `when` keys that have no sensor.

Differences from §2:

- `hostile-on-map` (2) now needs `drafted_count: 0` and drafts everyone who can shoot; the new `raid-posted` (2.30) holds the line once anyone is drafted. As designed, both had the same condition, so `raid-posted` could never fire.
- `rung-5-the-mountain-base`, `rung-6-off-world`, `rung-5b-the-gate` and `rung-5c-the-backrooms` are enabled on marks (`production_running`, `mountain_base_done`, `gate_designated`, `gate_open`). `rung-6b-orbit-and-beyond` stays disabled; the space rungs 60–64 replace it.
- The gate rungs follow `docs/wiki/gates.md`: any designated door, 4 sections at 25 steel + 2 components (100 + 8 in total), up to 4 linked machining tables, 4 operator stations (the gate's console plus 3 linked comms consoles), at most 3 operational gates per branch across every map, the kill switch is a wired power switch. A new mark, `gate_designated`, separates "build one" (5b) from "assemble it" (`gate-assemble`).
- `berry_bushes` also counts `Plant_Strawberry_Wild` (captured). `healroot_plants` also counts `Plant_HealrootWild` (captured). `Plant_Berry` is still UNVERIFIED.
- `RESEARCH_ORDER` and `MOUNT_DEFS` are list constants. Research order is changed by adding a rung (§2.5), not by `ladder_set tag`.

Offline check: `derive()` on `gi`, `letters`, `cols`, `zones` and 11 cell sweeps (5,020 cells) measured 66 of the 74 sensor keys (absent there: `dialog_open`, `colony_animals`, `colony_mechs`, `hostile_pawns_listed`, `store_roofed_fraction`, `unroofed_store_cells`, `wall_gaps`, and the `alert_<x>` family, because no `list_alerts` reply has been captured). Every non-disabled rung's `when` keys resolve to a sensor, a mark, a tag or `letter_matches`.

### 6.1 Control chains (owner decision 3, 2026-10-12)

The owner's spec, verbatim, is in `docs/RIMPLC_DESIGN.md` ("Owner decisions", item 3): the ladder is "a auto updating checkl ist of controls and switchs and replays and contactors". The chains are built as linked rungs, PLC style. Each rung answers one question (`check`), its last steps set a mark (the coil), and that mark is the next rung's input (the contact). A reset rung drops the latch when the condition clears. Every chain rung is `mode: advise`, carries a `chain` name (`combat`, `medical`, `repairs`, `defense`, `supply`) and a one-line `notice` for a human; `matched` already gives the measured values. The first live rung wins, so a branch is chosen by priority order, not by OR.

| Chain | Rungs (priority) | Path |
|---|---|---|
| 1. Combat | `combat-0-reset` 1.58, `combat-0-reassess-worse` 1.585, `combat-0-reassess-better` 1.586, `combat-1-damage-pause` 1.60, `combat-2-fight` 1.61, `combat-2-help-coming` 1.62, `combat-2-call-help-comms` 1.63, `combat-2-call-help-permit` 1.635, `combat-2-retreat` 1.64, `combat-2-kite` 1.65, `combat-3-hold-plan` 1.69 | colonist hurt + hostiles -> pause, mark `combat_paused` -> `fight_ratio >= FIGHT_RATIO_MIN`: fight (`combat_plan` 1) / else help coming (2) / else too many (`< CALL_HELP_RATIO`): call help by comms or permit (4), or retreat inside (5) / else kite (3) -> hold the plan. The reassess rungs are the float switch: the odds crossing `FIGHT_RATIO_MIN` either way pauses and re-plans. No hostiles: reset, undraft, run time. |
| 2. Medical | `med-1-bleeding-under-fire` 1.68, `med-2-field-tend` 2.06, `med-3-carry-to-hospital` 2.07 | bleeding + enemy: the combat plan stands, kill the threat first, never carry under fire -> no enemy: field tend in place (`field_tended`) -> carry to a Medical bed, tend again, clear the marks. |
| 3. Repairs | `repair-0-reset` 4.58, `repair-1-wait` 4.60, `repair-2-set` 4.61 | damaged + hostiles: wait (a notice; the combat rungs outrank it) -> safe: Home area + builders, `repairs_set` -> reset at 0 damaged. |
| 4. Defense | `defense-0-reset-embrasures` 19.40, `defense-0-reset-turrets` 19.41, `defense-0-reset-damage` 19.42, `defense-1-secure` 19.50, `defense-2-embrasures` 19.60, `defense-3-turrets` 19.70 | secure (embrasures >= `EMBRASURE_TARGET`, turrets >= `TURRET_TARGET`, nothing damaged): `defense_secure`, continue / not secure: the build list for what is short. Below `GRACE_FROM_PRIORITY`, so it runs from day 0 once something is built. Door/gate counts are not part of the check: the sweep cannot tell perimeter doors from interior ones. |
| 5. Supply | `supply-food-*` 22.60–22.61, `supply-steel-*` 22.62–22.64, `supply-podfuel-*` 22.65–22.66, `supply-shipfuel-*` 22.67–22.68, `supply-weapons-*` 22.69–22.71 | each level against its setpoint with a latched alarm and a reset: food under `FOOD_COMFORT_DAYS` (under `FOOD_MIN_DAYS` stays `food-low` 4.1), steel under `STEEL_RESERVE` (buy if comms + `TRADE_SILVER_MIN`, else mine), chemfuel under `POD_FUEL` with launchers, under `SHIP_FUEL_RESERVE` with a gravship, loose weapons over `WEAPON_KEEP` (sell if comms, else smelt). Held by the grace days like every rung from 20. |

New sensors (`gates.py`): `able_shooters` (crew not downed, dead or in a mental state), `fight_ratio` (`able_shooters / hostiles_on_map`, only while hostiles > 0), `colonist_hurt` (downed, `alert_needs_tend`, bleeding, or mark `colonist_hurt`), `pawn_bleeding` (`alert_bleeding`, `alert_life_threat`, or mark `pawn_bleeding`), `loose_weapons` / `junk_weapons` (sweep, `Gun_*` etc. lying in cells; awful/poor quality from the label), `buildings_damaged` (sweep, building cells below the best `hitPoints` of the same def and stuff). `ALERT_MATCH` gains `needs_tend`, `life_threat`, `bleeding`.

New variables: `FIGHT_RATIO_MIN` 1.0 (0.3–5), `CALL_HELP_RATIO` 0.5 (0.1–2), `WEAPON_KEEP` colonists + 2 (2–200), `SHIP_FUEL_RESERVE` 300 (50–10000). New numeric mark `combat_plan` (0 none, 1 fight, 2 hold for help, 3 kite, 4 help called, 5 retreat); new boolean marks `combat_paused`, `help_coming`, `colonist_hurt`, `pawn_bleeding`, `field_tended`, `repairs_set`, `defense_secure`, `food_short_set`, `steel_short_set`, `fuel_short_set`, `shipfuel_short_set`, `junk_weapons_set`.

UNVERIFIED in the chains:

- The bridge has no pawn health read: `list_colonists` has no health field and a pawn's cell `hitPoints` is -1 (captured). Hurt and bleeding come from alert labels never captured ("treatment", "life-threatening", "bleed") or from her marks after `pawn_check` Health.
- `able_shooters` cannot see incapable-of-violence or unarmed pawns.
- `buildings_damaged`: the cell reply has no `maxHitPoints`; no captured sweep shows a damaged building, and an evenly damaged group reads healthy.
- Weapon prefixes `MeleeWeapon_` and `Bow_` and the quality words awful/poor (only `Gun_ChargeRifle` "normal" is captured).
- Allied military aid through the comms console and the permit list; the gravship fuel type; the smelt-weapon recipe name.

Offline check (2026-10-12, a throwaway script, faked states, the AI's `ladder_set mark` steps applied between scans): combat with good odds ran pause -> fight -> hold -> (odds fell) reassess -> kite -> hold -> reset; outmatched without help -> kite; with help -> help-coming; too many with comms -> call-help-comms; with a title -> call-help-permit; with nothing -> retreat. Medical: pause -> fight -> bleeding-under-fire -> reset -> field-tend -> carry-to-hospital. Repairs: (hostile-on-map outranks the wait notice) -> set -> reset. Defense: embrasures -> turrets -> secure -> reset when embrasures fell. Supply: food low -> reset; steel buy -> reset -> mine; pod fuel low -> reset; ship fuel low -> reset; weapons sell -> reset -> smelt. No unknown keys, no unresolved bounds. `derive()` on 2,278 captured cells and the captured colonist list still runs: `able_shooters` 4, `buildings_damaged` 0, `loose_weapons` 0.

### 6.2 RimPLC P2 engine additions (2026-10-12)

Owner, verbatim: *"get to that PLC work to finish it"*. `gates.py` stays in step with RimPLC's C# engine (`RimPLC/Source/RimPLC/Engine.cs`); the full description is `docs/RIMPLC_DESIGN.md`, "Built status", P2.

1. **Nested instructions.** A `when` value that is an object is an instruction, and its key is only a label: `{"any": [when, ...]}` (OR), `{"not": when}`, `{"ton": when, "ticks": N | "hours": H}` (on-delay), `{"tof": when, ...}` (off-delay), `{"ctu": when, "preset": N, "reset": when}` (counter), `{"ons": when}` (one-shot). `not` of an unmeasured key stays unmeasured, so a missing key still never fires. Timer and counter memory moves once per `decide(write=True)` and is kept in `scratch/plc_memory.json`. `decide(write=False)` (training, offline checks) only reads it. No book rung uses them yet, so the book's answers and the brain's `ladder` text are unchanged.
2. **Fallback sensors.** The RimPLC preset rewrites `mark_research_microelectronics`, `mark_research_transport_pod`, `mark_research_xenogenetics` and `mark_caravan_out` to the sensors RimPLC measures (`research_microelectronicsbasics`, `research_transportpod`, `research_xenogenetics`, `caravan_out`). Each one names its old mark as `fallback` in the sensor table. `gates.py` cannot measure them, so it reads the mark, and the preset gives the same answers as the playbook. The playbook itself is unchanged.
3. **Thin client.** `ladder` / `ladder_set` keep their names, arguments and result text. When RimPLC is loaded they are answered by `rimplc/*` (or its command file). Otherwise this engine answers them.
