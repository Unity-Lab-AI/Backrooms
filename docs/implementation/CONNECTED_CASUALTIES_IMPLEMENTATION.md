# Connected-colony casualties and remains — carrying our own people and our dead home (0.5.2-dev)

**TODO / feature IDs:** master TODO §Native-provider foundation, resume step 4 of [`CONNECTED_COLONY_CHECKPOINT.md`](CONNECTED_COLONY_CHECKPOINT.md). RR-GATE, RR-EXP, RR-SPACE, RR-FAC, RR-COMPAT.

**Baseline:** `fd80d71` (0.5.1-dev, 88 C# files, 76 package files).

**This checkpoint — 0.5.2-dev:** **91 C# source files**, **76 approved package files**, zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `75288E6CA3FB53407C89EF67D8414255FFD1B8AF2AD08460D1E135703FCB5393`. Evidence: [`evidence/connected-casualties-2026-09-28/`](evidence/connected-casualties-2026-09-28/), reference manifests recomputed, no drift.

**No game was launched, no test was run, no RimSort mod list was changed.**

**Owned paths.** New: `ConnectedWork/Adapters/ConnectedCasualtyAdapter.cs`, `ConnectedWork/JobDriver_ConnectedCasualty.cs`, `ConnectedWork/ConnectedWorkScan.cs`. Modified: `ConnectedWork/ConnectedWorkAdapter.cs` (registry), `ConnectedWork/Adapters/ConnectedHaulingAdapter.cs` (corpses, container candidates, shared scan), `ConnectedWork/JobDriver_ConnectedHauling.cs` (family-agnostic fetch), `ConnectedWork/ConnectedWorkRecords.cs` (mutator rename), `ConnectedWork/WorkGiver_ConnectedWork.cs` (two subclasses), `Defs/JobDefs/RR_ConnectedWorkJobs.xml`, `Defs/WorkGiverDefs/RR_ConnectedWork.xml`, `Languages/English/Keyed/RR_ConnectedWork.xml`.

---

## Why this family came before construction

The owner's gate rule names what comes back through an opening: materials, tools, equipment, resources, furniture, production equipment — **and people and monstrosities**. `PortalTraversalPolicy` has permitted a carried passenger who is downed, dead or held prisoner since 0.4.3-dev, and the crossing service has preserved one since then too. But nothing ever *ordered* the carry. A colonist who went down on the far side could not be fetched by any route, automatic or manual.

That is a capability gap in an explicit requirement, not a scheduling preference, so it was built ahead of construction supply — which is the documented next family but is an addition rather than a gap.

## Two routes, and only one of them needed a new family

### Remains: it was already ordinary hauling

Core treats corpse hauling as ordinary hauling. `WorkGiver_HaulCorpses` is `WorkGiver_Haul` with a single extra guard, and burial works because a grave is an `IHaulDestination` reached through the same storage search as anything else. So carrying our dead home needed no new family at all — only the removal of the `Corpse` exclusion from the hauling adapter, plus Core's guard:

- A corpse is not taken if `map.physicalInteractionReservationManager.FirstReserverOf(thing)` is a non-player animal. Something is eating it.
- The category check is relaxed for corpses specifically rather than in general, so the "items only" rule still holds for everything else.

**One real defect had to be fixed for this to actually work.** The candidate pass was cell-only. A grave is an `IHaulDestination` and *not* an `ISlotGroupParent`, so `IsValidStorageFor` can never see it, and a corpse whose only destination was a grave would never have been planned for — the container delivery route built in 0.5.1-dev would have sat there unreachable for exactly the case it was built for. `AnyCandidateDestination` now checks cells and then containers, walking `AllHaulDestinationsListInPriorityOrder` with each destination's own `GetStoreSettings().Priority`, `Accepts(thing)` and `GetCountCanAccept(thing)` — all of which are properties of the destination rather than of the carrier's map, so they are fair questions to ask about the other side. An invalid cell with a true answer means "yes, but it is a container", which is enough to justify the trip because the real destination is chosen definitively on arrival.

### Casualties: a new family, mostly assembled from Core

`ConnectedCasualtyAdapter` brings one of our own downed people home to a bed.

**Candidate pass, on an explicit map.** `map.mapPawns.SpawnedDownedPawns` is Core's own per-map downed list, so asking the far map about its own casualties is legitimate. Filtered to `Faction.OfPlayer`, then through `HealthAIUtility.WantsToBeRescued`, which reads only the patient's own state (downed, not already in a bed, not charging, not deactivated) and is therefore a fair question about a map nobody is standing on. Plus: not the worker itself, not faction-forbidden, not in fog, not already leased, and inside the worker's observed allowed area for that map and for the arrival threshold.

**One direction, deliberately.** You carry a casualty *out*; you never carry one in. The destination is whatever map the worker is standing on, and the pass does not even start unless that map has a candidate bed — so it works from headquarters and from a staffed forward space without assuming which is which.

**Capture is deliberately absent.** Core makes taking a downed stranger prisoner a player order rather than automatic work, and the owner's rule is explicit that people and monstrosities come back because the player directed it. Automatic work rescues our own; anything else stays the player's call through the ordinary crossing order that already exists. This is a design decision, not a gap.

**The definitive far-side check is Core's own.** `HealthAIUtility.CanRescueNow(rescuer, patient, forced)` — same faction, wants rescue, not forbidden, no enemy within 25 cells, reservable and reachable. It was read before being trusted, and the important fact is what it does *not* check: it has no bed requirement. That is exactly why it is the right question on the far side, where there may be no bed at all, and why the bed is a separate question at the other end.

**The bed question answers itself once the worker has crossed.** `RestUtility` rejects a bed whose map differs from `sleeper.MapHeld` — which is the pinned review's warning, and it is why a remote bed search is impossible. But a *carried* pawn's `MapHeld` is the carrier's map. So after the crossing, `RestUtility.FindBedFor(patient, carrier, checkSocialProperness: false, ignoreOtherReservations: false, patient.GuestStatus)` — the same call Core's own `WorkGiver_TakeToBed.FindBed` makes — answers about the beds that are actually here. The two-phase contract fits this family without bending.

**Placement is Core's own bed handoff.** `JobDriver_ConnectedTakeToBed` is only the placement half of Core's take-to-bed job, built from Core's own public toils: `Toils_Bed.ClaimBedIfNonMedical`, goto with `FailOnBedNoLongerUsable`, `Toils_Reserve.Release`, `Toils_Bed.TuckIntoBed(bedIndex, takeeIndex, rescued: true)`. Core owns the actual handoff, which keeps bed ownership, medical-bed rules and rescue notifications correct rather than reimplemented. Reservations mirror Core exactly, including clearing the casualty's own claims first and reserving the bed by sleeping slot rather than whole.

**Why not just reuse Core's `Rescue` job for the delivery?** It was inspected, and it very nearly works: `JobDriver_TakeToBed` already jumps past both its goto and its pickup when `pawn.IsCarryingPawn(Takee)`, so an already-carrying worker is genuinely handled. The reason it is not reused is narrower — the job knows nothing about the saved intent, so nothing would record the trip's outcome, and maintenance would later read "cargo no longer in hand" as a failure for a rescue that in fact succeeded. Owning the driver means owning the finish action.

**The failure mode is a handoff, not a loss.** `RR_ConnectedTakeToBed` sets `carryThingAfterJob` to **false**, unlike every other segment. If the placement fails, Core sets the casualty down where the worker stands — and by then they are on this side of the gate, downed and not in a bed, which is precisely the situation Core's own rescue work giver exists to handle. The cross-gate part of the trip has already succeeded, so the intent closes as **Completed** whenever the worker reached the destination map, whether the person ended in the bed or beside it. A worker carrying someone around indefinitely would have been the worse outcome.

Two other outcomes are Completed rather than Failed for the same reason: arriving to find no bed free, and the person coming round while being carried. In both cases they are physically home, which is what the trip was for.

## Shared, not copied

`ConnectedWorkScan` now owns the rotating-window rules — `RotationOffset`, `WindowStart`, `ConnectedMaps` — and both adapters use it. The hauling adapter's private copies are gone. This is deliberate rather than tidiness: the rotating-window rule is subtle enough that a per-family copy would drift, and the drift would be invisible, because a scan that reads a fixed prefix looks identical to a correct one until the fifth gate opens. That was already caught once in 0.5.0-dev; one implementation means it cannot be reintroduced per family.

The fetch segment is also now shared. `RR_ConnectedFetch` serves both families, because Core carries a downed pawn with the same carry toil it uses for a crate. Its reservation was corrected to reserve a person *whole* (`stackCount` −1, as Core reserves a rescue target) rather than by quantity.

## Saved state

**No new saved key and no schema change.** The casualty family reuses the existing intent shape exactly: the patient is the intent's `SourceThing` and then its `Cargo`, and the bed is its `FinalTarget` — which is the field reserved from schema 1 for "the native object the work finally belongs to", used here for the first time as intended. The mutator was renamed from `RecordResolvedContainer` to `RecordResolvedTarget` to match what the field has always meant.

A 0.5.1-dev save loads unchanged.

## Work-giver placement

| Def | `priorityInType` | Neighbours in Core's `Doctor` |
|---|---|---|
| `RR_ConnectedCasualtyContinue` | 65 | above `DoctorRescue` (60), below the urgent doctor work at 70+ |
| `RR_ConnectedCasualty` | 59 | directly below `DoctorRescue` (60) |

Finishing a trip that already has someone in the worker's arms edges above native rescue; starting one sits just below it, so a casualty on *this* map is always rescued first. Both stay under the more urgent doctor work. Balance decisions, recorded as such and subject to the owner's runtime acceptance.

## What this closes, and what it does not

**Closes:** the "people and corpses as connected work" row, both halves. Our own downed people come home to a bed; our dead come home to a grave or a stockpile.

**Does not close, and is not claimed:**

- **Tending across a gate.** A doctor crossing to treat someone who stays where they are, or medicine carried to them, is a different capability from carrying a person back, and it needs its own adapter with its own medicine-as-cargo handling. Still owned by step 4.
- **Surgery, prisoner and guest care routes, patient feeding, self-tend.** Each is a distinct native route per the pinned review.
- **Construction supply and finishing, bills, research, food, rest** and the remaining families.

## Owner-launched acceptance, deferred

A colonist downed on a site with a rescuer at headquarters and a medical bed free; the same with no bed free, confirming they are set down on the near side and native rescue then takes over; the casualty coming round mid-carry; the rescuer drafted, downed or sent into a mental break at each of the four segments; save and reload while carrying a person mid-crossing, confirming the receipt holds one person and one carrier without duplication; two rescuers offered the same casualty; a casualty outside the rescuer's observed allowed area on the far side; a corpse hauled home to a grave and to a stockpile, confirming the container and cell routes are each taken once; a corpse an animal is feeding on being left alone; and a site with more than four connected maps open, confirming the rotating window reaches all of them for both families.
