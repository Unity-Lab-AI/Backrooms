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
    ///   {"cmd":"tower","x":"..","z":"..","size":"3"}  a roofed corner tower with embrasures outward, a base door and a sally port
    ///   {"cmd":"security_room","x":"..","z":".."}   the room off a tower for guns and medicine
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

        /// <summary>A weapon that is a weapon: not a wood log, a beer, a stone chunk or any other resource the game lets a pawn swing.</summary>
        private static bool RealWeapon(ThingDef d) =>
            d.IsWeapon && !d.IsStuff && !d.IsIngestible &&
            (d.thingCategories == null || !d.thingCategories.Any(c => c == ThingCategoryDefOf.ResourcesRaw || c.defName.StartsWith("Resources") || c.defName == "StoneChunks"));

        public static string Arm(Map map)
        {
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned.Where(p => !p.Downed && !p.InMentalState &&
                p.WorkTagIsDisabled(WorkTags.Violent) == false).ToList();
            if (crew.Count == 0) return "refused: no colonist able to fight";
            var claimed = new HashSet<Thing>();
            var report = new List<string>();
            int unarmed = 0;
            var noGun = new List<string>();      // armed with a melee weapon only: armed for now, a gun when one exists
            var bare = new List<string>();       // nothing in hand at all

            foreach (Pawn p in crew.Where(p => !HasRanged(p)))
            {
                // Run 5 (2026-10-13 23:20): the pod drop lands FORBIDDEN, so "no free ranged weapon on the map" with four guns
                // lying in the wreck (owner: "what happend to her guns did they not laod in"). A forbidden gun is a gun: it is
                // unforbidden the moment it is claimed.
                ThingWithComps gun = map.listerThings.ThingsInGroup(ThingRequestGroup.Weapon).OfType<ThingWithComps>()
                    .Where(t => t.def.IsRangedWeapon && RealWeapon(t.def) && !claimed.Contains(t) &&
                                p.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some))
                    .OrderBy(t => t.Position.DistanceToSquared(p.Position)).FirstOrDefault();
                if (gun == null)
                {
                    // run 3, 2026-10-13: "1 still unarmed" fourteen times for a colonist holding a knife, while the sensors
                    // read everyone armed -- name who and what, and count only an empty hand as unarmed
                    ThingWithComps held = p.equipment?.Primary;
                    if (held != null) noGun.Add(p.LabelShort + " holds " + held.LabelShort);
                    else { unarmed++; bare.Add(p.LabelShort); }
                    continue;
                }
                claimed.Add(gun);
                if (gun.IsForbidden(Faction.OfPlayer)) gun.SetForbidden(false);
                p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Equip, gun), JobTag.Misc);
                report.Add(p.LabelShort + " -> " + gun.LabelShort);
            }

            // Sidearms only for those already holding a gun: a pawn just ordered to equip keeps that job.
            foreach (Pawn p in crew.Where(p => HasRanged(p) && !CarriesMelee(p)))
            {
                ThingWithComps blade = map.listerThings.ThingsInGroup(ThingRequestGroup.Weapon).OfType<ThingWithComps>()
                    .Where(t => t.def.IsMeleeWeapon && RealWeapon(t.def) && !claimed.Contains(t) &&
                                p.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some))
                    .OrderBy(t => t.Position.DistanceToSquared(p.Position)).FirstOrDefault();
                if (blade == null) continue;
                claimed.Add(blade);
                if (blade.IsForbidden(Faction.OfPlayer)) blade.SetForbidden(false);
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
                    craft = "; " + unarmed + " with NO weapon (" + string.Join(", ", bare) + ") and no free gun and no built table that makes one -- game_set cmd build def CraftingSpot x z (a short bow), or trade";
            }
            string melee = noGun.Count == 0 ? "" : "; melee only, armed for now (no free gun): " + string.Join(", ", noGun) +
                           " -- a gun when a crafting spot (def CraftingSpot) makes a bow or a trader sells one";

            if (report.Count == 0 && unarmed == 0 && noGun.Count == 0) return "ok: everyone already carries a gun and a melee sidearm (or none is free)";
            return "ok: " + (report.Count == 0 ? "no free weapon moved" : string.Join("; ", report)) + melee + craft;
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

        // ---------------------------------------------------------------- tower

        /// <summary>
        /// PLAYBOOK 9, owner verbatim: "yopu need towers on all corrner that you can shhot out from with seperate
        /// ventalizatyion and added rooms for security stuff and embrassure sally ports". One call, one tower:
        ///   {"cmd":"tower","x":"120","z":"136","size":"3","stuff":"BlocksGranite"}
        /// The interior (size x size) grows from the given corner AWAY from the colony, so the tower stands proud of the
        /// perimeter. The two outward faces get embrasures on alternate cells and one sally-port door; the inward face gets
        /// the door back into the base; the roof is marked. Ventilation is a separate build (a cooler/vent in its own wall).
        /// </summary>
        public static string Tower(Map map, Dictionary<string, string> a)
        {
            int Int(string k, int d) => a.TryGetValue(k, out string s) && int.TryParse(s, out int v) ? v : d;
            IntVec3 corner = new IntVec3(Int("x", -1), 0, Int("z", -1));
            if (!corner.InBounds(map)) return "refused: x,z (the perimeter corner) outside the map";
            int size = Math.Max(2, Math.Min(6, Int("size", 3)));
            ThingDef embrasure = DefDatabase<ThingDef>.GetNamedSilentFail("Embrasure");
            a.TryGetValue("stuff", out string sn);
            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(sn ?? "") ?? ThingDefOf.WoodLog;

            // The colony's centre: the Home area's mean cell, else the colonists'.
            List<IntVec3> homeCells = map.areaManager.Home.ActiveCells.ToList();
            IntVec3 centre = homeCells.Count > 0
                ? new IntVec3((int)homeCells.Average(c => c.x), 0, (int)homeCells.Average(c => c.z))
                : (map.mapPawns.FreeColonistsSpawned.FirstOrDefault()?.Position ?? map.Center);
            int sx = corner.x >= centre.x ? 1 : -1, sz = corner.z >= centre.z ? 1 : -1;   // outward from the colony

            // interior cells: from the corner, outward on both axes
            int x0 = sx > 0 ? corner.x : corner.x - size + 1, z0 = sz > 0 ? corner.z : corner.z - size + 1;
            int x1 = x0 + size - 1, z1 = z0 + size - 1;
            // outward faces are the ring's x = x1+1 (sx>0) or x0-1, and z = z1+1 (sz>0) or z0-1
            int outX = sx > 0 ? x1 + 1 : x0 - 1, outZ = sz > 0 ? z1 + 1 : z0 - 1;
            int inX = sx > 0 ? x0 - 1 : x1 + 1, inZ = sz > 0 ? z0 - 1 : z1 + 1;
            IntVec3 homeDoor = new IntVec3((x0 + x1) / 2, 0, inZ);                    // back into the base
            IntVec3 sally = new IntVec3(outX, 0, (z0 + z1) / 2);                      // out through the side face

            int walls = 0, ports = 0, doors = 0, kept = 0, blocked = 0;
            for (int x = x0 - 1; x <= x1 + 1; x++)
                for (int z = z0 - 1; z <= z1 + 1; z++)
                {
                    bool ring = x == x0 - 1 || x == x1 + 1 || z == z0 - 1 || z == z1 + 1;
                    if (!ring) continue;
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map)) { blocked++; continue; }
                    Building ed = c.GetEdifice(map);
                    if (ed != null && (ed.def.passability == Traversability.Impassable || ed is Building_Door)) { kept++; continue; }
                    bool cornerCell = (x == x0 - 1 || x == x1 + 1) && (z == z0 - 1 || z == z1 + 1);
                    bool outward = !cornerCell && (x == outX || z == outZ);
                    ThingDef def; ThingDef useStuff = stuff;
                    if (c == homeDoor || c == sally) def = ThingDefOf.Door;
                    else if (outward && embrasure != null && ((x + z) & 1) == 0)
                    { def = embrasure; useStuff = embrasure.MadeFromStuff ? stuff : null; }
                    else def = ThingDefOf.Wall;
                    if (!GenConstruct.CanPlaceBlueprintAt(def, c, Rot4.North, map, false, null, null, useStuff).Accepted) { blocked++; continue; }
                    GenConstruct.PlaceBlueprintForBuild(def, c, map, Rot4.North, Faction.OfPlayer, useStuff);
                    if (def == ThingDefOf.Door) doors++; else if (def == embrasure) ports++; else walls++;
                }
            for (int x = x0; x <= x1; x++)
                for (int z = z0; z <= z1; z++)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (c.InBounds(map)) map.areaManager.BuildRoof[c] = true;
                }
            return (walls + ports + doors == 0 && kept == 0 ? "refused: " : "ok: ") + "tower " + size + "x" + size + " at " + x0 + "," + z0 +
                   "-" + x1 + "," + z1 + ": " + ports + " embrasures, " + walls + " walls, " + doors + " doors (base " + homeDoor.x + "," +
                   homeDoor.z + ", sally port " + sally.x + "," + sally.z + "), " + kept + " kept, " + blocked + " blocked; roof marked" +
                   (embrasure == null ? " -- no Embrasure def, walls only" : "") +
                   " -- its own ventilation is a separate build: freezer-style cooler or a vent in a tower wall";
        }

        /// <summary>
        /// PLAYBOOK 9: "added rooms for security stuff" off each tower (armory, guard room, med kit). Same corner as the
        /// tower; the room (w x h inside, default 4 x 3) sits on the colony side of the tower's base door so the door opens
        /// into it, walls and a door back into the base, roof marked:
        ///   {"cmd":"security_room","x":"120","z":"136","size":"3","w":"4","h":"3","stuff":"BlocksGranite"}
        /// </summary>
        public static string SecurityRoom(Map map, Dictionary<string, string> a)
        {
            int Int(string k, int d) => a.TryGetValue(k, out string s) && int.TryParse(s, out int v) ? v : d;
            IntVec3 corner = new IntVec3(Int("x", -1), 0, Int("z", -1));
            if (!corner.InBounds(map)) return "refused: x,z (the tower's perimeter corner) outside the map";
            int size = Math.Max(2, Math.Min(6, Int("size", 3)));
            int w = Math.Max(2, Math.Min(8, Int("w", 4))), h = Math.Max(2, Math.Min(8, Int("h", 3)));
            a.TryGetValue("stuff", out string sn);
            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(sn ?? "") ?? ThingDefOf.WoodLog;

            // The tower's geometry, exactly as Tower derives it.
            List<IntVec3> homeCells = map.areaManager.Home.ActiveCells.ToList();
            IntVec3 centre = homeCells.Count > 0
                ? new IntVec3((int)homeCells.Average(c => c.x), 0, (int)homeCells.Average(c => c.z))
                : (map.mapPawns.FreeColonistsSpawned.FirstOrDefault()?.Position ?? map.Center);
            int sx = corner.x >= centre.x ? 1 : -1, sz = corner.z >= centre.z ? 1 : -1;
            int x0 = sx > 0 ? corner.x : corner.x - size + 1, z0 = sz > 0 ? corner.z : corner.z - size + 1;
            int x1 = x0 + size - 1, z1 = z0 + size - 1;
            int inZ = sz > 0 ? z0 - 1 : z1 + 1;                         // the tower's inward wall line, holding its base door
            int doorX = (x0 + x1) / 2;

            // The room's interior: centred on the tower's base door, beyond the tower wall toward the colony.
            int rx0 = doorX - w / 2, rx1 = rx0 + w - 1;
            int rz0 = sz > 0 ? inZ - h : inZ + 1, rz1 = rz0 + h - 1;
            IntVec3 baseDoor = new IntVec3((rx0 + rx1) / 2, 0, sz > 0 ? rz0 - 1 : rz1 + 1);   // the far side, into the base

            int walls = 0, doors = 0, kept = 0, blocked = 0;
            for (int x = rx0 - 1; x <= rx1 + 1; x++)
                for (int z = rz0 - 1; z <= rz1 + 1; z++)
                {
                    bool ring = x == rx0 - 1 || x == rx1 + 1 || z == rz0 - 1 || z == rz1 + 1;
                    if (!ring) continue;
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map)) { blocked++; continue; }
                    Building ed = c.GetEdifice(map);
                    // the tower's own wall and door are shared, never doubled
                    if (ed != null && (ed.def.passability == Traversability.Impassable || ed is Building_Door)) { kept++; continue; }
                    if (c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) { kept++; continue; }
                    ThingDef def = c == baseDoor ? ThingDefOf.Door : ThingDefOf.Wall;
                    if (!GenConstruct.CanPlaceBlueprintAt(def, c, Rot4.North, map, false, null, null, stuff).Accepted) { blocked++; continue; }
                    GenConstruct.PlaceBlueprintForBuild(def, c, map, Rot4.North, Faction.OfPlayer, stuff);
                    if (def == ThingDefOf.Door) doors++; else walls++;
                }
            for (int x = rx0; x <= rx1; x++)
                for (int z = rz0; z <= rz1; z++)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (c.InBounds(map)) map.areaManager.BuildRoof[c] = true;
                }
            return (walls + doors == 0 && kept == 0 ? "refused: " : "ok: ") + "security room " + w + "x" + h + " at " + rx0 + "," + rz0 +
                   "-" + rx1 + "," + rz1 + " off the tower at " + corner.x + "," + corner.z + ": " + walls + " walls, " + doors +
                   " door (into the base at " + baseDoor.x + "," + baseDoor.z + "), " + kept + " shared/kept, " + blocked + " blocked; roof marked" +
                   " -- stock it: a shelf of guns and medicine (stockpile_room) and a bed for the guard";
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
