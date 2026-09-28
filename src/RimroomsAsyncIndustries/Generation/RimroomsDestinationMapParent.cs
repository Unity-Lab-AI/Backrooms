using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Stable Core world-object owner for one branch-local machine coordinate.
    /// The world tile is an engine address, not an in-fiction travel route.
    /// </summary>
    public sealed class RimroomsDestinationMapParent : MapParent
    {
        private string coordinateId;
        private int generatorVersion;
        private int roomLibraryVersion;
        private int layoutFingerprint;
        private bool layoutReady;
        private string generationFailureKey;
        private IntVec3 entryCell = IntVec3.Invalid;
        private IntVec3 returnCell = IntVec3.Invalid;
        private IntVec3 officeEvidenceCell = IntVec3.Invalid;
        private Thing returnAnchor;
        private bool generationAttempted;
        private bool layoutBuildStarted;
        private int plannerVersion;
        private int candidateIndex = -1;
        private int contentVersion;

        public string CoordinateId { get { return coordinateId; } }
        public int GeneratorVersion { get { return generatorVersion; } }
        public int RoomLibraryVersion { get { return roomLibraryVersion; } }
        public int LayoutFingerprint { get { return layoutFingerprint; } }
        public bool LayoutReady { get { return layoutReady; } }
        public string GenerationFailureKey { get { return generationFailureKey; } }
        public IntVec3 EntryCell { get { return entryCell; } }
        public IntVec3 ReturnCell { get { return returnCell; } }
        public IntVec3 OfficeEvidenceCell { get { return officeEvidenceCell; } }
        public Thing ReturnAnchor { get { return returnAnchor; } }
        public bool GenerationAttempted { get { return generationAttempted; } }
        public int PlannerVersion { get { return plannerVersion; } }
        public int CandidateIndex { get { return candidateIndex; } }
        public bool UsedSafeFallback { get { return plannerVersion > 0 && candidateIndex == RoomLayoutPlanner.FallbackCandidate; } }
        public int ContentVersion { get { return contentVersion; } }

        public override AcceptanceReport CanBeSettled { get { return false; } }
        public override bool GravShipCanLandOn { get { return false; } }
        protected override bool UseGenericEnterMapFloatMenuOption { get { return false; } }
        public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Caravan caravan)
        { yield return new FloatMenuOption("RR_Generation_GateAccessOnly".Translate(), null); }
        public override IEnumerable<FloatMenuOption> GetTransportersFloatMenuOptions(IEnumerable<IThingHolder> pods,
            Action<PlanetTile, TransportersArrivalAction> launchAction)
        { yield return new FloatMenuOption("RR_Generation_GateAccessOnly".Translate(), null); }
        public override IEnumerable<FloatMenuOption> GetShuttleFloatMenuOptions(IEnumerable<IThingHolder> pods,
            Action<PlanetTile, TransportersArrivalAction> launchAction)
        { yield return new FloatMenuOption("RR_Generation_GateAccessOnly".Translate(), null); }

        public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)
        {
            alsoRemoveWorldObject = false;
            return false;
        }

        public bool InitializeCoordinate(string id, int generator, int roomLibrary, int fingerprint)
        {
            if (string.IsNullOrWhiteSpace(id) || generator < 1 || roomLibrary < 1)
            {
                return false;
            }
            if (!string.IsNullOrEmpty(coordinateId))
            {
                return coordinateId == id && generatorVersion == generator &&
                    roomLibraryVersion == roomLibrary && layoutFingerprint == fingerprint;
            }
            coordinateId = id;
            generatorVersion = generator;
            roomLibraryVersion = roomLibrary;
            layoutFingerprint = fingerprint;
            return true;
        }

        public void MarkLayoutReady(IntVec3 entry, IntVec3 returnCellValue, IntVec3 evidenceCell, Thing anchor)
        {
            entryCell = entry;
            returnCell = returnCellValue;
            officeEvidenceCell = evidenceCell;
            returnAnchor = anchor;
            generationFailureKey = null;
            layoutReady = true;
        }

        public void MarkGenerationFailed(string key)
        {
            if (!layoutReady && string.IsNullOrWhiteSpace(generationFailureKey))
            {
                generationFailureKey = string.IsNullOrWhiteSpace(key) ? "RR_Generation_Failed" : key;
            }
        }

        public void BeginGenerationAttempt()
        {
            if (!layoutReady && !HasMap && !generationAttempted) { generationFailureKey = null; generationAttempted = true; }
        }

        internal void RecordGenerationPlan(int candidate, int content)
        {
            if (HasMap || generationAttempted || layoutReady) { return; }
            plannerVersion = candidate < 0 ? 0 : RoomLayoutPlanner.PlannerVersion;
            candidateIndex = candidate;
            contentVersion = content;
        }

        internal bool TryBeginLayout()
        {
            if (layoutBuildStarted || layoutReady) { return false; }
            layoutBuildStarted = true;
            generationAttempted = true;
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref generatorVersion, "rr_generatorVersion");
            Scribe_Values.Look(ref roomLibraryVersion, "rr_roomLibraryVersion");
            Scribe_Values.Look(ref layoutFingerprint, "rr_layoutFingerprint");
            Scribe_Values.Look(ref layoutReady, "rr_layoutReady");
            Scribe_Values.Look(ref generationFailureKey, "rr_generationFailureKey");
            Scribe_Values.Look(ref entryCell, "rr_entryCell", IntVec3.Invalid);
            Scribe_Values.Look(ref returnCell, "rr_returnCell", IntVec3.Invalid);
            Scribe_Values.Look(ref officeEvidenceCell, "rr_officeEvidenceCell", IntVec3.Invalid);
            Scribe_References.Look(ref returnAnchor, "rr_returnAnchor");
            Scribe_Values.Look(ref generationAttempted, "rr_generationAttempted");
            Scribe_Values.Look(ref layoutBuildStarted, "rr_layoutBuildStarted");
            Scribe_Values.Look(ref plannerVersion, "rr_plannerVersion");
            Scribe_Values.Look(ref candidateIndex, "rr_candidateIndex", -1);
            Scribe_Values.Look(ref contentVersion, "rr_contentVersion");
        }
    }
}
