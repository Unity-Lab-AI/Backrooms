using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// What a coordinate looks like, chosen by how deep it sits.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"we can use the floor lights i guess for the
    /// yellow carpet and yellow wood walls for the main backrooms look as we dont have over head
    /// florrecent lights unless we could repurpose floor lights correctly"*, and immediately
    /// after: *"andf remmeber thats just the main backrooms looks further in it gets very varied
    /// and weird"*.
    ///
    /// That second sentence is the one that shaped this file. A single global palette could
    /// only ever deliver the first half of the direction, so the look is a **function of
    /// depth**: depth 1 is the canonical yellow rooms, and every step inward diverges.
    ///
    /// ## The overhead light problem, solved with a Core def rather than a compromise
    ///
    /// The owner reached for floor lights because the Backrooms wants overhead fluorescents and
    /// assumed the game had none. **Core ships `WallLamp`** — it mounts on a wall instead of
    /// standing on the floor, which is both closer to the intended look and better for the
    /// aesthetic in a second way: an endless corridor reads as endless precisely because
    /// nothing is standing in it. `StandingLamp` was what generation used before, and it put
    /// furniture in the middle of every room.
    ///
    /// ## Yellow, from Core, with no new asset
    ///
    /// * **Floor** — Core's `Carpet`, whose own description says it is *"dyed a single
    ///   color"*. `TerrainGrid.colorGrid` is a public field, so the colour is set directly
    ///   after `SetTerrain` with no Harmony and no new terrain def.
    /// * **Walls** — Core `Wall` built from `WoodLog`, tinted through `CompColorable`, which
    ///   generation already used for its grey and tan rooms.
    ///
    /// **No new texture, no new terrain, no new building.** The whole look is Core content
    /// wearing a colour.
    /// </summary>
    public static class BackroomsPalette
    {
        /// <summary>The Backrooms yellow. Sickly mustard rather than a clean primary.</summary>
        private static readonly Color MonoYellow = new Color(0.79f, 0.72f, 0.36f);

        /// <summary>One coordinate's look.</summary>
        public struct Look
        {
            /// <summary>Floor under rooms and corridors.</summary>
            public TerrainDef floor;

            /// <summary>Accent floor used for the stripe pattern, for a readable non-colour cue.</summary>
            public TerrainDef accent;

            /// <summary>Colour applied to the floor, or null to leave the terrain's own colour.</summary>
            public ColorDef floorColor;

            /// <summary>What walls are built from.</summary>
            public ThingDef wallStuff;

            /// <summary>Colour applied to walls.</summary>
            public Color wallColor;

            /// <summary>The light fixture used throughout.</summary>
            public ThingDef light;

            /// <summary>A short, translatable name for this band, shown on the coordinate.</summary>
            public string nameKey;
        }

        /// <summary>
        /// How many distinct bands exist before the pattern repeats with a different seed roll.
        /// Deliberately small: the variation deeper down should come from **what is in a room**
        /// rather than from an ever-growing list of paint schemes, and a palette that never
        /// repeats stops reading as a place at all.
        /// </summary>
        public const int Bands = 5;

        /// <summary>
        /// The look for a coordinate at a given depth.
        ///
        /// Depth 1 is fixed and never rolls: **the first space a player ever sees must be the
        /// yellow rooms**, every time, on every seed. It is the image the whole setting rests on
        /// and a random alternative there would be a worse game for the sake of variety.
        ///
        /// Depth 2 and beyond roll from the coordinate's own seed within a band chosen by
        /// depth, so a space is stable across reloads and gets stranger the further in it is.
        /// </summary>
        public static Look For(int depth, int seed)
        {
            var look = new Look
            {
                wallStuff = ThingDefOf.WoodLog,
                wallColor = MonoYellow,
                light = Named("WallLamp") ?? Named("StandingLamp"),
                floor = Carpet("Structure_Mustard"),
                accent = Carpet("Structure_Mustard"),
                floorColor = NamedColor("Structure_Mustard"),
                nameKey = "RR_Palette_Monochrome",
            };

            if (depth <= 1)
            {
                // The canonical yellow rooms. Fixed, not rolled.
                if (look.floor == null) { look.floor = Named<TerrainDef>("WoodPlankFloor"); }
                if (look.accent == null) { look.accent = look.floor; }
                return look;
            }

            int band = Band(depth, seed);
            switch (band)
            {
                case 0: // Poolrooms: wet tile and hard light.
                    look.floor = Named<TerrainDef>("SterileTile") ?? look.floor;
                    look.accent = Named<TerrainDef>("SilverTile") ?? look.floor;
                    look.floorColor = NamedColor("Structure_BlueIce");
                    look.wallStuff = ThingDefOf.Steel;
                    look.wallColor = new Color(0.72f, 0.82f, 0.85f);
                    look.nameKey = "RR_Palette_Poolrooms";
                    break;
                case 1: // Machinery: plate, grating and grease.
                    look.floor = Named<TerrainDef>("MetalTile") ?? look.floor;
                    look.accent = Named<TerrainDef>("Concrete") ?? look.floor;
                    look.floorColor = NamedColor("Structure_GreyDark");
                    look.wallStuff = ThingDefOf.Steel;
                    look.wallColor = new Color(0.42f, 0.44f, 0.46f);
                    look.nameKey = "RR_Palette_Machinery";
                    break;
                case 2: // Offices: worn carpet under dead strip light.
                    look.floor = Carpet("Structure_GreenFaded") ?? look.floor;
                    look.accent = Named<TerrainDef>("PavedTile") ?? look.floor;
                    look.floorColor = NamedColor("Structure_GreenFaded");
                    look.wallStuff = ThingDefOf.WoodLog;
                    look.wallColor = new Color(0.66f, 0.63f, 0.55f);
                    look.nameKey = "RR_Palette_Offices";
                    break;
                case 3: // Cold storage: concrete and frost.
                    look.floor = Named<TerrainDef>("Concrete") ?? look.floor;
                    look.accent = Named<TerrainDef>("SterileTile") ?? look.floor;
                    look.floorColor = NamedColor("Structure_GrayLight");
                    look.wallStuff = ThingDefOf.Steel;
                    look.wallColor = new Color(0.78f, 0.80f, 0.83f);
                    look.nameKey = "RR_Palette_ColdStore";
                    break;
                default: // Wrong: the palette stops agreeing with itself.
                    look.floor = Carpet("Structure_UmberBurnt") ?? look.floor;
                    look.accent = Named<TerrainDef>("MetalTile") ?? look.floor;
                    look.floorColor = NamedColor("Structure_UmberBurnt");
                    look.wallStuff = ThingDefOf.WoodLog;
                    look.wallColor = new Color(0.47f, 0.33f, 0.30f);
                    look.nameKey = "RR_Palette_Wrong";
                    break;
            }

            if (look.floor == null) { look.floor = Named<TerrainDef>("Concrete"); }
            if (look.accent == null) { look.accent = look.floor; }
            if (look.wallStuff == null) { look.wallStuff = ThingDefOf.Steel; }
            if (look.light == null) { look.light = Named("StandingLamp"); }
            return look;
        }

        /// <summary>
        /// Which band a depth falls in. Depth advances the band, and the coordinate's own seed
        /// shifts it, so two spaces at the same depth in the same branch are not identical while
        /// each one stays the same across reloads.
        /// </summary>
        private static int Band(int depth, int seed)
        {
            int roll = Gen.HashCombineInt(seed, depth);
            if (roll < 0) { roll = ~roll; }
            return (depth - 2 + roll % 2) % Bands;
        }

        /// <summary>
        /// Paints a cell's floor. Terrain colour lives in a public array on the grid, and it is
        /// cleared by <c>SetTerrain</c>, so the colour has to be applied after the terrain and
        /// the cell has to be redrawn.
        /// </summary>
        public static void SetFloor(Map map, IntVec3 cell, TerrainDef terrain, ColorDef color)
        {
            if (map == null || terrain == null || !cell.InBounds(map)) { return; }
            map.terrainGrid.SetTerrain(cell, terrain);
            if (color == null || map.terrainGrid.colorGrid == null) { return; }
            int index = map.cellIndices.CellToIndex(cell);
            if (index < 0 || index >= map.terrainGrid.colorGrid.Length) { return; }
            map.terrainGrid.colorGrid[index] = color;
            if (map.mapDrawer != null)
            { map.mapDrawer.MapMeshDirty(cell, MapMeshFlagDefOf.Terrain); }
        }

        private static ThingDef Named(string defName)
        {
            return DefDatabase<ThingDef>.GetNamedSilentFail(defName);
        }

        private static T Named<T>(string defName) where T : Def, new()
        {
            return DefDatabase<T>.GetNamedSilentFail(defName);
        }

        private static ColorDef NamedColor(string defName)
        {
            return DefDatabase<ColorDef>.GetNamedSilentFail(defName);
        }

        /// <summary>
        /// The carpet `TerrainDef` for one structure colour.
        ///
        /// **There is no `TerrainDef` called "Carpet".** Core ships a `TerrainTemplateDef` of that
        /// name and `TerrainDefGenerator_Carpet` turns it into one real terrain per structure
        /// colour, named `Carpet` + the `ColorDef` name with `Structure_` removed — so
        /// `Structure_Mustard` becomes `CarpetMustard`.
        ///
        /// This existed as `Named&lt;TerrainDef&gt;("Carpet")`, which **silently returned null**,
        /// and every band that wanted carpet fell through to its `??` fallback. The depth-1 yellow
        /// rooms — the one look invariant 25 calls sacred — were laid in **wood plank flooring**
        /// from the day the palette shipped. Nothing said so: `GetNamedSilentFail` is silent by
        /// design, and the fallback made the result look deliberate.
        ///
        /// Unlike a wall, a carpet cannot be tinted at runtime: the colour is baked into the
        /// generated def. So the colour this band already names is the colour that picks the def,
        /// which is why no new data was needed to fix it.
        /// </summary>
        private static TerrainDef Carpet(string structureColorDefName)
        {
            if (string.IsNullOrEmpty(structureColorDefName)) { return null; }
            const string prefix = "Structure_";
            string suffix = structureColorDefName.StartsWith(prefix, System.StringComparison.Ordinal)
                ? structureColorDefName.Substring(prefix.Length)
                : structureColorDefName;
            return Named<TerrainDef>("Carpet" + suffix);
        }
    }
}
