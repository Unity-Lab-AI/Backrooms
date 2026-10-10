# -*- coding: utf-8 -*-
"""The last four misses: three weak plants and one weak claim.

All four are the same arithmetic mistake in different clothes: **the harness replaces the FIRST
occurrence, so a plant on a string that appears twice leaves the second one satisfying the check.**
`MIT` appears twice in the licence, `SWEPT 0.12.42-dev` twice in the queue, `check-dlc-gating.py`
twice in the checker (once in its docstring), and `RECONCILED 0.12.42-dev` fifty-six times.

A plant is only a test if it removes the last thing the claim can see.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-housekeeping.py")
PLANT = os.path.join(REPO, ".local", "register", "plant-housekeeping.py")

PLANT_EDITS = [
    # `MIT` appears twice: the title line and the copyright body. Planted on the title, which is
    # unique, so the whole statement of the licence goes.
    (u"""    ("the licence stops being stated", "Mod/Rimrooms - Async Industries/About/License.txt",
     "MIT", "Proprietary", COMPLIANCE),""",
     u"""    ("the licence stops being stated", "Mod/Rimrooms - Async Industries/About/License.txt",
     "MIT License\\n", "Proprietary License\\n", COMPLIANCE),"""),

    # The delegation line the REPORT prints, distinguished from the same filename in the
    # docstring above it. The claim below now reads the print rather than the mention.
    (u"""    ("the delegation list disappears, so a rule gains a second owner", COMPLIANCE,
     'print("    DLC gating and the five official package ids : check-dlc-gating.py")',
     'pass', PROOF),""",
     u"""    ("the delegation list disappears, so a rule gains a second owner", COMPLIANCE,
     'print("    DLC gating and the five official package ids : check-dlc-gating.py")',
     'print("    DLC gating : owned here too")', PROOF),"""),

    # Fifty-six rows carry the marker, so removing one cannot move a count claim. Planted on the
    # ONE row that row 1054 was written about, and the claim now names it.
    (u"""    ("the reconciliation is no longer recorded row by row", MASTER,
     "RECONCILED 0.12.42-dev", "DONE", PROOF),""",
     u"""    ("THE ROW ROW 1054 WAS WRITTEN ABOUT LOSES ITS RECONCILIATION", MASTER,
     "**RECONCILED 0.12.42-dev: SHIPPED, and this is the row row 1054 was written about.**",
     "Done.", PROOF),"""),

    # Two rows carry the sweep marker. Planted on the distinctive opening of the first, and the
    # claim now counts.
    (u"""    ("the retro sweep is not closed in the queue", QUEUE,
     "**SWEPT 0.12.42-dev", "**SWEPT later", PROOF),""",
     u"""    ("the retro sweep is not closed in the queue", QUEUE,
     "**SWEPT 0.12.42-dev. All twenty-one families are now done",
     "**Still to sweep", PROOF),"""),
]

PROOF_EDITS = [
    (u"""check("no rule has two owners",
      "delegated" in compliance and "check-dlc-gating.py" in compliance
      and "check-register-compliance.py" in compliance,
      "-- a second copy of a rule is a second thing that can disagree with it")""",
     u"""# Matched on the printed line, not on the filename. `check-dlc-gating.py` also appears in
# this checker's own docstring, so a plant that removed the delegation from the REPORT left the
# claim passing on the documentation of it.
check("no rule has two owners",
      "delegated" in compliance
      and 'print("    DLC gating and the five official package ids : check-dlc-gating.py")'
      in compliance
      and 'print("    hard dependencies and loadAfter : check-register-compliance.py")'
      in compliance,
      "-- a second copy of a rule is a second thing that can disagree with it")"""),

    (u"""reconciled = master.count("RECONCILED 0.12.42-dev")
check("the reconciliation is recorded row by row", reconciled >= 50,
      "-- found %d; row 1054 predicted the count understated the build \\"by roughly thirty "
      "points\\"" % reconciled)""",
     u"""reconciled = master.count("RECONCILED 0.12.42-dev")
check("the reconciliation is recorded row by row", reconciled >= 50,
      "-- found %d; row 1054 predicted the count understated the build \\"by roughly thirty "
      "points\\"" % reconciled)

# The one row row 1054 was actually written about -- *"the entire cross-map work engine sits
# under one unchecked row"*. A count claim cannot see this row going missing, so it is named.
check("the row row 1054 was written about is reconciled by name",
      "**RECONCILED 0.12.42-dev: SHIPPED, and this is the row row 1054 was written about.**"
      in master,
      "-- the cross-map work engine, 31 work families, which the row says sat under one "
      "unchecked row")"""),

    (u"""for marker, what in (
        ("**SWEPT 0.12.42-dev", "rows 206 and 302, the retro sweep"),""",
     u"""# Counted where a marker is used twice, because the plant harness replaces the first
# occurrence and a second one left the claim passing.
check("both retro-sweep rows are closed",
      queue.count("**SWEPT 0.12.42-dev") >= 2,
      "-- rows 206 and 302 are one sweep and both carry the marker (found %d)"
      % queue.count("**SWEPT 0.12.42-dev"))

for marker, what in (
        ("**SWEPT 0.12.42-dev. All twenty-one families are now done",
         "rows 206 and 302, the retro sweep"),"""),
]

proof = io.open(PROOF, encoding="utf-8").read()
plant = io.open(PLANT, encoding="utf-8").read()

problems = []
for old, _ in PLANT_EDITS:
    if plant.count(old) != 1:
        problems.append("plant: %d of %r" % (plant.count(old), old[:64]))
for old, _ in PROOF_EDITS:
    if proof.count(old) != 1:
        problems.append("proof: %d of %r" % (proof.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in PLANT_EDITS:
    plant = plant.replace(old, new, 1)
for old, new in PROOF_EDITS:
    proof = proof.replace(old, new, 1)

io.open(PLANT, "w", encoding="utf-8", newline="").write(plant)
io.open(PROOF, "w", encoding="utf-8", newline="").write(proof)
print("four plants and three claims corrected in one write")
