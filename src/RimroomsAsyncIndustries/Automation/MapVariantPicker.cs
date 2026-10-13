using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Picks which map of the chosen tile the colony lands on -- the Map Preview dice, done by the driver.
    ///
    /// Owner, verbatim: *"after it finds mountionous and forest ther is a dice button on the minimap headar bar
    /// clicking it shows the possible map generations of that tile you can select and it should select a N/S orintated
    /// mountain and the tan area of each map is the dirt and the braown area is the mountains and u check the one u one
    /// and chcik it accepted"* / *"Unity is gonna want one with a nock into the moutain of dirt land where mountian is
    /// on 3 sides dug into the main maountian"*.
    ///
    /// The dice window renders seeds original, original+1, ... with Map Preview's own generator and, on apply, commits
    /// the chosen seed to Map Preview's SeedRerollData; the real map is then generated from that seed. This does the
    /// same: it renders <see cref="Candidates"/> seeds through Map Preview's generator, reads each preview's rock cells
    /// (Map Preview paints mountain in four fixed browns), scores them, commits the best seed and reads it back.
    ///
    /// Score: a mountain that runs north-south (many columns mostly rock, others open; rock present top to bottom),
    /// plus a nook -- open ground with rock on at least three sides, opening off the main mountain. A map with neither
    /// can still win when nothing better rendered; the result file says so. Map Preview is optional: without it the
    /// tile is used as it comes, and the result file says that too. Everything is by reflection; no hard dependency.
    /// </summary>
    internal static class MapVariantPicker
    {
        private const int Candidates = 30;
        private const float TimeoutSeconds = 240f;
        private const int Cell = 3;          // the 300x300 preview is scored on a 100x100 grid of 3x3 blocks
        private const int NookReach = 25;    // a wall counts when rock is within 25 blocks (75 cells) that way

        private static readonly Color[] Rock =
        {
            new Color32(0x36, 0x27, 0x1C, 0xFF), new Color32(0x4C, 0x34, 0x26, 0xFF),
            new Color32(0x1C, 0x13, 0x0E, 0xFF), new Color32(0x42, 0x37, 0x2B, 0xFF),
        };

        private enum Phase { Idle, Rendering, Done }

        private static Phase phase = Phase.Idle;
        private static PlanetTile tile = PlanetTile.Invalid;
        private static int originalSeed;
        private static float startedAt;
        private static Delegate handler;
        private static EventInfo finishedEvent;
        private static readonly ConcurrentDictionary<int, Score> scores = new ConcurrentDictionary<int, Score>();

        public static PlanetTile ChosenTile => phase == Phase.Done ? tile : PlanetTile.Invalid;

        public static void Reset()
        {
            Unsubscribe();
            phase = Phase.Idle;
            tile = PlanetTile.Invalid;
            scores.Clear();
        }

        private struct Score
        {
            public float RockFraction, RowSpan, NorthSouth, NookBlocks, Total;
            public override string ToString() => string.Format("rock {0:P0}, top-to-bottom {1:P0}, N/S {2:F2}, nook {3} blocks, score {4:F2}",
                                                               RockFraction, RowSpan, NorthSouth, (int)NookBlocks, Total);
        }

        /// <summary>True once a tile and its map are settled; false while the previews are still rendering.</summary>
        public static bool Ready(Page_SelectStartingSite page)
        {
            try
            {
                switch (phase)
                {
                    case Phase.Done: return true;
                    case Phase.Idle: return Begin();
                    default: return Poll();
                }
            }
            catch (Exception e)
            {
                WorldSetupDriver.Note("map variant: failed (" + e.GetType().Name + ": " + e.Message + ") -- the tile's own map is used");
                Unsubscribe();
                phase = Phase.Done;
                return true;
            }
        }

        private static Type MapPreviewType(string name) =>
            AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType("MapPreview." + name, false)).FirstOrDefault(t => t != null);

        private static bool Begin()
        {
            tile = WorldSetupDriver.ChooseTile();
            if (!tile.Valid) { phase = Phase.Done; return true; }
            Find.WorldInterface.SelectedTile = tile;

            Type generator = MapPreviewType("MapPreviewGenerator");
            Type request = MapPreviewType("MapPreviewRequest");
            Type result = MapPreviewType("MapPreviewResult");
            Type reroll = MapPreviewType("SeedRerollData");
            if (generator == null || request == null || result == null || reroll == null)
            {
                WorldSetupDriver.Note("map variant: Map Preview is not loaded -- the tile's own map is used");
                phase = Phase.Done;
                return true;
            }

            originalSeed = Gen.HashCombineInt(Find.World.info.Seed, tile.GetHashCode());
            scores.Clear();

            // Map Preview raises OnFinishedGenerating(MapPreviewResult) on its worker thread for every finished preview
            finishedEvent = generator.GetEvent("OnFinishedGenerating", BindingFlags.Public | BindingFlags.Static);
            ParameterExpression arg = Expression.Parameter(result, "result");
            handler = Expression.Lambda(finishedEvent.EventHandlerType,
                Expression.Call(typeof(MapVariantPicker).GetMethod(nameof(OnPreview), BindingFlags.NonPublic | BindingFlags.Static),
                                Expression.Convert(arg, typeof(object))), arg).Compile();
            finishedEvent.AddEventHandler(null, handler);

            object gen = generator.GetMethod("Init", BindingFlags.Public | BindingFlags.Static).Invoke(null, null);
            generator.GetMethod("ClearQueue")?.Invoke(gen, null);
            MethodInfo queue = generator.GetMethod("QueuePreviewRequest");
            ConstructorInfo make = request.GetConstructor(new[] { typeof(int), typeof(PlanetTile), typeof(IntVec2) });
            // the size the colony is made at (Site sets the same 300x300); the preview must match the real map
            Find.GameInitData.mapSize = 300;
            var size = new IntVec2(300, 300);
            for (int i = 0; i < Candidates; i++)
            {
                int seed = unchecked(originalSeed + i);
                object req = make.Invoke(new object[] { seed, tile, size });
                request.GetProperty("GeneratorDef")?.SetValue(req, MapGeneratorDefOf.Base_Player);
                request.GetProperty("UseTrueTerrainColors")?.SetValue(req, false);
                request.GetProperty("UseMinimalMapComponents")?.SetValue(req, true);
                queue.Invoke(gen, new[] { req });
            }
            startedAt = Time.realtimeSinceStartup;
            phase = Phase.Rendering;
            WorldSetupDriver.Note(string.Format("map variant: tile {0} -- rendering {1} maps to find a north-south mountain with a nook",
                                                tile.tileId, Candidates));
            return false;
        }

        private static bool Poll()
        {
            bool timedOut = Time.realtimeSinceStartup - startedAt > TimeoutSeconds;
            if (scores.Count < Candidates && !timedOut) { return false; }
            Unsubscribe();
            phase = Phase.Done;
            if (scores.Count == 0)
            {
                WorldSetupDriver.Note("map variant: no preview finished in time -- the tile's own map is used");
                return true;
            }

            bool Passes(Score s) => s.RockFraction >= 0.15f && s.RockFraction <= 0.6f && s.RowSpan >= 0.8f && s.NookBlocks >= 40f;
            var passing = scores.Where(kv => Passes(kv.Value)).ToList();
            var pool = passing.Count > 0 ? passing : scores.ToList();
            var best = pool.OrderByDescending(kv => kv.Value.Total).First();

            object data = MapPreviewType("SeedRerollData").GetMethod("GetFor", BindingFlags.Public | BindingFlags.Static).Invoke(null, new object[] { Find.World });
            Type rerollType = data.GetType();
            if (best.Key == originalSeed) { rerollType.GetMethod("Reset", new[] { typeof(int) }).Invoke(data, new object[] { tile.tileId }); }
            else { rerollType.GetMethod("Commit", new[] { typeof(int), typeof(int) }).Invoke(data, new object[] { tile.tileId, best.Key }); }

            // read it back the way map generation will: the committed seed, or the original when none is stored
            object[] tryArgs = { tile.tileId, 0 };
            bool stored = (bool)rerollType.GetMethod("TryGet").Invoke(data, tryArgs);
            int effective = stored ? (int)tryArgs[1] : originalSeed;
            bool accepted = effective == best.Key;

            WorldSetupDriver.Note(string.Format("map variant: {0} of {1} rendered, {2} passed; chose {3} ({4}) -- {5}",
                scores.Count, Candidates, passing.Count, best.Key == originalSeed ? "the original" : "#" + unchecked(best.Key - originalSeed),
                best.Value, accepted ? "accepted" : "NOT accepted (seed read back " + effective + ")"));
            if (passing.Count == 0) { WorldSetupDriver.Note("map variant: none had both a north-south mountain and a nook -- took the best of them"); }
            return true;
        }

        private static void Unsubscribe()
        {
            if (finishedEvent != null && handler != null)
            {
                try { finishedEvent.RemoveEventHandler(null, handler); } catch { }
            }
            finishedEvent = null;
            handler = null;
        }

        /// <summary>Map Preview's worker thread: score one finished preview. Pure arithmetic on its pixel buffer.</summary>
        private static void OnPreview(object result)
        {
            try
            {
                Type t = result.GetType();
                object req = t.GetField("Request").GetValue(result);
                int seed = (int)req.GetType().GetProperty("Seed").GetValue(req);
                if (phase != Phase.Rendering) { return; }
                var mapTile = (PlanetTile)req.GetType().GetProperty("MapTile").GetValue(req);
                if (mapTile.tileId != tile.tileId) { return; }
                var pixels = (Color[])t.GetField("Pixels").GetValue(result);
                var tex = (IntVec2)t.GetProperty("TextureSize").GetValue(result);
                var map = (IntVec2)t.GetProperty("MapSize").GetValue(result);
                scores[seed] = Measure(pixels, tex.x, map.x, map.z);
            }
            catch { }
        }

        private static bool IsRock(Color c)
        {
            foreach (Color r in Rock)
            {
                if (Mathf.Abs(c.r - r.r) < 0.01f && Mathf.Abs(c.g - r.g) < 0.01f && Mathf.Abs(c.b - r.b) < 0.01f) { return true; }
            }
            return false;
        }

        private static Score Measure(Color[] pixels, int stride, int width, int height)
        {
            int w = width / Cell, h = height / Cell;
            var rock = new bool[w, h];
            int rockBlocks = 0;
            for (int bx = 0; bx < w; bx++)
            {
                for (int bz = 0; bz < h; bz++)
                {
                    int n = 0;
                    for (int dx = 0; dx < Cell; dx++)
                        for (int dz = 0; dz < Cell; dz++)
                            if (IsRock(pixels[(bz * Cell + dz) * stride + bx * Cell + dx])) n++;
                    if (n * 2 > Cell * Cell) { rock[bx, bz] = true; rockBlocks++; }
                }
            }

            // north-south: columns split into mostly-rock and mostly-open, rows do not; rock reaches top to bottom
            var col = new float[w];
            var row = new float[h];
            int rowsWithRock = 0;
            for (int bx = 0; bx < w; bx++) for (int bz = 0; bz < h; bz++) if (rock[bx, bz]) { col[bx]++; row[bz]++; }
            for (int bx = 0; bx < w; bx++) col[bx] /= h;
            for (int bz = 0; bz < h; bz++) { row[bz] /= w; if (row[bz] >= 0.1f) rowsWithRock++; }
            float Band(float[] v)
            {
                var s = v.OrderByDescending(x => x).ToArray();
                int top = Math.Max(1, s.Length / 5), low = Math.Max(1, s.Length / 2);
                return s.Take(top).Average() - s.Skip(s.Length - low).Average();
            }
            float northSouth = Band(col) - Band(row);

            // nook: open blocks with rock within reach on at least three of the four sides; the largest such patch
            var nook = new bool[w, h];
            for (int bx = 0; bx < w; bx++)
            {
                for (int bz = 0; bz < h; bz++)
                {
                    if (rock[bx, bz]) { continue; }
                    int walls = 0;
                    if (Hit(rock, w, h, bx, bz, 1, 0)) walls++;
                    if (Hit(rock, w, h, bx, bz, -1, 0)) walls++;
                    if (Hit(rock, w, h, bx, bz, 0, 1)) walls++;
                    if (Hit(rock, w, h, bx, bz, 0, -1)) walls++;
                    nook[bx, bz] = walls >= 3;
                }
            }
            int biggest = 0;
            var seen = new bool[w, h];
            var stack = new System.Collections.Generic.Stack<int>();
            for (int bx = 0; bx < w; bx++)
            {
                for (int bz = 0; bz < h; bz++)
                {
                    if (!nook[bx, bz] || seen[bx, bz]) { continue; }
                    int size = 0;
                    stack.Push(bx * h + bz); seen[bx, bz] = true;
                    while (stack.Count > 0)
                    {
                        int v = stack.Pop(), x = v / h, z = v % h; size++;
                        foreach (var (nx, nz) in new[] { (x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1) })
                        {
                            if (nx < 0 || nz < 0 || nx >= w || nz >= h || seen[nx, nz] || !nook[nx, nz]) { continue; }
                            seen[nx, nz] = true; stack.Push(nx * h + nz);
                        }
                    }
                    biggest = Math.Max(biggest, size);
                }
            }

            var score = new Score
            {
                RockFraction = rockBlocks / (float)(w * h),
                RowSpan = rowsWithRock / (float)h,
                NorthSouth = northSouth,
                NookBlocks = biggest,
            };
            // a nook of ~200 blocks (about 40x40 cells) is plenty; bigger stops counting
            score.Total = score.NorthSouth + 0.6f * Mathf.Min(biggest / 200f, 1f) + 0.3f * score.RowSpan;
            return score;
        }

        private static bool Hit(bool[,] rock, int w, int h, int x, int z, int dx, int dz)
        {
            for (int step = 1; step <= NookReach; step++)
            {
                int nx = x + dx * step, nz = z + dz * step;
                if (nx < 0 || nz < 0 || nx >= w || nz >= h) { return false; }
                if (rock[nx, nz]) { return true; }
            }
            return false;
        }
    }
}
