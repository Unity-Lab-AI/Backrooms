# -*- coding: utf-8 -*-
"""The gates were found, and three things were wrong with them."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ENTRY = u"""
## IN PROGRESS - a gate where a normal door should have been - 2026-10-01 (0.12.66-dev)

Owner, verbatim:

> **"okay i got into the backrooms but i found a door that was a gate, but it was where a normal
> door should of been(gates natural need to not also be used and needed as normal doors, becasue
> on the other side was the rest of the backrooms map and when i went to send my pawn through that
> door with a click, it said somthing like : this address is already being used, and anoother door
> said somthing like you cant doo that, request is not valid for this branch, and a differnet
> sdave address alread uses one of these doorsso it must be something about generationg the next
> world map or deeper backrroms idk for sure"**

> **"chack the game if you u need to"**

- [~] **"i found a door that was a gate, but it was where a normal door should of been"**
- [~] **"gates natural need to not also be used and needed as normal doors"**
- [~] **"becasue on the other side was the rest of the backrooms map"**
- [~] **"it said somthing like : this address is already being used"**
- [~] **"anoother door said somthing like you cant doo that, request is not valid for this
  branch"**
- [~] **"and a differnet sdave address alread uses one of these doors"**
- [~] **"so it must be something about generationg the next world map or deeper backrroms idk for
  sure"** - the owner's read is right: the world-map half and the deeper half are two different
  recordings, and only one of them was wired to a way through

---
"""

text = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"\n## TOMBSTONES"
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + ANCHOR, 1))
print("seven rows added, owner words verbatim")
