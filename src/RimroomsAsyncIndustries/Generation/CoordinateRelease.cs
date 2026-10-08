using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Letting a place go, so a machine gate can aim deeper.
    ///
    /// ## Owner direction, 2026-09-30
    ///
    /// *"yeah so if the player discovers and goes through a natural gate how do they turn them off
    /// to use the machine gates for more controll and aiming deeper?"* and, naming the trap
    /// plainly, *"get 5 natural gates u cant use a machine gate"*. The shape they chose is an
    /// **Operations held-places list with a Release button**.
    ///
    /// ## The trap is real, and a correction is owed on why
    ///
    /// The previous checkpoint's record said discovering a gate was free because no map existed
    /// until somebody crossed. **That was wrong.** `NaturalFrontierService.Discover` calls
    /// `PortalAddressService.RegisterNaturalAddress`, which calls
    /// <see cref="DestinationService.EnsureSite"/> **immediately** — because a natural edge is
    /// registered against the far side's own `ReturnAnchor`, and that `Thing` does not exist until
    /// the map does. **A discovery costs a slot the moment it is made**, so five natural gates
    /// really do lock a player out of their own machine gates, exactly as the owner said.
    ///
    /// ## Why a natural gate cannot simply be "turned off"
    ///
    /// Invariant 12: a natural gate is **permanently open**. That is what it is. So the door is
    /// not closed and not destroyed — **the place behind it is released.** The door stays, still
    /// marked, still permanently open, and remembers where it led.
    ///
    /// ## What a release costs, and the player is told before it happens
    ///
    /// The interior is regenerated from its own seed when it is re-opened, so it is **the same
    /// place** — the same rooms, the same shape — but **anything left inside is gone.** That is
    /// the honest price of not holding it open, and it is why this is a deliberate player action
    /// with a confirmation rather than the eviction timer the owner considered and rejected.
    ///
    /// ## What it refuses
    ///
    /// Crew on the map, a crossing part-way through it, the headquarters itself, or a coordinate
    /// with no live map to release. Each refusal names itself.
    /// </summary>
    internal static class CoordinateRelease
    {
        /// <summary>Why this place cannot be released right now, or null when it can.</summary>
        internal static string RefusalFor(RimroomsCampaignComponent campaign, CoordinateRecord coordinate)
        {
            if (campaign == null || !campaign.CanOperate) { return "RR_Release_Inactive"; }
            if (coordinate == null || string.IsNullOrWhiteSpace(coordinate.Id))
            { return "RR_Release_UnknownPlace"; }
            RimroomsDestinationMapParent parent = coordinate.Site as RimroomsDestinationMapParent;
            Map map = parent == null ? null : parent.Map;
            if (parent == null || map == null) { return "RR_Release_NotHeldOpen"; }
            if (campaign.Headquarters == map) { return "RR_Release_Headquarters"; }
            // Anybody at all that the player owns, not only colonists: a released map takes its
            // contents with it, and that includes a prisoner, a guest or an animal.
            if (map.mapPawns != null && map.mapPawns.AllPawnsSpawned
                .Any(pawn => pawn != null && (pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony)))
            { return "RR_Release_CrewInside"; }
            RimroomsPortalCrossingService crossings = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalCrossingService>();
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault) { return "RR_Release_Inactive"; }
            if (crossings != null)
            {
                foreach (PortalConnectionRecord edge in network.Connections)
                {
                    if (edge == null || edge.CoordinateId != coordinate.Id) { continue; }
                    if (crossings.IsConnectionInFlight(edge.Id)) { return "RR_Release_CrossingInFlight"; }
                }
            }
            return null;
        }

        /// <summary>How many things the player is about to lose, for the confirmation.</summary>
        internal static int ItemsLeftBehind(CoordinateRecord coordinate)
        {
            RimroomsDestinationMapParent parent = coordinate == null
                ? null : coordinate.Site as RimroomsDestinationMapParent;
            Map map = parent == null ? null : parent.Map;
            if (map == null || map.listerThings == null) { return 0; }
            int count = 0;
            foreach (Thing thing in map.listerThings.AllThings)
            {
                if (thing != null && thing.def != null && thing.def.category == ThingCategory.Item)
                { count++; }
            }
            return count;
        }

        /// <summary>
        /// Let this place go. Returns null on success, or a refusal key.
        ///
        /// **The order is the whole of the safety.** The doors are told what they led to *before*
        /// the edges are removed, and the edges are removed *before* the map is torn down — so
        /// there is no moment at which a record points at something that no longer exists.
        /// Reversing any two of those steps is how a place becomes unreachable.
        /// </summary>
        internal static string TryRelease(RimroomsCampaignComponent campaign, CoordinateRecord coordinate)
        {
            string refusal = RefusalFor(campaign, coordinate);
            if (refusal != null) { return refusal; }

            RimroomsDestinationMapParent parent = (RimroomsDestinationMapParent)coordinate.Site;
            Map map = parent.Map;
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();

            // 1. Every door that led here is told which place it led to, while the edges still
            //    say so. Without this the door becomes an ordinary marked door and the place
            //    behind it is unreachable for ever.
            var shelved = new List<PortalConnectionRecord>();
            foreach (PortalConnectionRecord edge in network.Connections)
            {
                if (edge == null || edge.CoordinateId != coordinate.Id) { continue; }
                shelved.Add(edge);
                RememberOn(edge.First, coordinate, map);
                RememberOn(edge.Second, coordinate, map);
            }

            // 2. The edges go, because every one of them points at a Thing on the map that is
            //    about to stop existing. Leaving them would be leaving dangling records, which is
            //    this project's most expensive defect class.
            for (int index = 0; index < shelved.Count; index++)
            { network.ForgetConnection(shelved[index].Id); }

            // 3. The map and its world object. The coordinate RECORD and its rooms are kept, so
            //    re-opening returns to the same place rather than a different one.
            coordinate.site = null;
            coordinate.status = CoordinateStatus.Discovered;
            coordinate.releasedByPlayer = true;
            Current.Game.DeinitAndRemoveMap(map, false);
            if (Find.WorldObjects.Contains(parent)) { Find.WorldObjects.Remove(parent); }

            campaign.RecordEvent("RR_Event_CoordinateReleased", coordinate.Id, coordinate.Label);
            return null;
        }

        /// <summary>
        /// Write the coordinate onto the surface door's own comp, so the door knows where it led.
        ///
        /// Only the door on **this** side. The far endpoint is on the map being released and is
        /// about to cease to exist, so remembering anything on it would be remembering it onto
        /// nothing.
        /// </summary>
        private static void RememberOn(PortalEndpointRecord endpoint, CoordinateRecord coordinate, Map releasing)
        {
            Thing anchor = endpoint == null ? null : endpoint.Anchor;
            if (anchor == null || anchor.Destroyed || anchor.Map == null || anchor.Map == releasing)
            { return; }
            CompRimroomsEmergence emergence = anchor.TryGetComp<CompRimroomsEmergence>();
            if (emergence == null) { return; }
            emergence.RememberShelvedPlace(coordinate.Id);
        }
    }
}
