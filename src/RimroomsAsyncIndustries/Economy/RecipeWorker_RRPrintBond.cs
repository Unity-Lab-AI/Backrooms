using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// Prints one bond of a fixed denomination at a bench, against the company account.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"a production bench with buills for makeing
    /// the differnt sizes"*.
    ///
    /// ## Why the recipe produces nothing and this worker mints instead
    ///
    /// A bond's value lives per instance, in a comp. A recipe's <c>products</c> list can only
    /// name a <see cref="ThingDef"/> and a count, and the hook that post-processes a finished
    /// product — <c>GenRecipe.PostProcessProduct</c> — is **private and static**, so there is no
    /// supported way to reach in and stamp a value on something a bill just made. Working around
    /// that would mean Harmony, which this mod does not use.
    ///
    /// So the recipe declares no products at all and this worker mints the bond itself in
    /// <see cref="Notify_IterationCompleted"/>, which **is** a documented virtual. That makes the
    /// outcome fully deterministic — the denomination comes from the recipe that is running, not
    /// from guessing which object on the floor was the one just made — and it means a failure to
    /// pay simply produces nothing rather than an unstamped book worth free market value.
    ///
    /// ## Paying for it
    ///
    /// The face value is debited from the company ledger through the campaign component's own
    /// idempotent transaction, keyed per bill iteration and tick. **If the balance will not
    /// cover it, no bond is made.** Printing paper the company cannot back would be printing
    /// money, which is the one thing this whole layer exists to prevent.
    /// </summary>
    public class RecipeWorker_RRPrintBond : RecipeWorker
    {
        /// <summary>
        /// The denomination this recipe prints, read from the trailing number of its defName —
        /// <c>RR_PrintBond_1000</c> prints a thousand-credit bond.
        ///
        /// Derived rather than declared in a def extension so that adding a rung to the ladder
        /// needs one more RecipeDef and no code at all. The ladder is the source of truth and
        /// the recipe name has to sit on it, or nothing is printed.
        /// </summary>
        public long Denomination
        {
            get
            {
                if (recipe == null || string.IsNullOrEmpty(recipe.defName)) { return 0L; }
                int split = recipe.defName.LastIndexOf('_');
                if (split < 0 || split + 1 >= recipe.defName.Length) { return 0L; }
                long parsed;
                if (!long.TryParse(recipe.defName.Substring(split + 1), out parsed)) { return 0L; }
                return CreditDenominations.IsDenomination(parsed) ? parsed : 0L;
            }
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            base.Notify_IterationCompleted(billDoer, ingredients);

            long denomination = Denomination;
            if (denomination <= 0L)
            {
                Log.ErrorOnce("[Rimrooms] bond recipe " +
                    (recipe == null ? "(null)" : recipe.defName) +
                    " does not name a denomination on the ladder; nothing printed.",
                    0x52526230);
                return;
            }

            Map map = billDoer == null ? null : billDoer.Map;
            if (map == null) { return; }

            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return; }

            string operationId = "rr.bond.print." +
                (recipe == null ? "?" : recipe.defName) + "." +
                (Find.TickManager == null ? 0 : Find.TickManager.TicksGame) + "." +
                billDoer.thingIDNumber.ToString();

            // Debit first. A bond that exists without the account having paid for it is
            // counterfeit, and the only safe order is to take the money before printing.
            CompanyActionResult paid = campaign.WithdrawForBond(operationId, denomination);
            if (!paid.Success)
            {
                Messages.Message("RR_Bond_PrintUnfunded".Translate(
                        CreditDenominations.ShortName(denomination)),
                    billDoer, MessageTypeDefOf.RejectInput, false);
                return;
            }

            Thing bond = BondService.MakeBond(denomination);
            if (bond == null || !GenPlace.TryPlaceThing(bond, billDoer.Position, map, ThingPlaceMode.Near))
            {
                // Could not place the paper. Put the money straight back rather than charging
                // for something that does not exist.
                if (bond != null && !bond.Destroyed) { bond.Destroy(DestroyMode.Vanish); }
                campaign.RefundBond(operationId + ".refund", denomination);
                return;
            }
        }
    }
}
