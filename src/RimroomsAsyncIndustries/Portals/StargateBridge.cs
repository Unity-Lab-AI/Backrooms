using System;
using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Read-only awareness of the Stargate mod. **It never attaches, dials or closes anything.**
    ///
    /// An earlier version put their `CompStargate` and a Core transporter on Rimrooms doors and
    /// dialled them. That could not be made correct from outside their mod:
    ///
    /// * their lookups only accept their own `Building_Stargate`, so the far door was never found
    ///   and a native gate elsewhere could have been chosen as the destination;
    /// * a zero-delay dial never reached their countdown tick, so nothing opened, and the call
    ///   reported success anyway;
    /// * a component added per instance is not rebuilt from `def.comps` on load, so a fresh one
    ///   would have been attached empty, without its peer, iris or loaded contents;
    /// * once open, their own float menu and loading jobs carried pawns and goods through without
    ///   any of this company's receipts, ownership or availability checks.
    ///
    /// So their mod keeps its own gates, untouched, and a Rimrooms door stays a Rimrooms door:
    /// every crossing goes through <see cref="PortalTravelService"/>.
    /// </summary>
    internal static class StargateBridge
    {
        private const string CompTypeName = "StargatesMod.CompStargate";

        private static bool resolved;
        private static Type compType;

        /// <summary>Whether the Stargate mod is loaded at all.</summary>
        internal static bool Available
        {
            get
            {
                Resolve();
                return compType != null;
            }
        }

        private static void Resolve()
        {
            if (resolved) { return; }
            resolved = true;
            compType = GenTypes.GetTypeInAnyAssembly(CompTypeName);
        }

        /// <summary>Their component on this thing, or null. Read only.</summary>
        internal static ThingComp On(ThingWithComps thing)
        {
            Resolve();
            if (compType == null || thing == null) { return null; }
            List<ThingComp> all = thing.AllComps;
            if (all == null) { return null; }
            for (int index = 0; index < all.Count; index++)
            {
                if (compType.IsInstanceOfType(all[index])) { return all[index]; }
            }
            return null;
        }
    }
}
