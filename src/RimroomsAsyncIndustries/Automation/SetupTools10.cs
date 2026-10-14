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

        // ---------------------------------------------------------------- prisoners

        // The plain-language names the model uses, to Core/DLC interaction modes. Execution, hemogen farming and
        // bloodfeeding are deliberately absent: the stream is clean, and those are owner decisions, not ladder steps.
        private static readonly Dictionary<string, string> PrisonerModes = new Dictionary<string, string>
        {
            { "recruit", "AttemptRecruit" }, { "chat", "ReduceResistance" }, { "enslave", "Enslave" },
            { "convert", "Convert" }, { "release", "Release" }, { "maintain", "MaintainOnly" },
            { "interrogate", "Interrogate" }, { "reducewill", "ReduceWill" }
        };

        /// <summary>{"cmd":"prisoner","mode":"recruit|chat|enslave|convert|release|maintain","pawn":"all|name"}</summary>
        public static string Prisoner(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("mode", out string mode);
            mode = (mode ?? "recruit").Trim().ToLowerInvariant();
            if (!PrisonerModes.TryGetValue(mode, out string defName))
                return "refused: mode is one of " + string.Join(", ", PrisonerModes.Keys);
            PrisonerInteractionModeDef def = DefDatabase<PrisonerInteractionModeDef>.GetNamedSilentFail(defName);
            if (def == null) return "refused: " + defName + " is not in this game (its DLC is not loaded)";
            a.TryGetValue("pawn", out string who);
            List<Pawn> prisoners = map.mapPawns.PrisonersOfColonySpawned
                .Where(p => string.IsNullOrEmpty(who) || who == "all" || p.LabelShort.Equals(who, System.StringComparison.OrdinalIgnoreCase))
                .ToList();
            if (prisoners.Count == 0) return "ok: no prisoner" + (string.IsNullOrEmpty(who) || who == "all" ? "" : " named " + who);
            var set = new List<string>();
            foreach (Pawn p in prisoners)
            {
                if (p.guest == null || p.guest.ExclusiveInteractionMode == def) continue;
                p.guest.SetExclusiveInteraction(def);
                set.Add(p.LabelShort);
            }
            return set.Count == 0 ? "ok: already " + def.label : "ok: " + string.Join(", ", set) + " -> " + def.label;
        }

        // ---------------------------------------------------------------- generator + battery

        /// <summary>
        /// {"cmd":"generator","kind":"wood|solar|chemfuel"} a generator and one battery touching it, on open ground just
        /// outside the colony; then `power` joins the buildings to it.
        /// </summary>
        public static string Generator(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("kind", out string kind);
            kind = (kind ?? "wood").ToLowerInvariant();
            string defName = kind == "solar" ? "SolarGenerator" : kind == "chemfuel" ? "ChemfuelPoweredGenerator" : "WoodFiredGenerator";
            ThingDef gen = DefDatabase<ThingDef>.GetNamedSilentFail(defName), battery = DefDatabase<ThingDef>.GetNamedSilentFail("Battery");
            if (gen == null || battery == null) return "refused: no " + defName + " or Battery def";
            if (!gen.IsResearchFinished) return "refused: " + gen.label + " is not researched yet (research_next)";
            bool batteryOk = battery.IsResearchFinished;

            List<IntVec3> home = map.areaManager.Home.ActiveCells.ToList();
            IntVec3 centre = home.Count > 0 ? new IntVec3((int)home.Average(c => c.x), 0, (int)home.Average(c => c.z))
                : (map.mapPawns.FreeColonistsSpawned.FirstOrDefault()?.Position ?? map.Center);
            ThingDef genStuff = gen.MadeFromStuff ? GenStuff.DefaultStuffFor(gen) : null;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, 30f, false))
            {
                if (c.DistanceTo(centre) < 6f || !c.InBounds(map) || map.fogGrid.IsFogged(c)) continue;
                if (gen == DefDatabase<ThingDef>.GetNamedSilentFail("SolarGenerator") && c.Roofed(map)) continue;
                if (!GenConstruct.CanPlaceBlueprintAt(gen, c, Rot4.North, map, false, null, null, genStuff).Accepted) continue;
                CellRect footprint = GenAdj.OccupiedRect(c, Rot4.North, gen.size);
                if (footprint.Cells.Any(x => map.fogGrid.IsFogged(x) || (defName == "SolarGenerator" && x.Roofed(map)))) continue;
                IntVec3 batteryCell = IntVec3.Invalid;
                if (batteryOk)
                {
                    // a battery cell on the footprint's edge, so the two touch and share a net
                    foreach (IntVec3 e in footprint.ExpandedBy(1).EdgeCells)
                    {
                        if (GenConstruct.CanPlaceBlueprintAt(battery, e, Rot4.North, map, false, null, null, null).Accepted &&
                            !GenAdj.OccupiedRect(e, Rot4.North, battery.size).Overlaps(footprint))
                        { batteryCell = e; break; }
                    }
                    if (!batteryCell.IsValid) continue;
                }
                GenConstruct.PlaceBlueprintForBuild(gen, c, map, Rot4.North, Faction.OfPlayer, genStuff);
                if (batteryCell.IsValid) GenConstruct.PlaceBlueprintForBuild(battery, batteryCell, map, Rot4.North, Faction.OfPlayer, null);
                return "ok: " + gen.label + " blueprint at " + c.x + "," + c.z +
                       (batteryCell.IsValid ? ", battery at " + batteryCell.x + "," + batteryCell.z : " (batteries not researched yet)") +
                       " -- once built, run power to join every building to it" + (defName == "WoodFiredGenerator" ? "; it burns wood, keep a log stockpile" : "");
            }
            return "refused: no open " + (defName == "SolarGenerator" ? "unroofed " : "") + "ground for a " + gen.label + " within 30 cells of the colony";
        }

        // ---------------------------------------------------------------- research

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
