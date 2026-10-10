# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""

**Verbatim owner direction (2026-09-29):** *"read now.md to continue the work completing the mod, and also real quick did we finish up that doc regress work and the later stuff i said about cleaning up text walls for everything making them a pleasure to read, lets make sure the docs and informations displays in game are proper to backrrooms universe and rimworld gameplay style of all displayed informations of varying types to include all."*

Four items, one per task, as the law requires.

- [ ] **"did we finish up that doc regress work"** - **partly. Answered with a measurement rather than a claim.** `check-doc-conformance.py` shipped in 0.10.0-dev and closed twenty-eight stale claims across ten living documents, and it passes. But its rule set is five rules wide: version claim, stale branch, retired def, checker count, DEFERRED-not-closed, plus LAW #0 quote reachability. It does **not** check the gate vocabulary in documents, and it does not check readability. A sweep on 2026-09-29 found **309 occurrences of the retired word across 34 living documents**, and `FEATURE_TRACEABILITY.md` still describes the mod in the vocabulary that 0.10.2-dev retired from the game. So: the checker is real and the drift it covers is closed; the drift it does not cover is open and is now written down here rather than left to be discovered again.
- [ ] **"the later stuff i said about cleaning up text walls for everything making them a pleasure to read"** - **partly.** `About.xml` was un-walled, `check-info-cards.py` gained the 420-character rule over **every** string the game displays and it passes, and `tools/make-readable-html.py` renders seven documents to standalone styled HTML. What was never done is the documents themselves: **twenty living documents carry prose lines past 400 characters**, `FINALIZED.md` has ninety-four of them. In-game text is clean; the documents a human sits down and reads are not.
- [ ] **"lets make sure the docs ... are proper to backrrooms universe and rimworld gameplay style"** - the document half of the direction above: the gate vocabulary and the readability rule leave the game and reach the living documents, enforced rather than swept once.
- [ ] **"informations displays in game are proper to backrrooms universe and rimworld gameplay style of all displayed informations of varying types to include all"** - **the surfaces, measured against RimWorld's own practice, one by one.** RimWorld does not have one voice for displayed text; it has a different convention per surface, and Core's own keyed files are organised by surface (`Alerts.xml`, `Letters.xml`, `Messages.xml`, `FloatMenu.xml`, `GameplayCommands.xml`) where ours are organised by system. *"to include all"* is the load-bearing phrase: the audit has to enumerate the surfaces and name the ones we use **zero** of.

"""

anchor = u'\n## Owner directions recorded late, second pass'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('display direction recorded verbatim in TODO.md, four tasks')
