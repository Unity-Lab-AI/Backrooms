# The campaign chart — missions, tech linkage, research tree

**This document is the authority on campaign structure.** It exists because of an explicit
owner instruction to complete the chart *before* building any of the content that hangs off it.

> *"make sure the whole mission line and tech linkange and research tree line chart is full
> complete before you start building out all the corporation requests tech research lines and all
> of that and any and all things i didnt mention that apply before you randomly and will nilly
> build out the scenerio quests that all should play out like a tutoriasl of sorts that turn open
> ended to campaine and nothing ever ever have time restripctions but the gate(ie power tech and
> maintanance and workflorce and other factors all determine the time a gate can be open) but
> missions and quests and offeres and trades are never time senstive the company will wait as
> long as possible for you to complete their task offers and never offer only one path but
> multiple success routes"*

Where this document and a prep document disagree, **this one wins and the prep document is
corrected**. Two of the owner's rules below directly contradict language that had been sitting in
four prep documents since Gate 0, and building from those documents would have built the wrong
mod.

---

## 1. The two absolutes

These are not design preferences. They are stated as *never* and *always*, and both are
**enforced by `tools/check-campaign-absolutes.py`** rather than trusted to memory.

### 1.1 The only clock is the gate

> *"nothing ever ever have time restripctions but the gate(ie power tech and maintanance and
> workflorce and other factors all determine the time a gate can be open)"*

A gate's connection has a duration. **Nothing else in this mod has a duration.** And the gate's
duration is not a timer set against the player either — it is the *consequence* of things the
player controls:

| Factor | Effect on how long a connection holds |
|---|---|
| **Power** | The reserve drains per tick; an empty reserve ends the opening |
| **Tech** | The window-tier ladder multiplies the base window; the top rung removes the countdown entirely |
| **Maintenance** | A lapsed assembly blocks the *next* opening — deliberately never the current one |
| **Workforce** | An operator off station, or no operator at all, is a failure state |
| **Other physical factors** | The kill switch, a broken battery, EMP, a game condition disabling electricity |

Every one of those is a thing the player can see, understand and act on. That is what makes the
gate's clock legitimate while a deadline on a contract is not.

**What this forbids, explicitly:**

- No expiry on a mission, quest, offer, contract, quote or trade.
- No penalty for delay. No cancellation for slowness. No "respond within N days".
- No timed investigation, including the *"timed distortion investigations"* and
  *"consequences for delay or abandonment"* that four prep documents promised. **Superseded.**
- No countdown on anything a player is asked to *do*.

**Clocks that remain, and why each is not a deadline** — the allowlist the checker enforces:

| Clock | Why it is legitimate |
|---|---|
| The gate's opening window and emergency return window | The one permitted clock, named in the direction |
| A glow pod's lifespan | Core content behaving as Core content. A pod designated as a marker is **held at zero**, so the player's own markers never expire |
| A travelling deployment's lease | Releases a reservation for a worker who never arrived. **A deployed worker has no countdown at all**, by an existing comment. Nothing is lost when it drops |
| Procurement dispatch delay and lead time | **Delivery takes time. That is not a deadline** — nothing is asked of the player and nothing fails. It is the supplier being slow, not the player being late |
| `nextRequestTick` on hiring, `PlanningCooldownTicks` | Cooldowns *before* the player may act again. A cooldown cannot be failed |
| Payroll's `NextPayrollTick`, an obligation's `dueTick` | A recurring cost and a schedule label. Nothing reads `dueTick` punitively |
| Ticks recording *when something happened* (`analyzedTick`, `closedTick`, `arrivalTick`, …) | History, not a countdown |

The distinction the checker encodes: **a delay is fine, a cooldown is fine, a record is fine; a
deadline is not.** If time passing can make a thing the player wanted become unavailable, it is a
deadline.

### 1.2 Every offer has at least two ways to succeed

> *"never offer only one path but multiple success routes"*

Every corporation request, mission, quest and contract must declare **two or more** completion
routes. One route is what an offer naturally has unless somebody insists otherwise, so the
checker requires it of every offer template as they are built.

Route kinds this chart uses, so that "multiple routes" means something concrete rather than two
labels on the same act:

| Route kind | Example |
|---|---|
| **Deliver** | Bring the thing back |
| **Document** | Bring the *record* back instead of the thing — analysis rather than salvage |
| **Substitute** | Satisfy the request with a different item of the same capability |
| **Purchase** | Buy the shortfall through procurement rather than recovering it |
| **Testify** | A staff member's account, where a crew saw what a record would have shown |
| **Decline-and-redirect** | Refuse the stated task and complete a related one the corporation also wants |
| **Research** | Complete a named company project |

