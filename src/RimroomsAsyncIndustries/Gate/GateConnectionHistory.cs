using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;


namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// One coordinate a laboratory gate has dialled, and what the player has chosen to call it.
    /// </summary>
    /// <summary>
    /// Implements <see cref="IRenameable"/> so the player renames an address through **the
    /// game's own rename dialog** — the same one used for zones, caravans and storage groups,
    /// and already used by this mod for the company name. No bespoke dialog, no new UI to keep
    /// consistent, and the interaction is one the player already knows.
    /// </summary>
    public sealed class GateHistoryEntry : IExposable, IRenameable
    {
        internal string coordinateId;
        internal string label;
        internal int firstTick = -1;
        internal int lastTick = -1;
        internal int times;
        internal bool pinned;

        /// <summary>
        /// How many openings to this coordinate ended with the operation closed, and how many
        /// ended in an emergency.
        ///
        /// Row 725's reliability half. The entry recorded `times` and **nothing about how any
        /// of it went**, so the history could not answer the one question a player would ask of
        /// it: which of these addresses has been costing me return windows.
        ///
        /// Counted rather than rated. A stored percentage would be a second number that could
        /// disagree with the counts it came from; the rate is derived on read from these two.
        /// </summary>
        internal int completed;

        internal int emergencies;

        public string CoordinateId { get { return coordinateId; } }
        public string Label { get { return label; } }
        public int FirstTick { get { return firstTick; } }
        public int LastTick { get { return lastTick; } }
        public int Times { get { return times; } }
        public int Completed { get { return completed; } }
        public int Emergencies { get { return emergencies; } }

        /// <summary>
        /// The share of recorded outcomes that ended well, or **-1 when nothing has been
        /// recorded yet**.
        ///
        /// -1 rather than 0 or 1, because *no data* is not *perfect* and is not *hopeless*
        /// either, and a surface showing either would be lying about a coordinate nobody has
        /// come back from yet. Derived, never stored.
        /// </summary>
        public float Reliability
        {
            get
            {
                int recorded = completed + emergencies;
                return recorded <= 0 ? -1f : (float)completed / recorded;
            }
        }

        /// <summary>Record how one opening ended. The only writer of either count.</summary>
        internal void NoteOutcome(bool emergency)
        {
            if (emergency) { emergencies++; }
            else { completed++; }
        }
        public bool Pinned { get { return pinned; } }

        public GateHistoryEntry() { }

        internal GateHistoryEntry(string coordinateId, string label, int tick)
        {
            this.coordinateId = coordinateId;
            this.label = label;
            firstTick = tick;
            lastTick = tick;
            times = 1;
        }

        /// <summary>
        /// The name the player sees and edits. Setting it blank restores the coordinate's own
        /// label rather than leaving an address with no name at all.
        /// </summary>
        public string RenamableLabel
        {
            get { return string.IsNullOrEmpty(label) ? BaseLabel : label; }
            set { label = string.IsNullOrWhiteSpace(value) ? null : value.Trim(); }
        }

        public string BaseLabel { get { return coordinateId ?? string.Empty; } }

        public string InspectLabel { get { return RenamableLabel; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref label, "rr_label");
            Scribe_Values.Look(ref firstTick, "rr_firstTick", -1);
            Scribe_Values.Look(ref lastTick, "rr_lastTick", -1);
            Scribe_Values.Look(ref times, "rr_times", 0);
            Scribe_Values.Look(ref pinned, "rr_gateHistoryPinned", false);
            Scribe_Values.Look(ref completed, "rr_completed", 0);
            Scribe_Values.Look(ref emergencies, "rr_emergencies", 0);
        }
    }

    /// <summary>
    /// The address book a laboratory gate keeps of everywhere it has connected to.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"we need a proper history list that lab gates
    /// are connected have connected to in a easily editable clear able and manage bench
    /// connected to the portal gates natural gates dont get to call a seed they are what they
    /// are"*.
    ///
    /// ## The list belongs to the gate, not to the branch
    ///
    /// *"connected to the portal gates"* — so **two gates keep different address books**. That
    /// is the right shape rather than a convenience: a branch running a gate in its
    /// headquarters and another at an outpost is running two different operations, and merging
    /// their histories into one branch-wide list would lose the distinction that makes a second
    /// gate worth building.
    ///
    /// ## A natural gate has no address book, and that is enforced upstream
    ///
    /// *"natural gates dont get to call a seed they are what they are"* — a natural gate's
    /// destination is fixed at discovery and permanent. It may not dial, so it has nothing to
    /// remember.
    ///
    /// **This needed no new guard.** Every gate gizmo already sits behind `IsDesignated`, which
    /// is only ever true of a laboratory gate the player assembled. A natural threshold is a
    /// `PortalConnectionKind.Natural` record with no designated gate behind it, so it never
    /// reaches this code at all. Adding a second check would have implied the first one was
    /// unreliable.
    ///
    /// ## Editable, clearable, and bounded
    ///
    /// The owner asked for *"easily editable clear able and manage"*, and the reason is
    /// practical: **a history nobody can prune becomes unusable in a long game.** Entries can
    /// be renamed, pinned, removed one at a time, or cleared wholesale.
    ///
    /// The list caps at <see cref="Capacity"/> and drops the **least recently used unpinned**
    /// entry when full. Pinning is what makes that safe — the addresses a player actually
    /// cares about are the ones they marked, and those are never evicted to make room for a
    /// space they visited once by accident.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>How many addresses one gate remembers before it starts forgetting.</summary>
        public const int Capacity = 32;

        private List<GateHistoryEntry> connectionHistory = new List<GateHistoryEntry>();

        /// <summary>
        /// Which coordinate the live opening is to, so its outcome can be filed against the
        /// right entry when it closes.
        ///
        /// Remembered explicitly rather than read off the front of the list. The history is
        /// most-recently-used first, so *"the first entry is the one we are connected to"* is
        /// true today and would be a silent lie the first time anything else records a
        /// connection between opening and closing. One saved string is cheaper than that bug.
        /// </summary>
        private string historyCoordinateId;

        internal void ExposeConnectionHistory()
        {
            Scribe_Collections.Look(ref connectionHistory, "rr_gateConnectionHistory", LookMode.Deep);
            Scribe_Values.Look(ref historyCoordinateId, "rr_gateHistoryCoordinateId");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && connectionHistory == null)
            { connectionHistory = new List<GateHistoryEntry>(); }
        }

        /// <summary>Everything this gate has dialled, most recently used first.</summary>
        public IReadOnlyList<GateHistoryEntry> ConnectionHistory
        {
            get
            {
                connectionHistory = connectionHistory ?? new List<GateHistoryEntry>();
                return connectionHistory;
            }
        }

        /// <summary>
        /// Records that this gate connected to a coordinate. Idempotent per coordinate: a second
        /// connection updates the existing entry rather than adding a duplicate, which is what
        /// keeps the list an address book rather than a log.
        /// </summary>
        public void NoteConnected(CoordinateRecord coordinate)
        {
            if (coordinate == null || string.IsNullOrEmpty(coordinate.Id)) { return; }
            historyCoordinateId = coordinate.Id;
            connectionHistory = connectionHistory ?? new List<GateHistoryEntry>();
            int now = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;

            for (int index = 0; index < connectionHistory.Count; index++)
            {
                GateHistoryEntry entry = connectionHistory[index];
                if (entry == null || !string.Equals(entry.coordinateId, coordinate.Id, StringComparison.Ordinal))
                { continue; }
                entry.lastTick = now;
                if (entry.times < int.MaxValue) { entry.times++; }
                // Most recently used first, so the list stays useful without the player sorting it.
                connectionHistory.RemoveAt(index);
                connectionHistory.Insert(0, entry);
                return;
            }

            if (connectionHistory.Count >= Capacity && !EvictOne()) { return; }
            connectionHistory.Insert(0, new GateHistoryEntry(coordinate.Id, coordinate.Label, now));
        }

        /// <summary>
        /// Drops the least recently used **unpinned** entry. Returns false when everything is
        /// pinned, in which case nothing new is recorded rather than something the player
        /// deliberately kept being thrown away.
        /// </summary>
        private bool EvictOne()
        {
            for (int index = connectionHistory.Count - 1; index >= 0; index--)
            {
                if (connectionHistory[index] != null && connectionHistory[index].pinned) { continue; }
                connectionHistory.RemoveAt(index);
                return true;
            }
            return false;
        }

        /// <summary>Renames an entry. An empty name restores the coordinate's own label.</summary>
        public void RenameHistoryEntry(GateHistoryEntry entry, string label)
        {
            if (entry == null) { return; }
            entry.label = string.IsNullOrWhiteSpace(label) ? null : label.Trim();
        }

        /// <summary>Pins or unpins an entry, protecting it from eviction.</summary>
        public void ToggleHistoryPin(GateHistoryEntry entry)
        {
            if (entry == null) { return; }
            entry.pinned = !entry.pinned;
        }

        /// <summary>Removes one entry.</summary>
        public void RemoveHistoryEntry(GateHistoryEntry entry)
        {
            if (entry == null || connectionHistory == null) { return; }
            connectionHistory.Remove(entry);
        }

        /// <summary>
        /// Clears the whole list, **except pinned entries**.
        ///
        /// Pinned entries surviving a clear is deliberate. "Clear" in a long game means "get rid
        /// of the noise", and a single button that also destroyed the handful of addresses
        /// somebody had explicitly marked would be a trap rather than a convenience.
        /// </summary>
        /// <summary>
        /// File how the live opening ended against the coordinate it was to.
        ///
        /// Called from the one place an opening is torn down, so an opening cannot be counted
        /// twice and cannot be missed. Silent when there is no remembered coordinate, which is
        /// the case for a legacy opening recorded before this field existed.
        /// </summary>
        internal void NoteOpeningOutcome(bool emergency)
        {
            if (string.IsNullOrEmpty(historyCoordinateId) || connectionHistory == null)
            { historyCoordinateId = null; return; }
            for (int index = 0; index < connectionHistory.Count; index++)
            {
                GateHistoryEntry entry = connectionHistory[index];
                if (entry != null && string.Equals(entry.coordinateId, historyCoordinateId,
                    StringComparison.Ordinal))
                { entry.NoteOutcome(emergency); break; }
            }
            historyCoordinateId = null;
        }

        public int ClearConnectionHistory()
        {
            if (connectionHistory == null) { return 0; }
            int before = connectionHistory.Count;
            connectionHistory.RemoveAll(entry => entry == null || !entry.pinned);
            return before - connectionHistory.Count;
        }

        /// <summary>
        /// The management surface: one row per remembered address, and a clear.
        ///
        /// A float menu rather than a window, deliberately. Everything the owner asked for —
        /// *"easily editable clear able and manage"* — is four verbs on a short list, and a
        /// bespoke window would be more code, more to keep consistent, and no easier to use.
        /// Each row opens its own actions rather than cramming rename, pin and remove onto one
        /// line where a misclick destroys an address.
        /// </summary>
        internal void OpenConnectionHistoryMenu()
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            var options = new List<FloatMenuOption>();

            IReadOnlyList<GateHistoryEntry> entries = ConnectionHistory;
            if (entries.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_GateHistory_Empty".Translate(), null));
                Find.WindowStack.Add(new FloatMenu(options));
                return;
            }

            for (int index = 0; index < entries.Count; index++)
            {
                GateHistoryEntry entry = entries[index];
                if (entry == null) { continue; }
                GateHistoryEntry captured = entry;
                string name = HistoryLabelFor(entry, campaign);
                string row = entry.pinned
                    ? "RR_GateHistory_RowPinned".Translate(name, entry.times.ToString("N0"))
                    : "RR_GateHistory_Row".Translate(name, entry.times.ToString("N0"));
                options.Add(new FloatMenuOption(row,
                    delegate { OpenEntryMenu(captured, campaign); }));
            }

            options.Add(new FloatMenuOption("RR_GateHistory_Clear".Translate(),
                delegate
                {
                    int removed = ClearConnectionHistory();
                    Messages.Message("RR_GateHistory_Cleared".Translate(removed.ToString("N0")),
                        parent, MessageTypeDefOf.TaskCompletion, false);
                }));

            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>
        /// How the trips to one address have actually gone, in words.
        ///
        /// Row 725's reliability half, shown where a player is already deciding which address to
        /// dial — which is the only place the number is a decision rather than trivia. Says
        /// **"none finished yet"** rather than a percentage when there is nothing recorded,
        /// because `Reliability` returns -1 for that and a surface that printed 0% or 100% would
        /// be inventing a claim about a coordinate nobody has come back from.
        /// </summary>
        private static string ReliabilityRow(GateHistoryEntry entry)
        {
            float rate = entry.Reliability;
            if (rate < 0f) { return "RR_GateHistory_NoOutcomes".Translate().ToString(); }
            int recorded = entry.Completed + entry.Emergencies;
            return "RR_GateHistory_Reliability".Translate(entry.Completed.ToString("N0"),
                recorded.ToString("N0"), rate.ToStringPercent("F0")).ToString();
        }

        private void OpenEntryMenu(GateHistoryEntry entry, RimroomsCampaignComponent campaign)
        {
            string name = HistoryLabelFor(entry, campaign);
            var options = new List<FloatMenuOption>
            {
                // Read-only, and first, because it is what the player needs to know before
                // choosing any of the actions below it.
                new FloatMenuOption(ReliabilityRow(entry), null),
                // First, because it is what the list is for. Everything below it is management.
                new FloatMenuOption("RR_GateHistory_Dial".Translate(name), delegate
                {
                    CompanyActionResult result = DialRememberedAddress(entry);
                    if (!result.Success && !string.IsNullOrWhiteSpace(result.MessageKey))
                    { Messages.Message(result.MessageKey.Translate(), parent, MessageTypeDefOf.RejectInput, false); }
                }),
                new FloatMenuOption("RR_GateHistory_Rename".Translate(name), delegate
                {
                    Find.WindowStack.Add(new UI.Dialog_RenameGateAddress(entry));
                }),
                new FloatMenuOption(
                    entry.pinned ? "RR_GateHistory_Unpin".Translate() : "RR_GateHistory_Pin".Translate(),
                    delegate { ToggleHistoryPin(entry); }),
                new FloatMenuOption("RR_GateHistory_Remove".Translate(name), delegate
                {
                    RemoveHistoryEntry(entry);
                }),
            };
            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>
        /// The display name for an entry: the player's own name if they set one, the
        /// coordinate's label if it still exists, and the raw id only as a last resort — which
        /// happens when a coordinate has been removed from the branch but the gate still
        /// remembers dialling it.
        /// </summary>
        public static string HistoryLabelFor(GateHistoryEntry entry, RimroomsCampaignComponent campaign)
        {
            if (entry == null) { return string.Empty; }
            if (!string.IsNullOrEmpty(entry.label)) { return entry.label; }
            if (campaign != null)
            {
                for (int index = 0; index < campaign.Coordinates.Count; index++)
                {
                    CoordinateRecord record = campaign.Coordinates[index];
                    if (record != null && string.Equals(record.Id, entry.coordinateId, StringComparison.Ordinal)
                        && !string.IsNullOrEmpty(record.Label))
                    { return record.Label; }
                }
            }
            return entry.coordinateId ?? string.Empty;
        }
    }
}
