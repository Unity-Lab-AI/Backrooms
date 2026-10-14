---
title: The ladder
summary: "What a rung is, and how conditions, timers, counters, latches and priority decide which one is live."
---

# The ladder

A ladder is a list of **rungs**. A rung is one rule:

```json
{
  "id": "cold-hold",
  "priority": 12,
  "family": "survival",
  "when": {"cold": {"ton": {"outdoor_temp": "<-10"}, "hours": 2}},
  "then": ["build a heater in the barracks"],
  "never": ["leave the door open"],
  "latch": false,
  "why": "owner: the barracks froze twice"
}
```

| Field | Meaning |
|---|---|
| `id` | Unique. A player copy of a preset rung keeps the preset's id. |
| `priority` | A number; **lower fires first**. Live rungs are listed in this order and the first is the colony's job. Ties are a checker error. |
| `family` | A grouping for the window's filter. |
| `when` | The conditions. Every key must hold for the rung to be live. |
| `then` | The steps, in order, in plain words. Each names the tool or command that does it. |
| `never` | What this rung must not do, however the steps are read. |
| `latch` | When true, the rung stays satisfied once it has fired, until its own reset. |
| `why` | Why the rung exists -- usually the words of whoever asked for it. |

## Conditions

A key is a sensor (`colonists`), a mark (`mark_camp_stable`), a tag inside braces
(`"<{STEEL_RESERVE}"`) or a definition read on demand (`count_Steel`, `research_Gunsmithing`,
`alert_HunterLacksRangedWeapon`). A value is:

| Value | Holds when |
|---|---|
| `true` / `false` / a number | the reading equals it |
| `">0"`, `"<3"`, `">=1"`, `"<=2"`, `"!=0"` | the comparison holds |
| `"<{FOOD_MIN_DAYS}"` | the comparison holds against that tag's current value |

**A missing reading never fires.** If the game cannot give `freezer_temp` (no freezer, or the
mod that measures it is absent) the contact shows amber and the rung stays quiet. It does not
become zero and it does not become true.

## Instructions

An object as a condition value is an instruction, named for the PLC instruction it copies:

| Instruction | Form | Holds when |
|---|---|---|
| `any` | `{"any": [{"corpses": ">0"}, {"designations_hunt": ">0"}]}` | at least one listed condition holds (OR) |
| `not` | `{"not": {"held": {...}}}` | the inner condition does not hold |
| `ton` | `{"ton": {"outdoor_temp": "<-10"}, "hours": 2}` | the inner condition has held continuously for that long (on-delay; `ticks` or `hours`) |
| `tof` | `{"tof": {...}, "hours": 1}` | the inner condition held within the last that-long (off-delay) |
| `ctu` | `{"ctu": {"mark_store_tried": true}, "preset": 2, "reset": {"food_store": true}}` | the inner condition has gone true that many times since the reset condition last held (count-up) |
| `ons` | `{"ons": {"threat_letter": true}}` | the inner condition went true on this scan (one-shot, rising edge) |

Instruction memory -- how long a `ton` has held, how many times a `ctu` has counted, whether an
`ons` has fired -- moves on tick scans only and is saved with the colony.

A common pattern: a rung tries a step, and a fallback rung with a `ctu` on a "tried" mark takes
over after two or three refusals:

```json
{"colony_exists": true, "mark_shelter_set": false,
 "shelter_tries": {"ctu": {"mark_shelter_tried": true}, "preset": 2, "reset": {"mark_shelter_set": true}}}
```

## Marks and tags

**Marks** are what the game cannot measure and someone records on purpose: `mark_camp_stable`,
`mark_raid_kind` (1 walk-in, 2 drop pods at the edge, 3 drop pods in the centre, 4 siege, 5
sappers, 6 manhunter pack, 7 mechanoids, 8 infestation, 9 tribal swarm, 10 pirate gunline),
`mark_gate_sections_done`. A boolean never set reads false. Where a sensor later replaced a mark,
the sensor's catalogue entry names the mark as its `fallback` and the mark is read only while
the sensor is unmeasured.

**Tags** are numbers with bounds. Variables (`FOOD_COMFORT_DAYS`, `STEEL_RESERVE`,
`COLONIST_TARGET`) can be overridden within `min..max`; constants are the owner's safety limits.
A rung reads one as `{NAME}` inside a comparison.

## What a live rung does

- It is listed, first one first, in the Ladder tab and in `read_ladder`.
- On its rising edge, with **Notices** on, its notice is posted as a game message.
- If it is switched to **auto**, its coils run: `message`, `set_mark` or `set_tag`. That is the
  whole list. RimPLC never drafts a pawn, places a blueprint, forbids an item or calls a trader.

The `then` steps of the shipped preset name concrete actions -- arm the colony, put a cooler in
the freezer wall, add a meal bill, pick the next research project. They are written for an
external assistant acting through another mod's automation file; without one, they are advice,
and the Ladder tab shows which steps a present client could carry out and which have no answer
in the loaded mods.

## The shipped ladder

`Presets/LadderV2.json` carries the whole book: a camp on landing (store over the supplies,
walls and a roof around them, a shelter, a stove and a meal bill, then exploring), weapons and
self-tend checked every scan, threat letters read the turn they land, hunting and butchering,
the freezer, research order, defence, trade, animals, the mountain base, Royalty, Ideology,
Biotech and Anomaly, the ship. Families and counts are in the window's filter; the
`why` on each rung says where it came from.
