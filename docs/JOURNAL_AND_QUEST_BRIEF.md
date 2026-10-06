# The journal and quest brief

**This document exists because the owner required it before any code.** Verbatim, 2026-10-06:

> *"this is big one to need proper write up before attempting the work and using ask me question where forks and questions about this intrical part of the jobs and quests and how the company recieves the starting journals via droppod and picks up the quest one when propeted to complete a mission with a geen light to show its ready to be sent to complete the quest mission, even the tutorial mission should have options to fillout the dataand research for the gate steps and send that back to the COMPANY where the journals are taken to a table and written out but these tasks are auto in the pawns work jobs so after doing all the gate steps, each step has a lab nots, research write up, investigation, analysis, ... what ever the task requires and what the company wants as far as data or anaylisiis or retreval and such we can even have like a research bench thats togglable to handling the lab nots write ups in jounrals and things and people brountgh back and major event reports i can think of all kinds of ways tand things it all just need correct combing and integrations  and the seend new journals after each quest finished/ starting new quests/missions, its almost like every book recieved needs to be tuned to or capable of listing the current quests its needed for that has been acceptred, with ability to accept more than one quests at a time and a variety to choose from after the inital tutorial like quests."*

**And verbatim on the defect in the journals that ship today:**

> *"the starting journals still arnot correct(need to figure this out for generating ones purchased too) both are named wrong and have differ information in the "i" write up saying incorrectly that one is about nutrition and the othert is about aiming. so the journal shit is very important and needs to be figured out proprly for what we need to be able to log things record whats needed with a pawn click actions with sterp by step instructions how to use the journal but not wordy keep it very concise asnd to the point and that shit all needs to be added propely to all the wikis shit where relevant."*

**And verbatim on parallelism, 2026-10-06:**

> *"and as for the write up stations u can have more than one to have more than one pawn doing it as u can have multiple quests going, and same with the coms and machine benches so that it isnt dependant at one pawn dying at the gate from starvvation trying to keep it open forever"*

**And verbatim on exploration feeding it, 2026-10-06:** *"and exploration need journal entry work stuff"*, scoped by the next message to *"once completed"*, and paid by the one after: *"can get $$$ form companty and such"*.

---

## 0. What already exists, measured before anything was designed

**Nothing below gets rebuilt.** Each row was read out of the source this session, not remembered.

| Piece | Where | What it already does |
|---|---|---|
| The record book itself | `CompRouteEvidence.NativeCarrierDef` | Resolves **Core's `TextBook`** and refuses anything else: Core content pack, a `Book` subclass, exactly one `CompProperties_RouteEvidence`, plus `CompBook` and `CompQuality`. The owner's own decision, *"Fold it into the record book crews already carry"* |
| Company-issued marking | `CompRouteEvidence.companyIssued` | Set **once, at the moment of granting**, and saved. Owner: *"Mark the company-issued ones"*. Nothing scans for books later, so a looted or bought book can never be retro-tagged |
| Arrival by drop | `RecordBookDelivery.cs` | **Deterministic, not an incident.** Two books drop when the branch is in corporation contact, holds a designated **and calibrated** gate, and has **no book anywhere on any owned map**. It can fire again, because a branch that loses its only book is blocked through no fault it can fix |
| Custody | `EvidenceSettlement.HasArchivedCustody` | The book is inside a storage thing linked to a designated gate in the **`RR_Link_Archive`** role. Read through Core's `StoringThing()`, so **any** shelf qualifies, including a modded one |
| The quest record | `ContractRecord` in `CampaignRecords.cs` | `id`, `templateId`, `titleKey`, `coordinateId`, `status`, `basePaymentUsd`, `bonusUsd`, `acceptedTick`, `completedTick`, `settlementOperationId`, a supply demand triple, and a field condition (`requiredDepth`, `requiredSurveyedRooms`) |
| The quests that exist | three `templateId`s | `rr.survey.onboarding.v1` (the tutorial), `rr.mission.oddconsignment.v1`, `rr.supply.odd.v1` |
| Routes through a request | `RequestRoutes.Available` | An **authored floor** of at least two routes of different kinds, plus derived extras a branch has earned. A derived route can never substitute for an authored one |
| Collection by radius | `ValuablesExchange` | A designated beacon takes **everything tradeable inside its radius** — Core's own trade-beacon contract, borrowed rather than reinvented |
| Payment | `PostTransaction(operationId, …)` | Idempotent by operation id, so a settlement cannot pay twice |

