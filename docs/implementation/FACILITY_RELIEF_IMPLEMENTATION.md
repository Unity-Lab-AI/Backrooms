# The corporation does not write off a branch — 0.11.7-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including the five defs it found
already written and wired to nothing. Never rewritten.

---

## The direction

> *"ie u need certain logs complete to operate the higher teri techs and shit and gate features
> and upgrades all story line in quests layed out and coporation requasts and missions.. and
> remember **the mega mother corp is greedy and will basic do anything and put up with anything to
> make sure you succssed to the point of sending clean up teams to your base with all access
> passses to wipe the facitly of all hostals and requisition a new basic team supplies drops like
> a fresh start of sorts so that facilities never die**, this is liken the store and solo/group
> scenerios once they reach contact with the corporation"*

And the scoping answer at the fork that followed:

> *"clena up tema is only once u are in communication and working with the corporation"*

---

## The register, checked first

Filtered on the families this touches: **world threat and event pacing** (3 rows), **faction
standing** (11), **scenario setup** (11), **recovery systems** (27).

One row matters and it is the reason a design decision below is written the way it is:

**[199] Safely Hidden Away (Continued)** — *World threat and event pacing*, Optional. It changes
how the game reasons about colonists who are not present. This mod routinely has an entire crew
standing inside a Backrooms coordinate, which is a different map, and that is **exactly** the
state the relief must not mistake for a dead facility. The rule below — *alive anywhere*, never
*alive here* — is now asserted by the proof rather than left to a comment.

**[150] No Solar Flares** is marked *No integration* and is unaffected: the relief reads no
`GameCondition` and fires from a company tick, not an incident.

Nothing else applied.

---

## Five defs that were already written and read by nothing

`1.6/Defs/PawnKindDefs/RR_Staff.xml` has held **five** `PawnKindDef`s since long before this
session: `RR_OperationsStaff`, `RR_ResearchStaff`, `RR_EngineeringStaff`, `RR_SecurityStaff`,
`RR_MedicalLogisticsStaff`, all under an abstract `RR_StaffBase`, each with skill ranges and work
tags matching one of the five company roles exactly.

**Not one source file mentioned any of them.** They loaded every run, validated every run, and
nothing in the game could ever produce one.

That is invariant 131 in its purest form, and it is the third time this session the same shape
has come up:

> *"make sure shit isnt unused it was put there for a reason"* — **a def nobody wired is a job
> nobody finished, not a def nobody wanted.**

They were authored for a five-person company crew. The relief team **is** a five-person company
crew, one per role. This is the job they were written for, and the queue entry that called them
*"unbuilt"* was wrong — they were built and orphaned, which is a different and more dangerous
thing, because an orphaned def looks finished from every angle except the one nobody checks.

The proof now asserts **both directions**: every kind the relief names exists, and every
`*Staff` kind we ship is read by the relief. They cannot quietly go back to being dead.

---

## Why this is not an `IncidentDef`

Owner decision at the storyteller fork, verbatim: ***"Both - guaranteed floor, storyteller
flavour"***.

This is the floor half, and it is deliberately **not** an incident:

**A storyteller decides whether and when to fire an incident. *"Facilities never die"* admits
neither question.** Cassandra weighting a rescue against colony wealth, or Randy declining to
roll it, would turn a promise into a probability. The player has been told they cannot lose, and
they arrange their play around that.

The storyteller half — lighter, world-facing events the player's own chosen storyteller paces —
is a separate surface and is next. It does not belong in the same code path as a guarantee.

---

## What it does, and the three decisions inside it

### It fires on "no employed staff alive **anywhere**"

Not *"no staff here"*. A crew standing in a Backrooms coordinate is alive, the facility is not
dead, and a player who takes everybody through a gate must never come home to a relief team and a
duplicate payroll.

