# -*- coding: utf-8 -*-
"""Bring the standing warning up to date. It still said "twice this session" from 0.12.19-dev.

The lesson is the same and has only got stronger, so the table of historical instances stays --
they are the evidence. What changes is the count and the framing: it is no longer *"a search that
finds nothing is not evidence"*, it is **"suspect your own measurement first"**, because five times
across 0.12.24 to 0.12.33 the measurement was the defect and the code was fine.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()

old = u"""## The warning that matters most right now

**A search that finds nothing is not evidence, and this session I twice took one as proof.**
Both directions of that failed, and both cost real things:"""

new = u"""## The warning that matters most right now

**SUSPECT YOUR OWN MEASUREMENT FIRST.** A search that finds nothing is not evidence, and across
0.12.24 → 0.12.33 **the measurement was the defect five separate times while the code was fine:**

| Measured wrong | The truth |
|---|---|
| a grep for the documented assembly hash returned nothing | the pattern was wrong; the line was correct |
| the queue reported **90 open** | 86 under one consistent pattern — two different greps, neither wrong about the file |
| a keyed-string parser found **33** strings | it matched the `<LanguageData>` wrapper; there are **1,499** |
| **three gate projects "grant nothing"** | they drive `PortalWindowTier` by counting completed projects **by defName**, which the def file's own comment says. I nearly shipped a three-hollow-projects finding |
| the wiring check reported **106 dangling defs**, then **3** | **zero.** Defs are consumed by name, **by type**, or by cross-reference from another def's XML, and I had only implemented the first, then the first two |

And a fault plant caught a **blind claim** of mine at 0.12.33-dev: *"the readout is wired"* checked
that a key **appeared** in the file, so replacing `listing.Label` with a no-op left the claim passing
while nothing was drawn. **A claim that searches for a string is not a claim about behaviour.**

The older instances below are kept because they are the evidence, and because two of them are the
reason `GetNamedSilentFail` is treated as dangerous here:"""

assert old in s, 'warning anchor missing'
assert s.count(old) == 1
s = s.replace(old, new, 1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('standing warning brought to 0.12.33-dev')
