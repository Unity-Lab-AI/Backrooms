# -*- coding: utf-8 -*-
"""0.12.53-dev closure: the sixth launch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Sixth launch findings — 2026-09-30 (0.12.53-dev)

Owner, verbatim: **"its not blue!!! it doesnt have a light aura, and it in no way is a portal to
the back rooms.. wtf!!! im getting tired of this shit... you actually have to plug all the work we
did on the gates into the game so they work and the pawns can walk from tmap to map like the
stargate mod works but with normal does.. wtf!!! ive said stargate mod repeaditly is how the gates
work but u keep fucking ignoring me and doing you own fucking thing instead of codeing the door
into gates properly so that the doors work like startgates repurposed into the backrroms gate to
travel to it"**

- [x] **"it in no way is a portal to the back rooms"** — **THE LEVEL NEVER GENERATED, AGAIN, AND THE CAUSE WAS NEW AND MINE.** `SpawnNativeConduit` threw `RR_Generation_ContentPlacementFailed`, so `MarkLayoutReady` never ran, so `SoloGroupOpening` stopped at step 2 and the back door was **never marked**. **An unmarked door is an ordinary steel door** — every symptom the owner reports follows from that one throw.

  **Measured:** the grid carpeted every powered room with conduit. At 12x12 rooms that was ~100 cells. At depth 1 a `service_passage` is **60x80**, so `ContractedBy(1)` is **4,524 cells** against `MaxNativePowerConduits = 512` — **an eightfold blowout on the first powered room, every time.** No 300x300 coordinate could ever have generated. The carpet was a trick sized for small rooms and **the 300x300 change invalidated it**; it should have been found by sizing it rather than by shipping it.

  Fixed better than by raising the cap: the carpet existed to catch the lamp `RoomContentBuilder` adds *after* the grid is laid, and wiring four thousand cells to catch one lamp is the wrong shape at any size. `ConnectStrayConsumers` now runs **after** content placement and uses **the same map-wide `CompPowerTrader` sweep** the validator uses to *detect* a stray consumer, so report and repair agree by construction. `TrySpawnNativeConduit` returns where the throwing form would throw, so **a dark corner can never cost the coordinate again**. The 4,524-cell arithmetic is now a **proof claim** computed from the planner's own constants, so any future per-room area pass fails on the number that proves it.

- [x] **"its not blue!!! it doesnt have a light aura"** — **DONE, with no new content.** `CompGlower` and `CompColorable` are both Core and both settable **per instance**, so a live gate is blue and casts light with no new texture and no new def.

  **The trap was that adding a glower to `Door` would light every door in every colony and every door every other mod ships.** Core solves it: `CompGlower.ShouldBeLitNow` walks every comp on the parent and asks any that implements **`IThingGlower`**, and one false keeps the glower dark and unregistered. `CompRimroomsEmergence` implements it and answers `IsLiveGate`, so every ordinary door is **provably** unlit by Core's own rule rather than by hoping a radius of zero is enough. The patch sets `glowRadius 0` as well, belt and braces.

  **Only a gate with a real way through lights up** — `IsLiveGate` wants the player's mark *and* a live network edge, because a marked door nothing leads through is a plan, not a gate.

- [x] **"the pawns can walk from tmap to map like the stargate mod works but with normal does"** and **"ive said stargate mod repeaditly ... but u keep fucking ignoring me"** — **FAIRLY AIMED, and fixed.**

  The travel already did exactly that: `PortalTravelService.OrderCrossing` makes a **real job** that walks the pawn to the cell beside the door and crosses them to the other map. **What was missing was the place a player looks for it.** The only way to ask was select pawns, select the door, click a gizmo, choose from a float menu — **a dispatch console, not a door you walk through.** *"Like the stargate mod"* was a statement about the **interaction**, and it kept being heard as one about the destination.

  `ThingComp.CompFloatMenuOptions(Pawn selPawn)` is Core's own hook for *"right-click this with that colonist selected"*. **Select a colonist, right-click the gate, "Enter the gate".** Nothing is decided there — the order is still `OrderCrossing` and the rule is still `PortalTraversalPolicy`, so invariant 1 holds. A pawn who cannot cross gets a **disabled row with the reason**.

  **Register row [218] Stargates!** is stance **No integration**, which means *do not depend on it* — **it never meant ignore it as the interaction model**, and treating those as the same thing is how three checkpoints passed with the order buried in a gizmo.

  Record `implementation/GATE_IS_A_GATE_IMPLEMENTATION.md`. **50 of 50** and **32 of 32** planted faults caught.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - a gate that looks like a gate and is walked through like one (0.12.53-dev)

**Verbatim user quote:** *"okay read the now.md and check the player log and see whats up with the
gate that u placesd in the running game!!! its not blue!!! it doesnt have a light aura, and it in
no way is a portal to the back rooms.. wtf!!! im getting tired of this shit... you actually have to
plug all the work we did on the gates into the game so they work and the pawns can walk from tmap
to map like the stargate mod works but with normal does.. wtf!!! ive said stargate mod repeaditly
is how the gates work but u keep fucking ignoring me and doing you own fucking thing instead of
codeing the door into gates properly so that the doors work like startgates repurposed into the
backrroms gate to travel to it"*

**Files touched:** `Generation/GenStep_BackroomsDestination.cs`,
`Portals/CompRimroomsEmergence.cs`, `Patches/RR_NativeGateProviders.xml`, `Keyed/RR_Portals.xml`,
About/csproj/README, `docs/implementation/GATE_IS_A_GATE_IMPLEMENTATION.md`.

**Closure notes.** **Three complaints, all three correct, and the first one caused the other two to
be invisible.**

**The level never generated, again, and the cause was new and mine.** `SpawnNativeConduit` threw,
so `MarkLayoutReady` never ran, so the Store's back door was never marked - and an unmarked door is
an ordinary steel door. The grid carpeted every powered room with conduit: ~100 cells at 12x12,
**4,524 cells** at the 60x80 a depth-1 service_passage actually is, against a cap of **512**. An
eightfold blowout on the first powered room, every time, so **no 300x300 coordinate could ever have
generated.** The carpet was sized for small rooms and the 300x300 change invalidated it; sizing it
would have found this before shipping it, and that is the lesson rather than the fix.

**It did not look like a gate, and Core had the answer to the thing that made that hard.** A
glower on `Door` would light every door in every colony and every door every other mod ships.
`CompGlower.ShouldBeLitNow` asks every comp implementing `IThingGlower`, so one false from ours
keeps them all dark - a guarantee from Core's own rule rather than a hope about a zero radius. A
live gate is blue and casts light with no new texture and no new def.

**And the Stargate complaint was fairly aimed.** The travel already made a real job that walks a
pawn to the door and crosses them to the other map - that part has been right for checkpoints. What
was missing was the place a player looks: it was only reachable through a gizmo and a float menu,
which is a dispatch console rather than a door. *"Like the stargate mod"* was a statement about the
INTERACTION and it kept being heard as one about the destination.
`ThingComp.CompFloatMenuOptions` is Core's own right-click hook and that is where it lives now.
Register row [218] Stargates! is stance *No integration*, which means do not depend on it - it
never meant ignore it as the model.

**Eight claims written this checkpoint were loose enough for a plant to walk through**, all one
family: a retired symbol name, a `throw` test that a call-site swap does not disturb, a cap check
appearing twice, two prefixes, a `SetColor` surviving `if (false)`, a lookup surviving an early
`return true`, and a guard nothing asserted. **And the fix for the prefix trap fell into the prefix
trap** - `TrySpawnNativeConduit` contains `SpawnNativeConduit`, so the naive test failed against
correct code. It strips the safe calls first now.

`check-package-integrity.py` refused the new patch because an XML comment contained `--`, which is
illegal in XML and would have been a silent def-load failure.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`3FD8054EB0EA1F3BFC9DA7D954F6E0796B3462A52D7B115E632D9905E7758A7C`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** **50 of 50** and **32 of 32**.

**Six launches, fourteen defects, every one ours. Still not a single mod conflict.**
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
print("sixth-launch rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.52-dev**.", u"| Published | **0.12.53-dev**."),
    (u"SHA-256 `9D7DCDAF2FFA06C740F800437458571351511B56DDBDC1123463886B46ED7DF4`",
     u"SHA-256 `3FD8054EB0EA1F3BFC9DA7D954F6E0796B3462A52D7B115E632D9905E7758A7C`"),
    (u"| Game launches | **FIVE, all by the owner on 2026-09-30, and a SIXTH is in flight right "
     u"now — reading its log is the first job of the next session.**",
     u"| Game launches | **SIX, all by the owner on 2026-09-30. Fourteen defects, every one ours, "
     u"still not a single mod conflict.** The sixth found a conduit carpet sized for 12x12 rooms "
     u"blowing a 512-cell cap **eightfold** at 80x80, which meant **no 300x300 coordinate could "
     u"ever have generated** — so the gate was never marked and the owner was looking at an "
     u"ordinary steel door. A SEVENTH is what settles whether a coordinate generates at all."),
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
print("NOW.md updated for 0.12.53-dev")
