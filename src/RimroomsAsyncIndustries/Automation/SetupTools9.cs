using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Batch 4 (building) of the owner's playbook: "power conduit as one string".
    ///   {"cmd":"power"}            every building that needs power and is on no grid gets one conduit line, the shortest
    ///                              buildable path to the nearest grid that holds a generator or a battery
    ///   {"cmd":"power","x":"..","z":".."}   just the building at that cell
    ///   {"cmd":"hall","x1":"..","z1":"..","x2":"..","z2":"..","width":"3"}   a straight walled, roofed hall
    /// Existing conduits and powered buildings on the path are reused, so a second call adds nothing.
    /// </summary>
    internal static class SetupTools9
    {
        private const int SearchLimit = 6000;   // cells a single path search may visit

        private static bool LiveNet(PowerNet net) =>
            net != null && (net.batteryComps.Count > 0 || net.powerComps.Any(c => c.PowerOutput > 0f));

        private static bool OnLiveGrid(Map map, IntVec3 c)
        {
            foreach (Thing t in c.GetThingList(map))
            {
                // Only something that passes power on (conduit, battery, generator) joins a line laid beside it; an
                // ordinary consumer takes power from a conduit but carries none onward.
                CompPower p = t.TryGetComp<CompPower>();
                if (p != null && p.Props.transmitsPower && LiveNet(p.PowerNet)) return true;
            }
            return false;
        }

        private static bool CarriesPower(Map map, IntVec3 c) =>
            c.GetThingList(map).Any(t => t.TryGetComp<CompPower>()?.Props.transmitsPower == true ||
                                         (t.def.IsBlueprint || t.def.IsFrame) && t.def.entityDefToBuild == ThingDefOf.PowerConduit);

        public static string Power(Map map, Dictionary<string, string> a)
        {
            ThingDef conduit = ThingDefOf.PowerConduit;
            if (!map.listerBuildings.allBuildingsColonist.Any(b => LiveNet(b.TryGetComp<CompPower>()?.PowerNet)))
                return "refused: no grid with a generator or battery yet -- build one first";

            IEnumerable<Building> targets = map.listerBuildings.allBuildingsColonist
                .Where(b => b.TryGetComp<CompPowerTrader>() != null && b.TryGetComp<CompPowerTrader>().PowerNet == null);
            if (a.TryGetValue("x", out string xs) && a.TryGetValue("z", out string zs) &&
                int.TryParse(xs, out int x) && int.TryParse(zs, out int z))
            {
                IntVec3 at = new IntVec3(x, 0, z);
                targets = targets.Where(b => b.OccupiedRect().Contains(at));
            }
            List<Building> unpowered = targets.ToList();
            if (unpowered.Count == 0) return "ok: every building that needs power is already on a grid";

            var report = new List<string>();
            int laid = 0;
            foreach (Building b in unpowered)
            {
                List<IntVec3> path = PathToGrid(map, b, conduit);
                if (path == null) { report.Add(b.LabelShort + " at " + b.Position.x + "," + b.Position.z + ": no buildable path"); continue; }
                int here = 0;
                foreach (IntVec3 c in path)
                {
                    if (CarriesPower(map, c)) continue;
                    GenConstruct.PlaceBlueprintForBuild(conduit, c, map, Rot4.North, Faction.OfPlayer, null);
                    here++;
                }
                laid += here;
                report.Add(b.LabelShort + " at " + b.Position.x + "," + b.Position.z + ": " + here + " conduit");
            }
            return (laid == 0 ? "refused: " : "ok: ") + string.Join("; ", report);
        }

        /// <summary>
        /// PLAYBOOK "3-wide halls": a straight hall between two cells, walls down both sides and roof marked over it; the
        /// ends stay open into whatever they meet (a door is a separate build). One straight run per call:
        ///   {"cmd":"hall","x1":"..","z1":"..","x2":"..","z2":"..","width":"3","stuff":"BlocksGranite"}
        /// x1,z1 -> x2,z2 must share an x or a z (the hall's centre line).
        /// </summary>
        public static string Hall(Map map, Dictionary<string, string> a)
        {
            int Int(string k, int d) => a.TryGetValue(k, out string s) && int.TryParse(s, out int v) ? v : d;
            IntVec3 p1 = new IntVec3(Int("x1", -1), 0, Int("z1", -1)), p2 = new IntVec3(Int("x2", -1), 0, Int("z2", -1));
            if (!p1.InBounds(map) || !p2.InBounds(map)) return "refused: x1,z1 and x2,z2 must be on the map";
            if (p1.x != p2.x && p1.z != p2.z) return "refused: a hall runs straight -- x1,z1 and x2,z2 must share an x or a z";
            int width = System.Math.Max(1, System.Math.Min(5, Int("width", 3)));
            a.TryGetValue("stuff", out string sn);
            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(sn ?? "") ?? ThingDefOf.WoodLog;

            bool alongX = p1.z == p2.z;                          // the hall runs east-west
            int lo = alongX ? System.Math.Min(p1.x, p2.x) : System.Math.Min(p1.z, p2.z);
            int hi = alongX ? System.Math.Max(p1.x, p2.x) : System.Math.Max(p1.z, p2.z);
            int centre = alongX ? p1.z : p1.x;
            int half = width / 2, sideA = centre - half - 1, sideB = centre - half + width;   // wall lines either side

            int walls = 0, kept = 0, blocked = 0, roofed = 0;
            void Wall(IntVec3 c)
            {
                if (!c.InBounds(map)) { blocked++; return; }
                Building ed = c.GetEdifice(map);
                if (ed != null && (ed.def.passability == Traversability.Impassable || ed is Building_Door)) { kept++; return; }
                if (!GenConstruct.CanPlaceBlueprintAt(ThingDefOf.Wall, c, Rot4.North, map, false, null, null, stuff).Accepted) { blocked++; return; }
                GenConstruct.PlaceBlueprintForBuild(ThingDefOf.Wall, c, map, Rot4.North, Faction.OfPlayer, stuff);
                walls++;
            }
            for (int i = lo; i <= hi; i++)
            {
                Wall(alongX ? new IntVec3(i, 0, sideA) : new IntVec3(sideA, 0, i));
                Wall(alongX ? new IntVec3(i, 0, sideB) : new IntVec3(sideB, 0, i));
                for (int w = sideA + 1; w < sideB; w++)
                {
                    IntVec3 c = alongX ? new IntVec3(i, 0, w) : new IntVec3(w, 0, i);
                    if (c.InBounds(map) && !map.areaManager.BuildRoof[c]) { map.areaManager.BuildRoof[c] = true; roofed++; }
                }
            }
            return (walls == 0 && kept == 0 ? "refused: " : "ok: ") + width + "-wide hall " + (alongX ? "east-west" : "north-south") +
                   " from " + lo + " to " + hi + " on " + (alongX ? "z " : "x ") + centre + ": " + walls + " wall blueprints, " + kept +
                   " existing kept, " + blocked + " blocked, " + roofed + " cells roofed -- the ends stay open into what they meet; " +
                   "build a door there with build def Door if a room needs closing";
        }

        /// <summary>
        /// Breadth-first from the building's own cells to the first cell on a live grid. A step is allowed onto a cell
        /// that already carries power or where a conduit blueprint is accepted, so the line goes under walls where Core
        /// allows it and around everything else. Returns the cells between, excluding the building and the grid cell.
        /// </summary>
        private static List<IntVec3> PathToGrid(Map map, Building from, ThingDef conduit)
        {
            var parent = new Dictionary<IntVec3, IntVec3>();
            var queue = new Queue<IntVec3>();
            foreach (IntVec3 c in from.OccupiedRect()) { parent[c] = IntVec3.Invalid; queue.Enqueue(c); }
            int visited = 0;
            while (queue.Count > 0 && visited++ < SearchLimit)
            {
                IntVec3 cur = queue.Dequeue();
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 n = cur + d;
                    if (!n.InBounds(map) || parent.ContainsKey(n) || map.fogGrid.IsFogged(n)) continue;
                    if (OnLiveGrid(map, n))
                    {
                        var path = new List<IntVec3>();
                        for (IntVec3 s = cur; s.IsValid && !from.OccupiedRect().Contains(s); s = parent[s]) path.Add(s);
                        path.Reverse();
                        return path;
                    }
                    bool ok = CarriesPower(map, n) ||
                              GenConstruct.CanPlaceBlueprintAt(conduit, n, Rot4.North, map, false, null, null, null).Accepted;
                    if (!ok) continue;
                    parent[n] = cur;
                    queue.Enqueue(n);
                }
            }
            return null;
        }
    }
}
