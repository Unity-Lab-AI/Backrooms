# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.77-dev."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: handoff-1277.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

HANDOFF = u"""## STATE AT THIS HANDOFF — `0.12.77-dev`, BUILT AND NOT YET STAGED

```
built       Rimrooms.AsyncIndustries  0.12.77-dev  92 files
assembly    __HASH__
            measured after the version bump, reproduced by two clean rebuilds
battery     16 checkers - 49 proofs - 20 plant suites - 752 anchors
            new suite: 12 of 12
tree        no planted fault, porcelain 0
```

### ⚠ STAGING IS PENDING AND THAT IS THE FIRST THING TO DO

`tools/stage-mod.ps1` **refused**: *"Close RimWorld before staging a new DLL."* The owner had the
game open. **The owner's fix is in this build and not in their game folder yet.** Re-run staging
once RimWorld is closed:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

Then read the hash back out of the game folder and confirm it matches the line above.

### ONE BATTERY WAS THE WHOLE RESERVE

Owner, from a running game: *"looks like only being able to connect 1 battery isnt anough and
there should be no loimit"*, and *"which i think is a power porblem"*. **Both halves were right.**

`nativeBattery` is the **anchor** that identifies the gate's circuit. `NativeGenerationWatts` has
always summed the whole net and `NativePowerConnected` has always checked it — **stored energy was
the one reading that never followed.** And the spend was worse: `TrySpendNativeEnergy` refused
outright when the anchor alone could not cover a cost, so **a drained anchor stalled a gate with
ten full batteries beside it on the same net.**

Fixed through Core: `PowerNet.CurrentStoredEnergy()` for the sum (EMP-aware for free), and the draw
**copied from `ChangeStoredEnergy`**, which does exactly this and is private.

**The anchor is still required.** Removing the limit is not removing the binding.

### AND THE REFUSAL NAMED THE WRONG THING, WHICH COST THE OWNER THE SESSION

`HasUsablePortalWindow` collapsed **seven** conditions into one bool, and the player read *"The
laboratory connection for that address is not open."* **A flat battery reported an address fault.**

`PortalWindowBlockerKey` is the third blocker key after `CalibrationBlockerKey` and
`StaffConsoleBlockerKey`, both added for the same reason. **`HasUsablePortalWindow` delegates to
it**, so the predicate and the message cannot disagree.

**Nothing in forty-eight proofs had ever claimed anything about the energy a gate runs on.** That
is why this reached play.

### THE READER-FACING LIST WAS MOSTLY NOT READER-FACING

Owner: *"public facing docs ... have no in house dev names and no todo numbering and no actual work
information"*, and *"ARE NOT to be text walls get to each point in as short a way as possible"*.

`READER_FACING` held thirteen entries and **most were never reader documents** — `HOWTO.md` opens
*"the practical guide for anyone (human or build agent) opening this repository"*; `SCENARIOS.md`
calls itself a *"design contract"*. Holding a dev document to a reader's vocabulary made it look
supervised while nothing was going to notice it was the wrong **kind** of document.

**`docs/wiki/` is thirteen pages and nothing else**, served by `docs/_config.yml`. The wall limit
is **360**, down from 700; the wiki tops out at **307**, so the limit is a floor under a standard
already met. Workshop links are authored as **clearly-marked placeholders** — nothing claims a page
that does not exist.

### A RULE NOW CATCHES THE DOCUMENTS THAT LIE ABOUT DEPENDENCIES

Yesterday's decision made *"Core only"* false in **twenty-six living documents**. The count is read
from `About.xml`, never typed, so **if the owner reverses the decision the rule stops firing on its
own.** D3 and D4 are recorded as changed in `GATE_0_DECISIONS.md`, following D1's own pattern.

**The verbatim ledger is exempt and the reason is a LAW.** `TODO.md`, `NOW.md`, `ROADMAP.md` and
the master backlog hold twenty-nine of the seventy-two matches, and **LAW #0 forbids altering the
owner's recorded words.**

### THE PLANTS CAUGHT FIVE CONSEQUENCES OF THIS SESSION'S OWN WORK

* **three went MISSED** because `PLAYING.md` left the supervised set — the one thing a
  reader-facing rule set loses silently. Re-aimed at the wiki,
* **one was only passing because of a bug**: it planted a stat base **inside an XML comment**, and
  that checker strips comments now. **A plant that tests a bug instead of a rule goes green while
  the rule is unguarded.**
* **one claim was the duplicate-string trap, third instance in one session** —
  `List<CompPowerBattery> batteries = net.batteryComps;` appears twice, so gutting the capacity
  reader left the claim true. **Count, never test presence.**

And the new dependency rule **reported wrong line numbers on its first run**, enumerating stripped
text while reporting file positions. **A finding with the wrong address is worse than no finding.**

"""
HANDOFF = HANDOFF.replace(u"__HASH__", HASH)

EDITS = [
    (u"| Published | **0.12.76-dev**.", u"| Published | **0.12.77-dev**."),
    (u"SHA-256 `B3B0B052445A706CF8A1F1BED154C9CA813B756AA019F773B7C26EE2225F6774`",
     u"SHA-256 `" + HASH + u"`"),
    (u"## STATE AT THIS HANDOFF — `0.12.76-dev`, STAGED AND VERIFIED",
     HANDOFF + u"## STATE AT THIS HANDOFF — `0.12.76-dev`, STAGED AND VERIFIED"),
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
if u"## STATE AT THIS HANDOFF — `0.12.77-dev`, BUILT AND NOT YET STAGED" not in after:
    failures.append("the handoff block is missing")
if HASH not in after:
    failures.append("the hash is not recorded")
if u"STAGING IS PENDING" not in after:
    failures.append("the pending stage is not flagged as the first thing to do")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("NOW.md leads with 0.12.77-dev and flags the pending stage")
