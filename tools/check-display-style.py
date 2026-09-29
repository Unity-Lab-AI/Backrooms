# -*- coding: utf-8 -*-
"""Hold every string to the conventions of the surface it is displayed on.

Why this exists
---------------
Owner direction, 2026-09-29, verbatim:

    "lets make sure the docs and informations displays in game are proper to backrrooms
     universe and rimworld gameplay style of all displayed informations of varying types
     to include all"

RimWorld does not have one voice for displayed text. It has a **different convention per
surface**, and it is consistent about them to a degree that is easy to miss and easy to
violate. Core's own keyed files are organised by surface -- `Alerts.xml`, `Letters.xml`,
`Messages.xml`, `FloatMenu.xml`, `GameplayCommands.xml`, `Designators.xml` -- where ours are
organised by system. Organising by system is normal for a mod and is not the problem; losing
the per-surface conventions along the way is.

`check-info-cards.py` already holds def labels and descriptions to Core's practice, and
already bans the retired vocabulary and walls of text across everything displayed. This
checker is the other half: the strings that are **not** on a card. A float menu row, a letter
headline, a message in the top-left corner and a button tooltip are four different kinds of
writing, and RimWorld writes them four different ways.

Where the numbers come from
---------------------------
Measured, never remembered -- the standing rule of this project, which has been wrong about
remembered game data before. Every threshold below is counted over RimWorld 1.6 Core's own
English keyed strings by `.local/register/measure-core-surfaces.py`:

    surface                 n     median   p90    max    ends with punctuation
    ------------------------------------------------------------------------
    Message               363     42       88     156    85%
    FloatMenu option      290     19       38      76     7%
    Letter label           74     15       24      45     2%
    Letter body           264     62      198     666    62%
    Alert label            77     21       87     363    14%
    Alert explanation      60    141      298     372    70%
    Command label         188     15       52     162    28%
    Explanatory *Desc     430     70      178     894    93%

Two of those columns carry the real lesson. A **float menu option ends with punctuation 7% of
the time** -- it is a command a player picks, not a sentence read to them. An **explanatory
description ends with punctuation 93% of the time** -- it is prose. Writing either one in the
other's register is the specific mistake this catches.

Sampling the wrong population is how a checker cries wolf
---------------------------------------------------------
The first run of this file reported seven failures that were not failures, and every one of
them came from measuring a **file** instead of a **surface**:

* Letter bodies were measured from `Letters.xml` alone, giving a maximum of 385. But Core's
  incident letters live in `Incidents.xml` and reach **666**. The mod's own welcome letter,
  474 characters across four paragraphs, was reported as longer than anything Core writes. It
  is not; it sits between Core's p90 and its maximum.
* Tooltips were measured from `GameplayCommands.xml` alone, giving a maximum of 204. Core's
  explanatory strings across every keyed file reach **894**, with p95 at 221 and p99 at 345.
  Six perfectly ordinary tooltips were reported for being four to a hundred-and-fifty
  characters over a ceiling that was never real.

The baselines were corrected, not the text. When a rule and the thing it is measuring
disagree, the rule has to justify itself first -- and a rule that would have had somebody
trimming four characters off a good sentence could not.

Classified by call site, not by name
------------------------------------
A key's name does not say where it is displayed. `RR_GateHistory_Empty` could be a message, a
tooltip or a float menu row, and only the C# that passes it tells the truth. So every rule
here is applied to keys found at a **call site of a known shape** -- inside
`Messages.Message(`, inside `new FloatMenuOption(`, assigned to `defaultLabel`, and so on --
plus the two def fields that carry letter keys in XML.

That deliberately leaves most keys unclassified, and the report says so out loud rather than
implying a coverage it does not have. A checker that reads one kind of source has a blind
side; the honest thing is to print the size of it.

The surface census
------------------
*"of all displayed informations of varying types to include all"* is the load-bearing phrase,
and the only way to act on "all" is to enumerate the surfaces and count them -- **including
the ones at zero**. The census at the bottom of the report is not decoration: it is how the
alerts readout was found to be a RimWorld display surface this mod used **none** of.

A zero in the census is not a failure. Not every mod needs every surface. It is a question
the report asks every run, instead of one nobody thinks to ask.

Usage
-----
    python tools/check-display-style.py
"""

import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SRC = os.path.join(REPO, "src")


