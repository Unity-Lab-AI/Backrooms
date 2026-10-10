# -*- coding: utf-8 -*-
"""Re-scope the anomaly effects from a coordinate to a plain list of cells.

The four effects were written against CoordinateRecord because a coordinate was the only
place they could happen. The threshold bleed happens at the HEADQUARTERS, in the room a gate
sits in, and it must be the SAME four effects rather than a second copy of them -- a copy
would drift, and the four safety promises in invariant 28 are carried by the bodies.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Threats', 'AnomalyEventService.cs')
s = io.open(p, encoding='utf-8-sig').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:70]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:70]
    s = s.replace(old, new, 1)


# ---------------------------------------------------------------- Fire dispatches on cells
sub(u"""        private static bool Fire(Map map, CoordinateRecord coordinate, RimroomsAnomalyEventDef definition)
        {
            bool happened;
            switch (definition.effect)
            {
                case AnomalyEffect.LightsFail:
                    happened = LightsFail(map, coordinate);
                    break;
                case AnomalyEffect.ColdSnap:
                    happened = ColdSnap(map, coordinate, definition.magnitude);
                    break;
                case AnomalyEffect.Seepage:
                    happened = Seepage(map, coordinate, definition.magnitude);
                    break;
                case AnomalyEffect.Rearrangement:
                    happened = Rearrange(map, coordinate, definition.magnitude);
                    break;
                default:
                    happened = true;
                    break;
            }
            if (!happened) { return false; }
""",
u"""        private static bool Fire(Map map, CoordinateRecord coordinate, RimroomsAnomalyEventDef definition)
        {
            if (!FireEffect(map, RoomCells(map, coordinate).ToList(), definition.effect, definition.magnitude))
            { return false; }
""")

# ---------------------------------------------------------------- the shared entry point
sub(u"""        /// <summary>
        /// Switches off every light in the space.""",
u"""        /// <summary>
        /// Run one effect over an explicit set of cells.
        ///
        /// **The one implementation of all four effects.** A coordinate passes the cells of its
        /// rooms minus the threshold; the threshold bleed at the headquarters passes the cells of
        /// the room a gate stands in. A second copy of these bodies would drift, and what would
        /// drift out of them are the four promises in invariant 28 -- nothing damages a pawn,
        /// nothing is destroyed, nothing blocks a route, and there is always a countermeasure.
        ///
        /// Returns false when the effect found nothing to do, so a caller can decline to
        /// announce an event that did not happen.
        /// </summary>
        public static bool FireEffect(Map map, List<IntVec3> cells, AnomalyEffect effect, int magnitude)
        {
            if (map == null || cells == null || cells.Count == 0) { return false; }
            switch (effect)
            {
                case AnomalyEffect.LightsFail: return LightsFail(map, cells);
                case AnomalyEffect.ColdSnap: return ColdSnap(map, cells, magnitude);
                case AnomalyEffect.Seepage: return Seepage(map, cells, magnitude);
                case AnomalyEffect.Rearrangement: return Rearrange(map, cells, magnitude);
                default: return true;
            }
        }

        /// <summary>
        /// Switches off every light in the space.""")

# ---------------------------------------------------------------- the four effect bodies
sub(u"""        private static bool LightsFail(Map map, CoordinateRecord coordinate)
        {
            bool any = false;
            foreach (Thing thing in InCoordinate(map, coordinate))""",
u"""        private static bool LightsFail(Map map, List<IntVec3> cells)
        {
            bool any = false;
            foreach (Thing thing in ThingsIn(map, cells))""")

sub(u"""        private static bool ColdSnap(Map map, CoordinateRecord coordinate, int degrees)
        {
            bool any = false;
            var seen = new HashSet<Room>();
            foreach (IntVec3 cell in RoomCells(map, coordinate))""",
u"""        private static bool ColdSnap(Map map, List<IntVec3> cells, int degrees)
        {
            bool any = false;
            var seen = new HashSet<Room>();
            foreach (IntVec3 cell in cells)""")

sub(u"""        private static bool Seepage(Map map, CoordinateRecord coordinate, int amount)
        {
            ThingDef filth = ThingDefOf.Filth_Dirt;
            if (filth == null) { return false; }
            int placed = 0;
            foreach (IntVec3 cell in RoomCells(map, coordinate))""",
u"""        private static bool Seepage(Map map, List<IntVec3> cells, int amount)
        {
            ThingDef filth = ThingDefOf.Filth_Dirt;
            if (filth == null) { return false; }
            int placed = 0;
            foreach (IntVec3 cell in cells)""")

sub(u"""        private static bool Rearrange(Map map, CoordinateRecord coordinate, int count)
        {
            var cells = RoomCells(map, coordinate).ToList();
            if (cells.Count == 0) { return false; }
""",
u"""        private static bool Rearrange(Map map, List<IntVec3> cells, int count)
        {
            if (cells.Count == 0) { return false; }
""")

# ---------------------------------------------------------------- the thing enumerator
sub(u"""        private static IEnumerable<Thing> InCoordinate(Map map, CoordinateRecord coordinate)
        {
            var seen = new HashSet<Thing>();
            foreach (IntVec3 cell in RoomCells(map, coordinate))
            {""",
u"""        private static IEnumerable<Thing> ThingsIn(Map map, List<IntVec3> cells)
        {
            var seen = new HashSet<Thing>();
            foreach (IntVec3 cell in cells)
            {""")

io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('AnomalyEventService re-scoped to cells')
