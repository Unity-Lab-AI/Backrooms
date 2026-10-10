using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Drives RimWorld's new-game pages the way the owner sets up every colony -- no mouse, no screen.
    ///
    /// Owner, verbatim: *"there is no wood no trees on this map, thats why in advanced setting on world gen setup you
    /// set 300x300 mapo and spring, and then when choosing a map tile u pic on that has mountains(the rock areas on
    /// map) in forest area and jungle areas"* / *"not peace full you cheap skat community buiilder go back"* /
    /// *"YOU HAVE TO USE PROPER PROCEESURE ONLY HAVE NORMAL PIRATES REMOVE THAE STARTING 3 and add normal canibals
    /// and a nude tribe when u set it up"* / *"wtf it didnt do the fucking map set up with faction adv settings
    /// pollution seed name none of it"*. Pollution 0% and the seed and names are Unity's (owner: "unity decides",
    /// "she can make a name and name settlement and faction when it pops up").
    ///
    /// GameComponents only tick inside a running game, so this is a small Unity behaviour made once at startup.
    /// While <c>RimroomsAutomation/newgame.request</c> exists it looks at the top new-game page once a second and
    /// does that page's job directly on its fields, then advances it through the page's own CanDoNext/DoNext:
    ///   storyteller  Cassandra Classic, Community builder (Easy), reload anytime
    ///   world        seed from the request, pollution 0, factions: no pirate gang but the normal one, plus the
    ///                cannibal tribe and the nudist tribe, everything else as offered
    ///   site         map 300x300, Spring, a valid mountainous temperate forest tile (rainforest, then large
    ///                hills, as fallbacks)
    ///   company      the mod's own setup page: acknowledged, the company name from the request
    ///   naming       the settlement and faction naming dialog, filled with the request's names
    /// Every step is logged to <c>newgame.result</c>. The request is removed once the naming dialog is answered.
    /// The scenario page itself is left to the caller (start-scenario.py picks the scenario row).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class WorldSetupDriverBootstrap
    {
        static WorldSetupDriverBootstrap()
        {
            var go = new GameObject("RimroomsNewGameDriver");
            UnityEngine.Object.DontDestroyOnLoad(go);
            go.AddComponent<WorldSetupDriver>();
        }
    }

    public sealed class WorldSetupDriver : MonoBehaviour
    {
        private const int MapSize = 300;
        private const BindingFlags Any = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;
        private static readonly string[] PirateKeep = { "Pirate" };
        private static readonly string[] FactionsToAdd = { "TribeCannibal", "NudistTribe" };

        private float nextCheck;
        private readonly HashSet<int> handled = new HashSet<int>();
        private static DateTime requestStamp;
        private static bool crewLoaded;

        private static string Folder => Path.Combine(GenFilePaths.ConfigFolderPath, "RimroomsAutomation");
        private static string RequestPath => Path.Combine(Folder, "newgame.request");
        private static string ResultPath => Path.Combine(Folder, "newgame.result");

        private static void Report(string line)
        {
            try { File.AppendAllText(ResultPath, DateTime.Now.ToString("HH:mm:ss") + " " + line + Environment.NewLine); } catch { }
            Log.Message("[Rimrooms][NewGame] " + line);
        }

        private static Dictionary<string, string> Request()
        {
            var d = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (string raw in File.ReadAllLines(RequestPath))
            {
                int eq = raw.IndexOf('=');
                if (eq > 0) { d[raw.Substring(0, eq).Trim()] = raw.Substring(eq + 1).Trim(); }
            }
            return d;
        }

        public void Update()
        {
            if (Time.realtimeSinceStartup < nextCheck) { return; }
            nextCheck = Time.realtimeSinceStartup + 1f;
            // a paused game does not tick, so the command channel is served from here while paused
            try
            {
                if (Current.ProgramState == ProgramState.Playing && Find.TickManager != null && Find.TickManager.Paused)
                {
                    RimroomsAutomationComponent.ProcessInbox();
                }
            }
            catch (Exception e) { Log.Warning("[Rimrooms][Automation] paused inbox: " + e.Message); }
            try
            {
                if (!File.Exists(RequestPath) || Find.WindowStack == null || LongEventHandler.AnyEventNowOrWaiting) { return; }
                // a fresh request starts a fresh run: nothing is handled yet and no crew is loaded
                DateTime stamp = File.GetLastWriteTimeUtc(RequestPath);
                if (stamp != requestStamp) { requestStamp = stamp; handled.Clear(); crewLoaded = false; }
                // the ideology page can sit UNDER the others (it opens right after the scenario page); it is
                // handled first wherever it is, then the topmost unhandled page
                var open = Find.WindowStack.Windows.Where(w => (w is Page || w is Dialog_NamePlayerFactionAndSettlement)
                                                               && !handled.Contains(w.ID)).ToList();
                Window top = open.FirstOrDefault(w => w is Page_ChooseIdeoPreset) ?? open.LastOrDefault();
                if (top == null) { return; }
                Dictionary<string, string> req = Request();

                switch (top)
                {
                    case Page_SelectStoryteller p: Storyteller(p); break;
                    case Page_CreateWorldParams p: WorldParams(p, req); break;
                    case Page_SelectStartingSite p: Site(p); break;
                    case Dialog_NamePlayerFactionAndSettlement d: Names(d, req); return;
                    case Page p when p.GetType().Name == "Page_RimroomsCompanySetup": Company(p, req); break;
                    case Page_ChooseIdeoPreset p:
                        if (!LoadIdeo(p, req)) { nextCheck = Time.realtimeSinceStartup + 5f; return; }
                        break;
                    case Page_ConfigureStartingPawns p:
                        if (!OpenPrepareCarefully(p)) { nextCheck = Time.realtimeSinceStartup + 5f; return; }
                        break;
                    case Page p when p.GetType().Name == "PagePrepareCarefully":
                        if (!LoadPreset(p, req)) { nextCheck = Time.realtimeSinceStartup + 5f; return; }
                        break;
                    default: return;   // the scenario page and anything unknown are not ours
                }

                handled.Add(top.ID);
            }
            catch (Exception e)
            {
                Report("error: " + e.GetType().Name + ": " + e.Message);
                nextCheck = Time.realtimeSinceStartup + 5f;
            }
        }

        /// <summary>The page's own Next: CanDoNext validates (and on the world page starts generation), DoNext moves on.</summary>
        private static bool Advance(Page page, string what)
        {
            MethodInfo can = page.GetType().GetMethod("CanDoNext", Any);
            MethodInfo next = page.GetType().GetMethod("DoNext", Any);
            bool ok = can == null || (bool)can.Invoke(page, null);
            if (ok && next != null) { next.Invoke(page, null); }
            Report(what + (ok ? " -> next" : " -> CanDoNext refused (generation may have started)"));
            return ok;
        }

        private static void Storyteller(Page_SelectStoryteller p)
        {
            StorytellerDef teller = DefDatabase<StorytellerDef>.GetNamedSilentFail("Cassandra");
            DifficultyDef diff = DefDatabase<DifficultyDef>.GetNamedSilentFail("Easy");
            typeof(Page_SelectStoryteller).GetField("storyteller", Any)?.SetValue(p, teller);
            typeof(Page_SelectStoryteller).GetField("difficulty", Any)?.SetValue(p, diff);
            typeof(Page_SelectStoryteller).GetField("difficultyValues", Any)?.SetValue(p, new Difficulty(diff));
            Find.GameInitData.permadeathChosen = true;
            Find.GameInitData.permadeath = false;   // reload anytime
            Report("storyteller: Cassandra Classic, Community builder, reload anytime");
            Advance(p, "storyteller");
        }

        private static void WorldParams(Page_CreateWorldParams p, Dictionary<string, string> req)
        {
            Type t = typeof(Page_CreateWorldParams);
            if (req.TryGetValue("seed", out string seed) && !string.IsNullOrWhiteSpace(seed))
            {
                t.GetField("seedString", Any)?.SetValue(p, seed);
            }
            t.GetField("pollution", Any)?.SetValue(p, 0f);
            // owner: "30% aas ive taught u with allthe other settings also" -- coverage 30%, the rest Normal
            float coverage = 0.3f;
            if (req.TryGetValue("coverage", out string cov)) { float.TryParse(cov, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out coverage); }
            t.GetField("planetCoverage", Any)?.SetValue(p, coverage);
            foreach (string f in new[] { "rainfall", "temperature", "population" })
            {
                FieldInfo fi = t.GetField(f, Any);
                if (fi != null && fi.FieldType.IsEnum) { fi.SetValue(p, Enum.Parse(fi.FieldType, "Normal")); }
            }

            var factions = t.GetField("factions", Any)?.GetValue(p) as List<FactionDef>;
            if (factions != null)
            {
                int before = factions.Count;
                // Owner, verbatim: "one of each and only one red pirate guy no other red ones  just not all the tribe
                // just the fun ones". Hidden factions (mechanoids, insects, ancients...) stay -- the game needs them.
                // Every hostile (red) one goes except the normal pirates; tribes are only the cannibals and nudists
                // (added below); everything else keeps one faction per kind.
                var seenKind = new HashSet<string>();
                factions.RemoveAll(f =>
                {
                    if (f == null) return true;
                    if (f.hidden) return false;
                    if (PirateKeep.Contains(f.defName) || FactionsToAdd.Contains(f.defName)) return false;
                    if (f.permanentEnemy || f.naturalEnemy) return true;
                    if (f.defName.IndexOf("Tribe", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        f.categoryTag == "Tribal") return true;
                    string kind = string.IsNullOrEmpty(f.categoryTag) ? f.defName : f.categoryTag;
                    return !seenKind.Add(kind);
                });
                foreach (string name in PirateKeep.Concat(FactionsToAdd))
                {
                    FactionDef def = DefDatabase<FactionDef>.GetNamedSilentFail(name);
                    if (def != null && !factions.Contains(def)) { factions.Add(def); }
                }
                Report("world: seed=" + (seed ?? "(page's)") + " pollution=0 factions " + before + " -> " + factions.Count +
                       " [" + string.Join(", ", factions.Where(f => f != null).Select(f => f.defName)) + "]");
            }
            Advance(p, "world (generating)");
        }

        private static void Site(Page_SelectStartingSite p)
        {
            Find.GameInitData.mapSize = MapSize;
            Find.GameInitData.startingSeason = Season.Spring;
            PlanetTile tile = PickTile(new[] { "TemperateForest", "TropicalRainforest" }, Hilliness.Mountainous);
            if (!tile.Valid) { tile = PickTile(new[] { "TemperateForest", "TropicalRainforest" }, Hilliness.LargeHills); }
            if (!tile.Valid) { Report("site: refused -- no forest or jungle tile with mountains or large hills"); return; }
            Find.GameInitData.startingTile = tile;
            Find.WorldInterface.SelectedTile = tile;
            Tile t = Find.WorldGrid[tile];
            Report(string.Format("site: map {0}x{0}, Spring, tile {1} {2} {3}", MapSize, tile.tileId, t.PrimaryBiome?.defName, t.hilliness));
            Advance(p, "site");
        }

        private static void Company(Page p, Dictionary<string, string> req)
        {
            if (!crewLoaded && p.prev is Page_ConfigureStartingPawns && GenTypes.GetTypeInAnyAssembly("EdB.PrepareCarefully.Mod") != null)
            {
                // live: the company page came up before the crew page was handled and five default staff landed.
                // Back to the pawns page (the page's own Back), so the preset is loaded first.
                typeof(Page).GetMethod("DoBack", Any)?.Invoke(p, null);
                Report("company setup: crew not loaded yet -- back to the pawns page");
                return;
            }
            p.GetType().GetField("reviewed", Any)?.SetValue(p, true);
            if (req.TryGetValue("company", out string company) && !string.IsNullOrWhiteSpace(company))
            {
                FieldInfo buf = p.GetType().GetField("companyNameBuffer", Any);
                if (buf != null && buf.FieldType == typeof(string)) { buf.SetValue(p, company); }
            }
            // CanDoNext re-syncs roles and clears 'reviewed' when the roster changed, so acknowledge again after it
            MethodInfo can = p.GetType().GetMethod("CanDoNext", Any);
            bool ok = (bool)can.Invoke(p, null);
            if (!ok) { p.GetType().GetField("reviewed", Any)?.SetValue(p, true); ok = (bool)can.Invoke(p, null); }
            if (ok) { p.GetType().GetMethod("DoNext", Any)?.Invoke(p, null); }
            Report("company setup: acknowledged" + (ok ? " -> next" : " -> refused"));
        }

        private void Names(Dialog_NamePlayerFactionAndSettlement d, Dictionary<string, string> req)
        {
            req.TryGetValue("settlement", out string settlement);
            req.TryGetValue("faction", out string faction);
            Type t = typeof(Dialog_GiveName);
            if (string.IsNullOrWhiteSpace(faction)) { faction = (string)t.GetField("curName", Any).GetValue(d); }
            if (string.IsNullOrWhiteSpace(settlement)) { settlement = (string)t.GetField("curSecondName", Any).GetValue(d); }
            d.GetType().GetMethod("Named", Any).Invoke(d, new object[] { faction });
            d.GetType().GetMethod("NamedSecond", Any).Invoke(d, new object[] { settlement });
            d.Close();
            handled.Add(d.ID);
            Report("named: faction '" + faction + "', settlement '" + settlement + "' -- done");
            File.Delete(RequestPath);
        }

        /// <summary>Page.DoNext's base behaviour, without the page's own override (the ideology page overrides it).</summary>
        private static void BaseNext(Page page)
        {
            if (page.next != null) { Find.WindowStack.Add(page.next); }
            page.nextAct?.Invoke();
            page.Close(true);
        }

        /// <summary>The saved ideoligion, loaded exactly as the page's own Load button does (owner: "Godsmultiplayer").</summary>
        private static bool LoadIdeo(Page_ChooseIdeoPreset page, Dictionary<string, string> req)
        {
            if (!req.TryGetValue("ideo", out string name) || string.IsNullOrWhiteSpace(name)) { name = "Godsmultiplayer"; }
            string path = GenFilePaths.AbsPathForIdeo(name);
            if (!File.Exists(path)) { Report("ideology: no saved ideoligion '" + name + "' at " + path); return false; }
            if (!GameDataSaveLoader.TryLoadIdeo(path, out Ideo ideo) || ideo == null) { Report("ideology: '" + name + "' failed to load"); return false; }
            ideo = IdeoGenerator.InitLoadedIdeo(ideo);
            Find.IdeoManager.classicMode = false;
            typeof(Page_ChooseIdeoPreset).GetMethod("AssignIdeoToPlayer", Any).Invoke(page, new object[] { ideo });
            Find.IdeoManager.RemoveUnusedStartingIdeos();
            Find.Scenario.PostIdeoChosen();
            if (page.next != null) { page.next.prev = page; }
            BaseNext(page);
            Report("ideology: loaded '" + ideo.name + "' from " + name + " -> next");
            return true;
        }

        /// <summary>Opens Prepare Carefully on the pawns page, the way its own button does (owner: the crew comes from a preset).</summary>
        private static bool OpenPrepareCarefully(Page_ConfigureStartingPawns page)
        {
            Type mod = GenTypes.GetTypeInAnyAssembly("EdB.PrepareCarefully.Mod");
            object instance = mod?.GetProperty("Instance", BindingFlags.Static | BindingFlags.Public)?.GetValue(null);
            MethodInfo start = mod?.GetMethod("Start", Any);
            if (instance == null || start == null)
            {
                Report("crew: Prepare Carefully is not loaded -- advancing with the scenario's own crew");
                return Advance(page, page.GetType().Name);
            }
            start.Invoke(instance, new object[] { page });
            Report("crew: Prepare Carefully opened");
            return true;
        }

        /// <summary>Loads the saved preset into Prepare Carefully and starts, which hands on to the next page (owner: Preset3).</summary>
        private static bool LoadPreset(Page pcPage, Dictionary<string, string> req)
        {
            if (!req.TryGetValue("preset", out string preset) || string.IsNullOrWhiteSpace(preset)) { preset = "Preset3"; }
            object controller = pcPage.GetType().GetProperty("Controller", Any)?.GetValue(pcPage);
            if (controller == null) { Report("crew: Prepare Carefully has no controller yet"); return false; }
            controller.GetType().GetMethod("LoadPreset", Any).Invoke(controller, new object[] { preset });
            controller.GetType().GetMethod("StartGame", Any).Invoke(controller, null);
            pcPage.Close(false);
            crewLoaded = true;
            Report("crew: preset '" + preset + "' loaded -> start");
            return true;
        }

        private static PlanetTile PickTile(string[] biomes, Hilliness wanted)
        {
            PlanetLayer surface = Find.WorldGrid.Surface;
            if (surface == null) { return PlanetTile.Invalid; }
            // owner: pollution 0 -- also never settle within 6 tiles of a polluted tile (the game asks "acidic smog,
            // settle anyway?" and the setup stalls on it)
            var polluted = new List<PlanetTile>();
            for (int i = 0; i < surface.TilesCount; i++)
            {
                PlanetTile pt = new PlanetTile(i, surface);
                if (Find.WorldGrid[pt].pollution > 0f) polluted.Add(pt);
            }
            foreach (string biome in biomes)
            {
                var found = new List<PlanetTile>();
                for (int i = 0; i < surface.TilesCount; i++)
                {
                    PlanetTile candidate = new PlanetTile(i, surface);
                    Tile t = Find.WorldGrid[candidate];
                    if (t.PrimaryBiome == null || t.PrimaryBiome.defName != biome || t.hilliness != wanted) { continue; }
                    if (Find.WorldObjects.AnyWorldObjectAt(candidate) || !TileFinder.IsValidTileForNewSettlement(candidate)) { continue; }
                    if (polluted.Any(pt => Find.WorldGrid.ApproxDistanceInTiles(candidate, pt) < 6f)) { continue; }
                    found.Add(candidate);
                }
                if (found.Count > 0) { return found.RandomElement(); }
            }
            return PlanetTile.Invalid;
        }
    }
}
