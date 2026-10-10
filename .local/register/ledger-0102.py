import io

# --- TODO first: the LAW #0 rule requires the direction be queued before it is archived ---
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = u"""
**Verbatim owner direction (2026-09-29):** *"get to it we are completeing and optimizing everything while doing everything in the columns of the prep docs and mod register"*

- [x] **HELD as the standing working method.** The register's columns - load order, mod, system family, stance, firmness, trace IDs and card - are what integration questions are answered from, and the 294 per-mod reviews under `research/reviews/mods/` are read before designing rather than after.

"""
anchor = u'\n**Verbatim owner direction (2026-09-29):** *"after u fix that get back to the doc drift'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)

# Tick the vocabulary rows.
pairs = [
 ('- [ ] **`gate`** - the machine in your wall.',
  '- [x] **BUILT 0.10.2-dev.** **`gate`** - the machine in your wall.'),
 ('- [ ] **`connection`** - the live link a gate holds open to one coordinate.',
  '- [x] **BUILT 0.10.2-dev.** **`connection`** - the live link a gate holds open to one coordinate.'),
 ('- [ ] **`threshold`** - the doorway you arrive at on the far side.',
  '- [x] **BUILT 0.10.2-dev.** **`threshold`** - the doorway you arrive at on the far side.'),
 ('- [ ] **Enforce it over player-facing text**',
  '- [x] **BUILT 0.10.2-dev** as a vocabulary rule in `check-info-cards.py`, proved by planting each banned term and by confirming key names and the blessed words stay allowed. **Enforce it over player-facing text**'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

# --- CHANGELOG -------------------------------------------------------------
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.10.2-dev - 2026-09-29 - one set of words

- **Everything the mod shows you now uses one set of words.** The **gate** is the machine in your wall. The **connection** is the live link it holds open. The **threshold** is the doorway you arrive at on the far side.
- That means the game can finally tell you *which* part failed. "The gate is fine, the connection dropped" is a sentence it could not say before.
- The biggest offender was **"machine gate"**, the name of an object retired two versions ago and still used in twenty-five places the game spoke to you.
- Eighty-four lines of screen text, tooltips, job reports and item cards brought into line.

Full record: [one set of words](docs/implementation/VOCABULARY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.10.2-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

# --- FINALIZED -------------------------------------------------------------
p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.10.2-dev - 2026-09-29 - one set of words

### Owner directions, verbatim

> *"also ive used alot of differnt terms for the gates.. from portals, gates, doors , the machine, the gizmo, ect ect we need a unified name throught the entire mode in all the equipment information and cards of things items resources and buildings and all things that our mod touches"*

> *"get to it we are completeing and optimizing everything while doing everything in the columns of the prep docs and mod register"*

### One word would have been the wrong answer

The obvious reading is to pick a word and use it everywhere. Asked at the fork, and the answer was **three words for three genuinely different things**: the **gate** is the machine in your wall, the **connection** is the live link it holds open, the **threshold** is the doorway you arrive at on the far side. *"The gate is fine, the connection dropped"* says something true and could not be said at all while both were called a portal. Gate already won on the evidence: 171 player-facing uses against 13 for portal.

### What was actually wrong

Not "portal". The biggest source of drift was **"machine gate"** - the name of `RR_MachineGate`, a def **retired in 0.9.0-dev** - still in **25 player-facing strings**. The def was gone and its name was still what the game called itself. 84 lines across 21 files changed.

Key names were deliberately left alone: a player never reads `RR_Portals_Heading`, and renaming keys is churn with real DefInjected risk for no reader benefit.

### A real bug, caught by a checker rather than by reading

A global word replacement renamed a key - `RR_Frontier_NotADoorway` became `RR_Frontier_NotADoor` - while the C# still asked for the old name, which a player would have seen as a raw key in a refusal. `check-keyed-strings.py` caught it immediately. The new name matches the new vocabulary, so the **C# reference was updated rather than the rename reverted**, and the replacement script now asserts that no key or class name count changes.

### Enforced, not just done

`check-info-cards.py` gained a vocabulary rule over everything a player can read, with the reason attached to each banned term. Proved by planting all four terms separately and confirming failure, then planting a key name containing "portal" and the three blessed words together and confirming silence.

### Build evidence

0.10.2-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **158** C# source files, **79** approved package files. Assembly SHA-256 `7F0ECE7490C23886E8862C1625812FEF27C2B9E31970FC55CD161E91B8157AB7`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All six checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Player-facing lines corrected: 84 across 21 files. Checker rules added: 1, proved in both directions.
**The worst offender was the name of a def retired two checkpoints earlier**, still being used as the game's own word for itself in 25 places.
**Bugs caught by a checker rather than by reading the diff: 1** - an accidental key rename that would have shown a player a raw key.
Still open and named in `TODO.md`: the survey tag as a `GlowPod` with marker types; custody at a designated archive shelf; the recorder merged into the book; the last two scenarios.
"""
assert '0.10.2-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

# --- NOW -------------------------------------------------------------------
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.10.1-dev** (this commit) |', u'| Published | **0.10.2-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `B0878FAE21A2EC14A7DA9AD06E2B2280EB481F985935087EF0BD4E973EFFA094`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `7F0ECE7490C23886E8862C1625812FEF27C2B9E31970FC55CD161E91B8157AB7`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.10.1', u'## What shipped this session, 0.7.1 → 0.10.2'),
 (u"| 0.10.1 | **LAW #0, made checkable** — 10 owner directions found unrecorded, and a rule so it cannot recur |",
  u"| 0.10.1 | **LAW #0, made checkable** — 10 owner directions found unrecorded, and a rule so it cannot recur |\n"
  u"| 0.10.2 | **One set of words** — gate / connection / threshold, enforced over all player-facing text |"),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
71. **The vocabulary is enforced, not merely agreed.** `check-info-cards.py` fails the build on "portal", "machine gate", "doorway" or "gizmo" in any displayed text. **Key names are exempt** — a player never reads one, and renaming keys is churn with DefInjected risk.
72. **A retired def's name outlives the def in player-facing text.** "machine gate" was still the game's own word for itself in 25 strings, two checkpoints after `RR_MachineGate` was deleted. Retiring a def means retiring its vocabulary too."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
