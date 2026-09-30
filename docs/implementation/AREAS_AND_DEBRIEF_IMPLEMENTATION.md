# Four area types, a debrief that gates the next trip, and two rows that were already true — 0.12.36-dev

**Rows closed:** 761 (the last two halves — staff debrief and quarantine, so the row closes
completely), 1215, 1235, 1239 (the four area types across a gate), 98 and 99 (mining and building
behind a gate, and the linked-equipment exception). **Six rows, one checkpoint.**

No game was launched. Nothing here claims a gameplay, balance, performance or compatibility
result.

---

## 1. The area rows carried their own expiry condition, and it had expired

`docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md` audited every zone and area type and recorded
four as **not covered, and correctly so** — with the reason written down and a condition attached:

| Area | Why it was correctly uncovered |
|---|---|
| `Area_BuildRoof` | inside a Backrooms coordinate **every cell already carries thick rock roof** |
| `Area_NoRoof` | **roof removal there is forbidden outright** by the world rule, and `BackroomsContainment` keeps the area emptied |
| `Area_SnowOrSandClear` | a coordinate **has no outside and therefore no weather** |
| `Area_PollutionClear` | same |

The condition was *"revisit when the ordinary-map endpoint lands"*. **It landed at 0.6.9-dev** — a
registered remote site is an ordinary world map reachable through a gate — so the reason expired
and the rows became real work. A colony map genuinely wants roofs built, genuinely has roofs worth
removing, does get snow, and can be polluted.

**Nothing here changes the Backrooms rule.** `BackroomsContainment` still empties `Area_NoRoof` on
a coordinate every interval, so on a coordinate the roof family finds an empty area and offers
nobody a crossing. The rule keeps itself; this work simply has nothing to do where the rule
applies. The proof asserts the roof provider contains **no Backrooms exception of its own**,
because a second check there could drift from the one that actually enforces it.

### One split decided by a number

Snow and pollution became **routes on the existing cleaning family**. Roofs needed **their own
family**. The reason is the priority ladder and nothing else:

```
BuildRoofs                                  100   (Core)
RemoveRoofs                                  90   (Core)
RR_ConnectedConstructionFinishingContinue     82   (ours)   <- below both

CleanClearSnow                                10   (Core)
CleanClearPollution                            0   (Core)
RR_ConnectedCleaningContinue                  22   (ours)   <- above both
```

The rule every family follows is that the **continuation** giver must outrank every local giver it
travels for, or a worker part way to a gate is turned around by work that appeared at home while
it walked. Cleaning already satisfied that for both new routes. Construction did not: roof routes
hung on the finishing family would have produced exactly that thrash, and raising 82 to beat them
would have lifted *frame finishing* over roof work too — a behaviour change to a family that was
tuned deliberately.

So `RoofWorkProvider` is a third `Construction` family, continuation at **101** (one above
`BuildRoofs`) and planning at **1** (below `ConstructSmoothWalls`, the lowest local giver in the
type), and the finishing and repair families keep their numbers.

### Core's real questions, asked rather than substituted for

Unusually for this layer, almost nothing needed a presence substitute. Every condition is a fact
about the map asked about and takes no pawn:

```csharp
map.areaManager.BuildRoof.TrueCount        // Core's own ShouldSkip
map.areaManager.NoRoof.ActiveCells
cell.Roofed(map)
RoofCollapseUtility.WithinRangeOfRoofHolder(cell, map)
map.snowGrid.GetDepth(cell) < 0.2f && cell.GetSandDepth(map) < 0.2f   // Core's own OR
map.pollutionGrid.IsPolluted(cell)
```

Two deliberate omissions. **`ConnectedToRoofHolder` is not asked from here** — it walks the roof
grid and is the expensive half of Core's test, while `WithinRangeOfRoofHolder` is a cheap radius
check that always agrees when it refuses, so the cheap one runs remotely and the thorough one at
arrival. And **`map.pollutionGrid == null` is the only gate the pollution route needs**: it is null
without Biotech, so an absent expansion is an empty world rather than a condition.

