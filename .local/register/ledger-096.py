import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.6-dev - 2026-09-29 - it came through with them

- **Something can follow your crew home.** In the worst coordinates, with an advanced gate and a connection actually open, a thing that reaches the doorway behind your people steps through it into the facility.
- **Once it is inside it is an ordinary hostile**, and does everything a hostile in your base does.
- **Only one per opening.** Closing the connection and opening it again is what resets that, which makes the emergency cutoff a decision rather than a formality.
- **Only if it fits through the gate.** A narrow gate is genuinely safer, so the small one is a defensive choice and not just the one you started with.
- **Never from a quiet space, and never on an unresearched machine.** A new branch with a fresh gate is not a way in.
- Closing the connection before it reaches the doorway stops it completely.

Full record: [it came through with them](docs/implementation/GATE_INCURSION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.6-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.6-dev - 2026-09-29 - it came through with them

### Owner direction, verbatim

> *"and even at higher techs they can come through the portal into your base and attack, kidnap, steal, do everything npcs can do in game"*

Asked at the fork and answered: **depth plus technology, while an opening is live** - *"it follows your pawn to the threshold; if it reaches the threshold before you close: it comes through."*

### Bounded on five axes at once

A live opening only; `Band.Hostile` only; an advanced machine only (`PortalWindowTier >= 1`, which needs the `RR_GateTelemetry` project - checked to be completable, because this session already produced an invariant about rules that can never fire); it has to fit through the opening; and once per opening, so that closing the gate is a countermeasure that works and is learnable from a single incident.

### The inhabitant still decides nothing

Invariant #1 holds as written. `MayApproachThresholdForTraversal` still returns false for everything, so nothing on the far side is ever given a threshold as a destination. A hostile walks to the doorway **because the player's people are standing there** - vanilla assault-lord behaviour aimed at colonists, not at a door - and the gate then notices what is on its doorstep and asks the policy. `AutonomousNonPlayerTraversalPermitted` is still a constant false.

The class-level documentation was **rewritten rather than left standing**: a founding comment that no longer describes the code is worse than no comment.

### Losing a pawn to a bug is not a threat, it is a corruption

The transfer preflights completely before anything is despawned, and a spawn that somehow fails puts the pawn back where it stood. A vanished hostile is a save with a hole in it that the player would never know about, and it would look exactly like the feature working.

### What it does once through: nothing bespoke

It is an ordinary hostile pawn on a player map, so every native behaviour applies. "Attack, kidnap, steal, do everything npcs can do in game" is satisfied by writing no behaviour code at all. Note the deliberate asymmetry with 0.9.5-dev: kidnapping and stealing are off inside a coordinate, where a kidnapper leaving by a map edge is a disappearance with no story, and on in the colony, where it is an ordinary raid the player can chase.

### Build evidence

0.9.6-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **157** C# source files (one new), **79** approved package files. Assembly SHA-256 `76F6C531C095C1EB6F8508209A23C18BE43E711CD8F205EF6E604AA3B88E584B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All five checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Keyed strings added: 7. Docs updated: 5 (1 new).
**Founding invariants deliberately given a named exception: 1**, bounded on five axes, with the class documentation rewritten to say so rather than left describing code that no longer exists.
**Behaviour written for "do everything npcs can do in game": none** - it is an ordinary hostile once inside.
Still open and named in `TODO.md`: the adjacent-door-run fallback; facilities; new-game playability; the player how-to; the rest of M2.
"""
assert '0.9.6-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [ ] **"they can come through the portal into your base"**',
  '- [x] **BUILT 0.9.6-dev**, bounded on five axes: live opening, `Band.Hostile`, `PortalWindowTier >= 1`, it must fit the opening, and once per opening so closing the gate genuinely stops it. **"they can come through the portal into your base"**'),
 ('- [ ] **"attack, kidnap, steal, do everything npcs can do in game"**',
  '- [x] **BUILT 0.9.6-dev by writing no behaviour at all.** Once through it is an ordinary hostile pawn on a player map and every native behaviour applies. **"attack, kidnap, steal, do everything npcs can do in game"**'),
 ('- [ ] **This does not break the traversal chokepoint, and must not.**',
  '- [x] **HELD 0.9.6-dev.** `MayApproachThresholdForTraversal` still returns false for everything and `AutonomousNonPlayerTraversalPermitted` is still a constant false; a hostile walks to the doorway because the player\'s people are there, and `PortalTraversalPolicy.IncursionFailureKey` is the only thing that may say yes. The class documentation was rewritten rather than left describing code that no longer exists. **This does not break the traversal chokepoint, and must not.**'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.5-dev** (this commit) |', u'| Published | **0.9.6-dev** (this commit) |'),
 (u'| Build | **156 C# files, 79 package files**, zero warnings, zero errors |',
  u'| Build | **157 C# files, 79 package files**, zero warnings, zero errors |'),
 (u'| Assembly | SHA-256 `C5160083A4903117221AF361E39C4709A6EF0B5E58755971513EE67640180E10`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `76F6C531C095C1EB6F8508209A23C18BE43E711CD8F205EF6E604AA3B88E584B`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.5', u'## What shipped this session, 0.7.1 → 0.9.6'),
 (u"| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold, on vanilla AI |",
  u"| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold, on vanilla AI |\n"
  u"| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |"),
 (u'3. **Incursion.** ~~Pursuit~~ **BUILT 0.9.5-dev**',
  u'3. ~~**Incursion.**~~ **BOTH HALVES BUILT — pursuit 0.9.5-dev, incursion 0.9.6-dev.** Original entry: ~~Pursuit~~ **BUILT 0.9.5-dev**'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
53. **Incursion is the one named exception to the founding rule**, and it is bounded on five axes: a live opening, `Band.Hostile`, `PortalWindowTier >= 1`, it must fit the opening, and once per opening. Widening any of them without the owner's word rewrites the mod's premise.
54. **`MayApproachThresholdForTraversal` must stay false for everything, forever.** Incursion works *because* nothing is drawn to a gate: a hostile walks to the doorway to reach the people standing there, and the gate notices what is already on its doorstep.
55. **A transfer that can lose a pawn is a corruption, not a threat.** Preflight fully, then move, and put it back where it stood if the move fails — a vanished pawn looks exactly like the feature working.
56. **When a founding comment stops describing the code, rewrite it in the same commit.** A doc that lies at the top of the chokepoint is worse than no doc."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
