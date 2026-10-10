import io

# --- TODO first: queue the direction before the archive quotes it ---------
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = u"""
**Verbatim owner direction (2026-09-29):** *"add a memory and a law to always check the registry of mods before building something to see what if anything applies, and do this retro actively dfor regress too"*

- [x] **Memory written** - `feedback_check_register_first.md`, loaded every session.
- [x] **LAW written** - `CONSTRAINTS.md §CHECK THE MOD REGISTER BEFORE BUILDING`, indexed in `.claude/CLAUDE.md`. It requires filtering the register by system family **before** designing, reading the per-mod review the row points at, and **stating in the implementation record what was checked and what applied, or that nothing did**. Silence is not evidence of having looked.
- [x] **`tools/register-query.py`** - the register answerable from the command line, because a LAW needing a browser and a 294-row scroll is a LAW that gets skipped exactly when it matters. It immediately found a parsing trap: the HTML holds **two tables** over the same mods with different layouts, and a naive parse returns 589 rows while looking correct.
- [x] **Retroactive pass, 0.10.4-dev.** Four results: a **real defect found and fixed** (row 78, drafted animals could cross a gate); the **stance-classifier bug confirmed on a concrete row** (78 reads Required, its review reads optional); **pursuit verified independent** of row 200, Search and Destroy; and **roof containment verified** to already survive row 188, Removable Mt.Rock Roof Patch.
- [ ] **Continue the retroactive pass** across the remaining system families. Done so far: animals, security, spatial construction, expedition logistics. Not yet swept: facilities, storage, furniture, commerce, contracts, power, medical, interface, world operations, and the rest.

"""
anchor = u'\n**Verbatim owner direction (2026-09-29):** *"and remembner alot of things you should be reviewing'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)

# The stance bug now has a named example.
old = "- [ ] **The register classifier bug"
if old in s:
    s = s.replace(old, "- [ ] **CONCRETE EXAMPLE FOUND 0.10.4-dev: row 78 reads `Required` while its own review reads `optional`.** **The register classifier bug", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.10.4-dev - 2026-09-29 - the register, checked backwards

- **A drafted animal could walk through a gate while a drafted colonist could not.** Fixed. A pawn under direct combat control does not wander off through a gate, whatever it is.
- That was only reachable if you run **Draftable Animals**, which vanilla cannot do - so it was found by checking the mod register against work already shipped, not by re-reading the code.
- Two other systems were checked against the profile and needed no change: what chases you works the same with or without **Search and Destroy**, and a coordinate still cannot be stripped of its roof with a roof-removal mod installed.

Full record: [the register, checked backwards](docs/implementation/REGISTER_RETRO_AUDIT.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.10.4-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.10.4-dev - 2026-09-29 - the register, checked backwards

### Owner direction, verbatim

> *"add a memory and a law to always check the registry of mods before building something to see what if anything applies, and do this retro actively dfor regress too"*

### A memory, a LAW, and a tool the LAW needs

The memory is loaded every session. The LAW lives in `CONSTRAINTS.md` and is indexed in `.claude/CLAUDE.md`: filter the register by system family **before** designing, read the per-mod review the row points at, and **state in the implementation record what was checked and what applied, or that nothing did**.

A LAW that requires opening a browser and scrolling a 294-row table is a LAW that gets skipped exactly when it is inconvenient, so `tools/register-query.py` makes the register answerable from the command line. It immediately found a parsing trap: the HTML carries **two tables** over the same 294 mods with different layouts, the second putting a Steam id where the system family belongs. A naive parse returns **589 rows** and would have made every family filter miss half its matches while appearing to work.

### The backwards pass found a real defect

**Row 78, Draftable Animals - Releashed**, is in the owner's profile. 0.9.4-dev let player animals cross a gate and its eligibility check returned early for animals **before** testing `Drafted`. A drafted colonist has never been allowed through; a drafted animal could. **Vanilla cannot draft an animal, so this read as dead code and is only reachable on somebody else's mod list** - exactly the class of defect the register exists to surface, and exactly the class no amount of re-reading a diff would find. Fixed in both the crossing service and the traversal policy.

### And three more results worth recording

**The stance-classifier bug now has a named example.** Row 78 reads `Required`; its own review reads *"Provisional disposition: optional"*. The open task had no reproducible case before. Consequence for the LAW: the `Stance` column is not trustworthy alone, and the per-mod review is.

**Pursuit verified independent** of row 200, Search and Destroy, whose review requires that *"authored threat behavior/player control remain independent"*. 0.9.5-dev uses vanilla `LordJob_AssaultColony`, independent by construction. No change needed, and now checked rather than lucky.

**Roof containment verified** against row 188, Removable Mt.Rock Roof Patch, whose review warns not to assume a mountain roof preserves protection after removal. `BackroomsContainment`'s second guarantee re-roofs any cell that loses its roof **whatever removed it**, written defensively before that mod was considered. No change needed - and recording that is the point, because silence is not evidence of having looked.

### Build evidence

0.10.4-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **159** C# source files, **79** approved package files. All six checkers pass. **No new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

LAWs added: 1. Memories added: 1. Tools added: 1. Defects found by the retroactive pass: **1, fixed**.
**Systems verified compliant rather than changed: 2** - recorded deliberately, because a check that only reports problems teaches nobody what was examined.
**Parsing traps found in the register itself: 1** - two tables, 589 rows, silent half-misses.
Still open: the remaining system families to sweep; the field-gear replacements; the last two scenarios.
"""
assert '0.10.4-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 (u'| Published | **0.10.3-dev** (this commit) |', u'| Published | **0.10.4-dev** (this commit) |'),
 (u'## What shipped this session, 0.7.1 → 0.10.3', u'## What shipped this session, 0.7.1 → 0.10.4'),
 (u"| 0.10.3 | **Something is not where you left it** — silent between-visit fixture displacement |",
  u"| 0.10.3 | **Something is not where you left it** — silent between-visit fixture displacement |\n"
  u"| 0.10.4 | **The register, checked backwards** — a LAW, a query tool, and a real defect found |"),
 (u'| Register | `outputs/rimrooms-async-industries-register-2026-09-27/…Register.html` — **open the HTML**, not the xlsx |',
  u'| Register | `python tools/register-query.py families\\|family <x>\\|find <x>\\|row <n>` — **the HTML is the register**, never the xlsx |'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
76. **LAW: check the mod register before building.** Filter by system family, read the per-mod review the row points at, and **state in the record what was checked and what applied — or that nothing did**. Retroactively for shipped work too. `python tools/register-query.py family <x>`.
77. **The register's `Stance` column is not trustworthy on its own.** Row 78 reads `Required`; its review reads `optional`. That is the known classifier bug, and the review is the authority.
78. **The register HTML has TWO tables** over the same 294 mods with different layouts. A naive parse yields 589 rows and silently halves every family filter. `register-query.py` keeps the row whose family reads as a family."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
