# -*- coding: utf-8 -*-
"""0.12.54-dev: the scale sweep, done once instead of one bug per launch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## The scale sweep — 2026-09-30 (0.12.54-dev)

Owner, verbatim: **"what the fuck do you mean its a design instruction??? its suppose to be built
and working 100% we finished the build yesterday!"**

- [x] **"its a design instruction" was the wrong phrase and it was mine** — the Stargate behaviour **is built and shipped**: right-click a live gate with a colonist selected, *"Enter the gate"*, and `CompFloatMenuOptions` plus `RR_DoorCross_Enter` are both verified present in the staged assembly. What went into NOW.md was the **lesson** so the next session does not repeat the misreading, and calling that "a design instruction" read as though the work were filed for later rather than done. **It is done.**

- [x] **"its suppose to be built and working 100%"** — **the build is complete; what kept failing was runtime, and the right response was to stop finding it one launch at a time.** Every constant in the generation path was listed and sized against a 300x300 map, 80-cell rooms and 42 rooms. **Two more would have killed a coordinate.**

  **Modelled rather than guessed.** `FindConduitRoute` BFSes from the whole wired set, so routes share a spine and the total is far below the sum of the distances:

      depth  rooms  consumers  conduit cells needed   against the old cap of 512
        1      6        7            460              under, by forty cells
        2     10       11            625              THROWS
        3     16       17            828              THROWS
        4     24       25          1,061              THROWS
        5     32       33          1,211              THROWS
        6     42       43          1,436              THROWS

  **So the seventh launch would probably have generated level 0 and killed every level below it** — the worst failure mode there is, because it looks fixed.

  Two fixes, both the principle the power validation already followed, *a dark corner beats no coordinate*: the cap is **4,000**, sized with 2.5x headroom at double the consumers, and **exceeding it stops the wiring instead of throwing**; and a consumer the routing cannot reach is **skipped**, where `FindConduitRoute` threw twice.

  **The sizing is a proof claim now**, computed from the planner's own constants rather than written down, so the cap cannot silently stop fitting again — and it checks the cap is not absurdly oversized either, because a cap that can never bind is not a cap.

- [x] **checked and fine, so the sweep is on record rather than implied** — `MaxInitialFuelStacks` (generator capacity, independent of map size), containment's `CellsPerSweep`/`Interval` (a rotating window; `ReroofWholeMap` does the real work on load), `ConstructionEcho`'s `WindowCells`/`Capacity` (windowed), `FacilityPlanner`'s 2-to-4 room groups at 45% eligibility (scales), `RoomArchetypeService.MaxFixtureSide` (fixture size, not map size), `RevisitDisplacement.MaxMoved`, `WorldTileCandidateBudget` (world tiles, unrelated).

- [x] **an operational mistake worth recording** — a proof was run **while a plant suite was still executing in the background**, so it read a planted fault and reported a failure that did not exist. **Never read the tree during a plant run.**

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - the scale sweep (0.12.54-dev)

**Verbatim user quote:** *"what the fuck do you mean its a design instruction??? its suppose to be
built and working 100% we finished the build yesterday!"*

**Files touched:** `Generation/GenStep_BackroomsDestination.cs`, About/csproj/README, `docs/TODO.md`,
`docs/NOW.md`.

**Closure notes.** **Two corrections, one of wording and one of method.**

*"Design instruction"* was the wrong phrase and it was mine. The Stargate behaviour **is built and
shipped** - right-click a live gate, *"Enter the gate"*, with `CompFloatMenuOptions` and
`RR_DoorCross_Enter` both verified in the staged assembly. What went into NOW.md was the LESSON, so
the next session does not repeat the misreading, and describing that as a design instruction read as
though the work were filed for later. It is done.

**The method correction is the substance.** The build is complete; runtime kept failing, and two
launches in a row had been spent discovering one scale bug at a time. So every constant in the
generation path was listed and sized against a 300x300 map, 80-cell rooms and 42 rooms - and **two
more would have killed a coordinate.**

**Modelled, not guessed.** `FindConduitRoute` BFSes from the whole wired set, so routes share a
spine: 460 cells at depth 1, rising to 1,436 at depth 6, against a cap of **512**. Depth 1 fitted
under it **by forty cells**, so the seventh launch would probably have generated level 0 and killed
every level below it - the worst failure mode there is, because it looks fixed.

Fixed on the principle the power validation already followed, *a dark corner beats no coordinate*:
the cap is 4,000 with 2.5x headroom at double the consumers, exceeding it stops the wiring rather
than throwing, and a consumer the routing cannot reach is skipped where `FindConduitRoute` threw
twice. **The sizing is a proof claim computed from the planner's own constants**, so it cannot
silently stop fitting again, and it also refuses a cap so large it could never bind.

**Seven constants were checked and are fine**, and that is on record rather than implied:
`MaxInitialFuelStacks`, containment's sweep window, `ConstructionEcho`'s window and capacity,
`FacilityPlanner`'s group sizing, `MaxFixtureSide`, `RevisitDisplacement.MaxMoved` and
`WorldTileCandidateBudget`.

**An operational mistake worth recording:** a proof was run while a plant suite was still executing
in the background, so it read a planted fault and reported a failure that did not exist. Never read
the tree during a plant run.

**Two more duplicate-string anchors** had to be disambiguated, both because a new line made an old
plant anchor match twice - the harness refused to run rather than mis-score, which is it working.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`1FA1CEE1987B5FF32042F6DBA8D4ED279F76843B59A9881C331CE0F174EBF39C`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** **56 of 56** planted faults caught.
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
print("scale-sweep rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.53-dev**.", u"| Published | **0.12.54-dev**."),
    (u"SHA-256 `3FD8054EB0EA1F3BFC9DA7D954F6E0796B3462A52D7B115E632D9905E7758A7C`",
     u"SHA-256 `1FA1CEE1987B5FF32042F6DBA8D4ED279F76843B59A9881C331CE0F174EBF39C`"),
    (u"""**THE LESSON, AND IT HAS NOW COST TWO LAUNCHES IN A ROW.** Both the light count at 0.12.48-dev and
