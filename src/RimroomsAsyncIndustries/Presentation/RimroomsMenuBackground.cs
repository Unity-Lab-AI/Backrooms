using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Core;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>
    /// Uses RimWorld's native renderer so existing expansion hover overlays remain available.
    /// During our crossfade the incoming image is drawn on top, so cycling pauses near the native
    /// expansion strip until its private fade has had time to clear.
    /// </summary>
    public sealed class RimroomsMenuBackground : UI_BackgroundMain
    {
        private const float DwellSeconds = 30f;
        private const float CrossfadeSeconds = 2f;
        private const float ExpansionFadeGraceSeconds = 1.15f;
        private const float NativeAspectWidth = 2048f;
        private const float NativeAspectHeight = 1280f;
        private const float VersionLabelX = 350f;

        /// <summary>
        /// Where the slides live, and the prefix that decides which of them are ours.
        ///
        /// **The folder is scanned rather than listed**, so a new slide is added by dropping a
        /// PNG in and nothing in C# changes. That matters because the menu art is the one place
        /// this project is allowed to add original images, and it is being produced separately
        /// from the code.
        ///
        /// **The prefix is not decoration.** `UI/Menu` is a generic content path and
        /// `ContentFinder` resolves across every loaded mod, so a folder scan alone would pull
        /// another mod's menu art into this slideshow. With 294 other mods in the target install
        /// that is a certainty rather than a risk. Only `RR_Menu_*` is ours.
        /// </summary>
        private const string SlideFolder = "UI/Menu";
        private const string SlidePrefix = "RR_Menu_";

        private static Texture2D[] loadedSlides;

        private Texture2D nativeImage;
        private Texture2D lastAssignedImage;
        private readonly List<Texture2D> slides;
        private int currentIndex;
        private int transitionTarget = -1;
        private float nextTransitionAt;
        private float transitionStartedAt;
        private float pauseStartedAt;
        private float lastExpansionHoverAt;
        private bool transitionPaused;
        private int settingsMode = -1;

        public RimroomsMenuBackground(Texture2D nativeSelectedImage)
        {
            nativeImage = nativeSelectedImage;
            slides = LoadSlides();
            lastExpansionHoverAt = Time.unscaledTime;
            nextTransitionAt = Time.unscaledTime + DwellSeconds;
            AssignOverride(nativeImage);
            SetupExpansionFadeData();
        }

        internal bool ObserveNativeSelection()
        {
            Texture2D observed = overrideBGImage;
            if (observed == lastAssignedImage) { return true; }
            if (!RimroomsMenuController.IsStockSelectedImage(observed)) { return false; }

            nativeImage = observed;
            lastAssignedImage = observed;
            return true;
        }

        public override void BackgroundOnGUI()
        {
            float now = Time.unscaledTime;
            bool protectNativeExpansionPreview = MouseOverExpansionStrip();
            if (protectNativeExpansionPreview) { lastExpansionHoverAt = now; }
            protectNativeExpansionPreview |= now - lastExpansionHoverAt < ExpansionFadeGraceSeconds;

            ApplySettings(now, protectNativeExpansionPreview);
            AdvanceTransition(now, protectNativeExpansionPreview);

            if (settingsMode == 0 || slides.Count == 0)
            {
                AssignOverride(nativeImage);
            }
            else
            {
                AssignOverride(slides[currentIndex]);
            }

            base.BackgroundOnGUI();

            if (transitionTarget >= 0 && !transitionPaused && !protectNativeExpansionPreview &&
                Event.current.type == EventType.Repaint)
            {
                float alpha = Mathf.Clamp01((now - transitionStartedAt) / CrossfadeSeconds);
                Color oldColor = GUI.color;
                GUI.color = new Color(1f, 1f, 1f, alpha);
                GUI.DrawTexture(BackgroundRect(slides[transitionTarget]), slides[transitionTarget], ScaleMode.ScaleToFit, true);
                GUI.color = oldColor;
            }

            DrawRimroomsVersion();
        }

        private void AssignOverride(Texture2D image)
        {
            overrideBGImage = image;
            lastAssignedImage = image;
        }

        private void ApplySettings(float now, bool protectNativeExpansionPreview)
        {
            RimroomsSettings settings = RimroomsMod.Settings;
            int mode = settings == null || !settings.MenuSlideshowEnabled || slides.Count == 0
                ? 0
                : settings.MenuReducedMotion ? 2 : 1;
            if (mode == settingsMode) { return; }

            settingsMode = mode;
            transitionTarget = -1;
            transitionPaused = false;
            currentIndex = 0;
            lastExpansionHoverAt = protectNativeExpansionPreview ? now : now - ExpansionFadeGraceSeconds;
            nextTransitionAt = now + DwellSeconds;
        }

        private void AdvanceTransition(float now, bool protectNativeExpansionPreview)
        {
            if (settingsMode != 1 || slides.Count < 2) { return; }

            if (protectNativeExpansionPreview)
            {
                if (!transitionPaused)
                {
                    transitionPaused = true;
                    pauseStartedAt = now;
                }
                return;
            }

            if (transitionPaused)
            {
                float pausedFor = Mathf.Max(0f, now - pauseStartedAt);
                nextTransitionAt += pausedFor;
                if (transitionTarget >= 0) { transitionStartedAt += pausedFor; }
                transitionPaused = false;
            }

            if (transitionTarget < 0 && now >= nextTransitionAt)
            {
                transitionTarget = (currentIndex + 1) % slides.Count;
                transitionStartedAt = now;
            }

            if (transitionTarget >= 0 && now - transitionStartedAt >= CrossfadeSeconds)
            {
                currentIndex = transitionTarget;
                transitionTarget = -1;
                nextTransitionAt = now + DwellSeconds;
            }
        }

        private bool MouseOverExpansionStrip()
        {
            var expansions = ModLister.AllExpansions;
            if (expansions == null) { return false; }
            int iconCount = expansions.Count(expansion => expansion != null && !expansion.isCore);
            if (iconCount <= 0) { return false; }

            float stripWidth = 32f + 64f * iconCount + (iconCount - 1) * 16f;
            Rect strip = new Rect(8f, Verse.UI.screenHeight - 104f, stripWidth, 96f);
            return Mouse.IsOver(strip);
        }

        private static List<Texture2D> LoadSlides()
        {
            if (loadedSlides == null)
            {
                // Sorted ordinally by name -- invariant 26 -- so the running order is the same on
                // every machine and every mod list, rather than whatever order the loader
                // happened to return. A slideshow whose order depends on the install is a
                // slideshow nobody can describe or reproduce a screenshot from.
                loadedSlides = ContentFinder<Texture2D>.GetAllInFolder(SlideFolder)
                    .Where(image => image != null && image.name != null &&
                        image.name.StartsWith(SlidePrefix, System.StringComparison.Ordinal))
                    .OrderBy(image => image.name, System.StringComparer.Ordinal)
                    .ToArray();
            }
            return new List<Texture2D>(loadedSlides);
        }

        private static Rect BackgroundRect(Texture2D image)
        {
            float imageWidth = image == null ? NativeAspectWidth : image.width;
            float imageHeight = image == null ? NativeAspectHeight : image.height;
            float aspect = imageWidth / imageHeight;
            if (Verse.UI.screenWidth > Verse.UI.screenHeight * aspect)
            {
                float height = Verse.UI.screenWidth / aspect;
                return new Rect(0f, (Verse.UI.screenHeight - height) / 2f, Verse.UI.screenWidth, height);
            }

            float width = Verse.UI.screenHeight * aspect;
            return new Rect((Verse.UI.screenWidth - width) / 2f, 0f, width, Verse.UI.screenHeight);
        }

        private static void DrawRimroomsVersion()
        {
            if (Event.current.type != EventType.Repaint) { return; }

            string label = "RR_Menu_VersionLabel".Translate(RimroomsMod.ModVersion);
            float width = Mathf.Min(420f, Mathf.Max(180f, Verse.UI.screenWidth - VersionLabelX - 220f));
            Rect rect = new Rect(VersionLabelX, 10f, width, 64f);

            GameFont oldFont = Text.Font;
            TextAnchor oldAnchor = Text.Anchor;
            Color oldColor = GUI.color;
            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.UpperLeft;
            GUI.color = new Color(1f, 1f, 1f, 0.78f);
            Widgets.Label(rect, label);
            GUI.color = oldColor;
            Text.Anchor = oldAnchor;
            Text.Font = oldFont;
        }
    }
}
