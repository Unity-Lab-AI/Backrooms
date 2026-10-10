# -*- coding: utf-8 -*-
"""NOW.md for 0.12.47-dev. Anchors asserted first, one write at the end."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

EDITS = [
    (u"| Published | **0.12.46-dev**.", u"| Published | **0.12.47-dev**."),

    (u"SHA-256 `1C0348B2D59F8B58743BE50BEA7AA67C6D2E79E832A10CD08497E6E5154E8455`",
     u"SHA-256 `85B6769552B8D94641A5DA8B93BB9514715FE90AE9087BC0106C528F60ECE540`"),

    (u"| Game launches | **THREE, all by the owner on 2026-09-30.** They have found **eight "
     u"defects** and every one was ours. Nothing found so far has been a mod conflict. See *What "
     u"the first launch found*. The staged copy is current at this checkpoint, hash-verified |",
     u"| Game launches | **FOUR, all by the owner on 2026-09-30.** They have found **ten "
     u"defects** and every one was ours. **Still not a single mod conflict.** The fourth launch "
     u"is also the first whose evidence came from the **running game** rather than from the log "
     u"alone: the owner said *\"you can use the api mod you have that we installed last so u can "
     u"see wtf rimworld is doing\"*, so RimBridgeServer 2.1.1 in direct mode, read-only, against "
     u"their own launched process. See *What the fourth launch found*. The staged copy is current "
     u"at this checkpoint, hash-verified |"),

    (u"grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 505 done",
     u"grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 510 done"),

    (u"## DO THIS FIRST — read the play-testing log, then launch again",
     u"""## DO THIS FIRST — read the play-testing log, then launch again

### The bridge is available now, and it changes how to diagnose

Owner direction, 2026-09-30, verbatim: **"you can use the api mod you have that we installed last
so u can see wtf rimworld is doing"**. **RimBridgeServer 2.1.1 is installed and it answered
questions in one call that would have taken a launch each to guess at.**

Direct mode, and the only inputs are the owner's own log and process:

```
grep -n "RimBridge" "$USERPROFILE/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
    [RimBridge] GABP server running standalone on port <port>
    [RimBridge] Bridge token: <token>
```

`.local/qa/bridge.py` is the scratch client for this — `list`, `call <tool> '<json>'`, and
`scan <minx> <minz> <maxx> <maxz>` for a cell-by-cell rect survey. The shipped
`tools/qa/rimbridge_readonly.py` keeps its five-tool allowlist and its fail-closed PID/log
pairing; the scratch client is for diagnosis, not for evidence.

The reads that earned their keep: `rimworld/get_cell_info` (what is actually in a cell — terrain,
roof, every thing, its class and hit points), `rimworld/list_colonists`, `rimworld/list_letters`,
`rimworld/get_game_info`, `rimworld/get_ui_layout` and `rimworld/take_screenshot` with
`clipTargetId`, `rimworld/list_selected_gizmos`.

**Only the owner launches. The bridge is read-only against a process they started, and they close
it themselves.** `kill` the game only when the owner says so — they did, verbatim: *"and when ur
ready to redo rimsort kill rimworld .exe and build the mod correctly in local with other mods and
then ill start rimsort"*.

### What the fourth launch found

**Two defects, both consequences of 0.12.46-dev correctly handing map generation back to Core** —
which was the right fix and had a bill nobody paid until a real launch.

The owner diagnosed it themselves before any code was read: *"i think the issue was there was shit
where it planned on putting the store and pawns so it errored it needs a like a burn into place
functiions to carve everyhting out and cut everything down and fill in with soil where water is
unmder where the store needs to propigate before game start"*.

**Measured in the live game.** `Player.log` named the throw at `(133, 0, 135)`; the bridge found a
**Granite Mineable with 900 hit points** there; a sweep of all **1020** footprint cells found
**164 Marble and 70 Granite formations, 177 cells of natural rock roof, ~440 plant cells, 34 cells
of rubble and chunks, and two monkeys**. `list_colonists` returned **0**. **234 of 1020 cells held
natural rock** — the facility had no chance and threw on its very first cell.

| | What went wrong | The fix |
|---|---|---|
| 9 | `Build` **refused** ground Core generated instead of preparing it | prevention **plus** the burn — see below |
| 10 | the arrival step **threw out of Core's `GenStep_ScenParts`**, so Core's whole scenario step died: **no colonists, no supplies** | fall back to `base.GenerateIntoMap` and never throw |

**Defect 10 is the important one to carry forward.** `MapGenerator.GenerateContentsIntoMap`
abandons a gen step at its first exception. **Anything this mod does inside a Core gen step must
not throw**, or the player loses everything else that step was going to do for them.

**The fix for defect 9 has two halves, and the first is why the map still looks like a map.**
`GenStep_RocksFromGrid` spawns a formation wherever `MapGenerator.Elevation` exceeds **0.7**, and
it runs at order 200; Core builds that grid at order 10. `RR_HeadquartersTerrain` moved from
**order 5 to order 100**, between them, and lowers site elevation to **0.55** — so the rock is
**never generated**, rather than carved out afterwards into a 234-cell crater. Then
`HeadquartersBuilder.BurnIntoPlace` runs **before a single wall** and carves, cuts, clears natural
roof and fills water with soil.

### Useful Core numbers, measured from the install this build targets

```
ElevationFertility   10      RocksFromGrid       200   (rock above elevation 0.7)
Terrain             210      Roads               390
MutatorCritical     500      MutatorNonCritical  700
ScatterRuinsSimple  750      ScatterShrines      750   (both respect UsedRects)
FindPlayerStartSpot 850      (only picks when PlayerStartSpot is invalid)
ScenParts           875      Plants              900
ScatterGeysers      950      RockChunks          970
Snow               1150      Animals            1200      Fog   1500
```

`RR_HeadquartersTerrain` is **100**, `RR_HeadquartersFacility` is **800**.
`RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**.

"""),

    (u"### The pattern in all eight, because it is the same pattern",
     u"""### The pattern in all ten, because it is the same pattern"""),

    (u"| 8 | F12, measured against Core alone | collided with HugsLib's log publisher |",
     u"""| 8 | F12, measured against Core alone | collided with HugsLib's log publisher |
| 9 | the footprint, assumed empty because our own generator made it | refused 234 cells of Core's rock |
| 10 | Core's `GenStep_ScenParts`, aborted by our throw | **no colonists and no supplies at all** |"""),

    (u"### What a fourth launch should settle",
     u"""### What a FIFTH launch should settle

- the Store stands on the owner's tile and map size, on **open ground with no rock crater**, and
  the rest of the tile keeps its biome character
- **colonists and starting supplies are present** — the thing that measured zero
- select a wall: **Deconstruct and Uninstall both offered** (`rimworld/list_selected_gizmos` will
  answer this without guessing), and Remove Floor works on the concrete
- deconstruct an interior wall and **no roof collapses**
- the back-room door nobody built, and the ways deeper or out to a world tile behind it
- the Operations tab on Backslash, with no HugsLib double-fire

### What the fourth launch settled, and the old list it replaces"""),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("NOW.md: %d edits applied in one write" % len(EDITS))