**The facility now ships eight `OrbitalTradeBeacon`s**, one per room holding a shelf, placed where the owner placed them. That is the delivery surface this brief uses, and it already exists on the map.

---

## 1. The four forks, all answered by the owner

| Fork | The owner's answer | What it costs, stated when it was asked |
|---|---|---|
| Journal scope | *"Both — per-quest books plus a branch ledger"* | Two objects to keep in agreement rather than one |
| Where the write-up happens | *"A dedicated write-up desk"* | **A new buildable.** The owner was shown that the standing rule is to reuse existing content, and chose it anyway |
| How a finished book returns | **Beacon radius pickup** | Nothing. It reuses `ValuablesExchange`'s radius contract and the eight beacons already placed |
| What the green light reads from | **Both, and they must agree** | Two derivations of one rule is the defect this project keeps meeting. **§6 spends that risk down to one writer and two readers** |

### 1.1 The records desk is the second approved exception to the content rule, and the art rule still binds

`CONTENT_REUSE_POLICY.md` allows new gameplay content only by exception, and the only prior exception is the original menu images. **The records desk is the second, approved for this purpose alone.**

**It does not get new art, and that distinction is the whole reason the previous custom items were retired.** The record that closed them says it plainly: *"The breach was the ART, not the defs."* So `RR_RecordsDesk` carries Core's own texture path, **`Things/Building/Furniture/Table1x2`**, verified present in Core's `Buildings_Furniture.xml` at line 907. One new def, zero new pixels.

---

## 2. The objects, and which one is the truth

| Object | What it is | Where it lives | Who may have several |
|---|---|---|---|
| **The quest book** | A Core `TextBook`, company-issued, bound to one accepted quest | hauled, filed, carried into a coordinate, finally placed in a beacon radius | **one per accepted quest**, because the book is the deliverable |
| **The branch ledger** | One book that lists every accepted quest and its green light | lives at headquarters, never sent | **exactly one per branch** |
| **The record** | `ContractRecord` plus its write-up tally | the campaign component, saved | one per quest, and **it is the truth** |

**The ledger is a dashboard, the books are deliverables, and the record is the authority.** A ledger that could be sent would be a branch sending away its own index.

---

## 3. Arrival: how a book reaches the branch

Three ways in, and all three already have a mechanism or a near one.

1. **The starting journals.** Placed by the start def. The Async Industries facility authors two `TextBook`s at (11,47) and (14,47); the laboratory start carries two. **They are items, so a pawn hauls them the moment the map starts** — which is why their authored cell reads empty and why absence there is not deletion.
2. **The corporation's drop.** `RecordBookDelivery` already does this, unchanged: two books, deterministic, only when the branch holds none.
3. **A new book per accepted quest.** The owner: *"the seend new journals after each quest finished/ starting new quests/missions"*. **Accepting a quest drops its book**, through the same `DropPodUtility.DropThingsNear` path and the same relief drop cell, so there is one delivery mechanism in the mod rather than two.

**Purchased books are covered by the same rule as granted ones.** The owner asked for it in the same sentence — *"need to figure this out for generating ones purchased too"* — and §5 is written so that the fix depends on `companyIssued` rather than on how the book arrived. A book the branch bought and then assigned to a quest is company-issued from that moment.

---

## 4. The write-up work, and why it is automatic

**The owner's words make it a work job rather than an order:** *"these tasks are auto in the pawns work jobs"*.

### 4.1 The kinds, which are the owner's own list

> *"each step has a lab nots, research write up, investigation, analysis, ... what ever the task requires and what the company wants as far as data or anaylisiis or retreval and such"*

Four named kinds, and the ellipsis is the owner saying the list is open:

| Kind | What produces it | What the branch must already hold |
|---|---|---|
| **Lab notes** | a gate step performed at the station | the step's own record |
| **Research write-up** | a company project finished | the project's completion |
| **Investigation** | an evidence record reaching **Secured** custody | the book on an archive shelf |
| **Analysis** | an evidence record analysed | `analyzedTick` set |
| *(open)* | *"what ever the task requires"* | declared per request, never hard-coded |

