# -*- coding: utf-8 -*-
"""NOW.md for 0.12.37-dev. Five rows closed; every number re-measured."""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, "anchor missing: %r" % old[:90]
    assert s.count(old) == 1, "anchor not unique: %r" % old[:90]
    s = s.replace(old, new, 1)


sub(u"| Published | **0.12.36-dev**.", u"| Published | **0.12.37-dev**.")
sub(u"| Build | **188 C# files, 87 package files**", u"| Build | **189 C# files, 87 package files**")
sub(u"SHA-256 `CF62F3C946CCEC8CB9E7A0CEC5B235394556B3254B399920D0FEE9DF8AE8D9DC`",
    u"SHA-256 `7CB355E054853C9E50461EEEAA68AA68F532320DB9073228E755223B12DAEF6A`")
sub(u"| Proofs | **THIRTY-THREE** in `.local/register/proof-*.py`.",
    u"| Proofs | **THIRTY-FOUR** in `.local/register/proof-*.py`.")
sub(u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.36-dev**.",
    u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.37-dev**.")
sub(u"## What shipped this session, 0.7.1 → 0.12.36",
    u"## What shipped this session, 0.7.1 → 0.12.37")

# ------------------------------------------------------------------ the twelfth checker
sub(u"| Checkers | **ELEVEN**, all passing.",
    u"| Checkers | **TWELVE**, all passing. The twelfth, `check-def-fields.py`, refuses a def "
    u"that sets a field the class does not have — RimWorld logs an unknown field and carries on, "
    u"so one had been silently inert for fourteen defs across two checkpoints. It **caught itself "
    u"twice** before it was right; see 0.12.37-dev.")

# ------------------------------------------------------------------ queue figures
sub(u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 68 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 50 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 464 done
```""",
    u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 64 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 49 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 469 done
```""")

# ------------------------------------------------------------------ replace DO THIS FIRST
start = s.index(u"## DO THIS FIRST — the generation batch")
end = s.index(u"## What shipped this session, 0.7.1 →")
sub(s[start:end], u"""## DO THIS FIRST — the gate subsystems batch

Row 725, and it is the largest single unbuilt row left: *"monitoring, cool-down, modules, repair
and reliability"* for a gate. Five nouns, and **three of them already have machinery that must be
read before anything is written.**

| Noun | What already ships |
|---|---|
| monitoring | the gate inspect pane, the three gate alerts (0.10.5-dev), the containment alerts (0.12.35-dev) |
| cool-down | **the return window and the opening clock** — `emergencyReturnTicksRemaining`, `openingTicksRemaining` |
| modules | **`GateEquipmentLinks`** (0.10.8-dev) — shelves, analysers and cabinets link into a gate with no reach limit |
| repair | `RR_ConnectedRepair` crosses for damaged buildings; a gate is a building |
| reliability | power reserves, calibration and the cutoff all ship |

Four things to settle:

1. **Find out which of the five are already built before writing any of them.** This session
   closed **eight** rows that turned out to be done or answered by Core — 227, 308, 493, 1266,
   98, 99, 1011, 1101. On the measured evidence, *monitoring* and *reliability* are the likely
   already-shipped pair and *cool-down* the likely genuine gap.
2. **A gate has exactly six ways to stop working, and that set is asserted** by
   `proof-areas-and-debrief.py`: the kill switch, power, the operator, two clocks and the
   deliberate cutoff. **Anything new that can stop a gate has to be added to that set on purpose**,
   and the proof will fail until it is — which is the point.
3. **"Modules" is the word to be careful with.** `GateEquipmentLinks` already is a module system,
   built to the owner's *"reach fare and through walls"* direction with **no distance and no
   line-of-sight check**. If row 725's modules are the same thing, close it by proof; if they are
   something else, **ask before authoring a def** — a module as a new `ThingDef` is forbidden by
   the existing-content-only constraint.
4. **`python tools/register-query.py family facilities` and `trace RR-GATE`** — facilities is
   swept, so the guidance is already read; the gate trace is the one to re-read for this row.

**The batch to pair it with** is items 8–10 below: vehicles and space hooks (764, 765, 766) and the
RWT multiplayer detection (784, 791), because all three are *optional-by-construction*
`PatchOperationFindMod` work that does nothing when the mod is absent, and all three touch the gate.

---

""")

# ------------------------------------------------------------------ the remaining list
sub(u"""4. **Mineable materials and recoverable floors** in a stripped interior. Row 1101. `FillWithRock`
   and `NaturalRockTypesIn` already ship; the floors half is what remains.
""", u"")
sub(u"""5. **Inhabitant and monstrosity families tiered by depth and wealth**, every variation seeded.
   Row 1011. The bands, archetypes and pressure ladder they sit on all ship.
""", u"")
sub(u"""6. **Material variety per coordinate** — archetype fixtures take their default stuff today.
   Row 1005.
""", u"")
sub(u"""13. **The unknown-def-field checker**, written once and **removed rather than shipped** because it
    passed its own planted fault. Row 922.
""", u"")
sub(u"""14. **Fix `disposition_stance()`** in the register generator: it counts a **negated** "required" as
    Required, and **14 of the 17** "Required" rows say the opposite. Row 1055.
""", u"")

# Renumber the systems section.
start = s.index(u"### Systems still unbuilt")
end = s.index(u"### Cannot close before the game runs once")
block = s[start:end]
numbers = re.findall(r"^(\d+)\. ", block, re.M)
for new_index, old_index in enumerate(numbers, start=1):
    block = re.sub(r"^%s\. " % old_index, u"\x00%d. " % new_index, block, count=1, flags=re.M)
block = block.replace(u"\x00", u"")
s = s[:start] + block + s[end:]

remaining = len(numbers)
sub(u"**18 genuine build items**, counted at 0.12.36-dev, listed in full under **What is left** "
    u"below. **Six rows closed in one batch**: 761 completely, the three area rows together, and "
    u"98 and 99 by proof.",
    u"**%d genuine build items**, counted at 0.12.37-dev, listed in full under **What is left** "
    u"below. **Five more rows closed in this batch**: 1005 built, 1011 and 1101 by proof, and 922 "
    u"and 1055 as tooling. **Eleven rows across the last two batches.**" % remaining)
sub(u"**18 genuine build items**, counted rather than estimated:",
    u"**%d genuine build items**, counted rather than estimated:" % remaining)

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("NOW.md updated for 0.12.37-dev: %d items remain" % remaining)
