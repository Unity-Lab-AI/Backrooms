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
