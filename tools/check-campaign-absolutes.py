# -*- coding: utf-8 -*-
"""Refuse to ship a deadline, and refuse to ship an offer with one way to succeed.

Why this exists
---------------
Owner direction, 2026-09-29, verbatim:

    "nothing ever ever have time restripctions but the gate(ie power tech and maintanance and
     workflorce and other factors all determine the time a gate can be open) but missions and
     quests and offeres and trades are never time senstive the company will wait as long as
     possible for you to complete their task offers and never offer only one path but multiple
     success routes"

Two rules stated as *never* and *always*, and both decay silently without enforcement:

* **A deadline is the easiest thing in the world to add by accident.** An expiry tick is three
  lines and reads like hygiene -- bounding a list, tidying stale records. Two were already in the
  build: a hiring offer withdrew itself after seven in-game days, and a purchase quote expired
  after about ten in-game hours. **Neither pool was bounded by its clock** -- both were already
  capped by a count -- so both were pure pressure with no function. Nobody decided that. It
  accumulated. And **the promise of more of it was sitting in seven prep documents**, which is
  how it would have arrived again.
* **One route is what an offer naturally has** unless something insists otherwise.

What "a deadline" means here
----------------------------
The test is not "does time appear". Time appears everywhere and must:

    A delay is fine.      The supplier is slow. Nothing is asked of the player.
    A cooldown is fine.   It gates when the player may act again. It cannot be failed.
    A timestamp is fine.  It records when something happened.
    A DEADLINE is not:    if time passing can make a thing the player wanted become
                          unavailable, it is a deadline.

The gate is the one permitted clock, by the direction, and even its clock is a *consequence* of
power, tech, maintenance and workforce rather than a timer set against the player.

Deliberately narrow scope
-------------------------
This checker looks for identifiers and def fields whose **names** mean "this becomes unavailable
when time passes" -- expiry, deadline, time limit. It does **not** scan every `...Ticks` field,
because roughly forty of them are delays, cooldowns and timestamps and flagging those would make
this a checker people learn to scroll past.

That means the allowlist below contains **only names this detector can actually match**. Listing
`dispatchDelayTicks` here would imply a coverage that does not exist. The full reasoning about
which clocks are legitimate lives in `docs/CAMPAIGN_CHART.md` §1.1, where it belongs.

Usage
-----
    python tools/check-campaign-absolutes.py
"""

import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")

# --------------------------------------------------------------------------- #
# Rule 1 -- the only clock is the gate
# --------------------------------------------------------------------------- #
#
# Names meaning "this becomes unavailable when time passes".
DEADLINE_NAME = re.compile(
    r"(expiry|expires|expired|expiration|deadline|timelimit|timeout|"
    r"mustcompleteby|failsattick|abandontick)", re.I)

# Only names DEADLINE_NAME can match belong here, each with the reason it is not a deadline.
# An entry for something the detector never looks at would be a false claim of coverage.
ALLOWED = {
    "expiresTick": "LEGACY, set by nothing and read by nothing since 0.11.0-dev. Kept scribed on "
                   "the hiring offer and the purchase quote only so a save written before that "
                   "checkpoint still loads. Archived: "
                   "historical-content/0.11.0-dev/RETIRED_OFFER_CLOCKS.md",
    "ExpiresTick": "same field, read side. Nothing calls it",
    "Expired": "LEGACY status and release reason on a hiring offer. Nothing sets either any more; "
               "kept because a pre-0.11.0-dev save contains them",
    "leaseExpiryTick": "releases a reservation for a worker who never arrived at all. A DEPLOYED "
                       "worker has no countdown -- nothing is lost when this drops, and the "
                       "player is not asked for anything",
    "LeaseExpiryTick": "same, read side",
}

# Documents allowed to discuss the rule, and phrases that mean a document is denying a deadline
# rather than promising one.
DOC_EXEMPT = ("docs/CAMPAIGN_CHART.md",)
DOC_HISTORICAL = ("docs/FINALIZED.md", "CHANGELOG.md", "docs/implementation", "docs/research",
                  ".claude", "outputs", ".local", ".git")
NEGATIONS = re.compile(
    r"(no deadline|not a deadline|deadlines do not|names no deadline|never states a deadline|"
    r"there is no deadline|avoid local wall-clock|expiration timer|timed shutdown|"
    r"none of them timed|no investigation is timed|timed slideshow|timed menu slideshow|"
    r"never a deadline|no deadlines|a deadline is the easiest|"
    r"carries a deadline, ever|because there is none|a deadline is not|deadline-negation)", re.I)
# `banned` and `superseded` were briefly in that list and were taken back out. They are broad
# enough to mask a real deadline promise that happens to sit near either word, and widening a
# rule so that existing text passes is how a rule stops meaning anything. Every phrase above
# names a deadline being denied, specifically.


