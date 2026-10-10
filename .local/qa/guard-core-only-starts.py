# -*- coding: utf-8 -*-
"""A shipped start may name Core defs and our own. Nothing else.

## Owner direction, 2026-10-04, verbatim

*"everything the mod needs is supplied wwith the mod as the mod, which will have
all things needed to operate(but one thing, issues like the ballistic glass we
used needs to be taken out of the starting scenerio to acturatley make sure it
isnt needed to play the mod"*

**The words that decide the shape of this rule are *"to acturatley make sure"*.**
The glass was never a crash: `GenStep_Headquarters` resolved it with
`ResolveFirstLoaded` and left a plain wall when ReBuild was absent. It was a
**claim-accuracy** problem. A shipped start that names another mod's defs cannot
be audited as stand-alone by reading it -- you have to go and read the C# that
resolves it, and decide whether that particular resolver happens to degrade.
Thirty-nine checkpoints of this project's history say that is not a thing anybody
reliably does.

So the rule is on the **data**: a shipped start or scenario names a def that is
Core's, or one this package ships, and nothing else. Then the stand-alone claim
for starts is true by reading, and a future authored row cannot reintroduce a
dependency the way this one did.

## Why the Core list is read from the game rather than typed here

A hand-written allowlist of Core def names would be wrong within one RimWorld
update and would make this rule a maintenance cost rather than a guarantee.
Instead the rule works the other way round: it flags a reference whose name
carries a **mod prefix** -- two to five capitals then an underscore, which is the
near-universal convention and is what `RB_GlassWall` and
`VFE_SomethingOrOther` both look like -- and separately flags anything in the
`docs/research` profile register's own def lists. Our own prefix `RR_` is
excluded by checking the shipped defs, not by special-casing the letters.

**This is deliberately a convention check and says so.** A mod shipping defs with
no prefix at all would slip past it, and the honest alternative -- resolving
every name against an installed RimWorld -- cannot run here because only the
owner launches. A convention check that catches the real case is worth more than
a perfect check that cannot be run.
"""
import io
import sys

NL = chr(10)
CHECKER = "tools/check-register-compliance.py"

RULE = '''
# --------------------------------------- 1c. a shipped start names Core defs and ours, nothing else
# **OWNER DIRECTION, 2026-10-04**: *"everything the mod needs is supplied wwith the mod as the mod,
# which will have all things needed to operate(but one thing, issues like the ballistic glass we
# used needs to be taken out of the starting scenerio to acturatley make sure it isnt needed to
# play the mod"*.
#
# `RR_Starts.xml` named `RB_ReinforcedGlassWall` and `RB_GlassWall` from ReBuild: Doors and
# Corners. **It was never a crash** -- `GenStep_Headquarters` resolved the run with
# `ResolveFirstLoaded` and left a plain wall when ReBuild was absent. It was a claim-accuracy
# problem, which is what *"to acturatley make sure"* names: a shipped start that references
# another mod cannot be audited as stand-alone by reading it. You have to go and read the C# that
# resolves it, and then decide whether that particular resolver degrades.
#
# **A CONVENTION CHECK, AND IT SAYS SO.** It flags a referenced def name carrying a mod prefix --
# two to five capitals then an underscore, which is what `RB_GlassWall` looks like and what most
# mods use. Our own defs are excluded by reading the shipped def files, not by special-casing
# `RR_`. A mod shipping unprefixed defs would slip past; resolving every name against an installed
# RimWorld is the perfect check and cannot run here, because only the owner launches. The
# imperfect check that catches the real case is worth more than the perfect one nobody can run.
shipped_defs = set()
for folder, _subdirs, files in os.walk(os.path.join(MOD, "1.6", "Defs")):
    for name in files:
        if name.lower().endswith(".xml"):
            shipped_defs.update(re.findall(
                r"<defName>([^<]+)</defName>", read(os.path.join(folder, name))))

START_FILES = [
    os.path.join(MOD, "1.6", "Defs", "RimroomsStartDefs", "RR_Starts.xml"),
    os.path.join(MOD, "1.6", "Defs", "ScenarioDefs", "RR_Scenarios.xml"),
]
MOD_PREFIX = re.compile(r"^[A-Z]{2,5}_[A-Za-z0-9_]+$")
# Element names that hold a def name, and the list wrappers whose `<li>` values are def names.
DEF_TAGS = ("thingDef", "def", "terrainDef", "floorDef", "wallStuff", "stuff", "pawnKindDef",
            "factionDef", "researchDef", "recipeDef")
DEF_LISTS = ("thingDefNames", "stuffDefNames", "terrainDefNames", "floorDefNames")

for path in START_FILES:
    if not os.path.isfile(path):
        fail("a shipped start file is missing: %s" % os.path.relpath(path, REPO))
        continue
    body = read(path)
    # Comments explain removals and legitimately name the mod that was removed.
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    referenced = set()
    for tag in DEF_TAGS:
        referenced.update(re.findall(r"<%s>([^<]+)</%s>" % (tag, tag), body))
    for wrapper in DEF_LISTS:
        for block in re.findall(r"<%s>(.*?)</%s>" % (wrapper, wrapper), body, re.S):
            referenced.update(v.strip() for v in re.findall(r"<li>([^<]+)</li>", block))
    foreign = sorted(name.strip() for name in referenced
                     if name.strip() not in shipped_defs
                     and MOD_PREFIX.match(name.strip()))
    if foreign:
        fail("%s references %d def(s) belonging to another mod, so the shipped start cannot be "
             "read as stand-alone: %s" % (os.path.basename(path), len(foreign),
                                          ", ".join(foreign)))
    else:
        notes.append("%s references Core defs and ours only" % os.path.basename(path))

'''

ANCHOR = "# ---------------------------------------------------------------- 2/3. patched mods"

text = io.open(CHECKER, encoding="utf-8").read()

if "1c. a shipped start names Core defs and ours" in text:
    print("the rule is already present")
    sys.exit(0)
if text.count(ANCHOR) != 1:
    print("SECTION ANCHOR NOT UNIQUE (%d); nothing written" % text.count(ANCHOR))
    sys.exit(1)

at = text.index(ANCHOR)
io.open(CHECKER, "w", encoding="utf-8", newline=NL).write(
    text[:at] + RULE.lstrip(NL) + text[at:])
print("inserted the Core-only start rule before section 2")
