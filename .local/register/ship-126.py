# -*- coding: utf-8 -*-
"""Ledger for 0.12.6-dev: arc 5's first piece."""
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


insert_before('CHANGELOG.md', u'## 0.12.5-dev', u"""## 0.12.6-dev - 2026-09-29 - a remote base is a costly responsibility

- **A new Sites pane.** Put a place your branch holds on the books, and it becomes the branch's responsibility - your people and supplies reach it, a gate can be built there, and a way out of the Backrooms can come up on it.
- **It costs every day, and you can see exactly how much.** A quarter of your branch's overhead per site, billed as its own line so you can decide whether a place is worth keeping.
- **The cost scales with your operation.** A site costs a research branch on fifty million rather more in absolute terms than it costs a furniture shop with two hundred silver in the till, and proportionally the same.
- **Taking a place off the books is free.** No fee and no notice. The colony there is still yours; it just stops being the branch's account.
- **A Backrooms coordinate can never be a site** - somewhere you go, not somewhere you keep.
- **Nothing here settles anything for you.** RimWorld already lets you found a second colony, and the mod's own portals already let a crew come out somewhere else. This is the paperwork, not the shovel.
- **A site you can no longer reach stops being billed**, and says so on its row rather than vanishing.

Full record: [a remote base is a costly responsibility](docs/implementation/REMOTE_SITES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - remote sites, arc 5's first piece (0.12.6-dev)

**Verbatim user quote:** *"go"*

**The arc this opens, verbatim from `CAMPAIGN_CONTENT_CATALOG.md`:** *"Remote sites need people, supplies, signals, protection, and an exit plan... A remote base is a costly responsibility rather than free map ownership."*

### What shipped

A branch can register a map it already holds as a remote site. Registration puts it inside `OwnsMap`, so connected work reaches it, a gate may anchor there and a way out may come up on it. It is billed daily at a quarter of the branch's own base overhead, as its own ledger line. Releasing is free.

### Files touched

`src/RimroomsAsyncIndustries/Company/RemoteSites.cs` (new), `UI/OperationsRemoteSites.cs` (new), `Company/RimroomsCampaignComponent.cs`, `Company/CampaignServices.cs`, `UI/MainTabWindow_Operations.cs`, `1.6/Languages/English/Keyed/RR_Operations.xml`, `docs/implementation/REMOTE_SITES_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and a tenth proof.

### Closure notes

- **The register found no outpost or multi-colony mod anywhere in the 295 rows.** Nothing to conflict with, and nothing to lean on. Every row in the four adjacent families is Optional or Configuration-only and none touches how a branch accounts for a place it holds.
- **Acquisition is the game's; recognition is ours.** RimWorld already lets a colony settle a second tile, and this mod's own topology already lets a crew come out of the Backrooms elsewhere. **Nothing here acquires anything**, and the proof bans `WorldObjectMaker.MakeWorldObject`, `GetOrGenerateMap`, `SettleInEmptyTileUtility` and `MapGenerator.GenerateMap` from the source.
- **The cost had to be a ratio.** Async Industries runs on $25,000 a day of overhead and the Store on $1,500; one absolute surcharge would be a rounding error for one and ruinous for the other. A quarter of base overhead per site means every start tunes it for free by tuning the number it already had.
- **A coordinate is never a site, and that is the distinction that made the naive version worthless** - my own, one checkpoint earlier. A surcharge alone would have computed **zero forever**, because `OwnsMap` covered the headquarters and transient open coordinates and nothing else. Refused in the service and again in the pane before the click.
- **One predicate, five features.** `OwnsMap` gained a third clause, and that single line is what *"people, supplies, signals, protection, and an exit plan"* means in this codebase. Thirty call sites across sixteen files consult it; extending one predicate rather than threading a second through all of them is the difference between a concept and a bolt-on. Placed **after** the coordinate check, and the order is asserted.
- **Releasing is free as a rule rather than as generosity.** Nothing in this mod has a deadline but the gate, and a release fee is a cost for changing your mind. The proof asserts the release path contains no transaction and no obligation.
- **Fault-planted four ways**, and the first is the one that mattered: removing the daily obligation silently restores free map ownership with no compiler error, no checker failure and no visible symptom.
- Build 0.12.6-dev, 172 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, ten proofs hold. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.5-dev**.', u'| Published | **0.12.6-dev**.'),
    (u'| Build | **170 C# files, 86 package files**, zero warnings, zero errors |',
     u'| Build | **172 C# files, 86 package files**, zero warnings, zero errors |'),
    (u'| Proofs | **nine** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **ten** in `.local/register/proof-*.py`, all holding.'),
    (u'## What shipped this session, 0.7.1 → 0.12.5',
     u'## What shipped this session, 0.7.1 → 0.12.6'),
    (u'| 0.12.5 | **The queue was in the wrong order** — tier 3 has no knobs to move; the chart authorises arcs 5–8 next. Four hollow unlocks not written |',
     u'| 0.12.5 | **The queue was in the wrong order** — tier 3 has no knobs to move; the chart authorises arcs 5–8 next. Four hollow unlocks not written |\n'
     u'| 0.12.6 | **A remote base is a costly responsibility** — arc 5 opens: sites on the books, billed daily, and a coordinate is never one |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

old_arc = u"""   - **Arc 5, "Build beyond headquarters".** *"Remote sites need people, supplies, signals,
     protection, and an exit plan... A remote base is a costly responsibility rather than free map
     ownership."* Its **first piece is a way to hold a remote site at all** — the surcharge that
     makes it costly follows, because today it would compute zero (`OwnsMap` returns true only for
     the headquarters and for transient open coordinates)."""
new_arc = u"""   - **Arc 5, "Build beyond headquarters".** *"Remote sites need people, supplies, signals,
     protection, and an exit plan... A remote base is a costly responsibility rather than free map
     ownership."* **The first piece shipped in 0.12.6-dev**: a branch registers a map it already
     holds, which puts it inside `OwnsMap` and on the daily bill. **Acquisition stays RimWorld's.**
     - **Still owed, and now all three are reachable because of that one predicate:** what a site
       needs to *be* one. **Staffing** it — a site with nobody at it is a line on a ledger.
       **Supplying** it — company-to-site logistics, where the procurement and cargo systems
       already exist and do not know about sites yet. **The exit plan** — the arc names it, and a
       gate may now anchor at a site, so this is where a second gate stops being theoretical.
     - **The chart also names** relay stations, caches, field shelters, guarded leases, resupply
       and evacuation missions. None is written."""
assert old_arc in s, 'arc 5 queue entry not found'
s = s.replace(old_arc, new_arc, 1)

marker = u'161. **Gate an opening requirement at the opening, never in the tick.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'162. **Acquisition is the game’s; recognition is ours.** RimWorld already settles a second '
     u'tile and this mod’s topology already emerges a crew elsewhere. A remote site is **registered, '
     u'never created** — `proof-remote-sites.py` bans `WorldObjectMaker.MakeWorldObject`, '
     u'`GetOrGenerateMap`, `SettleInEmptyTileUtility` and `MapGenerator.GenerateMap` from that '
     u'source. Inventing settling would be fighting Core for nothing and first to break on an update.\n'
     u'163. **A recurring cost must be a ratio of the branch’s own economy, never an absolute.** '
     u'Async runs on $25,000 a day of overhead and the Store on $1,500. One number is a rounding '
     u'error for one and ruinous for the other; a share of a number each start already tunes is '
     u'correct for both for free.\n'
     u'164. **A coordinate is never a base.** It is reached through a gate, it is transient, and it '
     u'is not the player’s to keep. A surcharge that counted coordinates computes zero and looks '
     u'like progress.\n'
     u'165. **Extend the one predicate, do not thread a second one.** `OwnsMap` has 30 call sites '
     u'across 16 files; its third clause is what makes work, gates and emergence anchors all reach '
     u'a registered site at once. Check that **every** consequence is wanted before widening it.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Owner directions recorded late, second pass', u"""
**Arc 5 opened (2026-09-29, 0.12.6-dev)**, the first work in the arcs the chart authorises at §7 step 8.

- [x] **A branch can hold a place beyond its headquarters, and it costs.** *"A remote base is a costly responsibility rather than free map ownership."* Registration puts a map inside `OwnsMap` - so connected work reaches it, a gate may anchor there and a way out may come up on it - and bills a quarter of the branch's own base overhead per live site, as its own ledger line. Releasing is free, because nothing in this mod has a deadline but the gate.
- [x] **Nothing here acquires a site.** RimWorld settles a second tile already, and the mod's topology already emerges a crew elsewhere. **Recognition, not acquisition**, and the proof bans the four Core calls that would cross that line.
- [x] **A Backrooms coordinate can never be registered.** This is what made the naive version - a surcharge with no registry - compute zero forever.
- [ ] **Still owed in arc 5, all three now reachable because of that predicate:** **staffing** a site, **supplying** it (company-to-site logistics; procurement and cargo exist and do not know about sites), and **the exit plan** (a gate may now anchor at a site, so a second gate stops being theoretical).
- [ ] **Also named by the chart and unwritten:** relay stations, caches, field shelters, guarded leases, resupply and evacuation missions.
""")
