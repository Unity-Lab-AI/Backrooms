using System;
using RimWorld;
using RimroomsAsyncIndustries.Core;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>Runs from RimWorld's synchronous main-thread static-constructor startup pass.</summary>
    [StaticConstructorOnStartup]
    internal static class RimroomsMenuBootstrap
    {
        static RimroomsMenuBootstrap()
        {
            LongEventHandler.ExecuteWhenFinished(EnsureStartedOnMainThread);
        }

        private static void EnsureStartedOnMainThread()
        {
            if (!UnityData.IsInMainThread)
            {
                Log.Warning("[Rimrooms][Menu] Native startup callback was not on Unity's main thread; menu controller was not created.");
                return;
            }
            RimroomsMenuController.EnsureStarted();
        }
    }

    /// <summary>Claims the title and loading background from any provider, and reclaims it if replaced.</summary>
    public sealed class RimroomsMenuController : MonoBehaviour
    {
        private static RimroomsMenuController instance;

        private UIMenuBackground originalBackground;
        private RimroomsMenuBackground ownedBackground;
        private bool yieldedForEntry;
        private bool failedForEntry;
        private string lastLoggedProvider;

        internal static void EnsureStarted()
        {
            if (!UnityData.IsInMainThread)
            {
                Log.Warning("[Rimrooms][Menu] Skipped controller creation because RimWorld did not dispatch startup on Unity's main thread.");
                return;
            }
            if (instance != null) { return; }
            var controllerObject = new GameObject("RimroomsMenuController");
            controllerObject.hideFlags = HideFlags.HideAndDontSave;
            UnityEngine.Object.DontDestroyOnLoad(controllerObject);
            instance = controllerObject.AddComponent<RimroomsMenuController>();
        }

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                UnityEngine.Object.Destroy(gameObject);
                return;
            }
            instance = this;
            UnityEngine.Object.DontDestroyOnLoad(gameObject);
        }

        private void Update()
        {
            // **RELEASED ONLY ONCE A MAP IS PLAYING, NOT THE MOMENT THE MENU IS LEFT.** This tested
            // `!= Entry`, so the first frame of a load handed the surface back to Core's stock
            // background -- and Core's loading screen draws exactly that surface. Owner, 2026-10-07:
            // *"the loading screen slideshow is still the bas games DLCs slide show not correctly
            // our mods slideart"*. The slides were installed, and we gave them back one frame
            // before they were needed. `MapInitializing` is the loading screen; the menu's own
            // ownership rules below apply to it unchanged, so a load started from inside a game
            // claims the stock background on the same terms the menu does.
            if (Current.ProgramState == ProgramState.Playing)
            {
                ReleaseIfStillOwner();
                yieldedForEntry = false;
                failedForEntry = false;
                return;
            }
            if (yieldedForEntry || failedForEntry) { return; }

            try
            {
                // **RIMROOMS OWNS THE MENU AND THE LOADING SCREEN, WHOEVER ELSE IS LOADED.** This
                // used to claim only the stock background and yield, silently, to any other owner.
                // Owner, 2026-10-21, on a RimSort list carrying Vanilla Backgrounds Expanded: *"im
                // not seeing it activated and its loading screen art and main menu art and im not
                // seeing the rimrooms versioning on main menu"* -- that mod sets its own picture,
                // so we yielded, and the version label went with the art. Asked, the owner chose
                // **"Rimrooms takes priority"**: claim the surface from any provider, and take it
                // back if something replaces it.
                UIMenuBackground active = UIMenuBackgroundManager.background;
                if (active == null) { return; }
                if (ownedBackground != null && active == ownedBackground)
                {
                    ownedBackground.ObserveNativeSelection();
                    return;
                }

                // UIRoot_Entry.Init replaces the background when returning to the menu, and another
                // mod may swap it at any time; either way the surface is claimed again.
                ownedBackground = null;
                originalBackground = null;
                Install(active);
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms][Menu] Slideshow setup failed; leaving the native background in control. " + exception.Message);
                ReleaseIfStillOwner();
                failedForEntry = true;
            }
        }

        private void Install(UIMenuBackground active)
        {
            var main = active as UI_BackgroundMain;
            bool stock = active.GetType() == typeof(UI_BackgroundMain) && IsStockSelectedImage(main.overrideBGImage);
            if (!stock && active.GetType().FullName != lastLoggedProvider)
            {
                // Once per provider, so a mod that swaps the background every frame cannot flood the log.
                lastLoggedProvider = active.GetType().FullName;
                Log.Message("[Rimrooms][Menu] Took the menu background over from " + active.GetType().FullName + ".");
            }
            originalBackground = active;
            // Only a stock expansion picture is kept as the native image; another provider's
            // picture is never shown under ours.
            Texture2D nativeImage = main != null && IsStockSelectedImage(main.overrideBGImage) ? main.overrideBGImage : null;
            ownedBackground = new RimroomsMenuBackground(nativeImage);
            UIMenuBackgroundManager.background = ownedBackground;
        }

        internal static bool IsStockSelectedImage(Texture2D image)
        {
            if (image == null) { return true; }
            var expansions = ModLister.AllExpansions;
            if (expansions == null) { return false; }
            for (int i = 0; i < expansions.Count; i++)
            {
                ExpansionDef expansion = expansions[i];
                if (expansion != null && expansion.BackgroundImage == image) { return true; }
            }
            return false;
        }

        private void ReleaseIfStillOwner()
        {
            if (ownedBackground != null && UIMenuBackgroundManager.background == ownedBackground &&
                originalBackground != null)
            {
                UIMenuBackgroundManager.background = originalBackground;
            }
            ownedBackground = null;
            originalBackground = null;
        }

        private void OnDestroy()
        {
            ReleaseIfStillOwner();
            if (instance == this) { instance = null; }
        }
    }
}
