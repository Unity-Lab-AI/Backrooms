# -*- coding: utf-8 -*-
"""Ledger for 0.12.19-dev: the yellow rooms were never carpeted."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def insert_before(rel, anchor, block):
    s = read(rel)
    assert anchor in s, '%s: anchor not found' % rel
    write(rel, s.replace(anchor, block + anchor, 1))


insert_before('CHANGELOG.md', u'## 0.12.18-dev', u"""## 0.12.19-dev - 2026-09-29 - the yellow rooms were never carpeted

- **A real, visible bug, fixed.** The first Backrooms level you ever walk into is supposed to be worn yellow carpet. It has been **wood plank flooring** since the look shipped, in every game, on every seed. Nothing ever reported it.
- **The cause:** RimWorld has no floor called "Carpet". It has a *template* that makes one carpet per colour, so asking for "Carpet" quietly returned nothing and the code fell back to wood. The fix uses the colour each level already names, so mustard carpet downstairs, faded green in the office levels, burnt umber where the place stops making sense.
- **Three things I had reported as missing are already in the game.** The rock between rooms is mineable in whatever stone that world tile actually has, and lifting a floor gives you back half of what it cost - carpet included. I was wrong about all three and the record says so.
- **All of that is now checked**, including the specific way it could silently break again: swapping in one of the floors RimWorld gives nothing back for.

