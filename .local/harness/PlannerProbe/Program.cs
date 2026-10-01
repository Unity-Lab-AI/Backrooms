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

            Console.WriteLine("WidestRoomSpan = " + widestSpan.GetValue(null, null));
            Console.WriteLine();

            int failures = 0;
            int totalBackToBack = 0;
            foreach (int depth in new[] { 1, 2, 3, 4, 5, 6, 8 })
            {
                int refused = 0;
                int rooms = 0;
                int widest = 0;
                int backToBack = 0;
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
                    backToBack += BackToBackPairs(layout);
                }

                totalBackToBack += backToBack;
                string verdict = refused == 0 ? "OK  " : "FAIL";
                Console.WriteLine(string.Format(
                    "{0} depth {1,-2}  refused {2,3}/{3}  avg rooms {4,5:0.0}  widest {5,3}  back-to-back pairs {6,4}",
                    verdict, depth, refused, Seeds, refused == Seeds ? 0.0 : (double)rooms / (Seeds - refused),
                    widest, backToBack));
                foreach (string reason in reasons) { Console.WriteLine("        reason: " + reason); }
                if (refused != 0) { failures++; }
            }

            Console.WriteLine();
            if (failures != 0)
            {
                Console.WriteLine("PROBE FAILED: " + failures + " depth band(s) refused a layout.");
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
