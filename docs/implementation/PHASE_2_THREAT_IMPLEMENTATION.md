# First-site route and encounter implementation

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Feature IDs:** RR-SPACE, RR-THREAT, RR-EVD, RR-EXP, RR-UI, RR-STYLE. **Input:** [threat sheets](../THREAT_DESIGN_SHEETS.md), [first-slice inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [procedural contract](../PROCEDURAL_SPACE_CONTRACT.md), Core row 4 and the [local source review](PHASE_2_INVESTIGATION_THREAT_REVIEW.md). These are original Rimrooms mechanics and artwork. No direct film/series creature, scene, dialogue or asset is included.

## Owned files and save state

[FirstSliceSiteComponent](../../src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs) owns site observations, individual previous-room records, encounter counters, current crew references and a deep-held recovery container for interrupted route-equipment deployment. [FirstSlicePursuer](../../src/RimroomsAsyncIndustries/Threats/FirstSlicePursuer.cs) owns the bounded approach/contact rules. [Thing_QuietPursuer](../../src/RimroomsAsyncIndustries/Threats/Thing_QuietPursuer.cs) is a Core `IAttackTarget` using native damage and targeting. [CompRouteAid](historical-content/0.10.7-dev/src/RimroomsAsyncIndustries/Investigation/CompRouteAid.cs) saves coordinate, recorded room, number and mismatch on each deployed physical tag/beacon. All are local to the branch/map.

An opening ID means the saved expedition, including its paid recovery windows. Resuming that expedition does not reset an encounter. A genuinely new expedition resets the bounded encounter while room survey records, recovered evidence and deployed route aids remain saved.

## Player route

1. Carry a field recorder, six tags, return beacon and evidence case through dispatch. Shared kit checks use actual inventories; replacement equipment is made through ordinary smithy/machining bills.
2. Explore the six required room families. Crew presence plus an inventoried recorder records survey observations. Operations shows missing required survey/mismatch and optional entity observations.
3. Deploy a numbered tag at a validated junction through a native walking/waiting job. Enter Borrowed Corridor. The event moves that same deployed tag to the next room, preserving its old room label and number. A visible overlay and written activity entry expose the mismatch. An unmarked route gives a written placement hint instead of inventing a tag.
4. A beacon at the validated junction and the original numbered tag provide the low-risk comparison. Continuing past the warning without that countermeasure may loop mobile crew to separate, already revealed, standable cells in the validated room. It cannot move the return anchor or injure a pawn. The saved 125-tick cost is applied once by the gate controller's operation receipt.
5. The Quiet Pursuer appears two graph rooms away where a real route through open doors exists. A still-unopened approach delays the attempt until exploration creates a valid route. Native spawn success is verified before a sighting is recorded. It advances at bounded intervals while crew remain nearby, can react to loud attacks, and never enters the threshold room. A deliberately closed door breaks reachable contact and pursuit. A firearm hit repels it through the existing room graph or makes it withdraw.
6. Contact has a written, saved warning bound to the particular target. At most one strike is attempted per expedition. The tutorial strike uses 2 blunt damage to a healthy pawn's sufficiently healthy arm; an unsuitable target makes it withdraw. Native medical treatment owns any injury. This bounded manifestation cannot be captured or sold.

## Failure and recovery

Deployment takes one existing inventory unit, never grants a replacement. Invalid/occupied cells and rejected jobs refuse. A failed spawn returns the unit to inventory where possible; otherwise the site saves the unit in its recovery holder and exposes an explicit field recovery action. Picking up a deployed aid clears deployment metadata; moving it as part of the corridor event preserves metadata.

Save fields retain individual crew route history, warning ticks/target, number counter, pursuer room/advance count, whether a strike was attempted, and whether the distortion cost still awaits acknowledgement. Encounter completion leaves the coordinate/evidence observations intact. A missing recording does not regenerate when the gate is reopened.

The branch evidence service records structured room surveys, displaced-tag room/number, an original recorder-gap observation and a live entity sighting only while the actual route recording and a crew-carried field recorder are on that site. It captures the witness and recorder carrier separately. Analysis freezes the available observations; the Investigation UI reads the frozen report, including explicit missing-detail labels for old records. The authored recorder gap is an original story observation, not a claim that the computer recorded or lost audio.

## Source review corrections and remaining acceptance

The source review led to corrections for closed-door contact, warning reuse on another pawn, crew-order-dependent distortion triggering, destructive item-cell placement, ignored ordered-job refusal and analyzed evidence being relabeled missing. Placement now also excludes occupied item cells; looping crew require enough separate unoccupied landing cells.

Compilation/source inspection do not prove pathing, targeting, injury bounds under optional mods, save/load, sprite readability or warning timing. Those require owner-launched acceptance with exact build/profile evidence. The 84/42/125-tick threat timing is the accepted in-game-minute interpretation pending the owner's timing choice. Original sprites and provenance are linked from the [build record](PHASE_2_BUILD_RECORD.md).
