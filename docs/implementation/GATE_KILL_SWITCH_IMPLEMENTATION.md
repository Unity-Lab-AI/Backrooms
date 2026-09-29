# The kill switch, and what cutting power already did (0.7.0-dev)

**Baseline:** `2209930` (0.6.9-dev, 118 C# files, 76 package files).

**This checkpoint — 0.7.0-dev:** **119 C# source files** (one new), **76 approved package files** (unchanged — fourteen keyed strings added to a file that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `3E0DA100B9C78E32AE733429B6F2FAEC48471F46AE40D1A1B11265171BB71464`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/gate-kill-switch-2026-09-29/`](evidence/gate-kill-switch-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies.. idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"*

## What already happened, stated before what is new

This matters because the honest answer changes what needed building.

**Cutting power to an open gate already closed it.** `TickGate` tests `HasPowerAndHeadroom()` every tick and calls `EnterEmergency("RR_Gate_PowerLost")` when it fails, which starts the bounded emergency-return window. And Core's own `Building_PowerSwitch` stops transmitting when it is open, so a switch wired upstream of a gate **already** cut its supply and **already** closed it.

So the physics was most of the way there. What was missing was everything that turns it from an accident into **a control**:

- the gate had no idea which switch was *its* switch, so it could not say so;
- nothing verified the switch was actually on the gate's circuit, so a player could build one, believe it was the kill switch, and discover otherwise in the one moment it mattered;
- a deliberate shutdown and a snapped conduit produced the **identical** message.

All three are closed here.

## The bind is refused unless the switch genuinely powers the gate

This is the part of the request about *how the equipment has to connect and operate*, and it is the whole design.

A switch may only be bound while it is **closed** and while it and the gate sit on the **same power net**:

```csharp
PowerNet gateNet = gatePower.PowerNet;
return gateNet != null && switchPower.PowerNet == gateNet;
```

That one condition separates a real kill switch from a decorative one. If the two share a net while the switch is closed, then opening the switch **necessarily** severs the gate from its supply — nothing has to simulate it, because it is Core's own power graph. The check simply refuses to let the player believe in a switch that would not work.

Requiring it to be **on** at bind time is deliberate and is the reason the check can be that simple: an open switch has already split the net, so the two would legitimately read as different nets and there would be nothing to compare. *Wire it in, close it, then choose it.*

The switch is matched **by capability, never by name** — anything carrying both `CompFlickable` and `CompPowerTransmitter` qualifies — so a modded switch works with nothing here naming it.

One switch may serve one gate. Two gates sharing a cutoff would mean one flick closed both, which is a surprise nobody asked for.

## Thrown means closed now, and the crew still get their window

The tick checks the cutoff **before** the generic power test:

```csharp
if (KillSwitchThrown) { EnterEmergency("RR_NativeGate_KillSwitchThrown"); }
else if (!HasPowerAndHeadroom()) { EnterEmergency("RR_Gate_PowerLost"); }
```

Ordering matters. A thrown switch would cut the supply a tick later anyway, and the recorded cause would then be *power lost* — indistinguishable from a snapped conduit. Somebody threw this, and the log, the readout and the gate's activity record should all say so.

**It does not skip the emergency-return window, and that is a decision rather than a shortfall.** The window is the entire reason the gate reserves its own watt-days; removing it would mean one flick permanently strands everybody on the far side. *"Instantly closes"* is honoured as **the opening ends the moment the switch is thrown** — the far side is sealed to new traffic — while the people already through keep the bounded chance to come back that every other emergency gives them.

## A consequence worth stating out loud

Flicking a switch is ordinary colonist work through Core's `Flick` designation, and this mod added cross-gate `BasicWorker` support in 0.6.7-dev.

So **somebody at home can be ordered to throw the cutoff while a team is still inside.** That is a feature, not an accident: it is precisely the scenario an emergency cutoff exists for, and the return window is what keeps it a decision rather than an execution.

## Optional, because every saved gate has to keep working

`BindNativeKillSwitch` is a **separate call** rather than a fourth argument on `BindNativeInfrastructure`. Every existing binding is untouched, no saved gate needs rebinding, and a gate without a cutoff behaves exactly as it always did.

`KillSwitch` re-derives from the saved reference on every read rather than trusting it — a switch that was deconstructed or ended up on another map stops being the cutoff without anything having to notice and clear it. The same live-re-derivation the emergence anchor uses.

## Saved state

One reference, `rr_gateKillSwitch`, defaulting to null. A 0.6.9-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- `tools/check-keyed-strings.py`: 1,128 keys, 0 duplicates, 1,096 references all resolving, 0 argument mismatches.
- `tools/check-dlc-gating.py` passes. All 58 package XML files parse.
- Compliance: no new def, no patch operation, no asset — the feature is source and keyed strings only. 76 approved package files, 0 missing. No attribution strings.

## What the same direction confirmed rather than changed

The owner's follow-up in the same session:

> *"remember the gate doent always stay open we need requirment s to be maintained and reached.. ie power(its a big draw if power runs out gate closes, research(maintained amounts of maintance and research on equipment but not crazy amounts like i say the first gate opening should be liek 30minuites real time only increasing from there"*

Checked against the shipped values rather than assumed, and **three of the four already match exactly**:

| Direction | Shipped |
|---|---|
| *"if power runs out gate closes"* | `HasPowerAndHeadroom()` fails → `EnterEmergency("RR_Gate_PowerLost")`, every tick |
| *"the first gate opening should be like 30 minutes real time"* | `portalBaseWindowTicks = 108000`. 108,000 ÷ 60 ticks per second = **1,800 seconds = exactly 30 real minutes** at normal speed |
| *"only increasing from there"* | `portalWindowMultiplierPerTier = 3f`, and `portalIndefiniteTier = 4` stops the countdown entirely while power, operator and energy hold |
| *"research ... on equipment"* | tiers are earned from **completed** projects in `portalWindowTierProjects`, never from spendable insight, so a tier cannot be lost by spending |

**The one genuinely new part is maintenance** — *"maintained amounts of maintance ... on equipment but not crazy amounts"*. There is **no equipment-upkeep concept anywhere in the gate** today. That is recorded in `TODO.md` verbatim and scoped to its own checkpoint rather than folded into this one, for the same reason the kill switch was not folded into the emergence work it interrupted.

## Not done, and named

- **Equipment maintenance.** The new half of the direction above.
- **A player-facing how-to for the gameplay and systems.** Also requested in the same message, also recorded. `docs/HOWTO.md` exists but documents the build, not play.

## For the post-completion test phase

Building a power switch **not** on the gate's circuit and confirming it cannot be chosen, with a readable reason; wiring one into the line feeding the gate, closing it, and confirming it can; confirming an open switch is refused at bind time with its own message; opening the gate and throwing the cutoff, and confirming the opening ends at once, the cause reads *emergency cutoff* rather than *power lost*, and the emergency-return window still runs its full length; confirming crew on the far side can still come back inside that window; confirming a second gate cannot claim the same switch; deconstructing a bound switch and confirming the gate reports no cutoff rather than faulting; ordering a colonist at home to flick the cutoff while a team is inside, which is the scenario it exists for; and loading a 0.6.9-dev save to confirm every gate still works with no cutoff set.
