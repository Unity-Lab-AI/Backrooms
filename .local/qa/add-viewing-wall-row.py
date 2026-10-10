# -*- coding: utf-8 -*-
"""Re-open the viewing-wall direction that was declared open and then lost, and answer it.

0.12.87-dev removed the ReBuild glass defs and its own archive entry says the owner direction they
served *"stays open in the queue"*. **It did not.** No open row for it exists in TODO.md,
DECOMPOSED.md or ROADMAP.md -- the sentence promising it would stay open was archived along with
the row that closed, and the direction went with it. Recorded here verbatim and answered.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — the viewing wall, re-opened after being lost, and answered (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"ioi thought the wiki says we dont need the stargate mod remember? and the ballistic glass we used in the scenria facility needs to be replaced too so we aarent uusing ballistic glass in game\"*",
"",
"**Verbatim owner direction this re-opens (2026-10-04, from the register sweep):** *\"with like ballistic glass  walls for viewing the machine remotely and safely with security zones and shit\"*",
"",
"### Two answers, and one of them is an apology",
"",
"**THE BALLISTIC GLASS IS ALREADY OUT OF THE GAME, and has been since 0.12.87-dev.** `RR_Starts.xml` named `RB_ReinforcedGlassWall` and `RB_GlassWall` from ReBuild: Doors and Corners (register row 185); both are gone, they were the **only two** non-Core def references in any shipped start, and `check-register-compliance.py` now refuses a non-Core def in a shipped start or scenario. Those eleven cells are plain steel wall. **Nothing in the game uses ballistic glass**, and the four remaining mentions of the word in that file are the comment recording its removal.",
"",
"**AND THE STARGATE MOD IS NOT A DEPENDENCY AND NEVER WAS.** The owner is right, and the error was mine, in a sentence I wrote about what to build next. **Stargates! is register row 218, GPL-3.0, explicitly not a dependency and nothing is taken from it** — `COMPLIANCE_AND_OFFICIAL_VERSIONS.md` records that copying from it would force this project to GPL, and `check-compliance.py` holds it. The owner's own words were a **comparison**: *\"300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels\"* and *\"like the stargate mod works but with normal does\"* — a 300×300 level reached through **an ordinary door**. The wiki mentions no mod by name for this and must not start.",
"",
"### What was actually still open, and was lost",
"",
"**The archive entry for the glass removal says in its own words that the direction it served *\"stays open in the queue\"*. It did not stay open.** No row for it exists in `TODO.md`, `DECOMPOSED.md` or `ROADMAP.md` — the promise was written inside the row that closed, so it was archived with it. **A sentence promising that something stays open is not a queue row.** An owner direction survives only as its own row.",
"",
"- [x] **\"with like ballistic glass  walls for viewing the machine remotely and safely with security zones and shit\"** — **ANSWERED CORE-ONLY 0.12.98-dev, and the answer is that there is no glass.** Measured against the installed game rather than assumed: **Core ships no barrier that is both see-through and sealing.** `Wall` blocks sight; `Barricade` is `passability PassThroughOnly` at `fillPercent 0.55`, holds no roof and seals nothing, so a run of them in a twenty-cell hall both breaks the seal and reintroduces the roof-collapse case `pillars` exists to prevent. There is no third option in Core. "
"**So \"remotely\" is answered by the thing that already ships: the Operations → Machine pane**, which reads live gate state from any map, and the physical answer is the **security zone the owner also asked for** — a solid wall with an **airlock of two automatic doors in series** between the control room and the hall. **That is strictly safer than glass**, which is the half of the direction a window would have failed: *\"remotely and safely\"*. Recorded in `RR_Starts.xml` in place of the note that said this was still undecided, and `scenarios.md` no longer tells a reader there is viewing glass.",
"- [ ] **A physical window stays a legitimate want, and it is a content decision rather than a gap.** If the owner wants to *see* the hall from the control room, Core cannot do it and the options are each a real trade: an open gap in the wall (line of sight, no seal), a run of barricades (sight, no seal, no roof support), or **our own see-through wall def**, which is the only one that keeps the seal and is also the only one that adds a building — and *\"repurpose existing game/mod content\"* is the standing rule, with the menu art the single approved exception. **Needs the owner's call; nothing is blocked on it.**",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "the viewing wall, re-opened after being lost" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d open, %d closed" % (SECTION.count("- [ ] "), SECTION.count("- [x] ")))
