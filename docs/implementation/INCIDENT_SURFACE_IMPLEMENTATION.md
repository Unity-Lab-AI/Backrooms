# The storyteller finally knows this mod exists — 0.11.8-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including an assertion it got wrong
on the way. Never rewritten.

---

## The question this answers

> *"we may need our own story teller right? or is that way way to much work? with the "AI" like
> ai thats not an ai that the storytellers use"*

And the decision at the fork:

> ***"Both - guaranteed floor, storyteller flavour"***

The guaranteed floor shipped in 0.11.7. **This is the flavour half.**

---

## No `StorytellerDef`, and the reason is not effort

A `StorytellerDef` would have been easy. It is also the single most hostile thing this mod could
ship, for three reasons in descending order of severity:

1. **It is an exclusive slot.** The player picks exactly one storyteller. Shipping ours means
   asking somebody running 294 other mods to give up Cassandra to play this. That is the exact
   inverse of the rule the whole project stands on — *"we are making a mod that works with the
   other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*
2. **It needs `portraitLarge` and `portraitTiny`.** Art, which the no-new-art rule forbids.
3. **Its job is pacing global incidents**, and this mod's pressure comes from the gate, which the
   player controls deliberately. Bolting a dice-roller onto a system built to be honest is a
   downgrade.

**The owner's instinct about the "AI" was exactly right, and it is why the slot is unnecessary.**
There is no intelligence in a storyteller to borrow: a `StorytellerComp` rolls a
mean-time-between against colony wealth and population and picks from a weighted `IncidentDef`
list. The part that behaves like a director is **`IncidentWorker.CanFireNowSub`** — the
conditions — and that is ours to write without owning anything.

**`proof-incidents.py` now asserts the never**: if a `StorytellerDef` ever appears in our defs,
the proof fails.

---

## The gap this closed

**Before this checkpoint the mod shipped zero `IncidentDef`s.** Every event fired from its own
`GameComponent` tick, which meant whichever storyteller the player chose had never heard of the
mod and never paced a single thing it did.

A mod that runs *beside* the game's event economy instead of *inside* it always reads as bolted
on, no matter how good the content is. That is the real answer to the owner's question, and it
cost two defs and one base class rather than a persona.

---

## The two incidents

### `RR_Incident_ThresholdBleed` — the space follows a crew home

A gate is a hole between a colony and somewhere that does not obey the same rules. Occasionally
the wrongness comes out the near side: the lights in the gate room go, or the room drops eight
degrees, or dirt that was not there is there now.

**It runs the same four effects a coordinate runs.** `AnomalyEventService` was re-scoped from
`CoordinateRecord` to a plain `List<IntVec3>` so there is **one implementation**, because what
would drift out of a second copy are the four promises in invariant 28 — readable warning,
learnable rule, a countermeasure, no unavoidable instant failure.

Three decisions inside it:

- **Scoped to the room a gate stands in**, never the whole colony. That is what makes the rule
  learnable: it happens where the hole is, and a player who works that out can keep the gate room
  away from anything that minds the cold.
- **Designated gates only.** A natural gate has no operator, no power and no address book —
  invariant 12 — and the bleed is a consequence of the branch *working* a hole.
- **Rearrangement is deliberately excluded at the headquarters.** In a coordinate, moving a loose
  item is a horror beat in a place the player is visiting. In a colony it shuffles things inside
  somebody's stockpile, and the honest word for that is not *unsettling*, it is *tedious*. The
  three that remain are each answered by something the player already knows how to do: flick the
  switch, wear a coat, sweep the floor.

It also requires the branch to have **visited at least one coordinate**. The space cannot follow
a crew home from somewhere the crew has never been.

### `RR_Incident_CorporationDelivery` — a crate nobody ordered

The everyday face of the same character that sends a clean-up team when the worst happens.
*"The mega mother corp is greedy"* — and greed is the **mechanism** for the generosity, not a
contradiction of it: an investor protecting an investment keeps the investment working.

Gated on `CorporationContact`, so the Store and Solo/Group starts get nothing until they earn it.

Deliberately **modest** — 40% of the clean-up team's crate, from the same table. A branch cannot
live on it. It is not meant to change how anybody plays; it is meant to be the thing a player
points at when they describe what this company is like.

---

## One table, two scales

