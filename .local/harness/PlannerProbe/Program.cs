using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

namespace PlannerProbe
{
    /// <summary>
    /// Asks the room planner, outside RimWorld, the one question nobody asked: does the layout it
    /// produces pass the validator that will judge it?
    ///
    /// 0.12.61-dev shipped a planner whose grand hall was 80 cells wide against a validator
    /// ceiling of 34. Every candidate was refused, `TrySelect` returned false, and the player got
    /// a letter saying no safe layout was found -- with nothing in the log and no coordinate. The
    /// planner is pure, so this was always answerable at the desk.
    /// </summary>
    internal static class Program
    {
        private const string Mod = "RimroomsAsyncIndustries";

        private static Type coordinateType;
        private static Type roomType;
        private static MethodInfo trySelect;
        private static MethodInfo validateRooms;
        private static MethodInfo sharesWall;
        private static PropertyInfo widestSpan;
        private static MethodInfo pillarCells;
        private static MethodInfo rockIntrusionCells;
        private static MethodInfo shapeDepthOf;
        private static MethodInfo onRouteCross;
        private static MethodInfo buildCandidate;
        private static MethodInfo anchorFor;
        private static FieldInfo coordinateRooms;
        private static MethodInfo candidateIsSafe;
        private static int candidateBudget;

