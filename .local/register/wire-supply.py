# -*- coding: utf-8 -*-
"""reserveChargePowerWatts as a supply requirement, and the dead headroom it revives."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ live generation on the circuit
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Gate', 'NativeGateBinding.cs')
sub(p, u"""        private bool NativePowerConnected()""",
u"""        /// <summary>
        /// What the gate's own circuit is **generating** right now, in watts.
        ///
        /// Only what is actually producing: a generator that is switched off, broken down or out
        /// of fuel contributes nothing, which is the entire point of asking. Stored charge is
        /// deliberately not counted — a battery is not supply, it is a buffer, and the owner's
        /// answer names delivery: *"the gate refuses to open unless its circuit can deliver this
        /// much power"*.
        /// </summary>
        private float NativeGenerationWatts()
        {
            CompPowerBattery battery = NativeBatteryComp;
            PowerNet net = battery == null ? null : battery.PowerNet;
            if (net == null) { return 0f; }
            float total = 0f;
            List<CompPowerTrader> traders = net.powerComps;
            for (int index = 0; index < traders.Count; index++)
            {
                CompPowerTrader trader = traders[index];
                if (trader == null || !trader.PowerOn) { continue; }
                float output = trader.PowerOutput;
                if (output > 0f && !float.IsNaN(output) && !float.IsInfinity(output)) { total += output; }
            }
            return total;
        }

        private bool NativePowerConnected()""")
print('NativeGenerationWatts added')

# ------------------------------------------------------------------ the opening supply gate
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGate.cs')
sub(p, u"""        /// <summary>Opening load is paid from the linked battery, never charged twice as grid load.</summary>
        private bool HasProjectedOpeningPowerHeadroom()
        {
            return NativeBindingFailureKey == null;
        }""",
u"""        /// <summary>
        /// Whether the circuit can support **starting** an opening, or a keyed reason why not.
        ///
        /// Opening load is paid from the linked battery, never charged twice as grid load — so this
        /// asks about **supply**, not about the cost of the opening itself.
        ///
        /// ## Two values that had nothing reading them
        ///
        /// **`reserveChargePowerWatts`.** Owner's answer, 2026-09-29, verbatim: *"A supply
        /// requirement before opening"* — *the gate refuses to open unless its circuit can deliver
        /// this much power*. Generation, not stored charge: a battery is a buffer, not supply, and
        /// a gate opened on one charged battery and no generator is a gate about to strand a crew.
        ///
        /// **`MinimumPowerHeadroomWatts`, which was read by NOTHING.** Found while wiring the
        /// above. Its own docstring says *"headroom a gate needs above its draw before it will
        /// open"*, and no code asked. Worse: **`RR_Cap_ReserveDiscipline` is granted by the tier 0
        /// Facilities project and its whole effect was to lower that unread number**, so the card
        /// promised *"the gate needs less spare headroom above its draw before it will open"* and
        /// changed nothing a player could ever observe.
        ///
        /// That is **invariant 136** exactly, and it is why the research proof could not catch it:
        /// the capability *is* read by real code, and the code reading it was itself dead. A live
        /// read site is not a live effect. Both values are now consumed here, so the tier 0
        /// Facilities unlock finally does the thing it says.
        ///
        /// **This gates opening only.** It is called once, from the can-open check, and never from
        /// the tick — a generation dip must not emergency-return a crew that is already through.
        /// </summary>
        private string ProjectedOpeningPowerFailure()
        {
            if (NativeBindingFailureKey != null) { return NativeBindingFailureKey; }
            float generation = NativeGenerationWatts();
            if (generation < GateProps.reserveChargePowerWatts)
            { return "RR_Gate_SupplyTooLow"; }
            if (generation < CurrentPowerDrawWatts + MinimumPowerHeadroomWatts)
            { return "RR_Gate_HeadroomTooLow"; }
            return null;
        }""")

sub(p, u"""            if (!HasProjectedOpeningPowerHeadroom())
            { return CompanyActionResult.Refused("RR_Gate_OpeningPowerUnstable"); }""",
u"""            // A keyed reason rather than one blanket refusal: "the circuit cannot deliver
            // enough" and "there is no margin above what the gate already draws" are different
            // problems with different fixes, and one string for both always lied about one.
            string supply = ProjectedOpeningPowerFailure();
            if (supply != null) { return CompanyActionResult.Refused(supply); }""")
print('opening supply gate wired')

# ------------------------------------------------------------------ keyed strings
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Gate.xml')
s = io.open(p, encoding='utf-8-sig').read()
for key in ('RR_Gate_SupplyTooLow', 'RR_Gate_HeadroomTooLow'):
    assert key not in s, '%s already present' % key
block = (u'  <RR_Gate_SupplyTooLow>The circuit cannot deliver enough power to start an opening. '
         u'A charged battery is not supply: the gate needs generators actually running.</RR_Gate_SupplyTooLow>\n'
         u'  <RR_Gate_HeadroomTooLow>There is no margin left above what the gate already draws. '
         u'Add generation, or take something else off this circuit.</RR_Gate_HeadroomTooLow>\n')
i = s.rindex(u'</LanguageData>')
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + block + s[i:])
ET.parse(p)
print('keyed strings added and parsed')