The snow test is Core's own **OR** of snow depth and sand depth. Turning it into an AND would
refuse real work, and that is one of the planted faults.

---

## 2. Staff debrief and quarantine turned out to be one mechanism

Row 761's last two halves, built together because building them apart would have meant inventing
something for quarantine to be about.

### Quarantine cannot be medical here, and that is a measurement

The obvious reading of *quarantine* is *hold somebody until an infection clears*. **This package
has no `HediffDefs` folder at all** — measured, not assumed — so there is no exposure,
contamination or illness of this mod's own to clear. Inventing one would be new gameplay content,
which the standing existing-content-only constraint forbids, and it would duplicate what Core's
health system already does to anybody who comes back hurt.

So quarantine here is the **other** thing the word means in a company that sends people into
places it does not understand: **you do not go back out until you have reported in.** That gives
the debrief a consequence, gives quarantine a mechanism, and invents nothing.

### Where the hold bites, and where it deliberately does not

It bites on `Dispatch`, beside the kit check: the company will not **send** an undebriefed crew
member out again.

It does **not** bite on `PortalTraversalPolicy`. That was the first instinct and it is wrong —
traversal is the chokepoint every crossing passes through, including a player walking one colonist
through a door by hand, and a company procedure has no business refusing that. What the company
controls is whether it dispatches an expedition, and that is exactly the scope of a quarantine
rule. The proof asserts `AwaitingDebrief` appears nowhere in `PortalTraversalPolicy`.

### What raises a hold, and what does not

`Complete(run)` — the moment an expedition's whole crew is back at the headquarters, reached from
`AllAtHeadquarters`. That is the one place in the code where *"they came home"* is already
established, so nothing new detects it. **A stranded, aborted or abandoned trip raises nothing**:
those people either are not home or belong to a different procedure, and a stranded trip raising
holds is a planted fault.

Raising is idempotent per pawn, so a save reloaded across a completion cannot stack two holds on
one person. The saved list is capped at 64 and drops the oldest, because the newest report is the
one still worth hearing. A hold whose pawn is gone from the save is dropped on load rather than
kept as a row that could never be cleared and would block dispatch forever.

### What a debrief needs

Somebody else has to take the report, at home, in the same place, and be able to take it. The
Social floor is `InterviewerSocialFloor` — **the same floor witness interviews use**, which already
drops when the branch has completed `RR_Measurement_StatementDiscipline`. One floor for both,
because a branch that has practised taking statements has practised taking statements; a second
constant here would be a second opinion about one capability, and inventing one is a planted fault.

**Nobody debriefs themselves.** That is the whole point of a debrief and it is the first refusal
among the pair rules — the only one that cannot be worked around by waiting.

### What it deliberately does not do

* **No second account of the trip.** The field observations were already written where they were
  made, by `RecordFieldObservation`. This records only that the report was given.
* **No thought, no mood effect, no hediff.** A debrief that handed out a `ThoughtDef` would be this
  mod writing a social consequence on top of mods whose whole job is social consequence, and would
  need a new def. The only thing a debrief changes is whether the company will send that person out
  again — a company rule about a company decision, which is the one thing no other mod owns.

---

## 3. Rows 98 and 99 were already true, and 99's premise was wrong

**Row 98** — *"in the real world you can mine and build and explore directly behind the gates
without actually affecting the gate"*. Proved rather than built, by enumerating what **can** stop a
gate working and showing that none of it reads a neighbouring cell. Six reasons exist:

| Reason | What it is about |
|---|---|
| `RR_NativeGate_KillSwitchThrown` | the switch |
| `RR_Gate_PowerLost` | power |
| `RR_Gate_OperatorLost` | the operator |
| `RR_Gate_WindowExpired` | the clock |
| `RR_Gate_TimeCostWindowExhausted` | the clock |
| `RR_Gate_EmergencyCutoff` | a deliberate order — the player's button, and now the containment procedure |

**Not one reads an adjacent cell**, and nothing in the gate calls `CellsAdjacent`. Mine it, wall
it, roof it, put a bedroom there: the gate does not look. The proof asserts the *set*, so a seventh
reason cannot be added without this row being reconsidered. (My first count said five — I forgot
the cutoff, which is the fifth time this session a count of mine was wrong and the code was fine.)

