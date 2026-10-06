using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The gate's assembly, split into sections so more than one person can build it.
    ///
    /// ## Owner direction, 2026-10-06, verbatim
    ///
    /// *"so that it isnt dependant at one pawn dying at the gate from starvvation trying to keep it
    /// open forever he can leave when another pawn hops on the other comms console toggled to gate
    /// contrtrols with say upto 4 of them available so pawns can do geate process better and
    /// faster"*, and the part this file is: *"and same with the coms and machine benches"*.
    ///
    /// Asked how to make a second bench mean something, the owner chose **split the gate's
    /// component count across the linked benches**, over *any linked bench satisfies the bill* and
    /// over leaving it documented.
    ///
    /// ## What was actually wrong, which is not what "link a second bench" suggests
    ///
    /// **A second machining table was already buildable and already linkable.** What it could not
    /// do is let a second pawn work the gate's assembly, because the assembly was **one bill of 100
    /// steel and 8 components on the one bound bench**, and one bill is one pawn however many
    /// benches a branch owns. So a link role on its own would have shipped *"a role that changes
    /// nothing"* -- the promise-that-changes-nothing four deleted research projects were deleted
    /// for.
    ///
    /// ## Four sections, and the total cost is unchanged
    ///
    /// | | Before | Now |
    /// |---|---|---|
    /// | Steel | 100 in one bill | 25 per section, four sections |
    /// | Components | 8 in one bill | 2 per section, four sections |
    /// | Work | 6000 in one bill | 1500 per section, four sections |
    ///
    /// **Nothing got cheaper and nothing got dearer.** What changed is that four people can be
    /// doing it at once on four benches, which is the owner's *"better and faster"*, and that a
    /// branch with one bench pays exactly what it always did in four trips instead of two. (100
    /// steel was never one carry: a colonist's load and steel's stack size both cap below that.)
    ///
    /// ## THE NAMED COST, AND IT IS ANSWERED BY NOT EXISTING
    ///
    /// The fork named the cost before the owner chose it: **a destroyed or unlinked bench must not
    /// leave an unfinishable remainder**, so the split *"has to be recomputed when the set of
    /// linked benches changes rather than fixed at the moment the bill is placed"*.
    ///
    /// **So a section is not assigned to a bench at all.** The count lives on the gate and any
    /// bound bench may install the next one. There is nothing to recompute, because there was never
    /// an allocation: destroy a bench mid-build and its unfinished sections are simply still
    /// outstanding, queueable anywhere, including on the primary bench alone. **An allocation that
    /// cannot be orphaned is better than one that is recomputed correctly**, because the recomputing
    /// is the part that would have had bugs.
    ///
    /// ## Why the shares are not a second recipe
    ///
    /// One `RecipeDef` with four iterations rather than four defs. A second def would be a second
    /// place stating the section cost, and the two would disagree the first time one was edited --
    /// the defect this project keeps meeting. The player's own bill carries the repeat count, which
    /// is theirs: queue four on one bench, or one on each of four.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>
        /// How many sections a gate's assembly is built in. **Four, matching the owner's four
        /// benches**, so a branch that built the fourth bench can have all four sections going at
        /// once and a branch with one bench does the same four in sequence.
        ///
        /// The per-section cost is declared in `RR_AssembleMachineGate` and this is the count the
        /// gate requires; multiply them to get the figures the wiki and step 5 state.
        /// </summary>
        public const int AssemblySharesRequired = 4;

        /// <summary>Sections installed so far. Never above <see cref="AssemblySharesRequired"/>.</summary>
        private int assemblyShares;

        internal void ExposeAssemblyShares()
        {
            Scribe_Values.Look(ref assemblyShares, "rr_gateAssemblyShares", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // A save written before the split has `assemblyComplete` true and no share count,
                // and a finished gate must read as finished rather than as nought of four.
                if (assemblyComplete) { assemblyShares = AssemblySharesRequired; }
                if (assemblyShares < 0) { assemblyShares = 0; }
                if (assemblyShares > AssemblySharesRequired) { assemblyShares = AssemblySharesRequired; }
            }
        }

        public int AssemblySharesDone { get { return assemblyShares; } }

        public int AssemblySharesRemaining
        { get { return assemblyComplete ? 0 : AssemblySharesRequired - assemblyShares; } }

        /// <summary>
        /// Every bench this gate's sections may be installed at.
        ///
        /// **The bound bench first**, because it is the one the branch designated and the one
        /// calibration, the step pane and the spin-up station already name. Then every thing linked
        /// in the `RR_Link_GateAssembly` role, which `maxLinked` caps at three -- so four benches in
        /// total, the owner's number, exactly as the relief stations work for consoles.
        ///
        /// An inactive link is excluded through <see cref="IsEquipmentLinkActive"/>: an unpowered
        /// bench is not a bench. Same answer Core gives for an unpowered multi-analyzer, and the
        /// same rule <see cref="BoundConsoles"/> applies one subsystem over.
        /// </summary>
        public IEnumerable<Thing> BoundAssemblyBenches
        {
            get
            {
                Thing primary = AssemblyBench;
                if (primary != null) { yield return primary; }
                RimroomsGateEquipmentDef role =
                    DefDatabase<RimroomsGateEquipmentDef>.GetNamedSilentFail("RR_Link_GateAssembly");
                // A missing role def means the package is incomplete, and the honest answer is the
                // bound bench alone rather than a throw while a bill is being offered.
                if (role == null) { yield break; }
                foreach (Thing linked in LinkedEquipment)
                {
                    if (linked == primary) { continue; }
                    if (RoleOf(linked) != role) { continue; }
                    if (!IsEquipmentLinkActive(linked)) { continue; }
                    yield return linked;
                }
            }
        }

        /// <summary>How many benches this gate's sections can be built at right now.</summary>
        public int BoundAssemblyBenchCount
        {
            get
            {
                int count = 0;
                foreach (Thing bench in BoundAssemblyBenches) { if (bench != null) { count++; } }
                return count;
            }
        }

        /// <summary>
        /// Whether this thing is one of the benches this gate's sections may be installed at.
        ///
        /// **The one question both the recipe's availability and its completion ask.** The recipe
        /// worker offers the bill where this is true and the gate accepts a finished section where
        /// this is true, so a bench cannot be offered work it is then refused credit for.
        /// </summary>
        public bool IsBoundAssemblyBench(Thing bench)
        {
            if (bench == null) { return false; }
            foreach (Thing candidate in BoundAssemblyBenches)
            {
                if (candidate == bench) { return true; }
            }
            return false;
        }

        /// <summary>
        /// The assembly line for the gate's inspect string, or null once it is built.
        ///
        /// Silent on a finished gate: a line reading "four of four" forever is the noise the
        /// servicing readout already refuses to be. The bench count rides along whenever there is
        /// more than one, because a player who built a second bench should be able to see that the
        /// gate knows about it.
        /// </summary>
        internal string AssemblyReadout()
        {
            if (!IsDesignated || assemblyComplete) { return null; }
            string text = "RR_Gate_AssemblySections".Translate(
                assemblyShares, AssemblySharesRequired).ToString();
            int benches = BoundAssemblyBenchCount;
            if (benches > 1)
            { text += " " + "RR_Gate_AssemblyBenches".Translate(benches).ToString(); }
            return text;
        }
    }
}
