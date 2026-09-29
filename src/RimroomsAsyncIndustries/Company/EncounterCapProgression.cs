using System;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// How far the branch has pushed, and therefore how much the Backrooms is allowed to bring
    /// against it.
    ///
    /// **Owner direction, 2026-09-28, verbatim clause:** *"caps on simultaneous encounters,
    /// inhabitants and events per opening and per coordinate, where **raising a cap is itself a
    /// recorded progression step**"*.
    ///
    /// That clause was the last part of the ladder still unmet. 0.8.0-dev built the cap and the
    /// absolute ceiling; what was missing is that the cap should not simply *be* the ceiling
    /// from the first day. It has to be **earned, recorded, and visible in the branch's own
    /// history** — so a player can look back and see the moment the rules changed, rather than
    /// discovering that the world quietly got harder.
    ///
    /// ## The step is reaching a depth nobody has reached before
    ///
    /// Deliberately not research, and not wealth. Wealth already feeds the ladder's ceiling, so
    /// using it again here would double-count the same input. Research is not an act of
    /// exploration. **Pushing deeper than the branch has ever been is the one thing that is
    /// unambiguously the player choosing to escalate**, and tying the cap to it means the
    /// Backrooms never brings more against somebody than they went looking for.
    ///
    /// A branch that stays shallow stays at the opening cap forever, however rich or advanced
    /// it becomes. That is the point.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Simultaneous encounters allowed before any progression step has been taken.
        /// One, so a branch's first dangerous space is dangerous rather than overwhelming.
        /// </summary>
        public const int OpeningEncounterCap = 1;

        /// <summary>Saved. Recorded progression steps that have raised the cap.</summary>
        private int encounterCapSteps;

        /// <summary>Saved. The deepest coordinate the branch has ever entered.</summary>
        private int deepestReached;

        internal void ExposeEncounterProgression()
        {
            Scribe_Values.Look(ref encounterCapSteps, "rr_encounterCapSteps", 0);
            Scribe_Values.Look(ref deepestReached, "rr_deepestReached", 0);
        }

        /// <summary>Recorded progression steps taken so far.</summary>
        public int EncounterCapSteps { get { return encounterCapSteps; } }

        /// <summary>The deepest the branch has ever gone.</summary>
        public int DeepestReached { get { return deepestReached; } }

        /// <summary>
        /// The branch's current cap on simultaneous encounters, before the coordinate's own band
        /// narrows it further.
        ///
        /// **Never above the absolute ceiling**, whatever the step count reaches. The ceiling is
        /// what keeps the owner's solo-survivability condition true, and a progression system
        /// that could grow past it would quietly dismantle that guarantee one step at a time.
        /// </summary>
        public int EncounterCap
        {
            get
            {
                int earned = OpeningEncounterCap + Math.Max(0, encounterCapSteps);
                return Math.Min(earned, Threats.CoordinatePressureLadder.MaxSimultaneousEncounters);
            }
        }

        /// <summary>
        /// Records that the branch has entered a coordinate at this depth, raising the cap if it
        /// is deeper than anywhere it has been.
        ///
        /// Idempotent: reaching the same depth again changes nothing, so a cap cannot be walked
        /// up by repeatedly re-entering one space.
        /// </summary>
        public void NoteDepthReached(int depth)
        {
            if (depth <= deepestReached) { return; }
            deepestReached = depth;

            // Depth 1 is where every branch starts. Reaching it is not an achievement and must
            // not raise anything, or the first coordinate a player ever opens would already
            // have escalated the rules.
            if (depth <= 1) { return; }

            int before = EncounterCap;
            encounterCapSteps++;
            int after = EncounterCap;
            if (after <= before)
            {
                // The ceiling is already reached. The step is still recorded, because the
                // history should show the branch went deeper even when nothing changed.
                RecordEvent("RR_Event_DepthReached", depth.ToString(), depth.ToString());
                return;
            }
            RecordEvent("RR_Event_EncounterCapRaised", depth.ToString(),
                depth.ToString(), after.ToString());
        }
    }
}
