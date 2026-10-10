# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.53-dev, written for a compaction.

Anchors asserted first, one write at the end.

Measured rather than carried:

    branch       feature/bug-testing   (TEN refs)
    published    a432825  0.12.53-dev
    C# files     200
    package       91
    checkers      13
    proofs        41   (+ 13 plant suites, both tracked in git)
    assembly     3FD8054E...58A7C
    launches     SIX, fourteen defects, all ours, no mod conflicts
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

OLD_FIRST = u"""## DO THIS FIRST — READ THE LOG FROM THE SIXTH LAUNCH

**The owner is testing 0.12.52-dev right now and asked for exactly this:** *"you can check the
player.log on the other side of the compact to see if it works and our gates are working"*."""

NEW_FIRST = u"""## DO THIS FIRST — READ THE LOG FROM THE SEVENTH LAUNCH

**The owner is testing 0.12.53-dev. Read the log before anything else**, and read it before
telling them anything works."""

OLD_SETTLE = u"""### What the sixth launch should settle, in order

1. **does a coordinate generate at all** — the whole generator is unrun
2. **is the back-room door a natural gate** rather than a steel door
3. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything matching
4. **one level in, the materials go wild** — two tables in one room in different stuffs, each room's
   walls a different material. This is the newest thing and the least like anything that has run
5. **no cave-in** when a wall or a pillar is deconstructed
6. **Operations → Places** lists the colony and any level, with the budget as `n/5`"""

NEW_SETTLE = u"""### WHAT THE SIXTH LAUNCH FOUND, AND WHY IT IS THE SAME SHAPE TWICE

**The level never generated. Again. The cause was new and it was ours.**

```
[Rimrooms][Generation] Site layout stopped: RR_Generation_ContentPlacementFailed
  at GenStep_BackroomsDestination.SpawnNativeConduit
  at GenStep_BackroomsDestination.SpawnNativePowerNetwork
```

`MarkLayoutReady` never ran → `SoloGroupOpening` stopped at step 2 → the Store's back door was
**never marked**. **An unmarked door is an ordinary steel door**, which is the whole of what the
owner saw: *"its not blue!!! it doesnt have a light aura, and it in no way is a portal"*.

**The cause, measured:** the power grid carpeted every powered room with conduit. ~100 cells at
12x12 rooms. At depth 1 a `service_passage` is **60x80**, so `ContractedBy(1)` is **4,524 cells**
against `MaxNativePowerConduits = 512` — **an eightfold blowout on the first powered room, every
time.** No 300x300 coordinate could ever have generated.

**THE LESSON, AND IT HAS NOW COST TWO LAUNCHES IN A ROW.** Both the light count at 0.12.48-dev and
this conduit carpet were **assumptions about scale that a constant quietly encoded**, and both
survived every proof because a proof reads source text and cannot see that a number no longer
fits. **When a dimension changes, go and size everything that was written against the old one.**
The 4,524 figure is a proof claim now, computed from the planner's own constants, so any future
per-room area pass fails on the number that proves it.

### What the SEVENTH launch has to settle, in this order

1. **DOES A COORDINATE GENERATE AT ALL.** Third attempt. Everything below depends on it, and the
   generator has still never run end to end.
2. **is the back-room door blue and glowing** once a level exists
3. **select a colonist, right-click the gate → "Enter the gate"** — they should walk over and come
   out on the other map
4. **every other door in the colony is unlit and unchanged** — the `IThingGlower` veto
5. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything matching
6. **one level in, the materials go wild** — two tables in one room in different stuffs, each
   room's walls a different material. Newest thing in the build, least like anything that has run
7. **no cave-in** when a wall or a pillar is deconstructed
8. **Operations → Places** lists the colony and any level, with the budget as `n/5`

### The three things the sixth launch changed, and how to check each

| | |
|---|---|
| **it generates** | the carpet is gone. `ConnectStrayConsumers` wires whatever the dressing added, **after** it exists, using the same `CompPowerTrader` sweep the validator uses to detect a stray — so report and repair cannot disagree. `TrySpawnNativeConduit` returns where the throwing form threw: a dark corner can never cost the coordinate again |
| **it looks like a gate** | `CompGlower` + `CompColorable`, both Core, both settable per instance — blue and casting light with **no new texture and no new def**. **The trap was that a glower on `Door` lights every door in the game**; Core's `IThingGlower` lets our comp veto it, so every ordinary door is provably dark by Core's own rule. Only a gate with a **real network edge** lights up |
| **you walk through it** | the travel job always did this correctly. **What was missing was where a player looks for it** — it was a gizmo plus a float menu, which is a dispatch console rather than a door. `CompFloatMenuOptions` is Core's right-click hook and that is where it lives now. The order is still `OrderCrossing`, the rule is still `PortalTraversalPolicy` |

### AND THE STARGATE COMPLAINT WAS FAIRLY AIMED — read this before designing anything else

Owner, after saying it repeatedly: *"ive said stargate mod repeaditly is how the gates work but u
keep fucking ignoring me and doing you own fucking thing"*.

**They were right, and the specific failure is worth naming so it is not repeated.** *"Like the
stargate mod"* was a statement about the **interaction** — you walk a pawn into a door and they
come out on another map — and it was repeatedly heard as a statement about the **destination**,
which the build already handled. The travel was correct for checkpoints; the way to ask for it was
buried where no RimWorld player would look.

**Register row [218] Stargates! is stance "No integration".** That means *do not depend on it or
adapt to it*. **It has never meant ignore it as the interaction model**, and treating those as the
same thing is how three checkpoints passed with the order in a gizmo. When the owner names a mod
as how something should *feel*, read it."""

OLD_TRAP_HEAD = u"### THE TRAP THAT NOW OUTRANKS EVERY OTHER ONE"

NEW_TRAP_HEAD = u"""### THE TRAP THAT NOW OUTRANKS EVERY OTHER ONE

**0.12.53-dev added eight more, bringing it to twenty, and one of them is the lesson in miniature:
the fix written to close the prefix trap fell into the prefix trap.** Asserting
`"SpawnNativeConduit(…" not in body` fails against **correct** code, because
`TrySpawnNativeConduit` *contains* `SpawnNativeConduit`. It strips the safe calls first now.

The eight from this checkpoint, on top of the twelve below: a **retired symbol name** (so a
re-carpet under a new name walked past); a `"throw" not in body` test that a **call-site swap** does
not disturb; a cap check appearing **twice**; **two prefixes** (`CompProperties_Glower` inside
`…GlowerUnused`, same for Colorable); a `SetColor` surviving being wrapped in **`if (false)`**; a
lookup whose later use survived an early **`return true`**; and a guard **nothing asserted at
all**."""

EDITS = [(OLD_FIRST, NEW_FIRST), (OLD_SETTLE, NEW_SETTLE), (OLD_TRAP_HEAD, NEW_TRAP_HEAD)]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("NOW.md: %d edits applied in one write" % len(EDITS))
