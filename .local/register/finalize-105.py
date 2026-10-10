# -*- coding: utf-8 -*-
import io

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()

entry = u"""

### 0.10.5-dev - every surface the game speaks through

> *"read now.md to continue the work completing the mod, and also real quick did we finish up that doc regress work and the later stuff i said about cleaning up text walls for everything making them a pleasure to read, lets make sure the docs and informations displays in game are proper to backrrooms universe and rimworld gameplay style of all displayed informations of varying types to include all."*

Four items in one direction. Two were questions and were answered with measurements rather than with a claim; both answers are **partly**, and both are written into the queue with their numbers. The fourth item shipped here. The third, the document half, is queued behind it.

**The questions, answered.** The documentation regression work closed the drift `check-doc-conformance.py` covers - twenty-eight stale claims across ten living documents - and that checker passes. Its rule set is five rules wide and does **not** cover the gate vocabulary in documents or their readability, and a sweep found **309 occurrences of the retired word across 34 living documents**. The text-wall work closed every wall the **game** displays, enforced at 420 characters, and generated readable HTML for seven documents; it never touched the documents themselves, where **twenty living documents carry prose lines past 400 characters**.

**RimWorld does not have one voice for displayed text - it has one per surface.** Core's own keyed files are organised by surface where ours are organised by system, and the conventions were lost in the gap. A float menu row ends with a full stop **7%** of the time in Core; an explanatory tooltip does **93%** of the time. Six of our strings were written in the wrong register, including a right-click row carrying a two-sentence instruction; the row now states only the condition and the instruction moved to the tooltip that exists for instructions.

**The census found a surface the mod used none of.** *"to include all"* is only actionable if the report counts the zeroes, and the alerts readout came back empty - every warning this mod gave was either a letter a player can dismiss and lose, or an inspect line a player has to already be looking at. Three alerts now: **recovery overdue** (critical), **return window closing** (high, and the one still actionable), **no gate operator** (medium, colony-wide so that keeping a spare door designated does not nag). No def, no asset, no Harmony - Core's `AlertsReadout` walks `typeof(Alert).AllLeafSubclasses()`, verified by decompiling it.

**The register changed the design.** Row 146, *No Hemogen Farm Medical Alert*, was the only applicable row in 295, and its review carries the author's own note about *"a possible small alert-check cost with many prisoners"*. Core calls `GetReport` on a rotating one-in-twenty-four schedule, so three alerts meant three building sweeps forever. One cached sweep per game tick instead - keyed on the tick **and** the game object, because keying on the tick alone hands a second save loaded at the same tick the first save's despawned components.

**The seventh checker reported seven faults that were not faults, and the baselines were wrong, not the text.** Letter bodies had been measured from `Letters.xml` alone (max 385) when Core's incident letters reach **666**; tooltips from `GameplayCommands.xml` alone (max 204) when Core's explanatory strings reach **894**. One good tooltip was flagged for being four characters over a ceiling that never existed. Measure a surface, never a file. Sanity-tested in both directions afterwards by planting a fault on each rule and confirming it fired, then reverting.

**Checkers: seven.** 160 C# files, 80 package files, zero warnings. No def, no art, no audio, no Harmony, no game launched. Record: `implementation/DISPLAY_SURFACE_IMPLEMENTATION.md`.
"""

s = s.rstrip('\n') + entry
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED entry appended')
