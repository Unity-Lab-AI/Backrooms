# -*- coding: utf-8 -*-
"""Three claims in proof-housekeeping.py were wrong about their own subject. Fix all three."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, ".local", "register", "proof-housekeeping.py")

original = io.open(PATH, encoding="utf-8").read()

EDITS = [
    # 1. The planner's own doc comment says "there is no CompanyActionResult anywhere in it",
    #    which is the sentence the claim wants -- and it made the claim fail. Comments have to be
    #    stripped before a claim about code reads the code.
    (u"""planner = read(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Expedition",
                            "CrewPlanner.cs"))
check("THE MEDIC GAP IS STILL NOT A REFUSAL",
      "MissingSkills" in planner and "CompanyActionResult" not in planner.replace(
          "ExpeditionCargo.CheckCapacity(pawn).Success", ""),""",
     u"""planner_raw = read(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Expedition",
                                "CrewPlanner.cs"))
# Comments stripped before reading. The planner's own doc comment says *"there is no
# `CompanyActionResult` anywhere in it"* -- the sentence this claim wants the file to contain --
# and reading the raw text made the claim fail on its own evidence.
planner = re.sub(r"^\\s*///.*$", "", planner_raw, flags=re.M)
planner = re.sub(r"//[^\\n]*", " ", planner)
check("THE MEDIC GAP IS STILL NOT A REFUSAL",
      "MissingSkills" in planner and "CompanyActionResult" not in planner.replace(
          "ExpeditionCargo.CheckCapacity(pawn).Success", ""),"""),

    # 2. There is no symbol named `supportedVersions`; the checker matches the XML element.
    (u"""CHECKS = (
    ("supportedVersions", "official RimWorld only"),
    ("DESTRUCTIVE", "no destructive patch operation"),
    ("GAME_BINARIES", "no bundled game binary"),
    ("PATCHING", "no game assembly patching"),
    ("ATTRIBUTION", "no AI attribution in a shipped file"),
    ("LICENCE_NEGATORS", "another project's licence terms"),
)
for symbol, what in CHECKS:
    check("it checks %s" % what, ("%s = " % symbol) in compliance)""",
     u"""# Each is matched at its DEFINITION, not by name, for the reason this file has now been
# caught by twice in two batches: a name is a substring of its own declaration and of any
# renaming of it. The first version of this loop tested `"supportedVersions = "`, which is not
# a symbol in the checker at all -- it reads the XML element -- so the claim failed rather than
# passing, which is the safe direction and is why it was found immediately.
CHECKS = (
    ("<supportedVersions>", "official RimWorld only"),
    ("DESTRUCTIVE = (", "no destructive patch operation"),
    ("GAME_BINARIES = (", "no bundled game binary"),
    ("PATCHING = (", "no game assembly patching"),
    ("ATTRIBUTION = (", "no AI attribution in a shipped file"),
    ("LICENCE_NEGATORS = (", "another project's licence terms"),
)
for symbol, what in CHECKS:
    check("it checks %s" % what, symbol in compliance,
          "-- looked for %r in the checker" % symbol)"""),

    # 3. The note reads "Not verified against the build". Compared case-insensitively.
    (u"""check("the source says the figures are unverified",
      "not verified against the build" in data.get("note", ""),""",
     u"""check("the source says the figures are unverified",
      "not verified against the build" in data.get("note", "").lower(),"""),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("three claims corrected in one write")