**Downed is also not dead.** A branch whose staff are all unconscious is in trouble, not gone, and
replacing people who are about to stand back up would have the corporation paying twice for the
same five jobs. It is also the obvious exploit — put your crew on the floor, collect a free crew —
and it is closed by the definition rather than by a counter-measure bolted on afterwards.

Both of those are asserted. The proof fails if the scan ever starts asking about `Spawned`,
`Map` or `Downed`.

### Hostiles are removed, not killed

*"all access passses to wipe the facitly of all hostals"*.

A clean-up team that left forty corpses on the floor of a facility with nobody in it to haul them
has not cleaned anything up. The rot, the filth and the mood penalty would land on the
replacement crew, who were not there for any of it. They are removed.

Only things genuinely hostile to the player, never the player's own — a colonist, a player animal
or a downed friendly is not swept up.

### There is no cap and no escalation

The corporation *"will put up with anything"*. A rescue that gets stingier the third time is a
deadline wearing a different hat, and §1.1 of the chart forbids those everywhere but the gate.

`reliefCount` is a **record**, and `lastReliefTick` is a **timestamp**. The proof asserts that
nothing compares either one against a limit, because the difference between a record and a
countdown is entirely in whether something reads it that way.

---

## The Core fact this stands on

When the last free colonist dies, `GameEnder.CheckOrUpdateGameOver()` sets `gameEnding = true`
and `ticksToGameOver = 400`, and the game-over letter lands 400 ticks later.

Read from the decompiled assembly rather than remembered:

- **`gameEnding` is a `public bool` field**, so the relief clears it directly and no Harmony patch
  is needed.
- **Core clears it itself** the moment any map holds a free colonist — `CheckOrUpdateGameOver`
  returns early on `FreeColonistsSpawnedOrInPlayerEjectablePodsCount >= 1`. So landing a crew is
  usually enough on its own.
- **400 ticks** is the whole budget. The relief is checked every **60**, which lands well inside
  it with room for a slow frame.

The relief does both: it lands the crew *and* clears the flag. Relying on Core to notice in time
is not the same thing as making sure, and all three of those facts are now asserted by the proof
against the live assembly — if a Core update moves any of them, this repository finds out before
a player does.

---

## Not routed through the hiring pipeline

`RegisterHiredStaff` exists to reconcile an onboarding charge against a saved quote, and its
refusals are almost entirely receipt checks.

**There is no charge here** — the parent corporation is paying for its own rescue. Sending a free
arrival through a function whose whole job is matching receipts would mean **inventing a receipt
to satisfy it**, and a fabricated ledger entry is worse than a second code path.

They are ordinary employees from the moment they land, on the ordinary wage read from the hiring
policy rather than restated as a constant. The next payroll bills for them like anybody else.
**The rescue is free; keeping the people afterwards is not.**

---

## The proof was fault-planted four ways

| Fault planted | Caught by |
|---|---|
| living-staff scan starts asking `pawn.Spawned` | *"does not ask where the pawn is"* |
| `ComponentIndustrial` renamed | *"is a Core ThingDef"* |
| the `corporationContact` guard removed | *"refuses before corporation contact"* |
| `reliefCount >= 3` added as a cap | *"nothing compares the relief count against a limit"* |

Four faults, four catches, each by the claim written for it, all restored. **A proof that has only
ever passed has not been tested** (invariant 109).

---

## Receipts

| | |
|---|---|
| Version | 0.11.7-dev |
| Build | 163 C# files, 85 package files, **0 warnings, 0 errors** |
| New defs | **none** — five existing `PawnKindDef`s wired for the first time |
| New art, audio or texture | **none** |
| Harmony | **none** — `GameEnder.gameEnding` is a public field |
| New keyed strings | **3** |
| Checkers | **eight**, all passing |
| Proofs | **five**; the new one fault-planted four ways |
| Game launched | **no** |

Next: the storyteller half — `IncidentDef`s with our own `IncidentWorker`s for the lighter
world-facing events, so the player's chosen storyteller paces them. This mod still has zero.
