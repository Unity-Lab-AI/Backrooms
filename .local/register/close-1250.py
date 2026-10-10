# -*- coding: utf-8 -*-
"""0.12.50-dev closure: TODO rows, FINALIZED entry, NOW.md state. Written as a file."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Coordinate rebuild, stages two to four — 2026-09-30 (0.12.50-dev)

- [x] **"dont let them go more than 5 remember the games mechanics and limits built in ... they should gett a warning this gate is blocked your holding open too many gates, but per scerio styled"** and **"5 is the limit of other colonies available so a backrooms level should be one colonly bacskicly in my thinking"** — **DONE.** `OpenMapBudget` reads **`Prefs.MaxNumberOfPlayerSettlements`** (the player's own 1-to-5 slider, which Core enforces in `SettleUtility`) rather than hard-coding a 5, counts coordinate maps alongside Core's settlements because Core cannot see ours, and accepts a per-scenario override via `RimroomsStartDef.openMapBudget`. **A floor of 2 is load-bearing**: the slider can be 1, and the solo/group start opens a coordinate while the surface map already counts, so without it that start refuses its own opening. Enforced at the doorway before any coordinate is minted, and again at `EnsureSite` as the backstop — but **after** the way-out attempt, because a way home costs no map and blocking it would strand a deep crew.

- [x] **ways onward and depth raised** — **DONE.** `FrontiersFor` gives **4 to 6**, one more per 20 rooms, read from the room count rather than depth. `MaximumNaturalDepth` **3 → 6**. What made it safe is the budget, not a change of mind about finiteness. **Two proofs objected correctly** and their restraints are kept and asserted harder: no research capability may buy more ways onward or reach further, now checked by reading `FrontiersFor`'s body.

- [x] **"and everything doesnt have to be square rooms and rectangle halways"** — **DONE.** `RockIntrusionCells` leaves rock standing in the **corners only**, as quarter-ellipses, **never on the centre cross or an edge midpoint** — which is what makes it provably unable to disconnect a doorway, modelled at every depth by filling every corner at full reach and flood-filling to all four edge midpoints. Depth 1 stays rectangular. Corridors are three or five cells from `CorridorHalfWidthBetween`, and the planner reads the same function the generator carves from.

- [x] **"make sure u are using prep and mod registry as needed"** — **DONE, and it found a live defect nothing in our own code could have.** Register row **[188] Removable Mt.Rock Roof Patch** is installed and patches `RoofRockThick.isThickRoof` to **false**, so in this profile Core's overhead mountain **vanishes on collapse**. Invariant 13 was **already broken before this session**; the new roof def repairs it, and it is a second reason patching Core's roof would have been wrong. Rows [69] Craftable Mountains and [63] Change map edge limit checked and clear.

- [x] **"they are just doors too right that dont need the mechine gate systems"** — **CONFIRMED by live measurement, not inference.** The natural gate in the owner's running game is a plain `RimWorld.Building_Door` in steel with Deconstruct, Uninstall, Reinstall and the emergence gizmo, no power, console, calibration or assembly.

- [x] **"so we need a way to deconstruct natural gates too i think"** and **"and then u lose them forever"** — **ALREADY HELD; nothing had to be added.** `EndpointPresent` refuses an edge whose anchor is destroyed, and `PortalDoorWarningMapComponent` already warned with informed consent.

- [x] **"but maybe allow minify move"** — **DONE, and it did not work before.** `EndpointPresent` also requires `Anchor.Position == AnchorCell`, and `PortalEndpointRecord` says the cell is a deliberate snapshot so *"moving a door cannot silently redirect a saved route"* — right under the old no-move rule, wrong now. `TryFollowMovedAnchor` is a **move**, not a refresh: same `Thing` instance only, branch-owned ground only, **refused while a crossing is in flight** (invariant 55), and not on load. Uninstall and deconstruct now say different things, and the red destructive confirmation is reserved for the one that is.

- [ ] **"how do they turn them off to use the machine gates for more controll and aiming deeper?"** / **"get 5 natural gates u cant use a machine gate"** — **OPEN, and deliberately NOT half-built. Next checkpoint, first thing.** The owner chose an **Operations held-places list with Release**. Releasing a place is not a UI problem; it needs (1) a **save-schema field on `CoordinateRecord`**, because `EnsureSite` deliberately refuses to regenerate a coordinate whose rooms were surveyed and only a flag can distinguish a deliberate release from a broken reference; (2) map teardown that orphans neither the world object, the `Site` reference, nor a portal edge pointing in; (3) a refusal set — crew present, crossing in flight, or the headquarters. Getting any of those wrong produces an unreachable place or a dead record, which is the exact defect class that cost thirty-nine checkpoints. **Mitigation meanwhile: discovering gates is free** — no map is generated until somebody crosses — so the cap is only met after five places are held open.

- [ ] **still open from the same direction** — the wild variation of materials across items, equipment, walls, floors, lights, furniture and benches, with the events, layouts and loot deeper in.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - the warren, the map budget, and a doorway you can carry (0.12.50-dev)

**Verbatim user quote:** *"dont let them go more than 5 remember the games mechanics and limits
built in if they find a gate to a world map tile or a deeper backrroms and they have 5 mpas they
should gett a warning this gate is blocked your holding open too many gates, but per scerio
styled"*

**Verbatim user quote:** *"5 is the limit of other colonies available so a backrooms level should be
one colonly bacskicly in my thinking"*

**Verbatim user quote:** *"and everything doesnt have to be square rooms and rectangle halways"*

**Verbatim user quote:** *"yeah so if the player discovers and goes through a natural gate how do
they turn them off to use the machine gates for more controll and aiming deeper?"*

**Verbatim user quote:** *"get 5 natural gates u cant use a machine gate"*

**Verbatim user quote:** *"so we need a way to deconstruct natural gates too i think"*

**Verbatim user quote:** *"and then u lose them forever but maybe allow minify move"*

**Verbatim user quote:** *"they are just doors too right that dont need the mechine gate systems"*

**Verbatim user quote:** *"make sure u are using prep and mod registry as needed"*

**Files touched:** `Portals/OpenMapBudget.cs` (new), `Portals/NaturalFrontierService.cs`,
`Portals/PortalConnectionRecord.cs`, `Portals/PortalCrossingService.cs`,
`Portals/RimroomsPortalNetwork.cs`, `Portals/CompRimroomsEmergence.cs`,
`Portals/PortalDoorWarning.cs`, `Generation/RoomLayoutPlanner.cs`,
`Generation/GenStep_BackroomsDestination.cs`, `Generation/DestinationService.cs`,
`Generation/BackroomsContainment.cs`, `Defs/RoofDefs/RR_Roofs.xml`, `Keyed/RR_Portals.xml`,
`Scenario/RimroomsStartDef.cs`, About/csproj/README,
`docs/implementation/WARREN_AND_DOORWAYS_IMPLEMENTATION.md`.

**Closure notes.** **The register instruction paid for itself in one query.** Row [188] *Removable
Mt.Rock Roof Patch* is installed in this profile and patches `RoofRockThick.isThickRoof` to false,
so Core's overhead mountain here **vanishes on collapse** - meaning invariant 13, *a Backrooms
coordinate has no outside*, **was already broken before this session's work**, and
`BackroomsContainment`'s claim that thick roof "never vanishes" was reasoning from unpatched Core.
The non-collapsing roof def introduced one checkpoint earlier for the cave-in direction repairs
that breach, and this is a second independent reason patching Core's roof would have been wrong.
**Nothing in our own code could have found this.**

**The map budget reads Core rather than writing a 5.** `Prefs.MaxNumberOfPlayerSettlements` is a
1-to-5 player slider Core enforces in `SettleUtility`, and Core's count cannot see a coordinate
map, so `OpenMapBudget` counts both. A floor of 2 exists because the slider can be 1 and the
solo/group start opens a coordinate while the surface map already counts. The budget is checked
**after** the way-out attempt, because a way home costs no map and blocking it would strand a deep
crew: the budget stops the mod opening another place, never closes the last door home. **And
discovering a gate is free** - no map exists until somebody crosses.

**Rooms stopped being rectangles in a way that is provably safe.** Rock is left in the corners
only, never on the centre cross, and the proof fills every corner at full reach and flood-fills
from the room centre to all four edge midpoints at every depth.

**A doorway can be carried now.** Destroying one already ended its route and already warned the
player; carrying one silently lost it, because the endpoint's cell is a deliberate snapshot.
`TryFollowMovedAnchor` is a move rather than a refresh: same Thing only, branch-owned ground only,
refused mid-crossing, and not on load.

**Eight of my own proof claims were too loose and plants found every one** - a doc comment, a
prefix, a surviving declaration, a shape appearing four times, the same line added to a second
function, a comment counting toward a count, an ordering compared across the wrong pair, and a
string appearing seven times. All eight are now scoped to a method body, an exact tag, or a call
site. **A claim about code must never be satisfiable by a comment, a prefix, a declaration, or a
duplicate.** And the heredoc rule earned its place twice more, the seventh and eighth times.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`0B307BD06299AE6EA7028267A1663D5D15315F540FEBDD8898432E60F1150599`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** 62 of 62 and 15 of 15 in the two
suites touched.

**One piece is deliberately not shipped and not half-built:** the Operations held-places Release
list. It needs a save-schema field on `CoordinateRecord` to tell a deliberate release from a broken
reference, teardown that orphans nothing, and a refusal set. Next checkpoint, first thing.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("stage two-to-four rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.49-dev**.", u"| Published | **0.12.50-dev**."),
    (u"SHA-256 `A17D99ED025EAAA975011D05F588BBB735793165EFF9E8E4881E2A18B26EEB13`",
     u"SHA-256 `0B307BD06299AE6EA7028267A1663D5D15315F540FEBDD8898432E60F1150599`"),
    (u"| Build | **199 C# files, 91 package files**",
     u"| Build | **200 C# files, 91 package files**"),
    (u"| Checkers | **THIRTEEN**, all passing.",
     u"| Checkers | **THIRTEEN**, all passing. **The proof count is FORTY-ONE since 0.12.49-dev** "
     u"-- `proof-coordinate-layout.py` was added after measuring that every constant in the "
     u"coordinate planner could be changed with all forty existing proofs still passing. "
     u"`check-info-cards.py` also caught a new keyed string saying *doorway* where the project's "
     u"vocabulary says *door*."),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.50-dev")