**A write-up kind is declared on the request, never inferred from the quest's name.** `RimroomsRequestDef` already carries authored routes, so the write-up list belongs beside them in XML, where the checker can see it and a reader can count it.

### 4.2 The job

A Core `WorkGiver` scans for a quest whose record has an outstanding write-up **whose precondition is already met**, reserves the records desk, and runs a bench toil. On completion it performs **one** operation, described in §6.

**It is ordinary work with an ordinary priority.** It competes with cooking and hauling like everything else, which is the point: a branch that never assigns anybody to paperwork never files anything, and that is a decision the player made rather than a bug.

**And the pawn is never trapped at it.** `GateWatch.MustLeave` exists because a pawn starved at the comms console, and the records desk inherits the same floor: starving, exhausted, burning, bleeding out or downed releases the pawn before any posture is consulted. A write-up is interruptible and resumable by construction, because the record holds the tally and the desk holds nothing.

### 4.3 Several desks, by design rather than by accident

Owner: *"u can have more than one to have more than one pawn doing it as u can have multiple quests going"*.

**The branch can accept several quests at once, so several pawns must be able to write them up at once.** A single desk would re-create the starvation problem one subsystem over: one pawn pinned, everything else queued behind them.

**No cap on desks, and that is deliberate.** The console cap of four is the owner's number for a scarce shared resource — a gate's window. A desk is not scarce and not shared; it is a work station, and RimWorld has never capped work stations. Capping it would invent a rule the player cannot see a reason for.

---

## 5. The naming defect, and the exact mechanism behind it

**The cause was read out of the shipped assembly, not guessed.** `Verse.Book.GenerateBook` resolves the title through grammar:

```csharp
request.Includes.Add(BookComp.Props.nameMaker);
title = GenText.CapitalizeAsTitle(GrammarResolver.Resolve("title", request)).StripTags();
```

…and the **subjects** come from `AppendDoerRules`, which asks every `BookOutcomeDoer` for its topic rule packs. **Core's `TextBook` carries skill doers, so the generated title and the "i" description name the skills those doers rolled.** The owner saw *nutrition* and *aiming*; those are Cooking and Shooting wearing their topic words.

**So nothing is broken and nothing was mis-authored. Repurposing an existing item kept its identity as well as its model** — which is the same lesson as the comms console coming back facing north.

**And the deeper cause is that no comp can reach a book at all.** `ThingWithComps.LabelNoCount` is where the comp `TransformLabel` chain runs, and `ThingWithComps.DescriptionFlavor` is where `GetDescriptionPart()` is collected. `Verse.Book` overrides **both**, plus `LabelNoParenthesis`, and never calls base. So `CompRouteEvidence.TransformLabel` — which has returned the company label since the owner answered *"Mark the company-issued ones"* — **was never called once.** The feature read as built in every file a reader would open.

### 5.1 Why the obvious fixes are all wrong, named so nobody retries them

| Candidate | Why it fails |
|---|---|
| Set `title` on the instance | `private string title;` on `Verse.Book`. **No setter, and a subclass cannot reach a private field of its base** |
| Patch `TextBook`'s `nameMaker` / `descriptionMaker` | Changes **every** textbook in the game, including the ones a player buys to teach Shooting |
| A brand new `ThingDef` for the journal | **Re-opens a decision the owner already made.** `RR_RouteRecording` was a custom def and the owner's answer was *"Fold it into the record book crews already carry"*. The def still exists only so old saves load |
| Reflection into the private field | Fragile across game versions, and the project has a sanctioned route that is not |
| **A `thingClass` XML patch** | **Tried, and `check-compliance` rule 3 refused it — correctly.** Core declares `thingClass` on the abstract `BookBase`, so no xpath reaches TextBook's own element and the only operation that works is a `PatchOperationReplace`, which takes ownership of a def where the last mod to load wins. Patching the parent instead would hand our class to `Novel`, `Schematic` and `Tome` |

### 5.2 The fix: a subclass bound at startup, overriding presentation only

`Verse.Book` publishes exactly the members needed as virtual, so `RimroomsRecordBook : Book` overrides three of them:

