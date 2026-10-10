# -*- coding: utf-8 -*-
"""Ledger for 0.12.12-dev: the company stops naming things."""
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


insert_before('CHANGELOG.md', u'## 0.12.11-dev', u"""## 0.12.12-dev - 2026-09-29 - the company stops naming things

- **Work keeps coming after the tutorial.** Once you have answered the seventh request, clients start asking: a coordinate written up, material by the crate, instruments left running, somebody recovered, a door they can rely on. Five kinds of job, straight from the campaign plan's own list.
- **You are never offered a job you cannot do.** A request only appears if your branch has at least two genuinely different ways to finish it. What it then shows you is still every route, including ones you have not earned yet.
- **Progress on a generated job is counted from when it appeared.** "Deliver two hundred and fifty steel" means two hundred and fifty more, not "happen to have some in a stockpile".
- **Still no clock anywhere.** The next job turns up when you have finished or turned down the last one, and the company works through the range of what it wants rather than repeating the cheapest thing.
- **A job you already finished cannot be offered back to you as free money.** A request whose only route is research you have already completed is never put on the table.

Full record: [the company stops naming things](docs/implementation/REQUEST_GENERATION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the company stops naming things (0.12.12-dev)

**Verbatim owner decision:** *"Both - filter picks the family, card never shrinks"*

**The chart line this builds, verbatim from `CAMPAIGN_CHART.md` arc 4:** *"Clients request surveys, samples, instruments, rescue, secure access"*

### What shipped

Generation after the hinge: the eligibility filter, the generated offer routine, and **arc 4's five families - one per item the chart names, nothing invented.**

### Files touched

`src/RimroomsAsyncIndustries/Company/RequestGeneration.cs` (new), `Company/RequestLine.cs`, `Company/RequestRoutes.cs`, `1.6/Defs/RimroomsRequestDefs/RR_Requests.xml`, `1.6/Languages/English/Keyed/RR_Requests.xml`, `docs/implementation/REQUEST_GENERATION_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `proof-request-generation.py` (new, the seventeenth) and `proof-request-line.py` (retargeted).

### Closure notes

- **The owner's two answers operate at two levels and both stand.** Eligibility decides **which family is offered**; the card shows the **full authored floor, unfiltered**. `RequestRoutes.Available` is not modified, and planting a capability filter into it makes the new proof fail. **Nothing from 0.11.1-dev is reversed.**
- **GENERATION EXPOSED A FLAW IN WHAT SHIPPED THE SAME DAY.** 0.12.11-dev measured satisfaction as **absolute state**, which is permanently true once true. Right for a tutorial request asked once; **wrong for anything repeatable, where it would have paid out the instant the player accepted.** A generated request now records where each route stood when it appeared and asks for that much more; a tutorial request records nothing and keeps measuring absolutely. Keyed by label key rather than list index so a reordered def cannot shift every baseline onto the wrong route.
- **`proof-request-line.py` failed on the refactor and was retargeted, which is the proof working.** The per-kind switch moved from `RouteSatisfied` into `MeasureRoute`; a claim that survives its subject moving is a claim keyed off nothing.
- **Every clause of the filter can refuse**, and the proof asserts none of them is `return true` - invariant 136, which has already deleted four research projects and three tier-2 constants in this project. Purchase refuses before contact, Document refuses when the branch has been nowhere, Testify refuses with no living witness, Research refuses when short of the log tier.
- **A finished project is not reachable**, which is the payout button one level up: a Research route against completed work is satisfied on sight. Qualification is asked of `ProjectQualificationFailureKey`, the **same function the research screen uses**, so the filter can never disagree with it. `CatalogueCarries` was made internal and shared rather than copied.
- **No clock, and the proof looks for four of them by name.** The next request appears when the open one resolves. Variety is least-asked-first, tie-broken ordinally then by the branch's seed, so a save reloaded twice does not produce two different campaigns.
- **The check I would not have thought to write: every authored route must be able to FIRE.** A `logKind` typo is completely invisible - `TryLogKind` returns false, the measurement is zero, the route is permanently unsatisfiable, and it still counts toward the two-different-kinds rule, so `ConfigErrors` passes and the package checker passes while a request ships promising two ways through and having one. Invariant 49. The proof parses the XML and checks log kinds, project names, redirect targets and catalogue carriage.
- **Save integrity changed with it.** Generated def names are no longer unique, so what replaced that check is stricter about what matters: ids carry an instance number, a **tutorial** request may appear at most once, and a save may hold **at most one open request** - two would mean a guard was bypassed and two payouts are running.
- **Six planted faults, six catches, clean on restore**, including the owner decision reversed and the baseline ignored.
- Build 0.12.12-dev, **173 C# files (measured)**, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, **seventeen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

# ---------------------------------------------------------------- NOW.md
s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.11-dev**.', u'| Published | **0.12.12-dev**.'),
    (u'| Build | **172 C# files, 86 package files**', u'| Build | **173 C# files, 86 package files**'),
    (u'## What shipped this session, 0.7.1 → 0.12.11',
     u'## What shipped this session, 0.7.1 → 0.12.12'),
    (u'| 0.12.11 | **The corporation starts asking** — the mission line reaches a player. **The whole campaign had been authored and read by nothing** |',
     u'| 0.12.11 | **The corporation starts asking** — the mission line reaches a player. **The whole campaign had been authored and read by nothing** |\n'
     u'| 0.12.12 | **The company stops naming things** — generation after the hinge, a filter that can refuse, arc 4’s five families. Fixed 0.12.11’s absolute-state flaw |'),
    (u'| Proofs | **SIXTEEN** in `.local/register/proof-*.py`.',
     u'| Proofs | **SEVENTEEN** in `.local/register/proof-*.py`.'),
    (u'7b. **Every proof (SIXTEEN), by exit status:**', u'7b. **Every proof (SEVENTEEN), by exit status:**'),
    (u"   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-line`,\n"
     u"   `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`.",
     u"   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,\n"
     u"   `request-line`, `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`."),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:70]
    s = s.replace(old, new, 1)

old_item3 = u"""3. **Generated requests after the hinge.** **The surface shipped 0.12.11-dev** — requests now
   reach a player, are accepted, complete on any one route coming true, and pay. What is left is
   **generation**: the arc 4–8 request families, and the eligibility filter the owner decided on."""
new_item3 = u"""3. **Generated requests after the hinge. THE MACHINERY IS DONE, 0.12.12-dev.** The eligibility
   filter, the generated offer routine and **arc 4's five families** ship, and progress on a
   generated request is counted from when it appeared. **What is left is content:** the thirteen
   remaining families for arcs 5–8, against the same proved pattern —
   relay stations · caches · field shelters · guarded leases · resupply · evacuation · witnesses ·
   missing residents · public danger · heavy cargo · staff transfer · combined families ·
   one unfamiliar rule at a time.
   **Every new route must name a def that exists**, or it can never fire and nothing but
   `proof-request-generation.py` will say so."""
assert old_item3 in s, 'queue item 3 not found'
s = s.replace(old_item3, new_item3, 1)

marker = u'180. **Zero hard dependencies and Core-only are different claims.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'181. **Absolute state is permanently true once true.** A check like *"does the branch hold '
     u'twenty meals"* is right for a request asked **once** and wrong for anything repeatable, '
     u'where it pays out on acceptance. A repeatable job records where it started and asks for that '
     u'much **more** — keyed by label key, never by list index.\n'
     u'182. **A route naming something that does not exist can never fire, and nothing says so.** A '
     u'`logKind` typo makes the measurement zero while still counting toward the two-different-kinds '
     u'rule, so every checker passes and the request ships promising two ways and having one. '
     u'**Parse the content and assert each route names a real def.** Invariant 49.\n'
     u'183. **A filter clause that cannot refuse is a hollow knob.** Assert no arm of an '
     u'eligibility switch is `return true`. Invariant 136 has already deleted four projects and '
     u'three constants here for the same reason.\n'
     u'184. **A route against work already finished is satisfied on sight.** Exclude the completed '
     u'case at the point of offering, not only at the point of measuring — otherwise the offer '
     u'itself is a payout button.\n'
     u'185. **A proof failing because its subject MOVED is the proof working.** Retarget it and say '
     u'so. A claim that survives an arbitrary refactor of the thing it describes is keyed off '
     u'nothing.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Built 2026-09-29, 0.12.11-dev', u"""
**Built 2026-09-29, 0.12.12-dev: the company stops naming things.**

- [x] **Generation after the hinge.** The eligibility filter, the generated offer routine, and **arc 4's five families** - one per item `CAMPAIGN_CHART.md` arc 4 names, nothing invented.
- [x] **The owner's decision implemented at both levels.** *"Both - filter picks the family, card never shrinks."* Eligibility decides which family is offered; `RequestRoutes.Available` is untouched and still shows the full authored floor. Planting a filter into it fails the proof.
- [x] **Fixed a flaw in 0.12.11-dev, shipped the same day.** Satisfaction was **absolute state**, permanently true once true, so a repeatable request would have paid out on acceptance. A generated request now measures progress from when it appeared; a tutorial request still measures absolutely, because its lesson may already be learned.
- [x] **Every filter clause can refuse** - asserted, per invariant 136. A finished project is not reachable, and qualification reuses `ProjectQualificationFailureKey` rather than a second copy.
- [x] **No clock**, and the proof looks for four by name. Variety is least-asked-first, seeded and ordinal.
- [x] **Every authored route is asserted to be able to fire** - log kinds, project names, redirect targets, catalogue carriage. A `logKind` typo is otherwise completely invisible.
- [x] **Save integrity tightened**: a tutorial request at most once, and at most one open request in the whole save.
- [ ] **Next: the thirteen remaining generated families for arcs 5-8**, against the proved pattern.
""")
