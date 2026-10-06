using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The company's designation icon for a gate that remains a bound native door run.
    ///
    /// **A GATE IS A DOOR THE PLAYER ALREADY OWNS, AND THAT IS NOT CHANGING.** Owner, 2026-10-06:
    /// *"need to be able to build upto three gates of differnt sizes to... remember?"* -- and the
    /// sizes come from **binding a run of adjacent real doors**: 1x1, 1x2 on Core's `OrnateDoor`,
    /// 1x3 and 2x3 bound, plus Doors Expanded's multi-cell doors when they are installed. A cloned
    /// door def would destroy the binding that produces those sizes and cut the gate off from
    /// Locks, Doors Expanded, ReBuild, Vault Walls and Doors and every prisoner-access mod in the
    /// profile. So `RR_MachineGate` is **not** a buildable and never will be.
    ///
    /// The original face-on arch stays a flat button icon. It is never used as a world sprite.
    /// `GateWorldFrames` draws separate, genuinely authored cardinal frames across the bound
    /// native door run, using its saved orientation and complete footprint. Missing art, a disabled
    /// setting or an incompatible footprint leaves the native rendering intact. That consumer is
    /// implemented; its appearance, occlusion and provider behaviour still need an owner-launched
    /// runtime review.
    ///
    /// Resolved once and cached, with failure answering null rather than throwing. Content loads
    /// after static construction in some orders, so the lookup is lazy and runs once per session
    /// rather than every frame.
    /// </summary>
    internal static class RimroomsGateArt
    {
        private const string DesignateIconPath = "Things/Building/Rimrooms/RR_MachineGate";

        private static Texture2D designateIcon;
        private static bool designateIconResolved;

        /// <summary>
        /// The company gate icon, or null when the package ships without it.
        ///
        /// Callers fall back to the door's own icon, so a stripped package shows the button it has
        /// always shown instead of a missing-texture square. `reportFailure: false` is deliberate:
        /// an absent optional icon is not an error worth a red line in somebody's log.
        /// </summary>
        internal static Texture2D DesignateIcon
        {
            get
            {
                if (designateIconResolved) { return designateIcon; }
                designateIconResolved = true;
                designateIcon = ContentFinder<Texture2D>.Get(DesignateIconPath, false);
                return designateIcon;
            }
        }
    }
}
