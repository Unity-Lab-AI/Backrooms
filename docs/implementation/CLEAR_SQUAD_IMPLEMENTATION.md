# The company clears the site — 0.12.76-dev

**Date:** 2026-10-01
**Assembly SHA-256:** `B3B0B052445A706CF8A1F1BED154C9CA813B756AA019F773B7C26EE2225F6774`
(measured after the version bump, reproduced by two clean rebuilds)

---

## The direction

Owner, verbatim:

> *"a the company clear squad when all pawns incompacitated.. they should arrive do a full sweep of
> every rroom on the reall world map, disconnect the gate and burry the dead or incenerate on
> propery might need to build graves in the moment then they go through the whole facility fix
> broken walls and equipment leave supplies food asurvival meals like starting all over again but
> this happens in game with the player never losing the game. but this only happens for the lab
> secnerio for now"*

And the short version:

> *"if u die all pawns incompacitated... \"The Company\" sends in a goon squad kills every thing
> takes the dead and leeaves three new pawns to run the facility they have keeys to all doors on
> map and can turn off the game and leave supplies and can kill anything without dying and use and
> or build a crematoryium and or graves to bury everthing dead then they haul everything and repair
> and shut down the gate and haull abay all bonds printed that are on the map u lose it all and 25M
> is deducted from account for \":restocking the pedycash\" upto 25M from account never going under
> 0 dollars in account"*

One fork was asked and answered before a line was written:

> *"the downed: No Witnesses"*

The trigger **is** total incapacitation, so the squad lands on people who are breathing and does
not leave them breathing. **This is a deliberate, destructive reset of the player's roster**,
settled in advance because the other reading — stabilise and keep them — would preserve colonists
the owner decided do not get preserved.

---

## The owner's challenge found two false statements in the handoff

Before any code was written the owner asked:

> *"are u shure zero goon squad code is written weve gone over this before by a different name"*

The handoff had asserted *"ZERO code written"* on the strength of `src/` matching the previous
checkpoint — which proves only that **this session** had written none. It says nothing about what
was built earlier under another name, and this repository has been caught by exactly that **nine
times**. The grep that answers the question found three things.

| The handoff's claim | What was true |
|---|---|
| *"Nothing in the battery claims anything about `FacilityRelief`"* | **`proof-facility-relief.py` is proof FIVE**, shipped 0.11.7-dev, and two of its claims contradicted the new direction |
| *"Core defs confirmed present: Grave, Sarcophagus, ElectricCrematorium, **Pyre**"* | **`Pyre` is Ideology**, in `Ideology/Defs/ThingDefs_Buildings/Buildings_Ideo.xml` |
| — | **`RepairableOn(map, faction)` already existed**, wrapping Core's own repairable lister |

The `Pyre` error is the instructive one: the check ran against the **installed game** rather than
against **Core**. For a Core-only mod that is the entire distinction, and it read as a pass because
it answered the wrong question.

The third find was pure profit — a second damaged-building scan was deleted from the plan before it
existed. **A second derivation of one rule is the defect this project keeps meeting.**

---

## The scoping saved two proof claims that looked like casualties

`proof-facility-relief.py` asserts *the relief requisitions five roles* and *the living-staff scan
does not treat downed as dead*. Both looked doomed — until the owner's own scoping resolved it:
*"this only happens for the lab secnerio for now"*.

So the squad is a **separate path**, not an edit to the old one:

```
TickFacilityRelief()
  ├─ laboratory  → TickClearSquad()      downed counts as lost, three staff
  └─ store, solo → AnyLivingStaff()      dead only, five staff   [unchanged]
```

The fork sits **above** the relief's own trigger, so the laboratory never reaches it. Both old
claims still hold untouched, and the comment that explained the old reasoning is **scoped rather
than deleted** — it is still a true statement about the path it guards. **A reason nobody believes
is worse than no reason.**

Making the change universal would have silently rewritten the bargain for two scenarios the owner
excluded. That is the defect shape this project keeps meeting: one rule, quietly applied where
nobody asked for it.

---

## The squad is an event, not a unit

The owner asked for a squad that *"can kill anything without dying"* and that *"have keeys to all
doors on map"*.

**Core cannot make a pawn invulnerable**, and a simulated squad that could be shot, or stopped by a
locked door, would break the single thing this feature exists to provide: a guarantee that a branch
never dies. So the work lands as **one deterministic operation**, and the only pawns the player
ever sees are the three who stay.

Door keys and invulnerability are therefore **moot rather than unimplemented** — there is no one to
stop and no door to open. `ClearHostiles` has worked exactly this way since 0.11.7-dev.

