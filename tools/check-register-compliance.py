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

  * **Every declared dependency is one a mod manager can act on.** This rule previously read
    *"About.xml must declare no modDependencies; the package has to load and run against Core
    alone"*. **The owner overruled that on 2026-10-01:** *"the mod DOES HAVE HARD DEPENDANCIES SO
    GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and
    *"WE ARE USING ALL OF THEM"*. The old rule was a fair reading of the register's guidance, and
    the register is **guidance, not law** by the owner's own standing correction, so an owner
    decision supersedes it. What is checked now is that each declaration is usable: a
    `displayName` because a manager shows it, a URL on anything that is not an expansion, and
    **a matching `loadAfter` entry** -- a requirement without an ordering constraint is how this
    package came to sit at position 197 of 296 with 99 mods loading after it.
  * **Every mod this package patches is a reviewed register row.** Patching something nobody
    reviewed is how an unreviewed assumption ships.
  * **Every foreign-mod patch sits inside `PatchOperationFindMod`.** Invariant 42: a target inside
    `FindMod` is optional by construction and applies nothing when the mod is absent. A patch
    outside one is a hard dependency wearing a different hat.
  * **Def types the register steered this mod away from are not authored.** Three separate reviews
    reached the same structural conclusion -- use our own def types rather than the native systems
    those mods operate on -- and that is what keeps this package clear of them:

        row 148 No Quests Without Comms, row 132 MFI     -> no `QuestScriptDef`
        (and a standing project rule)                    -> no `StorytellerDef`, ever

    **`ResearchProjectDef` was on that list until 0.12.99-dev and the register is what removed it.**
    The steer read *"rows 191 ResearchTree and 279 Research Whatever operate on this type; this mod
    uses its own RimroomsProjectDef so neither can see it"* -- and the owner then opened the Research
    tab, found nothing from this mod, and said so in capitals. Reading the two cards shows they ask
    for the opposite: row 191's planned use is that *"The Backrooms tree should own gate, mapping,
    containment, and spatial-analysis milestones and should not overwrite other research trees"*,
    with *"stable definitions and an independent route"*. Being seen by those mods was the goal all
    along. **A prohibition became four assertions**, which is strictly stronger: our own tab, a
    self-contained graph, one mirror per project with its fields agreeing
    (`tools/check-research-mirror.py`), and the sync still running both ways so the Operations insight
    route remains the independent one.

Nothing here is a judgement about another mod. Every check is about **this** package.

