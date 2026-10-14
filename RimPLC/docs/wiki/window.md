---
title: The window
summary: "The Ladder, Tags, Marks, Sensors and Log tabs, and what every control on them does."
---

# The window

The main tab **RimPLC** sits on the bottom bar. Its header carries the scan rate and the
**Notices** switch; below it, five tabs.

## Header

| Control | What it does |
|---|---|
| **-** / **+** | Halve or double the scan interval (60 to 2500 ticks). A faster scan reads the colony more often and costs more time per tick. |
| **Notices** | When ticked, a rung's notice is posted as a game message on its rising edge. Untick to keep the ladder silent and read it yourself. |

## Ladder

Every rung, one row each, in priority order. Each contact in the row is drawn by its state:

| Colour | Meaning |
|---|---|
| green | the condition holds |
| dark | it does not |
| amber | the reading it needs is **unmeasured** -- the game cannot give it, or the mod or expansion it names is not loaded |
| red | unresolved: the condition names something nothing writes |

A rung is live when every contact is green. The first live rung is the colony's job now.

| Control | What it does |
|---|---|
| **Live rungs only** | Hide every rung that does not hold right now. |
| **All families** | Filter the list by family: setup, survival, war, economy, research, base-and-fortress, animals, growth, configuration, royalty, ideology-biotech-anomaly, space, endgame, meta, start, backrooms. |
| **Letters seen** | Mark every letter on the stack as read, so `letters` drops to zero and an unread threat letter stops vouching. |
| **New rung** | Open the editor on an empty rung of your own. |
| **Edit** | Open the editor on the selected rung. Editing a preset rung makes a player copy under the same id; the preset is not changed. |
| **Remove** / **Revert** | Remove your own rung, or drop your copy of a preset rung so the preset's version returns. |
| **Export** / **Import** | See [Presets and building](presets.md). |
| on / off | Switch a rung off and it is skipped. Switching a preset rung off is an owner action when the owner route is used ([Commands](commands.md)). |
| advise / auto | **advise** (default): the rung only shows and posts its notice. **auto**: its coils run -- a message, a mark or a tag. Nothing else is ever executed. |

Select a rung to read its `then` steps, its `never` list and its `why` -- the reason it exists,
usually in the words of whoever asked for it.

### The rung editor

Rows of **key / operator / value**. The key picker searches the sensors, the marks, the tags and
the game's own definitions -- items, buildings, research projects and alert classes -- so a rung
can read `count_Steel`, `research_Gunsmithing` or `alert_ColonistNeedsRescue` without those
being pre-registered. A definition from a DLC or another mod adds a `requires` entry so the rung
stays quiet when that content is absent.

Instructions (OR, NOT, timers, counters, one-shots) are edited as JSON from templates. Saving runs
the same rules the repository's checker runs: unique ids, a numeric priority, every key a sensor,
mark, tag or definition, every condition a value the key's type can satisfy.

## Tags

Two lists. **Variables** are setpoints you may override within their `min..max`: food comfort
days, the steel reserve, the colonist target. **Constants** are the owner's safety limits and
change only through the owner route. **Set** writes an override, **Clear** returns to the preset
value.

## Marks

Named booleans and numbers for judgements the game cannot measure -- a camp declared stable,
which kind of raid the last letter described, how many gate sections are done. **Set**, **Clear**
and **Add** for a new one. A boolean mark never set reads false; a numeric mark reads its
documented default.

## Sensors

Every reading by group -- Game, World, Colony, Threats, Crew, Health, Food, Stores, Rooms, Power,
Defence, Production, Research, Stream -- with its value and a tooltip saying what it means and
when it warns. A **warnings panel** at the top lists the readings that are a problem right now
(critical in red, warning in amber); **Warnings only** hides the rest. Critical warnings also
raise an alert in RimWorld's own alert column.

The tab also lists every input a rung asks for that nothing is writing, with host inputs
(readings pushed from outside the game) marked as such.

## Log

The notices posted and the outputs recorded, newest first.