# --------------------------------------------------------------------------- #
# RimWorld 1.6 Core, measured
# --------------------------------------------------------------------------- #
#
# `max` is the longest string Core ships on that surface. Going past it is not automatically
# wrong, but it means the mod is writing something longer than anything the base game does in
# the same place, which is worth having to justify rather than doing by accident.
CORE = {
    # FloatMenu.xml -- Core's dedicated file for the surface, so this is the population.
    "float-menu":   {"n": 290, "median": 19, "max": 76, "ends_punct_pct": 7},
    # Messages.xml, likewise.
    "message":      {"n": 363, "median": 42, "max": 156, "ends_punct_pct": 85},
    # Letters.xml *Label keys.
    "letter-label": {"n": 74, "median": 15, "max": 45, "ends_punct_pct": 2},
    # Letters.xml bodies AND Incidents.xml. Measuring only the first gave 385 and was wrong.
    "letter-body":  {"n": 264, "median": 62, "max": 666, "ends_punct_pct": 62},
    # Alerts.xml, split on the Desc suffix Core uses consistently there.
    "alert-label":  {"n": 77, "median": 21, "max": 363, "ends_punct_pct": 14},
    "alert-desc":   {"n": 60, "median": 141, "max": 372, "ends_punct_pct": 70},
    # GameplayCommands.xml, keys without the Desc suffix.
    "gizmo-label":  {"n": 188, "median": 15, "max": 162, "ends_punct_pct": 28},
    # Every *Desc key in every Core keyed file: the population of explanatory paragraphs the
    # base game writes. Measuring one file gave 204 and reported six good tooltips as faults.
    "gizmo-desc":   {"n": 430, "median": 70, "max": 894, "ends_punct_pct": 93},
}

# Every surface RimWorld displays text on that a Core-only mod can reach without Harmony.
# Listed whether or not this mod uses it, so that "all" is a count rather than an impression.
SURFACE_CENSUS = (
    ("message", "top-left transient line"),
    ("letter-label", "letter headline in the right-hand stack"),
    ("letter-body", "letter body a player opens"),
    ("alert-label", "alerts readout down the right edge"),
    ("alert-desc", "alert explanation on hover"),
    ("gizmo-label", "command button under a selected thing"),
    ("gizmo-desc", "command button tooltip"),
    ("float-menu", "right-click option row"),
    ("inspect", "inspect pane under the selection"),
)

# Surfaces that are counted but not ruled on, and why. A count with no rule behind it is
# still worth printing -- it is what makes a zero in the census mean something -- but saying
# so is the difference between a limit that was chosen and one that was forgotten.
NO_RULE = {
    "inspect": "counted only: Core builds inspect lines from stat and need strings scattered "
               "across its keyed files, so there is no clean population to measure against",
}


# --------------------------------------------------------------------------- #
# Call sites
# --------------------------------------------------------------------------- #
#
# Each pattern matches a key literal in a position whose surface is unambiguous. Anything
# reached indirectly -- a key held in a variable, built by concatenation, or read from a def
# field other than the two below -- is deliberately not guessed at.
CALL_SITES = (
    ("message", re.compile(r'Messages\.Message\(\s*"(RR_[A-Za-z0-9_]+)"')),
    ("message", re.compile(r'Messages\.Message\(\s*\(\s*[A-Za-z_.]+\s*\?\?\s*"(RR_[A-Za-z0-9_]+)"')),
    ("letter-label", re.compile(r'ReceiveLetter\(\s*"(RR_[A-Za-z0-9_]+)"')),
    ("letter-body", re.compile(r'ReceiveLetter\(\s*"RR_[A-Za-z0-9_]+"\.Translate\([^;]*?\)\s*,\s*"(RR_[A-Za-z0-9_]+)"')),
    ("gizmo-label", re.compile(r'defaultLabel\s*=\s*"(RR_[A-Za-z0-9_]+)"')),
    ("gizmo-desc", re.compile(r'defaultDesc\s*=\s*"(RR_[A-Za-z0-9_]+)"')),
    ("alert-label", re.compile(r'defaultLabel\s*=\s*"(RR_[A-Za-z0-9_]+)"\.Translate\(\)\s*;')),
    ("alert-desc", re.compile(r'defaultExplanation\s*=\s*"(RR_[A-Za-z0-9_]+)"')),
    ("float-menu", re.compile(r'new FloatMenuOption\(\s*"(RR_[A-Za-z0-9_]+)"')),
)

# The two def fields that name a letter's strings in XML rather than in C#.
XML_KEY_FIELDS = (("letterLabelKey", "letter-label"), ("letterTextKey", "letter-body"))

# A string whose last token is a substitution ends wherever the substitution ends, so its
# final character says nothing about how it was written. Core does this too: 15% of its
# messages "do not end with punctuation" for exactly this reason.
ENDS_IN_PLACEHOLDER = re.compile(r"\{\d+\}\s*$")

# An alert label is set in a constructor the same way a gizmo label is set on a Command, so
# the two patterns overlap by construction. The alert file is the tiebreak.
ALERT_FILE = re.compile(r"Alert[A-Za-z]*\.cs$")

# The inspect pane is reached through a method override rather than a call, so it is found by
# reading the method body instead of matching an argument position.
INSPECT_METHOD = re.compile(r"CompInspectStringExtra\s*\(\s*\)")
KEY_LITERAL = re.compile(r'"(RR_[A-Za-z0-9_]+)"')


