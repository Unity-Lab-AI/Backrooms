# Design briefs — the three alternate starts

**Owner direction, 2026-10-05, asked which of three options to take on the outpost,
town-distortion and company-in-crisis openings. Verbatim:** *"Write briefs for all three"*.

The option chosen was described as *all three get a full brief before any code*, and the queue row
it answers states the condition in its own words: add these starts *"only after a design brief
defines their starting state, pressure, failure/recovery, and acceptance evidence."*

So each brief below has exactly those four sections, plus the two the shared contract adds and
these three starts have most trouble with: **convergence** and **the dependency boundary**.

**Nothing here is code.** No scenario def, gen step or scen part is written against this document
until the owner has read it. That sequencing is the owner's and it is the point of the answer:
building an opening on a guess is how it gets built twice.

---

## What binds all three before any of them is designed

These are not brief-specific. They are the rules a new start is most likely to break without
noticing, and each is enforced rather than remembered.

**The only clock is the gate.** `CAMPAIGN_CHART.md` §1.1, and it is the reason two of the three
candidate premises in `SCENARIOS.md` needed rewriting rather than expanding. `town_distortion`'s
recorded pressure was *"time pressure"* and `isolated_outpost`'s was *"uncertain evacuation"*. A
settlement start cannot run a countdown toward residents dying, and an outpost cannot run one
toward an evacuation window. **The pressure has to be a cost that grows, not a clock that ends.**

**Every offer has at least two ways to succeed, of at least two different kinds.** §1.2. Each
brief below names its opening offer's routes and their kinds explicitly, because an opening
request is the first offer a player ever sees and the one most likely to ship with one route.

**No first objective may be gated on a specific provider.** Zero dependencies are declared, so
Core content is the *supported* configuration rather than a fallback. Where a brief names an
optional mod it names what happens without it in the same sentence.

**Three gates, five maps, three crew.** `MaximumOperationalGates = 3`, `CrewPlanner.MaxCrew = 3`,
and the open-map budget reads the player's own `MaxNumberOfPlayerSettlements` with a floor of two.
A start that needs four simultaneous maps to make sense cannot be built as described.

**A coordinate's room at index 0 must be the threshold room.** `DestinationService` requires it
and the genstep takes `First(...)` of it. Any start that begins *inside* a coordinate inherits
this, which is why `lone_survivor` works and why a start claiming the player arrives somewhere
other than a threshold would not.

---

## 1. `isolated_outpost` — the post that is still company property

**Premise, from `SCENARIOS.md`:** *"A remote company post loses its radio relay and supply
link."* Distinct pressure as recorded: *"Small crew, low stock, unreliable communications, and
uncertain evacuation."*

### Starting state

One 50×50 surface map, the player's own company faction, **three** staff — the ceiling is three
crew and an outpost that cannot field a full crew teaches the wrong lesson about the cap.

The post has a working but **uncertified** gate: assembled, powered, and refused by the
certification check until its three train bills are complete. That is the single most important
choice in this brief and the reason to prefer it over a broken gate. A broken gate is a repair
job; an uncertified one is the branch discovering that its paperwork is load-bearing.

Starting stock is deliberately below what one opening costs: enough steel and components to finish
*either* the certification bills *or* the relay, not both. A **destroyed relay**, already on the
map as rubble. Food for four days. No bonds, no account access, and **150 silver in petty cash**
— the same physical float the facility start has, because the account is what is missing.

Known coordinates: **one**, saved with its seed and generator version, recorded by a crew that is
no longer here. That record is the start's only asset and the hook for its first objective.

### The pressure, and why it is not a clock

The pressure is **an account it cannot reach**. The post is company property with a ledger it
cannot post to, so procurement is unavailable: no dispatch, no lead time, no catalogue. Everything
has to come out of the coordinate or out of what is already on the map.

That is a cost that grows rather than a clock that ends. Food runs down, the reserve drains, and the
generator needs fuel — all ordinary RimWorld needs, all visible, none of them a countdown against
a task the player was asked to do. **Nothing expires. Nothing is cancelled for slowness.**

The second pressure is the one the premise names and §1.1 forbids expressing as time: *"unreliable
communications"*. It becomes a **confidence** property instead of a timer. Until the relay is
rebuilt the branch's own records are marked unverified, and an unverified record is worth less at
exchange — a price, not a clock.

### The opening offer and its routes

One already-accepted standing order, inherited from the crew that left: **restore reporting**.

