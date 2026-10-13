using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The rest of batch 2 (storage and food) of the owner's playbook as code: the freezer, the butcher table and the
    /// kitchen bills that go on when a stove or butcher table finishes. Each returns a read-back the model can check.
    ///   {"cmd":"freezer"}   a small sealed roofed room near the food store, a cooler in its wall with the blue (cold) side
    ///                       facing in; once the cooler is built and powered, its target goes to -5 C
    ///   {"cmd":"butcher"}   a butcher table blueprint in a roofed room near the food store, or the state of the one there is
    ///   {"cmd":"kitchen"}   every BUILT stove with no meal bill gets "simple meal until 30", every BUILT butcher table with no
    ///                       bill gets "butcher forever" -- the auto-attach the ladder fires when a kitchen table completes
    /// </summary>
    internal static class SetupTools7
    {
        private const float FreezerCelsius = -5f;
        private const int FreezerMaxCells = 60;
        private const int MealTarget = 30;

        private static bool Free(Map map, IntVec3 c) =>
            c.InBounds(map) && !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null;

        private static IntVec3 NearFoodStore(Map map)
        {
            Zone_Stockpile food = map.zoneManager.AllZones.OfType<Zone_Stockpile>().FirstOrDefault(z => z.label == "Food store");
            if (food != null && food.Cells.Count > 0) return food.Cells[0];
            Pawn anyone = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            return anyone != null ? anyone.Position : map.Center;
        }

        private static IEnumerable<Building> Built(Map map, string defName) =>
            map.listerBuildings.allBuildingsColonist.Where(b => b.def.defName == defName);

        private static Thing Planned(Map map, ThingDef def) =>
            map.listerThings.ThingsOfDef(def.blueprintDef).FirstOrDefault() ??
            map.listerThings.AllThings.FirstOrDefault(t => t.def.IsFrame && t.def.entityDefToBuild == def);

        // ---------------------------------------------------------------- freezer

        public static string Freezer(Map map)
        {
            ThingDef cooler = DefDatabase<ThingDef>.GetNamedSilentFail("Cooler");
            if (cooler == null) return "refused: no Cooler def";

            // A cooler already chilling a room is the freezer: report it, and set it cold once it has power.
            foreach (Building b in Built(map, "Cooler"))
            {
                Room cold = (b.Position + IntVec3.North.RotatedBy(b.Rotation)).GetRoom(map);
                if (cold == null || cold.PsychologicallyOutdoors || cold.UsesOutdoorTemperature) continue;
                CompTempControl temp = b.TryGetComp<CompTempControl>();
                CompPowerTrader power = b.TryGetComp<CompPowerTrader>();
                if (temp != null) temp.TargetTemperature = FreezerCelsius;
                bool powered = power == null || power.PowerOn;
                return "ok: freezer cooler BUILT at " + b.Position.x + "," + b.Position.z + ", target " + FreezerCelsius.ToString("0") +
                       " C, room now " + cold.Temperature.ToString("0") + " C" +
                       (powered ? "" : " -- NOT POWERED: run conduit from a generator or battery to it") +
                       " -- put the food store inside it (stockpile_room food)";
            }
            Thing plan = Planned(map, cooler);
            if (plan != null)
                return "ok: a freezer cooler is PLANNED (not built yet) at " + plan.Position.x + "," + plan.Position.z +
                       " -- keep time running; it needs power once built, then run freezer again to set it to -5 C";

            // The room: enclosed, roofed, not outdoors, no beds, small enough for one cooler, nearest the food store.
            IntVec3 near = NearFoodStore(map);
            var seen = new HashSet<Room>();
            var rooms = new List<Room>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, 30f, true))
            {
                if (!c.InBounds(map) || map.fogGrid.IsFogged(c)) continue;
                Room r = c.GetRoom(map);
                if (r == null || !seen.Add(r)) continue;
                if (r.PsychologicallyOutdoors || r.UsesOutdoorTemperature || r.OpenRoofCount > 0) continue;
                if (r.CellCount < 4 || r.CellCount > FreezerMaxCells) continue;
                if (r.ContainedBeds.Any()) continue;
                rooms.Add(r);
            }
            foreach (Room r in rooms)
            {
                // A wall a cooler may replace (isPlaceOverableWall) on the room's edge with room inside on one side and anything not in the room on the other,
                // so the hot side vents out. Rotation puts the cold (North-relative) face toward the room.
                foreach (IntVec3 inside in r.BorderCells)
                {
                    Building wall = inside.GetEdifice(map);
                    if (wall == null || wall.def.building == null || !wall.def.building.isPlaceOverableWall) continue;
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 coldCell = inside + d, hotCell = inside - d;
                        if (!coldCell.InBounds(map) || !hotCell.InBounds(map)) continue;
                        if (coldCell.GetRoom(map) != r || hotCell.GetRoom(map) == r) continue;
                        if (hotCell.Impassable(map)) continue;
                        Rot4 rot = Rot4.FromIntVec3(d);
                        if (!GenConstruct.CanPlaceBlueprintAt(cooler, inside, rot, map, false, null, null, null).Accepted) continue;
                        GenConstruct.PlaceBlueprintForBuild(cooler, inside, map, rot, Faction.OfPlayer, null);
                        return "ok: freezer cooler blueprint in the wall at " + inside.x + "," + inside.z + " (blue side into the " +
                               r.CellCount + "-cell room, hot side out) -- it needs power: conduit to a generator or battery; " +
                               "when built run freezer again to set -5 C, and stockpile_room food there";
                    }
                }
            }
            return rooms.Count == 0
                ? "refused: no small sealed roofed room without beds within 30 cells of the food store -- build_room one first (w 5 h 5)"
                : "refused: " + rooms.Count + " candidate room(s) but no wall cell with open air behind it for the hot side";
        }

        // ---------------------------------------------------------------- butcher table

        public static string Butcher(Map map)
        {
            ThingDef table = DefDatabase<ThingDef>.GetNamedSilentFail("TableButcher");
            if (table == null) return "refused: no TableButcher def";
            Building built = Built(map, "TableButcher").FirstOrDefault();
            if (built != null)
                return "ok: a butcher table is BUILT at " + built.Position.x + "," + built.Position.z +
                       " -- run kitchen to give it a butcher bill";
            Thing plan = Planned(map, table);
            if (plan != null)
                return "ok: a butcher table is PLANNED (not built yet) at " + plan.Position.x + "," + plan.Position.z +
                       " -- keep time running so it gets built, then run kitchen";
            ThingDef stuff = GenStuff.DefaultStuffFor(table);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(NearFoodStore(map), 25f, true))
            {
                if (!Free(map, c) || !c.Roofed(map) || map.zoneManager.ZoneAt(c) != null) continue;
                Room r = c.GetRoom(map);
                if (r == null || r.PsychologicallyOutdoors || r.ContainedBeds.Any()) continue;
                foreach (Rot4 rot in new[] { Rot4.South, Rot4.East, Rot4.North, Rot4.West })
                {
                    if (!GenConstruct.CanPlaceBlueprintAt(table, c, rot, map, false, null, null, stuff).Accepted) continue;
                    GenConstruct.PlaceBlueprintForBuild(table, c, map, rot, Faction.OfPlayer, stuff);
                    return "ok: butcher table blueprint at " + c.x + "," + c.z + " -- when built, run kitchen for its bill";
                }
            }
            return "refused: no roofed, explored free spot without beds near the food store";
        }

        // ---------------------------------------------------------------- kitchen bills

        public static string Kitchen(Map map)
        {
            RecipeDef meal = DefDatabase<RecipeDef>.GetNamedSilentFail("CookMealSimple");
            RecipeDef butcher = DefDatabase<RecipeDef>.GetNamedSilentFail("ButcherCorpseFlesh");
            var done = new List<string>();
            int stoves = 0, butchers = 0;
            foreach (Building_WorkTable t in map.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>())
            {
                // Any table that can cook a simple meal is a stove; a table that can butcher flesh is a butcher table.
                if (meal != null && t.def.AllRecipes.Contains(meal))
                {
                    stoves++;
                    if (t.BillStack.Bills.Any(b => b.recipe != null && b.recipe.ProducedThingDef != null &&
                                                   b.recipe.ProducedThingDef.IsNutritionGivingIngestible)) continue;
                    var bill = new Bill_Production(meal) { repeatMode = BillRepeatModeDefOf.TargetCount, targetCount = MealTarget };
                    bill.allowedSkillRange = new IntRange(0, 20);   // everyone can train (owner, 2026-10-10)
                    t.BillStack.AddBill(bill);
                    done.Add(t.LabelShort + " at " + t.Position.x + "," + t.Position.z + ": simple meal until " + MealTarget);
                }
                else if (butcher != null && t.def.AllRecipes.Contains(butcher))
                {
                    butchers++;
                    if (t.BillStack.Bills.Any(b => b.recipe == butcher)) continue;
                    var bill = new Bill_Production(butcher) { repeatMode = BillRepeatModeDefOf.Forever };
                    bill.allowedSkillRange = new IntRange(0, 20);
                    t.BillStack.AddBill(bill);
                    done.Add(t.LabelShort + " at " + t.Position.x + "," + t.Position.z + ": butcher forever");
                }
            }
            if (stoves == 0 && butchers == 0)
                return "refused: no BUILT stove or butcher table (run stove / butcher; blueprints and frames cannot take bills)";
            return done.Count == 0
                ? "ok: every built stove (" + stoves + ") and butcher table (" + butchers + ") already has its bill"
                : "ok: " + string.Join("; ", done);
        }
    }
}
