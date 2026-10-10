# -*- coding: utf-8 -*-
"""The TODO half of the `Pyre` correction. NOW.md took its edit already.

`fix-1276-pyre.py` writes NOW.md before it checks the TODO anchor, so the first run corrected
NOW.md and then refused on a wrong anchor -- the anchor carried a `**` that belongs to the line
above it. **The refusal is the behaviour that is wanted:** it stopped rather than guessing at a
second insertion point, and nothing was written twice.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")
TODO = os.path.join(REPO, "docs", "TODO.md")

now = io.open(NOW, encoding="utf-8").read()
if u"**AND `Pyre` IS NOT CORE**" not in now:
    print("NOW.md DID NOT TAKE THE FIRST EDIT -- run fix-1276-pyre.py instead")
    raise SystemExit(1)
if u"**`Pyre`**. **There is no def" in now:
    print("THE PYRE CLAIM IS STILL ASSERTED IN NOW.md")
    raise SystemExit(1)
print("NOW.md already corrected, verified, not touched again")

ANCHOR = u"  apply to itself:** *\"CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT\"*"
ADD = u"""
- [x] **`Pyre` is not a Core def** - the **second** factual error the owner's challenge found in
  the same handoff, which listed it among *"Core defs confirmed present"*. It lives in
  `Ideology/Defs/ThingDefs_Buildings/Buildings_Ideo.xml`. The mod ships **zero hard
  dependencies**, so nothing may name it. **The first check was run against the installed game
  rather than against Core**, and for a Core-only mod that is the whole distinction - which is
  why it read as a pass. `Grave`, `Sarcophagus` and `ElectricCrematorium` are genuinely Core;
  `Crematorium` does not exist under that name"""

todo = io.open(TODO, encoding="utf-8").read()
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ANCHOR + ADD, 1))

if u"`Pyre` is not a Core def" not in io.open(TODO, encoding="utf-8").read():
    print("ROW NOT WRITTEN")
    raise SystemExit(1)
print("TODO row written verbatim and verified")
