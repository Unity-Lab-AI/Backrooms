using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    /// <summary>Only a player-designated existing bench supplies the branch laboratory role.</summary>
    public sealed class RimroomsLaboratoryComponent : GameComponent
    {
        public const int CurrentSchemaVersion = 1;
        private int schemaVersion = CurrentSchemaVersion;
        private string branchId;
        private Map headquarters;
        private Building_ResearchBench bench;
        private string benchLoadId;
        private string benchDefName;
        private string providerPackageId;
        private string labelAtDesignation;
        private int revision;
        private string faultKey;

        public RimroomsLaboratoryComponent(Game game) { }
        public Building_ResearchBench DesignatedBench { get { return bench; } }
        public string BenchLoadId { get { return benchLoadId; } }
        public string BenchDefName { get { return benchDefName; } }
        public string ProviderPackageId { get { return providerPackageId; } }
        public string LabelAtDesignation { get { return labelAtDesignation; } }
        public bool HasDesignation { get { return !string.IsNullOrEmpty(benchLoadId); } }
        public int Revision { get { return revision; } }
        public string FaultKey { get { return faultKey; } }
        private RimroomsCampaignComponent Campaign
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_laboratorySchema", 1, true);
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_References.Look(ref headquarters, "rr_headquarters");
            Scribe_References.Look(ref bench, "rr_bench");
            Scribe_Values.Look(ref benchLoadId, "rr_benchLoadId");
            Scribe_Values.Look(ref benchDefName, "rr_benchDefName");
            Scribe_Values.Look(ref providerPackageId, "rr_providerPackageId");
            Scribe_Values.Look(ref labelAtDesignation, "rr_labelAtDesignation");
            Scribe_Values.Look(ref revision, "rr_revision");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                faultKey = null;
                if (schemaVersion != CurrentSchemaVersion) { faultKey = "RR_Lab_UnsupportedSchema"; }
                else if (revision < 0 || (HasDesignation && (string.IsNullOrEmpty(branchId) ||
                    string.IsNullOrEmpty(benchDefName) || string.IsNullOrEmpty(providerPackageId))) ||
                    (bench != null && (!HasDesignation || bench.GetUniqueLoadID() != benchLoadId)))
                { faultKey = "RR_Lab_InvalidSave"; }
                // Missing/despawned providers remain recorded. Loading never assigns a replacement.
            }
        }

        public static bool IsSupportedBench(Thing candidate)
        {
            if (!(candidate is Building_ResearchBench) || candidate.def == null ||
                candidate.def.modContentPack == null || !candidate.def.modContentPack.IsCoreMod) { return false; }
            return (candidate.def.defName == "SimpleResearchBench" || candidate.def.defName == "HiTechResearchBench") &&
                candidate.def == DefDatabase<ThingDef>.GetNamedSilentFail(candidate.def.defName);
        }

        private CompanyActionResult CheckBranch(RimroomsCampaignComponent campaign)
        {
            if (faultKey != null) { return CompanyActionResult.Refused(faultKey); }
            if (schemaVersion != CurrentSchemaVersion) { return CompanyActionResult.Refused("RR_Lab_UnsupportedSchema"); }
            if (campaign == null || !campaign.CanOperate || (!string.IsNullOrEmpty(branchId) && branchId != campaign.BranchId))
            { return CompanyActionResult.Refused("RR_Lab_BranchUnavailable"); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult CanDesignate(Thing candidate)
        {
            RimroomsCampaignComponent campaign = Campaign;
            CompanyActionResult branch = CheckBranch(campaign);
            if (!branch.Success) { return branch; }
            return PhysicalProviderStatus(candidate, campaign);
        }

        private static CompanyActionResult PhysicalProviderStatus(Thing candidate, RimroomsCampaignComponent campaign)
        {
            if (!IsSupportedBench(candidate)) { return CompanyActionResult.Refused("RR_Lab_UnsupportedBench"); }
            if (candidate.Destroyed || !candidate.Spawned || (candidate.def.useHitPoints && candidate.HitPoints <= 0))
            { return CompanyActionResult.Refused("RR_Lab_ProviderMissing"); }
            Map map = campaign.Headquarters;
            if (map == null || !Find.Maps.Contains(map) || !map.IsPlayerHome || candidate.Map != map)
            { return CompanyActionResult.Refused("RR_Lab_WrongHeadquarters"); }
            if (candidate.Faction != Faction.OfPlayer) { return CompanyActionResult.Refused("RR_Lab_NotOwned"); }
            if (candidate.Position.Fogged(map)) { return CompanyActionResult.Refused("RR_Lab_NotVisible"); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult DesignateBench(Thing candidate)
        {
            CompanyActionResult check = CanDesignate(candidate);
            if (!check.Success) { return check; }
            if (bench == candidate && benchLoadId == candidate.GetUniqueLoadID() && headquarters == Campaign.Headquarters &&
                benchDefName == candidate.def.defName && providerPackageId == candidate.def.modContentPack.PackageId)
            { return CompanyActionResult.Existing(); }
            if (revision == int.MaxValue) { return CompanyActionResult.Refused("RR_Lab_InvalidSave"); }
            branchId = Campaign.BranchId;
            headquarters = Campaign.Headquarters;
            bench = (Building_ResearchBench)candidate;
            benchLoadId = bench.GetUniqueLoadID();
            benchDefName = bench.def.defName;
            providerPackageId = bench.def.modContentPack.PackageId;
            labelAtDesignation = bench.LabelCap.ToString();
            revision++;
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult ClearDesignation()
        {
            CompanyActionResult check = CheckBranch(Campaign);
            if (!check.Success) { return check; }
            if (!HasDesignation) { return CompanyActionResult.Existing(); }
            if (revision == int.MaxValue) { return CompanyActionResult.Refused("RR_Lab_InvalidSave"); }
            bench = null;
            benchLoadId = null;
            benchDefName = null;
            providerPackageId = null;
            labelAtDesignation = null;
            headquarters = Campaign.Headquarters;
            revision++;
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult Readiness()
        {
            RimroomsCampaignComponent campaign = Campaign;
            CompanyActionResult check = CheckBranch(campaign);
            if (!check.Success) { return check; }
            if (!HasDesignation) { return CompanyActionResult.Refused("RR_Lab_NotDesignated"); }
            if (bench == null || bench.Destroyed) { return CompanyActionResult.Refused("RR_Lab_ProviderMissing"); }
            if (headquarters != campaign.Headquarters) { return CompanyActionResult.Refused("RR_Lab_WrongHeadquarters"); }
            if (bench.GetUniqueLoadID() != benchLoadId || bench.def == null || bench.def.defName != benchDefName ||
                bench.def.modContentPack == null || bench.def.modContentPack.PackageId != providerPackageId)
            { return CompanyActionResult.Refused("RR_Lab_IdentityChanged"); }
            check = PhysicalProviderStatus(bench, campaign);
            if (!check.Success) { return check; }
            if (bench.IsForbidden(Faction.OfPlayer)) { return CompanyActionResult.Refused("RR_Lab_Forbidden"); }
            if (!bench.def.hasInteractionCell || !bench.InteractionCell.IsValid || !bench.InteractionCell.InBounds(bench.Map) ||
                !bench.InteractionCell.Standable(bench.Map) || bench.InteractionCell.Fogged(bench.Map))
            { return CompanyActionResult.Refused("RR_Lab_InteractionBlocked"); }
            if (bench.IsBrokenDown()) { return CompanyActionResult.Refused("RR_Lab_Broken"); }
            if (!FlickUtility.WantsToBeOn(bench)) { return CompanyActionResult.Refused("RR_Lab_SwitchedOff"); }
            CompPowerTrader power = bench.TryGetComp<CompPowerTrader>();
            if ((bench.def.defName == "HiTechResearchBench" && power == null) || (power != null &&
                (!power.PowerOn || bench.Map.gameConditionManager.ElectricityDisabled(bench.Map))))
            { return CompanyActionResult.Refused("RR_Lab_NoPower"); }
            return CompanyActionResult.Applied();
        }

        public bool IsReadyBench(Thing candidate, RimroomsCampaignComponent campaign)
        {
            return candidate != null && campaign != null && campaign == Campaign && candidate == bench && Readiness().Success;
        }

        public IEnumerable<Building_ResearchBench> AvailableBenches()
        {
            RimroomsCampaignComponent campaign = Campaign;
            if (!CheckBranch(campaign).Success || campaign.Headquarters == null || !Find.Maps.Contains(campaign.Headquarters))
            { yield break; }
            foreach (Building candidate in campaign.Headquarters.listerBuildings.allBuildingsColonist)
            {
                if (PhysicalProviderStatus(candidate, campaign).Success) { yield return (Building_ResearchBench)candidate; }
            }
        }
    }
}
