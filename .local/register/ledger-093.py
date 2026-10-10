import io

# CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.3-dev - 2026-09-29 - everything you can look at says what it is

- **The facilities overview now explains each kind of room** - what it is for, and what goes wrong for a branch without it.
- **The procurement list now says what each thing is actually for**, not just what it costs and how long it takes to arrive.
- Sixteen descriptions written for things that previously showed you a bare name.
- Where the game itself does not describe something, neither do we. A work giver, a pawn kind, a trader and a category get a name and no more, because **that is exactly what RimWorld does** - it was counted rather than guessed.

Full record: [everything you can look at says what it is](docs/implementation/INFO_CARDS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.3-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

# FINALIZED
p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.3-dev - 2026-09-29 - everything you can look at says what it is

### Owner direction, verbatim

> *"we also need to be making sure all mod ingame decriptions and informational informations for everything is properly in the cards like the game does currently"*

### "like the game does currently" was measured, not guessed

Counting Core's own defs showed it describes 0 of 105 work givers, 0 of 109 pawn kinds, 0 of 16 trader kinds and 0 of 74 thing categories, and 80 of 80 recipes. The first draft of the checker demanded a description everywhere and reported **94 problems, 67 of them work givers** - which would have produced sixty-seven lines of text no player is ever shown. Matching the game meant writing fewer descriptions, in the right places. After calibration: 17 real problems, every one genuine.

### What shipped

A fifth checker, `check-info-cards.py`. Nine facility categories and seven procurement catalogue entries described, **and rendered** - the facilities overview now explains the chosen category and the procurement panel explains the selected item. Before this, exactly one of our own def types had its description displayed anywhere, so writing the rest without rendering them would have been text in a file.

One exemption with a stated reason: `RimroomsStartDef` is setup data and the `ScenarioDef` beside it is what a player actually reads.

### The checker caught a real bug in itself

A planted blank description was caught; a planted `TODO Structural steel...` passed clean, because the placeholder test only matched a whole string. The rule added for that **still** passed the plant, while the same regex tested correctly in isolation.

The cause was a literal backspace byte: writing a word-boundary escape through a shell collapsed one level too far, so the pattern demanded a 0x08 after the keyword and matched nothing, and it looked correct in every listing because a backspace renders as nothing. **This is exactly the failure the standing warning describes** - parts correct in isolation, assembly silently doing nothing - and the same shape as the unknown-def-field checker that was removed rather than shipped. The difference is that this one was debugged instead of abandoned. Proved afterwards in both directions.

### Build evidence

0.9.3-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **156** C# source files, **79** approved package files. Assembly SHA-256 `BF66AC9770AC85F7A6471E95BD7DFB9DC2B2F30A8603B33DBA4786C3DAB26220`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. **All five checkers pass.** **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Checkers: 4 -> 5. Descriptions written: 16. Rendering lines added: 2. Docs updated: 5 (1 new).
**Standards calibrated by counting the game's own data rather than assuming: 1** - and it cut the work from 94 items to 17.
**Bugs found inside a new checker by planting faults: 2**, the second of them invisible in every listing.
Still open and named in `TODO.md`: inspect-card text for the station and the beacon; what a gate's size lets through; hostiles needing width; the adjacent-door-run fallback.
"""
assert '0.9.3-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

# TODO
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [ ] **Every def this mod ships carries a real label and description**',
  '- [x] **BUILT 0.9.3-dev.** Calibrated against Core\'s own practice, which was counted rather than assumed: Core describes 0 of 105 work givers and 80 of 80 recipes, so demanding one everywhere would have added text no player sees. **Every def this mod ships carries a real label and description**'),
 ('- [ ] **Informational text on the cards** for everything a player can select or inspect',
  '- [~] **PART BUILT 0.9.3-dev** for our own defs, which are now described **and rendered** - the facilities overview and the procurement list. **Still open:** an audit of inspect-card text on the station and the beacon, the way the gate already has one. **Informational text on the cards** for everything a player can select or inspect'),
 ('- [ ] **Enforce it rather than trust it** — a checker that fails the build',
  '- [x] **BUILT 0.9.3-dev as `check-info-cards.py`, the fifth checker**, and proved by planting three faults - one of which exposed a real bug inside the checker itself, a literal backspace byte where a word boundary was meant. **Enforce it rather than trust it** — a checker that fails the build'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

# NOW
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.2-dev** (this commit) |', u'| Published | **0.9.3-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `0A2B527ED14475D56428DD2E63A0970853D5C70A854D4BB3516E4D9831FBE001`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `BF66AC9770AC85F7A6471E95BD7DFB9DC2B2F30A8603B33DBA4786C3DAB26220`, reproduced by two clean recompiles |'),
 (u'| Checkers | four, all passing |', u'| Checkers | **five**, all passing |'),
 (u'## What shipped this session, 0.7.1 → 0.9.2', u'## What shipped this session, 0.7.1 → 0.9.3'),
 (u"| 0.9.2 | **A gate has a size** — 1×1 to 2×3, Core's own `OrnateDoor` gives 1×2 free, cost scales with footprint |",
  u"| 0.9.2 | **A gate has a size** — 1×1 to 2×3, Core's own `OrnateDoor` gives 1×2 free, cost scales with footprint |\n"
  u"| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's own practice, fifth checker |"),
 (u'6. **All four checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `research/audit-gate0.py`.',
  u'6. **All five checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `research/audit-gate0.py`.'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
44. **"Like the game does" is measurable. Measure it.** Core describes 0 of 105 work givers and 80 of 80 recipes. Counting that cut a 94-item list to 17 and stopped 67 lines of text no player would ever see.
45. **A description nothing renders is text in a file.** Write it and show it in the same checkpoint, or do neither.
46. **Escapes written through a shell can collapse one level too far and leave an invisible byte.** A word-boundary escape became a literal backspace; the pattern matched nothing and looked perfect in every listing. Prefer a form that survives quoting, and always prove a checker by planting the fault it is meant to catch."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
