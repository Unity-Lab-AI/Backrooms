using System;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>
    /// Moves one spawned thing to another cell or map so that it always ends up somewhere.
    ///
    /// A bare despawn followed by a spawn has a gap between the two: if the spawn throws, the
    /// thing is on no map and in no container, and a person or an item simply stops existing as
    /// far as the player can tell. This closes the gap by putting the thing back where it stood
    /// whenever the placement throws or refuses.
    /// </summary>
    internal static class HeldCustody
    {
        /// <summary>
        /// Relocate <paramref name="thing"/>. <paramref name="near"/> places it on the nearest
        /// valid cell (and may merge an item into a stack there); otherwise it is spawned on the
        /// exact cell. Returns whether it arrived; on false it is back where it started, or the
        /// failure is logged if even that was impossible.
        /// </summary>
        internal static bool Relocate(Thing thing, Map destination, IntVec3 cell, bool near)
        {
            if (thing == null || !thing.Spawned || destination == null) { return false; }
            Map origin = thing.Map;
            IntVec3 was = thing.Position;
            Rot4 rotation = thing.Rotation;
            bool placed = false;
            try
            {
                thing.DeSpawn();
                placed = near
                    ? GenPlace.TryPlaceThing(thing, cell, destination, ThingPlaceMode.Near)
                    : GenSpawn.Spawn(thing, cell, destination, rotation) != null;
            }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms] A move did not finish; returning " + thing.LabelShort
                    + " to where it stood: " + error);
                placed = false;
            }
            if (placed || thing.Spawned || thing.Destroyed || thing.ParentHolder != null) { return placed; }
            try
            {
                if (origin != null && Find.Maps.Contains(origin))
                {
                    if (near) { GenPlace.TryPlaceThing(thing, was, origin, ThingPlaceMode.Near); }
                    else { GenSpawn.Spawn(thing, was, origin, rotation); }
                }
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms] Could not return " + thing.LabelShort + " to where it stood: " + error);
            }
            if (!thing.Spawned && !thing.Destroyed && thing.ParentHolder == null)
            { Log.Error("[Rimrooms] " + thing.LabelShort + " could not be placed on any map after a failed move."); }
            return false;
        }
    }
}
