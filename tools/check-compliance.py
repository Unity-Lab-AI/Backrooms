# -*- coding: utf-8 -*-
"""Hold the shipped package against Ludeon's modding terms and the Steam agreements.

Why this exists
---------------
Owner direction, verbatim, across five queue rows:

    "make sure we are foillowing all rimworld and steam TOS and requirments"
    "when it comes to issues similar and the issue of factions"
    "and pawn heduffs"
    "and the like"
    "this mod has to be working with official versions"

The fourth of those is the one that decides the shape of this file. *"And the like"* generalises
the rule to every def class the mod may ever add, and the queue row spells out what that means:
**one compliance test, applied to all of them.** Not a note per def class -- a test.

`docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md` held the position as a table of thirteen rows, each
with a "how it was checked" column, and its own closing section says *"Everything in the verified
table is mechanically checkable, so it is re-run rather than trusted."* It was never re-run. The
table was verified at **0.5.6-dev** and read as current for **thirty-six checkpoints**, over which
at least three of its rows stopped being true -- the package went from 76 approved files to 89,
the fourteen gameplay PNGs it enumerates were deleted at 0.12.22-dev, and it states there are
**zero** DLC references in package XML when the DLC-gated defs added since are exactly the
supported way to reference them.

**A dated table of mechanical checks is the same defect as a dated count.** So this is the table,
executable.

What it does not duplicate
--------------------------
Three of the original rows are already owned by other checkers, and a second copy of a rule is a
second thing that can disagree with it:

* **hard dependencies and `loadAfter`** -- `check-register-compliance.py`
* **DLC gating** -- `check-dlc-gating.py`, which knows the five official package ids
* **reference assembly drift** -- the per-checkpoint evidence manifest

Those are named in the report as delegated rather than silently dropped, because a compliance
report that quietly covers less than the table it replaces is worse than the table.

Exit status
-----------
    0   every check passed
    1   a check failed
    2   skipped -- the game install could not be read, so the official-assembly check is blind

Two is not a pass. It is the same distinction `check-def-fields.py` makes, for the same reason: a
check that could not run must not report the same thing as a check that ran and found nothing.

Usage
-----
    python tools/check-compliance.py
"""

import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SRC = os.path.join(REPO, "src")

problems = []
notes = []
skips = []


def fail(message):
    problems.append(message)


def read(path):
    return io.open(path, encoding="utf-8-sig", errors="replace").read()


def approved_files():
    """The package's own manifest of what it ships. One source of truth, not a directory walk."""
    manifest = os.path.join(REPO, "tools", "package-files.json")
    if not os.path.isfile(manifest):
        fail("tools/package-files.json is missing, so what the package ships cannot be stated")
        return []
    return json.loads(read(manifest)).get("files", [])


def package_xml():
    found = []
    for root, _dirs, files in os.walk(MOD):
        for name in files:
            if name.lower().endswith(".xml"):
                found.append(os.path.join(root, name))
    return sorted(found)


def source_cs():
    found = []
    for root, _dirs, files in os.walk(SRC):
        if os.sep + "obj" in root or os.sep + "bin" in root:
            continue
        for name in files:
            if name.lower().endswith(".cs"):
                found.append(os.path.join(root, name))
    return sorted(found)


shipped = approved_files()

# --------------------------------------------------------------------------- #
# 1. Official RimWorld only
# --------------------------------------------------------------------------- #
about = os.path.join(MOD, "About", "About.xml")
if not os.path.isfile(about):
    fail("About.xml is missing")
else:
    text = read(about)
    versions = re.findall(r"<li>([^<]+)</li>", "".join(
        re.findall(r"<supportedVersions>(.*?)</supportedVersions>", text, re.S)))
    versions = [v.strip() for v in versions if v.strip()]
    if versions != ["1.6"]:
        fail("supportedVersions is %r; the mod targets official RimWorld 1.6 alone (row 1290)"
             % versions)
    else:
        notes.append("supportedVersions is 1.6 alone")

folders = os.path.join(MOD, "LoadFolders.xml")
if not os.path.isfile(folders):
    fail("LoadFolders.xml is missing")
elif not re.search(r'<v1\.6>', read(folders)):
    fail("LoadFolders.xml does not map v1.6")
else:
    notes.append("LoadFolders.xml maps v1.6")

