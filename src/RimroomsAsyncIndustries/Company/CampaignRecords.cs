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
        public string Id { get { return id; } }
        public string Label { get { return label; } }
        public int Seed { get { return seed; } }
        public int GeneratorVersion { get { return generatorVersion; } }
        public CoordinateStatus Status { get { return status; } }
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
            if (Scribe.mode == LoadSaveMode.PostLoadInit && rooms == null) { rooms = new List<RoomRecord>(); }
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
