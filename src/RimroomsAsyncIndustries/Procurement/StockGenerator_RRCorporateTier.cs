using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Procurement
{
    /// <summary>
    /// Sells one tier of the corporate catalogue, and sells nothing at all while that tier is
    /// locked.
    ///
    /// ## Why this is not a subclass of Core's category generator
    ///
    /// <see cref="StockGenerator_Category"/> would have been the obvious parent, but every one
    /// of its fields — the category, the count range, the exclusions — is **private**, so a
    /// subclass could neither read them nor reuse its generation. Reproducing the forty lines
    /// that matter is honest; inheriting a class whose state is invisible would have been a
    /// subclass in name only.
    ///
    /// The generation itself still goes through Core's own
    /// <see cref="StockGeneratorUtility.TryMakeForStock"/>, so stuff quality, stacking and
    /// stuff selection behave exactly as they do for every vanilla trader.
    ///
    /// ## Locked means invisible, not greyed out
    ///
    /// A locked tier yields no stock **and** reports that it handles none of its own
    /// definitions. That second half matters: `HandlesThingDef` is what decides whether the
    /// trader will *buy* a thing and at what price, so a tier that generated nothing but still
    /// claimed its category would quietly let a player sell into a catalogue they had not
    /// unlocked.
    /// </summary>
    public class StockGenerator_RRCorporateTier : StockGenerator
    {
        /// <summary>The tier this generator sells, by defName.</summary>
        public string tier;

        private RimroomsSupplyTierDef resolved;

        private RimroomsSupplyTierDef Tier
        {
            get
            {
                if (resolved == null && !string.IsNullOrEmpty(tier))
                { resolved = DefDatabase<RimroomsSupplyTierDef>.GetNamedSilentFail(tier); }
                return resolved;
            }
        }

        private bool Unlocked
        {
            get
            {
                RimroomsSupplyTierDef definition = Tier;
                if (definition == null) { return false; }
                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                return campaign != null && campaign.IsSupplyTierUnlocked(definition);
            }
        }

        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            RimroomsSupplyTierDef definition = Tier;
            if (definition == null || definition.category == null || !Unlocked) { yield break; }

            var generated = new List<ThingDef>();
            int wanted = definition.thingDefCountRange.RandomInRange;
            for (int index = 0; index < wanted; index++)
            {
                ThingDef chosen;
                if (!definition.category.DescendantThingDefs.Where(candidate =>
                        candidate.tradeability.TraderCanSell()
                        && (int)candidate.techLevel <= (int)definition.maxTechLevel
                        && !generated.Contains(candidate)
                        && (definition.excludedThingDefs == null
                            || !definition.excludedThingDefs.Contains(candidate)))
                    .TryRandomElement(out chosen))
                { break; }

                foreach (Thing thing in StockGeneratorUtility.TryMakeForStock(
                    chosen, RandomCountOf(chosen), faction))
                { yield return thing; }
                generated.Add(chosen);
            }
        }

        public override bool HandlesThingDef(ThingDef thingDef)
        {
            RimroomsSupplyTierDef definition = Tier;
            if (definition == null || definition.category == null || thingDef == null) { return false; }
            if (!Unlocked) { return false; }
            if (!definition.category.DescendantThingDefs.Contains(thingDef)) { return false; }
            if (thingDef.tradeability == Tradeability.None) { return false; }
            if ((int)thingDef.techLevel > (int)definition.maxTechLevel) { return false; }
            return definition.excludedThingDefs == null
                || !definition.excludedThingDefs.Contains(thingDef);
        }

        public override IEnumerable<string> ConfigErrors(TraderKindDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
            if (string.IsNullOrEmpty(tier))
            { yield return "StockGenerator_RRCorporateTier on " + parentDef.defName + " names no tier."; }
        }
    }
}