def method_body(text, start):
    """The source between a method's opening brace and its matching close.

    Written out rather than approximated with a regex because a regex cannot balance braces,
    and an inspect method that contains a lambda or an object initialiser -- ours do -- would
    otherwise be cut off at the first inner `}` and silently under-report.
    """
    open_at = text.find("{", start)
    if open_at < 0:
        return ""
    depth = 0
    for index in range(open_at, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[open_at:index]
    return ""


def keyed_strings():
    found = {}
    for path in glob.glob(os.path.join(MOD, "*", "Languages", "English", "Keyed", "*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as error:
            print("XML does not parse: %s (%s)" % (path, error))
            continue
        for node in root:
            if isinstance(node.tag, str) and node.text is not None:
                found[node.tag] = node.text
    return found


def classify():
    """Map each key to the surfaces it is displayed on, by where it is used."""
    surfaces = {}
    for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
        text = io.open(path, encoding="utf-8-sig").read()
        in_alert = ALERT_FILE.search(path.replace(os.sep, "/")) is not None
        for surface, pattern in CALL_SITES:
            if surface == "gizmo-label" and in_alert:
                continue
            if surface == "alert-label" and not in_alert:
                continue
            for match in pattern.finditer(text):
                surfaces.setdefault(match.group(1), set()).add(surface)
        for match in INSPECT_METHOD.finditer(text):
            for key in KEY_LITERAL.findall(method_body(text, match.end())):
                surfaces.setdefault(key, set()).add("inspect")
    for path in sorted(glob.glob(os.path.join(MOD, "*", "Defs", "**", "*.xml"), recursive=True)):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            for field, surface in XML_KEY_FIELDS:
                if node.tag == field and node.text and node.text.strip().startswith("RR_"):
                    surfaces.setdefault(node.text.strip(), set()).add(surface)
    return surfaces


def flat(text):
    return " ".join(text.split())


def check(surface, key, text, problems):
    core = CORE.get(surface)
    if core is None:
        return
    one_line = flat(text)

    if len(one_line) > core["max"]:
        problems.append(
            "%s is %d characters on the %s surface; the longest Core ships there is %d "
            "(median %d) -- %r"
            % (key, len(one_line), surface, core["max"], core["median"], one_line[:60]))

    ends_punct = one_line.endswith((".", "!", "?", ":")) or bool(ENDS_IN_PLACEHOLDER.search(one_line))

    # A surface Core writes as prose: not ending a sentence reads as truncated text.
    if core["ends_punct_pct"] >= 90 and not ends_punct:
        problems.append("%s on the %s surface does not end a sentence; Core's do %d%% of the "
                        "time, because this surface is prose -- %r"
                        % (key, surface, core["ends_punct_pct"], one_line[:60]))

    # A surface Core writes as a label rather than a sentence: a float menu row is a thing the
    # player picks, a letter or alert headline is a headline. A full stop on any of them makes
    # a label read as a statement. Core puts one on 7%, 2% and 14% of them respectively.
    if core["ends_punct_pct"] <= 15 and one_line.endswith("."):
        problems.append("%s on the %s surface ends with a full stop; Core does that on %d%% of "
                        "them, because this surface is a label rather than a sentence -- %r"
                        % (key, surface, core["ends_punct_pct"], one_line[:60]))

    # Core ships zero messages containing a line break: the surface is one line in a corner.
    if surface == "message" and "\n" in text:
        problems.append("%s is a message containing a line break; Core ships none of those in "
                        "%d messages -- %r" % (key, core["n"], one_line[:60]))


def main():
    strings = keyed_strings()
    surfaces = classify()
    problems = []

    counts = {}
    for key, kinds in sorted(surfaces.items()):
        text = strings.get(key)
        if text is None:
            # check-keyed-strings.py owns unresolved references; not this checker's job.
            continue
        for surface in sorted(kinds):
            counts[surface] = counts.get(surface, 0) + 1
            check(surface, key, text, problems)

    print("display-style")
    print("  keyed strings              : %d" % len(strings))
    print("  classified by call site    : %d" % len([k for k in surfaces if k in strings]))
    print("  not reached by any pattern : %d  (held by check-info-cards.py for vocabulary "
          "and walls)" % len([k for k in strings if k not in surfaces]))
    print("")
    print("  surface census -- every place RimWorld displays text, used or not:")
    for surface, where in SURFACE_CENSUS:
        used = counts.get(surface, 0)
        note = "" if used else "   <- this mod displays nothing here"
        print("    %-14s %-42s %3d%s" % (surface, where, used, note))
    for surface, reason in sorted(NO_RULE.items()):
        print("")
        print("    %s is %s" % (surface, reason))
    print("")

    if problems:
        print("FAIL: %d problem(s)" % len(problems))
        for problem in sorted(set(problems)):
            print("  - %s" % problem)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
