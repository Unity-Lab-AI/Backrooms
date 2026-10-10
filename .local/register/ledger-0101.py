import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.10.1-dev - 2026-09-29 - LAW #0, made checkable

- Internal only; nothing in the game changes.
- The owner asked whether their instructions were always being written down properly. **They were not.** Ten of them had been acted on and archived without ever being written into the working queue.
- All ten are now recorded word for word, and a check refuses from here on to let an instruction reach the archive without appearing in the queue first.

Full record: [LAW #0, made checkable](docs/implementation/VERBATIM_QUEUE_RULE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.10.1-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.10.1-dev - 2026-09-29 - LAW #0, made checkable

### Owner direction, verbatim

> *"after u fix that get back to the doc drift and it seems i could be wrong but it seems like sometimes i dont see you record the verbatiums and then build them into tasks of the todo prperly, documenting them alll, idk"*

### The owner was not wrong

The right response was to measure it rather than argue. An audit of seventeen directions from the current session found **fourteen recorded in `TODO.md` and three not** - the ask-do-not-flag rule, the no-crossing-limits rule, and the cannot-expand-a-working-gate rule. All three were implemented correctly, so no work was lost, but the queue is supposed to be the record of what was asked for and for those three it was not.

The rule written to prevent a recurrence then found **seven more** from earlier in the run, including *"we cant have backrooms npc pawns all dying off if a person is slow to explore"* and *"WE ARE NOT EDITING OTHER PEOPLES MODS!"*. **Ten directions total, now recorded verbatim.**

### The rule

A direction quoted in `FINALIZED.md` is by definition something that shipped. If it never appeared in `TODO.md`, it skipped the queue entirely, and that is now a build failure. It is not a promise to do better; it is a check that runs at every checkpoint, and it caught seven things that had not been noticed.

### Two things that would have made it useless

**Markup false positives** - the same direction is quoted in one ledger with escaped quotation marks and in another without, and comparing raw text reported those as missing. Comparison is normalised so it fires on words rather than markup.

**Continuation prompts** - *"get to it all we are finishing everything"* is genuinely the owner's words and a queue entry for it would say nothing actionable. Six are listed **explicitly** rather than matched by pattern, because an over-eager pattern would swallow a direction carrying real content alongside a "get to it" - which has happened repeatedly here, most recently with *"get to it hallways can have furniture and produiction benches too..."*, a real design direction beginning with exactly that phrase.

### Build evidence

0.10.1-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **158** C# source files, **79** approved package files. Assembly SHA-256 `B0878FAE21A2EC14A7DA9AD06E2B2280EB481F985935087EF0BD4E973EFFA094`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All six checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Owner directions found unrecorded and then recorded: **10**. Checker rules added: 1.
**An owner suspicion about process, measured rather than argued, and confirmed correct.**
False-positive classes designed out before shipping: 2 - markup differences and continuation prompts.
Still open and named in `TODO.md`: unified terminology; the remaining field-gear replacements; the last two scenarios.
"""
assert '0.10.1-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.10.0-dev** (this commit) |', u'| Published | **0.10.1-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `1C54905192F5090A7C2F4F0D81321F1504919EB7E228CB9BB892A87265FADA73`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `B0878FAE21A2EC14A7DA9AD06E2B2280EB481F985935087EF0BD4E973EFFA094`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.10.0', u'## What shipped this session, 0.7.1 → 0.10.1'),
 (u"| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims across 10 living docs |",
  u"| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims across 10 living docs |\n"
  u"| 0.10.1 | **LAW #0, made checkable** — 10 owner directions found unrecorded, and a rule so it cannot recur |"),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
69. **Every owner direction quoted in `FINALIZED.md` must already exist in `TODO.md`.** LAW #0 is now a build failure rather than an intention. It found **ten** directions that had been acted on and archived without ever reaching the queue.
70. **When the owner suspects a process failure, measure it — do not argue.** The suspicion here was correct, and the audit that confirmed it took one script."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
