# -*- coding: utf-8 -*-
"""The thirteenth launch worked, and the owner walked the whole floor. Five rows, verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ENTRY = u"""
## IN PROGRESS - the floor is a string of pearls - 2026-10-01 (0.12.65-dev)

Owner, verbatim, first message:

> **"okay its working. if u check the game i explored the full map i think and i never found any
> natural cates to the world map tiles or natural portals to deep into the backrroooms so its
> great it working i just never found any other gates with option to \\"walk through\\" adding them
> to the loaded maps of my game play through"**

Owner, verbatim, second message:

> **"and another thing as you can see the hall ways are just rectangles and arnt correctly the
> themed color and materials and there wasnt enough \\"people-food\\" in the back rooms need to be
> able to survive a bit if it was a solo start. and i see the whole map is almost like a string of
> pears. when it should just be basicly \\"rooms\\" as halways with the exact shit thats in the
> rooms... get it? do you need to check prep work on the Universe of the backrooms?"**

- [~] **"i never found any natural cates to the world map tiles or natural portals to deep into
  the backrroooms"**
- [~] **"i just never found any other gates with option to \\"walk through\\" adding them to the
  loaded maps of my game play through"**
- [~] **"the hall ways are just rectangles and arnt correctly the themed color and materials"**
- [~] **"there wasnt enough \\"people-food\\" in the back rooms need to be able to survive a bit if
  it was a solo start"**
- [~] **"i see the whole map is almost like a string of pears. when it should just be basicly
  \\"rooms\\" as halways with the exact shit thats in the rooms"**
- [~] **"do you need to check prep work on the Universe of the backrooms?"** - **yes, and it
  exists.** `docs/UNIVERSE_ADAPTATION.md` says a coordinate is *"a stable, seeded expedition site
  made of rooms and routes"* and to *"reuse recognizable room categories, materials, fluorescent
  lighting, service infrastructure, and furniture as the baseline"* with a *"repeated hall"* as an
  intentional spatial change. `docs/PROCEDURAL_SPACE_CONTRACT.md` adds *"Unseen connections appear
  as unknown, not as empty corridors."* **The owner's correction is what the prep work already
  said**: a corridor is a room, with the same floors, walls, lights and contents, not a carved
  tunnel between rooms.

---
"""

text = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"\n## TOMBSTONES"
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + ANCHOR, 1))
print("six rows added, owner words verbatim")
