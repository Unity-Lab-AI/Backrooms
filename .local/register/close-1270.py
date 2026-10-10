# -*- coding: utf-8 -*-
"""0.12.70-dev: the assembly is a bill the player queues, and a component has two modes."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"EC6AAA0B82D00F3884994DEDECC2460B4E6777C0F90B4C64398725DB3CA0D30A"

ENTRY = u"""
---

## Session 2026-10-01 - the gate stops assembling itself, and a component has two modes (0.12.70-dev)

**Verbatim user quotes:** *"the machining table to op[en the gate needs to be a bill currently
they instantly try to open the gate and build it and i have no say in the mattter even tho nothing
is connected or built yet and havent started the mission line yet"*; *"we should have a set to gate
control for these components so other things arnt available and can toggle between normal op and
gate op depending whats wanted.."*; *"and dont forget to stage , now.md , then cascade"*; *"thats
the definiative order of operation(remember it and document)"*.

**Files touched:** `Gate/CompRimroomsGateConsole.cs`, `Gate/NativeGateBinding.cs`,
`Gate/GateSpinUp.cs`, `Keyed/RR_Gate.xml`, `docs/NOW.md`, `AGENTS.md`,
`proof-gate-links.py`, `plant-gate-links-carry.py`.

**Mod register.** Nothing applied. Both changes are our own comp on Core's own worktable and
console.

### The gate queued its own assembly, and nothing in the battery covered it

`BindNativeInfrastructure` ended with `EnsureNativeAssemblyBill`, which called
`EnsureAssemblyBill`, which **added an unsuspended `Bill_Production` to the machining table.** So
the instant a door was commissioned, crafters walked off with a hundred steel and eight
components. No decision, no mission, nothing connected -- which is exactly the report.

**The recipe's own description had said otherwise the whole time:** *"Designate the native door,
communications console, battery and machining table in Operations first"* is an instruction to a
player who then adds the bill, and `RR_AssembleMachineGate` has always carried
`recipeUsers: TableMachining`. **Nothing had to be built to give the player the choice. The choice
had been taken.**

`SyncAssemblyBill` replaces it -- renamed, because *ensure* was the whole defect. It **never adds a
bill**, and acts in the only direction that cannot take a decision away: it suspends a bill once
the gate is assembled, so a repeating one does not spend another hundred steel on a gate that
exists. It never un-suspends, and never touches the repeat mode or count.

**No proof and no plant mentioned the bill or the recipe**, which is why it shipped from the day it
was written. Three claims and five plants now cover it.

### Gate control: a component does its ordinary job or the gate's

Owner: *"we should have a set to gate control for these components so other things arnt available
and can toggle between normal op and gate op depending whats wanted.."*.

Every component bound to a gate carries a switch, and **it begins in normal operation**, so
commissioning still changes nothing about how the colony works.

**In gate control**, the component's ordinary company functions are withdrawn -- the corporate
supply call, the credit withdrawal, the containment alarm and the corporation contact stop being
offered -- and on a machining table **every bill that is not the gate assembly is suspended**,
recorded by Core's own unique load id so returning to normal resumes exactly those. A bill the
player had already suspended stays suspended, which is why the ids are recorded rather than the
state inferred.

**In normal operation the gate refuses**: the assembly recipe is unavailable on that bench, and
spin-up refuses naming the installation still doing its day job. *"depending whats wanted"* only
means something if both directions hold.

**And what Core-only cannot do is stated rather than pretended.** A comms console's own Core gizmo
cannot be removed without Harmony and a battery cannot be partitioned out of a power net, so gate
control withdraws **our** functions and gates **our** operations. The mode is still load-bearing
-- no spin-up, no assembly without it -- but Core's own call button remains pressable, and that is
a limit of staying Core-only rather than something hidden here.

### The order of operations is written down now

*"and dont forget to stage , now.md , then cascade"* — *"thats the definiative order of
operation(remember it and document)"*. **STAGE, then NOW.md, then CASCADE**, recorded at the top
of `docs/NOW.md` and in `AGENTS.md` beside the build rules, with the reason for each position:
stage first so play can begin immediately, NOW.md second so the handoff quotes a hash verified in
the game folder rather than an intended one, cascade last so the published commit contains the
handoff.

### The trap, an eighth time

**The machinery is not the behaviour.** The gate-control claim asserted
`suspendedByGateControl.Add(...)` and a plant deleted `bill.suspended = true;` beside it -- so
gate control recorded which bills it had suspended while suspending none of them, and every
asserted line was still present. The two are pinned together and in order now.

**And the scoping trap, a forty-first time.** `"EnsureAssemblyBill" not in console` failed against
correct code, because the comment explaining the method's removal names it.
`proof-gate-links.py` had no comment-free view; it has one now, as
`proof-coordinate-layout.py` has since 0.12.62-dev.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`EC6AAA0B82D00F3884994DEDECC2460B4E6777C0F90B4C64398725DB3CA0D30A`, measured after the version
bump, reproduced by two clean recompiles. **Fifteen checkers pass, forty-five proofs hold. 623 of
623** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = u"## IN PROGRESS - the gate assembles itself without being asked - 2026-10-01 (0.12.70-dev)"
HEAD_NEW = u"## The gate assembles itself without being asked - 2026-10-01 (0.12.70-dev) - DONE"
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
    (u"| Published | **0.12.69-dev**.", u"| Published | **0.12.70-dev**."),
    (u"SHA-256 `8E9ACA791C636A9636F3BAACD243DAB78BA720D7A102F250327EC9884089511F`",
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
print("NOW.md updated for 0.12.70-dev")
