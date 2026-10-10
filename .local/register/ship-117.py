# -*- coding: utf-8 -*-
"""CHANGELOG, FINALIZED, NOW and TODO for 0.11.7-dev."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def edit(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor not found' % rel
    write(rel, s.replace(old, new, 1))


# --------------------------------------------------------------------------- CHANGELOG
edit('CHANGELOG.md', u'# Changelog\n\n', u"""# Changelog

## 0.11.7-dev - 2026-09-29 - the corporation does not write off a branch

- **A clean-up team now arrives if your facility is wiped out.** Once you are in contact with the parent corporation, losing every last member of staff is no longer the end of the run.
- **They come in on all-access passes and clear the site of hostiles.** Removed, not killed - there is nobody left to haul forty corpses.
- **They bring a replacement crew of five**, one for each company role, and leave food, medicine, steel, components and wood. Enough to start again.
- **There is no limit on this and it never gets stingier.** The corporation is greedy, it is invested in you, and it will wait.
- **It will not fire while anybody is still alive** - including a crew that is standing inside the Backrooms when it happens. Staff who are merely unconscious are not replaced.
- **The Store and Solo/Group starts do not have this until they earn contact.** That absence is the point of those openings.
- **Five staff types that shipped with the mod but were used by nothing are now the replacement crew.** They were written for exactly this.

Full record: [the corporation does not write off a branch](docs/implementation/FACILITY_RELIEF_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

# --------------------------------------------------------------------------- FINALIZED
edit('docs/FINALIZED.md', u'\n## Inherited pre-workflow history', u"""
## Session 2026-09-29 - the clean-up team (0.11.7-dev)

**Verbatim user quote:** *"nicely done keep at it"*

**The direction this closes, verbatim:** *"the mega mother corp is greedy and will basic do anything and put up with anything to make sure you succssed to the point of sending clean up teams to your base with all access passses to wipe the facitly of all hostals and requisition a new basic team supplies drops like a fresh start of sorts so that facilities never die, this is liken the store and solo/group scenerios once they reach contact with the corporation"*

**And its scoping answer, verbatim:** *"clena up tema is only once u are in communication and working with the corporation"*

**And the storyteller fork decision, verbatim:** *"Both - guaranteed floor, storyteller flavour"*

### What shipped

The guaranteed-floor half. A branch in corporation contact that loses every living staff member gets a clean-up team: hostiles removed, five replacement staff requisitioned one per company role, and a basic supply drop. No cap, no escalation, and it refuses to fire while anybody is alive anywhere - including a crew standing inside a Backrooms coordinate.

### Files touched

`src/RimroomsAsyncIndustries/Company/FacilityRelief.cs` (new), `RimroomsCampaignComponent.cs`, `CampaignServices.cs`, `1.6/Languages/English/Keyed/RR_Requests.xml`, `docs/implementation/FACILITY_RELIEF_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and a fifth proof.

### Closure notes

- **Five `PawnKindDef`s were already written and read by nothing** - the whole `RR_*Staff` set, authored with skill ranges matching the five company roles exactly. Third instance this session of invariant 131. The queue called them "unbuilt"; they were **built and orphaned**, which is more dangerous, because an orphaned def looks finished from every angle except the one nobody checks.
- **Core facts read from the decompiled assembly, not remembered:** `GameEnder.gameEnding` is a public field, Core clears it whenever a map holds a free colonist, and the game-over countdown is 400 ticks. The relief is checked every 60. All three are now asserted against the live assembly.
- **Not routed through the hiring pipeline**, because that path's job is matching onboarding receipts and there is no charge here. Using it would have meant inventing a receipt.
- **A fifth proof**, fault-planted four ways and correct on every one.
- Build 0.11.7-dev, 163 C# files, 85 package files, **0 warnings, 0 errors**. Eight checkers pass. Assembly reproduced by two clean recompiles. **No game was launched.**

---
""")

# --------------------------------------------------------------------------- NOW
s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.11.6-dev**.', u'| Published | **0.11.7-dev**.'),
    (u'| Build | **162 C# files, 85 package files**, zero warnings, zero errors |',
     u'| Build | **163 C# files, 85 package files**, zero warnings, zero errors |'),
    (u'`018417AEA123B3894A44F9007535ACED27AC6FE09E972DFAFC3E29F427ADA71A`',
     u'`307D02D075BBBF4256FB019BF848E6705400D4F40EF79DA5E26EE11802BB2CCC`'),
    (u'| Proofs | **four** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **five** in `.local/register/proof-*.py`, all holding.'),
    (u'## What shipped this session, 0.7.1 → 0.11.6',
     u'## What shipped this session, 0.7.1 → 0.11.7'),
    (u'| 0.11.6 | **The second time you do a thing should be cheaper** — research tier 2; three planned unlocks deleted for changing nothing observable |',
     u'| 0.11.6 | **The second time you do a thing should be cheaper** — research tier 2; three planned unlocks deleted for changing nothing observable |\n'
     u'| 0.11.7 | **The corporation does not write off a branch** — the clean-up team; five `PawnKindDef`s found authored and read by nothing |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

# Queue: item 1 is done except its storyteller half, which becomes the new item 1.
start = s.index(u'1. **The clean-up team')
end = s.index(u'2. **Research tiers 3–4**')
s = s[:start] + u"""1. **The storyteller half of the owner's *"Both"* decision.** The guaranteed floor shipped in
   0.11.7; this is the other half. **This mod still has zero `IncidentDef`s**, so no storyteller
   knows it exists. Register lighter world-facing events as `IncidentDef`s with our own
   `IncidentWorker`s, gated in `CanFireNowSub`, and let the player's chosen storyteller pace them.
   The right home for arc 6, *"respond to openings in settlements"*. **Never a `StorytellerDef`** —
   it is an exclusive slot, it needs portrait art the no-new-art rule forbids, and there is no
   intelligence in one to borrow.
""" + s[end:]

# Invariants 139 and 140.
marker = u'138. **Check that a new tier does not switch off the tier below it.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'139. **An orphaned def is more dangerous than a missing one.** Five `RR_*Staff` '
     u'`PawnKindDef`s were authored, loaded and validated every run and read by **nothing**, and '
     u'the queue called them *"unbuilt"*. Built and orphaned looks finished from every angle '
     u'except the one nobody checks. **Third instance of invariant 131 this session.**\n'
     u'140. **A guarantee must not be an incident.** *"Facilities never die"* does not admit the '
     u'two questions a storyteller asks — whether, and when. The floor is deterministic; the '
     u'flavour is paced. Owner decision, verbatim: *"Both - guaranteed floor, storyteller '
     u'flavour"*.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# --------------------------------------------------------------------------- TODO
s = read('docs/TODO.md')
old = u'- [ ] **The clean-up team fires from our own component, deterministically**'
assert old in s
s = s.replace(old, u'- [x] **The clean-up team fires from our own component, deterministically** - SHIPPED in 0.11.7-dev. Record: `docs/implementation/FACILITY_RELIEF_IMPLEMENTATION.md`. It also wired **five `PawnKindDef`s that were authored and read by nothing**.', 1)
write('docs/TODO.md', s)
