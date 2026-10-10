# -*- coding: utf-8 -*-
"""NOW.md for 0.12.35-dev. Every number re-measured, and the next task replaced."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, "anchor missing: %r" % old[:90]
    assert s.count(old) == 1, "anchor not unique: %r" % old[:90]
    s = s.replace(old, new, 1)


sub(u"| Published | **0.12.34-dev**.", u"| Published | **0.12.35-dev**.")
sub(u"| Build | **182 C# files, 87 package files**", u"| Build | **186 C# files, 87 package files**")
sub(u"SHA-256 `5731D2E470D7B196DA671EBD81CFD8F002FC38A0235081FB21536C50EFB01FBD`",
    u"SHA-256 `F4252E3F04A178EB6B2FCB3C0D8C2B5D1A8114883404C46088278D9FA0B6892D`")
sub(u"| Proofs | **THIRTY-ONE** in `.local/register/proof-*.py`.",
    u"| Proofs | **THIRTY-TWO** in `.local/register/proof-*.py`.")
sub(u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.34-dev**.",
    u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.35-dev**.")
sub(u"## What shipped this session, 0.7.1 → 0.12.34",
    u"## What shipped this session, 0.7.1 → 0.12.35")

# ------------------------------------------------------------------ the item count
sub(u"**20 genuine build items**, counted at 0.12.34-dev, listed in full under **What is left** below.",
    u"**19 genuine build items**, counted at 0.12.35-dev, listed in full under **What is left** below.")
sub(u"""**20 genuine build items**, counted rather than estimated: `sed -n '/^## What is left, in order/,/^### Cannot close/p' docs/NOW.md | grep -cE '^[0-9]+\\. \\*\\*'`. Two closed this checkpoint. Anything marked closed below stays as a record so nobody rebuilds it.""",
    u"""**19 genuine build items**, counted rather than estimated: `sed -n '/^## What is left, in order/,/^### Cannot close/p' docs/NOW.md | grep -cE '^[0-9]+\\. \\*\\*'`. Anything marked closed below stays as a record so nobody rebuilds it.""")

# ------------------------------------------------------------------ replace DO THIS FIRST
start = s.index(u"## DO THIS FIRST — containment, quarantine and the alarm")
end = s.index(u"## What shipped this session, 0.7.1 →")
sub(s[start:end], u"""## DO THIS FIRST — staff debrief and quarantine, the last two halves of row 761

Three of row 761's five remaining halves shipped at 0.12.35-dev: containment rooms, the security
procedure and the alarm. **These two are what is left of it**, and they are one mechanism rather
than two, which is the thing to settle before writing anything.

Four things to establish:

1. **There is no exposure hediff in this mod, and that decides quarantine's shape.** Measured:
   the package has **no `HediffDefs` folder at all**. So there is nothing medical to hold somebody
   *for*, and quarantine cannot be *"wait until the sickness clears"* without inventing a hediff —
   which the existing-content-only constraint forbids. **The honest reading is that quarantine is
   "held apart until debriefed"**, which makes it the same mechanism as the debrief and gives the
   debrief a consequence.
2. **Debrief has most of its machinery already built, and it must not be rebuilt.**
   `EvidenceObservations.RecordFieldObservation` files what a crew member saw;
   `EvidenceInterview.SettleDisputedAccount` (0.12.28-dev) settles two accounts that disagree, with
   nine refusals and an interviewer chosen on Social. **Read both before designing.** What is
   plausibly missing is the *home-side* step: a returning crew member reporting in, as against an
   observation being written down in the field.
3. **Quarantine is an area question and three area rows are still open** — 1215, 1235 and 1239
   cover `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` across
   a gate. **Measured at 0.12.33-dev: one incidental `Area_NoRoof` use and no cross-gate
   coverage.** If quarantine is an area, build it with those three rather than beside them.
4. **`python tools/register-query.py family "staff psychology"`** — it is one of the **seven**
   families the register retro sweep has not reached (rows 206, 302), and a debrief is a mood event
   about what somebody saw. This is the sweep that owes this work its guidance.

**The thing to be careful about:** a debrief that hands out a mood effect is writing a `ThoughtDef`
consequence, and `ThoughtDefs` already ship in this package — so check what is there before adding
anything. 0.12.5-dev deleted four research projects for being unlocks with nothing to unlock, and a
debrief that changes nothing observable is the same defect.

---

""")

# ------------------------------------------------------------------ the remaining list
sub(u"""1. **Containment rooms, security procedures, staff debrief, quarantine, alarm and escape
   response.** Row 761. Evidence custody and case records already ship; **witness interviews
   shipped 0.12.28-dev.** This is the rest of that row, and **it is the DO THIS FIRST item** —
   see the top of this file for the four things to settle.
   **Row 1266 is closed** (0.12.34-dev): the eleven DLC container hauling givers are built as
   `machine-loading`, and the custody review they were waiting on found that **Core forbids every
   one of them from moving anything between maps**, so invariant 55 was never engaged. **The four
   painting givers in `Art` are closed with them** — `Art` had a bill family and no designation
   family, so nobody would ever have crossed to paint anything.""",
    u"""1. **Staff debrief and quarantine** — the last two halves of row 761, and **the DO THIS
   FIRST item**; see the top of this file for the four things to settle, of which *"there is no
   exposure hediff in this mod"* is the one that decides the shape.
   **Closed from that row at 0.12.35-dev:** containment rooms (a tenth facility category matched
   by capability, naming no expansion def), the security procedure (a standing order that cuts
   every open connection on a breach, through the gate's own existing cutoff) and the alarm. The
   finding worth keeping: **Core already ships four containment alerts and every one reads
   `Find.CurrentMap`**, so the gap was never that containment has no warning but that it has none
   about the maps you are not looking at.
   **Also closed, 0.12.34-dev:** row 1266's eleven DLC container hauling givers as
   `machine-loading` — **Core forbids every one of them from moving anything between maps**, so
   invariant 55 was never engaged — and the four `Art` painting givers as `painting`.""")

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("NOW.md updated for 0.12.35-dev")
