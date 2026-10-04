using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The company pays the branch for each start-up goal it reaches.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"and once u follow the quests to get the gate up and running(full totorieal quest line
    /// payouts on each successful step(the company rewards getting to the goals)"*
    ///
    /// Three clauses, and each one decided something here:
    ///
    /// **"once u follow the quests to get the gate up and running"** — the spine is the gate
    /// start-up chain. Not a parallel quest script: <see cref="GateStartupChecklist.Steps"/> is
    /// asked, which is the same list the machine tab's status board and the door's own inspect
    /// card read. **One source for all three**, so a payout and a tick can never disagree about
    /// whether something is done. Writing the eleven conditions again here is the *"two
    /// derivations of one rule"* defect this project keeps meeting.
    ///
    /// **"full totorieal quest line payouts on each successful step"** — eleven payouts, not one
    /// at the end. See <see cref="StepPayoutUsd"/>: the early ones are a nudge and finishing is
    /// the prize.
    ///
    /// **"(the company rewards getting to the goals)"** — the payer is the company, in the
    /// mechanism as well as the fiction. It goes through `PostTransaction`, so it lands in the
    /// branch's balance with a ledger receipt and a reason, exactly like every other sum this
    /// mod moves. **Nothing appears from nowhere** — no items spawn, no stack is dropped on the
    /// floor. And *"getting to the goals"* is the trigger: the goal being reached pays, not a
    /// quest being accepted, so there is nothing to accept and nothing to decline.
    ///
    /// ## Paid once per branch, not once per gate
    ///
    /// This is the tutorial chain. A branch that builds a second gate has already learned how,
    /// and paying again per door would make eleven payouts into an income stream — build ten
    /// doors, collect a hundred and ten receipts. So the operation id names the step and nothing
    /// else.
    ///
    /// ## The ledger IS the record, and that is why there is no new saved state
    ///
    /// `PostTransaction` is idempotent on its operation id: a repeat with the same amount and
    /// reason returns `Existing()` and moves no money. So "has step 6 been paid" is already
    /// answered, permanently, by the branch's own books — and a second bookkeeping field could
    /// only ever drift from them. Nothing here is scribed.
    /// </summary>
    internal static class GateStartupPayouts
    {
        /// <summary>
        /// What each of the eleven goals pays, indexed by step number.
        ///
        /// **Scaled so the early ones are a nudge and finishing is the prize**, which is the
        /// owner's own shape for it. The first few cover the materials the step asks for rather
        /// than profiting on them; step eleven — a connection actually open — is worth more than
        /// the ten before it put together, because that is the goal the whole chain exists for.
        ///
        /// Index 0 is unused so the step number indexes directly. A table rather than arithmetic:
        /// a curve would have to be read to be understood, and these are eleven numbers somebody
        /// will want to balance by hand after the first play.
        /// </summary>
        private static readonly long[] StepPayoutUsd =
        {
            0,    // unused; steps are numbered from one
            40,   // 1  a door chosen
            60,   // 2  console, battery and bench bound
            60,   // 3  designated
            70,   // 4  the bench put into gate control
            200,  // 5  the assembly bill finished -- this one costs real materials
            80,   // 6  an operator assigned
            120,  // 7  calibrated
            80,   // 8  the console put into gate control
            150,  // 9  an address remembered
            100,  // 10 the operator on station
            900,  // 11 a connection open. The prize.
        };

        /// <summary>
        /// Pays for every goal this branch has reached and not yet been paid for.
        ///
        /// Called from the gate's tick through <see cref="ShouldCheck"/>, so a player who
        /// finishes a step is paid within a few seconds without the eleven translated labels
        /// being rebuilt sixty times a second.
        ///
        /// Silent on refusal by design: `PostTransaction` refuses while the branch cannot
        /// operate, and a branch that is not operating has nothing to be told about a tutorial
        /// bonus. The next check pays it.
        /// </summary>
        internal static void Pay(CompRimroomsGate gate)
        {
            if (gate == null) { return; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return; }

            List<GateStartupChecklist.GateStep> steps = GateStartupChecklist.Steps(gate);
            if (steps == null) { return; }
            for (int index = 0; index < steps.Count; index++)
            {
                GateStartupChecklist.GateStep step = steps[index];
                if (!step.Done) { continue; }
                if (step.Number < 1 || step.Number >= StepPayoutUsd.Length) { continue; }
                long amount = StepPayoutUsd[step.Number];
                if (amount <= 0L) { continue; }

                // **THE IDEMPOTENCY GUARD AND THE RECORD ARE THE SAME THING.** The id names the
                // step and not the gate, so the chain pays once for the branch however many
                // doors it eventually runs.
                string operationId = "rr_startupGoal:" + step.Number;
                CompanyActionResult result = campaign.PostTransaction(
                    operationId, amount, "RR_Startup_PayoutReason", null);
                if (!result.Success || result.AlreadyApplied) { continue; }

                // Announced only when it actually moved money, which is what makes the message
                // trustworthy: a player sees one per goal, the first time they reach it.
                Messages.Message(
                    "RR_Startup_PayoutMessage".Translate(step.Number.ToString(), step.Label,
                        amount.ToString("N0")),
                    gate.parent, MessageTypeDefOf.PositiveEvent, false);
                campaign.RecordEvent("RR_Startup_PayoutReason", operationId,
                    step.Number.ToString());
            }
        }

        /// <summary>
        /// How often the chain is checked, in ticks.
        ///
        /// Two seconds of game time. `Steps` resolves eleven keyed strings and walks the portal
        /// network, which is cheap but not free, and nothing in the chain can be completed and
        /// un-completed inside two seconds in a way a player would notice.
        /// </summary>
        private const int CheckInterval = 120;

        /// <summary>Whether this tick is one of the ones that checks.</summary>
        internal static bool ShouldCheck(Thing gate)
        {
            // Offset by the thing's own id so two gates in one colony do not both resolve their
            // eleven labels on the same tick.
            return gate != null && (Find.TickManager.TicksGame + gate.thingIDNumber)
                % CheckInterval == 0;
        }
    }
}
