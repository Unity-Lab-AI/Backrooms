# -*- coding: utf-8 -*-
"""Correct a stale queue claim: the five staff PawnKinds were wired in 0.11.7-dev."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'NOW.md')
s = io.open(p, encoding='utf-8').read()

old = (u'6. **`RR_QuietPursuer` presentation** and the five `RR_*Staff` PawnKinds — the last '
       u'existing-content\n   replacements.\n')
new = (u'6. **`RR_QuietPursuer` presentation** — the last existing-content replacement.\n'
       u'   **The five `RR_*Staff` PawnKinds are NO LONGER part of this item:** they were found '
       u'already\n   authored and read by nothing, and wired as the clean-up team\'s relief crew '
       u'in 0.11.7-dev.\n   `proof-facility-relief.py` now asserts both directions so they cannot '
       u'go dead again.\n')
assert old in s, 'stale staff claim not found'
s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('stale staff claim corrected')
