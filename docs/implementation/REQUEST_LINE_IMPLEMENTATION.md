# The mission line reaches a player — 0.12.11-dev, 2026-09-29

**Dated record.** Never rewritten. Supersedes nothing; it completes what
`REQUEST_SHAPE_IMPLEMENTATION.md` (0.11.1-dev) and the hinge checkpoint (0.11.2-dev) started.

---

## What was actually wrong

`docs/CAMPAIGN_CHART.md` §7 recorded steps 4 and 5 as **done**:

> 4. ~~The offer/request def shape, with routes as a first-class field.~~ **Done, 0.11.1-dev.**
> 5. ~~Tutorial requests 1–6, then the hinge.~~ **Done, 0.11.1-dev and 0.11.2-dev.**

Both statements were true about what they claimed. `RimroomsRequestDef` exists, enforces two
routes of two different kinds at def load, and has no field a deadline could be written into.
`RequestRoutes` implements the owner's *"1 and 3"* route model. Seven requests are authored — the
whole tutorial line and the hinge.

**And nothing read any of it.**

```
grep -rn "RequestDef|RequestRoutes|SuccessRoute|TutorialLine" --include=*.cs src/ \
  | grep -v RequestDefs.cs | grep -v RequestRoutes.cs
  -> no output
```

Zero references. The defs were validated by `ConfigErrors` at load, checked by
`check-campaign-absolutes.py`, and proved by `proof-offer-routes.py`. **None of those is a player
seeing a request.** The campaign existed as a def file.

This is the same defect as the five `PawnKindDef`s found authored and read by nothing in
0.11.7-dev, and the three dead gate accessors in 0.12.4-dev — **at feature scale**, and the
reason it survived two checkpoints is that every tool watching it was watching the *shape* of the
content rather than whether anything consumed it.

### Why this reordered the queue

`NOW.md` had arcs 5–8 next, and the chart authorises that. **But arcs 6, 7 and 8 are request
content**, and authoring more requests would have authored more defs nothing reads. The surface
comes first or the arcs are written into a void.

---

## The register, checked first

| Row | Mod | Stance | What it meant here |
|---|---|---|---|
| **148** | No Quests Without Comms | Configuration only | operates on **native** quests |
| **132** | More Faction Interaction | Optional | operates on **native** quests |
| **81** | Dubs Mint Menus | Optional | architect and bill menus, not `MainTabWindow` panes |

The decision recorded at `FINALIZED.md:3566` — *"by not using that system this mod cannot collide
with either"* — was the right call and is **why this checkpoint had somewhere to go.** Requests
are presented in this mod's own Operations pane, not through `QuestScriptDef`. Nothing in the
interface family patches a main tab, so the pane is safe.

---

## What shipped

### The record and the line

`RequestRecord` carries what happened; the def stays pure content. Four states, and
**deliberately no `Expired`** — chart §1.1.

**Offering is three gates, each of which can refuse:**

| Gate | Rule | Why |
|---|---|---|
| Contact | `corporationContact` | *"option three with hints like i need to contact someone about this crazy shit"* — two of three starts open in silence |
| Order | one open request at a time | the tutorial teaches one system per step |
| Prerequisites | Completed **or Cancelled** | a refusal must never strand the rest of the line |

**The tutorial line is deliberately NOT capability-filtered.** The owner's eligibility answer —
***"filter picks the family, card never shrinks"*** — is about **generated** requests. Applied
here it would let a fresh branch that cannot yet take two routes be offered *nothing, for ever*,
which is the one failure a tutorial cannot have. The proof asserts the absence.

### Seven route kinds, seven different questions

The pair most at risk was `Document` and `Testify`: both name a log kind, and the obvious
implementation makes them the same call. **Request 5's only two routes are those two** — so
collapsing them would leave a request whose card promises two ways and whose code has one, while
`ConfigErrors` kept passing. The def rule would have been satisfied by text alone.

They are split on what actually differs:

| Route | Check | Survives |
|---|---|---|
| `Document` | an **analysed** record carries that log | the witness dying |
| `Testify` | **`count` distinct living employees** on a matching observation | the book burning |

`RouteMismatch` / `RecorderGap` / `EntitySighting` / `RoomSurvey` — already written by the
investigation system — map onto distortion / entity / route. **Nothing new is recorded for this
feature.** Testimony reads what crews were already producing.

`Research` and `Redirect` had the same problem at the hinge, which offers both against
`RR_GateSustainedAperture`. Split the same way: **Research is arriving, Redirect is saying where
you are going** (`workDone > 0`, or the insight committed).

### Two label corrections the checks forced

- **Request 5's Testify route now asks for `count` 2**, because its label is *"two crew accounts
  of the same room"*. Left at the default of one, the card promised a pair and accepted a single
  account. **The check made the label honest, not the other way round.**
