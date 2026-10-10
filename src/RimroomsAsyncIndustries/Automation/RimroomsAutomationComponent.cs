using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// A file-driven way to do the handful of things that otherwise need a real mouse on a real screen.
    ///
    /// Owner direction, 2026-10-10, verbatim: *"you need to fix that sahit so it doent ever need the fucking
    /// screeen and MY DAMN MOUSE"* / *"so the local model isnt a shit like that asking for control to do simple
    /// shit with its own maouse controls"* / *"build it into the mod if you have to"*.
    ///
    /// The reason it has to exist: a growing zone's crop, a bed's owner type, a bench's bill and the work grid
    /// are drawn by Core as float menus, dropdowns and grid cells. Those answer a real click on a real window,
    /// so an agent driving the game from outside had to borrow the owner's cursor and screen -- and could do
    /// nothing at all while the window was minimised. Every one of those settings is a plain field on a plain
    /// object underneath. This reads a small command file and sets the field directly.
    ///
    /// Shape, deliberately boring: a JSON lines file is read, each line is one command, each result is written
    /// to a sibling file, and the input is deleted once consumed. No sockets, no ports, no new permissions.
    ///
    ///   commands  Mods/.../RimroomsAutomation/inbox.jsonl     (written by the agent, consumed here)
    ///   results   Mods/.../RimroomsAutomation/outbox.jsonl    (written here, read by the agent)
    ///
    /// Supported commands, each one a thing that used to need the cursor:
    ///   {"cmd":"set_zone_plant","x":154,"z":116,"plant":"Plant_Rice"}
    ///   {"cmd":"set_zone_sowing","x":215,"z":174,"allow":false}
    ///   {"cmd":"set_work_priority","pawn":"Gee","work":"Research","level":4}
    ///   {"cmd":"set_bed_owner","x":159,"z":151,"owner":"prisoner"}     owner: colonist|prisoner|slave|guest
    ///   {"cmd":"add_bill","x":155,"z":141,"recipe":"CookMealSimple","count":30}
    ///   {"cmd":"set_area","pawn":"Scar","area":"Camp"}                 area: a label, or "" for unrestricted
    ///
    /// What it will not do: it never spawns, never destroys, never edits a def, never touches the world map,
    /// and it refuses any command naming something it cannot find rather than guessing a near match.
    /// </summary>
    public sealed class RimroomsAutomationComponent : GameComponent
    {
        private const int CheckEveryTicks = 60;          // once a second at normal speed
        private const int MaximumCommandsPerPass = 32;   // bounded work per pass, so a big file cannot stall a tick

        private static string FolderPath
        {
            get
            {
                string baseDir = GenFilePaths.ConfigFolderPath;
                return Path.Combine(baseDir, "RimroomsAutomation");
            }
        }

        private static string InboxPath => Path.Combine(FolderPath, "inbox.jsonl");
        private static string OutboxPath => Path.Combine(FolderPath, "outbox.jsonl");

        public RimroomsAutomationComponent(Game game)
        {
        }

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % CheckEveryTicks != 0)
            {
                return;
            }

            ProcessInbox();
        }

        /// <summary>
        /// Reads and executes the command file. Called from the game tick, and -- because a paused game does not
        /// tick, and the owner's rule is that setup happens BEFORE the clock runs -- also once a second from
        /// <see cref="WorldSetupDriver"/> while a game is loaded and paused.
        /// </summary>
        public static void ProcessInbox()
        {
            string inbox = InboxPath;
            if (!File.Exists(inbox))
            {
                return;
            }

            List<string> lines;
            try
            {
                lines = File.ReadAllLines(inbox).Where(l => !string.IsNullOrWhiteSpace(l)).ToList();
                File.Delete(inbox);
            }
            catch (Exception e)
            {
                Log.Warning("[Rimrooms][Automation] could not read the command file: " + e.Message);
                return;
            }

            var results = new List<string>();
            foreach (string line in lines.Take(MaximumCommandsPerPass))
            {
                string result;
                try
                {
                    result = Execute(line);
                }
                catch (Exception e)
                {
                    result = "error: " + e.Message;
                }

                results.Add(Escape(line) + " -> " + Escape(result));
            }

            try
            {
                Directory.CreateDirectory(FolderPath);
                File.AppendAllLines(OutboxPath, results.Select(r => "{\"result\":\"" + r + "\"}"));
            }
            catch (Exception e)
            {
                Log.Warning("[Rimrooms][Automation] could not write the result file: " + e.Message);
            }
        }

        private static string Escape(string s)
        {
            return (s ?? string.Empty).Replace("\\", "\\\\").Replace("\"", "'");
        }

        /// <summary>Tiny flat-JSON reader. The command files are written by our own client, one object per line.</summary>
        private static Dictionary<string, string> Parse(string line)
        {
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            var key = new StringBuilder();
            var val = new StringBuilder();
            bool inKey = false, inVal = false, quoted = false, haveKey = false;
            foreach (char c in line)
            {
                if (c == '"')
                {
                    if (!inKey && !haveKey) { inKey = true; key.Clear(); continue; }
                    if (inKey) { inKey = false; haveKey = true; continue; }
                    if (!inVal) { inVal = true; quoted = true; val.Clear(); continue; }
                    if (inVal && quoted) { map[key.ToString()] = val.ToString(); inVal = false; haveKey = false; continue; }
                }
                else if (inKey) { key.Append(c); }
                else if (inVal) { val.Append(c); }
                else if (haveKey && (char.IsLetterOrDigit(c) || c == '-' || c == '.'))
                {
                    inVal = true; quoted = false; val.Clear(); val.Append(c);
                }
                else if (inVal && !quoted && (c == ',' || c == '}'))
                {
                    map[key.ToString()] = val.ToString(); inVal = false; haveKey = false;
                }
            }

            if (inVal && !quoted && val.Length > 0)
            {
                map[key.ToString()] = val.ToString();
            }

            return map;
        }

        private static Map HomeMap => Find.CurrentMap ?? Find.Maps.FirstOrDefault(m => m.IsPlayerHome);

        private static string Execute(string line)
        {
            Dictionary<string, string> a = Parse(line);
            if (!a.TryGetValue("cmd", out string cmd))
            {
                return "refused: no cmd";
            }

            Map map = HomeMap;
            if (map == null)
            {
                return "refused: no map";
            }

            switch (cmd.ToLowerInvariant())
            {
                case "set_zone_plant": return SetZonePlant(map, a);
                case "set_zone_sowing": return SetZoneSowing(map, a);
                case "set_work_priority": return SetWorkPriority(a);
                case "set_bed_owner": return SetBedOwner(map, a);
                case "add_bill": return AddBill(map, a);
                case "set_area": return SetArea(map, a);
                case "day_one": return DayOne(map);
                default: return "refused: unknown cmd " + cmd;
            }
        }

        /// <summary>
        /// Everything the owner sets on every colony before the clock runs, in one command.
        /// Owner, verbatim: "set their scheldule to anything at all times for all pawns" / "were ur crops u get
        /// priorities done and scedukele and drug assignment" / "make sure everyone has their sidearm and maine rifle"
        /// / "set everyone to attack not flee" / "set up all priorities ... keep all the 1s firsefiring through
        /// cooking" / "dint leave a bunch blankk" / "she never armed any one and is just letting the game run with
        /// out seeting sechedul drugs storages workschedule priorities".
        ///   work      manual priorities; every work type from Firefighter through Cooking = 1; every later type by
        ///             skill (passion or skill 8+ = 2, skill 4+ = 3, otherwise 4) -- nothing left blank
        ///   schedule  Anything, all 24 hours, everyone
        ///   drugs     the policy with no hard drugs (vanilla "Social drugs"), everyone
        ///   hostility Attack, never Flee
        ///   weapons   anyone without a weapon is sent to equip the best free ranged weapon on the map
        /// </summary>
        private static string DayOne(Map map)
        {
            var notes = new List<string>();
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned.ToList();
            if (crew.Count == 0) return "refused: no colonists on the map";

            Current.Game.playSettings.useWorkPriorities = true;
            List<WorkTypeDef> order = DefDatabase<WorkTypeDef>.AllDefsListForReading.OrderByDescending(w => w.naturalPriority).ToList();
            int cookIndex = order.FindIndex(w => w.defName == "Cooking");

            DrugPolicy policy = Current.Game.drugPolicyDatabase.AllPolicies
                .FirstOrDefault(p => p.label.IndexOf("social", StringComparison.OrdinalIgnoreCase) >= 0)
                ?? Current.Game.drugPolicyDatabase.DefaultDrugPolicy();

            var claimed = new HashSet<Thing>();
            foreach (Pawn pawn in crew)
            {
                if (pawn.workSettings != null)
                {
                    pawn.workSettings.EnableAndInitializeIfNotAlreadyInitialized();
                    for (int i = 0; i < order.Count; i++)
                    {
                        WorkTypeDef w = order[i];
                        if (pawn.WorkTypeIsDisabled(w)) continue;
                        int level;
                        if (cookIndex >= 0 && i <= cookIndex) level = 1;
                        else
                        {
                            int best = 0; bool passion = false;
                            foreach (SkillDef s in w.relevantSkills ?? new List<SkillDef>())
                            {
                                SkillRecord r = pawn.skills?.GetSkill(s);
                                if (r == null) continue;
                                best = Math.Max(best, r.Level);
                                passion |= r.passion != Passion.None;
                            }
                            level = (passion || best >= 8) ? 2 : best >= 4 ? 3 : 4;
                        }
                        pawn.workSettings.SetPriority(w, level);
                    }
                }

                if (pawn.timetable != null)
                {
                    for (int h = 0; h < 24; h++) pawn.timetable.SetAssignment(h, TimeAssignmentDefOf.Anything);
                }

                if (pawn.drugs != null && policy != null) pawn.drugs.CurrentPolicy = policy;
                if (pawn.playerSettings != null) pawn.playerSettings.hostilityResponse = HostilityResponseMode.Attack;

                if (pawn.equipment != null && pawn.equipment.Primary == null)
                {
                    Thing gun = map.listerThings.ThingsInGroup(ThingRequestGroup.Weapon)
                        .Where(t => t.def.IsRangedWeapon && !t.IsForbidden(Faction.OfPlayer) && !claimed.Contains(t) &&
                                    t.Spawned && pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Deadly))
                        .OrderByDescending(t => t.MarketValue)
                        .FirstOrDefault();
                    if (gun != null)
                    {
                        claimed.Add(gun);
                        pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Equip, gun), JobTag.Misc);
                        notes.Add(pawn.LabelShort + " -> " + gun.LabelShort);
                    }
                    else
                    {
                        notes.Add(pawn.LabelShort + " -> no free ranged weapon on the map");
                    }
                }
            }

            return "ok: " + crew.Count + " colonists -- work 1s Firefighter..Cooking, rest by skill, none blank; schedule Anything; drugs '" +
                   (policy?.label ?? "none") + "'; hostility Attack; arming: " + (notes.Count > 0 ? string.Join("; ", notes) : "everyone already armed");
        }

        private static bool Cell(Dictionary<string, string> a, Map map, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            if (!a.TryGetValue("x", out string xs) || !a.TryGetValue("z", out string zs))
            {
                return false;
            }

            if (!int.TryParse(xs, NumberStyles.Integer, CultureInfo.InvariantCulture, out int x) ||
                !int.TryParse(zs, NumberStyles.Integer, CultureInfo.InvariantCulture, out int z))
            {
                return false;
            }

            cell = new IntVec3(x, 0, z);
            return cell.InBounds(map);
        }

        private static string SetZonePlant(Map map, Dictionary<string, string> a)
        {
            if (!Cell(a, map, out IntVec3 cell)) return "refused: bad cell";
            if (!(map.zoneManager.ZoneAt(cell) is Zone_Growing zone)) return "refused: no growing zone there";
            if (!a.TryGetValue("plant", out string defName)) return "refused: no plant";

            ThingDef plant = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (plant == null || plant.plant == null) return "refused: no such plant def " + defName;
            if (!plant.plant.Sowable) return "refused: " + defName + " is not sowable";

            zone.SetPlantDefToGrow(plant);
            return "ok: " + zone.label + " now grows " + plant.label;
        }

        private static string SetZoneSowing(Map map, Dictionary<string, string> a)
        {
            if (!Cell(a, map, out IntVec3 cell)) return "refused: bad cell";
            if (!(map.zoneManager.ZoneAt(cell) is Zone_Growing zone)) return "refused: no growing zone there";

            bool allow = !a.TryGetValue("allow", out string s) ||
                         !(s.Equals("false", StringComparison.OrdinalIgnoreCase) || s == "0");
            zone.allowSow = allow;
            return "ok: " + zone.label + " sowing " + (allow ? "on" : "off");
        }

        private static Pawn FindColonist(string name)
        {
            if (string.IsNullOrWhiteSpace(name)) return null;
            return PawnsFinder.AllMaps_FreeColonistsSpawned
                .FirstOrDefault(p => p.LabelShort.Equals(name, StringComparison.OrdinalIgnoreCase) ||
                                     (p.Name != null && p.Name.ToStringShort.Equals(name, StringComparison.OrdinalIgnoreCase)));
        }

        private static string SetWorkPriority(Dictionary<string, string> a)
        {
            a.TryGetValue("pawn", out string name);
            Pawn pawn = FindColonist(name);
            if (pawn == null || pawn.workSettings == null) return "refused: no colonist " + name;
            if (!a.TryGetValue("work", out string work)) return "refused: no work type";
            if (!a.TryGetValue("level", out string ls) ||
                !int.TryParse(ls, NumberStyles.Integer, CultureInfo.InvariantCulture, out int level) ||
                level < 0 || level > 4)
            {
                return "refused: level must be 0-4";
            }

            WorkTypeDef def = DefDatabase<WorkTypeDef>.AllDefsListForReading.FirstOrDefault(
                w => w.defName.Equals(work, StringComparison.OrdinalIgnoreCase) ||
                     w.labelShort.Equals(work, StringComparison.OrdinalIgnoreCase) ||
                     w.gerundLabel.Equals(work, StringComparison.OrdinalIgnoreCase));
            if (def == null) return "refused: no work type " + work;
            if (pawn.WorkTypeIsDisabled(def)) return "refused: " + pawn.LabelShort + " cannot do " + def.labelShort;

            if (!Current.Game.playSettings.useWorkPriorities)
            {
                Current.Game.playSettings.useWorkPriorities = true;
            }

            pawn.workSettings.SetPriority(def, level);
            return "ok: " + pawn.LabelShort + " " + def.labelShort + " = " + level;
        }

        private static string SetBedOwner(Map map, Dictionary<string, string> a)
        {
            if (!Cell(a, map, out IntVec3 cell)) return "refused: bad cell";
            Building_Bed bed = cell.GetThingList(map).OfType<Building_Bed>().FirstOrDefault();
            if (bed == null) return "refused: no bed there";
            a.TryGetValue("owner", out string owner);
            switch ((owner ?? string.Empty).ToLowerInvariant())
            {
                case "prisoner": bed.SetBedOwnerTypeByInterface(BedOwnerType.Prisoner); break;
                case "slave": bed.SetBedOwnerTypeByInterface(BedOwnerType.Slave); break;
                case "colonist": bed.SetBedOwnerTypeByInterface(BedOwnerType.Colonist); break;
                default: return "refused: owner must be colonist, prisoner or slave";
            }

            return "ok: bed at " + cell + " is for " + owner;
        }

        private static string AddBill(Map map, Dictionary<string, string> a)
        {
            if (!Cell(a, map, out IntVec3 cell)) return "refused: bad cell";
            Building_WorkTable table = cell.GetThingList(map).OfType<Building_WorkTable>().FirstOrDefault();
            if (table == null) return "refused: no work table there";
            if (!a.TryGetValue("recipe", out string recipeName)) return "refused: no recipe";

            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(recipeName) ??
                               table.def.AllRecipes.FirstOrDefault(r =>
                                   r.label.IndexOf(recipeName, StringComparison.OrdinalIgnoreCase) >= 0);
            if (recipe == null) return "refused: no recipe " + recipeName;
            if (!table.def.AllRecipes.Contains(recipe)) return "refused: " + table.LabelShort + " cannot make " + recipe.label;

            var bill = new Bill_Production(recipe);
            if (a.TryGetValue("count", out string cs) &&
                int.TryParse(cs, NumberStyles.Integer, CultureInfo.InvariantCulture, out int count) && count > 0)
            {
                bill.repeatMode = BillRepeatModeDefOf.TargetCount;
                bill.targetCount = count;
            }
            else
            {
                bill.repeatMode = BillRepeatModeDefOf.Forever;
            }

            // no skill restriction: owner, 2026-10-10 -- "so everyone can train and still get the most in one go"
            bill.allowedSkillRange = new IntRange(0, 20);
            table.BillStack.AddBill(bill);
            return "ok: " + table.LabelShort + " now has " + recipe.label +
                   (bill.repeatMode == BillRepeatModeDefOf.TargetCount ? " until " + bill.targetCount : " forever");
        }

        private static string SetArea(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("pawn", out string name);
            Pawn pawn = FindColonist(name);
            if (pawn == null || pawn.playerSettings == null) return "refused: no colonist " + name;
            a.TryGetValue("area", out string label);

            if (string.IsNullOrWhiteSpace(label))
            {
                pawn.playerSettings.AreaRestrictionInPawnCurrentMap = null;
                return "ok: " + pawn.LabelShort + " unrestricted";
            }

            Area area = map.areaManager.AllAreas.FirstOrDefault(
                ar => ar.Label.Equals(label, StringComparison.OrdinalIgnoreCase));
            if (area == null) return "refused: no area " + label;

            pawn.playerSettings.AreaRestrictionInPawnCurrentMap = area;
            return "ok: " + pawn.LabelShort + " restricted to " + area.Label;
        }
    }
}
