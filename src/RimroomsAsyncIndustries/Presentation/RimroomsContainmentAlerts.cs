using System.Collections.Generic;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>
    /// **Critical.** Something is coming off a holding platform on a map you are not looking
    /// at.
    ///
    /// Critical is the right band for the same reason
    /// <see cref="Alert_RimroomsRecoveryOverdue"/> is: this is a state that can cost a player
    /// real damage while their attention is genuinely somewhere else, which is what RimWorld
    /// reserves the band for. **The whole point of the alert is that the attention is
    /// elsewhere** — if it were not, Core's own containment warnings would already be on
    /// screen, and <see cref="ContainmentWatch"/> records why that matters and why these two
    /// alerts skip the current map.
    ///
    /// Reports the escaping **occupant** as the culprit rather than the platform, so clicking
    /// the alert jumps to the thing that is moving. Core's own containment alerts report pawns
    /// too, so this matches what a player has already learned to expect from them.
    /// </summary>
    public class Alert_RimroomsContainmentBreachElsewhere : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_RimroomsContainmentBreachElsewhere()
        {
            defaultLabel = "RR_Alert_ContainmentBreach".Translate();
            defaultExplanation = "RR_Alert_ContainmentBreachDesc".Translate();
            defaultPriority = AlertPriority.Critical;
        }

        public override AlertReport GetReport()
        {
            culprits.Clear();
            List<ContainmentWatch.HolderState> holders = ContainmentWatch.OccupiedHolders();
            for (int index = 0; index < holders.Count; index++)
            {
                ContainmentWatch.HolderState state = holders[index];
                // The map on screen belongs to Core's four alerts alone.
                if (!state.Escaping || state.Map == Find.CurrentMap) { continue; }
                culprits.Add(state.Occupant);
            }
            return AlertReport.CulpritsAre(culprits);
        }
    }

    /// <summary>
    /// **High.** A holding platform on a map you are not looking at has lost power with
    /// something on it.
    ///
    /// The warning that precedes the breach and the one a player can still act on — the same
    /// relationship <see cref="Alert_RimroomsReturnWindowClosing"/> has with
    /// <see cref="Alert_RimroomsRecoveryOverdue"/>.
    ///
    /// Deliberately **only** the power condition. Containment strength and activity level are
    /// Core's to judge and `Alert_InsufficientContainmentStrength` and
    /// `Alert_DangerousActivity` already judge them; restating either would be a second
    /// opinion beside a rule the player is already shown. Lost power is the one condition
    /// Core has no alert for at all, that is unambiguous, and that a player on another map
    /// cannot possibly see.
    /// </summary>
    public class Alert_RimroomsContainmentUnpoweredElsewhere : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_RimroomsContainmentUnpoweredElsewhere()
        {
            defaultLabel = "RR_Alert_ContainmentUnpowered".Translate();
            defaultExplanation = "RR_Alert_ContainmentUnpoweredDesc".Translate();
            defaultPriority = AlertPriority.High;
        }

        public override AlertReport GetReport()
        {
            culprits.Clear();
            List<ContainmentWatch.HolderState> holders = ContainmentWatch.OccupiedHolders();
            for (int index = 0; index < holders.Count; index++)
            {
                ContainmentWatch.HolderState state = holders[index];
                if (!state.Unpowered || state.Map == Find.CurrentMap) { continue; }
                // A platform already being escaped from is reported by the critical alert.
                // Saying both about one platform is the duplication this pair exists to avoid.
                if (state.Escaping) { continue; }
                culprits.Add(state.Holder);
            }
            return AlertReport.CulpritsAre(culprits);
        }
    }
}
