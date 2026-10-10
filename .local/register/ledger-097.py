import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.7-dev - 2026-09-29 - some places are bigger than a room

- **Runs of two to four connected rooms are now furnished as one thing.** You find a laboratory wing rather than a room with a bench in it, a dormitory block rather than a stray bed.
- **Deeper in they are still wrong in all the usual ways**, which is worse than a jumble rather than tidier: there is finally something recognisable for the wrongness to happen to.
- Quiet rooms are never part of one, so a coordinate still has its empty stretches. The room you arrive in is never part of one either.
- The shallow yellow rooms are untouched and stay sparse.

Full record: [some places are bigger than a room](docs/implementation/FACILITIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.7-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.7-dev - 2026-09-29 - some places are bigger than a room

### Owner directions, verbatim

> *"facilitys"*

> *"lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries"*

### What was wrong with what was there

Every room rolled its own kind independently, so a coordinate could put a laboratory bench in one room, a bed in the next and a smithy in the third. Each room was fine and **the place was nothing** - there was no laboratory, only a room with a bench in it.

### What shipped

A facility is a contiguous run of two to four rooms taken off the coordinate's own saved graph and dressed as the same kind. No new def type and no new content: the same fourteen archetypes, chosen once for a group instead of once per room. Resolution is through an anchor - the lowest room index - so every member asks the same question and gets the same answer, and **nothing is stored**: the assignment is recomputed identically from the saved graph and seed rather than written down, so it cannot fall out of step with the graph.

### Coherence makes a deep coordinate worse, not tidier

**A recognisable institution that is wrong is far worse than a jumble**, because a jumble has nothing to violate. The 0.8.7-dev derangement still applies on top, so a three-room nursery turns up where no nursery could be, furnished at a tech level nobody there should have had.

### Proved, because this is exactly how a generator ships a no-op

Half of every coordinate is a required quiet room and one more is the threshold, so the pool is small before any roll happens. It is entirely possible to write this, have every constraint be individually reasonable, and never once form a group - which would look precisely like a working feature. 2,800 simulated coordinates across seven sizes assert that facilities form (53.9% of coordinates, so a plain one still exists), that every group is contiguous through the graph, bounded 2-4, anchored at its lowest index, never consumes a quiet or threshold room, leaves the quiet guarantee intact, and replans identically from the same seed.

`EligibleShare` was compared at 0.45, 0.50, 0.60 and 0.70. **The code kept 0.45 and the proof was changed to match it** - a proof testing different numbers than the code is worthless.

### Build evidence

0.9.7-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **158** C# source files (one new), **79** approved package files. Assembly SHA-256 `77C50D056BBC91570AFB912B283A30F2EB49FA3EC7264A70C9DC8F4005EF5F37`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All five checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Package files created: 0. Docs updated: 5 (1 new).
**Structural properties asserted offline rather than assumed: 6**, across 2,800 simulated coordinates.
**Tuning constants changed to match the proof: 0. Proofs changed to match the code: 1.**
Still open and named in `TODO.md`: new-game playability; the player-facing how-to; the rest of M2; the adjacent-door-run fallback.
"""
assert '0.9.7-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
for old in ['- [ ] **Facilities** — larger functional spaces, as distinct from rooms and corridors.',
            '- [ ] **"facilitys"** — larger functional spaces, as distinct from rooms and corridors.']:
    if old in s:
        new = old.replace('- [ ]', '- [x] **BUILT 0.9.7-dev** as a contiguous run of 2-4 rooms dressed as one kind, off the coordinate\'s own graph, with nothing stored and the quiet guarantee untouched by construction.', 1)
        s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.6-dev** (this commit) |', u'| Published | **0.9.7-dev** (this commit) |'),
 (u'| Build | **157 C# files, 79 package files**, zero warnings, zero errors |',
  u'| Build | **158 C# files, 79 package files**, zero warnings, zero errors |'),
 (u'| Assembly | SHA-256 `76F6C531C095C1EB6F8508209A23C18BE43E711CD8F205EF6E604AA3B88E584B`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `77C50D056BBC91570AFB912B283A30F2EB49FA3EC7264A70C9DC8F4005EF5F37`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.6', u'## What shipped this session, 0.7.1 → 0.9.7'),
 (u"| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |",
  u"| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |\n"
  u"| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs of rooms |"),
 (u'4. **Facilities** — larger functional spaces, distinct from rooms and corridors. Generation must be finished before the scenarios that consume it.',
  u'4. ~~**Facilities**~~ **BUILT 0.9.7-dev** as contiguous runs of 2-4 rooms sharing one archetype, proved across 2,800 simulated coordinates.'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
57. **A facility is a contiguous run of 2–4 rooms sharing one archetype**, resolved through the lowest-index anchor and **stored nowhere** — recomputed identically from the saved graph and seed. Never a quiet room, never the threshold, never depth 1.
58. **Coherence is what wrongness needs.** A recognisable institution that is wrong beats a jumble, because a jumble has nothing to violate. Do not "fix" facilities by making deep coordinates tidier.
59. **When a proof and the code disagree on a constant, change the proof.** A proof testing different numbers than what ships is worthless. `EligibleShare` stayed 0.45; the proof moved to match."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
