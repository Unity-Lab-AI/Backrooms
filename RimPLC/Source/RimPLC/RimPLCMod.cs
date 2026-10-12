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
                    book = dir == null
                        ? new Ladder { LoadError = "RimPLC folder not found" }
                        : Ladder.Load(Path.Combine(Path.Combine(dir, "Presets"), BookFile));
                    if (book.LoadError != null) Log.Error("[RimPLC] book preset did not load: " + book.LoadError);
                    else Log.Message("[RimPLC] book " + book.PresetId + ": " + book.Rungs.Count + " rungs, " + book.Sensors.Count + " sensors");
                }

                return book;
            }
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
