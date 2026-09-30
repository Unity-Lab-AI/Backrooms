using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// **Sound the containment alarm** — on the comms console, beside the call to the company.
    ///
    /// The console is where every branch-wide order in this mod is given, and this is a
    /// branch-wide order: it shuts every connection the company has open, wherever the gates
    /// are. Putting it on one gate would be wrong, because one gate's cutoff button already
    /// exists and does one gate.
    ///
    /// **It holds no rule of its own.** Every condition and the whole effect live in
    /// <see cref="ContainmentProtocol"/>, so the manual alarm and the automatic procedure do
    /// exactly the same thing to exactly the same gates. A gizmo that decided for itself what
    /// an alarm closes would be a second opinion beside the procedure it is named after —
    /// which is the defect class this project keeps catching in presentation work.
    ///
    /// **It is disabled with its reason rather than hidden** when there is nothing open, per
    /// invariant 28: a player needs to learn that the alarm closes connections, and a button
    /// that vanishes teaches nothing. That also means the branch can always see the alarm
    /// exists before the night it is needed.
    /// </summary>
    public static class ContainmentAlarmGizmo
    {
        public static IEnumerable<Gizmo> For(Thing console)
        {
            if (console == null || !console.Spawned || console.Faction != Faction.OfPlayer)
            { yield break; }
            // A machining table carries the same component and is not a place orders are given.
            if (!(console is Building_CommsConsole)) { yield break; }

            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { yield break; }

            var alarm = new Command_Action
            {
                defaultLabel = "RR_Containment_AlarmLabel".Translate(),
                defaultDesc = "RR_Containment_AlarmDesc".Translate(),
                icon = TexCommand.ClearPrioritizedWork,
                action = delegate
                {
                    CompanyActionResult result = ContainmentProtocol.SoundTheAlarm(campaign);
                    if (!result.Success)
                    {
                        Messages.Message(result.MessageKey.Translate(),
                            MessageTypeDefOf.RejectInput, false);
                    }
                },
            };
            if (!campaign.OwnsMap(console.Map))
            { alarm.Disable("RR_Contact_NotOurs".Translate()); }
            yield return alarm;
        }
    }
}