# --------------------------------------------------------------------------- #
# 2. No destructive patch operation on a Core or DLC def
# --------------------------------------------------------------------------- #
# Rule 3 of the document, and the one with the sharpest edge: `PatchOperationReplace` on a Core
# def silently takes ownership of it, so the last mod to load wins and every other mod touching
# it loses. This package has always had zero of them and nothing asserted it.
DESTRUCTIVE = ("PatchOperationReplace", "PatchOperationRemove")
destructive = []
operations = {}
for path in package_xml():
    body = read(path)
    for match in re.finditer(r'Class="(Patch[A-Za-z]*)"', body):
        operations[match.group(1)] = operations.get(match.group(1), 0) + 1
    for kind in DESTRUCTIVE:
        if kind in body:
            destructive.append("%s in %s"
                               % (kind, os.path.relpath(path, REPO).replace(os.sep, "/")))
if destructive:
    fail("the package contains a destructive patch operation: %s. Rule 3: additive patches only, "
         "because a replace takes ownership of a def and the last mod to load wins"
         % ", ".join(sorted(destructive)))
else:
    notes.append("no destructive patch operation; operations in use: %s"
                 % (", ".join("%s x%d" % (k, v) for k, v in sorted(operations.items()))
                    or "none"))

# --------------------------------------------------------------------------- #
# 3. No game or third-party asset redistributed
# --------------------------------------------------------------------------- #
# Rule 1 and 2 together: a string naming Ludeon's asset is a reference and is fine; a copy of the
# file is redistribution and is not. So the test is on the FILES, not on the strings.
foreign = []
for rel in shipped:
    lowered = rel.lower()
    if lowered.endswith(".xml") or lowered.endswith(".txt"):
        continue
    if rel.startswith("About/"):
        continue                    # the mod's own preview and licence, which every mod ships
    if rel.endswith("RimroomsAsyncIndustries.dll"):
        continue                    # our own compiled assembly
    if re.search(r"/RR_[^/]+$", rel):
        continue                    # our own, RR_-prefixed
    foreign.append(rel)
if foreign:
    fail("the package ships a non-XML file that is not clearly its own: %s. Rule 1: add "
         "definitions, never redistribute assets" % ", ".join(sorted(foreign)))
else:
    notes.append("every non-XML file shipped is this package's own (%d approved files)"
                 % len(shipped))

# A game assembly or data file must never be in the package, under any name.
GAME_BINARIES = ("assembly-csharp", "unityengine", "mscorlib", "rimworldwin64", ".exe", ".bank")
bundled = [rel for rel in shipped
           if any(marker in rel.lower() for marker in GAME_BINARIES)]
if bundled:
    fail("the package bundles a game binary or data file: %s (row 1290)" % ", ".join(bundled))
else:
    notes.append("no game binary or data file is bundled")

# A texture path that is not ours is a reference to somebody else's. That is allowed -- and it is
# only allowed while we do not ALSO ship a file at that path, which would be the copy the rule
# forbids wearing a reference's name.
shipped_lower = set(rel.lower() for rel in shipped)
copied = []
for path in package_xml():
    for match in re.finditer(r"<(?:texPath|uiIconPath|iconPath)>([^<]+)</", read(path)):
        value = match.group(1).strip()
        if not value:
            continue
        for extension in (".png", ".jpg"):
            candidate = ("1.6/Textures/" + value + extension).lower()
            if candidate in shipped_lower and "/RR_" not in value and not value.startswith("RR_"):
                copied.append(value)
if copied:
    fail("the package ships a file at a non-RR_ texture path: %s. Referencing Ludeon's path is "
         "allowed; shipping a file there is the copy rule 2 forbids" % ", ".join(sorted(set(copied))))
else:
    notes.append("no shipped file sits at a texture path that is not this package's own")

