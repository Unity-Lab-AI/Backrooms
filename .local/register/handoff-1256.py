# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.56-dev: what the eighth launch settled and what it did not."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## DO THIS FIRST — READ THE LOG FROM THE EIGHTH LAUNCH"

NEW = u"""## DO THIS FIRST — READ THE LOG FROM THE NEXT LAUNCH

### THE EIGHTH LAUNCH NEVER REACHED A MAP: the setup page stopped drawing after three lines

**0.12.55-dev loaded clean — the owner's log went from 587 cross-reference errors to ZERO**, and
`[Rimrooms] odd-origin marker attached to 2744 thing definitions` is up from 2742, which is `Door`
and `Autodoor` back in the game. The `CompProperties_Colorable` fix is **confirmed in the running
game**, not from proofs.

**But the company setup page drew three lines and stopped**, so that launch never reached a map.
No roster, no funding, no supplies, no facility, one of five gate prerequisites — and **no
exception anywhere in the log.** The owner: *"there are no lists or supplies on the card pop up at
all.. so what the fuck?"*

`Verse.Listing.GetRect` → `NewColumnIfNeeded` → unless `maxOneColumn` is set,
`curY = 0f; curX += ColumnWidth + 17f` the moment content outgrows the rect. `Begin` sets
`ColumnWidth` to the **full width**, so the overflow is drawn a whole width to the right —
**outside the group `Begin` opened and clips to.** Painted off the edge, silently. And `CurHeight`
is `curY`, which `NewColumn` just zeroed, so `contentHeight = CurHeight + 20f` measured the
*second* column: the content shrank, the wrap came sooner, and it settled at three lines. That is
also why there was no scrollbar.

**Eight listings in the package, not one set the flag.** Seven fixed, including the Operations
board — the main window of the mod, which was carrying the same silent truncation. The settings
window keeps its deliberate two columns.

**THE LESSON, AND IT IS THE SAME SHAPE AS THE SEVENTH LAUNCH.** Every line of our code was
correct. The defect was **an unset Core default interacting with a value Core resets** — invisible
to any proof that reads our source, exactly like a `Class` name that does not resolve. **When a
claim is about whether something *works* rather than whether it is *written*, assert the engine's
contract, not our text.** `proof-setup-page-draws.py` does that: every listing in the package must
declare whether it is one column or more, and a new one that declares neither fails.

### AND THE SUPPLIES SECTION WAS ASKING THE WRONG OBJECT

It read `Find.Scenario.AllParts` — the **live** scenario — and EdB Prepare Carefully rewrites
exactly those parts (`ReplaceScenarioPatch`, `ShouldReplaceScenarioPart`, `OriginalScenarioParts`,
`ReplacedScenarioParts`, `CreateScenarioPartForCustomizedEquipment`). It reads the **authored
`ScenarioDef`** now, found by the start it declares, and draws **both** lists, because the owner
asked for *"the equipemnet for the gate that u get added to ur start on top of what u fill out in
edb prepare carfully"*. Register row **[85]** is Optional/Provisional and says *never a runtime
dependency* — nothing is patched, named in code, or required.

**A content bug this exposed by accident:** `RR_Setup_GateCost` promised *"Those are in the
supplies below."* The bill wants **100 steel and 8 components**; the **Furniture Store start
arrives with 80 steel and no components at all.** Written against the Async start, asserted for
all three.

### ORIGINAL ORDER OF BUSINESS, STILL UNSETTLED"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("NOW.md handoff rewritten for 0.12.56-dev")