| Route | Kind | What it is |
|---|---|---|
| Rebuild the relay | **Deliver** | Recover components from the coordinate and rebuild it |
| File the backlog by hand | **Document** | Complete the three certification bills and submit the dead crew's own records through the gate instead of over the air |
| Hand the post over | **Decline-and-redirect** | Report the post unrecoverable, keep the coordinate record, and take the assessment fee |

Three routes, three different kinds. The second is the designed one: it teaches that a record is a
deliverable, which is the whole `Document` route kind and the thing new players miss.

### Failure and recovery

**No softlock is reachable and each guard already exists.** An uncertified gate refuses with a
named reason and a fix. A dead generator stops openings and nothing else. A lost crew does not
vanish: `LostPawnRegister` stores names and a stranded crew survives and can be fetched, which is
a rescue lead rather than a loss.

If every colonist dies the post's coordinate, records and case survive as a lead a later company
start can pick up, exactly as `lone_survivor` already does. If no route can be generated for the
one known coordinate, the gate stays closed and a reroll is offered under a new coordinate ID.

The recovery that needs stating because it is new: **a post with no account and no relay can still
Release the gate**, and Release is permanent and loses stock. That has to be refused with its
consequence named up front, not confirmed quietly — releasing the only gate on a post with no
procurement is the one genuinely unrecoverable act available here.

### Acceptance evidence

1. The start appears in selection with an accurate summary, and reloading it does not duplicate
   pawns, the rubble, the petty cash or the inherited order.
2. The known coordinate reopens under its **saved** ID, seed and generator version after a
   reload — never a silently new destination.
3. The gate refuses to open, with the certification reason and the three outstanding bills named,
   on a fresh start.
4. All three offer routes complete independently on **Core only**, each posting once.
5. Procurement is visibly unavailable with its reason, and becomes available the moment reporting
   is restored by any of the three routes.
6. No clock anywhere: `check-campaign-absolutes.py` green against the start's own text.
7. A `Player.log` from an owner launch, because none of 1–6 is proved from here.

### Convergence and dependency boundary

Restoring reporting makes the post an ordinary branch on the corporate network with its ledger,
catalogue and request board live. Declining makes it a solo site that trades through the gate
alone. Both routes enter the same coordinate atlas and evidence custody.

**Core-only is the supported configuration.** The relay is built from Core components. Nothing in
the opening reads an optional provider; with storage or hauling mods present the post is more
pleasant and no objective changes, which is the register's recorded disposition for that whole
family — use native, keep the vanilla fallback, no patch.

---

## 2. `town_distortion` — the opening that belongs to somebody else

**Premise, from `SCENARIOS.md`:** *"A settlement reports an unstable opening and missing
residents."* Distinct pressure as recorded: *"Public safety, witnesses, time pressure, perimeter
security, and limited authority."*

### Starting state

One 60×60 map containing a **neutral settlement faction's** town and, at its edge, a natural
gate. The player controls **three** contracted investigators who do not own the ground they are
standing on. That is the whole design: this is the only start where the map is not yours.

The gate is **natural and permanently open** — not a machine gate, not assembled, not powered, and
not the player's to close. Natural depth runs to **6**, and this one sits shallow, so what comes
out of it is yellow rooms rather than the Wrong band.

Starting kit is an investigator's rather than a company's: a recorder, survey tags, a sealed
evidence case, two days of food, basic medicine, one firearm between three. A **provisional
advance** against a quoted contract, and no facility, no machine gate, no research.

**Residents are already missing when the scenario begins**, and the number is fixed and saved
rather than rolled per reload. Townspeople are present as the settlement faction's own pawns and
are not the player's to command, which is what *"limited authority"* means mechanically.

### The pressure, and why it is not a clock

The recorded pressure says *"time pressure"* and **that is superseded.** §1.1 is explicit: no
countdown on anything a player is asked to do, and a settlement cannot run a timer toward
residents dying. Nothing here expires and nothing is cancelled for slowness.

What replaces it is **standing**. The settlement faction's opinion of the branch moves with what
the player actually does — a perimeter that holds, residents accounted for, a cordon respected.
Goodwill is a Core mechanism, it is visible, it responds to action, and losing it costs trade and
access rather than ending a mission.

The second pressure is **the authority the player does not have**. A town pawn can walk into the
gate. The player cannot forbid it, only make it less likely by boarding up and cordoning — and
boarding up is 25 wood and 420 ticks, which is cheap, which is the point: the tool is available
and the decision is whether to use it on somebody else's property.

