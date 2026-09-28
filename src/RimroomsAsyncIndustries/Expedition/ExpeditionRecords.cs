using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Expedition
{
    public enum ExpeditionStatus { Staging = 0, OnSite = 1, Returning = 2, Stranded = 3, Completed = 4, Aborted = 5, Abandoned = 6 }
    public enum CargoLocation { WithCrew = 0, Delivered = 1, LeftAtSite = 2, Elsewhere = 3, Unresolved = 4, AtSiteInContainer = 5 }
    public enum CargoDisposition { Unspecified = 0, Consumed = 1, Lost = 2, LeftBehind = 3, Used = 4 }
    public enum CrewClosureLocation { Headquarters = 0, AtSite = 1, Elsewhere = 2, Unknown = 3 }

    public sealed class ExpeditionRecord : IExposable
    {
        internal string id;
        internal string branchId;
        internal string coordinateId;
        internal ExpeditionStatus status;
        internal Thing gate;
        internal Map headquarters;
        internal Map destination;
        internal IntVec3 entryCell;
        internal IntVec3 returnCell;
        internal List<Pawn> crew = new List<Pawn>();
        internal List<Pawn> returned = new List<Pawn>();
        internal List<Pawn> entered = new List<Pawn>();
        internal List<Pawn> rescueCrew = new List<Pawn>();
        internal List<Pawn> recoveryPassengers = new List<Pawn>();
        internal List<ExpeditionClosureRecord> closures = new List<ExpeditionClosureRecord>();
        internal bool reliefPending;
        internal int recoveryAttemptCounter;
        internal string currentRecoveryOperationId;
        internal List<CargoManifestEntry> cargo = new List<CargoManifestEntry>();
        internal int createdTick;
        internal int openedTick = -1;
        internal int closedTick = -1;
        internal bool emergency;
        internal string failureKey;
        public string ExpeditionId { get { return id; } }
        public string CoordinateId { get { return coordinateId; } }
        public ExpeditionStatus Status { get { return status; } }
        public IReadOnlyList<Pawn> InitialCrew { get { return crew; } }
        public IReadOnlyList<Pawn> ReturnedCrew { get { return returned; } }
        public IReadOnlyList<Pawn> RescueCrew { get { return rescueCrew; } }
        public IReadOnlyList<Pawn> RecoveryPassengers { get { return recoveryPassengers; } }
        public IReadOnlyList<ExpeditionClosureRecord> ClosureHistory { get { return closures; } }
        public IReadOnlyList<CargoManifestEntry> Cargo { get { return cargo; } }
        public Map Headquarters { get { return headquarters; } }
        public Map Destination { get { return destination; } }
        public Thing Gate { get { return gate; } }
        public IntVec3 ReturnCell { get { return returnCell; } }
        public string FailureKey { get { return failureKey; } }
        public bool Emergency { get { return emergency; } }
        public int RecoveryAttemptCounter { get { return recoveryAttemptCounter; } }
        public string CurrentRecoveryOperationId { get { return currentRecoveryOperationId; } }
        public bool Closed { get { return status == ExpeditionStatus.Completed || status == ExpeditionStatus.Aborted || status == ExpeditionStatus.Abandoned; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref status, "rr_status");
            Scribe_References.Look(ref gate, "rr_gate");
            Scribe_References.Look(ref headquarters, "rr_headquarters");
            Scribe_References.Look(ref destination, "rr_destination");
            Scribe_Values.Look(ref entryCell, "rr_entryCell");
            Scribe_Values.Look(ref returnCell, "rr_returnCell");
            Scribe_Collections.Look(ref crew, "rr_crew", LookMode.Reference);
            Scribe_Collections.Look(ref returned, "rr_returned", LookMode.Reference);
            Scribe_Collections.Look(ref entered, "rr_entered", LookMode.Reference);
            Scribe_Collections.Look(ref rescueCrew, "rr_rescueCrew", LookMode.Reference);
            Scribe_Collections.Look(ref recoveryPassengers, "rr_recoveryPassengers", LookMode.Reference);
            Scribe_Collections.Look(ref closures, "rr_closures", LookMode.Deep);
            Scribe_Values.Look(ref reliefPending, "rr_reliefPending");
            Scribe_Values.Look(ref recoveryAttemptCounter, "rr_recoveryAttemptCounter");
            Scribe_Values.Look(ref currentRecoveryOperationId, "rr_currentRecoveryOperationId");
            Scribe_Collections.Look(ref cargo, "rr_cargo", LookMode.Deep);
            Scribe_Values.Look(ref createdTick, "rr_createdTick");
            Scribe_Values.Look(ref openedTick, "rr_openedTick", -1);
            Scribe_Values.Look(ref closedTick, "rr_closedTick", -1);
            Scribe_Values.Look(ref emergency, "rr_emergency");
            Scribe_Values.Look(ref failureKey, "rr_failureKey");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                crew = crew ?? new List<Pawn>();
                returned = returned ?? new List<Pawn>();
                entered = entered ?? new List<Pawn>();
                rescueCrew = rescueCrew ?? new List<Pawn>();
                recoveryPassengers = recoveryPassengers ?? new List<Pawn>();
                closures = closures ?? new List<ExpeditionClosureRecord>();
                cargo = cargo ?? new List<CargoManifestEntry>();
            }
        }
    }

    public sealed class CargoManifestEntry : IExposable
    {
        internal string id;
        internal Thing item;
        internal string itemLoadId;
        internal string defName;
        internal string labelAtDeparture;
        internal Pawn originalCarrier;
        internal int originalCount;
        internal int originalHitPoints;
        internal int observedCount;
        internal bool damaged;
        internal CargoLocation location;
        internal CargoDisposition declaration;
        internal string note;
        internal int declaredCount;
        internal bool declarationNeedsReview;
        internal List<CargoDeclarationRecord> declarationHistory = new List<CargoDeclarationRecord>();
        public string Id { get { return id; } }
        public Thing Item { get { return item; } }
        public string Label { get { return item == null || item.Destroyed ? labelAtDeparture : item.LabelNoCount; } }
        public string OriginalThingId { get { return itemLoadId; } }
        public int OriginalCount { get { return originalCount; } }
        public int ObservedCount { get { return observedCount; } }
        public bool Damaged { get { return damaged; } }
        public CargoLocation Location { get { return location; } }
        public CargoDisposition Declaration { get { return declaration; } }
        public string Note { get { return note; } }
        public int DeclaredCount { get { return declaredCount; } }
        public bool DeclarationNeedsReview { get { return declarationNeedsReview; } }
        public IReadOnlyList<CargoDeclarationRecord> DeclarationHistory { get { return declarationHistory; } }
        public int UnresolvedCount { get { return System.Math.Max(0, originalCount - observedCount); } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_References.Look(ref item, "rr_item");
            Scribe_Values.Look(ref itemLoadId, "rr_itemLoadId");
            Scribe_Values.Look(ref defName, "rr_defName");
            Scribe_Values.Look(ref labelAtDeparture, "rr_label");
            Scribe_References.Look(ref originalCarrier, "rr_originalCarrier");
            Scribe_Values.Look(ref originalCount, "rr_originalCount");
            Scribe_Values.Look(ref originalHitPoints, "rr_originalHitPoints");
            Scribe_Values.Look(ref observedCount, "rr_observedCount");
            Scribe_Values.Look(ref damaged, "rr_damaged");
            Scribe_Values.Look(ref location, "rr_location");
            Scribe_Values.Look(ref declaration, "rr_declaration");
            Scribe_Values.Look(ref note, "rr_note");
            Scribe_Values.Look(ref declaredCount, "rr_declaredCount");
            Scribe_Values.Look(ref declarationNeedsReview, "rr_declarationNeedsReview");
            Scribe_Collections.Look(ref declarationHistory, "rr_declarationHistory", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) { declarationHistory = declarationHistory ?? new List<CargoDeclarationRecord>(); }
        }
    }

    public sealed class CargoDeclarationRecord : IExposable
    {
        internal CargoDisposition disposition;
        internal int count;
        internal string note;
        internal int tick;
        internal int observedCount;
        internal CargoLocation observedLocation;
        public CargoDisposition Disposition { get { return disposition; } }
        public int Count { get { return count; } }
        public string Note { get { return note; } }
        public int Tick { get { return tick; } }
        public int ObservedCount { get { return observedCount; } }
        public CargoLocation ObservedLocation { get { return observedLocation; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref disposition, "rr_disposition");
            Scribe_Values.Look(ref count, "rr_count");
            Scribe_Values.Look(ref note, "rr_note");
            Scribe_Values.Look(ref tick, "rr_tick");
            Scribe_Values.Look(ref observedCount, "rr_observedCount");
            Scribe_Values.Look(ref observedLocation, "rr_observedLocation");
        }
    }

    public sealed class ExpeditionClosureRecord : IExposable
    {
        internal string id;
        internal string reason;
        internal int tick;
        internal List<CrewClosureRecord> crew = new List<CrewClosureRecord>();
        internal List<CargoClosureRecord> cargo = new List<CargoClosureRecord>();
        internal int pendingTransferCount;
        internal int heldForRecoveryCount;
        public string Id { get { return id; } }
        public string Reason { get { return reason; } }
        public int Tick { get { return tick; } }
        public IReadOnlyList<CrewClosureRecord> Crew { get { return crew; } }
        public IReadOnlyList<CargoClosureRecord> Cargo { get { return cargo; } }
        public int PendingTransferCount { get { return pendingTransferCount; } }
        public int HeldForRecoveryCount { get { return heldForRecoveryCount; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref reason, "rr_reason");
            Scribe_Values.Look(ref tick, "rr_tick");
            Scribe_Collections.Look(ref crew, "rr_crew", LookMode.Deep);
            Scribe_Collections.Look(ref cargo, "rr_cargo", LookMode.Deep);
            Scribe_Values.Look(ref pendingTransferCount, "rr_pendingTransferCount");
            Scribe_Values.Look(ref heldForRecoveryCount, "rr_heldForRecoveryCount");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            { crew = crew ?? new List<CrewClosureRecord>(); cargo = cargo ?? new List<CargoClosureRecord>(); }
        }
    }

    public sealed class CargoClosureRecord : IExposable
    {
        internal string entryId;
        internal string thingId;
        internal string label;
        internal int count;
        internal CargoLocation location;
        internal bool knownDestroyed;
        internal CargoDisposition declaration;
        internal int declaredCount;
        internal string note;
        public string EntryId { get { return entryId; } }
        public string ThingId { get { return thingId; } }
        public string Label { get { return label; } }
        public int Count { get { return count; } }
        public CargoLocation Location { get { return location; } }
        public bool KnownDestroyed { get { return knownDestroyed; } }
        public CargoDisposition Declaration { get { return declaration; } }
        public int DeclaredCount { get { return declaredCount; } }
        public string Note { get { return note; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref entryId, "rr_entryId");
            Scribe_Values.Look(ref thingId, "rr_thingId");
            Scribe_Values.Look(ref label, "rr_label");
            Scribe_Values.Look(ref count, "rr_count");
            Scribe_Values.Look(ref location, "rr_location");
            Scribe_Values.Look(ref knownDestroyed, "rr_knownDestroyed");
            Scribe_Values.Look(ref declaration, "rr_declaration");
            Scribe_Values.Look(ref declaredCount, "rr_declaredCount");
            Scribe_Values.Look(ref note, "rr_note");
        }
    }

    public sealed class CrewClosureRecord : IExposable
    {
        internal Pawn pawn;
        internal string pawnId;
        internal string label;
        internal bool knownDead;
        internal CrewClosureLocation location;
        internal Map observedMap;
        public Pawn Pawn { get { return pawn; } }
        public string PawnId { get { return pawnId; } }
        public string Label { get { return label; } }
        public bool KnownDead { get { return knownDead; } }
        public CrewClosureLocation Location { get { return location; } }
        public Map ObservedMap { get { return observedMap; } }
        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "rr_pawn");
            Scribe_Values.Look(ref pawnId, "rr_pawnId");
            Scribe_Values.Look(ref label, "rr_label");
            Scribe_Values.Look(ref knownDead, "rr_knownDead");
            Scribe_Values.Look(ref location, "rr_location");
            Scribe_References.Look(ref observedMap, "rr_observedMap");
        }
    }

    public sealed class TransferRecoveryRecord : IExposable
    {
        internal Pawn pawn;
        internal Map source;
        internal IntVec3 sourceCell;
        internal string expeditionId;
        public Pawn Pawn { get { return pawn; } }
        public Map Source { get { return source; } }
        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "rr_pawn");
            Scribe_References.Look(ref source, "rr_source");
            Scribe_Values.Look(ref sourceCell, "rr_sourceCell");
            Scribe_Values.Look(ref expeditionId, "rr_expeditionId");
        }
    }
}
