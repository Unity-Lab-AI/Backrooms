# -*- coding: utf-8 -*-
"""0.12.65-dev: the ways onward nothing ever asked about, and a hallway that is a room."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"4C1C043BCD3F11D320D459091F4FB1D1D8FE595CADB5B89F3D67A0F67AADC5DF"

ENTRY = u"""
---

## Session 2026-10-01 - the ways onward nothing ever asked about (0.12.65-dev)

**Verbatim user quotes:** *"okay its working. if u check the game i explored the full map i think
and i never found any natural cates to the world map tiles or natural portals to deep into the
backrroooms so its great it working i just never found any other gates with option to \\"walk
through\\" adding them to the loaded maps of my game play through"*; *"and another thing as you can
see the hall ways are just rectangles and arnt correctly the themed color and materials and there
wasnt enough \\"people-food\\" in the back rooms need to be able to survive a bit if it was a solo
start. and i see the whole map is almost like a string of pears. when it should just be basicly
\\"rooms\\" as halways with the exact shit thats in the rooms... get it? do you need to check prep
work on the Universe of the backrooms?"*; *"and another thing they were all just square rooms
again..wtf dont u know any other compbinations"*.

**Files touched:** `Portals/CompRimroomsEmergence.cs`, `Generation/RoomLayoutPlanner.cs`,
`Generation/GenStep_BackroomsDestination.cs`,
`Defs/RimroomsRoomArchetypeDefs/RR_RoomArchetypes.xml`, `Keyed/RR_Portals.xml`,
`.local/harness/PlannerProbe/Program.cs`, all sixteen plant suites, three proofs.

**Mod register.** Nothing new applied. The generation work is our own arithmetic and our own
archetype defs over Core's own thing categories.

**The owner asked whether to check the prep work. The answer was yes, and it already said all of
this.** `docs/UNIVERSE_ADAPTATION.md`: a coordinate is *"a stable, seeded expedition site made of
rooms and routes"*, and the instruction is to *"reuse recognizable room categories, materials,
fluorescent lighting, service infrastructure, and furniture as the baseline"*, with a *"repeated
hall"* among the intended spatial changes. `docs/PROCEDURAL_SPACE_CONTRACT.md`: *"Unseen
connections appear as unknown, not as empty corridors."* **The owner's correction was the prep
work, and the code had drifted from it.**

### The ways onward had no caller at all

`NaturalFrontierService.Discover` and `IsFrontierCandidate` had **ZERO callers in the package.**
The draw, the cap, the emergence share, the world-exit fallback, the guaranteed pair added two
checkpoints ago, and **twenty-odd `RR_Frontier_*` strings written for the player to read** --
including `RR_Frontier_Discovered`, which announced an event nothing could raise. All correct, all
unreachable. **Nothing ever asked a door whether it was a way onward**, which is the fifth time in
this run that computing a value and using it turned out to be two different facts.

A door that is not a live gate is now asked, and a way onward offers *"Walk through - this door
leads somewhere else"*, which records it and crosses in one act because they are one act.
`Discover` is idempotent, so a second click simply crosses.

**And it glows blue before discovery**, because a natural gate is permanently open and the owner's
own cue for one is the blue. A way onward findable only by right-clicking every door on a
three-hundred-cell floor is a way onward nobody finds -- which is exactly what happened.

**A proof refused that and was right.** `Evaluate` serves ordinary maps too, under its own
`worldfrontier:` origin, so the first draft would have lit a door in an ancient structure on the
player's **own colony map** the moment the mod was installed. `CONTENT_REUSE_POLICY.md` forbids
changing an existing colony by installing, and the claim *"no other door in the game is affected"*
is what held the line. The glow is confined to a coordinate.

### The rooms were not square because the shaping was off -- it was because there was one shape

**The probe measured the old shaping running the whole time**: 89% of depth-1 rooms carried rock
at 7% of their interior. So the amount was never the problem, and the obvious guess -- more reach
-- would only have produced **rounder squares.** There was exactly one form: a quarter-ellipse
nibbled from each corner, and four rounded corners reads as a square room.

So the vocabulary grew instead. **Seven forms** -- corners, ell, tee, cross, wedge, partition,
bays -- chosen per room from its own seed, and a plain room is deliberately one of them. Rock went
from **7.1% to 18.5%** of interior at depth 1 with every layout still valid and no room losing its
landmark. The grand hall is excluded, for the reason `FalseOpening` excludes it.

**Every form is safe for free, and that is worth stating.** Rock lives only inside the inset-2
interior, so the one-cell ring behind the perimeter is always a complete walkable loop; and the
centre cross is inviolable. Any pattern obeying those two cannot disconnect anything, which is why
`CandidateIsSafe` keeps proving walkability against the same function without knowing which form
was drawn.

### A hallway is a room, and two hardcoded values were the whole of it

