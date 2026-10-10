# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.78-dev, written after staging and before the cascade."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: handoff-1278.py <assembly sha256 read back from the game folder>")
    raise SystemExit(1)

HANDOFF = u"""## STATE AT THIS HANDOFF — `0.12.78-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.78-dev  92 files
assembly    __HASH__
            read back out of the game folder after staging, not from the build
package     294 dependencies - 2 record books in the lab start - the east door
            RR_PortalTravel_DoorLocked and RR_BookDrop_Title both present
battery     16 checkers - 49 proofs - 21 plant suites - 771 anchors
            new suite: 12 of 12
tree        no planted fault, porcelain 0
```

**Refresh local mods in RimSort before launching.**

### THE BRIDGE WAS WORKING. READ THIS BEFORE CLAIMING IT IS NOT

Owner: *"the api mod is not working make it work"*. **It was running the whole time.** Two lines
are printed in `Player.log` on every launch:

```
[RimBridge] GABP server running standalone on port 5174
[RimBridge] Bridge token: <token>
```

**Read the log for the port and the token.** GABP is a framed protocol, not HTTP — four wrong
ports were probed with `curl` before the log was read. `tools/qa/rimbridge_readonly.py` already
speaks it:

```
python tools/qa/rimbridge_readonly.py --pid <PID> --log "<Player.log>" \\
  --output .local/qa/live/<new>.json --connect --select ping --select messages --select selection
```

`--connect` requires `--select ping`. Every output path must be **new**; it never overwrites.

**What was genuinely missing is what the owner asked for**: the allowlist had five selectors and
**none read a message**, so *"look at those messages"* was unanswerable. Added, all read-only:
`messages`, `alerts`, `letters`, `selection`, `colonists`, `camera`, `maps`, and `--rect` for a
bounded `get_cells_info`.

### THE SELECTION READ IS THE HIGHEST-VALUE ONE

`--select selection` returns the inspect string of whatever the owner has clicked. One call
answered a whole session's worth of guessing:

```
Door locked
Grid excess: 1185 W (533 Wd stored)
Linked battery charge: 533.13/2400.00 watt-days
Charge needed for normal window plus emergency return: 49.59 watt-days
Opening time: 7075 in-game minutes remaining | Status: Normal
```

**Ask for the selection before reasoning about a refusal.**

### TWO PUBLISHED CLAIMS WERE WRONG, AND BOTH WERE THE SAME MISTAKE

| Claimed to the owner | True |
|---|---|
| *"you hand-laid ~100 conduits; the start wires almost nothing"* | **17 RUNS were compared to 191 CELLS.** Expanded the runs are **205**; live is 191 + 14 hidden = **205**. Exact match, none added |
| *"you added 10 shelves"* | a shelf is **1x2**. 19 live vs 28 authored — **nine removed** |

**Never compare a count to a cell count without reading the footprint.** `<size>` is in Core's own
defs and `tools/check-start-layout.py` already reads 975 of them. The grave footprint was caught
this way the same day; this was the second instance and it reached the owner.

### WHAT THE OWNER'S FACILITY ACTUALLY LOOKS LIKE

Origin solved at **(120, 120)** from three single-instance devices. Scan with
`.local/qa/scan-facility.py <PID>` — **16x16 tiles, because 32x32 truncates** and two runs
disagreed about what the facility contained before that was found.

**Exactly as authored:** conduits, ballistic glass, generators, machining table, smithy, research
benches, glow pods. **Nothing was moved**, including the console and bench repositioned at
0.12.74-dev. Every delta is **fewer** — furniture deconstructed.

**One door added, at relative (51, 24)**, the compound's east perimeter wall at the dead end of the
service corridor. **No authored door was missing.** Authored now.

### THE TWO DEFECTS THE OWNER HIT IN PLAY

**A locked door refused in silence.** `OrderCrossing` validated the **approach cell** — on the
near side — and never asked whether the door would open. Now `DoorBlockerKey`, through Core's
`public virtual Building_Door.PawnCanOpen`, so the owner's `DoorsExpanded.Building_DoorRemote`
answers for itself and **nothing names that mod**. Register row 77's own disposition.

**No start shipped the record book every dispatch requires.** Laboratory: 112 fixtures, 17 types,
**zero books**. Store: 27, zero. Solo: nothing at all. The recorder folded into the book at
0.12.24-dev and **the stock was never updated**, so the first dispatch refused on every fresh
start, forever. The laboratory carries **two** now, and `RecordBookDelivery` sends two to any
branch with a calibrated gate and **no book anywhere it can reach** — which is what stops it being
a tap.

### A PROOF WITH NO PLANT SUITE IS A PROOF NOBODY HAS CHECKED

`proof-corporate-contact.py` is one of the oldest in the battery and **had never been planted
against** — the same shape as the defect beside it. Suite **twenty-one**, 12 of 12.

**Check for a suite before trusting a proof:**
`grep -l <proof-name> .local/register/plant-*.py`

And the new claims caught two of their own defects: a door claim asserting the **call** and not the
**act** (twelfth machinery-not-behaviour), and a plant testing a mod name in a **comment the proof
strips**.

"""
HANDOFF = HANDOFF.replace(u"__HASH__", HASH)

EDITS = [
    (u"| Published | **0.12.77-dev**.", u"| Published | **0.12.78-dev**."),
    (u"SHA-256 `5E87D3842B559E8ABCF44654D2178923D39D8EBE2A7D9F9D36A4FCAB441E39CC`",
     u"SHA-256 `" + HASH + u"`"),
    (u"## STATE AT THIS HANDOFF — `0.12.77-dev`, STAGED AND VERIFIED",
     HANDOFF + u"## STATE AT THIS HANDOFF — `0.12.77-dev`, STAGED AND VERIFIED"),
]

now = io.open(NOW, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)

after = io.open(NOW, encoding="utf-8").read()
failures = []
if u"## STATE AT THIS HANDOFF — `0.12.78-dev`, STAGED AND VERIFIED" not in after:
    failures.append("the handoff block is missing")
if HASH not in after:
    failures.append("the staged hash is not recorded")
if u"port 5174" not in after:
    failures.append("the bridge port is not written down")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("NOW.md leads with 0.12.78-dev, staged and verified")
