# -*- coding: utf-8 -*-
"""0.12.56-dev: the setup page drew three lines and stopped, and Core did it on purpose."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## The setup page that stopped drawing — 2026-09-30 (0.12.56-dev)

Owner, verbatim: **"the review company start up screen when i press start game on prepare carfully
says: \\"Those are in the supplies list below\\" but there are no lists or supplies on the card pop up
at all.. so what the fuck? if i do the company start will things actually be listed there?"**

and: **"like in the company start up that pop up should list all the equipemnet for the gate that u
get added to ur start on top of what u fill out in edb prepare carfully"**

- [x] **"there are no lists or supplies on the card pop up at all"** — **THE SUPPLIES WERE NOT THE ONLY THING MISSING. THE PAGE STOPPED DRAWING AFTER THREE LINES.** No roster, no funding, no supplies, no facility, and only the first of five gate prerequisites. A screenshot of the owner's running game, brightened four times over, is genuinely blank below that line, and **the log contains no exception at all** — so nothing threw and the page's own `RR_Setup_DrawFault` had nothing to report.

  **The cause is Core, and it is silent by design.** `Verse.Listing.GetRect` calls `NewColumnIfNeeded`, which — unless `maxOneColumn` is set — calls `NewColumn()` the moment content exceeds the listing rect: `curY = 0f; curX += ColumnWidth + 17f;`. `Listing.Begin` sets `ColumnWidth` to the **full rect width**, so overflowing moves drawing a whole width to the right, **outside the `Widgets.BeginGroup(rect)` that `Begin` opened** — which clips it. Everything past the overflow is painted off the edge of the world.

  **And it is self-reinforcing, which is why it collapsed to three lines instead of losing a tail.** `CurHeight` returns `curY`, which `NewColumn` just reset to zero, so `contentHeight = listing.CurHeight + 20f` recorded the second column rather than the total. The scroll content shrank, the wrap came sooner, and it settled at a few lines. It also explains the missing scrollbar: by then the content really did fit.

  **Swept, not patched where it hurt.** Eight listings exist in this package and **not one set the flag**, so every scrolling list carried the same silent truncation — including **the Operations board, the main window of the mod**. Seven are fixed. **The eighth is deliberately left alone:** the settings window sets its own `ColumnWidth` to half the window precisely so the priority sliders wrap into a real, visible second column.

- [x] **"that pop up should list all the equipemnet for the gate that u get added to ur start on top of what u fill out in edb prepare carfully"** — **DONE, and the section was asking the wrong object.** `SupplySummary` walks `Find.Scenario.AllParts` — the **live** scenario — and EdB Prepare Carefully rewrites exactly those parts. Its assembly carries `ReplaceScenarioPatch`, `ShouldReplaceScenarioPart`, `OriginalScenarioParts`, `ReplacedScenarioParts`, `RestoreScenarioParts` and `CreateScenarioPartForCustomizedEquipment`: **it swaps the scenario's starting-thing parts out for parts built from the player's edited equipment and restores the originals afterwards.** So while its page is open the live scenario is not the company's scenario, and what the company contributes is unreportable from it.

  `CompanySupplies` reads the **authored `ScenarioDef`**, found by the start it declares, so it is the same whether a setup utility is installed, absent or mid-edit. **Both lists are drawn** — the company's own contribution under its own heading, then whatever the live scenario carries — because the ask was *"on top of what u fill out"*. When the two disagree the page says so rather than leaving the player to spot it.

  **Public API only.** `ScenPart_ThingCount.thingDef`/`stuff`/`count` are `protected`, and this package uses no Harmony and no reflection; `ScenPart.GetSummaryListEntries` is public and already returns Core's own phrasing. `PlayerStartingThings` is still never called — it builds real objects.

  **Register LAW.** Row **[85] EdB Prepare Carefully**, family *Interface, scenario setup, and quality of life*, stance **Optional**, firmness **Provisional**. Its review says *"Check authored company starts, initial gear and limits"* and *"never a runtime dependency"*. Both honoured: nothing patched, nothing named in code, nothing required — the page just stopped asking a question the live scenario cannot answer.

- [x] **a content bug the screenshot exposed by accident** — `RR_Setup_GateCost` ended *"Those are in the supplies below."* **For the Furniture Store start that is false.** The bill wants **100 steel and 8 components**; the Store arrives with **80 steel and no components at all**. The sentence was written against the Async start and asserted for all three. It now names the cost and points at the list, and the list is the evidence.

- [x] **the forty-third proof, and why it had to exist** — every line of our code was correct; the defect was **an unset Core default interacting with a height we compute from a value Core resets.** Same family as the seventh launch: a claim about what our text says, where the truth lived in the game's behaviour. So the proof asserts the **Core contract** — every listing in the package declares whether it is one column or more, and a new listing that declares neither fails. **16 of 16** planted faults caught.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - the setup page that stopped drawing (0.12.56-dev)

**Verbatim user quote:** *"the review company start up screen when i press start game on prepare
carfully says: \\"Those are in the supplies list below\\" but there are no lists or supplies on the
card pop up at all.. so what the fuck? if i do the company start will things actually be listed
there?"* and *"like in the company start up that pop up should list all the equipemnet for the
gate that u get added to ur start on top of what u fill out in edb prepare carfully"*

**Files touched:** `Scenario/Page_RimroomsCompanySetup.cs`, `Scenario/RimroomsStartupComponent.cs`,
`UI/MainTabWindow_Operations.cs`, `UI/OperationsPersonnel.cs`, `UI/ExpeditionRecordDialogs.cs`,
`Keyed/RR_StartupSetup.xml`, About/csproj/README, `docs/TODO.md`, `docs/NOW.md`.

**Closure notes.** **The missing supplies list was a symptom. The page stopped drawing after three
lines.**

A screenshot of the owner's running game, brightened four times over, is blank below the third
line - no roster, no funding, no supplies, no facility, and one of five gate prerequisites - and
**the log holds no exception at all.** `Verse.Listing.GetRect` calls `NewColumnIfNeeded`, which
unless `maxOneColumn` is set runs `curY = 0f; curX += ColumnWidth + 17f` the moment content
outgrows the rect. `Begin` sets `ColumnWidth` to the full width, so the overflow is drawn a whole
width to the right, **outside the group `Begin` opened and clips to.** Painted off the edge of the
world, silently.

**And it feeds on itself:** `CurHeight` is `curY`, which `NewColumn` just zeroed, so
`contentHeight = CurHeight + 20f` measured the second column. The content shrank, the wrap came
sooner, and it settled at three lines - which is also why there was no scrollbar.

**Eight listings in the package, not one set the flag.** Seven fixed, including the Operations
board. The eighth - the settings window - sets its own `ColumnWidth` to half the window so the
sliders wrap into a real second column, and is deliberately left alone. That distinction is the
difference between a sweep and a find-and-replace.

**The supplies section was also asking the wrong object.** It read `Find.Scenario.AllParts`, and
EdB Prepare Carefully rewrites exactly those parts - its assembly carries `ReplaceScenarioPatch`,
`ShouldReplaceScenarioPart`, `OriginalScenarioParts`, `ReplacedScenarioParts` and
`CreateScenarioPartForCustomizedEquipment`. It now reads the **authored ScenarioDef**, found by
the start it declares, and draws **both** lists - the company's own contribution and whatever is
live - because the ask was *"on top of what u fill out"*. Public API only: the count fields are
protected and this package uses no reflection. Register row [85] is Optional/Provisional and says
*never a runtime dependency*; nothing is patched, named or required.

**A content bug the screenshot exposed by accident:** the gate line promised *"Those are in the
supplies below"*, and the Furniture Store arrives with **80 steel and no components** against a
bill wanting **100 steel and 8 components**. Written against the Async start, asserted for all
three. It points at the list now instead of promising.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`A0AE0AA2A671B846663EEB19F3E37BF0F052CBAA29D342538E81043AE5D9D536`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-three proofs hold. 490 of 490** planted faults caught
across fifteen suites.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("setup-page rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.55-dev**.", u"| Published | **0.12.56-dev**."),
    (u"SHA-256 `154428928909D68FFA599193CCE8997FBF10AC70671118AB958EEE701E3A3CF9`",
     u"SHA-256 `A0AE0AA2A671B846663EEB19F3E37BF0F052CBAA29D342538E81043AE5D9D536`"),
]
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
print("NOW.md updated for 0.12.56-dev")
