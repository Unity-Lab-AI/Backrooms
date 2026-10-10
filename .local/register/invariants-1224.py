# -*- coding: utf-8 -*-
"""Append the four invariants 0.12.24-dev earned, and fix the queue count beside its command."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()

anchor = (u'215. **When a def is infrastructure, the art is the breach.** Three of the four legacy '
          u'defs were mechanics or generator-placed markers that invariant 10 permits. Rebuilding '
          u'working systems was never the fix. **Separate the def from its texture before deciding '
          u'what to retire.**')
assert anchor in s and s.count(anchor) == 1

new = anchor + u"""
216. **A decision nobody proved is a decision that does not ship.** The recorder became the book at
     **0.12.24-dev**; the answer was written down at **0.9.9-dev** and sat for fourteen checkpoints
     with every checker and every proof green. **No proof mentioned `RR_FieldRecorder` at all.** A
     recorded decision with no assertion behind it is indistinguishable from an idea.
217. **Retire a def by removing every way to GET one, not by deleting it.** Recipe, scenario grant,
     trade and catalogue — four routes, all closable — while the def stays loadable so saves open.
     The owner's rule is a *"migration decision or declared development-save break before removing
     any Def a saved Thing references"*, and **never granting one again satisfies it without needing
     either.** Saved field names stay too: renaming one is a save break for a cosmetic gain.
219. **When a replacement is Core content, read what Core DOES with it.** `TextBook` has
     `Flammability 1` and sells only as random outlander stock, so swapping our recorder for it
     would have made a burnt book refuse every future dispatch for ever. **That defect was in none
     of the row, the plan or the owner's answer** — only in the Core def.
220. **A LAW that points at a document its own tool cannot open is a LAW that gets skipped.** The
     register's `card` column printed the words *"open card"* — a hyperlink label — while Planned
     Use, Integration Approach and Compatibility Watch sat in the `#cards` section and 294 review
     records on disk. **Four short columns got read instead, and it counted as consulted.** Reach the
     guidance from the tool or the rule is decorative."""

s = s.replace(anchor, new, 1)

# The queue count was measured two ways at one commit. The command goes beside the number.
old_count = (u'**And the queue was re-measured against the code**: 155 rows, **114 built or '
             u'superseded**, open rows\n**254 \u2192 90**. It could not answer *"how close are we"* '
             u'before that, because nobody had checked.')
new_count = (u'**And the queue was re-measured against the code**: 155 rows, **114 built or '
             u'superseded**, open rows\n**254 \u2192 86**. It could not answer *"how close are we"* '
             u'before that, because nobody had checked.\n\n**The count itself was measured two ways '
             u'and reported as 90.** Under one consistent pattern it is **86 open, 50 partial, 446 '
             u'done** at 0.12.24-dev. Neither reading was wrong about the file; they were different '
             u'greps. So the command lives beside the number now:\n\n```\ngrep -c \'^\\s*- \\[ \\]\' '
             u'docs/TODO.md     # open\ngrep -c \'^\\s*- \\[~\\]\' docs/TODO.md    # partial\n'
             u'grep -c \'^\\s*- \\[x\\]\' docs/TODO.md    # done\n```')
assert old_count in s, 'queue-count anchor missing'
s = s.replace(old_count, new_count, 1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md: four invariants appended, queue count pinned to its command')
