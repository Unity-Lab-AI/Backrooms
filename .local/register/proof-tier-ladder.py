# -*- coding: utf-8 -*-
"""Assert that the window-tier ladder is actually reachable.

The defect this exists to prevent: `portalIndefiniteTier` was 4 while the ladder listed ONE
project, so `PortalWindowTier` could never exceed 1 and a standing connection was unreachable
no matter how a branch played. Every individual value was valid, which is exactly why no
checker saw it.

Run from the repository root.
"""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                        "RimroomsProjectDefs", "RR_CompanyProjects.xml")
GATE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "CompRimroomsGate.cs")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# --------------------------------------------------------------------------- the defs
root = ET.parse(PROJECTS).getroot()
projects = {}
for node in root:
    name = node.findtext("defName")
    projects[name] = {
        "insight": int(node.findtext("insightCost") or "1"),
        "work": float(node.findtext("workRequired") or "6000"),
        "route": int(node.findtext("requiredRouteLogs") or "0"),
        "distortion": int(node.findtext("requiredDistortionLogs") or "0"),
        "entity": int(node.findtext("requiredEntityLogs") or "0"),
        "prereqs": [li.text.strip() for li in (node.find("prerequisiteProjects") or [])],
    }

# --------------------------------------------------------------------------- the ladder + tier
source = io.open(GATE, encoding="utf-8-sig").read()
ladder_block = re.search(r"portalWindowTierProjects = new List<string>\s*\{(.*?)\}", source, re.S)
ladder = re.findall(r'"([A-Za-z0-9_]+)"', ladder_block.group(1)) if ladder_block else []
indefinite = int(re.search(r"portalIndefiniteTier = (\d+);", source).group(1))

print("projects defined : %d" % len(projects))
print("ladder rungs     : %d  (%s)" % (len(ladder), ", ".join(ladder)))
print("indefinite tier  : %d" % indefinite)
print("")

# 1. THE defect. The tier can only rise once per completed ladder project, so the ladder must
#    be at least as long as the tier that unlocks an indefinite connection.
check("the ladder is long enough to reach the indefinite tier (%d rungs >= %d)"
      % (len(ladder), indefinite), len(ladder) >= indefinite,
      "-- a standing connection is UNREACHABLE")

# 2. Every rung must be a project that exists, or the tier silently never counts it.
for name in ladder:
    check("ladder rung %s is a defined project" % name, name in projects,
          "-- not in RR_CompanyProjects.xml")

# 3. No duplicate rungs: the tier counts one per entry, so a repeat would inflate it.
check("no ladder rung is listed twice", len(set(ladder)) == len(ladder))

# 4. The ladder must be a single chain in order. Rung N must require rung N-1, or a branch with
#    enough insight completes the top rung first and skips everything below it.
for index in range(1, len(ladder)):
    previous, current = ladder[index - 1], ladder[index]
    if current not in projects:
        continue
    check("%s requires %s" % (current, previous),
          previous in projects[current]["prereqs"],
          "-- the ladder can be climbed out of order")

# 5. Requirements must be non-decreasing up the ladder. A later rung that is cheaper to qualify
#    for than an earlier one makes the order meaningless.
for kind in ("route", "distortion", "entity", "insight", "work"):
    values = [projects[n][kind] for n in ladder if n in projects]
    check("%s requirement never decreases up the ladder (%s)"
          % (kind, " -> ".join(str(v) for v in values)),
          all(values[i] <= values[i + 1] for i in range(len(values) - 1)))

# 6. No prerequisite may name a project that does not exist: that rung would be unreachable
#    forever, which is the same failure mode in a different place.
for name, data in sorted(projects.items()):
    for required in data["prereqs"]:
        check("%s requires %s, which exists" % (name, required), required in projects,
              "-- unreachable forever")

# 7. No cycles. A cycle is unreachable content that looks completely normal in every def.
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

# 8. The first rung must be startable from nothing but a single survey. A ladder whose bottom
#    rung already needs a distortion or an entity log cannot be started by a new branch.
if ladder and ladder[0] in projects:
    first = projects[ladder[0]]
    check("the first rung needs no prerequisite", not first["prereqs"])
    check("the first rung needs no distortion or entity log",
          first["distortion"] == 0 and first["entity"] == 0,
          "-- a new branch cannot begin the ladder")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the ladder is reachable, ordered and monotonic")
