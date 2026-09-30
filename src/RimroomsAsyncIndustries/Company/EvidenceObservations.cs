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

    /// <summary>
    /// A second crew member's account of a fact somebody has already filed.
    ///
    /// **This is the thing that was being thrown away.** `StableId` is per-room only for a room
    /// survey, so an evidence record could hold exactly one route mismatch, one recorder gap and
    /// one entity sighting — and therefore exactly **one witness** each. Meanwhile
    /// `RecordEncounterObservations` loops over *every* present crew member, so the second one's
    /// account was either silently merged into the first (identical facts) or silently refused as
    /// a receipt mismatch (different facts), and the site tick ignores the result either way.
    ///
    /// The chart asks request 5 for *"two crew accounts of the same room"*. Two crew in the same
    /// room could never both be recorded, so that request was only ever satisfiable across two
    /// separate coordinates.
    ///
    /// An account that <see cref="agrees"/> is corroboration. One that does not is a
    /// **contradictory account**, which is the prep material's own words and opens a dispute.
    /// </summary>
    public sealed class WitnessAccountRecord : IExposable
    {
        internal Pawn witness;
        internal string witnessLoadId;
        internal string witnessName;
        internal int witnessRoomIndex = -1;
        internal int referencedRoomIndex = -1;
        internal int markerNumber;
        internal int tick = -1;
        internal bool agrees;

        public Pawn Witness { get { return witness; } }
        public string WitnessLoadId { get { return witnessLoadId; } }
        public string WitnessName { get { return witnessName; } }
        public int WitnessRoomIndex { get { return witnessRoomIndex; } }
        public int ReferencedRoomIndex { get { return referencedRoomIndex; } }
        public int MarkerNumber { get { return markerNumber; } }
        public int Tick { get { return tick; } }
        public bool Agrees { get { return agrees; } }

        internal WitnessAccountRecord SnapshotCopy()
        {
            return new WitnessAccountRecord
            {
                witness = witness,
                witnessLoadId = witnessLoadId,
                witnessName = witnessName,
                witnessRoomIndex = witnessRoomIndex,
                referencedRoomIndex = referencedRoomIndex,
                markerNumber = markerNumber,
                tick = tick,
                agrees = agrees
            };
        }

        internal bool SameSnapshot(WitnessAccountRecord other)
        {
            return other != null && witnessLoadId == other.witnessLoadId && witnessName == other.witnessName &&
                witnessRoomIndex == other.witnessRoomIndex && referencedRoomIndex == other.referencedRoomIndex &&
                markerNumber == other.markerNumber && tick == other.tick && agrees == other.agrees;
        }

        internal bool IsValidFor(IReadOnlyList<RoomRecord> rooms)
        {
            return tick >= 0 && witnessRoomIndex >= 0 && !string.IsNullOrWhiteSpace(witnessLoadId) &&
                !string.IsNullOrWhiteSpace(witnessName) && rooms != null &&
                rooms.Any(r => r != null && r.index == witnessRoomIndex);
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref witness, "rr_witness");
            Scribe_Values.Look(ref witnessLoadId, "rr_witnessLoadId");
            Scribe_Values.Look(ref witnessName, "rr_witnessName");
            Scribe_Values.Look(ref witnessRoomIndex, "rr_witnessRoomIndex", -1);
            Scribe_Values.Look(ref referencedRoomIndex, "rr_referencedRoomIndex", -1);
            Scribe_Values.Look(ref markerNumber, "rr_markerNumber");
            Scribe_Values.Look(ref tick, "rr_tick", -1);
            Scribe_Values.Look(ref agrees, "rr_agrees");
        }
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
        // Additive. An old save has no accounts, which is TRUE of it -- nobody was recording them.
        // No version bump: the existing observationSchemaVersion distinguishes "booleans predate
        // structured observations", and its own comment forbids synthesizing rows from them. An
        // empty accounts list needs no such distinction, because empty is the honest answer.
        internal List<WitnessAccountRecord> accounts = new List<WitnessAccountRecord>();

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
        public IReadOnlyList<WitnessAccountRecord> Accounts { get { return accounts; } }

        /// <summary>Somebody who was there says it did not happen the way it is filed.</summary>
        public bool Disputed { get { return accounts != null && accounts.Any(a => a != null && !a.agrees); } }

        /// <summary>
        /// Every distinct crew member whose account this fact carries, filed one plus corroborating
        /// and disputing ones. A dispute still counts as an account: somebody was there and said
        /// something, and a corporation that discards testimony because it is inconvenient is not
        /// what this campaign is about.
        /// </summary>
        internal IEnumerable<string> WitnessLoadIds
        {
            get
            {
                if (!string.IsNullOrEmpty(witnessLoadId)) { yield return witnessLoadId; }
                if (accounts == null) { yield break; }
                foreach (WitnessAccountRecord account in accounts)
                {
                    if (account != null && !string.IsNullOrEmpty(account.witnessLoadId))
                    { yield return account.witnessLoadId; }
                }
            }
        }

        /// <summary>
        /// File a second crew member's account of this same fact.
        ///
        /// Refuses a witness who is already on the record -- including the one who filed it --
        /// because the same person saying the same thing twice is not a second account, and
        /// `LivingWitnessCount` counts distinct people. A crew of two standing in one room ticks
        /// every fifteen ticks; without this the account list would grow without bound.
        /// </summary>
        internal bool AddAccount(Pawn accountWitness, int witnessRoom, int referencedRoom,
            int marker, int atTick, bool matchesFiledFact)
        {
            if (accountWitness == null || atTick < 0 || witnessRoom < 0) { return false; }
            accounts = accounts ?? new List<WitnessAccountRecord>();
            string loadId = accountWitness.GetUniqueLoadID();
            if (string.IsNullOrEmpty(loadId)) { return false; }
            foreach (string existing in WitnessLoadIds)
            {
                if (string.Equals(existing, loadId, StringComparison.Ordinal)) { return false; }
            }
            accounts.Add(new WitnessAccountRecord
            {
                witness = accountWitness,
                witnessLoadId = loadId,
                witnessName = accountWitness.LabelShortCap.ToString(),
                witnessRoomIndex = witnessRoom,
                referencedRoomIndex = referencedRoom,
                markerNumber = marker,
                tick = atTick,
                agrees = matchesFiledFact
            });
            return true;
        }

        internal static string StableId(string evidenceId, string observationKind, int observedRoom)
        {
            return observationKind == EvidenceObservationKinds.RoomSurvey
                ? evidenceId + ":observation:" + observationKind + ":" + observedRoom
                : evidenceId + ":observation:" + observationKind;
        }

        /// <summary>
        /// Accounts compared in order, because they are appended in the order they were given and
        /// a report snapshot is a copy of that same list. Order-insensitive comparison here would
        /// hide a reordering, and reordering testimony is exactly the kind of thing this record
        /// exists to make impossible.
        /// </summary>
        private bool SameAccounts(EvidenceObservationRecord other)
        {
            List<WitnessAccountRecord> mine = accounts ?? new List<WitnessAccountRecord>();
            List<WitnessAccountRecord> theirs = other.accounts ?? new List<WitnessAccountRecord>();
            if (mine.Count != theirs.Count) { return false; }
            for (int index = 0; index < mine.Count; index++)
            {
                if (mine[index] == null || !mine[index].SameSnapshot(theirs[index])) { return false; }
            }
            return true;
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
                recorderCarrierName == other.recorderCarrierName && SameAccounts(other);
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
                recorderCarrierName = recorderCarrierName,
                accounts = (accounts ?? new List<WitnessAccountRecord>())
                    .Where(a => a != null).Select(a => a.SnapshotCopy()).ToList()
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

            // Accounts are validated as strictly as the fact they attach to, and every witness on
            // the record has to be a different person. A duplicate would inflate
            // LivingWitnessCount, which is what decides whether a Testify route has been satisfied
            // -- so a repeated name would be a request paying out on one person's word twice.
            List<WitnessAccountRecord> filed = accounts ?? new List<WitnessAccountRecord>();
            if (filed.Any(a => a == null || !a.IsValidFor(rooms))) { return false; }
            List<string> speakers = WitnessLoadIds.ToList();
            if (speakers.Distinct(StringComparer.Ordinal).Count() != speakers.Count) { return false; }

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
            Scribe_Collections.Look(ref accounts, "rr_accounts", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && accounts == null)
            { accounts = new List<WitnessAccountRecord>(); }
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
            if (!TryFindRecordBook(run, map, record, out recorder, out recorderCarrier))
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
            // A fact somebody has already filed, and a second crew member who was also there.
            //
            // This used to be the end of the road. An identical account returned Existing() and
            // vanished; a DIFFERENT account was refused as a receipt mismatch and also vanished,
            // and since the site tick ignores the result, a contradiction between two crew in the
            // same room left no trace anywhere. The prep material asks for exactly that
            // contradiction, and the chart asks request 5 for "two crew accounts of the same room".
            //
            // Both are now filed as accounts. Agreement is corroboration and disagreement is a
            // dispute; neither is discarded, and a witness already on the record is not added
            // twice -- a crew standing still ticks every fifteen ticks.
            if (prior != null)
            {
                bool agrees = prior.SameFact(kind, roomIndex, referencedRoomIndex, markerNumber, witnessRoom.index);
                bool added = prior.AddAccount(witness, witnessRoom.index, referencedRoomIndex,
                    markerNumber, Find.TickManager.TicksGame, agrees);
                if (added) { record.observationSchemaVersion = EvidenceRecord.CurrentObservationSchemaVersion; }
                return added ? CompanyActionResult.Applied() : CompanyActionResult.Existing();
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

        /// <summary>
        /// The record this observation is written into, and the crew member writing in it.
        ///
        /// Until 0.12.24-dev this looked for a <i>second</i> object -- a field recorder somewhere
        /// in the crew's inventories -- and attributed the observation to that. It was always
        /// redundant: by the time this runs the caller has already established that
        /// <c>record.item</c> is a bound route-evidence book held on this map. So the record and
        /// the thing recording it were two objects that could get separated, which is exactly
        /// what the 0.9.9-dev plan said they should stop being.
        ///
        /// **The book has to be in a crew member's inventory.** A book lying on the floor two
        /// rooms back is not being written in. That is the same discipline the recorder's own
        /// inventory check enforced -- and it closes a disagreement between two gates that had
        /// never agreed: surveying needed the recorder <i>carried</i>, while the observation
        /// needed the book merely somewhere on the map.
        /// </summary>
        private static bool TryFindRecordBook(ExpeditionRecord run, Map map, EvidenceRecord record,
            out Thing book, out Pawn carrier)
        {
            book = null;
            carrier = null;
            if (run == null || map == null || record == null || record.item == null || record.item.Destroyed ||
                !CompRouteEvidence.IsSupportedCarrier(record.item)) { return false; }
            foreach (Pawn member in run.InitialCrew.Concat(run.RescueCrew).Concat(run.RecoveryPassengers))
            {
                if (member == null || member.Dead || member.Destroyed || !member.Spawned || member.Map != map ||
                    member.inventory == null || !member.inventory.innerContainer.Contains(record.item)) { continue; }
                book = record.item;
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
