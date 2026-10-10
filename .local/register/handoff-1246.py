# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.46-dev, written for a compaction.

Every anchor asserted before anything is written, one write at the end -- a `sub()` that throws
part way leaves the file untouched and loses the edits before it silently.

Measured rather than carried:

    branch       feature/bug-testing   (the cascade is TEN refs, not eight)
    C# files     199
    package       90
    checkers      13   (12 tools/check-*.py + tools/research/audit-gate0.py)
    proofs        40
    assembly     1C0348B2D59F...E8455, read from the live build after the determinism run
    queue         42 open / 45 partial / 505 done
    master        66 open / 190 done
    launches      THREE, all by the owner on 2026-09-30
    versions     all four sites agree on 0.12.46-dev
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

EDITS = [
    # The state table's launch count is the single most important line in the file now.
    (u"| Game launches | **ONE, by the owner, 2026-09-30.** It found three defects in the first "
     u"minute and all three were ours. See *What the first launch found*. The staged copy is "
     u"current as of this checkpoint |",
     u"| Game launches | **THREE, all by the owner on 2026-09-30.** They have found **eight "
     u"defects** and every one was ours. Nothing found so far has been a mod conflict. See *What "
     u"the first launch found*. The staged copy is current at this checkpoint, hash-verified |"),

    (u"| Checkers | **THIRTEEN**, all passing.",
     u"| Checkers | **THIRTEEN**, all passing. **Two of them caught me during 0.12.46-dev**: "
     u"`check-compliance.py` flagged a patch for containing `PatchOperationReplace` **in the "
     u"comment explaining why a replace is wrong** (it strips XML comments now), and "
     u"`proof-starts.py` asserted the exact thing being reversed. **A checker that tests for "
     u"mention rather than assertion has now cried wolf four times.**"),

    # The batch heading is stale: the build is done and this is the play-testing phase.
    (u"## DO THIS FIRST — re-stage the package, then launch it",
     u"""## DO THIS FIRST — read the play-testing log, then launch again

**The build is done. This is the play-testing phase**, on `feature/bug-testing`, and it has
already been worth more than any equivalent stretch of building: **three launches, eight defects,
every one ours.**

**The staged copy is current** — 0.12.46-dev, hash-verified against the build. Nothing to re-stage
unless the build moves.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

**Only the owner launches, through RimSort.** Standing instruction, unchanged.

### The pattern in all eight, because it is the same pattern

**Seven of the eight were this mod overriding or replacing something the player or the base game
already owned**, and the eighth was the mod inheriting global state it never set:

| # | What was overridden | What it produced |
|---|---|---|
| 1 | Unity's IMGUI draw state, never reset | a blank page with an empty log |
| 2 | the scroll view swallowed the confirm checkbox | Start refused and the reason was off screen |
| 3 | the same for the company name field | *"there is no box to type in"* |
| 4 | `GameInitData.mapSize` | a 50x50 map: *"a super micro blocked in area"* |
| 5 | `GameInitData.mapGeneratorDef` | *"bare dirt not even vegitation"* |
| 6 | the terrain grid, every cell | the tile's character erased |
| 7 | `SoloGroupOpening` gated on `insideStart` | the Store had no gate to enter |
| 8 | F12, measured against Core alone | collided with HugsLib's log publisher |

**The rule that falls out of it, and it is the thing to carry into the next launch: do not replace
what the player or the base game already owns. Add to it.** Every fix in 0.12.45 and 0.12.46 was
the same move — stop overriding, start contributing. The map generator patch is
`PatchOperationAdd` for exactly this reason.

### What a fourth launch should settle

- **the map is yours**: your chosen size, your chosen tile, and **what Map Preview showed you**.
  Rocks, plants, water, biome terrain all present; the facility centred with real ground round it.
- **a door in the Store's back room that nobody built** — permanently open, to a seeded
  coordinate, with an event announcing it.
- **through it**, and then onward: ways deeper, or out to a world tile, found by surveying
  doorways.
- **the Operations tab on Backslash**, and no double-fire with HugsLib.

**And the standing ask, which has paid for itself three times: if anything fails silently, that is
the bug.** The setup page names its own draw faults, gate refusals name themselves, crew refusals
name the person. Silence is the thing worth reporting.

---

## The re-stage command, for when the build does move"""),
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
print("handoff: %d edits applied in one write" % len(EDITS))
