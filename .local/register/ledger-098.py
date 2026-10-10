import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.8-dev - 2026-09-29 - one tech tree, different starting points

- **Every start uses the same company research tree.** A scenario chooses only which projects it begins with already finished, never what the tree contains.
- Adding a research project in future reaches every scenario at once, instead of needing each one updated by hand.
- No change to the Async Industries start: it still begins with gate telemetry available and unresearched.

Full record: [one tech tree, different starting points](docs/implementation/STARTING_RESEARCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.8-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.8-dev - 2026-09-29 - one tech tree, different starting points

### Owner direction, verbatim

> *"fyi all starts have same tech tree just differnt starting researches finished based on scenerio"*

### Why this piece, and why now

The recorded order puts new-game playability after M2, and the existing scenario still grants `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase` - legacy gear pending retirement. Writing two more scenarios granting the same gear would be building against content about to be removed, which is the exact thing the ordering exists to prevent. This piece touches none of it, is the scenario contract the other two starts need, and can be done in the right order.

### Taken literally, which changed the implementation

The tempting reading is to give each start a list of projects. That would have made three lists somebody has to keep in agreement, and "same tech tree" would have been a convention rather than a fact. So a start declares **only what begins finished**, and the tree is built from every `RimroomsProjectDef` the game has loaded. The tree is identical for every start **by construction**: a scenario cannot declare a different one because it never declares one at all. Adding a project later reaches every start at once, and a scenario that forgot to list it cannot exist.

### What it replaced

A single hardcoded `RR_GateTelemetry` record. A second project would have been invisible to every branch until somebody remembered to add it in three places. Today there is exactly one project def, so **this checkpoint changes no behaviour at all** - what changed is that the tree is now derived rather than asserted.

### Three details

A project that begins finished is also marked insight-committed, or the operations window would offer a "start" button on work already done. Ordinal sort before the list is built, because def load order varies with the mod list and two players starting the same scenario must get the same branch. A named project that no longer exists is reported and skipped rather than fatal - a player should not lose a new colony because a content update renamed something.

### Build evidence

0.9.8-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **158** C# source files, **79** approved package files. Assembly SHA-256 `211687673EA54860637418F89D3EFE90436387EDB9BB8284AA84A09A19295B94`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All five checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Def fields added: 1. Request fields added: 1. Methods added: 1. Hardcoded records removed: 1.
**Behaviour changed today: none.** The tree is derived rather than asserted, which is what makes the next two scenarios possible without a fourth list to keep in step.
**Scenarios deliberately NOT written this checkpoint: 2**, because they would have granted legacy gear that M2 is about to retire.
Still open and named in `TODO.md`: the field-gear replacement; the other two starts; the world tile.
"""
assert '0.9.8-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **"all starts have same tech tree just differnt starting researches finished based on scenerio"**'
new = ('- [x] **BUILT 0.9.8-dev, taken literally.** A start declares **only what begins finished**; the tree is built from every '
       '`RimroomsProjectDef` loaded, so it is identical for every start **by construction** rather than by keeping three lists in '
       'agreement. Replaced a hardcoded single `RR_GateTelemetry` record. No behaviour changed today, because there is exactly one '
       'project def. **"all starts have same tech tree just differnt starting researches finished based on scenerio"**')
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.7-dev** (this commit) |', u'| Published | **0.9.8-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `77C50D056BBC91570AFB912B283A30F2EB49FA3EC7264A70C9DC8F4005EF5F37`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `211687673EA54860637418F89D3EFE90436387EDB9BB8284AA84A09A19295B94`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.7', u'## What shipped this session, 0.7.1 → 0.9.8'),
 (u"| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs of rooms |",
  u"| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs of rooms |\n"
  u"| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared per scenario |"),
 (u'5. **New-game playability** — the world tile the branch does not hold (world object plus generated map) and **the three starting sites** (`SCENARIOS.md`).',
  u'5. **New-game playability.** The **starting-research contract is BUILT (0.9.8-dev)** — a start declares only what begins finished and the tree is derived from the def database. **Still open:** the world tile the branch does not hold (world object plus generated map) and **the other two starting sites** (`SCENARIOS.md`), which are **blocked behind the field-gear replacement** — the existing scenario grants `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase`, and writing two more against retiring content is what the ordering exists to prevent.'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
60. **A scenario declares what begins finished, never the tech tree.** The tree is every `RimroomsProjectDef` loaded, sorted ordinally. That is what makes "same tech tree" a fact rather than a convention three lists have to honour.
61. **A project that begins finished is also insight-committed**, or the UI offers a "start" button on work already done.
62. **The remaining two scenarios are blocked behind the field-gear replacement**, not behind effort. They would grant `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase` — content M2 is retiring."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
