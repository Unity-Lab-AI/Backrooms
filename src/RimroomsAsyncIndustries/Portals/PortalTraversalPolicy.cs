using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// The single place that decides who may pass through a portal and in what
    /// role. Every crossing path must ask this policy, so no later work adapter,
    /// job or scheduler can quietly let the far side walk out on its own.
    ///
    /// Owner rule: inhabitants and monstrosities stay in the Backrooms. Nothing
    /// that is not this company's own pawn crosses under its own will, and an open
    /// connection is never a reason for the far side to move toward the threshold.
    /// Anything else reaches the near side only because one of this company's
    /// pawns physically carried it through by ordinary work.
    ///
    /// Gate, machine door and portal are one thing; only the connection kind
    /// differs, laboratory or permanently open natural. The rule is per connection
    /// and holds for every gate at once. Opening a second or tenth gate never
    /// relaxes it, and there is no aggregate exception once several are connected.
    /// Every start can eventually run several gates, so nothing here may assume one
    /// gate per branch, per map or per coordinate.
    /// </summary>
    public static class PortalTraversalPolicy
    {
        /// <summary>
        /// Deliberately constant. A connection opening never grants any non-player
        /// pawn a reason, route or permission to traverse. There is no setting, no
        /// research and no upgrade that flips this.
        /// </summary>
        public const bool AutonomousNonPlayerTraversalPermitted = false;

        /// <summary>
        /// May this pawn traverse as a traveller, walking through on its own legs?
        /// Only this company's available colonists may, whether the order came from
        /// the player directly or from company work scheduling.
        /// </summary>
        public static string TravellerFailureKey(Pawn traveller)
        {
            if (traveller == null) { return "RR_PortalCrossing_PawnNotEligible"; }
            if (traveller.Faction != Faction.OfPlayer || !traveller.IsColonist)
            { return "RR_PortalTraversal_NotOurPerson"; }
            return RimroomsPortalCrossingService.EligibilityFailureKey(traveller);
        }

        /// <summary>
        /// May this object ride through in a carrier's hands? Materials, tools,
        /// equipment, resources, minified furniture and production benches, corpses,
        /// and people or creatures that are actually being carried all qualify. A
        /// pawn that could walk away on its own does not: it would be traversing,
        /// not being carried.
        /// </summary>
        public static string CargoFailureKey(Thing cargo, Pawn carrier)
        {
            if (cargo == null) { return null; }
            if (carrier == null || carrier.carryTracker == null ||
                carrier.carryTracker.innerContainer == null ||
                !carrier.carryTracker.innerContainer.Contains(cargo))
            { return "RR_PortalTraversal_CargoNotCarried"; }
            Pawn passenger = cargo as Pawn;
            if (passenger == null) { return null; }
            // A carried person or creature must genuinely be in someone's arms:
            // downed, dead, or held as a prisoner. Anything still on its feet would
            // be crossing under its own will, which this policy never allows.
            if (passenger.Dead || passenger.Downed || passenger.IsPrisonerOfColony) { return null; }
            return "RR_PortalTraversal_PassengerNotHeld";
        }

        /// <summary>
        /// Whether a spawned thing on either side may be treated as drawn toward a
        /// threshold. Always false: generation, encounters and threats must never
        /// use an open connection as a destination or a trigger to converge on it.
        /// </summary>
        public static bool MayApproachThresholdForTraversal(Thing thing)
        {
            return false;
        }
    }
}
