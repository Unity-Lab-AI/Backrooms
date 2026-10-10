# -*- coding: utf-8 -*-
"""Two more requirements, given while the level work was in flight."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ROW = u"""## IN PROGRESS — lights and geometry — 2026-09-30 (0.12.61-dev)

Owner, verbatim:

> **"and we need more lights and mixedered varies of lights but the main grand themed backrooms
> universe rooms need like a wall light on every column wall used as in the universe of backrooms
> the basic rooms are well lit"**

> **"and you can have back to back roomes and mazes of halways of varied widtchs and lengs and odd
> variers walls and contructions making narrows , expansies, triangle, octangones, rombones, all
> the geomentry and mixetrues and odd contructions of doors walls corners deadends doors to now
> where not just doors on 4 cosides of nothing but square rooms"**

- [ ] **"we need more lights and mixedered varies of lights"**
- [ ] **"the main grand themed backrooms universe rooms need like a wall light on every column wall used"** — the pillar lattice already exists in `RoomLayoutPlanner.PillarCells`, so every pillar is a known cell with a wall to hang a lamp on
- [ ] **"as in the universe of backrooms the basic rooms are well lit"** — brightness is part of the theme, not a convenience
- [ ] **"you can have back to back roomes"** — rooms sharing a wall, with no corridor between
- [ ] **"mazes of halways of varied widtchs and lengs"**
- [ ] **"odd variers walls and contructions making narrows , expansies"**
- [ ] **"triangle, octangones, rombones, all the geomentry and mixetrues"**
- [ ] **"odd contructions of doors walls corners deadends"**
- [ ] **"doors to now where"** — a door that opens onto solid rock or a sealed closet
- [ ] **"not just doors on 4 cosides of nothing but square rooms"** — the current rule is literally a doorway at the midpoint of each of four walls

---

"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("ten more rows recorded, verbatim")
