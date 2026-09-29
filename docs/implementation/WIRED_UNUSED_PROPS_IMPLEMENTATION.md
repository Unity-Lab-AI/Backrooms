# A designated gate is a machine that is on — 0.11.5-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including the decision it reversed.
Never rewritten.

---

## The direction that reversed three decisions

> *"then once you finalize that do the NOW.md write up procedures and prepare for the other side
> of compact and **make sure shit isnt unused it was put there for a reason**"*

Over 0.11.4-dev and the opening of 0.11.5-dev, three gate props were found to be read by nothing
and **retired** — archived properly, with reasons, and removed. The owner stopped it.

**A value nobody wired is a job nobody finished, not a value nobody wanted.** Retiring it throws
away the intention along with the dead code, and the intention is the part that was worth
keeping. All three were restored.

This is the second correction of the same shape this session. The first was *"how tf do you know
we didnt need that shit coded up correctly"*, about deleting tuned values. The pattern in both:
**I treated "unused" as "unwanted" and reached for removal.** The invariant is now written down
twice, at 105 and at 131.

---

## What each one is now

### `idlePowerDrawWatts` — wired

A designated gate drew **exactly nothing** while closed. `CurrentPowerDrawWatts` returned the
opening draw or zero, and there was no third case.

Now it draws `idlePowerDrawWatts × GateCellCount` from its bound battery every tick while closed —
scaled by footprint like the opening draw, because a bigger gate is more machine to keep warm. A
designated gate holds its calibration, keeps its address book live and keeps the reserve warm, and
that should cost something.

**It never drains below what an emergency return costs.** That floor is the difference between a
cost and a trap:

```csharp
if (NativeStoredEnergy - cost < GateProps.emergencyReturnCostWattDays) { return; }
```

A player who designates a gate and walks away should come back to a flat battery, not to a crew
that cannot be recovered. Nothing warns you about the second one because nothing could.

While a connection is open the opening draw is charged instead, so the two never stack.

### `returnReserveCapacityWattDays` — wired

Now the thing its name always read like: **the smallest reserve a gate will accept**, checked when
a battery is bound.

A battery too small to hold an emergency return is not a reserve. Binding one produces a gate that
looks finished and strands the first crew through it, so the refusal happens at the moment
somebody chooses the battery rather than as a surprise at the threshold.

### `reserveChargePowerWatts` — restored, **deliberately not wired**

**It is genuinely ambiguous and is not being guessed at.** The reserve is a Core battery on the
colony's power net, and **RimWorld already charges it**. So "the rate the gate charges its
reserve" either duplicates Core or means something else, and the candidates are all defensible:

| Reading | Problem |
|---|---|
| A **supply requirement** — the gate will not open unless its circuit can deliver this much | largely duplicates `minimumPowerHeadroomWatts` |
| A **display estimate** — *"the reserve refills in about N hours at the rated charge"* | honest, but only a readout |
| A **second charge path** — the gate pulls from the net into its reserve at this rate | double-charges alongside Core unless it replaces Core's charging for that battery |

Recorded as an open owner question in `TODO.md`. Guessing here would produce exactly the
contrived mechanic the "don't build willy nilly" direction warns against, and the correct move
when two readings both look reasonable is to ask.

---

## The sweep that made this findable

The first two dead props were found **by stumbling on them** while looking for a research knob.
That is not a method, so the third search was a sweep of all seventeen props on
`CompProperties_RimroomsGate`, counting real read sites for each.

It found one genuinely dead prop — and it **cleared one that an earlier one-off grep had wrongly
called dead**. That grep excluded every line containing `public `, which threw away the property
wrapper that reads it:

```csharp
public float CalibrationWorkRequired { get { return GateProps.calibrationWorkRequired; } }
```

**Finding dead values one at a time produces both false negatives and false positives.** Sweep the
class. Of seventeen gate props, exactly one was dead, and now none is.

---

## The balance change, named rather than buried

**A designated gate used to cost nothing to keep and now costs 250 W, scaled by footprint.** That
lands on every existing save.

It was made because the direction says an unused value is an unfinished job, and the unfinished
job here was clearly "a gate should have an idle load". But it *is* a balance change, it is the
kind a player notices, and if the intended behaviour was genuinely zero idle cost then this is the
one to reverse. It is recorded as an open question in `TODO.md` rather than left for somebody to
discover in-game.

---

## The 0.11.4 archive was not rewritten

`historical-content/0.11.4-dev/RETIRED_VESTIGIAL_POWER_PROPS.md` now opens with a note saying the
decision was reversed, and its body is **untouched**.

Dated records are never rewritten — that rule is what makes the evidence trail worth anything. The
record was true on the day. The reversal belongs here and in the ledgers, not inside it.

---

## Receipts

| | |
|---|---|
| Version | 0.11.5-dev |
| Build | 162 C# files, 85 package files, **0 warnings, 0 errors** |
| Props restored | **3** |
| Props wired | **2**; the third is an open owner question |
| Gate props with zero read sites | **0**, swept |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing |
| Proofs | **four**, all holding |
| Game launched | **no** |

Still queued, in the chart's order: research tier 2, then the clean-up team.
