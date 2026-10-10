using System;
using System.Collections.Generic;
using System.IO;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Sets up a new colony's world the way the owner always does it, with no mouse and no screen.
    ///
    /// Owner, verbatim: *"there is no wood no trees on this map, thats why in advanced setting on world gen setup
    /// you set 300x300 mapo and spring, and then when choosing a map tile u pic on that has mountains(the rock
    /// areas on map) in forest area and jungle areas the light green and green, terrain tab on left tells u all
    /// this when u highlight via select the tiles"* / *"and it didnt set up world generation correct"*.
    ///
    /// The automation component is a GameComponent, so it only ticks inside a running game; the starting-site
    /// page comes before that. This is a tiny Unity behaviour created once at startup that polls for one file,
    /// <c>RimroomsAutomation/setup.request</c>, and acts only while <see cref="Page_SelectStartingSite"/> is open:
    /// map size 300, starting season Spring, and the starting tile chosen from the world grid -- a valid
    /// settlement tile whose biome is temperate forest or tropical rainforest and whose hilliness is
    /// mountainous (large hills as the fallback). The result is written to <c>setup.result</c>. If the request
    /// file says <c>next</c>, it then calls the page's own Next (the page has no clickable button).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class WorldSetupDriverBootstrap
    {
        static WorldSetupDriverBootstrap()
        {
            var go = new GameObject("RimroomsWorldSetupDriver");
            UnityEngine.Object.DontDestroyOnLoad(go);
            go.AddComponent<WorldSetupDriver>();
        }
    }

    public sealed class WorldSetupDriver : MonoBehaviour
    {
        private const int MapSize = 300;
        private static readonly string[] Biomes = { "TemperateForest", "TropicalRainforest" };
        private float nextCheck;

        private static string Folder => Path.Combine(GenFilePaths.ConfigFolderPath, "RimroomsAutomation");

        public void Update()
        {
            if (Time.realtimeSinceStartup < nextCheck) { return; }
            nextCheck = Time.realtimeSinceStartup + 1f;
            string request = Path.Combine(Folder, "setup.request");
            try
            {
                if (!File.Exists(request)) { return; }
                if (Find.World == null || Find.GameInitData == null || Find.WindowStack == null ||
                    !Find.WindowStack.IsOpen<Page_SelectStartingSite>())
                {
                    return;
                }

                bool advance = File.ReadAllText(request).IndexOf("next", StringComparison.OrdinalIgnoreCase) >= 0;
                string result = Apply();
                if (advance && result.StartsWith("ok"))
                {
                    // the page draws into the world view, so it has no button the bridge can click: call its Next
                    Page_SelectStartingSite page = Find.WindowStack.WindowOfType<Page_SelectStartingSite>();
                    System.Reflection.MethodInfo next = typeof(Page).GetMethod("DoNext",
                        System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic |
                        System.Reflection.BindingFlags.Public);
                    if (page != null && next != null) { next.Invoke(page, null); result += " next=pressed"; }
                    else { result += " next=unavailable"; }
                }
                File.Delete(request);
                File.WriteAllText(Path.Combine(Folder, "setup.result"), result);
                Log.Message("[Rimrooms][Automation] world setup: " + result);
            }
            catch (Exception e)
            {
                try { File.WriteAllText(Path.Combine(Folder, "setup.result"), "error: " + e.Message); } catch { }
                Log.Warning("[Rimrooms][Automation] world setup failed: " + e.Message);
            }
        }

        private static string Apply()
        {
            Find.GameInitData.mapSize = MapSize;
            Find.GameInitData.startingSeason = Season.Spring;

            PlanetTile tile = PickTile(Hilliness.Mountainous);
            if (!tile.Valid) { tile = PickTile(Hilliness.LargeHills); }
            if (!tile.Valid) { return "refused: no forest or jungle tile with mountains or large hills"; }

            Find.GameInitData.startingTile = tile;
            Find.WorldInterface.SelectedTile = tile;
            Tile t = Find.WorldGrid[tile];
            return string.Format("ok map={0} season=Spring tile={1} biome={2} hilliness={3}",
                MapSize, tile.tileId, t.PrimaryBiome?.defName, t.hilliness);
        }

        private static PlanetTile PickTile(Hilliness wanted)
        {
            PlanetLayer surface = Find.WorldGrid.Surface;
            if (surface == null) { return PlanetTile.Invalid; }
            var found = new List<PlanetTile>();
            foreach (string biome in Biomes)
            {
                for (int i = 0; i < surface.TilesCount; i++)
                {
                    PlanetTile candidate = new PlanetTile(i, surface);
                    Tile t = Find.WorldGrid[candidate];
                    if (t.PrimaryBiome == null || t.PrimaryBiome.defName != biome || t.hilliness != wanted) { continue; }
                    if (Find.WorldObjects.AnyWorldObjectAt(candidate) || !TileFinder.IsValidTileForNewSettlement(candidate)) { continue; }
                    found.Add(candidate);
                }

                if (found.Count > 0) { return found.RandomElement(); }   // temperate forest first, jungle next
            }

            return PlanetTile.Invalid;
        }
    }
}