        private static int Main()
        {
            Assembly assembly = Assembly.Load(Mod);
            coordinateType = assembly.GetType("RimroomsAsyncIndustries.Company.CoordinateRecord", true);
            roomType = assembly.GetType("RimroomsAsyncIndustries.Company.RoomRecord", true);
            Type planner = assembly.GetType("RimroomsAsyncIndustries.Generation.RoomLayoutPlanner", true);
            Type service = assembly.GetType("RimroomsAsyncIndustries.Generation.DestinationService", true);

            const BindingFlags Statics = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
            trySelect = planner.GetMethod("TrySelect", Statics);
            validateRooms = service.GetMethod("ValidateRooms", Statics);
            sharesWall = planner.GetMethod("SharesWall", Statics);
            widestSpan = planner.GetProperty("WidestRoomSpan", Statics);
            pillarCells = planner.GetMethod("PillarCells", Statics);
            rockIntrusionCells = planner.GetMethod("RockIntrusionCells", Statics);
            shapeDepthOf = planner.GetMethod("ShapeDepthOf", Statics);
            Type builder = assembly.GetType("RimroomsAsyncIndustries.Generation.RoomContentBuilder", true);
            onRouteCross = builder.GetMethod("OnRouteCross", Statics);
            buildCandidate = planner.GetMethod("Build", Statics);
            Type facilities = assembly.GetType(
                "RimroomsAsyncIndustries.Generation.FacilityPlanner", true);
            anchorFor = facilities.GetMethod("AnchorFor", Statics);
            coordinateRooms = coordinateType.GetField("rooms",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            candidateIsSafe = planner.GetMethod("CandidateIsSafe", Statics);
            candidateBudget = (int)planner.GetField("CandidateBudget", Statics).GetValue(null);

            Console.WriteLine("WidestRoomSpan = " + widestSpan.GetValue(null, null));
            Console.WriteLine();

            int failures = 0;
            int totalBackToBack = 0;
            bool fellBackEverywhere = false;
            bool noInstitutions = false;
            foreach (int depth in new[] { 1, 2, 3, 4, 5, 6, 8 })
            {
                int refused = 0;
                int rooms = 0;
                int widest = 0;
                int backToBack = 0;
                int tightest = int.MaxValue;
                int starved = 0;
                int shapedRooms = 0;
                int fellBack = 0;
                int institutions = 0;
                int biggest = 0;
                int totalRooms = 0;
                long rockTotal = 0;
                long interiorTotal = 0;
                var reasons = new SortedSet<string>();
                const int Seeds = 200;
                for (int seed = 0; seed < Seeds; seed++)
                {
                    object coordinate = MakeCoordinate("probe-" + depth + "-" + seed, seed * 7919 + 13, depth);
                    object[] args = { coordinate, null };
                    bool selected = (bool)trySelect.Invoke(null, args);
                    if (!selected) { refused++; reasons.Add("TrySelect refused"); continue; }

                    IList layout = (IList)args[1];
                    rooms += layout.Count;

                    // The validator the game itself will run on the committed graph.
                    object[] check = { layout, null };
                    if (!(bool)validateRooms.Invoke(null, check))
                    { refused++; reasons.Add("ValidateRooms: " + check[1]); continue; }

                    foreach (object room in layout)
                    {
                        int width = Field<int>(room, "width");
                        int height = Field<int>(room, "height");
                        if (width > widest) { widest = width; }
                        if (height > widest) { widest = height; }
                    }
                    // **WHICH CANDIDATE WON.** `TrySelect` falls back to a serpentine when
                    // all three real candidates are refused, so a clean `refused` column
                    // can still mean not one real layout was built. It meant exactly that
                    // the first time the maze was measured.
                    int safeCandidates = 0;
                    for (int which = 0; which < candidateBudget; which++)
                    {
                        object built = buildCandidate.Invoke(
                            null, new object[] { coordinate, which });
                        if ((bool)candidateIsSafe.Invoke(null, new object[] { built, depth }))
                        { safeCandidates++; continue; }
                        object[] why = { built, null };
                        validateRooms.Invoke(null, why);
                        string key = why[1] == null ? "reachability or a family rule" : why[1].ToString();
                        reasons.Add("candidate refused: " + key + " -- " + Describe((IList)built));
                    }
                    if (safeCandidates == 0) { fellBack++; }

                    // **DO INSTITUTIONS ACTUALLY FORM?** `FacilityPlanner` was gated on
                    // `coordinate.Depth <= 1`, so a first level had none -- and nothing in
                    // the battery could see it, because the planner existed, was called,
                    // and returned an empty map. Seventh instance of that shape this run.
                    coordinateRooms.SetValue(coordinate, layout);
                    var groups = new Dictionary<int, int>();
                    foreach (object room in layout)
                    {
                        int index = Field<int>(room, "index");
                        var anchor = (int)anchorFor.Invoke(
                            null, new object[] { coordinate, index });
                        if (anchor < 0) { continue; }
                        int seen;
                        groups[anchor] = groups.TryGetValue(anchor, out seen) ? seen + 1 : 1;
                    }
                    institutions += groups.Count;
                    foreach (int size in groups.Values)
                    { if (size > biggest) { biggest = size; } }
                    backToBack += BackToBackPairs(layout);

                    // **CAN EVERY ROOM TAKE ITS LANDMARK?** A room's walls, pillar lattice and
                    // shaped rock, plus the reserved three-cell route cross, can between them
                    // leave a room with nowhere to put anything -- and a landmark that cannot be
                    // placed throws out of `GenStep.Generate`, which stops the level being built
                    // halfway. That cost a launch: the owner got a Backrooms map with no content,
                    // `EnsureSite` reported failure, and the gate was never marked.
                    foreach (object room in layout)
                    {
                        // **HOW SQUARE IS IT, REALLY.** The owner's complaint, as a number.
                        totalRooms++;
                        int roomShapeDepth = (int)shapeDepthOf.Invoke(
                            null, new object[] { layout, room, depth });
                        int rock = 0;
                        foreach (Verse.IntVec3 rockCell in (IEnumerable<Verse.IntVec3>)
                            rockIntrusionCells.Invoke(null, new object[] { room, roomShapeDepth }))
                        { rock++; }
                        if (rock > 0) { shapedRooms++; }
                        rockTotal += rock;
                        var roomBounds = (Verse.CellRect)roomType.GetProperty("Bounds")
                            .GetValue(room, null);
                        interiorTotal += roomBounds.ContractedBy(1).Area;
                        int margined = MarginedCells(layout, room, depth);
                        if (margined < tightest) { tightest = margined; }
                        if (margined <= 1) { starved++; }
                        if (LandmarkCells(layout, room, depth) == 0)
                        {
                            reasons.Add("room " + Field<int>(room, "index") + " ("
                                        + Field<string>(room, "familyId") + ", "
                                        + Field<int>(room, "width") + "x"
                                        + Field<int>(room, "height")
                                        + ") has nowhere to place a landmark");
                            refused++;
                            break;
                        }
                    }
                }

                totalBackToBack += backToBack;
                string verdict = refused == 0 ? "OK  " : "FAIL";
                Console.WriteLine(string.Format(
                    "{0} depth {1,-2} refused {2,3}/{3} rooms {4,4:0.0} widest {5,3} pairs {6,4} margin {7,3} starved {8,4} shaped {9,5:0.0}% rock {10,4:0.0}% fellback {11,4} institutions {12,5:0.0} biggest {13,3}",
                    verdict, depth, refused, Seeds, refused == Seeds ? 0.0 : (double)rooms / (Seeds - refused),
                    widest, backToBack, tightest == int.MaxValue ? -1 : tightest, starved,
                    totalRooms == 0 ? 0.0 : 100.0 * shapedRooms / totalRooms,
                    interiorTotal == 0 ? 0.0 : 100.0 * rockTotal / interiorTotal,
                    fellBack,
                    refused == Seeds ? 0.0 : (double)institutions / (Seeds - refused),
                    biggest));
                foreach (string reason in reasons) { Console.WriteLine("        reason: " + reason); }
                if (refused != 0) { failures++; }
                if (fellBack >= Seeds) { fellBackEverywhere = true; }
                if (institutions == 0) { noInstitutions = true; }
            }

            Console.WriteLine();
            if (failures != 0)
            {
                Console.WriteLine("PROBE FAILED: " + failures + " depth band(s) refused a layout.");
                return 1;
            }
            if (fellBackEverywhere)
            {
                Console.WriteLine("PROBE FAILED: at least one depth band built no real candidate "
                                  + "at all and the fallback caught every seed.");
                return 1;
            }
            if (noInstitutions)
            {
                Console.WriteLine("PROBE FAILED: a depth band formed no institutions at "
                                  + "all, so no school, hospital, armoury or storage "
                                  + "complex can exist there.");
                return 1;
            }
            if (totalBackToBack == 0)
            {
                // A silent nothing is the failure mode this whole checkpoint is about: the feature
                // compiled, the layout validated, and not one pair was ever actually produced.
                Console.WriteLine("PROBE FAILED: not one back-to-back pair in any layout.");
                return 1;
            }
            Console.WriteLine("PROBE HELD: every depth produced a layout the validator accepts, "
                              + "and " + totalBackToBack + " back-to-back pairs exist.");
            return 0;
        }

        /// <summary>
        /// Facts about a refused layout, so `RR_Generation_InvalidRoomGraph` stops being a dozen
        /// rules wearing one name.
        ///
        /// **Observations, not a second validator.** Every line here reads the layout and
        /// reports; none of it decides whether the layout is acceptable. Re-implementing
        /// `ValidateRooms` in the probe would give two opinions about one question, which is the
        /// defect this whole harness exists to catch.
        /// </summary>
        private static string Describe(IList layout)
        {
            var families = new Dictionary<string, int>();
            foreach (object room in layout)
            {
                string family = Field<string>(room, "familyId") ?? "(null)";
                int seen;
                families[family] = families.TryGetValue(family, out seen) ? seen + 1 : 1;
            }
            var report = new List<string> { layout.Count + " rooms" };
            foreach (string unique in new[] { "threshold_room", "office_copy", "return_gallery",
                                              "service_passage" })
            {
                int seen;
                report.Add(unique + "=" + (families.TryGetValue(unique, out seen) ? seen : 0));
            }

            for (int index = 0; index < layout.Count; index++)
            {
                object room = layout[index];
                int width = Field<int>(room, "width");
                int height = Field<int>(room, "height");
                if (width % 2 != 0 || height % 2 != 0)
                { report.Add("odd span at room " + index + " (" + width + "x" + height + ")"); break; }
            }

            for (int index = 0; index < layout.Count; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                if (a.minX < 1 || a.minZ < 1 || a.maxX > 298 || a.maxZ > 298)
                { report.Add("room " + index + " off the map " + a); break; }
            }

            bool overlapFound = false;
            for (int index = 0; index < layout.Count && !overlapFound; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                for (int other = index + 1; other < layout.Count; other++)
                {
                    var b = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[other], null);
                    if (!a.Overlaps(b)) { continue; }
                    report.Add("rooms " + index + " and " + other + " overlap " + a + " / " + b);
                    overlapFound = true;
                    break;
                }
            }

            bool axisFound = false;
            for (int index = 0; index < layout.Count && !axisFound; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                foreach (int linked in Field<List<int>>(layout[index], "links"))
                {
                    if (linked <= index || linked >= layout.Count) { continue; }
                    var b = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[linked], null);
                    if (a.CenterCell.x == b.CenterCell.x || a.CenterCell.z == b.CenterCell.z) { continue; }
                    report.Add("link " + index + "-" + linked + " shares no axis "
                               + a.CenterCell + " / " + b.CenterCell);
                    axisFound = true;
                    break;
                }
            }

