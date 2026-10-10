# -*- coding: utf-8 -*-
"""Record the gate-placement / build-around direction verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner direction (2026-09-29), gate placement and building around a portal:** *"and technically the way the gate works and make a portal when placing it on your map or having a natural one(natruals can not be destoryed or moved, so one can technically build a roomm directly on the other side of the portal door and it shouldnt interfere with the portal transition to the seeded backrooms"*

- [ ] **"natruals can not be destoryed or moved"** - a natural gate is **indestructible and immovable**. It is not something the branch built and it is not something the branch can unbuild. **Check first whether this is already true:** a natural gate is a Core `Door` with a registered natural address, and a Core door has hit points and a deconstruct designation, so a player can very probably destroy one today - which would break a connection the design calls **permanently open**.
- [ ] **"one can technically build a roomm directly on the other side of the portal door"** - the player may build **on the local map**, right up against and around the portal door, including enclosing its far face in a room of their own.
- [ ] **"and it shouldnt interfere with the portal transition to the seeded backrooms"** - and none of that may break the crossing. **This is the part most likely to be broken today:** every threshold is validated through `PortalAddressService.UsableThreshold(door, approach, map)` against an **approach cell**, and a wall built on that cell would make a permanently open gate refuse. A player who builds a proper airlock around their own gate must not lose it by doing so.
- [ ] **What to work out before building any of it:** whether the approach cell should be re-derived when the local geometry changes, or whether the rule should be that a portal door's approach cell simply cannot be built on - and if the latter, how the player is told. Both readings are defensible, which by invariant 134 means asking rather than guessing.
"""

anchor = u'\n**Verbatim owner answer (2026-09-29), at the exit-route fork:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('gate-building direction recorded verbatim')
