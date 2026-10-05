# TODO — Minor Task List (Active Tasks)

**Tier 2 of 3** — the MINOR task list. Holds active tasks (pending + in_progress) at the day-to-day work grain. Each minor task lives under a major milestone in `docs/ROADMAP.md` and decomposes further into entries in `docs/DECOMPOSED.md` when YOLO mode picks it up.

Completed tasks move to `docs/FINALIZED.md` per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`. Never delete a task description; only flip status (LAW: NEVER DELETE TODO INFO).

Status markers:
- `[ ]` pending
- `[~]` in_progress
- `[x]` complete (move to FINALIZED.md immediately, never leave here)
- `[T]` belongs to the **post-completion test phase** — cannot be *closed* without the game running, gates no work, and is never a reason to stop building

**There is no blocked-on-owner status, by owner direction 2026-09-28.** Nothing here waits on the owner. Runtime rows are `[T]` and feed one named phase that begins only once the mod is complete; see [`DEFERRED.md`](DEFERRED.md) §The post-completion test phase.

LAW #0 reminder: every task description preserves the user's verbatim words.

**Three-tier cascade:** ROADMAP.md (major) → TODO.md (minor, this file) → DECOMPOSED.md (decomposed). YOLO mode reads all three and works the cascade — see `.claude/commands/yolo.md` and `.claude/WORKFLOW.md §YOLO MODE`.

> **Live project TODO for Rimrooms - Async Industries.** Seeded 2026-09-28 when the Claude Code workflow took over from the previous build agent (ChatGPT 6 Astra). This file carries **every open item** of the complete mod backlog, quoted verbatim from [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) (the "master TODO"), grouped under the majors in `ROADMAP.md` and in the master TODO's own order. The master TODO stays the authoritative gate/evidence record; when an item here closes, tick the identical bounded subitem there in the same change with its evidence link, per `REGRESSION_CONTAINMENT.md`. Items whose source already exists but whose runtime acceptance is open stay `[ ]` — the master TODO's rule: *"Unchecked tasks below retain their full stated implementation/acceptance scope; they do not mean all referenced source is absent."*
>
> Owner sequencing override (2026-09-28): implement remaining systems while game testing is deferred; gameplay-gate statements govern acceptance/promotion, not permission to write source. Only the owner launches RimWorld, through RimSort.

---

## In progress

### Session direction, 2026-10-03 — build the buildable, stage nothing, cascade nothing

**Verbatim owner direction (2026-10-03), four clauses:** *"we are finishing buildable items still open in todos(test items and live runs are not being done yet so no need to stage and no need to cascade until told to start again"*

**These four are CONSTRAINTS ON THE SESSION, not units of work, so they carry no status marker.** Owner challenge, 2026-10-03, verbatim: *"50 partital sounds like you havent been completeing your work"* — **and they were right.** Written as `[~]` rows, these four read as four tasks in progress forever: a constraint cannot be *completed*, so it can never leave the queue, and it inflates the partial count while telling nobody anything. The owner's own 2026-10-02 direction already says where governance belongs: *"A rule that must survive goes to `.claude/CONSTRAINTS.md` or becomes a checker. Open work goes to `docs/TODO.md`."* Every word is kept; only the checkbox is gone.

- **"we are finishing buildable items still open in todos"** — the standing instruction for this session. Work the open rows that can be *built* from here, in cascade order, and keep going. A row that cannot be closed without the game running is not this session's work.
- **"(test items and live runs are not being done yet"** — `[T]` rows stay `[T]`. No checker is run *as acceptance*, no live-read instrument is pointed at a process, and nothing waits on an observation.
- **"so no need to stage"** — ~~`tools/stage-mod.ps1` is NOT run this session.~~ **SUPERSEDED, see below.**
- **"and no need to cascade until told to start again"** — ~~no publish, no push, no ten-ref cascade.~~ **SUPERSEDED, see below — and this clause asked to be told, so being told is the clause working rather than being overridden.**

### Session direction REPLACED, 2026-10-03 — staging, NOW.md and the cascade come back, in batches

**Verbatim owner direction (2026-10-03):** *"aftert u finish up go ahead and get back to the staging, now.md writeing, and the cascades but not every time u do something only after you finish like 10-12 items in the todo do u do another stage/cascade"*

**This supersedes the two struck clauses above**, which is the earlier direction's own stated exit — *"until told to start again"*. Also a constraint rather than work, so no status marker, and every word kept.

- **"aftert u finish up"** — the batch in flight finishes first. A stage in the middle of a half-landed change is the thing `stage-mod.ps1` already refuses for a different reason.
- **"go ahead and get back to the staging, now.md writeing, and the cascades"** — all three resume: `tools/stage-mod.ps1`, rewriting `docs/NOW.md` as the one handoff record, and the **ten-ref** cascade per `PUBLISHING.md` (`forgejo` and `github` × `feature/connected-colony-portals`, `Prep`, `Develop`, `Main`, **plus `feature/bug-testing` on both** — a publish that reads back eight has silently left the working branch unpublished).
- **"but not every time u do something"** — **the publication cadence is explicitly NOT per-change.** This agrees with the standing regression-containment rule already in `PUBLISHING.md`: *"publish only at meaningful milestones, all changes batched"*.
- **"only after you finish like 10-12 items in the todo do u do another stage/cascade"** — **the batch size is 10–12 closed items.** Counted as rows archived out of the queue to `FINALIZED.md`, because that is the one count that cannot be inflated: a row only leaves on a proved verbatim transfer.

### Owner answers at four forks — the chasers are ordinary pawns, the DLC only adds, and the glass comes out (2026-10-04)

Asked because each one gated work that was already queued, and three of the four changed what gets built rather than how.

### Owner direction — the unnerving register is not a room feature, it is the register everything plays in (2026-10-04)

**Verbatim owner direction (2026-10-04):** *"remember lsd unnerving feeling with all things ie events random spanwns, enemies, allies, nuetrals, even all the crazy things ive mentioned in the past and anything u can find in the many many prep docs on the Backrooms Universe"*

**THE WORD THAT CHANGES THE SCOPE IS *"all things"*.** The LSD direction has been read as an *architecture* direction for eight versions — bent corridors, seven room shapes, roads, neighbourhoods, a per-coordinate motif. All of that is built. **None of it reached a single encounter, spawn or event**, and the owner has now said twice that the register is wider than the walls: *"even wild waky carzxzy creepy things when u add places and events"*, and the complaint that produced it, *"zero weird events or people"*.

**This direction asked to be gathered, so it is gathered here rather than cited.** Every line below is the owner's own, verbatim, with where it was said:

| Owner's words, verbatim | Where it bears |
|---|---|
| *"its suppose to be a lsd trip when it comes to archeteture and shit"* | the original, and the half that is built |
| *"i want you to expand and expound on everything in a lsd way"* | answered at a fork; **"everything"**, not the walls |
| *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"* | the register deepens with depth |
| *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"* | **the mechanism: who WAS here, read off what they left** |
| *"even wild waky carzxzy creepy things when u add places and events"* | places **and events** |
| *"not enough weird stuff like a room with a lost person or a room full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or tool sheed or weapons locker with loot and supplies anssd furnuture"* | named examples, and three of them are **people**, not rooms |
| *"zero weird events or people"* | the complaint, in four words |
| *"with wild random events and layouts and spawns to find and loot!!!!!!"* | events, layouts **and spawns** |
| *"really want the creepy insane looks and feel of the universe"* | the acceptance condition |
| *"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"* | the register scales with depth and band, and must stay survivable |
| *"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"* | the relations this applies across |
| *"and remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"* | the instruction to do exactly this gathering |

**AND THE PREP DOCUMENTS ALREADY SAY HOW THE FEELING IS PRODUCED, which is the part that was never applied to people.** `docs/UNIVERSE_ADAPTATION.md` line 21, on translating the source: *"Ordinary industrial interiors become uncanny through exact changes ... Use intentional spatial changes such as a shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or a feature that has moved since the last visit."*

**The uncanny is an exact change to something ordinary.** It is not a new monster, a darker palette or a louder sound — the generator already applies that rule to space and it is why the floors read. Applied to an encounter it means: an ordinary RimWorld pawn, in an ordinary RimWorld relation, with **one exact thing wrong about it that the player can read**.

**`docs/THREAT_DESIGN_SHEETS.md` supplies the fairness frame and it binds every row below:** every encounter has *"a visible or otherwise accessible warning, a learnable rule, at least one countermeasure, and a recorded outcome"*; *"Do not use color or sound as the only way to notice a tell"*; first contact *"must not kill a healthy pawn instantly"*; effects are *"bounded, seed-stable, logged against a coordinate, and recoverable after saving and reloading"*. Its own closing section already named this gap — *"The other proposed monstrosities, world-town openings, missing-crew outcomes, infected or altered arrivals, containment escapes, hostile sites ... remain open design work. Do not reuse these two behaviors as a generic random-threat generator."*

- [T] **"remember lsd unnerving feeling with all things"** — **the standing acceptance condition on every encounter, spawn and event**, in the owner's words. A spawn that is merely a hostile, or merely a neutral, is the thing being complained about. The uncanny is one exact wrong detail on something ordinary, and it must be **readable** — text, never atmosphere alone. — **MECHANISM BUILT AND ENFORCED 0.12.88-dev; **the row stays open because only a launch judges a feeling.** What exists now: a `tellKey` on all twelve inhabitant families and a `traceKey` on all eight events, both refused at load if absent, both read off the thing rather than out of a notification, and both held to *one exact wrong fact, never a mood adjective* by `proof-unnerving-register.py` — the rule taken straight out of `UNIVERSE_ADAPTATION.md`. `plant-unnerving-register.py` is **32 of 32**. **What it does not cover yet**, named rather than implied: loot and equipment carry no tell of their own, the room clue texts are still instructional rather than uncanny (deliberately — they teach the vertical slice and rewriting them would remove teaching the owner valued), and *"all things"* is open-ended by construction. This is an acceptance row like *"its suppose to be a lsd trip"* and it closes when the owner plays it, not when a checker passes.** — **THE OBJECT HALF LANDED 0.12.89-dev; **the row stays open because only a launch judges a feeling.** 0.12.88-dev reached people and events; this batch reached **objects**, which the owner had named specifically — *"items and equipment and production benches"*. Twenty object tells across nine classes, each one exact wrong fact read off the thing, held to the **same no-mood-adjective gate** taken from `UNIVERSE_ADAPTATION.md`, and kept to a small derived minority of placed objects so the quiet rooms stay quiet. `plant-unnerving-register.py` is **50 of 50**. **What *"all things"* still does not cover**, named rather than implied: the room clue texts are still instructional rather than uncanny, deliberately, because they teach the vertical slice and rewriting them would remove teaching the owner valued. This is an acceptance row like *"its suppose to be a lsd trip"* and it closes when the owner plays it.** — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own words.** It already records the mechanism as *built and enforced* at 0.12.88-dev and says it stays open because **only a launch judges a feeling.** That is the definition of the post-completion test phase rather than of open work: there is nothing left to build, and the next step is the owner reading a spawn and saying whether it lands.

### Session direction, 2026-10-04 — this file ends as a template holding nothing

**Verbatim owner direction (2026-10-04):** *"read now.md and continue the work we are working off todo items to get the todo to a templet form with no items listed and all complketed and moved completed into finalized.md"*

**A constraint and a destination rather than a unit of work, so it carries no status marker** — the same treatment the 2026-10-03 session directions above have, and for the same reason: a destination cannot be *completed*, so written as a row it would never leave and would inflate the partial count while telling nobody anything.

- **"to get the todo to a templet form with no items listed"** — the terminal state is this file holding its **preamble, its status-marker legend and its headings, and zero rows**. That is what *"templet form"* means: the shape stays so the next queue can be poured into it.
- **"and all complketed and moved completed into finalized.md"** — and every row leaves by the one door, `tools/archive-finished-todo.py` into `docs/FINALIZED.md`, on a proved verbatim transfer. **Not by deletion.** The count at the start of this session was **79 open · 38 partial · 38 `[T]`**.
- **THE `[T]` ROWS ARE THE ONE HONEST OBSTACLE AND IT IS NAMED HERE RATHER THAN DISCOVERED LATER.** A `[T]` row cannot be closed without the game running, and only the owner launches. Thirty-eight of them cannot reach `FINALIZED.md` from a keyboard. Everything else can, and this session works the rest.

### Bug hunt, 2026-10-02 — starting goods and the tab that stole Architect's slot

**Verbatim owner direction (2026-10-02), the start:** *"okay bug hunt feature branch 1. im not correctly starting weith my set up prepare carfully goods and the scenerios starting good... as you can see they are not accurate if you check the current running game, just as an example of whats not right.. my preparecarfully mod food did not appear and the starting scenerio supplies of food did not appear and should start scenerio with survival meals not simple meals and should be like 100 to start besides whats set in prepare carfully so check the current game and whats on the map versus what they were suppose to start with verses how to fix it properly now"*

**Verbatim owner narrowing (2026-10-02), after the live read:** *"as far as that start bug it was just the simple meals that need to be survioval meals and they need to properly spawn in with starting goods"*

- [ ] **"they need to properly spawn in with starting goods"** — **STILL OPEN, and no fix was written on a hunch.** — **MEASURED FROM THE LIVE GAME AND IT IS A REAL DEFECT, not just the meal def.** A 9,216-cell sweep centred on the three colonists at (147,151) found **none** of the Store's seven `ScenPart_StartingThing_Defined` grants: no `Silver` (200), no `WoodLog` (200), no `Cloth` (120), no `MealSimple` (24), no `MedicineHerbal` (8), no `Gun_Revolver` (1), and only 6 `Steel` against 80. The shop's **fixtures** are all present (18 `Shelf`, 6 `Bed`, 3 `ElectricStove`, 12 `Table2x2c`), so the layout ran and the grants did not. The one `MealSurvivalPack` on the ground and the one in each pawn's inventory are **Core's default pawn possession**, not a scenario grant, and the `Gun_ChargeRifle`/`MedicineUltratech`/`MechSerumYouth`/`Neurotrainer_Mining` nearby are **ancient-danger loot** from Core's own scatter. — **CAUSE STILL NOT FOUND, AND FOUR CANDIDATES ELIMINATED 0.12.91-dev — **the row stays open because it says *no fix was written on a hunch* and that still holds.** Eliminated against the installed game rather than guessed: **(1)** the arrival part is not missing — `ScenPart_RimroomsArrival` **subclasses** `ScenPart_PlayerPawnsArriveMethod` and calls `base.GenerateIntoMap`, which is the one place in the game that collects `PlayerStartingThings()` and places it; **(2)** the start spot is not wrong — Core’s `FindPlayerStartSpot` is order 850 and only picks when none is valid, ours is set at 800 and kept; **(3)** the gen steps are not out of order — Core’s `ScenParts` is order **875**, after both; **(4)** the pawns do not arrive by pod and scatter — `Standing` is enum zero and the scenarios set it explicitly. **And the row’s own evidence rules out the next obvious one:** the pawns’ `MealSurvivalPack` possessions *did* arrive, and possessions travel in the same list as the grants through the same `DropThingGroupsNear` call — so the placement ran and the grants were not in the list it placed. **What landed instead is the thing that makes the next launch answer this.** The receipt now records what the scenario **promised** and what actually **arrived**, and the start reports the gap on the letter stack. The promise is read through `GetSummaryListEntries`, which **creates nothing** — enumerating `PlayerStartingThings()` again would manufacture a second set of goods, the exact double-grant the receipt exists to prevent. It never blocks a start, and it is silent unless a promise was recorded and nothing at all arrived.**
- [ ] **"my preparecarfully mod food did not appear"** — **STILL OPEN, and the blocker is named rather than pointed at: it waits on the same `Player.log` as the starting-goods row, because both halves of the original report travel the same path.** — same path. Prepare Carefully's equipment reaches the map through `ScenPart.PlayerStartingThings()`, which is the same enumeration the scenario grants use, so one break explains both halves of the original report. — **SAME PATH, SAME DIAGNOSTIC 0.12.91-dev. Prepare Carefully’s equipment reaches the map through `PlayerStartingThings()`, which is the same enumeration the scenario grants use — so one break explains both halves of the original report, exactly as this row says. **The new start report names this quarter explicitly**, so the next launch produces a log that either implicates it or clears it: the letter lists what the scenario promised and says that a mod supplying starting equipment is the most likely cause, with the request for the `Player.log`. The row stays open until that log exists.**

## Pending


### Owner direction — the mod's own menu images belong on the loading screens too (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and anothert thing.. we properly use the main menu images we made for the mod on the main menu page but i dont think we properly did the same for loading screens and the like add this to the todo"*

**Verbatim owner direction (2026-10-03), the shape of it:** *"so we need those mod images made for the menu to also use them randomly for load screen backgrounds"*

### Owner answers at three forks — don't limit yourself, expand it in an LSD way, 3× vanilla ore (2026-10-03)

Asked because each one changes what gets built, and all three were answered as *more* rather than as a choice between options.

### Owner report — a door refuses to become a gate until the battery is set up first (2026-10-03)

**Verbatim owner report (2026-10-03):** *"and another bug repoert, i try to first thing set a door as gate on the doors ui bar, but it tells me i have to set up the battery used for reserver before i can do anything, incrattely, i should be able to set the gate on a door first, so idk why its tellign me i cant set the gate door without setting the batteries first"*

**Verbatim owner scope (2026-10-03):** *"in company scenerio"*

**Located in source the same session; the cause is the all-or-nothing resolve inside the door's own button.** `Gate/CompRimroomsGate.cs` `MakeGateGizmos` resolves **three** providers before it will bind anything:

```csharp
Thing console = SoleCandidate(AvailableNativeConsoles(campaign));
Thing battery = SoleCandidate(AvailableNativeBatteries(campaign));
Thing bench   = SoleCandidate(AvailableNativeAssemblyBenches(campaign));
if (console == null || battery == null || bench == null)
{
    ShowOrderResult(CompanyActionResult.Refused(
        console == null ? "RR_NativeGate_NoSingleConsole"
        : battery == null ? "RR_NativeGate_NoSingleBattery"
        : "RR_NativeGate_ChooseBench"));
    return;
}
```

`SoleCandidate` returns null for **none** and for **more than one**, so the button refuses whenever the battery is absent *or* ambiguous — and `RR_NativeGate_NoSingleBattery` is the owner's *"i have to set up the battery used for reserver before i can do anything"*. The method's own docstring already says it is only meant to be the one-click path — *"anything ambiguous is named and chosen in the Operations pane, because picking one of several for the player is a decision rather than a shortcut"* — but **a refusal is not a route**, and the owner was reading the refusal as the answer.

- [T] **Observed on the company scenario start** — the owner's repro is a launch.

### Owner report — an open gate is charging power to send people through (2026-10-03)

**Verbatim owner report (2026-10-03):** *"and another bug report on the company scenerio start i build and set up and open the gate but it incorrectly says i dont have power to send people through, even tho the gate is open and connected,,, thast is wrong if its open it doenst need special power to send things through the gate"*

**Verbatim owner detail (2026-10-03), naming the message:** *"when i try to send people through it gives me a error about not enough reserver power in the batteries or something incarrate that shouldnt be"*

**The second message identifies the string, and the design statement in the first decides the fix.** Located in source the same session: `Gate/PortalGateOpening.cs:113` `PortalWindowBlockerKey` is the single authority gating a crossing — `HasUsablePortalWindow` only asks it — and on an **already-open** aperture it still applies three *opening-time* power conditions:

| Condition | Where | Why it does not belong on a crossing |
|---|---|---|
| `stablePowerTicks < stablePowerTicksRequired \|\| !HasPowerAndHeadroom()` → **`RR_Gate_PowerUnstable`**, *"The gate needs stable connected power and a charged return reserve."* | `CompRimroomsGate.CheckStationReadiness`, called at `PortalGateOpening.cs:124` | `stablePowerTicks` is a **spin-up** counter — it means "has held power long enough to open". Once open that is answered. And **"a charged return reserve" is the owner's *"reserver power in the batteries"*.** |
| `ProjectedOpeningPowerFailure()` → `RR_Gate_SupplyTooLow` / `RR_Gate_HeadroomTooLow` | same call | Both are projections of the **opening** draw. An aperture that is already held is not a projection. |
| `NativeStoredEnergy < OpeningPowerDrawWatts * WattsToWattDaysPerTick` → **`RR_PortalTravel_NoCharge`**, *"...Its circuit needs power in the batteries, not just a generator running..."* | `PortalGateOpening.cs:128-129` | Charges stored energy per crossing. This is the other candidate for the message, and it is the clearest case of *"if its open it doenst need special power to send things through"*. |

**And the per-crossing power check is redundant as well as wrong, which is why this is a deletion rather than a tuning.** Power loss while open is already owned by the tick: `CompRimroomsGate.cs:406` runs `HasPowerAndHeadroom()` every tick and calls `EnterEmergency("RR_Gate_PowerLost")`, and `PortalWindowBlockerKey` **already** refuses an emergency gate three lines earlier with `RR_PortalTravel_InEmergency`. So the crossing path is deriving, a second time and with a worse message, a rule the tick already enforces — *"two derivations of one rule is the defect this project keeps meeting"*, in the words of this very file.

- [T] **Observed in play on the company scenario start** — the owner's own repro is a launch, and only the owner launches.

### Owner direction — the mod must not need any dependency mods (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and something i dont like that is going to take major major work and should be added to the todo : rework mod to not need any depeancie mods"*

Recorded here because the owner said *"should be added to the todo"*. **It supersedes owner decision D3/D4 as amended 2026-10-01**, which currently reads *"the five expansions and the collection are declared requirements"* — recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md), [`ROADMAP.md`](ROADMAP.md) §Decision log and [`ARCHITECTURE.md`](ARCHITECTURE.md) §B1. Those three say the opposite of this direction and all three are rewritten in the same commit as the work, per `.claude/CONSTRAINTS.md §DOCS BEFORE PUSH`.

**Measured 2026-10-03 before writing this row, because the shape of the job is not what the words suggest:**

| What | Measurement | Where |
|---|---|---|
| Hard `modDependencies` declared | **294** | `Mod/Rimrooms - Async Industries/About/About.xml` |
| `loadAfter` entries | **294** | same file |
| Assembly references | **4 — `Assembly-CSharp` + `UnityEngine.CoreModule` / `IMGUIModule` / `TextRenderingModule`. Nothing else. No Harmony.** | `src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj` |

**So the two halves of this are wildly different sizes, and saying so is the point of measuring first.**

- [T] **Core-only startup actually observed.** The audit above closes on source evidence; a clean Core-only load with zero red errors is a launch, and only the owner launches. Post-completion test phase, gates nothing.

### Open rows carried out of the play-testing checkpoints (2026-09-30 to 2026-10-01)

**Lifted here 2026-10-02 by owner direction:** *"we need to move all finished items to finalized.md from the todo, the todods sahll never hold completed items, they are always to be moved to finalized first then deleted from the todods once confirmed virbatium transfer"* and, on being shown the queue still at ~96 KB, *"BEcause the todos are still like 100kb and i know that not all unfinished work and only unfinished work like it shall be"*.

Nine `##` sections titled as dated checkpoint records held **20.9 KB** between them, most of it the finished write-up of a launch or a rebuild stage, with these open rows buried inside. **A section called "Fifth launch findings - 2026-09-30" is a thing that happened, not a thing to do.** Each section is archived whole in `FINALIZED.md`, record intact; every open row it held is below, verbatim, tagged with the checkpoint it came out of.

