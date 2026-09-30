# -*- coding: utf-8 -*-
"""Assert the seven universe factions break no founding rule and touch no world generation.

The property this exists for
---------------------------
A `FactionDef` is the one kind of new Def this project permits, and the owner authorised these
explicitly on 2026-09-28: new `FactionDef`s **reusing existing pawn kinds and existing faction
icon paths**, because a faction is world configuration rather than a physical gameplay Def.

That permission is narrow, and three things would quietly widen it:

  * **A pawn kind that is not Core's.** The moment a `kindDef` option names something this mod
    authored, the exemption stops being about world configuration and invariant 10 is broken.
  * **An icon path Core does not already use.** Same failure through the art door, and it would
    fail at runtime rather than at load, because `ContentFinder` returns null for a missing
    texture and the faction simply has no icon.
  * **settlementGenerationWeight above zero.** This mod exists to work alongside 294 others.
    Seven settlement-generating factions would change every world map every player generates,
    for everyone, for ever. These groups have people and intentions, not towns.

And one that would break an owner answer:

  * **permanentEnemy.** Owner-answered: **all seven begin neutral** and hostility is earned by
    what the branch actually does. There is no starting-goodwill field on `FactionDef`, so
    neutrality is achieved by NOT setting something -- which is exactly the kind of correctness
    that decays silently, because nothing looks wrong when a flag appears.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
FACTIONS = os.path.join(MOD, "Defs", "FactionDefs", "RR_UniverseFactions.xml")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# ------------------------------------------------------------------ enumerate the installed game
# Invariant 19: never trust a remembered list against shipped game data. Enumerate.
core_pawn_kinds = set()
core_icon_paths = set()
for path in glob.glob(os.path.join(GAME, "**", "*.xml"), recursive=True):
    try:
        text = io.open(path, encoding="utf-8-sig").read()
    except Exception:
        continue
    if "PawnKindDef" in text:
        for match in re.finditer(r"<defName>([A-Za-z0-9_]+)</defName>", text):
            core_pawn_kinds.add(match.group(1))
    for match in re.finditer(r"<factionIconPath>([^<]+)</factionIconPath>", text):
        core_icon_paths.add(match.group(1).strip())

check("the installed game was enumerated",
      len(core_pawn_kinds) > 100 and len(core_icon_paths) >= 5,
      "-- found %d def names and %d icon paths; without real data every claim below is vacuous"
      % (len(core_pawn_kinds), len(core_icon_paths)))

# ------------------------------------------------------------------ our own factions
root = ET.parse(FACTIONS).getroot()
concrete = [node for node in root.findall("FactionDef")
            if node.get("Abstract") != "True" and node.findtext("defName")]
abstract = [node for node in root.findall("FactionDef") if node.get("Abstract") == "True"]

names = [node.findtext("defName").strip() for node in concrete]
print("factions: %s" % ", ".join(names))
check("seven concrete universe factions ship",
      len(concrete) == 7,
      "-- found %d; the owner named six and asked for further factions in the same vein"
      % len(concrete))
check("they share one abstract base",
      len(abstract) == 1,
      "-- shared defaults in one place is what stops the seven drifting apart")

# ------------------------------------------------------------------ invariant 10: no new content
bad_kinds, bad_icons = [], []
for node in concrete:
    name = node.findtext("defName").strip()
    for option_set in node.findall("pawnGroupMakers/li/options"):
        for option in list(option_set):
            if option.tag not in core_pawn_kinds:
                bad_kinds.append("%s -> %s" % (name, option.tag))
    icon = (node.findtext("factionIconPath") or "").strip()
    if icon and icon not in core_icon_paths:
        bad_icons.append("%s -> %s" % (name, icon))

check("every pawn kind named is one the installed game already ships",
      not bad_kinds,
      "-- %s: authoring a pawn kind here breaks invariant 10 and voids the reason a FactionDef "
      "was permitted at all" % ", ".join(bad_kinds))
check("every faction icon path is one Core already uses",
      not bad_icons,
      "-- %s: a missing texture returns null from ContentFinder, so this fails at RUNTIME with no "
      "load error and the faction simply has no icon" % ", ".join(bad_icons))

# ------------------------------------------------------------------ world generation untouched
def inherited(node, field):
    """The field on the def, or on the single abstract base it inherits from."""
    own = node.findtext(field)
    if own is not None:
        return own.strip()
    for base in abstract:
        value = base.findtext(field)
        if value is not None:
            return value.strip()
    return None


bad_weight, bad_random, bad_count, bad_enemy = [], [], [], []
for node in concrete:
    name = node.findtext("defName").strip()
    if (inherited(node, "settlementGenerationWeight") or "1") != "0":
        bad_weight.append(name)
    if (inherited(node, "canMakeRandomly") or "true").lower() != "false":
        bad_random.append(name)
    if (inherited(node, "requiredCountAtGameStart") or "0") != "1":
        bad_count.append(name)
    if (inherited(node, "permanentEnemy") or "false").lower() != "false":
        bad_enemy.append(name)

check("no universe faction generates settlements",
      not bad_weight,
      "-- %s: seven settlement-generating factions would change every world map every player "
      "generates, alongside 294 other mods" % ", ".join(bad_weight))
check("no universe faction can be added randomly at world generation",
      not bad_random,
      "-- %s: world generation could add a second copy of a named organisation"
      % ", ".join(bad_random))
check("each universe faction exists exactly once at game start",
      not bad_count,
      "-- %s: a faction that is never created cannot be neutral, hostile, or anything else"
      % ", ".join(bad_count))
check("no universe faction is a permanent enemy",
      not bad_enemy,
      "-- %s: owner-answered, ALL SEVEN BEGIN NEUTRAL and hostility is earned from play"
      % ", ".join(bad_enemy))

# ------------------------------------------------------------------ hostility can mean something
thin = [node.findtext("defName").strip() for node in concrete
        if len(node.findall("pawnGroupMakers/li")) < 2]
check("every faction can field both a peaceful and a combat group",
      not thin,
      "-- %s: a faction that cannot arrive either way is a name on a list, so earning its "
      "hostility would change nothing observable" % ", ".join(thin))

# ------------------------------------------------------------------ the owner's words stay in TODO
# The recorded row says: "Verbatim owner wording is in TODO.md ... do not paraphrase it into def
# descriptions." So the owner's own phrasing must NOT appear in a description.
owner_phrases = ("disgruntleed", "high tech theives", "sbaatosh", "propietary",
                 "concerned citizens..", "this is 1990's")
descriptions = " ".join((node.findtext("description") or "") for node in concrete).lower()
leaked = [phrase for phrase in owner_phrases if phrase.lower() in descriptions]
check("no owner phrasing was paraphrased into a def description",
      not leaked,
      "-- %s: the row explicitly asked for this" % ", ".join(leaked))

# The period is prose, not a field: RimWorld has no year, and techLevel Industrial is the 1990s in
# its vocabulary. Assert the vocabulary rather than a date nobody can set.
bad_tech = [node.findtext("defName").strip() for node in concrete
            if (inherited(node, "techLevel") or "") != "Industrial"]
check("every universe faction is Industrial, which is the 1990s in RimWorld's vocabulary",
      not bad_tech,
      "-- %s" % ", ".join(bad_tech))

# ------------------------------------------------------------------ the period constrains grants
# Owner-answered 2026-09-28: the 1990s framing "also constrains starting grants", while research
# may still climb anywhere so no start is dead-ended. There is no year field, so the check is that
# no start GRANTS spacer-tier content. Research reaching it later is fine and deliberate.
ANACHRONISTIC = ("Glitterworld", "Bionic", "Archotech", "ChargeRifle", "ChargeLance",
                 "PowerArmor", "Persona", "Luciferium")
starts = io.open(os.path.join(MOD, "Defs", "RimroomsStartDefs", "RR_Starts.xml"),
                 encoding="utf-8-sig").read()
found = [token for token in ANACHRONISTIC if token in starts]
check("no start grants spacer-tier content, so the 1990s framing holds",
      not found,
      "-- %s: research may climb anywhere, but a START may not open with it" % ", ".join(found))

# ------------------------------------------------------------------ the package knows about it
allow = io.open(os.path.join(REPO, "tools", "package-files.json"), encoding="utf-8").read()
check("the faction file is on the package allowlist",
      "1.6/Defs/FactionDefs/RR_UniverseFactions.xml" in allow,
      "-- it would ship unauthorised, which check-package-integrity.py already refuses")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: seven factions, no new content, no world generation touched, all neutral")
