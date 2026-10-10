# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.73-dev, written after the stage so it quotes a verified hash."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## STATE AT THIS HANDOFF — `0.12.72-dev`, STAGED AND VERIFIED"

NEW = u"""## STATE AT THIS HANDOFF — `0.12.73-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.73-dev  92 files
assembly    C6988A04423FE4A656A15D29EEE97C21BA2D323C842C07EE9A96B81AEF9F57D6
            read back out of the game folder after staging, not from the build
battery     17 checkers - 45 proofs - 659 of 659 plants - 16 suites
tree        no planted fault, porcelain 0
```

### READ THIS BEFORE TOUCHING THE GATE: THE ELEVEN STEPS ARE ON SCREEN NOW

The owner lost an afternoon to a gate that was **already assembled, already calibrated, already
crewed and un-tripped**, blocked by **one switch**: the machining table was in gate control and the
communications console on the same gate was not. `Autosave-5.rws` at 11:38 proved it, and nothing
in the interface could say it.

**Three things hid it, and all three are fixed:**

| | |
|---|---|
| `RR_Gate_CalibrationUnavailable` | said *"not ready for calibration"* for all eight of `CanCalibrate`'s conditions **including `calibrated`**. `CalibrationBlockerKey` names the real one, and `CanCalibrate` **asks** it rather than restating the conditions |
| `RR_Gate_JobUnavailable` | one key for four problems. `StaffConsoleBlockerKey` replaces it in `OrderStaffConsole`; the key still exists for `OrderAssignedJob`, which is what it actually describes |
| the portal panel | drew **no button and no sentence** with no address remembered. It lists every unmet precondition now, naming **which component** is in normal operation |

**`DrawGateStartupChecks` is the headline.** Eleven numbered checks at the top of the Machine tab,
read from live state, each with one sentence naming the thing to click, plus the first unfinished
one called out on its own line. **The order is enforced by proof**: gate control on the **table**
before the assembly, because the recipe is withdrawn from a bench in normal operation; gate control
on the **console** before staffing, because spin-up refuses while either is doing its day job.

### THE FACILITY IS A PLAN NOW, AND IT IS AUTHORED BY A PROGRAM

Thirteen rooms, twenty doors, two of them an airlock, **eleven cells of ballistic glass**, four
support columns, 145 fixture cells. A gate hall that is deliberately empty, a control room behind
the glass, a security airlock of two automatic doors in series, a lab wing, secure storage, a
workshop, a security office, decontamination, an archive.

**Do not hand-edit `RR_AsyncIndustriesStart`'s geometry.** Edit
`.local/register/build-async-facility.py` and re-run it: it derives every door from the wall it
belongs to and checks every footprint against Core's own `<size>` before emitting a line.
`GenStep_Headquarters.Build` **throws** on any geometry mistake and a throw inside a GenStep costs
the player the start.

**The existing battery caught the first authoring twice, and both were real:**

* `proof-startplacement.py` found **121 roofed cells beyond roof support**. An unsupported roof
  collapses on the pawn who deconstructs the wall holding it. The western wing and the gate hall's
  **columns** exist because of that, and `pillars` was added to the start schema for it.
* A claim that refused any two rooms sharing a wall cell was **wrong about its own premise** --
  `GenSpawn.Spawn` never throws on wall-over-wall; `SpawningWipes(Wall, Wall)` replaces it. Third
  time that claim has been wrong. It now asserts what checker sixteen asserts.

### TWO NEW CHECKERS, AND THE BATTERY IS SEVENTEEN

| | |
|---|---|
| `check-start-layout.py` | **SIXTEEN.** Re-validates every authored facility cell by cell from the emitted XML -- doors on walls, glazing on walls and not on doors, footprints on free interiors from **Core's own sizes**, columns on free interiors, conduits in extent. Two readers, and the one that validates did not author |
| `check-plant-anchors.py` | **SEVENTEEN.** Reads all sixteen `PLANTS` tables with `ast` and reports **every** stale anchor at once. This checkpoint paid the one-stale-anchor-per-four-minute-run toll **eight times** before it existed |

**Both cried wolf before they were right** -- 368 legitimate cells for the first, and for the
second `chr(10)` reading as unevaluable plus an entry `plant-def-fields.py` skips itself. That is
five and six in this battery's history of false alarms, and each is written down because a checker
stricter than the thing it guards is its own defect.

### WHAT IS LEFT, HONESTLY, AND IT IS NOT A BUILD QUEUE

Owner scope, 2026-10-01: *"basicly the build items not tests and steam and worklshop stuff.."*.
The 72 raw open rows in `docs/TODO.md` are **not** 72 build items. They are:

| Kind | What unblocks it |
|---|---|
| **launch-gated** -- balance, the 294-profile conflict sweep, the compatibility report, the release tag, screenshots, performance measurement | **an owner launch**, and the owner's standing direction is *"we are not testing again till its all done"*. These cannot close before that |
| **owner-decision** -- the site's domain, the Steam/Workshop Playwright session, a design brief for new starts, the PawnKind save-break | **an owner answer**. Excluded from scope by *"not tests and steam and worklshop stuff"* |
| **buildable** -- staff **prior exposure** on an expedition, the **review** workflow (the fourth of analyse/interview/compare/review), and verifying the stranded-crew rows against `LostPawnRegister` | **nothing. These are next.** |

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for 0.12.73-dev, after the stage")
