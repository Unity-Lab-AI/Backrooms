# -*- coding: utf-8 -*-
"""Generate the vanilla `ResearchProjectDef` mirror of every company project.

Owner, 2026-10-06, in capitals: *"AND A MAJOR ISSUE: I DONT SEE ANY RESEARCH FOR THE GATE SYSTEMS
AND EVERYTHING THIS MOD HAS!!!!!"* -- and they were right to look in the Research tab, because that
is where everybody looks. All 38 projects of the day existed and were reachable only through an
Operations section. There are 43 now, across seven bands, and the count is asserted rather than
assumed -- see EXPECTED_PROJECTS.

Asked how to resolve it, the owner chose **two genuine routes, either works**, and **our own tab,
nine columns by band**. Then: *"as far as the research layout wit has to work bvanillia and with the
research mods"*.

Why a generator rather than one hand-written def per project
-----------------------------------------------------------
**Because a mirror that drifts is a research tree that lies about what it unlocks.** Every field
here is derived from the company project it mirrors, so the two cannot disagree -- and
`check-research-mirror.py` asserts the pairing afterwards, which is the standing answer in this
repository to anything two generators agree about.

Working with vanilla AND with the research mods, which is one requirement not two
---------------------------------------------------------------------------------
Every research mod -- ResearchTree (register row 191), Research Whatever (row 279), the ones the
owner runs -- derives its own layout from the **prerequisite graph**. Vanilla instead uses the
explicit `researchViewX` / `researchViewY`. So both are emitted: the coordinates lay out nine
columns by seven bands for vanilla, and the graph is correct so every mod draws the same shape its
own way. The columns are ragged because the tree is: four branches have no top band and one has no
projects at all, each for a reason recorded beside the tier it is missing from.

**And the register asked for exactly this shape**, which is worth quoting because it reverses a
steer this repository had carried since 0.5.x. Row 191's planned use: *"The Backrooms tree should own
gate, mapping, containment, and spatial-analysis milestones and should not overwrite other research
trees"*, and *"Backrooms milestones need stable definitions and an independent route when optional
trees are absent."* Our own tab is the not-overwriting; the Operations insight route is the
independent one.

What the two routes cost, and the unit error that measuring caught
-----------------------------------------------------------------
The Operations route spends **insight and evidence logs** plus bench work. This route spends **bench
work only**. Equal cost would make this one strictly better and the evidence system decoration, so
it pays for its exemption -- but not in the currency the first version of this file used.

**That first version was `workRequired * (1 + insightCost)`, and it was a unit error.** Our
`workRequired` runs 4,000 to 18,000; vanilla's 113 research projects run **200 to 8,000, median
1,000**. The formula produced 8,000 to 108,000, so the *cheapest* mirror equalled vanilla's single
dearest project and the dearest was thirteen times it. **"Either route works" would have been false
while looking true**, and nothing in the build would have said so -- a research tab full of projects
no colony could finish.

So `BAND_COST` maps the bands onto vanilla's own distribution and the insight premium is a small
additive term. Its job is to make the evidence route worth taking, not to put this one out of reach.
"""
import io
import os
import re
import sys
from collections import defaultdict

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsProjectDefs", "RR_CompanyProjects.xml")
TARGET = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "ResearchProjectDefs", "RR_ResearchMirror.xml")
TAB = "RR_Research"
PREFIX = "RR_Mirror_"

# Column order. Nine branches by design; the eighth and ninth are deliberately thin -- Logistics and
# Gate stop at tier 3 for reasons recorded in the source file, and transport/orbital has no tier 0
# at all. A column with a gap is the honest shape.
COLUMNS = ["Gate", "Facilities", "Fieldcraft", "Logistics", "Measurement",
           "Spatial", "Commerce", "Entities", "Transport"]

# **A COST PER BAND, MEASURED AGAINST VANILLA RATHER THAN DERIVED FROM OUR OWN NUMBER.**
#
# The first version of this generator used `workRequired * (1 + insightCost)` on the reasoning that
# both are work done at a bench. **That was a unit error and measuring vanilla caught it.** Our
# `workRequired` runs 4,000 to 18,000; vanilla's 113 research projects run **200 to 8,000 with a
# median of 1,000**. The formula produced 8,000 to 108,000 -- the CHEAPEST mirror equalled vanilla's
# single most expensive project and the dearest was thirteen times it. Nobody would ever have
# finished one, so "either works" would have been false while looking true.
#
# So the bands are mapped onto vanilla's own distribution: band 0 sits below its median, band 6 at
# its top. The insight premium stays small and additive rather than multiplicative, because its job
# is to make the evidence route worth taking, not to put this route out of reach.
# Band 6 reuses band 5's base, so the top of the tree lands at 6600 + 7 * 200 = **8,000** -- exactly
# vanilla's single dearest project. That is deliberate rather than a coincidence of the formula: one
# project sits at the top of the whole tree, it earns the last level the Backrooms gives away, and
# pricing it at the ceiling of the distribution this generator was corrected against is the most
# honest number available. It is also the last band that can exist without raising MAX_COST in
# check-research-mirror.py, which would be moving the goalposts rather than paying them.
BAND_COST = [600, 1400, 2600, 4200, 6000, 6600, 6600]