**1 row(s) repeated verbatim across checkpoints and are carried once.** The same open item written three times is one open item; the repeats are named in the archive rather than dropped silently.

**From `## The first walked level — 2026-09-30 (0.12.61-dev) — DONE`:**

**Adjudicated against the source 2026-10-03.** The section title was never the marker, per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`: *"A section titled DONE whose rows are still `[ ]` does not move. The title is not the marker."* So each row below was read against the code rather than promoted on the heading's word. **Eleven of the twelve were built and nobody had ticked them.** `RoomLayoutPlanner.cs` (1,351 lines) and `RoomArchetypeService.cs` (392) were read in full; `RoomContentBuilder.cs`, `BackroomsPalette.cs`, `GuaranteedFrontiers.cs` and the four Def folders were read at the named sites. **Register checked:** `python tools/register-query.py trace RR-SPACE` → 15 rows, Core *Required* and the rest *Optional* / *Configuration only* / *No integration*; none applied, because this pass changes no code.












- [T] **"there is a weird route thing name a self in one of the rooms and this is kinda weird and odd"** — owner's own read: *"we probably havent gotten to a routing system yet for emergency exit and glow pods with the company start but lets try and fix this"* — **THE STATED CAUSE IS ANSWERED AND THE SIGHTING IS NOT, so this is the one row of the twelve that moves to the test phase rather than closing.** The routing system the owner supposed was missing **exists**: `CompRimroomsMarker` with five `RimroomsMarkerTypeDefs` — `RR_Marker_Route` labelled *"route home"*, plus `_Cleared`, `_Danger`, `_Cache`, `_Lead` — numbered through `FirstSliceSiteComponent.NextMarkerNumber`, and the survey tag is a Core `GlowPod` since 0.10.7-dev. **But markers are player-deployed, so a freshly generated level should carry none**, and **what the owner actually saw cannot be identified from here** — naming it needs somebody looking at the object on a map. Deliberately not guessed: editing a label on a hunch is the same move that lost three launches in one method.

**From `## Lights and geometry — 2026-09-30 (0.12.61-dev) — DONE`:**