**The `Research` kind was added in 0.11.2-dev**, when tutorial request 6 offered *"complete Field
Stability"* and none of the six above covered it. This table was always *"route kinds this chart
uses"* rather than a closed set; research is a thing a branch does, and it is not a delivery, a
document, a substitute, a purchase, a testimony or a redirect.

**A request is well-formed when at least two of its routes are of different kinds.** Two deliver
routes that differ only in which shelf the item lands on is one route wearing two hats.

---

## 2. The arc: tutorial that becomes a campaign

> *"that all should play out like a tutoriasl of sorts that turn open ended to campaine"*

The teaching is **the first three arcs being played**, not a tooltip layer. There is one designed
transition point rather than a fade-out.

| Phase | Arcs | What it is | How it teaches |
|---|---|---|---|
| **Tutorial** | 1–2 | A guided line with one obvious next action at every step | By requiring each system once, in dependency order, with the corporation asking for it |
| **The hinge** | 3 | **The designed transition.** The last guided request, and the first where the corporation offers a *choice* of what to pursue next | The player is asked to pick a direction for the first time |
| **Campaign** | 4–8 | Open-ended. Requests are generated from branch state, coordinate history and capability | Nothing new is taught; everything is combined |

**Corrected 0.11.2-dev.** This section previously said the hinge is where *"contact with the
corporation"* completes. That is not right, and the owner's answer at the fork is why:

> *"Async industries starts with this tech research and other basic gate techs it needs to operate
> and begin researching and gate operations at basic levels but the other two scenerios need
> special treatment in theri layout and starts"*

**Contact is a branch state, not a point on the tutorial line.** `beginsInCorporationContact`
decides where a start opens:

| Start | Opens in contact | What the tutorial line is for it |
|---|---|---|
| **Async Industries** | **Yes** | Training, paid for by a company that is already invested. The rescue applies from the first minute |
| **Store** | No | Its own layout, and **reaching contact is the achievement** |
| **Solo/Group** | No | Same, from a different point of view |

So the hinge is where the **tutorial** ends and the campaign opens, for every start. Whether the
corporation is already watching when you get there depends on which start you chose, and for two
of the three, **there is no rescue until you earn contact.** That absence is what makes those two
openings frightening.

### The eight arcs, from the prep material

Taken from `CAMPAIGN_CONTENT_CATALOG.md` rather than invented, with each arc's clock language
removed per §1.1.

| Arc | Player-facing | Built? |
|---|---|---|
| **1. Keep the doors open** | Small facility, five staff, unfinished gate. Power the site, assign an operator, bring home a record | **Mostly built** — gate, spin-up, operator, evidence |
| **2. Measure before trusting** | Familiar spaces reveal patterns, reports disagree. Decide what to measure | **Partly** — markers, logs, revisit displacement, coherence |
| **3. Return with control** | Known destinations become working routes; every opening costs power, staff, food, wear | **Partly** — the window ladder, address book, servicing |
| **4. Make a business of it** | Clients request surveys, samples, instruments, rescue, secure access | **Partly** — procurement, payroll, bonds, corporate trader; **one** contract template |
| **5. Build beyond headquarters** | Remote sites need people, supplies, signals, protection, an exit | **Not built** |
| **6. Respond to the outside world** | Openings appear in towns. Witnesses, missing residents, public danger | **Not built.** Its prep description was the worst offender against §1.1 |
| **7. Expand industrial reach** | Heavy cargo and staff across the wider world; optionally space | **Not built.** DLC-optional throughout |
| **8. Enter deeper systems** | Later coordinates combine known families, then introduce one unfamiliar rule at a time | **Partly** — depth bands, archetypes, pressure ladder |

---

## 3. The research tree

**Seven tiers and nine branches.** The first five are `CAMPAIGN_CONTENT_CATALOG.md`'s; tiers 5 and 6
were swept for and chosen at 0.12.99-dev. *This line read "Six tiers" until 2026-10-06, while the
table below it listed seven and §3.2's own summary said seven — the count was never updated when the
second of the two new tiers landed.* **Tiers are progression bands,
not a promise that every branch is a linear chain** — that caveat is the prep material's own and
it is kept, because §1.2 needs alternate routes through the tree as much as through a mission.

