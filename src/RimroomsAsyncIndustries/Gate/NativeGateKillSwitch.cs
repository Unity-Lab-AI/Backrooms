using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The kill switch: a real power switch, wired into the gate's own circuit, that a
    /// colonist can throw to shut an open gate now.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"we also need to have the ability to use a
    /// switch so cutting power instantly closes the lab gate in emergencies.. idk think of
    /// cool shit in how all the equipment needs to connect and operate for a lab gate"*
    ///
    /// ## What already happened, stated plainly before what is new
    ///
    /// Losing power to an open gate **already** closed it. `TickGate` checks
    /// `HasPowerAndHeadroom()` every tick and calls `EnterEmergency("RR_Gate_PowerLost")` when
    /// it fails, which starts the bounded emergency-return window. And Core's own
    /// `Building_PowerSwitch` stops transmitting when it is off, so a switch wired upstream of
    /// a gate would already have cut its power and already have closed it.
    ///
    /// So the physics was most of the way there. What was missing was everything that makes it
    /// **a control rather than an accident**:
    ///
    /// * the gate had no idea which switch was *its* switch, so it could not say so;
    /// * nothing verified the switch was actually on the gate's circuit, so a player could
    ///   build one, believe it was the kill switch, and find out otherwise in an emergency;
    /// * a deliberate shutdown and a snapped conduit produced the identical message.
    ///
    /// This closes all three, and it does it by **making the wiring real rather than
    /// cosmetic** — which is the part of the owner's request about how the equipment has to
    /// connect and operate.
    ///
    /// ## The bind is refused unless the switch genuinely powers the gate
    ///
    /// A switch may only be bound while it is **on** and while it and the gate sit on the
    /// **same power net**. That one condition is what separates a real kill switch from a
    /// decorative one: if the two are on the same net while the switch is closed, then opening
    /// the switch necessarily severs the gate from its supply. Nothing needs to simulate that
    /// — it is Core's own power graph, and the check simply refuses to pretend otherwise.
    ///
    /// The switch is matched **by capability**, never by name: anything carrying both
    /// `CompFlickable` and `CompPowerTransmitter` qualifies, so a modded switch works with
    /// nothing here naming it.
    ///
    /// ## Thrown means closed *now*, and the crew still get their window
    ///
    /// Throwing the switch ends the opening at once with its own distinct cause,
    /// `RR_NativeGate_KillSwitchThrown`, so the log and the readout say *somebody did this*
    /// rather than *the power failed*.
    ///
    /// It does **not** skip the emergency-return window, and that is deliberate rather than a
    /// shortfall. The window is the whole reason the gate reserves its own watt-days; removing
    /// it would mean a single flick permanently strands everyone on the far side. "Instantly
    /// closes" is honoured as *the opening ends the moment the switch is thrown* — the far
    /// side is sealed to new traffic — while the people already through it keep the bounded
    /// chance to come back that every other emergency gives them.
    ///
    /// One consequence worth stating out loud, because it is a feature and not an accident:
    /// flicking a switch is ordinary colonist work through Core's `Flick` designation, and
    /// this mod added cross-gate `BasicWorker` support in 0.6.7-dev. So somebody at home can
    /// be ordered to throw the switch while a team is still inside. That is exactly the
    /// scenario the control exists for.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        private Thing nativeKillSwitch;

        /// <summary>The bound switch, or null. Re-derived rather than trusted: a switch that
        /// was deconstructed or moved off the map stops being one without anything clearing it.</summary>
        public Thing KillSwitch
        {
            get
            {
                if (nativeKillSwitch == null || nativeKillSwitch.Destroyed || !nativeKillSwitch.Spawned ||
                    parent == null || nativeKillSwitch.Map != parent.Map)
                { return null; }
                return nativeKillSwitch;
            }
        }

        /// <summary>True when a bound switch is currently open, cutting the gate's supply.</summary>
        public bool KillSwitchThrown
        {
            get
            {
                Thing wired = KillSwitch;
                if (wired == null) { return false; }
                CompFlickable flick = wired.TryGetComp<CompFlickable>();
                return flick != null && !flick.SwitchIsOn;
            }
        }

        internal void ExposeKillSwitch()
        {
            Scribe_References.Look(ref nativeKillSwitch, "rr_gateKillSwitch");
        }

        /// <summary>
        /// Anything that can be flicked and carries power. Matched by capability so a modded
        /// switch qualifies with nothing here naming it.
        /// </summary>
        internal static bool UsableKillSwitch(Thing thing)
        {
            return thing != null && !thing.Destroyed && thing.Spawned &&
                thing.TryGetComp<CompFlickable>() != null &&
                thing.TryGetComp<CompPowerTransmitter>() != null;
        }

        /// <summary>
        /// Whether this switch really powers this gate right now: both on one net, with the
        /// switch closed. The single condition that makes the link meaningful.
        /// </summary>
        private bool SharesPowerNetWithGate(Thing candidate)
        {
            if (parent == null) { return false; }
            CompPowerTrader gatePower = parent.TryGetComp<CompPowerTrader>();
            CompPower switchPower = candidate == null ? null : candidate.TryGetComp<CompPowerTransmitter>();
            if (gatePower == null || switchPower == null) { return false; }
            PowerNet gateNet = gatePower.PowerNet;
            return gateNet != null && switchPower.PowerNet == gateNet;
        }

        /// <summary>
        /// Bind one switch as this gate's kill switch. Optional: a gate without one behaves
        /// exactly as it always did, which is why this is a separate call rather than a fourth
        /// argument on the existing binding — every saved gate keeps working untouched.
        /// </summary>
        public CompanyActionResult BindNativeKillSwitch(Thing powerSwitch)
        {
            if (!NativeDoorProvider()) { return RefuseNative("UnsupportedProvider"); }
            if (!IsDesignated) { return RefuseNative("NotBound"); }
            if (IsOpening) { return RefuseNative("ActiveCannotRebind"); }
            if (!SameNativeHeadquartersThing(powerSwitch)) { return RefuseNative("HeadquartersRequired"); }
            if (!UsableKillSwitch(powerSwitch)) { return RefuseNative("UnsupportedSwitch"); }
            CompFlickable flick = powerSwitch.TryGetComp<CompFlickable>();
            if (flick == null || !flick.SwitchIsOn) { return RefuseNative("SwitchMustBeOnToBind"); }
            // The condition that makes this a kill switch rather than a decoration.
            if (!SharesPowerNetWithGate(powerSwitch)) { return RefuseNative("SwitchNotOnGateCircuit"); }
            // One switch, one gate. Two gates sharing a switch would make a single flick close
            // both, which is a surprise nobody asked for.
            foreach (Building building in parent.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGate other = building.TryGetComp<CompRimroomsGate>();
                if (other != null && other != this && other.nativeKillSwitch == powerSwitch)
                { return RefuseNative("SwitchAlreadyBound"); }
            }
            if (nativeKillSwitch == powerSwitch) { return CompanyActionResult.Existing(); }
            nativeKillSwitch = powerSwitch;
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_GateKillSwitchBound", parent.GetUniqueLoadID()); }
            return CompanyActionResult.Applied();
        }

        /// <summary>Unbind the switch. The gate keeps working; it simply has no named cutoff.</summary>
        public CompanyActionResult ClearNativeKillSwitch()
        {
            if (IsOpening) { return RefuseNative("ActiveCannotRebind"); }
            if (nativeKillSwitch == null) { return CompanyActionResult.Existing(); }
            nativeKillSwitch = null;
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_GateKillSwitchCleared", parent.GetUniqueLoadID()); }
            return CompanyActionResult.Applied();
        }

        /// <summary>Every switch on this map that could serve, for the player's menu.</summary>
        internal List<Thing> KillSwitchCandidates()
        {
            var found = new List<Thing>();
            if (parent == null || parent.Map == null) { return found; }
            foreach (Building building in parent.Map.listerBuildings.allBuildingsColonist)
            {
                if (UsableKillSwitch(building) && SharesPowerNetWithGate(building)) { found.Add(building); }
            }
            return found;
        }

        internal void OpenKillSwitchMenu()
        {
            var options = new List<FloatMenuOption>();
            foreach (Thing candidate in KillSwitchCandidates())
            {
                Thing choice = candidate;
                options.Add(new FloatMenuOption(choice.LabelCap,
                    delegate { ShowOrderResult(BindNativeKillSwitch(choice)); }));
            }
            if (options.Count == 0)
            {
                // Named rather than an empty menu: the usual reason is that the switch is not
                // on the gate's circuit, which is the whole point and worth saying.
                options.Add(new FloatMenuOption("RR_Gate_NoKillSwitchCandidates".Translate(), null));
            }
            options.Add(new FloatMenuOption("RR_Gate_ClearKillSwitch".Translate(),
                delegate { ShowOrderResult(ClearNativeKillSwitch()); }));
            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>The readout line describing the cutoff, for the gate's inspect string.</summary>
        internal string KillSwitchReadout()
        {
            Thing wired = KillSwitch;
            if (wired == null) { return "RR_Gate_KillSwitchNone".Translate().ToString(); }
            return (KillSwitchThrown ? "RR_Gate_KillSwitchThrown" : "RR_Gate_KillSwitchArmed")
                .Translate(wired.LabelCap).ToString();
        }
    }
}
