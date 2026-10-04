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

- [ ] **"remember lsd unnerving feeling with all things"** — **the standing acceptance condition on every encounter, spawn and event**, in the owner's words. A spawn that is merely a hostile, or merely a neutral, is the thing being complained about. The uncanny is one exact wrong detail on something ordinary, and it must be **readable** — text, never atmosphere alone. — **MECHANISM BUILT AND ENFORCED 0.12.88-dev; **the row stays open because only a launch judges a feeling.** What exists now: a `tellKey` on all twelve inhabitant families and a `traceKey` on all eight events, both refused at load if absent, both read off the thing rather than out of a notification, and both held to *one exact wrong fact, never a mood adjective* by `proof-unnerving-register.py` — the rule taken straight out of `UNIVERSE_ADAPTATION.md`. `plant-unnerving-register.py` is **32 of 32**. **What it does not cover yet**, named rather than implied: loot and equipment carry no tell of their own, the room clue texts are still instructional rather than uncanny (deliberately — they teach the vertical slice and rewriting them would remove teaching the owner valued), and *"all things"* is open-ended by construction. This is an acceptance row like *"its suppose to be a lsd trip"* and it closes when the owner plays it, not when a checker passes.** — **THE OBJECT HALF LANDED 0.12.89-dev; **the row stays open because only a launch judges a feeling.** 0.12.88-dev reached people and events; this batch reached **objects**, which the owner had named specifically — *"items and equipment and production benches"*. Twenty object tells across nine classes, each one exact wrong fact read off the thing, held to the **same no-mood-adjective gate** taken from `UNIVERSE_ADAPTATION.md`, and kept to a small derived minority of placed objects so the quiet rooms stay quiet. `plant-unnerving-register.py` is **50 of 50**. **What *"all things"* still does not cover**, named rather than implied: the room clue texts are still instructional rather than uncanny, deliberately, because they teach the vertical slice and rewriting them would remove teaching the owner valued. This is an acceptance row like *"its suppose to be a lsd trip"* and it closes when the owner plays it.**

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
- [ ] **"my preparecarfully mod food did not appear"** — **STILL OPEN with the row below.** — same path. Prepare Carefully's equipment reaches the map through `ScenPart.PlayerStartingThings()`, which is the same enumeration the scenario grants use, so one break explains both halves of the original report. — **SAME PATH, SAME DIAGNOSTIC 0.12.91-dev. Prepare Carefully’s equipment reaches the map through `PlayerStartingThings()`, which is the same enumeration the scenario grants use — so one break explains both halves of the original report, exactly as this row says. **The new start report names this quarter explicitly**, so the next launch produces a log that either implicates it or clears it: the letter lists what the scenario promised and says that a mod supplying starting equipment is the most likely cause, with the request for the `Player.log`. The row stays open until that log exists.**

**Verbatim owner direction (2026-09-29), a crew left on the far side:** *"and remmebr turning off a company gate with pawns inside doesnt lose control of those pawns they have to survive till a reconnection is made so they can escape"*

- [ ] **"turning off a company gate with pawns inside doesnt lose control of those pawns"** - closing a gate on a crew **does not take them away from the player**. They stay the player's own pawns, under the player's own control, on the coordinate map.
- [ ] **"they have to survive till a reconnection is made"** - and now they are a survival problem. Food, warmth, injury, whatever is down there with them. The player plays them.
- [ ] **"so they can escape"** - reconnection or natural gates are the way out, and it is the player's to arrange from the near side. **Nothing here is timed** (`docs/CAMPAIGN_CHART.md` §1.1): a stranded crew is not on a countdown, they are simply somewhere hard.
- [ ] **What to verify before writing anything:** `Company/LostPawnRegister.cs` exists and the campaign calls `ExposeLostPawns()`. **The name is the thing to check.** If a closing gate hands its crew to the world-pawn pool, or despawns them, or marks them lost in any way that removes player control, that is a defect against this direction and the most consequential kind - it takes colonists away from somebody.

**Verbatim owner answer (2026-09-29), at the exit-route fork:** *"Two maps at start, coordinate is real (Recommended)"*

- [ ] **"Two maps at start, coordinate is real"** - the solo/group start generates **two** maps. The starting map is an ordinary surface map on the tile the player picked, holding a small concrete shell with one door in it. A **real Backrooms coordinate** is generated alongside, and the starting people and their supplies are put inside it before the player ever sees the surface. The exit is a genuine registered `Emergence` connection from the first tick.
- [ ] **This supersedes the earlier answer** *"Emerges on a fresh tile chosen by the seed"*, and the reason is a hard architectural constraint that was only found by reading `RimroomsPortalNetwork.Register`:
  - `Register` requires **`secondAnchor.Map.Parent as RimroomsDestinationMapParent`** with a matching `CoordinateRecord`. The Backrooms side of any connection must be a real coordinate map.
  - The solo/group start's map **cannot be one**, because `Game.InitNewGame` generates the starting map for a **player `Settlement`** world object and errors without one.
  - So 0.12.0-dev's design - *the starting map IS the coordinate* - is the thing that makes a registered exit impossible. Keeping it would have meant widening the validation that **every existing gate depends on**, which is the riskiest change available.
- [ ] **What this reworks from 0.12.0-dev:** `GenStep_InsideStart` and the `RR_InsideStart` map generator are **retired and archived**; the coordinate is generated by the existing `DestinationService.EnsureSite` through `GenStep_BackroomsDestination`, which is the proven path. `insideStart` stops meaning *"the starting map is a coordinate"* and starts meaning *"the starting people begin in a coordinate alongside the surface map"*.
- [ ] **The cost, stated plainly:** the surface tile is the one the player chose at setup rather than one derived from the seed. The owner took that trade knowingly at the fork.

**Verbatim owner direction (2026-09-29), constraining all of the above:** *"but remmebr this is all open eneded they can play how they choose"*