The corridor floor was the raw carve terrain -- `concrete`, what rock becomes when you clear it --
while every room got the band's palette floor with accent stripes. And the corridor walls were
`ThingDefOf.Steel`, **literally**, while a room's walls come from the coordinate's own materials
and carry the band's colour. **A themed yellow room opened onto a grey steel tunnel, on every
link, at every depth** -- which is *"arnt correctly the themed color and materials"* and most of
why the floor read as *"a string of pears"*.

Corridors are now painted by the same `BackroomsPalette.SetFloor` call `PaintRoom` makes, walled
in the coordinate's own stuff, tinted the band's colour, lit, and dressed with the same fixtures
the rooms carry -- **against their walls only.** `BuildCorridors` reports the cells one in from
each wall and never the centre line, so the route through a corridor stays as clear as a room's
reserved cross, and a three-cell corridor gets nothing while a five-cell one does.

### There is food down there

Food was in **one of sixteen archetypes**, behind `minDepth 2` and a 70% roll: best case about
twenty meals somewhere on the floor, usual case none. The solo start begins *inside* a coordinate
with whatever it holds. The canteen reaches a first level and is certain; the storeroom -- the
highest-weighted archetype at 1.4 -- holds raw food in quantity; the dormitory keeps a little by
the beds. All through Core's own `FoodRaw` and `FoodMeals` categories, so nothing is invented.

### The instrument that guards the source tree was corrupting it

A suite crashed mid-run and left `Campaign.NoteReturnedFromField(...)` **deleted** in
`RimroomsExpeditionComponent.cs` -- the second time that exact line has been found planted. Two
defects, one cause: `stdout=open(os.devnull, "w")` was **never closed**, in all sixteen suites, so
after enough plants Windows raised `OSError: [Errno 22]`; and **fifteen of the sixteen had no
`finally`**, so the restore -- the one line that makes a destructive instrument safe -- was the one
line not protected. Both fixed everywhere.

### Four traps, all caught by the instruments

**The scoping trap twice more, instances thirty-eight and thirty-nine.**
`PlaceWall(map, cell, wallDef, wallStuff);` occurs twice -- a room's wall ring and a corridor wall
-- so a plant reverting the corridor one to steel was satisfied by the other; the claim reads
`PlaceCorridorWall`'s own body now. And the centre-line guard exists on both corridor axes, so
removing one left the claim standing; it is counted now.

**The machinery is not the behaviour, a fifth time.** The lamp and fixture claims asserted that
`CorridorLampSpacing` and `CorridorFixtureSpacing` *exist*. A plant replacing the conditions with
`if (false)` left both constants defined and both claims passing while no hallway was ever lit
again. The claims pin the conditions.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`4C1C043BCD3F11D320D459091F4FB1D1D8FE595CADB5B89F3D67A0F67AADC5DF`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 583 of
583** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
EDITS = [
    (u"## IN PROGRESS - the floor is a string of pearls - 2026-10-01 (0.12.65-dev)",
     u"## The floor is a string of pearls - 2026-10-01 (0.12.65-dev) - DONE"),
]
for old, _ in EDITS:
    if todo.count(old) != 1:
        print("TODO ANCHOR PROBLEM: %d of %r" % (todo.count(old), old[:50]))
        raise SystemExit(1)
for old, new in EDITS:
    todo = todo.replace(old, new, 1)
# Status only; every description keeps every word.
todo = todo.replace(u'- [~] **"i never found any natural cates',
                    u'- [x] **"i never found any natural cates', 1)
todo = todo.replace(u'- [~] **"i just never found any other gates with option',
                    u'- [x] **"i just never found any other gates with option', 1)
todo = todo.replace(u'- [~] **"the hall ways are just rectangles',
                    u'- [x] **"the hall ways are just rectangles', 1)
todo = todo.replace(u'- [~] **"there wasnt enough \\"people-food\\"',
                    u'- [x] **"there wasnt enough \\"people-food\\"', 1)
todo = todo.replace(u'- [~] **"i see the whole map is almost like a string of pears',
                    u'- [x] **"i see the whole map is almost like a string of pears', 1)
todo = todo.replace(u'- [~] **"they were all just square rooms again',
                    u'- [x] **"they were all just square rooms again', 1)
todo = todo.replace(u'- [~] **"do you need to check prep work on the Universe of the backrooms?"**',
                    u'- [x] **"do you need to check prep work on the Universe of the backrooms?"**', 1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO marked done, every description kept")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.64-dev**.", u"| Published | **0.12.65-dev**."),
    (u"SHA-256 `29933F471C7631CCCA650E6246A6E09DBF63946C406FD055775A56658BAF5A8B`",
     u"SHA-256 `" + HASH + u"`"),
]
problems = []
for old, _ in NOW_EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in NOW_EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.65-dev")
