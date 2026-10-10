# -*- coding: utf-8 -*-
"""Row 725's two genuine gaps: damage-driven repair, and a reliability record.

Seven of the row's nine nouns were already built and were measured before anything was written
here. What this wires is the integrity tick and its refusal, and outcome counting on the
per-coordinate history entry -- which recorded `times` and nothing at all about how any of it
went, so the history could not answer the one question a player would ask of it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


GATE = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"
HISTORY = "src/RimroomsAsyncIndustries/Gate/GateConnectionHistory.cs"

# ------------------------------------------------------------------ the readout
sub(GATE, u"            string cutoffText = KillSwitchReadout();",
    u"""            string cutoffText = KillSwitchReadout();
            // Said only when the machine is not sound. A line reading "condition 100%" on every
            // gate forever is noise, and Core's own health bar already covers the ordinary case.
            string integrityText = IntegritySound ? null
                : "RR_Gate_IntegrityReadout".Translate(
                    IntegrityFraction.ToStringPercent("F0"),
                    IntegrityFloorFraction.ToStringPercent("F0")).ToString();""")

# ------------------------------------------------------------------ outcome fields on the entry
sub(HISTORY, u"""        internal int times;
        internal bool pinned;""",
    u"""        internal int times;
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

        internal int emergencies;""")

sub(HISTORY, u"        public int Times { get { return times; } }",
    u"""        public int Times { get { return times; } }
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
        }""")

sub(HISTORY, u'            Scribe_Values.Look(ref pinned, "rr_pinned", false);',
    u'            Scribe_Values.Look(ref pinned, "rr_gateHistoryPinned", false);\n'
    u'            Scribe_Values.Look(ref completed, "rr_completed", 0);\n'
    u'            Scribe_Values.Look(ref emergencies, "rr_emergencies", 0);')

# ------------------------------------------------------------------ remember which coordinate
sub(HISTORY, u"        private List<GateHistoryEntry> connectionHistory = new List<GateHistoryEntry>();",
    u"""        private List<GateHistoryEntry> connectionHistory = new List<GateHistoryEntry>();

        /// <summary>
        /// Which coordinate the live opening is to, so its outcome can be filed against the
        /// right entry when it closes.
        ///
        /// Remembered explicitly rather than read off the front of the list. The history is
        /// most-recently-used first, so *"the first entry is the one we are connected to"* is
        /// true today and would be a silent lie the first time anything else records a
        /// connection between opening and closing. One saved string is cheaper than that bug.
        /// </summary>
        private string historyCoordinateId;""")

sub(HISTORY, u'            connectionHistory.Insert(0, new GateHistoryEntry(coordinate.Id, coordinate.Label, now));',
    u'            connectionHistory.Insert(0, new GateHistoryEntry(coordinate.Id, coordinate.Label, now));')

sub(HISTORY, u"        public void NoteConnected(CoordinateRecord coordinate)\n        {\n"
             u"            if (coordinate == null || string.IsNullOrEmpty(coordinate.Id)) { return; }",
    u"        public void NoteConnected(CoordinateRecord coordinate)\n        {\n"
    u"            if (coordinate == null || string.IsNullOrEmpty(coordinate.Id)) { return; }\n"
    u"            historyCoordinateId = coordinate.Id;")

sub(HISTORY, u"        public int ClearConnectionHistory()",
    u"""        /// <summary>
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

        public int ClearConnectionHistory()""")

sub(HISTORY, u'            Scribe_Collections.Look(ref connectionHistory, "rr_gateConnectionHistory", LookMode.Deep);',
    u'            Scribe_Collections.Look(ref connectionHistory, "rr_gateConnectionHistory", LookMode.Deep);\n'
    u'            Scribe_Values.Look(ref historyCoordinateId, "rr_gateHistoryCoordinateId");')

# ------------------------------------------------------------------ file the outcome on close
sub(GATE, u"""        private void CloseOpeningCore()
        {
            if (portalOwnerFault || (!string.IsNullOrEmpty(portalOpeningId) && IsEmergency)) { return; }""",
    u"""        private void CloseOpeningCore()
        {
            if (portalOwnerFault || (!string.IsNullOrEmpty(portalOpeningId) && IsEmergency)) { return; }
            // Row 725's reliability half. Read before `failureKey` is cleared below, because
            // that field IS the emergency, and filed here because this is the one place an
            // opening is torn down -- so an outcome cannot be counted twice or missed.
            NoteOpeningOutcome(IsEmergency);""")

print("gate subsystems wired")
