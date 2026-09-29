# Eight more families in one pass: upkeep, fieldwork and fuel (0.6.2-dev)

**Baseline:** `4c5518f` (0.6.1-dev, 107 C# files, 76 package files).

**This checkpoint — 0.6.2-dev:** **110 C# source files**, **76 approved package files** (unchanged — sixteen work giver defs and sixteen keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `F575107A652079035111984660BADBD60235F80E3651FD9B025E8533AAE2A08C`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/work-families-2026-09-29/`](evidence/work-families-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## Eight families, three files, and the shape doing the work

| Family | Shape | Class |
|---|---|---|
| Cleaning | deployment | `CleaningProvider` |
| Repair | deployment | `RepairProvider` |
| Firefighting | deployment | `FirefightingProvider` |
| Mining | deployment | `MiningProvider` |
| Hunting | deployment | `HuntingProvider` |
| Plant cutting and harvesting | deployment | `PlantCuttingProvider` |
| Growing-zone work | deployment | `GrowingProvider` |
| Refuel **and rearm** | carry | `ConnectedFuelAdapter` |

Nineteen families now, eleven of them travel-to-work deployments. No new record, no new job driver, no new `JobDef` in the whole checkpoint.

## Three findings that did real work

### 1. The upkeep families are scoped for free by the Home area

Cleaning, repair and firefighting share one decisive Core rule, and it settles their whole scope without a design decision from us. All three check `map.areaManager.Home[position]`:

- `WorkGiver_CleanFilth` reads `listerFilthInHomeArea`;
- `WorkGiver_Repair` fails with `NotInHomeAreaTrans`;
- `WorkGiver_FightFires` does the same for any fire not burning on a pawn.

`areaManager` is public on `Map`, so it is a map-explicit question. And the consequence is exactly right: **a generated Backrooms coordinate with no Home area attracts none of this work**, precisely as it attracts none of Core's own. Nobody crosses a gate to sweep an anomalous corridor unless the player called it home. If the player *does* set a Home area over there, upkeep follows.

### 2. Refuel and rearm are one family, and Core says so

The register listed them as two. They are not. Core's own `RearmTurrets` work giver is **`WorkGiver_Refuel_Turret`** — a refuel giver restricted to turrets — because a turret holds its shells in a `CompRefuelable` with a shell fuel filter.

So one adapter serves a wood-fired generator, a smithy, a mortar and an autocannon, each taking whatever its own `Props.fuelFilter` accepts. Building two families would have duplicated the same code against the same comp. Reading Core first is what caught it.

That filter also means a **modded machine with an unusual fuel works for free**: the family never knows what fuel is, it asks the object.

### 3. A deployment provider answers one *question*, not one Core giver

Sowing and harvesting are two Core work givers. "Is there growing-zone work on that map" is **one question**, and on arrival Core's own two givers pick whichever applies. So they share a provider. Same for cutting and harvesting by designation.

This is worth recording as a rule, because the alternative — one provider per Core giver — would have produced four near-identical classes that all answer the same thing.

## The fieldwork families never infer anything

Mining, hunting and plant cutting are driven by **designations**; growing-zone work by a **zone**. Both are recorded on the map itself, through `map.designationManager` and `map.zoneManager`, which are public and map-explicit.

So the candidate question is *what did the player mark*, not *what could a pawn reach*. That makes these the safest families in the layer: if nothing was designated on a Backrooms coordinate, nobody crosses a gate to mine, hunt or cut anything there. Mining marks **cells** rather than things, so its candidate half reads designated cells.

## The danger question, answered

Firefighting is the first family where crossing *toward* trouble is the entire point, and the answer is deliberate:

Core's own `WorkGiver_FightFires` uses `Danger.Deadly` for its local pathing. **The crossing does not.** `ConnectedCrossing.StepToward` uses `pawn.NormalMaxDanger()`, as every automatic cross-gate step does, because a player order may accept deadly danger and automatic work may not. So a colonist crosses to fight a fire only while the route to the gate is within its own danger policy, and a burning map on the far side does not override what the player allowed.

That is the conservative reading and it is the right one: losing somebody in transit to a fire they were never ordered to fight is strictly worse than the fire.

Fires burning **on a pawn** are excluded from the remote half entirely — Core handles those with a proximity rule measured from the firefighter's own position, which is meaningless across a gate.

## Two Core internals handled honestly

**`WorkGiver_FightFires` is `internal`**, so `FireIsBeingHandled` is not callable. The rule is reproduced from the same public pieces Core uses — the fire's own reservation manager and whether the respected reserver stands within five cells — with a comment saying why it is reproduced rather than called.

**`WorkGiver_Grower.wantedPlantDef` is static mutable state** that Core writes during its own scan via `CalculateWantedPlantDef`. It is deliberately untouched: reading it would be meaningless, and writing it from a speculative remote probe could corrupt a scan in progress on another map — exactly the class of side effect the remote-probe prohibition exists to prevent. So the growing provider asks only about the zone and the plants standing in it, and Core computes the wanted def itself, locally, on arrival.

**`RepairUtility.PawnCanRepairNow` consults `pawn.Map`**, so it is arrival-only; its map-free half, `PawnCanRepairEver`, is used remotely and the remaining conditions are re-asked against the building's own map.

**`WorkGiver_HunterHunt.HasHuntingWeapon` and `HasShieldAndRangedWeapon` are public static** and read only equipment and apparel, so they are map-free and asked in `WorkerEligible`. A hunter with the wrong weapon is never sent anywhere.

## Priorities

| Giver | Work type | Continue | Plan |
|---|---|---|---|
| Cleaning | Cleaning | 22 | 2 |
| Repair | Construction | 42 | 3 |
| Firefighting | Firefighter | 82 | 2 |
| Mining | Mining | 22 | 2 |
| Hunting | Hunting | 22 | 2 |
| Plant cutting | PlantCutting | 22 | 2 |
| Growing | Growing | 22 | 2 |
| Fuel | Hauling | 16 | 6 |

The fieldwork four are **uniform on purpose**: each of those work types has a single Core giver, so a per-family number would imply a judgement that has not been made. Repair sits at 42 against Core's `Repair` (40), and its plan at 3 sits just under cross-gate construction finishing at 5, because a wall losing hit points is less urgent than a half-built one. Fuel continues at 16, just above `HaulGeneral` (15), and starts at 6 below food, medicine, construction material and bill ingredients, because something running dry across a gate is usually a planning problem and Core's local rearming at 150 will always beat it anyway.

Thirty-eight cross-gate numbers now, all player settings, tunable live.

## Saved state

**None added** by any of the eight. A 0.6.1-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key referenced from source resolves with 0 missing; every one of the sixteen new `giverClass` values resolves to a real class.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Not done, and named

- **Prisoner and guest care, wardening, childcare, animals and mechs** remain, each with its own rules and its own profile rows to read. Hospitality (270) and its two companions (285, 286) bear on guests; `WardenFeedUtility` deliberately owns prisoner feeding, which the food family excluded on purpose.
- **Joy and rituals** are need- and lord-driven rather than work-driven; expect the food and rest answer to apply, and decide it explicitly rather than leaving a row open.
- **Hauling providers** — Pick Up And Haul (164), Haul To Stack (107) and Prison Labor (288) are the three rows still open on the optional-provider register row.
- **Turret shell *choice*** — `CompChangeableProjectile` lets the player pick which shell a mortar loads. This family delivers what the fuel filter accepts and does not attempt to honour a per-turret shell preference across a gate; that is a narrower follow-up if play shows it matters.

## For the post-completion test phase

With a Home area set on the far side: confirming filth is cleaned, a damaged wall repaired and a fire beaten out by somebody who crossed for it — and with **no** Home area there, confirming none of the three attracts anybody. Confirming a designated mining cell, a designated hunt target and designated plants each pull a worker across, and that removing the designation stops it. Confirming a growing zone that wants sowing pulls a grower, and that a zone set to not allow cutting does not pull one for a plant it is protecting. Confirming a hunter without a ranged weapon, and one carrying a shield with a ranged weapon, are both never sent. Confirming fuel is carried to a dry generator, a dry smithy and an empty mortar, that a machine the player set to not auto-refuel is left alone, and that nothing crosses when fuel it accepts is already on that map. And confirming a colonist whose danger policy forbids the route does not cross toward a fire.
