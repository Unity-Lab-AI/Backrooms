using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Storage and food tools, batch 2 of the owner's playbook as code (owner: "that doesnt scratch the surface of
    /// all ive told you how to play").
    ///   {"cmd":"shelves"}           shelf blueprints along the walls of every stockpile (3 stacks a cell)
    ///   {"cmd":"stove"}             a fueled stove blueprint in a roofed explored room, next to the food store
    ///   {"cmd":"crops","plant":"Plant_Rice"}  a growing zone on the most fertile free soil near home, sowing that crop
    ///   {"cmd":"hunt"}              hunt designations on safe game only: never boomalopes, no big game under 3 rifles
    /// </summary>
    internal static class SetupTools2
    {
        private static bool Free(Map map, IntVec3 c) =>
            c.InBounds(map) && !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null;

        private static bool TryPlace(Map map, ThingDef def, IntVec3 c, Rot4 rot, ThingDef stuff)
        {
            if (!GenConstruct.CanPlaceBlueprintAt(def, c, rot, map, false, null, null, stuff).Accepted) return false;
            GenConstruct.PlaceBlueprintForBuild(def, c, map, rot, Faction.OfPlayer, stuff);
            return true;
        }

        public static string Shelves(Map map)
        {
            ThingDef shelf = DefDatabase<ThingDef>.GetNamedSilentFail("Shelf");
            if (shelf == null) return "refused: no Shelf def";
            ThingDef stuff = GenStuff.DefaultStuffFor(shelf);
            int placed = 0;
            foreach (Zone_Stockpile z in map.zoneManager.AllZones.OfType<Zone_Stockpile>())
            {
                foreach (IntVec3 c in z.Cells.ToList())
                {
                    if (placed >= 12) break;
                    // against a wall: a cardinal neighbour is impassable, so lanes stay clear
                    bool wall = GenAdj.CardinalDirections.Any(d => { IntVec3 n = c + d; return n.InBounds(map) && n.Impassable(map); });
                    if (!wall || !Free(map, c)) continue;
                    Rot4 rot = Rot4.South;
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 n = c + d;
                        if (n.InBounds(map) && n.Impassable(map)) { rot = Rot4.FromIntVec3(-d); break; }
                    }
                    if (TryPlace(map, shelf, c, rot, stuff)) placed++;
                }
            }
            return placed == 0 ? "refused: no stockpile with free wall cells (make a stockpile first)"
                               : "ok: " + placed + " shelf blueprints along the stockpile walls";
        }

        public static string Stove(Map map)
        {
            ThingDef stove = DefDatabase<ThingDef>.GetNamedSilentFail("FueledStove");
            if (stove == null) return "refused: no FueledStove def";
            Building built = map.listerBuildings.allBuildingsColonist.FirstOrDefault(b => b.def == stove);
            if (built != null)
                return "ok: a fueled stove is BUILT at " + built.Position.x + "," + built.Position.z +
                       " -- add_bill recipe CookMealSimple (the cell is optional, the bill finds the stove)";
            Thing plan = map.listerThings.ThingsOfDef(stove.blueprintDef).FirstOrDefault() ??
                         map.listerThings.AllThings.FirstOrDefault(t => t.def.IsFrame && t.def.entityDefToBuild == stove);
            if (plan != null)
                return "ok: a fueled stove is PLANNED (not built yet) at " + plan.Position.x + "," + plan.Position.z +
                       " -- keep time running so it gets built, then add_bill CookMealSimple";
            Zone_Stockpile food = map.zoneManager.AllZones.OfType<Zone_Stockpile>().FirstOrDefault(z => z.label == "Food store");
            IntVec3 near = food?.Cells.FirstOrDefault() ?? map.mapPawns.FreeColonistsSpawned.First().Position;
            ThingDef stuff = GenStuff.DefaultStuffFor(stove);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, 25f, true))
            {
                if (!Free(map, c) || c.Roofed(map) == false || map.zoneManager.ZoneAt(c) != null) continue;
                Room r = c.GetRoom(map);
                if (r == null || r.PsychologicallyOutdoors) continue;
                if (TryPlace(map, stove, c, Rot4.South, stuff))
                    return "ok: fueled stove blueprint at " + c.x + "," + c.z + " -- when built, add_bill x " + c.x + " z " + c.z + " recipe CookMealSimple count 30";
            }
            return "refused: no roofed, explored free spot near the food store";
        }

        public static string Crops(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("plant", out string plantName);
            ThingDef plant = DefDatabase<ThingDef>.GetNamedSilentFail(string.IsNullOrEmpty(plantName) ? "Plant_Rice" : plantName);
            if (plant?.plant == null || !plant.plant.Sowable) return "refused: no sowable plant " + plantName;
            IntVec3 home = map.mapPawns.FreeColonistsSpawned.First().Position;
            List<IntVec3> soil = GenRadial.RadialCellsAround(home, 45f, true)
                .Where(c => Free(map, c) && !c.Roofed(map) && map.zoneManager.ZoneAt(c) == null &&
                            c.GetFertility(map) >= 1f && plant.CanEverPlantAt(c, map))
                .Take(400).ToList();
            if (soil.Count < 9) return "refused: no fertile open soil within 45 cells of the crew -- explore outside first";
            // one compact block: the 9x9 around the first good cell, soil cells only
            IntVec3 seed = soil[0];
            List<IntVec3> block = soil.Where(c => Math.Abs(c.x - seed.x) <= 4 && Math.Abs(c.z - seed.z) <= 4).ToList();
            var zone = new Zone_Growing(map.zoneManager);
            map.zoneManager.RegisterZone(zone);
            foreach (IntVec3 c in block) zone.AddCell(c);
            zone.SetPlantDefToGrow(plant);
            return "ok: growing zone of " + block.Count + " cells at " + seed.x + "," + seed.z + " sowing " + plant.label;
        }

        public static string Hunt(Map map)
        {
            int rifles = map.mapPawns.FreeColonistsSpawned.Count(p => p.equipment?.Primary != null && p.equipment.Primary.def.IsRangedWeapon);
            int marked = 0;
            foreach (Pawn animal in map.mapPawns.AllPawnsSpawned.Where(p => p.RaceProps.Animal && p.Faction == null && !p.Downed))
            {
                string d = animal.def.defName.ToLowerInvariant();
                if (d.Contains("boomalope") || d.Contains("boomrat")) continue;                 // they explode
                if (animal.RaceProps.predator && rifles < 3) continue;                          // owner: no big game under 3 rifles
                if (animal.BodySize > 1.5f && rifles < 3) continue;
                if (map.designationManager.DesignationOn(animal, DesignationDefOf.Hunt) != null) continue;
                map.designationManager.AddDesignation(new Designation(animal, DesignationDefOf.Hunt));
                if (++marked >= 6) break;
            }
            return marked == 0 ? "ok: nothing safe to hunt right now (" + rifles + " armed)"
                               : "ok: " + marked + " safe animals marked to hunt (" + rifles + " armed; someone needs Hunting work on)";
        }
    }
}
