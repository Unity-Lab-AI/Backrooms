# -*- coding: utf-8 -*-
"""0.12.73-dev: the machine tab is numbered, and the facility becomes a facility."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: close-1273.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

ENTRY = u"""
---

## Session 2026-10-01 - the machine tab is numbered, and the facility becomes one (0.12.73-dev)

**Verbatim user quotes:** *"okay i need help. .. check the game what do i do to get this gate
open? ive tried everything.. follow my past attempts and tell me what im missing"*; *"well what
the fuck i already told you the company start needs a fulley connect and set up sweet ass
facility.. currently it looks like a 6yr old chimp made the facility as the gate is rfree standing
and it now weays looks like a working \"machine\" that should be designed intelligently with like
ballistic glass  walls for viewing the machine remotely and safely with security zones and shit and
lab rooms and shit i mean wtf is this this is a 50million dollar facilty"*; *"now it just says gate
is not ready to calibrate,, what am i missing"*; *"check the game cxurrently"*; *"the whole machine
tab needs to be numbered and everything step 1 step 2... ect ect so fucking simple a 6 yr old chimp
can do it"*; *"okay fucking do it then because im fucking lost on what to do ive done like 50
things in a row and its still not opening"*; *"this is fucking rediculous and it needs to have
checks showing the start up connection checks are complete or unfinished yet"*; *"and it need to
explain conciselky how, becuse this is fucking confusing"*.

**Files touched:** `UI/OperationsGateSteps.cs` (new), `UI/OperationsPortalNetwork.cs`,
`UI/OperationsExpeditions.cs`, `Gate/CompRimroomsGate.cs`, `Gate/NativeGateBinding.cs`,
`Scenario/RimroomsStartDef.cs`, `Scenario/GenStep_Headquarters.cs`,
`Keyed/RR_GateSteps.xml` (new), `Keyed/RR_Portals.xml`, `Keyed/RR_Gate.xml`,
`Defs/RimroomsStartDefs/RR_Starts.xml`, `tools/check-start-layout.py` (new, checker SIXTEEN),
`tools/check-plant-anchors.py` (new, checker SEVENTEEN),
`tools/package-files.json`, `proof-starts.py`, `plant-startplacement.py`.

**Mod register.** **Row 185, ReBuild: Doors and Corners, applied -- and its Planned Use is
verbatim what the owner asked for:** *"Use the construction and layout tools to create gate
control, labs, secure storage, accommodation, service corridors, and outposts."* Trace
`RR-FAC;RR-GATE`, stance **Optional**, firmness Settled, FinalDisposition *"Optional architecture
reference; do not reuse code/assets under CC BY-NC-ND."* So its `RB_ReinforcedGlassWall` is
**named at runtime and never reused**: no code, no texture, no def copied, and a profile without
the mod gets an ordinary wall. `find glass` over the register returns nothing, which is why the
288 installed Workshop folders were searched directly to find who provides one.

### Nothing was broken. The interface could not say what was missing

The owner spent an afternoon on a gate that was **already assembled, already calibrated, already
crewed and un-tripped.** `Autosave-5.rws` at 11:38 said so: `rr_gateAssemblyComplete True`,
`rr_gateCalibrated True`, operator `Thing_Human979`, kill switch null -- and
`TableMachining55327` with `gateControl True` while the `CommsConsole` bound to the same gate had
no entry at all, which is false.

**One switch out of eleven steps, and three separate things conspired to hide it:**

| | |
|---|---|
| `RR_Gate_CalibrationUnavailable` | *"The gate is not ready for calibration"* for **all eight** of `CanCalibrate`'s conditions, **including `calibrated` itself.** So the answer to *"now it just says gate is not ready to calibrate,, what am i missing"* was **nothing. It was finished.** |
| `RR_Gate_JobUnavailable` | one key for four different problems with four different fixes |
| the portal panel | the open buttons are drawn **one per remembered address**, so a gate with none drew **no button and no sentence**. There was nothing to press and nothing to read |

### The fix: eleven numbered checks, live, each with one sentence of how

Owner: *"the whole machine  tab needs to be numbered and everything step 1 step 2... ect ect so
fucking simple a 6 yr old chimp can do it"*.

`DrawGateStartupChecks` runs **first** in the Machine tab, because it is the thing that says which
of the two panels below it to use. It prints the count complete, **names the first unfinished step
on its own line**, then lists all eleven -- finished ones as one line, unfinished ones with their
instruction, so the list is not a wall of advice about things already handled. A binding fault is
printed after the list as a fault rather than as a step, because it is something that was done and
has since broken.

**The order is not cosmetic and the proof asserts it.** Gate control on the **table** precedes the
assembly, because `RecipeWorker_RimroomsGateAssembly.AvailableOnNow` withdraws the recipe from a
bench in normal operation. Gate control on the **console** precedes staffing, because
`BeginSpinUp` refuses while either component is doing its day job. A player following the list top
to bottom never meets a step that cannot be done yet.

**And nothing here decides anything.** `BeginSpinUp` is still the authority; each step
corresponds to one condition it already checks. `CanCalibrate` now **asks** `CalibrationBlockerKey`
rather than restating its eight conditions, so the predicate the work giver uses and the message
the player reads cannot drift apart -- two derivations of one rule is this project's most
expensive defect shape.

### The facility, and why it was authored by a program

Owner: *"it looks like a 6yr old chimp made the facility"*. It was a 44x44 rectangle with eight
boxes stamped in it and the furniture listed flat. It is now a plan: a **gate hall** that is
deliberately empty because a machine hall with furniture in it is a room, its aperture door in the
north wall; a **control room** directly south of it; **eleven cells of ballistic glass** in the
wall between them; a **security airlock** of two automatic doors in series through a vestibule; a
**lab wing**, **secure storage** and the **workshop** holding the machining table, off a
full-width east-west service corridor; housing, mess and medical off two north-south corridors.
Ten rooms, sixteen doors, 122 fixture cells.