### 3.1 Tiers

| Tier | Meaning |
|---|---|
| **0 — Facility foundations** | Make the company safe enough to work |
| **1 — First entry** | Prepare a measured short expedition and read a first return |
| **2 — Repeatable operations** | Revisit known coordinates; reduce preventable failures |
| **3 — Remote operations** | Support more than one site; work beyond headquarters |
| **4 — Deep operations** | Combine known techniques; extend reach |
| **5 — The settled branch** | Service, read and leave a space on the branch's own terms |
| **6 — Deep Reach** | One project, and it is the top of the whole tree |

**Tiers 5 and 6 were added at 0.12.99-dev and the top is RAGGED ON PURPOSE.** Five branches reach
band 5, one of those reaches band 6, and three reach neither; and every absence is a finding recorded beside the tier it is absent from in
`RR_CompanyProjects.xml`. The sweep that produced it is
[`research/RESEARCH_T5_T6_SWEEP.md`](research/RESEARCH_T5_T6_SWEEP.md), and the bar it applied is
the one this chart implies: **a tier may only exist where a player could name the effect in one
sentence, from play, without reading source.**

### 3.2 Branches, and what each already has

**Measured out of `RR_CompanyProjects.xml` rather than remembered.** An earlier version of this
table said *"—"* for seven of the nine branches long after they were built, which is the worst
failure mode a chart has: a document that understates the work reads as a to-do list and gets the
same thing built twice.

| Branch | Built rungs | Top band | Nothing above it, because |
|---|---|---|---|
| **Gate engineering and stability** | **All four**: Telemetry → Field Stability → Sustained Aperture → Standing Connection | 3 | the top rung already removes the countdown, and there is no state above *no countdown* |
| **Facilities and power** | all six: reserve, aperture, standby, sites, dialling, servicing | **5** | — |
| **Fieldcraft and medicine** | all six: drill, rescue, relief watch, way home, decompression, standing relief | **5** | — |
| **Measurement and evidence** | all six: second reading, corroboration, standards, rapid survey, statements, the trained eye | **5** | — |
| **Spatial mapping and topology** | all seven: atlas, alternate exits, known address, coordinate reading, surface reading, the near exit, deep reach | **6** | — |
| **Entities and containment** | all six: early warning, detection, containment, space discipline, steady nerve, quiet protocol | **5** | — |
| **Communications and logistics** | four: standing orders, relays, forward dispatch, unattended delivery | 3 | every Procurement knob is claimed; what is left are safety bounds no player reaches |
| **Commerce and organisation** | five: terms, leases, recruitment, site economies, open market | 4 | its remaining knobs **became player settings**, and a project over a slider you already own is two controls fighting |
| **Transport and orbital support** | none, deliberately | — | **no tier 0 by design.** DLC-optional throughout, and a top on an empty branch is incoherent |

**Forty-four projects across nine branches and seven bands.** The gate branch is the spine and was
completed first, at 0.10.9-dev; the eight others were written between 0.12.5-dev and 0.12.99-dev,
with four tier-3 projects deleted along the way for promising something and changing nothing.

### 3.3 The linkage rule

A project's prerequisites are of exactly three kinds, and no others:

1. **Completed logs** — route, distortion, entity. *"u need certain logs complete to operate the higher teri techs"*
2. **Prerequisite projects** — a named rung below it.
3. **Insight** — the price, not the qualification.

**No project may require a thing that only time can provide.** That is §1.1 applied to the tree,
and it is why there is no "operate for N days" prerequisite anywhere in this chart.

**Every tier above 0 must be reachable by more than one path.** §1.2 applies to the tree: a branch
that can only be entered through one project is a single point of failure for a player who has
not happened to generate the right log.

---

## 4. The mission line

### 4.1 Shape of a corporation request

| Field | Rule |
|---|---|
| What is wanted | Stated plainly before acceptance |
| Payment | Stated before acceptance. Advance, milestone and bonus allowed |
| **Routes** | **Two or more, of at least two different kinds** (§1.2) |
| **Expiry** | **None. Ever.** (§1.1) |
| Penalty | **None for delay.** A penalty for a *destroyed* deliverable is a consequence of an act, not of a clock |
| Cancellation | The **player** may cancel. The corporation may not |

### 4.2 The line, by phase