            return string.Join(", ", report.ToArray());
        }

        /// <summary>
        /// Cells in this room that could hold a landmark: inside the walls, off the reserved
        /// route cross, and not on a pillar or on shaped rock.
        ///
        /// **Every rule here is asked of the shipping code**, not re-derived: `PillarCells`,
        /// `RockIntrusionCells` and `ShapeDepthOf` from the planner, `OnRouteCross` from the
        /// content builder. The walkable margin a fixture prefers is deliberately NOT applied,
        /// because it is a preference -- what this counts is whether a landmark can be placed at
        /// all, which is the thing that throws.
        /// </summary>
        private static int LandmarkCells(IList layout, object room, int depth)
        {
            var bounds = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(room, null);
            Verse.CellRect interior = bounds.ContractedBy(1);
            var blocked = new HashSet<Verse.IntVec3>();
            foreach (Verse.IntVec3 cell in (IEnumerable<Verse.IntVec3>)pillarCells.Invoke(
                null, new[] { room }))
            { blocked.Add(cell); }
            int shapeDepth = (int)shapeDepthOf.Invoke(null, new object[] { layout, room, depth });
            foreach (Verse.IntVec3 cell in (IEnumerable<Verse.IntVec3>)rockIntrusionCells.Invoke(
                null, new object[] { room, shapeDepth }))
            { blocked.Add(cell); }

            int count = 0;
            foreach (Verse.IntVec3 cell in interior.Cells)
            {
                if (blocked.Contains(cell)) { continue; }
                if ((bool)onRouteCross.Invoke(null, new object[] { room, cell })) { continue; }
                count++;
            }
            return count;
        }