# **THE COUNT IS ASSERTED SO A HALF-PARSED SOURCE CANNOT WRITE A HALF-SIZED TREE.** The regex above
# reads the company file by text; a renamed def class or a malformed block would simply match fewer
# projects, and the generator would then emit a mirror that `check-research-mirror.py` reports as
# dozens of unmirrored projects rather than as the one fault it is. So it refuses instead.
#
# **It moves when the tree grows, and that is the point of naming it here rather than inlining it.**
# 38 at 0.12.99-dev when the mirror was built, 42 with the four tier-5 projects, 43 with the one
# tier-6 project above them, 44 once Fieldcraft tier 5 found its second subject.
EXPECTED_PROJECTS = 44


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def tag(block, name):
    match = re.search(r"<%s>(.*?)</%s>" % (name, name), block, re.S)
    return match.group(1).strip() if match else ""


def branch_of(name):
    if name.startswith("RR_Gate"):
        return "Gate"
    match = re.match(r"RR_([A-Za-z]+)_", name)
    return match.group(1) if match else "Other"


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def safe_comment(lines):
    """Join comment lines, replacing every `--` with an em dash.

    **`--` IS ILLEGAL INSIDE AN XML COMMENT AND I HAVE NOW WRITTEN ONE THREE TIMES** -- in
    `RR_GateJobs.xml`, in `write-facility-def.py`, and here. The double hyphen is this repository's
    markdown habit and every other file in the tree takes it happily, so the mistake is invisible
    until a parser refuses the whole def file.
    *
    Sanitised at the point of writing rather than remembered, because remembering is exactly what
    failed three times. The em dash is the better character in reader prose anyway.
    """
    return NL.join(lines).replace("--", chr(8212))


def sanitise_comments(text):
    """Replace `--` inside every XML comment BODY, never in its delimiters.

    The first version of this sanitiser ran over the whole header and rewrote the `--` of `<!--`
    itself, producing a file that failed on line 2. The delimiters are the one place the sequence is
    legal, so they are the one place it must survive.
    """
    out = []
    cursor = 0
    while True:
        start = text.find("<!--", cursor)
        if start < 0:
            out.append(text[cursor:])
            return "".join(out)
        finish = text.find("-->", start + 4)
        if finish < 0:
            out.append(text[cursor:])
            return "".join(out)
        out.append(text[cursor:start + 4])
        out.append(text[start + 4:finish].replace("--", chr(8212)))
        out.append("-->")
        cursor = finish + 3


