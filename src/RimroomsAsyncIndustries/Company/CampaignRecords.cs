using System.Collections.Generic;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    // Serialized enum values are fixed. Add new values without renumbering existing ones.
    public enum ContractStatus { Accepted = 0, Completed = 1, Failed = 2, Cancelled = 3 }
    public enum EvidenceStatus { Located = 0, Recovered = 1, Secured = 2, Analyzed = 3, Missing = 4 }
    public enum CoordinateStatus { Discovered = 0, Ready = 1, Unavailable = 2 }

    public sealed class LedgerEntry : IExposable
    {
        internal string operationId;
        internal long amountUsd;
        internal long balanceAfterUsd;
        internal int tick;
        internal string reasonKey;
        internal string relatedId;
        public string OperationId { get { return operationId; } }
        public long AmountUsd { get { return amountUsd; } }
        public long BalanceAfterUsd { get { return balanceAfterUsd; } }
        public int Tick { get { return tick; } }
        public string ReasonKey { get { return reasonKey; } }
        public string RelatedId { get { return relatedId; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref operationId, "rr_operationId");
            Scribe_Values.Look(ref amountUsd, "rr_amountUsd");
            Scribe_Values.Look(ref balanceAfterUsd, "rr_balanceAfterUsd");
            Scribe_Values.Look(ref tick, "rr_tick");
            Scribe_Values.Look(ref reasonKey, "rr_reasonKey");
            Scribe_Values.Look(ref relatedId, "rr_relatedId");
        }
    }

    public sealed class StaffRecord : IExposable
    {
        internal string id;
        internal Pawn pawn;
        internal string pawnLoadId;
        internal string nameAtHire;
        internal string role;
        internal long dailyWageUsd;
        internal int hiredTick;
        internal bool employed = true;
        public string Id { get { return id; } }
        public Pawn Pawn { get { return pawn; } }
        public string Name { get { return pawn == null ? nameAtHire : pawn.LabelShortCap.ToString(); } }
        public string Role { get { return role; } }
        public long DailyWageUsd { get { return dailyWageUsd; } }
        public bool Employed { get { return employed; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_References.Look(ref pawn, "rr_pawn");
            Scribe_Values.Look(ref pawnLoadId, "rr_pawnLoadId");
            Scribe_Values.Look(ref nameAtHire, "rr_nameAtHire");
            Scribe_Values.Look(ref role, "rr_role");
            Scribe_Values.Look(ref dailyWageUsd, "rr_dailyWageUsd");
            Scribe_Values.Look(ref hiredTick, "rr_hiredTick");
            Scribe_Values.Look(ref employed, "rr_employed", true);
        }
    }

    public sealed class CompanyObligation : IExposable
    {
        internal string id;
        internal string reasonKey;
        internal long amountUsd;
        internal int dueTick;
        internal bool paid;
        public string Id { get { return id; } }
        public string ReasonKey { get { return reasonKey; } }
        public long AmountUsd { get { return amountUsd; } }
        public int DueTick { get { return dueTick; } }
        public bool Paid { get { return paid; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref reasonKey, "rr_reasonKey");
            Scribe_Values.Look(ref amountUsd, "rr_amountUsd");
            Scribe_Values.Look(ref dueTick, "rr_dueTick");
            Scribe_Values.Look(ref paid, "rr_paid");
        }
    }

    public sealed class ContractRecord : IExposable
    {
        internal string id;
        internal string templateId;
        internal string titleKey;
        internal string coordinateId;
        internal ContractStatus status;
        internal long basePaymentUsd;
        internal long bonusUsd;
        internal int acceptedTick;
        internal int completedTick = -1;
        internal string settlementOperationId;

        /// <summary>
        /// Supply-contract demand: the thing definition wanted, how many, and how many have
        /// been handed over so far. Empty on every other contract kind, which is what
        /// <see cref="IsOddSupply"/> tests.
        ///
        /// A supply contract wants goods that came **out of a Backrooms coordinate** and will
        /// not accept the ordinary equivalent. That is the whole point of it, and it is why
        /// the marker had to exist first.
        /// </summary>
        internal string requiredThingDefName;
        internal int requiredCount;
        internal int deliveredCount;

        /// <summary>
        /// Consignment-mission field condition: a space at least this deep, surveyed at least
        /// this far. **Zero on every other record**, including every contract written before
        /// 0.12.41-dev, and a zero reports its condition met — which is what lets one settlement
        /// path serve a plain contract and a mission without a second copy of it.
        ///
        /// This is what makes a mission a mission. A contract pays for hauling; a mission does
        /// not settle until a space has actually been worked, which is the owner's own reason
        /// for the whole family: *"give reason for the players to have to advance and excplore
        /// and haul and use the spaces iin the backrooms"*.
        /// </summary>
        internal int requiredDepth;
        internal int requiredSurveyedRooms;

        public string RequiredThingDefName { get { return requiredThingDefName; } }
        public int RequiredCount { get { return requiredCount; } }
        public int DeliveredCount { get { return deliveredCount; } }
        public int RequiredDepth { get { return requiredDepth; } }
        public int RequiredSurveyedRooms { get { return requiredSurveyedRooms; } }

        /// <summary>True when this contract is a demand for odd goods rather than a survey.</summary>
        public bool IsOddSupply
        {
            get { return !string.IsNullOrEmpty(requiredThingDefName) && requiredCount > 0; }
        }

        /// <summary>
        /// True when this record is a consignment mission rather than a standing demand. The
        /// field condition is the only difference in the data, and it is the whole difference in
        /// what the player has to do.
        /// </summary>
        public bool IsOddConsignment
        {
            get { return IsOddSupply && requiredSurveyedRooms > 0; }
        }
        public string Id { get { return id; } }
        public string TemplateId { get { return templateId; } }
        public string TitleKey { get { return titleKey; } }
        public string CoordinateId { get { return coordinateId; } }
        public ContractStatus Status { get { return status; } }
        public long BasePaymentUsd { get { return basePaymentUsd; } }
        public long BonusUsd { get { return bonusUsd; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref templateId, "rr_templateId");
            Scribe_Values.Look(ref titleKey, "rr_titleKey");
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref status, "rr_status");
            Scribe_Values.Look(ref basePaymentUsd, "rr_basePaymentUsd");
            Scribe_Values.Look(ref bonusUsd, "rr_bonusUsd");
            Scribe_Values.Look(ref acceptedTick, "rr_acceptedTick");
            Scribe_Values.Look(ref completedTick, "rr_completedTick", -1);
            Scribe_Values.Look(ref settlementOperationId, "rr_settlementOperationId");
            Scribe_Values.Look(ref requiredThingDefName, "rr_requiredThingDefName");
            Scribe_Values.Look(ref requiredCount, "rr_requiredCount", 0);
            Scribe_Values.Look(ref deliveredCount, "rr_deliveredCount", 0);
            // Defaulted, so a save written before 0.12.41-dev loads with no field condition and
            // every contract in it keeps behaving exactly as it did.
            Scribe_Values.Look(ref requiredDepth, "rr_requiredDepth", 0);
            Scribe_Values.Look(ref requiredSurveyedRooms, "rr_requiredSurveyedRooms", 0);
        }
    }

    public sealed class CoordinateRecord : IExposable
    {
        internal string id;
        internal string label;
        internal int seed;
        internal int generatorVersion = 1;
        internal int roomLibraryVersion = 1;
        internal CoordinateStatus status;
        internal MapParent site;
        internal string lastFailureKey;
        internal List<RoomRecord> rooms = new List<RoomRecord>();

        /// <summary>
        /// The distinct thing definitions this coordinate actually produced as odd goods,
        /// recorded once at generation.
        ///
        /// Supply contracts are drawn from this rather than from the whole def database, and
        /// that is the difference between a demand a player can meet and one they cannot. A
        /// contract asking for a thousand odd cotton is worthless if no coordinate the branch
        /// has ever opened contained cotton — the player would be sent to look for something
        /// that does not exist down there. Recording what a space really held means every
        /// demand is answerable by going back to a space that has it.
        /// </summary>
        internal List<string> oddGoodsDefNames = new List<string>();

        /// <summary>
        /// How deep this coordinate sits, counted in portals from the ordinary world. The first
        /// space reached from a world map is 1; a frontier found inside it mints 2, and so on
        /// without limit.
        ///
        /// **This is what makes the place look like itself and then stop looking like itself.**
        /// Owner direction 2026-09-29: the yellow carpet, yellow wood walls and overhead light
        /// are *"the main backrooms look"*, and *"further in it gets very varied and weird"*. A
        /// single global palette could only ever deliver the first half of that. Depth is the
        /// axis the palette, the room library and eventually the escalation ladder all read.
        ///
        /// Defaults to 1 so a coordinate saved before 0.7.8-dev reads as a shallow one, which
        /// is both the safe answer and the true one for every space discovered so far.
        /// </summary>
        internal int depth = 1;

        /// <summary>
        /// The player let this place go on purpose, and it may be regenerated.
        ///
        /// **This flag exists to answer one question that cannot otherwise be answered.**
        /// <see cref="Generation.DestinationService.EnsureSite"/> refuses to build a map for a
        /// coordinate that has no site but whose rooms have been surveyed, because *"a broken
        /// reference must not create a competing owner or replace an already explored graph"*.
        /// That is exactly right for a fault. It is exactly wrong for a deliberate release, and
        /// from the outside the two look identical: no site, rooms surveyed.
        ///
        /// So a release says so, in the save. Cleared the moment the place is generated again.
        /// </summary>
        internal bool releasedByPlayer;

        public int Depth { get { return depth < 1 ? 1 : depth; } }

        /// <summary>
        /// How many times this coordinate has been opened, and how long the branch's people
        /// have actually worked inside it.
        ///
        /// These are the **saved observable causes** the escalation ladder is allowed to read.
        /// The owner's rule is explicit about what it may *not* read: wall-clock time, a fresh
        /// draw per load, or the mere fact that a gate is open. Both of these are things the
        /// player did, both are recorded, and **both survive a reload unchanged** — which is
        /// what makes revisiting a known space resume its pressure rather than reroll it up to
        /// punish the revisit or down to make it safe.
        /// </summary>
        internal int openings;
        internal int occupancyTicks;

        public int Openings { get { return openings; } }
        public int OccupancyTicks { get { return occupancyTicks; } }

        /// <summary>Records one opening. Saturates rather than overflowing on a very long game.</summary>
        internal void NoteOpened()
        {
            if (openings < int.MaxValue - 1) { openings++; }
        }

        /// <summary>Adds worked time inside this coordinate.</summary>
        /// <summary>
        /// Anomalous events that have already fired here and are not repeatable.
        ///
        /// Recorded so a revisit **resumes rather than replays** — the same rule the escalation
        /// ladder follows. A space a player knows should not perform its party trick every
        /// single time they walk in; that turns an unsettling event into a chore.
        /// </summary>
        internal List<string> firedEventDefNames = new List<string>();

        /// <summary>
        /// Room dimensions taken from the branch's own colony **at the moment this coordinate
        /// was discovered**, and never re-read afterwards.
        ///
        /// **Captured once rather than read live, and that is load-bearing.** Layout planning is
        /// re-run to verify a saved graph against its fingerprint, so if the planner consulted
        /// the colony's *current* rooms, a coordinate planned before the player built an
        /// extension would replan differently afterwards and **fail its own fingerprint check**
        /// — turning a working space into one that refuses to generate.
        ///
        /// Snapshotting at discovery also happens to be the better fiction: the place copied
        /// what it saw when it opened, not what you have built since.
        /// </summary>
        internal List<int> echoedRoomSizes = new List<int>();

        public IReadOnlyList<int> EchoedRoomSizes { get { return echoedRoomSizes; } }

        public bool HasFiredEvent(string defName)
        {
            return firedEventDefNames != null && firedEventDefNames.Contains(defName);
        }

        internal void NoteEventFired(string defName)
        {
            if (string.IsNullOrEmpty(defName)) { return; }
            firedEventDefNames = firedEventDefNames ?? new List<string>();
            if (!firedEventDefNames.Contains(defName)) { firedEventDefNames.Add(defName); }
        }

        internal void NoteOccupancy(int ticks)
        {
            if (ticks <= 0) { return; }
            long total = (long)occupancyTicks + ticks;
            occupancyTicks = total > int.MaxValue ? int.MaxValue : (int)total;
        }

        public IReadOnlyList<string> OddGoodsDefNames { get { return oddGoodsDefNames; } }
        public string Id { get { return id; } }
        public string Label { get { return label; } }

        /// <summary>
        /// **THE ONLY IDENTIFIER A PLAYER EVER SEES.**
        ///
        /// Owner, 2026-10-04: *"we dont need things like long string corrdinates list in the
        /// operations panel thing like that arnet needed only like the !A-01 address code is
        /// needed to be displayed to thew player and save able and useable"*.
        ///
        /// The code itself is not new — `label` has been `AI-01`, `AI-02` and so on since the
        /// first version, assigned in discovery order so it is short, unique within a branch and
        /// stable across a reload. **What was wrong is that the raw `id` leaked out beside it**:
        /// a thirty-character internal string on a button, and in an address list that printed
        /// the connection id, the coordinate id and the code all on one line.
        ///
        /// So this exists to be the thing every readout asks for, rather than each one choosing
        /// between `Label`, `Id` and a fallback. A record with no label falls back to its id
        /// because a row with no identifier at all is worse than an ugly one — and that is a
        /// repair case, not a display choice.
        /// </summary>
        public string AddressCode
        {
            get { return string.IsNullOrEmpty(label) ? id : label; }
        }

        public int Seed { get { return seed; } }
        public int GeneratorVersion { get { return generatorVersion; } }
        public CoordinateStatus Status { get { return status; } }
        public bool ReleasedByPlayer { get { return releasedByPlayer; } }
        public MapParent Site { get { return site; } }
        public IReadOnlyList<RoomRecord> Rooms { get { return rooms; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref label, "rr_label");
            Scribe_Values.Look(ref seed, "rr_seed");
            Scribe_Values.Look(ref generatorVersion, "rr_generatorVersion", 1, true);
            Scribe_Values.Look(ref roomLibraryVersion, "rr_roomLibraryVersion", 1, true);
            Scribe_Values.Look(ref status, "rr_status");
            Scribe_References.Look(ref site, "rr_site");
            Scribe_Values.Look(ref lastFailureKey, "rr_lastFailureKey");
            Scribe_Collections.Look(ref rooms, "rr_rooms", LookMode.Deep);
            Scribe_Collections.Look(ref oddGoodsDefNames, "rr_oddGoodsDefNames", LookMode.Value);
            Scribe_Values.Look(ref depth, "rr_depth", 1);
            Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);
            Scribe_Values.Look(ref openings, "rr_openings", 0);
            Scribe_Values.Look(ref occupancyTicks, "rr_occupancyTicks", 0);
            Scribe_Collections.Look(ref firedEventDefNames, "rr_firedEvents", LookMode.Value);
            Scribe_Collections.Look(ref echoedRoomSizes, "rr_echoedRoomSizes", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && firedEventDefNames == null)
            { firedEventDefNames = new List<string>(); }
            if (Scribe.mode == LoadSaveMode.PostLoadInit && echoedRoomSizes == null)
            { echoedRoomSizes = new List<int>(); }
            if (Scribe.mode == LoadSaveMode.PostLoadInit && rooms == null) { rooms = new List<RoomRecord>(); }
            // A coordinate saved before 0.7.2-dev has no recorded odd goods. An empty list is
            // the honest answer -- it simply offers no supply contracts of its own -- rather
            // than inventing contents for a space that was generated before this existed.
            if (Scribe.mode == LoadSaveMode.PostLoadInit && oddGoodsDefNames == null)
            { oddGoodsDefNames = new List<string>(); }
        }
    }

    public sealed class RoomRecord : IExposable
    {
        internal int index;
        internal string familyId;
        internal int x;
        internal int z;
        internal int width;
        internal int height;
        internal bool surveyed;
        internal List<int> links = new List<int>();
        public int Index { get { return index; } }
        public string FamilyId { get { return familyId; } }
        public CellRect Bounds { get { return new CellRect(x, z, width, height); } }
        public bool Surveyed { get { return surveyed; } }
        public IReadOnlyList<int> Links { get { return links; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref index, "rr_index");
            Scribe_Values.Look(ref familyId, "rr_familyId");
            Scribe_Values.Look(ref x, "rr_x");
            Scribe_Values.Look(ref z, "rr_z");
            Scribe_Values.Look(ref width, "rr_width");
            Scribe_Values.Look(ref height, "rr_height");
            Scribe_Values.Look(ref surveyed, "rr_surveyed");
            Scribe_Collections.Look(ref links, "rr_links", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && links == null) { links = new List<int>(); }
        }
    }

    public sealed class CaseRecord : IExposable
    {
        internal string id;
        internal string titleKey;
        internal string coordinateId;
        internal List<string> evidenceIds = new List<string>();
        internal bool closed;
        public string Id { get { return id; } }
        public string TitleKey { get { return titleKey; } }
        public string CoordinateId { get { return coordinateId; } }
        public IReadOnlyList<string> EvidenceIds { get { return evidenceIds; } }
        public bool Closed { get { return closed; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref titleKey, "rr_titleKey");
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Collections.Look(ref evidenceIds, "rr_evidenceIds", LookMode.Value);
            Scribe_Values.Look(ref closed, "rr_closed");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && evidenceIds == null) { evidenceIds = new List<string>(); }
        }
    }

    public sealed class EvidenceRecord : IExposable
    {
        internal const int CurrentObservationSchemaVersion = 1;
        internal string id;
        internal string coordinateId;
        internal string caseId;
        internal Thing item;
        internal string itemLoadId;
        internal EvidenceStatus status;
        internal bool routeRecorded;
        internal bool distortionRecorded;
        internal bool entityRecorded;
        internal string sourceExpeditionId;
        internal Pawn analyst;
        internal int analyzedTick = -1;
        internal float analysisWork;
        // Additive schema-2 fields. A missing version on an existing save means its
        // booleans predate structured observations; never synthesize rows from them.
        internal int observationSchemaVersion = CurrentObservationSchemaVersion;
        internal bool legacyRouteRecorded;
        internal List<EvidenceObservationRecord> observations = new List<EvidenceObservationRecord>();
        internal EvidenceAnalysisReport analysisReport;

        // **Review: the fourth workflow, additive on purpose.** Recorded BESIDE the status and
        // never instead of it -- `EvidenceStatus.Analyzed` is terminal and eight places compare
        // against it, so a sixth enum member would change all of them and break saves that
        // store the value. A record from before this existed loads with reviewer null and
        // reviewedTick -1, which reads as "not reviewed" and is exactly true.
        internal Pawn reviewer;
        internal int reviewedTick = -1;
        internal bool reviewEndorsed;

        public string Id { get { return id; } }
        public EvidenceStatus Status { get { return status; } }
        public Thing Item { get { return item; } }
        public string CoordinateId { get { return coordinateId; } }
        public float AnalysisWork { get { return analysisWork; } }
        public bool RouteRecorded { get { return routeRecorded; } }
        public bool DistortionRecorded { get { return distortionRecorded; } }
        public bool EntityRecorded { get { return entityRecorded; } }
        public IReadOnlyList<EvidenceObservationRecord> Observations { get { return observations; } }
        public EvidenceAnalysisReport AnalysisReport { get { return analysisReport; } }

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
        }
        public bool LegacyObservationDetailsUnavailable
        { get { return analysisReport != null && analysisReport.LegacyDetailsUnavailable; } }

        internal void FreezeAnalysisReport(Pawn completingAnalyst, int completedTick)
        {
            if (analysisReport != null) { return; }
            bool legacyUnavailable = observations.Count == 0 && observationSchemaVersion < CurrentObservationSchemaVersion;
            analysisReport = EvidenceAnalysisReport.Capture(observations, completingAnalyst, completedTick, legacyUnavailable);
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref caseId, "rr_caseId");
            Scribe_References.Look(ref item, "rr_item");
            Scribe_Values.Look(ref itemLoadId, "rr_itemLoadId");
            Scribe_Values.Look(ref status, "rr_status");
            Scribe_Values.Look(ref routeRecorded, "rr_routeRecorded");
            Scribe_Values.Look(ref distortionRecorded, "rr_distortionRecorded");
            Scribe_Values.Look(ref entityRecorded, "rr_entityRecorded");
            Scribe_Values.Look(ref sourceExpeditionId, "rr_sourceExpeditionId");
            Scribe_References.Look(ref analyst, "rr_analyst");
            Scribe_Values.Look(ref analyzedTick, "rr_analyzedTick", -1);
            Scribe_Values.Look(ref analysisWork, "rr_analysisWork");
            Scribe_Values.Look(ref observationSchemaVersion, "rr_observationSchemaVersion", 0);
            Scribe_Values.Look(ref legacyRouteRecorded, "rr_legacyRouteRecorded");
            Scribe_Collections.Look(ref observations, "rr_observations", LookMode.Deep);
            Scribe_Deep.Look(ref analysisReport, "rr_analysisReport");
            Scribe_References.Look(ref reviewer, "rr_reviewer");
            Scribe_Values.Look(ref reviewedTick, "rr_reviewedTick", -1);
            Scribe_Values.Look(ref reviewEndorsed, "rr_reviewEndorsed");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                observations = observations ?? new List<EvidenceObservationRecord>();
                if (observationSchemaVersion < CurrentObservationSchemaVersion && routeRecorded)
                { legacyRouteRecorded = true; }
                if (analysisReport == null && analyzedTick >= 0)
                {
                    // Older analyzed evidence had only checklist booleans. Preserve the
                    // analyst/time receipt and explicitly label its missing detail.
                    analysisReport = observations.Count == 0
                        ? EvidenceAnalysisReport.LegacyUnavailable(analyst, analyzedTick)
                        : EvidenceAnalysisReport.Capture(observations, analyst, analyzedTick, false);
                }
            }
        }
    }

    public sealed class ProjectRecord : IExposable
    {
        internal string id;
        internal string researchDefName;
        internal string insightOperationId;
        internal bool insightCommitted;
        internal bool completed;
        internal float workDone;
        public string Id { get { return id; } }
        public string ResearchDefName { get { return researchDefName; } }
        public bool InsightCommitted { get { return insightCommitted; } }
        public bool Completed { get { return completed; } }
        public float WorkDone { get { return workDone; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref researchDefName, "rr_researchDefName");
            Scribe_Values.Look(ref insightOperationId, "rr_insightOperationId");
            Scribe_Values.Look(ref insightCommitted, "rr_insightCommitted");
            Scribe_Values.Look(ref completed, "rr_completed");
            Scribe_Values.Look(ref workDone, "rr_workDone");
        }
    }

    public sealed class CompanyEventRecord : IExposable
    {
        internal int tick;
        internal string messageKey;
        internal string relatedId;
        internal List<string> arguments = new List<string>();
        public int Tick { get { return tick; } }
        public string MessageKey { get { return messageKey; } }
        public IReadOnlyList<string> Arguments { get { return arguments; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref tick, "rr_tick");
            Scribe_Values.Look(ref messageKey, "rr_messageKey");
            Scribe_Values.Look(ref relatedId, "rr_relatedId");
            Scribe_Collections.Look(ref arguments, "rr_arguments", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && arguments == null) { arguments = new List<string>(); }
        }
    }
}