### The opening offer and its routes

One investigation contract, offered by the settlement rather than the corporation, which is the
first time a player sees an offer from anyone else.

| Route | Kind | What it is |
|---|---|---|
| Account for the missing | **Deliver** | Enter the gate and bring people back, alive or otherwise |
| Explain the opening | **Document** | Record the distortion and the depth band, and deliver the analysis instead of the residents |
| Seal and monitor | **Substitute** | Board the gate, establish a watched perimeter, and satisfy the request with containment rather than answers |
| Call in the corporation | **Decline-and-redirect** | Hand the site to the parent company and take the finder's fee, losing the settlement's goodwill |

Four routes, four kinds. The fourth is deliberately the one with a cost the player can see before
choosing it, because an offer whose routes are all equally good is not a decision.

### Failure and recovery

A missing resident who is never found stays a **case** rather than becoming a failure state. A
resident killed in the gate costs goodwill and does not end the contract — §1.2 means there is
always another route still open.

A breached perimeter raises an incident and limits access; it does not delete the town. If the
settlement's goodwill reaches hostile the contract is not cancelled, it is **re-routed**: the
corporation's finder's-fee route stays available, which is why that route exists.

The player cannot be locked out of the map they started on. The natural gate is permanent, so the
one state that could strand the branch — a closed route home with the crew inside — is
unreachable here by construction.

### Acceptance evidence

1. Reload does not duplicate the advance, the kit, the missing-resident count or the contract.
2. The natural gate is permanently open after a save, a reload and a revisit, and its coordinate
   reopens under its saved ID and seed.
3. All four routes complete independently on Core only, each posting once, and the goodwill cost
   of the fourth is applied exactly once.
4. Town pawns remain the settlement faction's throughout; nothing silently recruits one.
5. A boarded gate stays boarded across a reload, at 25 wood and 420 ticks.
6. `check-campaign-absolutes.py` green against the start's own text -- this brief's own
   premise had to be rewritten for exactly that reason.
7. An owner `Player.log`.

### Convergence and dependency boundary

Completing the investigation by any route opens a paid follow-on and a branch ledger. The
monitored-site route turns the town into a permanent watched location on the corporate network;
the corporation route converts it into a company site the player no longer has goodwill at.

**Core-only.** Visitors and the settlement faction are Core mechanisms, which `SCENARIOS.md`
already requires of `furniture_knickknack_store` for the same reason and in the same words:
Hospitality *"may not be a single point of failure for an opening."* With Hospitality present the
town reads better; without it nothing in the opening changes.

---

## 3. `company_in_crisis` — the branch that is already running

**Premise, from `SCENARIOS.md`:** *"An existing branch begins with debts, damaged infrastructure,
and a missing crew."* Distinct pressure as recorded: *"Payroll, security, reputation, and recovery
compete with research and expansion."*

### Starting state

One 60×60 headquarters map — the facility start's own layout, **damaged**. Three staff, down from
a crew the save says was larger. The player's own company faction.

This is the only one of the three that begins **mid-campaign**, and that is its whole reason to
exist: every other start teaches the loop from zero. This one starts a player at the point where
the loop has already gone wrong, which is a different game and the one the request board's later
arcs are written for.

Concretely, and every figure here is a property the code already has:

- **A negative ledger balance** and a live payroll obligation. The account is real and it is
  short. Payroll is a recurring cost with a schedule label, never a thing that can be failed, and
  nothing reads a due tick punitively.
- **A gate below its integrity floor.** `IntegrityFloorFraction` is `0.5f`, so a gate under half
  integrity refuses to open and says so. The gate is present, assembled, certified — and refused.
- **A crew already stranded on the far side**, named in `LostPawnRegister`, on a coordinate whose
  ID, seed and generator version are saved. They are alive. They can be fetched.
- **Research partly done**: two or three projects complete across different branches, so the
  player starts with capability they did not earn and a tree they have to read.
- Stock worth less than the debt, and **bonds** rather than silver, because a bond banks at full
  value and that is the one piece of good news in the opening.

### The pressure, and why it is not a clock

The pressure is **competition for one pool of money**, which is exactly what the premise says and
is the cleanest expression of §1.1 of the three briefs. Payroll, gate repair, and the rescue all
want the same credits. Nothing expires; the branch simply cannot do all three at once.

