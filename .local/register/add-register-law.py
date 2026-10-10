import io

LAW = u"""
---

# LAW — CHECK THE MOD REGISTER BEFORE BUILDING

**Owner direction, 2026-09-29, verbatim:** *"add a memory and a law to always check the registry of mods before building something to see what if anything applies, and do this retro actively dfor regress too"*

## The rule

**Before building anything, check the 294-row mod integration register for what already applies.** Not after. Not when something breaks. Before.

This is a mod whose entire premise is *"we are making a mod that works with the other 274"*. The register is the reviewed record of what that profile already provides, what conflicts with it, and what has to be designed around. Building first and consulting it later produces one of two failures, and both are expensive:

- **Reinventing something a profile mod already does**, badly and incompatibly.
- **Shipping something that breaks** against a mod the owner actually runs.

## Required actions

1. **Open the register HTML.** `outputs/rimrooms-async-industries-register-2026-09-27/…Register.html`. **The HTML is the register**; the xlsx is not, and neither is anybody's memory of it.
2. **Filter by `System family`** matching whatever is about to be built, and read those rows' `Stance`, `Firmness`, `Trace IDs` and `Card` columns.
3. **Read the per-mod review** under `docs/research/reviews/mods/` for any row that looks relevant. The register row is a summary; the review carries the verified facts.
4. **Record the result in the implementation record** — which rows were checked, and what they changed. If none applied, **say so explicitly**. Silence is not evidence of having looked.
5. **Retroactively, for work already shipped.** A system built before this LAW gets the same check, and anything found is recorded as a task rather than quietly fixed or quietly ignored.

## Forbidden actions

- Designing a system from memory of the profile instead of from the register.
- Writing "no mods apply" without having filtered the register for that system family.
- Treating a remembered list of mods as authoritative. **Invariant #19 already exists for this reason**: never trust a remembered list against shipped data — enumerate.
- Reading the xlsx, or the register preview images, in place of the HTML.

## Why

It has already earned this, twice, in ways that were not predictable in advance:

- The register **recovered misread owner references** — phrases taken as flavour turned out to be mod names.
- Its **Doors Expanded row** supplied the exact footprints — `PH_DoorDouble` at 2×1, `PH_DoorTriple` at 3×1, `PH_DoorThickBlastDoor` at 3×2 — that matched the owner's requested 1×2 / 1×3 / 2×3 gate sizes **one for one**. The sizes were not arbitrary; they came from a mod the owner runs, and the register is what revealed that.

Neither of those would have been found by thinking harder.

## Enforcement protocol

Before any checkpoint that adds or changes a system:

```
[REGISTER CHECKED]
System family filtered: <family>
Rows examined: <count and ids>
Applies: <what, and how it changed the design> | NONE, and here is why
```

That statement belongs in the implementation record for the checkpoint. A checkpoint whose record does not say what was checked has not checked.

## Failure recovery

When the owner catches a system built without a register check:

1. Stop and run the check for that system family immediately.
2. Record what the check found — including "nothing" — in the implementation record.
3. If it found something the build should have honoured, **queue it in `TODO.md` as a task with the owner's words**, do not quietly patch it.
4. Do not resume other work until the finding is recorded.
"""

p = '.claude/CONSTRAINTS.md'
s = io.open(p, encoding='utf-8').read()
anchor = u'\n---\n\n## Adding project-specific LAWs'
assert anchor in s, 'anchor not found in CONSTRAINTS.md'
assert 'CHECK THE MOD REGISTER BEFORE BUILDING' not in s
s = s.replace(anchor, LAW + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('LAW added to .claude/CONSTRAINTS.md')

# Index one-liner in the LAW INDEX.
p = '.claude/CLAUDE.md'
s = io.open(p, encoding='utf-8').read()
anchor = u'- **Cross-platform case insensitivity.**'
assert anchor in s
entry = (u'- **Check the mod register before building.** This mod exists to work with 294 others. '
         u'Filter the register by system family **before** designing, read the per-mod reviews it '
         u'points at, and state in the implementation record what was checked and what applied — '
         u'or that nothing did. Retroactively for work already shipped. '
         u'→ `CONSTRAINTS.md §CHECK THE MOD REGISTER BEFORE BUILDING`\n')
assert 'Check the mod register before building' not in s
s = s.replace(anchor, entry + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('LAW indexed in .claude/CLAUDE.md')
