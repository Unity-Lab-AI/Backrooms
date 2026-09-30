using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// **A damaged gate needs work before it will hold a connection again**, and a record of how
    /// its openings have actually gone.
    ///
    /// Row 725 asks for *"power reserves, calibration, stabilizers, monitoring, emergency cutoff,
    /// cool-down, modules, repair, and reliability"*. Seven of those nine were already built and
    /// were checked before anything was written here, which is the habit that has closed eight
    /// rows this session:
    ///
    /// | Asked for | Already built as |
    /// |---|---|
    /// | power reserves | the bound battery, `ReturnReserveStoredWattDays` and the watt-day costs |
    /// | calibration | `calibrated`, its work giver and its refusal |
    /// | **stabilizers** | **`PortalWindowTier`** — a four-rung project ladder that multiplies the window and stops the countdown entirely at tier 4 |
    /// | monitoring | the inspect readout, three gate alerts (0.10.5-dev), two containment alerts (0.12.35-dev) |
    /// | emergency cutoff | `TriggerEmergencyCutoff`, the kill switch, and the containment procedure that calls it |
    /// | cool-down | the opening clock and the return window |
    /// | **modules** | **`GateEquipmentLinks`** — roles, `maxLinked`, single ownership across gates, built to *"reach fare and through walls"* |
    ///
    /// **Repair and reliability were the two genuine gaps**, and measuring found the more
    /// interesting of the two:
    ///
    /// ## A gate read no damage at all
    ///
    /// Nothing in `CompRimroomsGate` looked at `HitPoints`. A gate could be shot to twelve per
    /// cent, set on fire, and hit by a mortar, and it would still open a connection and hold it
    /// perfectly. `calibrated` was lost only when the binding changed. So the machine the whole
    /// mod is built around was the one building in the colony that damage did not affect.
    ///
    /// The fix is deliberately not a new mechanic. **Damage below the threshold loses
    /// calibration**, which is a state that already exists, already has a work giver, already has
    /// a refusal, and already reads in the inspect pane. So:
    ///
    /// * a beaten-up gate refuses to open, **with a reason the player can read**;
    /// * fixing it is **Core's own repair work** — nothing here repairs anything;
    /// * bringing it back is **the calibration job that already existed**.
    ///
    /// No new def, no new job, no new work giver, and one new failure reason.
    ///
    /// **That failure reason is a deliberate seventh.** `proof-areas-and-debrief.py` asserts the
    /// complete set of ways a gate can stop working — it was six — precisely so that an addition
    /// has to be made on purpose and cannot arrive unnoticed. It was six because row 98 needed
    /// to prove that ordinary map work near a gate cannot break it; this is a change to the
    /// machine itself rather than to its surroundings, so row 98's claim is untouched.
    ///
    /// ## Reliability is a record, not a dice roll
    ///
    /// The tempting reading of *"reliability"* is a failure chance that rises with use. That
    /// would be wrong here twice over. **Invariant 28 wants every rule learnable**, and a machine
    /// that sometimes fails for no visible reason is the definition of unlearnable; and this mod's
    /// failures are all deterministic and all named, which is what makes them fair.
    ///
    /// So reliability is **what actually happened**, counted per coordinate: how many openings
    /// completed and how many ended in an emergency. That is monitoring made useful — it tells a
    /// player which addresses have been costing them return windows — it is deterministic, it
    /// reads out of the history the gate already keeps, and it invents no number.
    ///
    /// `GateHistoryEntry` already recorded `times`, `firstTick` and `lastTick` per coordinate and
    /// **nothing about how any of it went**, which is why the history could not answer the one
    /// question a player would ask of it.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py family facilities` (swept) and `trace RR-GATE`. The facilities family's
    /// standing position is that this mod adds no construction or power mechanic of its own and
    /// leaves native building alone, and that is honoured exactly: **the damage read is
    /// `HitPoints` against `MaxHitPoints`**, both Core's, and the repair is Core's. A mod that
    /// changes building health, armour or repair rates changes Core's numbers and the threshold
    /// here reads whatever they become, because it is a fraction rather than an absolute.
    ///
    /// Nothing is patched, nothing is required, and every mod may be absent.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>
        /// How battered a gate may be and still hold a connection.
        ///
        /// Half, because it has to be a fraction rather than a hit-point count: the profile
        /// contains mods that change building health and armour, and an absolute number would
        /// mean something different in each of them. Half is also generous enough that ordinary
        /// wear and a stray shot do not cost a player their connection — it takes a real
        /// attack — which matters because losing calibration costs work to undo.
        /// </summary>
        public const float IntegrityFloorFraction = 0.5f;

        /// <summary>
        /// This gate's condition as a fraction, or 1 when the building does not use hit points
        /// at all. Core's numbers, read and never written.
        /// </summary>
        public float IntegrityFraction
        {
            get
            {
                if (parent == null || parent.def == null || !parent.def.useHitPoints)
                { return 1f; }
                int maximum = parent.MaxHitPoints;
                if (maximum <= 0) { return 1f; }
                return (float)parent.HitPoints / maximum;
            }
        }

        /// <summary>Whether the machine is sound enough to be trusted with a connection.</summary>
        public bool IntegritySound
        { get { return IntegrityFraction >= IntegrityFloorFraction; } }

        /// <summary>
        /// Checked from the gate's own tick. Losing calibration is the whole effect, because
        /// calibration is a state the player already understands, already has a job for, and
        /// already sees in the inspect pane.
        ///
        /// Ordered so the common case costs one float comparison: a sound gate returns at the
        /// first test, every tick, forever.
        /// </summary>
        internal void TickIntegrity()
        {
            if (!IsDesignated || IntegritySound) { return; }
            // An opening in progress is ended rather than left running on a machine that is
            // coming apart. The emergency path is the one that brings the crew home, which is
            // the difference between a gate failing and a gate losing people.
            if (IsOpening && !IsEmergency)
            { EnterEmergency("RR_Gate_IntegrityLost"); }
            if (!calibrated) { return; }
            calibrated = false;
            stablePowerTicks = 0;
            Find.LetterStack.ReceiveLetter("RR_Letter_GateIntegrityLabel".Translate(),
                "RR_Letter_GateIntegrityText".Translate(parent.LabelCap,
                    IntegrityFraction.ToStringPercent("F0")),
                LetterDefOf.NegativeEvent, parent);
        }

        /// <summary>
        /// Why this gate cannot be trusted right now, or null. Read by the opening refusal and
        /// by the readout, so the two cannot disagree about whether the machine is sound.
        /// </summary>
        public string IntegrityFailureKey
        { get { return IntegritySound ? null : "RR_Gate_IntegrityTooLow"; } }
    }
}