**Adjudicated against the source 2026-10-03, same pass as the section above.** **All ten were built and none had been ticked.** Seven of them are implemented by one function, `RoomLayoutPlanner.RockIntrusionCells`, whose seven forms exist precisely because of these rows.











### Major M1 — Connected colony portals (ROADMAP M1; master TODO §Native-provider foundation — 0.4.0-dev)

Binding contract: [`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md). Baseline commit `8ed4e32`, 0.4.1-dev, 75 C# files, 71 package files, zero warnings/errors. Read `implementation/CONNECTED_COLONY_CHECKPOINT.md`, `CONNECTED_COLONY_IMPLEMENTATION_TASK.md`, `CONNECTED_NETWORK_IMPLEMENTATION.md`, `CONNECTED_CROSSING_IMPLEMENTATION.md`, `CONNECTED_WORK_CORE_API.md`, `CONNECTED_PORTAL_STATE_MIGRATION.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md` before editing `src/RimroomsAsyncIndustries/Portals/` or `Gate/`. Source fact: nothing in the repo calls `RimroomsPortalNetwork.Register`, `PortalCrossingService.Cross`/`Recover`, or `CompRimroomsGate.BeginPortalOpening` yet.

**Master TODO items (verbatim):**

- [T] Implement every open item in [connected colony portals](CONNECTED_COLONY_PORTALS.md#required-implementation-backlog): independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants/complexity. This supersedes dispatch-only travel as the target. — **PARTLY BUILT**; what shipped is archived. **Open:** runtime acceptance of the built routes, and nothing in code. -- **EVERY ROUTE ON THIS ROW IS BUILT; WHAT IS LEFT IS A LAUNCH. 0.12.99-dev.** The pointer *"the individual routes listed below"* was the shape checker 25 was written against, and replacing it with the subjects is what showed the row was finished: **independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants** all ship. Cross-gate work is **31 families, 23 of them deployments**, and every work type in Core and all five expansions is covered or decided against with its reason recorded (`research/WORK_TYPE_COVERAGE_AUDIT.md`). **The only remaining step on any of its routes is runtime acceptance, which only the owner's launch can give**, so it belongs in the test phase rather than the working queue where it reads as something somebody could pick up.

**Resume order (verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`; these are the working sequence for the items above):**

