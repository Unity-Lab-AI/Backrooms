# -*- coding: utf-8 -*-
"""Record the natural-exit direction verbatim, and the thing it corrects."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner direction (2026-09-29), correcting 0.12.0-dev:** *"and remember the solo/group start in a backroom needs to 100% have a exit to map natural portal on their first backrroms level with natural portals deeper to an extent till they would need to buidl theri own gate"*

- [ ] **"needs to 100% have a exit to map natural portal on their first backrroms level"** - **THIS CORRECTS WHAT 0.12.0-dev SHIPPED.** That checkpoint's record says, in as many words, *"No gate anchor and no return cell... There is no way home and finding one is the whole opening."* That is wrong. The first level must have a **guaranteed** natural portal that exits to a map - not a discovered one, not a rarity draw. `NaturalFrontierService` finds frontiers at roughly one doorway in twelve, capped at two per coordinate, and a way out additionally requires a marked way home that a solo start does not have. **None of that can deliver 100%.**
- [ ] **"with natural portals deeper to an extent"** - natural portals also lead **inward** from the first level, and keep doing so for a bounded number of depths.
- [ ] **"till they would need to buidl theri own gate"** - past that extent the natural chain stops, and going deeper requires a gate the player built. That is the convergence into company play for this start: the Backrooms hands you a few levels for free and then asks you to become an engineer.

**What this means concretely, before any of it is built:**

- A natural gate is **permanently open**, has no timer, operator, power, close command or address book, and may not dial (invariant 12). So the exit is not a mechanism the player operates; it is a door that is simply a way out.
- The exit must be created **at generation**, by `GenStep_InsideStart`, not discovered by survey work. A survey draw is a probability and the direction says **100%**.
- The existing way-out path registers against a `CompRimroomsEmergence` anchor, which is **a door the player marked on their own map**. A solo/group start has no colony and no marked door, so that path cannot be the one used. The exit needs a destination that exists at new-game.
- The depth extent needs a number and it is **not yet chosen**. It is the difference between "a few levels of free exploration" and "the whole game without ever building anything".
"""

anchor = u'\n**Verbatim owner answers (2026-09-29), at the starts fork:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('exit direction recorded verbatim')
