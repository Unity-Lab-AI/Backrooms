---
title: RimPLC
summary: "A separate colony logic mod: live sensors, editable rules and a ladder window."
---

# RimPLC

![RimPLC — colony logic and control](https://raw.githubusercontent.com/G-Fourteen/RimPLC/main/About/Preview.png)

**RimPLC is a separate mod for colony rules.** It reads the colony, evaluates your conditions and
shows the matching advice in an in-game ladder window. Rimrooms does not require it, and RimPLC
does not require Rimrooms, another mod or an expansion. It uses no Harmony.

## Game versions

RimPLC is being prepared for **RimWorld 1.7 unstable / Waylith**, with **1.6 retained**. Both game
versions load the same `1.7/` content folder. The inspected compiler and API baseline is 1.6;
**1.7 runtime compatibility has not been verified**.

The [official announcement](https://store.steampowered.com/news/app/294100/view/672882362547178633)
explains the engine update and unstable branch. A version declaration does not replace an actual
result on that version.

## What you can do

| View | Purpose |
|---|---|
| **Ladder** | See which rules are true, false, unmeasured or unresolved; enable, edit or add a rule |
| **Tags** | Set bounded thresholds used by rules |
| **Marks** | Keep a named boolean or number for a judgement the game cannot measure |
| **Sensors** | Inspect the values read from the colony |
| **Log** | Review notices and recorded outputs |

Sensors include health, mood, food, materials, threats, research, temperature, alerts and buildings.
A missing value stays unmeasured; it does not become a guessed zero. Definitions are looked up by
name, so a rule whose required mod or expansion is absent stays unavailable.

Rules support comparisons, OR, NOT, timers, counters and one-shot conditions. Their memory is
saved with the colony, and timers advance in game ticks.

## Advice and automatic outputs

**Advice is the default.** A matching rule can tell you what to do next. In the current
implementation, automatic outputs are limited to **messages, marks and tags**.

RimPLC does not currently carry out world-changing actions such as drafting pawns, placing
blueprints, building a gate or changing work priorities. A plan describing those actions is not
an implemented output. Keep the game's normal controls available.

Many of the supplied preset's rules name a concrete next step -- arm the colony, put a cooler in
the freezer wall, add a meal bill, pick the next research project, ask a faction for a trader.
Those steps are written for an external assistant that can act through the Rimrooms mod's
[automation file](interface.md#automation-file-optional); without one, read them as advice. The
Ladder view shows, for each rule, which steps a present client could carry out and which have no
answer in the loaded mods.

## Presets and saved rules

The supplied ladder is a preset. Editing one of its rules creates a player override; reverting
returns to the preset. Player rules, switches, marks, tag overrides and instruction memory are
stored in the save.

Export and import use the game's configuration folder under `RimPLC/exports/`. An import shows
its changes before you apply it. Back up a colony before changing its rules or switching game
versions; save and load behavior on 1.7 remains unverified.

## Optional bridge access

The core mod needs no bridge. Its optional companion exposes rule reads and edits through
RimBridgeServer. The companion DLL belongs in the game's `BridgeTools/RimPLC/` folder, separate
from the mod package, and requires a matching installed bridge SDK.

Without that bridge, supported commands use `RimPLC/inbox.jsonl` and `outbox.jsonl` in the game's
configuration folder. The in-game window remains available either way. Owner-only changes stay
restricted to the owner route.

## Getting it

[RimPLC on Forgejo](https://git.unityailab.com/GFourteen/RimPLC) and
[RimPLC on GitHub](https://github.com/G-Fourteen/RimPLC) are the project repositories.
Use its documented package or build instructions; the source checkout is not a finished Workshop
installation. Place the loadable package in RimWorld's Local Mods folder with `About/` directly
inside it. Leave the shared `1.7/` folder name unchanged.

RimPLC and Rimrooms are independently enabled mods. A Rimrooms sensor link is separate
integration work; installing both does not prove that link exists or that 1.7 compatibility has
passed.

For Rimrooms installation, see [Install](install.md). For the project addresses, see [Links](links.md).
