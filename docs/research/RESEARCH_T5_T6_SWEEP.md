# The T5/T6 sweep — every unclaimed knob, and what a tier could honestly be

**Owner direction, 2026-10-05, asked how to resolve the open research-tier row. Verbatim:**
*"Sweep the constants and propose the tiers to you"*.

> ## ⛔ THE OWNER HAS PICKED, AND FOUR OF THESE ARE BUILT. READ THIS BEFORE SWEEPING AGAIN. ⛔
>
> **Asked which to build, the owner answered: *"All six, including the fourth crew member"*.**
>
> | | Candidate | Outcome, 0.12.99-dev |
> |---|---|---|
> | 1 | Facilities T5 servicing interval | **BUILT** as `RR_Facilities_ServicingRegime` |
> | 2 | Measurement T5 trained eye | **BUILT** as `RR_Measurement_TrainedEye` |
> | 3 | Spatial T5 near exit | **BUILT** as `RR_Spatial_NearExit` |
> | 4 | Entities T5 quiet protocol | **BUILT** as `RR_Entities_QuietProtocol`, `MaxEventsPerOpening` only |
> | 5 | Fieldcraft T5 fourth hand | **SUPERSEDED, then re-subjected.** Built as `RR_Fieldcraft_StandingRelief` |
> | 6 | Spatial T6 seventh level | **BUILT** as `RR_Spatial_DeepFrontier`. The sixth band was authored |
>
> **Candidate 5 was superseded minutes after it was approved**, by a direction answering a
> different question: *"rememberber pawns can cross gate as they plkease so no max number"*. The
> candidate's whole effect was raising `CrewPlanner.MaxCrew` from three to four. With no maximum
> there is nothing to raise, so it would have been *"a project that promises something and changes
> nothing"* — the exact phrase four deleted projects were deleted for.
>
> **Asked again, the owner chose the console hand-off.** Only two unclaimed knobs existed anywhere
> in this branch's own subject, and the other was the stranding margin on a need-crossing — which
> would have made it the only project in the tree that buys utility with safety. So Fieldcraft T5 is
> `RR_Fieldcraft_StandingRelief`: the relief grace doubles from half an in-game hour to one.
> **The fourth hand is still impossible and `proof-research-tier5.py` still proves why**, so if a
> crew cap ever returns, somebody is told rather than left to build a second tier for it.
>
> Both halves are enforced rather than remembered: `.local/register/proof-research-tier5.py` asserts
> the four, the five absences, and the condition that makes the Fieldcraft absence correct — **if a
> crew cap ever returns, that proof starts failing and names this document.**

So this was a **proposal**, not a build. Nothing in `RR_CompanyProjects.xml` changed until the owner
picked from the list below. **Six candidates survive, four branches get none, and the reason each
branch gets none is the point of the document** — a branch with no honest tier is a finding, not a
gap.

## The rule this sweep is bound by, which is the file's own

`RR_CompanyProjects.xml` deleted four projects at 0.12.5-dev and recorded why: *"a project here
would promise something and change nothing, which is exactly what 0.12.5-dev deleted four projects
for."* So the bar is not *is there a number left*. It is:

> **A tier may only exist where a player could name the effect.**

One sentence, from play, without reading source. *"Our gates need servicing half as often"* passes.
*"The candidate budget rose from 3 to 4"* does not — that is an implementation bound, and a project
granting it would be a project that promises something and changes nothing a player can see.

## What was measured

**278 numeric constants** across 232 source files, enumerated rather than remembered — the row's
recorded figure was 274 and the surface has grown since. **34 capabilities are granted and 34 are
read**, a perfect bijection: no hollow unlock, no dead read.

Sixteen files read a capability at all. Everything declared in those sixteen is treated as claimed
unless a specific constant is visibly outside the claimed branch.

Then every unclaimed constant was screened on three tests, and **most die on the third**:

1. **Nameable** — a player can say what changed in one sentence.
2. **Unclaimed** — no capability already gates it, and it is not already a player setting.
3. **A play knob at all** — not a schema version, tick interval, loop bound, sweep window,
   container capacity or seed salt.

Test 3 removes the large majority. `PlannerVersion`, `CurrentSchema`, `MaximumOperationsPerAdvance`,
`CellsPerSweep`, `MaximumPendingCrossings`, `GeneratorSeedPart` and their forty-odd siblings are
not tuning. They are the machine working.