def declared_identifiers():
    """Identifiers our own source declares: fields, properties, consts, enum members."""
    found = []
    member = re.compile(
        r"^\s*(?:public|private|internal|protected)[\w\s<>,\[\]?]*?\s(\w+)\s*(?:=|;|\{|=>)", re.M)
    enum_member = re.compile(r"^\s*(\w+)\s*=\s*\d+\s*,?\s*$", re.M)
    for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
        text = io.open(path, encoding="utf-8-sig").read()
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for match in member.finditer(text):
            found.append((rel, match.group(1)))
        for match in enum_member.finditer(text):
            found.append((rel, match.group(1)))
    return found


def check_source(problems):
    used = set()
    for rel, name in declared_identifiers():
        if not DEADLINE_NAME.search(name):
            continue
        if name in ALLOWED:
            used.add(name)
            continue
        problems.append(
            "%s declares %r, which reads as a deadline. The only clock in this mod is the gate's "
            "connection window. If this is a delay, a cooldown or a timestamp, rename it; if it "
            "genuinely is none of those, allowlist it with the reason."
            % (rel, name))
    return used


def check_def_fields(problems):
    """A def field is how a deadline would arrive with no C# changing at all."""
    checked = 0
    for path in sorted(glob.glob(os.path.join(MOD, "*", "Defs", "**", "*.xml"), recursive=True)):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for node in root.iter():
            if not isinstance(node.tag, str):
                continue
            checked += 1
            if DEADLINE_NAME.search(node.tag) and node.tag not in ALLOWED:
                problems.append("%s sets <%s>, which reads as a deadline on content."
                                % (rel, node.tag))
    return checked


def living_docs():
    found = []
    for path in glob.glob(os.path.join(REPO, "**", "*.md"), recursive=True):
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        if rel in DOC_EXEMPT:
            continue
        if any(rel == h or rel.startswith(h.replace(os.sep, "/") + "/") for h in DOC_HISTORICAL):
            continue
        found.append((rel, path))
    return sorted(found)


def check_docs(problems):
    """A living document may not promise a deadline.

    The promise is what builds the thing: seven prep documents promised deadlines, timed
    investigations and penalties for delay, and a future session reading one of them would have
    built exactly that. Denials are skipped -- a document is allowed to say there is no deadline.
    """
    docs = living_docs()
    promise = re.compile(r"(deadline|timed objectives|timed distortion|consequences? for delay)",
                         re.I)
    for rel, path in docs:
        text = io.open(path, encoding="utf-8-sig").read()
        for match in promise.finditer(text):
            window = text[max(0, match.start() - 120): match.end() + 120]
            if NEGATIONS.search(window):
                continue
            problems.append("%s promises %r. No mission, quest, offer, contract or trade has a "
                            "deadline; see docs/CAMPAIGN_CHART.md."
                            % (rel, match.group(0)))
    return len(docs)


# --------------------------------------------------------------------------- #
# Rule 2 -- every offer has at least two ways to succeed
# --------------------------------------------------------------------------- #
#
# Matched on the def-class name so a new offer type is covered the moment it is named, rather
# than the moment somebody remembers this file exists.
OFFER_SUFFIXES = ("RimroomsRequestDef", "RimroomsMissionDef", "RimroomsQuestDef",
                  "RimroomsContractDef", "RimroomsOfferDef")
ROUTES_FIELD = "successRoutes"
MINIMUM_ROUTES = 2


def check_offer_routes(problems):
    offers = 0
    for path in sorted(glob.glob(os.path.join(MOD, "*", "Defs", "**", "*.xml"), recursive=True)):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for node in root:
            if not isinstance(node.tag, str) or node.tag.split(".")[-1] not in OFFER_SUFFIXES:
                continue
            offers += 1
            name = node.findtext("defName") or "(unnamed)"
            routes = node.find(ROUTES_FIELD)
            count = 0 if routes is None else len(list(routes))
            if count < MINIMUM_ROUTES:
                problems.append("%s: offer %s declares %d success route(s); every offer needs at "
                                "least %d, of at least two different kinds."
                                % (rel, name, count, MINIMUM_ROUTES))
    return offers


def main():
    problems = []
    used = check_source(problems)
    fields = check_def_fields(problems)
    docs = check_docs(problems)
    offers = check_offer_routes(problems)

    print("campaign-absolutes")
    print("")
    print("  rule 1 -- the only clock is the gate")
    print("    scope                    : identifiers and def fields NAMED as an expiry or a")
    print("                               deadline. Delays, cooldowns and timestamps are out of")
    print("                               scope by design -- see CAMPAIGN_CHART.md #1.1")
    print("    allowlisted, with reason : %d" % len(ALLOWED))
    print("    of those, present        : %d" % len(used))
    stale = sorted(set(ALLOWED) - used)
    if stale:
        print("    allowlisted, not present : %s" % ", ".join(stale))
        print("                               (a justification for a clock that no longer exists;")
        print("                                remove the entry when its clock goes)")
    print("    def fields scanned       : %d" % fields)
    print("    living documents scanned : %d" % docs)
    print("")
    print("  rule 2 -- every offer has two or more success routes")
    print("    offer defs found : %d" % offers)
    if offers == 0:
        print("                       none yet, and that is expected. The rule is written before")
        print("                       the content so the first offer ever written has to satisfy")
        print("                       it -- per the instruction to finish the chart first.")
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