        /// <summary>
        /// Of those, how many also have a clear walkable margin -- no wall, pillar or rock within
        /// one cell -- **before a single fixture is placed.**
        ///
        /// This is the measurement, not an argument. A room reporting **one** is a room where the
        /// first fixture takes the only margined cell and the second has none, which is exactly
        /// the throw that stopped a level being built. It is reported rather than enforced,
        /// because a room with one margined cell is now a room with one margined fixture and the
        /// rest against the walls -- which is fine.
        /// </summary>
        private static int MarginedCells(IList layout, object room, int depth)
        {
            var bounds = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(room, null);
            Verse.CellRect interior = bounds.ContractedBy(1);
            var blocked = new HashSet<Verse.IntVec3>();
            foreach (Verse.IntVec3 cell in (IEnumerable<Verse.IntVec3>)pillarCells.Invoke(
                null, new[] { room }))
            { blocked.Add(cell); }
            int shapeDepth = (int)shapeDepthOf.Invoke(null, new object[] { layout, room, depth });
            foreach (Verse.IntVec3 cell in (IEnumerable<Verse.IntVec3>)rockIntrusionCells.Invoke(
                null, new object[] { room, shapeDepth }))
            { blocked.Add(cell); }
            // The room's own perimeter is wall, and wall is an edifice like any other.
            foreach (Verse.IntVec3 cell in bounds.Cells)
            { if (!interior.Contains(cell)) { blocked.Add(cell); } }

            // **AND THE LAMP ON EVERY PILLAR.** `SpawnPillarLamps` puts one at the first free
            // cardinal neighbour of each pillar, and a wall lamp is an edifice, so it shrinks the
            // margin exactly as a pillar does. It was added the same checkpoint as the varied
            // room spans, and modelling the pillars without it understates the pressure by half.
            Verse.IntVec3[] sides =
            {
                Verse.IntVec3.North, Verse.IntVec3.East, Verse.IntVec3.South, Verse.IntVec3.West,
            };
            var lamps = new List<Verse.IntVec3>();
            foreach (Verse.IntVec3 pillar in (IEnumerable<Verse.IntVec3>)pillarCells.Invoke(
                null, new[] { room }))
            {
                for (int side = 0; side < sides.Length; side++)
                {
                    Verse.IntVec3 cell = pillar + sides[side];
                    if (!interior.Contains(cell) || blocked.Contains(cell) || lamps.Contains(cell))
                    { continue; }
                    lamps.Add(cell);
                    break;
                }
            }
            foreach (Verse.IntVec3 cell in lamps) { blocked.Add(cell); }

            int count = 0;
            foreach (Verse.IntVec3 cell in interior.Cells)
            {
                if (blocked.Contains(cell)) { continue; }
                if ((bool)onRouteCross.Invoke(null, new object[] { room, cell })) { continue; }
                bool clear = true;
                for (int dx = -1; dx <= 1 && clear; dx++)
                {
                    for (int dz = -1; dz <= 1 && clear; dz++)
                    {
                        if (blocked.Contains(new Verse.IntVec3(cell.x + dx, 0, cell.z + dz)))
                        { clear = false; }
                    }
                }
                if (clear) { count++; }
            }
            return count;
        }

