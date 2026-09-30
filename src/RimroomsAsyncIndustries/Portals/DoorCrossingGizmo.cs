using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Ordering a crossing from the door, and naming the refusal there too.
    ///
    /// Row 832, and the row is honest about what it is: *"The capability is done: every refusal is
    /// a keyed reason and the player sees it. What is outstanding is surfacing the order and its
    /// reason on the door itself rather than in the Operations pane, which is presentation."*
    ///
    /// So nothing here decides anything. `PortalTravelService.OrderCrossing` is the order and
    /// `RimroomsPortalCrossingService.EligibilityFailureKey` is the rule, and both are called rather than
    /// reimplemented — **invariant 1: `PortalTraversalPolicy` is the only traversal chokepoint**,
    /// and a second opinion in a gizmo is exactly how a chokepoint stops being one.
    ///
    /// The list is of **selected** pawns, because a door does not know who you mean otherwise.
    /// A pawn who cannot cross is listed with the reason rather than hidden: *"drafted"* and
    /// *"prisoner"* are things a player needs told, and a name missing from a menu says neither.
    /// </summary>
    public static class DoorCrossingGizmo
    {
        public static IEnumerable<Gizmo> For(Thing door)
        {
            if (door == null || !door.Spawned || door.Map == null) { yield break; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { yield break; }

            // Only a door that is actually an endpoint of a live connection on this map.
            PortalConnectionRecord connection = ConnectionAt(door);
            if (connection == null) { yield break; }

            var order = new Command_Action
            {
                defaultLabel = "RR_DoorCross_Label".Translate(),
                defaultDesc = "RR_DoorCross_Desc".Translate(),
                icon = TexCommand.Install,
                action = delegate { Find.WindowStack.Add(new FloatMenu(Options(connection, door))); },
            };
            yield return order;
        }

        /// <summary>
        /// The live connection this door is an endpoint of, or null.
        ///
        /// Read from the network rather than from anything saved on the door, so a door that has
        /// been moved or whose address was cleared stops offering the order immediately.
        /// </summary>
        private static PortalConnectionRecord ConnectionAt(Thing door)
        {
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.Connections == null) { return null; }
            IReadOnlyList<PortalConnectionRecord> connections = network.Connections;
            for (int index = 0; index < connections.Count; index++)
            {
                PortalConnectionRecord connection = connections[index];
                if (connection == null) { continue; }
                if (connection.First != null && connection.First.Anchor == door) { return connection; }
                if (connection.Second != null && connection.Second.Anchor == door) { return connection; }
            }
            return null;
        }

        /// <summary>
        /// One row per selected pawn, ordered by name, with a refusal reason where there is one.
        ///
        /// Sorted ordinally: invariant 26, because a menu whose rows move between frames is a menu
        /// somebody misclicks — and this one issues an order.
        /// </summary>
        private static List<FloatMenuOption> Options(PortalConnectionRecord connection, Thing door)
        {
            var options = new List<FloatMenuOption>();
            List<Pawn> selected = Find.Selector == null
                ? new List<Pawn>()
                : Find.Selector.SelectedObjects.OfType<Pawn>()
                    .Where(pawn => pawn != null && pawn.Spawned && pawn.Map == door.Map)
                    .OrderBy(pawn => pawn.LabelShortCap.ToString(), System.StringComparer.Ordinal)
                    .ToList();

            if (selected.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_DoorCross_NobodySelected".Translate(), null));
                return options;
            }

            for (int index = 0; index < selected.Count; index++)
            {
                Pawn pawn = selected[index];
                // The rule, asked of the one place that owns it. Never re-derived here.
                string refusal = RimroomsPortalCrossingService.EligibilityFailureKey(pawn);
                if (refusal != null)
                {
                    options.Add(new FloatMenuOption(
                        "RR_DoorCross_Refused".Translate(pawn.LabelShortCap, refusal.Translate()), null));
                    continue;
                }
                Pawn ordered = pawn;
                options.Add(new FloatMenuOption(
                    "RR_DoorCross_Send".Translate(pawn.LabelShortCap),
                    delegate
                    {
                        CompanyActionResult result =
                            PortalTravelService.OrderCrossing(ordered, connection);
                        if (!result.Success && result.MessageKey != null)
                        {
                            Messages.Message(result.MessageKey.Translate(), door,
                                MessageTypeDefOf.RejectInput, false);
                        }
                    }));
            }
            return options;
        }
    }
}
