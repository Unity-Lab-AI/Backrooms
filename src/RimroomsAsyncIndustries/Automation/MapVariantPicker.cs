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
    /// Score (owner: "a true N/S facing must have its main mass touch both east and west sides of the tiles map to be
    /// N/S u can tell wehr like 30% of the map or more is all brown touching both sides"): the biggest connected rock
    /// mass must reach both the west and the east edge and cover 30%+ of the map, with a nook -- a pocket of open ground
    /// with that main mountain on at least three sides. When no map qualifies the closest one is taken and the result
    /// file says so. Map Preview is optional: without it the
    /// tile is used as it comes, and the result file says that too. Everything is by reflection; no hard dependency.
    /// </summary>
    internal static class MapVariantPicker
    {
        private const int Candidates = 60;
        private const float TimeoutSeconds = 120f;  // per batch
        // Map Preview's own preview window on the tile page can clear the shared render queue when the selected tile
        // changes (live 2026-10-13: 60 queued, none finished). No progress for this long re-queues what is missing.
        private const float StallSeconds = 15f;
        private const int MaxRequeues = 3;
        // owner: "and it can hit the recycle looking button to regenerate" -- the dice window's refresh shows the next
        // seeds; when no map in a batch qualifies, the next batch is rendered, up to this many
        private const int MaxBatches = 5;
        private const int Cell = 3;          // the 300x300 preview is scored on a 100x100 grid of 3x3 blocks
        private const int NookReach = 25;    // a wall counts when the main mountain is within 25 blocks (75 cells) that way
        private const int MinNook = 30;      // a pocket of at least ~30 blocks (about 270 cells) ...
        private const int MaxNook = 900;     // ... and at most ~900 (a pocket, not the open plain)

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
        private static int batch;
        private static int lastCount;
        private static float lastProgress;
        private static int requeues;
        private static object generatorInstance;
        private static MethodInfo queueMethod;
        private static ConstructorInfo makeRequest;
        private static Type requestType;
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
            public float RockFraction, MainMass, NookBlocks, Total;
            public bool EastToWest;
            public override string ToString() => string.Format("main mountain {0:P0} of the map{1}, all rock {2:P0}, nook {3} blocks, score {4:F2}",
                                                               MainMass, EastToWest ? " touching east and west" : " NOT edge to edge",
                                                               RockFraction, (int)NookBlocks, Total);
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

            generatorInstance = generator.GetMethod("Init", BindingFlags.Public | BindingFlags.Static).Invoke(null, null);
            generator.GetMethod("ClearQueue")?.Invoke(generatorInstance, null);
            queueMethod = generator.GetMethod("QueuePreviewRequest");
            requestType = request;
            makeRequest = request.GetConstructor(new[] { typeof(int), typeof(PlanetTile), typeof(IntVec2) });
            // the size the colony is made at (Site sets the same 300x300); the preview must match the real map
            Find.GameInitData.mapSize = 300;
            batch = 0;
            requeues = 0;
            QueueBatch();
            phase = Phase.Rendering;
            WorldSetupDriver.Note(string.Format("map variant: tile {0} -- rendering {1} maps to find a north/south-facing mountain (east to west, 30%+) with a nook",
                                                tile.tileId, Candidates));
            return false;
        }

        /// <summary>Seeds original + batch*Candidates ... + Candidates-1, as the dice window's refresh walks them.</summary>
        private static void QueueBatch()
        {
            var size = new IntVec2(300, 300);
            lastCount = scores.Count;
            lastProgress = Time.realtimeSinceStartup;
            for (int i = 0; i < Candidates; i++)
            {
                int seed = unchecked(originalSeed + batch * Candidates + i);
                if (scores.ContainsKey(seed)) { continue; }
                object req = makeRequest.Invoke(new object[] { seed, tile, size });
                requestType.GetProperty("GeneratorDef")?.SetValue(req, MapGeneratorDefOf.Base_Player);
                requestType.GetProperty("UseTrueTerrainColors")?.SetValue(req, false);
                requestType.GetProperty("UseMinimalMapComponents")?.SetValue(req, true);
                queueMethod.Invoke(generatorInstance, new[] { req });
            }
            startedAt = Time.realtimeSinceStartup;
        }

        private static bool Qualifies(Score s) => s.EastToWest && s.MainMass >= 0.30f && s.NookBlocks >= MinNook;

        private static bool Poll()
        {
            bool timedOut = Time.realtimeSinceStartup - startedAt > TimeoutSeconds;
            if (scores.Count != lastCount) { lastCount = scores.Count; lastProgress = Time.realtimeSinceStartup; }
            bool batchDone = scores.Count >= (batch + 1) * Candidates;
            if (!batchDone && !timedOut && Time.realtimeSinceStartup - lastProgress > StallSeconds)
            {
                if (requeues < MaxRequeues)
                {
                    requeues++;
                    WorldSetupDriver.Note(string.Format("map variant: rendering stalled at {0} -- queueing the missing maps again ({1} of {2})",
                                                        scores.Count, requeues, MaxRequeues));
                    float started = startedAt;
                    QueueBatch();
                    startedAt = started;
                    return false;
                }
                timedOut = true;
            }
            if (!batchDone && !timedOut) { return false; }
            if (!scores.Values.Any(Qualifies) && batch + 1 < MaxBatches && !timedOut)
            {
                batch++;
                WorldSetupDriver.Note(string.Format("map variant: none of {0} qualified -- regenerating (batch {1} of {2})",
                                                    scores.Count, batch + 1, MaxBatches));
                QueueBatch();
                return false;
            }
            Unsubscribe();
            phase = Phase.Done;
            if (scores.Count == 0)
            {
                WorldSetupDriver.Note("map variant: no preview finished in time -- the tile's own map is used");
                return true;
            }

            // owner: "a true N/S facing must have its main mass touch both east and west sides of the tiles map ... like 30%
            // of the map or more is all brown touching both sides", plus a nook dug into that mass
            var passing = scores.Where(kv => Qualifies(kv.Value)).ToList();
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
                scores.Count, (batch + 1) * Candidates, passing.Count, best.Key == originalSeed ? "the original" : "#" + unchecked(best.Key - originalSeed),
                best.Value, accepted ? "accepted" : "NOT accepted (seed read back " + effective + ")"));
            if (passing.Count == 0) { WorldSetupDriver.Note("map variant: none had a 30%+ east-to-west main mountain with a nook -- took the closest"); }
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

            // the main mountain: the biggest connected rock mass; it must reach both the west and the east edge
            var main = new bool[w, h];
            var seenRock = new bool[w, h];
            int mainSize = 0;
            bool mainWE = false;
            var stack = new System.Collections.Generic.Stack<int>();
            for (int bx = 0; bx < w; bx++)
            {
                for (int bz = 0; bz < h; bz++)
                {
                    if (!rock[bx, bz] || seenRock[bx, bz]) { continue; }
                    var cells = new System.Collections.Generic.List<int>();
                    bool west = false, east = false;
                    stack.Push(bx * h + bz); seenRock[bx, bz] = true;
                    while (stack.Count > 0)
                    {
                        int v = stack.Pop(), x = v / h, z = v % h;
                        cells.Add(v); west |= x == 0; east |= x == w - 1;
                        foreach (var (nx, nz) in new[] { (x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1) })
                        {
                            if (nx < 0 || nz < 0 || nx >= w || nz >= h || seenRock[nx, nz] || !rock[nx, nz]) { continue; }
                            seenRock[nx, nz] = true; stack.Push(nx * h + nz);
                        }
                    }
                    if (cells.Count > mainSize)
                    {
                        mainSize = cells.Count; mainWE = west && east;
                        Array.Clear(main, 0, main.Length);
                        foreach (int v in cells) { main[v / h, v % h] = true; }
                    }
                }
            }

            // nook: open ground with the MAIN mountain on at least three sides -- a pocket dug into it, not open plain
            var nook = new bool[w, h];
            for (int bx = 0; bx < w; bx++)
            {
                for (int bz = 0; bz < h; bz++)
                {
                    if (rock[bx, bz]) { continue; }
                    int walls = 0;
                    if (Hit(main, w, h, bx, bz, 1, 0)) walls++;
                    if (Hit(main, w, h, bx, bz, -1, 0)) walls++;
                    if (Hit(main, w, h, bx, bz, 0, 1)) walls++;
                    if (Hit(main, w, h, bx, bz, 0, -1)) walls++;
                    nook[bx, bz] = walls >= 3;
                }
            }
            int biggest = 0;
            var seen = new bool[w, h];
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
                    if (size <= MaxNook) { biggest = Math.Max(biggest, size); }
                }
            }

            var score = new Score
            {
                RockFraction = rockBlocks / (float)(w * h),
                MainMass = mainSize / (float)(w * h),
                EastToWest = mainWE,
                NookBlocks = biggest,
            };
            // edge to edge first, then a 30%+ main mass, then the nook (up to ~300 blocks counts); so much rock that
            // little tan ground is left costs
            score.Total = (mainWE ? 2f : 0f) + Mathf.Min(score.MainMass / 0.30f, 1f) + Mathf.Min(biggest / 300f, 1f)
                          - Mathf.Max(0f, score.RockFraction - 0.65f) * 3f;
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
