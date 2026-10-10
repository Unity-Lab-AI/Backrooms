# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

old = u'- [ ] **"informations displays in game are proper to backrrooms universe and rimworld gameplay style of all displayed informations of varying types to include all"**'
new = u'- [x] **"informations displays in game are proper to backrrooms universe and rimworld gameplay style of all displayed informations of varying types to include all"** - **BUILT 0.10.5-dev.**'
assert old in s, 'task line not found'
s = s.replace(old, new, 1)

# The closure note goes after the existing description, not over it: the description is
# permanent and only the status changes.
anchor = u'*"to include all"* is the load-bearing phrase: the audit has to enumerate the surfaces and name the ones we use **zero** of.'
assert anchor in s
closure = anchor + (
    u'\n  - Seventh checker `tools/check-display-style.py`: classifies each key by the **call '
    u'site** that displays it, holds each surface to Core\'s measured envelope, and prints a '
    u'**census of every surface including the ones at zero**.'
    u'\n  - Six strings were written in the wrong register and were rewritten; the kill-switch '
    u'row\'s instruction moved to the tooltip that exists for instructions.'
    u'\n  - The census found the **alerts readout empty**. Three alerts added - recovery overdue, '
    u'return window closing, no gate operator - with no def, no asset and no Harmony.'
    u'\n  - Register row 146 changed the design: its review warns about alert-check cost, so the '
    u'three alerts share one cached building sweep per game tick.'
    u'\n  - Record: `implementation/DISPLAY_SURFACE_IMPLEMENTATION.md`.')
s = s.replace(anchor, closure, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO item 4 closed, description preserved')