# --------------------------------------------------------------------------- #
# 4. No game assembly patching
# --------------------------------------------------------------------------- #
# The project has no Harmony by design, and *"no game assembly patching"* is a Ludeon-terms
# question as much as an architecture one. Reflection is the loophole: a `SetValue` into a game
# type is a game-assembly modification that no dependency list would show.
PATCHING = (
    (re.compile(r"\bHarmonyLib\b|\bHarmonyPatch\b|\bHarmonyInstance\b"), "Harmony"),
    (re.compile(r"\bDetour\b|\bMonoMod\b"), "a detour framework"),
    (re.compile(r"\bFieldInfo\b[^;]*\bSetValue\b|\bSetValue\s*\(\s*(?:null|[A-Za-z_])"),
     "a reflection write"),
    (re.compile(r"GetField\s*\([^)]*BindingFlags\.NonPublic"), "a private-field read by reflection"),
)
patching = []
for path in source_cs():
    body = re.sub(r"//[^\n]*", " ", read(path))
    body = re.sub(r"/\*.*?\*/", " ", body, flags=re.S)
    for pattern, what in PATCHING:
        if pattern.search(body):
            patching.append("%s in %s"
                            % (what, os.path.relpath(path, REPO).replace(os.sep, "/")))
if patching:
    fail("this package modifies the game assembly at runtime: %s. Behaviour is added through "
         "Core's own ThingComp, GameComponent, WorkGiver, JobDriver and Def extension points"
         % ", ".join(sorted(patching)))
else:
    notes.append("no Harmony, no detours, no reflection writes into game types")

# --------------------------------------------------------------------------- #
# 5. Our own licence, and nobody else's terms inherited
# --------------------------------------------------------------------------- #
licence = os.path.join(MOD, "About", "License.txt")
if not os.path.isfile(licence):
    fail("About/License.txt is missing; the package must state its own licence")
elif "MIT License" not in read(licence):
    # `"MIT" in text` is not this test. The MIT boilerplate contains the word **LIMITED**, which
    # contains MIT, so a licence file whose title had been replaced outright still passed. Found
    # by a plant that swapped `MIT License` for `Proprietary License` and was not caught.
    fail("About/License.txt does not state the MIT licence the project declares")
else:
    notes.append("About/License.txt states the MIT licence")

# Row 218 Stargates! is GPL-3.0. Copying from it would force this mod to GPL, which is why the
# absence is worth asserting rather than remembering.
#
# **Tested for assertion, not for mention**, and the first run of this file proved why: it flagged
# `ConnectedFoodAdapter.cs`, whose comment says Gastronomy has *"unresolved rights ... so its code
# and art must not be adapted and no adapter is built"*. That is the sentence the rule wants the
# code to contain. A naive substring ban fails exactly the files that document their own
# compliance -- the same trap `disposition_stance()` fell into by reading `"required" in text`, and
# the same one the row 791 claim guard was widened to avoid.
#
# The failure mode is chosen the same way too: a missing negator produces a false positive that
# blocks a build, which is loud and gets fixed. Never narrow the pattern to make a failure go away.
LICENCE_NEGATORS = ("must not", "not be adapted", "no adapter", "never", "cannot", "do not",
                    "does not", "unresolved", "not copied", "nothing is taken", "not a dependency",
                    "would force", "would relicense", "refers to")
LICENCE_PATTERN = re.compile(r"\bGPL\b|\bGNU General Public\b")
gpl = []
for path in source_cs():
    body = read(path)
    for match in LICENCE_PATTERN.finditer(body):
        # The sentence it sits in, bounded by sentence punctuation or a blank comment line.
        start = max(body.rfind(".", 0, match.start()), body.rfind("\n\n", 0, match.start()))
        end = body.find(".", match.end())
        sentence = body[start + 1:end if end > 0 else match.end() + 200].lower()
        if any(negator in sentence for negator in LICENCE_NEGATORS):
            continue
        gpl.append("%s: %s"
                   % (os.path.relpath(path, REPO).replace(os.sep, "/"),
                      " ".join(sentence.split())[:90]))
if gpl:
    fail("a source file invokes the GPL without denying it applies here: %s. Register row 218 "
         "(Stargates!) is GPL-3.0 and copying from it would relicense this mod"
         % "; ".join(sorted(gpl)))
else:
    notes.append("no source file carries another project's licence terms as its own "
                 "(mentions that deny they apply are read as compliance, not as breach)")

# --------------------------------------------------------------------------- #
# 6. No AI attribution in anything shipped
# --------------------------------------------------------------------------- #
# A standing project LAW, and also the honest position for authorship on a store page. Nothing
# checked the PACKAGE for it -- only commits and docs were ever considered.
ATTRIBUTION = ("co-authored-by: claude", "generated with [claude", "made with claude code",
               "noreply@anthropic.com", "anthropic.com/claude")
