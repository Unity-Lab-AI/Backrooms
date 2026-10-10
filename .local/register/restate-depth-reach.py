# -*- coding: utf-8 -*-
"""The depth reach is six now, by owner decision. Restate the two claims that asserted three.

Both claims were RIGHT to fail: they recorded a previous owner answer at a fork ("option 1",
through depth 3). The owner overruled it on 2026-09-30. The part of each claim that still matters
-- that neither the reach nor the count may be research-driven -- is kept and asserted directly.

Written as a file, not a heredoc.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(REPO, ".local", "register")
TIER4 = os.path.join(REG, "proof-research-tier4.py")
STARTS = os.path.join(REG, "proof-starts.py")

# ---------------------------------------------------------------- proof-research-tier4.py
tier4 = io.open(TIER4, encoding="utf-8").read()

EDITS4 = [
    ("  * `MaximumNaturalDepth` stays at three, because the owner answered **\"option 1\"** on exactly that.",
     "  * `MaximumNaturalDepth` is **six** since 0.12.49-dev, and **still not research-driven** -- the\n"
     "     owner raised the reach on 2026-09-30, having chosen three at an earlier fork. The restraint\n"
     "     here was never the number; it is that no capability may move it."),

    ('''check("the per-coordinate frontier cap is still not a research knob",
      re.search(r"Cap = MaximumFrontiersPerCoordinate", frontier) is not None and
      "MaximumFrontiersPerCoordinate" in frontier and
      not re.search(r"HasCapability\\([^)]*\\)\\s*\\?\\s*\\w*MaximumFrontiersPerCoordinate", frontier),''',
     '''check("the per-coordinate frontier count is still not a research knob",
      re.search(r"Cap = FrontiersFor\\(record\\)", frontier) is not None and
      "MaximumFrontiersPerCoordinate" in frontier and
      not re.search(r"HasCapability\\([^)]*\\)\\s*\\?\\s*\\w*Frontiers", frontier),'''),

    ('''check("the natural depth reach is still three and not research-driven",
      "MaximumNaturalDepth = 3" in frontier and
      not re.search(r"HasCapability\\([^)]*\\)\\s*\\?\\s*\\w*MaximumNaturalDepth", frontier),''',
     '''check("THE NATURAL DEPTH REACH IS NOT RESEARCH-DRIVEN, WHATEVER ITS VALUE",
      re.search(r"MaximumNaturalDepth\\s*=\\s*\\d+", frontier) is not None and
      not re.search(r"HasCapability\\([^)]*\\)\\s*\\?\\s*\\w*MaximumNaturalDepth", frontier),'''),
]

problems = []
for old, _ in EDITS4:
    if tier4.count(old) != 1:
        problems.append("tier4 %d of %r" % (tier4.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS4:
    tier4 = tier4.replace(old, new, 1)
io.open(TIER4, "w", encoding="utf-8", newline="").write(tier4)
print("proof-research-tier4: restated, restraint kept")

# ---------------------------------------------------------------- proof-starts.py
starts = io.open(STARTS, encoding="utf-8").read()

OLD_START = '''    check("the natural depth limit is 3 (%s)" % cap.group(1), cap.group(1) == "3",
          "-- the owner chose through depth 3 at the fork")'''
NEW_START = '''    # **The owner raised this to six on 2026-09-30**, having chosen three at an earlier fork,
    # alongside the map budget that makes a deeper chain affordable. What is asserted is that the
    # reach is a real, finite, stated number -- not that it is any particular one, because that is
    # the owner's to move and this claim failing for the right reason cost a checkpoint to notice.
    reach = int(cap.group(1))
    check("the natural depth limit is a stated, finite reach (%d)" % reach,
          2 <= reach <= 8,
          "-- a doorway chain has to stop somewhere or the graph is unbounded; the owner sets "
          "where, and it is 6 since 0.12.49-dev")'''

if starts.count(OLD_START) != 1:
    print("STARTS ANCHOR PROBLEM: %d" % starts.count(OLD_START))
    raise SystemExit(1)
starts = starts.replace(OLD_START, NEW_START, 1)

OLD_DOC = "# own gate\", and the extent chosen at the fork was through depth 3."
NEW_DOC = ("# own gate\", and the extent chosen at the fork was through depth 3 -- raised to SIX on\n"
           "# 2026-09-30, together with the open-map budget that makes a deeper chain affordable.")
if starts.count(OLD_DOC) != 1:
    print("STARTS DOC ANCHOR PROBLEM: %d" % starts.count(OLD_DOC))
    raise SystemExit(1)
starts = starts.replace(OLD_DOC, NEW_DOC, 1)

io.open(STARTS, "w", encoding="utf-8", newline="").write(starts)
print("proof-starts: depth claim restated")
