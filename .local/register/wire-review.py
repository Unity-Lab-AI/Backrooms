# -*- coding: utf-8 -*-
"""Wire the review workflow: record fields, save, and the two surfaces that reach it.

**Additive fields, never a sixth `EvidenceStatus`.** `Analyzed` is the terminal state that the
laboratory job driver, the first-slice site component, the objective hint and the resurvey gate
all test for, and the enum is saved by value. A new member would change every one of those
comparisons and break every existing save. This is the same discipline
`observationSchemaVersion` already uses in the same record.

**And it ships with its consumers in the same checkpoint.** Four of five bond defects were built,
correct and unreachable, so a workflow with no surface is not finished. Two surfaces:

* the evidence readout names the reviewer and says whether the branch stood behind the report,
* the objective hint tells the player a sign-off is the next step, between analysis and telemetry.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
RECORDS = os.path.join(SRC, "Company", "CampaignRecords.cs")
EVIDENCE_UI = os.path.join(SRC, "UI", "OperationsEvidence.cs")
EXPEDITIONS_UI = os.path.join(SRC, "UI", "OperationsExpeditions.cs")

EDITS = []

# ---------------------------------------------------------------- 1. the fields
EDITS.append((RECORDS, u"""        internal EvidenceAnalysisReport analysisReport;
        public string Id { get { return id; } }""", u"""        internal EvidenceAnalysisReport analysisReport;

        // **Review: the fourth workflow, additive on purpose.** Recorded BESIDE the status and
        // never instead of it -- `EvidenceStatus.Analyzed` is terminal and eight places compare
        // against it, so a sixth enum member would change all of them and break saves that
        // store the value. A record from before this existed loads with reviewer null and
        // reviewedTick -1, which reads as "not reviewed" and is exactly true.
        internal Pawn reviewer;
        internal int reviewedTick = -1;
        internal bool reviewEndorsed;

        public string Id { get { return id; } }"""))

EDITS.append((RECORDS, u"""        public EvidenceAnalysisReport AnalysisReport { get { return analysisReport; } }""",
              u"""        public EvidenceAnalysisReport AnalysisReport { get { return analysisReport; } }

        /// <summary>The analyst who completed the report, so a reviewer can be refused for being them.</summary>
        public Pawn Analyst { get { return analyst; } }

        /// <summary>Whether somebody has signed this report off, either way.</summary>
        public bool Reviewed { get { return reviewedTick >= 0; } }

        /// <summary>Who signed it off. Null until somebody has.</summary>
        public Pawn Reviewer { get { return reviewer; } }

        /// <summary>When it was signed off, or -1.</summary>
        public int ReviewedTick { get { return reviewedTick; } }

        /// <summary>
        /// Whether the branch stood behind the report. **False is a real outcome, not a
        /// failure**: a report whose observation detail never existed is one the company cannot
        /// endorse, and saying so is worth more to the player than a rubber stamp.
        /// </summary>
        public bool ReviewEndorsed { get { return reviewEndorsed; } }

        internal void MarkReviewed(Pawn signingReviewer, int tick, bool endorsed)
        {
            if (reviewedTick >= 0) { return; }
            reviewer = signingReviewer;
            reviewedTick = tick;
            reviewEndorsed = endorsed;
        }"""))

EDITS.append((RECORDS, u"""            Scribe_Deep.Look(ref analysisReport, "rr_analysisReport");""",
              u"""            Scribe_Deep.Look(ref analysisReport, "rr_analysisReport");
            Scribe_References.Look(ref reviewer, "rr_reviewer");
            Scribe_Values.Look(ref reviewedTick, "rr_reviewedTick", -1);
            Scribe_Values.Look(ref reviewEndorsed, "rr_reviewEndorsed");"""))

# ---------------------------------------------------------------- 2. the readout
EDITS.append((EVIDENCE_UI, u"""                listing.Label("RR_UI_AnalysisReportHeader".Translate(report.AnalystName, Day(report.CompletedTick)));
                listing.Label("RR_UI_AnalysisSnapshotNote".Translate());""",
              u"""                listing.Label("RR_UI_AnalysisReportHeader".Translate(report.AnalystName, Day(report.CompletedTick)));
                listing.Label("RR_UI_AnalysisSnapshotNote".Translate());
                // **The review workflow's readout.** A sign-off nobody can see is a sign-off
                // that may as well not have happened -- which is what became of every second
                // crew account until 0.12.25-dev.
                if (record.Reviewed)
                {
                    listing.Label((record.ReviewEndorsed
                        ? "RR_UI_ReviewEndorsed" : "RR_UI_ReviewReturned").Translate(
                            record.Reviewer == null
                                ? "RR_UI_ReviewerUnknown".Translate().ToString()
                                : record.Reviewer.LabelShortCap.ToString(),
                            Day(record.ReviewedTick)));
                }
                else { listing.Label("RR_UI_ReviewAwaiting".Translate()); }"""))

# ---------------------------------------------------------------- 3. the objective hint
EDITS.append((EXPEDITIONS_UI,
              u"""            else if (record.Status != EvidenceStatus.Analyzed) { key = "RR_UI_NextAnalysis"; pane = 6; }
            else if (!campaign.HasRouteTelemetry) { key = "RR_UI_NextTelemetry"; pane = 6; }""",
              u"""            else if (record.Status != EvidenceStatus.Analyzed) { key = "RR_UI_NextAnalysis"; pane = 6; }
            // **Review is the step between a finished report and the next lead**, and the
            // objective line is how the player learns the step exists at all.
            else if (campaign.AwaitsReview(record)) { key = "RR_UI_NextReview"; pane = 6; }
            else if (!campaign.HasRouteTelemetry) { key = "RR_UI_NextTelemetry"; pane = 6; }"""))

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:52], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

records = io.open(RECORDS, encoding="utf-8-sig").read()
evidence_ui = io.open(EVIDENCE_UI, encoding="utf-8-sig").read()
expeditions_ui = io.open(EXPEDITIONS_UI, encoding="utf-8-sig").read()

failures = []
for token in ("internal Pawn reviewer;", "public bool Reviewed", "internal void MarkReviewed",
              'Scribe_References.Look(ref reviewer, "rr_reviewer");',
              'Scribe_Values.Look(ref reviewedTick, "rr_reviewedTick", -1);'):
    if token not in records:
        failures.append("records missing %r" % token[:46])
if u"Located = 0, Recovered = 1, Secured = 2, Analyzed = 3, Missing = 4" not in records:
    failures.append("THE EvidenceStatus ENUM CHANGED -- it must not")
if u"RR_UI_ReviewEndorsed" not in evidence_ui:
    failures.append("the readout does not show the review")
if u'campaign.AwaitsReview(record)' not in expeditions_ui:
    failures.append("the objective hint never names review")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("review wired: additive fields, saved, and reachable from two surfaces")
print("EvidenceStatus is byte-for-byte unchanged")
