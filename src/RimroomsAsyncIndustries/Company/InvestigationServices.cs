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
            RimroomsEvidenceCreationComponent creation = Current.Game == null ? null : Current.Game.GetComponent<RimroomsEvidenceCreationComponent>();
            if (creation == null) { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
            CompanyActionResult creationReady = creation.Readiness();
            if (!creationReady.Success) { return creationReady; }
            EvidenceRecord prior = FindEvidence(coordinate.id + ":evidence:route");
            if (prior != null)
            {
                // A missing/destroyed recording remains a loss. Reopening a site must still be possible.
                if (prior.analyzedTick < 0 && (prior.item == null || prior.item.Destroyed)) { prior.status = EvidenceStatus.Missing; }
                return creation.ReconcileRegistered(prior);
            }
            RimroomsDestinationMapParent site = coordinate.site as RimroomsDestinationMapParent;
            Map map = site == null ? null : site.Map;
            if (map == null || !site.LayoutReady || site.CoordinateId != coordinate.id)
            { return CompanyActionResult.Refused("RR_Evidence_SiteUnavailable"); }
            if (!cases.Any(c => c.coordinateId == coordinate.id)) { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
            RoomRecord office = coordinate.rooms.FirstOrDefault(r => r.familyId == "office_copy");
            if (office == null) { return CompanyActionResult.Refused("RR_Evidence_NoSafeSlot"); }
            IntVec3 cell = site.OfficeEvidenceCell;
            if (!cell.IsValid || !office.Bounds.Contains(cell) || !cell.InBounds(map) || !cell.Standable(map))
            { return CompanyActionResult.Refused("RR_Evidence_NoSafeSlot"); }
            string id = coordinate.id + ":evidence:route";
            if (creation.HasAttempt(id)) { return creation.EnsureOriginal(this, coordinate, map, cell); }
            // A normal textbook is never inferred to be evidence. Recover only this bound identity,
            // or an unregistered company route recording left before registration completed. That
            // test was named `IsLegacyCarrier` while `RR_RouteRecording` existed only in old saves;
            // the def ships again as of 0.13.0-dev, so it now also catches a brand new one whose
            // registration was interrupted, which is the same situation and the same right answer.
            var physical = map.listerThings.AllThings.Where(t =>
                t.TryGetComp<CompRouteEvidence>()?.EvidenceId == id || (CompRouteEvidence.IsCompanyCarrier(t) &&
                string.IsNullOrEmpty(t.TryGetComp<CompRouteEvidence>()?.EvidenceId))).ToList();
            if (physical.Count == 1) { return RegisterRouteRecording(coordinate, physical[0]); }
            if (physical.Count > 1) { return CompanyActionResult.Refused("RR_Company_ReceiptMismatch"); }
            return creation.EnsureOriginal(this, coordinate, map, cell);
        }

        public CompanyActionResult RegisterRouteRecording(CoordinateRecord coordinate, Thing recording)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            CompRouteEvidence comp = recording == null ? null : recording.TryGetComp<CompRouteEvidence>();
            CaseRecord caseRecord = coordinate == null ? null : cases.FirstOrDefault(c => c.coordinateId == coordinate.id);
            if (coordinate == null || !coordinates.Contains(coordinate) || caseRecord == null || comp == null ||
                !CompRouteEvidence.IsSupportedCarrier(recording))
            { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
            string id = coordinate.id + ":evidence:route";
            EvidenceRecord existing = FindEvidence(id);
            if (existing != null)
            {
                return existing.item == recording && existing.itemLoadId == recording.GetUniqueLoadID() &&
                    CompRouteEvidence.IsBoundRouteEvidence(recording, id) ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Company_ReceiptMismatch");
            }
            if (coordinate.site == null || !recording.Spawned || recording.Map != coordinate.site.Map ||
                !recording.Map.listerThings.AllThings.Contains(recording) ||
                !recording.Position.GetThingList(recording.Map).Contains(recording) ||
                evidence.Any(e => e.item == recording || e.itemLoadId == recording.GetUniqueLoadID()) ||
                (recording is Book book && (string.IsNullOrWhiteSpace(book.Title) || book.BookComp == null)))
            { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
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
            string qualification = ProjectQualificationFailureKey(definition);
            if (qualification != null) { return CompanyActionResult.Refused(qualification); }
            if (researchInsights < definition.insightCost) { return CompanyActionResult.Refused("RR_Research_NeedsInsight"); }
            researchInsights -= definition.insightCost;
            project.insightCommitted = true;
            project.insightOperationId = project.id + ":insight";
            RecordEvent("RR_Event_ProjectStarted", project.id, definition.LabelCap.ToString());
            return CompanyActionResult.Applied();
        }


        /// <summary>
        /// Whether this branch has learned enough to attempt a project, or null if it has.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"u need certain logs complete to operate
        /// the higher teri techs and shit and gate features and upgrades"*.
        ///
        /// Checked **before** insight is spent, so a branch that is short of logs is told so
        /// rather than being charged and then refused. Separate from the cost for the same reason
        /// every other check in this mod is split: a qualification and a price are two different
        /// questions, and merging them hides which one failed.
        /// </summary>
        public string ProjectQualificationFailureKey(RimroomsProjectDef definition)
        {
            if (definition == null) { return "RR_Research_MissingProject"; }

            if (definition.prerequisiteProjects != null)
            {
                for (int index = 0; index < definition.prerequisiteProjects.Count; index++)
                {
                    string required = definition.prerequisiteProjects[index];
                    if (string.IsNullOrWhiteSpace(required)) { continue; }
                    if (!projects.Any(p => p != null && p.Completed && p.ResearchDefName == required))
                    { return "RR_Research_NeedsPrerequisite"; }
                }
            }

            if (CompletedLogCount(LogKind.Route) < definition.requiredRouteLogs)
            { return "RR_Research_NeedsRouteLogs"; }
            if (CompletedLogCount(LogKind.Distortion) < definition.requiredDistortionLogs)
            { return "RR_Research_NeedsDistortionLogs"; }
            if (CompletedLogCount(LogKind.Entity) < definition.requiredEntityLogs)
            { return "RR_Research_NeedsEntityLogs"; }
            return null;
        }

        /// <summary>The three kinds of log an analysed record can carry.</summary>
        public enum LogKind { Route = 0, Distortion = 1, Entity = 2 }

        /// <summary>
        /// Completed logs of one kind across the whole branch.
        ///
        /// **Only `Analyzed` records count.** A record that was carried home and never put through
        /// a bench is recovered evidence, not a completed log, and the owner's word was
        /// *"complete"*. A record that later goes `Missing` keeps its analysed tick, so a log that
        /// was completed stays completed even if the book itself burns — which is the same
        /// once-only rule the insight award already follows.
        /// </summary>
        public int CompletedLogCount(LogKind kind)
        {
            int count = 0;
            for (int index = 0; index < evidence.Count; index++)
            {
                EvidenceRecord record = evidence[index];
                if (record == null || record.analyzedTick < 0) { continue; }
                bool carries = kind == LogKind.Route ? record.RouteRecorded
                    : kind == LogKind.Distortion ? record.DistortionRecorded
                    : record.EntityRecorded;
                if (carries) { count++; }
            }
            return count;
        }

        /// <summary>
        /// Whether this analyst may analyse this record at this bench.
        ///
        /// **Custody is the archive OR the analyst's own hands, and it used to be the archive
        /// only.** `JobDriver_CompanyLaboratory` picks the record up and carries it to the bench,
        /// as a researcher would, and then asks this every tick of work. Asked of a record in the
        /// analyst's hands, "is it filed on an archive shelf?" is always no -- so the first tick
        /// refused, the job ended incompletable, the book was dropped beside the bench as
        /// *Recovered*, and analysis never once moved off 0 %. Found playing, 2026-10-07, with the
        /// AI-01 record secured, both required observations recorded, a designated bench and a
        /// researcher at it.
        ///
        /// **The filing rule is unchanged where it decides anything.** The work giver asks this
        /// before the record is picked up, when only the archive branch can be true, so a record
        /// still has to have been filed before anybody may start on it.
        /// </summary>
        internal bool CanAnalyze(EvidenceRecord record, Pawn analyst, Thing bench)
        {
            if (!CanOperate || record == null || record.analyzedTick >= 0 || !record.routeRecorded ||
                !record.distortionRecorded || record.item == null || record.item.Destroyed ||
                record.item.MapHeld != headquarters || record.item.GetUniqueLoadID() != record.itemLoadId ||
                !CompRouteEvidence.IsBoundRouteEvidence(record.item, record.id) ||
                !LaboratoryUtility.CanWork(analyst, bench, this, 4))
            { return false; }
            bool filed = record.status == EvidenceStatus.Secured && HasArchivedCustody(record);
            bool inAnalystsHands = analyst.carryTracker != null && analyst.carryTracker.CarriedThing == record.item;
            return filed || inAnalystsHands;
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
            // **RR_Cap_SecondReading** (Measurement and evidence, tier 0). A branch that has
            // learned to read its own records twice gets more out of each one. Guarded against
            // the same overflow the single award above is.
            if (HasCapability("RR_Cap_SecondReading") && researchInsights < int.MaxValue)
            { researchInsights++; }
            RecordEvent("RR_Event_EvidenceAnalyzed", record.id, analyst.LabelShortCap.ToString());
            // **`RR_AnalysisComplete` is played here, and it shipped with no consumer for a version.**
            // The brief's own words: *"A researcher finishes analysing a finding"*. After the record,
            // so a cue is never the only evidence that the work completed.
            if (analyst.Spawned && analyst.Map != null)
            { Audio.RimroomsAudio.Play("RR_AnalysisComplete", analyst.Map, analyst.Position, true); }
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
                // A capability is only real once the project that grants it is done.
                RebuildCapabilities();
                RecordEvent("RR_Event_ProjectCompleted", project.id, definition.LabelCap.ToString());
                Messages.Message("RR_Event_ProjectCompleted".Translate(definition.LabelCap), MessageTypeDefOf.PositiveEvent);
            }
            return CompanyActionResult.Applied();
        }

        private static bool PositiveFinite(float value) { return value > 0f && !float.IsNaN(value) && !float.IsInfinity(value); }
    }
}
