using RimroomsAsyncIndustries.Gate;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// The gate's aura: its colour and its radius, driven by the gate's own state.
    ///
    /// **Owner, 2026-10-06, verbatim:** *"maybe have the auro for the gat be gate sensitive change
    /// color to the state of the gate and like strobe on charge up callibation and activation and
    /// shit like star trek warp core"*.
    ///
    /// ## Why this is a second cadence rather than a faster first one
    ///
    /// `RefreshGateAppearance` runs every **250 ticks**, and its own docstring says why: `IsLiveGate`
    /// **walks every edge in the portal network**, which is not a per-tick question for every door
    /// in a colony. A strobe needs roughly four samples a second. Running the existing refresh that
    /// fast would perform that network walk **sixteen times more often, on every door in the
    /// colony**, to animate at most three gates.
    ///
    /// So the expensive question stays slow and its answer is cached in <see cref="auraLive"/>; only
    /// the cheap question — *what colour should this be right now* — runs fast.
    ///
    /// ## And it only touches the glow grid when something actually changed
    ///
    /// `CompGlower.UpdateLit` makes Core recompute that light's contribution to the map's glow grid.
    /// Calling it on every sample would be four grid updates a second per gate whether or not
    /// anything moved. The resolved colour and radius are compared against what was last pushed, and
    /// **the radius is quantised** so a pulse that moves by a hundredth of a cell does not count as
    /// a change. In the steady states — idle, live, not a gate — the aura settles and stops writing
    /// entirely.
    ///
    /// ## What does not change, deliberately
    ///
    /// **A live gate looks exactly as it did.** `LiveGlowColor` at `LiveGlowRadius`, steady. An
    /// existing colony sees no difference in the state it spends most of its time in, so this cannot
    /// be read as a regression by somebody who liked it.
    ///
    /// **A natural gate gets no state behaviour either.** It has no `CompRimroomsGate` states to
    /// read, so it falls through to the plain live blue — which is the same decision the owner made
    /// about the machine frame: *"lets keep natural doors just normal doors in game so there is
    /// distinction for it"*.
    ///
    /// ## And it is never the only signal
    ///
    /// `THREAT_DESIGN_SHEETS.md` binds this: *"Do not use color or sound as the only way to notice a
    /// tell."* Every state below already has a message, a pane indicator or both before the aura
    /// says anything. The aura is allowed to be beautiful; it is not allowed to be the evidence.
    /// </summary>
    public partial class CompRimroomsEmergence
    {
        /// <summary>Four samples a second. Fast enough to read as motion, slow enough to be cheap.</summary>
        private const int AuraInterval = 15;

        /// <summary>A designated gate that is doing nothing: present, not working.</summary>
        private static readonly ColorInt IdleGlowColor = new ColorInt(44, 80, 140, 0);
        private const float IdleGlowRadius = 2.5f;

        /// <summary>The ramp runs blue to near-white as the work completes. This is the far end.</summary>
        private static readonly ColorInt ChargedGlowColor = new ColorInt(185, 225, 255, 0);

        /// <summary>A fault while open. Amber, because the player already reads amber as a fault here.</summary>
        private static readonly ColorInt EmergencyGlowColor = new ColorInt(235, 150, 40, 0);

        /// <summary>Nobody is coming back on their own. The one state that earns red.</summary>
        private static readonly ColorInt RecoveryGlowColor = new ColorInt(235, 60, 50, 0);

        // A slow breath at rest and a hard rev at full. The rising RATE is what reads as a machine
        // winding up -- a fixed blink reads as a warning light, which is the opposite meaning.
        private const int ChargeSlowestPulseTicks = 96;
        private const int ChargeFastestPulseTicks = 20;
        private const int EmergencyPulseTicks = 80;
        private const int RecoveryPulseTicks = 36;

        /// <summary>Cached by the slow pass, because answering it walks the portal network.</summary>
        private bool auraLive;

        // What was last pushed to the glower, so nothing is pushed twice.
        private bool auraPushed;
        private float auraLastRadius = -1f;
        private ColorInt auraLastColor;

        /// <summary>
        /// Resolve the aura for this instant and push it only if it differs from the last push.
        ///
        /// Safe to call at any cadence and from either ticker. Does nothing at all when the parent
        /// is gone, unspawned or carries no glower.
        /// </summary>
        private void ApplyAura()
        {
            if (parent == null || !parent.Spawned || parent.Map == null) { return; }
            CompGlower glower = parent.TryGetComp<CompGlower>();
            if (glower == null) { return; }

            ColorInt colour;
            float radius;
            ResolveAura(out colour, out radius);

            // Quantised before comparing. A pulse moving by a hundredth of a cell is not a change
            // worth recomputing a map's glow grid for.
            radius = Mathf.Round(radius * 4f) / 4f;
            if (auraPushed && Mathf.Approximately(radius, auraLastRadius) && SameColor(colour, auraLastColor))
            { return; }

            glower.GlowRadius = radius;
            glower.GlowColor = colour;
            glower.UpdateLit(parent.Map);

            auraPushed = true;
            auraLastRadius = radius;
            auraLastColor = colour;
        }

        /// <summary>
        /// What the aura should be right now.
        ///
        /// **Ordered worst-state-first on purpose.** A gate that is open and faulted is both open and
        /// faulted; a player needs to see the fault. Checking the pleasant states first would hide
        /// the one that matters behind the one that does not.
        /// </summary>
        private void ResolveAura(out ColorInt colour, out float radius)
        {
            colour = LiveGlowColor;
            radius = auraLive ? LiveGlowRadius : 0f;

            CompRimroomsGate gate = parent.TryGetComp<CompRimroomsGate>();
            if (gate == null) { return; }

            if (gate.IsAwaitingRecovery)
            {
                colour = RecoveryGlowColor;
                radius = Pulse(RecoveryPulseTicks, LiveGlowRadius * 0.45f, LiveGlowRadius * 1.15f);
                return;
            }
            if (gate.IsEmergency)
            {
                colour = EmergencyGlowColor;
                radius = Pulse(EmergencyPulseTicks, LiveGlowRadius * 0.6f, LiveGlowRadius);
                return;
            }
            // **Open and well: untouched.** This is the state a colony spends most of its life in.
            if (auraLive) { return; }

            if (gate.IsSpinningUp)
            {
                // The rev. Colour climbs toward white with the work, and the pulse gets faster with
                // it, so the gate sounds and looks like it is being wound up rather than blinking.
                float progress = Mathf.Clamp01(gate.SpinUpProgress);
                colour = LerpColor(IdleGlowColor, ChargedGlowColor, progress);
                int period = Mathf.RoundToInt(Mathf.Lerp(ChargeSlowestPulseTicks,
                    ChargeFastestPulseTicks, progress));
                float ceiling = Mathf.Lerp(IdleGlowRadius, LiveGlowRadius, progress);
                radius = Pulse(Mathf.Max(1, period), ceiling * 0.55f, ceiling);
                return;
            }

            if (gate.IsDesignated)
            {
                colour = IdleGlowColor;
                radius = IdleGlowRadius;
            }
        }

        /// <summary>
        /// A triangle wave between two radii. Triangular rather than square: a hard on/off is a
        /// hazard light, and this is a machine running.
        /// </summary>
        private static float Pulse(int periodTicks, float low, float high)
        {
            if (Current.Game == null || Find.TickManager == null || periodTicks <= 0) { return high; }
            int position = Find.TickManager.TicksGame % periodTicks;
            float phase = position / (float)periodTicks;
            float wave = 1f - Mathf.Abs((phase * 2f) - 1f);
            return Mathf.Lerp(low, high, wave);
        }

        private static ColorInt LerpColor(ColorInt from, ColorInt to, float amount)
        {
            return new ColorInt(
                Mathf.RoundToInt(Mathf.Lerp(from.r, to.r, amount)),
                Mathf.RoundToInt(Mathf.Lerp(from.g, to.g, amount)),
                Mathf.RoundToInt(Mathf.Lerp(from.b, to.b, amount)),
                0);
        }

        private static bool SameColor(ColorInt left, ColorInt right)
        {
            return left.r == right.r && left.g == right.g && left.b == right.b;
        }
    }
}
