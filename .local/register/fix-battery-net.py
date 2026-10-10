# -*- coding: utf-8 -*-
"""Every battery on the gate's circuit counts, and there is no limit.

Owner, 2026-10-01, from a running game: *"looks like only being able to connect 1 battery isnt
anough and there should be no loimit"*, and *"which i think is a power porblem"*.

**The owner is right, and the mechanism is worse than the symptom.**

The bound battery was only ever meant to be the **anchor** that identifies which power net is the
gate's circuit. `NativeGenerationWatts` already sums the whole net. `NativePowerConnected` already
checks the whole net. **Stored energy was the one reading that never followed** -- it read
`nativeBattery.StoredEnergy` and nothing else, so every other battery on the same net counted for
nothing.

And the spend was worse than the read: `TrySpendNativeEnergy` refused outright when
`battery.StoredEnergy < remaining`, so **a drained bound battery stalled the gate with ten full
batteries beside it.**

## Why it read as an address fault

`HasUsablePortalWindow`'s last condition is the stored-energy check, and it is asked **on every
attempt to cross**. `RimroomsPortalNetwork` turns a false into `PortalNetworkResult.Closed`, which
`PortalTravelService` renders as *"The laboratory connection for that address is not open."*

So a flat battery reported an address problem. **The message named the wrong thing**, which is why
the owner spent the session looking at the address.

## What this changes

| | |
|---|---|
| `NativeStoredEnergy` | Core's own `PowerNet.CurrentStoredEnergy()` -- every battery on the net, and it skips EMP-stunned ones for free |
| `NativeBatteryCapacity` | summed `storedEnergyMax` across the net |
| the draw | walks `net.batteryComps` taking from each until paid, **which is exactly what Core's own `ChangeStoredEnergy` does** at its `givingBats[j].DrawPower(num3)` -- that method is private, so the pattern is copied rather than called |

**No limit.** Bind one battery as the anchor, then put as many as you like on the circuit.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BINDING = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "NativeGateBinding.cs")

OLD_READERS = u"""        private float NativeStoredEnergy
        {
            get
            {
                CompPowerBattery battery = NativeBatteryComp;
                return battery == null || !FiniteNonnegative(battery.StoredEnergy) ? 0f : battery.StoredEnergy;
            }
        }
        private float NativeBatteryCapacity
        {
            get
            {
                CompPowerBattery battery = NativeBatteryComp;
                return battery == null || !FiniteNonnegative(battery.Props.storedEnergyMax) ? 0f : battery.Props.storedEnergyMax;
            }
        }"""

NEW_READERS = u"""        /// <summary>
        /// The power net the gate's circuit is. **The bound battery is an anchor, not the
        /// reserve.**
        ///
        /// Owner, 2026-10-01, from a running game: *"only being able to connect 1 battery isnt
        /// anough and there should be no loimit"*. `NativeGenerationWatts` has always summed this
        /// whole net and `NativePowerConnected` has always checked it; the stored-energy reading
        /// was the one that never followed, and it read a single battery.
        /// </summary>
        private PowerNet NativePowerNet
        {
            get
            {
                CompPowerBattery battery = NativeBatteryComp;
                return battery == null ? null : battery.PowerNet;
            }
        }

        /// <summary>
        /// Everything stored on the gate's circuit, through **Core's own sum**.
        ///
        /// `PowerNet.CurrentStoredEnergy()` walks `batteryComps` and skips anything stunned by
        /// EMP, so an EMP'd battery stops counting toward a reserve without this having to know
        /// what EMP is.
        /// </summary>
        private float NativeStoredEnergy
        {
            get
            {
                PowerNet net = NativePowerNet;
                if (net == null) { return 0f; }
                float stored = net.CurrentStoredEnergy();
                return FiniteNonnegative(stored) ? stored : 0f;
            }
        }

        /// <summary>
        /// What the gate's circuit could hold if full. Summed across the net for the same reason
        /// the stored figure is: the readout a player reads has to be about the circuit they
        /// built, not about whichever battery they happened to click first.
        /// </summary>
        private float NativeBatteryCapacity
        {
            get
            {
                PowerNet net = NativePowerNet;
                if (net == null) { return 0f; }
                float total = 0f;
                List<CompPowerBattery> batteries = net.batteryComps;
                for (int index = 0; index < batteries.Count; index++)
                {
                    CompPowerBattery battery = batteries[index];
                    if (battery == null || battery.StunnedByEMP || battery.Props == null) { continue; }
                    float most = battery.Props.storedEnergyMax;
                    if (FiniteNonnegative(most)) { total += most; }
                }
                return total;
            }
        }

        /// <summary>
        /// Draws across every battery on the circuit and reports what was actually taken.
        ///
        /// **Copied from Core rather than called**: `PowerNet.ChangeStoredEnergy` does exactly
        /// this with `givingBats[j].DrawPower(num3)` and is `private`, so the pattern is
        /// reproduced and the behaviour matches what the game does to its own batteries.
        ///
        /// Returns the observed total, never the requested one. A battery that refuses to give
        /// what it said it held is the case the debit-fault machinery exists for, and that
        /// machinery compares observed against requested.
        /// </summary>
        private float DrawFromNativeCircuit(float amount)
        {
            PowerNet net = NativePowerNet;
            if (net == null || !FiniteNonnegative(amount) || amount <= 0f) { return 0f; }
            float remaining = amount;
            float drawn = 0f;
            List<CompPowerBattery> batteries = net.batteryComps;
            for (int index = 0; index < batteries.Count && remaining > 0f; index++)
            {
                CompPowerBattery battery = batteries[index];
                if (battery == null || battery.StunnedByEMP) { continue; }
                float available = battery.StoredEnergy;
                if (!FiniteNonnegative(available) || available <= 0f) { continue; }
                float take = available < remaining ? available : remaining;
                float before = battery.StoredEnergy;
                battery.DrawPower(take);
                float observed = before - battery.StoredEnergy;
                if (!FiniteNonnegative(observed)) { continue; }
                drawn += observed;
                remaining -= observed;
            }
            return drawn;
        }"""

OLD_IDLE = u"""            CompPowerBattery battery = NativeBatteryComp;
            if (battery == null) { return; }
            if (NativeStoredEnergy - cost < GateProps.emergencyReturnCostWattDays) { return; }
            battery.DrawPower(cost);"""

NEW_IDLE = u"""            if (NativePowerNet == null) { return; }
            if (NativeStoredEnergy - cost < GateProps.emergencyReturnCostWattDays) { return; }
            // Across the whole circuit, not out of one battery.
            DrawFromNativeCircuit(cost);"""

OLD_SPEND = u"""            CompPowerBattery battery = NativeBatteryComp;
            if (battery == null || !FiniteNonnegative(battery.StoredEnergy) || battery.StoredEnergy < remaining) { return false; }
            float before = battery.StoredEnergy;
            Exception interrupted = null;
            try { battery.DrawPower(remaining); }
            catch (Exception exception) { interrupted = exception; }
            float observed = before - battery.StoredEnergy;"""

NEW_SPEND = u"""            // **The circuit, not the one bound battery.** This refused outright when the bound
            // battery alone could not cover the cost, so a drained anchor stalled a gate that had
            // ten full batteries beside it on the same net. That is the defect the owner found in
            // a running game: *"only being able to connect 1 battery isnt anough"*.
            float availableNow = NativeStoredEnergy;
            if (NativePowerNet == null || !FiniteNonnegative(availableNow) || availableNow < remaining)
            { return false; }
            float before = availableNow;
            Exception interrupted = null;
            float taken = 0f;
            try { taken = DrawFromNativeCircuit(remaining); }
            catch (Exception exception) { interrupted = exception; }
            float observed = FiniteNonnegative(taken) ? taken : before - NativeStoredEnergy;"""

EDITS = [(OLD_READERS, NEW_READERS), (OLD_IDLE, NEW_IDLE), (OLD_SPEND, NEW_SPEND)]

text = io.open(BINDING, encoding="utf-8-sig").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:56]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(BINDING, "w", encoding="utf-8-sig", newline="").write(text)

after = io.open(BINDING, encoding="utf-8-sig").read()
failures = []
if u"net.CurrentStoredEnergy()" not in after:
    failures.append("the stored reading is not net-wide")
if u"private float DrawFromNativeCircuit(float amount)" not in after:
    failures.append("the net-wide draw was not defined")
if after.count(u"DrawFromNativeCircuit(") < 3:
    failures.append("THE NET-WIDE DRAW IS DEFINED AND NOT CALLED EVERYWHERE -- %d call site(s)"
                    % (after.count(u"DrawFromNativeCircuit(") - 1))
if u"battery.DrawPower(cost);" in after:
    failures.append("the idle tick still draws from one battery")
if u"battery.StoredEnergy < remaining" in after:
    failures.append("the spend still refuses on one battery's charge")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("the reserve is the whole circuit; no battery limit; draw copied from Core's own pattern")