| Override | What it does |
|---|---|
| `LabelNoParenthesis` | Core's generated title, **then the comp chain Book skipped** — asked of every comp in order, exactly as `ThingWithComps` would |
| `LabelNoCount` | the transformed name **plus** `GenLabel.LabelExtras`, so quality and damage survive |
| `DescriptionDetailed` | the company's own write-up on a company book, Core's on everything else. One override covers both surfaces, because `Book.DescriptionFlavor` calls it virtually |

**The binding is in code, at `StaticConstructorOnStartup`, not in XML** — `Investigation/RecordBookClassBinding.cs`. That is strictly more precise than any xpath, which is the same argument `FixtureTellService` already makes: it runs after inheritance resolves and after every mod's defs load, so it reads the value actually in play. **And it can decline.** If another mod already owns `TextBook`'s class, the binding leaves it alone and logs why, because two mods silently fighting over a single-valued field is worse than one mod visibly standing down.

Three properties make it safe:

- **An ordinary textbook is untouched.** The label chain is restored generically and our own transform returns its input unchanged unless the book is company-issued — so another mod's comp on a book starts working too, which is a repair rather than a regression.
- **The subclass holds no state.** Everything it reads lives in `CompRouteEvidence` or the campaign record, so `ExposeData` is unchanged.
- **Core's reading outcome is kept, on purpose.** A field journal full of observations plausibly teaches something, and suppressing it would mean subclassing `CompBook` to clear a `protected` list. **The title says what the book is; the stat panel still says, honestly, what reading it does.**

### 5.3 WHAT THIS CANNOT FIX, AND THE REMEDY THAT NEEDS NO MIGRATION

**A book already in a saved game keeps the class it was saved with.** RimWorld writes the runtime type into the save — `ScribeExtractor.SaveableFromNode` reads a `Class` attribute and instantiates that — so a textbook saved as `Verse.Book` loads as `Verse.Book` however the def now reads.

**So the fix applies to every book created from this version onward, and not to the two already sitting in a live save.** That was measured out of the assembly before the fix was designed, not discovered after shipping it.

**The in-game remedy already exists and is not a migration.** `RecordBookDelivery` sends two correct books whenever a branch holds **none anywhere**, so destroying a wrongly-titled pair gets a correctly-titled pair back on the company's next tick. A migration that destroyed and rebuilt each book in place was considered and **rejected**: `CompRouteEvidence` binds through `GetUniqueLoadID()`, a new object has a new one, and quietly re-pointing a bound evidence record is how a case gets lost. `SAVE_MIGRATION_POLICY.md` owns that call.

### 5.4 Marking, which turned out to be two more gaps

The whole repair is inert on a book nobody marked, so every route that mints one was audited. **Two of four were not marking:**

| Route | Before |
|---|---|
| the start def's authored books | marked |
| the scenario arrival sweep | marked |
| **the corporation's drop** | **not marked** — the route a player meets *second*, and the one that unblocks somebody who lost the first book |
| **a book bought from the company catalogue** | **not marked** — `RR_ProcurementCatalog.xml` sells `TextBook`, so the catalogue was the *"generating ones purchased too"* half of the owner's sentence all along |

**A book found in a coordinate is deliberately left unmarked.** It is somebody else's, which is the entire meaning of `RR_Evidence_Unregistered`, and checker 27 asserts that it stays that way so a future sweep cannot "fix" it.

### 5.5 The instrument, and the two false greens it found in itself

**No existing instrument could have caught this defect**, and that is the reason a new one exists. A checker reading our source saw a transform that looked correct; a checker reading the def saw a comp correctly attached. The fault lived in a Core class neither of them reads.

`tools/check-record-book-class.py` is **checker 27**, with ten rules, and `plant-record-book-class.py` is plant suite **35**, at **23 of 23**. The suite earned its keep immediately: it walked straight past two rules in the first draft, because `CLASS_NAME in patch` passed while one of two values was wrong, and `"PatchOperationAdd" in patch` passed on a *different* operation in the same file. **Both rules are scoped to the operation now.** A third rule passed on a rename, because `in` cannot tell a member from a prefix of one.

### 5.3 What a company book is called

The label names the work, never the subject: the quest's `titleKey` and its coordinate. The description is the step-by-step instruction block from §7, so the "i" panel that currently lies about nutrition becomes the place the player learns what the object is for.