Run from the repository root. Exits non-zero on a regression.
"""
import io
import csv
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
    declared_blocks = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    rows = []
    for block in declared_blocks:
        rows += re.findall(r"<li>(.*?)</li>", block, re.S)

    after = re.findall(r"<loadAfter>(.*?)</loadAfter>", text, re.S)
    load_after = []
    for block in after:
        load_after += [v.strip() for v in re.findall(r"<li>([^<]+)</li>", block)]
    load_after_keys = set(v.lower() for v in load_after)

    own = re.search(r"<packageId>([^<]+)</packageId>", text)
    own_key = own.group(1).strip().lower() if own else None

    entries = []
    for row in rows:
        package = re.search(r"<packageId>([^<]+)</packageId>", row)
        if package is None:
            fail("a modDependencies entry declares no packageId")
            continue
        key = package.group(1).strip()
        entries.append({
            "id": key,
            "key": key.lower(),
            "display": (re.search(r"<displayName>([^<]+)</displayName>", row) or [None])
                       and re.search(r"<displayName>([^<]+)</displayName>", row),
            "url": re.search(r"<(?:steamWorkshopUrl|downloadUrl)>([^<]+)</", row),
        })

    if not entries:
        # Still legal, and worth a note rather than a pass in silence: a package that declares
        # nothing is one a manager cannot sort or warn about.
        notes.append("no hard mod dependencies declared")
    else:
        seen = {}
        for entry in entries:
            seen[entry["key"]] = seen.get(entry["key"], 0) + 1
        duplicates = sorted(k for k, n in seen.items() if n > 1)
        if duplicates:
            fail("About.xml declares the same dependency twice: %s" % ", ".join(duplicates))

        if own_key and own_key in seen:
            fail("About.xml declares itself as its own dependency (%s)" % own_key)

        if "ludeon.rimworld" in seen:
            fail("Core is declared as a mod dependency. Core is always present; it belongs in "
                 "loadAfter, not in modDependencies")

        nameless = [e["id"] for e in entries if e["display"] is None]
        if nameless:
            fail("%d dependency row(s) carry no displayName, which is the text a mod manager "
                 "shows the player: %s" % (len(nameless), ", ".join(sorted(nameless)[:8])))

        # An expansion needs no URL: a player who lacks one cannot be sent to a Workshop page
        # for it. Everything else must be findable.
        unreachable = [e["id"] for e in entries
                       if e["url"] is None and not e["key"].startswith("ludeon.rimworld")]
        if unreachable:
            fail("%d dependency row(s) give the player no way to obtain the mod: %s"
                 % (len(unreachable), ", ".join(sorted(unreachable)[:8])))

        unordered = [e["id"] for e in entries if e["key"] not in load_after_keys]
        if unordered:
            fail("%d dependency row(s) are required but never ordered -- no loadAfter entry, so "
                 "this package may load before a mod it depends on: %s"
                 % (len(unordered), ", ".join(sorted(unordered)[:8])))

        if not (duplicates or nameless or unreachable or unordered):
            expansions = [e for e in entries if e["key"].startswith("ludeon.rimworld")]
            notes.append("%d hard dependencies declared (%d expansions, %d mods); every one "
                         "carries a displayName, a way to obtain it, and a matching loadAfter"
                         % (len(entries), len(expansions), len(entries) - len(expansions)))

    if "ludeon.rimworld" not in load_after_keys:
        fail("loadAfter does not name Core. Every package loads after Core and saying so is how "
             "a sorting manager knows where the floor is")
    else:
        notes.append("loadAfter names Core plus %d other entries" % (len(load_after) - 1))

# ------------------------------------------------- 1b. the load order carries the whole profile
# **A PLANT FOUND THIS GAP AND THE CHANGE ABOVE CREATED IT.** Owner, 2026-10-03: *"rework mod to
# not need any depeancie mods"*, *"we hope to have the mod as a complete stand alone"*. The 293
# hard dependencies came out of `About.xml` at 0.12.86-dev, and that was only safe because every
# one of them was already in `loadAfter`.
#
# So the rule above -- every declared dependency must also be ordered -- now has nothing to
# iterate, and `loadAfter` became the one thing carrying the whole weight and the one thing
# nobody checked. `plant-dependencies.py` reported MISSED when a former dependency was deleted
# from the order and not a single checker objected.
#
# **The cost is measured, not hypothetical.** Our mod sat at position 197 of 296 in the owner's
# live load order with 99 mods loading after it. A mod that loads before the defs it reads
# produces a null somewhere unrelated; it does not announce itself.
#
# Keyed to the register rather than to a literal count, so adding a mod to the profile updates
# this rule by updating the register.
profile = os.path.join(REPO, "docs", "research", "installed-mod-metadata-2026-09-27.csv")
if not os.path.isfile(profile):
    fail("the installed-mod metadata register is missing, so the load order cannot be checked "
         "against the profile it is meant to cover")
else:
    with io.open(profile, encoding="utf-8-sig") as handle:
        register_ids = set()
        for row in csv.DictReader(handle):
            value = (row.get("PackageID") or "").strip().lower()
            if value:
                register_ids.add(value)
    if not register_ids:
        fail("the installed-mod metadata register declares no PackageID column values")
    else:
        ordered = set(v.lower() for v in load_after)
        unordered = sorted(register_ids - ordered)
        strangers = sorted(ordered - register_ids)
        if unordered:
            fail("%d profile mod(s) are in the register and NOT in loadAfter, so this package "
                 "can load before them: %s" % (len(unordered), ", ".join(unordered[:8])))
        if strangers:
            fail("%d loadAfter entry/entries are not in the profile register, so nobody can say "
                 "what they are for: %s" % (len(strangers), ", ".join(strangers[:8])))
        if not unordered and not strangers:
            notes.append("loadAfter matches the %d-mod profile register exactly"
                         % len(register_ids))

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
# **ENUMERATED FROM THE FILES, NOT GUESSED, and the first draft proved why.** It listed
# `thingDef` and missed `<thing>` -- which is 114 of the 171 def references in `RR_Starts.xml`.
# A hand-planted foreign def sailed straight through and the rule reported PASS, which is the
# same defect class as the density tool counting zero and printing a number. These are every
# leaf tag in the two shipped start files whose value is a def name.
DEF_TAGS = ("thing", "thingDef", "def", "stuff", "wallStuff", "floor", "floorTerrain",
            "outdoorTerrain", "terrainDef", "floorDef", "pawnKindDef", "factionDef",
            "researchDef", "recipeDef", "startDef")
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

# ------------------------------------------------- the research mirror the register asked for
# **A PROHIBITION BECAME AN ASSERTION, and the register is what reversed it.**
#
# `STEERED` carried `ResearchProjectDef` since 0.5.x with the reason *"rows 191 ResearchTree and 279
# Research Whatever operate on this type; this mod uses its own RimroomsProjectDef so neither can see
# it"*. That steer was over-cautious, and the owner's report is what exposed it: they opened the
# Research tab, found nothing, and said so in capitals.
#
# **Read the two cards and they ask for the opposite of the steer.** Row 191's planned use:
# *"The Backrooms tree should own gate, mapping, containment, and spatial-analysis milestones and
# should not overwrite other research trees"*, and *"Backrooms milestones need stable definitions and
# an independent route when optional trees are absent."*
#
# So being seen by those mods was always the goal. What the register actually forbids is **crowding
# somebody else's tree** and **losing the independent route** -- and both are now asserted rather
# than avoided by shipping nothing:
#
#   * our own tab, so vanilla's tree is untouched
#   * a self-contained prerequisite graph, so no research mod draws ours through vanilla's
#   * one mirror per company project, label, description and graph agreeing
#   * the Operations insight route still completes a project with the Research tab untouched
#
# The first three are `tools/check-research-mirror.py`, checker 26. The fourth is here, because it is
# a statement about this package's own code rather than about its defs.
research_sync = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "ResearchMirror.cs")
if not os.path.isfile(research_sync):
    fail("the research mirror ships defs with no sync, so finishing one in the Research tab would "
         "unlock nothing. See check-research-mirror.py for the pairing rules.")
else:
    sync = io.open(research_sync, encoding="utf-8-sig").read()
    if "MarkResearchedExternally" not in sync or "FinishProject" not in sync:
        fail("the research mirror sync no longer runs both ways. One direction missing means either "
             "the Research tab unlocks nothing, or Operations leaves the tab offering work that is "
             "already done -- both are the tab lying to a player.")
    else:
        notes.append("research mirror syncs both ways; the Operations insight route is unchanged "
                     "and remains the independent one row 191 asks for")

# ------------------------------------------- the register's own one-word column may not contradict
# **THIS IS THE "NEEDS 294 MODS" DEFECT IN THE ONE PLACE NOBODY CHECKED.** `About.xml` has declared
# zero `modDependencies` since 0.12.86-dev, and five live documents still said otherwise until
# 0.12.95-dev. The register was not one of them -- but its `stance` column still read **Required**
# for three rows, and that column is what a reader filters on.
#
# The three cards were *precise*: Harmony is required by RimWorld Together and by several selected
# frameworks, **not by us**; Vanilla Expanded Framework is required by the Gravship Expanded chain,
# **not by us**. A one-word summary cannot carry *"required by something else in the profile"*, so
# it said the opposite of what its own card said -- and a reader who filters the register by
# `stance=Required` and finds three rows concludes this mod needs three mods.
#
# **Core is exempt by name, and only Core.** It is the game, not a mod, and nobody reading
# *"Core: Required"* is misled. Every other row must be Optional, Configuration only, Visual only
# or No integration while the package declares no dependencies.
CORE_ROW_EXEMPT = "core"
required_rows = [r for r in rows
                 if r["stance"].strip() == "Required"
                 and r["mod"].strip().lower() != CORE_ROW_EXEMPT]
if required_rows:
    for row in required_rows:
        fail("register row %s (%r) has stance 'Required' while About.xml declares no "
             "modDependencies. That column is what a reader filters on, and it cannot carry "
             "'required by something ELSE in the profile' -- which is what this row's own card "
             "says. Set the stance to Optional and leave the qualifier in the card."
             % (row["load"].strip(), row["mod"].strip()))
else:
    notes.append("no register row claims this package requires a mod; Core is the only Required "
                 "row and Core is the game")

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
