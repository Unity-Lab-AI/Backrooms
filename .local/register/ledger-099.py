import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.9-dev - 2026-09-29 - the beacon had nothing left to do

- **The return beacon is gone.** Your gate remembers every address it has dialled and the way back is saved with the space itself, so carrying a beacon to find your own door stopped being a job some time ago.
- Nothing was lost with it. Finding your way home is done by the gate's own address book and the saved return threshold, both of which are better at it than an item you could drop.
- Survey tags are untouched and still mark your route.

Full record: [the field kit, part one](docs/implementation/FIELD_KIT_RETIREMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.9-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.9-dev - 2026-09-29 - the beacon had nothing left to do

### Owner decisions, asked at the fork and answered

Four pieces of field gear needed capability replacements before the remaining scenarios could be written, and the owner has always refused to lose the mechanics. Core was enumerated first so the options were real, and all four were answered:

> **Survey tag -> Core `GlowPod`**, minifiable, carried, deployed, and it lights the room it marks.

> **Return beacon -> dropped.** The gate's address book and the saved return threshold already are the route authority.

> **Sealed evidence case -> a designated headquarters shelf is the archive**, with the book carried and custody completing when it arrives.

> **Field recorder -> the book is the recorder.** One Core `TextBook` carried in blank, written in the field, carried home as the evidence.

Further owner direction on the glow pods, recorded verbatim in `TODO.md`: *"lets not limit the amount as a backrooms instance can have 100s of rooms"*, *"maybe lets have the glow pods color setable"*, and *"color means differnt types of the needs markers"* - answered as **mod-defined marker types, each with its own colour**.

### What shipped here

Only the beacon, because it is the one that needed no replacement built: its job was genuinely taken over by work already shipped. The def, its recipe, its scenario grant, its keyed strings, its deploy button and all six C# references are gone.

`CompGlower.GlowColor` was verified to have a public setter backed by a **saved per-instance `glowColorOverride`**, and `CompProperties_Glower.colorPickerEnabled` turns on RimWorld's own colour picker - so settable colour needs no new UI. That is for the next checkpoint.

### The checker found the last trace

`RR_ReturnAnchor` used the beacon's texture, so the package still referenced a name it no longer declared. The texture is renamed to the def that actually uses it, leaving nothing pointing at a dead name. **Found by `check-package-integrity.py`, not by reading.**

### Build evidence

0.9.9-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **158** C# source files, **79** approved package files. Assembly SHA-256 `0E9BEEF6DA1A781EB58E8974340522DF4010EA00004F38F292880677F6FD7F600`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All five checkers pass. **Nothing was added.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Defs retired: 2 (the beacon and its recipe). C# references removed: 6. Keyed strings removed: 2. Textures renamed: 1.
**Owner forks asked and answered rather than guessed: 5** in one exchange, each grounded in enumerated Core content rather than in what seemed likely.
**Field gear retired because its job was taken over rather than replaced: 1.**
Still open and named in `TODO.md`: the survey tag as a glow pod with marker types; the evidence case as a designated archive; the recorder merged into the book; then the remaining two scenarios.
"""
assert '0.9.9-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

# TODO: record the decisions verbatim and tick the beacon.
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = u"""
**Verbatim owner direction (2026-09-29), on the glow pods:** *"tyhe glow pods can be used and lets not limit the amount as a backrooms instance can have 100s of rooms if the player is using 300x300 maps for instance and maybe lets have the glow pods color setable"* and *"color means differnt types of the needs markers"*

**Owner answers on the field kit, asked at the fork:**

- **Survey tag → Core `GlowPod`.** Minifiable, carried, deployed, and it lights the room it marks. *"place one per room you clear, room is lit AND numbered."*
- **Return beacon → dropped.** *"the gate IS the beacon"* — the address book and the saved return threshold already do its job. **DONE 0.9.9-dev.**
- **Sealed evidence case → a designated headquarters shelf is the archive.** The book is carried and custody completes when it reaches a Core `Shelf` designated as the evidence archive, the same designation pattern as the gate console and the laboratory bench.
- **Field recorder → the book is the recorder.** One Core `TextBook`: carried in blank, written in the field, carried home as the evidence. *"lose the book, lose the run."*

- [ ] **"lets not limit the amount"** — no cap on how many glow pods a crew carries or deploys. A 300x300 instance can have hundreds of rooms and the kit must not assume six.
- [ ] **"color means differnt types of the needs markers"** — **mod-defined marker types, each with its own colour**: route home, cleared, danger, supply cache, unexplored lead. Chosen when a pod is placed, and countable per coordinate in the operations readout because the mod knows what each one means rather than only what colour it is.
- [x] **`CompGlower.GlowColor` has a public setter** backed by a **saved per-instance `glowColorOverride`**, and `CompProperties_Glower.colorPickerEnabled` turns on RimWorld's own colour picker. Verified by decompiling, 0.9.9-dev. **Settable colour needs no new UI.**

"""
anchor = '- [ ] **Legacy field gear** `RR_FieldRecorder`'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.8-dev** (this commit) |', u'| Published | **0.9.9-dev** (this commit) |'),
 (u'| Assembly | SHA-256 `211687673EA54860637418F89D3EFE90436387EDB9BB8284AA84A09A19295B94`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `0E9BEEF6DA1A781EB58E8974340522DF4010EA00004F38F292880677F6FD7F600`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.8', u'## What shipped this session, 0.7.1 → 0.9.9'),
 (u"| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared per scenario |",
  u"| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared per scenario |\n"
  u"| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement, four replacements decided |"),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
63. **The field-kit replacements are decided.** Survey tag → Core `GlowPod`; return beacon → **dropped**, its job taken over by the gate's address book; evidence case → a **designated headquarters `Shelf`** as the archive; recorder → **the book is the recorder**. Asked at the fork, grounded in enumerated Core content.
64. **`CompGlower.GlowColor` has a public setter**, backed by a saved per-instance `glowColorOverride`, and `colorPickerEnabled` on the props turns on RimWorld's own colour picker. Settable glow colour needs no new UI.
65. **Glow pods are never capped.** Owner direction: a 300×300 instance can have hundreds of rooms. Colour is **semantic** — mod-defined marker types, not decoration."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
