# -*- coding: utf-8 -*-
"""0.12.75-dev: the bonds. Written as a FILE, because a heredoc mangles apostrophes.

`docs/NOW.md` says this in so many words and it has now been ignored a twelfth time: *"Use a FILE
for any script with escapes or apostrophes, never a bash heredoc."*
"""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
TODO = os.path.join(REPO, "docs", "TODO.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: close-1275.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

ENTRY = u"""
---

## Session 2026-10-01 - the bonds (0.12.75-dev)

**Verbatim user quotes:** *"and nother thing the bonds i pull out i dont sdeem to be able to put
them back in and and to combine them"*; *"and they need a name that is theri value and better
description and value is not correct"*; *"now the books as bonds just say noprmal the quality which
is normal"*.

**Files touched:** `Economy/BondPaper.cs` (new), `Economy/BondHandling.cs` (new),
`Economy/CompRimroomsBond.cs`, `Economy/BondService.cs`, `Company/BondTreasury.cs`,
`Keyed/RR_Bonds.xml`, `tools/check-register-compliance.py`, `proof-bonds.py` (new, proof
FORTY-SIX), `plant-rest.py`.

**Mod register.** Nothing applied. Bonds are a Core `Novel` carrying our own comp, and the one
register rule that bears on this -- the materials and cargo family, *"preserve each mod's normal
material and weight behavior"* -- is **honoured by construction**: the value change is a `StatPart`
that answers only for a stamped bond, so every other object in every other mod gets the number it
got before.

### Nothing in the battery had ever claimed anything about bonds

`grep -l Bond` across forty-five proofs and sixteen plant suites returned **nothing**. That is why
five separate defects shipped in one feature and the owner found all five in one sitting. **Four of
the five are the same shape: built, correct, and unreachable** -- this project's most repeated
defect, and the only thing that catches it is a claim asserting something is *called*.

| Reported | Cause |
|---|---|
| *"the books as bonds just say noprmal the quality"* | `CompRimroomsBond.TransformLabel` **had never run.** `Verse.Book.LabelNoCount` is `title + GenLabel.LabelExtras(...)` and never walks `comps` |
| *"value is not correct"* | a `Novel` is `MarketValue 160`, so a million-credit bond was 160 silver of paper |
| *"i dont sdeem to be able to put them back in"* | `RedeemBondsInRadius` worked and had **exactly one caller**: a credit beacon the player had not built |
| *"and to combine them"* | did not exist |
| *"better description"* | one sentence, telling the player to use the beacon they did not have |

### The name is the value, and the first attempt was refused for the right reason

The label comes from `Book_RimroomsBond`, assigned as the carrier's **`thingClass`** in the same
startup constructor that already adds the comp. An ordinary novel is untouched: every member defers
to `base` unless the thing carries a stamped face value, and the subclass satisfies every `is Book`
test in the game.

**The first attempt wrote `Book`'s private `title` by reflection, and `check-compliance.py` refused
it.** Its rule is principled and worth quoting: *"Reflection is the loophole: a `SetValue` into a
game type is a game-assembly modification that no dependency list would show"* -- a Ludeon-terms
question as much as an architecture one. Its stated boundary is behaviour through *"Core's own
ThingComp, GameComponent, WorkGiver, JobDriver and **Def extension points**"*, and `thingClass` is
one. **The checker was right and the code changed, not the checker.**

**And the dead hook is deleted rather than left in place.** A method that cannot be called is worse
than the bug it was meant to fix, because it reads like the problem is solved.

### The value, and the consequence stated rather than hidden

`StatPart_RimroomsBondValue` sets `MarketValue` to the face value. The face value lives **per
instance**, so no entry on a def can express it and a StatPart is the only mechanism that reads the
thing. It is additive; `MarketValue`'s own parts are untouched.

**No new exchange rate was invented.** `ValuablesExchange.UnitCreditsFor` already buys ordinary
goods at 0.85, so selling a bond through the company fetches 85% of face -- a spread -- while
depositing or banking it returns the full face. **Neither route prints money, and that was checked
before the stat was touched.**

Colony wealth counts market value, so a fortune held as paper raises raid points in a way the
ledger does not. **That is the trade the bond exists to offer** and `CompRimroomsBond` already said
it: *"Liquidity costs risk."*

### A way back in, and a way to combine

Both actions are **gizmos on the paper itself**, because a `Book` is a selectable item and
`ThingWithComps.GetGizmos` walks its comps -- the one surface that reaches a bond lying on a floor.
The beacon still banks a whole radius at once, which is what it is for.

Combining goes **through the ledger**: the paper is destroyed and credited, the replacement debited,
and anything that cannot be placed stays credited. Two halves of one operation id, so a reload
cannot pay twice and a credit cannot fall between the ledger and the floor. It uses the one
`CreditDenominations` decomposition every other payout uses, and it **refuses** rather than
shredding a pile it cannot improve.

### A checker read its own explanatory prose, for the fifth time

`check-register-compliance.py` refused the value change because the patch's **comment** contained
the word `statBases` -- in the sentence explaining that the face value *cannot* be a `statBases`
entry. **Fifth instance**, and the precedent was already documented: `check-compliance.py` strips
XML comments since 0.12.46-dev, where it flagged a patch for containing `PatchOperationReplace` in
the comment explaining why a replace is wrong. It strips comments now too.

**Two checkers refused this work and exactly one of them was wrong.** Knowing which is the whole
skill: the reflection rule stood and the code changed; the comment-matching rule was a defect and
the checker changed.

### And my own plants caught my own claims, for the third checkpoint running

`18 of 20`. The label claim asserted an expression that appears in **both** overrides, so a plant
that gutted `LabelNoCount` left the one in `LabelNoParenthesis` and the claim held while no bond
was named -- **duplicate-string trap, counted now rather than found.** The refusal claim asserted
the `Messages.Message` call was *written*; a plant prefixing `if (false)` left every asserted
character in place -- **tenth instance of machinery-not-behaviour**, pinned to the line above it
now.

**And the heredoc rule was broken a twelfth time** writing this very record: an apostrophe in the
prose killed the shell. `docs/NOW.md` says *"Use a FILE for any script with escapes or apostrophes,
never a bash heredoc"* and the only thing that has ever worked is reaching for the file first.

**206 C# files, 92 package files**, zero warnings, zero errors. Assembly SHA-256
`__HASH__`, measured after the version bump, reproduced by two clean recompiles.
**Seventeen checkers pass, FORTY-SIX proofs hold, 20 of 20 planted faults caught in the suite that
carries the bonds, 684 plant anchors findable.**
"""
ENTRY = ENTRY.replace(u"__HASH__", HASH)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
OLD = u"## IN PROGRESS - the bonds - 2026-10-01 (0.12.75-dev)"
NEW = u"## The bonds - 2026-10-01 (0.12.75-dev) - DONE"
if todo.count(OLD) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(OLD))
    raise SystemExit(1)
