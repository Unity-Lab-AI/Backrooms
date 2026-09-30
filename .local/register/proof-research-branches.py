# -*- coding: utf-8 -*-
"""Assert that no project promises an unlock nothing honours.

The property this exists for
----------------------------
A capability is a string on a def. Nothing about declaring one makes any system read it, and a
project whose card says "the gate needs less headroom" while no code looks at the capability is
**worse than a project with no effect at all** -- it is a lie the player has paid insight for,
and it is completely invisible: the def loads, the project completes, the card reads correctly,
and nothing happens.

This is the same failure class as the beacon condition that could never fire (0.10.7-dev) and the
tier ladder that could never be climbed (0.10.9-dev). Both compiled, both looked right in every
individual file, and both were only visible in the relationship between two places.

So: **every capability any project grants must be read by at least one source file**, and every
capability any source file reads must be granted by at least one project. Both directions,
because a read with no grant is dead code and a grant with no read is a lie.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                        "RimroomsProjectDefs", "RR_CompanyProjects.xml")
SRC = os.path.join(REPO, "src")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# --------------------------------------------------------------------------- the projects
projects = {}
for node in ET.parse(PROJECTS).getroot():
    name = node.findtext("defName")
    if not name:
        continue
    granted = []
    container = node.find("grantsCapabilities")
    for li in (container if container is not None else []):
        if li.text:
            granted.append(li.text.strip())
    projects[name.strip()] = {
        "insight": int(node.findtext("insightCost") or "1"),
        "work": float(node.findtext("workRequired") or "6000"),
        "route": int(node.findtext("requiredRouteLogs") or "0"),
        "distortion": int(node.findtext("requiredDistortionLogs") or "0"),
        "entity": int(node.findtext("requiredEntityLogs") or "0"),
        "prereqs": [li.text.strip() for li in (node.find("prerequisiteProjects") or [])],
        "grants": granted,
        "label": node.findtext("label"),
        "description": node.findtext("description"),
    }

# --------------------------------------------------------------------------- the source
source_by_file = {}
for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    source_by_file[rel] = io.open(path, encoding="utf-8-sig").read()

READ_CALL = re.compile(r'HasCapability\(\s*"([A-Za-z0-9_]+)"\s*\)')
read_in = {}
for rel, text in source_by_file.items():
    for capability in READ_CALL.findall(text):
        read_in.setdefault(capability, []).append(rel)

granted_all = sorted({c for data in projects.values() for c in data["grants"]})

print("projects defined     : %d" % len(projects))
print("capabilities granted : %d" % len(granted_all))
print("capabilities read    : %d" % len(read_in))
print("")

check("at least one project grants a capability", len(granted_all) > 0)

# ------------------------------------------------------------------ tier 3, and its restraints
# Tier 3 was DELETED rather than written at 0.12.5-dev because four of seven branches had nothing
# to move. Arc 5 wrote those systems, so it was written at 0.12.18-dev -- with two restraints that
# are the whole difference between an unlock and a design change, and that nothing else guards.
TIER3 = {
    "RR_Facilities_SiteNetwork": "RR_Cap_SiteNetwork",
    "RR_Commerce_SiteEfficiency": "RR_Cap_SiteEfficiency",
    "RR_Logistics_UnattendedDelivery": "RR_Cap_UnattendedDelivery",
    "RR_Spatial_CoordinateReading": "RR_Cap_CoordinateReading",
    "RR_Fieldcraft_WayHomeDiscipline": "RR_Cap_WayHomeDiscipline",
    "RR_Measurement_RapidSurvey": "RR_Cap_RapidSurvey",
    "RR_Entities_SpaceDiscipline": "RR_Cap_SpaceDiscipline",
}
missing = [name for name in TIER3 if name not in projects]
check("all seven tier-3 projects are authored, one per branch",
      not missing,
      "-- %s: a tier with a hole in it is a tier that steers every player down the same branch"
      % ", ".join(sorted(missing)))
for name, capability in sorted(TIER3.items()):
    if name not in projects:
        continue
    check("%s requires an entity log" % name,
          projects[name]["entity"] >= 1,
          "-- tier 3 is the first tier that asks whether the branch has MET something")
    check("%s grants %s" % (name, capability),
          capability in projects[name]["grants"])

frontier = io.open(os.path.join(SRC, "RimroomsAsyncIndustries", "Portals",
                              "NaturalFrontierService.cs"),
                   encoding="utf-8-sig").read()
pressure = io.open(os.path.join(SRC, "RimroomsAsyncIndustries", "Threats",
                              "BackroomsPressure.cs"),
                   encoding="utf-8-sig").read()

# RESTRAINT 1. The per-coordinate cap must never become a research knob. Its own summary says
# raising it is a design decision rather than a tuning knob, because the cap is what keeps a chain
# of spaces finite. Spatial makes the two arrive SOONER; it must never make them three.
# Keyed off the ASSIGNMENT, not off what happens to sit near it. The first version of this claim
# looked for the capability name within 400 characters of the cap and failed the moment the
# capability-aware RARITY line was written directly above it -- proximity is not the thing that
# happens, and that is the same mistake this project has caught four times.
# **RESTATED 0.12.49-dev. The restraint is unchanged; only its wording is.** The owner raised the
# count to four-to-six per level, so a claim that the assignment is a bare constant no longer
# describes anything worth protecting. What this restraint always protected is that **RESEARCH
# cannot buy more ways onward**, and that is now asserted MORE strictly: by reading the deciding
# function's own body rather than by inspecting the shape of an assignment. Scaling with the size
# of the place is a property of the place; a capability would be a tuning knob.
cap_assignment = re.search(r"Cap\s*=\s*([^,\r\n]+),", frontier)
frontiers_at = frontier.find("internal static int FrontiersFor(CoordinateRecord coordinate)")
frontiers_body = frontier[frontiers_at:frontier.find(chr(10) + "        }", frontiers_at)] \
    if frontiers_at >= 0 else ""
check("the per-coordinate frontier count comes from one named function",
      cap_assignment is not None
      and cap_assignment.group(1).strip() == "FrontiersFor(record)"
      and frontiers_at >= 0,
      "-- one deciding place, so there is exactly one body to read. Found %r"
      % (cap_assignment.group(1).strip() if cap_assignment else None))
check("NO RESEARCH CAPABILITY CAN BUY MORE WAYS ONWARD",
      frontiers_at >= 0 and "Capability" not in frontiers_body,
      "-- THIS is the restraint, and it survives the count being raised: how many ways onward a "
      "place offers is a property of the place, never something a branch can research")
check("the count is still bounded by a constant ceiling",
      "MaximumFrontiersPerCoordinate" in frontiers_body
      and re.search(r"const\s+int\s+MaximumFrontiersPerCoordinate\s*=\s*\d+", frontier) is not None,
      "-- a chain of spaces still has to be finite, and the ceiling is what keeps it so")
check("it scales on the size of the place and nothing else",
      "coordinate.Rooms.Count" in frontiers_body and "Depth" not in frontiers_body,
      "-- read from the room count rather than the depth, so it stays correct if the planner's "
      "depth profile changes again")
check("only the rarity is capability-aware, and it moves WHEN not HOW MANY",
      'HasCapability("RR_Cap_CoordinateReading")' in frontier
      and "PractisedFrontierRarity : FrontierRarity" in frontier,
      "-- the unlock must move how SOON a way onward is found, never how many exist")

# RESTRAINT 2. Shelter must never reach zero. A coordinate is always wearing, and no player may
# build a room that makes the place ordinary.
check("the improved shelter rate is still above zero",
      "DisciplinedShelterRate = 0.12f" in pressure,
      "-- a shelter rate of zero would let a player build a room that makes the Backrooms an "
      "ordinary building, which is the one thing the base constant exists to forbid")
check("the improved shelter rate is worse than no pressure and better than the base",
      "Mathf.Lerp(1f, best, Mathf.Clamp01(score))" in pressure
      and "DisciplinedShelterRate : BestShelterRate" in pressure,
      "-- the unlock must interpolate toward a better floor, never remove the floor")

# 1. THE property. Every granted capability is honoured by a real read site.
for capability in granted_all:
    sites = read_in.get(capability, [])
    check("%s is read by %s" % (capability, sites[0] if sites else "NOTHING"),
          len(sites) > 0,
          "-- the card promises an unlock and no code honours it")

# 2. The other direction. A read with no grant is dead code that can never be true.
for capability, sites in sorted(read_in.items()):
    check("%s is granted by a project" % capability,
          any(capability in data["grants"] for data in projects.values()),
          "-- read in %s but no project grants it" % ", ".join(sites))

# 3. A capability must not be granted twice. Two projects granting one capability means the
#    second is free, which is not what a card claiming an unlock implies.
for capability in granted_all:
    owners = [name for name, data in projects.items() if capability in data["grants"]]
    check("%s is granted by exactly one project" % capability, len(owners) == 1,
          "-- granted by " + ", ".join(sorted(owners)))

# 4. Tier 0 is the entry band, so its projects must have NO prerequisites. A root with a
#    prerequisite is not a root, and the branch it heads becomes unreachable.
roots = [name for name, data in projects.items() if not data["prereqs"]]
check("there are at least two independent roots (%d)" % len(roots), len(roots) >= 2,
      "-- a tree with one entrance is a single point of failure")

# 5. A root must be startable by a branch that has analysed one record and nothing more:
#    one insight, and no distortion or entity log, because those need things to have gone wrong.
for name in sorted(roots):
    data = projects[name]
    check("root %s needs no distortion or entity log" % name,
          data["distortion"] == 0 and data["entity"] == 0,
          "-- a new branch cannot start this branch of the tree")

# 6. Every project's card must actually say something. A blank description on a paid unlock is
#    the same problem as a missing effect, one layer up.
for name, data in sorted(projects.items()):
    check("%s has a label and a description" % name,
          bool(data["label"]) and bool(data["description"]) and len(data["description"]) > 40)

# 7. No prerequisite naming a project that does not exist, and no cycle.
for name, data in sorted(projects.items()):
    for required in data["prereqs"]:
        check("%s requires %s, which exists" % (name, required), required in projects,
              "-- unreachable forever")


def reaches(start, target, seen=None):
    seen = seen or set()
    if start in seen:
        return False
    seen.add(start)
    for required in projects.get(start, {}).get("prereqs", []):
        if required == target or reaches(required, target, seen):
            return True
    return False


cycles = [n for n in projects if reaches(n, n)]
check("no project requires itself through any chain", not cycles, "-- " + ", ".join(cycles))


# 8. THE CHART'S LINKAGE RULE. "Every tier above 0 must be reachable by more than one path" --
#    a band that can only be entered through one project is a single point of failure for a
#    player who has not happened to generate the right log.
#
#    Depth is the longest prerequisite chain, which is the tier a project actually sits at
#    regardless of what its name suggests.
def depth(name, seen=None):
    seen = seen or set()
    if name in seen:
        return 0
    seen.add(name)
    prereqs = projects.get(name, {}).get("prereqs", [])
    return 0 if not prereqs else 1 + max(depth(p, set(seen)) for p in prereqs)


def root_ancestors(name, seen=None):
    seen = seen or set()
    if name in seen:
        return set()
    seen.add(name)
    prereqs = projects.get(name, {}).get("prereqs", [])
    if not prereqs:
        return {name}
    found = set()
    for required in prereqs:
        found |= root_ancestors(required, set(seen))
    return found


depths = {}
for name in projects:
    depths.setdefault(depth(name), []).append(name)

print("")
for level in sorted(depths):
    print("  depth %d : %d project(s)" % (level, len(depths[level])))
print("")

#    The first version of this claim was WRONG, and the tree was right. It asserted that every
#    depth must contain projects tracing to two or more roots -- which the gate ladder fails by
#    design, because it is deliberately a single linear chain of four rungs and was proved
#    ordered and monotonic in 0.10.9-dev. Depth 2 and depth 3 are simply its upper rungs.
#
#    The chart's rule is about ENTERING a branch, not about every depth being wide:
#
#        "a branch that can only be entered through one project is a single point of failure
#         for a player who has not happened to generate the right log"
#
#    So what must be true is that the tree has several entrances -- asserted above, eight of
#    them -- and that no project downstream becomes a CHOKEPOINT where separate branches merge.
#    A linear chain within one branch is fine. A project that two different branches both have
#    to pass through is not.
for name in sorted(projects):
    if not projects[name]["prereqs"]:
        continue
    dependents = [other for other in projects if other != name and reaches(other, name)]
    lineages = set()
    for other in dependents:
        lineages |= root_ancestors(other)
    lineages |= root_ancestors(name)
    check("%s is not a chokepoint between branches (%d lineage(s))" % (name, len(lineages)),
          len(lineages) <= 1,
          "-- two branches merge here, so one project gates both")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every unlock a project promises is honoured by real code")
