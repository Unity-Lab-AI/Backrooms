using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    public sealed class CompProperties_RimroomsCreditBeacon : CompProperties
    {
        /// <summary>Cells from the beacon that count. Matches Core's trade beacon radius.</summary>
        public float radius = 7.9f;

        public CompProperties_RimroomsCreditBeacon()
        {
            compClass = typeof(CompRimroomsCreditBeacon);
        }
    }

    /// <summary>
    /// Turns a Core orbital trade beacon into a credit beacon: it reports the bonds in its
    /// radius and can bank them.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"like orbital beacons to beable to show that
    /// available credits"*.
    ///
    /// ## Why this reuse is the right one
    ///
    /// A trade beacon already means exactly this to a player: *the valuables inside this circle
    /// are the ones that count*. Nobody has to learn a new idea, the radius is already drawn on
    /// the ground by Core when you select it, and the habit of stacking things near a beacon is
    /// one players already have. It was the owner's own suggestion and it lands perfectly.
    ///
    /// The comp is **dormant until designated**, exactly like the gate and emergence comps on
    /// Core doors. An unrelated trade beacon in somebody's existing colony behaves as it always
    /// has and shows nothing, because installing this mod must never change a colony that was
    /// not asking for it.
    ///
    /// ## What it does not do
    ///
    /// It does not trade, does not talk to orbital ships, and does not alter how Core's own
    /// beacon behaviour works. It reads bonds and, on an explicit order, banks them.
    /// </summary>
    public sealed class CompRimroomsCreditBeacon : ThingComp
    {
        /// <summary>Saved. A beacon does nothing until the player says it is a credit beacon.</summary>
        private bool designated;

        private CompProperties_RimroomsCreditBeacon Props
        {
            get { return (CompProperties_RimroomsCreditBeacon)props; }
        }

        public bool Designated { get { return designated; } }

        /// <summary>
        /// The radius that counts, exposed so other subsystems can ask the beacon rather than
        /// re-reading its props.
        ///
        /// Added when quest-book collection needed the same circle. **The alternative was each
        /// caller reaching into `Props.radius` itself**, which is two readers of one number and the
        /// kind of thing that drifts the first time the default changes.
        /// </summary>
        public float Radius { get { return Props.radius; } }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref designated, "rr_creditBeacon", false);
        }

        /// <summary>Face value of every bond inside the radius right now.</summary>
        public long AvailableCredits
        {
            get
            {
                if (!designated || parent == null || !parent.Spawned) { return 0L; }
                long total;
                BondService.BondsInRadius(parent.Map, parent.Position, Props.radius, out total);
                return total;
            }
        }

        /// <summary>
        /// What this beacon is doing, and — the half the audit added — why it is doing nothing.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"we also need to be making sure all mod
        /// ingame decriptions and informational informations for everything is properly in the
        /// cards like the game does currently"*. The row's standard is *"What it is, what it
        /// needs, and why it is not working when it is not."*
        ///
        /// ## The gap
        ///
        /// This read `if (!designated) { return null; }` and stopped. **So the beacon was silent
        /// in precisely the state where a player needs to be told something**: bonds piled up
        /// inside its radius, nothing banking them, and no indication anywhere on the thing that
        /// one toggle away is the answer. A card that explains itself only once it is already
        /// working explains itself only to people who did not need it.
        ///
        /// ## Why it is still silent almost always, which is the constraint
        ///
        /// This comp is on Core's `OrbitalTradeBeacon`, so **every trade beacon in every colony
        /// in the game carries it**, and the dormant-until-designated rule that governs the gate,
        /// emergence and survivor comps governs this one too: installing this mod must not add a
        /// line to a building somebody already owns.
        ///
        /// So an undesignated beacon speaks **only when there is actually something for it to
        /// bank** — bonds of this branch's, inside this beacon's own radius, right now. That is
        /// the exact moment the information is worth having and no earlier, and a colony with no
        /// company bonds in range never sees it.
        /// </summary>
        public override string CompInspectStringExtra()
        {
            if (designated)
            {
                return "RR_CreditBeacon_Inspect".Translate(AvailableCredits.ToString("N0")).ToString();
            }
            if (parent == null || !parent.Spawned) { return null; }
            long waiting;
            BondService.BondsInRadius(parent.Map, parent.Position, Props.radius, out waiting);
            if (waiting <= 0L) { return null; }
            return "RR_CreditBeacon_Undesignated".Translate(waiting.ToString("N0")).ToString();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (parent == null || !parent.Spawned || parent.Faction != Faction.OfPlayer)
            { yield break; }

            yield return new Command_Toggle
            {
                defaultLabel = "RR_CreditBeacon_Designate".Translate(),
                defaultDesc = "RR_CreditBeacon_DesignateDesc".Translate(),
                icon = TexCommand.ForbidOff,
                isActive = () => designated,
                toggleAction = () => { designated = !designated; },
            };

            if (!designated) { yield break; }

            // Banking and selling both post to the company account, so they are offered only where
            // there is a working account to post to. A save with no branch would otherwise destroy
            // the goods and refuse the credit.
            if (campaignForQuote == null || !campaignForQuote.CanOperate) { yield break; }

            long available = AvailableCredits;
            var bank = new Command_Action
            {
                defaultLabel = "RR_CreditBeacon_Bank".Translate(),
                defaultDesc = "RR_CreditBeacon_BankDesc".Translate(available.ToString("N0")),
                icon = TexCommand.ForbidOff,
                action = BankBonds,
            };
            if (available <= 0L)
            { bank.Disable("RR_Bond_NoneInRange".Translate()); }
            yield return bank;

            // Selling valuables shares the beacon's radius on purpose. A Core trade beacon
            // already means "what is in this circle is what is on the table", so the exchange
            // borrows a contract the player already understands rather than inventing its own
            // selection rules. The radius is the control.
            long oddValue, ordinaryValue;
            int itemCount;
            campaignForQuote.QuoteExchange(parent.Map, parent.Position, Props.radius,
                out oddValue, out ordinaryValue, out itemCount);

            var sell = new Command_Action
            {
                defaultLabel = "RR_Exchange_Sell".Translate(),
                defaultDesc = "RR_Exchange_SellDesc".Translate(
                    itemCount.ToString("N0"),
                    (oddValue + ordinaryValue).ToString("N0"),
                    oddValue.ToString("N0"),
                    ordinaryValue.ToString("N0")),
                icon = TexCommand.ForbidOff,
                // Confirmed rather than immediate. Selling everything inside the radius is large
                // and irreversible, and the gizmo's own description is the only warning a player
                // gets otherwise -- read after the click, which is too late. Core ships the
                // confirmation dialog for exactly this, so no window of ours is added.
                action = delegate
                {
                    Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                        "RR_Exchange_SellConfirm".Translate(
                            itemCount.ToString("N0"),
                            (oddValue + ordinaryValue).ToString("N0")),
                        SellValuables, false, null, WindowLayer.Dialog));
                },
            };
            if (itemCount <= 0)
            { sell.Disable("RR_Exchange_NothingInRange".Translate()); }
            yield return sell;
        }

        private static RimroomsCampaignComponent campaignForQuote
        {
            get
            {
                return Verse.Current.Game == null
                    ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            }
        }

        private void SellValuables()
        {
            RimroomsCampaignComponent campaign = campaignForQuote;
            if (campaign == null) { return; }

            long credited;
            int sold;
            CompanyActionResult result = campaign.ExchangeValuables(
                parent.Map, parent.Position, Props.radius, out credited, out sold);
            if (!result.Success)
            {
                Messages.Message((result.MessageKey ?? "RR_Exchange_NothingInRange").Translate(),
                    parent, MessageTypeDefOf.RejectInput, false);
                return;
            }
            Messages.Message(
                "RR_Exchange_Sold".Translate(sold.ToString("N0"), credited.ToString("N0")),
                parent, MessageTypeDefOf.PositiveEvent, false);
        }

        private void BankBonds()
        {
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return; }

            long credited;
            int consumed;
            CompanyActionResult result = campaign.RedeemBondsInRadius(
                parent.Map, parent.Position, Props.radius, out credited, out consumed);
            if (!result.Success)
            {
                Messages.Message(
                    (result.MessageKey ?? "RR_Bond_NoneInRange").Translate(),
                    parent, MessageTypeDefOf.RejectInput, false);
                return;
            }
            Messages.Message(
                "RR_CreditBeacon_Banked".Translate(consumed.ToString("N0"), credited.ToString("N0")),
                parent, MessageTypeDefOf.PositiveEvent, false);
        }
    }
}
