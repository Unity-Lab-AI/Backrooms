# Deferment audit and closures — nine rows closed, natural gates reachable (0.5.1-dev)

**Owner direction, 2026-09-28, verbatim:**

> lets get to work.. and try not to deffer anything you may need to properly bbuild other coded systems so that you can do the deffered items(I DONT WANT YOU JUST DEFFERING SHIT THAT WE NEED WORKING !!! WE CANT NOT BUILD SHIT THAT THE MOD DEPENDS ON AND JUST MARK IT DEFFERED BECAUSE SOMETHING WELSE NEEDS DONE FIRST!!! DO THE FIRST THING TO UNDEFER SHIT! I DONT WANT TO GET COMPLETED WITH THIS MOD AND HAVE 1000s of defferments, we need to critical solve these issues wirthin the confines of the mods and the game

**Baseline:** `d85817d` (0.5.0-dev, 87 C# files, 76 package files).

**This checkpoint — 0.5.1-dev:** **88 C# source files**, **76 approved package files**, zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `E9A6363913C647D1091EA5ED25B2AD1473D5CDCE6F88E3DA8683473FCA6DFA5E`. Evidence: [`evidence/deferment-closures-2026-09-28/`](evidence/deferment-closures-2026-09-28/), with recomputed reference manifests showing no drift.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The audit, which is the reusable part

Three questions were asked of every open row in [`../DEFERRED.md`](../DEFERRED.md). They are worth re-asking every time the register is touched, because two of them caught real rot immediately.

1. **Is this row actually still open?** A row describing work that already shipped is worse than a deferment: it makes the register lie, and a future session reads it and either rebuilds the thing or plans around a limit that does not exist.
2. **Is this row blocked on anything?** "Owned by a later step" is only legitimate when the later step supplies something this row genuinely needs. If nothing is missing, the row is not a deferment, it is unstarted work.
3. **Does anything else depend on this row?** A dependency parked behind a convenience is the failure the owner is describing; it compounds, because each thing built on top of the gap inherits it.

A fourth check runs against the source rather than the register: **which public APIs have no callers?** That is how a layer ends up compiling perfectly and doing nothing, which is exactly what the portal layer did at 0.4.1-dev. `CreateDiscoveredCoordinate` was in that state — built in 0.4.2-dev, never called by anything — and its deferment row was the one saying natural gates could not be discovered yet.

### What question 1 found: three rows that had already shipped

All three were verified against source before closing, not assumed:

| Row | Reality |
|---|---|
| "Player-facing text for the 32 crossing failure keys" | All 32 `RR_PortalCrossing_*` keys are in `RR_Portals.xml`, and `JobDriver_CrossPortal.Report` surfaces them through `Messages.Message` at the moment a crossing is attempted. Shipped 0.4.2-dev. |
| "Emergency-return route for a laboratory session that closes while workers are across" | `PortalTravelService.OrderEmergencyReturn` exists, debits once per operation id, teleports nobody, and is wired to a button in the Operations portal pane. Shipped 0.4.2-dev. |
| "Surface unresolved crossing receipts in the Operations network view" | `DrawUnresolvedCrossings` lists every unresolved receipt with a reconcile action each. Shipped 0.4.2-dev. |

One row in that group was **re-owned rather than closed**, honestly: "the deliberate-cross gizmo must name the refusal reason". The *capability* is done — every refusal is a keyed reason surfaced to the player — but it is surfaced in the Operations pane rather than on a door gizmo. That is a presentation improvement and now sits under M5 where presentation lives, instead of masquerading as a blocking gap in the portal layer.

### What questions 2 and 3 found: six rows blocked on nothing

---

## Closure 1 — the receipt archive was a live bug, not a future cost

The row read "only becomes a real cost once receipts are reachable in play." Shipping automatic connected hauling in 0.5.0-dev *made* them reachable in play: a colonist hauling across a gate all day generates a crossing receipt per trip, and only *unresolved* receipts were bounded. Terminal receipts grew without limit, in the save, forever. My own previous wave turned a deferred hypothetical into a defect.

`RimroomsPortalCrossingService` now bounds the finished-receipt history to `MaximumArchivedCrossings = 512`, oldest first by the monotonic sequence receipts already carry, trimmed before a new receipt is added and again on load so an older save is brought inside the bound.

Unresolved receipts are never touched: they own a deep-held pawn or cargo, and losing one would lose that custody. Replay protection is unaffected, and this was reasoned rather than hoped — every operation id derives from an identity that cannot recur (a job load id, or a gate opening id), and a receipt can only be *finished* once the crossing it describes has already completed or rolled back, so no in-flight job can be holding a compacted id.

## Closure 2 — one `OwnsMap`, not three

The canonical accessor already existed on `RimroomsCampaignComponent`. The two private copies in `RimroomsPortalNetwork` and `RimroomsPortalCrossingService` now delegate to it. The campaign version is the strictest of the three — it also rejects a map that is no longer loaded — so this is safe or safer at every call site, and the network's copy in particular was the loose one.

## Closure 3 — container storage destinations

Deferred as "needs an adapter per provider." It does not. `IHaulDestination` exposes `Position`, `Map`, `HaulDestinationEnabled` and `Accepts(Thing)`, and `Toils_Haul` already has `CarryHauledThingToContainer` and `DepositHauledThingInContainer`. Core's own `HaulAIUtility.HaulToStorageJob` branches on exactly two cases, and that branch is now mirrored:

- destination is an `ISlotGroupParent` → deliver to a **cell** (this is the path a shelf takes, which is why shelves already worked);
- destination is a `Thing` exposing an inner `ThingOwner` → deliver **into** it.

`JobDriver_ConnectedDepositInContainer` uses Core's container toils, and mirrors Core's reservation rule of not exclusively reserving a destination that tracks enroute deliveries. The container reference is recorded in the intent's `finalTarget` field, which is precisely what that field was reserved for. If the best destination turns out to be unusable on arrival, the adapter falls back to the best plain cell before giving up rather than setting the object down.

This closes the row **and** most of the generic storage half of the optional-provider row: Adaptive Storage, LWM Deep Storage, Warehouse and RimFridge reach cross-gate hauling through `IHaulDestination` without a bespoke adapter each. What remains genuinely per-provider is behaviour those mods add beyond the interface, which is a smaller and honest claim than before.

## Closure 4 — remote allowed areas, solved by observing instead of guessing

The row was correct that Core exposes no public accessor for a pawn's allowed area on a map it is not standing on: `Pawn_PlayerSettings` keeps a `private Dictionary<Map, Area> allowedAreas` and offers only "in the pawn's current map" properties. Reflection or spoofing `pawn.Map` to read it are both out of the question.

The resolution is neither of those, and it is not a deferment either: **write down what we saw while we were legitimately able to see it.** `ObserveAreaHere` records a worker's effective area for the map it is standing on, every planning pass, into a saved bounded list of `ConnectedAreaObservation`. `ObservedAreaAllows` then answers about another map from that record.

An unobserved map answers *unrestricted* — which is not a guess, it is Core's own answer, because `EffectiveAreaRestrictionInPawnCurrentMap` returns null for any map no area was set on, and the player can only set one while the pawn is there. A removed area resolves to null on load and correctly reads as unrestricted rather than as a wall.

The candidate pass now checks the object's cell, the destination cell and the arrival threshold against those observations. This is deliberately an observation and not a guarantee: the definitive per-pawn check still runs on arrival. What changed is that the planner no longer commits a worker to a walk it already has evidence ends in a refusal. A paired transient refusal memory (`NoteDestinationRefused`, 15,000 ticks) stops a destination that turned a worker away from becoming a daily round trip to nowhere.

The row is closed as solved, not as accepted-with-a-limit.

## Closure 5 — natural gates are now findable in play

This is the row that most deserved the owner's complaint. It read "the trigger belongs with procedural frontiers", but it needed nothing from procedural frontiers. The deterministic coordinate API existed with **zero callers**, natural-edge registration existed and already ensured the far site itself, and the permanently-open natural half of the whole design was therefore unreachable except by a player hand-wiring an address in the Operations pane.

`Portals/NaturalFrontierService.cs` supplies the missing trigger as ordinary work. A colonist deeper in walks to a doorway, studies it for 600 ticks, and records that it leads somewhere new: `CreateDiscoveredCoordinate` derives the new coordinate's id and seed, and `RegisterNaturalAddress` binds the permanently open edge.

Bounded, and deterministic without randomness:

- A doorway's frontier status is drawn from **its own position under that coordinate's own saved seed**, so the same doorway is always the same answer. Reopening a known space never rerolls what it leads to, which is the contract's explicit requirement.
- At most `MaximumFrontiersPerCoordinate = 2` gates are ever found on one coordinate; roughly one doorway in `FrontierRarity = 12` qualifies. The campaign's existing 512-coordinate cap bounds the graph. This propagates further spaces without preallocating infinity.
- The site's own return anchor is never a frontier — the way home does not lead onward.
- A doorway already serving as any endpoint is refused, and one evaluation (`Evaluate`) backs both the work-scanning predicate and the recording action, so the doorway a worker was sent to survey cannot differ from the one that gets recorded.
- `ShouldSkip` makes the giver free on headquarters and on any space that has already given up all its ways onward, which is the overwhelmingly common case.

This finds a *way through*. It generates no inhabitants, encounters or pressure; what waits on the other side remains the escalation ladder's business, which is a genuine dependency and stays with step 5.

The survey work giver sits at `priorityInType` 115, just above bench research, justified by being a discrete short task capped at two per space. Like the hauling priorities, that exact number is a balance decision recorded as such.

## Closure 6 — one approach-cell implementation

Adding the frontier survey would have created a third hand-written copy of "find the standable cell cardinally adjacent to this door". Instead `PortalAddressService.ApproachCellFor` is now the single implementation, and the Operations pane's private copy was replaced with a call to it. Avoiding the duplicate was cheaper than the deferment row that tracking it would have required.

---

## Found while auditing: four missing player-facing strings

A sweep of every `RR_` identifier referenced in source against the keyed and def files turned up four that were translated at display time but had no text. All four are pre-existing, from earlier phases, and would have rendered as raw keys to the player:

| Key | Where it shows |
|---|---|
| `RR_UI_Procurement` | the Procurement tab label in the Operations window |
| `RR_Proc_NoOpenQuotes` | the empty-state line in the procurement pane |
| `RR_Proc_UnassignedCargo` | a procurement save-integrity message |
| `RR_Generation_Failed` | the default site-generation failure message |

All four now have text. The remaining unresolved identifiers in that sweep are concatenation prefixes (`"RR_Role_" + role` and similar); every one of those families was spot-checked and has its concrete keys defined.

---

## Saved state added

| Owner | Key | Rule |
|---|---|---|
| `RimroomsConnectedWorkComponent` | `rr_connectedWorkAreaObservations` | Additive; absent from a 0.5.0-dev save, which loads as "nothing observed" and therefore unrestricted everywhere, matching Core's own default. **No schema bump**, so a 0.5.0-dev save is not rejected. Bounded at 256, least-recently-confirmed row evicted. A row whose area or map no longer resolves is dropped on load. |

No existing key changed meaning. `RimroomsPortalCrossingService` gained no new key: the receipt bound operates on the existing `rr_portalCrossingReceipts` list.

## Deliberate limits that remain, with real dependencies

These stay deferred because something is genuinely missing, and the record now says what:

- **The remaining adapter families** (construction supply/finish, bills, research, tend/rescue, food, rest, the rest). Each needs its own source review and its own definitive native validation; the framework is ready and they are additive against it.
- **People and corpses as connected work.** Needs a bed, custody and grave route, which is the tend/rescue and remains families. The traversal policy already permits the carry; what is missing is the work that would order it.
- **The saved bounded escalation ladder** and procedural inhabitants. The ladder must be authored before generation ships, and generation is what it paces — a real ordering, not a convenience.
- **Connected-site scheduling, streaming and measurement.** Measurement is owner-blocked behind a RimSort launch.
- **M2 content replacement, M3 breadth, M5 interface, M6 release**, and every runtime-acceptance row.

## Owner-launched acceptance, deferred

Surveying a doorway that qualifies and one that does not; the same doorway surveyed twice, confirming the second is refused as already recorded; the per-coordinate cap of two; a save and reload between surveys confirming the same doorway still gives the same answer; crossing a discovered natural gate in both directions and confirming no timer, operator or battery is consulted; hauling into a container destination and into a shelf, confirming the two take different routes; a worker restricted to a zone at headquarters being correctly kept from planning a trip whose arrival is outside its observed zone on the far side; and a save carrying more than 512 finished crossing receipts being brought inside the bound on load without losing an unresolved one.
