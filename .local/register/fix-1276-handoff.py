# -*- coding: utf-8 -*-
"""Correct a false claim in the 0.12.76-dev handoff, caught by the owner before any code ran.

Owner, 2026-10-01: *"are u shure zero goon squad code is written weve gone over this before by a
different name"*.

The handoff said **"Nothing in the battery claims anything about `FacilityRelief`"**. That is
false. `proof-facility-relief.py` is proof FIVE, shipped 0.11.7-dev, and two of its claims
contradict the owner's new direction outright. Had the build followed the handoff it would have
hit two red FAILs and read them as a regression it had just caused.

**The owner's question is the reason this was found.** The repository's own highest-value habit --
*"CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT"*, nine rows saved by it this session --
was stated in this very file and then not applied to the file's own claim.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"""**Nothing in the battery claims anything about `FacilityRelief`** — the same hole that let five
bond defects ship in one feature. A new proof is required, not optional, and it must assert the
squad is **called**, not merely written: four of the five bond defects, and seven defects before
them, were *built, correct, and unreachable*.
"""

NEW = u"""**CORRECTED 2026-10-01, BY THE OWNER, BEFORE A LINE WAS WRITTEN.** This section previously read
*"Nothing in the battery claims anything about `FacilityRelief`"*. **That was false.** The owner
asked *"are u shure zero goon squad code is written weve gone over this before by a different
name"* and the grep that answers it found three things.

**`proof-facility-relief.py` is proof FIVE and it already exists** (0.11.7-dev). Two of its claims
**contradict this direction outright**, so the work is to RE-AIM them, not to add beside them:

| The existing claim | Why it now fails |
|---|---|
| `check("the relief requisitions five roles", len(relief_roles) == 5)` | the owner said **three** |
| `check("the living-staff scan does not treat downed as dead", "Downed" not in living_text)` | the owner said ***"the downed: No Witnesses"*** |

That second claim is the **old reasoning written into the battery as an assertion**, not merely a
stale comment. A build that followed the uncorrected handoff would have hit two red FAILs and read
them as a regression it had just caused.

**And the repair clause already has its instrument.** `ConnectedWork/Providers/UpkeepProviders.cs`
has `RepairableOn(map, faction)` wrapping **Core's own** `map.listerBuildingsRepairable
.RepairableBuildings(faction)` — map-explicit and already proven. **Do not write a second
damaged-building scan;** a second derivation of one rule is the defect this project keeps meeting.

What is genuinely absent, measured rather than assumed: `grep -rn` over `src/` for `goon`,
`GoonSquad`, `ClearSquad`, `CleanupTeam`, `FacilitySweep`, `Grave`, `Sarcophagus`, `Crematorium`,
`Pyre`, `Bury`, `25000000`, `restock` and `pedycash` returns **nothing**. No burial, no cremation,
no confiscation, no deduction.

The claims still have to assert the squad is **called**, not merely written: four of the five bond
defects, and seven defects before them, were *built, correct, and unreachable*.

**The lesson is this file's own rule, applied to this file.** *"CHECK A ROW AGAINST THE CODE
BEFORE BUILDING FOR IT"* — nine rows were saved by it this session, and the handoff asserting a
battery gap had not run the one grep that checks for one.
"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

check = io.open(NOW, encoding="utf-8").read()
if u"Nothing in the battery claims anything about `FacilityRelief`**" in check:
    print("THE FALSE CLAIM IS STILL ASSERTED")
    raise SystemExit(1)
print("handoff corrected: proof FIVE exists, two claims must be re-aimed, repair tool already built")
