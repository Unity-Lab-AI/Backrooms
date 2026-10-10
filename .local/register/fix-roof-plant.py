# -*- coding: utf-8 -*-
"""A plant that could never be caught, because it planted a comment at a proof that strips them.

`plant-areas-and-debrief.py` planted this into `RoofWorkProvider`:

    if (map.ParentHolder is object) { /* Backrooms Coordinate check */ }

...and required `proof-areas-and-debrief.py` to fail. It never could: the proof reads that file
through `strip_cs_comments`, deliberately, because the claim is *"the roof provider contains no
Backrooms exception OF ITS OWN"* and a comment mentioning the Backrooms is not a second opinion
that can drift. **The proof was right and the plant was wrong** -- the inverse of the trap that
has bitten twenty-one times, where a comment satisfied a code claim. Here a comment was expected
to violate one.

Planted as real code now: a depth test that short-circuits the provider is exactly the second
opinion the claim forbids, and the proof catches it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-areas-and-debrief.py")

OLD = u'''    ("the roof provider grows a Backrooms exception of its own", ROOF,
     "        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)\\n        {",
     "        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)\\n"
     "        {\\n            if (map.ParentHolder is object) { /* Backrooms Coordinate check */ }"),'''

NEW = u'''    # REAL CODE, NOT A COMMENT. This plant used to insert
    # `/* Backrooms Coordinate check */` and demand a failure, which the proof could never
    # deliver: it reads this file through `strip_cs_comments` on purpose, because a comment
    # naming the Backrooms is not a second opinion that can drift out of step with the rule.
    # A depth test that short-circuits the provider is, so that is what gets planted.
    ("the roof provider grows a Backrooms exception of its own", ROOF,
     "        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)\\n        {",
     "        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)\\n"
     "        {\\n            if (BackroomsCoordinateDepthOf(map) > 0) { return false; }"),'''

text = io.open(PLANT, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the roof plant plants code now")
