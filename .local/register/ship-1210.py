# -*- coding: utf-8 -*-
"""Ledger for 0.12.10-dev: the handoff audit."""
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


insert_before('CHANGELOG.md', u'## 0.12.9-dev', u"""## 0.12.10-dev - 2026-09-29 - the handoff, audited

- **Nothing in the game changed.** This is the session handoff, and writing it properly turned up four problems in the project's own checks.
- **Four of the mod's fifteen internal proofs had not been running.** They pass, but they were being skipped, so nobody knew.
- **The build fingerprint recorded in the handoff had been wrong for five versions.** It is now read from the build itself.
- **Two questions the owner had already answered were still listed as open.** Both closed with their answers.

Full record: [writing the handoff found four unrun proofs](docs/implementation/HANDOFF_AUDIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the handoff audit (0.12.10-dev)

**Verbatim user quote:** *"lets go ahead and do now.md prcedure for handoff before compact"*

### What shipped

The `NOW.md` compaction handoff, and **four defects in the handoff and the ritual itself**, found by reading every claim against the thing it describes rather than tidying the prose. **No gameplay changed.**

### Files touched

`docs/NOW.md`, `docs/implementation/HANDOFF_AUDIT_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and five renames in `.local/register/`.

### Closure notes

- **FOUR LIVE PROOFS HAD GONE UNRUN for most of the session.** The ritual said *"every proof (four)"*; the directory holds **fifteen**. Worse, the per-checkpoint runner grepped for `^PROOF HELD` - and four proofs end `PASS:`, so `displacement`, `facilities`, `fit` and `spinup` were skipped every checkpoint. **A skipped proof reports nothing, which is indistinguishable from a passing one.** All four pass, and passing is luck rather than evidence: they guard revisit displacement, facility formation, the body-size fit ladder and the spin-up decay curve, and this session touched all four areas. **The ritual now runs every proof by exit status**, which is phrasing-independent. Same failure as the three claims that could not fail, one level up: a runner matching a phrasing is a check keyed off a token.
- **Five patch scripts were named `proof-*`** - mine, from this session. So `proof-*.py` had stopped meaning *"a proof"*, and a future session would have run a landed patch and had to work out whether a proof had broken. Renamed to `patch-*`, and the ritual states the distinction.
- **The assembly hash had been stale for five checkpoints**, still holding 0.12.4's value. Nobody catches that by reading, because a SHA-256 looks equally plausible wrong. Corrected, then **immediately stale again** because bumping the version rebuilds the assembly - so it is now read from the live build **after** the determinism run, which is the only order that can be right, and the line says so.
- **Two "open owner questions" had been answered hours earlier** - `reserveChargePowerWatts` and the 250 W idle draw, both settled in 0.12.4-dev. Moved to a **Closed this session** block with their answers, alongside the three other decisions the owner made today.
- **The gotcha counts were wrong and flattering.** The heredoc trap said *"hit six times"*; the real count is **eight**, three of them **after** the line already warned about it.
- **The top warning was two sessions out of date.** Replaced with the evidenced version: **four things that could not fail, all mine**, three found by fault-planting and the fourth only by writing this file.
- Build 0.12.10-dev, 172 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, **fifteen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
old = u'| 0.12.10 | **The handoff** — four live proofs found unrun, five patch scripts un-named as proofs, a stale hash corrected |'
assert old in s
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Owner directions recorded late, second pass', u"""
**Verbatim owner request (2026-09-29):** *"lets go ahead and do now.md prcedure for handoff before compact"*

- [x] **The `NOW.md` handoff written, and four defects found in it and in the ritual.** No gameplay changed; what changed is what the next session can trust.
- [x] **Four live proofs had not been running.** The ritual said four proofs; there are **fifteen**, and the runner grepped `^PROOF HELD` while four end `PASS:`. `displacement`, `facilities`, `fit` and `spinup` were skipped every checkpoint. All pass - but they were not being consulted while the code they guard was edited. **The ritual now runs every proof by exit status.**
- [x] **Five of my own patch scripts were named `proof-*`** and are renamed `patch-*`, so the glob means "a proof" again.
- [x] **The assembly hash in the handoff had been stale for five checkpoints.** Now read from the live build after the determinism run.
- [x] **Two already-answered owner questions were still listed as open** and are moved to a closed block with their answers.
- [x] **The gotcha counts were flattering**: the heredoc trap is at **eight**, not six, and three of those came after the warning was already written.
""")
