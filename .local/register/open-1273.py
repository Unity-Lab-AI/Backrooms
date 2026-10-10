# -*- coding: utf-8 -*-
"""0.12.73-dev: the gate nobody could open, and the facility a six-year-old chimp built."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - the gate nobody could open, and the facility - 2026-10-01 (0.12.73-dev)

Owner, verbatim:

> **"okay i need help. .. check the game what do i do to get this gate open? ive tried
> everything.. follow my past attempts and tell me what im missing as they built the 8 componet
> thing at the attached machining table and then with out notice they went to the coms console and
> did something un pormpted(i thought the portal would open after he finished, but it didnt) so
> why does the game show the portal gate didnt open? what am i missing or is something major
> broken"**

> **"well what the fuck i already told you the company start needs a fulley connect and set up
> sweet ass facility.. currently it looks like a 6yr old chimp made the facility as the gate is
> rfree standing and it now weays looks like a working "machine" that should be designed
> intelligently with like ballistic glass  walls for viewing the machine remotely and safely with
> security zones and shit and lab rooms and shit i mean wtf is this this is a 50million dollar
> facilty"**

- [~] **"what do i do to get this gate open? ive tried everything"** - **nothing is broken.** The
  chain is intact; the interface never said which of eight preconditions was unmet, and with no
  address remembered it drew **no button and no sentence at all**
- [~] **"follow my past attempts and tell me what im missing"**
- [~] **"they built the 8 componet thing at the attached machining table"** - that completed the
  assembly. `RecipeWorker_RimroomsGateAssembly.Notify_IterationCompleted` -> `CompleteAssemblyFromBill`
- [~] **"then with out notice they went to the coms console and did something un
  pormpted(i thought the portal would open after he finished, but it didnt)"** - that was
  **calibration**, taken by `WorkGiver_RimroomsGate`. It is the step after assembly, not the
  opening
- [~] **"so why does the game show the portal gate didnt open?"**
- [~] **"what am i missing or is something major broken"**
- [~] **"the company start needs a fulley connect and set up sweet ass facility"**
- [~] **"currently it looks like a 6yr old chimp made the facility"**
- [~] **"the gate is rfree standing"**
- [~] **"it now weays looks like a working \\"machine\\" that should be designed intelligently"**
- [~] **"with like ballistic glass walls for viewing the machine remotely and safely"**
- [~] **"with security zones and shit"**
- [~] **"and lab rooms and shit"**
- [~] **"i mean wtf is this this is a 50million dollar facilty"**

### The eight preconditions, and which the interface hid

`BeginSpinUp` refuses for eight reasons and reports **one**, after a button press -- and the open
buttons are drawn per remembered laboratory address, so **a gate with none shows an empty panel**.
A player who has commissioned the door, run the bill and let the crew calibrate has done
everything the gate itself asks for and is looking at nothing.

Worse, two of the eight are the **gate-control switch added at 0.12.70-dev, which defaults to
normal operation on purpose** -- commissioning a door must not change how the colony works -- so a
player who never saw that gizmo has two components quietly refusing.
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))
print("TODO opened for 0.12.73-dev, both messages verbatim")
