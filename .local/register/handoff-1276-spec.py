# -*- coding: utf-8 -*-
"""NOW.md handoff for the goon squad SPEC. Nothing is built; this is the brief.

Owner direction, 2026-10-01: *"after u write that up write the now.,md , i need to compact no need
for stage and cascade this one time"*. So this writes the handoff and stops. No stage, no commit,
no cascade.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

ANCHOR = u"## STATE AT THIS HANDOFF — `0.12.75-dev`, STAGED AND VERIFIED"

NEW = u"""## NEXT UP, AND IT IS NOT BUILT: THE GOON SQUAD (0.12.76-dev)

```
state       SPEC ONLY. 25 rows recorded verbatim in docs/TODO.md. ZERO code written.
published   0.12.75-dev is the last staged, cascaded checkpoint and it is clean.
tree        docs/TODO.md and docs/NOW.md are MODIFIED AND UNCOMMITTED.
            Owner direction: *"no need for stage and cascade this one time"*.
            Nothing else is touched; src/ and Mod/ are exactly 0.12.75-dev.
```

**Do not re-ask the owner anything below. All of it is settled.**

### THE DIRECTION, AND THE ONE QUESTION THAT WAS ASKED

Owner, verbatim, is in `docs/TODO.md` under *"the goon squad, and never losing the game"* — 25
rows, one per clause. The short version in their words: *"if u die all pawns incompacitated...
\\"The Company\\" sends in a goon squad kills every thing takes the dead and leeaves three new pawns
to run the facility"*.

**One fork was asked and answered: the downed.** Owner: ***"the downed: No Witnesses"***. The
trigger is *all pawns incapacitated*, so the squad lands on colonists who are **down but alive**,
and **they do not survive it.** Every downed member of the branch is killed and goes into the
ground or the fire with the already-dead. **This is a deliberate, destructive reset of the
player's roster**, confirmed before a line was written, because the other reading — stabilise and
keep them — would have preserved colonists the owner has decided do not get preserved.

### THIS EXPANDS CODE THAT ALREADY EXISTS. READ IT FIRST

`Company/FacilityRelief.cs` **is** the clean-up team, built from the owner's 2026-09-29 direction
*"so that facilities never die"*. Today it already:

* fires on `corporationContact` and **no living staff anywhere**, on the company tick,
* destroys every pawn hostile to the player (`ClearHostiles`, `Destroy(Vanish)` — not killed, so
  no corpses and no rot for the replacement crew),
* drops `CompanySupplyDrop.Fill(payload, 1f)` — the corporation's crate at full scale,
* lands **five** staff from the five `RR_*Staff` PawnKinds, registering each on the payroll,
* clears `Find.GameEnder.gameEnding`, which is the *"never losing the game"* half,
* records `reliefCount` and `lastReliefTick` as **history, never a limit** — there is deliberately
  no cap and no escalating penalty, because *"the corporation will put up with anything"*.

**Its trigger comment is now wrong and says so:** *"Downed is also not dead. A branch whose staff
are all unconscious is in trouble, not gone."* The owner has overruled that. Change the condition,
and correct the comment rather than leaving a reason nobody believes.

### THE GAPS, WHICH ARE THE WORK

| Owner's clause | What has to change |
|---|---|
| *"when all pawns incompacitated"* | trigger counts **downed as lost**, not only dead |
| *"this only happens for the lab secnerio for now"* | gate the whole thing on `ScenarioId == "async_industries"`. The other two are **owner-excluded for now**, recorded in TODO and **not** in `docs/DEFERRED.md`, which stays closed at zero rows |
| *"the downed: No Witnesses"* | kill every downed player pawn, then treat them as dead |
| *"burry the dead or incenerate on propery"*, *"might need to build graves in the moment"*, *"use and or build a crematoryium"* | Core defs confirmed present: **`Grave`**, **`Sarcophagus`**, **`ElectricCrematorium`**, **`Pyre`**. **There is no def called `Crematorium`** — it is `ElectricCrematorium`. Build graves on free cells and inter the corpses; anything that will not fit is destroyed, which is *"incenerate on propery"* |
| *"leeaves three new pawns"* | **three**, not the five `ReliefRoles` currently lands |
| *"fix broken walls and equipment"*, *"and repair"* | restore `HitPoints` to max on every damaged player building. A **destroyed** wall leaves no record, so it cannot be rebuilt — say so rather than implying otherwise |
| *"disconnect the gate"*, *"shut down the gate"* | close any open session, abort a spin-up, throw the kill switch. **Leave it commissioned** — *"like starting all over again"* means the new crew bring it back up |
| *"haull abay all bonds printed that are on the map u lose it all"* | destroy every bond on every map and credit **nothing**. `BondService.FaceValueOf` finds them; do **not** route through `DepositBondPaper`, which pays |
| *"25M is deducted ... upto 25M ... never going under 0 dollars"* | `min(25_000_000, BalanceUsd)`, through `PostTransaction` with a stable operation id so a reload cannot charge twice |
| *"leave supplies food asurvival meals"* | the crate already drops; add `MealSurvivalPack` explicitly (def confirmed present) |
| *"full sweep of every rroom"*, *"they haul everything"* | the sweep is the clearance, the corpses and the bonds. Nothing else in the facility is the squad's business |

### THE ONE DESIGN DECISION ALREADY MADE, AND IT NEEDS NO PERMISSION

**The squad is an event, not a unit.** Owner: *"can kill anything without dying"* and *"they have
keeys to all doors on map"*.

**Core-only cannot make a pawn invulnerable**, and a simulated squad that could be killed, or
blocked by a door, would break the one thing this feature is for: a guarantee. So the squad's work
is applied as **one deterministic operation** — hostiles destroyed instantly, corpses interred,
repairs applied, bonds taken, supplies and three staff dropped — and the pawns the player sees are
the three who stay. The existing `ClearHostiles` already works exactly this way and already
satisfies *"kills every thing"* and *"without dying"* by never being a combatant at all.

Door keys and invulnerability are then **moot rather than unimplemented**, and that distinction
belongs in the implementation record.

### AND THE THREE BACKLOG ITEMS, WHICH THE OWNER ALSO ASKED FOR

Owner: *"andf yes do those three things you listed as well"*.

1. **staff prior exposure** affecting how an expedition goes — `docs/TODO.md` line ~308, the
   still-open half of the *"contradictory accounts"* row.
2. **the `review` workflow** — the fourth of analyse / interview / compare / review. The other
   three ship; `review` does not.
3. **the stranded-crew rows** — verify against `Company/LostPawnRegister.cs` that closing a gate
   on a crew never takes player control of them. The row itself says it: *"If a closing gate hands
   its crew to the world-pawn pool, or despawns them, or marks them lost in any way that removes
   player control, that is a defect against this direction and the most consequential kind."*

### WHEN IT IS BUILT

**Nothing in the battery claims anything about `FacilityRelief`** — the same hole that let five
bond defects ship in one feature. A new proof is required, not optional, and it must assert the
squad is **called**, not merely written: four of the five bond defects, and seven defects before
them, were *built, correct, and unreachable*.

Then the owner's standing order, which resumes next checkpoint:
**STAGE → NOW.md → CASCADE.**

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW + ANCHOR, 1))
print("NOW.md leads with the goon squad spec; nothing staged, nothing cascaded")
