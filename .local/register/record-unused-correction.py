# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""

**Verbatim owner direction (2026-09-29), correcting three retirements:** *"then once you finalize that do the NOW.md write up procedures and prepare for the other side of compact and make sure shit isnt unused it was put there for a reason"*

- [x] **"make sure shit isnt unused it was put there for a reason"** - **HELD, and it reversed three decisions.** Over 0.11.4-dev and the start of 0.11.5-dev, three gate props found to be read by nothing were **retired**. That was the wrong call. A value nobody wired is **a job nobody finished**, not a value nobody wanted, and retiring it throws away the intention along with the dead code. All three were restored, and the rule is now an invariant.
  - [x] **`idlePowerDrawWatts` restored and WIRED.** A designated gate now draws it from its bound battery every tick while closed, scaled by footprint like the opening draw. Before this a designated gate cost **exactly nothing** to keep. It never drains below what an emergency return costs: that floor is the difference between a cost and a trap.
  - [x] **`returnReserveCapacityWattDays` restored and WIRED**, as the thing its name always read like - the **smallest reserve a gate will accept**, refused at the moment somebody chooses the battery rather than as a surprise at the threshold. A gate backed by a battery too small to come home on would look finished and strand the first crew through it.
  - [ ] **`reserveChargePowerWatts` restored, NOT yet wired - an owner question.** It is genuinely ambiguous and is **not** being guessed at. The reserve is a Core battery on the colony's power net, and **RimWorld already charges it**, so "the rate the gate charges its reserve" either duplicates Core or means something else. The candidates, none of them obviously right:
    - a **supply requirement** - the gate will not open unless its circuit can deliver this much, which largely duplicates `minimumPowerHeadroomWatts`;
    - a **display estimate** - "the reserve refills in about N hours at the rated charge", honest but only a readout;
    - a **real second charge path** - the gate pulls from the net into its own reserve at this rate, which would double-charge alongside Core unless it replaced Core's charging for that battery.
  - [x] **`docs/implementation/historical-content/0.11.4-dev/RETIRED_VESTIGIAL_POWER_PROPS.md` is now a dated record of a decision that was reversed**, and says so. It is not rewritten: it was true on the day, and the reversal is recorded here and in `FINALIZED.md`.

- [ ] **Open owner question, found while sweeping:** a designated gate drew **nothing** while closed until 0.11.5-dev. It now draws `idlePowerDrawWatts` (250 W, scaled by footprint). That is a **balance change on every existing save**, made because the direction above says an unused value is an unfinished job. If the intended behaviour was genuinely zero idle cost, this is the one to reverse.

"""

anchor = u'\n## Owner directions recorded late, second pass'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('correction recorded verbatim in TODO.md')
