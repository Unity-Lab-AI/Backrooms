# -*- coding: utf-8 -*-
"""Record the no-projection clarification verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner clarification (2026-09-29), immediately after the above:** *"if u get what i mean .. in the real world maps the portals dont extend into the real world environment so in the real world you can mine and build and explore directly behind the gates with out actually effecting the gate, unless there is connected need requipremd equipemnet directly required placemnets behind the pgate doors.. so yeah you get it"*

- [ ] **"in the real world maps the portals dont extend into the real world environment"** - **a portal is exactly its own door cell and reserves nothing else.** There is no aura, no claimed radius, no protected zone and no reservation projected onto the local map. This is the rule the two preceding directions were pointing at.
- [ ] **"in the real world you can mine and build and explore directly behind the gates with out actually effecting the gate"** - the cells around and behind a gate are **ordinary map**. Mine them, wall them, roof them, put a bedroom there. The gate does not care and must keep working.
- [ ] **"unless there is connected need requipremd equipemnet directly required placemnets behind the pgate doors"** - **the one exception, and it is not the portal's doing.** Linked equipment - the console, the bound battery, shelves, analysers, tool cabinets - has placement requirements **of its own**, because a link has a reach. That is the equipment's constraint, not the portal projecting a zone, and the distinction matters: a player who is told "the gate needs space" would build differently from one told "this cabinet has to be within reach of that gate".

**Where this is very likely broken today, to check before building:**

- `PortalEndpointRecord` **snapshots the approach cell** - *"Endpoint cells are snapshots: moving a door cannot silently redirect a saved route"* - and `Matches(thing, approach)` demands exact equality.
- `PortalAddressService.UsableThreshold(door, approach, map)` then validates that saved cell.
- So **a wall built on a saved approach cell would break a live connection**, which is precisely the *"affecting the gate"* the owner says must not happen.
- **The likely correct shape:** keep the **anchor** cell snapshotted, because that is what stops a moved door silently redirecting a route, and **re-derive the approach cell** from the door's current surroundings at use time. Walling off your own door should stop you walking through it exactly as it does for any RimWorld door - and no more than that.
"""

anchor = u'\n**Verbatim owner direction (2026-09-29), gate placement and building around a portal:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('no-projection clarification recorded verbatim')
