# -*- coding: utf-8 -*-
"""Record the full wiki checkup: every claim measured against source, defects stacked with locations.

The owner asked for the analysis, not a description of one. So every row below carries the file,
the constant and the line that proves it, and the verified-correct table exists so a rewrite does
not "fix" the eight numbers that are already right.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Full wiki checkup analysis — measured against source, not read (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"read now.md and lets do that full wiki checkup analysis to stack\"*",
"",
"All thirteen pages read end to end — **988 lines, smaller than one source file** — and every countable or behavioural claim checked against the code that implements it. **Six claims are not stale, they are wrong**, and one of them advertises a transaction the code deliberately refuses to perform.",
"",
"### Verified CORRECT — recorded so a rewrite does not \"fix\" what is already right",
"",
"| Claim | Where it is proved |",
"|---|---|",
"| 294 mods in the load-order list, zero dependencies | `About.xml` — `loadAfter` 294 `<li>`, `modDependencies` **absent** |",
"| Up to three field staff | `CrewPlanner.MaxCrew = 3` |",
"| 100 steel + 8 industrial components | `RR_GateRecipes.xml` — `RR_AssembleMachineGate`, `workAmount 6000` |",
"| Below half condition a gate will not hold | `CompRimroomsGate.IntegrityFloorFraction = 0.5f`, read as a fraction of Core's `MaxHitPoints` |",
"| Up to 25,000,000 drawn, three replacement staff | `CompanyClearSquad.RestockingChargeUsd = 25000000L`; `ClearSquadRoles` = operations, engineering, security |",
"| Bonds from ten up to a quadrillion | 15 `RR_PrintBond_*` recipes, `_10` through `_1000000000000000` |",
"| An ornate door is a 2-cell gate | `GateFootprint` — `OrnateDoor` is 2x1, read out of the shipped assembly |",
"| Seven research branches | `RimroomsProjectDefs` — Commerce, Entities, Facilities, Fieldcraft, Logistics, Measurement, Spatial |",
"",
"### The defects, each with the line that proves it",
"",
"- [ ] **`gates.md` tells players the free doors stop at depth 3. They stop at 6.** *\"These reach **through depth 3 and no further**\"* against `NaturalFrontierService.MaximumNaturalDepth = 6` — **raised from 3 to 6 at 0.12.49-dev, owner direction 2026-09-30**, alongside the map budget that made a deeper chain affordable. **Half the free range is undocumented.** **And the root cause is in the source, not the page:** that constant carries **two consecutive `<summary>` blocks**, and the first one still argues for depth 3 in full — *\"the depth chosen at the fork was through depth 3\"*, *\"hands a branch three bands for free\"*. The page copied the stale one faithfully. **Fix both, or the next reader copies it again.**",
"- [ ] **`company.md` says the corporation asks for six things. It asks for seven.** `RimroomsRequestDef.tutorial` is true on **seven** requests with `tutorialOrder` **0 through 6** — PowerTheGate, AssembleAndCalibrate, BringBackOneRecord, MarkARouteHome, ReportADisagreement, HoldAConnectionOpen, ChooseADirection. **Somebody read the last index as the count.** The sentence calls this *\"the hinge of the opening arc\"*, so the number is the one thing on the line that has to be right.",
"- [ ] **`company.md` says four research tiers. There are five bands.** `RR_CompanyProjects.xml` is authored in headed blocks **TIER 0 through TIER 4** — foundations, first entry, repeatable operations, remote operations, the practised branch. 38 projects. Say the band count the file actually has, and say it the way the file does, because `NOW.md` already treats **T5/T6 as open work** and a page claiming four makes the top of the shipped tree invisible.",
"- [ ] **`company.md` advertises selling a bond at 85%, and the code refuses to do it on purpose.** `ValuablesExchange.ExchangeableIn` skips bonds outright — `if (BondService.FaceValueOf(thing) > 0L) { continue; }` — and the reason is written beside it: *\"quietly selling a million-credit bond at 0.85 would be a way to destroy a player's money by accident.\"* **The page documents the exact accident the code was written to prevent.** The 0.85 is real but it is `OrdinaryExchangeRate` for ordinary goods, not bonds. Deposit and bank at 100% is correct and stays.",
"- [ ] **`interface.md` is the pane-by-pane reference and it is missing a pane.** `MainTabWindow_Operations.PaneKeys` ships **fourteen**; the table lists **thirteen**. The absent one is `RR_UI_Places` — **\"Places\"**, between Sites and Help. A reference table that omits a pane is worse than no table: a player concludes the pane is not there.",
"- [ ] **`first-hour.md` promises eleven goals and documents six.** Its own summary says *\"eleven goals, in the order they unlock\"* and the body numbers **1 to 6**. **The summary is the correct one** — `GateStartupChecklist.Steps` is eleven, and `OperationsGateSteps.cs` says so in its own words: *\"a player who already knows simply sees eleven ticks.\"* Write all eleven, in the game's own labels: a door chosen · console, battery and table bound · **the gate commissioned** · **machining table set to gate control** · gate assembled · an operator assigned · the gate calibrated · **communications console set to gate control** · **an address remembered** · the operator standing at the console · a session opened.",
"- [ ] **THE ONE REPORTED \"IT WILL NOT OPEN\" FAILURE IS THE ONE THE WIKI NEVER MENTIONS.** Steps **4** and **8** are *\"set to gate control\"* — the table and the console, separately. That is verbatim the owner's own fault report: *\"ive done like 50 things in a row and its still not opening\"*, where the save had *\"the machining table in gate control while the communications console on the same gate was not\"*. **One switch, out of eleven steps.** It is the entire reason the Machine pane was renumbered. **It appears in `first-hour.md`, `gates.md` and `troubleshooting.md` exactly zero times** — and `troubleshooting.md`'s *\"Every box is ticked and it still will not connect\"* section, which exists for precisely this moment, sends the player to check the **address** instead. **That section is wrong in the only place a player reads it.**",
"- [ ] **A permanent, irreversible, item-destroying action ships with no wiki page at all.** The Places pane carries **24+ keyed strings** including a confirmation reading **\"THIS CANNOT BE UNDONE. The gate will not open again\"**, a *\"{0} item(s) would be left behind\"* warning, refusals for *\"somebody is still inside\"* and *\"somebody is part-way through a way into it\"*, and a whole second list — *\"Released, and reachable again from the door that found them\"*. **Nothing anywhere in the wiki warns a player that Release is forever or that stock is lost.** Of every gap in this sweep this is the one that costs a player something real.",
"",
"### The remaining undocumented systems, now with the game's own words rather than my description",
"",
"| System | The player-facing text that exists | In the wiki |",
"|---|---|---|",
"| Three operational gates | `NativeGateBinding.MaximumOperationalGates = 3` | **no** |",
"| The random dial | **\"Dial an unknown address\"** — *\"Let the gate choose somewhere. No request, no contract, nobody waiting\"* | **no** |",
"| The open-map budget | `RR_Release_Budget` — *\"Holding {0} of {1}. A Backrooms level costs a loaded map exactly as a colony does\"* | **no** |",
"| Boarding a doorway up | `RR_BoardUp_Label` — **\"Board it up ({0} wood)\"** | **no** |",
"| Staff certification and training | 3 certs (`RR_Cert_GateOperator`, `_FieldAnalyst`, `_ReserveTechnician`) and **3 training bills** on the machining table and crafting spot, with skill floors of Intellectual 4, Intellectual 3 and Crafting 5 | **no** |",
"| Grand pillared halls | shallow levels are few huge rooms, pillars on a 6.9 lattice | **no** |",
"| Material variation by depth | what a room is built from is part of the loot | **no** |",
"| A stranded crew | a closed gate does not take your people | **no** |",
"",
"- [ ] **Certification is the gap that dead-ends a player, so it is called out separately.** `first-hour.md` step 3 says *\"A qualified staff member calibrates the gate\"* and `troubleshooting.md` answers *\"Out of calibration\"* with *\"Have a qualified staff member calibrate it\"*. **Neither page, nor any other, says anywhere that you can make one** — three **train** bills sit on the machining table and the crafting spot. A player with nobody certified is told to go find a person who does not exist in their colony, and the instruction is a loop. **Name the bills, name the skill floors, say the crafting spot works so it is reachable before a table exists.**",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "Full wiki checkup analysis" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d open rows added" % SECTION.count("- [ ] "))