def main():
    source = io.open(SOURCE, encoding="utf-8-sig").read()
    blocks = re.findall(
        r"<RimroomsAsyncIndustries\.[A-Za-z.]*ProjectDef>(.*?)"
        r"</RimroomsAsyncIndustries\.[A-Za-z.]*ProjectDef>", source, re.S)
    projects = {}
    for block in blocks:
        name = tag(block, "defName")
        if not name:
            continue
        projects[name] = {
            "label": tag(block, "label"),
            "description": tag(block, "description"),
            "work": float(tag(block, "workRequired") or 6000),
            "insight": int(tag(block, "insightCost") or 1),
            "pre": re.findall(r"<li>([^<]+)</li>", tag(block, "prerequisiteProjects") or ""),
        }
    if len(projects) != EXPECTED_PROJECTS:
        say("expected %d company projects, parsed %d; refusing"
            % (EXPECTED_PROJECTS, len(projects)))
        return 1

    depth = {}

    def tier(name, seen=()):
        if name in depth:
            return depth[name]
        if name in seen:
            return 0
        parents = [p for p in projects[name]["pre"] if p in projects]
        depth[name] = 0 if not parents else 1 + max(tier(p, seen + (name,)) for p in parents)
        return depth[name]

    for name in projects:
        tier(name)

    # Tech level rises with the band, so a research mod sorting by tech level gets the same order
    # the bands already imply. Industrial at the bottom because a branch office is an industrial
    # operation, not a tribe.
    levels = ["Industrial", "Industrial", "Spacer", "Spacer", "Ultra", "Ultra", "Ultra"]

    rows = defaultdict(int)
    out = []
    for name in sorted(projects, key=lambda n: (COLUMNS.index(branch_of(n))
                                                if branch_of(n) in COLUMNS else 99,
                                                depth[n], n)):
        record = projects[name]
        branch = branch_of(name)
        column = COLUMNS.index(branch) if branch in COLUMNS else len(COLUMNS)
        band = depth[name]
        rows[(column, band)] += 1
        # Two projects in one cell would overlap in vanilla's view, so the second nudges sideways.
        nudge = (rows[(column, band)] - 1) * 0.45
        # Band base plus a small insight premium. See BAND_COST for why this is not
        # `workRequired` multiplied by anything.
        cost = BAND_COST[min(band, len(BAND_COST) - 1)] + record["insight"] * 200
        parents = [p for p in record["pre"] if p in projects]
        lines = ["  <ResearchProjectDef>",
                 "    <defName>%s%s</defName>" % (PREFIX, name),
                 "    <label>%s</label>" % escape(record["label"]),
                 "    <description>%s</description>" % escape(record["description"]),
                 "    <baseCost>%d</baseCost>" % int(round(cost)),
                 "    <techLevel>%s</techLevel>" % levels[min(band, len(levels) - 1)],
                 "    <tab>%s</tab>" % TAB,
                 "    <researchViewX>%.2f</researchViewX>" % (column * 1.0 + nudge),
                 "    <researchViewY>%.2f</researchViewY>" % (band * 1.0 + 0.5)]
        if parents:
            lines.append("    <prerequisites>")
            for parent in parents:
                lines.append("      <li>%s%s</li>" % (PREFIX, parent))
            lines.append("    </prerequisites>")
        lines.append("  </ResearchProjectDef>")
        out.append(NL.join(lines))

    header = NL.join([
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!--",
        "  GENERATED by .local/qa/generate-research-mirror.py. Do not hand-edit: every field is",
        "  derived from the company project it mirrors, and check-research-mirror.py asserts the",
        "  pairing. A mirror that drifts is a research tree that lies about what it unlocks.",
        "",
        "  Owner, 2026-10-06: \"AND A MAJOR ISSUE: I DONT SEE ANY RESEARCH FOR THE GATE SYSTEMS AND",
        "  EVERYTHING THIS MOD HAS!!!!!\" They were right to look in the Research tab. Every one of",
        "  the company projects existed and was reachable only through an Operations section, so this",
        "  mod contributed nothing to the tab every player opens, nor to ResearchTree or Research",
        "  Whatever, both of which the owner runs.",
        "",
        "  Asked how to fix it: \"Two genuine routes, either works\" and \"Own tab, nine columns by",
        "  band\". Then: \"as far as the research layout wit has to work bvanillia and with the",
        "  research mods\".",
        "",
        "  BOTH LAYOUT MECHANISMS ARE EMITTED because they are different mechanisms. Vanilla uses",
        "  researchViewX / researchViewY; every research mod derives its own layout from the",
        "  prerequisite graph. The coordinates give vanilla nine columns by seven bands, and the",
        "  graph is correct so each mod draws the same shape its own way. Columns are ragged on",
        "  purpose: four branches have nothing honest to put in the top band, and the company file",
        "  records the reason for each absence beside the tier it is absent from.",
        "",
        "  THE REGISTER ASKED FOR THIS SHAPE, which is why a steer that forbade shipping a",
        "  ResearchProjectDef at all is now wrong. Row 191 ResearchTree, planned use: \"The",
        "  Backrooms tree should own gate, mapping, containment, and spatial-analysis milestones",
        "  and should not overwrite other research trees\", and \"Backrooms milestones need stable",
        "  definitions and an independent route when optional trees are absent.\" Our own tab is",
        "  the not-overwriting. The Operations insight route is the independent one.",
        "",
        "  COST is a band base plus a small insight premium, MEASURED AGAINST VANILLA. The first",
        "  attempt used workRequired * (1 + insightCost) on the reasoning that both are bench work.",
        "  That was a unit error: our workRequired runs 4,000 to 18,000 and vanilla's 113 projects",
        "  run 200 to 8,000 with a median of 1,000, so it produced 8,000 to 108,000 -- the cheapest",
        "  mirror equalling vanilla's dearest project. Nobody would have finished one, so \"either",
        "  route works\" would have been false while looking true. Bands now sit inside vanilla's",
        "  own distribution and the insight premium is additive, because its job is to make the",
        "  evidence route worth taking rather than to put this one out of reach.",
        "-->",
        "<Defs>",
        "",
        "  <ResearchTabDef>",
        "    <defName>%s</defName>" % TAB,
        "    <label>Rimrooms</label>",
        "    <generalTitle>Company research</generalTitle>",
        "  </ResearchTabDef>",
        "",
    ])
    io.open(TARGET, "w", encoding="utf-8", newline=NL).write(sanitise_comments(
        header + (NL + NL).join(out) + NL + NL + "</Defs>" + NL))

    say("generate-research-mirror")
    say("  company projects    : %d" % len(projects))
    say("  mirrors written     : %d" % len(out))
    say("  tab                 : %s" % TAB)
    for column, branch in enumerate(COLUMNS):
        bands = sorted(depth[n] for n in projects if branch_of(n) == branch)
        say("    col %d  %-12s bands %s" % (column, branch, bands or "(none)"))
    costs = [BAND_COST[min(depth[n], len(BAND_COST) - 1)] + projects[n]["insight"] * 200
             for n in projects]
    say("  cost range          : %d to %d  (vanilla ships 200 to 8000, median 1000)"
        % (min(costs), max(costs)))
    say("  file                : %s" % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
