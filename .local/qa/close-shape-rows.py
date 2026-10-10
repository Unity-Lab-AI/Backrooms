# -*- coding: utf-8 -*-
"""Close the room-shape/pillars row and the supersession record under it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"and everything doesnt have to be square rooms and rectangle halways',
  'CLOSED 0.12.96-dev — **the owner was right that most of this was already done, and checking it '
  'found one real defect.** All eight clauses measured against the source rather than taken on '
  'trust. '
  '**"not square rooms and rectangle halways"** — the `Bounds` rect stays for bookkeeping and the '
  '**carve** changes: rock is left standing inside a room and **only in the corners**, never on '
  'the centre cross and never at an edge, so a straight walk from any doorway to any other stays '
  'clear whatever the room\'s size. '
  '**"u can use walls as pillars"** — `RoomLayoutPlanner.PillarCells` is the lattice and **nowhere '
  'else derives it**, because the planner has to prove the room is still walkable with the pillars '
  'in it before any map exists. Spacing comes from `RoofCollapseUtility.RoofMaxSupportDistance`, '
  'measured at **6.9** from the installed assembly, so a roofed span wider than ~13 cells has '
  'something holding it up. Two independent derivations of one lattice is the defect that stopped '
  'every coordinate generating for thirty-nine checkpoints, which is why it is one place. '
  '**"0 level rooms be grand large spaces"** and **"leas than 60-100 romms"** — `MinSlotsPerAxis` '
  'is **6**, so depth 1 is a **36-slot grid with rooms about 34 cells across**, and it was tuned '
  'against the owner\'s own walkthrough: at 3 slots the rooms were eighty cells across and the '
  'owner said *"not enough rooms"*. Deeper is more rooms, smaller and tighter. The 10x10 grid at '
  '19-cell spacing is superseded with the shape it was sized for. '
  '**"wild variatiosn of material typeds in all items equaipment walls floors lights furnature and '
  'benches"** — done, and more carefully than the row asked. Walls are chosen **per room** past '
  '`CoherentDepth`, measured by **distance from the spawn hall** rather than raw depth, because '
  'testing `coordinate.Depth` made every room at level 0 take the band\'s wood and the whole level '
  'read as one corridor — the level the owner walked and called *"nothing but what it currently '
  'is"*. Per **room** and not per cell, because a wall whose every cell is a different stone is a '
  'patchwork. And the arrival hall keeps the yellow look, per *"the normal yellow backrooms look '
  'isnt the whole floor but the main spanw room"*. '
  '**AND THE DEFECT THIS CHECK FOUND:** the ring around a room was built from the room\'s own '
  'material while **the pillars standing inside that same room used the level band\'s** — stone '
  'walls, wooden columns, in the one room big enough for anybody to notice. A pillar *is* a wall; '
  'it is literally `wallDef`. **Nothing asserted the material, which is exactly how it drifted** — '
  'every claim around it covered *where* the pillars go. Fixed, nothing structural changed because '
  'any wall stuff holds a roof, and now claimed: `proof-coordinate-layout.py` holds it and '
  '`plant-coordinate-layout.py` lands **159 of 159** with a plant that puts it back.'),

 ('- [ ] **SUPERSEDED IN PART, same day, by the row above**',
  'CLOSED 0.12.96-dev AS THE RECORD IT IS. This row carries no work: it states that the *"leas '
  'than 60-100 romms"* direction replaced its own 60-100 count and its uniform small-room grid, '
  'and it was *"kept whole because the size, family, gate-count, depth-cap and save decisions in '
  'it all still stand"*. All of those still stand and are asserted elsewhere — 300x300, the three '
  'unique families against the repeating ones, 4-6 onward gates, the depth cap and the save '
  'decisions. **A supersession is a record, and a record cannot be completed**, so it was holding '
  'a checkbox that could never be ticked. Archived as the history it is, which is where the '
  'superseding row above now points.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:85]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
