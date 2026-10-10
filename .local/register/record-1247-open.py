# -*- coding: utf-8 -*-
"""Open the fourth-launch findings in docs/TODO.md, verbatim, before any code moves."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"

ROW = u"""## Fourth launch findings — 2026-09-30

Owner, verbatim: **"i did a store start the map loaded correctly but i had pop up company could
not finish startup company placement stopped... so wtf is up with this??? also the starting store
structure was not built and i have no pawns on the map to control"**

And, verbatim: **"you can use the api mod you have that we installed last so u can see wtf
rimworld is doing"** — done. RimBridgeServer 2.1.1, direct mode, port read from the owner's own
live log, read-only calls against the running game (PID 43756). Every number below is measured
from the live map, not inferred.

- [~] **"i had pop up company could not finish startup company placement stopped... so wtf is up with this???"** — **CAUSE FOUND, measured in the live game.** The letter is ours (`RR_Start_Failed` + `RR_Start_PhysicalSetupFailed`) and it is telling the truth. `HeadquartersBuilder.Build` threw on its **very first cell**: `Headquarters wall intersects generated structure at (133, 0, 135)`. `rimworld/get_cell_info` at that cell returns a **`Granite` `RimWorld.Mineable` with 900 hit points** — a natural rock formation.

  **This is 0.12.46-dev's own consequence, and it was predictable.** Core generates the map now, so the footprint lands on real terrain instead of the flat Soil our retired generator handed it. A `rimworld/get_cell_info` sweep of all **1020 footprint cells** (x 133..166, z 135..164 — the Store's outer room offset onto the owner's 300x300 map) found:

      Marble  (Mineable)   164 cells      Plant_Grass          107 cells
      Granite (Mineable)    70 cells      Plant_ShrubLow        86 cells
      Filth_RubbleRock      29 cells      Plant_TallGrass       84 cells
      ChunkGranite           6 cells      Plant_Alocasia        44 cells
      ChunkMarble            5 cells      trees/bushes/reeds   ~80 cells
      Monkey                 2 cells      natural rock roof    177 cells

  **234 of 1020 cells held natural rock.** The build did not have a rare collision; it had no chance. `Build` refuses a footprint it does not own instead of preparing it — the exact inverse of what every vanilla structure gen step does.

  **Owner direction for the fix, verbatim:** *"i think the issue was there was shit where it
  planned on putting the store and pawns so it errored it needs a like a burn into place
  functiions to carve everyhting out and cut everything down and fill in with soil where water is
  unmder where the store needs to propigate before game start"*.

- [~] **"the starting store structure was not built"** — same root cause. `Build` throws on the first blocked cell and re-throws out of `Generate`, so `receipt.setupComplete` is never set, nothing after the first wall cell is placed, and `PostGameStart` correctly reports a failed startup.

- [~] **"i have no pawns on the map to control"** — **a SECOND, independent defect, and the one that made the game unplayable rather than merely wrong.** `ScenPart_RimroomsArrival.GenerateIntoMap` **throws** when the receipt is not complete. That method is called from Core's `GenStep_ScenParts`, and `MapGenerator.GenerateContentsIntoMap` abandons a gen step at its first exception. The log shows it: `Error in GenStep: [Rimrooms] Native arrival requires the prepared headquarters receipt.` **Core's entire scenario step died, so the player got no colonists and no starting supplies.** `rimworld/list_colonists` on the live map returns `count: 0`, and `rimworld/list_letters` returns exactly one letter — ours.

  **This is the eight-defect pattern again.** We subclass a Core ScenPart and then refuse to do Core's job when our own addition is not ready. A subclass of `ScenPart_PlayerPawnsArriveMethod` must never leave the player worse off than Core alone would have.

- [x] **"the map loaded correctly"** — **0.12.46-dev confirmed good by the owner and by measurement.** The footprint offset resolves to x 133 / z 135, which is only consistent with a **300x300** map, exactly what the owner picked; and the footprint sweep found biome plants, marble, granite, rubble, palms, teak, bamboo, reeds and wildlife. The barren-flat-dirt defect is gone.

---

"""

if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrences" % todo.count(ANCHOR))
    raise SystemExit(1)

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("fourth-launch findings opened")
