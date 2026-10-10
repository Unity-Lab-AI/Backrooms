# -*- coding: utf-8 -*-
"""Log the Operations-panel direction, verbatim, one row per clause."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = '''### Owner direction — the Operations panel is a text wall and has to become a utility (2026-10-04)

**Verbatim owner direction (2026-10-04):** *"and add to the todo we need to make the whole operations panel thing alot less of a text wall its like a fucking novel when it doesnt need to be for example one of many things that can be done and all things should be done to make it more of a utility, not  a text wall so that on the machine tab its shows the different systems with green and red lights of whether complete/active with a next step section showing what to do next  not every step having its own type up of whats next and things can be shortend and more concise and dirrect  with tools tips would less cluter it making them all concise and accurate, and all the tabs of operations are well designed for a tripple A Mod currently it looks like its all just text wall and shit, and everything that the machine needs to start up should be able to do in the worlkd from the devices themselfes with pawns controls and actrions not just in the opetaions tab,, ie setting the cordinace and all of those things need  to show and when u set a door to be a gatew  that gate should tell you next step in the game world not just in the operations tab and machine tab,, and we dont need things like long string corrdinates list in the operations panel thing like that arnet needed only like the !A-01 address code is needed to be displayed to thew player and save able and useable and gates need to be able to set up a max of three of them  so u can have three addrerss called at once wich would give 4 of 5 open maps,, and the closing of natural portals needs to be an option on the gate itself so pawns can close it with like 25 wood to board it up which makes it close its map freeing up a map from being open so others can be explored"*

**Eleven clauses, each its own row below.** This is the first direction in the project aimed squarely at the **UI as a product** rather than at a behaviour, and the owner's standard is explicit: *"well designed for a tripple A Mod"*.

- [ ] **"we need to make the whole operations panel thing alot less of a text wall its like a fucking novel when it doesnt need to be"** — the complaint, and the acceptance condition. **Measure the text volume before cutting any of it**, because "less" is a number and every previous attempt in this project to fix a feel without a measurement got the wrong half.
- [ ] **"for example one of many things that can be done and all things should be done to make it more of a utility, not  a text wall"** — *"all things should be done"*: the green/red readout below is named as **one example of many**, not as the fix. A utility is something a player reads at a glance and acts on; prose is something they read once and skip forever after.
- [ ] **"so that on the machine tab its shows the different systems with green and red lights of whether complete/active with a next step section showing what to do next  not every step having its own type up of whats next"** — a **status board**: one row per system, a light for complete/active, and **one** next-step section for the whole tab. The current shape writes a paragraph of what-to-do-next beside every individual step, which is what makes it a novel.
- [ ] **"and things can be shortend and more concise and dirrect  with tools tips would less cluter it making them all concise and accurate"** — the detail moves into **tooltips**. Short on the surface, full text on hover, and *"accurate"* is a constraint on the shortening: a label that fits by dropping the condition it describes is worse than the paragraph.
- [ ] **"and all the tabs of operations are well designed for a tripple A Mod currently it looks like its all just text wall and shit"** — **every tab**, not only the machine tab, and the bar is a commercial-quality mod UI.
- [ ] **"and everything that the machine needs to start up should be able to do in the worlkd from the devices themselfes with pawns controls and actrions not just in the opetaions tab"** — **the Operations panel must stop being the only way to do anything.** Every start-up step has to be available on the physical object, through pawn-facing gizmos and jobs. The panel becomes a readout and a convenience rather than the mechanism.
- [ ] **"ie setting the cordinace and all of those things need  to show"** — naming the hardest case: **setting the coordinate from the device**, and *"all of those things"* means the rest of the start-up chain with it.
- [ ] **"and when u set a door to be a gatew  that gate should tell you next step in the game world not just in the operations tab and machine tab"** — the gate tells the player what to do next **where the gate is**: its inspect card and its gizmos, in the world, at the moment of designation.
- [ ] **"and we dont need things like long string corrdinates list in the operations panel thing like that arnet needed only like the !A-01 address code is needed to be displayed to thew player and save able and useable"** — the long coordinate id comes **off the player-facing surface entirely**. The **short address code** is the only identifier a player ever sees, and it must be **saveable and useable** — the thing you store, recall and dial.
- [ ] **"and gates need to be able to set up a max of three of them  so u can have three addrerss called at once wich would give 4 of 5 open maps"** — **three addresses held per gate**, concurrently. The owner has done the arithmetic against the standing open-map budget: three called coordinates plus the colony is **four of five**, leaving one spare. That ties directly to `Portals/OpenMapBudget`.
- [ ] **"and the closing of natural portals needs to be an option on the gate itself so pawns can close it with like 25 wood to board it up which makes it close its map freeing up a map from being open so others can be explored"** — **boarding up a natural portal, from the gate, by a pawn, for about 25 wood**, which closes its map and returns a slot to the budget. This is the player-facing answer to the held-places problem that has been open since *"get 5 natural gates u cant use a machine gate"* — and it is a **job with a material cost**, not a menu button.

'''

text = io.open(TODO, encoding="utf-8").read()
anchor = "## Pending" + NL
if text.count(anchor) != 1:
    print("cannot find the single Pending heading")
    sys.exit(1)
at = text.index(anchor) + len(anchor)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + NL + SECTION + text[at:])
print("logged the direction, %d rows" % SECTION.count("- [ ] "))
