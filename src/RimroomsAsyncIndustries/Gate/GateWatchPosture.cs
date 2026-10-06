using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// How long an operator stays at the console before their own body wins.
    ///
    /// ## The defect this closes, which killed a colonist in the first launch
    ///
    /// **Owner report, 2026-10-06, verbatim:** *"current a pawn dies at the comms console... and we
    /// cant have them not going to eat or finding saftey, but there needs to be like a driop down
    /// sleector thing stay at post strict mild, default&gt; inbetween strict and mild"*.
    ///
    /// It was fatal **by construction**, not by bad luck, and three separate things had to be true
    /// at once:
    ///
    /// * `RR_OperateGate` declares `suspendable: false` and `casualInterruptible: false`, so
    ///   RimWorld's own need think-nodes never get the chance to pull the pawn off.
    /// * the station toil is `ToilCompleteMode.Never`, so it has no end of its own.
    /// * its `FailOn` tested the gate, the calibration, the operator's identity, `Downed` and
    ///   `InMentalState` — **and not one need.**
    ///
    /// So the only exits were collapse, a mental break, or the player noticing. The pawn stood
    /// there and starved.
    ///
    /// ## The floor is absolute and it is NOT the setting
    ///
    /// The owner said both halves in one sentence: *"we cant have them not going to eat or finding
    /// saftey"*, **and** that there should be a selector. So the selector tunes **when** an operator
    /// leaves and never **whether**. <see cref="MustLeave"/> is the floor, it is checked before the
    /// posture is consulted at all, and no posture can switch it off.
    ///
    /// **That ordering is the whole safety argument.** A single enum value meaning *never leave*
    /// would be one typo away from the bug this file exists to fix, so the value does not exist.
    ///
    /// ## Why the job stays non-suspendable
    ///
    /// Making the job suspendable would hand the decision to RimWorld's ordinary thresholds, which
    /// is exactly one of the three postures and cannot express the other two. Keeping it ours means
    /// the mod owns the decision, states it, and can be held to the floor by a proof.
    /// </summary>
    public enum GateWatchPosture
    {
        /// <summary>Leaves at the first ordinary need, like any other work. The vanilla instinct.</summary>
        Mild = 0,

        /// <summary>
        /// Between the two, and the shipped default because the owner named it as the default:
        /// *"default&gt; inbetween strict and mild"*.
        /// </summary>
        Balanced = 1,

        /// <summary>
        /// Stays until the floor and not one tick longer. **Not "never leaves"** — that value is
        /// deliberately absent from this enum.
        /// </summary>
        Strict = 2,
    }

    /// <summary>What each posture tolerates, and the floor none of them may cross.</summary>
    public static class GateWatch
    {
        /// <summary>
        /// The one question asked before any posture: is this pawn in danger standing here?
        ///
        /// **Starving and Exhausted are the floor rather than a threshold.** `Starving` is where
        /// RimWorld begins applying malnutrition, and `Exhausted` is where it begins applying
        /// tiredness damage and forces collapse — so staying past either is the mod choosing to
        /// hurt a colonist. Burning is immediate and obvious.
        ///
        /// A null need is treated as no reason to leave rather than as a reason: a mech or anything
        /// without a food need has nothing to flee from here, and reading null as danger would make
        /// such a pawn unable to hold a post at all.
        /// </summary>
        public static bool MustLeave(Pawn pawn)
        {
            if (pawn == null) { return true; }
            if (pawn.Downed || pawn.Dead || pawn.InMentalState) { return true; }
            if (pawn.IsBurning()) { return true; }
            Need_Food food = pawn.needs == null ? null : pawn.needs.food;
            if (food != null && food.CurCategory >= HungerCategory.Starving) { return true; }
            Need_Rest rest = pawn.needs == null ? null : pawn.needs.rest;
            if (rest != null && rest.CurCategory >= RestCategory.Exhausted) { return true; }
            // Bleeding out is the one injury state where standing still is the thing killing them.
            return pawn.health != null && pawn.health.hediffSet != null
                && pawn.health.hediffSet.BleedRateTotal > 0.1f;
        }

        /// <summary>
        /// Whether this posture releases the operator now. <see cref="MustLeave"/> is asked first
        /// and separately, so a `false` here never means *stay regardless*.
        /// </summary>
        public static bool Releases(Pawn pawn, GateWatchPosture posture)
        {
            if (pawn == null) { return true; }
            Need_Food food = pawn.needs == null ? null : pawn.needs.food;
            Need_Rest rest = pawn.needs == null ? null : pawn.needs.rest;
            switch (posture)
            {
                case GateWatchPosture.Mild:
                    // Ordinary work behaviour: the first real need wins.
                    if (food != null && food.CurCategory >= HungerCategory.Hungry) { return true; }
                    if (rest != null && rest.CurCategory >= RestCategory.Tired) { return true; }
                    return false;
                case GateWatchPosture.Strict:
                    // Only the floor, which is asked by the caller. Nothing extra here, and that
                    // is the point: Strict adds no tolerance of its own beyond the floor.
                    return false;
                default:
                    // Balanced. One step past ordinary and one step short of harm.
                    if (food != null && food.CurCategory >= HungerCategory.UrgentlyHungry) { return true; }
                    if (rest != null && rest.CurCategory >= RestCategory.VeryTired) { return true; }
                    return false;
            }
        }

        /// <summary>
        /// Why the operator left, for the player rather than for a log. Returns null when nothing
        /// releases them, so a caller can use it as the whole test.
        /// </summary>
        public static string ReleaseReasonKey(Pawn pawn, GateWatchPosture posture)
        {
            if (MustLeave(pawn)) { return "RR_GateWatch_LeftFloor"; }
            return Releases(pawn, posture) ? "RR_GateWatch_LeftPosture" : null;
        }

        public static string LabelKey(GateWatchPosture posture)
        {
            switch (posture)
            {
                case GateWatchPosture.Mild: return "RR_GateWatch_Mild";
                case GateWatchPosture.Strict: return "RR_GateWatch_Strict";
                default: return "RR_GateWatch_Balanced";
            }
        }

        public static string DescriptionKey(GateWatchPosture posture)
        {
            switch (posture)
            {
                case GateWatchPosture.Mild: return "RR_GateWatch_MildDesc";
                case GateWatchPosture.Strict: return "RR_GateWatch_StrictDesc";
                default: return "RR_GateWatch_BalancedDesc";
            }
        }
    }
}
