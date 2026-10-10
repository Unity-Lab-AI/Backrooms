# -*- coding: utf-8 -*-
"""Record the stranded-crew direction verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner direction (2026-09-29), a crew left on the far side:** *"and remmebr turning off a company gate with pawns inside doesnt lose control of those pawns they have to survive till a reconnection is made so they can escape"*

- [ ] **"turning off a company gate with pawns inside doesnt lose control of those pawns"** - closing a gate on a crew **does not take them away from the player**. They stay the player's own pawns, under the player's own control, on the coordinate map.
- [ ] **"they have to survive till a reconnection is made"** - and now they are a survival problem. Food, warmth, injury, whatever is down there with them. The player plays them.
- [ ] **"so they can escape"** - reconnection is the way out, and it is the player's to arrange from the near side. **Nothing here is timed** (`docs/CAMPAIGN_CHART.md` §1.1): a stranded crew is not on a countdown, they are simply somewhere hard.
- [ ] **What to verify before writing anything:** `Company/LostPawnRegister.cs` exists and the campaign calls `ExposeLostPawns()`. **The name is the thing to check.** If a closing gate hands its crew to the world-pawn pool, or despawns them, or marks them lost in any way that removes player control, that is a defect against this direction and the most consequential kind - it takes colonists away from somebody.
"""

anchor = u'\n**Verbatim owner clarification (2026-09-29), immediately after the above:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('stranded-crew direction recorded verbatim')
