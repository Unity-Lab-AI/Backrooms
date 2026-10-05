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

        /// <summary>
        /// Whether the account can cover the tier's access fee.
        ///
        /// **Asked through <see cref="SupplyFeeFor"/> so the test and the charge cannot disagree.**
        /// A player who scaled the fees down and was still told they could not afford a tier would
        /// be reading one number while the ledger used another.
        /// </summary>
        public bool SupplyTierAffordable(RimroomsSupplyTierDef tier)
        {
            return tier != null && BalanceUsd >= SupplyFeeFor(tier);
        }

        /// <summary>
        /// What a tier actually costs: its authored fee, scaled by the player's own multiplier.
        ///
        /// Owner, 2026-10-05: *"Make them player-visible settings"*. The authored figure stays the
        /// design -- the relative cost of the five tiers is the decision -- and the multiplier is
        /// how somebody playing moves the whole ladder without a rebuild. Rounded away from zero
        /// so a scaled-down fee never becomes free by accident.
        /// </summary>
        public static long SupplyFeeFor(RimroomsSupplyTierDef tier)
        {
            if (tier == null) { return 0L; }
            Core.RimroomsSettings tuning = Core.RimroomsMod.Settings;
            if (tuning == null) { return tier.unlockCostCredits; }
            double scaled = (double)tier.unlockCostCredits * tuning.EffectiveSupplyFeeMultiplier;
            if (scaled <= 0d) { return tier.unlockCostCredits > 0L ? 1L : 0L; }
            return (long)System.Math.Round(scaled);
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
            // **CHARGED THROUGH THE SAME HELPER THE AFFORDABILITY TEST USES.** Reading
            // `unlockCostCredits` here while the test read the scaled figure is exactly the
            // half-wiring this project keeps meeting: the button would offer a tier at one price
            // and the ledger would take another.
            long fee = SupplyFeeFor(tier);
            if (fee > 0L)
            {
                CompanyActionResult paid = PostTransaction(operationId, -fee,
                    "RR_Ledger_SupplyTierUnlocked", tier.defName);
                if (!paid.Success) { return paid; }
            }

            unlockedSupplyTiers = unlockedSupplyTiers ?? new List<string>();
            if (!unlockedSupplyTiers.Contains(tier.defName))
            { unlockedSupplyTiers.Add(tier.defName); }
            // The figure RECORDED is the figure CHARGED, so the ledger and the event agree.
            RecordEvent("RR_Event_SupplyTierUnlocked", tier.defName,
                tier.LabelCap.ToString(), fee.ToString("N0"));
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
