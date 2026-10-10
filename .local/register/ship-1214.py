# -*- coding: utf-8 -*-
"""Ledger for 0.12.14-dev: the queue could not answer the question."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def insert_before(rel, anchor, block):
    s = read(rel)
    assert anchor in s, '%s: anchor not found' % rel
    write(rel, s.replace(anchor, block + anchor, 1))


insert_before('CHANGELOG.md', u'## 0.12.13-dev', u"""## 0.12.14-dev - 2026-09-29 - the queue could not answer the question

- **Nothing in the game changed.** The owner asked how close the mod was to finished, and the working queue could not say, because 178 of its 254 open rows had never been re-checked against the code.
- **155 rows re-measured.** 114 of them turned out to be built or deliberately superseded; 41 were rewritten to name exactly what exists and what does not. Open rows went from **254 to 107**.
- **Nothing was ticked off on a guess.** Every flip names the file, symbol, def or version that proves it, so anybody can re-check it instead of trusting it.
- **It found a real hole:** the seven universe factions the owner asked for are completely unbuilt, and so is mining and floor recovery inside the Backrooms, which a code comment had been claiming for months.

Full record: [the queue could not answer the question](docs/implementation/BACKLOG_AUDIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the queue could not answer the question (0.12.14-dev)

**Verbatim user quote:** *"okay is that todo list getting there are we getting close to having all work complete on the mod build to completion and thourough totality? get to it all"*

### What shipped

A full re-measurement of `docs/TODO.md` against the shipped code. **No gameplay changed.**

### Files touched

`docs/TODO.md`, `docs/implementation/BACKLOG_AUDIT_IMPLEMENTATION.md`, `docs/NOW.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and three audit scripts in `.local/register/`.

### Closure notes

- **THE QUEUE COULD NOT ANSWER THE QUESTION, AND THAT WAS THE FINDING.** 254 open rows, **178 of them in the historical master-backlog section with statuses that had never been re-measured.** A large fraction shipped between 0.7.2-dev and 0.12.13-dev and nobody flipped a checkbox; some went stale **during this session**. Third appearance of the same defect as the stale assembly hash and the stale C# file count, and the first time it was being used to answer a question about whether the project was nearly finished.
- **155 rows re-measured: 114 built or superseded, 41 rewritten as partial with the gap named.** Open rows **254 to 107**, done rows 278 to 408. **LAW held throughout: status changes only, every original word kept, and evidence appended** - a file, symbol, def, version or invariant - so a flip can be re-checked rather than trusted. Nothing was flipped on a guess; anything unverifiable stayed open.
- **NO `FactionDef` EXISTS ANYWHERE IN THE PACKAGE.** The entire *"period and factions"* owner direction from 2026-09-28 - the 1990s framing and seven named universe factions - is unbuilt, thirteen rows, none started. It is also **explicitly authorised**: the owner answered that these are new `FactionDef`s reusing existing pawn kinds and icon paths, because a `FactionDef` is world configuration rather than a physical gameplay Def. **Largest completely unbuilt owner direction remaining.**
- **A code comment had been claiming something the code does not do.** `BackroomsContainment.cs` says *"every solid area is mineable in a variety of materials"*; **there is no mineable-rock placement anywhere in `Generation/`.** The roofing half is real and is what makes *"no outside"* survive another mod's roof removal. Invariant 130 again, and the reason this audit greps rather than reads. Three owner directions turn out to be one unbuilt piece: **mineable materials, reusable floor terrain, and floors that return something when lifted.**
- **One row's own complaint had gone stale.** *"`portalWindowTierProjects` currently names the single..."* - it names **three** and has since 0.10.9-dev.
- **Rows that structurally cannot close without the owner are now marked as such**, not left ambiguous: performance measurement, 294-profile def collisions, the compatibility report, balance and the invalid-state matrix, and the RWT surface. **Only the owner launches the game.**
- **One row was challenged rather than closed.** *"Remap RimWorld's menus, tabs and campaign views"* is invasive, would fight every interface mod in the register, and no owner direction has asked for it since; the twelve-pane Operations tab already is the company-first surface. **A row that would be wrong to satisfy silently is worth saying so about.**
- **The heredoc trap was hit for the NINTH time** while writing this ledger, four after the gotcha line already said to stop. The count is corrected rather than rounded down.
- Build 0.12.14-dev, 173 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, **seventeen** proofs exit zero. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.13-dev**.', u'| Published | **0.12.14-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.13',
     u'## What shipped this session, 0.7.1 → 0.12.14'),
    (u'| 0.12.13 | **Arcs 5 to 8 have work in them** — thirteen more families, one per item the chart names. **Chart §7 step 8 closed** |',
     u'| 0.12.13 | **Arcs 5 to 8 have work in them** — thirteen more families, one per item the chart names. **Chart §7 step 8 closed** |\n'
     u'| 0.12.14 | **The queue could not answer the question** — 155 backlog rows re-measured against the code; open rows 254 → 107. **No `FactionDef` exists at all** |'),
    (u'- **Bash heredocs mangle `\\n` and break on apostrophes.** Hit **EIGHT times**',
     u'- **Bash heredocs mangle `\\n` and break on apostrophes.** Hit **NINE times**'),
]
for old, new in pairs:
    assert old in s, 'anchor missing: %r' % old[:60]
    s = s.replace(old, new, 1)

marker = u'187. **Two documents can describe the same thing from two directions and nobody notices.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'188. **A queue nobody re-measures cannot answer "how much is left".** 178 rows carried a '
     u'status that was never re-checked; 114 of them were built. **Re-measure the queue against the '
     u'code before answering any question about progress**, and append the evidence so the next '
     u'reader can re-check rather than trust.\n'
     u'189. **Close a row with a named read site, or leave it open.** A flip on a guess is worse '
     u'than a stale row, because it removes the thing from view. Anything unverifiable stays open.\n'
     u'190. **Say when a row cannot close without the owner.** Performance, balance, the 294 '
     u'profile and the compatibility report all need a launch, and only the owner launches. Marking '
     u'that is honesty, not deferral — and `DEFERRED.md` still gets no rows.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

t = read('docs/TODO.md')
anchor = u'**Built 2026-09-29, 0.12.13-dev: arcs 5 to 8 have work in them.**'
assert anchor in t, 'TODO anchor not found'
assert u'0.12.14-dev: the queue could not answer' not in t, 'already applied'
block = u"""**Built 2026-09-29, 0.12.14-dev: the queue could not answer the question.**

**Verbatim owner question:** *"okay is that todo list getting there are we getting close to having all work complete on the mod build to completion and thourough totality? get to it all"*

- [x] **155 backlog rows re-measured against the shipped code.** 114 built or superseded, 41 rewritten as partial with the gap named. **Open rows 254 to 107.** LAW held: status only, every original word kept, evidence appended so a flip can be re-checked rather than trusted.
- [x] **The queue could not answer the question**, because 178 rows had never been re-measured. Third appearance of the stale-number defect, after the assembly hash and the C# file count.
- [x] **Found: no `FactionDef` exists anywhere in the package.** The seven universe factions are completely unbuilt and explicitly authorised. **Next checkpoint.**
- [x] **Found: `BackroomsContainment.cs` claims mineability in a comment that no code implements.** Mineable materials, reusable floor terrain and floor recovery are one unbuilt piece.
- [x] **Rows that cannot close without an owner launch are now marked as such** rather than left ambiguous.
- [x] **One row challenged rather than closed:** remapping Core's menus is invasive and nothing has asked for it since.

"""
write('docs/TODO.md', t.replace(anchor, block + anchor, 1))
