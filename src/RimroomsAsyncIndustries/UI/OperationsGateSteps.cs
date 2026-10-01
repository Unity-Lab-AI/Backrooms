using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// The start-up connection checks, numbered, with what to do for each one that is not done.
    ///
    /// **Owner direction, 2026-10-01, verbatim:** *"the whole machine  tab needs to be numbered
    /// and everything step 1 step 2... ect ect so fucking simple a 6 yr old chimp can do it"*,
    /// *"it needs to have checks showing the start up connection checks are complete or unfinished
    /// yet"*, *"and it need to explain conciselky how, becuse this is fucking confusing"*.
    ///
    /// ## Why this had to exist
    ///
    /// Opening a laboratory gate has **eleven** prerequisites spread across a door, three bound
    /// buildings, a worktable bill, a job, and two separate panels in this window. Every gate
    /// method checked its own set and reported **one** refusal, in prose that named none of them
    /// -- `RR_Gate_CalibrationUnavailable` read *"The gate is not ready for calibration"* for all
    /// eight of its conditions **including the one that means it is already calibrated**.
    ///
    /// The owner's report: *"ive done like 50 things in a row and its still not opening"*. Their
    /// save said the gate was assembled, calibrated, crewed and un-tripped, and that the machining
    /// table was in gate control while the communications console on the same gate was not. **One
    /// switch, out of eleven steps, and nothing on screen could say so.**
    ///
    /// ## What it does, and what it deliberately does not
    ///
    /// Every line is read from live state and **nothing here decides anything.** The authority on
    /// whether a gate opens is still `CompRimroomsGate.BeginSpinUp`; this reports the same facts
    /// in the order a player has to satisfy them. Two derivations of one rule is the defect this
    /// project keeps meeting, so each step corresponds to exactly one condition those methods
    /// already check, and when the two could disagree the step asks the gate rather than
    /// recomputing.
    ///
    /// The *how* is one sentence and names the thing to click. Not a tutorial, and nothing is
    /// tracked to completion or nagged about -- it is a readout, so a player who already knows
    /// simply sees eleven ticks.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        /// <summary>One numbered check: what it is, whether it is done, and how to finish it.</summary>
        private struct GateStep
        {
            public int Number;
            public string Label;
            public bool Done;
            public string How;
        }

        /// <summary>
        /// Draws the numbered start-up checks for the gate this tab is pointed at.
        ///
        /// Drawn first, above the binding and network panels, because it is the thing that says
        /// which of those two panels to go and use.
        /// </summary>
        private void DrawGateStartupChecks(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Steps_Heading".Translate());
            CompRimroomsGate gate = CurrentGate(campaign);
            List<GateStep> steps = GateStartupSteps(campaign, gate);
            int done = steps.Count(step => step.Done);
            listing.Label("RR_Steps_Progress".Translate(done.ToString(), steps.Count.ToString()));

            // The first unfinished step. Named separately above the list, because a list of
            // eleven lines is still a list to read and the answer to *"what do i do"* is one of
            // them.
            GateStep next = steps.FirstOrDefault(step => !step.Done);
            if (next.Number != 0)
            { listing.Label("RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)); }
            else
            { listing.Label("RR_Steps_AllDone".Translate()); }

            for (int index = 0; index < steps.Count; index++)
            {
                GateStep step = steps[index];
                // Done steps are one line. An unfinished one carries its instruction, so the
                // list does not become a wall of advice about things already handled.
                listing.Label(step.Done
                    ? "RR_Steps_LineDone".Translate(step.Number.ToString(), step.Label).ToString()
                    : "RR_Steps_LineToDo".Translate(step.Number.ToString(), step.Label, step.How).ToString());
            }

            // **AND WHAT TO DO ONCE IT IS OPEN**, because the eleven checks end at a live
            // connection and the player's actual goal is on the far side of it. Nothing in the
            // list said *now send somebody*, which is why a completed list still left the owner
            // asking what they were missing.
            if (gate != null && gate.IsOpening)
            { listing.Label("RR_Steps_NowCross".Translate()); }

            // A fault is not a step: it is something that was done and has since gone wrong, and
            // it blocks every remaining one. Said after the list so it reads as a problem rather
            // than as the next thing to do.
            if (gate != null && gate.NativeBindingFailureKey != null)
            { listing.Label("RR_Steps_Fault".Translate(gate.NativeBindingFailureKey.Translate())); }
            listing.GapLine();
        }

        /// <summary>
        /// The eleven checks, in the order they have to be satisfied.
        ///
        /// **The order is not cosmetic.** Gate control on the machining table comes before the
        /// assembly because `RecipeWorker_RimroomsGateAssembly.AvailableOnNow` withdraws the
        /// recipe from a bench in normal operation, and gate control on the console comes before
        /// staffing because `BeginSpinUp` refuses while either component is doing its day job.
        /// A player following this list top to bottom never meets a step that cannot be done yet.
        /// </summary>
        private List<GateStep> GateStartupSteps(RimroomsCampaignComponent campaign, CompRimroomsGate gate)
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
