# -*- coding: utf-8 -*-
"""The last stale plant, and the corridor guard claim that had to count both axes.

`furniture lands on the middle of a corridor and blocks the route` was MISSED because the guard
that keeps the centre line out of the reported cells exists **on both axes** -- once in the
horizontal run and once in the vertical. The plant removed one and the claim, reading the whole
file, was satisfied by the other. Thirty-ninth instance of the scoping trap, and the fix is the
same as it always is: count, or scope.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAYOUT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

STALE_OLD = u'''    ("SHALLOW COORDINATES START DEFORMING TOO", PLANNER,
     "            if (room == null || depth <= 1) { yield break; }",
     "            if (room == null) { yield break; }"),'''
STALE_NEW = u'''    ("SHALLOW COORDINATES START DEFORMING TOO", PLANNER,
     "            if (room == null || room.index == 0 || depth <= 1) { yield break; }",
     "            if (room == null || room.index == 0) { yield break; }"),'''

CLAIM_OLD = u'''      and "if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))" in genstep'''
CLAIM_NEW = u'''      # **BOTH AXES.** The guard that keeps the centre line out of the reported cells exists
      # once in the horizontal run and once in the vertical, so a plant that removed one was
      # satisfied by the other. Counted rather than merely found -- thirty-ninth instance.
      and genstep.count(
          "if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))") == 2'''

for path, old, new in [(LAYOUT, STALE_OLD, STALE_NEW), (PROOF, CLAIM_OLD, CLAIM_NEW)]:
    text = io.open(path, encoding="utf-8").read()
    if text.count(old) != 1:
        print("ANCHOR PROBLEM in %s: %d" % (os.path.basename(path), text.count(old)))
        raise SystemExit(1)
    io.open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new, 1))
    print("updated %s" % os.path.basename(path))
