# -*- coding: utf-8 -*-
"""Rewrite "Done since the last handoff" for 0.12.34 -> 0.12.39.

It still described 0.12.24 -> 0.12.33, which was true at the previous handoff and is six
checkpoints stale. This section exists so nobody rebuilds what shipped, so a stale version is the
actively harmful kind: it under-reports what is done and over-reports what is left.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

s = io.open(PATH, encoding="utf-8").read()

START = u"### Done since the last handoff, so nobody rebuilds it"
END = u"## Invariants — do not break these"

assert s.count(START) == 1, "start anchor: %d" % s.count(START)
assert s.count(END) == 1, "end anchor: %d" % s.count(END)

start = s.index(START)
end = s.index(END)

NEW = u"""### Done since the last handoff, so nobody rebuilds it

**Six checkpoints, 0.12.34 → 0.12.39, seventeen rows closed in four batches.** Every one published
to all eight refs with a read-back, a deterministic assembly, and the full checker and proof sweep.

**The owner changed how to work, mid-run:** *"lets start doing shit correctly and efficiently and
keep going iin batches of items completed so we have less work constantly pushing"*. So related
rows are grouped into one checkpoint and published once. It works — 0.12.36-dev closed **six rows
in one publish**.

**NINE ROWS TURNED OUT ALREADY BUILT, ALREADY TRUE, OR ANSWERED BY CORE.** The table under *Is it
done?* lists all nine. Twice the row's own *"confirmed absent by grep"* was itself the defect: row
725 said stabilizers and modules were absent and **both existed under different names**
(`PortalWindowTier`, `GateEquipmentLinks`). **Check a row against the code before building for
it** — it is the highest-value habit in this file.

**Custody across a gate was never a problem, and Core says so.** All eleven DLC container hauling
givers were decompiled. Every one refuses to act unless the thing it moves is already on the
worker's own map — `WorkGiver_CarryToBuilding` returns false unless `selectedPawn.Map == pawn.Map`,
`TakeEntityToHoldingPlatform` unless `targetHolder.MapHeld == t.MapHeld`, and the rest search
`pawn.Map`. So **invariant 55 was never engaged**, the family is the ordinary deployment shape, and
twenty-seven checkpoints of caution were spent on a question Core had already closed.

**A clamp was silently overwriting the mod's own shipped numbers on every game load.** `Effective`
clamped every value against one `MaximumPriority = 130` **including the shipped default**, and
`Apply` writes that into the defs at `FinalizeInit`. Six authored priorities were being replaced
before a pawn ever ran — worst, the far-side operating family authored at **502** to sit one above
Core's `Flick`, landing on **130**, below every local giver. **That is the exact failure the
two-giver split exists to prevent, inside the code that exists to prevent it.** The ceiling is now
per giver.

**Core's four containment alerts all read `Find.CurrentMap`.** Enumerating Core's own alert classes
before writing any found `Alert_InsufficientContainmentStrength`, `Alert_DangerousActivity`,
`Alert_EntityNeedsTend` and `Alert_NeedHoldingPlatform` — so shipping ours would have been a second
opinion beside a rule the player already sees. **The real gap is that Core's warnings are about the
map on screen**, and this mod's premise is several live maps at once. The two new alerts skip
`Find.CurrentMap` entirely, so the sets can never overlap.

**Quarantine could not be medical, and that is a measurement.** This package has **no `HediffDefs`
folder at all**, so there is nothing of ours to clear and inventing one is forbidden content.
Quarantine is therefore *you do not go back out until you have reported in* — which makes it and
the staff debrief **one mechanism**. The hold bites on `Dispatch`, deliberately **not** on
`PortalTraversalPolicy`, because a player walking one colonist through a door by hand is not a
company dispatch.

**Every stuffable fixture on every coordinate in the game was wooden.** Not the def's default —
`ThingDefOf.WoodLog`, hardcoded. A coordinate now takes a three-entry palette from its own seed,
and **the load-bearing line is a sort by defName**: the def database returns defs in an order that
depends on the installed mod list, so indexing it unsorted would give two players on one seed
different materials and change a coordinate when an unrelated mod is installed.

**A gate read no damage at all.** It could be shot to twelve per cent, set on fire and hit by a
mortar and still hold a connection perfectly. **The machine the entire mod is built around was the
one building in the colony that damage did not affect.** Below half condition it now loses
calibration — a state that already had a work giver, a refusal and a readout — so the fix adds no
mechanic.

**The register said don't patch, and reading it first is the only reason the last batch is right.**
*"No patch or code/assets copied"* for both gravship chapters; *"do not add vehicles solely because
the framework is installed"* for the vehicle framework. So the hook is a **read-only statement** of
what is installed and what this package does about it — which is what the rows asked for in their
own words. The defence that cannot rot is asserted: **only two files mention the detection class,
and no tracked package id appears in any other source file.**

**Two new checkers, taking it to twelve.** The def-field checker (row 922) **caught itself twice**
before it was right, both times in the same function — first reporting nothing, then reporting 159
false positives, because the field parser rejected any line containing `(` and every collection
field has one in its initialiser. And the row 791 claim guard, which **found a real denial in
`SCENARIOS.md` on its first run**.

---

"""

io.open(PATH, "w", encoding="utf-8", newline="").write(s[:start] + NEW + s[end:])
print("done-since rewritten for 0.12.34 -> 0.12.39")
