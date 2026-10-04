using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using UnityEngine;
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
        /// <summary>Height of one status row, and the side of the light on it.</summary>
        private const float StatusRowHeight = 24f;
        private const float StatusLightSide = 12f;

        /// <summary>
        /// The two indicator colours, and **the only authored colour anywhere in this window.**
        ///
        /// Owner, 2026-10-04: *"shows the different systems with green and red lights of whether
        /// complete/active"*. `check-display-style.py` otherwise refuses an authored colour in a
        /// readout file, and its reason is right: this package authors no palette so the player's
        /// own contrast and colourblind settings decide everything they read. **An indicator is
        /// not text**, the owner asked for these two by name, and the rule permits them here
        /// specifically — on the condition that `Widgets.CheckboxDraw` sits beside them, so the
        /// state is never carried by hue alone.
        ///
        /// Muted rather than saturated: a status board of twelve full-strength red squares reads
        /// as an alarm, and most of these are simply *not done yet*.
        /// </summary>
        private static readonly Color StatusLightComplete = new Color(0.35f, 0.72f, 0.38f);
        private static readonly Color StatusLightIncomplete = new Color(0.74f, 0.33f, 0.29f);

        /// <summary>
        /// A status board: one row per system, a light, and **one** next-step line for the lot.
        ///
        /// ## Owner direction, 2026-10-04, verbatim
        ///
        /// *"we need to make the whole operations panel thing alot less of a text wall its like a
        /// fucking novel when it doesnt need to be ... so that on the machine tab its shows the
        /// different systems with green and red lights of whether complete/active with a next step
        /// section showing what to do next  not every step having its own type up of whats next
        /// and things can be shortend and more concise and dirrect  with tools tips would less
        /// cluter it"*
        ///
        /// ## What this replaced, measured
        ///
        /// The same eleven checks, drawn as **fourteen wrapped paragraphs**: a heading, a progress
        /// line, a next-up line carrying its full instruction, then eleven lines each carrying its
        /// own instruction again, then two more. `check-operations-density.py` measured this pane
        /// at **356 words and zero things to click** — the worst ratio in the window and the
        /// literal shape of the owner's *"not every step having its own type up of whats next"*.
        ///
        /// **Nothing was shortened by dropping it.** Every instruction still exists, in full,
        /// where a player goes looking for it: the row's tooltip. The surface carries the light,
        /// the number and a few words; one next-step line at the top answers *"what do i do"*.
        ///
        /// ## The light is never the only channel
        ///
        /// Owner asked for *"green and red lights"* and gets them — and each one is paired with
        /// Core's own checkbox glyph, because colour alone fails
        /// `research/CONTENT_ACCESSIBILITY_BRIEF.md` and the player's colourblind setting cannot
        /// help a dot that means something by hue. `check-display-style.py` permits the two
        /// indicator colours in this file by name and **requires the glyph beside them**.
        /// </summary>
        private void DrawGateStartupChecks(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            CompRimroomsGate gate = CurrentGate(campaign);
            List<GateStartupChecklist.GateStep> steps = GateStartupChecklist.Steps(gate);
            int done = GateStartupChecklist.DoneCount(steps);
            listing.Label("RR_Steps_Progress".Translate(done.ToString(), steps.Count.ToString()));

            // **ONE next-step line for the whole board**, which is the owner's *"a next step
            // section showing what to do next"*. It carries the instruction because this is the
            // one place a player is told anything; the rows below do not repeat it.
            GateStartupChecklist.GateStep next = GateStartupChecklist.NextIncomplete(steps);
            if (next.Number != 0)
            { listing.Label("RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)); }
            else if (gate != null && gate.IsOpening)
            {
                // What to do once it is open, in the same slot rather than as an extra paragraph:
                // the eleven checks end at a live connection and the player's goal is past it.
                listing.Label("RR_Steps_NowCross".Translate());
            }
            else { listing.Label("RR_Steps_AllDone".Translate()); }

            for (int index = 0; index < steps.Count; index++)
            {
                DrawStatusRow(listing, steps[index]);
            }

            // A fault is not a step: it is something that was done and has since gone wrong, and
            // it blocks every remaining one. Said after the board so it reads as a problem rather
            // than as the next thing to do.
            if (gate != null && gate.NativeBindingFailureKey != null)
            { listing.Label("RR_Steps_Fault".Translate(gate.NativeBindingFailureKey.Translate())); }
            listing.GapLine();
        }

        /// <summary>
        /// One row: light, glyph, number, short label — and the full instruction on hover.
        ///
        /// The whole row is the hover target rather than the light, because a twelve-pixel square
        /// is not something a player finds by accident.
        /// </summary>
        private static void DrawStatusRow(Listing_Standard listing,
            GateStartupChecklist.GateStep step)
        {
            Rect row = listing.GetRect(StatusRowHeight);
            var light = new Rect(row.x + 2f,
                row.y + (StatusRowHeight - StatusLightSide) / 2f,
                StatusLightSide, StatusLightSide);
            Widgets.DrawBoxSolid(light, step.Done ? StatusLightComplete : StatusLightIncomplete);
            // Core's own checkbox glyph, so the state is readable without colour at all.
            Widgets.CheckboxDraw(light.xMax + 4f, row.y, step.Done, true, StatusRowHeight);
            var label = new Rect(light.xMax + 4f + StatusRowHeight + 4f, row.y,
                row.width - (light.xMax + 4f + StatusRowHeight + 4f - row.x), StatusRowHeight);
            Widgets.Label(label, "RR_Steps_Row".Translate(step.Number.ToString(), step.Label));
            if (Mouse.IsOver(row)) { Widgets.DrawHighlight(row); }
            // **THE INSTRUCTION IS NOT GONE, IT MOVED.** Owner: *"with tools tips would less
            // cluter it making them all concise and accurate"*. Shortening a readout by deleting
            // the condition it describes would be the other failure.
            TooltipHandler.TipRegion(row, step.Done
                ? "RR_Steps_TipDone".Translate(step.Label, step.How)
                : "RR_Steps_TipToDo".Translate(step.Label, step.How));
        }

    }
}
