---
title: Sensors
summary: "The readings by group, their cadence, their warnings, and what an unmeasured reading means."
---

# Sensors

A sensor is one reading of the colony with a fixed name, a type (number, boolean or list) and a
catalogue entry that says where it comes from, what it means and when it warns. The Sensors tab
shows them all; `read_state` returns them.

## Cadence

| Cadence | Every | Readings |
|---|---|---|
| fast | scan | clock, pause state, the crew's positions and drafted state, hostiles, letters, alerts |
| normal | 4th scan | stores, zones, buildings, designations, rooms, power, animals, weapons, research, mood |
| slow | 16th scan | wealth, damaged buildings, the world map |

A reading is taken once per scan and cached, so a ladder of four hundred rungs costs the same as
one.

## Groups

| Group | Examples |
|---|---|
| Game | `colony_exists`, `paused`, `day`, `season`, `ticks_moving` |
| World | `letters`, `threat_letter`, `threat_letter_unread`, `quest_letter`, `quests_active`, `caravans_out`, `trade_ships_in_orbit`, `visitors`, `game_conditions` |
| Colony | `colonists`, `prisoners`, `colony_animals`, `wealth`, `silver`, `pawns_unconfigured` |
| Threats | `hostiles_on_map`, `hostile_threat`, `mental_break`, `downed_count`, `corpses` |
| Crew | `unarmed_colonists`, `able_shooters_armed`, `pawns_without_sidearm`, `colonists_without_armor`, `grid_matches_plan` |
| Health | `needs_tend_count`, `pawn_bleeding`, `alert_life_threat`, immunity against severity |
| Food | `days_of_food`, `meals`, `stoves`, `butcher_tables`, `kitchen_tables_no_bill`, `growing_cells`, `wild_game` |
| Stores | `food_store`, `main_store`, `stockpiles`, `loose_items_unstored`, `forbidden_items`, `unroofed_store_cells`, `wood`, `count_<thingdef>` |
| Rooms | `beds`, rooms out of 10-35 C, unfloored cells, roof holes |
| Power | `power_nets`, `power_nets_dead`, unpowered buildings, battery days stored |
| Defence | `turrets`, `embrasures`, perimeter gaps, `designations_hunt`, `loose_weapons`, `junk_weapons` |
| Production | benches, bills, `research_benches`, multi-analyzers |
| Research | `research_<def>` for every project, `ship_research_done` |
| Stream | host inputs pushed from outside the game ([Commands](commands.md)) |

## Readings on demand

Three families of key are measured only when a rung names them, so the catalogue never has to
list every definition in every mod:

| Key | Reads |
|---|---|
| `count_<ThingDef>` | items: the total stack count on the map; buildings: how many stand |
| `research_<ProjectDef>` | whether that research project is finished (measured for every loaded project) |
| `alert_<AlertClass>` | whether that alert is active (`alert_HunterLacksRangedWeapon`, `alert_ColonistNeedsRescue`) |

A definition the game has not loaded leaves the key unmeasured.

## Unmeasured

A reading the game cannot give is **absent**. It is never zero, never false. A rung whose
condition names it shows that contact amber and stays quiet. This is deliberate: a guessed zero
would make "no freezer" look like "freezer at 0 C" and fire the wrong rung.

A sensor can also be catalogued `not-measured`: the name is reserved and rungs may read it, but
no code writes it yet. The Sensors tab lists those under the inputs nothing is writing.

## Warnings

Every catalogue entry carries a label, a group, a tooltip and a severity, and most carry a
`warn` rule -- a boolean rule for a boolean reading, an operator rule for a number. When the rule
holds the reading is listed in the warnings panel at the top of the Sensors tab, amber for a
warning and red for a critical one. Critical warnings also raise an alert in RimWorld's own
alert column: an unarmed colonist, a colonist never set up, an unread threat letter.

## Letters

`letters` counts letters on the stack not yet marked seen. `threat_letter` is true while a raid
or threat letter (`ThreatBig` / `ThreatSmall`) is on the stack and recent, and **for as long as
one is unread, whatever its age** -- an unread threat never ages out of the ladder.
`threat_letter_unread` is that last part on its own, and it is critical. The window's **Letters
seen** button, or the `letters_seen` command, marks the stack read.
