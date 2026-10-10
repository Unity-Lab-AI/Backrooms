import io

# --- TODO first, so the direction is queued before the archive quotes it ---
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = u"""
**Verbatim owner direction (2026-09-29):** *"and remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"*

- [x] **ACTED ON IMMEDIATELY 0.10.3-dev.** `UNIVERSE_ADAPTATION.md` lists five ways an ordinary interior is made uncanny. Four were built; **"a feature that has moved since the last visit" was not**, and it is the only one that depends on the player's own memory rather than on geometry. Built as silent between-visit fixture displacement.
- [ ] **Still unbuilt from the same prep document:** *"contradictory accounts"* from a returning crew - a report that does not match what another crew saw - and staff **prior exposure** affecting how an expedition goes.
- [ ] **Still unbuilt from the progression ladder:** step 5's *"respond to openings in settlements"* - a connection appearing somewhere the branch did not make one.
- [ ] **Keep doing this.** Each checkpoint should check one prep document against what exists rather than designing from memory. The register's columns - load order, mod, system family, stance, firmness, trace IDs, card - are the integration half of the same habit.

"""
anchor = u'\n**Verbatim owner direction (2026-09-29):** *"get to it we are completeing and optimizing'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.10.3-dev - 2026-09-29 - something is not where you left it

- **Go back to a space you have been to before and something is sometimes not where you left it.** A bench, a lamp, a shelf - in the same room, a few cells away.
- **Nothing tells you.** No letter, no alert. If you never notice, you have lost nothing. If you do notice, you found it yourself.
- **Not every time.** Roughly a third of returns are exactly as you left them, so you can never be sure whether the room changed or you misremembered.
- Never anything you built, never the way out, and never anything that could block a door.
- A first visit never changes, because there is nothing yet to remember.

Full record: [something is not where you left it](docs/implementation/REVISIT_DISPLACEMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.10.3-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.10.3-dev - 2026-09-29 - something is not where you left it

### Owner direction, verbatim

> *"and remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"*

### Found by reading the prep material, not by inventing

`UNIVERSE_ADAPTATION.md` lists five ways an ordinary interior is made uncanny: a shifted doorway, impossible adjacency, a repeated hall, changed room dimensions, and **a feature that has moved since the last visit**. Checked one by one, four were built and the fifth was not - and it is the only one that depends on **the player's own memory** rather than on the geometry.

### Not the rearrangement anomaly

`RR_Anomaly_Rearrangement` moves loose items **during a session**, at depth four and above, and **announces itself**. This moves fixtures **between visits**, **silently**, at any depth a coordinate has been opened twice. Opposites on purpose: an anomaly you are told about happened *to you*; a chair that is somewhere else happened **while you were not there**.

### The proof changed the design

The first version fired on **every single return** - 100% across 4,000 simulated visits - which is mechanical rather than uncanny, because a player would simply learn that returning moves things. The unease depends on not being certain whether you misremembered, so a once-per-visit roll now leaves roughly a third of returns untouched: 66.7% change something, a first visit never does across 500 seeds, and a sparsely dressed room still fires on 267 of 400 returns. **Second time this session a proof has changed a design rather than confirmed one.**

### Nothing is told to the player

No letter, no message, no alert; only a company log entry, so the discovery is checkable after the fact rather than announced before it. This does not breach the warning-first rule, which governs **threats** - a bench in a different corner cannot hurt anybody.

Never anything the player built or owns (ownership is the whole test - generation places with no faction), never the return threshold, never a door or a room edge, so a moved fixture cannot seal a route. Only furnishings move, so the layout fingerprint is untouched and a revisited coordinate still re-plans byte-identically.

### Build evidence

0.10.3-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **159** C# source files (one new), **79** approved package files. Assembly SHA-256 `081A4DA33DD2D3CEF92D856E7B7926222B491EDDADCB73ECEB84742DABBC0D9F`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All six checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Prep-document items checked against the build: 5, of which **1 was unbuilt**.
**Designs changed by an offline proof rather than confirmed by one: 1** - the feature was too reliable to be unsettling.
Still open and named in `TODO.md`: contradictory crew accounts and staff prior exposure, both from the same prep document; the remaining field-gear replacements; the last two scenarios.
"""
assert '0.10.3-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.10.2-dev** (this commit) |', u'| Published | **0.10.3-dev** (this commit) |'),
 (u'| Build | **158 C# files, 79 package files**, zero warnings, zero errors |',
  u'| Build | **159 C# files, 79 package files**, zero warnings, zero errors |'),
 (u'| Assembly | SHA-256 `7F0ECE7490C23886E8862C1625812FEF27C2B9E31970FC55CD161E91B8157AB7`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `081A4DA33DD2D3CEF92D856E7B7926222B491EDDADCB73ECEB84742DABBC0D9F`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.10.2', u'## What shipped this session, 0.7.1 → 0.10.3'),
 (u"| 0.10.2 | **One set of words** — gate / connection / threshold, enforced over all player-facing text |",
  u"| 0.10.2 | **One set of words** — gate / connection / threshold, enforced over all player-facing text |\n"
  u"| 0.10.3 | **Something is not where you left it** — silent between-visit fixture displacement |"),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
73. **Check a prep document against the build every checkpoint.** `UNIVERSE_ADAPTATION.md` listed five uncanny changes; four were built and the fifth had been silently skipped for the whole project. Designing from memory is how that happens.
74. **A horror mechanic that fires every time is a mechanic, not horror.** Revisit displacement was proved to fire on 100% of returns and was deliberately weakened to 66.7%, because the unease depends on not being sure whether you misremembered.
75. **Ownership is the test for "did the player make this".** Generation places things with no faction; a colonist's work belongs to the player. One check, no list to maintain."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
