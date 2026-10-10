# -*- coding: utf-8 -*-
"""Ledger for 0.12.4-dev."""
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


insert_before('CHANGELOG.md', u'## 0.12.3-dev', u"""## 0.12.4-dev - 2026-09-29 - four answers, and a research unlock that did nothing

- **A gate now needs real generators running before it will open**, not just a charged battery. You are told which is missing: the circuit cannot deliver enough, or there is no margin left above what the gate already draws.
- **A research unlock that changed nothing now works.** Reserve Discipline, the first Facilities project, promised the gate would need less spare power before opening. Nothing read that number. It does now.
- **The gate tells you how much of its reserve is held back for getting people home.** You used to see only the total.
- **A warning before you remove a natural way into the Backrooms.** Take it out and the access is gone; the space does not close and does not move, you just have no way back to it. Confirm and it goes; cancel and the order is dropped.
- **Machine gates you built get no such warning** - it is your machine, you can rebuild it.
- **The solo or group start has no mission list, on purpose.** Nobody is helping you because nobody knows you exist. Instead your people occasionally say what they are thinking - and none of it is an objective, nothing tracks whether you listened.
- **A designated gate still costs 250 W while closed.** Confirmed as intended rather than left as an open question.

Full record: [four answers, and a dead capability they uncovered](docs/implementation/FOUR_ANSWERS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - four answers (0.12.4-dev)

**Verbatim user quote:** *"okay yeah lets get to it all ask away then get to it"*

**Owner answers, verbatim:** *"we with minify i guess dont worry about it, can we at least do a rim style pop up warning ull lose valuable access to the backrooms and will have to find your own way back in"* / *"option three with hints like i need to contact someone about this crazy shit"* / *"A supply requirement before opening"* / *"Keep 250 W (Recommended)"*

### What shipped

All four answers, plus a real defect they uncovered: **`RR_Cap_ReserveDiscipline` promised an unlock and delivered nothing**, because the property it modified was read by no code at all.

### Files touched

`src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs`, `Gate/NativeGateBinding.cs`, `Portals/PortalDoorWarning.cs` (new), `Company/SoloGroupHints.cs` (new), `Company/RimroomsCampaignComponent.cs`, `Company/CampaignServices.cs`, keyed strings in `RR_Gate.xml` / `RR_NativeGate.xml` / `RR_Portals.xml` / `RR_Scenario.xml`, `docs/implementation/FOUR_ANSWERS_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and a ninth proof.

### Closure notes

- **A capability that promised an unlock and delivered nothing.** `MinimumPowerHeadroomWatts` applied `RR_Cap_ReserveDiscipline` and **was itself read by nothing**, so the tier 0 Facilities card promised *"the gate needs less spare headroom above its draw before it will open"* and changed nothing observable. **Invariant 136 exactly**, and exactly why `proof-research-branches.py` cannot catch it: the capability *was* read, and the reader was dead.
- **The sweep became a general proof.** `proof-live-effects.py` walks every public property on the gate comp whose body reads `GateProps` - fifteen of them - and insists each is consulted elsewhere. It found **two more**: `EmergencyReturnCostWattDays` and `RecoveryOpeningCostWattDays`, dead **accessors** rather than dead values. The totals were shown; how much of the total was the way home was not. Now it has its own line.
- **The supply check gates OPENING only**, never the tick. `NativeBindingFailureKey` is read every tick and a generation dip there would emergency-return a crew already across; the chart's rule is that a lapse blocks the next opening, never the current one. The proof asserts the absence.
- **Natural gates became informed consent rather than prohibition**, on the owner's own relaxation. Core decides destructibility at the def level and changing it would make every door in every colony indestructible for every mod. A laboratory gate gets no warning: warning about ordinary construction is how a player learns to click through warnings.
- **The solo/group start gets no request line, for honesty rather than difficulty.** Four hints, each once, none an objective, nothing tracking whether the player listened.
- **Two proof mistakes of my own.** The declaration scan matched nothing - a brace-nesting limit against a `{ get { ... } }` body - and so **passed every per-property claim by having none to check**, which is invariant 152 written this same session. And the hints built keyed strings at runtime; `check-keyed-strings.py` refused it and was right, because a constructed key cannot be verified in either direction.
- Build 0.12.4-dev, 170 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, nine proofs hold. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.3-dev**.', u'| Published | **0.12.4-dev**.'),
    (u'`826C21158ECB93979E2D89FEDBFB8FFC9EC4D825C439215F14A9B3A3D73AC46D`',
     u'`E62DF5326AC89E59E744E4AD10F054CA6674439AA7F73C34075DF1CF14AD2BE3`'),
    (u'| Proofs | **eight** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **nine** in `.local/register/proof-*.py`, all holding.'),
    (u'| Build | **168 C# files, 86 package files**, zero warnings, zero errors |',
     u'| Build | **170 C# files, 86 package files**, zero warnings, zero errors |'),
    (u'## What shipped this session, 0.7.1 → 0.12.3',
     u'## What shipped this session, 0.7.1 → 0.12.4'),
    (u'| 0.12.3 | **A portal is its own door cell** — a wall beside a gate no longer bricks it; eighth proof |',
     u'| 0.12.3 | **A portal is its own door cell** — a wall beside a gate no longer bricks it; eighth proof |\n'
     u'| 0.12.4 | **Four answers** — supply requirement, deconstruct warning, solo hints; **a tier 0 unlock that did nothing**, found by a new general sweep |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

# The natural-gate queue item is closed by the owner's relaxation.
start = s.index(u'1. **Natural gates that cannot be destroyed or moved.**')
end = s.index(u'2. **The solo/group tutorial line.**')
s = s[:start] + s[end:]
s = s.replace(u"""2. **The solo/group tutorial line.** *"the tutorial like quest chains should lay it all out"* —
   and *"this is all open eneded they can play how they choose"*, so it **guides without railing**.
   Requests have no per-start scoping yet: the six tutorial requests and the hinge are Async's
   unconditionally, so the request shape needs to know which start a line belongs to.
""", u"", 1)

marker = u'157. **Find every read site before changing a shared value.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'158. **Sweep the exposed surface, not the fields.** `MinimumPowerHeadroomWatts` applied a '
     u'research capability and **was itself read by nothing**, so the tier 0 Facilities unlock '
     u'promised a change and delivered none. `proof-live-effects.py` walks every public property '
     u'that reads `GateProps` and found two more. **A live read site is not a live effect** '
     u'(invariant 136); this is the sweep that catches it.\n'
     u'159. **A dead accessor and a dead value are different problems.** `EmergencyReturnCostWattDays` '
     u'was live as a field and dead as a property: the number reached the code and never reached the '
     u'player. The fix is to display it, not to wire it again.\n'
     u'160. **Never build a keyed string at runtime.** `"RR_Hint_" + id` cannot be verified in either '
     u'direction, so a typo ships as a raw key on screen. `check-keyed-strings.py` refuses it and is '
     u'right to.\n'
     u'161. **Gate an opening requirement at the opening, never in the tick.** '
     u'`NativeBindingFailureKey` is read every tick; a supply check there would emergency-return a '
     u'crew already across. A lapse blocks the **next** opening, never the current one.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# ---------------------------------------------------------------- TODO closures
s = read('docs/TODO.md')
for old, new in [
    (u'- [ ] **"needs to 100% have a exit to map natural portal on their first backrroms level"**',
     u'- [x] **"needs to 100% have a exit to map natural portal on their first backrroms level"** - SHIPPED 0.12.2-dev.'),
    (u'- [ ] **"with natural portals deeper to an extent"**',
     u'- [x] **"with natural portals deeper to an extent"** - SHIPPED 0.12.1-dev, through depth 3.'),
    (u'- [ ] **"till they would need to buidl theri own gate"**',
     u'- [x] **"till they would need to buidl theri own gate"** - SHIPPED 0.12.1-dev.'),
    (u'- [ ] **"natruals can not be destoryed or moved"**',
     u'- [x] **"natruals can not be destoryed or moved"** - **RELAXED by the owner and CLOSED 0.12.4-dev** as a confirmation warning rather than a prohibition.'),
    (u'- [ ] **"one can technically build a roomm directly on the other side of the portal door"**',
     u'- [x] **"one can technically build a roomm directly on the other side of the portal door"** - SHIPPED 0.12.3-dev.'),
    (u'- [ ] **"and it shouldnt interfere with the portal transition to the seeded backrooms"**',
     u'- [x] **"and it shouldnt interfere with the portal transition to the seeded backrooms"** - SHIPPED 0.12.3-dev. A real defect: the approach cell was frozen at registration.'),
    (u'- [ ] **"in the real world maps the portals dont extend into the real world environment"**',
     u'- [x] **"in the real world maps the portals dont extend into the real world environment"** - SHIPPED 0.12.3-dev, and asserted by `proof-portal-footprint.py`.'),
    (u'- [ ] **"Emerges on a fresh tile chosen by the seed"**',
     u'- [x] **"Emerges on a fresh tile chosen by the seed"** - **SUPERSEDED** by the owner at the exit-route fork: *"Two maps at start, coordinate is real"*. Shipped 0.12.2-dev.'),
    (u'- [ ] **"option three with hints like i need to contact someone about this crazy shit"**',
     u'- [x] **"option three with hints like i need to contact someone about this crazy shit"** - SHIPPED 0.12.4-dev. Four hints, each once, none an objective.'),
    (u'- [ ] **"A supply requirement before opening"**',
     u'- [x] **"A supply requirement before opening"** - SHIPPED 0.12.4-dev, and it revived a tier 0 capability that promised an unlock and delivered nothing.'),
    (u'- [ ] **"we with minify i guess dont worry about it, can we at least do a rim style pop up warning',
     u'- [x] **"we with minify i guess dont worry about it, can we at least do a rim style pop up warning'),
    (u'- [ ] **This deliberately RELAXES the earlier direction**',
     u'- [x] **This deliberately RELAXES the earlier direction**'),
    (u'- [ ] **What is asked for is a warning:**',
     u'- [x] **What is asked for is a warning:** SHIPPED 0.12.4-dev.'),
    (u'- [ ] **So the rule becomes informed consent rather than prohibition.**',
     u'- [x] **So the rule becomes informed consent rather than prohibition.**'),
    (u'- [ ] **Option three: no tutorial line at all until contact**',
     u'- [x] **Option three: no tutorial line at all until contact**'),
    (u'- [ ] **Plus hints, in the survivors’ own voice**',
     u'- [x] **Plus hints, in the survivors’ own voice**'),
    (u'- [ ] The gate **refuses to open unless its circuit can deliver this much power**',
     u'- [x] The gate **refuses to open unless its circuit can deliver this much power**'),
]:
    if old in s:
        s = s.replace(old, new, 1)
    else:
        print('  (skipped, not found: %s)' % old[:60])
write('docs/TODO.md', s)
