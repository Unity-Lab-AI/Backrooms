# -*- coding: utf-8 -*-
"""Mark this batch's closed rows and record the two findings that keep rows open.

LAW: the status marker is the ONLY thing that changes. Evidence is appended; not
one word of any description is removed or reworded.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

# (unique anchor inside the row, evidence appended after the row's own text)
CLOSED = [
 ('**"make sure hallways and corradors and shit arent all straight"** — bent corridors.',
  'CLOSED 0.12.82-dev. `RoomLayoutPlanner.BentLegs` routes a corridor through the rock lanes '
  'between rooms, and `RouteForms` is **seven** shapes rather than one: two elbows through a lane '
  'beside the first room, two beside the second, two five-leg routes that reach a slot two away, '
  'and a u-turn. Measured by `check-planner-layouts.py`: zero refusals and zero fallbacks at every '
  'depth. The lane is defined by a room’s own wall rather than by the slot grid, so a route '
  'needs nothing but the two rooms’ rects and no reader can be told a different spacing.'),

 ('- [ ] **"u -turns"**',
  'CLOSED 0.12.82-dev. Route form 6 leaves the room through the wall facing **away** from the '
  'destination, runs out to the lane on the wrong side, along a cross-lane, and doubles back — '
  'the literal article rather than a loop a player might happen to walk backwards. '
  '`BuildRouteWaypoints` case `default`.'),

 ('- [ ] **"multiple coices on directions to take in every rooms"** — **measured: avg degree 2.2–2.4, max 4.**',
  'CLOSED 0.12.82-dev. Re-measured: **avg degree 4.98 to 5.31, max 13 to 16**, and rooms with only '
  'one link fell from 6.5% to **0.2–0.7%**. Three mechanisms: the diagonal braid, the reach '
  'braid to slots two away, and one slot in eight being a **junction** that takes every link it '
  'can, which is what gives a spread rather than moving every room to the same new number.'),

 ('- [ ] **"non default fdoor possitions in rooms so doors are not just on each side"**',
  'CLOSED 0.12.82-dev, and it was never a door rule. `RoomLayoutPlanner.TryStraightCorridor` is '
  'now the single authority on where a straight corridor meets two rooms, and `DoorOpening` asks '
  'it for the line instead of assuming `CenterCell`. The midpoint was not a choice — a '
  'corridor could only run along a line both centres shared, so the wall midpoint was the only '
  'cell one could ever arrive at. **It also unsealed the grand hall**, whose centre sits between '
  'its two slots and which could therefore only lead out along its own row.'),

 ('- [ ] **"can have doors al over"**',
  'CLOSED 0.12.82-dev. A diagonal link opens the wall facing the other room on **both** axes, '
  'because which one the elbow uses is settled while the route is built after trying both; '
  're-deriving that choice in `DoorOpening` would be a second derivation of `BentLegs`. The unused '
  'opening is a door with rock behind it — and since the same version, that rock is an **ore '
  'vein**, so the owner’s *"doors that lead no where but to an ore or gem vein"* is the same '
  'door.'),

 ('- [ ] **"the backrooms is still incorrectly too much having the rooms like a string of pearls where the rooms are just one exit one entrance"**',
  'CLOSED 0.12.82-dev. The measurement that confirmed the complaint is the measurement that closes '
  'it: average degree **2.2–2.4 → 4.98–5.31**, and one-link rooms **6.5% → '
  '0.2–0.7%**. One in, one out is gone by measurement rather than by intent.'),

 ('- [ ] **"room connected to like 0 - 10 other rooms"** — a **degree range**',
  'CLOSED 0.12.82-dev, and the range is **0 to 16** measured, which brackets the owner’s '
  'number from both ends. The **0** is real and was the hard half: a zero-link room was refused '
  'outright by `CandidateIsSafe`, which proved every room reachable across carved floor. '
  '`SealedFamily` vaults have no links by design, their slots are reserved before the walk so '
  'nothing can link to them, and the reachability proof now asks its question of rooms that '
  '**claim** a route. `deg0` measures 2.1–3.3% at every depth.'),

 ('- [ ] **"not have so much empty rock space where nothing exists"** — at depth 1 the grid',
  'CLOSED 0.12.82-dev. roomfill **46.0% → 57.2%** at depth 1 and **17.1% → 44.9%** at '
  'depth 5 and deeper. The cause was arithmetic and the fix is arithmetic: the fraction of a slot a '
  'room occupies is `(1 - SlotGap / spacing)²`, so a **finer** grid fills **less** space — '
  'the rock between rooms is a fixed ten cells per boundary and more slots means more boundaries. '
  '`MaxSlotsPerAxis` 10 → 8 and `Margin` 14 → 6, which was throwing away a fifth of every '
  'map. `MaxRooms` is untouched at 60.'),

 ('- [ ] **"it looks too much like are long series connection of drooms"**',
  'CLOSED 0.12.82-dev with the row above, and recorded separately because the owner said it twice. '
  'The appearance follows the topology: a room with five ways out does not read as a bead on a '
  'string.'),

 ('- [ ] **"DO YOU UNDERSTAND WHAT A MAZE MEANS AND TO FILL THE SPACE WITH ROOMS"**',
  'CLOSED 0.12.82-dev. **And the two halves were never in conflict.** *"leas than 60-100 romms"* '
  'asks for fewer, larger rooms and this asks for less bare rock — which is the same '
  'instruction, because fewer larger rooms is what fills a fixed map. The room cap stayed at 60 and '
  'the fill rose by a factor of 2.6 at depth.'),

 ('- [ ] **"where there is mountain walls and no rooms areas minable need to have resources that you can mine like steel gold plasteel, gems, all of them"**',
  'CLOSED 0.12.82-dev. `Generation/OreVeinBuilder.cs`. **Nothing is named**: the ore list is read '
  'out of the loaded game — every def that is a natural resource rock — so *"all of '
  'them"* includes whatever the other 294 mods add, and the spread follows Core’s own '
  '`mineableScatterCommonality` so steel is ordinary and plasteel is not without this mod holding '
  'an opinion. It runs **after** the carve, so every cell it can see is rock a player can dig.'),

 ('- [ ] **"even underground resources that u can use deep drill with and chemfuel"**',
  'CLOSED 0.12.82-dev. `OreVeinBuilder.PlaceDeepResources` writes `Map.deepResourceGrid`, which is '
  'a different system from surface ore and is why no amount of rock would ever have produced one: a '
  'deep deposit is not a rock at all, it is a count the deep drill reads. Candidates are every def '
  'with `deepCommonality > 0`, **which is where chemfuel comes from without naming it** — that '
  'field is the game’s own statement about what can be drilled.'),

 ('- [ ] **"we should have doors that lead no where but to an ore or gem vein"**',
  'CLOSED 0.12.82-dev. `OreVeinBuilder.PlaceFalseDoorVeins` asks `RoomLayoutPlanner.FalseOpening` '
  'directly — rather than guessing which openings are real — and runs a vein outward from '
  'each one. The doorway already existed; what was behind it was plain rock, so it read as a '
  'mistake. Now it reads as a find.'),

 ('- [ ] **"and veins leading to other rooms"**',
  'CLOSED 0.12.82-dev. `PlaceBetweenRoomVeins` seams **unlinked** near pairs only, one pair in '
  'four: a vein between two rooms a corridor already joins teaches nothing. **Veins cannot break a '
  'level** — every cell is rock before and rock after, so no route, wall or doorway is '
  'touched, which is exactly why they are allowed to route freely across the whole map.'),

 ('- [ ] **"so insentive to mine things out to find isolated undiscorvered rooms when mining and deconsturcting wals and sucvh"**',
  'CLOSED 0.12.82-dev. `SealedFamily` vaults exist (`deg0` 2.1–3.3%), their slots are reserved '
  'out of the room budget rather than left to compete for it — **the probe caught that: '
  '`deg0` read 0.0% at depth 3 and deeper because the walk reached `MaxRooms` first and the vault '
  'was silently dropped** — and `PlaceVaultVeins` runs a seam from every vault to the nearest '
  'room with a way in, so the thing is findable rather than merely present.'),

 ('- [ ] **"so u can find back to back rooms"**',
  'CLOSED 0.12.82-dev, and this one was **regressing while nobody watched**. `PushAgainst` only '
  'ever moved rooms with exactly one link, and the degree work left a level with few dead ends: '
  'measured back-to-back pairs fell **131 → 23** as a side effect of a different feature. The '
  'push now proves the move itself — on the map, no collision, no existing link broken, and '
  '`SharesWall` agrees — so the link count stopped being the condition. **190 to 310 pairs per '
  'depth.** Plus `PlaceBetweenRoomVeins`, which is how you *find* one by digging.'),

 ('- [ ] **"it shouldnt just be one option"**',
  'CLOSED 0.12.82-dev. `RouteForms = 7`, tried in an order rotated by the pair’s own hash, '
  'each at two widths, first clear route wins.'),

 ('- [ ] **"option 2"** — **veins as routes AND scattered background deposits.**',
  'CLOSED 0.12.82-dev. Both: three kinds of routed vein (vault, false door, unlinked pair) and '
  'Core-style scattered lumps of 3 to 10 cells through the remaining rock.'),

 ('- [ ] **"but a bit more than vanilla like 3x more deposites than a default map"**',
  'CLOSED 0.12.82-dev. `VanillaDensityMultiple = 3` against `CoreLumpsPer10kCells()`, which reads '
  'the count off Core’s **own** `GenStep_ScatterLumpsMineable` at runtime rather than copying '
  'it — the only honest reading of "vanilla" is whatever Core computes for itself. The '
  'fallback, if that step is ever missing, is stated and logged once rather than silent.'),

 ('- [ ] **"we properly use the main menu images we made for the mod on the main menu page"**',
  'CLOSED 0.12.82-dev as the owner’s own correct read, and the list moved to '
  '`Presentation/RimroomsSlideArt.cs` so the menu and every other surface take the same images from '
  'one place — *"the same images"* cannot be two lists that agree until somebody adds a PNG.'),

 ('- [ ] **"so we need those mod images made for the menu to also use them randomly for load screen backgrounds"**',
  'CLOSED 0.12.82-dev, **and the owner’s instinct was exactly right.** `currentIndex` was '
  'pinned to `0` in the constructor and reset to `0` again in `ApplySettings`, so the menu — '
  'and therefore the backdrop behind every load started from it — opened on slide one of six, '
  'every single time, forever. It is drawn now, from the wall clock rather than from `Rand`, which '
  'is kept well away from the seeded randomness every generated place depends on.'),
]

FINDINGS = [
 ('- [ ] **"but i dont think we properly did the same for loading screens and the like"**',
  '**STILL OPEN, and here is the honest boundary.** The entry-state waits — loading a save, '
  'starting a game — draw `UIMenuBackgroundManager.background`, so those now show our art and '
  'show it randomly. **An in-play long event does not**: `Root.OnGUI` skips the UI root entirely '
  'while `LongEventHandler.ShouldWaitForEvent`, and the box Core draws over the frozen frame is '
  'Core’s own. Drawing behind that needs a transpiler, and this mod ships **no Harmony** by '
  'decision. What is reachable without one is a surface **we** own, which is the pre-generation '
  'notice in the row below — so these two rows close together.'),

 ('- [ ] **"that pops up befgore the "freeze" of the generation"**',
  '**STILL OPEN, and the design is settled rather than guessed.** Read against the code this '
  'session: `DestinationService.EnsureSite` calls `GetOrGenerateMapUtility.GetOrGenerateMap` '
  '**synchronously** at line 186 and returns the map through an `out` parameter, so every caller '
  'depends on it having finished. A window added to the stack immediately before that call renders '
  'on the *next* frame, which is after the freeze — so the popup cannot work until the '
  'generation is deferred into `LongEventHandler.QueueLongEvent`, which changes the contract every '
  'caller of `EnsureSite` relies on. **That is its own checkpoint and it is deliberately not '
  'half-built here**: a notice that appears after the thing it warns about is worse than none, and '
  'the keyed text would be *"a collected list nothing spends"*, which this repo names as its most '
  'repeated defect.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0

for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    # the row ends at the next blank line or the next list marker at column 0
    end = text.index(NL + NL, at) if NL + NL in text[at:] else len(text)
    nextrow = text.find(NL + "- [", at + 1)
    if nextrow != -1 and nextrow < end:
        end = nextrow
    row = text[at:end]
    # status marker only
    for marker in ("- [ ] ", "- [~] "):
        if row.startswith(marker):
            row = "- [x] " + row[len(marker):]
            break
    else:
        # the anchor starts mid-row; flip the marker on the row's own line
        line_start = text.rfind(NL, 0, at) + 1
        line = text[line_start:at]
        if "- [ ] " in line or "- [~] " in line:
            text = text[:line_start] + line.replace("- [ ] ", "- [x] ").replace("- [~] ", "- [x] ") \
                + text[at:]
            at = text.index(anchor)
            end = text.find(NL + "- [", at + 1)
            if end == -1:
                end = text.index(NL + NL, at)
            row = text[at:end]
        else:
            print("NO MARKER ON ROW: %s" % anchor[:88])
            problems += 1
            continue
    text = text[:at] + row + " — **" + evidence + "**" + text[end:]

for anchor, note in FINDINGS:
    found = text.count(anchor)
    if found != 1:
        print("FINDING ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    end = text.find(NL + "- [", at + 1)
    if end == -1:
        end = text.index(NL + NL, at)
    text = text[:end] + " — " + note + text[end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)

io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("marked %d rows [x] and recorded %d findings" % (len(CLOSED), len(FINDINGS)))
