# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.28-dev and set the next task."""
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


sub(u'| Published | **0.12.27-dev**.', u'| Published | **0.12.28-dev**.')
sub(u'| Build | **175 C# files, 87 package files**', u'| Build | **176 C# files, 87 package files**')
sub(u'| Assembly | SHA-256 `977BC6016FDF88FEADA0E7DA032BD5F8074DCB2C81E5078478B269D2E5B6CF2C`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `44D6083F3ED4DF1191563A6940524F2E23BC5336E64376A299BD7F852205307C`, '
    u'reproduced by two clean recompiles.')
sub(u'| Proofs | **TWENTY-FOUR** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-FIVE** in `.local/register/proof-*.py`.')

sub(u'| Genuine build items left | **~30**, some spanning several rows |',
    u'| Genuine build items left | **~28** at 0.12.28-dev, some spanning several rows |')

# ------------------------------------------------------------------ next task
sub(u"""## DO THIS FIRST — the interview that resolves a disagreement""",
    u"""## DO THIS FIRST — research tier 4

**Measured, not assumed: zero tier-4 projects exist.** `RR_CompanyProjects.xml` holds tiers 0 to 3
across seven branches, and the row for tier 4 has been open since the ladder was first declared.

**Survey it the way tier 3 was surveyed, and do not carry the old verdict.** The 0.12.5-dev deletion
of four tier 3 projects was correct at the time and became writeable only because arc 5 wrote the
systems underneath. Invariant 136 deleted those four for being unlocks with nothing to unlock, so:

1. **Find a real observable knob per branch before authoring anything.** A project that changes no
   number a player could name is not a project. The knobs that existed at tier 3 were
   `MaximumFrontiersPerCoordinate`, `FrontierRarity`, `EmergenceShare` and `SurveyTicks` — and
   three of those are Spatial's, so one branch cannot take them all.
2. **The ~30 `Maximum*` constants in `ConnectedWork/` are scan budgets, not unlocks.** Raising one
   is a performance decision with no effect a player could name. Do not reach for them.
3. **Two restraints from 0.12.18-dev still hold:** the per-coordinate frontier cap is **not** a
   research knob, and shelter never reaches zero.
4. **`python tools/register-query.py use RR-STA`** before designing — research and staff
   development is where the *"check research tab replacements, prerequisite edits, and project
   speed changes"* instruction lives, and Backrooms milestones need stable definitions with an
   independent route when optional trees are absent.

Systems that have grown since tier 3 and may now carry a knob: the five-map cap and world exits
(0.12.21), remote site count and overhead divisor (0.12.18), request generation (0.12.12), and the
interview just built — **a Social floor is a number, and a project that lowers it is observable.**

---

## Done, 0.12.28-dev — the interview

**Nobody is lying, and that is the design.** `RecordFieldObservation` validates a fact against the
real map **before** it looks for a prior observation, so a disputing account was already checked and
found true. Two crew disagree because **the marker moved between their visits** — 0.10.3-dev's
displacement, seen from inside an evidence file. So an interview decides **which account the
corporation files**, no reliability statistic was invented, and **the account not filed stays on the
record**. Full record: [nobody is lying](implementation/INTERVIEW_IMPLEMENTATION.md).""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.27 | **You cannot brick your own gate** — the approach cell is reserved against blocking, flooring is free. **Owner-answered at the fork**, and the integrity checker taught to verify an abstract-parent patch |',
    u'| 0.12.27 | **You cannot brick your own gate** — the approach cell is reserved against blocking, flooring is free. **Owner-answered at the fork**, and the integrity checker taught to verify an abstract-parent patch |\n'
    u'| 0.12.28 | **Nobody is lying** — the interview files one account and keeps both. **The code made a lie detector impossible and the design better**: a disputing account was already validated against the map |')
sub(u'## What shipped this session, 0.7.1 → 0.12.27', u'## What shipped this session, 0.7.1 → 0.12.28')

# ------------------------------------------------------------------ invariants
anchor = u"231. **A tool that cannot verify a technique is forbidding it.**"
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
232. **Read the ORDER of the checks before designing on top of them.** I set out to build a lie
     detector; `validFact` runs *before* the prior-observation branch, so every disputing account
     had already been checked against the map and found true. **Nobody is lying** — the marker
     moved. The code did not merely constrain the design, it improved it, and only reading the
     sequence showed that.
233. **When two mechanics meet, one of them is already the explanation.** Between-visit displacement
     (0.10.3-dev) is *why* two honest crew accounts conflict. Nothing new had to be invented to
     justify the disagreement, and inventing a reliability statistic would have contradicted a
     mechanic that already shipped.
234. **Settle a dispute by recording the choice, never by rewriting the fact.** Both accounts stay,
     with both names. `Disputed` and `Settled` are two separate questions and a settled fact is
     still disputed. **An evidence chain that erases the testimony it declined is worth less than
     one that keeps both and says which.**
235. **A workflow that writes a saved decision must refuse once the record is frozen — AND be
     threaded through the snapshot anyway.** The refusal is the rule; the snapshot comparison is
     what catches the rule being wrong. Ship both, and fault-plant the second, because it has no
     symptom until much later.""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.28-dev, next task set to research tier 4')
