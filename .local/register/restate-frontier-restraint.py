# -*- coding: utf-8 -*-
"""Restate the frontier-count restraints for 0.12.49-dev, more strictly than before.

The owner raised the count to four-to-six per level and the depth reach to six. Two proofs
correctly objected, because they encoded the previous decisions. What those restraints were ever
protecting is preserved and asserted harder:

  * research must never buy more ways onward, and
  * the chain of spaces must stay finite.

Written as a FILE. A bash heredoc mangled the escapes in this exact edit, which is the seventh
time in two days -- see the rule in docs/NOW.md.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(REPO, ".local", "register")

BRANCHES = os.path.join(REG, "proof-research-branches.py")
TIER4 = os.path.join(REG, "proof-research-tier4.py")
STARTS = os.path.join(REG, "proof-starts.py")

# ---------------------------------------------------------------- proof-research-branches.py
branches = io.open(BRANCHES, encoding="utf-8").read()

old = '''cap_assignment = re.search(r"Cap\\s*=\\s*([^,\\r\\n]+),", frontier)
check("the per-coordinate frontier cap is assigned the bare constant",
      cap_assignment is not None
      and cap_assignment.group(1).strip() == "MaximumFrontiersPerCoordinate",
      "-- raising the cap is a DESIGN decision, not a tuning knob: the cap is what keeps a chain "
      "of spaces finite. Found %r"
      % (cap_assignment.group(1).strip() if cap_assignment else None))
check("no second per-coordinate cap constant exists to switch to",
      len(re.findall(r"const\\s+int\\s+\\w*FrontiersPerCoordinate\\s*=", frontier)) == 1,
      "-- an 'expanded cap' constant is the shape this restraint exists to forbid")'''

new = '''# **RESTATED 0.12.49-dev. The restraint is unchanged; only its wording is.** The owner raised the
# count to four-to-six per level, so a claim that the assignment is a bare constant no longer
# describes anything worth protecting. What this restraint always protected is that **RESEARCH
# cannot buy more ways onward**, and that is now asserted MORE strictly: by reading the deciding
# function's own body rather than by inspecting the shape of an assignment. Scaling with the size
# of the place is a property of the place; a capability would be a tuning knob.
cap_assignment = re.search(r"Cap\\s*=\\s*([^,\\r\\n]+),", frontier)
frontiers_at = frontier.find("internal static int FrontiersFor(CoordinateRecord coordinate)")
frontiers_body = frontier[frontiers_at:frontier.find(chr(10) + "        }", frontiers_at)] \\
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
      and re.search(r"const\\s+int\\s+MaximumFrontiersPerCoordinate\\s*=\\s*\\d+", frontier) is not None,
      "-- a chain of spaces still has to be finite, and the ceiling is what keeps it so")
check("it scales on the size of the place and nothing else",
      "coordinate.Rooms.Count" in frontiers_body and "Depth" not in frontiers_body,
      "-- read from the room count rather than the depth, so it stays correct if the planner's "
      "depth profile changes again")'''

if branches.count(old) != 1:
    print("BRANCHES ANCHOR PROBLEM: %d" % branches.count(old))
    raise SystemExit(1)
branches = branches.replace(old, new, 1)

old2 = '''check("only the rarity is capability-aware, and it still refuses more than two",'''
new2 = '''check("only the rarity is capability-aware, and it moves WHEN not HOW MANY",'''
if branches.count(old2) != 1:
    print("BRANCHES ANCHOR 2 PROBLEM: %d" % branches.count(old2))
    raise SystemExit(1)
branches = branches.replace(old2, new2, 1)

io.open(BRANCHES, "w", encoding="utf-8", newline="").write(branches)
print("proof-research-branches: restraint restated")

# ---------------------------------------------------------------- proof-research-tier4.py
tier4 = io.open(TIER4, encoding="utf-8").read()
print("--- tier4 claims that mention the cap or the depth ---")
for index, line in enumerate(tier4.split(chr(10)), 1):
    if "frontier cap" in line or "natural depth" in line or "MaximumNaturalDepth" in line \
            or "MaximumFrontiersPerCoordinate" in line:
        print("%5d  %s" % (index, line.rstrip()))

# ---------------------------------------------------------------- proof-starts.py
starts = io.open(STARTS, encoding="utf-8").read()
print("--- starts claims that mention the depth ---")
for index, line in enumerate(starts.split(chr(10)), 1):
    if "natural depth" in line or "MaximumNaturalDepth" in line or "depth 3" in line:
        print("%5d  %s" % (index, line.rstrip()))
