# -*- coding: utf-8 -*-
"""Record the open-ended constraint verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'TODO.md')
s = io.open(p, encoding='utf-8').read()

block = u"""
**Verbatim owner direction (2026-09-29), constraining all of the above:** *"but remmebr this is all open eneded they can play how they choose"*

- [ ] **"this is all open eneded they can play how they choose"** - **the tutorial chain guides, it never rails.** This is the same rule `docs/CAMPAIGN_CHART.md` already holds the Async line to and it now governs the solo/group line too:
  - The exit is **guaranteed to exist**, and **using it is a choice**. A player who wants to live down there, dig, farm and never come out is playing the game correctly.
  - The depth-3 limit is a property of **natural portals**, not a gate on the player. It does not stop anybody doing anything; it only means the free doorways run out and a built gate is how you go further **if you want to go further**.
  - Nothing in the chain expires, nothing is failed by ignoring it, and every step offers more than one way through (chart #1.1 and #1.2, both already enforced by `check-campaign-absolutes.py`).
  - **The chain is a set of offers describing what is possible, not an order of operations.** If a player reaches the surface before anybody suggested it, the chain has to read as already-done rather than skipped.
"""

anchor = u'\n**Verbatim owner answers (2026-09-29), at the exit fork:**'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('open-ended constraint recorded verbatim')
