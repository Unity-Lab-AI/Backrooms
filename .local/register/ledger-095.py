import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.5-dev - 2026-09-29 - they follow you

- **In the worst coordinates, what lives there no longer holds its ground.** It follows your crew, room after room, all the way to the doorway you came in by.
- **Everywhere quieter it still gives you a warning and lets you back away.** That has not changed, and it is what makes the deep ones mean something.
- Nothing kidnaps anyone or carries anything off the map. What follows you follows you; it does not disappear with one of your people.
- The limits that keep a lone survivor alive are untouched: never more than three things acting at once, quiet rooms still guaranteed, and nothing ever waiting in the room you arrive in.

Full record: [they follow you](docs/implementation/PURSUIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.5-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.5-dev - 2026-09-29 - they follow you

### Owner direction, verbatim

> *"and at deeper levels i do want monstrosities and npcs to \\"Chase\\" pawns/ kill them all the way to the gate"*

### What was already there and did the opposite, on purpose

A hostile inhabitant was given a `LordJob_DefendPoint`, with a comment saying why: *"the warning-first rule requires that a player who backs off is not pursued across the whole space."* That was a deliberate decision and at shallow depth it is still right. The direction is not that it was wrong, but that it should stop being true as you go deeper.

### The threshold already existed

`Band.Hostile` is defined in the pressure ladder as *"more than one thing acts, and the space stops being forgiving"* - the owner's "deeper levels" already written down, derived from depth, operating history, technology and colony wealth together. A second threshold beside it would have given one idea two definitions that could drift. Below `Hostile`, unchanged; at `Hostile`, it hunts.

### No pursuit code was written

RimWorld's own assault lord already walks a hostile toward whoever it can reach. "All the way to the gate" needed nothing added, because the threshold room is excluded from *spawning*, never from being walked into. **Fifth time this session a requirement was met by an existing guarantee rather than new code.**

Kidnapping, stealing, fleeing and timing out are all off: every generated coordinate has map edges, and a kidnapper carrying somebody off one would be a disappearance with no story attached to it.

### A bug caught by reading the diff

`LordJob_AssaultColony`'s first parameter is the **assaulter's** faction. The first version passed `Faction.OfPlayer`, naming the player as the attacker. It compiled, and no checker would have caught it - the type is right and the value is a real faction. It was found by re-reading the change against the decompiled constructor.

### Build evidence

0.9.5-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **156** C# source files, **79** approved package files. Assembly SHA-256 `C5160083A4903117221AF361E39C4709A6EF0B5E58755971513EE67640180E10`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All five checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Methods added: 1. Call sites changed: 1. Docs updated: 5 (1 new).
**Bugs caught by re-reading a diff against decompiled Core rather than by any checker: 1.**
**Requirements met by existing vanilla behaviour rather than new code: 1** - pursuit to the threshold.
Still open and named in `TODO.md`: coming through the gate into the colony, which inverts the mod's founding rule and needs its own diff; the legacy `RR_QuietPursuer` scripted chase, untouched here because it is a separate older system on a custom def.
"""
assert '0.9.5-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **"Chase" pawns/ kill them all the way to the gate"**'
new = ('- [x] **BUILT 0.9.5-dev, and it needed no pursuit code.** At `Band.Hostile` a hostile gets an assault lord instead of a '
       'defend lord, and vanilla AI walks it to whoever it can reach; the threshold room was only ever excluded from *spawning*, '
       'never from being walked into. Below that band the warning-first retreat rule is untouched. '
       '**"Chase" pawns/ kill them all the way to the gate"**')
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.4-dev** (this commit) |', u'| Published | **0.9.5-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `8B01DE3983F9E2AA05011B50F497BFCF4F37B548A60EB74ABAF2EB82D00B16A3`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `C5160083A4903117221AF361E39C4709A6EF0B5E58755971513EE67640180E10`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.4', u'## What shipped this session, 0.7.1 → 0.9.5'),
 (u"| 0.9.4 | **What a gate's size lets through** — animals may cross, and width decides which fit |",
  u"| 0.9.4 | **What a gate's size lets through** — animals may cross, and width decides which fit |\n"
  u"| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold, on vanilla AI |"),
 (u'3. **Pursuit and incursion.** Grouped here so **all the gate work happens once**.',
  u'3. **Incursion.** ~~Pursuit~~ **BUILT 0.9.5-dev** with no pursuit code: at `Band.Hostile` a hostile gets an assault lord and vanilla AI walks it to the threshold. **Still open: coming *through*.** Original entry:'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
50. **`Band.Hostile` is the "deeper levels" threshold.** Its own definition is *"the space stops being forgiving"*. Anything gated on depth-plus-history should use it rather than inventing a second number that can drift from it.
51. **A hostile below `Band.Hostile` holds ground; at it, it hunts.** The warning-first retreat rule is what makes a shallow coordinate survivable for one person, and it must stay true there.
52. **`LordJob_AssaultColony`'s first parameter is the ASSAULTER's faction.** Passing the player's names the player as the attacker, compiles cleanly, and no checker can catch it."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
