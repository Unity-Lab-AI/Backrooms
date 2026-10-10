# -*- coding: utf-8 -*-
"""A plant put the room back on its host's wall column and every proof still passed.

The planted fault was one character: `mover.x = b.maxX + 1` back to `mover.x = b.maxX`. Nothing
caught it, and the reason is worth more than the fix.

**The revert guard swallowed it.** The pushed room now overlapped its host, `collides` saw that,
and the move was undone -- so the layout stayed perfectly valid and simply **never produced a
single back-to-back pair again.** No refusal, no error, nothing in a log. The feature would have
been switched off and every one of forty-five proofs would have agreed it was present, because the
function is there, the call is there, and the guard is there.

That is the dominant defect class in this project -- content and behaviour switched off, with
proofs that read source text unable to see it -- and it is the reason `PlannerProbe` exists. The
probe counts the pairs. A source claim cannot.

So two things change: this claim pins the four push expressions, and the probe joins the battery
as a checker, because the one thing that can see absence should not be the one thing nobody runs.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

ANCHOR = u'''check("AND THE PUSH IS PUT BACK IF IT LANDED ON SOMEBODY",'''

NEW = u'''check("THE PUSH LANDS ONE CELL CLEAR, ON ALL FOUR SIDES",
      "if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX + 1; }" in planner
      and "else if (verticalOverlap && a.maxX < b.minX) { mover.x = b.minX - a.Width - 1; }" in planner
      and "else if (horizontalOverlap && a.minZ > b.maxZ) { mover.z = b.maxZ + 1; }" in planner
      and "else if (horizontalOverlap && a.maxZ < b.minZ) { mover.z = b.minZ - a.Height - 1; }" in planner,
      "-- all four, because the first draft had two branches overlap and two abut, and the two "
      "that abutted were the ones the old `SharesWall` could not see. **A plant that dropped the "
      "+ 1 from one branch was missed by every proof**: the revert guard caught the overlap and "
      "put the room back, so the layout stayed valid and simply never produced a back-to-back "
      "pair again. Switched off, silently, with every claim still passing -- which is what "
      "`PlannerProbe` counts and a source claim cannot")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("the four push expressions are now claimed")
