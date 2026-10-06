using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What the branch must already hold before a write-up can be written.
    ///
    /// **An enum, where the kinds themselves are defs, and the asymmetry is deliberate.** The owner
    /// said the list of kinds is open -- *"each step has a lab nots, research write up,
    /// investigation, analysis, ... what ever the task requires"* -- and the ellipsis is why
    /// <see cref="RimroomsWriteUpDef"/> is a `Def`: a new kind is XML.
    ///
    /// A **precondition** is not open in the same way, because each one is a question asked of real
    /// saved state and that question is code. So a new kind may reuse any precondition here for
    /// free; a genuinely new *condition* needs a line of code, and saying so is better than an
    /// extension point that silently answers `true`.
    /// </summary>
    public enum WriteUpPrecondition
    {
        /// <summary>Nothing. The paperwork can be written the moment the quest is accepted.</summary>
        None = 0,

        /// <summary>A gate step has been performed and recorded. The owner's *"lab nots"*.</summary>
        GateStepRecorded = 1,

        /// <summary>A company project has been completed.</summary>
        ProjectCompleted = 2,

        /// <summary>An evidence record has reached <c>Secured</c> custody on an archive shelf.</summary>
        EvidenceSecured = 3,

        /// <summary>An evidence record has been analysed.</summary>
        EvidenceAnalysed = 4,

        /// <summary>A coordinate's authored rooms have all been entered. Exploration's own entry.</summary>
        SurveyComplete = 5,
    }

    /// <summary>
    /// One kind of paperwork the company wants written up at a records desk.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"after doing all the gate steps, each step has a
    /// lab nots, research write up, investigation, analysis, ... what ever the task requires and
    /// what the company wants as far as data or anaylisiis or retreval and such"*.
    ///
    /// ## Why this is a Def and not an enum
    ///
    /// **The ellipsis in the owner's sentence is the specification.** Four kinds are named and the
    /// list is explicitly open, so a fifth must not require a recompile. That is the same reason
    /// `RimroomsGateEquipmentDef`, `RimroomsInhabitantDef` and `RimroomsAnomalyEventDef` are defs:
    /// this mod already treats *a named kind of thing the player meets* as data.
    ///
    /// ## And a kind is declared on the request, never inferred from its name
    ///
    /// A quest called *"Analysis of coordinate 4-A"* must not get an analysis write-up because
    /// somebody matched a word in its label. `RimroomsRequestDef.writeUps` lists the defNames, so
    /// the requirement is readable in XML, countable by a checker, and identical for every branch.
    /// </summary>
    public sealed class RimroomsWriteUpDef : Def
    {
        /// <summary>What the branch must already hold. See <see cref="WriteUpPrecondition"/>.</summary>
        public WriteUpPrecondition precondition = WriteUpPrecondition.None;

        /// <summary>
        /// Bench work one of these costs.
        ///
        /// **Real work over time, because the owner said these are jobs:** *"these tasks are auto in
        /// the pawns work jobs"*. A write-up that completed instantly would be a button wearing a
        /// pawn's clothes.
        /// </summary>
        public float workRequired = 900f;

        /// <summary>
        /// The order these are offered in, so a branch works through a quest's paperwork in a
        /// stated sequence rather than whichever the def database happened to list first.
        /// </summary>
        public int displayOrder;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(label))
            { yield return "A write-up kind must have a label; a pawn's job and the ledger both show it."; }
            if (string.IsNullOrEmpty(description))
            { yield return "A write-up kind must have a description; it is what tells a player what the company wants."; }
            // Mirrors `CompProperties_RouteEvidence.ConfigErrors`, which refuses a non-finite
            // analysis cost for the same reason: a NaN work requirement is a job that never ends.
            if (workRequired <= 0f || float.IsNaN(workRequired) || float.IsInfinity(workRequired))
            { yield return "workRequired must be finite and positive; anything else is a job that cannot finish."; }
        }

        /// <summary>
        /// Every kind, in declared order then ordinally.
        ///
        /// Sorted rather than taken in database order, because this decides what a pawn writes
        /// first and what the ledger lists first, and two players must see the same sequence.
        /// </summary>
        public static List<RimroomsWriteUpDef> AllInOrder()
        {
            var all = new List<RimroomsWriteUpDef>(DefDatabase<RimroomsWriteUpDef>.AllDefsListForReading);
            all.Sort(delegate (RimroomsWriteUpDef left, RimroomsWriteUpDef right)
            {
                int byOrder = left.displayOrder.CompareTo(right.displayOrder);
                return byOrder != 0 ? byOrder
                    : string.Compare(left.defName, right.defName, System.StringComparison.Ordinal);
            });
            return all;
        }
    }
}
