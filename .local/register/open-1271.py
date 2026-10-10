# -*- coding: utf-8 -*-
"""0.12.71-dev: the solo/group start left everybody on the surface. Owner words, verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - the solo/group start never got inside - 2026-10-01 (0.12.71-dev)

Owner, verbatim:

> **"read now.md to resume. i just started it up and tried solo/group start and for some weird
> reason i ended up in the world map with no connection to the back rooms.. i should of been in
> the back rooms and i dont have a warp do to get back.. i think it was the issue of the building
> starting door being the same as the warp gate door, but im suppose to find the gate to the world
> map in the backrooms before i can get my pawns to the world map tile i selected at game and
> world setup,.... so wtf is up can u fix this easily by checking the game running"**

- [~] **"i just started it up and tried solo/group start and for some weird reason i ended up in
  the world map with no connection to the back rooms"**
- [~] **"i should of been in the back rooms and i dont have a warp do to get back"**
- [~] **"i think it was the issue of the building starting door being the same as the warp gate
  door"** - **the hypothesis is wrong and the log says so.** The door was never reached. Step 2 of
  the opening, the coordinate's own map, failed; steps 3 and 4 that mark the door and register the
  way out never ran
- [~] **"but im suppose to find the gate to the world map in the backrooms before i can get my
  pawns to the world map tile i selected at game and world setup"** - that is what the start
  already does, and the reason they saw none of it
- [~] **"so wtf is up can u fix this easily by checking the game running"**

### What the log said, and what pinned it

`RR_Generation_UnreachableRequiredCell` out of `ValidatePlacedLayoutCore`, which **throws that one
key from two different places**. The stack carried `[0x001f8]` and nothing else, so the source
could not answer which. `.local/harness/PdbLine` reads the portable PDB's sequence points and
resolved it to **line 1446** -- the clue landmark's approach, not the office or return cell -- with
the assembly MVID matching the one in the stack trace.

Also in the same log, from the same generation: **sixty-two power-net rebuild failures** and one
`Tried to register trasmitter ... but there is already a power net here`.
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))
print("TODO opened for 0.12.71-dev, owner words verbatim")
