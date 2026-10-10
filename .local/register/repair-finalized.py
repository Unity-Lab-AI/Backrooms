# -*- coding: utf-8 -*-
"""Restore the FINALIZED section heading that ship-117 replaced instead of inserting before.

FINALIZED is append-only. The 0.11.7 ledger script used a replace() helper whose `new` text did
not re-include the anchor, so the heading

    ## Inherited pre-workflow history (2026-09-27 -> 2026-09-28, previous build agent)

was consumed and its section was left headless under the 0.11.7 entry. No entry text was lost --
only the heading and its parenthetical. Both are restored verbatim from HEAD~1.
"""
import io
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rel = 'docs/FINALIZED.md'
p = os.path.join(REPO, rel)

previous = subprocess.check_output(
    ['git', 'show', 'HEAD~1:docs/FINALIZED.md'], cwd=REPO).decode('utf-8')
heading = [line for line in previous.split('\n')
           if line.startswith('## Inherited pre-workflow history')]
assert len(heading) == 1, 'expected exactly one heading in HEAD~1'
heading = heading[0]

# The paragraph that opened that section, so the restored heading lands above its own body.
body_marker = u'Not verbatim user tasks'
s = io.open(p, encoding='utf-8').read()
assert heading not in s, 'heading already present -- nothing to repair'
assert body_marker in s, 'the section body is missing too, which is a different problem'
assert s.count(body_marker) == 1, 'body marker not unique'

s = s.replace(body_marker, heading + u'\n\n' + body_marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('restored: %s' % heading)
