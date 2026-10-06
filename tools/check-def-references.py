# -*- coding: utf-8 -*-
"""Resolve every def name this package references against the real game on disk.

Why this exists
---------------
Owner direction, 2026-10-06: *"do it all in the needed order and completely and thouroughly
correct to the games requirments and having mods not breaking it that are in the suggested
list... i cuttenlty have 296 (6DLCs, Rimbridge , Rimrooms(locally))"*.

**ONLY THE OWNER LAUNCHES.** So a def that names `MicroelectronicsBasic` instead of
`MicroelectronicsBasics`, or inherits from an abstract parent that does not exist, is invisible
here and is a red wall of cross-reference errors there -- and on a 296 mod profile a red log is
read as *this mod broke my game* long before anybody finds the typo. 0.13.0-dev added eight new
ThingDefs, a TerrainDef and a SoundDef in one session, every one of them naming Core content by
string. That is the largest reference surface this package has ever shipped in one change.

**The game is the authority, not a list kept here.** The installed `Data/` folders are parsed for
every `defName` and every abstract `Name`, and our references are resolved against that union plus
our own defs. A list of valid names maintained in this file would be stale the first time Ludeon
renames anything, which is the failure this whole battery exists to avoid.

What is checked
---------------
  1. **Every `ParentName` resolves.** An unresolved abstract parent drops the whole def silently in
     some orders and errors loudly in others; neither is a thing to discover at runtime.
  2. **Every referenced def name resolves** -- research prerequisites, build costs, stuff
     categories, thing categories, terrain, sounds, fuel filters, burned results, name makers.
  3. **Every class we name exists in our own source.** A `Class=` or `thingClass` pointing at a
     `RimroomsAsyncIndustries.*` type that no longer exists throws out of `DirectXmlToObjectNew`,
     and that does not fail one component -- **it discards the whole ThingDef being parsed**. This
     package has already paid for that once: a `CompProperties_Colorable` that does not exist took
     `Door` and `Autodoor` out of the game and turned the log red from the top.

Game types outside our namespace are NOT checked. Verifying `Building_PowerSwitch` would mean
reflecting over the game's assemblies, which is a RimWorld process and cannot run here.

Run from the repository root. Exits non-zero on an unresolved reference.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SOURCE = os.path.join(REPO, "src")

GAME_ROOTS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
    r"C:\Program Files\Steam\steamapps\common\RimWorld\Data",
    os.path.join(os.path.expanduser("~"), "RimWorld", "Data"),
]

# Leaf elements whose text is a def name, and the list wrappers whose <li> values are def names.
# **ENUMERATED FROM THE SHIPPED FILES RATHER THAN IMAGINED.** A tag missing from this list is a
# reference nobody checks, which is the same hole `check-register-compliance` found when its first
# draft listed `thingDef` and missed `<thing>`.
DEF_TAGS = (
    "burnedDef", "destroySound", "soundDoorOpenPowered", "soundDoorClosePowered",
    "nameMaker", "descriptionMaker", "designationCategory", "researchPrerequisite",
    "smeltProducts", "filthLeaving", "terrainDef", "stuff",
)
DEF_LISTS = (
    "researchPrerequisites", "thingCategories", "stuffCategories", "thingDefs",
    "placeWorkers", "inspectorTabs", "modExtensions", "thingSetMakerTags",
)
# Wrappers whose child ELEMENT NAMES are def names rather than their values.
COST_WRAPPERS = ("costList", "statBases", "building")

# statBases and building hold stat/field names, not thing defs. Only costList's children are defs.
CHILD_NAME_DEF_WRAPPERS = ("costList",)

OUR_NAMESPACE = "RimroomsAsyncIndustries"

problems = []
notes = []


def fail(message):
    problems.append(message)


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def strip_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def xml_files(root):
    found = []
    for folder, _subdirs, files in os.walk(root):
        for name in files:
            if name.lower().endswith(".xml"):
                found.append(os.path.join(folder, name))
    return sorted(found)


def game_data_root():
    for candidate in GAME_ROOTS:
        if os.path.isdir(candidate):
            return candidate
    return None


def main():
    root = game_data_root()
    if root is None:
        # **LOUD, NOT SILENT.** A checker that passes because it could not look is worse than no
        # checker: it reports PASS for a build nobody verified.
        print("def references")
        print("  SKIPPED: no RimWorld Data folder found in any known location.")
        print("")
        print("SKIPPED: this check needs the game on disk and could not run. It did NOT pass.")
        return 2

    game_names = set()
    packs = []
    for pack in sorted(os.listdir(root)):
        folder = os.path.join(root, pack, "Defs")
        if not os.path.isdir(folder):
            continue
        packs.append(pack)
        for path in xml_files(folder):
            body = strip_comments(read(path))
            game_names.update(re.findall(r"<defName>([^<]+)</defName>", body))
            game_names.update(re.findall(r'\bName\s*=\s*"([^"]+)"', body))
    if not game_names:
        fail("the game's Data folder was found but no defs could be parsed from it")
        game_names = set()
    else:
        notes.append("%d def and abstract names parsed from %s" % (len(game_names), ", ".join(packs)))

    ours = set()
    our_files = xml_files(os.path.join(MOD, "1.6", "Defs"))
    for path in our_files:
        body = strip_comments(read(path))
        ours.update(re.findall(r"<defName>([^<]+)</defName>", body))
        ours.update(re.findall(r'\bName\s*=\s*"([^"]+)"', body))
    notes.append("%d def names declared by this package across %d files" % (len(ours), len(our_files)))

    known = game_names | ours

    # Our own types, read out of the source rather than listed here.
    our_types = set()
    for folder, _subdirs, files in os.walk(SOURCE):
        if os.sep + "obj" in folder or os.sep + "bin" in folder:
            continue
        for name in files:
            if name.lower().endswith(".cs"):
                body = read(os.path.join(folder, name))
                namespace = re.search(r"namespace\s+([\w.]+)", body)
                prefix = namespace.group(1) + "." if namespace else ""
                for cls in re.findall(r"\bclass\s+(\w+)", body):
                    our_types.add(prefix + cls)
                    our_types.add(cls)
    notes.append("%d type names read from this package's source" % len(our_types))

    unresolved = []
    for path in our_files:
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        body = strip_comments(read(path))

        for parent in re.findall(r'\bParentName\s*=\s*"([^"]+)"', body):
            if parent not in known:
                unresolved.append("%s inherits ParentName %r, which no loaded def declares" % (rel, parent))

        for tag in DEF_TAGS:
            for value in re.findall(r"<%s>([^<]+)</%s>" % (tag, tag), body):
                value = value.strip()
                if value and value not in known:
                    unresolved.append("%s names <%s>%s</%s>, which resolves to nothing" % (rel, tag, value, tag))

        for wrapper in DEF_LISTS:
            for block in re.findall(r"<%s>(.*?)</%s>" % (wrapper, wrapper), body, re.S):
                for value in re.findall(r"<li>([^<]+)</li>", block):
                    value = value.strip()
                    # PlaceWorkers and ITabs are types, not defs, and are not resolvable here.
                    if wrapper in ("placeWorkers", "inspectorTabs", "modExtensions", "thingSetMakerTags"):
                        continue
                    if value and value not in known:
                        unresolved.append("%s lists %r inside <%s>, which resolves to nothing"
                                          % (rel, value, wrapper))

        for wrapper in CHILD_NAME_DEF_WRAPPERS:
            for block in re.findall(r"<%s>(.*?)</%s>" % (wrapper, wrapper), body, re.S):
                for child in re.findall(r"<(\w+)>", block):
                    if child not in known:
                        unresolved.append("%s builds from %r inside <%s>, which is not a thing def"
                                          % (rel, child, wrapper))

        for named in re.findall(r'Class\s*=\s*"([^"]+)"', body) + re.findall(r"<thingClass>([^<]+)</thingClass>", body) \
                + re.findall(r"<compClass>([^<]+)</compClass>", body):
            named = named.strip()
            if OUR_NAMESPACE not in named:
                continue
            short = named.rsplit(".", 1)[-1]
            if named not in our_types and short not in our_types:
                unresolved.append("%s names our type %r, which this package's source does not "
                                  "declare. An unresolvable class discards the WHOLE def." % (rel, named))

    if unresolved:
        for problem in sorted(set(unresolved)):
            fail(problem)
    else:
        notes.append("every ParentName, def reference and Rimrooms type in the shipped defs resolves")

    print("def references")
    for note in notes:
        print("  note: %s" % note)

    if problems:
        print("")
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1

    print("")
    print("PASS: every def name this package references exists in the game or in this package")
    return 0


if __name__ == "__main__":
    sys.exit(main())
