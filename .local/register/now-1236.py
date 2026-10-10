# -*- coding: utf-8 -*-
"""NOW.md for 0.12.36-dev. Six rows closed; every number re-measured."""
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


sub(u"| Published | **0.12.35-dev**.", u"| Published | **0.12.36-dev**.")
sub(u"| Build | **186 C# files, 87 package files**", u"| Build | **188 C# files, 87 package files**")
sub(u"SHA-256 `F4252E3F04A178EB6B2FCB3C0D8C2B5D1A8114883404C46088278D9FA0B6892D`",
    u"SHA-256 `CF62F3C946CCEC8CB9E7A0CEC5B235394556B3254B399920D0FEE9DF8AE8D9DC`")
sub(u"| Proofs | **THIRTY-TWO** in `.local/register/proof-*.py`.",
    u"| Proofs | **THIRTY-THREE** in `.local/register/proof-*.py`.")
sub(u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.35-dev**.",
    u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.36-dev**.")
sub(u"## What shipped this session, 0.7.1 → 0.12.35",
    u"## What shipped this session, 0.7.1 → 0.12.36")

# ------------------------------------------------------------------ queue figures
sub(u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 74 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 50 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 458 done
```""",
    u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 68 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 50 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 464 done
```""")

# ------------------------------------------------------------------ the working-style note
sub(u"### The standing instruction",
    u"""### How to work, owner direction 2026-09-29

> *"lets start doing shit correctly and efficiently and keep going iin batches of items completed
> so we have less work constantly pushing and all of that"*

**Batch related rows into one checkpoint and publish once.** 0.12.36-dev closed **six** rows in one
publish, and they were related on purpose: quarantine is an area question, so the area rows rode
with it, and the two ordinary-map rows were proved in the same sweep. Chain the work, then do one
build, one determinism run, one checker and proof sweep, one commit, one cascade.

### The standing instruction""")

# ------------------------------------------------------------------ replace DO THIS FIRST
start = s.index(u"## DO THIS FIRST — staff debrief and quarantine")
end = s.index(u"## What shipped this session, 0.7.1 →")
sub(s[start:end], u"""## DO THIS FIRST — the generation batch: materials, mineables, floors and families

Four rows that are one piece of work, and they should be built together for the same reason the
last batch was: they all touch what a generated coordinate is *made of*.

| Row | What |
|---|---|
| **1005** | material variety per coordinate — archetype fixtures take their default stuff today |
| **1101** | mineable materials and recoverable floors in a stripped interior |
| **1011** | inhabitant and monstrosity families tiered by depth and wealth, every variation seeded |
| **1266's neighbours** | nothing; 1266 is closed |

Four things to establish before writing a line:

1. **Half of 1101 already ships and must not be rebuilt.** `FillWithRock` and `NaturalRockTypesIn`
   are already used by generation — measured at 0.12.33-dev. **The floors half is what remains**:
   a recoverable floor means `TerrainDef.removeBuildingBlueprint` or Core's own floor-removal
   designation working on a coordinate's terrain. Read `GenStep_BackroomsDestination` first.
2. **1005 and 1011 share a seed, and that is the constraint that matters.** A coordinate is
   regenerated from its seed, and **two players must see the same thing happen** — that rule is
   already written into `GateIncursion`'s candidate ordering and into the displacement work at
   0.10.3-dev. Any material or family choice must come out of the coordinate's own seed, never out
   of `Rand` without a pushed state.
3. **1011's ladder already exists and must be read rather than re-invented.** The bands, the
   archetypes and `CoordinatePressureLadder` all ship, and 0.12.33-dev surfaced the band per
   coordinate in the Operations pane. *"Tiered by depth and wealth"* is the ladder's own two
   inputs — `CoordinatePressureLadder.ColonyWealth()` is already how incursion scales.
4. **`python tools/register-query.py family materials`** — **one of the seven families the
   register retro sweep has not reached** (rows 206, 302), and it is exactly the family this batch
   is about. This is the sweep that owes this work its guidance, so read the rows directly.

**The constraint that will bite:** *"material variety"* must not become new `ThingDef`s. Existing
content only — the variety has to come from Core's own stuffable materials and rock types chosen
per coordinate, not from anything authored here.

---

""")

# ------------------------------------------------------------------ the remaining list
sub(u"""1. **Staff debrief and quarantine** — the last two halves of row 761, and **the DO THIS
   FIRST item**; see the top of this file for the four things to settle, of which *"there is no
   exposure hediff in this mod"* is the one that decides the shape.
   **Closed from that row at 0.12.35-dev:** containment rooms (a tenth facility category matched
   by capability, naming no expansion def), the security procedure (a standing order that cuts
   every open connection on a breach, through the gate's own existing cutoff) and the alarm. The
   finding worth keeping: **Core already ships four containment alerts and every one reads
   `Find.CurrentMap`**, so the gap was never that containment has no warning but that it has none
   about the maps you are not looking at.
   **Also closed, 0.12.34-dev:** row 1266's eleven DLC container hauling givers as
   `machine-loading` — **Core forbids every one of them from moving anything between maps**, so
   invariant 55 was never engaged — and the four `Art` painting givers as `painting`.""",
    u"""1. **ROW 761 IS CLOSED** (0.12.35-dev and 0.12.36-dev). Containment rooms, the security
   procedure and the alarm shipped first; **staff debrief and quarantine closed it**, and they
   turned out to be one mechanism because this package has **no `HediffDefs` folder at all**, so
   quarantine is *"you do not go back out until you have reported in"* rather than anything
   medical. Two findings worth keeping: **Core already ships four containment alerts and every one
   reads `Find.CurrentMap`**, so the gap was never that containment has no warning but that it has
   none about the maps you are not looking at; and the debrief hold bites on **`Dispatch`, not on
   `PortalTraversalPolicy`**, because a player walking one colonist through a door by hand is not
   a company dispatch.
   **Also closed, 0.12.34-dev:** row 1266's eleven DLC container hauling givers as
   `machine-loading` — **Core forbids every one of them from moving anything between maps**, so
   invariant 55 was never engaged — and the four `Art` painting givers as `painting`.""")

# ------------------------------------------------------------------ the three closed area / map rows
sub(u"""5. **Mineable materials and recoverable floors**""",
    u"""5. **Mineable materials and recoverable floors**""")

sub(u"""6. **The four area types across a gate** — `Area_BuildRoof`, `Area_NoRoof`,
   `Area_SnowOrSandClear`, `Area_PollutionClear`. Rows 1215, 1235, 1239. **Measured: one incidental
   `Area_NoRoof` use and no cross-gate coverage.**
""", u"")

sub(u"""4. **Mining and building behind a gate.** Rows 98 and 99. The cells around a gate are ordinary map;
   the one exception is linked equipment, which has placement requirements **of its own**.
   **Row 113 is closed** (0.12.27-dev) — the approach cell is reserved against blocking, and
   flooring is fine.
""", u"")

# Renumber what is left in the systems section.
start = s.index(u"### Systems still unbuilt")
end = s.index(u"### Cannot close before the game runs once")
block = s[start:end]
numbered = re.findall(r"^(\d+)\. ", block, re.M)
renumbered = block
for new_index, old_index in enumerate(numbered, start=1):
    renumbered = re.sub(r"^%s\. " % old_index, u"\x00%d. " % new_index, renumbered, count=1,
                        flags=re.M)
renumbered = renumbered.replace(u"\x00", u"")
s = s[:start] + renumbered + s[end:]

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("NOW.md updated for 0.12.36-dev")
