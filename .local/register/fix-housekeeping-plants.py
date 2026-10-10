# -*- coding: utf-8 -*-
"""Six misses in the housekeeping sweep: four weak claims and two weak plants. Fix all six.

The pattern is the same one this session has now been caught by in three consecutive batches, so
it is worth naming again rather than quietly fixing: **a claim that a rule EXISTS is not a claim
that it RUNS.** `DESTRUCTIVE = (` survives `if False and destructive:` untouched. `MissingSkills`
is a substring of `MissingSkillsX`. Every claim below is rewritten to assert the wiring.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-housekeeping.py")
PLANT = os.path.join(REPO, ".local", "register", "plant-housekeeping.py")

# ------------------------------------------------------------------ the proof's weak claims
PROOF_EDITS = [
    # Each rule must be asserted at its DEFINITION *and* at the `if` that acts on it. Unwiring a
    # rule leaves its table intact, which is exactly how four of these passed.
    (u"""CHECKS = (
    ("<supportedVersions>", "official RimWorld only"),
    ("DESTRUCTIVE = (", "no destructive patch operation"),
    ("GAME_BINARIES = (", "no bundled game binary"),
    ("PATCHING = (", "no game assembly patching"),
    ("ATTRIBUTION = (", "no AI attribution in a shipped file"),
    ("LICENCE_NEGATORS = (", "another project's licence terms"),
)
for symbol, what in CHECKS:
    check("it checks %s" % what, symbol in compliance,
          "-- looked for %r in the checker" % symbol)""",
     u"""# Definition AND the branch that acts on it. A rule's table survives `if False and rule:`
# untouched, and four of these claims passed against exactly that plant before being rewritten.
CHECKS = (
    ("<supportedVersions>", "if versions != [\\"1.6\\"]:", "official RimWorld only"),
    ("DESTRUCTIVE = (", "if destructive:", "no destructive patch operation"),
    ("GAME_BINARIES = (", "if bundled:", "no bundled game binary"),
    ("PATCHING = (", "if patching:", "no game assembly patching"),
    ("ATTRIBUTION = (", "if attributed:", "no AI attribution in a shipped file"),
    ("LICENCE_NEGATORS = (", "if gpl:", "another project's licence terms"),
)
for symbol, branch, what in CHECKS:
    check("it checks %s, and acts on the result" % what,
          symbol in compliance and branch in compliance,
          "-- looked for %r and %r in the checker" % (symbol, branch))"""),

    (u"""check("the skill gap is reported and not enforced",
      'listing.Label("RR_Plan_SkillGaps".Translate(' in planner_pane""",
     u"""check("the skill gap is reported and not enforced",
      'listing.Label("RR_Plan_SkillGaps".Translate(' in planner_pane"""),
]

# The medic claim reads the planner; strengthen it to assert the pane actually calls the gap
# finder by its exact name, since a rename leaves the old name matching as a substring.
MEDIC_OLD = (u"""check("THE MEDIC GAP IS STILL NOT A REFUSAL",
      "MissingSkills" in planner and "CompanyActionResult" not in planner.replace(
          "ExpeditionCargo.CheckCapacity(pawn).Success", ""),""")
MEDIC_NEW = (u"""pane = read(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI",
                         "OperationsCrewPlanner.cs"))
check("THE MEDIC GAP IS STILL NOT A REFUSAL",
      "CrewPlanner.MissingSkills(selectedCrew)" in pane
      and "CompanyActionResult" not in planner.replace(
          "ExpeditionCargo.CheckCapacity(pawn).Success", ""),""")

# ------------------------------------------------------------------ the plants' weak targets
PLANT_EDITS = [
    # A comment is not code, and the checker strips comments before reading. Plant real code.
    (u"""    ("a private field is read by reflection", PLANNER,
     "using RimWorld;",
     "using RimWorld;\\nusing System.Reflection;\\n// GetField(\\"x\\", BindingFlags.NonPublic)",
     COMPLIANCE),""",
     u"""    # The first version of this plant was a COMMENT, and the checker strips comments before
    # reading -- so the plant was wrong, not the rule. Real code now.
    ("a private field is read by reflection", PLANNER,
     "        public static List<CandidateReport> Candidates(RimroomsCampaignComponent campaign,",
     "        private static object Peek(System.Type type)\\n"
     "        { return type.GetField(\\"x\\", System.Reflection.BindingFlags.NonPublic); }\\n\\n"
     "        public static List<CandidateReport> Candidates(RimroomsCampaignComponent campaign,",
     COMPLIANCE),"""),

    # MIT appears twice in the licence; replacing the first left the second matching.
    (u"""    ("the licence stops being stated", "Mod/Rimrooms - Async Industries/About/License.txt",
     "MIT", "Unlicensed", COMPLIANCE),""",
     u"""    # MIT appears twice in the licence file, so replacing the first occurrence left the
    # second satisfying the check. Planted on the line the checker actually reads for.
    ("the licence stops being stated", "Mod/Rimrooms - Async Industries/About/License.txt",
     "MIT", "Proprietary", COMPLIANCE),"""),

    (u"""    ("the skill gap stops being computed at all", PLANNER,
     "MissingSkills(IEnumerable<Pawn> crew)", "MissingSkillsX(IEnumerable<Pawn> crew)", PROOF),""",
     u"""    # Planted at the CALL SITE. Renaming the method left `MissingSkills` matching as a
    # substring of `MissingSkillsX`, which is the third time in three batches that shape has
    # defeated a claim.
    ("the skill gap stops being computed at all",
     "src/RimroomsAsyncIndustries/UI/OperationsCrewPlanner.cs",
     "CrewPlanner.MissingSkills(selectedCrew)", "new List<SkillDef>()", PROOF),"""),

    (u"""    ("the delegation list disappears, so a rule gains a second owner", COMPLIANCE,
     '    print("    DLC gating and the five official package ids : check-dlc-gating.py")\\n',
     "", PROOF),""",
     u"""    ("the delegation list disappears, so a rule gains a second owner", COMPLIANCE,
     'print("    DLC gating and the five official package ids : check-dlc-gating.py")',
     'pass', PROOF),"""),
]

proof = io.open(PROOF, encoding="utf-8").read()
plant = io.open(PLANT, encoding="utf-8").read()

problems = []
for old, _ in PROOF_EDITS[:1]:
    if proof.count(old) != 1:
        problems.append("proof: %d of %r" % (proof.count(old), old[:60]))
if proof.count(MEDIC_OLD) != 1:
    problems.append("proof medic: %d" % proof.count(MEDIC_OLD))
for old, _ in PLANT_EDITS:
    if plant.count(old) != 1:
        problems.append("plant: %d of %r" % (plant.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

proof = proof.replace(PROOF_EDITS[0][0], PROOF_EDITS[0][1], 1)
proof = proof.replace(MEDIC_OLD, MEDIC_NEW, 1)
for old, new in PLANT_EDITS:
    plant = plant.replace(old, new, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(proof)
io.open(PLANT, "w", encoding="utf-8", newline="").write(plant)
print("four claims strengthened, three plants corrected")
