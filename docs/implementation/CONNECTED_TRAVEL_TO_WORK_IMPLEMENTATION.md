# Travel-to-work: a builder crosses a gate, and Core does the building (0.5.5-dev)

**Baseline:** `d78559b` (0.5.4-dev, 94 C# files, 76 package files).

**This checkpoint — 0.5.5-dev:** **99 C# source files**, **76 approved package files** (unchanged — no new package file, two work giver defs and nine keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `00D209DC9AD497E054A9FB11D71D4FCEEB8826B72329315C8C73B3F90A82B26C`, **reproduced after deleting `obj/` and `bin/` and recompiling from scratch**. Evidence: [`evidence/travel-to-work-2026-09-28/`](evidence/travel-to-work-2026-09-28/); reference manifests recomputed, no drift.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## What this closes

Two deferment rows, and the owner's selected next build:

> Construction finishing — a worker crossing to do build work with nothing carried. Needs the travel-to-work intent shape rather than another adapter.

Every family shipped in 0.5.0-dev through 0.5.3-dev is **fetch → carry → deliver**: storage hauling, casualties and remains, construction supply. Construction *finishing* is not that shape. A frame whose material is all delivered does not need anything carried to it — it needs somebody to stand next to it and build. So does research, so does tending in place, and so does every other family where the work happens at the far end with empty hands.

Building that inside an adapter would have put it in the wrong place, which is why it was deferred rather than bolted on.

## The shape, and why it is a sibling record

The design question recorded at handoff was: a new phase on `ConnectedWorkIntent`, or a separate record. It is a separate record — `ConnectedDeploymentIntent`, with its own `ConnectedDeploymentPhase` of `Travelling → Deployed → (Completed | Cancelled | Failed)`.

Three reasons, in order of weight:

1. **The intent integrity check would have to be weakened.** `ValidateSavedState` faults a `Planned` intent with no `SourceThing` and a `Carrying` intent with no cargo. Those two rules are what stop a half-formed trip loading out of a save and moving somebody's goods. A deployment has neither a source object nor cargo, so reusing the record means carving an exemption into the guard that protects three shipped families — and the exemption would be invisible at the call site.
2. **The adapter contract is fetch-shaped by construction.** `TryPlan` / `RevalidateAtFetchSide` / `FetchJob` / `RevalidateAtStoreSide` / `DeliverJob` describes a carry. A deployment has no fetch side and no delivery, so four of the five would be stubs, and a stub in a contract is an invitation for the next family to fill it in with something wrong.
3. **A sibling duplicates almost nothing.** Everything a deployment actually shares — the planning cooldown, the destination refusal memory, the bounded route cursors, the traversal policy, the crossing job — lives on the component and the work giver, not on the record. The sibling's only duplicated field is an expiry tick.

## What the deployment is actually for

It issues no work. On arrival it hands out nothing at all.

That restraint is the design. Once the worker is standing on the destination map, Core's own `WorkGiver_ConstructFinishFrames` is already scanning that map in this pawn's own priority order, and it will take the frame with its own reservation, its own blocking-thing handling and its own toils. Reimplementing any of that would mean reimplementing all of it and getting something subtly wrong.

So what does the record do? It stops the thrash. Without it:

- the worker crosses, builds, and on the very next job search the cross-map hauling planner offers it a trip home — so it abandons the frame it just crossed for;
- or it crosses, finds the work already done, and crosses straight back, forever.

The record is the memory that says *this person is over there on purpose*. `HasLiveCommitment` is the single chokepoint enforcing one commitment per worker across both record kinds, checked in `Open`, `OpenDeployment` and both work giver families — because a worker promised two things abandons one of them, and which one would depend on job-search timing rather than on anything designed.

## The two halves of validation, kept apart

The invariant holds unchanged: a candidate predicate may read an explicit `Map`; it may never ask a native pawn-specific question about a map the worker is not standing on.

Core's own `GenConstruct.CanConstruct` was read and split by **what each rule reads**, not by guesswork:

| Rule | Reads | Asked remotely? |
|---|---|---|
| `frame.Faction != pawn.Faction` | the frame, the pawn | yes |
| `frame.IsCompleted()` (all material delivered) | the frame | yes |
| `frame.WorkLeft > 0` | the frame | yes |
| `frame.IsBurning()` | the frame's own map | yes |
| `IsForbidden(Faction.OfPlayer)` | the frame, the player faction | yes — the **faction** form |
| `Position.Fogged(map)` | the explicit map | yes |
| `GenConstruct.FirstBlockingThing` | the frame's **own** map, identity compare only | yes |
| construction and artistic skill prerequisites | the pawn's skills, the frame's def | yes |
| `pawn.Ideo.MembersCanBuild(frame)` | the pawn's ideo, the frame | yes |
| `GenConstruct.CanTouchTargetFromValidCell` | the **worker's** map, via `RCellFinder` | **no** — arrival only |
| `CanReserveAndReach` | the **worker's** map and reservation manager | **no** — arrival only |

Note the forbidden check uses the **faction** overload remotely, not the pawn overload: the pawn overload consults the pawn's allowed area *in its current map*, which is the wrong map. The allowed-area question for the far side is answered from `ObservedAreaAllows` — what we last saw while the worker was legitimately standing there — with an unobserved map reading unrestricted, which is Core's own answer for a map no area was ever set on.

On arrival, `HasWorkHere` calls Core's own `GenConstruct.CanConstruct` outright, plus `frame.IsForbidden(pawn)` because Core's scanner framework filters forbidden things *before* calling its giver and so `CanConstruct` does not check it itself.

### One deliberate asymmetry in the scan bound

The remote candidate scan is a **rotating window** (`MaximumFramesPerMap = 24`), per the standing rule that a bounded scan is never a prefix. The arrival check is **not windowed**, and that is on purpose: a window that missed the work would release a deployment while there was still work to do, and the worker would be planned straight back across the gate — the exact thrash the record exists to prevent. A remote miss costs one cooldown; an arrival miss costs a loop. The cost of the unwindowed pass is one scan of Core's own frame group, for a worker that is already deployed.

## Priorities, against Core's real ladder

Core's `Construction` work type, read from `Data/Core/Defs/WorkGiverDefs/WorkGivers.xml`:

`120` FixBrokenDownBuilding · `110` Uninstall · `100` BuildRoofs · `90` RemoveRoofs · `85` DeconstructForBlueprint · **`80` ConstructFinishFrames** · `70` DeliverResourcesToFrames · `60` DeliverResourcesToBlueprints · `51` FillIn · `50` Deconstruct · `40` Repair · `30` RemoveFoundations / RemoveFloors · `20` SmoothFloors · `10` SmoothWalls

| Giver | Priority | Why there |
|---|---|---|
| `RR_ConnectedConstructionFinishingContinue` | **82** | Above frame finishing, so a builder partway to a gate is not turned around by a frame that appeared at home while it walked. Still below clearing a blueprint site (85), roof work, uninstalls and breakdown repair, which are more urgent or block other work outright. |
| `RR_ConnectedConstructionFinishing` | **5** | Below *every* Core construction giver. Crossing a gate to build happens only when there is nothing constructive left on this side at all — not even smoothing a wall. |

Both are balance decisions, recorded as such, subject to the owner's runtime acceptance.

### The pinned fact that made an explicit guard necessary

`JobGiver_Work.TryIssueJobPackage` was re-read for this checkpoint. It is a **single loop in priority order**, and for each giver it calls `NonScanJob` first and returns immediately if that produced a job; the scanner branch only accumulates `bestTargetOfLastPriority`, and the loop breaks out at the next *different* priority once a target is valid.

So a lower-priority `NonScanJob` cannot steal a higher-priority scanner's hit — but "there is local work" still cannot be **inferred** from the priority number, because the planning giver's `NonScanJob` runs before its own priority band's scan resolves in the general case. The planner therefore asks `provider.HasWorkHere(pawn)` outright and refuses to plan while local work of the same kind exists. Without that call a builder would cross a gate while frames waited at home, and the bug would have been invisible in review because the priority numbers look correct.

## Release, and never dragging anyone home

| Situation | Ending | Refusal recorded? |
|---|---|---|
| Arrived, no qualifying work (was still `Travelling`) | `Cancelled`, `RR_ConnectedWork_NoWorkOnArrival` | **yes** — we walked for nothing; leave the map alone for a while |
| Work ran out while `Deployed` | `Completed` | **no** — coming back when there is more to do is correct |
| Worker left the destination map while `Deployed` | `Cancelled`, `RR_ConnectedWork_WorkerDeparted` | no |
| Attempt cap hit at the threshold | `Failed`, `RR_ConnectedWork_RouteExhausted` | yes |
| Route graph genuinely exhausted | `Cancelled`, `RR_ConnectedWork_NoRoute` | no |

Closing a deployment moves nobody. A worker whose deployment ends is simply free, standing where it stands, with its own needs and whatever local work it finds — which is what the portal contract already says about anyone who crossed legitimately. **Nothing in this layer walks a pawn home.**

### The lease does not count down once the worker has arrived

While `Travelling`, the ordinary `LeaseDurationTicks` window applies: a journey that has not progressed is stale. Once `Deployed`, there is no countdown at all, and what ends the deployment is *leaving the map*.

This is not leniency. A countdown would expire the deployment overnight while the builder slept beside an unfinished wall, and the anti-thrash guard would drop at exactly the wrong moment. A worker standing where it was sent needs no timer, because its being there is the whole content of the record.

## One implementation of stepping through a gate

`ConnectedCrossing.StepToward` was extracted from `WorkGiver_ConnectedWork.CrossToward` — a pure extraction, behaviour unchanged — and is now shared by the carry families and travel-to-work.

This matters because the rules attached to that step are not decoration: automatic work respects the pawn's own danger policy, its allowed area, and locked or forbidden doors, where a *player* order may use `Deadly`. A second copy would drift, and the drift would be a colonist walking into something the player told it to avoid.

What deliberately stays with each caller is the attempt cap and what a refusal costs, because the endings differ: a carry trip out of attempts has failed with cargo in real hands and is worth the player's attention; a deployment out of attempts has cost a walk.

## Saved state

| Owner | Key | Rule |
|---|---|---|
| `RimroomsConnectedWorkComponent` | `rr_connectedWorkDeployments` | **Additive, no schema bump.** Absent from every save before this build, which loads correctly as "nobody is deployed" — the same pattern as `rr_connectedWorkAreaObservations` before it. A 0.5.4-dev save loads unchanged. |

`nextSequence` is shared between intents and deployments, so ids stay unique across everything the branch saved. `ValidateSavedState` shares both its id set and its live-worker set across the two lists, so a save cannot load with one worker owing a carry trip *and* a deployment — a state with no defined answer for which wins.

What the deployment check deliberately does **not** require is a source object. That absence is the whole reason this is a separate record rather than an exemption inside the intent check.

There is also deliberately **no saved reference to the frame that justified the trip**. A deployment lasts as long as *any* qualifying work remains on that map, so keying it to one frame would end it the moment that frame finished — the opposite of what is wanted.

## Player-facing

The Operations connected-work pane lists deployments separately from carry trips, because reading them as hauling would be misleading: nobody here is bringing anything back. Each line names the worker, the work that justified the trip, the destination, and whether they are still walking. Nine keyed strings added; every referenced `RR_` key resolves (530 referenced from source, 0 missing).

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted, full recompile, identical assembly SHA-256.
- All 58 package XML files parse.
- Every `RR_` key referenced from C# resolves in a keyed file: 530 referenced, 0 missing.
- Every `giverClass` in a `WorkGiverDef` resolves to a class that exists in source.
- No AI-attribution string anywhere in source or package: 0 hits.
- 76 approved package files, 0 missing from disk. Reference assemblies recomputed, no drift.

## Not done, and named

- **Bills and unfinished work** is next, per the owner's ordering decision to finish the work families before the faction layer. It needs the *carry* shape again, keeping the actual `Bill` and unfinished-thing references rather than a def and a count.
- **Research** is the next natural travel-to-work provider and should reuse this shape directly: it is stationary work at a real bench with nothing carried. This checkpoint deliberately shipped one provider rather than two, so the shape is proven against one reviewed native route first.
- **Tending across a gate** still needs medicine-as-cargo and its own source review per native route.
- **Balance review** of the two new priorities (82 and 5), like the existing families', needs play to judge feel.

## Owner-launched acceptance, deferred

Opening a gate with an all-material-delivered frame on the far side and no construction work at home, and confirming a builder crosses and finishes it; confirming a builder does **not** cross while any local construction work remains, down to smoothing a wall; confirming the worker is not walked home when the far-side work runs out; saving and reloading mid-journey and mid-deployment; drafting a deployed builder and confirming the deployment ends without moving anyone; confirming a builder whose construction work type is switched off is never sent; confirming a frame still owing material is not treated as finishing work; and confirming the Operations pane lists a deployment distinctly from a carry trip.
