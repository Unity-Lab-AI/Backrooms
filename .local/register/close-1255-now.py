# -*- coding: utf-8 -*-
"""The NOW.md half of the 0.12.55-dev close, retargeted at the text 0.12.54-dev left behind.

TODO and FINALIZED were already written and verified by `close-1255.py`; this does the NOW.md
edits only, and its first run failed loudly on a stale anchor rather than writing a wrong file.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

HEAD_OLD = u"""## DO THIS FIRST — READ THE LOG FROM THE SEVENTH LAUNCH

**0.12.54-dev is staged and the owner has not launched it yet.** Read `Player.log` before anything
else, and **read it before telling them anything works** — the last two times that question was
answered from proofs rather than from a log, the answer was wrong."""

HEAD_NEW = u"""## DO THIS FIRST — READ THE LOG FROM THE EIGHTH LAUNCH

**Read `Player.log` before anything else, and read it before telling the owner anything works.**
Three checkpoints in a row have now been answered from proofs rather than from a log, and three
times the answer was wrong.

### WHAT THE SEVENTH LAUNCH FOUND: 587 RED LINES FROM ONE LINE

**The game never left the main menu, so the seventh launch tested NOTHING but def load.**

```
Exception loading def from file Buildings_Structure.xml: System.ArgumentException:
  Could not find type named CompProperties_Colorable from node
  <li Class="CompProperties_Colorable" />
Could not resolve cross-reference to Verse.ThingDef named Door ...        (x529)
Could not resolve cross-reference: No Verse.ThingDef named Autodoor ...   (x59)
```

Every one of the 587 errors named `Door`, `Autodoor` or `CompProperties_Colorable` **and nothing
else**. There is no `CompProperties_Colorable` type: `CompColorable` takes a plain
`CompProperties` with a `compClass`, as Core does for textiles, apparel and the Ideology floor
coverings — and the last of those are buildings, so it was the right mechanism for a door all
along, spelled with a class that does not exist. **A bad `Class` throws out of
`DirectXmlToObjectNew`, which discards the entire ThingDef**, so `Door` and `Autodoor` left the
game and 585 further errors were other defs — 541 of them vanilla prefabs — failing to
cross-reference them.

**Still not one mod conflict in seven launches.** Doors Expanded and Mechhive appear in that log
only as victims of our missing `Door`.

### THREE THINGS TO KNOW BEFORE WRITING ANOTHER PROOF

1. **A proof that reads text cannot tell whether a resolver resolves.** The forty-second proof,
   `proof-class-resolution.py`, is the first that **imports the checker and interrogates it**.
   When a claim is about whether something *works* rather than whether it is *written*, execute
   it. The first draft of that very resolver split the metadata heap on NUL, which misses
   suffix-shared names and **rejected `Building`** — failing correct code, which is worse than
   the hole it closed, and entirely invisible to a text-reading proof.
2. **Asserting our XML contains a string proves we wrote it, never that the game can use it.**
   `proof-gate-links.py` required `'<li Class="CompProperties_Colorable" />'` as its evidence that
   a gate is blue — **it held the bug in place**, and the matching plant mangled that string and
   watched the proof fail, which is a plant proving a broken line was load-bearing.
3. **Run EVERY plant suite, not the ones you touched.** Doing so found a plant that could never
   have been caught: it planted a comment at a proof that strips comments on purpose. The proof
   was right and the plant was wrong — the inverse of the usual trap.

### What the EIGHTH launch has to settle, in this order

1. **DOES A COORDINATE GENERATE AT ALL.** Fourth attempt, and the generator has still never run
   end to end. Everything below depends on it.
2. **is the back-room door blue and glowing** once a level exists
3. **select a colonist, right-click the gate → "Enter the gate"** — they should walk over and
   come out on the other map
4. **every other door in the colony is unlit and unchanged** — the `IThingGlower` veto
5. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything
   matching
6. **one level in, the materials go wild** — two tables in one room in different stuffs, each
   room's walls a different material. Newest thing in the build, least like anything that has run
7. **no cave-in** when a wall or a pillar is deconstructed
8. **Operations → Places** lists the colony and any level, with the budget as `n/5`"""

EDITS = [
    (u"| Published | **0.12.54-dev**.", u"| Published | **0.12.55-dev**."),
    (u"SHA-256 `1FA1CEE1987B5FF32042F6DBA8D4ED279F76843B59A9881C331CE0F174EBF39C`",
     u"SHA-256 `154428928909D68FFA599193CCE8997FBF10AC70671118AB958EEE701E3A3CF9`"),
    (HEAD_OLD, HEAD_NEW),
]

now = io.open(NOW, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:60]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.55-dev")
