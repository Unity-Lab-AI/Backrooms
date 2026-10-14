using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Batch 5 (trade) of the owner's playbook. PLAYBOOK 10: "research Microelectronics, build a trade beacon, then call
    /// ships; until then trade only with caravans that walk in", and "never sell irreplaceable high tech (age-reversing
    /// serums, anything that cannot be made or bought back)". The negotiator has to be THERE, as for a player: at a powered
    /// comms console for a ship, beside the trader for a caravan. The deal itself is Core's own TradeSession, so prices,
    /// silver and beacon range are the game's.
    ///   {"cmd":"trade"}                                  list traders in reach and what each buys and sells
    ///   {"cmd":"trade","with":"ship|caravan","trader":"<name>","sell":"Cloth:200,Beer:40","buy":"Steel:300,ComponentIndustrial:10"}
    /// `trader` picks the one you called (owner: "call the trader they selected"); with several in reach and no name, refused.
    /// </summary>
    internal static class SetupTools11
    {
        private static Dictionary<string, int> Parse(Dictionary<string, string> a, string key)
        {
            var d = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            if (!a.TryGetValue(key, out string s) || string.IsNullOrWhiteSpace(s)) return d;
            foreach (string part in s.Split(','))
            {
                string[] kv = part.Split(':');
                if (kv.Length == 2 && int.TryParse(kv[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int n) && n > 0)
                    d[kv[0].Trim()] = n;
            }
            return d;
        }

        /// <summary>The playbook's never-sell rule: spacer tech and above cannot be made or bought back by a colony.</summary>
        private static bool Irreplaceable(ThingDef def) => def != null && def.techLevel >= TechLevel.Spacer;

        private static Pawn Negotiator(Map map) =>
            map.mapPawns.FreeColonistsSpawned
                .Where(p => !p.Downed && !p.InMentalState && p.health.capacities.CapableOf(PawnCapacityDefOf.Talking))
                .OrderByDescending(p => p.GetStatValue(StatDefOf.TradePriceImprovement)).FirstOrDefault();

        public static string Trade(Map map, Dictionary<string, string> a)
        {
            Building_CommsConsole console = map.listerBuildings.allBuildingsColonist.OfType<Building_CommsConsole>()
                .FirstOrDefault(c => c.CanUseCommsNow);
            List<TradeShip> ships = map.passingShipManager.passingShips.OfType<TradeShip>().ToList();
            List<Pawn> caravans = map.mapPawns.AllPawnsSpawned
                .Where(p => p.trader?.traderKind != null && p.CanTradeNow && !p.HostileTo(Faction.OfPlayer)).ToList();

            Dictionary<string, int> sell = Parse(a, "sell"), buy = Parse(a, "buy");
            int silverAfter = 0;
            a.TryGetValue("with", out string with);
            if (sell.Count == 0 && buy.Count == 0) return List(console, ships, caravans);

            ITrader trader; Pawn traderPawn = null;
            a.TryGetValue("trader", out string who);
            bool Named(string label) => string.IsNullOrEmpty(who) || (label ?? "").IndexOf(who, StringComparison.OrdinalIgnoreCase) >= 0;
            bool wantShip = with != null && with.StartsWith("s", StringComparison.OrdinalIgnoreCase);
            if (wantShip || (with == null && ships.Count > 0 && caravans.Count == 0))
            {
                if (ships.Count == 0) return "refused: no trade ship in orbit";
                if (console == null) return "refused: no powered comms console -- a ship can only be reached through one";
                List<TradeShip> chosen = ships.Where(s => Named(s.TraderName) || Named(s.TraderKind.label)).ToList();
                if (chosen.Count == 0) return "refused: no ship in orbit named " + who + " -- in orbit: " + string.Join(", ", ships.Select(s => s.TraderName));
                if (chosen.Count > 1) return "refused: name the ship (trader=): " + string.Join(", ", chosen.Select(s => s.TraderName + " (" + s.TraderKind.label + ")"));
                trader = chosen[0];
            }
            else
            {
                if (caravans.Count == 0) return "refused: no trader caravan here" + (ships.Count > 0 ? " (a ship is in orbit: with ship)" : "");
                List<Pawn> chosen = caravans.Where(p => Named(p.LabelShort) || Named(p.Faction?.Name) || Named(p.trader.traderKind.label)).ToList();
                if (chosen.Count == 0) return "refused: no caravan trader named " + who + " -- here: " + string.Join(", ", caravans.Select(p => p.LabelShort + " of " + (p.Faction?.Name ?? "?")));
                if (chosen.Count > 1) return "refused: name the trader (trader=): " + string.Join(", ", chosen.Select(p => p.LabelShort + " of " + (p.Faction?.Name ?? "?")));
                traderPawn = chosen[0];
                trader = traderPawn;
            }

            Pawn negotiator = Negotiator(map);
            if (negotiator == null) return "refused: no colonist who can talk";

            // Be there first, as a player's colonist must.
            IntVec3 spot = traderPawn != null ? traderPawn.Position : console.InteractionCell;
            bool there = traderPawn != null ? negotiator.Position.AdjacentTo8WayOrInside(traderPawn.Position) : negotiator.Position == spot;
            if (!there)
            {
                if (!negotiator.CanReach(spot, PathEndMode.Touch, Danger.Some)) return "refused: " + negotiator.LabelShort + " cannot reach the " + (traderPawn != null ? "trader" : "comms console");
                negotiator.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, spot), JobTag.Misc);
                return "ok: " + negotiator.LabelShort + " walking to the " + (traderPawn != null ? traderPawn.LabelShort : "comms console") +
                       " at " + spot.x + "," + spot.z + " -- run the same trade again once there";
            }

            var done = new List<string>();
            var skipped = new List<string>();
            try
            {
                TradeSession.SetupWith(trader, negotiator, false);
                List<Tradeable> all = TradeSession.deal.AllTradeables.ToList();
                foreach (KeyValuePair<string, int> s in sell)
                {
                    Tradeable t = all.FirstOrDefault(x => x.ThingDef != null && x.ThingDef.defName.Equals(s.Key, StringComparison.OrdinalIgnoreCase));
                    if (t == null) { skipped.Add("sell " + s.Key + " (trader will not take it or none in reach)"); continue; }
                    if (Irreplaceable(t.ThingDef)) { skipped.Add("sell " + s.Key + " (never sell irreplaceable high tech)"); continue; }
                    int n = Math.Min(s.Value, t.CountHeldBy(Transactor.Colony));
                    if (n <= 0 || !SetTo(t, n, TradeAction.PlayerSells)) { skipped.Add("sell " + s.Key + " (none to sell)"); continue; }
                    done.Add("sell " + n + " " + t.Label);
                }
                foreach (KeyValuePair<string, int> b in buy)
                {
                    Tradeable t = all.FirstOrDefault(x => x.ThingDef != null && x.ThingDef.defName.Equals(b.Key, StringComparison.OrdinalIgnoreCase));
                    if (t == null) { skipped.Add("buy " + b.Key + " (trader has none)"); continue; }
                    int n = Math.Min(b.Value, t.CountHeldBy(Transactor.Trader));
                    if (n <= 0 || !SetTo(t, n, TradeAction.PlayerBuys)) { skipped.Add("buy " + b.Key + " (none on offer)"); continue; }
                    done.Add("buy " + n + " " + t.Label);
                }
                if (done.Count == 0) return "refused: nothing to trade -- " + string.Join("; ", skipped);
                // Owner, 2026-10-13: "always keeping and trying to end a trade ewwith at least a 1000 silver surpluse for calling
                // the next trasder tyo land". The floor is the deal's own arithmetic -- silver held plus what this deal moves
                // (Core's currency line: negative when the colony pays) -- never a guess from a stale sensor.
                int floor = a.TryGetValue("floor", out string fs) && int.TryParse(fs, out int fv) ? fv : 1000;
                bool force = a.TryGetValue("force", out string fo) && fo.StartsWith("t", StringComparison.OrdinalIgnoreCase);
                TradeSession.deal.UpdateCurrencyCount();
                Tradeable cur = TradeSession.deal.CurrencyTradeable;
                int held = cur != null ? cur.CountHeldBy(Transactor.Colony) : 0;
                silverAfter = cur != null ? held + cur.CountToTransfer : held;
                if (cur != null && buy.Count > 0 && silverAfter < floor && !force)
                    return "refused: the deal would leave " + silverAfter + " silver (" + held + " now), under the " + floor +
                           " floor that calls the next trader -- sell more or buy less (force true overrides): " + string.Join(", ", done);
                // Core refuses a deal the colony cannot pay for; the message says why.
                if (!TradeSession.deal.TryExecute(out bool traded) || !traded)
                    return "refused: the trader would not accept that deal (not enough silver in beacon range, or the trader's limits): " + string.Join(", ", done);
            }
            finally { TradeSession.Close(); }
            return "ok: traded with " + trader.TraderName + " through " + negotiator.LabelShort + ": " + string.Join(", ", done) +
                   "; silver after the deal about " + silverAfter + (skipped.Count > 0 ? " -- skipped " + string.Join("; ", skipped) : "");
        }

        /// <summary>
        /// Set a line to move n units in the wanted direction. Which sign is "sell" is Core's business, so it is read back
        /// from the line's own ActionToDo rather than assumed: try one sign, and if Core reads it the other way, flip.
        /// </summary>
        private static bool SetTo(Tradeable t, int n, TradeAction want)
        {
            foreach (int count in new[] { n, -n })
            {
                if (!t.CanAdjustTo(count).Accepted) continue;
                t.AdjustTo(count);
                if (t.ActionToDo == want) return true;
            }
            if (t.CanAdjustTo(0).Accepted) t.AdjustTo(0);
            return false;
        }

        private static string List(Building_CommsConsole console, List<TradeShip> ships, List<Pawn> caravans)
        {
            var lines = new List<string>();
            foreach (TradeShip s in ships)
                lines.Add("ship " + s.TraderName + " (" + s.TraderKind.label + ")" + (console == null ? " -- needs a powered comms console" : ""));
            foreach (Pawn p in caravans)
                lines.Add("caravan " + p.LabelShort + " of " + (p.Faction?.Name ?? "?") + " (" + p.trader.traderKind.label + ") at " + p.Position.x + "," + p.Position.z);
            if (lines.Count == 0) return "ok: no trader in reach -- research MicroelectronicsBasics, build a comms console and an orbital trade beacon to call ships";
            return "ok: " + string.Join("; ", lines) + " -- trade with=ship|caravan trader=<name> sell=Def:n,.. buy=Def:n,.. (never spacer-tech sells)";
        }
    }
}
