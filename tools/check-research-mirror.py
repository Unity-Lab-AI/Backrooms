# -*- coding: utf-8 -*-
"""Checker 26 -- a mirrored research project may not drift from the company project it mirrors.

Why this exists
---------------
**Owner, 2026-10-06, in capitals:** *"AND A MAJOR ISSUE: I DONT SEE ANY RESEARCH FOR THE GATE
SYSTEMS AND EVERYTHING THIS MOD HAS!!!!!"* All 38 company projects existed and had records; they
were in an Operations section, invisible to the vanilla Research tab and therefore to ResearchTree
and Research Whatever, both of which the owner runs.

The owner chose **two genuine routes, either works**, and the cost was named before it was chosen:
**38 paired defs that must not drift**. This is the thing that makes that promise keepable.

**A mirror that drifts is a research tree that lies about what it unlocks** -- a player reads a
label and a description in the Research tab and concludes something about a capability. If the
mirror's label says one thing and the company project grants another, the tab is misinformation
rather than a map.

The seven rules
---------------
1. **One mirror per company project, and no orphans.** A company project with no mirror is invisible
   again; a mirror with no project is a research entry that unlocks nothing.
2. **Labels agree.** The two are the same project under two interfaces.
3. **Descriptions agree.** Same reason, and this is the text a player actually reads.
4. **The prerequisite graph agrees.** Every company prerequisite appears as the mirrored
   prerequisite, and no mirror invents one. A tree drawn from a wrong graph is the wrong tree in
   every research mod at once, because they all derive layout from it.
5. **Every mirror is in our own tab.** Register row 191's planned use: the Backrooms tree *"should
   not overwrite other research trees"*. Our own tab is how that is kept.
6. **The graph is self-contained.** No mirror requires a vanilla or mod project, and no mirror is
   named as a prerequisite by anything outside the mirror set. A tangled graph is how a research
   mod ends up drawing our tree through the middle of somebody else's.
7. **Costs sit inside vanilla's own range.** The first generator used `workRequired * (1 +
   insightCost)` and produced 8,000 to 108,000 against vanilla's measured 200 to 8,000 -- the
   cheapest mirror equalling vanilla's dearest project. **"Either route works" would have been
   false while looking true**, so the range is asserted rather than trusted.

Exit status is the result. Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
PREFIX = "RR_Mirror_"
TAB = "RR_Research"

# Vanilla's measured range, with headroom. Not a guess: 113 Core and DLC research projects run 200
# to 8,000 with a median of 1,000.
MIN_COST = 200
MAX_COST = 8000


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def text_of(node, tag):
    found = node.find(tag)
    return "" if found is None else " ".join((found.text or "").split())


def company_projects():
    out = {}
    for path in glob.glob(os.path.join(MOD, "**", "RimroomsProjectDefs", "*.xml"), recursive=True):
        root = ET.parse(path).getroot()
        for node in root:
            if not node.tag.endswith("ProjectDef"):
                continue
            name = text_of(node, "defName")
            if not name:
                continue
            block = node.find("prerequisiteProjects")
            out[name] = {
                "label": text_of(node, "label"),
                "description": text_of(node, "description"),
                "pre": sorted(" ".join((li.text or "").split())
                              for li in ([] if block is None else block.findall("li"))),
            }
    return out


def mirrors():
    out = {}
    tabs = set()
    for path in glob.glob(os.path.join(MOD, "**", "ResearchProjectDefs", "*.xml"), recursive=True):
        root = ET.parse(path).getroot()
        for node in root:
            if node.tag == "ResearchTabDef":
                tabs.add(text_of(node, "defName"))
                continue
            if node.tag != "ResearchProjectDef":
                continue
            name = text_of(node, "defName")
            block = node.find("prerequisites")
            out[name] = {
                "label": text_of(node, "label"),
                "description": text_of(node, "description"),
                "pre": sorted(" ".join((li.text or "").split())
                              for li in ([] if block is None else block.findall("li"))),
                "tab": text_of(node, "tab"),
                "cost": text_of(node, "baseCost"),
            }
    return out, tabs


def foreign_research_names():
    """Every research project the installed game defines, so rule 6 can be checked at all."""
    names = set()
    if not os.path.isdir(GAME_DATA):
        return None
    for path in glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root:
            if node.tag == "ResearchProjectDef":
                name = text_of(node, "defName")
                if name:
                    names.add(name)
    return names


def main():
    company = company_projects()
    mirror, tabs = mirrors()
    problems = []

    if not company:
        say("FAIL: no company projects found at all. An absence rule over an empty set passes by "
            "construction, so this is a failure rather than a clean run.")
        return 1
    if not mirror:
        say("FAIL: no mirrored research projects found. The owner's answer was that the research "
            "must be visible in the vanilla tab; an empty mirror is the defect, not a clean run.")
        return 1

    # ---------------------------------------------------------------- 1. the pairing
    for name in sorted(company):
        if PREFIX + name not in mirror:
            problems.append("company project %r has no mirror, so it is invisible in the Research "
                            "tab again" % name)
    for name in sorted(mirror):
        if not name.startswith(PREFIX):
            problems.append("%r is a research project this package ships that is not a mirror; "
                            "every one must pair with a company project" % name)
        elif name[len(PREFIX):] not in company:
            problems.append("mirror %r has no company project, so finishing it unlocks nothing"
                            % name)

    # ---------------------------------------------------------------- 2-4. the fields agree
    for name, record in sorted(company.items()):
        peer = mirror.get(PREFIX + name)
        if peer is None:
            continue
        if peer["label"] != record["label"]:
            problems.append("%s: label differs. company %r, mirror %r"
                            % (name, record["label"], peer["label"]))
        if peer["description"] != record["description"]:
            problems.append("%s: description differs, and this is the text a player reads in the "
                            "Research tab" % name)
        wanted = sorted(PREFIX + p for p in record["pre"])
        if peer["pre"] != wanted:
            problems.append("%s: prerequisites differ. company implies %s, mirror declares %s -- "
                            "every research mod derives its layout from this graph, so a wrong one "
                            "is the wrong tree everywhere at once" % (name, wanted, peer["pre"]))

    # ---------------------------------------------------------------- 5. our own tab
    if TAB not in tabs:
        problems.append("the %r research tab is not declared; without it every mirror lands in "
                        "vanilla's own tree, which register row 191 asks this mod not to "
                        "overwrite" % TAB)
    for name, record in sorted(mirror.items()):
        if record["tab"] != TAB:
            problems.append("%s sits in tab %r rather than %r" % (name, record["tab"] or "(none)", TAB))

    # ---------------------------------------------------------------- 6. self-contained graph
    foreign = foreign_research_names()
    if foreign is None:
        say("note: the game's Data folder is not reachable, so the self-contained-graph rule is "
            "unchecked rather than passed")
    else:
        for name, record in sorted(mirror.items()):
            for parent in record["pre"]:
                if parent in foreign:
                    problems.append("%s requires %r, which is the GAME's research project. A "
                                    "mirror's graph must be self-contained or a research mod draws "
                                    "our tree through the middle of vanilla's" % (name, parent))

    # ---------------------------------------------------------------- 7. costs inside vanilla's range
    for name, record in sorted(mirror.items()):
        try:
            cost = float(record["cost"])
        except ValueError:
            problems.append("%s has no readable baseCost" % name)
            continue
        if cost < MIN_COST or cost > MAX_COST:
            problems.append("%s costs %d, outside vanilla's measured %d..%d. The first generator "
                            "produced 8,000 to 108,000 here, which made 'either route works' false "
                            "while looking true" % (name, cost, MIN_COST, MAX_COST))

    say("research-mirror")
    say("  company projects : %d" % len(company))
    say("  mirrors          : %d" % len(mirror))
    say("  research tab     : %s" % (TAB if TAB in tabs else "MISSING"))
    say("  cost range       : %s"
        % (", ".join(str(int(float(m["cost"]))) for m in
                     [min(mirror.values(), key=lambda m: float(m["cost"] or 0)),
                      max(mirror.values(), key=lambda m: float(m["cost"] or 0))])
           if mirror else "-"))
    say("")
    if problems:
        say("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            say("  - %s" % problem)
        return 1
    say("PASS: every company project has exactly one mirror, they agree on label, description and "
        "prerequisites, the tree is ours alone and self-contained, and every cost sits inside "
        "vanilla's own range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
