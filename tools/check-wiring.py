# -*- coding: utf-8 -*-
"""Refuse to ship a thing this mod authors that nothing reads.

Why this exists
---------------
This project's most expensive defect class, four times over:

  * **0.11.7-dev** -- five `RR_*Staff` PawnKinds, authored and read by nothing.
  * **0.11.8-dev** -- no `IncidentDef` existed, so the storyteller did not know the mod was there.
  * **0.12.11-dev** -- `RimroomsRequestDef`, `RequestRoutes` and seven authored requests were read
    by **zero lines of C#**. The whole campaign had been written and was unreachable, and the
    chart recorded both steps as *done*.
  * **0.12.30-dev** -- `EstablishCorporationContact()` had **no caller**, which left two of the
    three shipped starts with no campaign at all, permanently.

Every one of those passed every checker and every proof of its day. Nothing was wrong with any
individual file; the wiring between them was missing, and no tool looked at wiring.

What "wired" means, precisely
-----------------------------
**A def** is wired when any one of these is true, and the three are genuinely different routes:

  1. its `defName` appears in our C# -- resolved by name;
  2. its **type** is enumerated by our C# (`DefDatabase<ThatType>`) or is a def type **RimWorld
     itself** consumes (`ThingDef`, `ScenarioDef`, `FactionDef`, `RecipeDef`, ...) -- consumed by
     type rather than by name, which is how most content defs work;
  3. its `defName` appears in **another def's XML** -- a cross-reference, which is how the three
     `RimroomsStartDef`s are reached from their `ScenarioDef`s.

Rule 3 exists because leaving it out reported those three starts as dangling when they are not.

**An action** -- a `public` method returning `CompanyActionResult`, which is this mod's whole
player-facing verb surface -- is wired when something other than its own declaration calls it.
That is the rule that catches `EstablishCorporationContact`.

Exit status is the result. Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

# Def types RimWorld resolves itself, so our code never has to name or enumerate them. Kept short
# and explicit: a type added here without a reason is a hole in the check.
CORE_CONSUMED = set("""
ThingDef TerrainDef RecipeDef ScenarioDef FactionDef IncidentDef ResearchProjectDef JobDef
WorkGiverDef ThingCategoryDef SoundDef ThoughtDef HediffDef PawnKindDef ScenPartDef
MapGeneratorDef GenStepDef DesignationCategoryDef WorkTypeDef StatDef TraitDef RulePackDef
MainButtonDef KeyBindingDef TaleDef ColorDef
""".split())

problems = []
notes = []


def fail(message):
    problems.append(message)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def source_files():
    """Hand-written C# only. obj/ and bin/ hold generated copies that would mask a real gap."""
    found = {}
    for root, _, names in os.walk(SRC):
        if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
            continue
        for name in names:
            if name.endswith(".cs"):
                path = os.path.join(root, name)
                found[path] = strip_cs_comments(read(path))
    return found


def declared_defs():
    """defName -> type name, for every def this package declares."""
    found = {}
    for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
        text = strip_xml_comments(read(path))
        wrapper = re.search(r"<Defs>(.*)</Defs>", text, re.S)
        if wrapper is None:
            continue
        for match in re.finditer(r"<([A-Za-z0-9_.]+)(?:\s[^>]*)?>\s*(.*?)\s*</\1>",
                                 wrapper.group(1), re.S):
            body = match.group(2)
            name = re.search(r"<defName>([^<]+)</defName>", body)
            if name:
                found.setdefault(name.group(1).strip(), match.group(1))
    return found


def check_defs(problems, source_blob):
    declared = declared_defs()
    if not declared:
        fail("no defs parsed at all; the package layout has moved")
        return 0

    enumerated = set(t.split(".")[-1]
                     for t in re.findall(r"DefDatabase<([A-Za-z0-9_.]+)>", source_blob))

    # Every def XML, so a cross-reference from one def to another counts as wiring.
    def_xml = "\n".join(strip_xml_comments(read(path)) for path in
                        glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True))

    for name, kind in sorted(declared.items()):
        short = kind.split(".")[-1]
        if re.search(r"\b" + re.escape(name) + r"\b", source_blob):
            continue
        if short in enumerated or short in CORE_CONSUMED:
            continue
        # A cross-reference means the name appears somewhere OTHER than its own declaration.
        if len(re.findall(r"\b" + re.escape(name) + r"\b", def_xml)) > 1:
            continue
        fail("%s (%s) is declared and nothing reads it: not named in C#, its type is neither "
             "enumerated nor Core-consumed, and no other def references it" % (name, short))
    notes.append("%d def(s) declared, %d type(s) enumerated by our own code"
                 % (len(declared), len(enumerated)))
    return len(declared)


def check_actions(problems, files):
    """Every public CompanyActionResult method must be called from somewhere."""
    signature = re.compile(r"public\s+(?:static\s+)?CompanyActionResult\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    total = 0
    for path, text in sorted(files.items()):
        for match in signature.finditer(text):
            name = match.group(1)
            total += 1
            calls = 0
            for other, body in files.items():
                hits = len(re.findall(r"\b" + re.escape(name) + r"\s*\(", body))
                # Its own file contains the declaration, so one hit there is not a call.
                calls += hits - 1 if other == path else hits
            if calls <= 0:
                fail("%s in %s returns a CompanyActionResult and nothing calls it. A verb with no "
                     "caller is a feature that does not exist -- this is how "
                     "EstablishCorporationContact left two starts with no campaign"
                     % (name, os.path.relpath(path, REPO)))
    notes.append("%d public action method(s) checked for callers" % total)
    return total


def main():
    files = source_files()
    if not files:
        fail("no C# sources found; the source layout has moved")
        return report()
    blob = "\n".join(files.values())
    check_defs(problems, blob)
    check_actions(problems, files)
    return report()


def report():
    print("wiring check")
    for note in notes:
        print("  note: %s" % note)
    if problems:
        print("")
        for problem in problems:
            print("  FAIL %s" % problem)
        print("")
        print("FAILED: %d problem(s)" % len(problems))
        return 1
    print("  everything this mod authors is read by something")
    return 0


if __name__ == "__main__":
    sys.exit(main())
