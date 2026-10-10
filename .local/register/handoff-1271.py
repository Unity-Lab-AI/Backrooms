# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.71-dev, written after the stage so it quotes a verified hash."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## STATE AT THIS HANDOFF — `0.12.70-dev`, STAGED AND VERIFIED"

NEW = u"""## STATE AT THIS HANDOFF — `0.12.71-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.71-dev  91 files
assembly    F4E367E7C4DBC3C3AF92E7A06FF7CF59E421A397426A3F404206367BF91ACE41
            read back out of the game folder after staging, not from the build
battery     15 checkers - 45 proofs - 633 of 633 plants - 16 suites
tree        no planted fault, porcelain 0
```

### WHY THE OWNER'S SOLO/GROUP START PUT THEM ON THE WORLD MAP

**One clue nobody could walk up to killed the whole level.** Their words: *"i ended up in the world
map with no connection to the back rooms.. i should of been in the back rooms and i dont have a
warp do to get back"*.

`SoloGroupOpening.Open` is five steps. Step 2 -- the coordinate's own map -- threw
`RR_Generation_UnreachableRequiredCell`, so steps 3, 4 and 5 never ran: **the surface door was
never marked, no address was registered, and nobody was moved inside.** Their own guess,
*"i think it was the issue of the building starting door being the same as the warp gate door"*,
is wrong and it is recorded as wrong in `docs/TODO.md` -- the door was never reached at all.

**Three things changed, and one of them is a judgment call worth knowing about:**

| | |
|---|---|
| `RouteTrunk` | The landmark is offered a cell beside the room's **clear, joined-up route cross**, which is reserved for the whole of population. Nothing placed later can take it, so the approach is structural rather than lucky. It falls back when a room has no such cell, and **the probe measures how often that happens** -- zero, across 1,400 layouts |
| the landmark's ring | Reserved once it is placed, exactly as `Populate` already does for the gate anchor |
| **an unreachable clue now WARNS** | It used to throw and take the level with it. One clue nobody can reach is one awkward room; the generator's own written rule says a coordinate that does not exist costs the player the gate that leads to it. **The structural checks around it stay fatal.** This is a deliberate downgrade, not an oversight |

### AND THE SIXTY-TWO POWER WARNINGS WERE MOSTLY OUR OWN RETRY

Core clears its delayed power queue **after** the loop that processes it, so a throw part-way
leaves applied entries queued -- and `ConnectStrayConsumers` rebuilt once per stray consumer, so
it called again and re-applied them. That is where Core's *"there is already a power net here"*
came from, naming the generator on the generator's own cell.

`RebuildPowerNets` returns a bool now, the sweep stops on false, and nothing asks twice.
**The root of the FIRST throw is still unknown** -- it is inside Core, through a 294-mod profile,
and the log only ever printed `(NullReferenceException)`. It logs the full exception now, so the
next launch answers it. **That is not claimed as fixed.**

### WHAT THE OWNER HAS NOT SEEN YET

**Ten checkpoints are built and never run.** The last launch to reach a playable level was
`0.12.67-dev`; `0.12.71-dev` is the first to attempt the solo/group start since the maze landed.

| Checkpoint | Unseen in a game |
|---|---|
| 0.12.68-dev | the braided maze, the raised graph ceiling, **the new packageId** |
| 0.12.69-dev | institutions on a first level, complexes to six rooms, loot in all sixteen archetypes |
| 0.12.70-dev | the assembly as a player-queued bill, and gate control on the components |
| 0.12.71-dev | **the solo/group start reaching a Backrooms level at all** |

**A NEW START IS REQUIRED.** The failed coordinate is recorded `Unavailable` and nothing retries
the opening. Owner's decision when asked, 2026-10-01: *"Just the fix, I'll restart"* -- so a
replacement-coordinate recovery path for `lone_survivor` was **deliberately not built**.
`ReaddressPristineInitialSurvey` still refuses any scenario but `async_industries`.

### A NEW INSTRUMENT, AND WHY IT IS TRACKED

`.local/harness/PdbLine` maps an IL offset from a RimWorld stack trace to a source line, by
reading the portable PDB's sequence points, and prints the assembly MVID so the answer can be
tied to the assembly that actually threw.

It exists because `ValidatePlacedLayoutCore` raised **one key from two places**, the trace carried
`[0x001f8]` and nothing else, and no amount of reading the source can tell those apart. It
answered line 1446 with a matching MVID. **There is one throw site for that key now**, but the
shape recurs, so the tool is tracked rather than thrown away.

```
.local/harness/PdbLine/bin/Release/net8.0/PdbLine.exe <assembly.dll> <Type> <Method> [0xOFFSET ...]
```

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for 0.12.71-dev, after the stage")
