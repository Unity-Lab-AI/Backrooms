using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The two research routes, kept in step so neither can lie about the other.
    ///
    /// ## Why this exists
    ///
    /// **Owner, 2026-10-06, in capitals:** *"AND A MAJOR ISSUE: I DONT SEE ANY RESEARCH FOR THE GATE
    /// SYSTEMS AND EVERYTHING THIS MOD HAS!!!!!"*
    ///
    /// They were right to look in the Research tab, and nothing was broken: the branch had
    /// initialised cleanly and all 38 projects had records. **They were simply in a place nobody
    /// looks** -- a `RimroomsProjectDef` in an Operations section, invisible to the vanilla tab and
    /// therefore invisible to ResearchTree (register row 191) and Research Whatever (row 279), both
    /// of which the owner runs.
    ///
    /// Asked how to resolve it, the owner chose **two genuine routes, either works**.
    ///
    /// ## What each route costs, and why that is not symmetrical
    ///
    /// * **Operations:** commit an **insight** -- paid for out of evidence recovered from a
    ///   coordinate -- then work it at a bench. The route the mod is about.
    /// * **The Research tab:** bench work alone, at a price set against vanilla's own distribution.
    ///
    /// The second buys you out of the evidence requirement, so it costs more bench time. **It does
    /// not bypass the capability**: whichever route finishes, the capability is granted once and the
    /// company record is the thing that holds it.
    ///
    /// ## Both directions, and the reason both are needed
    ///
    /// A player who finishes a mirror in the Research tab must get the capability, or the tab is a
    /// lie. A player who finishes the company project in Operations must see the mirror marked done,
    /// or the tab is a *different* lie -- it would offer research they have already completed, and
    /// ResearchTree would draw an unfinished node for finished work.
    ///
    /// So the sync runs **both ways**, and it is idempotent in both: the test is always *are these
    /// two disagreeing*, never *has something just happened*. That matters because this runs on a
    /// cadence rather than on an event, and an event-shaped sync would miss a project finished by a
    /// mod, by a dev command, or by a quest reward.
    ///
    /// ## Never the other way round for an UNFINISH
    ///
    /// Nothing here ever un-completes anything. If a save somehow holds a finished mirror and an
    /// unfinished company project, the project is completed -- the generous direction. **Taking a
    /// capability back from a player who has it is a worse outcome than granting one twice**, and
    /// granting twice is already impossible because the record is a boolean.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// The prefix the generated mirror uses. One copy, here, because
        /// `.local/qa/generate-research-mirror.py` writes the other and a second literal would be
        /// the drift the pairing checker exists to refuse.
        /// </summary>
        public const string ResearchMirrorPrefix = "RR_Mirror_";

        /// <summary>
        /// Ticks between sync passes. Four seconds of game time: a player who finishes a project
        /// wants to see it reflected, and nobody can perceive four seconds against a research
        /// project that took hours.
        /// </summary>
        private const int MirrorInterval = 240;

        /// <summary>The mirror for one company project, or null if the def is not loaded.</summary>
        public static ResearchProjectDef MirrorFor(string companyDefName)
        {
            return string.IsNullOrEmpty(companyDefName)
                ? null
                : DefDatabase<ResearchProjectDef>.GetNamedSilentFail(
                    ResearchMirrorPrefix + companyDefName);
        }

        /// <summary>
        /// Bring the two routes into agreement, in both directions, idempotently.
        ///
        /// Called from the component's own tick on <see cref="MirrorInterval"/>. Returns the number
        /// of records it changed, which is what the proof reads rather than trusting a log line.
        /// </summary>
        internal int SyncResearchMirror()
        {
            if (!CanOperate) { return 0; }
            ResearchManager manager = Find.ResearchManager;
            if (manager == null) { return 0; }
            int changed = 0;
            IReadOnlyList<ProjectRecord> records = Projects;
            for (int index = 0; index < records.Count; index++)
            {
                ProjectRecord record = records[index];
                if (record == null) { continue; }
                ResearchProjectDef mirror = MirrorFor(record.ResearchDefName);
                if (mirror == null) { continue; }
                bool mirrorDone = mirror.IsFinished;
                if (record.Completed && !mirrorDone)
                {
                    // Operations finished it. Mark the tab so it does not offer work already done.
                    manager.FinishProject(mirror, doCompletionDialog: false, null, true);
                    changed++;
                }
                else if (mirrorDone && !record.Completed)
                {
                    // The Research tab finished it. The capability lives on the company record, so
                    // the record is what has to move -- and `RebuildCapabilities` is what makes a
                    // capability real, exactly as the Operations route does it.
                    CompleteProjectFromResearch(record);
                    changed++;
                }
            }
            if (changed > 0) { RebuildCapabilities(); }
            return changed;
        }

        /// <summary>
        /// Complete a company project because its mirror was researched.
        ///
        /// **Deliberately not a second completion path.** It sets the same two fields the Operations
        /// route sets and then defers to the same `RebuildCapabilities`, so there is one definition
        /// of *what a finished project means* and this is a different way of arriving at it.
        ///
        /// `insightCommitted` is set true as well, because the record's own integrity check requires
        /// a committed insight behind a completed project -- the same rule that once set a state
        /// fault on turn one and made every button in the mod refuse. The receipt records that the
        /// research tab paid for it rather than evidence.
        /// </summary>
        private void CompleteProjectFromResearch(ProjectRecord record)
        {
            record.MarkResearchedExternally(record.Id + ":research-tab");
            Investigation.RimroomsProjectDef definition =
                DefDatabase<Investigation.RimroomsProjectDef>.GetNamedSilentFail(
                    record.ResearchDefName);
            string label = definition == null ? record.ResearchDefName
                : definition.LabelCap.ToString();
            RecordEvent("RR_Event_ProjectCompleted", record.Id, label);
        }
    }
}
