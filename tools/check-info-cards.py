"""Refuse to ship a def a player can look at that has nothing to read.

Why this exists
---------------
Owner direction, 2026-09-29, verbatim:

    "we also need to be making sure all mod ingame decriptions and informational
     informations for everything is properly in the cards like the game does currently"

A player learns what a thing is by reading its card. A def of ours with a blank description
is a hole in that surface, and it is **invisible**: nothing errors, nothing logs, the card is
simply empty and the player concludes the mod is unfinished. Nobody re-reads 181 defs by
hand, which is the same argument that produced every other checker here.

"like the game does currently" is a measurable standard, not a matter of taste
-----------------------------------------------------------------------------
So it was measured, across Core's own 1,400-odd defs, rather than guessed:

    WorkGiverDef       label  97%   description   0%
    ThoughtDef         label   0%   description   0%   (its text lives in stages)
    PawnKindDef        label  91%   description   0%
    TraderKindDef      label  87%   description   0%
    ThingCategoryDef   label 100%   description   0%
    JobDef             label   0%   description   0%   (the player reads reportString)
    RecipeDef          label 100%   description 100%
    ThingDef           label  89%   description  75%
    ScenarioDef        label 100%   description  80%
    WorldObjectDef     label 100%   description  80%
    MainButtonDef      label 100%   description  92%

Core **never** describes a work giver, pawn kind, trader kind or thing category, and it
always describes a recipe. Demanding a description everywhere would not match the game; it
would just produce 67 lines of text no player will ever be shown. So the rule below follows
what the game actually does.

**Our own def types are different and are held to a higher bar**: they are ours, they appear
in our own windows, and a description on one of them is only worth writing because we also
render it. Every `RimroomsAsyncIndustries.*Def` must carry one.

Usage
-----
    python tools/check-info-cards.py
"""

import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")

# Never surfaced to a player at all.
EXEMPT = {
    "GenStepDef": "map generation plumbing; never surfaced to a player",
    "MapGeneratorDef": "map generation plumbing; never surfaced to a player",
    "ScenPartDef": "scenario machinery; the scenario's own text is what is read",
    "SoundDef": "audio cue; RimWorld shows no card for one",
    "RimroomsAsyncIndustries.Scenario.RimroomsStartDef":
        "branch setup data; the ScenarioDef beside it is what a player reads at the "
        "scenario picker, and duplicating that text here would show nobody anything",
}

# The player reads a report line, not a card. Core gives these no label either.
REPORT_STRING_TYPES = {"JobDef"}

# Text lives in the stages, exactly as Core does it: 0% of Core thoughts carry a top-level
# label or description, and every stage carries both.
STAGED_TYPES = {"ThoughtDef"}

# Core describes these, so we do.
DESCRIPTION_REQUIRED = {
    "ThingDef", "RecipeDef", "ScenarioDef", "WorldObjectDef", "MainButtonDef", "TerrainDef",
}

# Core labels these but never describes them. Requiring one would add text no player sees.
LABEL_ONLY = {
    "WorkGiverDef": "Core describes 0 of 105 work givers",
    "PawnKindDef": "Core describes 0 of 109 pawn kinds",
    "TraderKindDef": "Core describes 0 of 16 trader kinds",
    "ThingCategoryDef": "Core describes 0 of 74 thing categories",
}

# Whole-string placeholders, and text that merely *opens* with one. The second case was
# added after a planted "TODO Structural steel..." passed clean: a description that
# begins with TODO is unfinished text a player would be shown, not a finished sentence.
PLACEHOLDER = re.compile(r"^\s*(todo|tbd|tba|placeholder|description|label|n/?a|\.\.\.|-+)\s*$", re.I)
PLACEHOLDER_PREFIX = re.compile('^\\s*(todo|tbd|tba|fixme|xxx|placeholder)(?![A-Za-z])', re.I)


# --------------------------------------------------------------------------- #
# The vocabulary a player reads
# --------------------------------------------------------------------------- #
#
# Owner direction, 2026-09-29, verbatim: *"ive used alot of differnt terms for the gates..
# from portals, gates, doors , the machine, the gizmo, ect ect we need a unified name
# throught the entire mode in all the equipment information and cards of things items
# resources and buildings and all things that our mod touches"*.
#
# Answered at the fork as three words for three genuinely different things, because one word
# for all of them would have cost the game the ability to say which part failed:
#
#     GATE        the machine in your wall. Always a designated door.
#     CONNECTION  the live link a gate holds open to one coordinate.
#     THRESHOLD   the doorway you arrive at on the far side.
#
# "the gate is fine, the connection dropped" says something true and could not be said at
# all while both were called a portal.
#
# Key NAMES are deliberately not checked. A player never reads `RR_Portals_Heading`, and
# renaming keys is churn with real DefInjected risk for no reader benefit. Only what is
# displayed is held to the vocabulary.
BANNED_TERMS = {
    "the machine": "the gate is a 'gate'; 'machining table' is Core content and stays",
    "portal": "the machine is a 'gate'; the link it holds open is a 'connection'",
    "machine gate": "the machine gate def was retired in 0.9.0-dev; it is a 'gate'",
    "doorway": "a plain door is a 'door'; the far-side arrival point is a 'threshold'",
    "gizmo": "'gizmo' is RimWorld's word for a button, never a name for our gate",
}
BANNED_PATTERNS = [
    (term, re.compile(r"\b" + term.replace(" ", r"\s+") + r"s?\b", re.I))
    for term in BANNED_TERMS
]


def our_def_type(kind):
    return kind.startswith("RimroomsAsyncIndustries.")


