# -*- coding: utf-8 -*-
"""0.12.76-dev: the goon squad. Owner words, verbatim, every clause its own row."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - the goon squad, and never losing the game - 2026-10-01 (0.12.76-dev)

Owner, verbatim:

> **"a the company clear squad when all pawns incompacitated.. they should arrive do a full sweep
> of every rroom on the reall world map, disconnect the gate and burry the dead or incenerate on
> propery might need to build graves in the moment then they go through the whole facility fix
> broken walls and equipment leave supplies food asurvival meals like starting all over again but
> this happens in game with the player never losing the game. but this only happens for the lab
> secnerio for now we will figure out how to impliment it in other scenreios later and that can be
> differed short version:if u die all pawns incompacitated... \\"The Company\\" sends in a goon squad
> kills every thing takes the dead and leeaves three new pawns to run the facility they have keeys
> to all doors on map and can turn off the game and leave supplies and can kill anything without
> dying and use and or build a crematoryium and or graves to bury everthing dead then they haul
> everything and repair and shut down the gate and haull abay all bonds printed that are on the map
> u lose it all and 25M is deducted from account for \\":restocking the pedycash\\" upto 25M from
> account never going under 0 dollars in account andf yes do those three things you listed as
> well"**

**This expands `Company/FacilityRelief.cs`, which already exists** from the owner's 2026-09-29
direction: *"sending clean up teams to your base with all access passses to wipe the facitly of
all hostals and requisition a new basic team supplies drops like a fresh start of sorts so that
facilities never die"*. Today it clears hostiles, drops the corporation's crate at full scale,
lands **five** staff and clears `Find.GameEnder.gameEnding`. Every row below is a gap against the
new direction.

- [~] **"a the company clear squad when all pawns incompacitated"** - the existing trigger fires on
  **no living staff anywhere** and deliberately excludes downed, with a written reason: *"Downed is
  also not dead. A branch whose staff are all unconscious is in trouble, not gone."* **The owner
  is overruling that**, and it is recorded here because the old reasoning is now wrong rather than
  forgotten
- [~] **"they should arrive do a full sweep of every rroom on the reall world map"**
- [~] **"disconnect the gate"**
- [~] **"and burry the dead or incenerate on propery"**
- [~] **"might need to build graves in the moment"**
- [~] **"then they go through the whole facility fix broken walls and equipment"**
- [~] **"leave supplies food asurvival meals like starting all over again"**
- [~] **"but this happens in game with the player never losing the game"**
- [~] **"but this only happens for the lab secnerio for now"**
- [~] **"we will figure out how to impliment it in other scenreios later and that can be
  differed"** - **recorded here and NOT in `docs/DEFERRED.md`**, which is closed with zero rows
  and the standing instruction is never to add one. Scoped to the lab start; the other two
  scenarios are owner-excluded for now
- [~] **"if u die all pawns incompacitated..."**
- [~] **"\\"The Company\\" sends in a goon squad kills every thing"**
- [~] **"takes the dead"**
- [~] **"and leeaves three new pawns to run the facility"** - the existing relief lands **five**
- [~] **"they have keeys to all doors on map"**
- [~] **"and can turn off the game"**
- [~] **"and leave supplies"**
- [~] **"and can kill anything without dying"**
- [~] **"and use and or build a crematoryium and or graves to bury everthing dead"**
- [~] **"then they haul everything"**
- [~] **"and repair"**
- [~] **"and shut down the gate"**
- [~] **"and haull abay all bonds printed that are on the map u lose it all"**
- [~] **"and 25M is deducted from account for \\":restocking the pedycash\\""**
- [~] **"upto 25M from account never going under 0 dollars in account"**
- [~] **"andf yes do those three things you listed as well"** - staff **prior exposure** on an
  expedition, the **review** workflow (the fourth of analyse/interview/compare/review), and
  verifying the stranded-crew rows against `Company/LostPawnRegister.cs`
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))
print("TODO opened for 0.12.76-dev: 25 rows, every clause verbatim")
