# -*- coding: utf-8 -*-
"""The ninth launch WORKED, and the owner walked a level. This is what they found."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ROW = u"""## IN PROGRESS — the first walked level — 2026-09-30 (0.12.61-dev)

**IT WORKED. The owner is in the Backrooms for the first time, on the ninth launch:**
**"okay it fucking worked!!! im in the backrooms!!! but issues..."**

Owner, verbatim, in full:

> **"1. i explored it all and there were zero weird events or people, there were zero portals to
> be discovered. as in the didfferent scernios they all should have an additional portal to other
> maps and levels... and i love the backrooms level i looked at and went into one issue not enough
> rooms and not enough loot and not enough weird stuff like a room with a lost person or a room
> full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or
> tool sheed or weapons locker with loot and supplies anssd furnuture all ot of it randomly like
> and scary freaky spooky like. . its currently really nice but the furnature is only in the four
> corners of the rooms that nots very random. 2. there is a weird route thing name a self in one of
> the rooms and this is kinda weird and odd and we probably havent gotten to a routing system yet
> for emergency exit and glow pods with the company start but lets try and fix this so the normal
> yellow backrooms look isnt the whole floor but the main spanw room and going deeping in can mean
> the numner of branch hallways and rooms distancing from the main portal spawn in the back rooms
> continuw on into the map with variations and oddity and events and locations and places that vary
> more even on the first level. cant have a whole backrooms be nothing but what it currently is if
> u look at the game and where Gee is at it needs to be more maze liek and scary inducing beyond
> the main starting themed opening room and have more natural portals guaranteeed so the backrooms
> never ends \\"persay\\""**

> **"every backrooms instance need a protal to the world map and a deeper in portal"**

**MEASURED FROM THE LIVE MAP, so the scale of the gap is known rather than guessed.** The minimap
shows **nine rectangular rooms on straight corridors**, and the planner explains it exactly:
`slots = MinSlotsPerAxis + (depth - 1)` is **3** at depth 1, so a 3x3 grid of nine slots, of which
`chain` takes six and spurs take three. **Nine rooms, all boxes, one serpentine corridor.**

- [ ] **"every backrooms instance need a protal to the world map and a deeper in portal"** — a hard guarantee of **two** natural gates per instance: one out to the world map, one deeper. Not a chance roll.
- [ ] **"there were zero portals to be discovered"** and **"have more natural portals guaranteeed so the backrooms never ends persay"**
- [ ] **"not enough rooms"** — nine is not a Backrooms level
- [ ] **"it needs to be more maze liek and scary inducing beyond the main starting themed opening room"**
- [ ] **"the normal yellow backrooms look isnt the whole floor but the main spanw room"**
- [ ] **"going deeping in can mean the numner of branch hallways and rooms distancing from the main portal spawn in the back rooms continuw on into the map with variations and oddity and events and locations and places that vary more even on the first level"**
- [ ] **"not enough loot"**
- [ ] **"not enough weird stuff like a room with a lost person or a room full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or tool sheed or weapons locker with loot and supplies anssd furnuture"**
- [ ] **"all ot of it randomly like and scary freaky spooky like"**
- [ ] **"the furnature is only in the four corners of the rooms that nots very random"**
- [ ] **"zero weird events or people"**
- [ ] **"there is a weird route thing name a self in one of the rooms and this is kinda weird and odd"** — owner's own read: *"we probably havent gotten to a routing system yet for emergency exit and glow pods with the company start but lets try and fix this"*

---

"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("thirteen rows recorded, every one in the owner's own words")
