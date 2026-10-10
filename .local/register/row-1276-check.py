# -*- coding: utf-8 -*-
"""The owner's challenge to the handoff, verbatim, and what it found."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = (u"- [~] **\"andf yes do those three things you listed as well\"** - staff **prior "
          u"exposure** on an\n  expedition, the **review** workflow (the fourth of "
          u"analyse/interview/compare/review), and\n  verifying the stranded-crew rows against "
          u"`Company/LostPawnRegister.cs`")

ADDITION = u"""
- [x] **"are u shure zero goon squad code is written weve gone over this before by a different
  name"** - **the owner was right to ask, and the handoff was wrong.** It asserted *"Nothing in
  the battery claims anything about `FacilityRelief`"*. **`proof-facility-relief.py` is proof
  FIVE and has existed since 0.11.7-dev**, and two of its claims contradict this direction
  outright: `len(relief_roles) == 5` against the owner's **three**, and *"the living-staff scan
  does not treat downed as dead"* against ***"the downed: No Witnesses"***. **The old reasoning
  was written into the battery as an assertion**, so the work is to RE-AIM two claims, not add
  beside them - and a build following the uncorrected handoff would have read two red FAILs as a
  regression it had just caused. Also found: `ConnectedWork/Providers/UpkeepProviders.cs` already
  wraps **Core's own** `listerBuildingsRepairable.RepairableBuildings(faction)` as
  `RepairableOn(map, faction)`, so *"fix broken walls and equipment"* needs **no second
  damaged-building scan**. What is genuinely absent was then measured rather than assumed: `goon`,
  `GoonSquad`, `ClearSquad`, `CleanupTeam`, `FacilitySweep`, `Grave`, `Sarcophagus`,
  `Crematorium`, `Pyre`, `Bury`, `25000000`, `restock`, `pedycash` - **zero hits across `src/`**.
  **This is the project's own highest-value habit, which the handoff stated and then failed to
  apply to itself:** *"CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT"*"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    text.replace(ANCHOR, ANCHOR + ADDITION, 1))

if u"are u shure zero goon squad code is written" not in io.open(TODO, encoding="utf-8").read():
    print("ROW NOT WRITTEN")
    raise SystemExit(1)
print("TODO row written verbatim and verified")
