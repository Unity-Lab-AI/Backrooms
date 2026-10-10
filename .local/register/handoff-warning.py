# -*- coding: utf-8 -*-
"""Replace the top warning with this session's sharper, evidenced version."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'NOW.md')
s = io.open(p, encoding='utf-8').read()

old = u"""## The warning that matters most right now

**A checker that silently passes everything is worse than no checker — it manufactures confidence.**

Proved twice more this session. A placeholder rule contained a **literal backspace byte** where a word boundary was meant, matched nothing, and looked perfect in every listing. A vocabulary sweep **renamed a keyed string** and only `check-keyed-strings.py` noticed.

- **Sanity-test every checker by breaking something and confirming it fails.** Both directions: plant the fault, **and** plant what must be ignored.
- **When a proof only confirms, suspect it.** Two designs changed this session *because* a proof disagreed — the spin-up decay rate, and revisit displacement firing 100% of the time."""

new = u"""## The warning that matters most right now

**A check that cannot fail manufactures confidence, and every instance of it this session was
mine.** Four, all found by planting faults rather than by reading:

| What could not fail | Why |
|---|---|
| the natural-depth ordering claim | keyed off a **variable name**; renaming it made the claim fail *open* |
| the on-the-books claim | counted a **refusal string** that survived the guard being deleted |
| the staffing ordering claim | had a **conditional fallback** on a method name absent from the file, so it collapsed to a tautology |
| the whole proof runner | **grepped for `PROOF HELD`**, and four live proofs end `PASS:` — so four went unrun for most of the session |

The first three were caught by fault-planting. **The fourth was caught only by writing this
handoff**, which is the argument for writing it.

### The rules that come out of that

- **Key a claim off the thing that happens** — a guard expression, an assignment, a refusal, an
  exit status. Never off a token near it, a variable's spelling, or a count of a string.
- **A claim with a conditional fallback can be trivially true.** If the anchor is missing, the
  whole expression degenerates and says nothing.
- **Plant the fault and confirm it fails for the RIGHT reason.** A claim that fails for the wrong
  reason will pass for the wrong reason too.
- **Check the plant landed.** A patch script asserts before it writes, so a mistyped anchor plants
  nothing — and the proof passing afterwards proves nothing.
- **A wrong claim is far better than an unfalsifiable one.** Three times this session a corrected
  claim was *also* wrong on its first try and failed immediately. That is the system working: the
  wrong one tells you.

**And the older lesson still holds:** when a proof only ever confirms, suspect it. Two designs
changed *because* a proof disagreed — the spin-up decay rate, and revisit displacement firing
every single time."""

assert old in s, 'warning section not found'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('the top warning replaced with the evidenced version')