---

## What the squad does, in the order the owner described it

| Clause | Mechanism |
|---|---|
| *"when all pawns incompacitated"* | `AnyCapableStaff()` — counts `Downed` as lost, and still asks **anywhere**, so a crew standing in a coordinate is not a dead facility |
| *"the downed: No Witnesses"* | `SilenceWitnesses` — player-faction humanlikes and prisoners of the colony, killed not destroyed because the burial needs a body |
| *"kills every thing"* | existing `ClearHostiles`, which vanishes hostiles so the replacement crew do not inherit corpses and rot |
| *"takes the dead"*, *"burry the dead or incenerate on propery"* | `InterTheDead` — a `Grave` where ground will take one, destruction where it will not |
| *"fix broken walls and equipment"* | `RepairTheFacility` through the existing `RepairableOn` wrapper over Core's lister, and Core is told the building is whole again |
| *"disconnect the gate"*, *"shut down the gate"* | `ShutDownGates` — `AbortSpinUp` for a ramp, `TriggerEmergencyCutoff` for an open connection. **Left commissioned** |
| *"haull abay all bonds ... u lose it all"* | `ConfiscateBonds` → `BondService.ConsumeBonds`, credited **nowhere** |
| *"25M ... upto 25M ... never going under 0"* | `min(25_000_000, BalanceUsd)`, clamped before posting, with the clearance number in the operation id |
| *"leave supplies food asurvival meals"* | the existing crate at full scale, which already carries 30 `MealSurvivalPack` |
| *"leeaves three new pawns"* | three roles — operations, engineering, security |
| *"never losing the game"* | `Find.GameEnder.gameEnding = false` |

**The order matters and is asserted.** Witnesses are silenced *before* the dead are gathered, or a
pawn still down when corpses are collected would be left on the floor of a finished facility. And
**the charge is posted after the arrival is certain** — billing twenty-five million and landing
nobody would be worse than the failure itself.

---

## The grave does not fit indoors, and that was measured

Core's `Grave` is **(1,2)** — two cells, not one — and needs the **`Diggable`** terrain affordance.
Exactly **ten** Core terrains carry it:

```
Soil  SoilRich  Sand  SoftSand  Gravel  PackedDirt  MossyTerrain  MarshyTerrain  Riverbank  Ice
```

**Every constructed floor is excluded** — `Concrete`, `SterileTile`, `MetalTile`, every stone tile,
every carpet, every bridge. **So a grave cannot be dug inside the facility at all.**

Found by reading the game's own data rather than at runtime, which is the difference between a
feature and a feature that never worked. Burial goes to open ground; the facility's unroofed
breezeway and compound are exactly that.

The footprint is checked through **`GenAdj.OccupiedRect`** and the affordance through
**`GenConstruct.CanBuildOnTerrain`** — Core's own arithmetic, because three separate models of
rotation maths have already disagreed in this project and a local table of diggable terrains would
go stale the first time Core added one.

**No crematorium is built.** A bill needs a worker and there is nobody alive to work it, so an
unpowered one would be scenery pretending to be a mechanism. Destruction is the incineration.

---

## Mod register

Rows **4–9** are Core and the five expansions. Rows 5–9 carry stance **Optional**, and row 5 carries
firmness **Provisional**. **The owner has overruled all five into hard dependencies**, which is the
register being *"not law but guidance"* working exactly as the owner's standing correction says it
should. The rows are not wrong; they are superseded, by the only authority that can supersede them.

Row **77**, *Doors Expanded*, is still patched through `PatchOperationFindMod` and nothing about
that changed.

---

## Verification

**`proof-clear-squad.py` is proof FORTY-SEVEN** — 31 claims, and almost every one asserts something
is **called**, **saved** or **visible** rather than merely written. Four of five bond defects, and
seven before them, were *built, correct and unreachable*.

**`plant-clearsquad.py` is suite EIGHTEEN — 27 of 27 planted faults caught.** The weighting is
deliberate: the first plants cut the call, not the code. One exists purely to protect somebody
else's promise — giving `AnyLivingStaff` the laboratory's trigger, verified against
`proof-facility-relief.py`, because that is the proof that should scream.

```
16 checkers pass        48 proofs hold        738 plant anchors findable
210 C# files            92 package files      0 warnings, 0 errors
```

**And `check-plant-anchors.py` earned its place twice in one checkpoint**: once rejecting the first
draft of a plant table written in the wrong shape, and once catching a letter trim that had
invalidated an anchor — in bulk, without anybody running the suite.