- [T] **Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change." — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`. — **Open and structurally must stay open:** runtime acceptance, because only the owner launches. -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words.** It says *"Open and structurally must stay open: runtime acceptance, because only the owner launches."* **Every source and build milestone it asks for is met** -- build, evidence folder, build record, ticks, cascade -- and the cascade is now twelve refs with the tool receipting itself. What is left is acceptance, and acceptance is a launch. **A row whose only remaining step is an owner launch does not belong in the working queue.**

**Required implementation backlog (verbatim from `CONNECTED_COLONY_PORTALS.md`; the acceptance list the majors above must satisfy):**

- [T] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions. *(source partially complete in 0.5.0-dev: discovery, destination targets, bounded routing, planning leases and real native destination reservations exist and are proven for the storage-hauling family only; the other families are not implemented and runtime acceptance is open)* -- **MOVED TO THE TEST PHASE 0.12.99-dev -- THE PARENTHETICAL WAS A 0.5.0-dev STATUS NOTE AND IS STALE.** It says discovery, destination targets, bounded routing, planning leases and real native destination reservations exist *"and are proven for the storage-hauling family only; the other families are not implemented"*. **Thirty-one families are implemented**, 23 of them deployments, and `research/WORK_TYPE_COVERAGE_AUDIT.md` shows every work type in Core and all five expansions either covered or decided against with its reason recorded -- plus, as of this batch, the thirteen work types the 294 profile adds. Native priorities, schedules and restrictions are preserved and the handling closed earlier. **The row's own last clause is what remains:** *"runtime acceptance is open"*, and only the owner launches.
- [T] Implement connected-site scheduling/streaming and measure performance after an owner-launched build. — **STILL OPEN.** Scheduling and streaming ship. **Measuring performance requires an owner-launched build, which is the one thing this project cannot do for itself.** -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words.** It says *"Scheduling and streaming ship. Measuring performance requires an owner-launched build, which is the one thing this project cannot do for itself."* **A row whose only remaining step is an owner launch does not belong in the working queue**, where it reads as something somebody could pick up today. Every scan in `ConnectedWork/` is already a bounded rotating window rather than a prefix, by invariant 5, with roughly thirty budgets -- so the bounding half is done and the measuring half is a launch.
- [T] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants. — post-completion test phase (owner RimSort launch).

