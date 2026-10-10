# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.30-dev and set the next task."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:90]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:90]
    s = s.replace(old, new, 1)


sub(u'| Published | **0.12.29-dev**.', u'| Published | **0.12.30-dev**.')
sub(u'| Build | **176 C# files, 87 package files**', u'| Build | **178 C# files, 87 package files**')
sub(u'| Assembly | SHA-256 `5AC7B632E73EF27710CE5EEE10311007B14579C62788353AF41C6F6619753E7A`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `90E0885C229B6972E5209E3C30B4487F9BB3431AB5B5490A75B6B36188AA1923`, '
    u'reproduced by two clean recompiles.')
sub(u'| Proofs | **TWENTY-SIX** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-SEVEN** in `.local/register/proof-*.py`.')
sub(u'| Genuine build items left | **~27** at 0.12.29-dev, some spanning several rows |',
    u'| Genuine build items left | **~26** at 0.12.30-dev, some spanning several rows |')

# ------------------------------------------------------------------ next task
sub(u"""## DO THIS FIRST — the solo/group tutorial line""",
    u"""## DO THIS FIRST — the adjacent-door-run fallback

Three rows point at one feature (568, 610, 959) and the owner answered it long ago, verbatim:

> *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit
> vehicals and the like"*

**The answer on record is BOTH paths** — Doors Expanded when present, and a run of adjacent Core
1×1 doors when not. The single-door half shipped at 0.9.2-dev, where Core's own `OrnateDoor` gives
2×1 free. **1×3 and 2×3 are what remain.**

What to establish first:

1. **Invariant 47: a connection has one width, in both directions.** Per-endpoint measuring traps
   an animal in the Backrooms. A bound run must present *one* width to both sides.
2. **Invariant 40: width and footprint are different numbers.** Width decides what fits; footprint
   decides what it costs. A run of three 1×1 doors is footprint 3 and width 3, which is the easy
   case — **2×3 is the one to think about.**
3. **Invariant 41: throughput is never capped.** A wide gate gets more doorway cells, never a
   quota. There is no counter, deliberately.
4. **Invariant 12 and 32:** there is exactly one way a laboratory gate opens, through the spin-up,
   and every entry point routes into it. A bound run is **one gate**, not three.
5. **`python tools/register-query.py use RR-GATE`** — the construction family has real instructions
   about reachability and native build costs, and 0.12.27-dev already found two that applied.

The framing correction on record, which must not be undone: the option was once written as
*"Core-only must reach every width"*, which treats a vanilla install as the audience. **It is not.**
Zero hard dependencies is a *build* property; the 294-mod register is the *play* property.

---

## Done, 0.12.30-dev — two of three starts had no campaign

**The largest reachability hole found in this project so far**, and it turned up while following the
solo-tutorial row. `EstablishCorporationContact()` had **no caller anywhere**, and
`corporationContact` gates the tutorial line, generated requests, the Purchase route and the
clean-up team's rescue — so the Store and Solo/Group starts had **no campaign at all, permanently.**

The owner named the mechanism mid-build and it deleted most of the planned work: a call on a comms
console, starting **the existing Async line**. No solo line was needed. Full record:
[two of three starts had no campaign](implementation/CORPORATE_CONTACT_IMPLEMENTATION.md).""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.29 | **Six rungs, and two that could not exist** — research tier 4. **Logistics gets none and the gate line cannot have one**, and both absences are asserted rather than assumed |',
    u'| 0.12.29 | **Six rungs, and two that could not exist** — research tier 4. **Logistics gets none and the gate line cannot have one**, and both absences are asserted rather than assumed |\n'
    u'| 0.12.30 | **You can call the company** — `EstablishCorporationContact` had no caller, so **two of three starts had no campaign at all**. Earned on a comms console, and it opens the line that already existed |')
sub(u'## What shipped this session, 0.7.1 → 0.12.29', u'## What shipped this session, 0.7.1 → 0.12.30')

# ------------------------------------------------------------------ invariants
anchor = u"239. **Four times this session my measurement was the defect, not the code.**"
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
240. **A public method with no caller is a feature that does not exist.** `EstablishCorporationContact`
     was one-way, recorded its event, had its keyed string written — and was unreachable, which left
     **two of three starts with no campaign at all**. Grep for callers, not for definitions. The
     nine checkers and twenty-six proofs were all green over it.
241. **When two documents agree about something nobody built, they are not wrong — they are a
     specification.** The chart and `RR_Starts.xml` both said *"reaching contact is the
     achievement"*. Neither was stale. **The achievement had no mechanism**, and a hint was already
     pointing the player at a console with nothing to do with it.
242. **Follow the row into the code before scoping the work.** The row said *"the solo start has no
     tutorial line"*. The defect was that two starts had no campaign. **The row was accurate and
     far too small**, which is a different failure from a stale row and harder to see.
243. **An owner answer can delete work, not just direct it.** *"they can start async quest line"*
     meant no parallel line, no discriminator on the def, no second selector — the existing gate on
     `corporationContact` was already the whole mechanism. **Ask before building the bigger
     version.**""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.30-dev, next task set to the door-run fallback')
