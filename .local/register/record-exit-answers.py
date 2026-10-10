# -*- coding: utf-8 -*-
"""Record the owner's answers at the exit fork, verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner answers (2026-09-29), at the exit fork:** *"Emerges on a fresh tile chosen by the seed"* / *"option 1 and the tutorial like quest chains should lay it all out"*

- [ ] **"Emerges on a fresh tile chosen by the seed"** - the exit opens onto a **fresh world tile**, and the tile is **derived deterministically from the coordinate's own seed** rather than chosen by the player. The survivor crawls out of a hole and comes out where the hole comes out. That surface map is then theirs to build a facility on, which is the older direction this serves: *"the solo/group start has to be able to get out and start building thsir facility"*.
- [ ] **"option 1"** - natural portals reach **through depth 3**, then stop. Level 1 where they start, plus two more levels found by doorway. Past that, deeper requires a gate they built.
- [ ] **"and the tutorial like quest chains should lay it all out"** - the solo/group start gets **its own tutorial line**, the way Async Industries has one. It has to teach, in order: that there is a way out and where to look, that coming out gives you a tile to build on, that the natural chain runs out at depth 3, and that a gate is how you go further. **Requests currently have no per-start scoping** - the six tutorial requests plus the hinge are Async's, unconditionally - so a second line needs the request shape to know which start it belongs to.

**Sequencing, decided rather than asked:** the bounded natural depth and the guaranteed exit ship together, because the exit is the load-bearing half of the direction and the depth cap is what gives it a point. The tutorial chain follows in its own checkpoint, because it needs a new field on the request shape and a second line of authored content, and rushing it behind the world-tile work is how a request line ends up teaching the wrong order.
"""

anchor = u'\n**Verbatim owner answers (2026-09-29), at the starts fork:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('exit answers recorded verbatim')