- **`RR_Requests_NoDeadline` was renamed `RR_Requests_NoTimeLimit`.** See below.

### `bonusUsd` stopped being a hollow field

Exactly one authored request carries a bonus — *"bring back one record"*, the first time a branch
sends people through a gate. The condition is **everybody who was on the books when the request
was accepted is still on them, alive**, measured against a **snapshot** taken at acceptance
(invariant 27) so that firing the casualty cannot earn it. Invariant 136: a number on a card that
always pays is not a bonus.

### The pane

Requests are drawn above the existing contracts in pane 2. Every authored route is shown
**whether or not the branch can take it**, per the owner's decision, with a `[done]` marker on
the ones already satisfied.

**Satisfaction is read, not computed in the pane.** The tick that evaluates every route records
which ones are true and the pane reads that list. A panel redraws sixty times a second and two of
the checks scan every map the branch runs; computing it there would be the same answer, worked out
again, more expensively, with somewhere new to drift. Same discipline as the gate's
`IdlePowerDrawWatts`.

---

## Four defects found in my own work while building this

### 1. A runtime-built keyed string, again

`("RR_Requests_Status_" + record.Status).Translate()`. `check-keyed-strings.py` caught it — it can
see the prefix and nothing else. **Third time this pattern has been written in this project** (the
first was `"RR_Hint_" + id`). Replaced with literal keys behind a hand-written switch, and the
reason is now in a doc comment at the site.

### 2. A proof rule that banned its own negation

The rule *"the request line never mentions 'deadline'"* failed on `RR_Requests_NoDeadline`, whose
text was *"There is no time limit. The company waits."* — the rule cannot read intent.

**The key was renamed; the rule was not softened.** Widening a check so my own text passes is how
a checker stops working, and this session already refused that once when
`check-campaign-absolutes.py` flagged a TODO wording.

### 3. The C# file count has been wrong for five checkpoints

Writing the receipts table below meant measuring the file count instead of copying it, and the
figure carried since 0.12.6-dev was **172 when the real count was 170**:

```sh
for c in ac6422b 70c1e95 ba24a7c 7796d51 4ebff3e; do
  git ls-tree -r $c --name-only | grep -c '^src/.*\.cs$'    # 170, every one
done                                                         # every record said 172
```

**Exactly the stale assembly hash again**, and it survived for the same reason: a plausible
number nobody re-measures. It is now genuinely 172 because this checkpoint adds two files —
**which is precisely how a wrong number outlives its correction**, and the reason the command is
written down here rather than the answer.

### 4. The same rule then matched an XML comment

After the rename it failed again, on a comment *I had written saying no string mentions a
deadline*. **Invariant 130**, where an incursion word-search matched a doc comment.

XML comments are now stripped before the check — **narrowing the population, which is legitimate,
rather than softening the rule, which is not.** The distinction is only honest if the narrowing is
proved not to blind the check, so a fault was planted: a real keyed string reading *"Meet the
deadline or lose the contract."* makes the proof exit 1, and removing it returns it to 0.

---

## The proof, fault-planted five ways

`proof-request-line.py`, **41 claims**. Its first claim is the one that would have caught the
original defect: **the request def is read by source outside its own definition.**

| Planted fault | Exit | Caught |
|---|---|---|
| a real keyed string containing "deadline" | 1 | ✓ |
| `Testify` collapsed into `Document` | 1 | ✓ |
| `OwnedThingCount` uses `OwnsMap` (a coordinate counts as home) | 1 | ✓ |
| the status flip removed from completion | 1 | ✓ |
| **`DrawRequests` commented out — the original defect, restaged** | 1 | ✓ |
| *restored* | **0** | — |

Every plant asserted its anchor **before** writing, so a mistyped anchor aborts rather than
planting nothing and passing — the gotcha that cost a false result earlier this session.

---

## Deliberately not in this checkpoint

- **Generated requests after the hinge.** The eligibility filter — the owner's *"filter picks the
  family"* half — needs the arc 4–8 request families to filter, and it must have **teeth**
  (invariant 136): every clause has to be able to refuse. Next checkpoint.
- **An `Offered` request is evaluated but never completed.** Accepting is the branch saying yes,
  and a job nobody took cannot pay. The player can see what is already done before deciding.

---

## Receipts

| | |
|---|---|
| Version | 0.12.11-dev |
| Build | **172 C# files** (measured, not carried — see defect 3), 86 package files, **0 warnings, 0 errors** |
| New source | `Company/RequestLine.cs`, `UI/OperationsRequests.cs` |
| Request defs that now reach a player | **7**, including the hinge |
| Route kinds with a distinct check | **7 of 7** |
| Dead fields given a real read site | `bonusUsd` |
| Checkers | **eight**, all passing |
| Proofs | **sixteen**, all exiting zero |
| Planted faults caught | **5 of 5** |
| Game launched | **no**, and nothing in this mod has ever been played |
