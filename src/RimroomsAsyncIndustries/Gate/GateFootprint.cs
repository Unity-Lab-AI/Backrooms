using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// A gate has a size, and the size is the doorway it actually is.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"and rember ther are 1x1 1x2 and 1x3 and
    /// 2x3 gate doors that allow differnt capabilities as to the universe and scerios needs"*.
    ///
    /// ## Nothing here invents a door
    ///
    /// The size comes from the door the player designated, so a gate is exactly as wide as the
    /// thing standing in the wall. **RimWorld already ships multi-cell doors** -- Core's
    /// `OrnateDoor` is 2x1 and Anomaly's `SecurityDoor` is 2x1 -- which was found by reading
    /// the installed game data rather than assumed, and it means a 1x2 gate needs no mods at
    /// all. Doors Expanded supplies the 1x3 and 2x3 shapes for anyone running it, through a
    /// conditional patch that does nothing when it is absent.
    ///
    /// ## Width is the doorway, not the building
    ///
    /// Two numbers matter and they are not the same:
    ///
    /// - <see cref="GateWidth"/> is how many cells wide the **opening** is, measured on the
    ///   face people actually walk through. It is what decides how big a thing fits and how
    ///   many walk abreast.
    /// - <see cref="GateCellCount"/> is the whole footprint. A 2x3 blast door is three wide
    ///   but six cells of machine, and it is the machine that has to be powered and brought
    ///   up.
    ///
    /// Keeping them separate is why a thick door costs more to run without letting anything
    /// bigger through than a thin door of the same width, which is the honest result.
    ///
    /// ## Throughput is never capped
    ///
    /// **Owner direction, verbatim:** *"in vinilla any number of pawns can use a door at once
    /// so we dont want limitations"*.
    ///
    /// So a wide gate does **not** get a permit quota. It gets **more doorway cells**, and
    /// ordinary pathfinding spreads people across them exactly as it does across any wide
    /// vanilla door. There is no counter anywhere in this file, deliberately: the only thing
    /// that ever limits how many people cross at once is the width of the hole in the wall.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>
        /// The footprints a gate may have, as sorted (short, long) pairs. Exactly the four the
        /// owner named. A door of any other shape is not refused because it is unknown -- it is
        /// refused because the capability ladder is defined for these and nothing else.
        /// </summary>
        private static readonly IntVec2[] LegalFootprints =
        {
            new IntVec2(1, 1),
            new IntVec2(1, 2),
            new IntVec2(1, 3),
            new IntVec2(2, 3),
        };

        /// <summary>Whether a def's footprint is one this mod is prepared to operate as a gate.</summary>
        internal static bool LegalGateFootprint(IntVec2 size)
        {
            int shortSide = size.x <= size.z ? size.x : size.z;
            int longSide = size.x <= size.z ? size.z : size.x;
            for (int index = 0; index < LegalFootprints.Length; index++)
            {
                if (LegalFootprints[index].x == shortSide && LegalFootprints[index].z == longSide)
                { return true; }
            }
            return false;
        }

        /// <summary>Every cell this gate's door stands on.</summary>
        public CellRect GateOccupiedRect
        {
            get { return parent == null || !parent.Spawned ? CellRect.Empty : parent.OccupiedRect(); }
        }

        /// <summary>The whole footprint, in cells. Drives what it costs to power and to bring up.</summary>
        public int GateCellCount
        {
            get
            {
                if (parent == null || parent.def == null) { return 1; }
                int area = parent.def.size.x * parent.def.size.z;
                return area < 1 ? 1 : area;
            }
        }

        /// <summary>
        /// How many cells wide the opening is on the side people walk through. One for an
        /// ordinary door, two for an ornate or security door, three for a triple or a blast
        /// door.
        /// </summary>
        public int GateWidth
        {
            get
            {
                List<IntVec3> cells = GateEntryCells;
                return cells.Count < 1 ? 1 : cells.Count;
            }
        }

        /// <summary>
        /// Every cell on the approach side of the doorway.
        ///
        /// Derived from the occupied rectangle rather than from the door's drawn rotation,
        /// because **Core rewrites a one-cell door's `Rotation` while drawing it** -- a trap
        /// this code base has already been caught by once, which is why the bound orientation
        /// is saved at designation and used here instead of whatever the door currently says.
        ///
        /// A cell one step out from the rectangle that is still *inside* the rectangle belongs
        /// to a thicker door's far row, so it is discarded: only the outward face counts.
        /// </summary>
        public List<IntVec3> GateEntryCells
        {
            get
            {
                var cells = new List<IntVec3>();
                if (parent == null || !parent.Spawned || parent.Map == null || !IsDesignated)
                { return cells; }
                CellRect rect = GateOccupiedRect;
                if (rect.Area <= 0) { return cells; }
                Rot4 orientation = new Rot4(nativeBoundRotation);
                IntVec3 step = nativeOppositeEntrySide ? orientation.FacingCell : orientation.Opposite.FacingCell;
                Map map = parent.Map;
                foreach (IntVec3 cell in rect)
                {
                    IntVec3 candidate = cell + step;
                    if (rect.Contains(candidate)) { continue; }
                    if (!candidate.InBounds(map) || !candidate.Standable(map)) { continue; }
                    cells.Add(candidate);
                }
                return cells;
            }
        }

        /// <summary>
        /// What one opening draws, scaled by the whole footprint.
        ///
        /// Scaled on cells rather than width on purpose: a 2x3 blast door is six cells of
        /// machine to energise even though only three of them are the hole people walk
        /// through. **"costs more to run"** is the owner's own condition on the bigger sizes,
        /// and it is what keeps a large gate a thing a branch works toward rather than a free
        /// upgrade taken on the first day.
        /// </summary>
        public float OpeningPowerDrawWatts
        {
            get
            {
                float draw = GateProps.openingPowerDrawWatts * GateCellCount;
                // **RR_Cap_EfficientAperture** (Facilities and power, tier 1). A branch that has
                // measured its own aperture holds one open for less. Applied after the footprint
                // multiplier, so a larger gate saves proportionally more -- which is the point.
                Company.RimroomsCampaignComponent campaign = NativeCampaign;
                if (campaign != null && campaign.HasCapability("RR_Cap_EfficientAperture"))
                { draw *= 0.85f; }
                return draw;
            }
        }

        /// <summary>The gate's size, as a player reads it: the opening first.</summary>
        internal string FootprintReadout()
        {
            if (parent == null || parent.def == null) { return null; }
            return "RR_Gate_FootprintReadout".Translate(GateWidth.ToString(),
                GateCellCount.ToString(), parent.def.label).ToString();
        }
    }
}
