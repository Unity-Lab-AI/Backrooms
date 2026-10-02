# -*- coding: utf-8 -*-
"""Rows 206, 302, 1054, 1268, 1269 and 1286-1290: the housekeeping, with teeth.

Four rows of bookkeeping, and every one of them turned out to be about something being **true**
rather than about tidying. What this file asserts:

  * **206, 302 -- the register retro sweep's last seven families.** They collapse into five family
    strings, every one was already honoured, and **no code changed.** So the sweep's product is
    assertions: the four rules that were satisfied by nothing but the current shape of the
    package now have checks behind them.

  * **1054 -- the master backlog.** It predicted the count understated the build *"by roughly
    thirty points"*. It was 56. Asserted here: every flipped row kept its original text, and **no
    runtime-acceptance row was flipped**, because no game has ever been launched from this
    repository and marking those done would erase the only honest caveat the project has.

  * **1268, 1269 -- the economy workbook.** *"Unopenable"* was about Excel, not about the bytes:
    an xlsx is a zip of XML and the standard library reads both. Five documents linked a file
    nobody could read. Asserted: the tracked source matches the workbook byte for byte, and the
    HTML says its figures are transcribed rather than verified.

  * **1286-1290 -- the compliance pass.** The queue row asks for *"one compliance test, applied to
    all of them"*, and the document's own closing line said its table *"is re-run rather than
    trusted"*. It was never re-run: verified at 0.5.6-dev, read as current for thirty-six
    checkpoints, and **three of its rows had stopped being true.**

Run from the repository root.
"""
import io
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(REPO, "tools")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


compliance = read(os.path.join(TOOLS, "check-compliance.py"))
register = read(os.path.join(TOOLS, "check-register-compliance.py"))
extractor = read(os.path.join(TOOLS, "extract-economy-workbook.py"))
compliance_doc = read(os.path.join(REPO, "docs", "COMPLIANCE_AND_OFFICIAL_VERSIONS.md"))
master = read(os.path.join(REPO, "docs", "PREPRODUCTION_AND_IMPLEMENTATION_TODO.md"))
queue = read(os.path.join(REPO, "docs", "TODO.md"))

# --------------------------------------------------------------------------------------------
print("")
print("rows 206 and 302: the last five family strings, and their rules now have checks")
print("-" * 90)

check("the sweep's rules live in the register checker",
      "PATCH_STEERED = {" in compliance_doc.replace("x", "x") or "PATCH_STEERED = {" in register,
      "-- a sweep whose product is a paragraph is a promise")

# Each rule, with the row it was quoted from. The row citation is the part that cannot rot: a
# rule with no source is unarguable and therefore unmaintainable.
# The citation is matched in FULL. "row 2" is a substring of "row 218" and "row 227", so a
# plant that stripped the citation left the claim passing on an unrelated row number.
for def_type, row in (("ThoughtDef", "row 2 SF Grim Reality"),
                      ("TraderKindDef", "row 17 [KV] Call Trade Ships"),
                      ("HediffDef", "the medical family, rows 23-272"),
                      ("MainButtonDef", "the hospitality family, rows 62-286")):
    check("%s is refused in patches, citing %s" % (def_type, row.split(",")[0]),
          ('"%s": "%s' % (def_type, row)) in register,
          "-- the family's own Integration Approach is the source, and the citation is matched "
          "in full so that stripping it fails the claim")

check("no patch may alter another def's stat bases",
      "if mass_patches:" in register and "Preserve each mod" in register,
      "-- the materials and cargo family, rows 52-228. Setting a mass on OUR def is normal; "
      "altering theirs is what the rule is about, so the check is on the patches")

check("the register checker still passes",
      subprocess.call([sys.executable, os.path.join(TOOLS, "check-register-compliance.py")],
                      stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT) == 0)

# The finding worth keeping. The medical family's rule is that the expedition loop must not
# require a medical mod, and 0.12.41-dev came within one decision of breaking it.
planner_raw = read(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Expedition",
                                "CrewPlanner.cs"))
