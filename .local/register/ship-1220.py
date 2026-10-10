# -*- coding: utf-8 -*-
"""Ledger for 0.12.20-dev: the register became queryable by the column that matters."""
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


insert_before('CHANGELOG.md', u'## 0.12.19-dev', u"""## 0.12.20-dev - 2026-09-29 - the register, by the column that matters

- **The mod register can now be asked the question it exists to answer.** Every one of its 295 rows carries a trace code saying which part of this mod it bears on, and there was no way to search by it. Now there is, so "what applies to the thing I am about to build" is one command.
- **A new check verifies this mod still uses other people's mods the way the register says to.** It confirms no hard dependency on any mod, that the one mod we patch at all is a reviewed row, that the patch does nothing when that mod is absent, and that none of another mod's content has been copied in here.
- **We patch exactly one mod, optionally**, and depend on none.

Full record: [the register, by the column that matters](docs/implementation/REGISTER_COMPLIANCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the register, by the column that matters (0.12.20-dev)

**Verbatim user quotes, in order:** *"lets get it and rememebr we are trying to get shit done in droves and correctly and guided by the columns in the mod registar"*, then *"now that you can actually read the registar that ive been telling to to use make sure nothing regressed in the build that it mentions how those mods are to be use by ours"*, then *"remmebr its not law but guidance"*, then *"remmebr we dont change the mods we dont have rights to edit 274 or sum mods"*.

### What shipped

`register-query.py` gained `traces` and `trace <code>`, and **a ninth checker** verifies the build against the register's structural guidance on using other mods.

### Files touched

`tools/register-query.py`, `tools/check-register-compliance.py` (new), `docs/implementation/REGISTER_COMPLIANCE_IMPLEMENTATION.md`, `docs/NOW.md`, `docs/TODO.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj.

### Closure notes

- **"GUIDED BY THE COLUMNS" NAMED THE COLUMN I HAD BEEN SKIPPING.** The register has six columns and I had been querying three: family, stance, firmness. The **trace** column is the one that answers the question the LAW actually asks - *what applies to the thing I am about to build* - because it names the **Rimrooms feature** a row bears on rather than the mod's own subject matter. **It had no query at all**, which is exactly why it got skipped: a column nobody can ask about is a column nobody consults. Sixteen codes are in use; `RR-OUT` alone covers 65 rows and is precisely *"a way out into the world"*.
- **A truncated code was found and fixed while adding it.** The first pattern capped codes at eight characters and reported `RR-SPACEFLI`; the real code is `RR-SPACEFLIGHT`. A summary that silently truncates its own keys is a summary that merges two categories.
- **THE REGISTER IS GUIDANCE, NOT LAW - owner-corrected, and the checker is written that way.** *"remmebr its not law but guidance"*. `check-register-compliance.py` does **not** veto work because a row exists. It verifies only the handful of dispositions that are **structural** and would regress silently, and every check is about **this** package rather than a judgement about anybody else's.
- **What it verifies, and the answer today:** no hard mod dependency at all (`modDependencies` empty; `loadAfter` names Core only); the only mod this package patches is **Doors Expanded, row 77, Optional, Settled, trace RR-FAC;RR-THREAT;RR-STYLE;RR-COMPAT**; that patch sits inside a `PatchOperationFindMod` so it applies nothing when the mod is absent (invariant 42); and **no `ResearchProjectDef`, `QuestScriptDef` or `StorytellerDef` is authored**, which is what keeps this mod clear of rows 191, 279, 148 and 132 by construction rather than by care.
- **WE NEVER EDIT THEIR FILES, and that is now asserted rather than remembered.** *"remmebr we dont change the mods we dont have rights to edit"*. A `PatchOperationFindMod` does **not** edit anybody's files - the owner confirmed that reading explicitly on 2026-09-29 - it patches the loaded def database at runtime. What would breach the direction is this repository **containing** another mod's content, so the checker asserts every shipped file belongs to this package and that no second `About.xml` has appeared.
- **Nothing had regressed.** Three separate reviews had independently concluded that this mod should use its own def types rather than the native systems those mods operate on, and the build still does. That conclusion is now checked every checkpoint instead of re-derived by reading.
- **The four remaining `ThingDef`s were confirmed as the known open ones** - `RR_FieldRecorder`, `RR_RouteRecording`, `RR_ReturnAnchor`, `RR_QuietPursuer` - all already tracked in the queue as the last existing-content replacements. No new gameplay def has crept in.
- **Three planted faults, three catches, clean on restore:** a declared hard dependency, an authored `ResearchProjectDef`, and patching a mod that is not a reviewed row.
- Build 0.12.20-dev, 173 C# files, 91 package files, **0 warnings, 0 errors**. **No C# changed.** **NINE checkers** pass, twenty proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.19-dev**.', u'| Published | **0.12.20-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.19',
     u'## What shipped this session, 0.7.1 → 0.12.20'),
    (u'| 0.12.19 | **The yellow rooms were never carpeted** — a real shipped defect; three of my own audit verdicts corrected. **Twentieth proof** |',
     u'| 0.12.19 | **The yellow rooms were never carpeted** — a real shipped defect; three of my own audit verdicts corrected. **Twentieth proof** |\n'
     u'| 0.12.20 | **The register, by the column that matters** — `trace` querying, and a **ninth checker** verifying how this mod uses other mods |'),
    (u'| Checkers | **eight**, all passing |', u'| Checkers | **NINE**, all passing |'),
    (u'7. **Every checker** (eight): `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `research/audit-gate0.py`.',
     u'7. **Every checker** (NINE): `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `check-register-compliance.py`, `research/audit-gate0.py`.'),
    (u'| Register | `python tools/register-query.py families\\|family <x>\\|find <x>\\|row <n>` — **the HTML is the register**, never the xlsx |',
     u'| Register | `python tools/register-query.py families\\|family <x>\\|find <x>\\|row <n>\\|traces\\|trace <code>` — **query by `trace`**: it names the Rimrooms feature a row bears on, which is the question *"what applies to what I am building"*. **The HTML is the register**, never the xlsx. **It is GUIDANCE, not law** (owner, 2026-09-29) |'),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:70]
    s = s.replace(old, new, 1)

marker = u'205. **A filter that skips the case it guards against is worse than no check.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'206. **The mod register is GUIDANCE, not law.** Owner-corrected 2026-09-29: *"remmebr its not '
     u'law but guidance"*. Consult it, let it shape the design, and say what it said — but a row '
     u'does not veto work, and a checker built on it must only assert what is **structural**.\n'
     u'207. **Query the register by `trace`, not only by family.** The trace column names the '
     u'**Rimrooms feature** a row bears on, which is the question the rule actually asks. It had no '
     u'query until 0.12.20-dev, and that is precisely why it was the column that got skipped. '
     u'**A column nobody can ask about is a column nobody consults.**\n'
     u'208. **A `PatchOperationFindMod` does not edit anybody’s files** — owner-confirmed. It '
     u'patches the loaded def database at runtime and applies nothing when the mod is absent. What '
     u'would breach *"WE ARE NOT EDITING OTHER PEOPLES MODS"* is **shipping their content here**, '
     u'and that is what `check-register-compliance.py` asserts.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

t = read('docs/TODO.md')
anchor = u'**Built 2026-09-29, 0.12.19-dev'
if anchor not in t:
    anchor = u'**Built 2026-09-29, 0.12.18-dev: the company stops naming things.**'
    if anchor not in t:
        anchor = u'**Built 2026-09-29, 0.12.13-dev: arcs 5 to 8 have work in them.**'
assert anchor in t, 'TODO anchor not found'
block = u"""**Built 2026-09-29, 0.12.20-dev: the register, by the column that matters.**

**Verbatim owner directions:** *"guided by the columns in the mod registar"*, *"make sure nothing regressed in the build that it mentions how those mods are to be use by ours"*, *"remmebr its not law but guidance"*, *"remmebr we dont change the mods we dont have rights to edit 274 or sum mods"*.

- [x] **`register-query.py` gained `traces` and `trace <code>`.** The trace column names which Rimrooms feature each row bears on, which is the question the rule actually asks, and it had **no query at all** - which is why it was the column that got skipped. Sixteen codes in use; `RR-OUT` alone is 65 rows. A truncated code was found and fixed on the way: `RR-SPACEFLI` was really `RR-SPACEFLIGHT`.
- [x] **THE REGISTER IS GUIDANCE, NOT LAW** - owner-corrected, and recorded as invariant 206. A row does not veto work.
- [x] **A ninth checker, `check-register-compliance.py`**, verifies only what is structural: no hard mod dependency, the one patched mod is a reviewed row, the patch is inside `PatchOperationFindMod` so it does nothing when absent, no `ResearchProjectDef`/`QuestScriptDef`/`StorytellerDef` authored, and no other mod's content shipped here.
- [x] **Nothing had regressed.** We patch exactly one mod, optionally - Doors Expanded, row 77 - and depend on none.
- [x] **"We don't edit their files" is now asserted rather than remembered.** A `PatchOperationFindMod` patches the runtime def database, not their files; shipping their content here is what would breach it, and that is what is checked.

"""
write('docs/TODO.md', t.replace(anchor, block + anchor, 1))
