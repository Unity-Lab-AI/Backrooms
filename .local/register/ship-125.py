# -*- coding: utf-8 -*-
"""Ledger for 0.12.5-dev: the build-order correction."""
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


insert_before('CHANGELOG.md', u'## 0.12.4-dev', u"""## 0.12.5-dev - 2026-09-29 - the queue was in the wrong order

- **Nothing in the game changed, on purpose.** This checkpoint is a correction to what gets built next, and shipping it is cheaper than building the wrong thing.
- **Four research projects were NOT written**, because the things they would have unlocked do not exist yet. The research band after the current one is about running remote sites, and remote sites are not built.
- **The build order now matches the design chart**, which said all along that the remaining research stops at the current band and the campaign arcs come next.

Full record: [the queue was in the wrong order](docs/implementation/BUILD_ORDER_CORRECTION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the build-order correction (0.12.5-dev)

**Verbatim user quote:** *"if all that is good to go then continue wwhats next, but idk, sounds like ur wording means its full of buggs"*

### What shipped

A correction, and deliberately no gameplay change. Research tier 3 was next in `NOW.md`; the knob sweep found it has almost nothing to move, and `docs/CAMPAIGN_CHART.md` §7 turned out to authorise **"tier 0 to 2 first"** with arcs 5 to 8 next. The queue is corrected to match the chart.

### Files touched

`docs/implementation/BUILD_ORDER_CORRECTION.md`, `docs/NOW.md`, `docs/TODO.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj.

### Closure notes

- **Seven tier 3 projects would have needed four invented effects.** The sweep found ~30 `Maximum*` constants in `ConnectedWork/` that are **scan budgets, not unlocks**; three good knobs that all belong to Spatial; one that belongs to Measurement; and **nothing at all** for Facilities, Fieldcraft, Entities and Commerce, because the systems a remote-operations unlock would modify are not written. That is exactly what three tier 2 unlocks were deleted for at 0.11.6-dev.
- **The chart had the answer already.** §7 step 6 reads *"the remaining eight research branches, tier 0 to 2 first"*, and step 8 is arcs 5 to 8. Tier 3 is *remote operations*; **arc 5 is what builds remote sites.** A research band cannot unlock capabilities for a system that does not exist.
- **Arc 5's obvious first piece is blocked too, and that was checked rather than assumed.** *"A remote base is a costly responsibility rather than free map ownership"* suggests a daily surcharge per held site - but `OwnsMap` returns true for the headquarters and for **open Backrooms coordinates**, which are transient destinations rather than bases. There is no way to acquire an ordinary remote world site yet, so the surcharge would always compute **zero**. The acquisition is arc 5's real first piece.
- **On the user's question about bug volume, answered with numbers rather than reassurance:** of the defects found in already-shipped code this session, **exactly one** would visibly malfunction in play - the frozen approach cell fixed in 0.12.3. The rest *did nothing*: an unlock that moved no number, two clocks that bounded nothing, values nobody read. Everything else reported loudly this session was caught in code written minutes earlier, before it shipped. **The standing caveat is the real one: no game has ever been launched, so the entire class of runtime defects is unverified.**
- Build 0.12.5-dev, 170 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, nine proofs hold. **No game was launched.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.4-dev**.', u'| Published | **0.12.5-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.4',
     u'## What shipped this session, 0.7.1 → 0.12.5'),
    (u'| 0.12.4 | **Four answers** — supply requirement, deconstruct warning, solo hints; **a tier 0 unlock that did nothing**, found by a new general sweep |',
     u'| 0.12.4 | **Four answers** — supply requirement, deconstruct warning, solo hints; **a tier 0 unlock that did nothing**, found by a new general sweep |\n'
     u'| 0.12.5 | **The queue was in the wrong order** — tier 3 has no knobs to move; the chart authorises arcs 5–8 next. Four hollow unlocks not written |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

# Reorder the queue to match the chart, and say why in place.
start = s.index(u'1. **Research tiers 3–4**')
end = s.index(u'3. **The Store and Solo/Group starts.**') if u'3. **The Store and Solo/Group starts.**' in s \
    else s.index(u'4. **Generated requests after the hinge**')
s = s[:start] + u"""1. **Arcs 5–8.** **This is what `docs/CAMPAIGN_CHART.md` §7 step 8 authorises next**, and the
   chart beats any other document. Steps 6 and 7 are done.
   - **Arc 5, "Build beyond headquarters".** *"Remote sites need people, supplies, signals,
     protection, and an exit plan... A remote base is a costly responsibility rather than free map
     ownership."* Its **first piece is a way to hold a remote site at all** — the surcharge that
     makes it costly follows, because today it would compute zero (`OwnsMap` returns true only for
     the headquarters and for transient open coordinates).
   - Arc 6, the outside world — **the `IncidentDef` surface built in 0.11.8 is its home.**
   - Arc 7, industrial reach. **DLC-optional throughout.**
   - Arc 8, deeper systems — partly built already: depth bands, archetypes, the pressure ladder.
2. **Research tiers 3–4, AFTER the arcs.** **Deliberately moved behind them, 0.12.5-dev.** Tier 3
   is *"remote operations: support more than one site; work beyond headquarters"*, and the knob
   sweep found **nothing to move** for Facilities, Fieldcraft, Entities or Commerce, because the
   systems such an unlock would modify are not written. Four of seven projects would have been
   invented effects. Record: `implementation/BUILD_ORDER_CORRECTION.md`.
   - The knobs that **do** exist and are real: `MaximumFrontiersPerCoordinate`, `FrontierRarity`
     and `EmergenceShare` (all three Spatial's, so one branch cannot take them all) and
     `SurveyTicks` (Measurement's).
   - **The ~30 `Maximum*` constants in `ConnectedWork/` are scan budgets, not unlocks.** Raising
     one is a performance decision with no effect a player could name. Do not reach for them.
""" + s[end:]
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Owner directions recorded late, second pass', u"""
**Build-order correction (2026-09-29, 0.12.5-dev), answering** *"if all that is good to go then continue wwhats next, but idk, sounds like ur wording means its full of buggs"*

- [x] **The queue in `NOW.md` was in the wrong order and is corrected.** It listed research tiers 3-4 before arcs 5-8. `docs/CAMPAIGN_CHART.md` §7 authorises *"the remaining eight research branches, **tier 0 to 2 first**"* at step 6 and **arcs 5 to 8 at step 8**. Steps 6 and 7 are done, so the next authorised step is 8. The chart beats any other document by its own rule.
- [x] **Four tier 3 projects were not written**, because the sweep found no knob for Facilities, Fieldcraft, Entities or Commerce at that band. Tier 3 is *remote operations* and **arc 5 is what builds remote sites**; a research band cannot unlock capabilities for a system that does not exist. Exactly what three tier 2 unlocks were deleted for at 0.11.6-dev.
- [x] **Arc 5's obvious first piece was checked and is also blocked.** A daily surcharge per remote site would always compute **zero**, because `OwnsMap` covers only the headquarters and transient open coordinates and nothing can acquire an ordinary remote world site yet. **The acquisition is arc 5's real first piece.**
- [x] **Bug volume answered with numbers.** Of the defects found in already-shipped code this session, **one** would visibly malfunction in play (the frozen approach cell, fixed 0.12.3). The rest did nothing. Everything else reported was caught in code written minutes earlier. **The real caveat: no game has ever been launched, so every runtime defect class is unverified.**
""")