# Comments stripped before reading. The planner's own doc comment says *"there is no
# `CompanyActionResult` anywhere in it"* -- the sentence this claim wants the file to contain --
# and reading the raw text made the claim fail on its own evidence.
planner = re.sub(r"^\s*///.*$", "", planner_raw, flags=re.M)
planner = re.sub(r"//[^\n]*", " ", planner)
pane = read(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI",
                         "OperationsCrewPlanner.cs"))
check("THE MEDIC GAP IS STILL NOT A REFUSAL",
      "CrewPlanner.MissingSkills(selectedCrew)" in pane
      and "CompanyActionResult" not in planner.replace(
          "ExpeditionCargo.CheckCapacity(pawn).Success", ""),
      "-- the medical family, rows 23-272: *\"the core expedition loop must not require one "
      "medical or Biotech mod to treat a pawn\"*. Had the missing-medic gap been written as a "
      "refusal -- the obvious way -- the loop would have required a medic, and on a profile "
      "where a medical mod owns treatment that is a requirement on that mod")

# --------------------------------------------------------------------------------------------
print("")
print("rows 1286-1290: one compliance test, applied to all of them")
print("-" * 90)

check("the compliance checker exists", os.path.isfile(os.path.join(TOOLS, "check-compliance.py")))

# Each is matched at its DEFINITION, not by name, for the reason this file has now been
# caught by twice in two batches: a name is a substring of its own declaration and of any
# renaming of it. The first version of this loop tested `"supportedVersions = "`, which is not
# a symbol in the checker at all -- it reads the XML element -- so the claim failed rather than
# passing, which is the safe direction and is why it was found immediately.
# Definition AND the branch that acts on it. A rule's table survives `if False and rule:`
# untouched, and four of these claims passed against exactly that plant before being rewritten.
CHECKS = (
    ("<supportedVersions>", "if versions != [\"1.6\"]:", "official RimWorld only"),
    ("DESTRUCTIVE = (", "if destructive:", "no destructive patch operation"),
    ("GAME_BINARIES = (", "if bundled:", "no bundled game binary"),
    ("PATCHING = (", "if patching:", "no game assembly patching"),
    ("ATTRIBUTION = (", "if attributed:", "no AI attribution in a shipped file"),
    ("LICENCE_NEGATORS = (", "if gpl:", "another project's licence terms"),
)
for symbol, branch, what in CHECKS:
    check("it checks %s, and acts on the result" % what,
          symbol in compliance and branch in compliance,
          "-- looked for %r and %r in the checker" % (symbol, branch))

check("it refuses Harmony, detours and reflection writes",
      "HarmonyLib" in compliance and "MonoMod" in compliance and "SetValue" in compliance,
      "-- reflection is the loophole: a write into a game type is an assembly modification no "
      "dependency list would show")

check("THE LICENCE CHECK TESTS ASSERTION, NOT MENTION",
      "LICENCE_NEGATORS" in compliance and "any(negator in sentence" in compliance,
      "-- its first run flagged ConnectedFoodAdapter.cs, whose comment says Gastronomy's rights "
      "are unresolved *so its code must not be adapted*. That is the sentence the rule wants the "
      "code to contain, and a substring ban fails exactly the files that document compliance")

check("ZERO PARSED REFERENCES FAILS RATHER THAN PASSING",
      "A build that references " in compliance and "must not read as a pass" in compliance,
      "-- the first version read the wrong manifest key and reported \"0 assemblies, all from "
      "the official install\". A compliance check that finds nothing and says ok is worse than "
      "no check")

check("a blinded check is skipped rather than passed",
      "sys.exit(2)" in compliance and "SKIPPED" in compliance,
      "-- two is not a pass; same distinction check-def-fields.py makes")

# Matched on the printed line, not on the filename. `check-dlc-gating.py` also appears in
# this checker's own docstring, so a plant that removed the delegation from the REPORT left the
# claim passing on the documentation of it.
check("no rule has two owners",
      "delegated" in compliance
      and 'print("    DLC gating and the five official package ids : check-dlc-gating.py")'
      in compliance
      and 'print("    hard dependencies and loadAfter : check-register-compliance.py")'
      in compliance,
      "-- a second copy of a rule is a second thing that can disagree with it")