this conduit carpet were **assumptions about scale that a constant quietly encoded**, and both
survived every proof because a proof reads source text and cannot see that a number no longer
fits. **When a dimension changes, go and size everything that was written against the old one.**
The 4,524 figure is a proof claim now, computed from the planner's own constants, so any future
per-room area pass fails on the number that proves it.""",
     u"""**THE LESSON, AND IT HAD ALREADY COST TWO LAUNCHES.** Both the light count at 0.12.48-dev and
this conduit carpet were **assumptions about scale that a constant quietly encoded**, and both
survived every proof because a proof reads source text and cannot see that a number no longer
fits. **When a dimension changes, go and size everything that was written against the old one.**

**0.12.54-dev did exactly that, once, instead of one bug per launch** — and found **two more that
would have killed a coordinate.** `FindConduitRoute` threw twice when a consumer could not be
reached, and `MaxNativePowerConduits = 512` was sized for 60x60: modelled against what the routing
actually does, a coordinate needs **460 cells at depth 1 rising to 1,436 at depth 6**. Depth 1
fitted under 512 **by forty cells**, so the seventh launch would probably have generated level 0
and killed every level below it — **the worst failure mode there is, because it looks fixed.**

The cap is 4,000 with 2.5x headroom at double the consumers, exceeding it stops the wiring instead
of throwing, and an unreachable consumer is skipped. **The sizing is a proof claim computed from
the planner's own constants**, so it cannot silently stop fitting again — and it refuses a cap so
large it could never bind, because that is not a cap. Seven other constants were sized and are
fine, recorded in `docs/TODO.md` rather than left implied."""),
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
print("NOW.md updated for 0.12.54-dev")