| # | Request | Arc | Teaches | Routes |
|---|---|---|---|---|
| 1 | **Power the gate** | 1 | reserve, wiring, the console | build a battery · buy one · bind an existing one |
| 2 | **Assemble and calibrate** | 1 | the bill, the operator | assemble on site · requisition a finished assembly |
| 3 | **Bring back one record** | 1 | surveying, the book, the archive | survey and analyse · recover an existing record from a coordinate |
| 4 | **Mark a route home** | 2 | markers, colour meaning | place and mark pods · testify from a crew account |
| 5 | **Report a disagreement** | 2 | distortion logs | analyse a distortion record · two crew accounts of the same room |
| 6 | **Hold a connection open** | 3 | the ladder, power draw | complete Field Stability · buy a longer window as a service |
| 7 | **The hinge: choose a direction** | 3 | **the transition** | declare a direction · say nothing and go do something · take the aperture further. **Every choice is a success** |

**The hinge's routes were corrected in 0.11.2-dev, by the two-kinds rule biting on this chart's
own content.** As first drawn — *"pick any one of the eight branches"* — every route would have
been the same kind, which fails the rule that a request offers two routes of two **different**
kinds. Rather than carve out an exception, the hinge was redesigned, and the redesign is better:
you may **declare** a direction, or you may simply **go and do something** in one and let the work
speak. *"Every choice is a success"* is more true when nothing has to be announced.
| 8+ | Generated | 4–8 | nothing new | generated from branch state, coordinate history, capability |

Requests 1–6 are the tutorial and are **fixed**. Request 7 is the hinge. Everything after is
generated.

### 4.3 The corporation's character

> *"the mega mother corp is greedy and will basic do anything and put up with anything to make
> sure you succssed"*

Greed is the *mechanism* for the patience, not a contradiction of it. An investor protecting an
investment does not withdraw it for slowness. Three consequences:

1. **It waits.** §1.1 is in character, not a concession.
2. **It offers routes.** §1.2 is in character: it does not care *how* the branch succeeds.
3. **It will not let a facility die** — the clean-up team, scoped to the Store and Solo/Group
   starts after contact. Queued, and designed only once this chart is settled.

---

## 5. What the prep material got wrong, and is corrected

| Document | Said | Now |
|---|---|---|
| `CAMPAIGN_CONTENT_CATALOG.md` arc 4 | contract states its *"deadline"* | states its routes |
| `CAMPAIGN_CONTENT_CATALOG.md` arc 6 | *"Timed distortion investigations … consequences for delay or abandonment"* | untimed; consequences for **abandonment**, never for delay |
| `CAMPAIGN_CONTENT_CATALOG.md` missions | *"any deadline, payment, bonus, penalty"* | no deadline field exists |
| `CAMPAIGN_ECONOMY_MODEL.md` | contract card names a *"deadline"*, quote generated from *"deadline"* | removed from both |
| `CAMPAIGN_ECONOMY_PROGRESSION.md` | contract names its *"deadline"* | removed |
| `CAMPAIGN_ROSTER_FREEZE.md` | *"Deadlines and local trust matter"*, *"arrival window and consequence of failure"* | trust matters; deadlines do not |

**Nothing was built from these lines**, which is the good news and is exactly why the owner's
instruction to finish the chart first was the right call: the content that would have carried the
deadlines into the game does not exist yet.

---

## 6. What is not yet decided, and is the owner's

Named rather than guessed, and none of it blocks the next checkpoint:

1. ~~**Where the hinge sits precisely**~~ — **built after request 6 as drawn.** Still movable: it is
   one `tutorialOrder` value and one prerequisite, and the proof asserts the line stays contiguous
   and acyclic whatever it is changed to.
2. **Whether the eight branches unlock in any order after the hinge**, or whether some require a
   tier-2 gate rung first.
3. **How generated requests pick their routes** — a fixed route set per request family, or routes
   derived from what the branch happens to have.

---

## 7. Build order this chart authorises

1. ~~The gate branch~~ — **done, 0.10.9-dev.**
2. **The two absolutes made enforceable**, and the existing breaches removed. *(This checkpoint.)*
3. The prep documents corrected. *(This checkpoint.)*
4. ~~The offer/request def shape, with routes as a first-class field.~~ **Done, 0.11.1-dev.**
5. ~~Tutorial requests 1–6, then the hinge.~~ **Done, 0.11.1-dev and 0.11.2-dev.**
6. The remaining eight research branches, tier 0 → 2 first.
7. The clean-up team that means a facility never dies.
8. Arcs 5–8.

**No quest, request or research content is written before step 4**, per the instruction that
opens this document.
