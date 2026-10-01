# Every battery counts — 0.12.77-dev

**Date:** 2026-10-01
**Assembly SHA-256:** `5E87D3842B559E8ABCF44654D2178923D39D8EBE2A7D9F9D36A4FCAB441E39CC`
(measured after the version bump, reproduced by two clean rebuilds)

---

## The report

Owner, verbatim, from a running game:

> *"its the same problem as before: the laboratory address for that is not open.... thats just
> clicking on the portal and trying to send them through not working,,, and using operations
> clicking send pawns through which i think is a power porblem but you can check the game current
> running,, looks like only being able to connect 1 battery isnt anough and there should be no
> loimit"*

**Both halves of that were right.** It was a power problem, and one battery was not enough.

The bridge was not reachable, so this was diagnosed from source rather than from the running game.
Said plainly, because a diagnosis from reading is a weaker claim than one from observing.

---

## Defect one: the reserve was a single battery

`nativeBattery` was only ever meant to be the **anchor** that identifies which power net is the
gate's circuit. Two of the three readings already understood that:

| Reading | Scope |
|---|---|
| `NativeGenerationWatts` | the whole net |
| `NativePowerConnected` | the whole net |
| **`NativeStoredEnergy`** | **one battery** |

So every other battery on the same circuit counted for nothing, and adding batteries did not help.

**And the spend was worse than the reading.** `TrySpendNativeEnergy` refused outright when the
anchor alone could not cover a cost:

```csharp
if (battery == null || battery.StoredEnergy < remaining) { return false; }
```

A drained anchor stalled a gate **with ten full batteries beside it on the same net**.

### The fix, through Core's own mechanisms

| | |
|---|---|
| **Stored** | `PowerNet.CurrentStoredEnergy()` — walks `batteryComps` and skips EMP-stunned batteries, so an EMP'd one stops counting toward a reserve without this code knowing what EMP is |
| **Capacity** | summed `Props.storedEnergyMax` across the net |
| **The draw** | walks `batteryComps` taking from each until paid |

The draw is **copied from Core rather than called**: `PowerNet.ChangeStoredEnergy` does exactly
this with `givingBats[j].DrawPower(num3)` and is `private`. Copying the pattern means the gate
treats batteries the way the game treats its own.

**The anchor is still required.** Removing the limit is not removing the binding — the bound
battery is how a gate knows which net is its own.

---

## Defect two: the refusal named the wrong thing

`HasUsablePortalWindow` collapsed **seven** conditions into one bool.
`RimroomsPortalNetwork` turned a false into `PortalNetworkResult.Closed`.
`PortalTravelService` rendered that as:

> *"The laboratory connection for that address is not open."*

**So a flat battery reported an address fault**, and the owner spent a session looking at the
address.

### The fix

`PortalWindowBlockerKey` is the **third blocker key** in this file's history, after
`CalibrationBlockerKey` and `StaffConsoleBlockerKey` — both added because *"one
`RR_Gate_JobUnavailable` covered four different problems with four different fixes."*

| Cause | Now says |
|---|---|
| No stored charge | the circuit needs power in the batteries, and any number of them count |
| Expedition holds it | recall or close it first |
| In emergency | the crew have a return window; nobody else goes through |
| Window expired | that opening has run out of time |
| Operator off station | the station's own reason |
| Wrong gate | this gate does not hold that connection |

**`HasUsablePortalWindow` delegates to it**, so the predicate that gates a crossing and the message
a player reads cannot disagree. The generic fallback is kept, so a cause nobody anticipated still
produces a sentence rather than silence.

---

## What was checked and ruled out

`returnReserveCapacityWattDays` is **2** and a Core `Battery` holds **600**, so the bind-time
*ReserveTooSmall* refusal was not the cause. Measured rather than assumed.

---

## Verification

**Nothing in forty-eight proofs had ever claimed anything about the energy a gate runs on.**
`grep -l` for `NativeStoredEnergy`, `HasUsablePortalWindow` and `ReturnReserveStored` returned
nothing — which is why a defect this central reached a running game.

**`proof-gate-circuit.py` is proof FORTY-NINE**, 12 claims.
**`plant-gate-circuit.py` is suite TWENTY — 12 of 12 planted faults caught.**

One of those plants found a defect in the proof itself: `List<CompPowerBattery> batteries =
net.batteryComps;` appears **twice**, so an `in` test held while the capacity reader was gutted.
**Duplicate-string trap, third instance in one session.** The claim counts now.

```
16 checkers pass        49 proofs hold        752 plant anchors findable
210 C# files            92 package files      0 warnings, 0 errors
```
