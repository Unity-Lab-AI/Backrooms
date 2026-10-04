using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Portals;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The eleven start-up checks, in the order they have to be satisfied — readable from
    /// anywhere, not just from the Operations window.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"and when u set a door to be a gatew  that gate should tell you next step in the game
    /// world not just in the operations tab and machine tab"*
    ///
    /// and the clause it belongs to: *"and everything that the machine needs to start up should
    /// be able to do in the worlkd from the devices themselfes with pawns controls and actrions
    /// not just in the opetaions tab"*.
    ///
    /// ## Why this moved out of the UI
    ///
    /// The list lived in `UI/OperationsGateSteps.cs` as a private method on
    /// `MainTabWindow_Operations`, so **the only place in the game that could answer *"what do I
    /// do next"* was the window the owner was complaining about.** Answering it on the door as
    /// well had exactly two options: call into the window, or write the eleven conditions a
    /// second time. The second is the defect this project keeps meeting — *"two derivations of
    /// one rule"* — and it is the specific defect that produced
    /// `RR_Gate_CalibrationUnavailable` reading *"The gate is not ready for calibration"* for
    /// eight different reasons including *already calibrated*.
    ///
    /// So the list is here, in the gate's own namespace, and both surfaces ask it. The window
    /// draws every row; the door's inspect card names the first unfinished one.
    ///
    /// ## It still decides nothing
    ///
    /// `CompRimroomsGate.BeginSpinUp` remains the only authority on whether a gate opens. Each
    /// step corresponds to exactly one condition those methods already check, and where the two
    /// could drift the step **asks the gate** rather than recomputing. Nothing here is tracked,
    /// nagged or persisted: it is a readout of live state, so a player who already knows simply
    /// sees eleven ticks.
    /// </summary>
    internal static class GateStartupChecklist
    {
        /// <summary>One numbered check: what it is, whether it is done, and how to finish it.</summary>
        internal struct GateStep
        {
            public int Number;
            public string Label;
            public bool Done;
            public string How;
        }

        /// <summary>How many of the eleven are satisfied.</summary>
        internal static int DoneCount(List<GateStep> steps)
        {
            return steps == null ? 0 : steps.Count(step => step.Done);
        }

        /// <summary>
        /// The first unfinished check, or a step with <c>Number == 0</c> when all eleven are done.
        ///
        /// Zero rather than a nullable, because every caller has to draw something in the
        /// all-done case and an `if (next.HasValue)` at each one is a second place to get the
        /// same question wrong.
        /// </summary>
        internal static GateStep NextIncomplete(List<GateStep> steps)
        {
            return steps == null ? default(GateStep) : steps.FirstOrDefault(step => !step.Done);
        }

        /// <summary>
        /// The eleven checks for one gate.
        ///
        /// **The order is not cosmetic.** Gate control on the machining table comes before the
        /// assembly because `RecipeWorker_RimroomsGateAssembly.AvailableOnNow` withdraws the
        /// recipe from a bench in normal operation, and gate control on the console comes before
        /// staffing because `BeginSpinUp` refuses while either component is doing its day job.
        /// A player following this list top to bottom never meets a step that cannot be done yet.
        ///
        /// A null gate is the pre-selection state and yields eleven unfinished steps, which is
        /// what the Operations window needs in order to say *"pick a door"* as step one.
        /// </summary>
        internal static List<GateStep> Steps(CompRimroomsGate gate)
        {
            var steps = new List<GateStep>();
            bool haveGate = gate != null;
            steps.Add(new GateStep
            {
                Number = 1,
                Label = "RR_Steps_1Label".Translate(),
                Done = haveGate,
                How = "RR_Steps_1How".Translate(),
            });

            CompRimroomsGateConsole station = haveGate && gate.LinkedConsole != null
                ? gate.LinkedConsole.TryGetComp<CompRimroomsGateConsole>() : null;
            CompRimroomsGateConsole workshop = haveGate && gate.AssemblyBench != null
                ? gate.AssemblyBench.TryGetComp<CompRimroomsGateConsole>() : null;
            bool bound = haveGate && gate.LinkedConsole != null && gate.LinkedBattery != null &&
                gate.AssemblyBench != null;
            steps.Add(new GateStep
            {
                Number = 2,
                Label = "RR_Steps_2Label".Translate(),
                Done = bound,
                How = "RR_Steps_2How".Translate(),
            });

            steps.Add(new GateStep
            {
                Number = 3,
                Label = "RR_Steps_3Label".Translate(),
                Done = haveGate && gate.IsDesignated,
                How = "RR_Steps_3How".Translate(),
            });

            steps.Add(new GateStep
            {
                Number = 4,
                Label = "RR_Steps_4Label".Translate(),
                Done = workshop != null && workshop.IsGateControl,
                How = "RR_Steps_4How".Translate(haveGate && gate.AssemblyBench != null
                    ? gate.AssemblyBench.LabelCap.ToString()
                    : "RR_Steps_TheTable".Translate().ToString()),
            });

            steps.Add(new GateStep
            {
                Number = 5,
                Label = "RR_Steps_5Label".Translate(),
                Done = haveGate && gate.AssemblyComplete,
                How = "RR_Steps_5How".Translate(),
            });

            steps.Add(new GateStep
            {
                Number = 6,
                Label = "RR_Steps_6Label".Translate(),
                Done = haveGate && gate.AssignedOperator != null,
                How = "RR_Steps_6How".Translate(),
            });

            steps.Add(new GateStep
            {
                Number = 7,
                Label = "RR_Steps_7Label".Translate(),
                Done = haveGate && gate.Calibrated,
                How = "RR_Steps_7How".Translate(),
            });

            steps.Add(new GateStep
            {
                Number = 8,
                Label = "RR_Steps_8Label".Translate(),
                Done = station != null && station.IsGateControl,
                How = "RR_Steps_8How".Translate(haveGate && gate.LinkedConsole != null
                    ? gate.LinkedConsole.LabelCap.ToString()
                    : "RR_Steps_TheConsole".Translate().ToString()),
            });

            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            bool remembered = haveGate && network != null && !network.HasStateFault &&
                network.Connections.Any(edge => edge != null && edge.Kind == PortalConnectionKind.Laboratory &&
                    edge.First != null && edge.First.Anchor == gate.parent);
            steps.Add(new GateStep
            {
                Number = 9,
                Label = "RR_Steps_9Label".Translate(),
                Done = remembered,
                How = "RR_Steps_9How".Translate(),
            });

            steps.Add(new GateStep
            {
                Number = 10,
                Label = "RR_Steps_10Label".Translate(),
                Done = haveGate && gate.IsOperatorOnStation,
                How = "RR_Steps_10How".Translate(),
            });

            // **A RAMP IS NOT AN OPEN CONNECTION, and conflating them was a defect.** This read
            // `IsOpening || IsSpinningUp`, so the moment a player pressed "open a session" every
            // one of the eleven checks showed complete -- and then `PortalTravelService` refused
            // the crossing with *"the laboratory connection for that address is not open"*,
            // because it is not. Owner: *"every check mark is complete but it still says: the lab
            // connection to that address is not connected.. but the checked staps says
            // otherwise"*. **They were reading a tick that was wrong.**
            //
            // `IsSpinningUp` is explicitly `!IsOpening`, so the ramp is a distinct state and the
            // step says which one it is in, with the live percentage the portal panel already
            // shows. Opening is work and it **bleeds back down** if the operator leaves, which is
            // the one thing a player watching a progress bar needs told.
            bool ramping = haveGate && gate.IsSpinningUp;
            steps.Add(new GateStep
            {
                Number = 11,
                Label = "RR_Steps_11Label".Translate(),
                Done = haveGate && gate.IsOpening,
                How = ramping
                    ? "RR_Steps_11HowRamping".Translate(
                        (gate.SpinUpProgress * 100f).ToString("F0")).ToString()
                    : "RR_Steps_11How".Translate().ToString(),
            });
            return steps;
        }
    }
}