**`GenStep_Headquarters.Build` throws on any geometry mistake, and a throw inside a GenStep costs
the player the start.** So none of it was typed: `.local/register/build-async-facility.py` derives
every door from the wall it belongs to and checks every footprint against Core's own `<size>`
before emitting a line, and **`tools/check-start-layout.py` -- checker SIXTEEN -- re-validates the
emitted XML afterwards.** Two readers, and the one that validates did not author.

**The glass is named as strings, and that is the whole design of the field.** A `ThingDef` field
is a cross-reference resolved at load, and an unresolved one discards the **entire** containing
def -- which is exactly what took `Door` and `Autodoor` out of the game on the seventh launch and
produced **587 red lines** before the main menu. `ResolveFirstLoaded` asks the database at
generation time and the run falls back to an ordinary wall, because a solid viewing wall is a
cosmetic loss and a missing wall is a hole in a sealed gate hall.

**And the headquarters power rebuild is guarded now.** It was a bare
`UpdatePowerNetsAndConnections_First()` inside a GenStep -- the exact shape that cost two launches
in the destination generator this same day.

### Checker seventeen, because this checkpoint paid the same toll eight times

A plant suite stops at the first anchor it cannot find -- correctly, since a stale anchor would
silently skip a planted fault -- but it only finds the *next* stale one after running every plant
before it, and the suites take minutes each. Rebuilding the facility and renaming three gate
methods moved a lot of anchored text, and **eight separate four-minute runs were spent discovering
one stale anchor at a time.**

`tools/check-plant-anchors.py` reads every suite's `PLANTS` table with `ast` -- nothing executed,
nothing mutated -- and reports **all** of them at once. It found the remaining two in seconds.

**It cried wolf twice before it was right, and both corrections are the point.** `CHR_NL = chr(10)`
is a call rather than a literal, so `ast.literal_eval` refused it and **most anchors in the battery
read as unevaluable**; and it refused an entry `plant-def-fields.py` **skips itself** -- its loop
reads `if want is None: continue`, with a comment saying two earlier plants cover the same
property. A checker stricter than the thing it guards is the cry-wolf failure this battery has had
five of, so it now matches each suite's own rule: refuse an anchor with **no** match, report one
with several, and honour a skip the suite declares.

### Two claims were wrong about their own premises

**`proof-starts.py` refused any two rooms sharing a wall cell**, on the stated grounds that
*"wall on wall is the collision the generator actually throws on"*. **It does not throw.**
`Verse.GenSpawn.Spawn`, decompiled from the installed 1.6 assembly, logs for out-of-bounds and for
already-spawned and otherwise calls `WipeExistingThings`; `SpawningWipes(Wall, Wall)` is true, so
the second wall replaces the first. A wing built against the compound's outer wall is ordinary
architecture and the rule forbade it.

**That is the third time this claim has been wrong about its premise** -- the version before it
refused an interior room inside an outer shell. It now asserts the rule that is true and harmful,
the same one checker sixteen enforces: a wall must not cross another room's interior unless it is
nested inside it.

**And checker sixteen cried wolf on its first run**, flagging 368 legitimate cells in the Async
layout and 210 in the store before the nesting case was understood. Caught before it was committed,
which is the fifth false alarm in this battery's history and the reason each one is written down.

**Forty-fourth instance of the scoping trap, and it was mine:** a new claim asserted
`RR_Gate_JobUnavailable` was gone from the whole file and failed against correct code --
`OrderAssignedJob` still uses it for a missing job def and a pawn who cannot take the job, which
is what it actually describes. The claim is scoped to `OrderStaffConsole`.

**The interpreter caught one too**: a dead `"".join([... and 1 or 0 and "" ...])` expression left
in a new claim raised `TypeError` rather than passing silently. The `all()` checks beside it were
always the real assertion.

**205 C# files, 92 package files**, zero warnings, zero errors. Assembly SHA-256
`%(hash)s`, measured after the version bump, reproduced by two clean recompiles.
**SEVENTEEN checkers pass, forty-five proofs hold, 659 of 659 planted faults caught across sixteen suites.**
""" % {"hash": HASH}

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = u"## IN PROGRESS - the gate nobody could open, and the facility - 2026-10-01 (0.12.73-dev)"
HEAD_NEW = u"## The gate nobody could open, and the facility - 2026-10-01 (0.12.73-dev) - DONE"
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
    (u"| Published | **0.12.72-dev**.", u"| Published | **0.12.73-dev**."),
    (u"SHA-256 `8FFCF0F0BE7CA434F2883F94F7693B53AE65F4CF08B353F1CB0F7086BC1739D6`",
     u"SHA-256 `" + HASH + u"`"),
    (u"| Checkers | **FIFTEEN**, all passing.",
     u"| Checkers | **SIXTEEN**, all passing. **The sixteenth validates every authored starting "
     u"facility offline, cell by cell.** `GenStep_Headquarters` throws on any geometry mistake "
     u"and a throw inside a GenStep costs the player the start; the Async facility is ten rooms, "
     u"sixteen doors and 122 fixture cells, and nothing else in this battery looked at a single "
     u"one of them. It derives footprints from **Core's own `<size>`** with ParentName "
     u"inheritance rather than from a table, because a table is a second derivation that goes "
     u"stale. **It cried wolf on its first run** -- 368 legitimate cells -- before the nesting "
     u"case was understood, which is the fifth false alarm in this battery and the reason each "
     u"is written down."),
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
print("NOW.md updated for 0.12.73-dev, and the checker count with it")
