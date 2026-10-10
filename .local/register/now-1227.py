# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.27-dev and record the measured remaining-work answer."""
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


sub(u'| Published | **0.12.26-dev**.', u'| Published | **0.12.27-dev**.')
sub(u'| Build | **174 C# files, 86 package files**', u'| Build | **175 C# files, 87 package files**')
sub(u'| Assembly | SHA-256 `0E265705F23D1CC907E25CF48C767B5548ED99F8EB3588FD992DD9488DD68EA5`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `977BC6016FDF88FEADA0E7DA032BD5F8074DCB2C81E5078478B269D2E5B6CF2C`, '
    u'reproduced by two clean recompiles.')
sub(u'| Proofs | **TWENTY-THREE** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-FOUR** in `.local/register/proof-*.py`.')

# ------------------------------------------------------------------ the measured answer
sub(u"""## DO THIS FIRST — the interview that resolves a disagreement""",
    u"""## THE ANSWER TO "IS IT DONE" — measured 2026-09-29, and the answer is NO

The owner asked directly: *"are all build items complete and mod 100% but bug testing?"* Measured
rather than estimated, and **the queue could not answer it** — the raw open count overstates,
because rows closed by work that shipped the same day still carried `[ ]`.

| | |
|---|---|
| Genuine build items left | **~30**, some spanning several rows |
| Rows that **cannot** close before a first launch | **~8** |
| Rows the owner excluded (Steam, site, collection) | **9** |
| Open rows already built and never closed | **~13** |

**Three things I was tempted to assume were done and checked instead — all three genuinely
unbuilt:** the solo/group tutorial line (zero solo-specific requests exist), research tier 4 (zero
tier-4 projects), and the four area types across a gate (one incidental use, no cross-gate
coverage). **Measuring first is what keeps the done column honest.**

### The ~8 that cannot be finished before the game runs once

Not evasion — it is what they are, in their own words:

- **exchange-rate and catalogue balance** — *"neither has any play behind it"*
- **duplicate def and patch collisions in the exact 294 profile** — needs the profile loaded for a
  conflict to be reproducible
- **performance measurement and profiling under a long save**
- **the user-facing compatibility report** — *"cannot honestly state a tested order before anything
  has been tested"*
- **whether the creepy-versus-normal balance lands** — *"a play question"*

So *"all build items complete, then bug test"* has a hard edge. Everything structural can be
finished first; those rows are waiting on a launch, not on more building.

### The package is staged and loadable right now

The copy in the owner's Local Mods folder was **`0.4.0-dev`, twenty-two checkpoints stale** —
nothing built since the start of the project had ever been staged. Re-staged at 0.12.26-dev, 87
files hash-verified, old copy backed up to `artifacts/staging-backups/`. **The mod list was not
touched and nothing was launched.**

---

## DO THIS FIRST — the interview that resolves a disagreement""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.26 | **The in-game text names only what exists** — fourteen strings instructed the player to use retired gear. **A tenth checker**, and an archive hole repaired so its derivation is complete |',
    u'| 0.12.26 | **The in-game text names only what exists** — fourteen strings instructed the player to use retired gear. **A tenth checker**, and an archive hole repaired so its derivation is complete |\n'
    u'| 0.12.27 | **You cannot brick your own gate** — the approach cell is reserved against blocking, flooring is free. **Owner-answered at the fork**, and the integrity checker taught to verify an abstract-parent patch |')
sub(u'## What shipped this session, 0.7.1 → 0.12.26', u'## What shipped this session, 0.7.1 → 0.12.27')

# ------------------------------------------------------------------ invariants
anchor = u"227. **Retiring a thing leaves its WORDS behind, and they need a disposition.**"
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
228. **Pick the mechanism whose SHAPE gives you the exception for free.** *"Option 2 but flooring is
     fine"* cost nothing to honour as a `PlaceWorker`, because a floor is a `TerrainDef` and terrain
     placement never consults one. The map-component version — my first instinct — would have
     needed the carve-out written by hand and then remembered.
229. **Derive a rule from Core's own predicate, never from a list of def names.** Blocking is
     `passability != Traversability.Standable`, straight out of `GenGrid.Standable`. A list would
     have been wrong for the 294 mods the moment one of them shipped a new wall.
230. **When a check runs on everything, doubt must allow.** A place worker fires on every placement
     check for every building in the game. A wrong refusal is a player who cannot build; a wrong
     allowance is a gate re-deriving a cell it already re-derives. **Catch the exception and
     accept.**
231. **A tool that cannot verify a technique is forbidding it.** `check-package-integrity.py`
     understood only `defName="X"`, so every patch on an abstract inheritance parent was refused as
     unverifiable — ruling out the one way to reach a property of every building at once. Teach the
     tool; do not route around it.""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.27-dev with the measured answer')
