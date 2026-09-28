using System;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Investigation;
using RimroomsAsyncIndustries.Generation;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed partial class RimroomsCampaignComponent
    {
        public EvidenceRecord FindEvidence(string id) { return evidence.FirstOrDefault(e => e.id == id); }
        public ProjectRecord ActiveProject { get { return projects.FirstOrDefault(p => p.insightCommitted && !p.completed); } }
        public bool HasRouteTelemetry
        {
            get { return projects.Any(p => p.completed && DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(p.researchDefName)?.unlocksSurveyedRoutePlanning == true); }
        }

        public CompanyActionResult EnsureRouteRecording(CoordinateRecord coordinate)
        {
            if (!CanOperate || coordinate == null || !coordinates.Contains(coordinate))
            { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            EvidenceRecord prior = FindEvidence(coordinate.id + ":evidence:route");
            if (prior != null)
            {
                // A missing/destroyed recording remains a loss. Reopening a site must still be possible.
                if (prior.analyzedTick < 0 && (prior.item == null || prior.item.Destroyed)) { prior.status = EvidenceStatus.Missing; }
                return CompanyActionResult.Existing();
            }
            Map map = coordinate.site == null ? null : coordinate.site.Map;
            if (map == null) { return CompanyActionResult.Refused("RR_Evidence_SiteUnavailable"); }
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_RouteRecording");
            if (definition == null) { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
            // Recover a physical spawn whose record-registration was interrupted; do not mint another.
            var physical = map.listerThings.ThingsOfDef(definition);
            if (physical.Count == 1) { return RegisterRouteRecording(coordinate, physical[0]); }
            if (physical.Count > 1) { return CompanyActionResult.Refused("RR_Company_ReceiptMismatch"); }
            RoomRecord office = coordinate.rooms.FirstOrDefault(r => r.familyId == "office_copy");
            if (office == null) { return CompanyActionResult.Refused("RR_Evidence_NoSafeSlot"); }
            IntVec3 cell = (coordinate.site as RimroomsDestinationMapParent)?.OfficeEvidenceCell ?? IntVec3.Invalid;
            if (!cell.IsValid || !office.Bounds.Contains(cell) || !cell.InBounds(map) || !cell.Standable(map) || cell.GetFirstItem(map) != null)
            { return CompanyActionResult.Refused("RR_Evidence_NoSafeSlot"); }
            try
            {
                Thing recording = ThingMaker.MakeThing(definition);
                GenSpawn.Spawn(recording, cell, map);
                recording.SetForbidden(false, false);
                return RegisterRouteRecording(coordinate, recording);
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Evidence] Retained site after recording placement failure: " + error);
                return CompanyActionResult.Refused("RR_Evidence_NoSafeSlot");
            }
        }

        public CompanyActionResult RegisterRouteRecording(CoordinateRecord coordinate, Thing recording)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            CompRouteEvidence comp = recording == null ? null : recording.TryGetComp<CompRouteEvidence>();
            CaseRecord caseRecord = coordinate == null ? null : cases.FirstOrDefault(c => c.coordinateId == coordinate.id);
            if (coordinate == null || !coordinates.Contains(coordinate) || caseRecord == null || comp == null || recording.Destroyed || recording.stackCount != 1)
            { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
            string id = coordinate.id + ":evidence:route";
            EvidenceRecord existing = FindEvidence(id);
            if (existing != null)
            {
                return existing.item == recording && comp.EvidenceId == id ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Company_ReceiptMismatch");
            }
            if (!comp.Initialize(id)) { return CompanyActionResult.Refused("RR_Company_ReceiptMismatch"); }
            evidence.Add(new EvidenceRecord { id = id, coordinateId = coordinate.id, caseId = caseRecord.id,
                item = recording, itemLoadId = recording.GetUniqueLoadID(), status = EvidenceStatus.Located });
            if (!caseRecord.evidenceIds.Contains(id)) { caseRecord.evidenceIds.Add(id); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult BeginCompanyProject(string projectId)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            ProjectRecord project = projects.FirstOrDefault(p => p.id == projectId);
            RimroomsProjectDef definition = project == null ? null : DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(project.researchDefName);
            if (definition == null) { return CompanyActionResult.Refused("RR_Research_MissingProject"); }
            if (project.insightCommitted || project.completed) { return CompanyActionResult.Existing(); }
            if (ActiveProject != null) { return CompanyActionResult.Refused("RR_Research_ProjectAlreadyActive"); }
            if (researchInsights < definition.insightCost) { return CompanyActionResult.Refused("RR_Research_NeedsInsight"); }
            researchInsights -= definition.insightCost;
            project.insightCommitted = true;
            project.insightOperationId = project.id + ":insight";
            RecordEvent("RR_Event_ProjectStarted", project.id, definition.LabelCap.ToString());
            return CompanyActionResult.Applied();
        }

        internal bool CanAnalyze(EvidenceRecord record, Pawn analyst, Thing bench)
        {
            return CanOperate && record != null && record.status == EvidenceStatus.Secured && record.analyzedTick < 0 &&
                record.routeRecorded && record.distortionRecorded && record.item != null &&
                !record.item.Destroyed && record.item.MapHeld == headquarters && HasSecuredEvidenceCase(record) &&
                record.item.TryGetComp<CompRouteEvidence>()?.EvidenceId == record.id &&
                LaboratoryUtility.CanWork(analyst, bench, this, 4);
        }

        internal CompanyActionResult AddAnalysisWork(EvidenceRecord record, Pawn analyst, Thing bench, float work)
        {
            if (!CanAnalyze(record, analyst, bench) || !LaboratoryUtility.IsAtBench(analyst, bench) ||
                analyst.carryTracker.CarriedThing != record.item || !PositiveFinite(work))
            { return CompanyActionResult.Refused("RR_Evidence_NotReady"); }
            CompRouteEvidence comp = record.item.TryGetComp<CompRouteEvidence>();
            record.analysisWork = Math.Min(comp.WorkRequired, record.analysisWork + work);
            if (record.analysisWork < comp.WorkRequired) { return CompanyActionResult.Applied(); }
            if (researchInsights == int.MaxValue) { return CompanyActionResult.Refused("RR_Company_InvalidAmount"); }
            record.FreezeAnalysisReport(analyst, Find.TickManager.TicksGame);
            record.analyst = analyst;
            record.analyzedTick = Find.TickManager.TicksGame;
            record.status = EvidenceStatus.Analyzed;
            researchInsights++;
            RecordEvent("RR_Event_EvidenceAnalyzed", record.id, analyst.LabelShortCap.ToString());
            UpdateEvidenceAndContracts();
            // The evidence record itself is the once-only insight receipt. Contract settlement is retriable independently.
            return CompanyActionResult.Applied();
        }

        internal CompanyActionResult AddProjectWork(ProjectRecord project, Pawn researcher, Thing bench, float work)
        {
            RimroomsProjectDef definition = project == null ? null : DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(project.researchDefName);
            if (!CanOperate || project != ActiveProject || definition == null || !PositiveFinite(work) ||
                !LaboratoryUtility.CanWork(researcher, bench, this, definition.minimumIntellectual) || !LaboratoryUtility.IsAtBench(researcher, bench))
            { return CompanyActionResult.Refused("RR_Research_NotReady"); }
            project.workDone = Math.Min(definition.workRequired, project.workDone + work);
            if (project.workDone >= definition.workRequired)
            {
                project.completed = true;
                RecordEvent("RR_Event_ProjectCompleted", project.id, definition.LabelCap.ToString());
                Messages.Message("RR_Event_ProjectCompleted".Translate(definition.LabelCap), MessageTypeDefOf.PositiveEvent);
            }
            return CompanyActionResult.Applied();
        }

        private static bool PositiveFinite(float value) { return value > 0f && !float.IsNaN(value) && !float.IsInfinity(value); }
    }
}
