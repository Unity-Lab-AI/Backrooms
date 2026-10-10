"""Append the 0.12.80-dev session entry to docs/FINALIZED.md.

File, not a heredoc. Eleven mangles are on the record.
"""

import io
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PATH = os.path.join(REPO, "docs", "FINALIZED.md")

ENTRY = u"""
---

## Session 2026-10-02 - the tab that stole Architect's corner, and a shop stocked with food that rots (0.12.80-dev)

**Verbatim user direction, the start:** *"okay bug hunt feature branch 1. im not correctly starting
weith my set up prepare carfully goods and the scenerios starting good... as you can see they are
not accurate if you check the current running game, just as an example of whats not right.. my
preparecarfully mod food did not appear and the starting scenerio supplies of food did not appear
and should start scenerio with survival meals not simple meals and should be like 100 to start
besides whats set in prepare carfully so check the current game and whats on the map versus what
they were suppose to start with verses how to fix it properly now"*

**Verbatim user narrowing, after the live read:** *"as far as that start bug it was just the simple
meals that need to be survioval meals and they need to properly spawn in with starting goods"* and
*"wtf its fucking simple to see the simple meals didnt appear"*

**Verbatim user direction, the tab bar:** *"and i want you to fix the operations tab it should not
replace the architects default possition, i find my self trying to click archetic(which was in far
left) but find my self out of habit click operations(because it took the archetect postioton) So we
need to swap theri postions at the bottom so archetic is back in the far left tab position and
operations tab moves to where archetic tab is... so we are swapping theri positions the archetect
and operations tab so archetect tab is back in its default far left position"*

**Files touched:** `Mod/.../Defs/ScenarioDefs/RR_Scenarios.xml`,
`Mod/.../Defs/MainButtonDefs/RR_MainButtons.xml`, `Mod/.../About/About.xml`, the csproj,
`CHANGELOG.md`, `README.md`, `docs/implementation/PLAYER_FACING_IMPLEMENTATION.md`,
`docs/TODO.md`, `docs/NOW.md`, `.local/register/proof-playing-and-help.py`,
`.local/register/plant-playing-and-help.py`, `.local/qa/scan-starting-goods.py` (new).

**Mod register.** Checked before either change, per the LAW. The **Interface / scenario setup and
quality of life** family is **eleven rows and every one is Optional, none Required** - row 85 EdB
Prepare Carefully (traces `RR-FAC;RR-STA;RR-UI;RR-COMPAT`, directly on the starting-goods path),
row 81 Dubs Mint Menus, row 155 Numbers, row 64 Character Editor and the rest. **Nothing in it
constrains either fix**, and that is the reason the tab move is a value on this mod's own def
rather than a patch against Core's Architect: a `PatchOperation` on Core's button bar is the one
route a Harmony-free mod still has, and it would fight every row in that family at once.

### THE LIVE READ, BECAUSE THE REPORT WAS ABOUT A RUNNING GAME

Read through the bridge against the owner's own process, read-only. **The bridge was working** -
`127.0.0.1:5174` listening on PID 21632 - which is worth stating because a previous session
declared it broken while probing the wrong ports.

`.local/qa/scan-starting-goods.py` swept **9,216 cells** around the three colonists at (147, 151)
and tallied every thing in them. Two facts came out of it that no amount of reading the defs would
have given:

- **The running package was `0.12.78-dev`, not the built `0.12.79-dev`.** The staged copy was a
  checkpoint behind, so the game under inspection was not the game in the repository.
- **The scenario was `furniture_knickknack_store`** - confirmed from the branch-init line in
  `Player.log`, and matching the three colonists. The log also shows a `lone_survivor` init and a
  second Store init earlier, so the owner had been rerolling.

**No simple meal was anywhere on the map**, and the sweep reads shelf contents - it reported
`Steel`, `MedicineUltratech` and `Gun_ChargeRifle` sitting inside shelf cells - so the absence is
measured, not inferred from a gap in the instrument.

**What was on the map was mostly not the start at all.** The single `MealSurvivalPack` on the
ground and the one in each pawn's inventory are **Core's default pawn possession**. The
`Gun_ChargeRifle` x3, `MedicineUltratech`, `MechSerumYouth` and `Neurotrainer_Mining` are
**ancient-danger loot** from Core's own scatter, beside `AncientCryptosleepCasket`,
`AncientHermeticCrate`, `Sarcophagus` x6 and `SteleLarge` x12. Reading those as a broken start
would have been the obvious mistake.

### THE MEAL, AND WHY SIMPLE WAS THE WRONG DEF TWICE OVER

The Store granted `MealSimple` **24**. It is now `MealSurvivalPack` **100**.

**It was the only simple meal any scenario granted** - Async already gave `MealSurvivalPack` 50 and
solo/group 5 - so the Store was the odd one out rather than the pattern. And **a simple meal
spoils**: `MealSimple` carries `daysToRotStart`, so a shop start was handing the player two dozen
meals and then quietly taking them away again. A packaged survival meal is what a stocked shop
should hold.

**Both defs were verified present in the installed game data before the swap** rather than assumed
- `MealSimple` and `MealSurvivalPack` both resolve in `Data/Core/Defs/ThingDefs_Items/Items_Food.xml`
- so a missing reference was ruled out as the cause instead of being left as a theory.

### ARCHITECT GETS ITS CORNER BACK

`RR_MainButtons.xml` went `<order>95</order>` to `<order>0</order>` at 0.12.40-dev under a
"company-first means first" reading of master row 821. **Core's Architect is order 1, so order 0
takes the far-left slot off it.**

**A tab bar is muscle memory, and that cost was never weighed.** The owner kept clicking Operations
while reaching for Architect. `<order>5</order>` sits between Architect (1) and Work (10), so
Core's own sort puts Architect back at far left and Operations immediately to its right - the swap,
as one field, with nothing of Core's touched.

**Being first in the bar was never what row 821 asked for.** *Reachability* was, and that half -
all five surfaces opened through `MainButtonDef.Worker.InterfaceTryActivate()` - is built and is
completely independent of this value.

### THE RE-AIM MADE THE CLAIM STRONGER, WHICH IS THE THIRD TIME THAT HAS HAPPENED

`proof-playing-and-help.py` asserted *"the company tab sorts left of Architect"* as `order < 1`.
That claim now encodes the owner's rule and asserts **both** bounds, because a one-sided bound
would pass a value that re-broke the other end: **above** Architect (1) so Architect keeps far
left, and **below** Work (10) so Operations lands in the slot Architect held.

Three plants hold it where there were two: the far right of the bar, **order 0 taking the slot back
off Architect**, and order 1 sorting level with it. **57 of 57 caught.**

### WHAT IS NOT CLOSED, STATED PLAINLY

The owner's narrowing says *"they need to properly spawn in with starting goods"*. The meal def is
changed and the spoilage reason is gone, **but no fix was written for a spawn path, because the
measurement did not isolate one.** The sweep found none of the Store's other consumable grants
either - no `Silver` 200, no `WoodLog` 200, no `Cloth` 120, no `MedicineHerbal` 8, no
`Gun_Revolver`, and 6 `Steel` against 80 - while every shop **fixture** was present. That is either
a real break in the `PlayerStartingThings()` enumeration or goods placed outside the swept band,
and **guessing between those two would have meant editing the arrival path on a hunch**. The
arrival part has two silent `return` sites before it ever calls `base.GenerateIntoMap`, which is
where to look first, and it needs a fresh start on a staged `0.12.80-dev` to measure against.

**No game was launched.** The package could **not** be staged in this checkpoint:
`stage-mod.ps1` refuses while RimWorld is running and the owner's session was live throughout. It
refused correctly - it will not stop a process - so staging is the first action once the game is
closed, and until then the game folder holds `0.12.78-dev`.

**0.12.80-dev. 211 C# files, 92 package files, zero warnings, zero errors. Sixteen checkers pass,
forty-nine proofs hold, 57 of 57 in the re-aimed plant suite.** Two checkers caught the version
bump mid-change - `README.md` and the `About.xml` description still naming 0.12.79-dev - which is
the dated-claim rule doing its job on the same commit that created the claim.
"""

text = io.open(PATH, encoding="utf-8").read()
if u"## Session 2026-10-02 - the tab that stole Architect" in text:
    raise SystemExit("entry already present")
io.open(PATH, "w", encoding="utf-8", newline="").write(text.rstrip("\n") + "\n" + ENTRY)
print("appended 0.12.80-dev session entry")
