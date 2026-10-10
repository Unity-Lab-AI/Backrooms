# -*- coding: utf-8 -*-
"""Ledger for 0.12.13-dev: arcs 5 to 8 have work in them."""
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


insert_before('CHANGELOG.md', u'## 0.12.12-dev', u"""## 0.12.13-dev - 2026-09-29 - arcs 5 to 8 have work in them

- **Thirteen more kinds of job**, one for every item the campaign plan names across the last four arcs: relay stations, caches, field shelters, guarded leases, resupply, evacuation, a town that saw something, residents who are missing, something loose where people live, cargo that does not fit through a door, people who know what they are looking at, a place that is two places at once, and one rule nobody has seen before.
- **Eighteen kinds of job in total** once you are past the tutorial, and the company works through the range of them rather than repeating the cheapest.
- **Every job offers the capability or the shortcut.** Do the work and own it, or pay to make the problem somebody else's. The company genuinely does not mind which, and would quietly rather you did the first.
- **Nothing new was added to the game to make this work** - no new items, no new art, no new sounds. It is written entirely out of things already there.

Full record: [arcs 5 to 8 have work in them](docs/implementation/ARCS_5_TO_8_REQUESTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - arcs 5 to 8 have work in them (0.12.13-dev)

**The chart lines this closes, verbatim from `CAMPAIGN_CHART.md`:** arc 5 *"Remote sites need people, supplies, signals, protection, and an exit plan"*; arc 6 *"Openings appear in towns. Witnesses, missing residents, public danger"*; arc 7 *"Heavy cargo and staff across the wider world"*; arc 8 *"Later coordinates combine known families, then introduce one unfamiliar rule at a time"*.

### What shipped

**Thirteen generated request families, one per item the chart names.** With arc 4's five from 0.12.12-dev that is **18 generated families across arcs 4-8** plus the seven fixed tutorial requests: **25 request defs**. Chart §7 step 8 is closed.

### Files touched

`1.6/Defs/RimroomsRequestDefs/RR_Requests.xml`, `1.6/Languages/English/Keyed/RR_Requests.xml`, `docs/implementation/ARCS_5_TO_8_REQUESTS_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and `proof-request-generation.py`. **No C# changed** - this is content against the pattern proved in 0.12.12-dev.

### Closure notes

- **ARC 5'S "STILL UNWRITTEN" LIST HAD REAL READ SITES ALL ALONG.** `NOW.md` has carried *"still unwritten: relay stations, caches, field shelters, guarded leases, and resupply and evacuation missions"* since 0.12.9-dev with the instruction to check each against a real read site first. Checked: **every one of them already had a research project** - `RR_Logistics_Relays`, `RR_Commerce_Leases`, `RR_Commerce_NegotiatedTerms`, `RR_Logistics_StandingOrders`, `RR_Fieldcraft_ReturnDrill` - shipped between 0.11.3 and 0.11.6. **The chart's arc-5 names and the research tree's branch names were describing the same things from two directions and nobody had connected them.**
- **Every route resolves against a def that exists**, which is the constraint that shaped all thirteen. A `Document` or `Testify` route with a mistyped log kind is **permanently unsatisfiable while still counting toward the two-different-kinds rule** - so `ConfigErrors` passes, the package checker passes, and the request ships promising two ways through and having one. Invariant 49 with teeth.
- **The proof counts per arc, not in total**, and that distinction is load-bearing: a total of eighteen is satisfied by eighteen copies of arc 4. Fault-planted exactly that way - **moving one arc 6 family into arc 4 leaves the total at eighteen and still fails**, because arc 6 drops to two.
- **Written entirely out of things that already exist.** Six catalogue-carried things, three log kinds, eleven of the twenty-five projects. **No new ThingDef, PawnKindDef, art or audio** - invariant 10 holds.
- **The company's character does the writing.** Chart §4.3: greed is the *mechanism* for the patience. So the first route is nearly always the capability the company would rather own, because it can sell that again, and the second is the expensive shortcut it will happily accept - buy the metal and neither party mentions it again, hand over the hardware and formally pass the problem on, pay enough silver that staffing becomes a competitor's problem. **Same greed producing both halves is what makes two routes read as one company talking rather than a menu.**
- Build 0.12.13-dev, **173 C# files (measured)**, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, **seventeen** proofs exit zero, the generation proof now carrying **48** claims. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.12-dev**.', u'| Published | **0.12.13-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.12',
     u'## What shipped this session, 0.7.1 → 0.12.13'),
    (u'| 0.12.12 | **The company stops naming things** — generation after the hinge, a filter that can refuse, arc 4’s five families. Fixed 0.12.11’s absolute-state flaw |',
     u'| 0.12.12 | **The company stops naming things** — generation after the hinge, a filter that can refuse, arc 4’s five families. Fixed 0.12.11’s absolute-state flaw |\n'
     u'| 0.12.13 | **Arcs 5 to 8 have work in them** — thirteen more families, one per item the chart names. **Chart §7 step 8 closed** |'),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:70]
    s = s.replace(old, new, 1)

old_item1 = u"""1. **Arcs 5–8.** **This is what `docs/CAMPAIGN_CHART.md` §7 step 8 authorises next**, and the
   chart beats any other document. Steps 6 and 7 are done."""
new_item1 = u"""1. ~~**Arcs 5–8.**~~ **CLOSED, 0.12.13-dev.** `docs/CAMPAIGN_CHART.md` §7 step 8 is done: every
   arc now has work a player can be asked to do. **18 generated families across arcs 4–8**, one per
   item the chart names, plus the seven fixed tutorial requests. Arc 5's *"still unwritten"* list
   turned out to have had real read sites since 0.11.6 — the chart's arc names and the research
   tree's branch names were describing the same things from two directions.
   **The systems each arc needs still have room to grow**; what is closed is that nothing in the
   chart's eight arcs is now unreachable content. Historical detail follows."""
assert old_item1 in s, 'queue item 1 not found'
s = s.replace(old_item1, new_item1, 1)

old_item3 = u"""   **What is left is content:** the thirteen
   remaining families for arcs 5–8, against the same proved pattern —
   relay stations · caches · field shelters · guarded leases · resupply · evacuation · witnesses ·
   missing residents · public danger · heavy cargo · staff transfer · combined families ·
   one unfamiliar rule at a time.
   **Every new route must name a def that exists**, or it can never fire and nothing but
   `proof-request-generation.py` will say so."""
new_item3 = u"""   **The thirteen remaining families shipped 0.12.13-dev**, so this
   item is closed too: 18 generated families across arcs 4–8, coverage asserted **per arc** because
   a total would be satisfied by eighteen copies of one arc.
   **Every new route must name a def that exists**, or it can never fire and nothing but
   `proof-request-generation.py` will say so."""
assert old_item3 in s, 'queue item 3 tail not found'
s = s.replace(old_item3, new_item3, 1)

marker = u'185. **A proof failing because its subject MOVED is the proof working.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'186. **Count coverage per category, never in total.** Eighteen generated families is '
     u'satisfied by eighteen copies of one arc. The claim that matters is that **each** arc has '
     u'somewhere to put work, and only a per-arc count catches a family moving between them.\n'
     u'187. **Two documents can describe the same thing from two directions and nobody notices.** '
     u'Arc 5’s *"still unwritten"* list — relay stations, caches, leases, resupply, evacuation — had '
     u'had research projects since 0.11.6. **Before building a named item, grep the def names for '
     u'its nouns.**\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

s = read('docs/TODO.md')
anchor = u'**Built 2026-09-29, 0.12.12-dev: the company stops naming things.**'
assert anchor in s, 'TODO anchor not found'
assert u'0.12.13-dev: arcs 5 to 8' not in s, 'already applied'
block = u"""**Built 2026-09-29, 0.12.13-dev: arcs 5 to 8 have work in them.**

- [x] **Thirteen generated request families, one per item `CAMPAIGN_CHART.md` names** across arcs 5, 6, 7 and 8. With arc 4's five that is **18 generated families**, plus the seven tutorial requests: **25 request defs**. **Chart §7 step 8 is closed.**
- [x] **Arc 5's "still unwritten" list is written**, and checking it against real read sites first found that **every item already had a research project** from 0.11.3-0.11.6. The chart's arc names and the research tree's branch names were describing the same things from two directions.
- [x] **Arc 6 "respond to openings in settlements" is built** - the witnesses, missing residents and public danger families. This also closes the prep item of the same name.
- [x] **Coverage is asserted per arc, not in total**, because eighteen families is satisfied by eighteen copies of arc 4. Fault-planted by moving one arc 6 family into arc 4: total unchanged, proof fails.
- [x] **No new ThingDef, PawnKindDef, art or audio** - 13 request defs, 26 routes, 52 keyed strings, all built from six catalogue-carried things, three log kinds and eleven existing projects.
"""
write('docs/TODO.md', s.replace(anchor, block + u'\n' + anchor, 1))