attributed = []
for rel in shipped:
    path = os.path.join(MOD, rel.replace("/", os.sep))
    if not os.path.isfile(path) or not rel.lower().endswith((".xml", ".txt")):
        continue
    lowered = read(path).lower()
    for marker in ATTRIBUTION:
        if marker in lowered:
            attributed.append("%s in %s" % (marker, rel))
if attributed:
    fail("a shipped file carries AI attribution: %s. The team ships work as its own"
         % ", ".join(sorted(attributed)))
else:
    notes.append("no shipped file carries AI attribution")

# --------------------------------------------------------------------------- #
# 7. The QA overlay is not shipped
# --------------------------------------------------------------------------- #
overlay = [rel for rel in shipped if "rimbridge" in rel.lower() or "rimapi" in rel.lower()]
if overlay:
    fail("the QA overlay is inside the package: %s. It is a separately attached owner tool and "
         "is never a dependency or a shipped file" % ", ".join(overlay))
else:
    notes.append("the QA overlay is not in the package")

# --------------------------------------------------------------------------- #
# 8. Official assemblies only, unmodified -- the one check that can be blinded
# --------------------------------------------------------------------------- #
# Read from the per-checkpoint evidence manifest rather than from the game install, because the
# manifest is what the build actually compiled against. If there is no manifest the check is
# SKIPPED and says so; it does not pass.
manifests = []
evidence = os.path.join(REPO, "docs", "implementation", "evidence")
if os.path.isdir(evidence):
    for root, _dirs, files in os.walk(evidence):
        for name in files:
            if name == "reference-manifest.json":
                manifests.append(os.path.join(root, name))
if not manifests:
    skips.append("no reference-manifest.json under docs/implementation/evidence, so which game "
                 "assemblies the build compiled against cannot be stated")
else:
    latest = sorted(manifests)[-1]
    try:
        data = json.loads(read(latest))
    except ValueError as exception:
        fail("the reference manifest could not be parsed: %s" % exception)
        data = None
    if data is not None:
        # Keys are matched case-insensitively, and **zero references is a failure, not a pass.**
        # The first version of this read `data.get("references")`, the manifest's key is
        # `References`, and the result was a confident `ok: references 0 assemblies, all from the
        # official install`. A compliance check that finds nothing and reports success is worse
        # than no check -- it is the defect this whole file exists to replace.
        entries = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ("references", "files") and isinstance(value, list):
                    entries = value
                    break
        names = []
        for entry in entries:
            if isinstance(entry, dict):
                for key, value in entry.items():
                    if key.lower() in ("name", "file", "path"):
                        names.append(str(value))
                        break
            else:
                names.append(str(entry))
        names = [n for n in names if n]
        if not names:
            fail("the reference manifest %s parsed to zero assemblies. A build that references "
                 "none is impossible, so this is a parse failure and must not read as a pass"
                 % os.path.relpath(latest, REPO).replace(os.sep, "/"))
        else:
            unofficial = [n for n in names
                          if not re.search(r"(Assembly-CSharp|UnityEngine|mscorlib|System)",
                                           n, re.I)]
            if unofficial:
                fail("the build references an assembly that is not part of the official install: "
                     "%s" % ", ".join(sorted(unofficial)))
            else:
                notes.append("references %d assemblies, all from the official install (%s)"
                             % (len(names), os.path.relpath(latest, REPO).replace(os.sep, "/")))

# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
print("compliance -- Ludeon modding terms, Steam agreements, official versions")
for note in notes:
    print("  ok   : %s" % note)
print("")
print("  delegated, so no rule has two owners that can disagree:")
print("    hard dependencies and loadAfter : check-register-compliance.py")
print("    DLC gating and the five official package ids : check-dlc-gating.py")
print("    what the package is allowed to contain : tools/package-files.json")

if skips:
    print("")
    print("SKIPPED: %d check(s) could not run" % len(skips))
    for skip in skips:
        print("  - %s" % skip)
    if problems:
        print("")
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        sys.exit(1)
    sys.exit(2)

if problems:
    print("")
    print("FAIL: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    sys.exit(1)

print("")
print("PASS")
sys.exit(0)