The relief crate and the courier crate are **the same corporation with the same warehouse**, so
`CompanySupplyDrop` holds one table and both read it at different scales. Two tables would have
drifted apart the first time either was tuned, and the letter would have kept promising the old
one.

A line that scales below a single item is **dropped entirely** rather than rounded up: a crate
containing one component reads as an insult, and this corporation is many things but it is not
petty.

---

## What is deliberately NOT an incident

| | Why |
|---|---|
| **The clean-up team** | It is a **guarantee**. A storyteller asks *whether* and *when*, and *"facilities never die"* admits neither question. Asserted: no incident worker calls into the relief |
| **Incursion** | Invariant 53 bounds it on five axes through one entry point. A second door into the one named exception to the founding rule is not a feature. Asserted |
| **Anything inside a coordinate** | What happens down there is the space's business, paced by arrival and depth. A storyteller has no view of it and should not |

---

## The assertion that was wrong, and the source that was right

The first version of the incursion claim searched the whole incident source for the word
`Incursion` — and **failed on this mod's own doc comment explaining why incursion is excluded
from the incident surface.**

**The assertion was wrong and the source was right** (invariant 130). The rule is that no
incident worker *calls into* incursion; documenting why one must not is precisely the comment
worth keeping, and a proof that punishes the explanation teaches people to delete explanations.

It now strips comments before asking, and it still catches the real thing — planting a call to
`TickFacilityRelief()` in a worker fails it immediately.

**This is the second time this session an assertion failed and the code turned out to be
correct.** The first was the depth rule against the gate ladder, at 0.11.4.

---

## The proof was fault-planted four ways

| Fault planted | Caught by |
|---|---|
| `workerClass` typo — **the exact silent failure this proof exists for** | *"workerClass resolves to a real class"* **and** *"is referenced by an IncidentDef"*, from both directions |
| target changed to `World` | *"targets only Map_PlayerHome"* |
| a `StorytellerDef` added | *"the mod ships no StorytellerDef"* |
| a worker calling `TickFacilityRelief()` | *"no incident worker runs the facility relief"* |

All restored, proof holding.

---

## A ledger script ate a heading

While writing this checkpoint's ledger the patch failed on a missing anchor, which is how a
defect in the **0.11.7** ledger script was found.

Its `edit()` helper did `s.replace(anchor, new)` where `new` did **not** re-include the anchor,
so inserting the 0.11.7 entry **consumed** the heading

```
## Inherited pre-workflow history (2026-09-27 → 2026-09-28, previous build agent)
```

and left that whole section headless underneath the new entry.

**`FINALIZED.md` is append-only.** No entry text was lost — only the heading and its
parenthetical — and both are restored verbatim from `HEAD~1`. The check that proves it is a diff
filtered for removed lines, which now returns nothing.

Two things changed as a result:

- Every insertion in the 0.11.8 script uses an `insert_before` helper that **re-includes its
  anchor**, so the same mistake cannot be written again.
- The diff of an append-only file is **checked for removed lines** before the commit, rather than
  trusted because the script printed "updated".

It is invariant 144. The general shape is one this session keeps meeting from different angles:
**a patch that silently succeeds at the wrong thing is worse than one that fails**, and the only
defence is to assert the property rather than the operation.

---

## The heredoc, for the seventh time

Patching the proof through a shell heredoc collapsed `\n` inside a Python string literal into a
real newline and produced an unterminated-string syntax error.

**This is the seventh time, and `docs/NOW.md` already lists it under gotchas with the fix next to
it: use Write.** The count is the useful part — a gotcha that has been documented and re-hit six
times is not a gotcha, it is a habit, and the only reliable answer is to stop reaching for the
heredoc at all when the payload contains an escape.

---

## Receipts

| | |
|---|---|
| Version | 0.11.8-dev |
| Build | 167 C# files, 86 package files, **0 warnings, 0 errors** |
| New defs | **2 `IncidentDef`** — the mod's first |
| `StorytellerDef` | **none, and now asserted** |
| New art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **2** |
| Checkers | **eight**, all passing |
| Proofs | **six**; the new one fault-planted four ways |
| Game launched | **no** |

Next, in the chart's order: the Store and Solo/Group starts, each with its own layout, and
**neither begins in corporation contact** — so neither has the clean-up team or the courier until
it earns them.
