# -*- coding: utf-8 -*-
"""Documents for 0.12.77-dev, in the same atomic commit as the code."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: docs-1277.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

CHANGELOG = os.path.join(REPO, "CHANGELOG.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
TODO = os.path.join(REPO, "docs", "TODO.md")

entry = u"""# Changelog

## 0.12.77-dev - 2026-10-01 - every battery counts, and the refusal tells you the truth

- **A gate now runs off its whole circuit.** It used to read charge from the single battery you
  bound to it and ignore every other battery on the same power net, so adding batteries did
  nothing. Bind one as the anchor, then put **as many on the circuit as you like** — there is no
  limit, and the readout shows the circuit's total.
- **And it spends from the whole circuit too.** Worse than the reading: a drained anchor battery
  refused to open or hold a connection *while ten full batteries sat beside it on the same net*.
- **A refusal now names the real cause.** Seven different problems used to produce one message:
  *"The laboratory connection for that address is not open."* So a flat battery reported an
  address fault. There are now separate reasons for no stored charge, an expedition holding the
  connection, an emergency in progress, an expired window, and an operator off station.
- **The wiki.** How to install it, how to set up your mod manager, how to play, what is through
  the gate, and what to do when something refuses — written as short pages instead of one long
  document, and linked from the mod description in game.
- **Reports get signed off, and your people remember where they have been** — carried over from
  the previous build and now documented.

Full record: [every battery counts](docs/implementation/GATE_CIRCUIT_IMPLEMENTATION.md). No
gameplay, balance, performance or compatibility result is claimed.

"""
text = io.open(CHANGELOG, encoding="utf-8").read()
if not text.startswith(u"# Changelog\n"):
    print("CHANGELOG does not start as expected")
    raise SystemExit(1)
io.open(CHANGELOG, "w", encoding="utf-8", newline="").write(
    entry + text[len(u"# Changelog\n"):].lstrip(u"\n"))
print("CHANGELOG entry written")

record = u"""
---

## Session 2026-10-01 - the public wiki, and one battery was the whole reserve (0.12.77-dev)

