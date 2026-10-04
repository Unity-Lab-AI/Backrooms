using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The scheduling surface: a standing order to call the crew home at a chosen point in the
    /// gate's own window.
    ///
    /// **Owner direction, verbatim:** *"Add schedule, warning, recall, evacuation, emergency
    /// close, lost-connection, failed return, and rescue workflows"*. Warning, recall, emergency
    /// close, lost-connection, failed return and rescue all shipped. **Schedule was the one left.**
    ///
    /// ## Why a schedule is allowed here when nothing else in this mod may have one
    ///
    /// `docs/CAMPAIGN_CHART.md` §1.1 is absolute and is enforced by
    /// `tools/check-campaign-absolutes.py`: *"A gate's connection has a duration. **Nothing else
    /// in this mod has a duration.**"* Owner's words: *"nothing ever ever have time restripctions
    /// but the gate"*.
    ///
    /// So this adds **no clock at all.** It reads `OpeningTicksRemaining` — the gate's existing
    /// window, which is itself the consequence of power, tech, maintenance and workforce — and it
    /// acts at a point on that window the player picked. Three things keep it on the right side
    /// of the rule:
    ///
    /// * **It is off by default.** A player who never opens the menu is never scheduled.
    /// * **It takes nothing away.** The action it fires is `Recall`, which orders the crew to walk
    ///   home. It cannot close the gate, cannot strand anybody, and cannot fail the trip.
    /// * **The thresholds are the warning thresholds**, not new ones. See
    ///   <see cref="RecallOptionTicks"/>: a player schedules the recall to the same moments the
    ///   gate already shouts at them about, so the schedule and the warnings can never disagree
    ///   about how much window is left.
    ///
    /// That last point is the design rather than a convenience. Inventing a fourth threshold would
    /// have meant two separate ideas of *running out of time* on one gate.
    ///
    /// ## What it is actually for
    ///
    /// The stranded-crew guarantee is the most expensive thing in this package to get wrong, and
    /// the way a player loses a crew is not misunderstanding the rules — it is being busy
    /// somewhere else on the map when the five-minute warning scrolls past. A warning needs a
    /// player watching. A standing order does not.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>
        /// The points in the window a recall may be scheduled to, longest first, with zero
        /// meaning no standing order.
        ///
        /// **Exactly the thresholds `SendOpeningWindowWarnings` already uses**, and deliberately
        /// not a free number the player types. A schedule that could sit between two warnings
        /// would be a second opinion about when a window is nearly over.
        /// </summary>
        internal static readonly int[] RecallOptionTicks = { 0, 417, 208, 83 };

        /// <summary>
        /// Saved. Ticks of window remaining at which the crew is called home, or 0 for no
        /// standing order.
        ///
        /// Named for what it does. Anything matching *expiry*, *deadline* or *timeout* is refused
        /// outright by `check-campaign-absolutes.py`, and rightly — but the name matters beyond
        /// the checker, because this genuinely is not a deadline: nothing is lost when it fires.
        /// </summary>
        private int standingRecallTicks;

        /// <summary>
        /// Saved. Whether this opening's standing recall has already been issued, so it fires
        /// once rather than every tick below the threshold.
        ///
        /// Cleared by <see cref="ResetStandingRecall"/> alongside the window warnings, because an
        /// order issued in a previous opening says nothing about this one.
        /// </summary>
        private bool standingRecallIssued;

        /// <summary>The scheduled point, or 0 when the player has set no standing order.</summary>
        public int StandingRecallTicks { get { return standingRecallTicks; } }

        internal void ExposeStandingRecall()
        {
            Scribe_Values.Look(ref standingRecallTicks, "rr_gateStandingRecallTicks", 0);
            Scribe_Values.Look(ref standingRecallIssued, "rr_gateStandingRecallIssued", false);
        }

        /// <summary>Clears this opening's issued flag. Called with the window warnings.</summary>
        private void ResetStandingRecall() { standingRecallIssued = false; }

        /// <summary>
        /// Sets or clears the standing order.
        ///
        /// Refuses a value that is not one of <see cref="RecallOptionTicks"/>, so a save edit or a
        /// future caller cannot introduce the fourth threshold this deliberately does not have.
        /// </summary>
        public void SetStandingRecall(int ticks)
        {
            for (int index = 0; index < RecallOptionTicks.Length; index++)
            {
                if (RecallOptionTicks[index] != ticks) { continue; }
                standingRecallTicks = ticks;
                return;
            }
        }

        /// <summary>
        /// Issues the scheduled recall when the window reaches the chosen point.
        ///
        /// **Called from the same place as the window warnings**, so the order and the shout that
        /// accompanies it are decided by one pass over one number. Doing it anywhere else would
        /// let the two drift apart by a tick and read as a bug.
        ///
        /// Every refusal is silent here on purpose, and it is the one place in this file where
        /// that is right: a standing order that cannot act because there is no crew out, or
        /// because they are already walking home, has nothing to tell anybody. The recall's own
        /// refusals are keyed and surfaced where a player asked for one by hand.
        /// </summary>
        private void IssueStandingRecall()
        {
            if (standingRecallTicks <= 0 || standingRecallIssued) { return; }
            if (openingTicksRemaining > standingRecallTicks) { return; }
            // Marked before the attempt, not after. A recall that refuses because the crew is
            // already returning must not be retried every tick for the rest of the window.
            standingRecallIssued = true;

            RimroomsExpeditionComponent trips = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsExpeditionComponent>();
            if (trips == null) { return; }
            CompanyActionResult result = trips.Recall();
            if (!result.Success) { return; }

            Messages.Message("RR_Gate_StandingRecallIssued".Translate(), parent,
                MessageTypeDefOf.ThreatSmall, false);
            Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
            RecordGateActivity("RR_Gate_StandingRecallIssued", CurrentOpeningId);
        }

        /// <summary>
        /// The player's way to set it: one gizmo, a float menu of the three window points and
        /// off.
        ///
        /// On the gate rather than in Operations, because the owner's standing direction is that
        /// *"everything that the machine needs to start up should be able to do in the worlkd
        /// from the devices themselfes"*, and because a standing order about this gate's window
        /// belongs on this gate.
        /// </summary>
        internal IEnumerable<Gizmo> StandingRecallGizmos()
        {
            if (parent == null || !parent.Spawned || parent.Faction != Faction.OfPlayer)
            { yield break; }
            if (!IsDesignated) { yield break; }

            var command = new Command_Action
            {
                defaultLabel = "RR_Gate_StandingRecallLabel".Translate(
                    StandingRecallDescription(standingRecallTicks)),
                defaultDesc = "RR_Gate_StandingRecallDesc".Translate(),
                icon = TexCommand.ForbidOff,
                action = delegate
                {
                    var options = new List<FloatMenuOption>();
                    for (int index = 0; index < RecallOptionTicks.Length; index++)
                    {
                        int ticks = RecallOptionTicks[index];
                        options.Add(new FloatMenuOption(
                            StandingRecallDescription(ticks),
                            delegate { SetStandingRecall(ticks); }));
                    }
                    Find.WindowStack.Add(new FloatMenu(options));
                },
            };
            yield return command;
        }

        /// <summary>What a scheduled point is called on screen.</summary>
        internal static string StandingRecallDescription(int ticks)
        {
            if (ticks <= 0) { return "RR_Gate_StandingRecallOff".Translate().ToString(); }
            return "RR_Gate_StandingRecallAt".Translate(ticks.ToStringTicksToPeriod()).ToString();
        }

        /// <summary>
        /// The standing order, read off the gate.
        ///
        /// Printed only when one is set. A gate with no standing order says nothing about having
        /// none, because a line reading *no standing recall* on every gate in the colony is the
        /// text wall the owner asked to be rid of.
        /// </summary>
        internal string StandingRecallReadout()
        {
            return standingRecallTicks <= 0
                ? null
                : "RR_Gate_StandingRecallInspect".Translate(
                    standingRecallTicks.ToStringTicksToPeriod()).ToString();
        }
    }
}
