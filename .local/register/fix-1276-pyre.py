# -*- coding: utf-8 -*-
"""`Pyre` is Ideology, not Core. Second factual error in the 0.12.76-dev handoff.

Found by the same owner challenge that found the first: *"are u shure zero goon squad code is
written weve gone over this before by a different name"*. The handoff listed `Pyre` among
**"Core defs confirmed present"**. It is not in Core at all --
`Ideology/Defs/ThingDefs_Buildings/Buildings_Ideo.xml` -- and this mod ships with **zero hard
dependencies**, so naming it in a def or a hard lookup would be a dependency on a DLC the player
may not own.

The original check was run against the *installed game* rather than against *Core*, which is the
distinction that matters for a Core-only mod and the reason the first pass read as a pass.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")
TODO = os.path.join(REPO, "docs", "TODO.md")

OLD = (u"Core defs confirmed present: **`Grave`**, **`Sarcophagus`**, "
       u"**`ElectricCrematorium`**, **`Pyre`**. **There is no def called `Crematorium`** — "
       u"it is `ElectricCrematorium`.")

NEW = (u"Core defs confirmed present, counted against **Core only** and not against the installed "
       u"game: **`Grave`**, **`Sarcophagus`**, **`ElectricCrematorium`**. **There is no def called "
       u"`Crematorium`** — it is `ElectricCrematorium`. **AND `Pyre` IS NOT CORE** — it is "
       u"`Ideology/Defs/ThingDefs_Buildings/Buildings_Ideo.xml`, so this handoff was wrong to list "
       u"it and nothing may name it: the mod has **zero hard dependencies** and a player without "
       u"Ideology must lose nothing. Burial is `Grave`; the fire is `ElectricCrematorium` if one "
       u"stands, and otherwise destruction, which is *\"incenerate on propery\"* either way.")

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("NOW ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

ROW_ANCHOR = u"  **apply to itself:** *\"CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT\"*"
ROW_ADD = u"""
- [x] **`Pyre` is not a Core def** - the **second** factual error the owner's challenge found in
  the same handoff, which listed it among *"Core defs confirmed present"*. It lives in
  `Ideology/Defs/ThingDefs_Buildings/Buildings_Ideo.xml`. The mod ships **zero hard
  dependencies**, so nothing may name it. **The first check was run against the installed game
  rather than against Core**, and for a Core-only mod that is the whole distinction - which is
  why it read as a pass. `Grave`, `Sarcophagus` and `ElectricCrematorium` are genuinely Core;
  `Crematorium` does not exist under that name"""

todo = io.open(TODO, encoding="utf-8").read()
if todo.count(ROW_ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ROW_ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    todo.replace(ROW_ANCHOR, ROW_ANCHOR + ROW_ADD, 1))

after = io.open(NOW, encoding="utf-8").read()
if u"**`Pyre`**. **There is no def" in after:
    print("THE PYRE CLAIM IS STILL ASSERTED")
    raise SystemExit(1)
if u"`Pyre` is not a Core def" not in io.open(TODO, encoding="utf-8").read():
    print("ROW NOT WRITTEN")
    raise SystemExit(1)
print("Pyre corrected in NOW.md and recorded in TODO.md")
