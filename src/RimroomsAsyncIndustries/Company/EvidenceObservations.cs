using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Generation;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public static class EvidenceObservationKinds
    {
        public const string RoomSurvey = "room_survey";
        public const string RouteMismatch = "route_mismatch";
        public const string RecorderGap = "recorder_gap";
        public const string EntitySighting = "entity_sighting";
    }

    /// <summary>A saved, witnessed fact associated with one physical route recording.</summary>
    public sealed class EvidenceObservationRecord : IExposable
    {
        internal string id;
        internal string kind;
        internal int roomIndex = -1;
        internal int referencedRoomIndex = -1;
        internal int markerNumber;
        internal int witnessRoomIndex = -1;
        internal int tick = -1;
        internal Pawn witness;
        internal string witnessLoadId;
        internal string witnessName;
        internal Thing recorder;
        internal string recorderLoadId;
        internal Pawn recorderCarrier;
        internal string recorderCarrierLoadId;
        internal string recorderCarrierName;

        public string Id { get { return id; } }
        public string Kind { get { return kind; } }
        public int RoomIndex { get { return roomIndex; } }
        public int ReferencedRoomIndex { get { return referencedRoomIndex; } }
        public int MarkerNumber { get { return markerNumber; } }
        public int WitnessRoomIndex { get { return witnessRoomIndex; } }
        public int Tick { get { return tick; } }
        public Pawn Witness { get { return witness; } }
        public string WitnessLoadId { get { return witnessLoadId; } }
        public string WitnessName { get { return witnessName; } }
        public Thing Recorder { get { return recorder; } }
        public string RecorderLoadId { get { return recorderLoadId; } }
        public Pawn RecorderCarrier { get { return recorderCarrier; } }
        public string RecorderCarrierLoadId { get { return recorderCarrierLoadId; } }
        public string RecorderCarrierName { get { return recorderCarrierName; } }

        internal static string StableId(string evidenceId, string observationKind, int observedRoom)
        {
            return observationKind == EvidenceObservationKinds.RoomSurvey
                ? evidenceId + ":observation:" + observationKind + ":" + observedRoom
                : evidenceId + ":observation:" + observationKind;
        }

        internal bool SameFact(string observationKind, int observedRoom, int referencedRoom, int marker, int witnessRoomValue)
        {
            return kind == observationKind && roomIndex == observedRoom &&
                referencedRoomIndex == referencedRoom && markerNumber == marker && witnessRoomIndex == witnessRoomValue;
        }

        internal bool SameSnapshot(EvidenceObservationRecord other)
        {
            return other != null && id == other.id && kind == other.kind && roomIndex == other.roomIndex &&
                referencedRoomIndex == other.referencedRoomIndex && markerNumber == other.markerNumber &&
                witnessRoomIndex == other.witnessRoomIndex && tick == other.tick &&
                witnessLoadId == other.witnessLoadId && witnessName == other.witnessName &&
                recorderLoadId == other.recorderLoadId && recorderCarrierLoadId == other.recorderCarrierLoadId &&
                recorderCarrierName == other.recorderCarrierName;
        }

        internal EvidenceObservationRecord SnapshotCopy()
        {
            return new EvidenceObservationRecord
            {
                id = id,
                kind = kind,
                roomIndex = roomIndex,
                referencedRoomIndex = referencedRoomIndex,
                markerNumber = markerNumber,
                witnessRoomIndex = witnessRoomIndex,
                tick = tick,
                witness = witness,
                witnessLoadId = witnessLoadId,
                witnessName = witnessName,
                recorder = recorder,
                recorderLoadId = recorderLoadId,
                recorderCarrier = recorderCarrier,
                recorderCarrierLoadId = recorderCarrierLoadId,
                recorderCarrierName = recorderCarrierName
            };
        }

        internal bool IsValidFor(string evidenceId, IReadOnlyList<RoomRecord> rooms)
        {
            if (string.IsNullOrWhiteSpace(evidenceId) || id != StableId(evidenceId, kind, roomIndex) ||
                tick < 0 || roomIndex < 0 || witnessRoomIndex < 0 ||
                string.IsNullOrWhiteSpace(witnessLoadId) || string.IsNullOrWhiteSpace(witnessName) ||
                string.IsNullOrWhiteSpace(recorderLoadId) || string.IsNullOrWhiteSpace(recorderCarrierLoadId) ||
                string.IsNullOrWhiteSpace(recorderCarrierName) || rooms == null ||
                !rooms.Any(r => r != null && r.index == roomIndex) ||
                !rooms.Any(r => r != null && r.index == witnessRoomIndex)) { return false; }

            switch (kind)
            {
                case EvidenceObservationKinds.RoomSurvey:
                    return referencedRoomIndex == -1 && markerNumber == 0 && witnessRoomIndex == roomIndex;
                case EvidenceObservationKinds.RouteMismatch:
                case EvidenceObservationKinds.RecorderGap:
                    return referencedRoomIndex >= 0 && referencedRoomIndex != roomIndex && markerNumber > 0 &&
                        rooms.Any(r => r != null && r.index == referencedRoomIndex);
                case EvidenceObservationKinds.EntitySighting:
                    return referencedRoomIndex == witnessRoomIndex && markerNumber == 0;
                default:
                    return false;
            }
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref kind, "rr_kind");
            Scribe_Values.Look(ref roomIndex, "rr_roomIndex", -1);
            Scribe_Values.Look(ref referencedRoomIndex, "rr_referencedRoomIndex", -1);
            Scribe_Values.Look(ref markerNumber, "rr_markerNumber");
            Scribe_Values.Look(ref witnessRoomIndex, "rr_witnessRoomIndex", -1);
            Scribe_Values.Look(ref tick, "rr_tick", -1);
            Scribe_References.Look(ref witness, "rr_witness");
            Scribe_Values.Look(ref witnessLoadId, "rr_witnessLoadId");
            Scribe_Values.Look(ref witnessName, "rr_witnessName");
            Scribe_References.Look(ref recorder, "rr_recorder");
            Scribe_Values.Look(ref recorderLoadId, "rr_recorderLoadId");
            Scribe_References.Look(ref recorderCarrier, "rr_recorderCarrier");
            Scribe_Values.Look(ref recorderCarrierLoadId, "rr_recorderCarrierLoadId");
            Scribe_Values.Look(ref recorderCarrierName, "rr_recorderCarrierName");
        }
    }

    /// <summary>Immutable copy of the observations available when analysis completed.</summary>
    public sealed class EvidenceAnalysisReport : IExposable
    {
        internal List<EvidenceObservationRecord> observations = new List<EvidenceObservationRecord>();
        internal Pawn analyst;
        internal string analystLoadId;
        internal string analystName;
        internal int completedTick = -1;
        internal bool detailsUnavailable;
        internal bool legacyDetailsUnavailable;

        public IReadOnlyList<EvidenceObservationRecord> Observations { get { return observations; } }
        public Pawn Analyst { get { return analyst; } }
        public string AnalystLoadId { get { return analystLoadId; } }
        public string AnalystName { get { return analystName; } }
        public int CompletedTick { get { return completedTick; } }
        public bool DetailsUnavailable { get { return detailsUnavailable; } }
        public bool LegacyDetailsUnavailable { get { return legacyDetailsUnavailable; } }

        internal bool IsValidFor(EvidenceRecord evidenceRecord, IReadOnlyList<RoomRecord> rooms)
        {
            if (evidenceRecord == null || completedTick < 0 || completedTick != evidenceRecord.analyzedTick ||
                string.IsNullOrWhiteSpace(analystLoadId) || string.IsNullOrWhiteSpace(analystName) ||
                observations == null || detailsUnavailable != (observations.Count == 0) ||
                (legacyDetailsUnavailable && observations.Count != 0)) { return false; }
            if (observations.Select(o => o == null ? null : o.id).Distinct(StringComparer.Ordinal).Count() != observations.Count ||
                observations.Any(o => o == null || !o.IsValidFor(evidenceRecord.id, rooms)) ||
                evidenceRecord.observations == null || observations.Count != evidenceRecord.observations.Count) { return false; }
            return observations.All(snapshot => evidenceRecord.observations.Any(current => current != null && snapshot.SameSnapshot(current)));
        }

        internal static EvidenceAnalysisReport Capture(IEnumerable<EvidenceObservationRecord> source,
            Pawn completingAnalyst, int tick, bool legacyUnavailable)
        {
            List<EvidenceObservationRecord> snapshot = (source ?? Enumerable.Empty<EvidenceObservationRecord>())
                .Where(o => o != null).Select(o => o.SnapshotCopy()).ToList();
            return new EvidenceAnalysisReport
            {
                observations = snapshot,
                analyst = completingAnalyst,
                analystLoadId = completingAnalyst == null ? "rr-legacy-unknown-analyst" : completingAnalyst.GetUniqueLoadID(),
                analystName = completingAnalyst == null ? "Unknown analyst" : completingAnalyst.LabelShortCap.ToString(),
                completedTick = tick,
                detailsUnavailable = snapshot.Count == 0,
                legacyDetailsUnavailable = legacyUnavailable
            };
        }

        internal static EvidenceAnalysisReport LegacyUnavailable(Pawn completingAnalyst, int tick)
        {
            return Capture(null, completingAnalyst, tick, true);
        }

        public void ExposeData()
        {
            Scribe_Collections.Look(ref observations, "rr_observations", LookMode.Deep);
            Scribe_References.Look(ref analyst, "rr_analyst");
            Scribe_Values.Look(ref analystLoadId, "rr_analystLoadId");
            Scribe_Values.Look(ref analystName, "rr_analystName");
            Scribe_Values.Look(ref completedTick, "rr_completedTick", -1);
            Scribe_Values.Look(ref detailsUnavailable, "rr_detailsUnavailable");
            Scribe_Values.Look(ref legacyDetailsUnavailable, "rr_legacyDetailsUnavailable");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && observations == null)
            { observations = new List<EvidenceObservationRecord>(); }
        }
    }

    public sealed partial class RimroomsCampaignComponent
    {
        private static readonly string[] RequiredSurveyFamilies =
        {
            "threshold_room", "survey_lobby", "office_copy", "service_passage", "borrowed_corridor", "return_gallery"
        };

        /// <summary>
        /// Records only a witnessed field fact while a real expedition member carries the
        /// physical recorder on this coordinate. Tick and recorder custody are captured here.
        /// roomIndex is the surveyed/tag/entity room; route mismatch/gap referencedRoomIndex is
        /// the tag's recorded junction; entity sighting referencedRoomIndex is the witness room.
        /// </summary>
        public CompanyActionResult RecordFieldObservation(EvidenceRecord record, string kind,
            int roomIndex, int referencedRoomIndex, int markerNumber, Pawn witness)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            if (record == null || !evidence.Any(e => ReferenceEquals(e, record)) ||
                record.analyzedTick >= 0 || record.analysisReport != null || record.item == null || record.item.Destroyed ||
                record.status == EvidenceStatus.Missing || record.item.GetUniqueLoadID() != record.itemLoadId ||
                !CompRouteEvidence.IsBoundRouteEvidence(record.item, record.id))
            { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }

            CoordinateRecord coordinate = coordinates.FirstOrDefault(c => c.id == record.coordinateId);
            RimroomsDestinationMapParent site = coordinate == null ? null : coordinate.site as RimroomsDestinationMapParent;
            Map map = site == null ? null : site.Map;
            if (coordinate == null || site == null || !site.LayoutReady || site.CoordinateId != coordinate.id ||
                map == null || record.item.MapHeld != map || coordinate.rooms == null)
            { return CompanyActionResult.Refused("RR_Evidence_SiteUnavailable"); }

            RimroomsExpeditionComponent expeditions = Current.Game == null ? null : Current.Game.GetComponent<RimroomsExpeditionComponent>();
            ExpeditionRecord run = expeditions == null ? null : expeditions.Active;
            bool activeAtSite = run != null && run.CoordinateId == coordinate.id && run.Destination == map &&
                (run.Status == ExpeditionStatus.OnSite || run.Status == ExpeditionStatus.Returning || run.Status == ExpeditionStatus.Stranded);
            bool runWitness = activeAtSite && run.InitialCrew.Concat(run.RescueCrew).Concat(run.RecoveryPassengers).Contains(witness);
            if (!runWitness || witness == null || witness.Dead || witness.Downed || !witness.Spawned ||
                witness.Map != map || witness.Faction != Faction.OfPlayer || witness.inventory == null)
            { return CompanyActionResult.Refused("RR_Evidence_NotReady"); }

            RoomRecord witnessRoom = coordinate.rooms.FirstOrDefault(r => r != null && r.Bounds.Contains(witness.Position));
            RoomRecord observedRoom = coordinate.rooms.FirstOrDefault(r => r != null && r.index == roomIndex);
            if (witnessRoom == null || observedRoom == null)
            { return CompanyActionResult.Refused("RR_Evidence_NotReady"); }

            Thing recorder;
            Pawn recorderCarrier;
            if (!TryFindFieldRecorder(run, map, out recorder, out recorderCarrier))
            { return CompanyActionResult.Refused("RR_Evidence_NotReady"); }

            bool validFact;
            switch (kind)
            {
                case EvidenceObservationKinds.RoomSurvey:
                    validFact = referencedRoomIndex == -1 && markerNumber == 0 &&
                        witnessRoom.index == roomIndex && observedRoom.surveyed;
                    break;
                case EvidenceObservationKinds.RouteMismatch:
                    validFact = witnessRoom.index == roomIndex && HasDisplacedMarker(
                        coordinate, map, roomIndex, referencedRoomIndex, markerNumber);
                    break;
                case EvidenceObservationKinds.RecorderGap:
                    validFact = witnessRoom.index == roomIndex && HasDisplacedMarker(
                        coordinate, map, roomIndex, referencedRoomIndex, markerNumber) &&
                        record.observations.Any(o => o != null && o.kind == EvidenceObservationKinds.RouteMismatch &&
                            o.roomIndex == roomIndex && o.referencedRoomIndex == referencedRoomIndex && o.markerNumber == markerNumber);
                    break;
                case EvidenceObservationKinds.EntitySighting:
                    validFact = referencedRoomIndex == witnessRoom.index && markerNumber == 0 &&
                        HasSpawnedEntityInRoom(map, observedRoom);
                    break;
                default:
                    return CompanyActionResult.Refused("RR_Evidence_NotReady");
            }
            if (!validFact) { return CompanyActionResult.Refused("RR_Evidence_NotReady"); }

            record.observations = record.observations ?? new List<EvidenceObservationRecord>();
            string observationId = EvidenceObservationRecord.StableId(record.id, kind, roomIndex);
            EvidenceObservationRecord prior = record.observations.FirstOrDefault(o => o != null && o.id == observationId);
            if (prior != null)
            {
                return prior.SameFact(kind, roomIndex, referencedRoomIndex, markerNumber, witnessRoom.index)
                    ? CompanyActionResult.Existing() : CompanyActionResult.Refused("RR_Company_ReceiptMismatch");
            }

            record.observationSchemaVersion = EvidenceRecord.CurrentObservationSchemaVersion;
            record.observations.Add(new EvidenceObservationRecord
            {
                id = observationId,
                kind = kind,
                roomIndex = roomIndex,
                referencedRoomIndex = referencedRoomIndex,
                markerNumber = markerNumber,
                witnessRoomIndex = witnessRoom.index,
                tick = Find.TickManager.TicksGame,
                witness = witness,
                witnessLoadId = witness.GetUniqueLoadID(),
                witnessName = witness.LabelShortCap.ToString(),
                recorder = recorder,
                recorderLoadId = recorder.GetUniqueLoadID(),
                recorderCarrier = recorderCarrier,
                recorderCarrierLoadId = recorderCarrier.GetUniqueLoadID(),
                recorderCarrierName = recorderCarrier.LabelShortCap.ToString()
            });

            if (kind == EvidenceObservationKinds.RoomSurvey)
            { RefreshRouteRecorded(record, coordinate); }
            else if (kind == EvidenceObservationKinds.RouteMismatch)
            { record.distortionRecorded = true; }
            else if (kind == EvidenceObservationKinds.EntitySighting)
            { record.entityRecorded = true; }
            return CompanyActionResult.Applied();
        }

        private static bool TryFindFieldRecorder(ExpeditionRecord run, Map map, out Thing recorder, out Pawn carrier)
        {
            recorder = null;
            carrier = null;
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_FieldRecorder");
            if (run == null || map == null || definition == null) { return false; }
            foreach (Pawn member in run.InitialCrew.Concat(run.RescueCrew).Concat(run.RecoveryPassengers))
            {
                if (member == null || member.Dead || member.Destroyed || !member.Spawned || member.Map != map || member.inventory == null) { continue; }
                Thing found = member.inventory.innerContainer.FirstOrDefault(t => !t.Destroyed && t.def == definition && t.stackCount > 0);
                if (found == null) { continue; }
                recorder = found;
                carrier = member;
                return true;
            }
            return false;
        }

        private static bool HasDisplacedMarker(CoordinateRecord coordinate, Map map,
            int observedRoom, int recordedRoom, int markerNumber)
        {
            if (recordedRoom < 0 || recordedRoom == observedRoom || markerNumber <= 0) { return false; }
            foreach (Investigation.CompRimroomsMarker marker in Investigation.CompRimroomsMarker.OnMap(map))
            {
                Thing item = marker.parent;
                if (item.Destroyed || !item.Spawned || item.Map != map ||
                    marker.CoordinateId != coordinate.id || marker.RoomIndex != recordedRoom ||
                    marker.Number != markerNumber) { continue; }
                if (coordinate.rooms.Any(r => r != null && r.index == observedRoom && r.Bounds.Contains(item.Position))) { return true; }
            }
            return false;
        }

        private static bool HasSpawnedEntityInRoom(Map map, RoomRecord room)
        {
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_QuietPursuer");
            return definition != null && map.listerThings.ThingsOfDef(definition).Any(item =>
                !item.Destroyed && item.Spawned && item.Map == map && room.Bounds.Contains(item.Position));
        }

        private static bool ValidObservationState(EvidenceRecord record, CoordinateRecord coordinate)
        {
            if (record == null || coordinate == null || record.observations == null ||
                record.observationSchemaVersion < 0 || record.observationSchemaVersion > EvidenceRecord.CurrentObservationSchemaVersion)
            { return false; }
            if (record.observations.Select(o => o == null ? null : o.id).Distinct(StringComparer.Ordinal).Count() != record.observations.Count ||
                record.observations.Any(o => o == null || !o.IsValidFor(record.id, coordinate.rooms))) { return false; }
            RefreshRouteRecorded(record, coordinate);
            if (record.analyzedTick < 0) { return record.analysisReport == null; }
            return record.analysisReport != null && record.analysisReport.IsValidFor(record, coordinate.rooms);
        }

        private static void RefreshRouteRecorded(EvidenceRecord record, CoordinateRecord coordinate)
        {
            record.routeRecorded = record.legacyRouteRecorded || RequiredSurveyFamilies.All(family =>
            {
                RoomRecord room = coordinate.rooms.FirstOrDefault(r => r != null && r.familyId == family);
                return room != null && record.observations.Any(o => o != null &&
                    o.kind == EvidenceObservationKinds.RoomSurvey && o.roomIndex == room.index);
            });
        }
    }
}
