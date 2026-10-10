# -*- coding: utf-8 -*-
"""Remove the stale duplicate arcs entry and renumber the queue."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'NOW.md')
s = io.open(p, encoding='utf-8').read()

stale = u'5. **Arcs 5–8** — remote sites, the outside world, industrial reach, deeper systems.\n'
assert stale in s, 'stale arcs entry not found'
s = s.replace(stale, u'', 1)

# Renumber what follows the two rewritten leaders.
renumber = [
    (u'4. **Generated requests after the hinge**', u'3. **Generated requests after the hinge**'),
    (u'6. **Still unbuilt from the prep material**', u'4. **Still unbuilt from the prep material**'),
    (u'7. **The adjacent-door-run fallback**', u'5. **The adjacent-door-run fallback**'),
    (u'8. **`RR_QuietPursuer` presentation**', u'6. **`RR_QuietPursuer` presentation**'),
    (u'9. **The player-facing how-to.**', u'7. **The player-facing how-to.**'),
    (u'10. **Public release**', u'8. **Public release**'),
    (u'11. **Continue the register retro sweep.**', u'9. **Continue the register retro sweep.**'),
    (u'12. Reconcile 0.5.0–0.7.1', u'10. Reconcile 0.5.0–0.7.1'),
]
for old, new in renumber:
    if old in s:
        s = s.replace(old, new, 1)
    else:
        print('  (not found, skipped: %s)' % old[:44])

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('queue de-duplicated and renumbered')