def read_defs():
    found = {}
    pattern = os.path.join(MOD, "*", "Defs", "**", "*.xml")
    for path in sorted(glob.glob(pattern, recursive=True)):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as error:
            print("XML does not parse: %s (%s)" % (path, error))
            continue
        for node in root:
            name = node.findtext("defName")
            if not name or not name.strip():
                continue
            stages = []
            stage_root = node.find("stages")
            if stage_root is not None:
                for stage in stage_root:
                    stages.append(((stage.findtext("label") or "").strip(),
                                   (stage.findtext("description") or "").strip()))
            found[name.strip()] = {
                "kind": node.tag,
                "path": os.path.relpath(path, REPO).replace(os.sep, "/"),
                "label": (node.findtext("label") or "").strip(),
                "description": (node.findtext("description") or "").strip(),
                "report": (node.findtext("reportString") or "").strip(),
                "stages": stages,
            }
    return found


def read_injected():
    labels, descriptions = {}, {}
    pattern = os.path.join(MOD, "*", "Languages", "**", "DefInjected", "**", "*.xml")
    for path in glob.glob(pattern, recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root:
            text = (node.text or "").strip()
            if node.tag.endswith(".label"):
                labels[node.tag[: -len(".label")]] = text
            elif node.tag.endswith(".description"):
                descriptions[node.tag[: -len(".description")]] = text
    return labels, descriptions


def usable(text, name):
    if not text or PLACEHOLDER.match(text) or PLACEHOLDER_PREFIX.match(text):
        return False
    return text.strip().lower() != name.strip().lower()


def displayed_text():
    """Every string a player can actually read: keyed values, and def labels and descriptions."""
    found = []
    pattern = os.path.join(MOD, "*", "Languages", "**", "*.xml")
    for path in glob.glob(pattern, recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            if node.text and node.tag != "LanguageData":
                found.append((os.path.relpath(path, REPO).replace(os.sep, "/"), node.tag, node.text))
    for path in glob.glob(os.path.join(MOD, "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            if node.tag in ("label", "description", "jobString", "reportString",
                            "verb", "gerund", "summary") and node.text:
                found.append((os.path.relpath(path, REPO).replace(os.sep, "/"), node.tag, node.text))
    return found


def check_vocabulary(problems):
    for path, tag, text in displayed_text():
        flat = " ".join(text.split())
        for term, pattern in BANNED_PATTERNS:
            match = pattern.search(flat)
            if not match:
                continue
            problems.append("%s <%s> says %r -- %s: %r"
                            % (path, tag, match.group(0), BANNED_TERMS[term], flat[:70]))


# --------------------------------------------------------------------------- #
# Walls of text
# --------------------------------------------------------------------------- #
#
# Owner direction, 2026-09-29, verbatim: *"its a massive text wall needs style formating and
# beautiful layout"*, about an About.xml description that had reached a single unbroken line
# of 6,724 characters -- one sentence appended per checkpoint for twenty-odd checkpoints.
#
# RimWorld renders newlines in a description, a letter and a scenario summary, so a wall is
# a choice rather than a limitation. Past this length without a single paragraph break, it
# is a choice nobody made deliberately.
WALL_CHARS = 420
WALL_EXEMPT_TAGS = ("jobString", "reportString", "verb", "gerund", "label")


def check_walls(problems):
    for path, tag, text in displayed_text():
        if tag in WALL_EXEMPT_TAGS:
            continue
        flat = " ".join(text.split())
        if len(flat) <= WALL_CHARS:
            continue
        if "\n" in text or "\\n" in text:
            continue
        problems.append("%s <%s> is %d characters with no paragraph break -- a player meets "
                        "this as a wall (%r)" % (path, tag, len(flat), flat[:60]))


def main():
    defs = read_defs()
    labels, descriptions = read_injected()
    problems = []
    checked = 0

    for name in sorted(defs):
        entry = defs[name]
        kind = entry["kind"]
        path = entry["path"]
        if kind in EXEMPT:
            continue
        checked += 1

        if kind in REPORT_STRING_TYPES:
            if not usable(entry["report"], name):
                problems.append("%s %s has no reportString, so a player watching this job "
                                "reads nothing that says what it is (%s)" % (kind, name, path))
            continue

        if kind in STAGED_TYPES:
            if not entry["stages"]:
                problems.append("%s %s declares no stages, so it can show a player nothing "
                                "(%s)" % (kind, name, path))
            for index, (stage_label, stage_description) in enumerate(entry["stages"]):
                if not usable(stage_label, name):
                    problems.append("%s %s stage %d has no label (%s)" % (kind, name, index, path))
                if not usable(stage_description, name):
                    problems.append("%s %s stage %d has no description (%s)" % (kind, name, index, path))
            continue

        if not usable(entry["label"] or labels.get(name, ""), name):
            problems.append("%s %s has no usable label (%s)" % (kind, name, path))

        wants_description = kind in DESCRIPTION_REQUIRED or our_def_type(kind)
        if kind in LABEL_ONLY:
            wants_description = False
        if wants_description and not usable(entry["description"] or descriptions.get(name, ""), name):
            problems.append("%s %s has no usable description, so what a player is shown about "
                            "it is a bare name (%s)" % (kind, name, path))

    check_vocabulary(problems)
    check_walls(problems)

    print("info-cards")
    print("  defs declared        : %d" % len(defs))
    print("  checked              : %d" % checked)
    print("  exempt, never shown  : %d types" % len(EXEMPT))
    print("  labelled but not described, matching Core:")
    for kind in sorted(LABEL_ONLY):
        print("      %-18s %s" % (kind, LABEL_ONLY[kind]))
    print("")

    if problems:
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
