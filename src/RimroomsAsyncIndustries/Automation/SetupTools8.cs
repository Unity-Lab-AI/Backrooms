using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Batch 3 (defence) of the owner's playbook as code. PLAYBOOK.md: "Rifles and sidearms on everyone, a fallback point,
    /// embrasures toward the approach" and "Every colonist carries a melee sidearm ... alongside the rifle".
    ///   {"cmd":"arm"}                          every colonist with no ranged weapon goes to equip the nearest free one;
    ///                                          an armed colonist with no melee weapon carried picks one up as a sidearm;
    ///                                          if guns run out, a crafting bill for the shortfall goes on a table that can
    ///   {"cmd":"draft","pawn":"all|Gee","on":"true|false"}   draft or release a group in one call
    ///   {"cmd":"hold"}                         draft every armed colonist and send each to its own cell behind an embrasure
    ///                                          (else sandbags / barricades), the ones nearest the threat first
    /// </summary>
    internal static class SetupTools8
    {
        // Cheapest first, so a short-handed colony gets something in hands soonest.
        private static readonly string[] GunRecipes =
            { "Make_Gun_Revolver", "Make_Gun_BoltActionRifle", "Make_Bow_Short", "Make_Bow_Recurve" };

        private static bool HasRanged(Pawn p) => p.equipment?.Primary != null && p.equipment.Primary.def.IsRangedWeapon;

        private static bool CarriesMelee(Pawn p) =>
            (p.equipment?.Primary != null && p.equipment.Primary.def.IsMeleeWeapon) ||
            (p.inventory?.innerContainer != null && p.inventory.innerContainer.Any(t => t.def.IsMeleeWeapon));

        private static List<Pawn> Crew(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("pawn", out string who);
            List<Pawn> all = map.mapPawns.FreeColonistsSpawned.Where(p => !p.Downed).ToList();
            if (string.IsNullOrEmpty(who) || who.Equals("all", StringComparison.OrdinalIgnoreCase)) return all;
            var names = who.Split(',').Select(n => n.Trim()).Where(n => n.Length > 0).ToList();
            return all.Where(p => names.Any(n => p.LabelShort.Equals(n, StringComparison.OrdinalIgnoreCase))).ToList();
        }

        private static bool On(Dictionary<string, string> a) =>
            !a.TryGetValue("on", out string s) || s == null || !s.Trim().StartsWith("f", StringComparison.OrdinalIgnoreCase);

        // ---------------------------------------------------------------- arm

        public static string Arm(Map map)
        {
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned.Where(p => !p.Downed && !p.InMentalState &&
                p.WorkTagIsDisabled(WorkTags.Violent) == false).ToList();
            if (crew.Count == 0) return "refused: no colonist able to fight";
            var claimed = new HashSet<Thing>();
            var report = new List<string>();
            int unarmed = 0;

            foreach (Pawn p in crew.Where(p => !HasRanged(p)))
            {
                ThingWithComps gun = map.listerThings.ThingsInGroup(ThingRequestGroup.Weapon).OfType<ThingWithComps>()
                    .Where(t => t.def.IsRangedWeapon && !claimed.Contains(t) && !t.IsForbidden(p) &&
                                p.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some))
                    .OrderBy(t => t.Position.DistanceToSquared(p.Position)).FirstOrDefault();
                if (gun == null) { unarmed++; continue; }
                claimed.Add(gun);
                p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Equip, gun), JobTag.Misc);
                report.Add(p.LabelShort + " -> " + gun.LabelShort);
            }

            // Sidearms only for those already holding a gun: a pawn just ordered to equip keeps that job.
            foreach (Pawn p in crew.Where(p => HasRanged(p) && !CarriesMelee(p)))
            {
                ThingWithComps blade = map.listerThings.ThingsInGroup(ThingRequestGroup.Weapon).OfType<ThingWithComps>()
                    .Where(t => t.def.IsMeleeWeapon && !claimed.Contains(t) && !t.IsForbidden(p) &&
                                p.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some))
                    .OrderBy(t => t.Position.DistanceToSquared(p.Position)).FirstOrDefault();
                if (blade == null) continue;
                claimed.Add(blade);
                Job carry = JobMaker.MakeJob(JobDefOf.TakeInventory, blade);
                carry.count = 1;
                p.jobs.TryTakeOrderedJob(carry, JobTag.Misc);
                report.Add(p.LabelShort + " carries " + blade.LabelShort + " as a sidearm");
            }

            string craft = "";
            if (unarmed > 0)
            {
                // No gun left on the map for these: make the shortfall, on the first built table that can.
                foreach (string name in GunRecipes)
                {
                    RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(name);
                    if (recipe == null) continue;
                    Building_WorkTable table = map.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>()
                        .FirstOrDefault(t => t.def.AllRecipes.Contains(recipe));
                    if (table == null) continue;
                    if (table.BillStack.Bills.Any(b => b.recipe == recipe)) { craft = "; a " + recipe.label + " bill is already up"; break; }
                    var bill = new Bill_Production(recipe) { repeatMode = BillRepeatModeDefOf.RepeatCount, repeatCount = unarmed };
                    bill.allowedSkillRange = new IntRange(0, 20);
                    table.BillStack.AddBill(bill);
                    craft = "; " + unarmed + " still unarmed, so " + table.LabelShort + " at " + table.Position.x + "," +
                            table.Position.z + " makes " + unarmed + "x " + recipe.label;
                    break;
                }
                if (craft.Length == 0)
                    craft = "; " + unarmed + " still unarmed and no built table can make a gun or bow (build a crafting spot or machining table)";
            }

            if (report.Count == 0 && unarmed == 0) return "ok: everyone already carries a gun and a melee sidearm (or none is free)";
            return "ok: " + (report.Count == 0 ? "no free weapon moved" : string.Join("; ", report)) + craft;
        }

        // ---------------------------------------------------------------- draft

        public static string Draft(Map map, Dictionary<string, string> a)
        {
            List<Pawn> crew = Crew(map, a);
            if (crew.Count == 0) return "refused: no such colonist (pawn = all or names, comma separated)";
            bool on = On(a);
            var changed = new List<string>();
            foreach (Pawn p in crew)
            {
                if (p.drafter == null || p.Drafted == on) continue;
                p.drafter.Drafted = on;
                changed.Add(p.LabelShort);
            }
            return changed.Count == 0 ? "ok: already " + (on ? "drafted" : "released")
                                      : "ok: " + (on ? "drafted " : "released ") + string.Join(", ", changed);
        }

        // ---------------------------------------------------------------- hold

        public static string Hold(Map map)
        {
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned
                .Where(p => !p.Downed && !p.InMentalState && HasRanged(p) && p.drafter != null).ToList();
            if (crew.Count == 0) return "refused: nobody holds a gun -- arm first";

            // Where the threat is: the nearest hostile, else the nearest map edge to the colony (the approach).
            IntVec3 home = crew[0].Position;
            Pawn enemy = map.mapPawns.AllPawnsSpawned.Where(p => !p.Downed && p.HostileTo(Faction.OfPlayer))
                .OrderBy(p => p.Position.DistanceToSquared(home)).FirstOrDefault();
            IntVec3 threat = enemy != null ? enemy.Position : CellFinder.RandomEdgeCell(map);

            // Firing positions: a standable cell beside an embrasure, else beside sandbags / barricades, inside the base side.
            List<Thing> cover = map.listerBuildings.allBuildingsColonist.Cast<Thing>()
                .Where(b => b.def.defName.IndexOf("Embrasure", StringComparison.OrdinalIgnoreCase) >= 0).ToList();
            string coverKind = "embrasure";
            if (cover.Count == 0)
            {
                cover = map.listerBuildings.allBuildingsColonist.Cast<Thing>()
                    .Where(b => b.def.defName == "Sandbags" || b.def.defName == "Barricade").ToList();
                coverKind = "sandbag/barricade";
            }
            if (cover.Count == 0) return "refused: no embrasures, sandbags or barricades built -- build them toward the approach first";

            var spots = new List<IntVec3>();
            foreach (Thing c in cover.OrderBy(t => t.Position.DistanceToSquared(threat)))
            {
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 s = c.Position + d;
                    // the defender's side: farther from the threat than the cover itself
                    if (!s.InBounds(map) || !s.Standable(map) || s.DistanceToSquared(threat) <= c.Position.DistanceToSquared(threat)) continue;
                    if (spots.Contains(s)) continue;
                    spots.Add(s);
                    break;
                }
            }
            if (spots.Count == 0) return "refused: every " + coverKind + " is blocked on the base side";

            var sent = new List<string>();
            var taken = new HashSet<IntVec3>();
            foreach (Pawn p in crew)
            {
                List<IntVec3> open = spots.Where(s => !taken.Contains(s) && p.CanReach(s, PathEndMode.OnCell, Danger.Deadly))
                    .OrderBy(s => s.DistanceToSquared(p.Position)).ToList();
                if (open.Count == 0) continue;
                IntVec3 spot = open[0];
                taken.Add(spot);
                if (!p.Drafted) p.drafter.Drafted = true;
                p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, spot), JobTag.DraftedOrder);
                sent.Add(p.LabelShort + " -> " + spot.x + "," + spot.z);
            }
            return sent.Count == 0 ? "refused: no armed colonist can reach a " + coverKind + " position"
                : "ok: holding at " + coverKind + "s facing " + (enemy != null ? enemy.LabelShort + " at " + threat.x + "," + threat.z : "the map edge") +
                  ": " + string.Join("; ", sent) + (crew.Count > sent.Count ? " (" + (crew.Count - sent.Count) + " had no spot)" : "");
        }
    }
}