**Task-record subitems still open (verbatim from `implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md`):**

- [T] Owner-launched acceptance: both directions; chains/loops; closed/blocked endpoints; permanent natural links; save/reload; cargo identity; interrupted jobs; all supported native/provider routes. — post-completion test phase (owner RimSort launch).

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **Connected-site scheduling and streaming, then measurement.** Active connected job destinations must not be silently unloaded to meet a budget. Measurement itself belongs to the post-completion test phase and gates nothing. Source: `CONNECTED_COLONY_PORTALS.md`, `research/PERFORMANCE_BENCHMARK_PLAN.md`.

## Public face: the site, the Workshop page and the collection

**Verbatim owner direction (2026-09-29):** *"fyi when we get to it we will build a github deployable html build that catologs the whole mod and is the main mod site wiki and documentation dump in a beauty of a deployable github page with what ever you can do so the deploy address is not some random git hub address but is a nice backrooms url for github deployed page where we document all the mods capabilities and howto and related public facing docs and information into a website that lays everything out top to bottom beautiffully just like other rimworld mods make theri third party sites, not to metione the building of the steam workkshop mod collection and workshop mod deploy for our mode with write ups for  both with links in them to each other and the deployed site so things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop, idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"*

**Full plan: [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md)** - structure, the ordering chain, the domain question, and the three decisions that are the owner's to make.

**Not started. Owner said *"when we get to it"*, and it is correctly last:** every one of these artefacts describes the mod, so each is written twice if the mod is still changing underneath it. The same reason the player-facing how-to sits at the end of the build order.

### The ordering the owner named, which is a real dependency chain

1. **The mod is settled** - content set final, scenarios in, nothing still being retired.
2. **The site is deployed and working**, at its proper address.
3. **Then** the Workshop mod page, whose write-up links to the site.
4. **Then** the Workshop collection, whose write-up links to both.

Owner's words: *"things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop"*. Doing any of it earlier means publishing links that point at nothing.

### The Steam Workshop

- [ ] **Owner idea, verbatim:** *"idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"* - Playwright driving the Steam Workshop UI. **Ask before doing this**: it means automating an authenticated session on the owner's Steam account, which is a different kind of action from anything done so far and needs explicit permission, not an assumption. The alternative is a prepared write-up the owner pastes, which is far less work for whoever is not doing the clicking.

### Standing constraints that still apply

- **No Claude attribution** in any of it - site, Workshop page, collection write-up.
- **The owner alone launches, sorts and publishes.** Deployment of a site is not the same act as launching the game, but the Workshop is the owner's account and the owner's decision.


## Owner directions recorded late

These three were **acted on correctly and recorded in `NOW.md` or `FINALIZED.md`, but never
written into this queue as tasks**. The owner noticed the gap on 2026-09-29 and was right.
They are recorded here verbatim now, and `check-doc-conformance.py` refuses from this point
on to let a direction reach `FINALIZED.md` without appearing here first.

