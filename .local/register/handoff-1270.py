# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.70-dev, written after the stage so it quotes a verified hash."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## THE ORDER OF OPERATIONS, AND IT IS THE OWNER'S"

NEW = u"""## STATE AT THIS HANDOFF — `0.12.70-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.70-dev  91 files
assembly    EC6AAA0B82D00F3884994DEDECC2460B4E6777C0F90B4C64398725DB3CA0D30A
            read back out of the game folder after staging, not from the build
battery     15 checkers · 45 proofs · 623 of 623 plants · 16 suites
tree        no planted fault, porcelain 0
```

**Nothing is half-finished and nothing waits on a decision.** The last two checkpoints answered
the gate's controls; everything before them answered the generator.

### WHAT THE OWNER HAS NOT SEEN YET

**Nine checkpoints are built, measured at the desk, and never run.** The last launch reported on
was `0.12.67-dev`.

| Checkpoint | Unseen in a game |
|---|---|
| 0.12.68-dev | the braided maze, the raised graph ceiling, **the new packageId** |
| 0.12.69-dev | institutions on a first level, complexes to six rooms, loot in all sixteen archetypes |
| 0.12.70-dev | the assembly as a player-queued bill, and gate control on the components |

**A NEW START IS REQUIRED** — all of the generation work lands on newly generated levels.

### THE TWO NEWEST THINGS, BECAUSE THEY CHANGE HOW THE GATE IS OPERATED

**1. The gate no longer assembles itself.** `BindNativeInfrastructure` used to add an unsuspended
`Bill_Production` to the machining table, so commissioning a door sent crafters off with a hundred
steel immediately. Owner: *"i have no say in the mattter even tho nothing is connected or built
yet"*. The recipe is on the table's own list and **the player queues it.** `SyncAssemblyBill` never
adds a bill; it only suspends one once the gate exists.

**2. A component does its ordinary job or the gate's.** Owner: *"we should have a set to gate
control for these components so other things arnt available and can toggle between normal op and
gate op depending whats wanted"*. Every bound component carries a switch and **begins in normal
operation**. In gate control its company functions are withdrawn and a worktable's other bills are
suspended by load id; in normal operation **the assembly recipe is unavailable and spin-up
refuses**, naming the installation still doing its day job.

**The honest limit, stated here so nobody re-discovers it as a bug:** Core-only, a comms console's
own Core gizmo cannot be removed and a battery cannot be partitioned out of a power net. Gate
control withdraws **our** functions and gates **our** operations. Core's call button stays
pressable.

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for 0.12.70-dev, after the stage")
