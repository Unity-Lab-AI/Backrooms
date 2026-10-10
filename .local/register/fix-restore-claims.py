# -*- coding: utf-8 -*-
"""Two claims were deleted by my own fix script, and the plants said so.

`fix-claim-scope.py` rebuilt the file as `text[:start] + replacement + text[end:]`, where `start`
was the claim being re-scoped and `end` was the next section header -- so **everything between
them went**, and two claims that sat in that gap were silently removed. The plant suite caught it
immediately: *"A LANDMARK REFUSAL GOES SILENT AGAIN"* and *"the route cross is derived in two
places again"* were both MISSED, because the claims that would have refused them no longer
existed.

**An anchored span is only safe when you have read what is inside it.** Two anchors and a slice
is a delete, and this one deleted work from four minutes earlier.

A third plant was missed for a different reason: the margin claim asserted the fallback
machinery -- the `withoutMargin` variable and its return -- and a plant that restored the hard
`continue` left all of that in place and simply never reached it. **The machinery is not the
behaviour.** The claim now pins the branch that returns the margined cell, which is the line the
plant has to touch.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

STRENGTHEN_OLD = u'''check("THE WALKABLE MARGIN IS A PREFERENCE, NOT A REQUIREMENT",
      "private static IntVec3 FixtureCell(" in content
      and "IntVec3 withoutMargin = IntVec3.Invalid;" in content
      and "if (!withoutMargin.IsValid) { withoutMargin = cell; }" in content
      and "return withoutMargin;" in content,'''

STRENGTHEN_NEW = u'''check("THE WALKABLE MARGIN IS A PREFERENCE, NOT A REQUIREMENT",
      "private static IntVec3 FixtureCell(" in content
      and "IntVec3 withoutMargin = IntVec3.Invalid;" in content
      and "if (!withoutMargin.IsValid) { withoutMargin = cell; }" in content
      and "return withoutMargin;" in content
      # **THE BRANCH, not just the machinery it feeds.** A plant restored the hard `continue` and
      # left every line above it untouched, so the fallback still existed and was simply never
      # reached. Computing a value and using it are two different facts, for the fourth time.
      and "if (!footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
      in content
      and "{ return cell; }" in content
      and "if (footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
      not in content,'''

RESTORE_ANCHOR = u'''# -------------------------------------------------- two transmitters on one cell'''

RESTORED = u'''check("A LANDMARK REFUSAL SAYS WHICH ROOM",
      "No cell for the landmark " in content
      and "room.familyId" in content and "room.width" in content,
      "-- last time this threw, the log carried the method and a key and nothing else, so the "
      "room had to be reasoned about from the arithmetic of every room it could have been")

check("and the route cross is derived in exactly one place",
      "internal static bool OnRouteCross(" in content
      and "if (OnRouteCross(room, cell)) { reserved.Add(cell); } }" in content
      and "Math.Abs(cell.x - center.x) <= 1 || Math.Abs(cell.z - center.z) <= 1" in content,
      "-- the layout probe counts placeable cells against it, so a second copy of the rule would "
      "let the probe and the generator disagree about what is reserved. **These two claims were "
      "deleted by a fix script that sliced between two anchors without reading what was between "
      "them**, and the plant suite is what noticed")

''' + RESTORE_ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
EDITS = [(STRENGTHEN_OLD, STRENGTHEN_NEW), (RESTORE_ANCHOR, RESTORED)]
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("two claims restored, the margin claim now pins the branch")
