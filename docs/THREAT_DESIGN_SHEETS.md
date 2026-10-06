# Rimrooms - Async Industries: threat and distortion design sheets

**Gate traversal and pacing rule (owner, 2026-09-28):** inhabitants and monstrosities stay in the Backrooms. Nothing but this company's own pawns crosses a gate under its own will, and an open gate is never an objective, lure, spawn target, raid route or attack trigger. Everything else reaches the near side only because one of our pawns physically carried it through by ordinary work, including people and monstrosities that are genuinely downed, dead or imprisoned -- **with two owner-directed exceptions, both decided at the one chokepoint and nowhere else.** A hostile that followed a crew to the far doorway may come through it once, on an advanced machine, in the worst coordinates (2026-09-29). And **anything standing on your own map may walk out through an open gate** -- owner, 2026-10-06: *"not anyone in base, but anyone on your map.. a enemy can break in and cross the gate to get valuables and members"*, then *"hold up now friendlys can too"*. Neither is a lure: the gate is never a destination for anybody who is not ours, and both cross because they were already at a threshold that happened to be open. Pressure escalates gradually from saved causes, bounded per opening and per coordinate, with quiet stretches as required content. Gate, machine door and portal are one thing in the owner's vocabulary; every start can eventually run several gates. See [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side).

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** version 0.2, and **it is no longer only a pre-code contract.** The two first-slice entries below are original game design, not confirmed Backrooms canon or tested behaviour. **Eleven broad families are now implemented**, and their sheets — in [the broad families](#the-broad-families) — were written **after** the content, describing what the shipped defs and code actually do. Five families remain specified and unbuilt, and they say so in those words.

**The original rule still binds the unbuilt five:** a family needs its completed sheet before its defs or quests are implemented. What changed is that eleven of them earned their sheets late rather than early, which is worth recording as a departure rather than presenting as the plan.

**Feature route:** [RR-THREAT](FEATURE_TRACEABILITY.md), [RR-SPACE](FEATURE_TRACEABILITY.md), [RR-EXP](FEATURE_TRACEABILITY.md), [RR-EVD](FEATURE_TRACEABILITY.md), and [RR-MSN](FEATURE_TRACEABILITY.md). The initial encounter is specified in the [first playable contract](FIRST_PLAYABLE_CONTRACT.md) and [content inventory](FIRST_SLICE_CONTENT_INVENTORY.md).

## Shared design rules

- Every encounter has a visible or otherwise accessible warning, a learnable rule, at least one countermeasure, and a recorded outcome.
- Do not use color or sound as the only way to notice a tell. Pair visual changes with a label, map marker, text alert, or other clear cue.
- A threat may surprise the player, but first contact must not kill a healthy pawn instantly or erase the return route without warning.
- The player can learn, avoid, repel, contain, study, trade, sell, or abandon a threat only where that behavior is explicitly specified. Do not grant a hidden capture, sale, or research result.
- Threat effects are bounded, seed-stable, logged against a coordinate, and recoverable after saving and reloading.
- Source story notes can suggest a mood or question. Use original names, shapes, text, rooms, and event sequences; do not treat fan summaries as rules from the series.

## RR-D-001 — The Borrowed Corridor

**Type:** environmental route distortion. **First-slice status:** required once on AI-01. **Lore label:** original design inspired by uncertain routes and marked paths described in the series fan notes for [Found Footage](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-01), [Missing Persons](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-05), and [Informational Video](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-07). The exact loop rule below is invented for Rimrooms.

| Rule | First-slice behavior |
| --- | --- |
| Tell | The room/map label repeats after the crew passes a tagged junction. A numbered survey tag appears on the wrong side of the familiar doorway. A text alert says the route and physical landmark disagree. |
| Trigger | The event can activate once when the crew crosses the seeded Borrowed Corridor connection. It cannot activate again during the same opening. |
| Effect | The familiar-looking doorway returns the crew to the last validated junction and consumes 3 reported in-game minutes. It does not create an unbounded graph loop or silently move the gate exit. |
| Counterplay | Stop at the mismatch, compare the numbered tags, place the short return beacon at the known junction, and follow the last validated route. The player may recall immediately instead of investigating. |
| Risk | Ignoring the mismatch costs time and can leave optional salvage behind. The event alone causes no injury and cannot kill a pawn. The creature encounter below supplies the first combat decision. |
| Evidence | The route recording stores the duplicated room label and mismatched tag position. A researcher can use it for Gate Telemetry. |
| Recovery | Recall uses the saved validated path. If path recovery fails, dispatch is refused or the expedition returns to the last valid point with a case note; it never rerolls AI-01. |
| Accessibility | Use a map-label change, numbered tag, and written alert. Sound can add atmosphere but never carries the only warning. |

## RR-ENT-001 — The Quiet Pursuer

**Type:** original hostile entity. **First-slice status:** one bounded sighting on AI-01; it may injure a pawn, but capture is deferred. Its working name and appearance are not taken from a Kane Pixels or A24 character.

| Rule | First-slice behavior |
| --- | --- |
| Appearance | A distant upright figure holds still beyond the crew's light or view. Use an original silhouette and readable posture; avoid a direct recreation of a video or film shot. |
| Tell | The figure appears two rooms away. It is visibly nearer after two in-game minutes without the crew changing rooms or immediately after a loud action. The route recorder also records a missing interval. The UI logs its last seen room and distance. |
| Trigger | It appears once after the crew reaches the Borrowed Corridor. It advances one room every two in-game minutes while the crew remains in its connected area. A loud action advances it immediately instead of waiting. |
| Limit | It advances at most three rooms, never travels through the Threshold Room or validated gate exit, and does not spawn a second copy during the same opening. Its current state is saved on the site. |
| Counterplay | The crew can withdraw behind a closed door, keep moving along numbered markers, or use the guard's firearm to force it back one room. The crew gets a clear warning before it advances again. |
| Contact | If it reaches the crew and they remain in the same room through one further one-minute warning, it can strike one pawn once, causing a recoverable injury, then withdraw. It cannot one-hit kill a healthy pawn in this tutorial encounter. |
| Evidence | A clear observation, recorder gap, and a recovered trace are separate facts. A single sighting does not identify what the entity is or unlock capture. |
| Outcome | Retreating completes the onboarding survey if its required route record is returned. A fight is optional and cannot be the only way to finish the contract. Injuries follow ordinary medical care and are written to the expedition/case record. |
| Containment/sale | Not available in the first slice. Later capture, study, sale, detention, or disposal requires a separate containment, custody, and value contract. |
| Accessibility | Pair distance and warning text with the visible figure/map marker. Do not rely on footsteps, static, darkness, red overlays, or color alone. |

## Authoring sheet for every later threat

Complete this record before implementation and link it from [FEATURE_TRACEABILITY.md](FEATURE_TRACEABILITY.md):

| Field | Required answer |
| --- | --- |
| Stable ID and name | Unique internal ID plus player-facing name; note whether the name is provisional. |
| Type and intended use | Entity, environmental distortion, incident, equipment failure, or human decision; identify the scenario, quest, or coordinate that can use it. |
| Lore route | Cite the relevant series or separate film note. Label the source fact, fan interpretation, or original design; identify all invented behavior. |
| Appearance and tells | What players can see, hear, read, or measure before the effect occurs; provide redundant cues and accessibility alternatives. |
| Trigger and behavior | Exact trigger, selection conditions, action loop, range, duration, target, and what ends or interrupts it. |
| Limits and fairness | Maximum active count, escalation bound, warning interval, protected start/return areas, and conditions that prevent unavoidable instant failure. |
| Counterplay | At least one accessible player response, required gear/staff, time/cost/risk, and the result of each response. |
| Evidence and study | Physical/logged evidence, custody rules, confidence, analysis, unlock, and what remains unknown. |
| Capture and disposition | Whether capture exists; required room, staff, equipment, containment capacity, transfer rules, sale/study/release outcomes, and failure recovery. If not implemented, say so. |
| Save and generation | Stable coordinate/seed inputs, saved event state, duplicate prevention, revisit behavior, and migration behavior. |
| Dependencies and acceptance | Core path, optional DLC/mod handling, exact UI/job route, test profile, success cases, failure cases, save/reload evidence, and logs needed before claiming support. |

---

# The broad families

**Owner direction, 2026-10-06, at the fork:** author the broad family sheets. **Nothing in this half of the document is built by it** — these are specifications. Where a family is implemented, the sheet describes what the shipped defs and code actually do, measured rather than remembered. Where a family is not implemented, the sheet says so in those words.

**Broad families only, per the owner's earlier S1/B answer.** A family is a contract for a *kind* of thing, not a creature. That is deliberate and it is the only honest grain available: one sheet per monster would be a bestiary nobody asked for, and the two worked entries above are **instances** of families rather than families themselves.

## The family contract

**Every family inherits all of this. No sheet below restates it**, because a rule written twice is a rule that disagrees with itself the first time one copy is edited — the defect this project keeps meeting.

### Placement and pacing

| Rule | Where it lives |
|---|---|
| A body is placed when the space is **generated**; everything that acts is placed **on arrival**, against the coordinate's band at that moment | `InhabitantService` |
| **A first visit is always `Quiet`**, whatever the colony is worth and however deep the space | `CoordinatePressureLadder` |
| **Half of a coordinate's rooms present nothing at all, by count and not by chance** | `QuietRoomFraction`, and no research may move it |
| **At most three things act at once**, whatever any def's `count` says | `MaxSimultaneousEncounters`, an absolute |
| At most **two events** fire per opening — one for a branch holding Quiet Protocol | `AnomalyEventService` |
| A one-shot event is **written to the coordinate**, so a revisit does not replay it | `coordinate.NoteEventFired` |
| Every family declares a `minDepth` **and** a `minBand`, and the reach of a level counts, not its doorstep | `InhabitantService.ReachOf` |

### Fairness, and what nothing may do

- **The threshold room is excluded from every event effect, always.** Whatever happens, walking back out is possible.
- **No event damages a pawn, destroys a thing, or blocks a route.** Every effect has an answer the player can perform, and the answer is usually a vanilla one — a colonist walks over and switches the lights back on.
- **Only the unstable family is hostile, and that is enforced in code** rather than trusted to a def. A hostile family that did not read as hostile would break the warning-first rule.
- **Nothing is ever lured to a gate.** `MayApproachThresholdForTraversal` is false for everything. Two owner-directed crossings exist and both are decided at the one chokepoint; **anybody in this colony's custody never crosses on their own legs**.

### Content, cues and evidence

- **Every family generates from a `PawnKindDef` the loaded game already ships**, with fallback lists, so a Core-only install and a 294-mod profile both work. No new pawn kind, no new texture.
- **Every family carries a keyed letter and a keyed tell.** Colour and sound never carry a warning alone.
- **Everything is derived from the coordinate's own seed, never `Rand`.** Two players on one seed meet the same space, and a reload cannot reroll what is in it.
- **Evidence is the record book and the archive**, with the custody rules the company already uses. A sighting is not an identification.

## Implemented families

### RR-FAM-001 — Somebody who is simply here

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_Wanderer`, kind `Wanderer` |
| Type and use | Neutral person, found standing in a room. Any coordinate from depth 2, band `Unsettled`, one at a time |
| Lore route | Original design. The owner's *"findeding dead ones pasycholitc ones lost pawns all kinds of crazy variations as per the lore"* |
| Tells | A letter on arrival and a keyed tell on the pawn. They do not explain themselves |
| Behaviour | Ordinary neutral-faction behaviour. They were not brought in and they are not yours |
| Counterplay | Talk, ignore, or leave. Nothing is required of the player |
| Evidence | An entity observation, if somebody records one |
| Capture | **Not a capture subject.** They are a person, and recruiting is RimWorld's own business |
| Open question | Whether a wanderer should ever ask to be taken home. Today they never do, and `Survivor` is the family that does |

### RR-FAM-002 — Somebody who went missing

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_Missing`, kind `Missing` |
| Type and use | Neutral person. Depth 2, band `Unsettled` |
| **What makes it its own family** | **Where the branch has lost people, it is one of them.** The company keeps a lost-pawn register, and this family reads it |
| Tells | The letter names them. That is the whole of the effect and it is enough |
| Counterplay | Bring them home, or do not |
| Evidence | The register already holds the loss; recovering the person closes it |
| Capture | Not applicable |
| Open question | What a branch owes somebody it lost and then found. Nothing in the economy answers that yet |

### RR-FAM-003 — Somebody who can come home

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_Survivor`, kind `Survivor` |
| Type and use | Neutral person, one or two. Depth 2, band `Unsettled` |
| **Why it exists** | **The reason to enter a coordinate, not only to endure one.** A branch that only ever meets threats has no reason to go in twice |
| Counterplay | Rescue is ordinary RimWorld rescue and ordinary medicine |
| Capture | Not applicable. A survivor is not contained |
| Open question | Whether a survivor should carry something only they know. Today they carry only themselves |

### RR-FAM-004 — Somebody who has stopped being somebody

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_Psychotic` (depth 3, band `Active`, one or two) and `RR_Inhabitant_PsychoticPack` (depth 5, band `Hostile`, two or three) |
| Type and use | **The only hostile human family, and the reason the encounter cap exists** |
| Tells | A letter, a keyed tell, and the band itself: `Active` means *something acts, singly, with a warning first* |
| Behaviour | Below `Hostile` they hold an area. At `Hostile` they hunt — the band's own definition is *"more than one thing acts, and the space stops being forgiving"* |
| Limits | The absolute three-at-once ceiling clamps every count here, whatever the defs say |
| Counterplay | Ordinary combat, ordinary retreat, ordinary doors. A crew may always withdraw through the threshold room |
| Capture | **Downed, they are carried home like anything else.** The crossing policy requires a carrier; nothing walks through in custody |
| Open question | Whether this family should ever be talked down. There is no social route today |

### RR-FAM-005 — What is left

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_DeadRecent` (depth 2), `RR_Inhabitant_DeadStripped` (depth 3), `RR_Inhabitant_DeadCrew` (depth 4, two to four) |
| Type and use | **Content, not a threat.** Placed at generation, at band `Quiet`, because finding a body should not wait on a danger band and a corpse does not act |
| Tells | What they are carrying, and what has already been taken off them |
| Counterplay | None needed. Haul, bury, or leave |
| Evidence | A body is a fact about the place. `DeadCrew` is a fact about somebody else's expedition |
| Open question | Whether a dead crew should ever be **this** branch's own, recorded from the lost register the way `Missing` is. It is the sharpest unbuilt idea in this document |

### RR-FAM-006 — Somebody who helps, and should not be able to

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_Helper`, kind `Helper`. Depth 3, band `Unsettled`, one, and the rarest family at `0.2` |
| **Why an ally is the unnerving one** | Owner: *"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"*, under *"remember lsd unnerving feeling with all things"*. **A thing that attacks you is explicable.** Somebody who has been down here long enough to be part of it, who takes your side, and who **will not leave with you**, is not |
| Behaviour | Generated into an existing non-hostile faction and given Core's own defend-the-area lord, so the help is **real**: they fight the unstable families for you with ordinary AI |
| Counterplay | None is needed and none is offered. Accepting help is the player's choice |
| Open question | What happens if a branch tries hard to take one home. Nothing special happens today, and something probably should |

### RR-FAM-007 — Somebody who is in your base right now

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_Echo`, kind `Echo`. Depth 3, band `Unsettled`, one |
| Type and use | **Somebody wearing the name and clothes of a colonist who is alive at that moment** |
| **Why it is not the Missing family** | Deliberately not a copy of somebody you lost — that is sadder and simpler. An echo is uncanny *because the real one is standing in your base*. The owner's *"echos of thier inhabitance in weird ways"* |
| Tells | The name. A player reads it and looks at their own colonist list |
| Counterplay | Nothing is demanded. It does not attack |
| Open question | Whether an echo should ever be met twice, and whether the second time should differ. It is one sighting today |

### RR-FAM-008 — An animal that is in here

| Field | Answer |
|---|---|
| Implemented as | `RR_Inhabitant_FaunaDomestic` (depth 2) and `RR_Inhabitant_FaunaWild` (depth 4, one or two) |
| Type and use | Unfactioned animals, exactly as anywhere else in the game. Owner: *"things that chase you are just npc pawns and wild animals and shit of the gasme"* |
| **The point of it** | **The unnerving part is not that it is dangerous. It is that it is in here, and something had to bring it.** A stray dog four levels down is a worse feeling than a predator |
| Counterplay | Ordinary animal handling, ordinary hunting, ordinary avoidance |
| Capture | Ordinary taming. Nothing bespoke, and a tamed animal crosses home in the ordinary way |

### RR-FAM-009 — The building acting

| Field | Answer |
|---|---|
| Implemented as | `RR_Anomaly_LightsFail` and `RR_Anomaly_Blackout` (lights), `RR_Anomaly_ColdSnap` and `RR_Anomaly_DeepCold` (cold), `RR_Anomaly_Seepage` (filth), `RR_Anomaly_Rearrangement` (loose items move) |
| Type and use | Environmental events, fired on arrival. Depth 2 upward; the severe pair need depth 5 and bands `Active` and `Hostile` |
| Tells | A letter, and a readable trace left in the room afterwards so a later crew finds the sign of it |
| **Limits that are the design** | The threshold is excluded. **Lights use vanilla's own flick switch, so the countermeasure is vanilla too.** Rearrangement moves **loose items only** and never a landmark the clue system recorded, and it puts anything back that fails to place. Money is never moved |
| Counterplay | Turn them back on, bring a heater, clean it, go and find the thing. All ordinary work |
| Evidence | The trace is recorded against the room, so the event outlives its own letter |
| Open question | Whether the building should ever act **while** a crew is in a room rather than on arrival. Today every event fires once, on entry |

### RR-FAM-010 — A transmission, and whose voice it is

| Field | Answer |
|---|---|
| Implemented as | `RR_Anomaly_Presence` (depth 2) and `RR_Anomaly_RadioFragment` (depth 3) |
| Type and use | A transmission rather than a change to the space. It needs nothing to act on and can never fail to find something |
| **Whose voice** | **Somebody this branch knows.** A living employed colonist by preference; failing that, a name from the lost register. **With neither — nobody home and nobody lost — there is no fragment at all**, because a transmission from a name nobody knows is the thing this is not |
| Derivation | From the coordinate's seed and its opening count, so the same opening always carries the same voice and a reload cannot reroll who is on the radio |
| Counterplay | None. It is atmosphere with a name in it |
| Open question | Whether a fragment should ever say something a player can act on. It never has, and that restraint is probably right |

### RR-FAM-011 — The objects' own testimony

| Field | Answer |
|---|---|
| Implemented as | Twenty `RimroomsFixtureTellDef`s across benches, seats, tables, beds, storage, lights, items and equipment |
| Type and use | **One exact wrong fact about an ordinary object.** Roughly one placed object in eight carries one; one in six for a branch holding The Trained Eye |
| **The restraint that is the design** | *"The first one a player finds should be the only one in the room."* A coordinate where every stool has a sentence on it is a museum with too many placards, and it buries the sharper beats |
| Derivation | A stable hash of the coordinate, the room, the variant and the definition. **Raising the share can only ever add a tell, never move one**, so a space re-read after research keeps everything a crew already wrote down |
| Counterplay | Reading is the whole interaction. Nothing is demanded |
| Accessibility | Each tell is a keyed sentence on the object's own inspect card. Nothing depends on noticing a texture |
| Open question | Whether a tell should ever be **wrong on purpose** — a space lying about itself rather than being odd. Nothing does that today |

## Families specified and NOT built

**Nothing below is implemented. No def, no code, no keyed string.** Each sheet is the contract a build would have to satisfy, and each names the question the owner would have to answer first. They are written here so that the next person to build one inherits the rules rather than inventing them, which is what the authoring sheet above has always asked for.

### RR-FAM-012 — Something that follows

- **Status: one worked instance, no family.** `RR-ENT-001 The Quiet Pursuer` above is a complete sheet for *one* entity in the vertical slice. **There is no pursuit system**, no def family, and no generator.
- **What a build must answer:** how many may ever follow at once (the three-at-once ceiling applies); whether pursuit survives a closed gate (it must not, under the one-chokepoint rule); and what a pursuer does when the crew leaves — today's answer for the slice is that it withdraws.
- **The owner's question first:** whether pursuit is a *family* at all, or whether the Quiet Pursuer should stay the only one of its kind.

### RR-FAM-013 — Altered arrivals

- **Status: nothing is built.** Named in the earlier backlog as *"infected or altered arrivals"*.
- **What a build must answer:** what *altered* means mechanically when the mod may not author a new pawn kind, a hediff or a texture; whether the alteration is visible before the crossing; and what happens to the branch's own colonist who comes back changed.
- **The hard constraint:** the content policy. An altered arrival that needs a new hediff is a new def, and the only approved exceptions are the menu art and the records desk.

### RR-FAM-014 — Containment escape

- **Status: nothing is built, and a prerequisite is missing.** Containment exists as a *facility* concern, and `RR-ENT-001` states plainly that capture is deferred: *"Later capture, study, sale, detention, or disposal requires a separate containment, custody, and value contract."*
- **What a build must answer:** that contract, first. Then what escapes, into what, and whether an escape may ever reach a gate — which the chokepoint rule already answers with no.
- **Why it is not simply a raid:** the thing escaping is already inside, and the warning-first rule has to hold for a threat that starts in the middle of the base.

### RR-FAM-015 — Hostile sites on the world side

- **Status: nothing is built.** Remote sites exist and are billed and staffed; **a hostile one does not.**
- **What a build must answer:** whether a hostile site is ours to lose or somebody else's to raid; how it interacts with the five-map budget; and whether losing one costs the branch anything beyond the site.
- **Open to the owner:** whether this belongs to the threat system at all, or to the sites and commerce line.

### RR-FAM-016 — Late-game space threats

- **Status: nothing is built, and the branch above it is deliberately empty.** Transport and orbital support has **no tier 0 by design**, and the gravship question is deferred to the expansion milestone by owner direction.
- **What a build must answer:** nothing yet. A threat family above an empty branch would be content with no route to it, which is the shape four deleted research projects had.

## What remains open

**The two worked entries are instances, and eleven families are specified from shipped content.** What is still genuinely open is the five unbuilt families above, and inside the built ones, the open question each sheet names.

**Do not reuse any behaviour here as a generic random-threat generator, and do not mark the threat backlog complete.** The generator the mod has is the band ladder plus the family weights, and it is bounded on purpose: three things at once, half the rooms empty, a quiet first visit, and a threshold nothing touches.

