# Four answers, and a dead capability they uncovered — 0.12.4-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including two proof mistakes of its
own. Never rewritten.

---

## The four answers

| Question | Owner's answer, verbatim |
|---|---|
| Natural gates | *"we with minify i guess dont worry about it, can we at least do a rim style pop up warning ull lose valuable access to the backrooms and will have to find your own way back in"* |
| Solo/group guidance | *"option three with hints like i need to contact someone about this crazy shit"* |
| `reserveChargePowerWatts` | *"A supply requirement before opening"* |
| Idle draw | *"Keep 250 W (Recommended)"* |

All four are now closed. The fourth needed no code: **the shipped 250 W is the intended
behaviour**, and the open balance question from 0.11.5-dev is settled.

---

## The real find: a capability that promised an unlock and delivered nothing

Wiring the supply requirement meant reading what already consumed the gate's power values. It
turned out something did not:

```csharp
public float MinimumPowerHeadroomWatts      // reads the prop, applies RR_Cap_ReserveDiscipline
{ get { ... } }                             // and was itself READ BY NOTHING
```

**`RR_Cap_ReserveDiscipline` is the tier-0 Facilities unlock**, and its entire effect was to lower
that number. So the card promised *"the gate needs less spare headroom above its draw before it
will open"* and changed **nothing a player could ever observe.**

This is **invariant 136** exactly — written at 0.11.6-dev after three tier-2 unlocks were deleted
for the same reason — and it is precisely why `proof-research-branches.py` could not catch it:

> The capability **was** read, by real code. The code reading it was itself dead.

**A live read site is not a live effect.** The research proof asserts the first thing and cannot
see the second.

---

## So the sweep became a proof

Invariant 132 says sweep the class rather than grep for one name, because finding dead values one
at a time produces both false negatives and false positives. `proof-live-effects.py` does that,
generally: it walks **every public property on the gate comp whose body reads `GateProps`** and
insists each is consulted somewhere else.

Fifteen properties. It found **two more**:

| Found dead | What it turned out to be |
|---|---|
| `EmergencyReturnCostWattDays` | not a dead value — a dead **accessor**. The field is live; nothing showed the number |
| `RecoveryOpeningCostWattDays` | the same |

Those two are a different problem from the headroom one, and worth separating. The readout already
showed the **totals** that include them, so the player was told *"this much to open and come
home"* — and never told **how much of it was the coming home.** That is the number that decides
whether it is safe to send anybody.

Now it has its own line:

> *"Of that, N watt-days is held back for an emergency return, and a recovery opening costs M
> watt-days."*

Three dead members, one general sweep, and the sweep will keep working after everybody has
forgotten why it exists.

---

## The supply requirement

`ProjectedOpeningPowerFailure()` replaces a method that returned the same thing as its neighbour
and added nothing. It consumes both values:

- **`reserveChargePowerWatts`** — the circuit must be **generating** this much. Not stored charge:
  a battery is a buffer, not supply, and a gate opened on one charged battery and no generator is
  a gate about to strand a crew. `NativeGenerationWatts()` sums only what is actually producing,
  so a generator that is off, broken or out of fuel counts for nothing.
- **`MinimumPowerHeadroomWatts`** — and there must be margin above what the gate already draws,
  which is what finally makes the tier-0 unlock real.

**It gates opening only.** It is called once, from the can-open check, and deliberately **not**
from `NativeBindingFailureKey` — that property is read every tick and a generation dip would
emergency-return a crew that is already across. The chart's own rule: a lapse blocks the *next*
opening, never the current one. The proof asserts the absence.

Two distinct refusals rather than one blanket key, because *"the circuit cannot deliver enough"*
and *"there is no margin above what the gate draws"* are different problems with different fixes,
and one string for both always lied about one of them.

---

## Natural gates: informed consent, not prohibition

The earlier direction was *"natruals can not be destoryed or moved"*. The owner's answer relaxes
it — *"dont worry about it"* — and asks for a warning instead.

That is also the only honest option. Core decides destructibility at the **def** level, and
changing it would make every door in every colony indestructible for every player and every other
mod.

So `PortalDoorWarningMapComponent` warns before a natural or emergence door is deconstructed:
confirm and the work proceeds; cancel and the designation is cleared and nothing else is touched.
**A player may close their own way in. They may not do it by accident.** That sits better with
*"this is all open eneded they can play how they choose"* than a prohibition would have.

**A laboratory gate gets no warning**, deliberately. It is a machine the branch built and may
unbuild, nothing is lost that cannot be rebuilt, and warning about ordinary construction is how a
player learns to click through warnings.

**A map sweep, not a comp on every door.** The obvious shape would have every door in every colony
ticking forever to catch something that happens twice a playthrough. The connection list is small,
bounded by the coordinate cap, and knows exactly which doors matter.

---

## Solo/group: option three, and four things people say

**No request line until contact.** Not for difficulty — for honesty. Nobody is helping them
because nobody knows they exist, and a quest-giver would have to be invented, which is the most
obvious lie this start could tell.

Instead, four hints in the survivors' own voice, each firing **once ever** on a condition that is
already true when it fires:

| Hint | When |
|---|---|
| somebody needs to be told about this | a day in |
| open sky, and nothing standing here we did not walk out of | anybody reaches an ordinary map |
| the radio works, and nobody has a category for this | a powered comms console exists |
| the doors stop going anywhere new around here | a coordinate at the natural depth limit is known |

**None of them is an objective.** Nothing is tracked to completion, nothing notices whether the
player acted, nothing repeats. A hint that checked whether you obeyed it would be a quest wearing
a costume. And a player who worked it out first simply never hears the hint, which is the correct
outcome rather than a missed step.

---

## Two mistakes of my own, both in the proof

**The declaration scan matched nothing.** The first version used one regex with a brace-nesting
limit, and a property body is `{ get { ... } }` — two levels. It reported *"0 exposed properties"*
and then **passed every per-property claim by having none to check.** A proof that fails open,
which is invariant 152, written this same session. Rewritten to find declarations and read the
window after each, which cannot silently match zero.

**A runtime-built keyed string.** The hints used `"RR_Hint_" + id`, and
`check-keyed-strings.py` refused it. **The checker was right:** a key assembled at runtime cannot
be verified in either direction, so a typo in one would have shipped as a raw key on a player's
screen. The keys are literals now.

---

## Fault-planted three ways

| Fault planted | Caught by |
|---|---|
| the headroom read removed — **the original bug, restored** | *"MinimumPowerHeadroomWatts is consulted somewhere (0 uses)"* **and** *"it requires headroom above the current draw"* |
| the supply floor removed | *"it requires generation to meet reserveChargePowerWatts"* |
| the breakdown line removed | both accessor claims, re-deadened |

All restored, proof holding.

---

## Receipts

| | |
|---|---|
| Version | 0.12.4-dev |
| Build | 170 C# files, 86 package files, **0 warnings, 0 errors** |
| Dead members found by the sweep and wired | **3** |
| Capabilities revived from promising nothing | **1** (`RR_Cap_ReserveDiscipline`) |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **9** |
| Checkers | **eight**, all passing; keyed-strings caught a constructed key |
| Proofs | **nine** — a new general one, fault-planted three ways |
| Game launched | **no**, and nothing here has been played |
