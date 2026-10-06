using RimroomsAsyncIndustries.Core;
using Verse;
using Verse.Sound;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The gate's two looping cues: the charge loop while it ramps, and the quieter presence while
    /// a connection is open.
    ///
    /// **Owner, 2026-10-06:** *"ramp up and down and rev"*.
    ///
    /// ## Reconciled every tick, never started and stopped by event
    ///
    /// The obvious shape is start-on-begin and stop-on-end. It is also the shape that leaks: every
    /// path that ends a ramp — completion, abort, lapse, power loss, the operator walking away, a
    /// fault, a save reloaded mid-cycle — would each need to remember to stop the sound, and the
    /// first one anybody forgets is **a hum that plays until the map unloads**.
    ///
    /// So nothing is started or stopped by an event. Every tick asks *what should be playing right
    /// now* and makes reality match. **It is self-healing in both directions:** a loop that should
    /// have stopped stops on the next tick, and a game reloaded in the middle of a ramp starts the
    /// loop again with no saved state at all. Nothing about this is scribed, deliberately — a sound
    /// is not part of a save.
    ///
    /// ## And it survives the gate dying, which the event shape would not
    ///
    /// The sustainer is created with `MaintenanceType.PerTick`, so RimWorld ends it itself as soon
    /// as it stops being maintained. A destroyed gate stops ticking and therefore stops maintaining,
    /// and the sound dies on its own. **Forgetting to stop one is not a failure mode here.**
    ///
    /// ## Where it is called from, and why not inside TickGate
    ///
    /// `TickGate` returns early when the gate is unspawned or in a portal-owner fault. Reconciling
    /// inside it would mean a gate that faults mid-ramp keeps its loop running for ever — the exact
    /// leak this shape exists to prevent. It is called from `CompTick` **outside** that guard, and
    /// answers "nothing" for those states rather than being skipped.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        private Sustainer loopSustainer;
        private string loopCueId;

        /// <summary>The cue that should be looping right now, or null for silence.</summary>
        private string DesiredLoopCue
        {
            get
            {
                if (parent == null || !parent.Spawned || parent.Destroyed || parent.Map == null)
                { return null; }
                if (RimroomsMod.Settings == null) { return null; }
                // **A faulted gate falls silent rather than droning.** The emergency has its own
                // one-shot and its own aura; a steady hum underneath would say the machine is fine.
                if (IsEmergency || IsAwaitingRecovery) { return null; }
                if (IsSpinningUp) { return "RR_GateSpinLoop"; }
                return IsOpening ? "RR_GateOpenLoop" : null;
            }
        }

        /// <summary>
        /// Make the running loop match the state, then maintain it.
        ///
        /// Called every tick from <c>CompTick</c>, outside the early returns, so that "should be
        /// nothing" is a state this can act on rather than one it never sees.
        /// </summary>
        private void TickGateLoops()
        {
            string wanted = DesiredLoopCue;

            if (loopSustainer != null && (wanted == null || wanted != loopCueId ||
                loopSustainer.Ended))
            {
                // Ended already cleans itself up; calling End on a finished sustainer is refused by
                // Core, so the check is not optional.
                if (!loopSustainer.Ended) { loopSustainer.End(); }
                loopSustainer = null;
                loopCueId = null;
            }

            if (wanted == null) { return; }

            if (loopSustainer == null)
            {
                loopSustainer = Audio.RimroomsAudio.TryStartSustainer(
                    wanted, parent.Map, parent.Position, false);
                // A null here is normal rather than an error: muted cues, a volume of zero, another
                // map on screen, or a package with no Sounds folder. It is retried next tick, which
                // is also how the loop arrives when a player un-mutes mid-ramp.
                if (loopSustainer == null) { return; }
                loopCueId = wanted;
            }

            loopSustainer.Maintain();
        }
    }
}
