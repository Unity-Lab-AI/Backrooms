using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What the green light on a quest actually means.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"picks up the quest one when propeted to complete
    /// a mission with a geen light to show its ready to be sent to complete the quest mission"*.
    ///
    /// Three states, and the third is the one that makes the design safe:
    ///
    /// | State | Condition | What the player does |
    /// |---|---|---|
    /// | **dark** | write-ups outstanding | assign somebody to a records desk |
    /// | **green** | every required write-up filed, book present, in custody, and agreeing | send it back |
    /// | **amber** | the record is complete and no agreeing book exists | issue or re-stamp a book |
    ///
    /// **Amber is why the record is the authority rather than the book.** Burn the book, lose it in
    /// a coordinate, or leave it on a crew who did not come back, and the branch has lost a
    /// *deliverable* rather than a month of work. That is recoverable; the alternative is not.
    /// </summary>
    public enum QuestLight
    {
        /// <summary>Paperwork outstanding. Nothing to send.</summary>
        Dark = 0,

        /// <summary>Ready to send back.</summary>
        Green = 1,

        /// <summary>Filed, but no agreeing book exists. The work survives; the deliverable does not.</summary>
        Amber = 2,
    }

    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// The write-up kinds this quest wants, in their declared order.
        ///
        /// Resolved through the request def, so **an unlisted kind is never wanted and a listed one
        /// is always wanted.** Returns an empty list for a quest with no paperwork, which is most of
        /// them: *"paperwork is a thing the company asks for on some work, not a tax on all of it."*
        /// </summary>
        public List<RimroomsWriteUpDef> WriteUpsWanted(RequestRecord request)
        {
            var wanted = new List<RimroomsWriteUpDef>();
            RimroomsRequestDef definition = request == null ? null : request.Definition;
            if (definition == null || definition.writeUps == null) { return wanted; }
            // Walked in the def's own order rather than the def database's, because this decides
            // what a pawn writes first and what the ledger lists first.
            foreach (RimroomsWriteUpDef kind in RimroomsWriteUpDef.AllInOrder())
            {
                if (kind != null && definition.writeUps.Contains(kind.defName)) { wanted.Add(kind); }
            }
            return wanted;
        }

        /// <summary>
        /// Whether the branch holds what this kind of write-up is written *from*.
        ///
        /// **Nothing is invented at the desk.** The owner's model is that paperwork reports work
        /// that happened: *"after doing all the gate steps, each step has a lab nots"*. So a kind
        /// whose precondition is unmet is not merely blocked, it has no subject, and offering the
        /// job would produce a pawn writing up something nobody did.
        /// </summary>
        public bool WriteUpPreconditionMet(RimroomsWriteUpDef kind, RequestRecord request)
        {
            if (kind == null || request == null) { return false; }
            switch (kind.precondition)
            {
                case WriteUpPrecondition.None:
                    return true;

                case WriteUpPrecondition.GateStepRecorded:
                    // **Asked of the checklist that already owns the question**, never re-derived.
                    // `GateStartupChecklist.Steps` is what the startup pane reads, so what a player
                    // sees ticked is exactly what the company will accept lab notes for. A second
                    // derivation here would let the pane and the paperwork disagree about whether a
                    // step happened, and the player would be right and the company wrong.
                    return AnyGateStepDone();

                case WriteUpPrecondition.ProjectCompleted:
                    return projects != null && projects.Any(project => project != null && project.Completed);

                case WriteUpPrecondition.EvidenceSecured:
                    // Secured OR analysed: analysis happens *after* custody, so a record that has
                    // moved on has plainly met the custody condition. Testing Secured alone would
                    // make the investigation write-up impossible on any record somebody analysed
                    // promptly, which is a reward for being slow.
                    return evidence != null && evidence.Any(record => record != null &&
                        (record.Status == EvidenceStatus.Secured || record.Status == EvidenceStatus.Analyzed));

                case WriteUpPrecondition.EvidenceAnalysed:
                    return evidence != null && evidence.Any(record => record != null &&
                        record.Status == EvidenceStatus.Analyzed);

                case WriteUpPrecondition.SurveyComplete:
                    // **ASKED OF THE ONE DERIVATION, which this used to duplicate and get wrong.**
                    // The first version tested `room.Surveyed` on EVERY room of a coordinate. A
                    // `SealedFamily` vault has no doors by design and is reached by mining, so any
                    // coordinate holding one could never satisfy that -- and the survey write-up, the
                    // whole point of the exploration feature, would have been permanently unwritable
                    // with nothing anywhere saying why.
                    //
                    // `ExplorationMapComponent.Complete` is what the explore toggle uses to decide it
                    // is finished and to fire the owner's *"radioed in exploration complete"* notice.
                    // **The notice and the paperwork must mean the same thing**, so they ask the same
                    // method. This is the identical defect that killed the solo start, where the
                    // planner and the layout validator disagreed about a vault.
                    return coordinates != null && coordinates.Any(coordinate =>
                        coordinate != null && coordinate.Rooms != null && coordinate.Rooms.Count > 0 &&
                        Generation.ExplorationMapComponent.Complete(coordinate));

                default:
                    // **An unhandled precondition is refused, never waved through.** A new enum
                    // member that silently returned true would hand a branch free paperwork, and
                    // the failure would look like the feature working.
                    return false;
            }
        }

        /// <summary>
        /// A quest by its record id, for anything holding a stamp rather than a def name.
        ///
        /// `RequestFor` already looks a quest up by **def name**, which is what the Operations pane
        /// has. A book carries the **record id**, because a def name would stop identifying one quest
        /// the moment the same request could be offered twice.
        /// </summary>
        public RequestRecord RequestById(string id)
        {
            if (string.IsNullOrEmpty(id)) { return null; }
            IReadOnlyList<RequestRecord> line = Requests;
            if (line == null) { return null; }
            for (int index = 0; index < line.Count; index++)
            {
                if (line[index] != null && line[index].Id == id) { return line[index]; }
            }
            return null;
        }

        /// <summary>
        /// The nearest storage thing a gate links as its records archive, or null.
        ///
        /// **Asked of the gate links**, which is where `HasArchivedCustody` reads custody from, so
        /// the shelf this offers to haul to is the shelf that will satisfy the test. Offering the
        /// nearest *shelf* instead would send a pawn across the base to a container that does not
        /// count.
        /// </summary>
        public Thing NearestArchiveStore(Thing item)
        {
            if (item == null || item.Map == null) { return null; }
            RimroomsGateEquipmentDefRole archive = ArchiveRole();
            if (archive.Role == null) { return null; }
            Thing best = null;
            int bestDistance = int.MaxValue;
            List<Building> buildings = item.Map.listerBuildings.allBuildingsColonist;
            for (int index = 0; index < buildings.Count; index++)
            {
                Gate.CompRimroomsGate gate = buildings[index] == null
                    ? null : buildings[index].TryGetComp<Gate.CompRimroomsGate>();
                if (gate == null || !gate.IsDesignated) { continue; }
                foreach (Thing linked in gate.LinkedEquipment)
                {
                    if (linked == null || !linked.Spawned || linked.Map != item.Map) { continue; }
                    if (gate.RoleOf(linked) != archive.Role) { continue; }
                    int distance = item.Position.DistanceToSquared(linked.Position);
                    if (distance >= bestDistance) { continue; }
                    best = linked;
                    bestDistance = distance;
                }
            }
            return best;
        }

        /// <summary>The archive role, resolved once so neither caller types the defName.</summary>
        private struct RimroomsGateEquipmentDefRole { public Gate.RimroomsGateEquipmentDef Role; }

        private static RimroomsGateEquipmentDefRole ArchiveRole()
        {
            return new RimroomsGateEquipmentDefRole
            {
                Role = DefDatabase<Gate.RimroomsGateEquipmentDef>.GetNamedSilentFail("RR_Link_Archive")
            };
        }

        /// <summary>
        /// A cell inside the nearest designated credit beacon's radius, or an invalid cell.
        ///
        /// **The beacon's own cell when it is standable, and a cell beside it otherwise.** A beacon
        /// is a building, so a haul order aimed at its position would be a haul into a wall; the
        /// radius is what matters and anything inside it is equally collected.
        /// </summary>
        public IntVec3 NearestCreditBeaconCell(Thing item)
        {
            if (item == null || item.Map == null) { return IntVec3.Invalid; }
            Building nearest = null;
            int bestDistance = int.MaxValue;
            List<Building> buildings = item.Map.listerBuildings.allBuildingsColonist;
            for (int index = 0; index < buildings.Count; index++)
            {
                Building building = buildings[index];
                if (building == null || building.Destroyed) { continue; }
                Economy.CompRimroomsCreditBeacon beacon =
                    building.TryGetComp<Economy.CompRimroomsCreditBeacon>();
                if (beacon == null || !beacon.Designated) { continue; }
                int distance = item.Position.DistanceToSquared(building.Position);
                if (distance >= bestDistance) { continue; }
                nearest = building;
                bestDistance = distance;
            }
            if (nearest == null) { return IntVec3.Invalid; }
            // Walked outward from the beacon in Core's own radial order, so the chosen cell is the
            // same on every reload and is as close to the beacon as the map allows.
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(nearest.Position, 2.9f, true))
            {
                if (cell.InBounds(item.Map) && cell.Standable(item.Map)) { return cell; }
            }
            return IntVec3.Invalid;
        }

        /// <summary>
        /// Whether any designated gate on an owned map has completed at least one startup step.
        ///
        /// Stops at the first one found, so on a branch that has done anything at all this is a
        /// handful of comparisons.
        /// </summary>
        private bool AnyGateStepDone()
        {
            List<Map> maps = Find.Maps;
            if (maps == null) { return false; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map.listerBuildings == null || !OwnsMap(map)) { continue; }
                List<Building> buildings = map.listerBuildings.allBuildingsColonist;
                for (int item = 0; item < buildings.Count; item++)
                {
                    Gate.CompRimroomsGate gate = buildings[item] == null
                        ? null : buildings[item].TryGetComp<Gate.CompRimroomsGate>();
                    if (gate == null || !gate.IsDesignated) { continue; }
                    List<Gate.GateStartupChecklist.GateStep> steps = Gate.GateStartupChecklist.Steps(gate);
                    if (Gate.GateStartupChecklist.DoneCount(steps) > 0) { return true; }
                }
            }
            return false;
        }

        /// <summary>
        /// The next write-up a pawn could actually sit down and write, or null.
        ///
        /// Outstanding **and** precondition met, in declared order, so a branch works through a
        /// quest's paperwork in the sequence the defs state rather than whichever the scan reached
        /// first.
        /// </summary>
        public RimroomsWriteUpDef NextWriteUp(RequestRecord request)
        {
            if (request == null || request.Status != RequestStatus.Accepted) { return null; }
            foreach (RimroomsWriteUpDef kind in WriteUpsWanted(request))
            {
                if (kind == null || request.WriteUpsFiled.Contains(kind.defName)) { continue; }
                if (WriteUpPreconditionMet(kind, request)) { return kind; }
            }
            return null;
        }

        /// <summary>
        /// The first accepted quest with writable paperwork nobody else is writing, and which kind.
        ///
        /// **One place answers "is there paperwork for THIS pawn to do", and the work giver and the
        /// job driver both ask it.** Two copies of this scan would be two chances for the giver to
        /// offer a job the driver then refuses, which reads to a player as a colonist walking to a
        /// desk and standing there.
        ///
        /// Quests are taken in list order, which is acceptance order, so a branch works its oldest
        /// outstanding obligation first.
        ///
        /// **There is deliberately no pawn-less overload.** One was written and immediately had no
        /// callers: everything that asks this question is a pawn about to sit down, and an overload
        /// that passed `null` would be a quiet way to get the old behaviour back -- the behaviour
        /// that let two people write the same page. A dead convenience that reintroduces a bug when
        /// somebody uses it is worse than no convenience.
        ///
        /// **There is deliberately no pawn-less overload.** One was written and immediately had no
        /// callers: everything that asks this question is a pawn about to sit down, and an overload
        /// that passed `null` would be a quiet way to get the old behaviour back -- the behaviour
        /// that let two people write the same page. A dead convenience that reintroduces a bug when
        /// somebody uses it is worse than no convenience.
        ///
        /// ## THE DEFECT THIS EXISTS FOR, AND IT WAS IN THE PARALLELISM THE OWNER ASKED FOR
        ///
        /// Owner: *"u can have more than one to have more than one pawn doing it as u can have
        /// multiple quests going"*. The desk was uncapped and the work giver scanned every desk, so
        /// two people could sit down at once -- **and they would both write the same thing**, because
        /// this scan returned the first outstanding write-up and knew nothing about who was already
        /// writing it.
        ///
        /// **The second pawn's session was not merely wasted; it landed on the wrong report.** The
        /// job re-resolved its target every tick and carried its progress across, so when the first
        /// writer filed, the second's accumulated progress was tested against the NEXT write-up's
        /// requirement -- and a pawn 900 ticks into a 1000-tick report would instantly complete a
        /// 600-tick one. **One session of work, two reports filed.** Parallel by accident, which is
        /// the exact failure the queue row predicted one subsystem over.
        ///
        /// ## How a claim is read, and why it is not stored anywhere
        ///
        /// A claim is **what another pawn's active job driver says it is writing**, read off the
        /// pawns. Nothing is reserved, nothing is scribed, and there is no claim table to go stale:
        /// a pawn who dies, is drafted or is interrupted stops holding a claim by the only means
        /// that matters, which is no longer having the job. Same shape as
        /// `CompRimroomsGateConsole.HasAssemblyJob`, which asks the map's pawns what they are doing
        /// rather than keeping a register of it.
        ///
        /// **The limitation, stated rather than hidden:** a pawn with the job queued but not yet
        /// current holds no claim, so two can still be dispatched at the same instant. That is a
        /// wasted walk at worst -- the job pins its own target the moment work starts and
        /// `RequestRecord.FileWriteUp` is idempotent, so the outcome is never a double file.
        /// </summary>
        public bool TryFindWriteUpWork(Pawn asker, out RequestRecord request,
            out RimroomsWriteUpDef kind)
        {
            request = null;
            kind = null;
            if (!CanOperate) { return false; }
            IReadOnlyList<RequestRecord> line = Requests;
            if (line == null) { return false; }
            for (int index = 0; index < line.Count; index++)
            {
                RequestRecord candidate = line[index];
                if (candidate == null || candidate.Status != RequestStatus.Accepted) { continue; }
                foreach (RimroomsWriteUpDef next in WriteUpsWanted(candidate))
                {
                    if (next == null || candidate.WriteUpsFiled.Contains(next.defName)) { continue; }
                    if (!WriteUpPreconditionMet(next, candidate)) { continue; }
                    if (ClaimedByAnother(asker, candidate, next)) { continue; }
                    request = candidate;
                    kind = next;
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Whether a pawn other than <paramref name="asker"/> is writing this exact report now.
        ///
        /// Across every loaded map, because a branch's paperwork is a branch-wide record and a
        /// colonist on a coordinate writing at a desk is writing the same report as one at home.
        /// </summary>
        private static bool ClaimedByAnother(Pawn asker, RequestRecord request,
            RimroomsWriteUpDef kind)
        {
            if (request == null || kind == null) { return false; }
            List<Map> maps = Find.Maps;
            if (maps == null) { return false; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map.mapPawns == null) { continue; }
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int slot = 0; slot < pawns.Count; slot++)
                {
                    Pawn other = pawns[slot];
                    if (other == null || other == asker || other.jobs == null) { continue; }
                    JobDriver_RRWriteUp writing = other.jobs.curDriver as JobDriver_RRWriteUp;
                    if (writing == null) { continue; }
                    if (writing.IsWriting(request, kind)) { return true; }
                }
            }
            return false;
        }

        /// <summary>Whether every write-up this quest wants has been filed.</summary>
        public bool PaperworkComplete(RequestRecord request)
        {
            if (request == null) { return false; }
            foreach (RimroomsWriteUpDef kind in WriteUpsWanted(request))
            {
                if (kind != null && !request.WriteUpsFiled.Contains(kind.defName)) { return false; }
            }
            return true;
        }

        /// <summary>
        /// The quest's book: a company-issued record book stamped for this quest and in custody.
        ///
        /// **Custody is the archive, read through `EvidenceSettlement`'s own rule** rather than a
        /// second copy of it, so the shelf a player designated is the shelf that counts here too,
        /// and a modded shelf works because the test is Core's `StoringThing()`.
        /// </summary>
        public Thing BookFor(RequestRecord request)
        {
            if (request == null || string.IsNullOrEmpty(request.Id)) { return null; }
            ThingDef book = Expedition.ExpeditionCargo.RecordBookDef;
            if (book == null) { return null; }
            List<Map> maps = Find.Maps;
            if (maps == null) { return null; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map.listerThings == null || !OwnsMap(map)) { continue; }
                List<Thing> candidates = map.listerThings.ThingsOfDef(book);
                for (int item = 0; item < candidates.Count; item++)
                {
                    CompRouteEvidence record = candidates[item].TryGetComp<CompRouteEvidence>();
                    if (record != null && record.IsCompanyIssued &&
                        record.StampedQuestId == request.Id)
                    { return candidates[item]; }
                }
            }
            return null;
        }

        /// <summary>
        /// What the quest's light shows. **Reads the record and requires the book.**
        ///
        /// The record is asked first and alone for *is the work done*, so losing a book can never
        /// un-finish work. The book is then required for **green**, because the owner's answer was
        /// that both must agree and a deliverable that does not exist cannot be delivered.
        /// </summary>
        public QuestLight LightFor(RequestRecord request)
        {
            if (request == null || request.Status != RequestStatus.Accepted) { return QuestLight.Dark; }
            if (!PaperworkComplete(request)) { return QuestLight.Dark; }
            Thing book = BookFor(request);
            if (book == null) { return QuestLight.Amber; }
            CompRouteEvidence stamp = book.TryGetComp<CompRouteEvidence>();
            // **The agreement test, and it compares counts rather than trusting the stamp.** A book
            // stamped for this quest but carrying fewer filed kinds than the record is a book from
            // before the last write-up, which is exactly the disagreement the owner asked to be
            // visible rather than papered over.
            if (stamp == null || stamp.StampedWriteUpCount < request.WriteUpsFiled.Count)
            { return QuestLight.Amber; }
            return HasArchivedCustody(book) ? QuestLight.Green : QuestLight.Dark;
        }

        /// <summary>
        /// **One writer, two readers.** Advance the record and stamp the book, in one call, record
        /// first.
        ///
        /// Returns false when nothing changed, which a caller may ignore: a job that finishes twice
        /// after a reload is not an error.
        ///
        /// **The record is written before the book on purpose.** If the stamp somehow fails the
        /// branch has done the work and holds a book that disagrees — which reads as **amber** and
        /// tells the player to re-issue one. The reverse order would stamp a book for work the
        /// record never recorded, which is a book that claims something false.
        /// </summary>
        internal bool FileWriteUpAndStamp(RequestRecord request, RimroomsWriteUpDef kind)
        {
            if (request == null || kind == null) { return false; }
            if (!request.FileWriteUp(kind.defName)) { return false; }
            Thing book = BookFor(request);
            CompRouteEvidence stamp = book == null ? null : book.TryGetComp<CompRouteEvidence>();
            if (stamp != null) { stamp.StampForQuest(request.Id, request.WriteUpsFiled.Count); }
            RecordEvent("RR_Event_WriteUpFiled", kind.label, request.Id);
            return true;
        }
    }
}
