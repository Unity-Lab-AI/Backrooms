# -*- coding: utf-8 -*-
"""Prepend the 0.12.82-dev entry."""
import io

NL = chr(10)
ENTRY = '''## 0.12.82-dev - 2026-10-04 - The corridors bend, a room has five ways out, and the rock is worth digging

- **Corridors are not all straight any more, and there are seven shapes of bend rather than one.**
  A corridor could only run along one axis, which is *why* a link had to join grid-adjacent slots:
  four neighbours, so a measured maximum degree of 4 at every depth and an average of 2.2 to 2.4 —
  one way in and one way out, which is a line with rooms on it. Routes now run through the rock
  lanes between rooms as elbows, as five-leg routes that reach a slot two away, and as a u-turn
  that leaves through the wall facing away from where it is going. A lane is defined by a room's
  own wall rather than by the slot grid, so a route needs nothing but the two rooms' rectangles.
- **A room now has 0 to 16 ways out, averaging 5.** Three mechanisms: a diagonal braid, a reach
  braid to slots two away, and one slot in eight being a junction that takes every link it can —
  which gives a spread rather than moving every room to the same new number. Rooms with only one
  link fell from 6.5% to under 1%.
- **Some rooms have no way in at all, and you find them by mining.** A sealed vault's slot is
  reserved before the maze walk, so nothing can link to it, and a seam of ore runs from it to the
  nearest room that does have a door. The reachability proof now asks its question of rooms that
  *claim* a route; a room with none is reached with a pick.
- **The rock is worth digging.** Ore veins run from every door-onto-nothing, between near rooms a
  corridor does not join, and out of every sealed vault — plus scattered deposits at three times
  Core's own density, read off Core's own scatter step rather than copied. Deep-drillable
  resources including chemfuel are written under the whole coordinate. Nothing is named: the ore
  list is read out of the loaded game, so other mods' ores are included without an adapter.
- **A deep level is no longer 83% bare rock.** Room fill rose from 17.1% to 44.9% at depth, and
  from 46.0% to 57.2% at the first level. The cause was arithmetic — a finer slot grid fills
  *less* space, because the rock between rooms is fixed per boundary — so the grid stops at
  eight slots per axis and the map margin came down from fourteen cells to six. The room cap is
  unchanged.
- **Doors are no longer all at the exact middle of a wall.** That was never a door rule: a
  corridor could only run along a line both room centres shared, so the midpoint was the only cell
  one could arrive at. One function now decides where a straight corridor meets two rooms, and the
  door is wherever that line lands. It also unsealed the grand hall, whose centre sits between its
  two slots and which could previously only lead out along its own row.
- **Rooms stand back to back far more often, and that had quietly regressed.** Only dead ends were
  ever pushed together, and the better-connected maze left few dead ends: measured pairs fell from
  131 to 23 as a side effect of a different feature. Any room may be pushed now, because the push
  proves the move itself — on the map, nothing overlapped, no existing corridor broken, and the
  two rooms really share a wall, or it is undone.
- **The main menu opened on the same picture every single time.** The slide index was pinned to
  zero in two places, so the first thing anyone ever saw — and the backdrop behind every load
  started from the menu — was slide one of six. It is drawn at random now, and the slide list
  moved to one place so the menu and every other surface take the same images from the same source.
- Internal: the validator stopped keeping its own copy of the room-adjacency rule and asks the
  planner, which was a live defect — the planner's half had to grow and the copy would have
  refused every graph it had just learned to build, on load, for every saved coordinate. The
  layout probe stopped keeping a third copy for its own diagnostics, which had begun reporting the
  wrong reason for every refusal.

'''

f = "CHANGELOG.md"
t = io.open(f, encoding="utf-8").read()
head = "# Changelog" + NL + NL
assert t.startswith(head), "changelog head not found"
io.open(f, "w", encoding="utf-8", newline=NL).write(head + ENTRY + t[len(head):])
print("changelog entry prepended")