**Verbatim user quotes:** *"make sure to update all the public facing doc and workflow
docs(remember public facing docs are concise easy to read and have no in house dev names and no
todo numbering and no actual work information but are concise and informatitve laying out the full
wiki of the dame how to play how to set it all up rimsort all of it ... public facing documnets ARE
NOT to be text walls get to each point in as short a way as possible"*; and from a running game:
*"its the same problem as before: the laboratory address for that is not open.... looks like only
being able to connect 1 battery isnt anough and there should be no loimit"*.

**Files touched:** `docs/wiki/` (13 new pages), `docs/_config.yml` (new), `README.md`,
`Gate/NativeGateBinding.cs`, `Gate/PortalGateOpening.cs`, `Portals/PortalTravelService.cs`,
`Keyed/RR_Portals.xml`, `About/About.xml`, `tools/check-doc-conformance.py`,
`docs/GATE_0_DECISIONS.md`, twenty-one documents given a supersession banner,
`proof-gate-circuit.py` (new, proof FORTY-NINE), `plant-gate-circuit.py` (new, suite TWENTY),
`proof-playing-and-help.py`, `proof-integrations.py`, `plant-playing-and-help.py`,
`plant-housekeeping.py`, `plant-integrations.py`.

**Mod register.** Nothing new applied. The expansion rows are already recorded as superseded in
D3/D4.

### ONE BATTERY WAS THE WHOLE RESERVE, AND THE MESSAGE SENT THE OWNER THE WRONG WAY

The owner's own diagnosis was right: *"which i think is a power porblem"*.

`nativeBattery` was only ever meant to be the **anchor** identifying which power net is the gate's
circuit. `NativeGenerationWatts` has always summed the whole net. `NativePowerConnected` has always
checked the whole net. **Stored energy was the one reading that never followed** — it read one
battery's `StoredEnergy` and nothing else.

And the spend was worse than the read: `TrySpendNativeEnergy` **refused outright** when the anchor
alone could not cover a cost, so a drained bound battery stalled a gate with ten full batteries on
the same net.

**Why it looked like an address fault.** `HasUsablePortalWindow` collapsed seven conditions into
one bool; `RimroomsPortalNetwork` turned false into `Closed`; the player read *"The laboratory
connection for that address is not open."* A flat battery reported an address problem, which is
why the owner spent the session on the address.

Both halves are fixed through Core's own mechanisms: `PowerNet.CurrentStoredEnergy()` for the sum
(EMP-aware for free), and the draw pattern copied from `ChangeStoredEnergy`, which does exactly
this and is private. The refusal is now a **blocker key** — the third of its kind after
`CalibrationBlockerKey` and `StaffConsoleBlockerKey`, both added because one generic message
covered several problems with several different fixes. **`HasUsablePortalWindow` delegates to it**,
so the predicate and the message cannot disagree.

**`returnReserveCapacityWattDays` is 2 and a Core `Battery` holds 600**, so the bind-time
*ReserveTooSmall* refusal was checked and ruled out rather than assumed.

**And nothing in forty-eight proofs had ever claimed anything about the energy a gate runs on.**
`grep -l` for `NativeStoredEnergy`, `HasUsablePortalWindow` and `ReturnReserveStored` returned
nothing, which is why a defect this central reached a running game.

### THE READER-FACING LIST WAS MOSTLY NOT READER-FACING

Owner: *"public facing docs ... have no in house dev names and no todo numbering and no actual work
information"*.

`READER_FACING` held thirteen entries and **most were never reader documents**. `HOWTO.md` opens
*"the practical guide for anyone (human or build agent) opening this repository"* and carries
in-house tooling names, owner-decision identifiers and the branch cascade. `SCENARIOS.md` calls
itself a *"design contract"* with *"tuning hypotheses"*. **Holding a development document to a
reader's vocabulary made it look supervised while nothing was ever going to notice it was the
wrong kind of document.**

`docs/wiki/` is thirteen pages and nothing else. The wall limit dropped from **700 to 360**,
because 700 was derived from the old documents' own shapes and the owner asked for shorter than
those. **The wiki tops out at 307**, so the limit is a floor under a standard already met.

**The vocabulary rule caught two real violations in the wiki's first draft** — the gate called
*"the machine"* in two nav tables, in the one document set whose job is to use the project's words.
Three further matches were the pane's actual name, so the exemption is the two-word phrase
`Machine pane` and nothing else.

### TWENTY-SIX DOCUMENTS LIED IN ONE COMMIT, AND A RULE NOW CATCHES IT

Yesterday's dependency decision made *"Core only"*, *"no hard dependencies"* and *"needs Core
only"* false in **twenty-six living documents**. Every one was true when written.

The count is read from `About.xml`, never typed: **when the package declares dependencies, no
living document may say it has none**, and if the owner reverses the decision the rule stops firing
on its own. D3 and D4 are recorded as changed in `GATE_0_DECISIONS.md`, following D1's own pattern.

**The verbatim ledger is exempt and the reason is a LAW.** `TODO.md`, `NOW.md`, `ROADMAP.md` and
the master backlog carry twenty-nine of the seventy-two matches, and **LAW #0 forbids altering the
owner's recorded words.** They are records of what was said, not claims about what is true.

### THE PLANTS CAUGHT FIVE CONSEQUENCES OF THIS SESSION'S OWN WORK

* **Three plants went MISSED** because `PLAYING.md` left the supervised set — exactly the thing a
  reader-facing rule set can lose silently. Re-aimed at the wiki, where the wall they test is now
  **360** rather than 700.
* **One plant was only ever passing because of a bug.** `plant-housekeeping.py` planted a stat base
  **inside an XML comment**, and that checker has stripped XML comments since the fix for reading
  its own prose. It plants a real one now. **A plant that tests a bug instead of a rule goes green
  while the rule is unguarded.**
* **One claim was the duplicate-string trap, third instance this session.**
  `List<CompPowerBattery> batteries = net.batteryComps;` appears twice, so gutting the capacity
  reader left the claim true. It counts now, as the bond label claim does.

And **the dependency rule reported wrong line numbers on its first run** — it enumerated stripped
text while reporting file positions, so every number after a document's first code fence was wrong.
**A finding with the wrong address is worse than no finding.**

**210 C# files, 92 package files**, zero warnings, zero errors. Assembly SHA-256
`__HASH__`, measured after the version bump, reproduced by two clean rebuilds.
**Sixteen checkers pass, FORTY-NINE proofs hold, 12 of 12 planted faults caught in the new suite,
752 plant anchors findable.**
"""
record = record.replace(u"__HASH__", HASH)
text = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(text + record)
if record not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
CLOSURES = [
    (u"## IN PROGRESS - the public wiki - 2026-10-01 (0.12.77-dev)",
     u"## The public wiki - 2026-10-01 (0.12.77-dev) - DONE"),
    (u"## IN PROGRESS - one battery was the whole reserve - 2026-10-01 (0.12.77-dev)",
     u"## One battery was the whole reserve - 2026-10-01 (0.12.77-dev) - DONE"),
]
problems = []
for old, _ in CLOSURES:
    if todo.count(old) != 1:
        problems.append("%d of %r" % (todo.count(old), old[:56]))
if problems:
    for problem in problems:
        print("TODO ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in CLOSURES:
    todo = todo.replace(old, new, 1)
    start = todo.index(new)
    end = todo.index(u"\n---", start)
    todo = todo[:start] + todo[start:end].replace(u"- [~] **", u"- [x] **") + todo[end:]
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO closed for both batches, every description kept")
