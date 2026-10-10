# -*- coding: utf-8 -*-
"""0.12.60-dev: the door was invisible, not missing."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## The door was invisible, not missing — 2026-09-30 (0.12.60-dev)

Owner, verbatim: **"okay , i see the blue glow, i do not see the door, i do not see the portal fx
from stargate, i do see the backrooms map option at the top where pawns appear when they travel
there, clicking on where the door and portal should be only gives \\"go here\\" option like clicking
anywewhere with a pawen does. walking a pawn to the empty spot in the wall where the door used to
be(with the blue aura is there in the opening and surrounding area"** and **"check the game i
paused it see whats up"**

**EVERY LINE BELOW IS READ OUT OF THE OWNER'S PAUSED GAME, NOT INFERRED.**

- [x] **"i do not see the door"** — **THE DOOR WAS NEVER GONE.** Cell (160,161) holds a `Door`, `RimWorld.Building_Door`, Steel, **160 hit points, intact.** It was drawn **fully transparent**.

      private static readonly ColorInt LiveGlowColor = new ColorInt(70, 130, 220, 0);
      glower.GlowColor = LiveGlowColor;              // correct
      colorable.SetColor(LiveGlowColor.ToColor);     // ALPHA ZERO

  `ColorInt.ToColor` divides **every** channel by 255 **including alpha**, so `a: 0` became a fully transparent `Color`, and `Thing.DrawColor` returns whatever `CompColorable` holds. **A glow colour and a draw colour are not the same kind of colour** — alpha zero is the convention for a `ColorInt` glow, and their own stargate def uses `(115,171,224,0)` for exactly that reason. One constant was doing both jobs. There are two now, and the tint is opaque.

- [x] **"clicking ... only gives \\"go here\\" option"** — **THE FLOAT MENU WORKS.** Selecting a colonist in the paused game and right-clicking (160,161) through the live UI returns exactly one option: **"Enter the gate"**. Nothing was wrong with it. **The owner could not click the door because the door was invisible.**

- [x] **"i do not see the portal fx from stargate"** — **their component is attached and healthy, and the gate is simply not active yet.** The door's gizmos include **"Load"**, which is our `CompTransporter`, so `Attach` ran and `Available` was true. Its inspect string reads *"Please respawn this gate (and its accompanying DHD) using devmode, as an update has broken it"* — that is `CompStargate.CompInspectStringExtra`, which is **unconditional**: it is their nag for a gate that is not on `Building_Stargate`, whose own `GetInspectString` calls `sgComp.GetInspectString()` and never lets it run. **Cosmetic noise, not a fault.** Their `PostDraw` only paints an event horizon while `StargateIsActive`, so no puddle means the dial has not succeeded.

- [x] **AND THE REASON THAT TOOK A WHOLE LAUNCH TO NARROW IS MINE.** Every refusal in the dialling path returned **silently** — not available, no component, hibernating, already open, receiving, no far end. That is right for a colony without the Stargate mod and **useless the moment something does not work.** The owner's log contained nothing at all because this code was written to say nothing at all. A live gate that cannot show a wormhole now **names the guard that stopped it, once per door**, at `Log.Message` — information, not a fault.

  **The prime suspect is now reported rather than guessed:** `RimroomsDestinationMapParent.DoorThresholdContentVersion = 4`, and a site below it *"keeps its historical anchor until repaired"* — an anchor that is not a door, which `as ThingWithComps` turns into null, which returned without a word.

- [x] **A PLANT SUITE HAD LEFT A LINE DELETED IN THE SOURCE TREE, AND IT WOULD HAVE SHIPPED.** `git status` showed `RimroomsExpeditionComponent.cs` modified when nothing in this checkpoint touched it: `Campaign.NoteReturnedFromField(run.crew, run.coordinateId);` was **missing**, so no crew member would have had a debrief hold raised on return. A suite was interrupted mid-plant and never restored it. **Found only because the suite that plants it refused to run and the tree was checked.**

- [x] **and `proof-gate-links.py` asserted the exact line that caused the bug** — it required `SetColor(LiveGlowColor.ToColor)`, the invisible-door call. **The second time that same file has held a bug in place by naming it**, after it required `Class="CompProperties_Colorable"` at the seventh launch. **Asserting an exact line proves we wrote it and says nothing about whether it is right.** The claim asserts the property now: the tint must be opaque and must not derive from the glow constant.

- [x] **four more claims of mine were too loose**, including `"not a doorway"` satisfying `"not a door"` — the prefix trap again. **526 of 526** planted faults caught across sixteen suites.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - the door was invisible, not missing (0.12.60-dev)

**Verbatim user quote:** *"i see the blue glow, i do not see the door, i do not see the portal fx
from stargate ... clicking on where the door and portal should be only gives \\"go here\\" option"*
and *"check the game i paused it see whats up"*

**Files touched:** `Portals/CompRimroomsEmergence.cs`, About/csproj/README, `docs/TODO.md`,
`docs/NOW.md`.

**Closure notes.** **Everything here was read out of the paused game.**

The door was never gone: cell (160,161) holds an intact `Building_Door` with 160 hit points. It
was drawn fully transparent, because `ColorInt.ToColor` divides alpha by 255 as well and the glow
constant is `a: 0`. One constant was doing two jobs - a glow colour and a draw colour are not the
same kind of colour, and their own stargate def uses `(115,171,224,0)` for the glow half for
exactly that reason.

**The float menu was never broken.** Selecting a colonist and right-clicking the cell through the
live UI returns exactly one option: *"Enter the gate"*. The owner could not click the door because
the door was invisible.

**Their component is attached and healthy.** The door carries our `CompTransporter` ("Load"), and
its inspect string is their unconditional `CompInspectStringExtra` nag for a gate that is not on
`Building_Stargate` - cosmetic, not a fault. No event horizon means the gate is simply not active,
because their `PostDraw` only paints one while `StargateIsActive`.

**And the reason that took a launch to narrow is mine.** Every refusal in the dialling path
returned silently, so the log held nothing. Correct for a colony without their mod; useless the
moment something does not work. A live gate that cannot show a wormhole now names the guard that
stopped it, once per door, at Log.Message.

**A plant suite had left a line deleted in the source tree and it would have shipped.**
`RimroomsExpeditionComponent.cs` was missing `Campaign.NoteReturnedFromField(...)`, so no crew
member would have had a debrief hold raised on return. A suite was interrupted mid-plant and never
restored it, and it was found only because the suite that plants it refused to run and the tree
was checked.

**And `proof-gate-links.py` asserted the exact line that caused the bug** - the second time that
file has held a defect in place by naming it. Asserting an exact line proves we wrote it and says
nothing about whether it is right.

**181 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`0862FB8D411E16755614AABF316DFFEB7FD1AB2ABF98714235AD0FD050DBD93D`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-five proofs hold. 526 of 526** planted faults caught.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")
io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.59-dev**.", u"| Published | **0.12.60-dev**."),
    (u"SHA-256 `F267F664D0DB8B70E147FC035614F033BA8546BE12983824622089B260F4F1E9`",
     u"SHA-256 `0862FB8D411E16755614AABF316DFFEB7FD1AB2ABF98714235AD0FD050DBD93D`"),
]
for old, _ in EDITS:
    if now.count(old) != 1:
        print("NOW ANCHOR PROBLEM: %d of %r" % (now.count(old), old[:50]))
        raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.60-dev")
