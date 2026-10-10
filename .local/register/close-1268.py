# -*- coding: utf-8 -*-
"""0.12.68-dev: the lab name comes out, and a line that snaked becomes a braided maze."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"298068EE470739CF278A6972F3723770BFE2C1631C9B2386C7D65ADCE9E1076E"

ENTRY = u"""
---

## Session 2026-10-01 - the lab name comes out, and the line becomes a maze (0.12.68-dev)

**Verbatim user quotes:** *"take the Unity Lab AI and the Unity AI Lab out of all refrences and
nameing but we will keep the repos as is for now. especially remove the Unitylabai from the mod
information that i see on Rimsort ie the package id and folder naming and such and files, and
there is one issue all the backrooms so far are just one lone strain of perals arangement that
snakes back and forth across the map like one series line... i want them to be mazes like xcrazy
like all levels mazes do you unerstand! lsd crazy shaped mazes and facilitys and :\\"buildings and
neighboorhoods and complexes and shools and hospitals and military and storages need loot inside
of them too"*.

**Files touched:** `Generation/RoomLayoutPlanner.cs`, `Generation/DestinationService.cs`,
`Core/RimroomsMod.cs`, `About/About.xml`, `tools/BuildCommon.ps1`, `tools/stage-mod.ps1`,
`tools/package-files.json`, eleven live documents, `.local/harness/PlannerProbe/Program.cs`,
two proofs, one plant suite.

**Mod register.** Nothing applied. The maze is our own arithmetic and the rename is our own
metadata.

### The name

Chosen at the fork: packageId **`Rimrooms.AsyncIndustries`**, sweep across the shipped package and
the live documentation, `.claude/` and the git remotes untouched. The identity is asserted in six
places that must agree or the build refuses itself -- `About.xml`, `RimroomsMod.PackageId`,
`package-files.json` and three guards in the build and staging scripts, the staging one being
what stops it overwriting another mod's folder.

**Dated records are not rewritten.** `docs/FINALIZED.md` and everything under
`docs/implementation/evidence/` are manifests and receipts of what was true on the day they were
written; editing them would make the archive lie about history to tidy the present. The rename
script **reports every file that still carries the old id and why**, rather than claiming a clean
sweep: fifty-one of them, all dated archives or `.claude/`. `docs/TODO.md` keeps the lab's name
too, because the owner's own words quote it and LAW #0 says those go in verbatim.

**The folder name never carried it.** It is already `Rimrooms - Async Industries`, and so are the
title and the namespace. The packageId was the only thing a player could see.

### The maze, and the owner described the algorithm without seeing it

*"one lone strain of perals arangement that snakes back and forth across the map like one series
line"* **is a description of the code.** `Build` walked the slot grid row-major with alternating
direction, called it *"the serpentine"* in its own comment, and linked room N to room N-1. Dead
ends were hung off it afterwards, so the topology was a corridor with alcoves -- a single route
however many rooms it had, because it was one.

It is now a **randomised depth-first maze** over the slot grid, grown from the hall, then
**braided**: adjacent rooms the walk left unconnected get linked back one in three, which is what
turns a tree -- exactly one route between any two rooms -- into something with loops and junctions
that lie.

**And then the real finding.** `ValidateRooms` ended with `directedEdges > 2 * rooms.Count`. A
connected graph needs `n - 1` edges, so that ceiling allowed **exactly one more: one loop, in the
whole level, at every depth.** The line with alcoves was never a choice the generator made -- **it
was the only shape the validator would accept.** The ceiling is now the grid's own limit, two
undirected edges per room, which is what a four-neighbour slot graph can produce at all; the floor
that guarantees one connected place is untouched.

Measured, before and after, at depth 1: **24 rooms, no hall in the layout actually used, 0
back-to-back pairs** became **35 rooms, the 80-cell hall, 12 pairs**; depth 2 reaches 48 rooms and
53 pairs; depth 3 and beyond fill the 60-room cap.

### The probe had a blind spot and now it does not

The first measurement of the maze reported `refused 0/200` at every depth -- total success -- while
**not one maze had been built.** `TrySelect` falls back to the serpentine when all three real
candidates are refused, and it had caught every seed. The only visible symptom was indirect:
`rooms 24.0` and `widest 40`, which are the fallback's own fingerprint.

**An instrument that can only be read by recognising a number's fingerprint has a blind spot.** It
asks directly now -- how many of the three real candidates pass, and what `ValidateRooms` says
about the ones that do not -- it **describes** a refused layout rather than naming a key that
covers a dozen rules, and **falling back on every seed is a failure**, not a quiet note.

That upgrade is what found both maze defects: the edge ceiling, and before it a hall whose centre
sits between its two slots, so a step from it in any direction but along its own row produced a
link `AreGridNeighbors` refuses. The walk declines such a step now and reaches the slot later from
another parent -- a thing a maze can do and a line cannot.

### Four claims and five plants described a spine that no longer exists

Every refusal was correct and none was relaxed: the chain length, the spur rate, the push call,
the hall's slot arguments and the room-making sites were all rewritten to assert what now
guarantees the same property, and six new plants cover the walk, the braid, the ceiling and the
fallback.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`298068EE470739CF278A6972F3723770BFE2C1631C9B2386C7D65ADCE9E1076E`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 606 of
606** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = (u"## IN PROGRESS - the lab name comes out, and every level becomes a maze "
            u"- 2026-10-01 (0.12.68-dev)")
HEAD_NEW = (u"## The lab name comes out, and every level becomes a maze "
            u"- 2026-10-01 (0.12.68-dev) - PARTLY DONE")
if todo.count(HEAD_OLD) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(HEAD_OLD))
    raise SystemExit(1)
todo = todo.replace(HEAD_OLD, HEAD_NEW, 1)

# Status only, and only on the rows actually finished. Every description keeps every word.
DONE = [
    u'- [~] **"take the Unity Lab AI and the Unity AI Lab out of all refrences and nameing"**',
    u'- [~] **"but we will keep the repos as is for now"**',
    u'- [~] **"especially remove the Unitylabai from the mod information that i see on Rimsort ie the\n  package id and folder naming and such and files"**',
    u'- [~] **"all the backrooms so far are just one lone strain of perals arangement that snakes\n  back and forth across the map like one series line"**',
    u'- [~] **"i want them to be mazes like xcrazy like all levels mazes do you unerstand!"**',
    u'- [~] **"lsd crazy shaped mazes"**',
]
for row in DONE:
    if row in todo:
        todo = todo.replace(row, row.replace(u"- [~]", u"- [x]", 1), 1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO status updated; the loot row stays open and keeps every word")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.67-dev**.", u"| Published | **0.12.68-dev**."),
    (u"SHA-256 `58D9FD124C6B051ED6798B783DF6D006D87F5A731933DB8C92089F08F5656359`",
     u"SHA-256 `" + HASH + u"`"),
]
problems = []
for old, _ in NOW_EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in NOW_EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.68-dev")
