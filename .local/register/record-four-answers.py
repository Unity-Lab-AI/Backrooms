# -*- coding: utf-8 -*-
"""Record the four owner answers verbatim, including one that relaxes an earlier direction."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner answers (2026-09-29), four open questions closed at once:**

**1. Natural gates.** *"we with minify i guess dont worry about it, can we at least do a rim style pop up warning ull lose valuable access to the backrooms and will have to find your own way back in"*

- [ ] **This deliberately RELAXES the earlier direction** *"natruals can not be destoryed or moved"*. The owner's own words are *"dont worry about it"* - so the mod does **not** fight Core over destructibility or movability, and does not absorb damage either, because that was not asked for.
- [ ] **What is asked for is a warning:** a RimWorld-style confirmation when a player designates a natural gate for deconstruction, saying plainly that they will lose valuable access to the Backrooms and will have to find their own way back in.
- [ ] **So the rule becomes informed consent rather than prohibition.** A player may close their own way in; they may not do it by accident. That is a better fit with *"this is all open eneded they can play how they choose"* than a prohibition would have been.

**2. Solo/group guidance.** *"option three with hints like i need to contact someone about this crazy shit"*

- [ ] **Option three: no tutorial line at all until contact**, and then the ordinary line begins. Nobody is helping them because nobody knows they exist.
- [ ] **Plus hints, in the survivors' own voice** - *"i need to contact someone about this crazy shit"*. Not requests, not objectives, not a quest chain: things the people down there think and say. **A hint describes; it never asks**, which is what keeps this open-ended.

**3. `reserveChargePowerWatts`.** *"A supply requirement before opening"*

- [ ] The gate **refuses to open unless its circuit can deliver this much power**. Distinct from `minimumPowerHeadroomWatts` as the stricter check: it means real generation rather than a charged battery, so a player cannot open a gate on one battery and no generator.

**4. Idle draw.** *"Keep 250 W (Recommended)"*

- [x] **SETTLED. The 250 W idle draw stays.** A designated gate is a machine that is on: it holds calibration, keeps its address book live and keeps the reserve warm. It never drains below what an emergency return costs, so it is a visible cost and never a trap. **This closes the open balance question raised in 0.11.5-dev** - no change needed, the shipped behaviour is the intended behaviour.
"""

anchor = u'\n**Verbatim owner clarification (2026-09-29), immediately after the above:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('four answers recorded verbatim')