check("the compliance checker passes",
      subprocess.call([sys.executable, os.path.join(TOOLS, "check-compliance.py")],
                      stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT) == 0)

check("the document points at the checker instead of a date",
      "tools/check-compliance.py" in compliance_doc
      and "Verified position at 0.5.6-dev" not in compliance_doc,
      "-- a dated table of mechanical checks is the same defect as a dated count")

check("the three stale rows are corrected and say they were stale",
      compliance_doc.count("this row's old text was stale") == 2
      and "89" in compliance_doc and "deleted at 0.12.22-dev" in compliance_doc,
      "-- it claimed 76 approved files, enumerated fourteen PNGs that no longer exist, and "
      "stated there were zero DLC references in package XML")

# --------------------------------------------------------------------------------------------
print("")
print("rows 1268 and 1269: the workbook five documents linked and nobody could read")
print("-" * 90)

source = os.path.join(REPO, "docs", "research", "campaign-economy-workbook.json")
check("the tracked source exists", os.path.isfile(source))
check("the generator exists", os.path.isfile(os.path.join(TOOLS, "extract-economy-workbook.py")))
check("the HTML output exists",
      os.path.isfile(os.path.join(REPO, "outputs", "readable", "campaign-economy.html")))

check("THE TRACKED SOURCE MATCHES THE WORKBOOK",
      subprocess.call([sys.executable, os.path.join(TOOLS, "extract-economy-workbook.py"),
                       "--check"],
                      stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT) == 0,
      "-- the generator re-reads the xlsx and compares; a source that drifted from the workbook "
      "would be a third version of the numbers rather than a readable one")

check("it reads shared strings rather than printing their indices",
      "sharedStrings" in extractor and "kind == \"s\"" in extractor,
      "-- xlsx stores repeated text once and cells reference it by index, so a reader that "
      "ignored that would print integers where the labels are")

check("sheet order comes from the workbook, not from filenames",
      "workbook.xml.rels" in extractor,
      "-- reading worksheets in name order guesses wrong the moment a sheet is inserted rather "
      "than appended")

data = json.loads(read(source))
check("the source carries every sheet", len(data.get("sheets", [])) >= 5,
      "-- found %d" % len(data.get("sheets", [])))
check("the source says the figures are unverified",
      "not verified against the build" in data.get("note", "").lower(),
      "-- the row is explicit that this is a different dataset whose content has not been "
      "verified, and a generator that corrected a figure would destroy the only useful property "
      "it has: being what its author wrote")

html = read(os.path.join(REPO, "outputs", "readable", "campaign-economy.html"))
check("the HTML says so too, at the top",
      "transcribed, not verified" in html and "has ever been launched" in html)
check("the HTML authors no colour or font size",
      "color:" not in html.replace("currentColor", "") and "font-size" not in html,
      "-- same rule as the in-game readouts, for the same reason: the reader's own settings "
      "should apply")

readme = os.path.join(REPO, "outputs", "rimrooms-async-industries-register-2026-09-27",
                      "README.md")
check("the superseded PNGs carry a note rather than being deleted", os.path.isfile(readme),
      "-- row 1269: *\"Not deleted -- they are tracked artifacts and removing them is the "
      "owner's call -- but they must not be read as showing the current file\"*")
if os.path.isfile(readme):
    note = read(readme)
    check("the note says which file is authoritative",
          "THE REGISTER" in note and "The HTML is the register" in note)
    check("nothing in that folder was deleted",
          "Nothing in this folder has been removed" in note)

# --------------------------------------------------------------------------------------------
print("")
print("row 1054: the master backlog, reconciled -- and it predicted thirty")
print("-" * 90)

reconciled = master.count("RECONCILED 0.12.42-dev")
check("the reconciliation is recorded row by row", reconciled >= 50,
      "-- found %d; row 1054 predicted the count understated the build \"by roughly thirty "
      "points\"" % reconciled)

# The one row row 1054 was actually written about -- *"the entire cross-map work engine sits
# under one unchecked row"*. A count claim cannot see this row going missing, so it is named.
check("the row row 1054 was written about is reconciled by name",
      "**RECONCILED 0.12.42-dev: SHIPPED, and this is the row row 1054 was written about.**"
      in master,
      "-- the cross-map work engine, 31 work families, which the row says sat under one "
      "unchecked row")

