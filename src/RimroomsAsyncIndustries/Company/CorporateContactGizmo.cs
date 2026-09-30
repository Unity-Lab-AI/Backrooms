using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Calling the corporation, from a comms console, for a branch that started without one.
    ///
    /// **This closes a hole that made two of the three shipped starts unreachable.**
    /// `EstablishCorporationContact()` existed, was one-way, recorded its event, had a translated
    /// string waiting for it — and **had no caller anywhere.** `corporationContact` gates the
    /// tutorial line, generated requests, the Purchase route and the clean-up team's rescue, and
    /// the Store and Solo/Group starts both declare `beginsInCorporationContact false`. So both
    /// of them had **no campaign at all, permanently**, while `docs/CAMPAIGN_CHART.md` said of
    /// each that *"reaching contact is the achievement"* and `RR_Starts.xml` said in its own
    /// comment *"Reaching contact is the achievement here, not the starting condition."*
    ///
    /// The owner named the mechanism while this was being built, verbatim:
    ///
    ///     "once they "contact the cvompany in comms" they can start async quest line"
    ///
    /// So it is a call placed on a comms console, and what it starts is **the existing Async
    /// tutorial line** — not a parallel one. Nothing new had to be authored for the line itself:
    /// `OfferNextTutorialRequest` already refuses until `corporationContact`, so the line begins on
    /// its own the moment this succeeds.
    ///
    /// The console is Core's `CommsConsole` and already carries a Rimrooms comp, which is why this
    /// is a gizmo provider on the existing component rather than a new comp and a new patch. It
    /// deliberately does **not** appear on a machining table, which shares that comp.
    ///
    /// **It is not offered to a branch already in contact**, because the call has nothing to say.
    /// </summary>
    public static class CorporateContactGizmo
    {
        public static IEnumerable<Gizmo> For(Thing console)
        {
            if (console == null || !console.Spawned || console.Faction != Faction.OfPlayer)
            { yield break; }
            // A machining table carries the same component. A branch does not telephone anybody
            // from a machining table.
            if (!(console is Building_CommsConsole)) { yield break; }

            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { yield break; }
            // Already on the books. The ordinary request line is the guidance from here, and a
            // button that can only tell you it did nothing is worse than no button.
            if (campaign.CorporationContact) { yield break; }

            var call = new Command_Action
            {
                defaultLabel = "RR_Contact_Call".Translate(),
                defaultDesc = "RR_Contact_CallDesc".Translate(),
                icon = TexCommand.Attack,
                action = delegate
                {
                    CompanyActionResult result = campaign.CallTheCorporation(console);
                    if (!result.Success)
                    {
                        Messages.Message(result.MessageKey.Translate(),
                            MessageTypeDefOf.RejectInput, false);
                    }
                },
            };

            // Disabled with its reason on the tooltip rather than hidden, so a player can see
            // what the call is waiting for. Invariant 28: the rule has to be learnable.
            string blocker = campaign.CorporationCallBlocker(console);
            if (blocker != null) { call.Disable(blocker.Translate()); }
            yield return call;
        }
    }
}
