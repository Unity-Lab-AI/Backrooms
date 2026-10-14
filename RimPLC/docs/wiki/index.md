---
title: RimPLC
summary: "Colony logic as a PLC ladder: live sensors, editable rules and an in-game ladder window."
---

# RimPLC

**RimPLC is a standalone RimWorld mod that lays the colony's whole "if this, then this" logic
out as a PLC ladder and scans it in game.** Sensors read the colony. Tags set thresholds. Marks
hold what the game cannot measure. Rungs say what to do when their conditions hold, and the
ladder window shows every one of them live: green when true, dark when false, amber when a
reading is missing.

It needs no other mod, no expansion and no Harmony. Package id `Operator.RimPLC`.

## Reading order

| Page | What it answers |
|---|---|
| [Install](install.md) | Where the files go, game versions, the optional bridge companion |
| [The window](window.md) | The Ladder, Tags, Marks, Sensors and Log tabs, and every button on them |
| [The ladder](ladder.md) | What a rung is, how conditions, timers, counters, latches and priority work |
| [Sensors](sensors.md) | The readings by group, warnings, and what "unmeasured" means |
| [Commands and the AI API](commands.md) | The command file and the RimBridgeServer tools |
| [Presets and building](presets.md) | The shipped ladder, export and import, building from source |
| [Links](links.md) | Repositories, the Rimrooms wiki, licence |

## What it does, in one scan

1. Every scan (fast), every fourth (normal) or every sixteenth (slow) the sensors read the game:
   clock, crew, health, hostiles, letters, stores, zones, buildings, designations, animals,
   weapons, alerts, temperature, research, mood, wealth, damaged buildings. A reading the game
   cannot give is **absent**, never a made-up zero.
2. Every rung's `when` is evaluated against those readings, the tags and the marks. Comparisons,
   OR, NOT, on/off delays, counters and one-shots are all instructions a rung can carry; their
   memory moves on tick scans only and is saved with the colony.
3. The live rungs are listed by priority. The first one is the colony's job right now; the
   ladder window shows it and every other rung's state.
4. On a rung's rising edge RimPLC posts its notice as a game message. Rungs switched to **auto**
   may also set a mark, set a tag or post a message. **Nothing that changes the game world is
   executed by RimPLC** -- it never drafts, builds, forbids or trades. Those steps are written
   for an external assistant acting through another mod's automation file; without one, read
   them as advice.

## Game versions

RimPLC declares RimWorld **1.6** and **1.7**, both loading the same `1.7/` content folder. The
compiler and API baseline is 1.6 and the recorded play observations are from 1.6; a 1.7
running-session result is still pending. A version declaration is not a compatibility result.

## Where to start

Install it ([Install](install.md)), open the **RimPLC** tab on the bottom bar, and read the
Ladder with **Live rungs only** ticked. The top rung is what the colony needs next. Switch a
rung off if you disagree with it, edit it if you half agree, or write your own with **New rung**.
