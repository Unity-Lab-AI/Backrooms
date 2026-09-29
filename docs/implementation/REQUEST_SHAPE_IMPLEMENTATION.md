# An offer with more than one way through — 0.11.1-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"use ask me question then get to the work of getting this mod done as ouutlined and as
> described in totality and what/how it needs implimentation useing the prep docs and mod chart's
> information to properlly build everything as detailed and layed out and as the lkayout needs
> currects or has conflicts use ask me question soon than later"*

Four blocking questions were asked before a line was written. This is **step 4 of the build order
in `docs/CAMPAIGN_CHART.md`**: the offer shape, with routes as a first-class field, built before
any request content so that the first request ever written has to satisfy the absolutes rather
than being retrofitted to them.

---

## The four answers, and what each one decided

| Question | Answer | Consequence |
|---|---|---|
| Quest surface | **Our Operations tab records** | `ContractRecord` is extended; native `QuestScriptDef` is not adopted |
| Route model | ***"1 and 3"*** | Authored floor **and** derived extras — the same answer at two strengths |
| Research | **Our project defs** | The eight remaining branches join the gate ladder's insight-plus-logs system |
| Rescue scoping | **Contact is a state, not a scenario** | A branch-level flag, not a scenario property |

### Why not the native quest system

Core's quest system is built around **time-limited offers with single objectives** — precisely the
two things the absolutes forbid. Adopting it would have meant fighting it to arrive back where we
started.

It also turned out to be the safer register answer. Rows **148 No Quests Without Comms** and
**132 More Faction Interaction** both operate on native quests. By not using that system, this mod
cannot collide with either. That is the register check paying off in the negative — the useful
finding was *what not to touch*.

### Contact is a state, not a scenario

Owner, verbatim:

> *"clena up tema is only once u are in communication and working with the corporation Async
> industries starts with this tech research and other basic gate techs it needs to operate and
> begin researching and gate operations at basic levels but the other two scenerios need special
> treatment in theri layout and starts"*

This reframed the question that was asked. The blocking problem had looked like *"the rescue is
scoped to two scenarios that do not exist"*; the answer is that **it is not scoped to scenarios at
all**. `RimroomsCampaignComponent.corporationContact` is a saved branch flag, and
`RimroomsStartDef.beginsInCorporationContact` decides where a start opens.

**Async Industries begins with it true.** The Store and Solo/Group starts will begin false, and
reaching contact is what turns the corporation's attention on. That absence is the point: before
contact there is no rescue, which is what makes those two openings frightening.

**It is one-way by design.** There is deliberately no method to take contact back. A corporation
that has seen a return on an investment does not forget about it, and revoking contact would take
the never-die guarantee away from a player who had earned it.

A further constraint the answer carried, recorded for every branch still to be built:

> *"the samw universial rimworld tech tree of all our mods in the collection on top of our mod"*

**Our research layers on the shared tree and never forks it.**

---

## The shape

### Two absolutes, enforced twice

| Absolute | How |
|---|---|
| *"never offer only one path but multiple success routes"* | **two authored routes, of two different kinds** |
| *"missions … are never time senstive"* | **there is no field to put a deadline in** |

The second is enforced **by absence**, which is the strongest form available: a deadline cannot be
configured onto a request because the shape has nowhere to hold one. The proof asserts that no
such field exists, so adding one later fails the build rather than quietly working.

Both are checked in **two places**: `ConfigErrors` at def load, and
`check-campaign-absolutes.py` before shipping. Two layers because they catch different things —
the checker catches a bad def in this repository, `ConfigErrors` catches one arriving from a
patch, another mod, or a hand edit after shipping.

### Route kinds

`Deliver`, `Document`, `Substitute`, `Purchase`, `Testify`, `Redirect`.

The kinds exist so that "two routes" means something. **Two `Deliver` routes differing only in
which shelf the item lands on is one route wearing two hats**, and a rule that counted it as two
would be satisfied by text rather than by design.

### The floor, then the extras

Owner's answer was *"1 and 3"* — options that are the same answer at two strengths, and both
halves matter:

- **The authored floor makes the absolute unbreakable.** Every family declares at least two routes
  of different kinds in XML. A branch with nothing always sees two ways through.
- **The derived extras make a developed branch feel developed.** A catalogue that carries the
  wanted thing adds a **Purchase** route. A completed log of the right kind adds a **Testify**
  route — somebody on this branch has been there and the log proves it.

**The safety property is an ordering, not a count.** The floor is assembled *before* capability is
consulted, so if deriving ever returned nothing — no catalogue, a broken save, a mod that removed
the procurement defs — the request still offers two ways through. The proof asserts that ordering
against the source, because no test can prove it without a running game.

Authored routes are **never filtered by capability**. A route a player cannot currently take is
still a route they can see and work toward, which is more useful than a card that quietly shrinks
when the branch is poor.

---

## The worked request

`RR_Request_PowerTheGate` — the first rung of the tutorial line, with exactly the routes the chart
already names for it: build a battery, or bind one you already have. Nothing invented.

It is one request on purpose. The shape needed a worked instance to be provable; the remaining
tutorial requests and the hinge are step 5 and follow the chart's order.

---

## The proof

`.local/register/proof-offer-routes.py`, nineteen claims, all held. It checks **the floor alone,
with capability deliberately ignored**, because that is the case nobody plays and therefore the
case nobody notices is broken.

- two or more authored routes, of two or more different kinds;
- every route string resolves, including the four shared derived-route strings, so no player reads
  a raw key off a card;
- **the authored floor is added before capability is consulted**;
- `AuthoredKinds` counts only `definition.successRoutes` and can never see a derived route;
- **no deadline field exists** on the request def, under four spellings;
- tutorial orders are distinct and start at the first.

### Sanity-tested in both directions

| Planted | Result |
|---|---|
| The second route's kind changed to match the first | **FAIL** — *"one route written twice"* |
| The derive block moved above the authored floor | **FAIL** — *"deriving first would let a capability route stand in for an authored one"* |
| Both reverted | **PROOF HELD** |

---

## Receipts

| | |
|---|---|
| Version | 0.11.1-dev |
| Build | 162 C# files, 85 package files, **0 warnings, 0 errors** |
| New source | `Company/RequestDefs.cs`, `Company/RequestRoutes.cs` |
| New defs | `RimroomsRequestDef` ×1 — a mechanics def, **no gameplay ThingDef** |
| New state | `corporationContact` on the branch, `beginsInCorporationContact` on a start |
| New art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing; rule 2 went from 0 offer defs to 1 |
| Game launched | **no** |

Next, in the chart's order: **tutorial requests 2–6 and the hinge**, then the eight remaining
research branches, then the clean-up team — which now has a real state to key on.