---

## 6. The green light: both, and one writer

**The owner chose *"Both, and they must agree"*, and the risk in that choice was stated when it was offered:** two derivations of one rule is the defect this project keeps meeting. So the design spends it down instead of accepting it.

### 6.1 One writer, two readers

**The write-up job performs a single operation** that advances the record's tally **and** stamps the book, inside one call, with the record written first. There is no second computation anywhere:

- the **record** is the authority, as `ContractRecord` already is for payment;
- the **book** carries a copy of the record's quest id and tally, as a receipt;
- the **light** reads the record, and requires the book to be present and in custody.

**So a mismatch cannot be produced by the mod working normally.** It can only mean a book from another branch, a save edited by hand, or damage — and each of those is a thing the player should be told about rather than a thing to paper over.

### 6.2 The three states the light can show

| State | Condition | What the player does |
|---|---|---|
| **dark** | write-ups outstanding | assign somebody to the desk |
| **green** | every required write-up done, book present and in custody, book agrees with the record | haul the book into a beacon radius |
| **amber — unverified** | the record is complete but no agreeing book exists | the work is **not lost**; issue or re-stamp a book |

**Amber is the reason the record is the authority rather than the book.** Burn the book, lose it in a coordinate, leave it on a crew who did not come back, and the branch has lost a deliverable rather than a month of work. That is recoverable, and the alternative is not.

**The light shows on three surfaces, all existing:** the ledger's own entry, the quest's row in the Operations pane, and the book itself.

---

## 7. Pawn click actions, kept short

Owner: *"with a pawn click actions with sterp by step instructions how to use the journal but not wordy keep it very concise asnd to the point"*.

**Core already has the surface:** `Book.GetFloatMenuOptions(Pawn selPawn)` is `public override`, so right-clicking a book with a colonist selected is where these live, beside Core's own *Read*.

| Option | When it shows | What it does |
|---|---|---|
| **Read** | always | Core's, untouched |
| **Write up here** | the record has an outstanding write-up and a desk exists | sends the pawn to the nearest free records desk |
| **File in archive** | the book is not in archive custody | hauls it to an archive shelf |
| **Send to company** | the light is green | hauls it into the nearest beacon radius |
| **What is this for?** | always | the instruction block, four lines, no more |

**Four lines is the ceiling and it is the owner's instruction, not a style preference.** The block names: what the book is bound to, what is outstanding, where it goes next, and what pays. Anything else belongs in the wiki.

---

## 8. Sending it back: the beacon radius

**The owner's choice, and it reuses a contract the player already understands:** what is in the circle is what is on the table.

1. A pawn hauls a green book inside a designated beacon's radius.
2. On the company's own tick, every green book in a radius is collected together.
3. The quest settles through `PostTransaction` with its existing operation id, so **collection cannot pay twice**.
4. One letter reports the batch, naming each quest settled.

**Three properties follow from using the radius rather than a courier or a gate window:**

- **The player controls the timing.** A finished book can sit on a shelf indefinitely. **§1.1's no-clock absolute binds here: there is no deadline on a write-up, ever.**
- **Paperwork never competes with expeditions.** Sending a book back costs no gate window, which the gate route would have.
- **A book inside a radius by accident is still a choice the player made**, the same as any other thing left in a trade beacon's circle. The collection letter names what went, so it is never silent.

---

## 9. The branch ledger

| Column | Source |
|---|---|
| quest | `ContractRecord.titleKey` |
| coordinate | `ContractRecord.coordinateId` |
| accepted | `acceptedTick` |
| write-ups | the record's tally, *done of required* |
| light | §6.2 |
| pays | `basePaymentUsd` and `bonusUsd` |

**It lists accepted quests and nothing else.** A ledger that also listed offers would be an offer board, and the Operations pane is already that.

**Several quests at once is the owner's requirement** — *"with ability to accept more than one quests at a time"* — and nothing in `ContractRecord` ever prevented it: `contracts` is a list, and `rr.survey.onboarding.v1` is simply the only one a fresh branch is handed. **What was missing is the index, which is this.**

---

## 10. Exploration feeds it, once

Owner: *"and exploration need journal entry work stuff"* → *"once completed"* → *"can get $$$ form companty and such"*.

