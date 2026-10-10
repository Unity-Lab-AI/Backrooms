# -*- coding: utf-8 -*-
"""FINALIZED first, verified, then the TODO status flips. Descriptions are never touched."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")

ENTRY = u"""
---

## Session 2026-09-30 - the site had to be prepared, not refused (0.12.47-dev)

**Verbatim user quote:** *"i did a store start the map loaded correctly but i had pop up company
could not finish startup company placement stopped... so wtf is up with this??? also the starting
store structure was not built and i have no pawns on the map to control"*

**Verbatim user quote:** *"you can use the api mod you have that we installed last so u can see wtf
rimworld is doing"*

**Verbatim user quote:** *"i think the issue was there was shit where it planned on putting the
store and pawns so it errored it needs a like a burn into place functiions to carve everyhting out
and cut everything down and fill in with soil where water is unmder where the store needs to
propigate before game start"*

**Verbatim user quote:** *"and the store facilities walls floors and all of it have to be
reconfigureable deconstructable and minifyable(the minify mod) just like the game with the mods
allows"*

**Verbatim user quote:** *"and when ur ready to redo rimsort kill rimworld .exe and build the mod
correctly in local with other mods and then ill start rimsort"*

**Files touched:** `src/RimroomsAsyncIndustries/Scenario/GenStep_Headquarters.cs`,
`src/RimroomsAsyncIndustries/Scenario/HeadquartersLayout.cs`,
`src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsArrival.cs`,
`Mod/Rimrooms - Async Industries/1.6/Defs/ScenarioDefs/RR_Scenarios.xml`,
`Mod/Rimrooms - Async Industries/About/About.xml`,
`src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj`, `README.md`,
`docs/implementation/BURN_INTO_PLACE_IMPLEMENTATION.md`, `docs/TODO.md`, `docs/NOW.md`.

**Closure notes.** **The owner's own diagnosis was right before any code was read**, and the fix
carries their name. This is also the first checkpoint whose evidence came from the running game:
the owner said *"you can use the api mod"*, so RimBridgeServer 2.1.1 in direct mode, read-only,
against their own launched process — the port and token read from their live log.

**Measured rather than inferred.** `Player.log` named the throw at `(133, 0, 135)`;
`rimworld/get_cell_info` found a **Granite Mineable with 900 hit points** there; a sweep of all
**1020** footprint cells found **164 Marble and 70 Granite formations, 177 cells of natural rock
roof, roughly 440 plant cells, 34 cells of rubble and chunks, and two monkeys**.
`rimworld/list_colonists` returned **0**. **234 of 1020 cells held natural rock** — the build had
no chance and threw on its very first cell.

**Two defects, both consequences of 0.12.46-dev correctly handing the map back to Core.**

**One: the facility refused ground it did not own.** Fixed in two halves. Prevention —
`RR_HeadquartersTerrain` moved from **order 5 to order 100**, between Core's `ElevationFertility`
(10) and `RocksFromGrid` (200), and lowers site elevation to **0.55** against Core's **0.7** rock
threshold, so no formation and no natural roof are ever generated there. At order 5 the elevation
grid did not exist yet and the terrain it wrote was overwritten at order 210, so that step had been
doing nothing. Then the burn — `HeadquartersBuilder.BurnIntoPlace`, running **before a single
wall**, carving everything out, cutting everything down, clearing the natural roof a formation
leaves behind, and filling water and impassable terrain with the start's own soil. Nothing living
is touched, and a faction structure is **named in a warning** before it is cleared.

**Two: the arrival killed Core's scenario step, and that is what made it unplayable.**
`ScenPart_RimroomsArrival.GenerateIntoMap` threw when the receipt was incomplete.
`MapGenerator.GenerateContentsIntoMap` abandons a gen step at its first exception, so **Core's
entire scenario step died: no colonists, no supplies.** A subclass of
`ScenPart_PlayerPawnsArriveMethod` is an addition to Core's arrival, not a replacement — it falls
back to `base.GenerateIntoMap` now, and still records `arrivalStarted` so a retry cannot grant
stock twice. The facility's `catch` stopped re-throwing too and hands
`MapGenerator.PlayerStartSpot` back to Core, which picks a real spot at order 850.

**Reconfigurable, deconstructable, minifiable: it already held, and the work was making it
checked.** Register row **[128] MinifyEverything** — its installed assembly mutates
`ThingDef.minifiedDef` and `building.alwaysUninstallable` at startup, **on defs, not instances**,
so every Core def the facility places is covered and a def of our own would be outside its reach
entirely. Every placement carries `Faction.OfPlayer`; nothing touches `designationManager`;
`TerrainGrid.SetTerrain` records the under-terrain for layerable floors so Remove Floor works.
And the one that needed measuring: `RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**, and
replicating that rule found **zero unsupported roof cells in all three layouts** — 884/540/0,
686/334/0, 25/24/0. The Store's 34x30 showroom holds up only because its inner rooms' walls stand
inside it; that was luck, and it is a proof claim now.

**Verification.** `proof-startplacement.py` gained **20 claims** and `plant-startplacement.py`
gained **21 plants plus one retarget** — the old whole-map-flatten plant anchored on a loop the
terrain step no longer has, and **a plant whose anchor has rotted away aborts the suite rather
than scoring a fault it never planted.** Sweep **56 of 56**. The interpreter caught a real
mistake: the new claims named a variable `arrival` that the reachability section already used for
an `re.search` match 200 lines later.

**199 C# files, 90 package files**, zero warnings, zero errors. Assembly SHA-256
`85B6769552B8D94641A5DA8B93BB9514715FE90AE9087BC0106C528F60ECE540`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty proofs hold**, all read by exit status. Record:
`implementation/BURN_INTO_PLACE_IMPLEMENTATION.md`.

**Four launches, ten defects, every one ours. Still not a single mod conflict.**
"""

FLIPS = [
    u'- [~] **"i had pop up company could not finish startup company placement stopped',
    u'- [~] **"the starting store structure was not built"**',
    u'- [~] **"i have no pawns on the map to control"**',
]

todo = io.open(TODO, encoding="utf-8").read()
problems = []
for flip in FLIPS:
    if todo.count(flip) != 1:
        problems.append("%d occurrence(s) of %r" % (todo.count(flip), flip[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

# FINALIZED first, and verified, before the TODO status moves.
final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- TODO left untouched")
    raise SystemExit(1)
print("FINALIZED entry written and verified")

for flip in FLIPS:
    todo = todo.replace(flip, flip.replace(u"- [~] ", u"- [x] ", 1), 1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("%d TODO row(s) flipped to done, descriptions untouched" % len(FLIPS))
