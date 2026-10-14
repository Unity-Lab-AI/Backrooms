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
            if (placed > 0) return "ok: " + placed + " shelf blueprints along the stockpile walls";
            bool anyStore = map.zoneManager.AllZones.OfType<Zone_Stockpile>().Any();
            return anyStore
                ? "refused: the stockpile has no wall beside it -- shelves stand against walls; storage_room walls and roofs the main store first, then shelves"
                : "refused: no stockpile yet -- stockpile_camp (nofood) first, then storage_room, then shelves";
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
            IntVec3 anchor = CampAnchor.Get(map);
            IntVec3 near = food?.Cells.FirstOrDefault() ?? (anchor.IsValid ? anchor : map.mapPawns.FreeColonistsSpawned.First().Position);
            ThingDef stuff = GenStuff.DefaultStuffFor(stove);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, 25f, true))
            {
                if (!Free(map, c) || c.Roofed(map) == false || map.zoneManager.ZoneAt(c) != null) continue;
                Room r = c.GetRoom(map);
                if (r == null || r.PsychologicallyOutdoors) continue;
                // against a wall, not in the doorway (owner: furniture along the walls, paths kept clear)
                bool onWall = GenAdj.CardinalDirections.Any(d => { IntVec3 n = c + d; return n.InBounds(map) && n.Impassable(map); });
                bool nearDoor = GenAdj.AdjacentCells.Any(d => { IntVec3 n = c + d; return n.InBounds(map) && n.GetEdifice(map) is Building_Door; });
                if (!onWall || nearDoor) continue;
                if (TryPlace(map, stove, c, Rot4.South, stuff))
                    return "ok: fueled stove blueprint at " + c.x + "," + c.z + " -- when built, kitchen (or add_bill recipe CookMealSimple count 30)";
            }
            // No roofed room by the store. A crash camp has none until one is built: plan the kitchen room beside the
            // store at the camp anchor instead of refusing (test run 2026-10-13: four stove refusals, no kitchen ever).
            Thing pending = map.listerThings.AllThings.FirstOrDefault(t => t.Faction == Faction.OfPlayer && (t.def.IsBlueprint || t.def.IsFrame) &&
                                                                          t.def.entityDefToBuild == ThingDefOf.Wall);
            if (pending != null)
                return "refused for now: no finished roofed room by the store -- walls are still planned or being built near " + pending.Position.x + "," +
                       pending.Position.z + "; the stove goes in once a room stands (keep Construction on). Do not call stove again until then";
            var args = new Dictionary<string, string> { { "w", "5" }, { "h", "4" } };
            string room = SetupTools3.Shelter(map, args);
            return room.StartsWith("ok")
                ? "refused for now: no roofed room, so a 5x4 kitchen room was planned at the camp -- " + room.Substring(4) + "; stove once it stands"
                : "refused: no roofed room by the store and no kitchen room could be planned (" + room + ")";
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