- **One entry for a finished survey of a coordinate, not one per room.** A write-up per room would bury a branch in paperwork for walking down a corridor.
- **Completion is a real state**: every room the planner authored has been entered. Not every cell unfogged, because a sealed pocket behind unmined rock would make completion unreachable and the notice would never fire.
- **The record already has the field for it.** `ContractRecord.requiredSurveyedRooms` exists and a zero reports its condition met, so a survey quest needs no new data shape.
- **It pays like any deliverable**, and **§1.2 binds the offer to two routes of two different kinds** — which a survey has naturally: **Document** the finished map, or **Testify** to what the crew saw where a record was lost.
- **§1.1 binds it too: no clock on the survey**, however long the maze takes.

---

## 11. Variety after the tutorial

Owner: *"a variety to choose from after the inital tutorial like quests"*.

**Three templates exist and the mechanism for more is already there.** A new quest family is a `RimroomsRequestDef` with its authored routes and now its write-up list — XML, not code. The tutorial stays `rr.survey.onboarding.v1` and stays first, because it is the thing that teaches the loop.

**§1.2 binds every family that is ever added: two routes of two different kinds, and no clock on any of it.**

---

## 12. What the register said, checked before designing

`python tools/register-query.py use RR-MSN` → **23 rows**; `trace RR-EVD` → **31 rows**; `find book` → **0 rows**.

| Row | What applied |
|---|---|
| **[4] Core** *(Required)* | *"do not make a DLC feature the sole route through the campaign."* Books, beacons and work givers are all base game, so the whole brief is Core-only by construction |
| **[10] Adaptive Storage Framework** *(Optional)* | *"keep vanilla stockpiles useful when ASF is absent."* **Already satisfied, and worth stating:** custody is tested through Core's `StoringThing()` against the gate's linked archive role, never against a shelf's def name, so a modded shelf counts and a vanilla one still works |
| **[100] Go Explore!** *(Optional)* | *"Do not make it the Backrooms coordinate, room, or mission generator."* **Binds §10:** survey completion is read off our own authored room records, never off another mod's exploration events |
| **[132] More Faction Interaction** *(Optional)* | *"Add company jobs through a dedicated Operations interface"*, and *"Keep the company ledger distinct from vanilla silver"*. The ledger is `PostTransaction` credits, not silver, and the surface is the Operations pane |
| **[24]/[25]/[26] Adaptive \* Storage** *(Optional)* | same finding as [10], same mechanism, no separate work |

**Nothing in the 294 ships a book, which is why binding `TextBook`'s class is safe today — and the binding does not rely on that staying true.** It reads the resolved value at startup and stands down with a log line if another mod has already taken the field, so a profile change reports itself instead of becoming a load-order coin toss.

---

## 13. The absolutes this brief is held to

- **§1.1 — a gate's connection has a duration. Nothing else in this mod has a duration.** No deadline on a write-up, a survey, a filing or a send-back.
- **§1.2 — two routes of two different kinds**, on every request this brief adds.
- **The solo guarantee** is untouched: nothing here spawns an encounter or changes a room count.
- **No new art.** One new def, Core's texture.
- **Core API only, no Harmony.** Every extension point used here is `virtual` or `public override` in the shipped assembly, and each one is quoted in the section that uses it.

---

## 14. The build order, which is a real dependency chain

1. ~~**The naming fix** (§5)~~ — **BUILT, 0.12.99-dev.** `RimroomsRecordBook`, bound at startup, plus the two unmarked routes, the click action, checker 27 and plant suite 35 at 23 of 23. It was taken first because it is self-contained, it is the owner's loudest complaint, and every later section shows text on a book.
2. **The write-up list on `RimroomsRequestDef`** (§4.1). Data before the job that reads it.
3. **The records desk** (§1.1) and the work giver (§4.2).
4. **The single stamping operation** (§6.1), then the light (§6.2).
5. **The ledger** (§9), which only displays what 1 to 4 produce.
6. **Click actions** (§7), last of the player-facing pieces, because each option needs its underlying action to exist.
7. **Beacon collection** (§8).
8. **Exploration's entry** (§10) after the explore toggle itself lands.
9. **The wiki pass**, which the owner named in the same sentence and which is not optional.