        /// <summary>Linked pairs standing wall against wall, by the planner's own predicate.</summary>
        private static int BackToBackPairs(IList layout)
        {
            var byIndex = new Dictionary<int, object>();
            foreach (object room in layout) { byIndex[Field<int>(room, "index")] = room; }
            int pairs = 0;
            foreach (object room in layout)
            {
                int index = Field<int>(room, "index");
                foreach (int linked in Field<List<int>>(room, "links"))
                {
                    if (linked <= index) { continue; }
                    object other;
                    if (!byIndex.TryGetValue(linked, out other)) { continue; }
                    if ((bool)sharesWall.Invoke(null, new[] { room, other })) { pairs++; }
                }
            }
            return pairs;
        }

        private static object MakeCoordinate(string id, int seed, int depth)
        {
            object coordinate = Activator.CreateInstance(coordinateType);
            Set(coordinate, "id", id);
            Set(coordinate, "label", id);
            Set(coordinate, "seed", seed);
            Set(coordinate, "depth", depth);
            Set(coordinate, "generatorVersion", 1);
            Set(coordinate, "roomLibraryVersion", 1);
            return coordinate;
        }

        private static void Set(object target, string field, object value)
        {
            FieldInfo info = target.GetType().GetField(field,
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (info == null) { throw new MissingFieldException(target.GetType().Name, field); }
            info.SetValue(target, value);
        }

        private static T Field<T>(object target, string field)
        {
            FieldInfo info = target.GetType().GetField(field,
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (info == null) { throw new MissingFieldException(target.GetType().Name, field); }
            return (T)info.GetValue(target);
        }
    }
}
