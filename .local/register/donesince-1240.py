# -*- coding: utf-8 -*-
"""Extend "Done since the last handoff" with 0.12.40-dev.

The section exists so nobody rebuilds what shipped, which makes a stale version the actively
harmful kind: it under-reports what is done and over-reports what is left. It described
0.12.34 -> 0.12.39 and this is the seventh checkpoint.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

OPENING_OLD = (u"**Six checkpoints, 0.12.34 → 0.12.39, seventeen rows closed in four "
               u"batches.** Every one published\nto all eight refs with a read-back, a "
               u"deterministic assembly, and the full checker and proof sweep.")
OPENING_NEW = (u"**Seven checkpoints, 0.12.34 → 0.12.40, twenty-two rows closed in five "
               u"batches.** Every one published\nto all eight refs with a read-back, a "
               u"deterministic assembly, and the full checker and proof sweep.")

TAIL_ANCHOR = (u"**Two new checkers, taking it to twelve.** The def-field checker (row 922) "
               u"**caught itself twice**")

TAIL_NEW = u"""**The first surface row 821 names opened from nowhere at all.** Not from the company panel, not
from any pane, not from anywhere in 191 files: `grep -rn "Architect" --include=*.cs src` returned
**nothing**. And this file said it was already reachable, which makes it the worst kind of stale
measurement — the one a fresh session would trust instead of checking. Architect is the surface
every building action in RimWorld goes through. All five surfaces the row names now open from the
panel, each through the game's own `MainButtonDef.Worker.InterfaceTryActivate()`.

**A tab called company-first was second from the right.** Core's orders are Architect 1 through
Factions 90 and Menu 500; Operations shipped at **95**, between the last two. It is order 0 now,
left of Architect. One field, and **the invasive reading of "remap" stays unbuilt on purpose** —
rewriting Core's own tab bar would fight every interface mod in the register at once, and
reachability was what the row actually required. The absence is asserted rather than assumed,
including against the def-database route a Harmony-free mod still has.

**The whole keyboard requirement was one XML field, and Core writes the rest.**
`KeyBindingDefGenerator.ImpliedKeyBindingDefs` emits a rebindable `MainTab_<defName>` into the
`MainTabs` category for any `MainButtonDef` that sets `defaultHotKey`. So the binding appears in the
player's own Key Bindings dialog and **this package authors no `KeyBindingDef` at all**. The default
is **F12, the only function key Core leaves free** — it takes Tab and F1–F9 for main tabs,
F10 for a screenshot and F11 for screenshot mode.

**Contrast and scale were already right, with nothing holding them right.** Not one file under
`UI/` authored a colour, and the only font work in the folder is one `GameFont.Medium` heading with
the caller's font restored. So the position is that this package authors **neither colour nor font
size in anything a player reads text from**, and the player's own Options for scale, font and
colourblind mode apply exactly as they do to the base game. **An option of ours would have been a
second, worse copy of a setting the game already has.** That is now a checker rule, because it was
true by accident.

**The plant harness verifies its targets before it plants anything**, and the first sweep of this
batch justified it: **33 of 42, and all nine misses were real.** Two were gaps in the new checker
— `new UnityEngine.Color(...)` walked past a pattern matching `new Color(`, and `(GameFont)7`
walked past an exemption meant for the `previousFont` restore. Four were claims that tested a
**mention** rather than a **use**: `def check_readability(` satisfies a probe for
`check_readability(problems)`, and `AUTHORED_COLOUR` matches `AUTHORED_COLOUR_UNUSED`. One was a
detector that depended on a variable being named conveniently. Two were weak plants — and one
of those found a writing fault, because the document stated the same key in two places.

---

"""

EDITS = [
    (OPENING_OLD, OPENING_NEW),
    (TAIL_ANCHOR, TAIL_NEW + TAIL_ANCHOR),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:74]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("done-since extended through 0.12.40-dev")