open_rows = len(re.findall(r"^\s*- \[ \]", master, re.M))
done_rows = len(re.findall(r"^\s*- \[x\]", master, re.M))
check("the master count now reflects the build",
      done_rows > open_rows * 2,
      "-- %d done against %d open" % (done_rows, open_rows))

# THE claim of this half. A reconciliation that marked runtime acceptance done would erase the
# project's only honest caveat.
flipped_runtime = [line for line in master.split("\n")
                   if line.strip().startswith("- [x]")
                   and "RECONCILED 0.12.42-dev" in line
                   and re.search(r"[Rr]untime acceptance|after the owner launches", line)]
check("NO RUNTIME-ACCEPTANCE ROW WAS FLIPPED", not flipped_runtime,
      "-- %s. Runtime acceptance is still unrecorded: the mod has been launched and never played "
      "through"
      % "; ".join(line.strip()[:80] for line in flipped_runtime))

check("runtime acceptance rows are still open",
      len([line for line in master.split("\n")
           if line.strip().startswith("- [ ]")
           and re.search(r"[Rr]untime acceptance|after the owner launches", line)]) >= 2,
      "-- they are the rows that cannot close without a launch, and they must stay visible")

# Every original word kept. The LAW is that marking a task done changes the status ONLY.
truncated = []
for line in master.split("\n"):
    if "RECONCILED 0.12.42-dev" not in line:
        continue
    body = line.split("— **RECONCILED")[0]
    if len(body.strip()) < 30:
        truncated.append(line.strip()[:70])
check("every reconciled row kept its original text", not truncated,
      "-- %s looks shortened. The LAW is that marking a task done changes the status ONLY"
      % "; ".join(truncated))

# --------------------------------------------------------------------------------------------
print("")
print("the queue rows these close")
print("-" * 90)

# RE-AIMED 2026-10-02, and the re-aim strengthens the claim rather than relaxing it.
#
# Owner direction, verbatim: *"we need to move all finished items to finalized.md from the
# todo, the todods sahll never hold completed items, they are always to be moved to finalized
# first then deleted from the todods once confirmed virbatium transfer"*. A closed row no
# longer sits in the queue at all, so reading the closure marker out of `docs/TODO.md` is
# reading the wrong file -- these four rows closed and were archived.
#
# "Closed" is now asserted in BOTH directions, which the single-file read could not do:
# the closure is recorded in the archive, AND the row is gone from the queue. A row that was
# flipped to [x] and left sitting in the queue would have passed the old claim and fails this
# one; so would a row deleted from the queue with nothing written to the archive.
archive = read(os.path.join(REPO, "docs", "FINALIZED.md"))

# Counted where a marker is used twice, because the plant harness replaces the first
# occurrence and a second one left the claim passing.
check("both retro-sweep rows are closed",
      archive.count("**SWEPT 0.12.42-dev") >= 2,
      "-- rows 206 and 302 are one sweep and both carry the marker (found %d)"
      % archive.count("**SWEPT 0.12.42-dev"))

for marker, what in (
        ("**SWEPT 0.12.42-dev. All twenty-one families are now done",
         "rows 206 and 302, the retro sweep"),
        ("**RECONCILED 0.12.42-dev, and the row underestimated", "row 1054, the master backlog"),
        ("**BUILT 0.12.42-dev as `tools/extract-economy-workbook.py`", "rows 1268 and 1269"),
        ("**BUILT 0.12.42-dev as `tools/check-compliance.py`", "rows 1286-1290")):
    check("%s is closed in the archive" % what, marker in archive)
    check("%s no longer sits in the queue" % what, marker not in queue,
          "-- a finished row left in docs/TODO.md is the defect the 2026-10-02 direction "
          "names: the queue shall never hold completed items")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the sweep's rules are checks, the compliance table is executable, the "
      "workbook is readable and says it is unverified, and the master backlog counts the build "
      "without marking a single unlaunched thing accepted")
