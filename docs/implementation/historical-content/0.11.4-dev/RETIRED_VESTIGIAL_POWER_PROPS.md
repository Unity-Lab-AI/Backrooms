# Two vestigial power props — archived 0.11.4-dev

> **THIS DECISION WAS REVERSED IN 0.11.5-dev.** Both props were restored, and two of the three
> retirements of this kind were wired instead. Owner direction, 2026-09-29, verbatim: *"make sure
> shit isnt unused it was put there for a reason"* — **a value nobody wired is a job nobody
> finished, not a value nobody wanted.**
>
> This record is **not rewritten**, because it was true on the day it was written and the evidence
> trail depends on that. What follows is the reasoning as it stood; the reversal is recorded in
> `FINALIZED.md` and `TODO.md`.


**Archive, not a deletion.** Found while looking for a tier-1 research knob, which is the only
reason anybody looked at them.

---

## What they were

```csharp
// CompProperties_RimroomsGate
public float reserveChargePowerWatts = 1000f;
public float returnReserveCapacityWattDays = 2f;
```

And their validation, in `ConfigErrors`:

```csharp
if (!PositiveFinite(minimumPowerHeadroomWatts) || !PositiveFinite(idlePowerDrawWatts) ||
    !PositiveFinite(openingPowerDrawWatts) || !PositiveFinite(reserveChargePowerWatts) ||
    !PositiveFinite(returnReserveCapacityWattDays) || !PositiveFinite(emergencyReturnCostWattDays) ||
    !PositiveFinite(recoveryOpeningCostWattDays) ||
    emergencyReturnCostWattDays + recoveryOpeningCostWattDays > returnReserveCapacityWattDays ||
    !PositiveFinite(calibrationWorkRequired))
{ yield return "Rimrooms gate power, reserve, and work settings must be finite and positive."; }
```

---

## Why they are gone

**Neither was ever read.** Both appeared in exactly two places: the declaration, and that
validation. No system consulted either one.

They are residue from the power model retired in **0.9.1-dev** — *"a vestigial power model gone"*.
Back when `RR_MachineGate` was a custom building, the gate owned its own reserve, and these named
how big it was and how fast it refilled. Since the gate became a designated door bound to a Core
battery, the reserve **is** that battery:

```csharp
public float ReturnReserveStoredWattDays   { get { return NativeStoredEnergy; } }    // the battery
public float ReturnReserveCapacityWattDays { get { return NativeBatteryCapacity; } } // the battery
```

RimWorld's own power net charges it, at whatever rate the colony's generation allows. There is no
separate reserve for `reserveChargePowerWatts` to charge, and no nominal capacity for
`returnReserveCapacityWattDays` to declare.

**Note the collision:** the *property* `ReturnReserveCapacityWattDays` reads the battery, while
the *field* `returnReserveCapacityWattDays` read nothing. One character of casing between a value
that means something and a value that means nothing, sitting in the same class.

## The validation went with them

`emergencyReturnCostWattDays + recoveryOpeningCostWattDays > returnReserveCapacityWattDays` looks
like a real guarantee — *"the two costs must fit in the reserve"* — and guaranteed nothing,
because it compared them against a number unrelated to the battery a player actually binds.

**The real guarantee already exists and is unaffected**, in `SpendNativeOpeningTick`:

```csharp
if (NativeStoredEnergy < cost + GateProps.emergencyReturnCostWattDays) { return false; }
```

That one checks the actual stored energy of the actual battery, every tick.

---

## How they were found

A tier-1 research project for the Facilities and power branch was going to grant a capability
that raised `reserveChargePowerWatts`, so that a branch could recharge its reserve faster.

**That would have shipped an unlock that changed nothing** — the exact lie the checkpoint before
this one built `proof-research-branches.py` to prevent, arriving one checkpoint later through a
door the proof does not watch: the proof asserts that a *capability* is read, and this would have
been a capability that *was* read, modifying a prop that was not.

The Facilities tier-1 project now moves `openingPowerDrawWatts` instead, which is read by
`GateFootprint.OpeningPowerDrawWatts` and is what a connection actually costs to hold open.

---

## The general lesson

**A dead prop is a trap for the next person who goes looking for a knob**, because it reads
exactly like a live one — it has a plausible name, a sensible default, and a validation rule
implying somebody cared about it. It is more dangerous than dead code, which at least looks dead.
