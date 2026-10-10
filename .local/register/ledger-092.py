import io

# CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.2-dev - 2026-09-29 - a gate has a size

- **A gate can be wider than one cell.** An ordinary door gives you a one-wide gate; **the game's own ornate door gives you a two-wide one with no other mods at all**, and so does Anomaly's security door.
- If you run **Doors Expanded**, its double and triple doors and its big blast door work as gates too, giving you three-wide and two-by-three. If you do not run it, nothing changes and nothing is touched.
- **A wider gate is more machine.** It draws more power while open and takes longer to bring up, in proportion to its whole footprint, so a big gate is something you work toward and plan power for.
- **A wide gate never limits how many people cross at once.** It simply has a wider opening, and your colonists spread across it the way they do at any wide door.
- **A gate cannot be resized while it is working** - not while it is open, and not while it is being brought up.
- The gate now tells you its size when you select it.

Full record: [a gate has a size](docs/implementation/GATE_FOOTPRINT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.2-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

# FINALIZED
p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.2-dev - 2026-09-29 - a gate has a size

### Owner directions, verbatim

> *"and rember ther are 1x1 1x2 and 1x3 and 2x3 gate doors that allow differnt capabilities as to the universe and scerios needs"*

> *"gate doors expansions can NOT be done on a working gate"*

> *"2 should really limit numbers through at once because in vinilla any number of pawns can use a door at once so we dont want limitations"*

### The premise changed because the data was read

The plan assumed Core ships only 1x1 doors. Reading the installed game data instead found `Building_MultiTileDoor` and two defs using it: Core's `OrnateDoor` at 2x1 and Anomaly's `SecurityDoor` at 2x1. The class chain `Building_MultiTileDoor : Building_SupportedDoor : Building_Door` was confirmed by decompiling. **So a 1x2 gate needs no mods at all.** Enumerating the installed Doors Expanded copy produced the rest, including `PH_DoorThickBlastDoor` at 3x2 - exactly the 2x3 the owner named. The four sizes in the direction line up one-for-one with doors that already exist.

### What shipped

Width and footprint are tracked separately, because a 2x3 blast door is three wide but six cells of machine. Opening draw and spin-up work scale on cell count, so a bigger gate costs more to run. Entry cells are derived per doorway cell, so a wide gate physically admits more people at once **without any quota** - checked first, and `OrderCrossing` only ever refused the same pawn twice, so the correct action was to add nothing. Rebinding is refused while a gate is ramping, not only while open. Supported providers are declared in the patch file rather than named in code: carrying the component is the allowlist, and only the shape is enforced in code.

### A checker gap, closed narrowly and proved narrow

Patching Doors Expanded made `check-package-integrity.py` fail seven targets, correctly, because it had no concept of optional compatibility. A target inside a `PatchOperationFindMod` is optional by construction. The check now exempts exactly those and still reports them as notes. **The exemption was proved narrow by planting a bogus target outside `FindMod` and confirming it still fails** - an exemption that leaked would be worse than no check.

### Build evidence

0.9.2-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **156** C# source files (one new), **79** approved package files. Assembly SHA-256 `0A2B527ED14475D56428DD2E63A0970853D5C70A854D4BB3516E4D9831FBE001`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; 1,201 keyed references all resolving. **No new gameplay def, asset or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Package files created: 0. Docs updated: 5 (1 new).
**Design premises corrected by reading shipped data rather than trusting memory: 1** - Core does ship a multi-cell door.
**Requirements met by adding nothing: 1** - throughput was already uncapped, so the no-limitations rule needed no code.
**Checker exemptions added and proved narrow by breaking them: 1.**
Gotchas hit again: the `--` in an XML comment, for the **third** time.
Still open and named in `TODO.md`: what a size lets through; hostiles needing width; the adjacent-door-run fallback.
"""
assert '0.9.2-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

# TODO
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **"1x1 1x2 and 1x3 and 2x3 gate doors"**'
new = '- [x] **BUILT 0.9.2-dev, and Core turned out to ship a 2x1 door of its own (`OrnateDoor`), so a 1x2 gate needs no mods at all.** **"1x1 1x2 and 1x3 and 2x3 gate doors"**'
assert old in s
s = s.replace(old, new, 1)
old = '- [ ] **"allow differnt capabilities"** — width is the capability.'
new = ('- [~] **PART BUILT 0.9.2-dev.** Costs-more-to-run and more-people-abreast are done: draw and spin-up scale on '
       'footprint, and width adds doorway cells with **no quota anywhere**, per *"we dont want limitations"*. '
       'Still open: what size lets *through* (body size at the traversal chokepoint) and hostiles needing width. '
       '**"allow differnt capabilities"** — width is the capability.')
assert old in s
s = s.replace(old, new, 1)
anchor = '- [ ] **"all starts have same tech tree'
extra = (u'- [ ] **What a gate\'s size lets through.** Body-size limits at `PortalTraversalPolicy`, so *"vehicals and the like and bigger creatures"* need a wider gate. Its own checkpoint: it belongs at the single traversal chokepoint and deserves a diff that says only that.\n'
         u'- [ ] **The adjacent-door-run fallback** for reaching 1x3 and 2x3 without Doors Expanded, per *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed"*.\n')
assert anchor in s
s = s.replace(anchor, extra + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

# NOW
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.9.1-dev** (this commit) |', u'| Published | **0.9.2-dev** (this commit) |'),
 (u'| Build | **155 C# files, 79 package files**, zero warnings, zero errors |',
  u'| Build | **156 C# files, 79 package files**, zero warnings, zero errors |'),
 (u'| Assembly | SHA-256 `152660F9835E71DD9A75E9D59C1B9EDE72F9D09CF47C488F0A552EF1DC9FCBAE`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `0A2B527ED14475D56428DD2E63A0970853D5C70A854D4BB3516E4D9831FBE001`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.9.1', u'## What shipped this session, 0.7.1 → 0.9.2'),
 (u'| 0.9.1 | **One kind of gate** — 68 dead branches collapsed, a vestigial power model removed, net −112 lines |',
  u'| 0.9.1 | **One kind of gate** — 68 dead branches collapsed, a vestigial power model removed, net −112 lines |\n'
  u'| 0.9.2 | **A gate has a size** — 1×1 to 2×3, Core\'s own `OrnateDoor` gives 1×2 free, cost scales with footprint |'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

old = u'2. **Multi-cell gates** — 1x2, 1x3 and 2x3, on the settled Core-door-only gate model.'
new = (u'2. **What a gate\'s size lets through.** ~~Multi-cell gates~~ **BUILT 0.9.2-dev** for the sizes themselves: '
       u'Core\'s `OrnateDoor` is 2x1 so **1×2 needs no mods**, Anomaly\'s `SecurityDoor` matches it, and Doors Expanded '
       u'supplies 1×3 and 2×3 behind a `PatchOperationFindMod`. **Still open:** body-size limits at '
       u'`PortalTraversalPolicy` so bigger creatures and vehicles need a wider gate, and the adjacent-door-run fallback '
       u'for 1×3 and 2×3 without that mod. Original entry: multi-cell gates')
assert old in s
s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
40. **A gate's width and its footprint are different numbers.** A 2×3 blast door is three wide and six cells of machine. Width decides what fits through; footprint decides what it costs to run.
41. **Throughput is never capped.** Owner direction: *"in vinilla any number of pawns can use a door at once so we dont want limitations"*. A wide gate gets more doorway cells, never a quota. There is no counter, deliberately.
42. **A patch target inside `PatchOperationFindMod` is optional by construction**, and only there. The integrity checker exempts exactly those and still reports them. The exemption was proved narrow by planting a bogus target outside it.
43. **Core ships `OrnateDoor` at 2×1 and `Building_MultiTileDoor` to drive it.** Anomaly adds `SecurityDoor`. This was found by enumerating installed data after the opposite was assumed."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
