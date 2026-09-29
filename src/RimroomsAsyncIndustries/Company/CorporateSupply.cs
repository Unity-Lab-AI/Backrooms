using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Procurement;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The company's side of the parent corporation's catalogue: which tiers are open, what it
    /// costs to open one, and calling the supplier in.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"ther should be a trader that is the multi
    /// trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies
    /// like a universersal trader but things are tech and company quest locked out till passed"*
    /// and *"and even cost credits to unlock item and materials and equipment gates in buying"*.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>Saved. Tier defNames the branch has paid for and opened.</summary>
        private List<string> unlockedSupplyTiers = new List<string>();

        internal void ExposeCorporateSupply()
        {
            Scribe_Collections.Look(ref unlockedSupplyTiers, "rr_unlockedSupplyTiers", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && unlockedSupplyTiers == null)
            { unlockedSupplyTiers = new List<string>(); }
        }

        /// <summary>Every tier the game has loaded, in the order the player should meet them.</summary>
        public static List<RimroomsSupplyTierDef> AllSupplyTiers()
        {
            var tiers = DefDatabase<RimroomsSupplyTierDef>.AllDefsListForReading.ToList();
            tiers.Sort((left, right) => left.tierIndex.CompareTo(right.tierIndex));
            return tiers;
        }

        /// <summary>Whether a tier is open for business.</summary>
        public bool IsSupplyTierUnlocked(RimroomsSupplyTierDef tier)
        {
            if (tier == null) { return false; }
            // A tier with no locks at all is open from the start. A corporation that sells you
            // nothing until you have already succeeded is not a supplier, it is a wall.
            if (!HasAnyLock(tier)) { return true; }
            return unlockedSupplyTiers != null && unlockedSupplyTiers.Contains(tier.defName);
        }

        private static bool HasAnyLock(RimroomsSupplyTierDef tier)
        {
            return !string.IsNullOrEmpty(tier.requiredResearchDefName)
                || !string.IsNullOrEmpty(tier.requiredContractTemplateId)
                || tier.unlockCostCredits > 0L;
        }

        /// <summary>Whether the research lock is satisfied. True when there is no research lock.</summary>
        public bool SupplyTierResearchMet(RimroomsSupplyTierDef tier)
        {
            if (tier == null || string.IsNullOrEmpty(tier.requiredResearchDefName)) { return true; }
            ResearchProjectDef project =
                DefDatabase<ResearchProjectDef>.GetNamedSilentFail(tier.requiredResearchDefName);
            // A project that does not exist -- a DLC one on a Core-only install -- leaves the
            // tier shut rather than silently opening it. Saying "unavailable" is honest; opening
            // a gate because its key is missing is not.
            return project != null && project.IsFinished;
        }

        /// <summary>Whether the contract lock is satisfied. True when there is no contract lock.</summary>
        public bool SupplyTierContractMet(RimroomsSupplyTierDef tier)
        {
            if (tier == null || string.IsNullOrEmpty(tier.requiredContractTemplateId)) { return true; }
            return contracts.Any(record => record != null
                && record.status == ContractStatus.Completed
                && string.Equals(record.templateId, tier.requiredContractTemplateId,
                    StringComparison.Ordinal));
        }

        /// <summary>Whether the account can cover the tier's access fee.</summary>
        public bool SupplyTierAffordable(RimroomsSupplyTierDef tier)
        {
            return tier != null && BalanceUsd >= tier.unlockCostCredits;
        }

        /// <summary>
        /// Opens a tier, charging its access fee once.
        ///
        /// **All three locks are re-checked here**, not just the one the caller thought was
        /// outstanding. A UI that offered the button is not evidence that the conditions still
        /// hold — research can be lost to a mod, a contract record can be edited by a save fix,
        /// and the balance can change between the menu opening and the click landing.
        /// </summary>
        internal CompanyActionResult UnlockSupplyTier(RimroomsSupplyTierDef tier)
        {
            if (tier == null) { return CompanyActionResult.Refused("RR_Supply_UnknownTier"); }
            if (IsSupplyTierUnlocked(tier)) { return CompanyActionResult.Existing(); }
            if (!SupplyTierResearchMet(tier)) { return CompanyActionResult.Refused("RR_Supply_ResearchLocked"); }
            if (!SupplyTierContractMet(tier)) { return CompanyActionResult.Refused("RR_Supply_ContractLocked"); }
            if (!SupplyTierAffordable(tier)) { return CompanyActionResult.Refused("RR_Supply_Unaffordable"); }

            string operationId = "rr.supply.unlock." + tier.defName;
            if (tier.unlockCostCredits > 0L)
            {
                CompanyActionResult paid = PostTransaction(operationId, -tier.unlockCostCredits,
                    "RR_Ledger_SupplyTierUnlocked", tier.defName);
                if (!paid.Success) { return paid; }
            }

            unlockedSupplyTiers = unlockedSupplyTiers ?? new List<string>();
            if (!unlockedSupplyTiers.Contains(tier.defName))
            { unlockedSupplyTiers.Add(tier.defName); }
            RecordEvent("RR_Event_SupplyTierUnlocked", tier.defName,
                tier.LabelCap.ToString(), tier.unlockCostCredits.ToString("N0"));
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Calls the corporation in. Uses Core's own passing-ship manager, so the trade window,
        /// the caravan-free delivery and the goods-must-be-near-a-beacon rule are all vanilla
        /// behaviour rather than anything reimplemented here.
        /// </summary>
        internal CompanyActionResult RequestCorporateSupplier(Map map)
        {
            if (map == null) { return CompanyActionResult.Refused("RR_Supply_NoMap"); }
            TraderKindDef kind = DefDatabase<TraderKindDef>.GetNamedSilentFail("RR_CorporateSupply");
            if (kind == null) { return CompanyActionResult.Refused("RR_Supply_UnknownTier"); }
            if (map.passingShipManager == null) { return CompanyActionResult.Refused("RR_Supply_NoMap"); }
            if (map.passingShipManager.passingShips.Any(passing =>
                    passing is TradeShip && ((TradeShip)passing).def == kind))
            { return CompanyActionResult.Refused("RR_Supply_AlreadyHere"); }

            var supplier = new TradeShip(kind);
            map.passingShipManager.AddShip(supplier);
            supplier.GenerateThings();
            RecordEvent("RR_Event_CorporateSupplierCalled", branchId ?? "branch");
            return CompanyActionResult.Applied();
        }
    }
}
