using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>
    /// The mod's own menu art, and **the single place it is found**.
    ///
    /// ## Owner direction, 2026-10-03, verbatim
    ///
    /// *"and anothert thing.. we properly use the main menu images we made for the mod on the main
    /// menu page but i dont think we properly did the same for loading screens and the like"*, then
    /// *"so we need those mod images made for the menu to also use them randomly for load screen
    /// backgrounds"*, then *"do it properly"*.
    ///
    /// ## Why this exists as its own type
    ///
    /// The loader lived inside <see cref="RimroomsMenuBackground"/>, which is a
    /// `UI_BackgroundMain` and therefore only ever constructed for the main menu. Anything else
    /// that wanted the same images would have had to find them again — a second folder scan, a
    /// second prefix, a second ordering — and *"the same images"* would then be two lists that
    /// agree until somebody adds a PNG. **The owner's ask is explicitly that they are the same
    /// images**, so there is one list and both readers take it from here.
    ///
    /// ## The prefix is not decoration
    ///
    /// `UI/Menu` is a generic content path and `ContentFinder` resolves across **every** loaded
    /// mod, so a folder scan alone pulls another mod's menu art in. With 294 other mods in the
    /// target install that is a certainty rather than a risk. Only `RR_Menu_*` is ours.
    /// </summary>
    internal static class RimroomsSlideArt
    {
        private const string SlideFolder = "UI/Menu";
        private const string SlidePrefix = "RR_Menu_";

        private static Texture2D[] loaded;

        /// <summary>
        /// Every slide the mod ships, ordered by name.
        ///
        /// Sorted ordinally — invariant 26 — so the running order is the same on every machine and
        /// every mod list rather than whatever order the loader happened to return. A slideshow
        /// whose order depends on the install is one nobody can describe or reproduce a screenshot
        /// from. **Randomness is applied by the reader choosing a starting point, never by
        /// shuffling this**, so the sequence stays describable while the entry point varies.
        /// </summary>
        internal static List<Texture2D> Slides()
        {
            if (loaded == null)
            {
                loaded = ContentFinder<Texture2D>.GetAllInFolder(SlideFolder)
                    .Where(image => image != null && image.name != null &&
                        image.name.StartsWith(SlidePrefix, StringComparison.Ordinal))
                    .OrderBy(image => image.name, StringComparer.Ordinal)
                    .ToArray();
            }
            return new List<Texture2D>(loaded);
        }

        /// <summary>
        /// A starting index drawn without touching the game's seeded randomness.
        ///
        /// Owner: *"use them randomly"*. **`Rand` is deliberately not used.** Everything else in
        /// this mod that draws a number takes it from a coordinate's own seed so a place is the
        /// same place on every visit, and `Rand` during map generation is pushed and popped around
        /// so a layout is reproducible. Which picture is behind a loading box is the one thing here
        /// that genuinely should differ run to run and that nothing should ever depend on, so it
        /// comes from the wall clock and is kept well away from both.
        /// </summary>
        internal static int RandomIndex(int count)
        {
            if (count <= 1) { return 0; }
            int draw = Environment.TickCount;
            if (draw < 0) { draw = ~draw; }
            return draw % count;
        }

        /// <summary>One slide, or null when the mod's art is missing from the package.</summary>
        internal static Texture2D RandomSlide()
        {
            List<Texture2D> slides = Slides();
            return slides.Count == 0 ? null : slides[RandomIndex(slides.Count)];
        }

        /// <summary>
        /// The rect that covers the screen with this image, cropping rather than letterboxing.
        ///
        /// Shared for the same reason the list is: a loading backdrop that framed the art
        /// differently from the menu would read as a different mod's screen.
        /// </summary>
        internal static Rect FullScreenRect(Texture2D image)
        {
            float imageWidth = image == null ? 2048f : image.width;
            float imageHeight = image == null ? 1280f : image.height;
            float aspect = imageWidth / imageHeight;
            if (Verse.UI.screenWidth > Verse.UI.screenHeight * aspect)
            {
                float height = Verse.UI.screenWidth / aspect;
                return new Rect(0f, (Verse.UI.screenHeight - height) / 2f, Verse.UI.screenWidth, height);
            }
            float width = Verse.UI.screenHeight * aspect;
            return new Rect((Verse.UI.screenWidth - width) / 2f, 0f, width, Verse.UI.screenHeight);
        }
    }
}
