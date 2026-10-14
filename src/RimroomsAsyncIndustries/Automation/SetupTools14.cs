using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Calling a trader in through the comms console, PLAYBOOK 10 ("traders worked"). This is Core's own "Request trader"
    /// menu option, reached by reflection (`FactionDialogMaker.RequestTraderOption` is private), so the goodwill cost, the
    /// cooldown, the "cannot request" reasons and the arrival delay are the game's and never re-implemented here. As for a
    /// player, the negotiator has to be standing at a powered comms console first.
    ///   {"cmd":"call_trader"}                                   list factions that can be asked and their trader kinds
    ///   {"cmd":"call_trader","faction":"Outlander","kind":"bulk goods"}   ask that faction for that kind of caravan
    /// </summary>
    internal static class SetupTools14
    {
        private const BindingFlags Any = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

        private static string Text(DiaOption o)
        {
            FieldInfo f = typeof(DiaOption).GetField("text", Any);
            return f == null ? "?" : (f.GetValue(o) as string ?? "?");
        }

        private static bool CanBeAsked(Faction f) =>
            f != null && !f.IsPlayer && !f.Hidden && !f.HostileTo(Faction.OfPlayer) && f.def.humanlikeFaction &&
            f.def.caravanTraderKinds != null && f.def.caravanTraderKinds.Count > 0;

        public static string CallTrader(Map map, Dictionary<string, string> a)
        {
            Building_CommsConsole console = map.listerBuildings.allBuildingsColonist.OfType<Building_CommsConsole>()
                .FirstOrDefault(c => c.CanUseCommsNow);
            if (console == null) return "refused: no powered comms console";
            List<Faction> askable = Find.FactionManager.AllFactionsVisible.Where(CanBeAsked)
                .OrderByDescending(f => f.PlayerGoodwill).ToList();
            if (askable.Count == 0) return "ok: no non-hostile faction with trader caravans";

            a.TryGetValue("faction", out string fname);
            a.TryGetValue("kind", out string kname);
            if (string.IsNullOrEmpty(fname))
                return "ok: " + string.Join("; ", askable.Select(f => f.Name + " (goodwill " + f.PlayerGoodwill + "): " +
                    string.Join(", ", f.def.caravanTraderKinds.Select(k => k.label)))) + " -- call_trader faction=<name> kind=<label>";
            Faction faction = askable.FirstOrDefault(f => f.Name.IndexOf(fname, StringComparison.OrdinalIgnoreCase) >= 0 ||
                                                           f.def.label.IndexOf(fname, StringComparison.OrdinalIgnoreCase) >= 0);
            if (faction == null) return "refused: no askable faction matches " + fname;

            Pawn negotiator = map.mapPawns.FreeColonistsSpawned
                .Where(p => !p.Downed && !p.InMentalState && p.health.capacities.CapableOf(PawnCapacityDefOf.Talking))
                .OrderByDescending(p => p.GetStatValue(StatDefOf.NegotiationAbility)).FirstOrDefault();
            if (negotiator == null) return "refused: no colonist who can talk";
            if (negotiator.Position != console.InteractionCell)
            {
                if (!negotiator.CanReach(console.InteractionCell, PathEndMode.OnCell, Danger.Some))
                    return "refused: " + negotiator.LabelShort + " cannot reach the comms console";
                negotiator.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, console.InteractionCell), JobTag.Misc);
                return "ok: " + negotiator.LabelShort + " walking to the comms console at " + console.InteractionCell.x + "," +
                       console.InteractionCell.z + " -- run the same call_trader again once there";
            }

            // Core's own menu option, with its arguments matched by type so a signature change is a plain refusal, not a crash.
            MethodInfo method = typeof(FactionDialogMaker).GetMethod("RequestTraderOption", Any);
            if (method == null) return "refused: this game version has no FactionDialogMaker.RequestTraderOption";
            ParameterInfo[] ps = method.GetParameters();
            object[] args = new object[ps.Length];
            for (int i = 0; i < ps.Length; i++)
            {
                Type t = ps[i].ParameterType;
                if (t == typeof(Map)) args[i] = map;
                else if (t == typeof(Faction)) args[i] = faction;
                else if (t == typeof(Pawn)) args[i] = negotiator;
                else return "refused: RequestTraderOption wants a " + t.Name + " this command does not know";
            }
            DiaOption option = method.Invoke(null, args) as DiaOption;
            if (option == null) return "refused: the request option could not be built";
            if (option.disabled) return "refused: " + faction.Name + " cannot be asked now -- " + (option.disabledReason ?? "no reason given");

            // The kinds submenu: one option per caravan kind; its action is what spends goodwill and queues the arrival.
            List<DiaOption> kinds = option.link != null ? option.link.options : null;
            if (kinds == null || kinds.Count == 0)
            {
                if (option.action == null) return "refused: the request option offers nothing to choose";
                option.action();
                return "ok: asked " + faction.Name + " for a trader through " + negotiator.LabelShort + "; goodwill now " + faction.PlayerGoodwill;
            }
            DiaOption pick = string.IsNullOrEmpty(kname)
                ? kinds.FirstOrDefault(k => !k.disabled && k.action != null)
                : kinds.FirstOrDefault(k => Text(k).IndexOf(kname, StringComparison.OrdinalIgnoreCase) >= 0);
            if (pick == null)
                return "refused: no caravan kind matches " + kname + " -- offered: " + string.Join(", ", kinds.Select(Text));
            if (pick.disabled) return "refused: " + Text(pick) + " -- " + (pick.disabledReason ?? "not available");
            if (pick.action == null) return "refused: " + Text(pick) + " has no action (it is a back/disconnect entry)";
            int before = faction.PlayerGoodwill;
            pick.action();
            return "ok: asked " + faction.Name + " for " + Text(pick) + " through " + negotiator.LabelShort +
                   "; goodwill " + before + " -> " + faction.PlayerGoodwill + "; the caravan arrives in a few days";
        }
    }
}
