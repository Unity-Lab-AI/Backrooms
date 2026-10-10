# -*- coding: utf-8 -*-
"""Ledger updates for 0.11.6-dev: FINALIZED, NOW, TODO."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


# --------------------------------------------------------------------------- FINALIZED
s = read('docs/FINALIZED.md')
entry = u"""
## Session 2026-09-29 - research tier 2, and the storyteller question (0.11.6-dev)

**Verbatim user quote:** *"read now.md to continue the work guided by the prep docs and mod register and worrkflow docs to make an all encompassing mod(You do know how to properly make rimworld mods right for 1.6?) should of asked that before now, get to work!"*

**Verbatim user quote, mid-turn:** *"we may need our own story teller right? or is that way way to much work? with the “AI” like ai thats not an ai that the storytellers use"*

**Verbatim user decision at that fork:** *"Both - guaranteed floor, storyteller flavour"*

### What shipped

Research tier 2: seven `RimroomsProjectDef`, one per branch, each requiring its tier 1 sibling and a completed distortion log. Standby Discipline, Relief Watch, Reference Standards, Known Address, Containment Protocol, Forward Dispatch, Specialist Recruitment. **Every one moves a knob no other project touches**, so nothing in this band supersedes anything and no card has to explain another.

### Files touched

`Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml`, `src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs`, `src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs`, `src/RimroomsAsyncIndustries/Gate/GateSpinUp.cs`, `src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs`, `src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementComponent.cs`, `src/RimroomsAsyncIndustries/Personnel/RimroomsPersonnelComponent.cs`, `docs/implementation/RESEARCH_TIER2_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj.

### Closure notes

- **Three of the seven knobs the previous handoff called "already identified" were verified hollow and replaced.** `stablePowerTicksRequired` is one second; `MaximumOpenOrders` is a sanity cap of 100; catalogue `maxOrderQuantity` is already up to a million. **All three would have passed `proof-research-branches.py`**, because the capability would have been read by real code - it would simply have moved a number no player could observe. A live read site is not a live effect.
- **`Forward Dispatch` would have switched `Relays` off** had the lead-time clamp kept reading the raw dispatch delay. A tier 2 project silently disabling its own tier 1 prerequisite, reported by nothing.
- **Idle draw is read in two places** - what the gate reports and what it spends - and the capability now lives in one property both call, so the readout can never lie about the drain.
- **No custom storyteller**, and the reasoning is recorded in `TODO.md`: a `StorytellerDef` is an exclusive slot, it needs portrait art the no-new-art rule forbids, and there is no intelligence in one to borrow. The owner's decision is both a guaranteed floor in our own component and an `IncidentDef` surface for the player's chosen storyteller.
- Build 0.11.6-dev, 162 C# files, 85 package files, **0 warnings, 0 errors**. Eight checkers pass; `check-doc-conformance.py` caught a stale README version and it was fixed. Four proofs hold, and `proof-research-branches.py` was **fault-planted in both directions** and failed correctly both times before being restored.
- **No game was launched.**

---
"""
anchor = u'\n## Inherited pre-workflow history'
assert anchor in s
s = s.replace(anchor, entry + anchor, 1)
write('docs/FINALIZED.md', s)

# --------------------------------------------------------------------------- NOW.md
s = read('docs/NOW.md')

pairs = [
    (u'| Published | **0.11.5-dev**.', u'| Published | **0.11.6-dev**.'),
    (u'| 0.11.5 | **A designated gate is a machine that is on** — three unused props restored, two wired. **Reversed 0.11.4’s retirements.** |',
     u'| 0.11.5 | **A designated gate is a machine that is on** — three unused props restored, two wired. **Reversed 0.11.4’s retirements.** |\n'
     u'| 0.11.6 | **The second time you do a thing should be cheaper** — research tier 2; three planned unlocks deleted for changing nothing observable |'),
    (u'## What shipped this session, 0.7.1 → 0.11.5', u'## What shipped this session, 0.7.1 → 0.11.6'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

# The queue: tier 2 is done, so item 1 goes and the clean-up team carries the owner's decision.
start = s.index(u'1. **Research tier 2**')
end = s.index(u'3. **The Store and Solo/Group starts.**')
replacement = u"""1. **The clean-up team — *"so that facilities never die"*.** The state it keys on **already
   exists**: `campaign.CorporationContact`, one-way, set from `beginsInCorporationContact`. Async
   Industries begins true; the Store and Solo/Group begin false and must earn it. On collapse the
   corporation sends a team with all-access passes, clears every hostile, requisitions a fresh
   basic team and drops supplies. **A no-fail floor, chosen deliberately by the owner.**

   **Owner decision at the storyteller fork, 2026-09-29, verbatim: *"Both - guaranteed floor,
   storyteller flavour"*.** So this is built twice over:
   - **The rescue fires from our own `GameComponent`, deterministically.** A promise that says
     *"facilities never die"* must never be at the mercy of a dice roll.
   - **Lighter world-facing events register as `IncidentDef`s with our own `IncidentWorker`s**, so
     the player's chosen storyteller paces them. **This mod currently has zero `IncidentDef`s**,
     which means no storyteller knows it exists. It is also the right home for arc 6,
     *"respond to openings in settlements"*.
   - **No custom `StorytellerDef`, ever.** It is an exclusive slot the player would have to give
     up Cassandra or Randy for, it needs portrait art the no-new-art rule forbids, and there is no
     intelligence in one to borrow — a `StorytellerComp` rolls a mean-time-between against wealth
     and population. The part that feels like a director is `IncidentWorker.CanFireNowSub`, and
     that is ours without owning the slot.
2. **Research tiers 3–4** — remote and deep operations.
"""
s = s[:start] + replacement + s[end:]

# Renumber nothing else; the list below keeps its own numbers and the order still reads.
s = s.replace(u'4. **Research tiers 3–4** — remote and deep operations.\n', u'', 1)

# Invariant 136.
old_inv = u'135. **A reversed dated record is annotated, never rewritten.**'
idx = s.index(old_inv)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'136. **A live read site is not a live effect.** Three tier 2 unlocks were deleted before '
     u'being written because the knobs they moved were a one-second wait, a cap of 100 orders and '
     u'a quantity limit already set to a million. **All three would have passed '
     u'`proof-research-branches.py`**, because the capability would have been read by real code. '
     u'Open the file, find the value, and ask what a player would observe.\n'
     u'137. **A number displayed and a number spent must come from one place.** Idle draw is read '
     u'by the gate’s readout and by the tick that drains the reserve; research applied to one and '
     u'not the other would make the readout lie, silently, because nothing compares them.\n'
     u'138. **Check that a new tier does not switch off the tier below it.** Forward Dispatch '
     u'halves the dispatch delay, and the lead-time clamp had to be moved onto the effective value '
     u'or Relays would have stopped biting for exactly the branches holding both.\n' +
     s[line_end + 1:])

write('docs/NOW.md', s)

# --------------------------------------------------------------------------- TODO
s = read('docs/TODO.md')
s = s.replace(
    u'- [~] **"get to work!"** - research tier 2, seven projects, one per branch.',
    u'- [x] **"get to work!"** - research tier 2 SHIPPED in 0.11.6-dev: seven projects, one per '
    u'branch, each requiring its tier 1 sibling and a completed distortion log. Record: '
    u'`docs/implementation/RESEARCH_TIER2_IMPLEMENTATION.md`.', 1)
write('docs/TODO.md', s)
