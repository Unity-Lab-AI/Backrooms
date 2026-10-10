# -*- coding: utf-8 -*-
"""0.12.58-dev: their effects, at a door's scale."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Their effects, at a door's scale — 2026-09-30 (0.12.58-dev)

Owner, verbatim: **"yeah lets use the fx and visual stuff if we can and make them appropriate
sizes to the sizes of possible doors natural and maching gate types"**

- [x] **"lets use the fx and visual stuff"** — **their event horizon and their iris, on an ordinary door.** The texture paths are **read off their own gate's properties**, so a retextured stargate retextures these too; nothing is copied into this package and no art is shipped.

- [x] **"make them appropriate sizes to the sizes of possible doors"** — **THE RATIO IS THEIRS, MEASURED ACROSS ALL THREE OF THEIR GATES, NOT INVENTED:**

      StargateMod_Stargate          size (5,1)   puddleDrawSize 8.7   = 1.74x
      StargateMod_OrlinStargate     size (3,1)   puddleDrawSize 5.3   = 1.77x
      StargateMod_AdvancedStargate  size (5,1)   puddleDrawSize 7.9   = 1.58x

  So **1.6 sits inside their own band**, and the puddle is read off `def.size` rather than listed per def:

      footprint        width  puddle  vortex cells  iris
      Door                 1    1.60             1  no
      OrnateDoor           2    3.20             2  yes
      SecurityDoor         2    3.20             2  yes
      gate 1x2             2    3.20             2  yes
      gate 1x3             3    4.80             3  yes
      gate 2x3             3    4.80             3  yes

  **Every footprint a gate may use is covered** — Core's 1x1 `Door`, the 2x1 `OrnateDoor`, Anomaly's `SecurityDoor`, and the four shapes a gate run may take — **because the number is computed, not enumerated.** A door this package has never seen is sized correctly the first time it carries a gate.

- [x] **"natural and maching gate types"** — the size comes from the **parent def**, so whichever gate attaches the component gets the right scale without either one knowing about the other.

- [x] **THE VORTEX IS THE PART THAT HAD TO SHRINK, and this is the safety note.** Theirs is **thirteen cells, three wide and four deep** — right for a ring standing in the open, and a demolition charge on a shop's back wall. A door's unstable vortex is now **its own opening, one cell deep, across its own width**: still fatal to stand in, which is the Stargate rule, and still a doorway rather than a crater. An iris is offered only where there is an opening worth covering, which is the same reason their own makeshift gate sets `canHaveIris` false.

- [x] **and not one field of theirs is assigned** — the properties are built by handing **Core's own `DirectXmlToObject.ObjectFromXml`** the same shape of node a def file contains. The game populates its own type through its own machinery, so this package still holds no `SetValue` and no `BindingFlags`. A failure to size **falls back to their properties rather than breaking the gate** — theirs unchanged is a worse look, never a dead route — and the result is cached per def, because a shop has nine doors and a coordinate has dozens.

- [x] **two more of my own claims proved the sizing without requiring it to be used** — nothing asserted that `Attach` passes the sized properties to the component, so a plant swapping them back for the unsized ones passed every numeric claim while a 1x1 door got a seven-by-seven kawoosh; and the vortex-depth claim checked that the right cell is emitted rather than that no others are. **Computing a value correctly and using it are two different facts.** **29 of 29** planted faults caught.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - their effects, at a door's scale (0.12.58-dev)

**Verbatim user quote:** *"yeah lets use the fx and visual stuff if we can and make them
appropriate sizes to the sizes of possible doors natural and maching gate types"*

**Files touched:** `Portals/StargateBridge.cs`, About/csproj/README, `docs/TODO.md`,
`docs/NOW.md`.

**Closure notes.** **Their event horizon and their iris, sized off the door rather than off a
stargate.**

The ratio was measured across all three of their gate defs rather than invented - 8.7/5, 5.3/3
and 7.9/5, so 1.74, 1.77 and 1.58 - and 1.6 sits inside that band. The puddle is read off
`def.size`, so a 1x1 Door gets 1.6, a 2x1 OrnateDoor or SecurityDoor gets 3.2, and a three-wide
door gets 4.8. **Every footprint is covered because the number is computed rather than
enumerated**, including doors this package has never seen.

**The vortex had to shrink and that is the safety note.** Theirs is thirteen cells, three wide and
four deep - correct for a ring standing in the open, a demolition charge on a shop's back wall. A
door's vortex is its own opening, one cell deep, across its own width: still fatal to stand in,
still a doorway. An iris is offered only where there is an opening worth covering, which is why
their own makeshift gate sets canHaveIris false.

**No field of theirs is assigned.** The properties are built by handing Core's own
`DirectXmlToObject.ObjectFromXml` the same node a def file would contain, so the game populates
its own type through its own loader. The texture paths are READ off their gate, so a retexture
follows. A sizing failure falls back to their properties rather than breaking the route, and the
result is cached per def.

**Two more claims of mine proved the sizing without requiring it to be used:** nothing asserted
that `Attach` passes the sized properties on, so a plant restoring the unsized ones satisfied
every numeric claim while a 1x1 door got a seven-by-seven kawoosh. Computing a value correctly and
using it are two different facts, and only one was being proved.

**181 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`521BCBE4EA437ED9A9BD93C5A054B1ADA4179F00A74303F89BADECCDAFCA6DC6`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-five proofs hold. 519 of 519** planted faults caught
across sixteen suites.
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
print("fx rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.57-dev**.", u"| Published | **0.12.58-dev**."),
    (u"SHA-256 `59F77C337E26C59B55355B10E1C7EC7B7EA29A137E529D3B4EA597CDF5C68546`",
     u"SHA-256 `521BCBE4EA437ED9A9BD93C5A054B1ADA4179F00A74303F89BADECCDAFCA6DC6`"),
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
print("NOW.md updated for 0.12.58-dev")
