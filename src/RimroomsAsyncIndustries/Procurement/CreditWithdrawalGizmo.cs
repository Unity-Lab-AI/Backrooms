using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Procurement
{
    /// <summary>
    /// Drawing credits out of the company account as physical paper — the counterpart to
    /// banking them at a beacon.
    ///
    /// The amounts offered are **the denomination ladder itself**, filtered to what the account
    /// can actually cover. That means there is no number to type, no slider to drag, and no way
    /// to ask for an amount that cannot be represented: pick a rung, get exactly one bond of
    /// that size. Asking for more than one is asking twice, which is honest about what is
    /// happening — the corporation is printing a specific instrument, not dispensing change.
    ///
    /// Withdrawing a larger sum than any single rung is what
    /// <see cref="RimroomsCampaignComponent.IssueBonds"/> is for, and it pays out largest-first
    /// as the owner required. This gizmo is the common case: one piece of paper, chosen.
    /// </summary>
    public static class CreditWithdrawalGizmo
    {
        public static IEnumerable<Gizmo> For(Thing console)
        {
            if (console == null || !console.Spawned || console.Faction != Faction.OfPlayer)
            { yield break; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { yield break; }

            var withdraw = new Command_Action
            {
                defaultLabel = "RR_Bond_Withdraw".Translate(),
                defaultDesc = "RR_Bond_WithdrawDesc".Translate(campaign.BalanceUsd.ToString("N0")),
                icon = TexCommand.ForbidOff,
                action = delegate
                {
                    Find.WindowStack.Add(new FloatMenu(Options(campaign, console)));
                },
            };
            if (campaign.BalanceUsd < CreditDenominations.Smallest)
            { withdraw.Disable("RR_Bond_BelowSmallest".Translate()); }
            yield return withdraw;
        }

        private static List<FloatMenuOption> Options(RimroomsCampaignComponent campaign, Thing console)
        {
            var options = new List<FloatMenuOption>();
            IReadOnlyList<long> ladder = CreditDenominations.Values;

            // Largest first, so the rung a player most likely wants is at the top rather than
            // eleven rows down.
            for (int index = ladder.Count - 1; index >= 0; index--)
            {
                long denomination = ladder[index];
                if (denomination > campaign.BalanceUsd) { continue; }
                long captured = denomination;
                options.Add(new FloatMenuOption(
                    "RR_Bond_WithdrawOne".Translate(CreditDenominations.ShortName(denomination)),
                    delegate
                    {
                        int issued;
                        long kept;
                        CompanyActionResult result = campaign.IssueBonds(
                            console.Map, console.Position, captured, out issued, out kept);
                        Messages.Message(
                            result.Success
                                ? "RR_Bond_Withdrawn".Translate(
                                    issued.ToString("N0"),
                                    CreditDenominations.ShortName(captured))
                                : (result.MessageKey ?? "RR_Bond_Unfunded").Translate(),
                            console,
                            result.Success ? MessageTypeDefOf.PositiveEvent : MessageTypeDefOf.RejectInput,
                            false);
                    }));
            }

            if (options.Count == 0)
            { options.Add(new FloatMenuOption("RR_Bond_BelowSmallest".Translate(), null)); }
            return options;
        }
    }
}
