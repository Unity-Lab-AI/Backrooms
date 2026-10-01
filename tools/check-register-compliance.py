# -*- coding: utf-8 -*-
"""Verify the build against what the mod register says about using other people's mods.

Why this exists
---------------
Owner direction, 2026-09-29, verbatim:

    "now that you can actually read the registar that ive been telling to to use make sure
     nothing regressed in the build that it mentions how those mods are to be use by ours"

and immediately after, correcting how the register should be treated:

    "remmebr its not law but guidance"

So this checker does **not** veto work because a register row exists. It verifies the small number
of dispositions the register states about *how this mod may use other mods* -- the ones that are
structural rather than advisory, and that would regress silently:

  * **No hard dependency on any mod.** `About.xml` must declare no `modDependencies`. The package
    has to load and run against Core alone. This is the one that matters most, because it is the
    difference between "works with the 294" and "requires some of them".
  * **Every mod this package patches is a reviewed register row.** Patching something nobody
    reviewed is how an unreviewed assumption ships.
  * **Every foreign-mod patch sits inside `PatchOperationFindMod`.** Invariant 42: a target inside
    `FindMod` is optional by construction and applies nothing when the mod is absent. A patch
    outside one is a hard dependency wearing a different hat.
  * **Def types the register steered this mod away from are not authored.** Three separate reviews
    reached the same structural conclusion -- use our own def types rather than the native systems
    those mods operate on -- and that is what keeps this package clear of them:

        row 191 ResearchTree, row 279 Research Whatever  -> no `ResearchProjectDef`
        row 148 No Quests Without Comms, row 132 MFI     -> no `QuestScriptDef`
        (and a standing project rule)                    -> no `StorytellerDef`, ever

Nothing here is a judgement about another mod. Every check is about **this** package.

Run from the repository root. Exits non-zero on a regression.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
TOOLS = os.path.join(REPO, "tools")

problems = []
notes = []


def fail(message):
    problems.append(message)


def strip_xml_comments(text):
    """XML comments out, so a rule never matches the prose explaining it."""
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def register_rows():
    """Reuse the register parser rather than writing a second one that can disagree with it."""
    sys.path.insert(0, TOOLS)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "register_query", os.path.join(TOOLS, "register-query.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.rows()
    except Exception as exception:          # pragma: no cover - reported, never swallowed
        fail("the register could not be parsed: %s" % exception)
        return []


def package_xml_files():
    found = []
    for root, _dirs, files in os.walk(MOD):
        for name in files:
            if name.lower().endswith(".xml"):
                found.append(os.path.join(root, name))
    return sorted(found)


# ---------------------------------------------------------------- 1. no hard dependency
about = os.path.join(MOD, "About", "About.xml")
if not os.path.isfile(about):
    fail("About.xml is missing")
else:
    text = read(about)
    declared = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    entries = []
    for block in declared:
        entries += re.findall(r"<packageId>([^<]+)</packageId>", block)
    if entries:
        fail("About.xml declares hard mod dependencies: %s. The package must load and run "
             "against Core alone." % ", ".join(entries))
    else:
        notes.append("no hard mod dependencies declared")

    after = re.findall(r"<loadAfter>(.*?)</loadAfter>", text, re.S)
    load_after = []
    for block in after:
        load_after += [v.strip() for v in re.findall(r"<li>([^<]+)</li>", block)]
    unexpected = [v for v in load_after if v.lower() != "ludeon.rimworld"]
    if unexpected:
        notes.append("loadAfter names beyond Core: %s (ordering only, not a dependency)"
                     % ", ".join(unexpected))
    else:
        notes.append("loadAfter names Core only")

# ---------------------------------------------------------------- 2/3. patched mods
rows = register_rows()
register_names = {}
for row in rows:
    register_names[row["mod"].strip().lower()] = row

patched = set()
for path in package_xml_files():
    text = read(path)
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    for block in re.findall(r"<Operation[^>]*PatchOperationFindMod.*?</Operation>", text, re.S):
        for name in re.findall(r"<li>([^<]+)</li>", block):
            patched.add((name.strip(), rel))
    # A foreign mod named anywhere in a patch file but NOT inside a FindMod block is the
    # regression this catches: the patch would apply unconditionally.
    if "PatchOperationFindMod" in text:
        continue
    if os.sep + "Patches" + os.sep not in path:
        continue
    for name in re.findall(r"<mods>\s*<li>([^<]+)</li>", text):
        fail("%s names mod %r outside a PatchOperationFindMod; the patch would apply "
             "unconditionally" % (rel, name.strip()))

for name, rel in sorted(patched):
    row = register_names.get(name.lower())
    if row is None:
        fail("%s patches %r, which is not a reviewed register row" % (rel, name))
    else:
        notes.append("patches %r -- row %s, %s, %s, trace %s"
                     % (name, row["load"].strip(), row["stance"].strip(),
                        row["firmness"].strip(), row["trace"].strip()))

if not patched:
    notes.append("this package patches no other mod at all")

# ---------------------------------------------------------------- 4. def types steered away from
STEERED = {
    "ResearchProjectDef": "rows 191 ResearchTree and 279 Research Whatever operate on this type; "
                          "this mod uses its own RimroomsProjectDef so neither can see it",
    "QuestScriptDef": "rows 148 No Quests Without Comms and 132 More Faction Interaction operate "
                      "on native quests; this mod uses its own request defs and an Operations pane",
    "StorytellerDef": "a StorytellerDef is an exclusive slot -- shipping one would ask a player to "
                      "give up Cassandra to play this mod",
}
defs_root = os.path.join(MOD, "1.6", "Defs")
for def_type, reason in sorted(STEERED.items()):
    offenders = []
    for path in package_xml_files():
        if not path.startswith(defs_root):
            continue
        if re.search(r"<%s[\s>]" % re.escape(def_type), read(path)):
            offenders.append(os.path.relpath(path, REPO).replace(os.sep, "/"))
    if offenders:
        fail("this package authors %s in %s. %s" % (def_type, ", ".join(offenders), reason))
    else:
        notes.append("authors no %s" % def_type)

# ---------------------------------------------------------------- 5. their files are never touched
# Owner direction, standing and restated 2026-09-29: "remmebr we dont change the mods we dont have
# rights to edit 274 or sum mods", and earlier "WE ARE NOT EDITING OTHER PEOPLES MODS!".
#
# A PatchOperationFindMod does NOT edit their files -- the owner confirmed that reading explicitly.
# It patches the loaded def database at runtime, and applies nothing when the mod is absent. What
# WOULD breach the direction is this repository containing, shipping or rewriting another mod's
# content, so that is what is checked: every file this package ships belongs to this package.
FOREIGN_MARKERS = ("steamapps", "294_profile_copy", "vendored", "thirdparty", "third-party")
foreign = []
for path in package_xml_files():
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    lowered = rel.lower()
    if any(marker in lowered for marker in FOREIGN_MARKERS):
        foreign.append(rel)

# And the package must contain no other mod's About.xml, which is the unambiguous sign that
# somebody else's mod has been copied in.
for root, _dirs, files in os.walk(MOD):
    for name in files:
        if name.lower() != "about.xml":
            continue
        found = os.path.join(root, name)
        if os.path.normpath(found) != os.path.normpath(about):
            foreign.append(os.path.relpath(found, REPO).replace(os.sep, "/"))

if foreign:
    fail("this package ships files that are not its own: %s. Another mod's content must never be "
         "copied, shipped or rewritten here." % ", ".join(sorted(set(foreign))))
else:
    notes.append("every shipped file belongs to this package; no other mod's content is present")

# ------------------------------------------------ 5b. the last seven families, swept 0.12.42-dev
#
# Rows 206 and 302 asked for a retroactive sweep of every system family. Fourteen were swept
# between 0.10.4-dev and 0.12.33-dev; the last seven -- medical, world operations, cargo,
# hospitality, materials, visitor economy, staff psychology -- collapse into **five family strings**
# in the register, because the register groups two or three names per family.
#
# Every one of the five turned out to be **already honoured**, which is worth stating plainly
# rather than dressing up: no code changed. What DID change is that four of the five rules were
# satisfied by nothing but the current shape of the package, and a rule with no check behind it is
# a promise. So the sweep's product is these assertions.
#
# Each rule is quoted from the family's own Integration Approach, with the row it came from.
#
# The one that is worth reading twice: the medical family's rule is *"the core expedition loop must
# not require one medical or Biotech mod to treat a pawn"*, and **0.12.41-dev came within one
# decision of breaking it.** The crew planner reports a crew with no medical skill as a gap and
# does **not** refuse the dispatch. Had that gap been a refusal -- which is the obvious way to
# write it -- the expedition loop would have required a medic, and on a profile where a medical mod
# owns treatment that is a requirement on that mod. It was written as advisory for a different
# reason, and the register independently requires it.
PATCH_STEERED = {
    "ThoughtDef": "row 2 SF Grim Reality: \"Keep any future company thoughts isolated and "
                  "additive; do not overwrite its thought definitions.\" This package authors one "
                  "ThoughtDef of its own and patches none",
    "TraderKindDef": "row 17 [KV] Call Trade Ships: \"Leave calls and trader options on the "
                     "existing Comms Console; no Rimrooms trade-ship override planned.\" The "
                     "corporate trader is a new TraderKindDef reached through a gizmo on Core's "
                     "own console",
    "HediffDef": "the medical family, rows 23-272: \"The core expedition loop must not require "
                 "one medical or Biotech mod to treat a pawn.\" This package has no HediffDefs "
                 "folder at all, and the only medical reference in the expedition code is "
                 "SkillDefOf.Medicine, read to report a gap and never to refuse a dispatch",
    "MainButtonDef": "the hospitality family, rows 62-286: test state changes \"instead of "
                     "replacing their native menus.\" Row 821's company-first layout is this "
                     "package's own button's order field and nothing else",
}
patches_root = os.path.join(MOD, "1.6", "Patches")
for def_type, reason in sorted(PATCH_STEERED.items()):
    offenders = []
    for path in package_xml_files():
        if not path.startswith(patches_root):
            continue
        if re.search(r"\b%s\b" % re.escape(def_type), read(path)):
            offenders.append(os.path.relpath(path, REPO).replace(os.sep, "/"))
    if offenders:
        fail("a patch in this package names %s (%s). %s"
             % (def_type, ", ".join(offenders), reason))
    else:
        notes.append("patches no %s" % def_type)

# The materials and cargo family, rows 52-228: *"Preserve each mod's normal material and weight
# behavior; add only a Backrooms cargo manifest and appraisal layer."* Setting a mass on **our own**
# def is normal and is not what the rule is about; altering **theirs** is. So the check is on the
# patches, where a stat override would have to live.
mass_patches = []
for path in package_xml_files():
    if not path.startswith(patches_root):
        continue
    # **COMMENTS STRIPPED FIRST.** This matched the word `statBases` inside the comment of a patch
    # explaining that the face value *cannot* be a statBases entry -- so the patch was refused for
    # saying what it does not do. **Fifth instance of a checker reading its own explanatory
    # prose**, and the precedent is documented: `check-compliance.py` strips XML comments since
    # 0.12.46-dev, where it flagged a patch for containing `PatchOperationReplace` in the comment
    # explaining why a replace is wrong. A checker that tests for MENTION rather than for the
    # thing itself cries wolf, and this battery has now had five.
    if re.search(r"<Mass>|statBases", strip_xml_comments(read(path))):
        mass_patches.append(os.path.relpath(path, REPO).replace(os.sep, "/"))
if mass_patches:
    fail("a patch in this package alters stat bases (%s). The materials and cargo family, rows "
         "52-228: \"Preserve each mod's normal material and weight behavior\" -- every mass this "
         "package reads comes from the item's own StatDefOf.Mass or from MassUtility"
         % ", ".join(mass_patches))
else:
    notes.append("no patch alters another def's stat bases")

# ---------------------------------------------------------------- 6. no new gameplay art
# Invariant 10: no new gameplay ThingDef, PawnKindDef, art or audio. Original main-menu images are
# the single declared exception, so the rule is checkable as a shape rather than a count: every PNG
# this package ships is a menu slide, and nothing else.
#
# Closed at 0.12.22-dev, when the last four gameplay textures were replaced with paths enumerated
# out of Core's own defs. Before that, four shipped and each was a real breach nothing asserted.
MENU_PREFIX = "1.6/Textures/UI/Menu/"
gameplay_art = []
for root, _dirs, files in os.walk(MOD):
    for name in files:
        if not name.lower().endswith((".png", ".jpg", ".jpeg", ".wav", ".ogg", ".mp3")):
            continue
        rel = os.path.relpath(os.path.join(root, name), MOD).replace(os.sep, "/")
        if rel.startswith(MENU_PREFIX):
            continue
        if rel.startswith("About/"):
            continue          # the mod's own preview and icon, which every mod must ship
        gameplay_art.append(rel)

if gameplay_art:
    fail("this package ships gameplay art or audio: %s. Invariant 10 permits original MENU images "
         "only; every other texture must name a path Core or an installed mod already ships."
         % ", ".join(sorted(gameplay_art)))
else:
    notes.append("ships no gameplay art or audio; menu images only")

# ---------------------------------------------------------------- report
print("register compliance")
for note in notes:
    print("  note: %s" % note)
print("  register rows parsed: %d" % len(rows))

if problems:
    print("")
    print("FAIL: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    sys.exit(1)

print("")
print("PASS: the build honours the register's structural guidance on using other mods")
