using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class EvidenceCreationAttempt : IExposable
    {
        internal string evidenceId;
        internal string coordinateId;
        internal Map map;
        internal IntVec3 cell = IntVec3.Invalid;
        internal Thing item;
        internal string itemLoadId;
        internal bool creationAttempted;
        internal bool qualityAttempted;
        internal bool qualityComplete;
        internal bool registered;
        internal string failureKey;
        public string EvidenceId { get { return evidenceId; } }
        public string CoordinateId { get { return coordinateId; } }
        public Thing Item { get { return item; } }
        public string ItemLoadId { get { return itemLoadId; } }
        public bool Registered { get { return registered; } }
        public bool QualityComplete { get { return qualityComplete; } }
        public string FailureKey { get { return failureKey; } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref evidenceId, "evidenceId");
            Scribe_Values.Look(ref coordinateId, "coordinateId");
            Scribe_References.Look(ref map, "map");
            Scribe_Values.Look(ref cell, "cell", IntVec3.Invalid);
            Scribe_References.Look(ref item, "item");
            Scribe_Values.Look(ref itemLoadId, "itemLoadId");
            Scribe_Values.Look(ref creationAttempted, "creationAttempted");
            Scribe_Values.Look(ref qualityAttempted, "qualityAttempted");
            Scribe_Values.Look(ref qualityComplete, "qualityComplete");
            Scribe_Values.Look(ref registered, "registered");
            Scribe_Values.Look(ref failureKey, "failureKey");
        }
    }

    /// <summary>Owns only the unfinished original carrier; the company owns case/analysis state.</summary>
    public sealed class RimroomsEvidenceCreationComponent : GameComponent, IThingHolder
    {
        private int schemaVersion = 1;
        private string branchId;
        private List<EvidenceCreationAttempt> attempts = new List<EvidenceCreationAttempt>();
        private ThingOwner<Thing> held;
        private string faultKey;
        private bool busy;
        public RimroomsEvidenceCreationComponent(Game game) { held = new ThingOwner<Thing>(this); }
        public IThingHolder ParentHolder { get { return null; } }
        public ThingOwner GetDirectlyHeldThings() { return held; }
        public void GetChildHolders(List<IThingHolder> children) { ThingOwnerUtility.AppendThingHoldersFromThings(children, held); }
        public IReadOnlyList<EvidenceCreationAttempt> Attempts { get { return attempts; } }
        public int HeldCount { get { return held.Count; } }
        public string FaultKey { get { return faultKey; } }
        public bool HasAttempt(string evidenceId) { return attempts.Any(a => a != null && a.evidenceId == evidenceId); }
        public CompanyActionResult Readiness() { return CheckActive(Campaign); }
        private RimroomsCampaignComponent Campaign
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_evidenceCreationSchema", 1, true);
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_Collections.Look(ref attempts, "rr_creationAttempts", LookMode.Deep);
            Scribe_Deep.Look(ref held, "rr_unspawnedEvidence", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                attempts = attempts ?? new List<EvidenceCreationAttempt>();
                held = held ?? new ThingOwner<Thing>(this);
                faultKey = null;
                if (schemaVersion != 1) { faultKey = "RR_EvidenceCreation_UnsupportedSchema"; }
                else if ((attempts.Count > 0 && string.IsNullOrEmpty(branchId)) ||
                    attempts.Any(a => a == null || string.IsNullOrEmpty(a.coordinateId) ||
                        a.evidenceId != a.coordinateId + ":evidence:route" ||
                        !a.coordinateId.StartsWith(branchId + ":coordinate:", StringComparison.Ordinal) ||
                        (a.qualityComplete && !a.qualityAttempted) || (a.qualityAttempted && !a.creationAttempted) ||
                        (a.registered && !a.qualityComplete) ||
                        (a.item != null && (!a.creationAttempted || a.item.GetUniqueLoadID() != a.itemLoadId))) ||
                    attempts.Select(a => a.evidenceId).Distinct(StringComparer.Ordinal).Count() != attempts.Count ||
                    attempts.Where(a => !string.IsNullOrEmpty(a.itemLoadId)).Select(a => a.itemLoadId).Distinct(StringComparer.Ordinal).Count() !=
                        attempts.Count(a => !string.IsNullOrEmpty(a.itemLoadId)) ||
                    held.Cast<Thing>().Any(t => !attempts.Any(a => !a.registered && a.item == t)))
                { faultKey = "RR_EvidenceCreation_InvalidSave"; }
            }
        }

        private CompanyActionResult CheckActive(RimroomsCampaignComponent campaign)
        {
            if (faultKey != null) { return CompanyActionResult.Refused(faultKey); }
            if (schemaVersion != 1) { return CompanyActionResult.Refused("RR_EvidenceCreation_UnsupportedSchema"); }
            if (campaign == null || campaign != Campaign || !campaign.CanOperate ||
                (!string.IsNullOrEmpty(branchId) && branchId != campaign.BranchId))
            { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            if (busy) { return CompanyActionResult.Refused("RR_EvidenceCreation_Busy"); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult ReconcileRegistered(EvidenceRecord record)
        {
            CompanyActionResult check = CheckActive(Campaign);
            if (!check.Success) { return check; }
            if (record == null) { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
            EvidenceCreationAttempt attempt = attempts.FirstOrDefault(a => a.evidenceId == record.Id);
            if (attempt == null) { return CompanyActionResult.Existing(); }
            if (!attempt.qualityComplete || string.IsNullOrEmpty(attempt.itemLoadId) ||
                record.itemLoadId != attempt.itemLoadId || record.CoordinateId != attempt.coordinateId ||
                (record.Item != null && attempt.item != null && record.Item != attempt.item) ||
                (attempt.item != null && attempt.item.holdingOwner == held))
            { return Fail(attempt, "RR_Company_ReceiptMismatch"); }
            attempt.registered = true;
            attempt.failureKey = null;
            return CompanyActionResult.Existing();
        }

        internal CompanyActionResult EnsureOriginal(RimroomsCampaignComponent campaign, CoordinateRecord coordinate, Map map, IntVec3 cell)
        {
            CompanyActionResult check = CheckActive(campaign);
            if (!check.Success) { return check; }
            if (coordinate == null || !campaign.Coordinates.Contains(coordinate) || map == null ||
                coordinate.Site == null || coordinate.Site.Map != map || !Find.Maps.Contains(map))
            { return CompanyActionResult.Refused("RR_Evidence_SiteUnavailable"); }
            string id = coordinate.Id + ":evidence:route";
            EvidenceCreationAttempt attempt = attempts.FirstOrDefault(a => a.evidenceId == id);
            if (attempt == null)
            {
                ThingDef definition = CompRouteEvidence.NativeCarrierDef;
                if (definition == null) { return CompanyActionResult.Refused("RR_Evidence_InvalidRecord"); }
                if (!CellAvailable(definition, map, cell)) { return CompanyActionResult.Refused("RR_Evidence_NoSafeSlot"); }
                if (attempts.Count(a => !a.registered) >= 8)
                { return CompanyActionResult.Refused("RR_EvidenceCreation_RetainedLimit"); }
                branchId = campaign.BranchId;
                attempt = new EvidenceCreationAttempt { evidenceId = id, coordinateId = coordinate.Id, map = map, cell = cell };
                attempts.Add(attempt);
            }
            if (attempt.coordinateId != coordinate.Id || attempt.map != map || attempt.cell != cell)
            { return Fail(attempt, "RR_Company_ReceiptMismatch"); }
            if (attempt.registered)
            { return campaign.FindEvidence(id) == null ? Fail(attempt, "RR_Company_ReceiptMismatch") : CompanyActionResult.Existing(); }
            busy = true;
            try
            {
                if (!attempt.creationAttempted)
                {
                    // Write the receipt before native creation. Even a throwing creation is never repeated.
                    attempt.creationAttempted = true;
                    ThingDef definition = CompRouteEvidence.NativeCarrierDef;
                    if (definition == null) { return Fail(attempt, "RR_Evidence_InvalidRecord"); }
                    attempt.item = ThingMaker.MakeThing(definition);
                    if (attempt.item == null) { return Fail(attempt, "RR_EvidenceCreation_CreationInterrupted"); }
                    attempt.itemLoadId = attempt.item.GetUniqueLoadID();
                    PreserveOriginal(attempt);
                }
                Thing item = attempt.item;
                if (item == null || item.Destroyed)
                { return Fail(attempt, "RR_EvidenceCreation_OriginalMissing"); }
                if (!(item is Book book) || !CompRouteEvidence.IsSupportedCarrier(item) || item.GetUniqueLoadID() != attempt.itemLoadId ||
                    (item.holdingOwner != null && item.holdingOwner != held))
                { return Fail(attempt, "RR_EvidenceCreation_CustodyChanged"); }
                if (!item.TryGetComp<CompRouteEvidence>().Initialize(id))
                { return Fail(attempt, "RR_Company_ReceiptMismatch"); }
                if (!attempt.qualityComplete)
                {
                    if (attempt.qualityAttempted)
                    { return Fail(attempt, "RR_EvidenceCreation_InitializationInterrupted"); }
                    if (item.Spawned || item.holdingOwner != held)
                    { return Fail(attempt, "RR_EvidenceCreation_CustodyChanged"); }
                    CompQuality quality = item.TryGetComp<CompQuality>();
                    if (quality == null) { return Fail(attempt, "RR_Evidence_InvalidRecord"); }
                    attempt.qualityAttempted = true;
                    quality.SetQuality(QualityCategory.Normal, ArtGenerationContext.Outsider);
                    if (string.IsNullOrWhiteSpace(book.Title) || book.BookComp == null)
                    { return Fail(attempt, "RR_EvidenceCreation_InitializationInterrupted"); }
                    attempt.qualityComplete = true;
                }
                if (!item.Spawned)
                {
                    if (item.holdingOwner != held) { return Fail(attempt, "RR_EvidenceCreation_CustodyChanged"); }
                    if (!CellAvailable(item.def, map, cell)) { return Fail(attempt, "RR_Evidence_NoSafeSlot"); }
                    GenSpawn.Spawn(item, cell, map, WipeMode.VanishOrMoveAside);
                }
                if (!item.Spawned || item.Map != map || !map.listerThings.AllThings.Contains(item) ||
                    !item.Position.GetThingList(map).Contains(item))
                { PreserveOriginal(attempt); return Fail(attempt, "RR_EvidenceCreation_CustodyChanged"); }
                item.SetForbidden(false, false);
                CompanyActionResult result = campaign.RegisterRouteRecording(coordinate, item);
                if (!result.Success) { return Fail(attempt, result.MessageKey); }
                attempt.registered = true;
                attempt.failureKey = null;
                return result;
            }
            catch (Exception exception)
            {
                PreserveOriginal(attempt);
                Log.Warning("[Rimrooms][Evidence] Retained original creation attempt " + id + ": " + exception.GetType().Name);
                return Fail(attempt, attempt.qualityAttempted && !attempt.qualityComplete
                    ? "RR_EvidenceCreation_InitializationInterrupted" : "RR_EvidenceCreation_CreationInterrupted");
            }
            finally { busy = false; }
        }

        private void PreserveOriginal(EvidenceCreationAttempt attempt)
        {
            Thing item = attempt.item;
            try
            {
                if (item != null && !item.Destroyed && !item.Spawned && item.holdingOwner == null && !held.TryAdd(item, false))
                { faultKey = "RR_EvidenceCreation_InvalidSave"; }
            }
            catch (Exception exception)
            {
                faultKey = "RR_EvidenceCreation_InvalidSave";
                Log.Error("[Rimrooms][Evidence] Could not preserve the original carrier holder: " + exception.GetType().Name);
            }
        }

        private static bool CellAvailable(ThingDef definition, Map map, IntVec3 cell)
        {
            return definition != null && map != null && cell.IsValid && cell.InBounds(map) && cell.Standable(map) &&
                GenSpawn.CanSpawnAt(definition, cell, map, Rot4.North, false) &&
                cell.GetThingList(map).All(t => !(t is Pawn) && !(t is Corpse) && t.def.category != ThingCategory.Building &&
                    t.def.category != ThingCategory.Item && !GenSpawn.SpawningWipes(definition, t.def));
        }
        private static CompanyActionResult Fail(EvidenceCreationAttempt attempt, string key)
        { attempt.failureKey = key; return CompanyActionResult.Refused(key); }
    }
}
