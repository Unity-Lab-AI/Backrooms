# -*- coding: utf-8 -*-
"""Plant a fault, run the check, require failure, restore. Verified writes.

Every target is run clean before anything is planted.

Three targets, because this batch ships two checkers and a generator:

  * `proof-housekeeping.py` -- the sweep's rules, the compliance checker's shape, the workbook's
    tracked source, the master reconciliation's two LAWs
  * `tools/check-compliance.py` -- planted with a REAL destructive patch operation, a REAL
    reflection write and REAL AI attribution in a REAL shipped file
  * `tools/check-register-compliance.py` -- planted with a REAL patch naming each steered def type
"""
import io
import os
import subprocess
import sys
import time

REPO_TOOLS = "tools"
COMPLIANCE = REPO_TOOLS + "/check-compliance.py"
REGISTER = REPO_TOOLS + "/check-register-compliance.py"
EXTRACTOR = REPO_TOOLS + "/extract-economy-workbook.py"
SOURCE = "docs/research/campaign-economy-workbook.json"
HTML = "outputs/readable/campaign-economy.html"
README = "outputs/rimrooms-async-industries-register-2026-09-27/README.md"
MASTER = "docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md"
DOC = "docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md"
QUEUE = "docs/TODO.md"
PLANNER = "src/RimroomsAsyncIndustries/Expedition/CrewPlanner.cs"
PATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_GlowPodMarker.xml"
ABOUT = "Mod/Rimrooms - Async Industries/About/About.xml"
PROOF = ".local/register/proof-housekeeping.py"

