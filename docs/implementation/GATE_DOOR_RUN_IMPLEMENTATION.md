# A wide gate out of plain doors — 0.12.31-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the fallback half of the gate-size question, and with it
three rows that were one feature.

---

## The answer was on record, and it was BOTH paths

> *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit
> vehicals and the like"*

Three rows (568, 610, 959) pointed at this one feature. The single-door half shipped at 0.9.2-dev —
Core's own `OrnateDoor` is 2×1, so **1×2 needed no mods at all**, which was found by reading the
installed game rather than assumed. Doors Expanded supplies real 1×3 and 2×3 shapes through a
conditional patch. **What was missing was the no-mod path to those two sizes.**

And a framing correction that had to survive: the option was once written as *"Core-only must reach
every width"*, which treats a vanilla install as the audience. **It is not.** Zero hard dependencies
is a *build* property; the 294-mod register is the *play* property. This is a fallback for a player
who does not happen to run a door mod, not a claim about who the mod is for.

---

## The run flows through the code that already existed

This is the part worth recording, because it is why the change is small.

Everything about a gate's size already derives from **one `CellRect`**:

```
GateOccupiedRect ──> GateEntryCells ──> GateWidth
                 └─> GateCellCount ──> OpeningPowerDrawWatts
                                   └─> SpinUpWorkRequiredFor
```

And **a straight line of N adjacent 1×1 doors is a 1×N `CellRect`.** Two such lines side by side are
a 2×N one. So `GateOccupiedRect` returns the union of the run and *nothing downstream needed to
learn that a run exists* — the width, the entry cells, the power draw and the spin-up work all came
out right on their own.

A run therefore **costs more to power and more work to bring up**, in exactly the proportion a real
wide door does, because both are measured on cells. That is the owner's *"costs more to run"* applied
to the fallback without a single line written for it.

---

## Four invariants, and the run is built out of them

### Invariant 32 — one gate, one spin-up

Exactly one door in the run is the gate. The rest are **extensions**, and an extension reports
`IsDesignated` **false**:

```csharp
public bool IsDesignated
{
    get
    {
        return !IsRunExtension && NativeDoorProvider() &&
            nativeBindingSchema == 1 && nativeDesignated;
    }
}
```

So an extension has no address, no console, no window, no operator and no spin-up — because as far
as every other system in this mod is concerned **it is not a gate, it is part of one.** Three gates
in a row pretending to be one opening would be three spin-ups and three addresses.

A door that is already a gate, or already in somebody else's run, refuses. And a gate that is itself
an extension cannot take anything in, or a chain of hosts forms and nothing is the gate.

### Invariant 47 — one width, in both directions

Per-endpoint measuring traps an animal in the Backrooms. Width is derived **once**, off the run's
rectangle, and both sides read that number. There is no second derivation anywhere.

### Invariant 41 — throughput is never capped

A bound run gets **more entry cells and no quota**, exactly as a real wide door does. The proof
asserts no counter, cap or permit limit was introduced, by name.

### A run is a solid rectangle of a legal size

**A ring of doors around a gap has a legal-looking bounding box and is not an opening.** So the
union is accepted only when its area equals the number of doors in it, and only when its shape is
one of the **same four** a single door is allowed: 1×1, 1×2, 1×3, 2×3. A fallback must not reach a
size a real door could not.

Legality is a property of the **whole run**, not of the door being added, so extending proposes the
door, checks the result, and puts it back on failure. The candidate search asks the same way — by
proposing each neighbour — rather than reimplementing the rule, because a second copy would drift
out of step with the first.

### And not while it is working

*"gate doors expansions can NOT be done on a working gate"* — the owner's existing rule, applied
unchanged. An opening **and** a spin-up both refuse, in both directions: you cannot extend a working
gate and you cannot release one either.

---

## Both defects in this checkpoint were mine, and the checkers caught both

| | |
|---|---|
| **`check-keyed-strings`** | I wrote `CompanyActionResult.Refused("RR_GateRun_" + suffix)` — **a runtime-built keyed string, the fifth time this project has caught that pattern.** A key assembled at run time cannot be checked in either direction, so a typo ships as a raw key on screen. Replaced with thirteen literal keys |
| **`check-info-cards`** | I used the word **"doorway" five times** in player-facing text. The vocabulary rule is that a plain door is a **door** and the far-side arrival point is a **threshold**. **I had already been corrected on that exact word earlier in this session.** The word for what a run makes is the gate's *opening*, which is what `GateEntryCells` already called it |

The second one is the more embarrassing: a rule I had personally broken and had explained to me
hours earlier. **The checker did not care, which is the entire argument for having it.** Six comment
uses of the banned word went too — a comment teaching the wrong word to the next reader is how the
wrong word gets back into a string.

---

## The proof, fault-planted eleven ways

`.local/register/proof-gate-door-run.py` — the **twenty-eighth** — asserts **39 claims**.

| Planted fault | Exit | Caught |
|---|---|---|
| an extension becomes a gate in its own right | 1 | ✓ |
| the rect stops being the run, so width is per door again | 1 | ✓ |
| the cell count goes back to the def size | 1 | ✓ |
| **a bounding box with a hole in it counts as an opening** | 1 | ✓ |
| a run may exceed the legal gate sizes | 1 | ✓ |
| a working gate can be re-cut | 1 | ✓ |
| **releasing leaves extensions pointing at a released host** | 1 | ✓ |
| **the run stops being saved** | 1 | ✓ |
| the save method stops being called | 1 | ✓ |
| candidates stop being sorted | 1 | ✓ |
| the banned word comes back into player text | 1 | ✓ |
| *restored* | **0** | — |

The three in bold have no symptom until much later: a hole is only visible when something tries to
walk through it, a released host only matters to a door that has become nothing, and an unsaved run
silently becomes three ordinary doors on the next reload.

---

## Receipts

| | |
|---|---|
| Version | 0.12.31-dev |
| Build | **179 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `BA503ACA67B06719663B35D406E536C63DF266F55F926602B6958DE7CF76F757`, identical across two clean rebuilds |
| Rows closed | **three** (568, 610, 959), which were one feature |
| New content | **none.** A saved list, a saved reference, one gizmo, fourteen keyed strings |
| Gate sizes reachable with no mods | **1×1, 1×2 (Core's `OrnateDoor`), 1×3 and 2×3 (bound run)** |
| Checkers | **ten**, and two of them caught my own defects |
| Proofs | **twenty-eight**, all exiting zero |
| Planted faults caught | **11 of 11** |
| Game launched | **no.** Nobody has walked a vehicle through one of these |
