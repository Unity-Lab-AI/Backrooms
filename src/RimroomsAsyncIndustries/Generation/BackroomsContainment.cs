using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// The rule that a Backrooms coordinate has no outside, held against everything that would
    /// otherwise break it.
    ///
    /// **Owner direction, 2026-09-29:** a Backrooms environment can never have an outside; the
    /// whole seed map is inside mountain roof; no roof anywhere in it may ever be removed; and
    /// the only way out into a world map area is a portal found inside the Backrooms.
    ///
    /// **What the interior may still do, per the owner's refinement the same day:** every wall
    /// and door is deconstructable, every solid area is mineable in a variety of materials, and
    /// carpet and tile can be lifted. The interior is fully strippable. Only the ceiling and the
    /// absence of a sky are inviolable.
    ///
    /// Those two directions sit together comfortably because of one Core fact, verified in
    /// source rather than assumed:
    ///
    /// <code>RoofDef.VanishOnCollapse => !isThickRoof;</code>
    ///
    /// **Thick rock roof never vanishes when it collapses.** Mining out the rock that supports
    /// it produces rubble and a collapse exactly as it does under any mountain, and the cell
    /// stays roofed afterwards. So a player may mine a coordinate to nothing and still never
    /// open a hole in the world. Containment survives unlimited mining with **no restriction on
    /// the player at all**, which is a far better answer than forbidding the pickaxe.
    ///
    /// ## What actually needed guarding
    ///
    /// Vanilla alone can strip the ceiling. `WorkGiver_RemoveRoof` is driven by
    /// <c>map.areaManager.NoRoof</c> and contains **no** check for natural or thick roof — it
    /// only asks whether the cell is in the area and is roofed at all. A player could paint a
    /// no-roof area across a coordinate and colonists would obediently remove a mountain
    /// ceiling. That is precisely the hole the owner named.
    ///
    /// This component closes it two ways, with public API only and no Harmony:
    ///
    /// 1. **The no-roof area is kept empty** on a Backrooms map. With no active cells,
    ///    `WorkGiver_RemoveRoof.ShouldSkip` returns true and no removal job is ever offered —
    ///    and any mod that drives removal through the same area is neutralised by the same
    ///    stroke, because the area is the shared mechanism rather than a vanilla detail.
    /// 2. **Any cell that somehow loses its roof is re-roofed** with thick rock. This is the
    ///    belt to the first brace: it does not care *how* the roof went, so a mod that removes
    ///    roof by a route nobody has seen is still corrected. It is a repair rather than a
    ///    prohibition, which is why it can be honest about mods it has never been tested with.
    ///
    /// Both passes are bounded. The re-roof sweep walks a rotating window of cells per interval
    /// rather than the whole map, so the cost is fixed regardless of map size and no region of
    /// the map can be starved — the same rotating-window rule the work layer uses.
    /// </summary>
    public sealed class BackroomsContainmentMapComponent : MapComponent
    {
        /// <summary>How often the guard runs. Roughly once a second at normal speed.</summary>
        private const int Interval = 60;

        /// <summary>
        /// How many cells one sweep examines. A rotating window, so a large map is covered
        /// across successive sweeps at a fixed cost per sweep.
        /// </summary>
        private const int CellsPerSweep = 400;

        private int cursor;

        public BackroomsContainmentMapComponent(Map map) : base(map) { }

        /// <summary>
        /// Whether this map is a Backrooms coordinate whose containment must hold. An ordinary
        /// colony or world map is none of this component's business, and it does nothing there.
        /// </summary>
        private bool Contained
        {
            get
            {
                var site = map == null ? null : map.Parent as RimroomsDestinationMapParent;
                return site != null && site.LayoutReady;
            }
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            if (!Contained) { return; }
            // On load, correct anything a previous session or an absent mod left behind before
            // the player can see it, rather than waiting for the rotating sweep to reach it.
            ClearNoRoofArea();
            ReroofWholeMap();
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!Contained) { return; }
            if (Find.TickManager.TicksGame % Interval != 0) { return; }
            ClearNoRoofArea();
            SweepReroof();
        }

        /// <summary>
        /// Keep the no-roof area empty. This is the primary guard: with no active cells the
        /// remove-roof work giver skips entirely, so the job is never offered rather than being
        /// offered and then refused.
        /// </summary>
        private void ClearNoRoofArea()
        {
            Area_NoRoof area = map.areaManager == null ? null : map.areaManager.NoRoof;
            if (area == null || area.TrueCount == 0) { return; }
            // Copy first: clearing while enumerating the live cell list is not safe.
            var marked = new List<IntVec3>(area.ActiveCells);
            for (int index = 0; index < marked.Count; index++) { area[marked[index]] = false; }
        }

        /// <summary>One bounded rotating window of cells, re-roofed if any lost its roof.</summary>
        private void SweepReroof()
        {
            RoofDef thick = RoofDefOf.RoofRockThick;
            if (thick == null || map.roofGrid == null) { return; }
            int total = map.Size.x * map.Size.z;
            if (total <= 0) { return; }
            if (cursor >= total) { cursor = 0; }
            int examined = 0;
            while (examined < CellsPerSweep && examined < total)
            {
                IntVec3 cell = map.cellIndices.IndexToCell(cursor);
                if (!map.roofGrid.Roofed(cell)) { map.roofGrid.SetRoof(cell, thick); }
                cursor++;
                if (cursor >= total) { cursor = 0; }
                examined++;
            }
        }

        /// <summary>
        /// Every cell at once. Used on load and immediately after generation, where a partial
        /// sweep would leave a visible hole until the rotation came round.
        /// </summary>
        internal void ReroofWholeMap()
        {
            RoofDef thick = RoofDefOf.RoofRockThick;
            if (thick == null || map.roofGrid == null) { return; }
            foreach (IntVec3 cell in map.AllCells)
            {
                if (!map.roofGrid.Roofed(cell)) { map.roofGrid.SetRoof(cell, thick); }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            // Transient by nature: the cursor is a scan position, and starting a session from
            // zero costs one extra sweep and nothing else.
            Scribe_Values.Look(ref cursor, "rr_containmentCursor", 0);
        }
    }
}