---

## The six candidates

Ordered by how confident the sweep is, not by branch. Each names the exact constant, so the owner
is choosing a real change rather than a label.

### 1. Facilities T5 — servicing interval · **CONFIDENT**

| | |
|---|---|
| Constants | `NativeGateServicing.ServiceCapacityTicks` (600000), `TechnicianServiceFactor` (0.7f) |
| Named effect | *"Our gates need servicing half as often, and a technician does it faster."* |
| Why it is honest | **§1.1 names maintenance as one of the four things that decide how long a gate can be open.** This is the only one of the four with no project on it — power has `ReserveDiscipline`, tech has the window ladder, workforce has `StandbyDiscipline`. Maintenance has nothing |
| Cost | None to the design. A lapsed assembly blocks the *next* opening and never the current one, so improving the interval cannot create a new failure |

**This is the one the sweep would build first.** It fills a named gap rather than inventing a knob.

### 2. Measurement T5 — the trained eye · **CONFIDENT**

| | |
|---|---|
| Constant | `FixtureTellService.TellPercent` (12) |
| Named effect | *"We spot the one wrong detail more often."* |
| Why it is honest | The fixture tell **is** the thing the owner's *"remember lsd unnerving feeling with all things"* direction produced, and a measurement branch that teaches a branch to read a space but not to notice its tells is missing its own subject |
| Cost | Raising it dilutes the tell. At 12% a wrong fixture is an event; at 50% it is wallpaper. A tier should move it one step, not uncap it |

### 3. Spatial T5 — the near exit · **CONFIDENT**

| | |
|---|---|
| Constants | `WorldExit.WorldExitMinimumTiles` (7), `WorldExitMaximumTiles` (20) |
| Named effect | *"A way out puts us nearer home than it used to."* |
| Why it is honest | A player notices the distance of an exit immediately and has no influence over it at all today. It is the most visible unclaimed number in the whole sweep |
| Cost | None. Narrowing the band cannot make a route invalid; the search already refuses an unreachable tile |

### 4. Entities T5 — quiet protocol · **PLAUSIBLE, with a reservation**

| | |
|---|---|
| Constants | `AnomalyEventService.MaxEventsPerOpening` (2), or `CoordinatePressureLadder.QuietRoomFraction` (0.5f) |
| Named effect | *"Fewer things happen to us per opening."* |
| Why it is honest | Nameable, unclaimed, and a real play knob |
| **The reservation** | **It buys safety by subtracting content.** Every other project on this list adds a capability; this one removes encounters. `QuietRoomFraction` is also half of the solo-survivability guarantee — *"half of every coordinate's rooms bare by count rather than by chance"* — and a project that moves a survival guarantee is a project that can make the guarantee a research gate instead of an absolute |

**The sweep's recommendation is to take `MaxEventsPerOpening` and leave `QuietRoomFraction`
alone.** The first is pacing; the second is a promise.

### 5. Fieldcraft T5 — the fourth hand · **A DESIGN DECISION, NOT A SWEEP RESULT**

| | |
|---|---|
| Constant | `CrewPlanner.MaxCrew` (3) → 4 |
| Named effect | *"We can send four people."* The most nameable effect on this entire list |
| Why it is flagged rather than recommended | **Three is a stated design figure, not a convenience bound.** It appears in the briefs, the wiki and the pressure arithmetic. Raising it changes what a coordinate has to survive, what a crew can carry, and the whole shape of the three-at-once encounter cap |
| Pull in the other direction | The owner's standing instruction is *"so dont limit yourself"*, and a cap earned by research is precisely not a limit imposed by convenience |

**This is the owner's call and the sweep will not make it.** If it is taken, it is a tier whose
acceptance evidence has to include a re-measured pressure ladder, not just a working slider.

### 6. Spatial T6 — the seventh level · **A CONTENT DECISION, NOT A SWEEP RESULT**

