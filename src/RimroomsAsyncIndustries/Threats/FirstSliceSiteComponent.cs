using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Investigation;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Threats
{
    // Site-owned observations survive gate closure. Opening-specific encounter state is never held by UI.
    public sealed partial class FirstSliceSiteComponent : MapComponent, IThingHolder
    {
        private string openingId;
        private List<Pawn> crew = new List<Pawn>();
        private List<CrewRouteRecord> crewRoutes = new List<CrewRouteRecord>();
        private ThingOwner<Thing> deploymentRecovery;
        private bool unmarkedWarningSent;
        private int nextMarkerNumber = 1;
        private int lastValidatedRoom = -1;
        private bool distortionWarned;
        private bool distortionResolved;
        private int distortionWarningTick;
        private Pawn distortionPawn;
        private IntVec3 distortionWarningCell;
        private bool distortionTimeSpent;
        private Thing_QuietPursuer pursuer;
        private bool pursuerEncounterStarted;
        private bool pursuerWithdrawn;
        private int pursuerRoom = -1;
        private int advances;
        private int nextAdvanceTick;
        private int contactWarningTick = -1;
        private Pawn contactPawn;
        private int lastLoudTick = -1;
        private int lastObservedCrewRoom = -1;
        private bool attemptedStrike;

        public FirstSliceSiteComponent(Map map) : base(map) { deploymentRecovery = new ThingOwner<Thing>(this); }
        public IThingHolder ParentHolder { get { return null; } }
        public ThingOwner GetDirectlyHeldThings() { return deploymentRecovery; }
        public void GetChildHolders(List<IThingHolder> outChildren) { ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, deploymentRecovery); }
        public int DeploymentRecoveryCount { get { return deploymentRecovery.Count; } }
        private RimroomsCampaignComponent Campaign { get { return Current.Game?.GetComponent<RimroomsCampaignComponent>(); } }
        public CoordinateRecord Coordinate { get { return Campaign?.Coordinates.FirstOrDefault(c => c.Site?.Map == map); } }
        public string OpeningId { get { return openingId; } }
        public bool DistortionObserved { get { return distortionWarned; } }
        public bool EntityObserved { get { return pursuerEncounterStarted; } }
        public int LastSeenPursuerRoom { get { return pursuerRoom; } }
        public bool PursuerWithdrawn { get { return pursuerWithdrawn; } }

        public void BeginOpening(string expeditionId, List<Pawn> originalCrew)
        {
            if (string.IsNullOrEmpty(expeditionId) || openingId == expeditionId) { return; }
            WithdrawPursuer(false);
            openingId = expeditionId;
            crew = originalCrew == null ? new List<Pawn>() : originalCrew.Where(p => p != null).Distinct().ToList();
            crewRoutes.Clear(); unmarkedWarningSent = false;
            lastValidatedRoom = -1;
            distortionWarned = false; distortionResolved = false; distortionTimeSpent = false;
            distortionPawn = null; distortionWarningCell = IntVec3.Invalid;
            pursuerEncounterStarted = false; pursuerWithdrawn = false; pursuerRoom = -1;
            advances = 0; nextAdvanceTick = 0; contactWarningTick = -1; lastLoudTick = Find.TickManager.TicksGame;
            lastObservedCrewRoom = -1; attemptedStrike = false;
            contactPawn = null;
        }
        public void AddReliefPawn(Pawn pawn) { if (pawn != null && !crew.Contains(pawn)) { crew.Add(pawn); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref openingId, "rr_openingId");
            Scribe_Collections.Look(ref crew, "rr_crew", LookMode.Reference);
            Scribe_Collections.Look(ref crewRoutes, "rr_crewRoutes", LookMode.Deep);
            Scribe_Deep.Look(ref deploymentRecovery, "rr_deploymentRecovery", this);
            Scribe_Values.Look(ref unmarkedWarningSent, "rr_unmarkedWarningSent");
            Scribe_Values.Look(ref nextMarkerNumber, "rr_nextMarkerNumber", 1);
            Scribe_Values.Look(ref lastValidatedRoom, "rr_lastValidatedRoom", -1);
            Scribe_Values.Look(ref distortionWarned, "rr_distortionWarned");
            Scribe_Values.Look(ref distortionResolved, "rr_distortionResolved");
            Scribe_Values.Look(ref distortionWarningTick, "rr_distortionWarningTick");
            Scribe_References.Look(ref distortionPawn, "rr_distortionPawn");
            Scribe_Values.Look(ref distortionWarningCell, "rr_distortionWarningCell");
            Scribe_Values.Look(ref distortionTimeSpent, "rr_distortionTimeSpent");
            Scribe_References.Look(ref pursuer, "rr_pursuer");
            Scribe_Values.Look(ref pursuerEncounterStarted, "rr_pursuerEncounterStarted");
            Scribe_Values.Look(ref pursuerWithdrawn, "rr_pursuerWithdrawn");
            Scribe_Values.Look(ref pursuerRoom, "rr_pursuerRoom", -1);
            Scribe_Values.Look(ref advances, "rr_advances");
            Scribe_Values.Look(ref nextAdvanceTick, "rr_nextAdvanceTick");
            Scribe_Values.Look(ref contactWarningTick, "rr_contactWarningTick", -1);
            Scribe_References.Look(ref contactPawn, "rr_contactPawn");
            Scribe_Values.Look(ref lastLoudTick, "rr_lastLoudTick", -1);
            Scribe_Values.Look(ref lastObservedCrewRoom, "rr_lastObservedCrewRoom", -1);
            Scribe_Values.Look(ref attemptedStrike, "rr_attemptedStrike");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                crew = crew ?? new List<Pawn>(); crewRoutes = crewRoutes ?? new List<CrewRouteRecord>();
                deploymentRecovery = deploymentRecovery ?? new ThingOwner<Thing>(this);
            }
        }

        public override void MapComponentTick()
        {
            using (Core.RimroomsDiagnostics.Measure("site-tick")) { TickSite(); }
        }

        private void TickSite()
        {
            int now = Find.TickManager.TicksGame;
            if (now % 15 != 0 || string.IsNullOrEmpty(openingId)) { return; }
            CoordinateRecord coordinate = Coordinate;
            if (Campaign?.CanOperate != true || coordinate == null || coordinate.Rooms.Count == 0) { return; }
            List<Pawn> present = crew.Where(p => p != null && !p.Dead && p.Spawned && p.Map == map).ToList();
            if (present.Count == 0) { return; }
            bool recording = present.Any(p => HasItem(p, "RR_FieldRecorder"));
            EvidenceRecord record = Campaign.FindEvidence(coordinate.Id + ":evidence:route");
            foreach (Pawn pawn in present)
            {
                RoomRecord room = RoomAt(pawn.Position);
                if (room != null && recording && !room.surveyed)
                {
                    room.surveyed = true;
                    Note("RR_Event_RoomSurveyed", coordinate.Label, (room.index + 1).ToString(), ("RR_Room_" + room.familyId).Translate().ToString());
                }
                if (room != null && recording && record != null && record.Status != EvidenceStatus.Analyzed && !pawn.Downed)
                { Campaign.RecordFieldObservation(record, EvidenceObservationKinds.RoomSurvey, room.Index, -1, 0, pawn); }
            }
            Pawn leader = present.FirstOrDefault(p => !p.Downed && RoomAt(p.Position)?.familyId == "borrowed_corridor")
                ?? present.FirstOrDefault(p => !p.Downed);
            if (leader == null) { return; }
            RoomRecord currentRoom = RoomAt(leader.Position);
            if (currentRoom == null) { return; }
            if (!distortionWarned && currentRoom.familyId == "borrowed_corridor")
            {
                CrewRouteRecord route = crewRoutes.FirstOrDefault(r => r.pawn == leader);
                int previous = route == null ? -1 : route.lastValidatedRoom;
                RoomRecord junction = coordinate.Rooms.FirstOrDefault(r => r.index == previous && r.familyId != "borrowed_corridor")
                    ?? coordinate.Rooms.FirstOrDefault(r => r.familyId == "service_passage");
                if (junction != null)
                {
                    CompRouteAid tag = DeployedAids().FirstOrDefault(a => !a.Beacon && a.RoomIndex == junction.index &&
                        RoomAt(a.parent.Position)?.index == junction.index && !a.parent.def.AffectsRegions);
                    if (tag != null && TryRoomCell(currentRoom, out IntVec3 tagCell) && tagCell.GetFirstItem(map) == null)
                    {
                        tag.parent.Position = tagCell;
                        tag.MarkMismatch();
                        lastValidatedRoom = junction.index;
                        distortionWarned = true; distortionWarningTick = now; distortionPawn = leader; distortionWarningCell = leader.Position;
                        Note("RR_Event_CorridorMismatch", coordinate.Label, (junction.index + 1).ToString());
                        StartPursuer(currentRoom, now);
                    }
                    else if (!unmarkedWarningSent)
                    { unmarkedWarningSent = true; Note("RR_Event_CorridorUnmarked", (junction.index + 1).ToString()); }
                }
            }
            if (distortionWarned && !pursuerEncounterStarted && currentRoom.familyId != "threshold_room")
            { StartPursuer(currentRoom, now); }
            RecordEncounterObservations(record, present, recording);
            foreach (Pawn pawn in present)
            {
                RoomRecord room = RoomAt(pawn.Position);
                if (room == null || room.familyId == "borrowed_corridor") { continue; }
                CrewRouteRecord route = crewRoutes.FirstOrDefault(r => r.pawn == pawn);
                if (route == null) { route = new CrewRouteRecord { pawn = pawn }; crewRoutes.Add(route); }
                route.lastValidatedRoom = room.index;
            }
            ResolveDistortion(now, present);
            AdvancePursuer(now, present, currentRoom);
        }

        private void RecordEncounterObservations(EvidenceRecord record, List<Pawn> present, bool recording)
        {
            if (!recording || record == null || record.Status == EvidenceStatus.Analyzed) { return; }
            foreach (Pawn witness in present.Where(p => !p.Downed))
            {
                RoomRecord room = RoomAt(witness.Position);
                if (room == null) { continue; }
                CompRouteAid displaced = DeployedAids().FirstOrDefault(a => !a.Beacon &&
                    a.RoomIndex != room.Index && RoomAt(a.parent.Position)?.Index == room.Index);
                if (distortionWarned && displaced != null)
                {
                    Campaign.RecordFieldObservation(record, EvidenceObservationKinds.RouteMismatch,
                        room.Index, displaced.RoomIndex, displaced.Number, witness);
                    Campaign.RecordFieldObservation(record, EvidenceObservationKinds.RecorderGap,
                        room.Index, displaced.RoomIndex, displaced.Number, witness);
                }
                if (pursuer != null && pursuer.Spawned && !pursuerWithdrawn && pursuer.Map == map)
                {
                    Campaign.RecordFieldObservation(record, EvidenceObservationKinds.EntitySighting,
                        pursuerRoom, room.Index, 0, witness);
                }
            }
        }

        private void ResolveDistortion(int now, List<Pawn> present)
        {
            if (!distortionWarned || distortionResolved || now <= distortionWarningTick) { return; }
            RoomRecord junction = Coordinate.Rooms.FirstOrDefault(r => r.index == lastValidatedRoom);
            if (junction == null) { return; }
            bool protectedRoute = DeployedAids().Any(a => a.Beacon && a.RoomIndex == junction.index && RoomAt(a.parent.Position)?.index == junction.index) &&
                DeployedAids().Any(a => !a.Beacon && a.RoomIndex == junction.index);
            if (protectedRoute)
            {
                distortionResolved = true;
                Note("RR_Event_CorridorCountered", (junction.index + 1).ToString());
                return;
            }
            if (distortionPawn == null || !distortionPawn.Spawned || distortionPawn.Map != map || distortionPawn.Downed) { return; }
            RoomRecord room = RoomAt(distortionPawn.Position);
            if (room == null || room.familyId != "borrowed_corridor" || distortionPawn.Position.DistanceToSquared(distortionWarningCell) < 4) { return; }
            var safeCells = junction.Bounds.Cells.Where(c => c.InBounds(map) && c.Standable(map) && !c.Fogged(map) && c.GetFirstPawn(map) == null)
                .OrderBy(c => c.DistanceToSquared(junction.Bounds.CenterCell)).ToList();
            List<Pawn> looped = present.Where(p => !p.Downed && RoomAt(p.Position)?.familyId == "borrowed_corridor").ToList();
            if (safeCells.Count < looped.Count) { Note("RR_Event_CorridorRouteBlocked"); distortionResolved = true; return; }
            distortionResolved = true;
            int cellIndex = 0;
            foreach (Pawn pawn in looped)
            {
                pawn.Position = safeCells[cellIndex++];
                pawn.Notify_Teleported();
            }
            // Gate countdown accounting is integrated through this once-only, saved pending cost.
            distortionTimeSpent = true;
            Note("RR_Event_CorridorLoop", (junction.index + 1).ToString());
        }

        public int PendingDistortionCost { get { return distortionTimeSpent ? 125 : 0; } }
        public void AcknowledgeDistortionCost() { distortionTimeSpent = false; }

        public RoomRecord RoomAt(IntVec3 cell) { return Coordinate?.Rooms.FirstOrDefault(r => r.Bounds.Contains(cell)); }
        internal static bool HasItem(Pawn pawn, string defName)
        {
            return pawn?.inventory != null && pawn.inventory.innerContainer.Any(t => !t.Destroyed && t.def.defName == defName && t.stackCount > 0);
        }
        private IEnumerable<CompRouteAid> DeployedAids()
        {
            foreach (string name in new[] { "RR_SurveyTag", "RR_ReturnBeacon" })
            {
                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (definition == null) { continue; }
                foreach (Thing item in map.listerThings.ThingsOfDef(definition))
                {
                    CompRouteAid aid = item.TryGetComp<CompRouteAid>();
                    if (aid != null && aid.Deployed && aid.CoordinateId == Coordinate?.Id) { yield return aid; }
                }
            }
        }
        public CompanyActionResult QueueDeployAid(Pawn pawn, bool beacon)
        {
            if (pawn == null || !crew.Contains(pawn) || !pawn.Spawned || pawn.Map != map || pawn.Downed || RoomAt(pawn.Position) == null)
            { return CompanyActionResult.Refused("RR_Field_CannotDeploy"); }
            Thing item = pawn.inventory?.innerContainer.FirstOrDefault(t => t.def.defName == (beacon ? "RR_ReturnBeacon" : "RR_SurveyTag"));
            if (item == null) { return CompanyActionResult.Refused("RR_Field_AidMissing"); }
            IntVec3 cell = GenRadial.RadialCellsAround(pawn.Position, 2f, true).FirstOrDefault(c => c.InBounds(map) &&
                c.Standable(map) && c.GetFirstItem(map) == null && RoomAt(c) == RoomAt(pawn.Position));
            if (!cell.InBounds(map) || !cell.Standable(map) || cell.GetFirstItem(map) != null || RoomAt(cell) != RoomAt(pawn.Position))
            { return CompanyActionResult.Refused("RR_Field_CannotDeploy"); }
            Job job = JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("RR_DeployRouteAid"), cell, item);
            return pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc) ? CompanyActionResult.Applied() : CompanyActionResult.Refused("RR_Field_CannotDeploy");
        }
        internal CompanyActionResult DeployAid(Pawn pawn, Thing item, IntVec3 cell)
        {
            RoomRecord room = RoomAt(cell);
            if (pawn == null || !crew.Contains(pawn) || pawn.Map != map || pawn.Position != cell || room == null ||
                item == null || item.TryGetComp<CompRouteAid>() == null || !pawn.inventory.innerContainer.Contains(item) || nextMarkerNumber == int.MaxValue ||
                cell.GetFirstItem(map) != null || !cell.Standable(map))
            { return CompanyActionResult.Refused("RR_Field_CannotDeploy"); }
            if (DeployedAids().Any(a => a.RoomIndex == room.index && a.Beacon == item.TryGetComp<CompRouteAid>().Beacon))
            { return CompanyActionResult.Refused("RR_Field_AidAlreadyPlaced"); }
            Thing unit = pawn.inventory.innerContainer.Take(item, 1);
            if (unit == null) { return CompanyActionResult.Refused("RR_Field_AidMissing"); }
            try
            {
                GenSpawn.Spawn(unit, cell, map);
                if (!unit.Spawned || unit.Map != map) { throw new InvalidOperationException("Route aid did not reach its requested map."); }
                unit.TryGetComp<CompRouteAid>().Deploy(Coordinate.Id, room.index, nextMarkerNumber++);
                unit.SetForbidden(true, false);
                Note("RR_Event_RouteAidPlaced", unit.LabelCap, (room.index + 1).ToString());
                return CompanyActionResult.Applied();
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Route] Placement interrupted: " + error);
                if (!unit.Spawned && !unit.Destroyed && !pawn.inventory.innerContainer.TryAdd(unit))
                { deploymentRecovery.TryAdd(unit); }
                return CompanyActionResult.Refused("RR_Field_CannotDeploy");
            }
        }
        public CompanyActionResult RecoverDeploymentItems(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map != map || !crew.Contains(pawn) || pawn.Downed)
            { return CompanyActionResult.Refused("RR_Field_CannotDeploy"); }
            foreach (Thing item in deploymentRecovery.ToList())
            {
                IntVec3 dropCell = IntVec3.Invalid;
                foreach (IntVec3 candidate in GenRadial.RadialCellsAround(pawn.Position, 3f, true))
                {
                    if (candidate.InBounds(map) && candidate.Standable(map) && !candidate.Fogged(map) &&
                        candidate.GetFirstItem(map) == null && pawn.CanReach(candidate, PathEndMode.OnCell, Danger.Some))
                    { dropCell = candidate; break; }
                }
                if (!dropCell.IsValid || !deploymentRecovery.TryDrop(item, dropCell, map, ThingPlaceMode.Direct, out Thing dropped))
                { return CompanyActionResult.Refused("RR_Field_CannotDeploy"); }
            }
            return CompanyActionResult.Applied();
        }
        private void Note(string key, params string[] arguments)
        {
            Campaign.RecordEvent(key, Coordinate.Id, arguments);
            string message = string.Format(key.Translate().ToString(), arguments.Cast<object>().ToArray());
            bool spatial = key == "RR_Event_CorridorMismatch" || key == "RR_Event_CorridorLoop";
            bool radio = key == "RR_Event_PursuerSighting" || key == "RR_Event_PursuerContactWarning" || key == "RR_Event_RouteAidPlaced";
            Messages.Message(message, spatial || radio ? MessageTypeDefOf.SilentInput : MessageTypeDefOf.NeutralEvent, false);
            if (spatial || radio)
            {
                Pawn listener = crew.FirstOrDefault(p => p != null && p.Spawned && p.Map == map && !p.Dead);
                if (listener != null)
                { Audio.RimroomsAudio.Play(spatial ? "RR_SpatialTell" : "RR_FieldRadio", map, listener.Position, true); }
            }
        }
    }
    public sealed class CrewRouteRecord : IExposable
    {
        internal Pawn pawn;
        internal int lastValidatedRoom = -1;
        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "rr_pawn");
            Scribe_Values.Look(ref lastValidatedRoom, "rr_lastValidatedRoom", -1);
        }
    }
}
