# -*- coding: utf-8 -*-
"""Ledger for 0.12.7-dev: company-to-site logistics."""
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


insert_before('CHANGELOG.md', u'## 0.12.6-dev', u"""## 0.12.7-dev - 2026-09-29 - shipments can go to your sites

- **The corporation will now deliver to a site you have put on the books**, not only to headquarters. Pick any stockpile at any place the branch holds.
- **Stockpiles say where they are** once you hold more than one place, so two stockpiles both called "Stockpile" are never confusable.
- **You can reroute a shipment in flight to a different place**, and it arrives there.
- **A bug was fixed that would have swallowed shipments.** Rerouting an order updated which stockpile it was bound for but not which map, so the moment deliveries to sites became possible a cross-map reroute would have left the shipment paid for, held, and never arriving.
- **A shipment bound for a place that is not loaded now says so honestly** instead of blaming headquarters.
- **The supplier will not unload anywhere you have not accepted responsibility for** - headquarters or a registered site, and never a Backrooms coordinate.

Full record: [company-to-site logistics](docs/implementation/SITE_DELIVERIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - company-to-site logistics (0.12.7-dev)

**Verbatim user quote:** *"lets get to it"*

**The arc line this closes, verbatim from `CAMPAIGN_CONTENT_CATALOG.md`:** *"company-to-site logistics"*

### What shipped

Procurement may deliver to any place the branch has on the books. The destination is the receiving stockpile's own map, gated by a new `CanReceiveDeliveryAt` - headquarters or a live registered site, never a coordinate. In-flight orders may be rerouted across maps. The order menu offers stockpiles at every destination and names the place when the branch holds more than one.

### Files touched

`src/RimroomsAsyncIndustries/Company/RemoteSites.cs`, `Procurement/RimroomsProcurementComponent.cs`, `UI/OperationsProcurement.cs`, `1.6/Languages/English/Keyed/RR_Procurement.xml`, `docs/implementation/SITE_DELIVERIES_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and the sites proof.

### Closure notes

- **The design had anticipated this.** `ProcurementOrderRecord.receivingMap` already existed and **the delivery path already honoured it**; only the selection was pinned, in seven places. A widening rather than a rewrite, and its smallness is evidence the original design expected the far side to move.
- **A LATENT BUG, found by reading every write before changing what the record could hold.** The redirect path updated `receivingZone`, `receivingZoneId` and `receivingZoneLabel` and **never `receivingMap`**. Harmless while one map was legal; the moment a second was, a cross-map reroute would leave the order pointing at the old map and the delivery check would refuse it **on every attempt, for ever** - paid for, cargo held, never arriving. **A bug that only exists once you add the feature is the hardest kind to find, because it is not there while you are looking.** Same method as the frozen approach cell at 0.12.3, and what invariant 157 was written for.
- **A CLAIM OF MINE FAILED OPEN, for the second time today.** The on-the-books claim counted the refusal string; a planted fault replaced the guard with `if (false)` and **left the string sitting there unused**, so the count passed and the proof said nothing. **The plant that mattered most was the one the proof ignored.** Rewritten as three claims keyed off each guard expression, then re-planted and confirmed. This is invariant 152 written earlier the same day: the rule is not "fix it when caught", it is **check what your claim survives before believing it**.
- **Reachable, not merely permitted.** `HeadquartersStockpiles` listed only the headquarters', so widening the service alone would have left the feature unofferable. Stockpiles now say where they are, but **only when the branch holds more than one place** - otherwise every row would read "at headquarters", which is noise teaching nothing.
- Build 0.12.7-dev, 172 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, ten proofs hold, the sites proof fault-planted five ways. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.6-dev**.', u'| Published | **0.12.7-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.6',
     u'## What shipped this session, 0.7.1 → 0.12.7'),
    (u'| 0.12.6 | **A remote base is a costly responsibility** — arc 5 opens: sites on the books, billed daily, and a coordinate is never one |',
     u'| 0.12.6 | **A remote base is a costly responsibility** — arc 5 opens: sites on the books, billed daily, and a coordinate is never one |\n'
     u'| 0.12.7 | **Company-to-site logistics** — shipments reach a registered site; a latent cross-map reroute bug fixed before it could bite |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

old_still = u"""     - **Still owed, and now all three are reachable because of that one predicate:** what a site
       needs to *be* one. **Staffing** it — a site with nobody at it is a line on a ledger.
       **Supplying** it — company-to-site logistics, where the procurement and cargo systems
       already exist and do not know about sites yet. **The exit plan** — the arc names it, and a
       gate may now anchor at a site, so this is where a second gate stops being theoretical."""
new_still = u"""     - **Supplying it: DONE, 0.12.7-dev.** Procurement delivers to any place on the books, and a
       latent cross-map reroute bug was found and fixed before it could swallow a shipment.
     - **Still owed:** **staffing** a site — a site with nobody at it is a line on a ledger — and
       **the exit plan**, which the arc names and which a gate anchored at a site now makes
       possible rather than theoretical."""
assert old_still in s, 'still-owed block not found'
s = s.replace(old_still, new_still, 1)

marker = u'165. **Extend the one predicate, do not thread a second one.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'166. **A bug that only exists once you add the feature is the hardest kind to find, because '
     u'it is not there while you are looking.** The procurement redirect updated the receiving '
     u'zone and never the receiving map — harmless with one legal map, a shipment lost for ever '
     u'with two. **Read every WRITE to a record before changing what the record may hold.**\n'
     u'167. **Check what your claim survives before believing it.** The on-the-books claim counted '
     u'a refusal string; a planted fault removed the guard, left the string, and the proof passed. '
     u'**Key a claim off the thing that happens** — a guard expression, a refusal, an assignment — '
     u'never off a token near it. Second instance in one day (see 152).\n'
     u'168. **Permitted is not reachable.** Widening procurement without widening the stockpile '
     u'menu would have left site delivery legal and unofferable. Every widening needs its surface '
     u'widened in the same checkpoint.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Owner directions recorded late, second pass', u"""
**Arc 5 continued (2026-09-29, 0.12.7-dev): company-to-site logistics.**

- [x] **Procurement delivers to a registered site**, not only to headquarters. The destination is the receiving stockpile's own map, gated by `CanReceiveDeliveryAt` - headquarters or a live registered site, and **never a Backrooms coordinate**, which is excluded by construction because it can never be registered.
- [x] **A latent bug found and fixed.** The redirect path updated the receiving zone and **never the receiving map**. Harmless while one map was legal; with two, a cross-map reroute would have left a shipment paid for, held, and refused on every attempt for ever.
- [x] **The stockpile menu offers every destination**, and names the place only when the branch holds more than one - otherwise every row reads "at headquarters", which is noise.
- [x] **A proof claim of mine failed open and was fixed.** It counted a refusal string rather than asserting the guard, so a planted fault that disabled the guard still passed.
""")
