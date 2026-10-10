# -*- coding: utf-8 -*-
"""Close the four TODO rows the ship script could not match.

Three were section headings rather than checkboxes, and one used a curly apostrophe the patch
wrote as a straight one. Status changes only; every word of the descriptions is kept, per the
never-delete-TODO-info LAW.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

pairs = [
    (u"- [ ] **Plus hints, in the survivors' own voice**",
     u"- [x] **Plus hints, in the survivors' own voice** - SHIPPED 0.12.4-dev, four of them.**"
     u" ORIGINAL NOTE FOLLOWS:**"),
    (u'**1. Natural gates.** *"we with minify',
     u'**1. Natural gates. CLOSED 0.12.4-dev as a confirmation warning.** *"we with minify'),
    (u'**2. Solo/group guidance.** *"option three with hints',
     u'**2. Solo/group guidance. CLOSED 0.12.4-dev.** *"option three with hints'),
    (u'**3. `reserveChargePowerWatts`.** *"A supply requirement before opening"*',
     u'**3. `reserveChargePowerWatts`. CLOSED 0.12.4-dev, and it revived a tier 0 capability that '
     u'promised an unlock and delivered nothing.** *"A supply requirement before opening"*'),
]
for old, new in pairs:
    assert old in s, 'not found: %r' % old[:60]
    s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('four remaining rows closed, descriptions intact')