| | |
|---|---|
| Constant | `NaturalFrontierService.MaximumNaturalDepth` (6) → 7 |
| Named effect | *"We reach a level nobody has come back from."* |
| Why it is the only T6 candidate | A T6 should be the top of a branch and feel like it. Nothing else unclaimed is big enough to sit above a T5 |
| **The blocker, and it is real** | `BackroomsPalette.Bands` is **5**, and depth 6 already lands in the deepest band. A seventh level with no sixth band is a seventh level that looks exactly like the sixth. **This is a content question before it is a research question** |
| **How it was answered, 0.12.99-dev** | **The sixth band was authored**, which cost no asset: a band is a selection of Core terrain, a stuff and a colour, exactly as the other five are. `RR_Palette_Undercroft`. The band derivation also stopped **wrapping** — at five bands a depth-six coordinate came up Poolrooms on half its seeds, so the deepest place a branch could reach already wore the second shallowest face in the game |

**So T6 was one candidate gated on authoring a band**, and the band was authored at 0.12.99-dev
rather than deferred to the expansion milestone. The two options the queue row offered were a sixth
band or level seven reusing the deepest existing one as a stated limitation; **the first cost
nothing but authoring, so shipping the limitation would have been a choice to ship less.**

---

## The four branches with no candidate, and why each is a finding

### Gate — nothing exists above indefinite

Already recorded in the file. The window ladder's top rung removes the countdown entirely
(`portalIndefiniteTier = 4`), and there is no state above *no countdown*. **A fifth rung would have
to promise something and change nothing**, which is the exact fault four deleted projects had.

### Logistics — every knob is already claimed, and the file already says so

The four tiers it has exhaust the subject: lead time, dispatch delay, order capacity and unattended
delivery. **Zero of the twelve `Procurement` constants are unclaimed** — every one is declared in a
file that reads a capability. What remains there is safety bounds no player will ever reach, which
is the reason the file gives for Logistics having no tier 4 either.

### Commerce — its knobs became player settings, and that is better

**This is the finding the sweep did not expect.** Commerce's candidates were the exchange rates and
the catalogue fee, and at 0.12.98-dev the owner answered a different question with *"Make them
player-visible settings"*. They are now four sliders with the shipped constants as defaults.

**A research tier and a player slider over the same number is two controls fighting.** The player
drags the rate, the project changes it underneath, and neither reads as cause. The right record is
that the slider **replaced** the tier rather than that the tier is missing.

`RR_Cap_OpenMarket` already shows the only honest shape here: the capability switches *which*
setting is read, rather than changing a number the player also owns. A T5 could add a fourth rate
to switch to — and would be a project whose entire effect is *"the slider you already have reads a
different default"*. **That is a promise that changes nothing.**

### Transport and orbital — has no tier 0 on purpose

The eighth branch is deliberately empty at the bottom, so proposing a tier at the top is
incoherent. Its content question is the gravship, which is deferred to the expansion milestone by
owner direction.

---

## What the sweep recommends, in one line each

| | Branch | Tier | Build it? |
|---|---|---|---|
| 1 | Facilities | T5 servicing interval | **Yes** — fills a gap §1.1 itself names |
| 2 | Measurement | T5 trained eye | **Yes** — one step, not uncapped |
| 3 | Spatial | T5 near exit | **Yes** — most visible unclaimed number |
| 4 | Entities | T5 quiet protocol | **Yes, as `MaxEventsPerOpening` only** |
| 5 | Fieldcraft | T5 fourth hand | **Owner's call** — changes the pressure arithmetic |
| 6 | Spatial | T6 seventh level | **Built** — the sixth band was authored rather than deferred |
| — | Gate | none | Nothing above indefinite |
| — | Logistics | none | Every knob claimed |
| — | Commerce | none | Its knobs became player settings |
| — | Transport | none | No tier 0 by design |

**Four to build, one to decide, one blocked on content, four branches honestly empty.** That is
not the symmetric seven-project tier the row might have expected, and the asymmetry is the
accurate answer: *"a tier number is not a promise of a linear chain"* is the file's own rule, and
this is what it looks like applied.

## Links

- [`CAMPAIGN_CHART.md`](../CAMPAIGN_CHART.md) — nine branches, five bands; §1.1 names the four
  factors that decide a gate's window, one of which has no project. **Overrules this document.**
- `Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml` — the 38
  projects, and the recorded reasoning for every absence.
- `tools/check-stated-bounds.py` — why a cap carries its reason, which is what made this sweep
  possible to do by reading rather than by guessing.
