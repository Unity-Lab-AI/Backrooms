using System;
using System.IO;
using System.Linq;
using Verse;

namespace RimPLC
{
    /// <summary>Finds the mod's own folder (for the preset) and loads the book once per session.</summary>
    public sealed class RimPLCMod : Mod
    {
        public const string PackageId = "Operator.RimPLC";
        public const string BookFile = "LadderV2.json";

        private static string rootDir;
        private static Ladder book;

        public RimPLCMod(ModContentPack content) : base(content)
        {
            rootDir = content.RootDir;
        }

        public static string RootDir
        {
            get
            {
                if (rootDir == null)
                {
                    ModContentPack pack = LoadedModManager.RunningModsListForReading.FirstOrDefault(
                        m => string.Equals(m.PackageId, PackageId, StringComparison.OrdinalIgnoreCase));
                    rootDir = pack?.RootDir;
                }

                return rootDir;
            }
        }

        /// <summary>The book preset (Presets/LadderV2.json, written by tools/rimplc-check.py --emit from docs/playbook.gates.json).</summary>
        public static Ladder Book
        {
            get
            {
                if (book == null)
                {
                    string dir = RootDir;
                    string path = dir == null ? null : Path.Combine(Path.Combine(dir, "Presets"), BookFile);
                    book = path == null
                        ? new Ladder { LoadError = "RimPLC folder not found" }
                        : Ladder.Load(path);
                    if (book.LoadError != null) Log.Error("[RimPLC] book preset did not load: " + book.LoadError);
                    // The file is named with its size and its raw rung count (2026-10-13: a stale Player.log from the day before was
                    // read as "127 rungs" against a 427-rung preset -- the line now says WHICH file was read and what the text holds).
                    else Log.Message("[RimPLC] book " + book.PresetId + ": " + book.Rungs.Count + " rungs, " + book.Sensors.Count + " sensors" +
                                     " (" + path + ", " + FileBytes(path) + " bytes, " + RawRungCount(path) + " rung ids in the text)");
                }

                return book;
            }
        }

        private static long FileBytes(string path)
        {
            try { return new FileInfo(path).Length; } catch (Exception) { return -1; }
        }

        /// <summary>How many `"id":` keys the preset text holds at rung depth (the two-space, three-space pretty print of the emitter).</summary>
        private static int RawRungCount(string path)
        {
            try
            {
                string text = File.ReadAllText(path);
                int n = 0, i = 0;
                while ((i = text.IndexOf("\n   \"id\": \"", i, StringComparison.Ordinal)) >= 0) { n++; i++; }
                return n;
            }
            catch (Exception) { return -1; }
        }

        /// <summary>A rung's requires entry: a DLC name or mod:&lt;packageId&gt;.</summary>
        public static bool Applicable(string requirement)
        {
            switch (requirement)
            {
                case "Royalty": return ModsConfig.RoyaltyActive;
                case "Ideology": return ModsConfig.IdeologyActive;
                case "Biotech": return ModsConfig.BiotechActive;
                case "Anomaly": return ModsConfig.AnomalyActive;
                case "Odyssey": return ModsConfig.OdysseyActive;
            }

            if (requirement != null && requirement.StartsWith("mod:", StringComparison.Ordinal))
            {
                return ModsConfig.IsActive(requirement.Substring(4));
            }

            return false;
        }
    }
}
