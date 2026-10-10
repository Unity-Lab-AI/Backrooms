# -*- coding: utf-8 -*-
"""0.12.74-dev: a ramp is not an open connection, and the generators go outside."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: close-1274.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

ENTRY = u"""
---

## Session 2026-10-01 - a ramp is not an open connection, and the generators go outside (0.12.74-dev)

**Verbatim user quotes:** *"check the game last notices every check mark is complete but it still
says:  the lab connection to that address is not connected.. but the checked staps says
otherwise.. i see the glow and all boxes where done"*; *"and do u see where i moved the comms to
and the machining bench thats where i want them so fix there spawn position"*; *"and actuall make
onbe of the rooms a power room and where the generators are should be a breeze way thats unroffeced
area complete just that area they are in thats inclose by walls and doors"*; *"generators out side
batteries inside"*.

**Files touched:** `UI/OperationsGateSteps.cs`, `Scenario/GenStep_Headquarters.cs`,
`Scenario/RimroomsStartDef.cs`, `Keyed/RR_GateSteps.xml`,
`Defs/RimroomsStartDefs/RR_Starts.xml`, `tools/check-start-layout.py`,
`build-async-facility.py`, `proof-starts.py`, `proof-startplacement.py`,
`plant-startplacement.py`.

**Mod register.** Nothing new applied. Row 185 still carries the viewing glass, unchanged.

### The tick was wrong, and it was mine

Owner: *"every check mark is complete but it still says: the lab connection to that address is not
connected.. but the checked staps says otherwise"*.

Step 11 read `Done = gate.IsOpening || gate.IsSpinningUp`. **`IsSpinningUp` is defined as
`!IsOpening`** -- it is the ramp, the deliberate *"ramp up process that takes a bit of time"* the
owner asked for in September. So the moment they pressed *open a session*, all eleven checks showed
complete, they sent a colonist, and `PortalTravelService` refused with
`RR_PortalTravel_SessionClosed`: *"The laboratory connection for that address is not open."*
**The refusal was correct and the checklist was lying.**

Step 11 is `Done = gate.IsOpening` now, and while the ramp runs it reports **the live percentage**
and says the thing a player watching a progress bar needs told: the charge bleeds back down while
nobody holds the console, and at zero it lapses.

**And the list now ends somewhere useful.** Eleven checks finished at a live connection and said
nothing about the player's actual goal, so a completed list still left them asking what they were
missing. `RR_Steps_NowCross` appears once the session is open: select one colonist, press *order a
crossing*, and opening a door never moves anybody by itself.

### Core moves the centre of an even-dimension building, and three of our models did not

Owner: *"do u see where i moved the comms to and the machining bench thats where i want them"*.
Read out of `Autosave-3.rws` and converted by the layout offset of **(120,120)** on their
300-cell map: console **(32,33) facing south**, assembly bench **(45,33)**.

At first reading the console looked impossible: a 3x2 footprint at z=33 would cover z=34, which is
the ballistic glass. **The game had already accepted it, so the model was wrong.**
`GenAdj.AdjustForRotation`, decompiled from the installed assembly, swaps the axes for a horizontal
rotation and then, **if a dimension is even, shifts the centre by one** -- `(-1,-1)` for south. So
the console occupies z32..33 and its interaction cell is (32,31). The operator stands in the
control room looking north at a console that looks into the gate hall, which is a better station
than the one that was authored.

**Three copies of that rule were wrong at once** -- checker sixteen, the facility generator and
`proof-starts.py` -- and all three said the owner's console overlapped the glass it is sitting
against. Three derivations of one Core rule is the defect this project keeps meeting; all three now
carry the same arithmetic and cite the decompiled source.

**That is the second time today reasoning from memory about Core produced the wrong answer** -- the
first was `GenSpawn.Spawn` supposedly throwing on wall-over-wall. The decompiler is the authority.

### A new rule, and it found a defect the day it was written

`IsOperatorOnStation` requires the pawn to stand on **exactly** the interaction cell, so a bench
whose interaction cell is a wall can never be used -- and the owner's entire gate saga was a
console they could not staff. Checker sixteen refuses that now, and immediately refused
**`RR_FurnitureStoreStart`**: its comms console at (17,32) had its interaction cell at (17,34), the
staff room's north wall. **That console had never been usable**, and reaching the corporation is
that scenario's whole achievement. Rotated south; the operator stands at (17,30).

### The power room and the breezeway

Owner: *"actuall make onbe of the rooms a power room and where the generators are should be a
breeze way thats unroffeced area complete just that area they are in thats inclose by walls and
doors"*, and *"generators out side batteries inside"*.

**`roofed: false` did nothing before this.** Every room is nested inside a roofed compound and the
compound's pass ran first, so a nested room asking for no roof got one anyway -- meaningless for
exactly the case it is needed in. It sets **or clears** now, in authored order, so a later room
cuts a hole in an earlier one's roof with no special case.

The **breezeway** is the only unroofed room in the facility: walled, doored, and open to the sky,
with both wood-fired generators in it. A fuel generator in a sealed room cooks the room. The
**power room** next door is roofed and holds the four-battery bank, which had been sitting in the
control room only because the first authoring had nowhere better. Fifteen rooms, twenty-two doors,
150 fixture cells.

`proof-startplacement.py`'s roof model had to learn the same rule: an unroofed nested room
**discards** what an earlier one laid, or the model would call the breezeway roofed and then demand
support for it.

### Two of my own claims had holes, and my own plants found them

**Ninth instance of machinery-not-behaviour.** The ramp claim asserted that `ramping` was computed
and that `RR_Steps_11HowRamping` existed. A plant set `How = false` and **both stayed true** while
the ramp never reported its progress again. The claim pins the branch now.

**Forty-fifth instance of the scoping trap.** The interaction-cell claim asserted the message text
appeared in the checker; a plant that commented the whole `fail(...)` out left the words sitting in
a comment. The claim pins the call.

**`89 of 91` is the only reason either was found.** Both are plants I wrote against claims I wrote,
and the suite caught the claims rather than the code -- which is the second time in two checkpoints
that has happened, and the clearest argument there is for writing the plant before trusting the
claim.

**205 C# files, 92 package files**, zero warnings, zero errors. Assembly SHA-256
`%(hash)s`, measured after the version bump, reproduced by two clean recompiles.
**Seventeen checkers pass, forty-five proofs hold, 91 of 91 planted faults caught in the
start-placement suite, 669 plant anchors findable.**
""" % {"hash": HASH}

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = u"## IN PROGRESS - a ramp is not an open connection, and the power room - 2026-10-01 (0.12.74-dev)"
HEAD_NEW = u"## A ramp is not an open connection, and the power room - 2026-10-01 (0.12.74-dev) - DONE"
if todo.count(HEAD_OLD) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(HEAD_OLD))
    raise SystemExit(1)
todo = todo.replace(HEAD_OLD, HEAD_NEW, 1)
start = todo.index(HEAD_NEW)
end = todo.index(u"\n---", start)
block = todo[start:end].replace(u"- [~] **", u"- [x] **")
todo = todo[:start] + block + todo[end:]
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO marked done, every description kept")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.73-dev**.", u"| Published | **0.12.74-dev**."),
    (u"SHA-256 `C6988A04423FE4A656A15D29EEE97C21BA2D323C842C07EE9A96B81AEF9F57D6`",
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
print("NOW.md updated for 0.12.74-dev")
