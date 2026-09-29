using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Procurement
{
    /// <summary>
    /// One tier of the parent corporation's catalogue, and the three locks in front of it.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"and ther should be a trader that is the multi
    /// trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies like
    /// a universersal trader but things are tech and company quest locked out till passed"*, and
    /// then *"and even cost credits to unlock item and materials and equipment gates in buying"*.
    ///
    /// ## Three locks, and why all three earn their place
    ///
    /// A tier opens only when **all** of these are satisfied, and each one gates a different
    /// kind of progress, which is why none of them is redundant:
    ///
    /// 1. **Research** — you have to understand it. Ordinary tech progression.
    /// 2. **A company contract** — you have to have *done something for them*. This reuses the
    ///    existing contract record rather than inventing a quest system, so an odd-goods supply
    ///    contract or a survey can be the thing that earns a tier.
    /// 3. **Credits** — you have to pay for access, not just for the goods. This is the lock
    ///    that makes the bond layer matter beyond storage: a vault full of paper is now
    ///    *spendable on capability* rather than only on stock.
    ///
    /// Any of the three may be left empty, which makes a tier open from the start. The first
    /// tier is deliberately like that: a corporation that sells you nothing until you have
    /// already succeeded is not a supplier, it is a wall.
    ///
    /// ## Universal by category, not by hand-listed item
    ///
    /// The owner asked for *"all kinds of equipenmnt tools amaterials and supplies like a
    /// universersal trader"*. Each tier names a **`ThingCategoryDef`**, so it sells whatever the
    /// loaded game puts in that category — Core, DLC and any of the other 274 mods alike —
    /// without this mod listing a single item or inventing one. A profile that adds new metals
    /// sells new metals here the day it is installed.
    /// </summary>
    public sealed class RimroomsSupplyTierDef : Def
    {
        /// <summary>Order shown to the player. Lower opens earlier.</summary>
        public int tierIndex;

        /// <summary>
        /// Research that must be finished. Empty means no research lock.
        /// Resolved by name so a DLC-only project degrades to "unavailable" rather than a load error.
        /// </summary>
        public string requiredResearchDefName;

        /// <summary>
        /// A contract template that must have been completed. Empty means no contract lock.
        /// Matched against <c>ContractRecord.templateId</c>, so the company's existing work is
        /// what earns access rather than a parallel quest system.
        /// </summary>
        public string requiredContractTemplateId;

        /// <summary>Credits charged once to open this tier. Zero means no credit lock.</summary>
        public long unlockCostCredits;

        /// <summary>What this tier sells. Everything the loaded game puts in the category.</summary>
        public ThingCategoryDef category;

        /// <summary>How many distinct definitions appear in a single visit.</summary>
        public IntRange thingDefCountRange = new IntRange(3, 6);

        /// <summary>Definitions this tier never sells, whatever the category says.</summary>
        public List<ThingDef> excludedThingDefs;

        /// <summary>Highest tech level this tier will generate or buy.</summary>
        public TechLevel maxTechLevel = TechLevel.Archotech;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (category == null)
            { yield return "RimroomsSupplyTierDef " + defName + " has no category, so it can sell nothing."; }
            if (unlockCostCredits < 0L)
            { yield return "RimroomsSupplyTierDef " + defName + " has a negative unlock cost."; }
        }
    }
}
