# The crew planner, and missions as distinct from contracts — 0.12.41-dev

**Rows 728, 1031, 1032, 1033**, and the parent row 1028 closes with them. The last two gameplay
systems in the queue; everything after this is housekeeping.

## The queue rows, verbatim

> *"Add crew composition and cargo planner with skill/health/weight/gate-window checks,
> ready/unready reasons, and cost preview. (optional mission UI under the connected-colony
> contract; must not own connection existence)"* (row 728)

> *"have quests and missions and contracts and stuff for like 1000 (odd) cotton or like 10
> uninstalled electic stoves(odd) and the such for all things materials and resources ect ect that
> can give reason for the players to have to advance and excplore and haul and use the spaces iin
> the backrooms"* (rows 1028, 1031)

## The register, checked first

`python tools/register-query.py trace cargo` and `trace expedition-logistics`. The cargo family's
standing instruction is *"preserve each mod's normal material and weight"* — which is why every
mass figure in the planner comes from `MassUtility` and the item, and not one number is authored
here. A planner that quoted its own weights would be wrong for every cargo mod in the register.
Nothing in the family asked for a planner; it constrained how one may measure.

## Row 728: every check it asks for was already enforced. Not one was named

This is the measurement that decided the whole build.

`Dispatch` refuses on **fifteen** distinct grounds. `CheckCrew` collapses **five** of them — wrong
crew size, a duplicate, cannot walk, not employed, and by extension dead, downed, mid-mental-break
or incapable of moving — into the single key **`RR_Exp_InvalidCrew`**. Weight was already checked
(`ExpeditionCargo.CheckCapacity`), hauling was already checked, the operator was already held back,
and the debrief hold was already enforced.

So a player ticks three boxes, presses dispatch, and is told *"invalid crew"* — one message for
five conditions across three people, naming neither the person nor the condition.

**That is row 728.** Not a second set of checks: **the same conditions, attributed.**

| Row 728 asks for | Before | Now |
|---|---|---|
| health checks | enforced, unnamed | five separate reasons, per person |
| weight checks | enforced, unnamed | per-person free space, plus the crew total |
| skill checks | **absent** | best level per field skill, and the gaps named |
| gate-window checks | absent from the planner | the window at the current tier, or "held" at the top tier |
| ready/unready reasons | one key for five conditions | **ten named reasons, one per person** |
| cost preview | **absent** | watt-days for a full window, quoted against the reserve |

### It must not own connection existence, and that is asserted rather than intended

The row's own constraint. `CrewPlanner` returns a **report and never a refusal** — no
`CompanyActionResult` is constructed anywhere in it, and **the proof enumerates every C# file in
the package and refuses any reference to the type from outside `UI/`**. A call from `Dispatch`,
`CheckCrew` or any gate code would make it load-bearing, and that is the thing the claim exists to
catch. Deleting the planner would change no outcome in the game.

Which also means it is allowed to be wrong in the safe direction: if it ever disagreed with
dispatch, the player would be told no by dispatch — never yes by dispatch after being told no here.

### Two things it reads that it would have been easy to reimplement

**The capacity check is `ExpeditionCargo.CheckCapacity`**, not a mass calculation of its own. A
second one would eventually disagree with the one that actually refuses, and the panel would say
ready about somebody dispatch turns away.

**The cost preview reads `OpeningPowerDrawWatts` off `GateFootprint`**, not the raw prop. A second
accessor reading `GateProps.openingPowerDrawWatts` was written, and **the compiler refused it as a
duplicate** — which was the right answer twice over. The existing one scales by cell count and
discounts by `RR_Cap_EfficientAperture`, so the raw prop is not what any gate above 1×1 actually
draws. A preview built on it would have quoted the wrong number for every large gate and every
advanced branch. **Fifteenth time this session a measurement was the defect, and the cheapest — the
compiler found it.**

## Rows 1031 and 1032: what makes a mission a mission

The owner's reason names four things a demand should make a player do: **advance**, **explore**,
**haul**, and **use the spaces**. The odd-supply contract built at 0.7.3-dev pays for **haul and
nothing else** — it draws from the union of everything every coordinate ever produced, and settles
the moment the goods sit at headquarters. A branch with a shelf of odd cotton can fill one without
opening a connection at all.

**A consignment mission pays for the other three.** It names one coordinate, it wants goods *that
coordinate* produced, and it does not settle until a space **at that depth** has been surveyed
further than it had been when the mission was offered. You cannot fill it out of stock, and you
cannot fill it without going deeper and looking around.

| | Contract | Consignment mission |
|---|---|---|
| goods drawn from | every coordinate's union | **the one coordinate it names** |
| settles on | delivery at headquarters | delivery **and** survey work at depth |
| open at once | three | **one** |
| offered every | ~1 day | ~3 days |
| pays | market × 6 | market × 6 **× 2** |
| deadline | none | **none** |

