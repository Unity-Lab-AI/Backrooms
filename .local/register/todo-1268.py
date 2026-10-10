# -*- coding: utf-8 -*-
"""Two asks: the lab name comes out of the shipped package, and every level becomes a maze."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ENTRY = u"""
## IN PROGRESS - the lab name comes out, and every level becomes a maze - 2026-10-01 (0.12.68-dev)

Owner, verbatim:

> **"take the Unity Lab AI and the Unity AI Lab out of all refrences and nameing but we will keep
> the repos as is for now. especially remove the Unitylabai from the mod information that i see on
> Rimsort ie the package id and folder naming and such and files, and there is one issue all the
> backrooms so far are just one lone strain of perals arangement that snakes back and forth across
> the map like one series line... i want them to be mazes like xcrazy like all levels mazes do you
> unerstand! lsd crazy shaped mazes and facilitys and :\\"buildings and neighboorhoods and
> complexes and shools and hospitals and military and storages need loot inside of them too"**

- [~] **"take the Unity Lab AI and the Unity AI Lab out of all refrences and nameing"**
- [~] **"but we will keep the repos as is for now"** - the remotes, the org and the repo names are
  untouched; this is the shipped package and its text only
- [~] **"especially remove the Unitylabai from the mod information that i see on Rimsort ie the
  package id and folder naming and such and files"**
- [~] **"all the backrooms so far are just one lone strain of perals arangement that snakes back
  and forth across the map like one series line"** - **the owner is describing the algorithm
  exactly.** `RoomLayoutPlanner.Build` walks the slot grid row-major with alternating direction
  and calls it a *serpentine*; it is one line that snakes, by construction
- [~] **"i want them to be mazes like xcrazy like all levels mazes do you unerstand!"**
- [~] **"lsd crazy shaped mazes"**
- [~] **"and facilitys and buildings and neighboorhoods and complexes and shools and hospitals and
  military and storages need loot inside of them too"**

---
"""

text = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"\n## TOMBSTONES"
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + ANCHOR, 1))
print("seven rows added, owner words verbatim")