### Phase 1 leftovers (master TODO §Phase 1 — repository, build, and content foundations)

- [T] Define RimSort-managed test profiles: preserve the 295-entry product target (the existing 294 plus Rimrooms), then record RimBridgeServer as a separate QA overlay (normally 296 loaded entries). RimSort owns sorting, saving mod lists, and every launch; the owner starts sessions through RimSort. Do not add direct RimWorld or GABS launch profiles or remove target mods to offset the bridge. — post-completion test phase (owner-operated RimSort action).
- [T] After the first owner-launched full-target startup, collect matched Core/profile performance baselines on RR-DEV-01 and implement any missing counters per the [benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Enforce the recorded budgets before promoting features or larger room/map bands. — post-completion test phase (owner RimSort launch).

### Phase 2 — code architecture and safe vertical slice (master TODO; source largely present per `implementation/PHASE_2_BUILD_RECORD.md`, full stated scope + Gate 2 acceptance still open)

**Vertical slice implementation:**

- [T] Save, reload, revisit the same coordinate, and confirm map state and unique rewards persist without duplication. — post-completion test phase (owner RimSort launch).

**Gate 2 passes when** (master TODO): "the first complete loop plays from a fresh save through build, staff, expedition, extraction, analysis, reward, save/reload, and a second visit without a softlock or lost state." — owner-launched only.

### Major M3 — Phase 3 interconnected company simulation (ROADMAP M3; master TODO §Phase 3)

**Scenario framework and alternate starts** (contract: [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md); owner questions still open: inside-start party size; first-exit fixed vs chosen):

- [T] Verify every start's reload behavior, deterministic coordinate, objective idempotency, optional-DLC fallback, solo behavior, and RWT eligibility against `SCENARIOS.md`. — post-completion test phase (owner RimSort launch).

**Procedural sites and propagation** (contract: [`PROCEDURAL_SPACE_CONTRACT.md`](PROCEDURAL_SPACE_CONTRACT.md)):

- [T] Bound active map count, pawn/thing count, graph search, event evaluation, and background tick cost; profile large, long-running saves. — **Bounding is done; profiling is not and cannot be.** Every scan in `ConnectedWork/` is a bounded rotating window, never a prefix (invariant 5), with roughly thirty `Maximum*` scan budgets. **Profiling a long-running save requires launching the game, which only the owner does.** — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own words.** It says in its own text: *"Bounding is done; profiling is not and cannot be"*, and that profiling a long-running save **requires launching the game, which only the owner does.** Every scan is already a bounded rotating window rather than a prefix, with roughly thirty budgets. **A row whose only remaining step is an owner launch belongs in the test phase**, not in the working queue where it reads as something somebody could pick up.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [~] Research IDs across tiers T0–T6 and the nine branches; entity family sheets (broad families only per S1/B). — **Tiers 0–2 complete across seven branches; T3 is the next checkpoint.** The eighth branch (transport and orbital) has **no tier 0 at all, deliberately**, and the tree is derived rather than declared, so a tier number is not a promise of a linear chain. — **MEASURED 0.12.92-dev AND THE ROW WAS WRONG ABOUT T3. It says *"Tiers 0–2 complete across seven branches; T3 is the next checkpoint"*. **T3 is fully built** — seven projects, one per branch, each requiring its tier-2 sibling plus three route, two distortion and one entity log, with its own header at `RR_CompanyProjects.xml` line 418 and a record in `BUILD_ORDER_CORRECTION.md`. **T4 is built too**, six of seven, and both absences are reasoned in the file: Logistics has no tier 4 because lead time, dispatch delay, order capacity and unattended delivery are already taken by tiers 1, 2, 0 and 3, and what remains in Procurement is safety bounds no player will ever reach — *"a project here would promise something and change nothing, which is exactly what 0.12.5-dev deleted four projects for"*. The gate line has none and cannot: there is nothing above indefinite. **And the tier system is measurably healthy: 34 capabilities granted, 34 read, a perfect bijection** — no hollow unlock and no dead read. **So what is actually open is T5 and T6**, and the file’s own rule makes that a knob sweep rather than an authoring job: a tier may only exist where an unclaimed, player-noticeable knob does. 274 tunable constants exist and 34 are claimed, so the sweep has somewhere to look — but deciding which of the remainder a player could *name the effect of* is the work, and inventing seven projects without it would ship exactly the lie the file deletes projects for.** -- **THE SWEEP IS DONE AND THE PROPOSAL IS THE OWNER'S TO ANSWER. 0.12.99-dev.** Owner direction, asked how to resolve this row: *"Sweep the constants and propose the tiers to you"*. **`docs/research/RESEARCH_T5_T6_SWEEP.md`** is the sweep: **278 numeric constants enumerated** across 232 files, each screened on nameable / unclaimed / a play knob at all, and **most die on the third test** -- a schema version, a tick interval or a loop bound is not tuning, it is the machine working. **Six candidates survive and four branches honestly get none.** To build: **Facilities T5** servicing interval, which fills a gap **§1.1 itself names** (maintenance is one of the four factors that decide a gate's window and it is the only one with no project on it); **Measurement T5** the trained eye; **Spatial T5** the near exit, the most visible unclaimed number in the mod. **Entities T5** as `MaxEventsPerOpening` only, because `QuietRoomFraction` is half of the solo-survivability guarantee and a project that moves a guarantee turns an absolute into a research gate. **Fieldcraft T5** -- a fourth crew member -- is **the owner's call and the sweep will not make it**, because three is a stated design figure and raising it re-shapes the pressure arithmetic. **Spatial T6** -- a seventh level -- is the only T6 candidate and is **blocked on a sixth palette band**, which is a content question before it is a research one. **The four empty branches are each a finding, not a gap:** Gate has nothing above indefinite; Logistics has **zero** unclaimed knobs, every procurement constant living in a file that reads a capability; Transport has no tier 0 by design; and **Commerce's candidates became player settings at 0.12.98-dev**, which is better -- a research tier and a slider over one number is two controls fighting, and a project whose whole effect is *the slider you already have reads a different default* is exactly the promise-that-changes-nothing four deleted projects were deleted for. **Stays `[~]` because the decision is the owner's**, which is what *propose to you* means, and no project def is written until they pick.

### Major M4 — Phase 4 multiplayer, DLC, and the full profile (ROADMAP M4; master TODO §Phase 4)

Every item in this major needs a Rimrooms build the owner has launched; source-side preparation (feature detection, guards, adapters) can proceed, verification cannot.

**RimWorld Together adapter** (pinned release 26.8.31.1; no supported client extension API identified 2026-09-27):

