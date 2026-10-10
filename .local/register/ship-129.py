# -*- coding: utf-8 -*-
"""Ledger for 0.12.9-dev: the exit plan."""
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


insert_before('CHANGELOG.md', u'## 0.12.8-dev', u"""## 0.12.9-dev - 2026-09-29 - the exit plan

- **You can build a gate at a site, not only at headquarters.** A second gate has stopped being theoretical.
- **A remote gate needs its own facility.** Its own comms console, its own bound battery and its own assembly bench, standing at that site. You cannot run a gate at the far end of the world off the equipment back home.
- **A way out of the Backrooms can already come up at a site too**, which came free from how ownership works rather than from a separate rule.
- **A Backrooms coordinate still cannot hold a company gate.** What is down there is a natural gate: no operator, no power, no address book, and not yours to build.
- **The refusal message stopped lying.** It used to say infrastructure had to be on the headquarters map, which is no longer true.

Full record: [the exit plan](docs/implementation/GATE_AT_A_SITE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the exit plan (0.12.9-dev)

**Verbatim user quote:** *"lets get it"*

**The arc line this closes, verbatim from `CAMPAIGN_CONTENT_CATALOG.md`:** *"Remote sites need people, supplies, signals, protection, and an exit plan"*

### What shipped

A gate may be designated at a registered site. **Arc 5's named list is now complete** - sites on the books (0.12.6), supplies (0.12.7), people (0.12.8), and an exit plan (this one).

### Files touched

`src/RimroomsAsyncIndustries/Company/RemoteSites.cs`, `Gate/NativeGateBinding.cs`, `1.6/Languages/English/Keyed/RR_NativeGate.xml`, `docs/implementation/GATE_AT_A_SITE_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and the sites proof.

### Closure notes

- **One line was the whole blocker.** `SameNativeHeadquartersThing` compared `parent.Map` against `campaign.Headquarters`, and **eleven call sites** inherited it - console, battery, assembly bench, kill switch, equipment links, console lookup. It now asks `campaign.OperatesAt(parent.Map)`. **The name is kept**: all eleven read it as *"the branch's own infrastructure, here"*, which is still exactly what it means; only the set of valid *heres* grew.
- **The clause I did NOT touch is the good part.** `thing.Map == parent.Map` survives, so a gate at a remote site needs **its own console, battery and bench at that site**. Widening the map test without touching it is what turns the arc's list into a build order: a site with a gate is a real facility or it is nothing. The proof asserts that clause explicitly, because deleting it would look like a simplification.
- **A coordinate still cannot host a company gate - by construction, not by a check.** `OperatesAt` admits the headquarters or a **registered** site, and a coordinate can never be registered. Invariant 12 holds without anybody remembering it. The proof asserts the place-set never mentions `RimroomsDestinationMapParent` at all.
- **Two questions, one place-set.** `OperatesAt` and `CanReceiveDeliveryAt` delegate to one private `IsBranchPlace`, and are **named apart on purpose**: a site could one day be too remote for a supplier and still fine to build a gate on. Shared implementation stops them drifting while they agree; separate names give the difference somewhere to go.
- **A way out at a site came free.** `OrdinaryBranchMap` already routes through `OwnsMap`, so 0.12.6's third clause delivered emergence anchors at sites with no line written here. **Second time the single-predicate decision has paid** - and why the proof checks each of the four consequences is still wanted.
- Build 0.12.9-dev, 172 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, eleven proofs hold, the sites proof fault-planted four more ways. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.8-dev**.', u'| Published | **0.12.9-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.8',
     u'## What shipped this session, 0.7.1 → 0.12.9'),
    (u'| 0.12.8 | **Remote sites need people** — a shipment to an empty site waits; the stranded-crew guarantee proved rather than rebuilt |',
     u'| 0.12.8 | **Remote sites need people** — a shipment to an empty site waits; the stranded-crew guarantee proved rather than rebuilt |\n'
     u'| 0.12.9 | **The exit plan** — a gate may stand at a registered site, with its own facility. Arc 5’s named list complete |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

old_still = u"""     - **Still owed: the exit plan.** A gate anchored at a registered site — which the ownership
       predicate now permits and nothing yet does. **This is where a second gate stops being
       theoretical.**"""
new_still = u"""     - **The exit plan: DONE, 0.12.9-dev.** A gate may be designated at a registered site, and it
       needs **its own console, battery and assembly bench there** — a site with a gate is a real
       facility or it is nothing. A way out may come up at a site too, which came free from the
       ownership predicate.
     - **Arc 5's named list is complete**: people, supplies, signals, protection, exit plan.
     - **Still unwritten from the chart:** relay stations, caches, field shelters, guarded leases,
       and resupply and evacuation missions. **Check each against a real read site before
       building** — invariant 136, which deleted four tier 3 projects at 0.12.5."""
assert old_still in s, 'still-owed block not found'
s = s.replace(old_still, new_still, 1)

marker = u'171. **Gate a requirement where it bites, not where it is convenient.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'172. **A gate runs on the equipment beside it.** `thing.Map == parent.Map` is what makes a '
     u'remote gate a real facility rather than a remote control for the headquarters. Widening '
     u'*where* a gate may stand must never widen *what it may draw on*.\n'
     u'173. **Exclude by construction, not by a check somebody must remember.** A designated gate '
     u'cannot appear in a coordinate because `OperatesAt` admits only registered places and a '
     u'coordinate can never be registered. Invariant 12 then holds with nothing to forget.\n'
     u'174. **Two questions may share a place-set and must not share a name.** `OperatesAt` and '
     u'`CanReceiveDeliveryAt` agree today and are different questions; one implementation stops '
     u'them drifting, two names give the difference somewhere to go when it arrives.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Owner directions recorded late, second pass', u"""
**Arc 5 completed (2026-09-29, 0.12.9-dev): the exit plan.**

- [x] **A gate may be designated at a registered site.** `SameNativeHeadquartersThing` compared `parent.Map` against `campaign.Headquarters` and **eleven call sites** inherited it, so the exit plan was unreachable however many sites a branch held. It now asks `OperatesAt`.
- [x] **A remote gate needs its own facility at that site** - console, bound battery, assembly bench. The `thing.Map == parent.Map` clause was deliberately left alone, and it is what makes a site with a gate a real facility rather than a remote control for headquarters.
- [x] **A coordinate still cannot host a company gate**, by construction: `OperatesAt` admits only registered places and a coordinate can never be registered.
- [x] **A way out may come up at a site**, which came free from the ownership predicate rather than from a new rule.
- [x] **Arc 5's named list is complete:** people, supplies, signals, protection, exit plan.
- [ ] **Still unwritten from the chart for arc 5:** relay stations, caches, field shelters, guarded leases, resupply and evacuation missions. Check each against a real read site before building.
""")
