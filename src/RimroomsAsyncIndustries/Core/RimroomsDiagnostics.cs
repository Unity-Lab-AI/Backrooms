using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>RR-COMPAT: opt-in, bounded development counters; never saved as campaign data.</summary>
    public static class RimroomsDiagnostics
    {
        private const int CategoryLimit = 16;
        private const int SampleCapacity = 2048;
        private static readonly Dictionary<string, Counter> Counters = new Dictionary<string, Counter>(StringComparer.Ordinal);
        public static bool Enabled { get; private set; }
        public static void Start()
        {
            Counters.Clear(); Enabled = true;
            Log.Message("[Rimrooms][Performance] Begin " + RimroomsMod.ModVersion + "; component scopes only, no whole-game tick baseline.");
        }
        public static void Stop() { Enabled = false; }
        public static Measurement Measure(string category)
        { return Enabled ? new Measurement(category, Stopwatch.GetTimestamp()) : default(Measurement); }

        public static string Snapshot()
        {
            var lines = new List<string> { "Rimrooms " + RimroomsMod.ModVersion + "; component samples; counters " + (Enabled ? "running" : "stopped") };
            foreach (KeyValuePair<string, Counter> pair in Counters.OrderBy(p => p.Key))
            {
                Counter counter = pair.Value;
                double[] sorted = counter.samples.Take(counter.retained).OrderBy(value => value).ToArray();
                double median = sorted.Length == 0 ? 0 : sorted[(sorted.Length - 1) / 2];
                double p95 = sorted.Length == 0 ? 0 : sorted[(int)Math.Ceiling(sorted.Length * 0.95) - 1];
                lines.Add(string.Format(CultureInfo.InvariantCulture,
                    "{0}: calls={1}; mean={2:F4}ms; max={3:F4}ms; recent[{4}] p50={5:F4}ms p95={6:F4}ms",
                    pair.Key, counter.calls, counter.calls == 0 ? 0 : counter.total / counter.calls, counter.maximum, sorted.Length, median, p95));
            }
            lines.Add("Loaded maps=" + (Current.Game == null ? 0 : Find.Maps.Count) + "; managed bytes=" + GC.GetTotalMemory(false));
            using (Process process = Process.GetCurrentProcess()) { lines.Add("Private process bytes=" + process.PrivateMemorySize64); }
            return string.Join("\n", lines.ToArray());
        }
        public static void WriteSnapshot() { Log.Message("[Rimrooms][Performance] " + Snapshot()); }

        public static void WriteRuntimeIdentity()
        {
            var mods = LoadedModManager.RunningMods.ToList();
            var assembly = typeof(RimroomsMod).Assembly;
            var lines = new List<string>
            {
                "Rimrooms=" + RimroomsMod.ModVersion + "; module=" + assembly.ManifestModule.ModuleVersionId,
                "Core assembly=" + typeof(Game).Assembly.GetName().Version,
                "Loaded entries=" + mods.Count + "; package IDs below are the current native order, not a compatibility result."
            };
            for (int i = 0; i < mods.Count; i++) { lines.Add((i + 1) + ": " + mods[i].PackageIdPlayerFacing); }
            if (Current.Game != null)
            {
                var campaign = Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
                lines.Add("Tick=" + Find.TickManager.TicksGame + "; maps=" + Find.Maps.Count +
                    "; branch=" + (campaign?.BranchId ?? "none"));
                if (campaign != null)
                {
                    foreach (var coordinate in campaign.Coordinates)
                    {
                        var site = coordinate.Site as Generation.RimroomsDestinationMapParent;
                        lines.Add("Coordinate=" + coordinate.Id + "; seed=" + coordinate.Seed +
                            "; generator=" + coordinate.GeneratorVersion + "; status=" + coordinate.Status +
                            "; map=" + (site?.Map == null ? "absent" : site.Map.uniqueID.ToString()) +
                            "; candidate=" + (site == null ? "none" : site.CandidateIndex.ToString()) +
                            "; failure=" + (site?.GenerationFailureKey ?? "none"));
                    }
                }
            }
            Log.Message("[Rimrooms][Identity]\n" + string.Join("\n", lines.ToArray()));
        }

        private static void Record(string category, long start)
        {
            if (!Enabled || category == null) { return; }
            Counter counter;
            if (!Counters.TryGetValue(category, out counter))
            {
                if (Counters.Count >= CategoryLimit) { return; }
                counter = new Counter(); Counters.Add(category, counter);
            }
            double elapsed = (Stopwatch.GetTimestamp() - start) * 1000.0 / Stopwatch.Frequency;
            counter.calls++; counter.total += elapsed; counter.maximum = Math.Max(counter.maximum, elapsed);
            counter.samples[counter.next] = elapsed; counter.next = (counter.next + 1) % SampleCapacity;
            counter.retained = Math.Min(SampleCapacity, counter.retained + 1);
        }
        public struct Measurement : IDisposable
        {
            private readonly string category;
            private readonly long start;
            internal Measurement(string category, long start) { this.category = category; this.start = start; }
            public void Dispose() { if (category != null) { Record(category, start); } }
        }
        private sealed class Counter
        {
            internal long calls;
            internal double total;
            internal double maximum;
            internal int next;
            internal int retained;
            internal readonly double[] samples = new double[SampleCapacity];
        }
    }
}