- [T] Verify guild identity, facility mapping, configured visits/snapshot behavior, visits when online/offline, transfer spot, chill/defense spots, caravan interactions, events, sites, roads, aid, gifts, and trading. — post-completion test phase (owner-launched two-client run).
- [T] Verify transfer receipt IDs and item/pawn state prevent duplicates, loss, stale ownership, and broken stacks on disconnect/reconnect. — post-completion test phase (owner-launched two-client run).
- [T] Verify Backrooms Research Dossier item transfer; receiving branch must explicitly study it locally and be unable to claim it twice in one save. — post-completion test phase (owner-launched two-client run); dossier binds to an existing physical document object per the content-reuse rule.
- [T] Test unsupported/complex modded items and define an honest fallback message rather than promising an unverified transfer. — post-completion test phase (owner-launched two-client run).
- [T] Test separate colony saves, shared world actions, mod order/config enforcement, RWT server restart/backups, and an admin changing settings during play. — post-completion test phase (owner-launched two-client run).

**Five DLC layers:**

- [T] Before implementing or advertising optional VGE support, verify the clean Core + Harmony + Odyssey + VEF + both VGE chapters stack, Chapter 1 operations, Chapter 2 threat/defense/salvage, optional Insectoids 2, save/reload, and the gravship-touch profile graph. Keep this in the per-integration acceptance gate; it is not a Gate 0 requirement. See the [gravship profile review](research/GRAVSHIP_PROFILE_INTERACTIONS.md). — post-completion test phase (owner RimSort launch).
- [T] Verify all five individually enabled/disabled, then all combined. Maintain a 32-row DLC bitmask matrix (all combinations of five DLCs) if claiming full combinatorial support; at minimum, explicitly publish exactly which combinations were run. — post-completion test phase (owner RimSort launch).

**All 294 profile entries** (all rows source-reviewed; zero rows runtime-cleared):

- [T] Pin the exact profile and test clean Core, Core+RWT/Harmony, selected VGE stack, each high-risk family, and the full ordered profile. — post-completion test phase (owner RimSort launch).
- [~] For each workbook row, close its status with evidence: reviewed version, load-order placement, applicable DLC, behavior used/preserved, patch/adaptor/no-code reason, and result. — **CONTRADICTION RESOLVED 2026-10-03: THERE WAS NEVER ONE. Two different claims were being compared as though they were one, and both are true.** The *retro-sweep* row counts **families swept for what applies** and all twenty-one really are done (0.12.42-dev). This row counts something else entirely — **per-row disposition closure with evidence and a result** — and it is genuinely open. Counted from the register HTML rather than from either row's memory: **201 `Provisional` against 95 `Settled`** across 295 parsed rows, which matches the independently recorded *"200 of the 294 dispositions are still provisional"* in the M6a consequence row. So the work remaining is **201 rows to settle**, not *"7 families to sweep"* — the 14-of-21 figure was measuring the other row's unit and was the thing making this look contradictory. **Stays `[~]` because that is honest:** 95 rows are closed with evidence and 201 are not. The dangling *"see Contradictions found while splitting rows below"* pointer is removed; that section was archived on 2026-10-02 and the cross-reference had been pointing at nothing since.
- [T] Verify all QoL features remain available, including work-priority, UI, scheduling, storage, movement, hauling, selection, visitors, prisoners, health, combat, map, and scenario helpers represented in the list. — post-completion test phase (owner RimSort launch).
- [ ] Resolve duplicate Defs/patch collisions in the exact 294 profile; use load-after patches only where a reproducible conflict requires one. — **STILL OPEN.** **Structurally requires a launch with the 294 profile loaded**, which only the owner does, through RimSort.
- [T] Test gravship-changing profile mods against both VGE chapters; publish incompatible combinations rather than hiding known conflicts. — post-completion test phase (owner RimSort launch).
- [ ] Add a user-facing compatibility report with tested order, versions, DLC, known issues, unsupported features, and save caveats. — **STILL OPEN.** Cannot honestly state a tested order before anything has been tested.

### Major M5 — Phase 5 complete Company Command interface and polish (ROADMAP M5; master TODO §Phase 5)

Contracts: [`OPERATIONS_ACTION_CONTRACTS.md`](OPERATIONS_ACTION_CONTRACTS.md), [`research/VISUAL_AUDIO_STYLE_BRIEF.md`](research/VISUAL_AUDIO_STYLE_BRIEF.md), [`research/CONTENT_ACCESSIBILITY_BRIEF.md`](research/CONTENT_ACCESSIBILITY_BRIEF.md), [`TUTORIAL_SCRIPT.md`](TUTORIAL_SCRIPT.md). Source checkpoint: ten Operations panes, two original menu images, slideshow controller, settings, dynamic title/version exist.

- [T] Review every slideshow image with the actual menu overlay across supported aspect ratios, resolutions, and UI scales; check text contrast, crop safety, quiet transitions, reduced-motion behavior, and no-audio use. — post-completion test phase (owner RimSort launch).
- [T] Review text length, font scale, combat readability, motion sensitivity, audio levels, UI overlap at supported screen sizes, and translations. — post-completion test phase (owner RimSort launch).
- [T] Verify no UI panel conceals urgent health, fire, power, missing crew, gate recall, containment, or contract priorities. — post-completion test phase (owner RimSort launch).

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [~] Slideshow integration review, additional menu images per shipped scenario. — **Open, and it needs a launch:** the integration **review** itself — how the slides read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right — cannot be judged from here. (Six slides and `proof-menu-slides.py` closed at 0.12.17-dev; archived.)
- [ ] Validation sweep, invalid-state matrix, balance, release report, packaging. — **split 2026-09-29 by owner decision 19.** The validation sweep and packaging halves are M6a and close without a launch; the invalid-state matrix, balance and release report are M6b and cannot. Tracked as separate rows in `TODO.md`. — **STILL OPEN.** **Structurally requires a launch.** Balance in particular cannot be claimed: nothing in this mod has ever been played.
- [T] **Automated fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration.** Deferred **by explicit owner instruction**, 2026-09-29 (decision 20, verbatim *"option 2 and option 3"*), not by dependency: the owner authorised automated fixtures **and** chose to hold them until after the first launch so their content follows observed failures rather than guessed ones. This is the **only** exception to the `CONTRIBUTING.md` no-tests rule anywhere in the repo, it covers this row alone, and **nothing for it may be written before the owner has launched the game once**. Owned by M6b.
- [T] **Screenshots, trailer and preview art for the mod page.** Need a running game, so they split from the M6a mod-page row into M6b. Everything else on that row — description, feature list, installation guide, dependencies, DLC matrix, RWT setup, credits, provenance, license, FAQ, update plan — closes without a launch and is M6a.