todo = todo.replace(OLD, NEW, 1)
start = todo.index(NEW)
end = todo.index(u"\n---", start)
todo = todo[:start] + todo[start:end].replace(u"- [~] **", u"- [x] **") + todo[end:]
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO marked done, every description kept")

HANDOFF = u"""## STATE AT THIS HANDOFF — `0.12.75-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.75-dev  92 files
assembly    __HASH__
            read back out of the game folder after staging, not from the build
battery     17 checkers - 46 proofs - 20 of 20 in the bond suite - 684 anchors findable
tree        no planted fault, porcelain 0
```

### FIVE BOND DEFECTS, AND NO CLAIM HAD EVER BEEN MADE ABOUT BONDS

`grep -l Bond` across forty-five proofs and sixteen plant suites returned **nothing**, which is why
the owner found five defects in one feature in one sitting. **Four of the five were the same shape:
built, correct, and unreachable.**

| | |
|---|---|
| the label | `CompRimroomsBond.TransformLabel` **had never run**: `Verse.Book.LabelNoCount` is `title + GenLabel.LabelExtras(...)` and never walks `comps`. The label is a `thingClass` override now, and the dead hook is **deleted** |
| the value | a `Novel` is `MarketValue 160`. A `StatPart` sets it to the face value, additively, reading the thing because the face value is per instance |
| putting one back | `RedeemBondsInRadius` had **exactly one caller**, a beacon the player had not built. There is a gizmo on the paper now |
| combining | did not exist. It goes through the ledger in two halves of one operation id, so a credit cannot fall between the ledger and the floor |
| the description | told the player to use the beacon they did not have |

**`proof-bonds.py` is proof FORTY-SIX** and the first claim ever made about this feature.

### THE COMPLIANCE CHECKERS REFUSED THE FIRST ATTEMPT, AND ONE OF THEM WAS RIGHT

The label was first written by **reflection into `Book`'s private `title`**, and
`check-compliance.py` refused it: *"a `SetValue` into a game type is a game-assembly modification
that no dependency list would show"* — a Ludeon-terms question, not only architecture. Its stated
boundary is **Def extension points**, and `thingClass` is one. **The code changed, not the
checker.**

`check-register-compliance.py` then refused the value change because the patch's **comment**
contained the word `statBases`, in the sentence saying the face value *cannot* be one. **Fifth
instance of a checker reading its own prose**; it strips XML comments now, as
`check-compliance.py` has since 0.12.46-dev. **That one was the checker's defect and the checker
changed.** Knowing which of the two is wrong is the whole skill here.

### NO MONEY IS PRINTED, AND THAT WAS CHECKED BEFORE THE STAT WAS TOUCHED

Selling a bond through the company fetches **85%** of face, because `ValuablesExchange` already
buys ordinary goods at 0.85. Depositing or banking returns **100%**. No new rate was invented.
Holding paper raises colony wealth where the ledger does not, which is the trade the bond exists to
offer: *"Liquidity costs risk."*

"""
HANDOFF = HANDOFF.replace(u"__HASH__", HASH)

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.74-dev**.", u"| Published | **0.12.75-dev**."),
    (u"SHA-256 `39C05DB8EFD9852A29BB0C8DD7FD7F25550D204431AD5C7F4C38F3A2DBE88941`",
     u"SHA-256 `" + HASH + u"`"),
    (u"## STATE AT THIS HANDOFF — `0.12.74-dev`, STAGED AND VERIFIED",
     HANDOFF + u"## STATE AT THIS HANDOFF — `0.12.74-dev`, STAGED AND VERIFIED"),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated and the handoff written for 0.12.75-dev")