PLANTS = [
    # ---------------------------------------------- the register sweep's rules, in the checker
    ("A PATCH STARTS NAMING A ThoughtDef", PATCH,
     "<Patch>", "<Patch>\n  <!-- ThoughtDef -->", REGISTER),

    ("a patch starts naming a TraderKindDef", PATCH,
     "<Patch>", "<Patch>\n  <!-- TraderKindDef -->", REGISTER),

    ("a patch starts naming a HediffDef", PATCH,
     "<Patch>", "<Patch>\n  <!-- HediffDef -->", REGISTER),

    ("a patch starts naming a MainButtonDef", PATCH,
     "<Patch>", "<Patch>\n  <!-- MainButtonDef -->", REGISTER),

    ("A PATCH STARTS ALTERING ANOTHER DEF'S STAT BASES", PATCH,
     "<Patch>", "<Patch>\n  <!-- <Mass>5</Mass> -->", REGISTER),

    ("the ThoughtDef rule loses its register citation", REGISTER,
     '"ThoughtDef": "row 2 SF Grim Reality', '"ThoughtDef": "because it is tidier', PROOF),

    ("the stat-base rule is unwired", REGISTER,
     "if mass_patches:", "if False and mass_patches:", PROOF),

    ("THE MEDIC GAP BECOMES A REFUSAL", PLANNER,
     "        public static List<SkillDef> MissingSkills(IEnumerable<Pawn> crew)",
     "        public static Company.CompanyActionResult Veto() "
     "{ return Company.CompanyActionResult.Refused(\"RR_Plan_Dead\"); }\n\n"
     "        public static List<SkillDef> MissingSkills(IEnumerable<Pawn> crew)", PROOF),

    # Planted at the CALL SITE. Renaming the method left `MissingSkills` matching as a
    # substring of `MissingSkillsX`, which is the third time in three batches that shape has
    # defeated a claim.
    ("the skill gap stops being computed at all",
     "src/RimroomsAsyncIndustries/UI/OperationsCrewPlanner.cs",
     "CrewPlanner.MissingSkills(selectedCrew)", "new List<SkillDef>()", PROOF),

    # ---------------------------------------------- the compliance checker, planted with reality
    ("ROW 1287: A DESTRUCTIVE PATCH OPERATION ENTERS THE PACKAGE", PATCH,
     '<Operation Class="PatchOperationConditional"',
     '<Operation Class="PatchOperationReplace"', COMPLIANCE),

    ("ROW 1290: the package claims a version it does not target", ABOUT,
     "<li>1.6</li>", "<li>1.6</li><li>1.5</li>", COMPLIANCE),

    ("ROW 1288: A REFLECTION WRITE ENTERS THE SOURCE", PLANNER,
     "        public static CandidateReport Assess(RimroomsCampaignComponent campaign,",
     "        private static void Poke(System.Reflection.FieldInfo field, object target)\n"
     "        { field.SetValue(target, null); }\n\n"
     "        public static CandidateReport Assess(RimroomsCampaignComponent campaign,",
     COMPLIANCE),

    ("Harmony enters the source", PLANNER,
     "using RimWorld;", "using RimWorld;\nusing HarmonyLib;", COMPLIANCE),

    # The first version of this plant was a COMMENT, and the checker strips comments before
    # reading -- so the plant was wrong, not the rule. Real code now.
    ("a private field is read by reflection", PLANNER,
     "        public static List<CandidateReport> Candidates(RimroomsCampaignComponent campaign,",
     "        private static object Peek(System.Type type)\n"
     "        { return type.GetField(\"x\", System.Reflection.BindingFlags.NonPublic); }\n\n"
     "        public static List<CandidateReport> Candidates(RimroomsCampaignComponent campaign,",
     COMPLIANCE),

    ("AI ATTRIBUTION LANDS IN A SHIPPED FILE", ABOUT,
     "<author>", "<author>Co-Authored-By: Claude ", COMPLIANCE),

    # MIT appears twice in the licence file, so replacing the first occurrence left the
    # second satisfying the check. Planted on the line the checker actually reads for.
    ("the licence stops being stated", "Mod/Rimrooms - Async Industries/About/License.txt",
     "MIT License\n", "Proprietary License\n", COMPLIANCE),

    ("the destructive-operation check is unwired", COMPLIANCE,
     "if destructive:", "if False and destructive:", PROOF),

    ("the attribution check is unwired", COMPLIANCE,
     "if attributed:", "if False and attributed:", PROOF),

    ("the reflection check is unwired", COMPLIANCE,
     "if patching:", "if False and patching:", PROOF),

    ("THE LICENCE CHECK GOES BACK TO TESTING MENTION", COMPLIANCE,
     "        if any(negator in sentence for negator in LICENCE_NEGATORS):\n"
     "            continue\n", "", COMPLIANCE),

    ("ZERO PARSED REFERENCES GOES BACK TO PASSING", COMPLIANCE,
     '            fail("the reference manifest %s parsed to zero assemblies. A build that '
     'references "', '            notes.append("no references. %s" % "'.replace('"', '"'),
     PROOF),

    ("a blinded check starts passing instead of skipping", COMPLIANCE,
     "    sys.exit(2)", "    sys.exit(0)", PROOF),

    ("the delegation list disappears, so a rule gains a second owner", COMPLIANCE,
     'print("    DLC gating and the five official package ids : check-dlc-gating.py")',
     'print("    DLC gating : owned here too")', PROOF),

    ("the compliance document goes back to being dated", DOC,
     "## Verified position — re-run every checkpoint by `tools/check-compliance.py`",
     "## Verified position at 0.5.6-dev", PROOF),

    ("the document stops admitting its rows were stale", DOC,
     "this row's old text was stale", "this row reads", PROOF),

    # ---------------------------------------------- the workbook
    ("THE TRACKED SOURCE DRIFTS FROM THE WORKBOOK", SOURCE,
     '"note":', '"drifted": true, "note":', PROOF),

    ("the source stops saying the figures are unverified", SOURCE,
     "Not verified against the build", "Verified against the build", PROOF),

    ("the HTML stops saying the figures are transcribed", HTML,
     "transcribed, not verified", "authoritative", PROOF),

    ("the HTML stops saying no game has been launched", HTML,
     "has ever been launched", "will be launched", PROOF),

    ("the HTML starts authoring its own colour", HTML,
     "border:1px solid currentColor", "border:1px solid #333;color:#111", PROOF),

    ("shared strings stop being resolved", EXTRACTOR,
     'if kind == "s" and value_node is not None:', "if False:", PROOF),

    ("sheet order goes back to filename order", EXTRACTOR,
     'rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))',
     "rels = []", PROOF),

    # ---------------------------------------------- the superseded PNGs
    ("the note beside the superseded images stops naming the authority", README,
     "The HTML is the register", "The images are old", PROOF),

    ("the note stops saying nothing was deleted", README,
     "Nothing in this folder has been removed", "Some files were tidied", PROOF),

    # ---------------------------------------------- the master reconciliation's two LAWs
    ("A RUNTIME-ACCEPTANCE ROW GETS MARKED DONE", MASTER,
     "- [ ] Runtime regression acceptance for these increments",
     "- [x] Runtime regression acceptance for these increments — **RECONCILED 0.12.42-dev: "
     "SHIPPED.**", PROOF),

    ("a reconciled row loses its original words", MASTER,
     "  - [x] Implement and integrate native work/needs adapters, physical ingredient logistics "
     "and per-provider coverage without separate mandatory labor/material pools. — "
     "**RECONCILED 0.12.42-dev",
     "  - [x] Adapters. — **RECONCILED 0.12.42-dev", PROOF),

    ("THE ROW ROW 1054 WAS WRITTEN ABOUT LOSES ITS RECONCILIATION", MASTER,
     "**RECONCILED 0.12.42-dev: SHIPPED, and this is the row row 1054 was written about.**",
     "Done.", PROOF),

    # ---------------------------------------------- the queue closures
    ("the retro sweep is not closed in the queue", QUEUE,
     "**SWEPT 0.12.42-dev. All twenty-one families are now done",
     "**Still to sweep", PROOF),

    ("the master reconciliation is not closed in the queue", QUEUE,
     "**RECONCILED 0.12.42-dev, and the row underestimated",
     "**RECONCILED later, and the row underestimated", PROOF),

    ("the workbook generator is not closed in the queue", QUEUE,
     "**BUILT 0.12.42-dev as `tools/extract-economy-workbook.py`",
     "**BUILT later as `tools/extract-economy-workbook.py`", PROOF),

    ("the compliance checker is not closed in the queue", QUEUE,
     "**BUILT 0.12.42-dev as `tools/check-compliance.py`",
     "**BUILT later as `tools/check-compliance.py`", PROOF),
]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- each target must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
