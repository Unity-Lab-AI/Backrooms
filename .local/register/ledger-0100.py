import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.10.0-dev - 2026-09-29 - the documents say what is true

- **The readme said this was version 0.4.1-dev.** It is 0.10.0-dev. That and twenty-seven other stale claims across ten documents are corrected.
- The publishing procedure named a branch that has not been the working branch for the whole of this development run.
- Documents no longer describe retired objects as things you can build, or point at a deferral list that was closed.
- A sixth check now refuses to ship documentation that describes a mod this is not. **Dated records are deliberately exempt**: an old build record saying "all four checkers pass" was true when it was written, and rewriting history would be worse than leaving it.

Full record: [the documents say what is true](docs/implementation/DOC_CONFORMANCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.10.0-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.10.0-dev - 2026-09-29 - the documents say what is true

### Owner direction, verbatim

> *"we need to keep using the mod register and all the prep docs while updating old out of date docs, readmes, how tos and other docs making sure they conform to the wanted stake state"*

### What was wrong

`README.md` opened with **"Current development version: 0.4.1-dev"** against a build at 0.9.9-dev - twenty-five checkpoints stale, on the front page. `PUBLISHING.md`, the procedure followed at every checkpoint, named `feature/preproduction-handoff` as the working branch when the real one has been `feature/connected-colony-portals` throughout; that one is not cosmetic, because it is the document an agent follows to push. **28 genuine problems across 10 living documents.**

### Living documents and dated records are different things

A living document must describe the mod as it is now. A dated record describes a moment that has passed, and one saying *"all four checkers pass"* **was telling the truth on the day it was written** - rewriting it would falsify the evidence trail this project's method rests on. Dated records are never checked; 48 living documents are checked strictly.

### Precision mattered more than coverage

The first branch rule matched any `feature/...` string and produced 26 false positives: file paths, prose. The `DEFERRED.md` rule flagged `NOW.md` for the sentence that **forbids** deferring. **A checker that cries wolf is one people learn to scroll past**, which is worse than not having it. Branch names now come from an explicit list; a retired def may be named freely while explaining that it is retired; `DEFERRED.md` fails only if a document never says anywhere that it is closed. 54 raw hits became 28 real ones.

### Proved in both directions

Each fault planted separately, so a rule that does nothing cannot hide behind one that works: stale version CAUGHT, retired branch CAUGHT, retired def CAUGHT, wrong checker count CAUGHT. Then all four planted **in a dated record** and correctly not flagged - because an exemption that leaked would quietly disable the whole check.

### It caught itself

Adding this checker made six, and its own count said five, so it failed `NOW.md` on the checkpoint ritual. Its message also hardcoded the word "four" instead of quoting what it found, which it now does.

### Build evidence

0.10.0-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **158** C# source files, **79** approved package files. Assembly SHA-256 `1C54905192F5090A7C2F4F0D81321F1504919EB7E228CB9BB892A87265FADA73`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. **All six checkers pass.** **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Checkers: 5 -> 6. Living documents corrected: 10. Stale claims fixed: 28.
**False positives designed out before shipping: 26** - the first rule would have made the check noise.
**Rules proved by planting their own fault: 4, plus the exemption proved by planting four faults it must ignore.**
Still open and named in `TODO.md`: unified terminology (gate / connection / threshold, decided this checkpoint); the remaining field-gear replacements; the last two scenarios.
"""
assert '0.10.0-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

# TODO: the new direction, verbatim, and the decision.
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = u"""
**Verbatim owner direction (2026-09-29):** *"we need to keep using the mod register and all the prep docs while updating old out of date docs, readmes, how tos and other docs making sure they conform to the wanted stake state"*

- [x] **BUILT 0.10.0-dev as `check-doc-conformance.py`, the sixth checker.** 28 stale claims across 10 living documents corrected, including a readme claiming version 0.4.1-dev against a 0.9.9-dev build and a publishing procedure naming a branch that has not been the working branch all run. **Dated records are exempt by design** - an implementation record saying "all four checkers pass" was true when written, and rewriting it would falsify the evidence trail.

**Verbatim owner direction (2026-09-29):** *"also ive used alot of differnt terms for the gates.. from portals, gates, doors , the machine, the gizmo, ect ect we need a unified name throught the entire mode in all the equipment information and cards of things items resources and buildings and all things that our mod touches"*

**Owner answer, asked at the fork:** **gate / connection / threshold** - three words for three genuinely different things, rather than one word that would lose the distinction.

- [ ] **`gate`** - the machine in your wall. Always a designated door. Already dominant at 171 player-facing uses against 13 for "portal".
- [ ] **`connection`** - the live link a gate holds open to one coordinate. Lets the game say *"the gate is fine, the connection dropped"*, which is a real thing that happens and currently cannot be said clearly.
- [ ] **`threshold`** - the doorway you arrive at on the far side.
- [ ] **Enforce it over player-facing text** - keyed strings and def labels and descriptions - so the vocabulary cannot drift back. Same reasoning as every other checker here.

"""
anchor = u'\n**Verbatim owner direction (2026-09-29), on the glow pods:**'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.9-dev** (this commit) |', u'| Published | **0.10.0-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `0E9BEEF6DA1A781EB58E8974340522DF4010EA00004F38F292880677F6FD7F600`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `1C54905192F5090A7C2F4F0D81321F1504919EB7E228CB9BB892A87265FADA73`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.9', u'## What shipped this session, 0.7.1 → 0.10.0'),
 (u"| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement, four replacements decided |",
  u"| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement, four replacements decided |\n"
  u"| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims across 10 living docs |"),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
66. **Living documents and dated records are different things.** A readme must describe the mod now; an implementation record describes a moment that has passed and **must never be rewritten** — one saying "all four checkers pass" was true when written. `check-doc-conformance.py` exempts dated records by path, and that exemption is proved by planting faults it must ignore.
67. **A checker that cries wolf is worse than no checker.** The first branch rule produced 26 false positives on file paths and prose. Precision before coverage, every time.
68. **The unified vocabulary is gate / connection / threshold.** The **gate** is the machine in your wall; the **connection** is the live link it holds open; the **threshold** is the doorway on the far side. Never "portal", "the machine" or "the gizmo" in player-facing text."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
