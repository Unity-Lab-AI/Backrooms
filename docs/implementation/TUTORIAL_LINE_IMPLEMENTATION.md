# The company asks for six things, then stops asking — 0.11.2-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## What this is

**Step 5 of the build order in `docs/CAMPAIGN_CHART.md`**: tutorial requests 2–6 and the hinge,
following request 1 which shipped in 0.11.1-dev with the offer shape.

Nothing here was invented. Each request's routes are the ones the chart already names for it, and
every def name referenced was read out of the installed game or out of our own project file.

---

## The line

| # | Request | Arc | Teaches | Routes, and their kinds |
|---|---|---|---|---|
| 1 | **power the gate** | 1 | reserve, wiring | build a battery *(Deliver)* · bind one you have *(Substitute)* |
| 2 | **assemble and calibrate** | 1 | the bill, the operator | assemble here *(Deliver)* · requisition it *(Purchase)* |
| 3 | **bring back one record** | 1 | surveying, the book, the archive | survey and analyse *(Document)* · recover one already down there *(Deliver)* |
| 4 | **mark a route home** | 2 | markers, colour as meaning | mark the junctions *(Deliver)* · your crew already knows the way *(Testify)* |
| 5 | **report a disagreement** | 2 | distortion logs | analyse a distortion record *(Document)* · two accounts of the same room *(Testify)* |
| 6 | **hold a connection open** | 3 | the ladder, power draw | complete Field Stability *(Research)* · buy the hardware *(Purchase)* |
| 7 | **choose a direction** | 3 | **the transition** | declare it *(Redirect)* · say nothing and go *(Document)* · take the aperture further *(Research)* |

Each requires the one before it, so the line is a single chain. The proof asserts that, plus
contiguity from zero and the absence of any cycle.

**Every request pays, and none of them expires.** There is no field to put an expiry in.

---

## Two conflicts with the chart, found while mapping routes

Both were raised at the point they were found, per the standing instruction, and both were small
enough to resolve with a stated judgment rather than a block.

### 1. A route kind that did not exist

Request 6 offers *"complete Field Stability"*, and none of the chart's six kinds covered it.
Research is a thing a branch **does**, and it is not a delivery, a document, a substitute, a
purchase, a testimony or a redirect.

**`Research` added as a seventh kind**, with a `projectDefName` field and a `ConfigErrors` rule
requiring it. The chart's table was always *"route kinds this chart uses"* rather than a closed
set, so this is a fill rather than a change of direction. Chart updated.

### 2. The rule bit the chart's own content, and the result is better

The hinge was drawn as *"pick any one of the eight branches"*. **Every route would have been the
same kind**, which fails the rule that a request offers two routes of two **different** kinds.

The tempting move was a carve-out — exempt the hinge because it is special. That is exactly the
failure recorded one checkpoint earlier as *"never widen a rule so that existing text passes"*.

So the hinge was redesigned instead, and the redesign is better than what it replaced:

- **Declare a direction** *(Redirect)* — tell the company and it writes it down.
- **Say nothing and go** *(Document)* — go and meet something down there, and let the record speak.
- **Take the aperture further** *(Research)* — push the gate rather than the business.

***"Every choice is a success"* is more true when nothing has to be announced.** A rule that
forced a better design earned its keep.

---

## A third conflict, in the chart's own prose

§2 claimed *"the hinge is where contact with the corporation completes"*. The owner's answer at
the previous fork makes that false: **Async Industries begins in contact**, so for that start the
hinge is not where contact happens at all.

| Start | Opens in contact | What the tutorial line is for it |
|---|---|---|
| **Async Industries** | **Yes** | Training, paid for by a company already invested. The rescue applies from minute one |
| **Store** | No | Its own layout, and **reaching contact is the achievement** |
| **Solo/Group** | No | The same, from a different point of view |

The hinge is where the **tutorial** ends, for every start. Whether the corporation is watching
when you arrive depends on which start you chose — and for two of three, **there is no rescue
until contact is earned**. Chart corrected.

---

## The proof

`.local/register/proof-offer-routes.py`, extended from nineteen claims to fifty-eight. Everything
0.11.1-dev asserted, plus:

- **every `thingDefName` resolves to a real ThingDef in the installed game** — the failure mode
  that once put `Multianalyzer` in a marker role and matched nothing;
- every `projectDefName` and every `redirectTo` resolves;
- **every `logKind` is one the campaign can actually count**, because `CompletedLogCount` returns
  0 for an unknown kind *silently*, so a typo would produce a route that can never be satisfied;
- **request N requires request N−1**, so the line cannot be taken out of order;
- no prerequisite cycle, checked transitively;
- tutorial orders contiguous from zero.

### The proof was wrong before the content was

The first run reported `TextBook` as not existing. It does — in `Core/Defs/Books/BookDefs.xml`,
which is not under a `ThingDefs*` path, and the index only globbed those.

**The index was wrong, not the content.** RimWorld does not require a `ThingDef` to live in a file
whose name says so, and a proof that assumes otherwise reports a correct reference as a fault —
which is the worst thing a proof can do, because the obvious response is to "fix" working content.
The index now reads every `Defs` file.

### Sanity-tested in both directions

| Planted | Result |
|---|---|
| `distortion` → `distorsion` on a log route | **FAIL** — *"CompletedLogCount returns 0 for anything else, silently"* |
| A prerequisite removed from the middle of the line | **FAIL** — *"the tutorial line can be taken out of order"* |
| Both reverted | **PROOF HELD** |

---

## Receipts

| | |
|---|---|
| Version | 0.11.2-dev |
| Build | 162 C# files, 85 package files, **0 warnings, 0 errors** |
| New defs | 6 more `RimroomsRequestDef`, 7 total — a mechanics def, **no gameplay ThingDef** |
| New route kind | `Research` |
| Chart corrections | 4 — the seventh kind, the hinge's routes, the hinge/contact claim, the build order |
| New art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing; rule 2 now checks 7 offer defs |
| Game launched | **no** |

Next in the chart's order: **the eight remaining research branches**, tier 0 → 2 first, then the
clean-up team.
