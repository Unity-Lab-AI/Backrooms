# TODO — Minor Task List (Active Tasks)

**Tier 2 of 4** — the MINOR task list. Holds active tasks (pending + in_progress) at the day-to-day work grain. Each minor task lives under a major milestone in `docs/ROADMAP.md` and decomposes further into entries in `docs/DECOMPOSED.md` when YOLO mode picks it up.

**It holds buildable work only.** Rows that cannot be closed without the game running live in [`TEST.md`](TEST.md) since 2026-10-06.

Completed tasks move to `docs/FINALIZED.md` per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`. Never delete a task description; only flip status (LAW: NEVER DELETE TODO INFO).

Status markers:
- `[ ]` pending
- `[~]` in_progress
- `[x]` complete (move to FINALIZED.md immediately, never leave here)
- ~~`[T]`~~ **moved out 2026-10-06. It must not reappear here** — see [`TEST.md`](TEST.md)

**There is no blocked-on-owner status, by owner direction 2026-09-28.** Nothing here waits on the owner. Runtime rows are `[T]` and live in [`TEST.md`](TEST.md), one named phase that begins only once the mod is complete.

LAW #0 reminder: every task description preserves the user's verbatim words.

**Four-tier cascade:** ROADMAP.md (major) → TODO.md (minor, this file) → DECOMPOSED.md (decomposed), with [`TEST.md`](TEST.md) alongside for everything that needs a launch. The first three are the build cascade and YOLO works them; the fourth is not buildable by anyone here — see `.claude/commands/yolo.md` and `.claude/WORKFLOW.md §YOLO MODE`.

> **Live project TODO for Rimrooms - Async Industries.** Seeded 2026-09-28 when the Claude Code workflow took over from the previous build agent (ChatGPT 6 Astra). This file carries **every open item** of the complete mod backlog, quoted verbatim from [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) (the "master TODO"), grouped under the majors in `ROADMAP.md` and in the master TODO's own order. The master TODO stays the authoritative gate/evidence record; when an item here closes, tick the identical bounded subitem there in the same change with its evidence link, per `REGRESSION_CONTAINMENT.md`. Items whose source already exists but whose runtime acceptance is open stay `[ ]` — the master TODO's rule: *"Unchecked tasks below retain their full stated implementation/acceptance scope; they do not mean all referenced source is absent."*
>
> Owner sequencing override (2026-09-28): implement remaining systems while game testing is deferred; gameplay-gate statements govern acceptance/promotion, not permission to write source. Only the owner launches RimWorld, through RimSort.

---
## Pending

### ⛔ CONFIRMED DEFECT — A CONSIGNMENT MISSION DISABLES THE WHOLE COMPANY IN ANY SAVE (2026-10-06) ⛔

**Found by playing, in the owner's own colony.** On load: `[Rimrooms][Save] Campaign integrity failed; company actions are disabled. Preserve the original save.` **The mod switches itself off**, and every company row in `TEST.md` is untestable in that save.

**The cause, pinned to one line.** `RimroomsCampaignComponent.ValidateRecordRelationships`:

> `valid &= contracts.All(c => (c.IsOddSupply ? string.IsNullOrEmpty(c.coordinateId) : coordinateIds.Contains(c.coordinateId)) && ...)`

- `IsOddSupply` is `!string.IsNullOrEmpty(requiredThingDefName) && requiredCount > 0` — **it has nothing to do with the template name.**
- `IsConsignmentMission` is `IsOddSupply && requiredSurveyedRooms > 0`, so **a consignment mission IS an odd-supply contract.**
- And a consignment mission **names one coordinate** by design — the 0.12.41-dev record says so in its own words: *"A mission names **one coordinate**, wants goods **that coordinate produced**"*.

So the moment one exists, `IsOddSupply` is true, `coordinateId` is not empty, `valid` goes false, and `stateFaultKey` is set. **Measured in the save rather than reasoned about:** `rr.mission.oddconsignment.v1`, coordinate set, `requiredThingDefName=XER_MediumTableM`, `requiredCount=8`, `requiredSurveyedRooms=2`. The two plain `rr.supply.odd.v1` contracts correctly carry no coordinate and pass.

**The validator's own comment is the record of how it went wrong:** *"An odd-supply contract is branch-wide rather than tied to one coordinate ... So it legitimately carries no coordinate id, and requiring one would fault a valid save."* **That was true before consignment missions existed and was never revisited when they landed.**

- [ ] **No instrument covers this and that is why it shipped.** Every checker reads source or defs; **none validates a saved campaign**, so a validator that rejects its own legal data is invisible until somebody loads a save. The diagnostic written to find it — re-running each condition against a save's XML — is the shape the missing instrument should take.

### ⛔ OWNER DIRECTION — I PLAY THE GAME NOW, AND THIS SUPERSEDES "ONLY THE OWNER LAUNCHES" (2026-10-06) ⛔

**Verbatim owner direction (2026-10-06):** *"okay u fucking play the game and restart the scenerios as needed to test whats needed"*

**THIS OVERRULES A STANDING CONSTRAINT THAT IS WRITTEN INTO FIVE PLACES, AND NONE OF THEM IS DELETED.** *"Only the owner launches RimWorld, through RimSort"* appears in `TODO.md`'s own header, in `TEST.md` twice, in `NOW.md`, and on the RimSort profile row. The 2026-09-28 sequencing override that created it is kept verbatim where it sits; **what changes is permission, from this message on**, and the old text stays because a direction the owner superseded is still the reason the old rows read as they do.

- [ ] **"restart the scenerios as needed"** — a row that needs a different opening gets one, rather than being left because the running save is the wrong start. **THE OWNER'S OWN SAVES ARE NOT MINE TO OVERWRITE.** There is a `Godsmultiplayer` save on this machine and a live `lone_survivor` session at tick 1346 with three colonists. **Every save I write is prefixed and additive, the existing list is read before anything is written, and the running session is preserved under its own name before any restart.**
- [ ] **"to test whats needed"** — work `TEST.md`, highest value first: the things today's build changed and no launch has ever seen. The art and audio in world, the aura's five states, the three animation sequences, and **the five cues that had no consumer until today** — those have never played for anybody. Then the rows the owner's own bug reports are waiting on.

### From the live session, 2026-10-06 — found by watching rather than by being told

**Verbatim owner question (2026-10-06):** *"have you been paying attention?"*

**Everything below came out of the owner's running game through the bridge and the log.** The owner reported none of it and was not asked to. **Nothing here is built while they are playing** — a rebuild re-stages the package under a live session and makes the staged copy disagree with the running one.

**Session facts, measured:** `0.13.0-dev` loaded — today's build, so the sort and save landed. Scenario `lone_survivor`, seed 1969031978, 3 colonists, 2 maps, tick climbing past 1346. Fixture tells attached to 1802 definitions, odd-origin marker to 2769.

- [ ] **ONE WELCOME LETTER IS SENT TO ALL THREE STARTS, AND IT DESCRIBES A FACILITY AND A GATE THAT TWO OF THEM DO NOT HAVE.** `ScenPart_RimroomsStart` sends `RR_Start_WelcomeTitle` + **`RR_Setup_Welcome`** unconditionally, with no branch on `startDef`. On the `lone_survivor` start the player is told *"The fixed facility is separate from those supplies"* and to *"complete the gate and prepare a real return route"* — and `scenarios.md` says that start has **"None, and no facility"**. The owner read that letter this session.
- [ ] **AND THE RIGHT TEXT ALREADY EXISTS WITH NO CONSUMER.** `RR_Start_Welcome` is declared in `RR_Scenario.xml` and **no C# file names it**: *"Your Async Industries branch is operational. The gate is still incomplete."* So the Async-specific welcome was written, shipped, and never sent, while the generic one goes to everybody. **This is the third instance today of content with no consumer** — after five sound cues and the gallery pictures — and `check-keyed-strings.py` has **no unused-key rule at all**, so an orphaned keyed string is invisible exactly as an unplayed cue was.
- [ ] **`rimworld/list_maps` DOES NOT EXIST ON THIS BRIDGE, and it is in the shipped client's allowlist.** `tools/qa/rimbridge_readonly.py` lists `maps` in `READ_TOOLS`; the live bridge answers *"Tool 'rimworld/list_maps' not found"*. It failed **50 times in one session**. Either the name changed or it never existed — `rimworld/list_zones`, `list_areas` and `get_game_info`'s own `mapCount` are what the live bridge offers.
- [ ] **605 OFF-THREAD RESOURCE ERRORS IN THE SESSION, AND I NEARLY REPORTED THEM AS TODAY'S FAULT.** Verbatim, repeating: *"Tried to get a resource "lock" from a different thread. All resources must be loaded in the main thread."* **The first one lands immediately after our own `[Rimrooms][Company] Initialized ... scenario=lone_survivor` line**, which looks like a smoking gun and is not one. **Yesterday's 0.12.99-dev session has 580 of the same thing** — so it is pre-existing, it is not today's build, and it is not the watcher, which did not exist yesterday. **The shape is exact and worth keeping:** five resources — `lock`, `unlock`, `UI/Commands/CopySettings`, `UI/Commands/PasteSettings`, `UI/Commands/ChangeColor` — each requested **the same number of times** (121 each today, 116 each yesterday, 5 × 121 = 605). That is **a door's gizmo set, resolved once per door**, during threaded map generation. **It is not us doing the enumerating:** we *provide* gizmos through `CompGetGizmosExtra` on `CompRimroomsGate`, and providing one resolves no icon until something asks — nothing in our source calls `GetGizmos`. The `lock`/`unlock` pair points at a door-access mod in the profile. **Bears on the compatibility rows rather than on a Rimrooms defect**, and the correlation with our log line is an artefact of company init being the last thing written before generation threads.

### Owner answers at four forks, 2026-10-07 — two are buildable and come here, two are the test phase

**Verbatim owner direction (2026-10-07):** *"im looking at the back rroms you did the lights look great, and use ask me question iof u have issues of forks in the testing items you should be crossing off, use ask me question where u need my eyes"*

- [ ] **"not self but shelf! its like items in the game are names route 30 or other names i can litterally see the text under funature and stufff name route 21 and shit, do you get it now? these seem weird like what tdo i do with these route 12 furnature things"** — the text under furniture is the room clue label (`RR_Clue_Label_service_passage` is *"Route-marking point — room {0}"*, drawn under the service passage's shelf). **The label names the thing and never says what a player does with it**, and that is the whole of the complaint.

### Found playing, 2026-10-07 — a refused dispatch leaves an expedition behind

- [ ] **THREE PLANT ANCHORS NO LONGER FIND THEIR CODE, AND THE "33 OF 33" IN NOW.md WAS NOT TRUE.** `check-plant-anchors.py` fails at `4469e9f` before any change of this session: `plant-generation.py` *"A ROOM WITH NO WALL GETS THE WALL FIXTURE ON THE FLOOR AGAIN"* and *"the hallways stop being lit"* find no match in `GenStep_BackroomsDestination.cs`, and `plant-unnerving-register.py` *"MARKING MOVES ABOVE THE SPAWN"* none in `RoomContentBuilder.cs`. The lighting and walls commit `bcf0701` rewrote both files. Re-aim each anchor at the code as it stands; never weaken the claim.
- [ ] **The English DefInjected file still describes the single-bill gate.** `Languages/English/DefInjected/RecipeDef/RR_GateRecipes.xml` overrides `RR_AssembleMachineGate` to *"assemble gate"* and *"Physically carry 100 steel and 8 industrial components"*; the def is one **section** of 25 steel and 2 components, four sections. The bill reads "Assemble gate" on the table for that reason.

### Found playing, 2026-10-07 — an expedition's gate closes twenty minutes after the crew crosses

**Owner direction this was played under, verbatim (2026-10-07):** *"wtf keep fucking playing and set a watch dog so if u stop thinking idel for 1 minute we get woken with \"get the tests all completed\""*


- [ ] **A survey counts only the FIRST room of each required family, and nothing on screen says so.** `EvidenceObservations.RefreshRouteRecorded` takes `coordinate.rooms.FirstOrDefault(r => r.familyId == family)` for each of the six families, so the crew had surveyed a survey lobby (room 6) and a borrowed corridor (rooms 5, 23, 29) on AI-01 and neither family counted -- only rooms 3 and 2 did. The objective reads *"Survey the six required room families"*, which a player takes to mean any room of each. **And the record book that counts is the bound one found in the office, not the blank book the kit loads**: room visits while only a blank company book was carried marked the Atlas but recorded no observation, so the checklist read *"No witnessed observations have been recorded yet"* over seven surveyed rooms.


- [ ] **The Quiet Pursuer never spawns, so the optional entity observation can never be recorded.** Played 2026-10-07 on AI-01: a route-home glow pod set in room 1, the crew walked into the borrowed corridor, the route mismatch fired and recorded (*"a door repeats the last room's label, but the route counter disagrees"*), and no pursuer appeared in the minutes after. The save reads `rr_distortionWarned True` with `rr_pursuerEncounterStarted` never set. `FirstSlicePursuer.StartPursuer` only places the chaser in a room two away that can reach the crew under `TraverseMode.NoPassClosedDoors`, and returns silently when none can -- and `bcf0701`, the same day, put *"A door across every corridor leg"*, so every room two away is behind a closed door. Likely a regression from that commit. **The fork is how the chaser should path**: through doors as a pawn would, or placement ignoring doors and the chaser opening its own way.


- [ ] **The equipment-link menu lists every candidate as an identical row with no position.** *Linked equipment* on the gate offered *"Link Wooden shelf as Records archive"* sixteen times and *"Link Wooden shelf as Armory"* sixteen more, with nothing saying which shelf each was; the one linked turned out to be the security-room shelf at `(159, 141)`, found only by reading the save. Each row needs the thing's position, or the menu needs to highlight its target on hover.

## TOMBSTONES

_(none)_