### Major M6b — Phase 6 work that structurally requires the owner's launch (ROADMAP M6b; master TODO §Phase 6)

**Exit condition (D1, changed 2026-09-29):** the Core-only solo path passes. The private RWT prototype is no longer a release prerequisite and co-op validation no longer gates the first publication. The no-compatibility-claim rule stays binding and is now the main protection.

- [T] Create a reproducible fresh-start/save/reload/revisit checklist and automated or manual fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs, and schema migration. — **owner decision 20, 2026-09-29, verbatim: *"option 2 and option 3"***, being *automated fixtures in code* **and** *defer until after the first launch*, taken together. So: **automated fixtures are authorised** for this row, replacing the manual-checklist-only reading, **and none of it is written until the owner has launched the game once**, so its content is shaped by observed failures rather than guessed ones. The exception is narrow — the five subjects named in this row and nothing else — and is not permission for a general test suite.
- [T] Run the scenario acceptance checklist for every shipped opening: fresh start, reload, failure/recovery, route back to the shared campaign, and optional-mod/DLC absence. — post-completion test phase (owner RimSort launch).
- [T] Exercise invalid states: insufficient power, no operator, blocked route, missing exit, destroyed gate, overloaded expedition cargo, receiving bay full, split/delayed bulk shipment, missing/changed OgreStack setting, dead/missing crew, unsafe return, destroyed relay, unavailable RWT feature, failed item transfer, missing DLC, bad mod order, and old save migration. Include a one-million-silver case: 67 stacks under the active OgreStack default assumption, 2,000 under Core limits; verify actual in-save settings and record hauling/storage/transfer results. — post-completion test phase (owner RimSort launch).
- [T] Check performance on worst-case room graphs, multi-outpost company, long play time, many evidence/case records, visitors/prisoners, active threats, and gravship combat. — post-completion test phase (owner RimSort launch).
- [T] Balance economy and progression from fresh-start play through late game; check grind, runaway money, research skip routes, dead-end tech, exploitative optimal choices, and difficulty scaling. — post-completion test phase (owner-launched play).
- [T] Verify the full mod list one final time and capture game/RWT/DLC/profile versions, settings, logs, save, known compatibility issues, and results in a release report. — post-completion test phase (owner RimSort launch).
- [T] Test clean install/uninstall, load order, Workshop update, dedicated RWT server setup, player join, server backup/restore, save migration, and rollback to previous mod release. — post-completion test phase (owner-operated).
- [T] The launch-gated half of the mod-page row: **screenshots, trailer/preview art**, and any known-issues entry that needs an observed failure. The row itself lives in M6a with its full verbatim text; only these pieces need a running game. — post-completion test phase (owner RimSort launch).
- [T] The launch-gated half of the tag-release row: *"publish only features that passed their listed acceptance criteria"* — **nothing has passed anything, because nothing has run.** The row itself lives in M6a with its full verbatim text; the tag cannot be cut until the acceptance results above exist. — post-completion test phase (owner RimSort launch).

### Owner direction — the place copies you, and who you find in it (2026-09-29)

**Verbatim owner direction (2026-09-29), on ordering the remaining work:** *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*


- [ ] **"to the extent we want normal and really want the creepy insane looks and feel"** — the balance between recognisable and wrong is currently fixed by the depth curve. Whether it lands is a play question and belongs to the post-completion test phase.

### Owner direction — the look, and the seed generator that has to carry the universe (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly, and remmeber when building the seed genrator for the back rooms everything ive said and how the backrooms universe works to be lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

**And immediately after:** *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

That second message is what shaped the palette: a single global look could only ever deliver half the direction, so the look is a **function of depth**. Record: [`implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md`](implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md).

- [T] **"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying"** — **THE ARITHMETIC GUARANTEES IT AS OF 0.8.0-dev**, as three properties rather than tuning: an **absolute** cap of three simultaneous encounters at any depth and any wealth; **half of every coordinate's rooms bare by count rather than by chance**, so an unlucky run of rolls cannot produce a space with something in every room; and a first visit always quiet. Shallow coordinates are also capped below the top band regardless of wealth. **Stays in progress until inhabitants exist and the condition can actually be observed.** — **an acceptance condition on the whole generator, not a nice-to-have.** A high-tier coordinate that cannot be survived solo by building, supplying and finding a way out has failed this direction regardless of how good it looks. — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own condition.** It says it stays in progress *"until inhabitants exist and the condition can actually be observed"*. **Inhabitants exist** — twelve defs, wanderers through to the dead and the psychotic — and the three guarantees are constants in source rather than tuning: `MaxSimultaneousEncounters = 3`, half of every coordinate's rooms bare by count, and a quiet first visit. **So nothing buildable remains; what remains is watching it**, which is the owner's launch and belongs in the test phase rather than the working queue.

### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)

**Verbatim owner request (2026-09-29, seven items):** *"read Now. md and any and all revent prep docs as you continue the todo work and take not there is a mode .xlml like thing that im not sure is fully working i try to open it but its not human navigatable but its suppose to spreeadsheet out all the mods and potential uses and issues and theri uses and descriptions and shit if i remember correctly and you should definatly be using it and or fixing it up as you go along with build the Mod here and or update it where need of past work already done and continue it forward and making sure it is human havigate able becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"*

**Verbatim owner identification (2026-09-29):** *"Rimrooms_Async_Industries_294_Mod_Integration_Register this thing is what i was talking about"*

**Verbatim owner report (2026-09-29, the root cause):** *"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt??? wtf i thought it was the mod spreedsheeet! fix it"*

Full record in [`implementation/MOD_REGISTER_REBUILD.md`](implementation/MOD_REGISTER_REBUILD.md); the work-type findings it produced are in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md).



**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **The register opens without a repair prompt or a layout complaint** in whatever the owner actually uses. This is the one claim structural verification cannot make; it belongs to the post-completion test phase.

### Post-completion test phase — `[T]`, gates nothing

- [T] Runtime regression acceptance for these increments and their connected first-expedition loop, after the owner launches the disposable RimSort profile. *(master TODO §Earlier company/scenario increments)* — Needs, in the post-completion test phase: the owner's RimSort launch of the 295-entry product target (296 with the RimBridgeServer QA overlay attached afterward). Claude never starts RimWorld, never touches the active RimSort list, never attaches RimBridgeServer outside `research/RIMBRIDGE_TEST_HARNESS.md`.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **Every runtime acceptance row** across M1–M6 (Gate 2 onward), including the per-checkpoint acceptance lists at the foot of each implementation record. These feed the phase above. They gate nothing.

## TOMBSTONES

_(none)_
