# -*- coding: utf-8 -*-
"""Ledger for 0.12.29-dev: research tier 4."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def sub(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    write(rel, s.replace(old, new, 1))


sub('CHANGELOG.md', u'## 0.12.28-dev', u"""## 0.12.29-dev - 2026-09-29 - the top of the research ladder

- **Six new company projects, one for each branch that had somewhere left to go.**
  - **Practised Dialling** - bringing any gate up takes a fifth less work, on every route rather than only familiar ones.
  - **Decompression** - a crew shakes the place off twice as fast once they are out of it.
  - **Open Market** - the company stops underpaying you for ordinary salvage.
  - **Statement Discipline** - most of the branch can take a statement, not just your two most sociable staff.
  - **Surface Reading** - ways into the Backrooms turn up on your own maps noticeably more often.
  - **Steady Nerve** - the worst the place can weigh on somebody drops from severe to noticeable.
- **Two branches get nothing, on purpose.** Company logistics has already learned everything there is to learn about delivery, and the gate line's top project already stops the countdown entirely - there is nothing above a connection that does not end.
- **Nothing was invented to fill a gap.** Every one of the six moves a number that was already in the game and that nothing else was touching.

Full record: [six rungs, and two that could not exist](docs/implementation/RESEARCH_TIER_4_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.28-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - six rungs, and two that could not exist (0.12.29-dev)

**Verbatim user quote:** *"get it done"*

### What shipped

Research tier 4 - the top of the ladder - surveyed the way the row demanded rather than assumed.

### Files touched

`1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml`, `src/.../Gate/GateSpinUp.cs`, `src/.../Threats/BackroomsPressure.cs`, `src/.../Threats/BackroomsPressureComponent.cs`, `src/.../Company/ValuablesExchange.cs`, `src/.../Portals/NaturalFrontierService.cs`, `src/.../Company/EvidenceInterview.cs`, `src/.../UI/OperationsEvidence.cs`, `.local/register/proof-research-tier4.py` **new**, `.local/register/fault-plant-1229.py` **new**, `.local/register/proof-interview.py`, `docs/implementation/RESEARCH_TIER_4_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **SURVEYED, NOT ASSUMED, AND THE SURVEY SAID SIX NOT EIGHT.** The row said *"re-run the sweep, do not carry an old verdict"* and it was right: **0.12.5-dev deleted four tier 3 projects** because the systems their unlocks would have modified were not written, and tier 3 only became writeable at 0.12.18-dev because arc 5 had since built them. Six branches had a fifth unclaimed knob a player can name the effect of; two did not.
- **The six knobs, all previously unclaimed against all 28 existing capability read sites:** Facilities `dialSpinUpWorkRequired`, Fieldcraft `RecoveryRate`, Commerce `OrdinaryExchangeRate` 0.85 to 0.95, Measurement `MinimumInterviewerSocial` 4 to 2, Spatial `WorldFrontierRarity` 40 to 28, Entities `MaxPenalty` 10 to 6.
- **MEASUREMENT'S KNOB ONLY EXISTS BECAUSE OF THE PREVIOUS CHECKPOINT.** The interview shipped at 0.12.28-dev with a Social 4 floor, and a project that lowers a floor is observable. A day earlier there was nothing there to move.
- **LOGISTICS HAS NO TIER 4, AND THAT IS A FINDING.** Order capacity (tier 0), lead time (tier 1), dispatch delay (tier 2) and unattended delivery (tier 3) are all claimed. What remains is `MaximumOpenOrders` at 100, `MaximumPhysicalStacksPerOrder` at 4096 and `MaximumStacksDeliveredPerTick` at 4 - safety bounds no player will reach. **A fifth Logistics project would have been the fifth invented effect this project has caught.** The proof asserts both that it does not exist AND that the lower tiers still claim those four knobs, **so if a lower tier ever stops claiming one, the proof starts failing and Logistics gets its tier 4 after all.**
- **THE GATE LINE CANNOT HAVE A FIFTH RUNG.** Its fourth is already *"a connection that no longer counts down"* and `portalIndefiniteTier` is 4, which the ladder reaches. **There is nothing above indefinite.** The absence is the shape of the thing, not a gap in the work.
- **AN ABSENCE CANNOT BE SEEN BY READING**, which is why both are proof claims rather than comments. A reader opening the def file sees six tier-4 projects and has no way to tell whether the other two were considered and declined or simply forgotten.
- **Three restraints and one owner answer survived.** The per-coordinate frontier cap is still not a research knob, so Spatial took the **ordinary-map rarity** - a different number about a different place, with both frontier caps untouched: only *how often*, never *how many*. Shelter never reaches zero, so Entities took the **penalty ceiling** rather than the shelter rate a second time, and the new ceiling is 6 against a minimum of 1. Practised dialling discounts the **requirement, not the floor**, honouring the owner's condition that larger gates cost more to run. And `MaximumNaturalDepth` stays at 3 because the owner answered **"option 1"** on exactly that. Unprompted: **the odd exchange premium is untouched** - Commerce learns to stop being fleeced on scrap, not to make the Backrooms pay better.
- **A FALSE FINDING, CAUGHT BEFORE IT WAS WRITTEN.** My grep reported that three gate projects grant nothing - three hollow projects shipped, the exact defect invariant 136 exists for. I checked before asserting: the gate line drives `PortalWindowTier` by **counting completed projects by defName**, which the def file's own comment says. They are fully wired; **my grep looked for `grantsCapabilities` and `unlocks*` and the mechanism is neither.** **Fourth time this session my measurement was the defect rather than the code**, after the queue count, the assembly-hash grep and the keyed-string parser.
- **The existing `proof-research-branches.py` picked up all six new capabilities automatically** and verified each has a real read site - which is why the new proof concentrates on what that one cannot see.
- **Twenty-sixth proof, 40 claims, fault-planted eight ways and caught 8 of 8**, including a seventh Logistics project appearing and a fifth rung being added to the gate ladder.
- Build 0.12.29-dev, **176 C# files, 87 package files**, **0 warnings, 0 errors**, **38 projects** up from 32. Assembly `5AC7B632E73EF27710CE5EEE10311007B14579C62788353AF41C6F6619753E7A`, identical across two clean rebuilds. Ten checkers pass, **twenty-six** proofs exit zero. **No game was launched, so not one of these numbers has been watched changing.**

---

## Completed sessions""")

print('ledger written for 0.12.29-dev')
