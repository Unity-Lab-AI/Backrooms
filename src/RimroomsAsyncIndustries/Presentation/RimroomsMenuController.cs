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

    /// <summary>Claims only the stock title background and yields to other background owners.</summary>
    public sealed class RimroomsMenuController : MonoBehaviour
    {
        private static RimroomsMenuController instance;

        private UI_BackgroundMain originalBackground;
        private RimroomsMenuBackground ownedBackground;
        private bool yieldedForEntry;
        private bool failedForEntry;

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
                UIMenuBackground active = UIMenuBackgroundManager.background;
                if (ownedBackground != null)
                {
                    if (active == ownedBackground)
                    {
                        if (ownedBackground.ObserveNativeSelection()) { return; }
                        ReleaseIfStillOwner();
                        yieldedForEntry = true;
                        return;
                    }

                    ownedBackground = null;
                    originalBackground = null;
                    if (active != null && active.GetType() == typeof(UI_BackgroundMain) &&
                        IsStockSelectedImage(((UI_BackgroundMain)active).overrideBGImage))
                    {
                        // UIRoot_Entry.Init replaces the native background when returning to the menu.
                        Install((UI_BackgroundMain)active);
                        return;
                    }

                    // A different renderer or non-stock image means another provider owns the surface.
                    yieldedForEntry = true;
                    return;
                }

                if (active == null) { return; }
                if (active.GetType() != typeof(UI_BackgroundMain))
                {
                    yieldedForEntry = true;
                    return;
                }

                var stock = (UI_BackgroundMain)active;
                if (!IsStockSelectedImage(stock.overrideBGImage))
                {
                    // A provider may use the stock type; an unknown image means ownership is ambiguous.
                    yieldedForEntry = true;
                    return;
                }

                Install(stock);
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms][Menu] Slideshow setup failed; leaving the native background in control. " + exception.Message);
                ReleaseIfStillOwner();
                failedForEntry = true;
            }
        }

        private void Install(UI_BackgroundMain stock)
        {
            originalBackground = stock;
            ownedBackground = new RimroomsMenuBackground(stock.overrideBGImage);
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