The one placement constraint is the approach cell, closed as row 113 at 0.12.27-dev: it is reserved
against **blocking** placement and flooring is fine, because terrain never consults a
`PlaceWorker`. Every uncertainty there returns accepted.

**Row 99's premise is wrong about this mod.** The row says linked equipment constrains placement
*"because a link has a reach"*. `GateEquipmentLinks` deliberately has **no distance check and no
line-of-sight check** — owner direction was *"reach fare and through walls"*, and Core's own
`CompProperties_Facility` defaults (`maxDistance = 8f`, `requiresLOS = true`) were the opposite of
what was asked for, so the reach was removed rather than reused. Same map and same branch is the
whole spatial rule. The real constraints are power-net membership for anything with a power
component, and single ownership across gates.

---

## 4. Register rows read before building

`register-query.py family "spatial construction"` — swept, and its standing position is that this
mod adds no construction mechanic of its own and leaves native building alone. Nothing in the roof
family builds, removes or reads a roof: it reads two areas and hands out no job, so a mod that
changes roofing costs, roof types or collapse rules changes Core's answers on arrival and none of
ours. **There is no roof material named anywhere in the file.**

`register-query.py family "staff psychology"` — **one of the seven families the retro sweep has not
reached** (rows 206, 302), so its rows were read directly here rather than through the sweep. Their
shared instruction is to *"use the active trait, memory, social-fight, relationship, conversion and
faction-reaction rules"* and to *"keep the company's evaluation based on actual pawn traits, skills
and relationships"*, with the watch *"preserve native jobs, needs, guest/faction ownership, and
social behavior"*. That is honoured by the debrief writing **no thought and no hediff**, and by the
Social skill being **read and never written** — so a trait or relationship mod changes who is good
at taking a report and nothing else.

Nothing is patched, nothing is required, and every mod may be absent.

---

## 5. Files

**New:** `src/.../ConnectedWork/Providers/RoofWorkProvider.cs`,
`src/.../Company/StaffDebrief.cs`, `.local/register/proof-areas-and-debrief.py`, this record.

**Edited:** `src/.../ConnectedWork/Providers/UpkeepProviders.cs` (two weather routes on the
cleaning family), `src/.../ConnectedWork/ConnectedDeploymentProvider.cs` (the roof family id,
instance and registry row), `src/.../ConnectedWork/WorkGiver_ConnectedDeployment.cs` (two giver
classes), `src/.../Core/ConnectedWorkPriorities.cs` (the roof settings row),
`src/.../Company/RimroomsCampaignComponent.cs` (the debrief persistence call),
`src/.../Expedition/RimroomsExpeditionComponent.cs` (the completion hook and the dispatch
refusal), `src/.../UI/OperationsFacilities.cs` (the debrief section and the interviewer choice),
`1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml` (two defs),
`1.6/Languages/English/Keyed/RR_ConnectedWork.xml`, `RR_Audio.xml`, `RR_Company.xml`,
`RR_Expedition.xml`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `docs/NOW.md`,
`docs/TODO.md`, `docs/FINALIZED.md`, `docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.

**No new gameplay content.** Two `WorkGiverDef`s and seventeen keyed strings; no `ThingDef`,
`HediffDef`, `ThoughtDef`, `PawnKindDef`, recipe, bench, item, texture or sound.

## 6. Verification

* **Build 0.12.36-dev** — 188 C# files, 87 package files, **0 warnings, 0 errors**.
* **Assembly reproduced across two clean rebuilds.**
* **Eleven checkers pass. Thirty-three proofs exit zero.**
* **25 of 25 planted faults caught.**
* **A fault-plant run failed mid-way and left a planted fault on disk.** `io.open(w)` truncates
  before writing, so a failed write is not a no-op. It was found by grepping for the planted key,
  restored, and the plant harness now **reads every write back and compares** before continuing.
  Recorded because a plant harness that can silently leave a fault in the tree is worse than no
  harness.
* **No game was launched.** Every statement here is structural.