- [ ] **"this is all open eneded they can play how they choose"** - **the tutorial chain guides, it never rails.** This is the same rule `docs/CAMPAIGN_CHART.md` already holds the Async line to and it now governs the solo/group line too:
  - The exit is **guaranteed to exist**, and **using it is a choice**. A player who wants to live down there, dig, farm and never come out is playing the game correctly.
  - The depth-3 limit is a property of **natural portals**, not a gate on the player. It does not stop anybody doing anything; it only means the free doorways run out and a built gate is how you go further **if you want to go further**.
  - Nothing in the chain expires, nothing is failed by ignoring it, and every step offers more than one way through (chart #1.1 and #1.2, both already enforced by `check-campaign-absolutes.py`).
  - **The chain is a set of offers describing what is possible, not an order of operations.** If a player reaches the surface before anybody suggested it, the chain has to read as already-done rather than skipped.

**Verbatim owner answers (2026-09-29), at the exit fork:** *"Emerges on a fresh tile chosen by the seed"* / *"option 1 and the tutorial like quest chains should lay it all out"*

- [ ] **"option 1"** - natural portals reach **through depth 3**, then stop. Level 1 where they start, plus two more levels found by doorway. Past that, deeper requires a gate they built.

**Sequencing, decided rather than asked:** the bounded natural depth and the guaranteed exit ship together, because the exit is the load-bearing half of the direction and the depth cap is what gives it a point. The tutorial chain follows in its own checkpoint, because it needs a new field on the request shape and a second line of authored content, and rushing it behind the world-tile work is how a request line ends up teaching the wrong order.

## Pending


### Owner direction — the Operations panel is a text wall and has to become a utility (2026-10-04)

**Verbatim owner direction (2026-10-04):** *"and add to the todo we need to make the whole operations panel thing alot less of a text wall its like a fucking novel when it doesnt need to be for example one of many things that can be done and all things should be done to make it more of a utility, not  a text wall so that on the machine tab its shows the different systems with green and red lights of whether complete/active with a next step section showing what to do next  not every step having its own type up of whats next and things can be shortend and more concise and dirrect  with tools tips would less cluter it making them all concise and accurate, and all the tabs of operations are well designed for a tripple A Mod currently it looks like its all just text wall and shit, and everything that the machine needs to start up should be able to do in the worlkd from the devices themselfes with pawns controls and actrions not just in the opetaions tab,, ie setting the cordinace and all of those things need  to show and when u set a door to be a gatew  that gate should tell you next step in the game world not just in the operations tab and machine tab,, and we dont need things like long string corrdinates list in the operations panel thing like that arnet needed only like the !A-01 address code is needed to be displayed to thew player and save able and useable and gates need to be able to set up a max of three of them  so u can have three addrerss called at once wich would give 4 of 5 open maps,, and the closing of natural portals needs to be an option on the gate itself so pawns can close it with like 25 wood to board it up which makes it close its map freeing up a map from being open so others can be explored"*

**Eleven clauses, each its own row below.** This is the first direction in the project aimed squarely at the **UI as a product** rather than at a behaviour, and the owner's standard is explicit: *"well designed for a tripple A Mod"*.

- [ ] **"and gates need to be able to set up a max of three of them  so u can have three addrerss called at once wich would give 4 of 5 open maps"** — ~~three addresses held per gate~~ **CORRECTED BY THE OWNER, 2026-10-04, verbatim:** *"not three address per gate!!! up to three differnt operational gates that can call any address and we need a Random address option not just company requested task and quests at specific xcorrdinates"*.

  So: **up to three operational gates**, and **each one can call any address.** The cap is on gates, not on addresses, and there is no pairing between a gate and a place. The arithmetic the owner did is exactly that: three gates each holding one open coordinate, plus the colony, is **four of five** against `Portals/OpenMapBudget`, leaving one spare.

  **The wrong reading is struck rather than deleted.** I had started building a per-gate address cap off it; a correction nobody can see is a correction that gets made again.


### Owner direction — an LSD trip, not a grid: bent corridors, doors anywhere, and the hall is not always in the corner (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and make sure hallways and corradors and shit arent all straight.. its suppose to be a lsd trip when it comes to archeteture and shit, repeated patternes in variations, u -turns, multiple coices on directions to take in every rooms, non default fdoor possitions in rooms so doors are not just on each side, can have doors al over, and starting room is not to always be in bottom left of map, starts locations of main grand rooms can be anywhere on the map and lead anywhere in multiple differetn varied ways"*

**Extends the string-of-pearls direction below.** Three of these nine clauses were confirmed against the source within minutes, and **two of them are single literals** — this is not a design problem, it is hardcoded values nobody had questioned.

| Clause | Confirmed in code | Where |
|---|---|---|
| *"starting room is not to always be in bottom left of map"* | **`var hallFirst = new IntVec2(0, 0); var hallSecond = new IntVec2(1, 0);`** — and `SlotCenter(0) = Margin + spacing / 2`, the lowest cell on both axes. **Every coordinate ever generated puts the grand hall in the same corner.** | `RoomLayoutPlanner.BuildMaze:650-651` |
| *"hallways and corradors and shit arent all straight"* | `if (first.CenterCell.z == second.CenterCell.z)` then a single `for (int x = fromX; x <= toX; x++)` run at a fixed `centerZ`. **One axis, no bend, by construction** — and `AreNeighbourRooms` *requires* linked centres to share a row or column, so a bent corridor is currently illegal rather than merely absent. | `GenStep_BackroomsDestination.BuildCorridors:979-986` |
| *"non default fdoor possitions in rooms so doors are not just on each side"* | `DoorOpening` opens a wall cell only where `cell.z == room.Bounds.CenterCell.z` or `cell.x == room.Bounds.CenterCell.x` — **the exact midpoint of each of the four walls.** `FalseOpening` adds one more at a third along a wall with no link behind it, and that is the only non-midpoint opening that exists. | `RoomLayoutPlanner.DoorOpening:1261-1282` |


- [ ] **"its suppose to be a lsd trip when it comes to archeteture and shit"** — the acceptance condition on the whole generator, in the owner's words. Recognisable, then wrong, then wronger.

- [ ] **"starts locations of main grand rooms can be anywhere on the map and lead anywhere in multiple differetn varied ways"** — plural **"rooms"**: more than one grand room, placed anywhere, each with several ways out. Today there is exactly one hall, it takes two slots, and `MakeHall` is the only caller — so "grand rooms" plural is new content as well as new placement.

### Owner direction — the mod's own menu images belong on the loading screens too (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and anothert thing.. we properly use the main menu images we made for the mod on the main menu page but i dont think we properly did the same for loading screens and the like add this to the todo"*

**Verbatim owner direction (2026-10-03), the shape of it:** *"so we need those mod images made for the menu to also use them randomly for load screen backgrounds"*

### Owner direction — tell the player the freeze is coming, in the universe's own voice (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and another thing when first loading a new backrooms on gate enter and or using the operations tab machine when finally opening the gate(loading the backrooms) we need a popup and notice in that portion of the machine gate connection step that pops up befgore the "freeze" of the generation telling the player "Time has froze due to mass distortions, please wait" but noit that i want u to make a universe of backrooms themed notcie of the pause that is expected and propely keep it toned to the experience we are trying to make per scenrio type this needs to be added to todo work"*

**This is a real freeze and it is unavoidable, which is exactly why it needs saying.** `GenStep_BackroomsDestination` carves a 300×300 map — rooms, corridors, pillars, rock intrusions, ore, fixtures, lights, power — inside Core's map generation, which runs on the main thread with no progress surface. The player gets a hung window and no idea whether the game died. **An unexplained freeze reads as a crash; an explained one reads as the setting.**
- [ ] **"when first loading a new backrooms on gate enter and or using the operations tab machine when finally opening the gate(loading the backrooms)"** — **both entry points**, named separately because they are different code: crossing in through a gate, and opening the gate from the Operations pane. Whichever the player used, the notice comes from the same place so the two cannot drift. — **PARTLY CLOSED 0.12.83-dev, and **the Operations pane half is done**: both of its openings — the laboratory address and a natural doorway — announce before the freeze. `OperationsPortalNetwork`. **The gate-enter half is genuinely different code and is recorded rather than claimed**: a pawn walking through is a job tick, and `GateSpinUp` reaches `EnsureSite` from a tick as well. A tick cannot queue a long event and then carry on, so that path needs the result chain deferred — the same refactor the row below names.**

### Owner answers at three forks — don't limit yourself, expand it in an LSD way, 3× vanilla ore (2026-10-03)

Asked because each one changes what gets built, and all three were answered as *more* rather than as a choice between options.

**Verbatim owner answer (2026-10-03), on the degree ceiling:** *"it shouldnt just be one option there needs to be wide varying variations of all types so dont limit yourself"*
- [ ] **"so dont limit yourself"** — recorded as the standing instruction it is. Where a bound exists it has to be a bound the geometry imposes and is **stated**, not a bound chosen for convenience. `MaximumUndirectedEdgesPerRoom` is the live example: it was 2 *"because a slot has four neighbours"*, and when bends made eight neighbours reachable the constant was the thing refusing them.

### Owner direction — it is STILL a string of pearls, fill the space, and the rock has to be worth mining (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and another thing to add to todo( the backrooms is still incorrectly too much having the rooms like a string of pearls where the rooms are just one exit one entrance. this is not the backrooms universe MAZES!!!! room connected to like 0 - 10 other rooms and not have so much empty rock space where nothing exists. it looks too much like are long series connection of drooms, DO YOU UNDERSTAND WHAT A MAZE MEANS AND TO FILL THE SPACE WITH ROOMS and where there is mountain walls and no rooms areas minable need to have resources that you can mine like steel gold plasteel, gems, all of them, even underground resources that u can use deep drill with and chemfuel, and im reiterating the fact that we need to fix the depancy list so that its accurate to what is required and we hope to have the mod as a complete stand alone"*

> **⛔ THIS DIRECTION CONTRADICTS WHAT WAS REPORTED TO THE OWNER EARLIER THE SAME DAY, AND THE OWNER IS THE ONE WHO SAW IT RUN.** The 2026-10-03 adjudication pass closed *"all the backrooms so far are just one lone strain of perals arangement"* and *"it needs to be more maze liek"* as **built**, citing `RoomLayoutPlanner.BuildMaze` and `BraidRarity`. The owner has now walked it and says it is **still a string of pearls with one entrance and one exit per room**. Source-presence was read as behaviour, which is the exact mistake this repo keeps naming.

**MEASURED 2026-10-03, and the first hypothesis was WRONG — recorded rather than quietly replaced.** The guess was that `TrySelect`'s three maze candidates were being refused and every level was silently getting `BuildSerpentine`, the way it had before. **`fellback 0` at every depth across 200 seeds: the maze IS selected.** The string-of-pearls look has a different and more fundamental cause, and it took extending the probe to see it, because **checker 14 could not measure the complaint**: every column it reported was about whether a layout is *legal*, and none about whether it reads as a maze. Degree and fill columns were added to `.local/harness/PlannerProbe/Program.cs` for this.

| depth | avg degree | max degree | deg 0 | deg 1 | roomfill of 300×300 |
|---|---|---|---|---|---|
| 1 | **2.39** | **4** | 0.0% | 6.5% | 46.0% |
| 2 | 2.41 | 4 | 0.0% | 7.3% | 42.4% |
| 3 | 2.40 | 4 | 0.0% | 5.0% | 38.7% |
| 4 | 2.23 | 4 | 0.0% | 4.6% | 27.1% |
| 5 / 6 / 8 | **2.20** | **4** | 0.0% | 4.0% | **17.1%** |

**What the numbers say, clause by clause:**
- *"the rooms are just one exit one entrance"* — **confirmed exactly.** An average degree of **2.2 to 2.4** means the typical room has two links: one in, one out. That is a corridor with rooms on it, which is what a string of pearls is. The braid is contributing only ~0.4 above the spanning tree's 2.0, so `BraidRarity = 3` is far too sparse to read as a maze.
- *"room connected to like 0 - 10 other rooms"* — **structurally unreachable today, and this is the architectural finding.** Max degree is **4** at every depth, because every link must join **grid-adjacent slots**: `AreNeighbourRooms` requires linked centres to share a row or column and `BuildCorridors` carves straight between them, so a slot has at most four orthogonal neighbours. **Reaching 10 requires links that are not grid-adjacent**, which means corridors that bend — a change to the corridor carver and to `ValidateRooms`, not a tuning of the braid. `deg 0` is 0.0% as well, so the owner's explicit *"0"* case does not occur at all.
- *"not have so much empty rock space where nothing exists"* / *"FILL THE SPACE WITH ROOMS"* — **confirmed, and it gets worse the deeper you go, which is backwards.** Rooms occupy **46%** of a depth-1 map and only **17%** by depth 5. The cause is arithmetic: slots rise 6×6 → 10×10 while `VariedRoomSpan` shrinks 34 → 16, so area per room falls faster than room count rises, and `MaxRooms = 60` caps the count before it can compensate. **83% of a deep coordinate is uncarved rock** — which is also exactly the space the ore clauses below want to make worth digging.

`python tools/check-planner-layouts.py` runs this; the `maze` line beside each depth is the new measurement and is how any fix gets confirmed.

- [ ] **"this is not the backrooms universe MAZES!!!!"** — the acceptance condition on the whole layout, in the owner's own words.
- [ ] **"im reiterating the fact that we need to fix the depancy list so that its accurate to what is required and we hope to have the mod as a complete stand alone"** — **a REITERATION of the 2026-10-03 direction** *"rework mod to not need any depeancie mods"*, and it adds the goal in plain words: **a complete stand-alone mod.** Tracked under *Owner direction — the mod must not need any dependency mods*; recorded here too because the owner said it again and LAW #0 does not let a repeat be dropped as redundant. — **PARTLY CLOSED 0.12.86-dev, and the two clauses of this reiteration land differently. *"fix the depancy list so that its accurate to what is required"* **is done**: the 293 hard `modDependencies` are gone and `loadAfter` carries the 294-row profile, which is accurate — the assembly references `Assembly-CSharp` and three UnityEngine modules and nothing else. *"we hope to have the mod as a complete stand alone"* **is not**, and removing a declaration does not make absence safe; it only stops advertising. The row below names what is left and this one stays open until it closes.**

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

- [ ] **"rework mod to not need any depeancie mods"** — **the guarantee half, and THIS is the *"major major work"* the owner means.** Removing a declaration does not make absence safe; it only stops advertising. What has to be proven, row by row, is that the Core-only path **runs**: every by-name `GetNamedSilentFail` lookup degrades rather than returning null into a dereference; both `Patches/` `PatchOperation`s stay guarded by `PatchOperationFindMod` / `PatchOperationConditional` so an absent target applies nothing (invariant 42); and no Def, scenario grant, recipe, archetype slot or keyed string silently assumes a DLC or profile def exists. `ARCHITECTURE.md` currently states the guards exist *"so an absent one degrades instead of throwing, **not** to advertise that absence is supported"* — that sentence is the gap this row closes. — **STILL OPEN, and the declaration half landing at 0.12.86-dev **does not touch it.** What has to be proved row by row is unchanged: every by-name `GetNamedSilentFail` degrades rather than returning null into a dereference; both `Patches/` operations stay guarded by `PatchOperationFindMod` / `PatchOperationConditional` so an absent target applies nothing (invariant 42); and no Def, scenario grant, recipe, archetype slot or keyed string silently assumes a DLC or profile def exists. **`ARCHITECTURE.md` now says so in the same sentence as the change** — the DLC line reads *"that is still not a claim that absence is supported"* — so the document no longer implies this row is covered by the deletion.**
- [T] **Core-only startup actually observed.** The audit above closes on source evidence; a clean Core-only load with zero red errors is a launch, and only the owner launches. Post-completion test phase, gates nothing.

### Open rows carried out of the play-testing checkpoints (2026-09-30 to 2026-10-01)

**Lifted here 2026-10-02 by owner direction:** *"we need to move all finished items to finalized.md from the todo, the todods sahll never hold completed items, they are always to be moved to finalized first then deleted from the todods once confirmed virbatium transfer"* and, on being shown the queue still at ~96 KB, *"BEcause the todos are still like 100kb and i know that not all unfinished work and only unfinished work like it shall be"*.

Nine `##` sections titled as dated checkpoint records held **20.9 KB** between them, most of it the finished write-up of a launch or a rebuild stage, with these open rows buried inside. **A section called "Fifth launch findings - 2026-09-30" is a thing that happened, not a thing to do.** Each section is archived whole in `FINALIZED.md`, record intact; every open row it held is below, verbatim, tagged with the checkpoint it came out of.

**1 row(s) repeated verbatim across checkpoints and are carried once.** The same open item written three times is one open item; the repeats are named in the archive rather than dropped silently.

**From `## Fifth launch findings — 2026-09-30`:**

- [ ] **"and everything doesnt have to be square rooms and rectangle halways and u can use walls as pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms and this can propigate depper with the wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches that are found everywher deeper in with wild random events and layouts and spawns to find and loot!!!!!!"** — **OPEN. This REVISES the room-count answer given an hour earlier and it is the better call.** Taken apart into what each clause actually requires:

  | Clause, verbatim | What it means in the generator |
  |---|---|
  | *"everything doesnt have to be square rooms and rectangle halways"* | a room's `Bounds` stays a rect for bookkeeping, but the **carved shape** does not: L, T, cross and ragged-edged rooms, and corridors that change width and bend |
  | *"u can use walls as pillars"* | interior `ThingDefOf.Wall` on a support lattice. **This is the thing that makes grand spaces possible at all** — `RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**, so a roofed span wider than ~13 cells needs something holding it up, and a pillar is exactly that |
  | *"making the 0 level rooms be grand large spaces"* | shallow depth is **few, very large, pillared halls** — not the tidy 10-16 cell boxes the planner builds today |
  | *"leas than 60-100 romms"* | **supersedes the 60-100 dense-warren answer.** Fewer rooms, each far bigger. The warren idea moves inward rather than being dropped |
  | *"this can propigate depper"* | the variation is a **function of depth**, which `BackroomsPalette` and `Derange` already are. Same axis, more of it |
  | *"wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches"* | `CoordinateMaterials` already picks stuff per coordinate; widen it across **every** placed category and let the spread grow with depth |
  | *"found everywher deeper in"* | material variety is discovered content, so what a room is **built from** is part of the loot |
  | *"with wild random events and layouts and spawns to find and loot!!!!!!"* | `AnomalyEventService`, `InhabitantService` and `RoomArchetypeService` all exist; the layouts and the loot density scale inward with the rest |

  **What stands from the four earlier answers:** levels are **300x300**; `threshold_room` / `office_copy` / `return_gallery` stay **unique** while other families **repeat**; **new structural families** are authored as layout and dressing only with **no new ThingDefs**; **4-6 onward gates** per level with `MaximumNaturalDepth` **3 to 6**; **fresh save**, the 60x60 path dropped.

  **What changes:** *"leas than 60-100 romms"* replaces the 60-100 count, and grand pillared halls at shallow depth replace the uniform small-room grid. The 10x10 planning grid at 19-cell spacing was sized for the old shape and is superseded with it — a grand hall does not fit in a 19-cell slot.

- [ ] **SUPERSEDED IN PART, same day, by the row above** -- the *"leas than 60-100 romms"* direction replaces this row's 60-100 count and its uniform small-room grid. Kept whole because the size, family, gate-count, depth-cap and save decisions in it all still stand.

- [ ] **"theri 300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels with thir natual gate spawns to different levels within"** — **OPEN, and fully specified by the owner across four questions this checkpoint.** Levels become **300×300** (from 60×60); **60–100 rooms** in a dense warren on a **10×10** planning grid at the existing 19-cell spacing; **threshold_room / office_copy / return_gallery stay unique**, the other five families **repeat**, and **new structural families** are authored (flooded_room, stairwell, dead_end, pillar_hall) — **layout and dressing only, no new ThingDefs**; **4–6 onward gates per level**, one per ~15 rooms, with `MaximumNaturalDepth` **3 → 6**; and a **fresh save**, dropping the 60×60 path entirely for one shape, the simplest code and the cleanest proofs.

**From `## Coordinate rebuild, stage one — 2026-09-30 (0.12.49-dev)`:**

- [ ] **"dont let them go more than 5 remember the games mechanics and limits built in if they find a gate to a world map tile or a deeper backrroms and they have 5 mpas they should gett a warning this gate is blocked your holding open too many gates, but per scerio styled"**, clarified by **"5 is the limit of other colonies available so a backrooms level should be one colonly bacskicly in my thinking"** — **OPEN, stage two, and it SUPERSEDES the LRU-eviction answer given minutes earlier.**

  A hard cap with **no eviction** is strictly better: nothing the player looted or built ever resets, memory is bounded by construction, and the limit is **diegetic** rather than an apology about memory.

  **And the owner's clarification grounds the number in Core.** `Prefs.MaxNumberOfPlayerSettlements` is a player option, a slider from **1 to 5, default 5**, enforced by `SettleUtility` as `count >= Prefs.MaxNumberOfPlayerSettlements`. Core counts only `map.IsPlayerHome && map.Parent is Settlement` plus gravship landings, so a `RimroomsDestinationMapParent` is **invisible to it**. So the budget is read from that pref rather than hard-coded, and a coordinate map counts against it — *"a backrooms level should be one colonly bacskicly"*. A player who sets the slider to 3 gets 3.

  *"per scerio styled"* means the budget belongs on the scenario, not a global constant.

  **This ships together with raising onward gates to 4-6 and `MaximumNaturalDepth` 3 to 6**, because the cap without the gates is pointless and the gates without the cap is what kills the game: `RimroomsDestinationMapParent.ShouldRemoveMapNow` always returns false, so at 90,000 cells and ~70,000 mineables per level, hundreds of reachable levels against a `MaximumCoordinates` of 512 would be fatal.


**From `## Coordinate rebuild, stages two to four — 2026-09-30 (0.12.50-dev)`:**

- [ ] **"how do they turn them off to use the machine gates for more controll and aiming deeper?"** / **"get 5 natural gates u cant use a machine gate"** — **OPEN, and deliberately NOT half-built. Next checkpoint, first thing.** The owner chose an **Operations held-places list with Release**. Releasing a place is not a UI problem; it needs (1) a **save-schema field on `CoordinateRecord`**, because `EnsureSite` deliberately refuses to regenerate a coordinate whose rooms were surveyed and only a flag can distinguish a deliberate release from a broken reference; (2) map teardown that orphans neither the world object, the `Site` reference, nor a portal edge pointing in; (3) a refusal set — crew present, crossing in flight, or the headquarters. Getting any of those wrong produces an unreachable place or a dead record, which is the exact defect class that cost thirty-nine checkpoints. **Mitigation meanwhile: discovering gates is free** — no map is generated until somebody crosses — so the cap is only met after five places are held open.


**From `## The first walked level — 2026-09-30 (0.12.61-dev) — DONE`:**

**Adjudicated against the source 2026-10-03.** The section title was never the marker, per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`: *"A section titled DONE whose rows are still `[ ]` does not move. The title is not the marker."* So each row below was read against the code rather than promoted on the heading's word. **Eleven of the twelve were built and nobody had ticked them.** `RoomLayoutPlanner.cs` (1,351 lines) and `RoomArchetypeService.cs` (392) were read in full; `RoomContentBuilder.cs`, `BackroomsPalette.cs`, `GuaranteedFrontiers.cs` and the four Def folders were read at the named sites. **Register checked:** `python tools/register-query.py trace RR-SPACE` → 15 rows, Core *Required* and the rest *Optional* / *Configuration only* / *No integration*; none applied, because this pass changes no code.












- [T] **"there is a weird route thing name a self in one of the rooms and this is kinda weird and odd"** — owner's own read: *"we probably havent gotten to a routing system yet for emergency exit and glow pods with the company start but lets try and fix this"* — **THE STATED CAUSE IS ANSWERED AND THE SIGHTING IS NOT, so this is the one row of the twelve that moves to the test phase rather than closing.** The routing system the owner supposed was missing **exists**: `CompRimroomsMarker` with five `RimroomsMarkerTypeDefs` — `RR_Marker_Route` labelled *"route home"*, plus `_Cleared`, `_Danger`, `_Cache`, `_Lead` — numbered through `FirstSliceSiteComponent.NextMarkerNumber`, and the survey tag is a Core `GlowPod` since 0.10.7-dev. **But markers are player-deployed, so a freshly generated level should carry none**, and **what the owner actually saw cannot be identified from here** — naming it needs somebody looking at the object on a map. Deliberately not guessed: editing a label on a hunch is the same move that lost three launches in one method.

**From `## Lights and geometry — 2026-09-30 (0.12.61-dev) — DONE`:**

**Adjudicated against the source 2026-10-03, same pass as the section above.** **All ten were built and none had been ticked.** Seven of them are implemented by one function, `RoomLayoutPlanner.RockIntrusionCells`, whose seven forms exist precisely because of these rows.











**From `## The lab name comes out, and every level becomes a maze - 2026-10-01 (0.12.68-dev, 0.12.69-dev) - DONE`:**

- [~] **"all the backrooms so far are just one lone strain of perals arangement that snakes back
  and forth across the map like one series line"** - **the owner is describing the algorithm
  exactly.** `RoomLayoutPlanner.Build` walks the slot grid row-major with alternating direction
  and calls it a *serpentine*; it is one line that snakes, by construction

### Major M1 — Connected colony portals (ROADMAP M1; master TODO §Native-provider foundation — 0.4.0-dev)

Binding contract: [`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md). Baseline commit `8ed4e32`, 0.4.1-dev, 75 C# files, 71 package files, zero warnings/errors. Read `implementation/CONNECTED_COLONY_CHECKPOINT.md`, `CONNECTED_COLONY_IMPLEMENTATION_TASK.md`, `CONNECTED_NETWORK_IMPLEMENTATION.md`, `CONNECTED_CROSSING_IMPLEMENTATION.md`, `CONNECTED_WORK_CORE_API.md`, `CONNECTED_PORTAL_STATE_MIGRATION.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md` before editing `src/RimroomsAsyncIndustries/Portals/` or `Gate/`. Source fact: nothing in the repo calls `RimroomsPortalNetwork.Register`, `PortalCrossingService.Cross`/`Recover`, or `CompRimroomsGate.BeginPortalOpening` yet.

**Master TODO items (verbatim):**

- [~] Implement every open item in [connected colony portals](CONNECTED_COLONY_PORTALS.md#required-implementation-backlog): independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants/complexity. This supersedes dispatch-only travel as the target. — **PARTLY BUILT**; what shipped is archived. **Open:** the individual routes listed below.

**Resume order (verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`; these are the working sequence for the items above):**

- [~] **Resume step 4:** "Implement saved work intents, quantity leases and native destination job revalidation; then physical hauling, construction, bills, research, medical/food/bed and other work/needs families. Preserve priorities, schedules, areas, locks, custody and actual inventory. A generic graph does not implement these adapters."
  - [~] The remaining work/needs families, and every installed work giver in the 294-row profile. **Next (2026-09-29):** cleaning, repair, firefighting, plants/mining/hunting, prisoner and guest care, wardening, childcare, animals and mechs, refuel and rearm, joy, rituals, hauling providers. Expect most to be short: the deployment shape covers anything done at the far site, and the carry shape covers anything delivered. Read the relevant profile rows for each before writing. — **31 families built, 23 of them deployments; every Core and DLC work type is covered or decided against with its reason recorded. Six build passes archived.** **ONLY REMAINDER: a mod-added work type with its own givers.** The bill family covers modded *benches* inside existing work types automatically, but a wholly new work type gets no provider, because the providers and their giver defs are shipped rather than derived — and it cannot be built against a mod nobody has named. Coverage: [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md), 23 work types, 145 giver defs.

**This row does NOT close on completeness.** The remembered list above was checked against the shipped game data and found **incomplete**: it omitted `DarkStudy` and `Fishing` entirely, and both are real work types with no mention anywhere in the mod's source. The enumeration is in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md) — 23 work types, 145 giver defs, coverage read out of the mod's own source. Four genuine gaps remain, recorded below as new rows because this is new information rather than a restatement.

- [~] **Resume step 5:** "Integrate exact optional work/storage providers and scenario openings, then procedural inhabitants, rare monstrosities, saved events and tech-driven complexity. Keep every wider master TODO feature in scope." — **Open:** optional provider adapters, on their own row below. (Scenario openings closed; archived.)
- [~] **Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change." — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`. — **Open and structurally must stay open:** runtime acceptance, because only the owner launches.

**Required implementation backlog (verbatim from `CONNECTED_COLONY_PORTALS.md`; the acceptance list the majors above must satisfy):**

- [~] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions. *(source partially complete in 0.5.0-dev: discovery, destination targets, bounded routing, planning leases and real native destination reservations exist and are proven for the storage-hauling family only; the other families are not implemented and runtime acceptance is open)*
- [ ] Implement connected-site scheduling/streaming and measure performance after an owner-launched build. — **STILL OPEN.** Scheduling and streaming ship. **Measuring performance requires an owner-launched build, which is the one thing this project cannot do for itself.**
- [T] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants. — post-completion test phase (owner RimSort launch).

**Task-record subitems still open (verbatim from `implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md`):**

- [~] Optional profile interfaces and native priority/schedule/restriction coverage. — **Open:** the optional provider interfaces, on their own row below. (Native priority, schedule and restriction handling closed; archived.)
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

### The site

- [ ] **A real domain, not a `github.io` path.** *"a nice backrooms url"*. This needs a domain the owner controls plus a `CNAME` file in the Pages branch and DNS records pointing at GitHub. **The domain is the owner's to choose and register** - ask before building the Pages config, because a custom domain and a project-path deploy are configured differently and the wrong one means rebuilding. — **SUPPORT AUTHORED 0.12.92-dev, DOMAIN STILL THE OWNER’S TO BUY. `docs/CNAME.example` has the DNS records, the copy step and the verification, and the site needs **no page edits** when the domain arrives because nothing hard-codes its own address. The row stays open because the thing it asks for is a domain, and naming one this repository does not serve is the specific failure the row’s sibling forbids.** — **RE-AIMED 0.12.94-dev AT THE PUBLIC REPOSITORY, STILL THE OWNER’S TO BUY. The domain now belongs to `G-Fourteen/Rimrooms-AsyncIndustries`, which is the only thing that deploys. `CNAME.example` carries the DNS records, the copy step and the `curl -sI` verification, and **the export needs no page edits when the domain arrives** because nothing in the rendered site hard-codes its own address — every link is relative. The row stays open because the thing it asks for is a domain.**

### The Steam Workshop

- [ ] **The mod page write-up**, linking to the site.
- [ ] **The collection**, with its own write-up, linking to the mod page and the site.
- [ ] **Both written from the same source as the site**, so three descriptions of one mod cannot disagree.
- [ ] **Owner idea, verbatim:** *"idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"* - Playwright driving the Steam Workshop UI. **Ask before doing this**: it means automating an authenticated session on the owner's Steam account, which is a different kind of action from anything done so far and needs explicit permission, not an assumption. The alternative is a prepared write-up the owner pastes, which is far less work for whoever is not doing the clicking.

### Standing constraints that still apply

- **No Claude attribution** in any of it - site, Workshop page, collection write-up.
- **The owner alone launches, sorts and publishes.** Deployment of a site is not the same act as launching the game, but the Workshop is the owner's account and the owner's decision.


**Verbatim owner directions:** *"go ahead with now.md protocol and get ready form compact with creating the handoff before i compact"*, *"ask me the question remebr i said sooner than later with those"*, *"that means asap"*.

- [ ] **NEXT: build the recorder fold.** Four live read sites move onto the book.

**Built 2026-09-29, 0.12.14-dev: the queue could not answer the question.**

## Owner decisions, 2026-09-29 — the three reserved questions answered, and one I should never have asked

**Verbatim owner correction:** *"wtf are you talking about core only we have 294 recommend mods you fuck!!!!"*


**Q4 — how far the public release goes. ANSWERED: everything, including Playwright driving Steam.**

- [ ] Repo, site and the Steam Workshop page driven through Playwright. **The concern was stated plainly before the choice was made and the owner chose this option anyway**, which makes it an informed decision and it stands. Recorded here so the decision is not re-litigated at the release checkpoint. Still correctly **last** in the queue, and it needs the owner present for the Steam session.

---

## Owner directions recorded late

These three were **acted on correctly and recorded in `NOW.md` or `FINALIZED.md`, but never
written into this queue as tasks**. The owner noticed the gap on 2026-09-29 and was right.
They are recorded here verbatim now, and `check-doc-conformance.py` refuses from this point
on to let a direction reach `FINALIZED.md` without appearing here first.

**Verbatim owner direction (2026-09-29), on the glow pods:** *"tyhe glow pods can be used and lets not limit the amount as a backrooms instance can have 100s of rooms if the player is using 300x300 maps for instance and maybe lets have the glow pods color setable"* and *"color means differnt types of the needs markers"*

**Owner answers on the field kit, asked at the fork:**

- **Survey tag → Core `GlowPod`.** Minifiable, carried, deployed, and it lights the room it marks. *"place one per room you clear, room is lit AND numbered."* **BUILT 0.10.7-dev.**
- **Return beacon → dropped.** *"the gate IS the beacon"* — the address book and the saved return threshold already do its job. **DONE 0.9.9-dev.**
- **Sealed evidence case → a designated headquarters shelf is the archive.** The book is carried and custody completes when it reaches a Core `Shelf` designated as the evidence archive, the same designation pattern as the gate console and the laboratory bench.
- **Field recorder → the book is the recorder.** One Core `TextBook`: carried in blank, written in the field, carried home as the evidence. *"lose the book, lose the run."*


- [ ] **Migration decision or declared development-save break** before removing any Def a saved `Thing` references, with the old build preserved. Shares saved keys with the portal legacy-threshold repair built in step 2 — decide them together. — **NO DECISION IS NEEDED YET, AND THE CANDIDATE LIST IS NOW MEASURED RATHER THAN OPEN-ENDED, 0.12.93-dev. The row fires *"before removing any Def a saved `Thing` references"* — and **nothing is being removed.** The five `RR_*Staff` PawnKinds were the other half of this cluster and they are **kept and wired**, not retired, so the save-break risk the row guards against does not arise from them at all. The one remaining candidate is the hidden legacy analysis bench, and `SAVE_MIGRATION_POLICY.md` already records its terms in the file: new starts do not spawn it, it cannot be built, company jobs do not use it, and *"final removal still requires migration or the explicit development-save boundary"*. **The row stays open because the decision is the owner’s and it is blocking nothing being built** — a save break is a decision about other people’s games, and per the M6 answer there are none yet: *"we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*. It becomes a real question the first time a removal is actually proposed, and none is.**

### Phase 1 leftovers (master TODO §Phase 1 — repository, build, and content foundations)

- [T] Define RimSort-managed test profiles: preserve the 295-entry product target (the existing 294 plus Rimrooms), then record RimBridgeServer as a separate QA overlay (normally 296 loaded entries). RimSort owns sorting, saving mod lists, and every launch; the owner starts sessions through RimSort. Do not add direct RimWorld or GABS launch profiles or remove target mods to offset the bridge. — post-completion test phase (owner-operated RimSort action).
- [T] After the first owner-launched full-target startup, collect matched Core/profile performance baselines on RR-DEV-01 and implement any missing counters per the [benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Enforce the recorded budgets before promoting features or larger room/map bands. — post-completion test phase (owner RimSort launch).

### Phase 2 — code architecture and safe vertical slice (master TODO; source largely present per `implementation/PHASE_2_BUILD_RECORD.md`, full stated scope + Gate 2 acceptance still open)

**Vertical slice implementation:**

- [T] Save, reload, revisit the same coordinate, and confirm map state and unique rewards persist without duplication. — post-completion test phase (owner RimSort launch).

**Gate 2 passes when** (master TODO): "the first complete loop plays from a fresh save through build, staff, expedition, extraction, analysis, reward, save/reload, and a second visit without a softlock or lost state." — owner-launched only.

### Major M3 — Phase 3 interconnected company simulation (ROADMAP M3; master TODO §Phase 3)

**Scenario framework and alternate starts** (contract: [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md); owner questions still open: inside-start party size; first-exit fixed vs chosen):

- [ ] Add outpost, town-distortion, or company-in-crisis starts only after a design brief defines their starting state, pressure, failure/recovery, and acceptance evidence. — **Still open, and correctly gated on its own condition:** no design brief exists. Three starts ship. **This needs an owner decision before it is work at all.**
- [T] Verify every start's reload behavior, deterministic coordinate, objective idempotency, optional-DLC fallback, solo behavior, and RWT eligibility against `SCENARIOS.md`. — post-completion test phase (owner RimSort launch).

**Procedural sites and propagation** (contract: [`PROCEDURAL_SPACE_CONTRACT.md`](PROCEDURAL_SPACE_CONTRACT.md)):

- [~] Bound active map count, pawn/thing count, graph search, event evaluation, and background tick cost; profile large, long-running saves. — **Bounding is done; profiling is not and cannot be.** Every scan in `ConnectedWork/` is a bounded rotating window, never a prefix (invariant 5), with roughly thirty `Maximum*` scan budgets. **Profiling a long-running save requires launching the game, which only the owner does.**

**Research, entity, and expansion progression** (owner S1/B: broad threat families only; the five named sketches in `CAMPAIGN_ROSTER_FREEZE.md` stay deferred until approved):

- [~] Author entity/anomaly design sheets first: appearance/readability, AI rules, triggers, limits, interaction, tells, counters, evidence, study risk, capture/storage, sale value, and fail states. — **Partly built.** Inhabitant defs carry AI rules, bands, tells and counters, and the escalation ladder is bounded. **Not built as authored design documents**, and the `RR_QuietPursuer` presentation is still the last open existing-content replacement.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [~] Research IDs across tiers T0–T6 and the nine branches; entity family sheets (broad families only per S1/B). — **Tiers 0–2 complete across seven branches; T3 is the next checkpoint.** The eighth branch (transport and orbital) has **no tier 0 at all, deliberately**, and the tree is derived rather than declared, so a tier number is not a promise of a linear chain. — **MEASURED 0.12.92-dev AND THE ROW WAS WRONG ABOUT T3. It says *"Tiers 0–2 complete across seven branches; T3 is the next checkpoint"*. **T3 is fully built** — seven projects, one per branch, each requiring its tier-2 sibling plus three route, two distortion and one entity log, with its own header at `RR_CompanyProjects.xml` line 418 and a record in `BUILD_ORDER_CORRECTION.md`. **T4 is built too**, six of seven, and both absences are reasoned in the file: Logistics has no tier 4 because lead time, dispatch delay, order capacity and unattended delivery are already taken by tiers 1, 2, 0 and 3, and what remains in Procurement is safety bounds no player will ever reach — *"a project here would promise something and change nothing, which is exactly what 0.12.5-dev deleted four projects for"*. The gate line has none and cannot: there is nothing above indefinite. **And the tier system is measurably healthy: 34 capabilities granted, 34 read, a perfect bijection** — no hollow unlock and no dead read. **So what is actually open is T5 and T6**, and the file’s own rule makes that a knob sweep rather than an authoring job: a tier may only exist where an unclaimed, player-noticeable knob does. 274 tunable constants exist and 34 are claimed, so the sweep has somewhere to look — but deciding which of the remainder a player could *name the effect of* is the work, and inventing seven projects without it would ship exactly the lie the file deletes projects for.**
- [~] Containment, interviews, settlement openings, outposts, vehicles, VGE hooks. — **Open:** containment, vehicles and the VGE hooks, each listed individually above. (Settlement openings and outposts closed 0.12.13-dev; interviews closed 0.12.28-dev; archived.) — **CONTAINMENT CLOSED 0.12.90-dev — it is one of the four dispositions on the choices row above, with a daily charge on its own ledger line and a way out that pays nothing. **The row stays `[~]` because vehicles and the VGE hooks are still open and still on their own rows**, and nothing in this batch touched either.**

### Major M4 — Phase 4 multiplayer, DLC, and the full profile (ROADMAP M4; master TODO §Phase 4)

Every item in this major needs a Rimrooms build the owner has launched; source-side preparation (feature detection, guards, adapters) can proceed, verification cannot.

**RimWorld Together adapter** (pinned release 26.8.31.1; no supported client extension API identified 2026-09-27):

- [T] Verify guild identity, facility mapping, configured visits/snapshot behavior, visits when online/offline, transfer spot, chill/defense spots, caravan interactions, events, sites, roads, aid, gifts, and trading. — post-completion test phase (owner-launched two-client run).
- [T] Verify transfer receipt IDs and item/pawn state prevent duplicates, loss, stale ownership, and broken stacks on disconnect/reconnect. — post-completion test phase (owner-launched two-client run).
- [T] Verify Backrooms Research Dossier item transfer; receiving branch must explicitly study it locally and be unable to claim it twice in one save. — post-completion test phase (owner-launched two-client run); dossier binds to an existing physical document object per the content-reuse rule.
- [T] Test unsupported/complex modded items and define an honest fallback message rather than promising an unverified transfer. — post-completion test phase (owner-launched two-client run).
- [T] Test separate colony saves, shared world actions, mod order/config enforcement, RWT server restart/backups, and an admin changing settings during play. — post-completion test phase (owner-launched two-client run).

**Five DLC layers:**

- [~] Royalty conditional content: titles/quests/faction/psycasts only as optional company routes. — **Open:** no Royalty-specific content is authored. That is honest rather than a gap: it must be an optional route or nothing. (Gating mechanism closed and enforced; archived.) — **NO HONEST HOOK EXISTS YET, AND THAT IS RECORDED RATHER THAN PADDED 0.12.91-dev. Royalty ships **almost no buildings** — thrones are Core; what it adds is titles, permits, psycasts and the Empire. None of those is equipment a facility can be linked to, and the row’s own condition is *"only as optional company routes"*: a success route must be a **thing** (Deliver/Substitute/Purchase), a **log** (Document/Testify) or a **project** (Research). A title is none of the three. **So an honest Royalty hook needs a new route kind**, which is a design decision rather than a def edit, and inventing a thin one would be the hollow unlock this package keeps refusing. Stated the same way the project tree states that transport and orbital support has no tier 0 project, deliberately. The one place Royalty content already reaches the campaign is indirect and real: the Empire is a faction, and 0.12.90-dev made the world’s faction hostility one of the four inputs biasing which request family the corporation leads with.**
- [~] Ideology conditional content: beliefs, meditation, rituals, staff policies, and recreation only when available. — **Open:** no Ideology-specific content authored. (Gating closed; archived.) — **THE RECREATION CLAUSE LANDED 0.12.91-dev; the row stays open for the rest. `RR_Link_Assembly` is a room the branch gathers in — somewhere to be presentable, somewhere to be heard, and something to make a noise with — linked from `StylingStation`, `Loudspeaker` and `Drum`, and **hidden entirely without Ideology** by `Fillable` rather than merely gated. **One clause of five, and that is said plainly rather than claimed as the row.** Beliefs, meditation, rituals and staff policies are pawn-level and ideo-level mechanics with no facility or supply shape, and each would need its own decision about what an *optional* version looks like.**
- [~] Biotech conditional content: genes, mechanitors, children, medicine, pollution, and mechanoid options; no mandatory gene/resource dependency. — **Open:** no Biotech-specific content authored. Nothing is mandatory. (Gating closed; archived.) — **THE EQUIPMENT CLAUSE LANDED 0.12.91-dev; the row stays open for the rest. `RR_Link_Biolab` is this facility’s biological wing — gene assembler, gene bank, growth vat, mech gestator, subcore encoder and softscanner — because what comes back from a coordinate is not always a thing on a shelf. **Hidden entirely without Biotech** by `Fillable`. **Nothing is mandatory, which is the clause the row cares most about**, and it is now measured rather than asserted: `check-standalone-guarantee.py` confirms every Biotech reference in the package is gated and every Biotech lookup in C# degrades. Genes, children, medicine and pollution remain unaddressed, each needing its own answer about what optional means.**
- [~] Odyssey conditional content: gravship/off-world logistics and any compatible space travel. — **Open:** no gravship integration is written, and it stays DLC-optional throughout. (Gating and arc 7's request families closed; archived.) — **THE LOGISTICS CLAUSE LANDED 0.12.91-dev; the row stays open for space travel. `RR_Link_OffworldLogistics` puts a gravitational engine on the branch’s books, so the company can account for a facility that is able to leave — a branch that can move is a branch whose gate is not the only way anything arrives. **Hidden entirely without Odyssey** by `Fillable`, and the gate works identically without it. **A gravship actually carrying a branch between tiles is not built**, and that is the larger half: it needs the same world-object-and-generated-map checkpoint the two outstanding *"world tile the branch does not hold"* rows name.**
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

- [~] Eleven-pane Company Command, deep links, reason codes, native menu remap. — **Open:** deep links are partial, and the native menu remap is open and questioned on its own row above. (Twelve panes and reason codes closed; archived.) — **DEEP LINKS CLOSED 0.12.89-dev — pawn, building and research project all reach now, through `UI/OperationsLinks.cs`; see the deep-link row above for what the research half was doing before. **The row stays `[~]` because the native menu remap is still open and still questioned on its own row**, and nothing in this batch touched it.**
- [~] Slideshow integration review, additional menu images per shipped scenario. — **Open, and it needs a launch:** the integration **review** itself — how the slides read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right — cannot be judged from here. (Six slides and `proof-menu-slides.py` closed at 0.12.17-dev; archived.)
- [ ] Validation sweep, invalid-state matrix, balance, release report, packaging. — **split 2026-09-29 by owner decision 19.** The validation sweep and packaging halves are M6a and close without a launch; the invalid-state matrix, balance and release report are M6b and cannot. Tracked as separate rows in `TODO.md`. — **STILL OPEN.** **Structurally requires a launch.** Balance in particular cannot be claimed: nothing in this mod has ever been played.
- [T] **Automated fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration.** Deferred **by explicit owner instruction**, 2026-09-29 (decision 20, verbatim *"option 2 and option 3"*), not by dependency: the owner authorised automated fixtures **and** chose to hold them until after the first launch so their content follows observed failures rather than guessed ones. This is the **only** exception to the `CONTRIBUTING.md` no-tests rule anywhere in the repo, it covers this row alone, and **nothing for it may be written before the owner has launched the game once**. Owned by M6b.
- [T] **Screenshots, trailer and preview art for the mod page.** Need a running game, so they split from the M6a mod-page row into M6b. Everything else on that row — description, feature list, installation guide, dependencies, DLC matrix, RWT setup, credits, provenance, license, FAQ, update plan — closes without a launch and is M6a.

### Major M6a — Phase 6 work that closes without a launch (ROADMAP M6a; master TODO §Phase 6)

**Split from M6 by owner decision 19, 2026-09-29.** Bookkeeping only — no row is dropped, reworded or moved out of Phase 6, and every row below is still quoted verbatim from the master TODO.

**Owner decision D1, changed 2026-09-29:** ~~private RimWorld Together test build first; public Workshop only after named-profile and multiplayer validation~~ → **public Steam Workshop is the first distribution target; do not announce compatibility until validation is complete.** Verbatim: *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*. The mod-page and provenance row therefore moves forward rather than waiting on M4 verification.

**The `CONTRIBUTING.md` no-tests rule now has exactly one scoped exception**, recorded as owner decision 20 — see the fixtures row in M6b. It covers that row alone and nothing may be written for it before the owner's first launch. The rule is otherwise unchanged everywhere in this repo.

- [ ] Validate Def references, language keys, patch targets, load folders, package metadata, missing textures/audio, logs, build output, and clean-install folder structure.
- [ ] Prepare final mod page, description, feature list, screenshots, trailer/preview art, installation guide, dependencies, DLC matrix, RWT setup, credits, source provenance, license, FAQ, known issues, and update/support plan. — **the screenshots, trailer and preview art half needs a running game and belongs to M6b; everything else closes here.**
- [ ] Tag release, archive exact source and build artifacts, preserve a known-good server profile, and publish only features that passed their listed acceptance criteria. — **the ritual and the archive close here; the actual tag cannot be cut until M6b supplies the acceptance results this row requires.**

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

### Owner direction — credits, bonds, and the weight of the place (2026-09-29)

**Verbatim owner requests (2026-09-29, three more):** *"yeah keep teriing it then dont stop at 1 million"*; *"and ther should be a trader that is the multi trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies like a universersal trader but things are tech and company quest locked out till passed"*; *"and even cost credits to unlock item and materials and equipment gates in buying"*.

- [ ] **Exchange-rate balance** alongside catalogue balance. Both are constants in one place; neither has any play behind it.
- [ ] **Corporate catalogue balance.** The five tiers and their access fees are a first pass with no play behind them. They are data, so changing them is a def edit rather than a code change.


### Owner direction — the place copies you, and who you find in it (2026-09-29)

**Verbatim owner direction (2026-09-29), on ordering the remaining work:** *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*


- [ ] **"to the extent we want normal and really want the creepy insane looks and feel"** — the balance between recognisable and wrong is currently fixed by the depth curve. Whether it lands is a play question and belongs to the post-completion test phase.

### Owner direction — the look, and the seed generator that has to carry the universe (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly, and remmeber when building the seed genrator for the back rooms everything ive said and how the backrooms universe works to be lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

**And immediately after:** *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

That second message is what shaped the palette: a single global look could only ever deliver half the direction, so the look is a **function of depth**. Record: [`implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md`](implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md).

- [~] **"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying"** — **THE ARITHMETIC GUARANTEES IT AS OF 0.8.0-dev**, as three properties rather than tuning: an **absolute** cap of three simultaneous encounters at any depth and any wealth; **half of every coordinate's rooms bare by count rather than by chance**, so an unlucky run of rolls cannot produce a space with something in every room; and a first visit always quiet. Shallow coordinates are also capped below the top band regardless of wealth. **Stays in progress until inhabitants exist and the condition can actually be observed.** — **an acceptance condition on the whole generator, not a nice-to-have.** A high-tier coordinate that cannot be survived solo by building, supplying and finding a way out has failed this direction regardless of how good it looks.

### Owner direction — the M6 release gate (2026-09-29)

**Verbatim owner request (2026-09-29, three answers):** *"what is the m6 gate use askme question lets get past it"*, then the answers themselves — **M6 path:** *"Split M6a / M6b, build all of M6a"*; **fixtures:** *"option 2 and option 3"*; **release:** *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*.

Two of the three override standing policy, so all three are recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) as decisions 19, 20 and 21, and **D1 is superseded** there. This is the first change to a D-numbered Gate 0 decision since they were recorded on 2026-09-27.

- [ ] **Consequence: save migration becomes a standing obligation from the first published version.** It was a release-day checkbox on the assumption that publication came last. From publication onward there *are* other people's saves, so every subsequent version must carry a migration or a declared break. Owned by [`SAVE_MIGRATION_POLICY.md`](SAVE_MIGRATION_POLICY.md); D2's version policy is unchanged (`0.x` pre-release, `1.0.0` first stable).

### Owner direction — the other half of the topology: a way out into the world (2026-09-29)

**Verbatim owner requests, carried from the topology direction:** *"and or pop out any where in the game world on a tile map"*, and the worked examples *"map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map"*.

Record: [`implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md`](implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md).

- [ ] **A world tile the branch does not hold** — still the larger half, needing a new world object and a generated map. Its own checkpoint.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [ ] **A world tile the branch does not hold** — still open. A new world object and a generated map; its own checkpoint.

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

## Owner question — do RimWorld's map layers change the five-map limit? (2026-10-05)

**Verbatim owner question (2026-10-05):** *"and somthing someone told me is that with rimworld updates there are now map layers? is that usable in any way as per our 5 mcolony limit we use to propigate and sustain our entire gameplay limitations"*

### Measured from the installed game before answering

**Layers are real, and they are extensible.** `PlanetLayerDef` is a def type. Core ships one, `Surface`. **Odyssey** ships `Orbit`, and leaves a **commented-out `Moon` layer** in `Odyssey/Defs/PlanetLayerDefs/PlanetLayers.xml` — Ludeon documenting, in data, exactly how a modder adds a surface layer of their own.

**A layer carries real behaviour, not just a camera position:** `canFormCaravans`, `onlyAllowWhitelistedIncidents`, `onlyAllowWhitelistedGameConditions`, `onlyAllowWhitelistedArrivals`, `onlyAllowWhitelistedArrivalModes`, `isSpace`, `ignoreNoBuildArea`, `defaultBiome`, `settlementWorldObjectDef`, `raidPointsFactor`, and its own `worldGenSteps`, `worldDrawLayers` and `worldTabs`.

**And layers CONNECT.** `PlanetLayer.HasConnectionFromTo(PlanetLayer)` and `TryGetConnectionFromTo(...)` with a `PlanetLayerConnection`. That is this mod's central idea written in Core's own vocabulary.

### THE ANSWER: layers do not raise the cap, and our coordinate maps were never counted by it

**Read out of `RimWorld.Planet.SettleUtility.PlayerSettlementsCountLimitReached`, not inferred:** it walks `Find.Maps` and counts a map when `map.IsPlayerHome && map.Parent is Settlement`, **or** when `map.wasSpawnedViaGravShipLanding`, then compares against `Prefs.MaxNumberOfPlayerSettlements`.

- **It is NOT layer-aware.** An orbital colony counts against the same number as a surface one. **A layer buys zero extra colonies.**
- **But it only counts settlement-parented homes and gravship landings.** `RimroomsDestinationMapParent` derives `MapParent`, **not** `Settlement`, so **every Backrooms coordinate map is already invisible to the player's settlement cap.** The only thing counting them is ours.
- **Our five is the owner's own direction, not an engine limit** — *"lets have that 5 map count be universal max for back rooms main map and claiming maps where u pop out and anything over 5 maps defaults to caravans"* — and `WorldExit.MaximumBranchMaps` counts headquarters, loaded coordinates, registered sites and claimed tiles together, with the stricter of ours and the player's preference winning.
- **The real cost of a map is simulation, and a layer does not make one cheaper.** Eight loaded maps is eight maps of pathfinding, temperature, weather and pawn ticking whichever layer their world object sits on. Raising the cap is a performance decision, and performance is the one thing this project cannot measure for itself.

### What layers would actually be worth using for

Not more maps. **Expressing our rules in Core's data instead of our C#**, which is cheaper to maintain and automatically correct as the game changes.

- [ ] **A `Backrooms` PlanetLayer as a design question, not a capacity one.** `canFormCaravans: false` is our no-caravan rule; `onlyAllowWhitelistedArrivals` and `onlyAllowWhitelistedIncidents` are `PortalTraversalPolicy` and the incident gate expressed as data; a `defaultBiome` and `raidPointsFactor` of its own replace tuning we currently carry in code. **It would also make `PlanetLayerConnection` the engine's own word for a gate.** Needs an owner decision because it is a visible change: a layer gets its own world-view gizmo and its own tab, so the Backrooms would become somewhere the player can look at from the planet view — which may be exactly right or exactly wrong for a space that is meant to be found through a door.
- [ ] **Measure before any of it:** whether a `MapParent` on a non-surface layer still generates and saves identically, and whether `onlyAllowWhitelistedIncidents` would silence the unnerving register rather than shape it. **This is `[T]`-shaped work** — it needs a launch, and the owner is the only one who launches.
- [ ] **The cap itself stays five until the owner says otherwise.** It is their number, and the measurement above does not argue for changing it: nothing found gives a free map, and the thing that would — raising the number — is a performance trade nobody has measured yet.
