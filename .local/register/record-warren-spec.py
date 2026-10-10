# -*- coding: utf-8 -*-
"""The owner's revised coordinate-generation direction, verbatim.

Supersedes part of the four answers given earlier the same day. Per LAW, the earlier row is
ANNOTATED rather than rewritten -- the original words stay.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

todo = io.open(TODO, encoding="utf-8").read()

ANCHOR = (u"- [ ] **\"theri 300x300 gate ie the stargate mode that prcedurally generated the "
          u"backrooms of diffent levels with thir natual gate spawns to different levels within\"**")

REVISION = u"""- [ ] **"and everything doesnt have to be square rooms and rectangle halways and u can use walls as pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms and this can propigate depper with the wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches that are found everywher deeper in with wild random events and layouts and spawns to find and loot!!!!!!"** — **OPEN. This REVISES the room-count answer given an hour earlier and it is the better call.** Taken apart into what each clause actually requires:

  | Clause, verbatim | What it means in the generator |
  |---|---|
  | *"everything doesnt have to be square rooms and rectangle halways"* | a room's `Bounds` stays a rect for bookkeeping, but the **carved shape** does not: L, T, cross and ragged-edged rooms, and corridors that change width and bend |
  | *"u can use walls as pillars"* | interior `ThingDefOf.Wall` on a support lattice. **This is the thing that makes grand spaces possible at all** — `RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**, so a roofed span wider than ~13 cells needs something holding it up, and a pillar is exactly that |
  | *"making the 0 level rooms be grand large spaces"* | shallow depth is **few, very large, pillared halls** — not the tidy 10-16 cell boxes the planner builds today |
  | *"leas than 60-100 romms"* | **supersedes the 60-100 dense-warren answer.** Fewer rooms, each far bigger. The warren idea moves inward rather than being dropped |
  | *"this can propigate depper"* | the variation is a **function of depth**, which `BackroomsPalette` and `Derange` already are. Same axis, more of it |
  | *"wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches"* | `CoordinateMaterials` already picks stuff per coordinate; widen it across **every** placed category and let the spread grow with depth |
  | *"found everywher deeper in"* | material variety is discovered content, so what a room is **built from** is part of the loot |
  | *"with wild random events and layouts and spawns to find and loot!!!!!!"* | `AnomalyEventService`, `InhabitantService` and `RoomArchetypeService` all exist; the layouts and the loot density scale inward with the rest |

  **What stands from the four earlier answers:** levels are **300x300**; `threshold_room` / `office_copy` / `return_gallery` stay **unique** while other families **repeat**; **new structural families** are authored as layout and dressing only with **no new ThingDefs**; **4-6 onward gates** per level with `MaximumNaturalDepth` **3 to 6**; **fresh save**, the 60x60 path dropped.

  **What changes:** *"leas than 60-100 romms"* replaces the 60-100 count, and grand pillared halls at shallow depth replace the uniform small-room grid. The 10x10 planning grid at 19-cell spacing was sized for the old shape and is superseded with it — a grand hall does not fit in a 19-cell slot.

"""

if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s)" % todo.count(ANCHOR))
    raise SystemExit(1)

NOTE = (u"- [ ] **SUPERSEDED IN PART, same day, by the row above** -- the *\"leas than 60-100 romms\"* "
        u"direction replaces this row's 60-100 count and its uniform small-room grid. Kept whole "
        u"because the size, family, gate-count, depth-cap and save decisions in it all still "
        u"stand.\n"
        u"- [ ] **\"theri 300x300 gate ie the stargate mode that prcedurally generated the "
        u"backrooms of diffent levels with thir natual gate spawns to different levels within\"**")

todo = todo.replace(ANCHOR, NOTE, 1)
todo = todo.replace(u"## Fifth launch findings — 2026-09-30\n",
                    u"## Fifth launch findings — 2026-09-30\n", 1)

# The revision row goes directly above the row it supersedes.
marker = u"- [ ] **SUPERSEDED IN PART, same day, by the row above**"
if todo.count(marker) != 1:
    print("MARKER PROBLEM")
    raise SystemExit(1)
todo = todo.replace(marker, REVISION + marker, 1)

io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("revised coordinate-generation direction recorded, earlier row annotated not rewritten")
