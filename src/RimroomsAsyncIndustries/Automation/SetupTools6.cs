using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Batch 3 of the rebuilt ladder's commands (2026-10-13 inventory section D; owner: "kill em,, we have to finishe the
    /// RimPLC"). Storage copy/priority and the one-call crew setup the pawns_unconfigured rung needs.
    ///   {"cmd":"stockpile_priority","zone":"Stockpile zone 1","priority":"Important"}
    ///   {"cmd":"stockpile_copy","from":"Food store","to":"Stockpile zone 3"}   filter + priority copied
    ///   {"cmd":"crew_setup","pawn":"Gee" (empty = everyone)}  Attack, self-tend where they can doctor, the "No drugs"
    ///                                                          policy; weapons stay with empire_pass / equip
    ///   {"cmd":"terraform","mode":"bridge|smooth|remove_floor","x":10,"z":10,"w":5,"h":5}
    ///       bridge: a Bridge blueprint on every cell of the rectangle that takes one (water, marsh); smooth / remove_floor:
    ///       Core's own Designator_SmoothSurface / Designator_RemoveFloor, cell by cell, with their own checks. Core has no
    ///       way to turn mud or water into soil, so "terraform" means: bridge what is wet, smooth or strip what is built on.
    /// Mod register checked: storage mods (Adaptive / LWM / Warehouse / RimFridge) keep vanilla StorageSettings on zones,
    /// so CopyFrom works on their zones too; Simple sidearms is untouched (weapons are not handled here).
    /// </summary>
    internal static class SetupTools6
    {
        private static Zone_Stockpile Zone(Map map, string label) =>
            map.zoneManager.AllZones.OfType<Zone_Stockpile>().FirstOrDefault(z => z.label.Equals(label ?? "", StringComparison.OrdinalIgnoreCase));

        public static string StockpilePriority(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("zone", out string name);
            Zone_Stockpile z = Zone(map, name);
            if (z == null) return "refused: no stockpile named '" + name + "' (" + string.Join(", ", map.zoneManager.AllZones.OfType<Zone_Stockpile>().Select(x => x.label)) + ")";
            a.TryGetValue("priority", out string pr);
            if (!Enum.TryParse(pr ?? "", true, out StoragePriority p) || p == StoragePriority.Unstored) return "refused: priority Low|Normal|Preferred|Important|Critical";
            z.settings.Priority = p;
            return "ok: " + z.label + " priority " + z.settings.Priority;
        }

        public static string StockpileCopy(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("from", out string from);
            a.TryGetValue("to", out string to);
            Zone_Stockpile src = Zone(map, from), dst = Zone(map, to);
            if (src == null || dst == null) return "refused: name both stockpiles (from, to)";
            if (src == dst) return "refused: from and to are the same stockpile";
            dst.settings.CopyFrom(src.settings);
            return "ok: " + dst.label + " now stores what " + src.label + " stores, priority " + dst.settings.Priority;
        }

        public static string CrewSetup(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("pawn", out string who);
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned
                                 .Where(p => string.IsNullOrEmpty(who) || p.LabelShort.Equals(who, StringComparison.OrdinalIgnoreCase)).ToList();
            if (crew.Count == 0) return "refused: no such colonist";
            DrugPolicy noDrugs = Current.Game.drugPolicyDatabase.AllPolicies
                                        .FirstOrDefault(d => d.label.IndexOf("no", StringComparison.OrdinalIgnoreCase) >= 0 &&
                                                             d.label.IndexOf("drug", StringComparison.OrdinalIgnoreCase) >= 0);
            var lines = new List<string>();
            foreach (Pawn p in crew)
            {
                var done = new List<string>();
                if (p.playerSettings != null && !p.WorkTagIsDisabled(WorkTags.Violent))
                { p.playerSettings.hostilityResponse = HostilityResponseMode.Attack; done.Add("attack"); }
                if (p.playerSettings != null && !p.WorkTypeIsDisabled(WorkTypeDefOf.Doctor))
                { p.playerSettings.selfTend = true; done.Add("self-tend"); }
                if (noDrugs != null && p.drugs != null) { p.drugs.CurrentPolicy = noDrugs; done.Add("no drugs"); }
                bool armed = p.equipment?.Primary != null;
                lines.Add(p.LabelShort + ": " + string.Join(", ", done) + (armed || p.WorkTagIsDisabled(WorkTags.Violent) ? "" : " -- STILL UNARMED: run empire_pass"));
            }
            return "ok: " + string.Join("; ", lines) + (noDrugs == null ? " (no 'No drugs' policy found)" : "");
        }

        public static string Terraform(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("mode", out string mode);
            mode = (mode ?? "bridge").ToLowerInvariant();
            int x = Num(a, "x", -1), z = Num(a, "z", -1);
            CellRect r = new CellRect(x, z, Math.Max(1, Math.Min(30, Num(a, "w", 1))), Math.Max(1, Math.Min(30, Num(a, "h", 1)))).ClipInsideMap(map);
            if (r.Area == 0 || !new IntVec3(x, 0, z).InBounds(map)) return "refused: x,z outside the map";
            int done = 0, refused = 0;
            string why = null;
            if (mode == "bridge")
            {
                TerrainDef bridge = TerrainDefOf.Bridge;
                if (bridge == null) return "refused: no Bridge terrain def";
                foreach (IntVec3 c in r)
                {
                    AcceptanceReport ok = GenConstruct.CanPlaceBlueprintAt(bridge, c, Rot4.North, map, false, null, null, null);
                    if (ok.Accepted) { GenConstruct.PlaceBlueprintForBuild(bridge, c, map, Rot4.North, Faction.OfPlayer, null); done++; }
                    else { refused++; why = why ?? ok.Reason; }
                }
            }
            else if (mode == "smooth" || mode == "remove_floor")
            {
                // Core designators act on Find.CurrentMap, so the map has to be the one on screen
                if (Find.CurrentMap != map) return "refused: " + mode + " needs that map on screen (Core designators work on the current map)";
                Designator d = mode == "smooth" ? (Designator)new Designator_SmoothSurface() : new Designator_RemoveFloor();
                foreach (IntVec3 c in r)
                {
                    AcceptanceReport ok = d.CanDesignateCell(c);
                    if (ok.Accepted) { d.DesignateSingleCell(c); done++; }
                    else { refused++; why = why ?? ok.Reason; }
                }
            }
            else return "refused: mode is bridge, smooth or remove_floor";
            return (done > 0 ? "ok: " : "refused: ") + mode + " on " + done + " cell(s), " + refused + " refused" +
                   (why != null ? " (first refusal: " + why + ")" : "") + (mode == "bridge" && done > 0 ? " -- needs wood and Construction work on" : "");
        }

        private static int Num(Dictionary<string, string> a, string k, int dflt) =>
            a.TryGetValue(k, out string s) && int.TryParse(s, System.Globalization.NumberStyles.Integer, System.Globalization.CultureInfo.InvariantCulture, out int v) ? v : dflt;
    }
}
