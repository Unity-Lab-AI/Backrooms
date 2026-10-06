using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// A room nobody has walked into offers no work, and starts offering it the moment somebody has.
    ///
    /// ## The defect, reported from the first launch
    ///
    /// **Owner, 2026-10-06, verbatim:** *"and something we need to fix is that the pawns when
    /// entering the back room instantly try to find tasks and start running of for example to flower
    /// pots to plant the flower work, so we need something that spawned in its like flower pots in
    /// the backrooms dont pull a pawn to run through the map to plant a flower or other things
    /// similar that casue jobs work just being in the game wehn pawns look for axcessible tasks.
    /// like make it so unexplored areas can propigate work as no one knows or has been in those
    /// rooms yet."*
    ///
    /// A crew steps through a gate and immediately sprints the width of a three-hundred-cell maze to
    /// sow a flower pot in a room no living person has seen. **It is not a pathfinding quirk and it
    /// is not vanilla being greedy — the generator caused it, deliberately, in two lines.**
    ///
    /// ## The cause was ours and it was explicit
    ///
    /// `RoomContentBuilder` called `thing.SetForbidden(false, false)` on **every** piece of room
    /// content it placed, and the corridor fixtures are spawned as `Faction.OfPlayer`. So the
    /// instant a coordinate exists, every pot, bench and bed on it is colony property, unforbidden,
    /// and therefore a legitimate work target the full width of the map away.
    ///
    /// ## Why forbidding is the right mechanism, read out of the game rather than guessed
    ///
    /// `ForbidUtility.IsForbidden(Thing, Pawn)` was decompiled from the shipped assembly to settle
    /// this. **Fog is not part of it** — the checks are the thing's own forbidden flag, its cell's
    /// `InAllowedArea`, and a lord's extra-forbidden list. So making a coordinate fogged does
    /// nothing on its own, and the two mechanisms that *do* work are an allowed area and the
    /// forbidden flag.
    ///
    /// **The flag wins over the area, and the reason is the player.** An allowed area would have to
    /// be assigned to each crossing pawn, overriding whatever area the player had them on — the mod
    /// reaching into a control the player owns. The forbidden flag touches only the things the
    /// generator itself placed, which is content the mod already owns outright.
    ///
    /// **And forbidding does not restrict movement.** A forbidden thing is not a work target and
    /// not haulable; it is not a wall. A crew still walks wherever it likes, which is what makes
    /// exploring possible at all.
    ///
    /// ## What is deliberately NOT forbidden
    ///
    /// Doors, the gate anchor, the found gate and the conduits. A forbidden door is a door a
    /// colonist will not pass, which would turn this fix into a maze nobody can enter; and the
    /// conduits are the power grid rather than scenery. Each of those un-forbids itself at its own
    /// spawn site and this component never touches them, because **it only ever un-forbids** —
    /// it never forbids anything at runtime, so a thing the player has deliberately unforbidden
    /// stays that way.
    ///
    /// ## Discovery is fog, and fog is already how this map works
    ///
    /// `GenStep_BackroomsDestination` unfogs the entry and return cells and nothing else, so a
    /// coordinate is already unexplored by construction. Fog lifts as pawns walk, by Core's own
    /// rules, so **this component needs no notion of exploring at all** — it watches for cells that
    /// have become visible and releases what stands on them.
    ///
    /// A bounded rotating window per invariant 5, never a prefix: a coordinate is 90,000 cells and
    /// sweeping all of them every tick to catch a door opening would cost more than the feature is
    /// worth. A cell found late costs one sweep of delay before its contents become workable, which
    /// nobody can perceive.
    /// </summary>
    public sealed class UnexploredWorkMapComponent : MapComponent
    {
        /// <summary>
        /// Ticks between sweeps. One second of game time at normal speed: a crew walking into a
        /// room should find it alive almost at once, and nothing here is urgent enough to run
        /// every tick.
        /// </summary>
        private const int Interval = 60;

        /// <summary>
        /// Cells examined per sweep. A 300x300 coordinate is 90,000 cells, so the whole map is
        /// covered in about 75 sweeps — roughly a minute and a quarter of game time — and a room a
        /// crew is standing in is reached far sooner than that because the sweep is continuous
        /// rather than triggered.
        /// </summary>
        private const int CellsPerSweep = 600;

        private int cursor;
        private bool applicable;
        private bool applicableKnown;

        public UnexploredWorkMapComponent(Map map) : base(map) { }

        /// <summary>
        /// Only a Backrooms coordinate. A colony map's own buildings are the player's and nothing
        /// here has any business touching them.
        /// </summary>
        private bool Applicable
        {
            get
            {
                if (!applicableKnown)
                {
                    applicable = map != null && map.Parent is RimroomsDestinationMapParent;
                    applicableKnown = true;
                }
                return applicable;
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!Applicable || Find.TickManager == null) { return; }
            if (Find.TickManager.TicksGame % Interval != 0) { return; }
            Release();
        }

        /// <summary>
        /// Un-forbid what stands on cells that are no longer fogged.
        ///
        /// **One direction only.** This never forbids anything, so a player who unforbids a thing
        /// by hand keeps that decision, and a thing in a room still unseen is left exactly as the
        /// generator placed it.
        /// </summary>
        private void Release()
        {
            if (map.fogGrid == null) { return; }
            // `CellIndices` is a struct, so there is nothing to null-check here; the map
            // itself was checked by `Applicable`.
            int total = map.cellIndices.NumGridCells;
            if (total <= 0) { return; }
            int examined = 0;
            while (examined < CellsPerSweep && examined < total)
            {
                if (cursor >= total) { cursor = 0; }
                IntVec3 cell = map.cellIndices.IndexToCell(cursor);
                cursor++;
                examined++;
                if (map.fogGrid.IsFogged(cell)) { continue; }
                System.Collections.Generic.List<Thing> things = cell.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    Thing thing = things[index];
                    if (thing == null || thing.def == null) { continue; }
                    // Only what can be forbidden at all; asking anything else wastes the budget.
                    if (!thing.def.useHitPoints && thing.def.category != ThingCategory.Item)
                    { continue; }
                    if (thing.IsForbidden(Faction.OfPlayer))
                    { thing.SetForbidden(false, warnOnFail: false); }
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            // The cursor is saved so a reload does not restart the sweep from zero and leave the
            // far half of a coordinate quiet for a minute longer than it should be.
            Scribe_Values.Look(ref cursor, "rr_unexploredWorkCursor", 0);
        }
    }
}
