# Rest and beds: one real gap, and one "no" that Core decides for us (0.6.1-dev)

**Baseline:** `6c001ac` (0.6.0-dev, 106 C# files, 76 package files).

**This checkpoint — 0.6.1-dev:** **107 C# source files**, **76 approved package files** (unchanged — two work giver defs and two keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `1775A5EA03840F323634A8C081D5F53338D17BA53A2F779768E62BBFB823542B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/connected-rest-2026-09-29/`](evidence/connected-rest-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The rest item had three parts, and only one of them was work

Handled as one register item with everything it needed, per the standing rule.

| Part | Outcome |
|---|---|
| A tired pawn crossing a gate to sleep | **Decided against — and Core decides it, not us.** |
| Beds existing where people are | **Already covered**, verified rather than assumed. |
| Putting a casualty into a bed on the far side instead of hauling them home | **Built.** `RescueInPlaceProvider`, the fifth deployment provider. |

## A tired pawn does not cross a gate to sleep, and this one is not a judgement call

Food's equivalent "no" rested on two arguments of ours: needs come from the think tree, and a closing gate strands a starving pawn. Both apply here too. But rest has a third reason that is stronger than either, because it is Core's own rule rather than our caution.

`RestUtility.CanUseBedNow`, read at source:

```csharp
if (building_Bed.Map != sleeper.MapHeld)
{
    return false;
}
```

**A bed on a different map from the sleeper is never usable.** It is the third check in the method, before burning, before vacuum, before `CanUseBedEver`. And `RestUtility.FindBedFor` only ever searches `sleeper.MapHeld` in the first place.

So there is no "claim a bed over there" route to build. Patching Core's think tree to walk a tired pawn toward a gate would not even achieve the goal — `CanUseBedNow` would refuse the bed on arrival, and the pawn would have made a dangerous journey for nothing. That closes the question completely rather than declining it on grounds of taste.

Recorded as an invariant consequence: **a bed is only ever a bed on its own map.** Any future feature that wants to reserve, assign or own a bed across a gate is arguing with Core, and will lose.

## Beds where people are: already covered, and checked

The useful half of "beds across a gate" is that a bed should *exist* on the far side. A bed is a built thing, so that is construction, and cross-gate construction already ships in both halves:

- **material to the site** — `ConnectedConstructionAdapter` (0.5.3-dev) carries real material into a real frame or blueprint;
- **the building itself** — `ConstructionFinishingProvider` (0.5.5-dev) sends a builder across to finish a frame whose material is all delivered.

A bed blueprint on the far side therefore already attracts both. Nothing was missing, and no family was written for symmetry. Stating that is the finding; writing a redundant family would have been the mistake.

## The one real gap: bedding a casualty where they lie

This is the counterpart of the casualty family, not a duplicate of it:

| Family | What it does | When it is right |
|---|---|---|
| **Casualty carry** (0.5.2-dev) | Carries our own downed **home** to a bed | The far side has no bed for them |
| **Rescue in place** (this) | Sends somebody across to tuck them into a bed **there** | The far side does have one |

An injured person taken through a gate is one more crossing for somebody who cannot walk, and the traversal contract prefers fewer. So when there is a bed on that side, going to them beats bringing them back.

The two coexist safely without new machinery: `HasLiveCommitment` already allows a worker only one commitment at a time, and Core's own reservation on the patient settles which of two different workers arrives first.

On arrival this provider issues nothing. Core's own `WorkGiver_RescueDowned` takes over — and notably its `ShouldSkip` looks for a pawn of the worker's own faction that is downed and not in bed, which is precisely the situation that justified sending somebody. It then does the bed search, the reservation and the tucking with its own code.

### Why the candidate half is shaped the way it is

Core's `WorkGiver_RescueDowned.HasJobOnThing` needs two things, and **neither can be asked remotely**:

- `HealthAIUtility.CanRescueNow` ends in `rescuer.CanReserveAndReach(patient, ...)` — the rescuer's own map.
- the bed comes from `WorkGiver_TakeToBed.FindBed`, which is `protected`, and the underlying `RestUtility.FindBedFor` searches with `TraverseParms.For(traveler)` — a cross-map reachability query if the traveller is our remote pawn, which is exactly what the two-halves rule forbids.

So the candidate half asks only what is fair about a map nobody stands on:

| Rule | Reads | Asked remotely? |
|---|---|---|
| `map.mapPawns.SpawnedDownedPawns` | Core's own map-explicit accessor | yes |
| `patient.Downed`, `InBed()`, faction, `WantsToBeRescued` | the patient | yes |
| `IsForbidden(Faction.OfPlayer)` | the **faction** form, never the pawn form | yes |
| `ChildcareUtility.CanSuckle` → excluded | the patient | yes |
| `RestUtility.CanUseBedEver(patient, bed.def)` | a pawn and a `ThingDef`; **touches no map at all** | yes |
| `AnyUnoccupiedSleepingSlot`, `ForPrisoners`, burning, fogged | the bed itself | yes |
| `HealthAIUtility.CanRescueNow` | the rescuer's map | **no — arrival only** |
| `RestUtility.FindBedFor` with our pawn as traveller | the rescuer's map | **no — arrival only** |

Babies are excluded outright rather than half-handled: they go through `ChildcareUtility.SafePlaceForBaby`, a different route with its own rules, and Core handles them locally. A prisoner bed is excluded too — it is not somewhere our own downed colonist gets tucked in.

## Priorities

| Giver | Work type | Priority | Why there |
|---|---|---|---|
| `RR_ConnectedRescueInPlaceContinue` | Doctor | **62** | Just above Core's `DoctorRescue` (60), so a rescuer partway to a gate is not turned around by a casualty at home somebody else can reach — and still below the medical operation (70) and all tending above it. |
| `RR_ConnectedRescueInPlace` | Doctor | **3** | Below every Core doctor giver, and below both cross-gate tending (5) and feeding (4): somebody already lying on the floor across a gate is the least time-critical of the three once the gate is open. |

Twenty-two cross-gate numbers now, all player settings, tunable live.

## Saved state

**None added.** A deployment provider is data about a question, not new state. A 0.6.0-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key referenced from source resolves with 0 missing; every `giverClass` resolves to a real class.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Not done, and named

- **A tired pawn crossing a gate to sleep** — closed by Core's own rule, above. Not a gap.
- **Bed ownership and assignment across a gate** — same answer, same reason: `CanUseBedNow` rejects an off-map bed, so an assignment to one could never be honoured.
- **Animal sleeping spots and beds for non-humanlikes** are reached by the same provider where the downed pawn is one of ours, since `CanUseBedEver` is asked per pawn and per bed def; no separate family.
- **Prisoner and guest bedding** stays with prisoner and guest care, which is already its own row.
- Next: the remaining work families — cleaning, repair, firefighting, plants/mining/hunting, prisoner and guest care, wardening, childcare, animals and mechs, refuel and rearm, joy, rituals, hauling providers — then every installed work giver in the 294-row profile. Then the 1990s period and the universe factions.

## For the post-completion test phase

Opening a gate with a downed colonist and a free bed on the far side and nobody there, and confirming somebody crosses and beds them **there** rather than carrying them home; confirming that with **no** bed on the far side the casualty family carries them home instead, and that the two do not both act on the same person; confirming a baby is never picked up by this route; confirming a prisoner bed is never used for one of ours; confirming an occupied bed does not attract a trip; confirming a local casualty at home outranks starting a cross-gate trip, and that a rescuer already partway to a gate is not turned around by one; and confirming a bed blueprint on the far side is supplied and finished by the existing construction families with nothing new needed.
