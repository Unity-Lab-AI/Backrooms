# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.29-dev and set the next task."""
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


sub(u'| Published | **0.12.28-dev**.', u'| Published | **0.12.29-dev**.')
sub(u'| Assembly | SHA-256 `44D6083F3ED4DF1191563A6940524F2E23BC5336E64376A299BD7F852205307C`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `5AC7B632E73EF27710CE5EEE10311007B14579C62788353AF41C6F6619753E7A`, '
    u'reproduced by two clean recompiles.')
sub(u'| Proofs | **TWENTY-FIVE** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-SIX** in `.local/register/proof-*.py`.')
sub(u'| Genuine build items left | **~28** at 0.12.28-dev, some spanning several rows |',
    u'| Genuine build items left | **~27** at 0.12.29-dev, some spanning several rows |')

# ------------------------------------------------------------------ next task
sub(u"""## DO THIS FIRST — research tier 4""",
    u"""## DO THIS FIRST — the solo/group tutorial line

**Measured: zero solo-specific requests exist.** `RR_Requests.xml` holds 7 fixed tutorial requests
and 18 generated families, all of them the Async Industries line. The solo/group start ships (0.12.0
to 0.12.2) and **teaches nothing.**

`docs/CAMPAIGN_CHART.md` is the authority. The owner's direction for this line, verbatim:

> *"and the tutorial like quest chains should lay it all out"* — the solo/group start gets **its own
> tutorial line**, the way Async Industries has one. It has to teach, in order: that there is a way
> out and where to look, that coming out gives you a tile to build on, that the natural chain
> reaches through depth 3 and no further, and that deeper needs a gate you built.

And the standing constraint on both lines:

> *"this is all open eneded they can play how they choose"* — **the tutorial chain guides, it never
> rails.**

Four things to settle before writing a def:

1. **There is no company in a solo start**, so `RimroomsRequestDef` may not fit as-is. The Async
   line is a *corporation asking*. A solo crew has nobody to ask them. **Check what the request
   machinery actually requires** — `corporationContact` is a branch state in `RequestGeneration`,
   and a line that needs a corporation cannot be the solo line.
2. **`RR_Requests_NoTimeLimit` is the rule.** No clock, ever — the only clock is the gate.
3. **Every route must name a def that exists**, or the request can never fire and only
   `proof-request-generation.py` will say so.
4. **`python tools/register-query.py use RR-SCEN` and `use RR-MSN`** before designing.

---

## Done, 0.12.29-dev — the research ladder is complete

**Six rungs, and two that could not exist.** Surveyed rather than assumed, because 0.12.5-dev
deleted four tier 3 projects for being unlocks with nothing to unlock. **Logistics gets no tier 4**
— all four of its knobs are claimed and what remains are safety bounds no player reaches — and the
**gate line cannot have one**, because its fourth rung already stops the countdown. Both absences
are proof claims, since an absence cannot be seen by reading. Full record:
[six rungs, and two that could not exist](implementation/RESEARCH_TIER_4_IMPLEMENTATION.md).""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.28 | **Nobody is lying** — the interview files one account and keeps both. **The code made a lie detector impossible and the design better**: a disputing account was already validated against the map |',
    u'| 0.12.28 | **Nobody is lying** — the interview files one account and keeps both. **The code made a lie detector impossible and the design better**: a disputing account was already validated against the map |\n'
    u'| 0.12.29 | **Six rungs, and two that could not exist** — research tier 4. **Logistics gets none and the gate line cannot have one**, and both absences are asserted rather than assumed |')
sub(u'## What shipped this session, 0.7.1 → 0.12.28', u'## What shipped this session, 0.7.1 → 0.12.29')

# ------------------------------------------------------------------ invariants
anchor = u"235. **A workflow that writes a saved decision must refuse once the record is frozen"
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
236. **ASSERT AN ABSENCE, because an absence cannot be read.** Tier 4 has six projects and two
     branches deliberately without one. A reader sees six and cannot tell whether the other two
     were declined or forgotten. **The proof is the only thing that carries that difference
     forward** — and it also asserts *why*, so if a lower tier ever stops claiming Logistics' lead
     time, the proof fails and the decision gets revisited.
237. **Some absences are the shape of the thing, not a gap in the work.** The gate line's top rung
     is *"a connection that no longer counts down"*. There is nothing above indefinite. A fifth
     rung is impossible rather than unwritten, and writing one would have been the fifth invented
     effect this project has caught.
238. **A new system creates knobs for the tier above it.** Measurement had no fifth knob until the
     interview shipped one checkpoint earlier and gave it a Social floor to lower. **Sweep after
     building, not before** — which is exactly why the old verdict must not be carried.
239. **Four times this session my measurement was the defect, not the code.** The queue count, the
     assembly-hash grep, the keyed-string parser, and a grep that reported three hollow gate
     projects when the mechanism is a defName count. **Check before asserting a defect in working
     code** — invariant 203, and it keeps earning its place.""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.29-dev, next task set to the solo tutorial line')