Choosing is the game. Repair first and the crew stays out longer. Rescue first and payroll lapses,
which costs mood and standing rather than ending anything. Pay first and neither happens yet.

The stranded crew is the pressure that would be a timer in almost any other game and **is not one
here**. They survive. They do not starve on a schedule, they are not lost after N days, and the
rescue lead does not expire. What grows is the cost of the choice, not a countdown.

### The opening offer and its routes

The request board opens with the parent corporation's audit, which is a request rather than a
threat because §1.1 forbids the threat.

| Route | Kind | What it is |
|---|---|---|
| Clear the arrears | **Purchase** | Bank the bonds, sell what is in range, and post the balance |
| Account for the crew | **Document** | Deliver the loss record and the coordinate; an honest accounting satisfies the audit |
| Bring them back | **Deliver** | Repair the gate above the integrity floor and fetch them |
| Testify | **Testify** | A staff member's account of what happened, where a crew saw what a record would have shown |

Four routes, four kinds, and the `Testify` route is here because this is the one start where a
surviving witness to the branch's own disaster exists. That makes it the natural place to teach a
route kind the other starts can only gesture at.

### Failure and recovery

**The stranded crew is the recovery, not the failure.** The guarantee already holds: they survive,
`DeinitAndRemoveMap` is reached from exactly one place and it is a player action, and the register
stores names rather than pawn references so nothing is dropped by a map unload.

A lapsed payroll costs mood and standing. It does not end the branch, seize the facility or cancel
the audit. A gate that cannot be repaired leaves the Document and Testify routes open, which is
§1.2 doing the work it exists for.

The unrecoverable act available here is the same one as in `isolated_outpost` and needs the same
treatment: **Release is permanent and loses stock.** Releasing a below-floor gate on a branch in
arrears has to state that consequence before it is confirmed, because a player reading the gate as
useless is the player most likely to release it.

If every colonist dies, the branch's coordinates, records, cases and the stranded crew all persist
as leads. A start whose premise is *recovery* must not be the one start that loses state on death.

### Acceptance evidence

1. Reload does not duplicate the debt, the payroll obligation, the bonds, the damage, the
   completed research or the stranded-crew register entry.
2. The gate refuses to open with the integrity reason named, and opens once repaired above
   `IntegrityFloorFraction`.
3. The stranded crew survive a save, a reload, a map unload and a revisit, and can be fetched.
4. All four routes complete independently on Core only, each posting once.
5. The completed starting research grants exactly the capabilities it should and no others —
   the capability bijection holds, which is 34 granted and 34 read today.
6. Payroll lapses without ending anything, and nothing reads a due tick as a penalty.
7. `check-campaign-absolutes.py` green.
8. An owner `Player.log`.

### Convergence and dependency boundary

This start *is* the company campaign from its first tick; there is no convergence step to design.
What it needs instead is an **exit from crisis** that is legible: the audit closed by any route
returns the branch to ordinary standing, and from there it is the facility campaign.

**Core-only**, and this is the start where that is easiest to get wrong. Starting research must
not include a project whose capability only matters with an expansion present, or the opening hands
a Core-only player capability they cannot use. The three completed projects must be chosen from
branches whose effects are Core-readable.

---

## What is NOT in these briefs, deliberately

**No numbers are presented as approved.** Every count, dimension and figure above is a hypothesis
in the same sense the `SCENARIOS.md` start cards say of themselves: *"tuning hypotheses, not
owner-approved canon."* Where a figure is a property of the shipped code — three gates, three
crew, depth 6, the half-integrity floor, 25 wood, 420 ticks, the five-band palette — it is stated
as such and is not a hypothesis.

**No implementation order.** Which of the three to build, or whether to build any, is the owner's
call and the brief exists to make that call possible rather than to pre-empt it.

**No co-op claim.** All three are solo until a pinned-profile result exists, per D1, which is
unchanged.

---

## Links

- [`SCENARIOS.md`](SCENARIOS.md) — the shared contract every start must satisfy, and the three
  candidate rows these briefs expand.
- [`CAMPAIGN_CHART.md`](CAMPAIGN_CHART.md) — §1.1 the only clock is the gate, §1.2 two routes of
  two kinds. **Overrules any prep document, including this one.**
- [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md) — setup
  refinements and the tile-selection rule.
- [`THREAT_DESIGN_SHEETS.md`](THREAT_DESIGN_SHEETS.md) — the fairness frame every encounter in any
  start is bound by.
