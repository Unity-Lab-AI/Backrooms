# -*- coding: utf-8 -*-
"""Append the 0.12.82-dev publication record to docs/FINALIZED.md.

Written BEFORE the commit, per `PUBLISHING.md` section 6.
"""
import io

NL = chr(10)
ENTRY = '''
## The corridors bend, a room has five ways out, and the rock is worth digging - 0.12.82-dev, 2026-10-04

**Staged and read back from the game folder**, not from the build output: `0.12.82-dev`,
SHA-256 `E2F34B711D0F93487FD0FF707866A8A56E6AEBFA770699CFC5E47B30693FA376`, 92 package files.

**Verified before publication:** build 0 warnings / 0 errors, 213 C# files; **16 of 16 checkers**
exit 0; **49 of 49 proofs** hold; `plant-coordinate-layout` **148 of 148**, `plant-generation`
**103 of 103**, `plant-menu-slides` **9 of 9** (new suite), `plant-dependencies` **7 of 7**,
`plant-world-return` **8 of 8**; **820 plant anchors** findable. Queue after the archive:
**83 open / 38 partial / 38 `[T]` / 0 `[x]`**.

### What the probe measured, before and after

Same instrument, same 200 seeds per depth, `python tools/check-planner-layouts.py`.

| | before | after |
|---|---|---|
| average links per room | 2.2 – 2.4 | **4.98 – 5.31** |
| most links on one room | 4 | **13 – 16** |
| rooms with one link | 6.5% | **0.2 – 0.7%** |
| rooms with none (sealed vaults) | 0.0% | **2.1 – 3.3%** |
| room fill, depth 1 | 46.0% | **57.2%** |
| room fill, depth 5+ | 17.1% | **44.9%** |
| back-to-back pairs | 131 | **190 – 310 per depth** |
| candidate refusals / fallbacks | 0 / 0 | **0 / 0** |

### The finding that shaped all of it

**Every one of those ceilings was geometric rather than a tuning, and the degree ceiling was the
corridor carver wearing a disguise.** A corridor ran along one axis, so `AreNeighbourRooms` had to
demand that two linked centres share a row or a column, so a slot had four neighbours, so max
degree was 4 — at every depth, for every seed, forever. Nothing about `BraidRarity` could have
changed it. The same shape appeared three more times in one session:

- **`MaximumUndirectedEdgesPerRoom` was 2** *because a slot has four neighbours*, and when bends
  made sixteen reachable the constant was the thing refusing them.
- **Room fill fell with depth** because the fraction of a slot a room occupies is
  `(1 - SlotGap / spacing)²` — so a **finer** grid fills **less** space, and ten slots per axis
  was the cause of 83% bare rock rather than a victim of it.
- **Every door sat at the exact middle of its wall** because a corridor could only run along a
  shared centre line, so the midpoint was the only cell it could ever arrive at. *"non default
  fdoor possitions"* was never a door rule.

### Two owner-asked features were regressing as a side effect, and only the probe saw it

**Back-to-back pairs fell 131 → 23** because `PushAgainst` only moved rooms with exactly one
link and the better-connected maze left few dead ends. **Room shaping fell 83.5% → 42.2%** at
depth 1 because `ShapeDepthOf` divides distance-from-the-hall by `LinksPerShapeBand`, and a
five-connected maze has a short diameter. Neither was in the change anybody was making; both are
fixed. **A feature can switch itself off while every claim about it still passes.**

### Three plants that caught nothing, and one that caught a non-fault

`plant-coordinate-layout` reported **MISSED** three times after the new claims landed: the guard
was still defined, the condition still named it, and the **call** had been replaced by a constant.
A fourth plant reported MISSED because its fault had *stopped being a fault* — the braid's
`AreNeighbourRooms` guard became redundant once the route check sat on the next line, so the plant
had been reporting CAUGHT for nothing. It was re-aimed at a fault that is still real rather than
deleted. **The MISSED is the instrument working.**

And `proof-menu-slides.py` broke the moment the slide list moved out of `RimroomsMenuBackground`,
which is exactly what it was built to do: it reads the folder and prefix out of the source rather
than restating them. A second AI reading the diff independently flagged the same thing.

### The defect behind the menu report

Owner: *"i dont think we properly did the same for loading screens and the like"*, then *"use them
randomly"*. `currentIndex` was pinned to `0` in the constructor **and reset to `0` again** in the
settings handler, so the menu — and the backdrop behind every load started from it — opened on
slide one of six, every single time, forever. The slideshow cycled perfectly and nothing in the
battery could see it, because every claim was about the folder scan and the crossfade. There was
**no plant suite covering the menu art at all**; there is now, and the first plant in it is this
defect.

### Two findings recorded rather than half-built

- **The pre-generation freeze notice needs the generation deferred.** `EnsureSite` calls
  `GetOrGenerateMap` synchronously and returns the map through an `out` parameter, so a window
  added immediately before it renders on the *next* frame — after the freeze. It needs
  `LongEventHandler.QueueLongEvent`, which changes a contract every caller relies on. Its own
  checkpoint. A notice that appears after the thing it warns about is worse than none.
- **Our art cannot be drawn behind an in-play long event without Harmony**, and this mod ships
  none by decision. `Root.OnGUI` skips the UI root entirely while `ShouldWaitForEvent`. Entry-state
  waits do draw the background, so those now show our art and show it randomly.

### Mod register

`python tools/register-query.py trace RR-SPACE` — the generator family. Nothing applied: this
change adds no integration surface and touches no other mod's defs. The ore work deliberately
reads `isResourceRock` and `deepCommonality` out of the loaded game rather than naming any def, so
a profile mod's ores and deep resources are included **without** an adapter — which is the
`modDependencies` removal direction being served by construction rather than by a later pass.

'''

f = "docs/FINALIZED.md"
t = io.open(f, encoding="utf-8").read()
if not t.endswith(NL):
    t += NL
io.open(f, "w", encoding="utf-8", newline=NL).write(t + ENTRY)
print("publication record appended")