### The obvious design cannot be built, and the code is why

*"Bring back odd goods from coordinate AI-04, verified at settlement"* is the first thing anyone
would reach for. **`ThingOrigin` has three values — Outside, Backrooms, Unknown — and carries no
coordinate at all**, and `CompRimroomsOddOrigin.AllowStackWith` lets odd stacks merge, so a
per-coordinate tag would either break stacking or be lost the first time two stacks met.

So the mission names a coordinate in its **demand** — which definition it wants, drawn from what
that place held — and verifies its field condition against **recorded survey state**, which is
real, saved, and cannot be faked by hauling. The proof asserts the mark still carries no
coordinate, so if that ever changes the claim fails and the mission can be made stricter.

### No deadline, and that is not an omission

`check-campaign-absolutes.py` refuses to let this package ship an expiry under any name, and the
absolute applies here exactly as it does to a request: the company waits as long as it takes. **A
mission is harder than a contract because of what it asks, never because of a clock.** A plant that
adds an `expiryTick` to the mission is caught.

### One settlement path, deliberately

`SettleSupplyContracts` gained **one call** to `FieldConditionMet` rather than growing a second
settlement path, because two paths that both consume goods and both pay money will eventually
disagree about one of them. **A record with no field condition reports true** — every contract
written before this checkpoint, and every plain contract written after it — so nothing about
existing behaviour changes. The saved fields default to zero for the same reason.

The condition is checked against **any** coordinate deep enough rather than the named one, because
a named coordinate can fail generation through no fault of the player and a permanently
unsatisfiable mission is worse than one satisfied somewhere else at the same depth.

## Row 1033: the pane was not silent about odd demands. It was wrong about them

The row says *"the Operations pane does not list them."* It understates it. The pane listed every
contract and printed **`RR_UI_ContractTerms` on all of them** — which is the *survey* contract's
terms, written for a different job. So a demand for two hundred odd cotton displayed *"Survey the
route, record the distortion, recover the record book and analyse it at headquarters."*

**A confident wrong answer is worse than silence.** Silence sends a player looking; this stopped
them.

Meanwhile `requiredThingDefName`, `requiredCount` and `deliveredCount` were saved, given public
accessors, and **read by nothing but the settlement code** — the defect class `check-wiring.py`
exists for, in C# where it cannot see it.

The pane now says what is wanted, how much has been handed over, that ordinary stock will not do,
and — for a mission — which coordinate it came out of, the survey progress toward the requirement,
and whether the requirement is met. The survey terms are still shown on a survey contract, because
they were right for the contract they were written for.

## The proof, and what the plants found

`.local/register/proof-planner-and-missions.py` — **thirty-eighth proof**.
`.local/register/plant-planner-and-missions.py` plants **48 faults** and all 48 are caught.

**The baseline check earned its place on the first run.** A patch to the proof left a syntax error
in it, the proof exited non-zero unconditionally, and **the harness refused to plant anything and
said why** — which is exactly the 0.12.39-dev failure that the baseline check was added to prevent,
reproduced and caught one checkpoint later.

**The first sweep caught 39 of 47, and six of the eight misses were the same defect as last
batch: a claim that tests a mention rather than a use.**

* `"TotallyDisabled" in planner` — the gap finder stopped consulting it and the claim passed,
  because `BestLevel` mentions it too. Both readers are now asserted.
* `"MassUtility.CanEverCarryAnything" in planner` and `"CrewPlanner.MaxCrew" in planner_pane` —
  each has **two** use sites, and a plant on one left the other matching. Both are now **counted**.
* `"return -1f;" in planner` — appears three times in that one method, so it said nothing about
  which branch survives. The guard is matched whole.
* `"RR_Plan_Reserve" in planner_pane` — a **prefix of `RR_Plan_ReserveShort`**, so the warning
  alone satisfied it. Matched on the `.Translate(` call.
* `"IsOddConsignment" in records` — a **prefix of any renaming of it**, so appending `Unused` to
  the property passed. Declaration and both readers now.
* `"ConsignmentPremium" in missions` — the constant existing is not the claim; the multiplication
  is.

Two were **weak plants**: one wrapped a label in `var unused = (...)` and called it a refusal when
it was neither, and one replaced a `MassUtility` call at a single site out of two.

**The lesson, stated once because it has now cost two batches:** *a name is a substring of its own
declaration, of any renaming of it, and of every other symbol that starts with it.* A claim worth
making is a claim about a **call**, and if a call happens twice the claim is about **how many
times**.

## Build

**196 C# files, 89 package files**, zero warnings, zero errors. Assembly SHA-256
`5670CA7C784A5E11B2A50DBEC461B469D015727A8B453711FB35E938C7270C69`, reproduced by two clean
recompiles. **Twelve checkers pass, thirty-eight proofs hold**, all read by exit status.

No game was launched. Nothing here has been played.
