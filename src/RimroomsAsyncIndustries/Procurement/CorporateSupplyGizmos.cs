using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Procurement
{
    /// <summary>
    /// The player's way into the corporate catalogue: call the supplier in, and open tiers.
    ///
    /// Offered on the designated gate console rather than on a new building, because the
    /// console is already the thing a branch talks to the company through. **No new building,
    /// no new bench, no new UI window** — a gizmo and a float menu, which is the lightest
    /// surface that can carry the three locks legibly.
    /// </summary>
    public static class CorporateSupplyGizmos
    {
        public static IEnumerable<Gizmo> For(Thing console)
        {
            if (console == null || !console.Spawned || console.Faction != Faction.OfPlayer)
            { yield break; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { yield break; }

            yield return new Command_Action
            {
                defaultLabel = "RR_Supply_Hail".Translate(),
                defaultDesc = "RR_Supply_HailDesc".Translate(),
                icon = TexCommand.ForbidOff,
                action = delegate
                {
                    CompanyActionResult result = campaign.RequestCorporateSupplier(console.Map);
                    Messages.Message(
                        result.Success
                            ? "RR_Supply_Hailed".Translate()
                            : (result.MessageKey ?? "RR_Supply_NoMap").Translate(),
                        console,
                        result.Success ? MessageTypeDefOf.PositiveEvent : MessageTypeDefOf.RejectInput,
                        false);
                },
            };

            yield return new Command_Action
            {
                defaultLabel = "RR_Supply_Catalogue".Translate(),
                defaultDesc = "RR_Supply_CatalogueDesc".Translate(),
                icon = TexCommand.ForbidOff,
                action = delegate { Find.WindowStack.Add(new FloatMenu(TierOptions(campaign))); },
            };
        }

        /// <summary>
        /// One row per tier. A locked row **says which lock is holding it**, rather than being
        /// greyed out with no explanation — three separate conditions are exactly the case where
        /// "you cannot do this" is a useless message.
        /// </summary>
        private static List<FloatMenuOption> TierOptions(RimroomsCampaignComponent campaign)
        {
            var options = new List<FloatMenuOption>();
            List<RimroomsSupplyTierDef> tiers = RimroomsCampaignComponent.AllSupplyTiers();
            if (tiers.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_Supply_NoTiers".Translate(), null));
                return options;
            }

            for (int index = 0; index < tiers.Count; index++)
            {
                RimroomsSupplyTierDef tier = tiers[index];
                if (campaign.IsSupplyTierUnlocked(tier))
                {
                    options.Add(new FloatMenuOption(
                        "RR_Supply_TierOpen".Translate(tier.LabelCap), null));
                    continue;
                }

                if (!campaign.SupplyTierResearchMet(tier))
                {
                    // **THIS ROW USED TO PRINT THE RAW defName AT THE PLAYER** -- an internal
                    // identifier the game shows nowhere else -- behind a null action, so the one
                    // screen that said *you need a research project* named it unrecognisably and
                    // offered no way to go and look at it. Owner: *"Make each screen deep-link to
                    // the relevant ... research project"*.
                    //
                    // The row is only clickable when the project is actually loaded. A tier
                    // locked behind DLC research on a Core-only install still SAYS so -- the
                    // label falls back to the name -- and simply does not offer a link to
                    // somewhere that does not exist.
                    ResearchProjectDef required =
                        UI.OperationsLinks.ResearchNamed(tier.requiredResearchDefName);
                    options.Add(new FloatMenuOption(
                        "RR_Supply_TierResearch".Translate(tier.LabelCap,
                            UI.OperationsLinks.ResearchLabel(tier.requiredResearchDefName)),
                        required == null
                            ? (Action)null
                            : delegate { UI.OperationsLinks.ShowResearch(required); }));
                    continue;
                }
                if (!campaign.SupplyTierContractMet(tier))
                {
                    options.Add(new FloatMenuOption("RR_Supply_TierContract".Translate(
                        tier.LabelCap), null));
                    continue;
                }
                if (!campaign.SupplyTierAffordable(tier))
                {
                    options.Add(new FloatMenuOption("RR_Supply_TierCost".Translate(
                        tier.LabelCap, tier.unlockCostCredits.ToString("N0")), null));
                    continue;
                }

                RimroomsSupplyTierDef captured = tier;
                options.Add(new FloatMenuOption(
                    "RR_Supply_TierUnlock".Translate(tier.LabelCap,
                        tier.unlockCostCredits.ToString("N0")),
                    delegate
                    {
                        CompanyActionResult result = campaign.UnlockSupplyTier(captured);
                        Messages.Message(
                            result.Success
                                ? "RR_Supply_TierUnlocked".Translate(captured.LabelCap)
                                : (result.MessageKey ?? "RR_Supply_UnknownTier").Translate(),
                            result.Success ? MessageTypeDefOf.PositiveEvent : MessageTypeDefOf.RejectInput,
                            false);
                    }));
            }
            return options;
        }
    }
}
