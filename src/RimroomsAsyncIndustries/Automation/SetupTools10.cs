using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Batch 5 (research) of the owner's playbook. PLAYBOOK 4b, owner verbatim: "you should be rushing microelectionices
    /// then the mico analysis things then the computing reasearching building them as you research them".
    ///   {"cmd":"research_next"}   sets the current project to the first unfinished, available one in the playbook order,
    ///                             else the cheapest available; and names every research upgrade that is unlocked but not
    ///                             built, because the playbook builds each "the moment it is researched"
    /// </summary>
    internal static class SetupTools10
    {
        // Power first (nothing else runs without it), then the owner's rush, then antibiotics and gifts by pod.
        private static readonly string[] Order =
        {
            "Electricity", "Batteries", "MicroelectronicsBasics", "MultiAnalyzer",
            "DrugProduction", "PenoxycylineProduction", "TransportPod"
        };

        // Buildings that raise research speed or unlock trade -- the "build it the moment it is researched" list.
        private static readonly string[] Upgrades =
            { "HiTechResearchBench", "MultiAnalyzer", "OrbitalTradeBeacon", "CommsConsole", "DrugLab" };

        public static string ResearchNext()
        {
            ResearchManager rm = Find.ResearchManager;
            ResearchProjectDef pick = null;
            string why = "";
            foreach (string name in Order)
            {
                ResearchProjectDef p = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(name);
                if (p == null || p.IsFinished || !p.CanStartNow) continue;
                pick = p; why = "playbook order"; break;
            }
            if (pick == null)
            {
                pick = DefDatabase<ResearchProjectDef>.AllDefsListForReading
                    .Where(p => !p.IsFinished && p.CanStartNow)
                    .OrderBy(p => p.CostApparent).FirstOrDefault();
                why = "cheapest available";
            }

            string set;
            if (pick == null) set = "nothing left that can start now";
            else if (rm.GetProject() == pick) set = "already on " + pick.LabelCap + " (" + why + ")";
            else { rm.SetCurrentProject(pick); set = "now researching " + pick.LabelCap + " (" + why + ", " + pick.CostApparent.ToString("0") + " points)"; }

            // Unlocked and not built (or planned) on any player map.
            var missing = new List<string>();
            foreach (string name in Upgrades)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def == null || !def.IsResearchFinished) continue;
                bool have = Find.Maps.Any(m => m.IsPlayerHome &&
                    (m.listerBuildings.allBuildingsColonist.Any(b => b.def == def) ||
                     m.listerThings.AllThings.Any(t => (t.def.IsBlueprint || t.def.IsFrame) && t.def.entityDefToBuild == def)));
                if (!have) missing.Add(name);
            }
            return "ok: " + set + (missing.Count == 0 ? "" : " -- unlocked and not built: " + string.Join(", ", missing) +
                   " (build def <name> next to the research benches / comms)");
        }
    }
}