Full record: [the yellow rooms were never carpeted](docs/implementation/INTERIOR_RESOURCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the yellow rooms were never carpeted (0.12.19-dev)

**Verbatim user quote:** *"continue"*, following *"make sure you are use the prep docs and mod register as a guide in all you build"*

**The owner directions this settles, verbatim:** *"and areas minable and of all types of materisals throughout"*, *"and capte ands tile can all be uninstalled , moved, resued , sold , studied"*, *"all of it"*

### What shipped

A **real, shipped, player-visible defect** fixed, and **three of my own audit verdicts corrected**. I set out to build "the interior as a resource" and found it was already built - then found a genuine bug while proving it.

### Files touched

`Generation/BackroomsPalette.cs`, `docs/implementation/INTERIOR_RESOURCE_IMPLEMENTATION.md`, `docs/TODO.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and `proof-interior-resource.py` (new, the twentieth).

### Closure notes

- **THE DEPTH-1 YELLOW ROOMS HAVE NEVER BEEN CARPETED.** `BackroomsPalette` asked for `Named<TerrainDef>("Carpet")`, and **there is no `TerrainDef` called `Carpet`**: Core ships a `TerrainTemplateDef` of that name and `TerrainDefGenerator_Carpet` produces one real terrain per structure colour, named `Carpet` + the colour def name minus `Structure_`. So the lookup returned null through `GetNamedSilentFail`, which is silent by design, and **every carpet band fell through to its `??` fallback** - wood plank flooring at depth 1. Worn yellow carpet is the defining surface of the Backrooms and invariant 25 calls depth 1 **sacred**. No build error, no checker, no log line, and the fallback made the wrong floor look deliberate.
- **The fix needed no new data.** Each band already names its own floor colour - `Structure_Mustard` at depth 1, `Structure_GreenFaded` for the office band, `Structure_UmberBurnt` for the wrong band - and all three generated defs exist. A carpet **cannot** be tinted at runtime the way a wall can, because the colour is baked into the generated def, so the colour the band already named is exactly what picks the def.
- **THREE OF MY OWN 0.12.14-dev AUDIT VERDICTS WERE WRONG**, and correcting them is most of this checkpoint:
  - *"areas minable and of all types of materisals"* was marked **STILL OPEN, confirmed unbuilt by grep**. It is **fully built**: `FillWithRock` plus `NaturalRockTypesFor`, which asks `Find.World.NaturalRockTypesIn(map.Tile)` for whatever that tile actually has. My grep searched `Generation/` for *"Mineable"*, *"Granite"*, *"RockRubble"* - **none of which the code contains**. A grep for the words I expected is not a search.
  - I accused `BackroomsContainment.cs` of **claiming mineability its code does not implement**. **The comment was telling the truth.** The implementation is in a different file. I invoked invariant 130 while committing its inverse: condemning correct code on a failed search is worse than trusting a wrong comment, because it marks working behaviour as broken.
  - I asserted **vanilla returns no materials for a lifted floor**. `TerrainGrid.RemoveTopLayer` defaults `doLeavings: true` and calls `GenLeaving.DoLeavingsFor(TerrainDef, cell, map)`, which returns `CostListAdjusted()` times `resourcesFractionWhenDeconstructed` - **0.5 by default on `BuildableDef`**. Every floor the palette lays returns half its cost. The premise of the row was wrong.
- **So nothing needed building, and the proof is the deliverable.** What was genuinely missing was anything watching: **the behaviour depends entirely on which terrains the palette picks**, and Core ships `PackedDirt`, `BrokenAsphalt` and stone tiles that return **nothing**. A future palette change would have silently ended the owner direction.
- **MY FIRST VERSION OF THAT EXACT CLAIM WAS BLIND, AND ONLY A PLANTED FAULT FOUND IT.** It skipped any terrain with no cost list, reasoning that natural terrain was never built - which excused **precisely** the case it existed to catch: swapping a floor for `PackedDirt` **passed**. A filter that skips the case it guards against is worse than no check. Rewritten to require both halves: it cost something, and it returns some of that.
- **Two more of my claims were wrong on the first run.** One searched for `RoofConstructed` and was broken by the two doc comments saying the roof is deliberately **not** `RoofConstructed` - a claim defeated by the code explaining itself, **sixth time** in this project. The other asserted `SetFaction` never appears in generation; it appears **six times**, deliberately, on the player's own equipment and doors, which is what makes them the player's to use. Both rekeyed off the spawn.
- **Register checked first this time, and it shaped the work.** Row **101 Gold & Silver Ingots is *Required*** but is smelting recipes only, with no ore veins, and its review says not to require it for core progression - so mineable rock uses **Core** ore. Row **152 Non uno Pinata** changes corpse inventory and auto-strip behaviour, **not terrain drops**, so floor recovery is clear of it. Row **127 Mine Sight** is a designation UI, so real mineable rock simply appears in it. Rows 144, 221 and 52 alter material properties, not placement.
- **Five planted faults, five catches, clean on restore**, including the formerly-blind one and the original defect restaged.
- Build 0.12.19-dev, 173 C# files, 91 package files, **0 warnings, 0 errors**. Eight checkers pass, **twenty** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched - so the carpet is correct by def name and cost, and nobody has seen it.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.18-dev**.', u'| Published | **0.12.19-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.18',
     u'## What shipped this session, 0.7.1 → 0.12.19'),
    (u'| 0.12.18 | **The third rung of every branch** — research tier 3, **all seven**, every one moving an observable knob. Two design restraints asserted |',
     u'| 0.12.18 | **The third rung of every branch** — research tier 3, **all seven**, every one moving an observable knob. Two design restraints asserted |\n'
     u'| 0.12.19 | **The yellow rooms were never carpeted** — a real shipped defect; three of my own audit verdicts corrected. **Twentieth proof** |'),
    (u'| Proofs | **NINETEEN** in `.local/register/proof-*.py`.',
     u'| Proofs | **TWENTY** in `.local/register/proof-*.py`.'),
    (u'7b. **Every proof (NINETEEN), by exit status:**', u'7b. **Every proof (TWENTY), by exit status:**'),
    (u'   `live-effects`, `menu-slides`, `offer-routes`,',
     u'   `interior-resource`, `live-effects`, `menu-slides`, `offer-routes`,'),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:60]
    s = s.replace(old, new, 1)

marker = u'202. **Proximity is not the thing that happens.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'203. **A grep for the words you expected, in the file you expected, is not a search.** The '
     u'mineable-rock fill was marked *"confirmed unbuilt by grep"* while fully shipping, because the '
     u'code says `Find.World.NaturalRockTypesIn` and contains none of the words searched for. '
     u'**Condemning correct code on a failed search is worse than trusting a wrong comment.**\n'
     u'204. **`Named<X>("Foo")` on a TEMPLATE def returns null, silently, and a `??` fallback makes '
     u'the wrong result look deliberate.** Core ships `Carpet` as a `TerrainTemplateDef` and '
     u'generates `Carpet<Colour>`. The yellow rooms were wood plank flooring from the day they '
     u'shipped. **Assert that every def a generator names actually resolves.**\n'
     u'205. **A filter that skips the case it guards against is worse than no check.** The floor '
     u'claim excused terrains with no cost list as *"never built"*, which excused `PackedDirt` — the '
     u'exact plant it existed to catch. **Only the planted fault found it; reading it would not '
     u'have.**\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# ------------------------------------------------------------------ correct the three audit rows
t = read('docs/TODO.md')
CORR = u' — **CORRECTED 0.12.19-dev: my 0.12.14-dev verdict was WRONG.** '
rows = [
    (u'**"and areas minable and of all types of materisals throughout"**',
     u'**BUILT, and it was built all along.** `FillWithRock` plus `NaturalRockTypesFor` in '
     u'`GenStep_BackroomsDestination.cs`, asking `Find.World.NaturalRockTypesIn(map.Tile)` so the '
     u'materials are whatever that tile actually has, seeded deterministically per cell. The audit '
     u'grepped for *"Mineable"*, *"Granite"* and *"RockRubble"*, **none of which the code contains**. '
     u'A grep for the words I expected is not a search.'),
    (u'**"and capte ands tile can all be uninstalled , moved, resued , sold , studied"**',
     u'**SATISFIED by Core, and now asserted.** Every floor the palette lays is a real `TerrainDef` '
     u'with a cost list, and `TerrainGrid.RemoveTopLayer` defaults `doLeavings: true`, returning '
     u'`CostListAdjusted()` times `resourcesFractionWhenDeconstructed` — **0.5** by default. Carpet '
     u'returns Cloth, wood returns WoodLog, tile returns Steel or Silver, all at half. '
     u'`proof-interior-resource.py` guards the one way this breaks: a palette swap to `PackedDirt`, '
     u'`BrokenAsphalt` or a stone tile, which return nothing.'),
    (u'**Floors recovered when lifted.**',
     u'**THE PREMISE WAS WRONG.** This row said vanilla returns no materials when a floor is '
     u'removed. It does: `RemoveTopLayer(c, doLeavings = true)` calls '
     u'`GenLeaving.DoLeavingsFor(TerrainDef, cell, map)`. Nothing needed building. What was missing '
     u'was anything **watching** which terrains the palette picks, and that is what shipped.'),
]
closed = 0
for anchor, note in rows:
    for prefix in (u'- [ ] ', u'- [~] ', u'  - [ ] '):
        target = prefix + anchor
        if target in t and t.count(target) == 1:
            start = t.index(target)
            end = t.index(u'\n', start)
            body = t[start:end].split(u'] ', 1)[1].split(u' — **STILL OPEN')[0].split(u' — **PARTLY')[0]
            t = t[:start] + prefix.replace(u'[ ]', u'[x]').replace(u'[~]', u'[x]') + body + CORR + note + t[end:]
            closed += 1
            break
write('docs/TODO.md', t)
print('corrected %d audit rows' % closed)
