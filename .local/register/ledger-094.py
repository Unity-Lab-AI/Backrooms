import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.4-dev - 2026-09-29 - what a gate's size lets through

- **Your animals can walk through a gate.** They could not before at all, which meant gate size had nothing to stop.
- **How big a creature fits depends on how wide the gate is.** A one-cell doorway passes people, dogs and deer. A two-cell doorway passes pack animals - muffalo, dromedaries, donkeys. Three cells or more passes anything, up to and including a thrumbo.
- **A gate has one width in both directions**, so an animal that walked in can always walk back out again.
- **Nothing from the other side gained anything.** A Backrooms creature still cannot cross under any circumstances; the rule that changed is about what is *yours*.
- Cross-gate **work** is still colonists only. An animal crosses because you told it to, never because a job was scheduled for it.

Full record: [what a gate's size lets through](docs/implementation/GATE_FIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.4-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.4-dev - 2026-09-29 - what a gate's size lets through

### Owner directions, verbatim

> *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit vehicals and the like and bigger creatures"*

> Asked at the fork and answered: **any player-owned animal may cross, freely.**

### The code was read before the feature was designed

Animals could not cross a gate at all: `EligibilityFailureKey` required `IsColonist`. So "bigger creatures fit through a wider gate" **had no subject** - every colonist is body size 1.0 and fits the narrowest gate there is, and a body-size rule written on top of that could never have fired. The owner was asked rather than guessed at.

### Two rules, deliberately kept apart

`TravellerFailureKey` is **unchanged** and still colonists only: it governs traversal in the course of company work, and eleven connected-work adapters ask it before planning a job across a gate. Relaxing that would have made animals eligible to be scheduled into bills. A new `OrderedCrossingFailureKey` governs crossing because the player ordered it, and admits player animals.

**The rule that matters was not weakened.** The chokepoint exists to stop the far side walking out, and the test is ownership: a Backrooms inhabitant is hostile or unfactioned and fails exactly as before. `AutonomousNonPlayerTraversalPermitted` is still constant false.

### Width belongs to the connection, not to an endpoint

A connection has one width in both directions. Measuring each end separately would have been the obvious implementation and would have been **wrong**: a generated return threshold is always a one-cell door, so a pack animal could have walked in through a wide gate and been unable to come home.

### Proved, not assumed

The ladder was proved offline against all 113 races the installed game ships: 73 fit one wide, 97 fit two, 113 fit three. Strictly widening, a person always admitted, and pack animals genuinely blocked by a 1x1 - which is what makes the wider sizes worth building. The proof asserts those properties rather than printing them, so a future threshold change that let everything through a 1x1 fails rather than passing quietly.

### Build evidence

0.9.4-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **156** C# source files, **79** approved package files. Assembly SHA-256 `8B01DE3983F9E2AA05011B50F497BFCF4F37B548A60EB74ABAF2EB82D00B16A3`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All five checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files modified: 3. Keyed strings added: 1, corrected: 2 (they claimed colonists only).
**Features that would have been unable to fire until the code was read: 1** - body size, with no non-colonist able to cross.
**Wrong-but-obvious implementations avoided by reasoning about the topology: 1** - per-endpoint width, which would have trapped animals in the Backrooms.
Still open and named in `TODO.md`: hostiles needing width; the adjacent-door-run fallback.
"""
assert '0.9.4-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = "- [ ] **What a gate's size lets through.** Body-size limits at `PortalTraversalPolicy`"
new = ("- [x] **BUILT 0.9.4-dev**, and it first required letting animals cross at all - they could not, so the rule had no subject. "
       "Owner answered: any player-owned animal may cross freely. Proved across all 113 installed races: 73 fit one wide, 97 fit two, 113 fit three. "
       "**What a gate's size lets through.** Body-size limits at `PortalTraversalPolicy`")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.3-dev** (this commit) |', u'| Published | **0.9.4-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `BF66AC9770AC85F7A6471E95BD7DFB9DC2B2F30A8603B33DBA4786C3DAB26220`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `8B01DE3983F9E2AA05011B50F497BFCF4F37B548A60EB74ABAF2EB82D00B16A3`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.3', u'## What shipped this session, 0.7.1 → 0.9.4'),
 (u"| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's own practice, fifth checker |",
  u"| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's own practice, fifth checker |\n"
  u"| 0.9.4 | **What a gate's size lets through** — animals may cross, and width decides which fit |"),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

old = u"2. **What a gate's size lets through.**"
new = u"2. ~~**What a gate's size lets through.**~~ **BUILT 0.9.4-dev.** Original entry:"
assert old in s
s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
47. **A connection has one width, in both directions.** Measuring each endpoint separately traps an animal in the Backrooms, because a generated return threshold is always a one-cell door.
48. **Company work and player orders are two different traversal rules.** `TravellerFailureKey` governs work and stays colonists only; `OrderedCrossingFailureKey` governs a player order and admits player animals. Widening the first would schedule animals into bills.
49. **Before designing a rule, check it can fire.** Body size could never have mattered while no non-colonist could cross."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
