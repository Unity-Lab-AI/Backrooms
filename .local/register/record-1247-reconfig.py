# -*- coding: utf-8 -*-
"""The reconfigurable/deconstructable/minifiable requirement, verbatim, plus what was measured."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"- [x] **\"the map loaded correctly\"**"

ROW = u"""- [x] **"and the store facilities walls floors and all of it have to be reconfigureable deconstructable and minifyable(the minify mod) just like the game with the mods allows"** — **VERIFIED, and it already held; the work was turning an assumption into a check.**

  **Minifiable.** Register row **[128] MinifyEverything** (Workshop `872762753`, family *Facility construction and material access*, stance Optional, firmness Settled, traces RR-FAC / RR-OUT / RR-SPACEFLIGHT / RR-COMPAT). Read its installed assembly rather than the card: it mutates **`ThingDef.minifiedDef`** and **`building.alwaysUninstallable`** for every qualifying def at startup, skipping only natural rock, zero-work defs, mineables and `Smooth*`. **It operates on defs, not on instances.** The facility is built from `ThingDefOf.Wall`, `ThingDefOf.Door` and the authored furniture list — **all Core defs** — so whatever MinifyEverything does to a wall applies to ours identically. This is the existing-content-only rule paying off: a ThingDef of our own would be outside its reach and could not be made minifiable by it at all.

  **Deconstructable.** Every thing the facility places is given `Faction.OfPlayer` before it is spawned, which is all `Designator_Deconstruct` and `Designator_Uninstall` require. Nothing in the scenario path adds, blocks or removes a Deconstruct or Uninstall designation on the facility.

  **Floors removable.** The floor is written with `map.terrainGrid.SetTerrain`, and `TerrainGrid.SetTerrain` records the displaced terrain in `underGrid` whenever the new terrain is `layerable` — `CanRemoveTopLayerAt` needs exactly that. Concrete is layerable, so **Remove Floor works and reveals what Core generated.** The burn's water fill is deliberately ordered before it: Soil goes down first, then Concrete over it, so the under-terrain is Soil rather than water.

  **Reconfigurable, which is the one that needed measuring.** Deconstructing a wall under an unsupported roof collapses it. `RoofCollapseUtility.RoofMaxSupportDistance` is **6.9** and support is found by flood-filling roofed cells within that distance looking for a `holdsRoof` edifice. Replicating that rule against all three layouts:

      RR_AsyncIndustriesStart    roofed 884   walls 540   UNSUPPORTED 0
      RR_FurnitureStoreStart     roofed 686   walls 334   UNSUPPORTED 0
      RR_SoloGroupStart          roofed  25   walls  24   UNSUPPORTED 0

  **Not one unsupported roof cell in any layout.** The Store's outer room is 34x30, far wider than a 6.9 span, and it is supported because the inner rooms' walls stand inside it. That was luck rather than design, so it is now a proof claim: any future room that roofs a span nothing holds up will fail the proof instead of dropping a roof on the player's pawns the first time they remodel.

- [x] **"the map loaded correctly"**"""

if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrences" % todo.count(ANCHOR))
    raise SystemExit(1)

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW, 1))
print("reconfigurable requirement recorded")
