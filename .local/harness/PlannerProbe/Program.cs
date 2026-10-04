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
        private static MethodInfo areNeighbourRooms;
        private static MethodInfo corridorLegs;
        private static PropertyInfo widestSpan;
        private static MethodInfo pillarCells;
        private static MethodInfo rockIntrusionCells;
        private static MethodInfo shapeDepthOf;
        private static MethodInfo onRouteCross;
        private static MethodInfo buildCandidate;
        private static MethodInfo anchorFor;
        private static FieldInfo coordinateRooms;
        private static MethodInfo candidateIsSafe;
        private static MethodInfo motifFor;
        private static Type motifType;
        private const BindingFlags Instanced = BindingFlags.Instance | BindingFlags.Public
            | BindingFlags.NonPublic;
        private static MethodInfo shapeFormOf;

        /// <summary>
        /// The motif of the coordinate being measured, set once per coordinate.
        ///
        /// A field rather than a parameter threaded through six methods: this is a harness, the
        /// value is constant for the whole of one coordinate's measurement, and the alternative
        /// is six signatures carrying a diagnostic concern. It is set immediately after the
        /// coordinate is built and read nowhere else.
        /// </summary>
        private static object currentMotif;
        // Read from DestinationService rather than written here, so the fill percentage is
        // against the map the game actually generates. A constant of our own would be a second
        // opinion about how big a coordinate is.
        private static int mapWidth;
        private static int mapHeight;
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
            areNeighbourRooms = planner.GetMethod("AreNeighbourRooms", Statics);
            corridorLegs = planner.GetMethod("CorridorLegs", Statics);
            widestSpan = planner.GetProperty("WidestRoomSpan", Statics);
            mapWidth = (int)service.GetField("MapWidth", Statics).GetValue(null);
            mapHeight = (int)service.GetField("MapHeight", Statics).GetValue(null);
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
            shapeFormOf = planner.GetMethod("ShapeFormOf", Statics);
            motifType = planner.Assembly
                .GetType("RimroomsAsyncIndustries.Generation.CoordinateMotif");
            motifFor = motifType.GetMethod("For", Statics);
            candidateBudget = (int)planner.GetField("CandidateBudget", Statics).GetValue(null);

            Console.WriteLine("WidestRoomSpan = " + widestSpan.GetValue(null, null));
            Console.WriteLine();

            int failures = 0;
            int totalBackToBack = 0;
            bool fellBackEverywhere = false;
            bool noInstitutions = false;
            int roomsWithNoApproach = 0;
            foreach (int depth in new[] { 1, 2, 3, 4, 5, 6, 8 })
            {
                int refused = 0;
                int rooms = 0;
                int widest = 0;
                int backToBack = 0;
                int tightest = int.MaxValue;
                int starved = 0;
                int tightestApproach = int.MaxValue;
                int noApproach = 0;
                int shapedRooms = 0;
                int fellBack = 0;
                int institutions = 0;
                int biggest = 0;
                int totalRooms = 0;
                long rockTotal = 0;
                long interiorTotal = 0;
                // **DEGREE AND FILL, ADDED 2026-10-03, because this probe could not see the
                // defect the owner was reporting.** Owner, verbatim: *"the rooms are just one
                // exit one entrance ... room connected to like 0 - 10 other rooms and not have so
                // much empty rock space where nothing exists ... FILL THE SPACE WITH ROOMS"*.
                // Every column above is about whether a layout is LEGAL; none of them is about
                // whether it reads as a maze. A checker that cannot measure the complaint cannot
                // confirm the fix either.
                long degreeTotal = 0;
                int degreeMax = 0;
                int degreeOne = 0;
                int degreeZero = 0;
                long roomCellTotal = 0;
                // **IS IT A PATTERN WITH VARIATIONS, OR IS IT NOISE?** Owner, 2026-10-03:
                // *"repeated patternes in variations"*. Seven room shapes already existed and
                // every room rolled its own independently, which is not a pattern -- and nothing
                // in the battery could see that, exactly as nothing could see the average degree
                // before this probe was taught to count links. Two numbers: the share of rooms
                // that take the coordinate's motif shape, and how many distinct shapes a level
                // holds. A floor that is all motif is monotonous; one at a seventh of it is
                // random; the owner asked for the ground in between, and it has to be visible to
                // be aimed at.
                int onMotif = 0;
                // **ARE THERE ROADS AND BLOCKS, OR ONLY THE INTENTION OF THEM?** Owner,
                // 2026-10-03: *"roads neighborrs hood"*. A braid makes loops and a walk makes
                // branches; neither ever deliberately makes a LINE, and the back-to-back push
                // rolls per room so its pairs are scattered rather than clustered. Two numbers:
                // the longest straight run of linked rooms on one level, and the largest group
                // standing wall to wall. Both were invisible before, exactly as the average
                // degree was.
                int longestRoad = 0;
                int largestBlock = 0;
                var shapesSeen = new HashSet<int>();
                // **WHERE THE GRAND HALL LANDS.** Owner, 2026-10-03: *"starting room is not to
                // always be in bottom left of map"*. It was two literals, and nothing measured
                // it -- so "always the same corner" was invisible to every instrument here.
                // Tracked as distinct hall origins across the seed sweep plus how many of them
                // are the old corner, because "it varies" and "it stopped being the corner" are
                // two different claims and only the second is what the owner asked for.
                var hallOrigins = new HashSet<string>();
                int hallAtOldCorner = 0;
                int hallVertical = 0;
                var reasons = new SortedSet<string>();
                const int Seeds = 200;
                for (int seed = 0; seed < Seeds; seed++)
                {
                    object coordinate = MakeCoordinate("probe-" + depth + "-" + seed, seed * 7919 + 13, depth);
                    // **THE COORDINATE'S MOTIF, from the planner rather than re-derived.** Owner,
                    // 2026-10-03: *"repeated patternes in variations"*. Every shape decision now
                    // reads it, so the harness has to hold the same one the carver would.
                    currentMotif = motifFor.Invoke(null, new object[] { coordinate });
                    object[] args = { coordinate, null };
                    bool selected = (bool)trySelect.Invoke(null, args);
                    if (!selected) { refused++; reasons.Add("TrySelect refused"); continue; }

                    IList layout = (IList)args[1];
                    rooms += layout.Count;

                    // The validator the game itself will run on the committed graph.
                    object[] check = { layout, null };
                    if (!(bool)validateRooms.Invoke(null, check))
                    { refused++; reasons.Add("ValidateRooms: " + check[1]); continue; }

                    // Room 0 is the hall by construction (`AssignMazeFamilies` sets index 0 to
                    // the threshold family), so its bounds are where the hall is.
                    if (layout.Count > 0)
                    {
                        var hallBounds = (Verse.CellRect)roomType.GetProperty("Bounds")
                            .GetValue(layout[0], null);
                        hallOrigins.Add(hallBounds.minX + "," + hallBounds.minZ);
                        if (hallBounds.Height > hallBounds.Width) { hallVertical++; }
                        // The old behaviour put the hall's first slot at index 0 on both axes.
                        if (hallBounds.minX < mapWidth / 4 && hallBounds.minZ < mapHeight / 4)
                        { hallAtOldCorner++; }
                    }

                    foreach (object room in layout)
                    {
                        int width = Field<int>(room, "width");
                        int height = Field<int>(room, "height");
                        if (width > widest) { widest = width; }
                        if (height > widest) { widest = height; }

                        // How many other rooms this one actually reaches, and how much of the map
                        // it occupies. `links` is the committed graph the game will save, so this
                        // is the degree a player walks rather than the degree the planner meant.
                        int degree = Field<List<int>>(room, "links").Count;
                        degreeTotal += degree;
                        if (degree > degreeMax) { degreeMax = degree; }
                        if (degree == 0) { degreeZero++; }
                        if (degree == 1) { degreeOne++; }
                        roomCellTotal += ((Verse.CellRect)roomType.GetProperty("Bounds")
                            .GetValue(room, null)).Area;
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
                        if ((bool)candidateIsSafe.Invoke(null,
                            new object[] { built, depth, currentMotif }))
                        { safeCandidates++; continue; }
                        object[] why = { built, null };
                        validateRooms.Invoke(null, why);
                        string key = why[1] == null ? "reachability or a family rule" : why[1].ToString();
                        reasons.Add("candidate refused: " + key + " -- " + Describe((IList)built, depth));
                    }
                    if (safeCandidates == 0) { fellBack++; }

                    int road = LongestRoad(layout);
                    if (road > longestRoad) { longestRoad = road; }
                    int block = LargestWallToWallBlock(layout);
                    if (block > largestBlock) { largestBlock = block; }

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
                            rockIntrusionCells.Invoke(null,
                                new object[] { room, roomShapeDepth, currentMotif }))
                        { rock++; }
                        if (rock > 0) { shapedRooms++; }
                        int motifShape = (int)motifType.GetField("Shape", Instanced)
                            .GetValue(currentMotif);
                        int roomShape = (int)shapeFormOf.Invoke(null,
                            new object[] { room, roomShapeDepth, currentMotif });
                        shapesSeen.Add(roomShape);
                        if (roomShape == motifShape) { onMotif++; }
                        rockTotal += rock;
                        var roomBounds = (Verse.CellRect)roomType.GetProperty("Bounds")
                            .GetValue(room, null);
                        interiorTotal += roomBounds.ContractedBy(1).Area;
                        int margined = MarginedCells(layout, room, depth);
                        if (margined < tightest) { tightest = margined; }
                        if (margined <= 1) { starved++; }
                        // **AND CAN THE LANDMARK KEEP A WAY UP TO IT?** See ApproachCells: a
                        // landmark off the clear route cross is back to the lottery that cost the
                        // owner a start, so the count that matters is how often the structural
                        // guarantee is available rather than how often the fallback saves it.
                        int approach = ApproachCells(layout, room, depth);
                        if (approach < tightestApproach) { tightestApproach = approach; }
                        if (approach == 0) { noApproach++; }
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
                    "{0} depth {1,-2} refused {2,3}/{3} rooms {4,4:0.0} widest {5,3} pairs {6,4} margin {7,3} starved {8,4} shaped {9,5:0.0}% rock {10,4:0.0}% fellback {11,4} institutions {12,5:0.0} biggest {13,3} approach {14,3} noapproach {15,4}",
                    verdict, depth, refused, Seeds, refused == Seeds ? 0.0 : (double)rooms / (Seeds - refused),
                    widest, backToBack, tightest == int.MaxValue ? -1 : tightest, starved,
                    totalRooms == 0 ? 0.0 : 100.0 * shapedRooms / totalRooms,
                    interiorTotal == 0 ? 0.0 : 100.0 * rockTotal / interiorTotal,
                    fellBack,
                    refused == Seeds ? 0.0 : (double)institutions / (Seeds - refused),
                    biggest,
                    tightestApproach == int.MaxValue ? -1 : tightestApproach, noApproach));
                // The maze line. Degree is what *"one exit one entrance"* means as a number, and
                // roomfill is what *"so much empty rock space"* means as a number. Reported
                // beside the legality line rather than folded into it, because a layout can be
                // perfectly legal and still read as a string of pearls -- which is exactly the
                // report this was added for.
                int measuredRooms = totalRooms == 0 ? 1 : totalRooms;
                int mapArea = mapWidth * mapHeight;
                Console.WriteLine(string.Format(
                    "     maze  depth {0,-2} degree avg {1,4:0.00} max {2,2} deg0 {3,5:0.0}% deg1 {4,5:0.0}% roomfill {5,4:0.0}% of {6}x{7}"
                    + "  hallspots {8,3} corner {9,5:0.0}% vertical {10,5:0.0}%"
                    + "  onmotif {11,5:0.0}% shapes {12} road {13,2} block {14,2}",
                    depth, (double)degreeTotal / measuredRooms, degreeMax,
                    100.0 * degreeZero / measuredRooms, 100.0 * degreeOne / measuredRooms,
                    refused == Seeds ? 0.0 : 100.0 * roomCellTotal / ((Seeds - refused) * (long)mapArea),
                    mapWidth, mapHeight,
                    hallOrigins.Count,
                    refused == Seeds ? 0.0 : 100.0 * hallAtOldCorner / (Seeds - refused),
                    refused == Seeds ? 0.0 : 100.0 * hallVertical / (Seeds - refused),
                    100.0 * onMotif / measuredRooms, shapesSeen.Count,
                    longestRoad, largestBlock));
                foreach (string reason in reasons) { Console.WriteLine("        reason: " + reason); }
                if (refused != 0) { failures++; }
                if (fellBack >= Seeds) { fellBackEverywhere = true; }
                if (institutions == 0) { noInstitutions = true; }
                if (noApproach != 0) { roomsWithNoApproach += noApproach; }
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
            if (roomsWithNoApproach != 0)
            {
                // **The fallback must not be the thing that works.** A room with no landmark cell
                // beside its clear route cross puts that landmark back on the lottery that cost
                // the owner a start: no reserved approach, so the dressing fills every neighbour,
                // so `ValidatePlacedLayout` finds a clue nobody can reach. Measured at zero
                // across every band when it was written, so anything above zero is new.
                Console.WriteLine("PROBE FAILED: " + roomsWithNoApproach + " room(s) have no "
                                  + "landmark cell beside their clear route cross, so the "
                                  + "landmark's approach is not reserved and the dressing can "
                                  + "seal the clue in.");
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
                              + totalBackToBack + " back-to-back pairs exist, and every room can "
                              + "put its landmark beside a reserved route cross.");
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
        private static string Describe(IList layout, int depth)
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

            // **THE PROBE ASKS THE PLANNER RATHER THAN RE-DERIVING ADJACENCY, and it used to do
            // the opposite.** This held `a.CenterCell.x == b.CenterCell.x || ...z == ...z` -- a
            // third copy of the rule, beside the planner's and the validator's. The moment
            // corridors learned to bend it started reporting `shares no axis` for links that are
            // perfectly legal, so every refusal diagnosis it printed was wrong and pointed at the
            // wrong rule. A diagnostic that re-derives the thing it is diagnosing is the same
            // defect class it exists to find.
            bool linkFound = false;
            for (int index = 0; index < layout.Count && !linkFound; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                foreach (int linked in Field<List<int>>(layout[index], "links"))
                {
                    if (linked <= index || linked >= layout.Count) { continue; }
                    var b = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[linked], null);
                    bool neighbours = (bool)areNeighbourRooms.Invoke(null,
                        new object[] { layout[index], layout[linked] });
                    if (!neighbours)
                    {
                        report.Add("link " + index + "-" + linked + " is not a shape a corridor can join "
                                   + a.CenterCell + " / " + b.CenterCell);
                        linkFound = true;
                        break;
                    }
                    bool shared = (bool)sharesWall.Invoke(null,
                        new object[] { layout[index], layout[linked] });
                    if (shared) { continue; }
                    var legs = (System.Collections.ICollection)corridorLegs.Invoke(null,
                        new object[] { layout[index], layout[linked], depth, layout });
                    if (legs.Count > 0) { continue; }
                    report.Add("link " + index + "-" + linked + " has no route under it "
                               + a.CenterCell + " / " + b.CenterCell);
                    linkFound = true;
                    break;
                }
            }

            int tooMany = 0;
            for (int index = 0; index < layout.Count; index++)
            {
                int count = Field<List<int>>(layout[index], "links").Count;
                if (count > tooMany) { tooMany = count; }
            }
            // **SIXTEEN, not eight.** `MaximumUndirectedEdgesPerRoom` bounds the layout's TOTAL
            // edges as `2 * 8 * rooms`, so it is an average rather than a per-room cap -- a
            // junction may hold far more while the average stays low, and that spread is the
            // point of it. The geometric maximum is the sixteen slots a lane route can reach.
            if (tooMany > 16)
            { report.Add("a room carries " + tooMany + " links, past the sixteen the grid can reach"); }

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
            HashSet<Verse.IntVec3> blocked = BlockedCells(layout, room, depth);

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
            HashSet<Verse.IntVec3> blocked = BlockedCells(layout, room, depth);

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

        /// <summary>
        /// Of the cells that could hold a landmark, how many sit orthogonally beside a cell of
        /// the room's **clear, joined-up route cross** -- which is what
        /// `RoomContentBuilder.RouteTrunk` offers a landmark, and what
        /// `ValidatePlacedLayout` then demands of it.
        ///
        /// ## Why this is measured and not assumed
        ///
        /// A landmark beside a cross cell can never be sealed in, because cross cells are
        /// reserved for the whole of population. A landmark that had to fall back off the cross
        /// is back to the old lottery, and the old lottery is what cost the owner a start:
        /// `RR_Generation_UnreachableRequiredCell`, so no level, so no gate, so
        /// *"i ended up in the world map with no connection to the back rooms"*.
        ///
        /// **Zero here means the fallback is carrying that room**, and a net that catches
        /// everything is a net nobody can see through. That is the same blind spot as the
        /// `fellback` column, which reported a clean `refused 0/200` while not one real maze had
        /// been built.
        ///
        /// Pillar lamps are in the blocked set, because `SpawnPillarLamps` reserves against
        /// `reservedProviderCells` and **the route cross is not in that set** -- it belongs to
        /// `RoomContentBuilder`. So a lamp really can stand on a cross cell and really does take
        /// it out of the trunk, exactly as `ClearTrunkCell` finds when it asks the live map.
        /// </summary>
        private static int ApproachCells(IList layout, object room, int depth)
        {
            var bounds = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(room, null);
            Verse.CellRect interior = bounds.ContractedBy(1);
            HashSet<Verse.IntVec3> blocked = BlockedCells(layout, room, depth);

            // The trunk: clear cross cells continuous with the one nearest the middle.
            var cross = new List<Verse.IntVec3>();
            foreach (Verse.IntVec3 cell in interior.Cells)
            {
                if (blocked.Contains(cell)) { continue; }
                if (!(bool)onRouteCross.Invoke(null, new object[] { room, cell })) { continue; }
                cross.Add(cell);
            }
            if (cross.Count == 0) { return 0; }
            Verse.IntVec3 centre = bounds.CenterCell;
            cross.Sort(delegate (Verse.IntVec3 left, Verse.IntVec3 right)
            {
                int byDistance = Squared(left, centre) - Squared(right, centre);
                if (byDistance != 0) { return byDistance; }
                if (left.x != right.x) { return left.x - right.x; }
                return left.z - right.z;
            });
            var available = new HashSet<Verse.IntVec3>(cross);
            var trunk = new HashSet<Verse.IntVec3> { cross[0] };
            var pending = new Queue<Verse.IntVec3>();
            pending.Enqueue(cross[0]);
            Verse.IntVec3[] sides =
            {
                Verse.IntVec3.North, Verse.IntVec3.East, Verse.IntVec3.South, Verse.IntVec3.West,
            };
            while (pending.Count > 0)
            {
                Verse.IntVec3 current = pending.Dequeue();
                for (int side = 0; side < sides.Length; side++)
                {
                    Verse.IntVec3 next = current + sides[side];
                    if (!available.Contains(next) || !trunk.Add(next)) { continue; }
                    pending.Enqueue(next);
                }
            }

            int count = 0;
            foreach (Verse.IntVec3 cell in interior.Cells)
            {
                if (blocked.Contains(cell)) { continue; }
                if ((bool)onRouteCross.Invoke(null, new object[] { room, cell })) { continue; }
                for (int side = 0; side < sides.Length; side++)
                {
                    if (!trunk.Contains(cell + sides[side])) { continue; }
                    count++;
                    break;
                }
            }
            return count;
        }

        /// <summary>
        /// Squared distance between two cells on the floor plane. Written out rather than taken
        /// from Verse, which the probe's reference set does not reach.
        /// </summary>
        private static int Squared(Verse.IntVec3 from, Verse.IntVec3 to)
        {
            int dx = from.x - to.x;
            int dz = from.z - to.z;
            return dx * dx + dz * dz;
        }

        /// <summary>
        /// Everything standing in this room before a single fixture is placed: its own perimeter
        /// wall, the pillar lattice, the shaped rock, and the lamp on every pillar.
        ///
        /// **One derivation, three callers.** `LandmarkCells`, `MarginedCells` and
        /// `ApproachCells` each built this set, and three copies of one rule is the defect this
        /// project keeps meeting -- it is why the planner and the validator once disagreed about
        /// the widest room in the place.
        /// </summary>
        private static HashSet<Verse.IntVec3> BlockedCells(IList layout, object room, int depth)
        {
            var bounds = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(room, null);
            Verse.CellRect interior = bounds.ContractedBy(1);
            var blocked = new HashSet<Verse.IntVec3>();
            foreach (Verse.IntVec3 cell in (IEnumerable<Verse.IntVec3>)pillarCells.Invoke(
                null, new[] { room }))
            { blocked.Add(cell); }
            int shapeDepth = (int)shapeDepthOf.Invoke(null, new object[] { layout, room, depth });
            foreach (Verse.IntVec3 cell in (IEnumerable<Verse.IntVec3>)rockIntrusionCells.Invoke(
                null, new object[] { room, shapeDepth, currentMotif }))
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
            return blocked;
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

        /// <summary>
        /// The longest straight run of rooms linked end to end on this layout.
        ///
        /// **Observation, not a second opinion.** It asks the planner's own `OnRoad` nothing; it
        /// counts collinear consecutive links, which is the property `OnRoad` is a question about.
        /// A road of three is the shortest thing the word can mean.
        /// </summary>
        private static int LongestRoad(IList layout)
        {
            int best = 0;
            for (int index = 0; index < layout.Count; index++)
            {
                var from = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                foreach (int linked in Field<List<int>>(layout[index], "links"))
                {
                    if (linked < 0 || linked >= layout.Count) { continue; }
                    var next = (Verse.CellRect)roomType.GetProperty("Bounds")
                        .GetValue(layout[linked], null);
                    bool alongX = from.CenterCell.z == next.CenterCell.z;
                    bool alongZ = from.CenterCell.x == next.CenterCell.x;
                    if (alongX == alongZ) { continue; }
                    int run = 2 + WalkOn(layout, index, linked, alongX);
                    if (run > best) { best = run; }
                }
            }
            return best;
        }

        /// <summary>How many more rooms the line continues for past <paramref name="through"/>.</summary>
        private static int WalkOn(IList layout, int from, int through, bool alongX)
        {
            var near = ((Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[from], null))
                .CenterCell;
            var hub = ((Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[through], null))
                .CenterCell;
            foreach (int linked in Field<List<int>>(layout[through], "links"))
            {
                if (linked == from || linked < 0 || linked >= layout.Count) { continue; }
                var far = ((Verse.CellRect)roomType.GetProperty("Bounds")
                    .GetValue(layout[linked], null)).CenterCell;
                if (alongX)
                {
                    if (far.z != hub.z) { continue; }
                    if (near.x < hub.x ? far.x <= hub.x : far.x >= hub.x) { continue; }
                }
                else
                {
                    if (far.x != hub.x) { continue; }
                    if (near.z < hub.z ? far.z <= hub.z : far.z >= hub.z) { continue; }
                }
                return 1 + WalkOn(layout, through, linked, alongX);
            }
            return 0;
        }

        /// <summary>
        /// The largest group of rooms standing wall to wall, asked of the planner's own
        /// `SharesWall` so the probe keeps no third copy of that rule.
        ///
        /// A SCATTERED pair is not a neighbourhood. The push loop produced two to three hundred
        /// pairs per depth and no blocks at all, which is the difference this counts.
        /// </summary>
        private static int LargestWallToWallBlock(IList layout)
        {
            var seen = new HashSet<int>();
            int best = 0;
            for (int start = 0; start < layout.Count; start++)
            {
                if (!seen.Add(start)) { continue; }
                var pending = new Queue<int>();
                pending.Enqueue(start);
                int size = 0;
                while (pending.Count > 0)
                {
                    int current = pending.Dequeue();
                    size++;
                    for (int other = 0; other < layout.Count; other++)
                    {
                        if (seen.Contains(other)) { continue; }
                        if (!(bool)sharesWall.Invoke(null, new[] { layout[current], layout[other] }))
                        { continue; }
                        seen.Add(other);
                        pending.Enqueue(other);
                    }
                }
                if (size > best) { best = size; }
            }
            return best;
        }

    }
}
