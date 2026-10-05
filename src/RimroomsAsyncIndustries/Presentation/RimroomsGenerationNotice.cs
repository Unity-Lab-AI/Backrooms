using System;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Scenario;
using RimroomsAsyncIndustries.UI;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>
    /// Tells the player the freeze is coming, in the setting's own voice, **before** it happens.
    ///
    /// ## Owner direction, 2026-10-03, verbatim
    ///
    /// *"and another thing when first loading a new backrooms on gate enter and or using the
    /// operations tab machine when finally opening the gate(loading the backrooms) we need a popup
    /// and notice in that portion of the machine gate connection step that pops up befgore the
    /// "freeze" of the generation telling the player "Time has froze due to mass distortions,
    /// please wait" but noit that i want u to make a universe of backrooms themed notcie of the
    /// pause that is expected and propely keep it toned to the experience we are trying to make
    /// per scenrio type this needs to be added to todo work"*
    ///
    /// and, on the loading screens: *"so we need those mod images made for the menu to also use
    /// them randomly for load screen backgrounds"*, then *"do it properly"*.
    ///
    /// ## The freeze is real, unavoidable, and that is exactly why it needs saying
    ///
    /// `GenStep_BackroomsDestination` carves a 300x300 map — rooms, corridors, pillars, rock
    /// shaping, ore veins, deep resources, fixtures, lights and power — inside Core's map
    /// generation, which runs on the main thread. The player gets a window that stops answering.
    /// **An unexplained freeze reads as a crash; an explained one reads as the setting.**
    ///
    /// ## Why a popup first and a long event second, rather than one or the other
    ///
    /// `DestinationService.EnsureSite` generates **synchronously** and hands the map back through
    /// an `out` parameter, so a window added immediately before it would render on the *next*
    /// frame — after the freeze it was warning about. The work therefore moves into
    /// `LongEventHandler.QueueLongEvent`, which is the pattern Core itself uses for settling, and
    /// that is only legal where nothing is waiting on a return value. **A UI button callback is
    /// exactly such a place**; a method that returns a `CompanyActionResult` is not, which is why
    /// this hooks the Operations pane's buttons rather than `EnsureSite`.
    ///
    /// So: the popup is drawn and dismissed while the game can still draw, and then Core's own
    /// wait box carries our keyed text through the freeze. Both halves of the owner's ask, and
    /// the popup's backdrop is one of the mod's own menu images, drawn at random from
    /// <see cref="RimroomsSlideArt"/> — the same list the main menu reads, because *"the same
    /// images"* must not be able to become two lists.
    ///
    /// ## Only when a space is actually being built
    ///
    /// A coordinate that already has its site is being *re-entered*, not resolved, and there is no
    /// freeze to warn about. Interrupting every crossing with a window the player has read a
    /// hundred times would be the notice becoming the nuisance.
    /// </summary>
    internal static class RimroomsGenerationNotice
    {
        /// <summary>The text Core's own wait box carries through the freeze.</summary>
        internal const string LongEventKey = "RR_Generation_FreezeEvent";

        /// <summary>The notice shown when the scenario is not one this mod authored a tone for.</summary>
        internal const string DefaultNoticeKey = "RR_Generation_FreezeNotice";

        /// <summary>
        /// The close-out, shown once the space has settled and time is moving again.
        ///
        /// **Owner direction, 2026-10-05, verbatim:** *"the notice needs to appear before the map
        /// bagins to load then close out with a normalization notice"*.
        ///
        /// The hold notice is a promise -- *nothing on this side advances until this finishes* --
        /// and a promise with no close is a player wondering whether it ever did. **The pair is
        /// the feature**: one says the stop is expected, the other says it is over.
        /// </summary>
        internal const string DefaultNormalizationKey = "RR_Generation_NormalNotice";

        /// <summary>
        /// Whether a space is about to be resolved from nothing.
        ///
        /// `Site == null` is the one condition that means a map will be generated; everything else
        /// is a re-entry. Read rather than tracked, so it cannot fall out of step with
        /// `EnsureSite`'s own branch on the same field.
        /// </summary>
        internal static bool ShouldAnnounce(CoordinateRecord coordinate)
        {
            return coordinate != null && coordinate.Site == null;
        }

        /// <summary>
        /// Warn, then do the work inside a long event so the freeze is explained while it happens.
        ///
        /// When there is nothing to warn about the work runs immediately and unchanged, so a
        /// caller never has to ask which case it is in.
        /// </summary>
        internal static void Announce(CoordinateRecord coordinate, Action work)
        {
            if (work == null) { return; }
            if (!ShouldAnnounce(coordinate)) { work(); return; }
            Find.WindowStack.Add(new Dialog_RimroomsGenerationNotice(NoticeText(), () =>
                LongEventHandler.QueueLongEvent(work, LongEventKey, false, null,
                    showExtraUIInfo: true, forceHideUI: false, callback: ShowNormalization)));
        }

        /// <summary>
        /// The close-out, on Core's own completion callback rather than on a guess about timing.
        ///
        /// **`QueueLongEvent` takes a `callback` and invokes it after the event finishes** --
        /// read out of `LongEventHandler` in the shipped assembly rather than assumed, and it is
        /// the same hook Core uses to follow its own long work. The alternatives were both worse:
        /// calling this at the end of `work` would run it while the event is still the thing on
        /// screen, and `ExecuteWhenFinished` fires when the *whole queue* drains, which is a
        /// different moment the first time two events are ever queued together.
        ///
        /// **It is deliberately not the full-screen surface the hold notice uses.** The player has
        /// just arrived somewhere and the first thing they should see is the place, not another
        /// picture of a corridor over the top of it.
        /// </summary>
        internal static void ShowNormalization()
        {
            Find.WindowStack.Add(new Dialog_RimroomsNormalizationNotice(NormalizationText()));
        }

        /// <summary>
        /// The close-out text, toned to the scenario exactly as the hold notice is.
        ///
        /// Same scoped-key-then-fallback rule and the same reason: a player on a scenario this mod
        /// did not author still gets told the hold is over, which is the load-bearing half.
        /// </summary>
        internal static TaggedString NormalizationText()
        {
            return Toned(DefaultNormalizationKey);
        }

        /// <summary>
        /// A keyed string, preferring a per-start variant when one is authored.
        ///
        /// Lifted out of <see cref="NoticeText"/> when the close-out needed the identical rule.
        /// **Two copies of a key-scoping rule is how the hold notice and its close-out would end
        /// up toned for different scenarios**, which is the drift this project keeps meeting.
        /// </summary>
        private static TaggedString Toned(string baseKey)
        {
            string key = baseKey;
            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;
            if (part != null && part.startDef != null && part.startDef.defName != null)
            {
                string scoped = baseKey + "_" + part.startDef.defName;
                if (scoped.CanTranslate()) { key = scoped; }
            }
            return key.Translate();
        }

        /// <summary>
        /// The notice, toned to the scenario the player actually started.
        ///
        /// Owner: *"propely keep it toned to the experience we are trying to make per scenrio
        /// type"*. The company reads an instrument; somebody alone in the dark does not. The
        /// scenario comes from `Find.Scenario`, which persists in the save, so the tone is right
        /// mid-game and not only at setup.
        ///
        /// Falls back to the generic notice rather than to nothing: a player on a scenario this
        /// mod did not author still gets told the freeze is expected, which is the load-bearing
        /// half of the direction.
        /// </summary>
        internal static TaggedString NoticeText()
        {
            return Toned(DefaultNoticeKey);
        }
    }

    /// <summary>
    /// The notice itself: one of the mod's own menu images, full screen, with the warning on it.
    ///
    /// **This is the loading screen the mod actually owns.** Core skips the UI root entirely while
    /// a long event is running (`Root.OnGUI` checks `LongEventHandler.ShouldWaitForEvent`), so the
    /// box drawn over the frozen frame is Core's and nothing of ours can be drawn behind it
    /// without a transpiler. This window is drawn *before* the event is queued, while the game can
    /// still draw — which is both what the owner asked for and the only surface available.
    /// </summary>
    internal sealed class Dialog_RimroomsGenerationNotice : Window
    {
        private const float PanelWidth = 560f;
        private const float PanelPadding = 24f;
        private const float ButtonHeight = 38f;

        private readonly TaggedString notice;
        private readonly Action onContinue;
        private readonly Texture2D backdrop;

        internal Dialog_RimroomsGenerationNotice(TaggedString notice, Action onContinue)
        {
            this.notice = notice;
            this.onContinue = onContinue;
            // Drawn once per notice rather than per frame, so the picture does not flicker
            // between images while the player is reading it.
            backdrop = RimroomsSlideArt.RandomSlide();
            forcePause = true;
            absorbInputAroundWindow = true;
            closeOnClickedOutside = false;
            closeOnAccept = false;
            closeOnCancel = false;
            doCloseX = false;
            doCloseButton = false;
            // No frame and no shadow: the window IS the screen, and a vanilla dialog frame round
            // a full-screen image reads as a bug rather than as a loading screen.
            doWindowBackground = false;
            drawShadow = false;
            layer = WindowLayer.Super;
            preventCameraMotion = true;
        }

        public override Vector2 InitialSize
        {
            get { return new Vector2(Verse.UI.screenWidth, Verse.UI.screenHeight); }
        }

        protected override float Margin { get { return 0f; } }

        /// <summary>
        /// **GUARDED, AND HERE IT IS LOAD-BEARING RATHER THAN HOUSEKEEPING.** Unity's IMGUI state
        /// is process-wide: a mod that sets `GUI.color` and returns without restoring it leaves
        /// every window drawn afterwards painting in that colour, and at zero alpha painting
        /// nothing at all. That is the first bug a real launch of this package ever found -- a
        /// setup page with its frame visible and its body blank, and nothing in the log.
        ///
        /// A full-screen image is the most vulnerable thing in the mod to it: an invisible
        /// backdrop on a window with no frame is an invisible window, and the player would be
        /// looking at a frozen game with no notice on it -- the exact failure this whole feature
        /// exists to prevent, arriving through the feature itself.
        /// </summary>
        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { Draw(inRect); }
        }

        private void Draw(Rect inRect)
        {
            if (backdrop != null)
            {
                GUI.DrawTexture(RimroomsSlideArt.FullScreenRect(backdrop), backdrop,
                    ScaleMode.ScaleAndCrop, true);
            }
            else
            {
                // The art is part of the package, so its absence is a packaging fault rather than
                // a state to design for -- but a black screen with the words on it still says the
                // one thing that matters.
                GUI.DrawTexture(inRect, BaseContent.BlackTex);
            }

            float textHeight = Text.CalcHeight(notice, PanelWidth - PanelPadding * 2f);
            float panelHeight = textHeight + PanelPadding * 3f + ButtonHeight;
            var panel = new Rect(
                (inRect.width - PanelWidth) / 2f,
                (inRect.height - panelHeight) / 2f,
                PanelWidth,
                panelHeight);

            Widgets.DrawShadowAround(panel);
            Widgets.DrawWindowBackground(panel);
            Widgets.Label(
                new Rect(panel.x + PanelPadding, panel.y + PanelPadding,
                    PanelWidth - PanelPadding * 2f, textHeight),
                notice);

            var button = new Rect(panel.x + PanelPadding,
                panel.yMax - PanelPadding - ButtonHeight,
                PanelWidth - PanelPadding * 2f, ButtonHeight);
            if (Widgets.ButtonText(button, "RR_Generation_FreezeAcknowledge".Translate()))
            {
                // **CLOSED FIRST, THEN THE WORK IS QUEUED.** The long event blocks the main thread
                // the moment it runs, so a window still on the stack would be frozen on screen
                // underneath Core's wait box for the whole generation.
                Close(false);
                if (onContinue != null) { onContinue(); }
            }
        }
    }

    /// <summary>
    /// The close-out: the space has settled, and time is moving again.
    ///
    /// **Owner direction, 2026-10-05, verbatim:** *"the notice needs to appear before the map
    /// bagins to load then close out with a normalization notice"*.
    ///
    /// ## Deliberately small, and deliberately not the hold screen
    ///
    /// <see cref="Dialog_RimroomsGenerationNotice"/> is full screen because it is replacing a view
    /// that is about to stop answering. This one arrives when the player has just been put
    /// somewhere new, so it is a panel over the map rather than a picture instead of it: **the
    /// first thing they should see is the place they have arrived in.**
    ///
    /// It does not force a pause either. The hold notice pauses because the freeze is coming; this
    /// one says the freeze is over, and pausing to announce that time is moving again would be the
    /// notice contradicting its own text.
    ///
    /// ## It only ever appears where the hold notice did
    ///
    /// Posted from `QueueLongEvent`'s completion callback, which is reached only through
    /// <see cref="RimroomsGenerationNotice.Announce"/> on a coordinate that had no site -- so a
    /// re-entry, which never saw a hold notice, never gets a close-out for a hold that did not
    /// happen.
    /// </summary>
    internal sealed class Dialog_RimroomsNormalizationNotice : Window
    {
        private const float PanelWidth = 460f;
        private const float PanelPadding = 20f;
        private const float ButtonHeight = 34f;

        private readonly TaggedString notice;

        internal Dialog_RimroomsNormalizationNotice(TaggedString notice)
        {
            this.notice = notice;
            absorbInputAroundWindow = true;
            closeOnClickedOutside = false;
            closeOnAccept = true;
            closeOnCancel = true;
            doCloseX = false;
            doCloseButton = false;
            preventCameraMotion = false;
        }

        public override Vector2 InitialSize
        {
            get
            {
                float text = Text.CalcHeight(notice, PanelWidth - PanelPadding * 2f);
                return new Vector2(PanelWidth, text + PanelPadding * 3f + ButtonHeight);
            }
        }

        /// <summary>
        /// Guarded for the same reason the hold notice is: Unity's IMGUI colour and font state is
        /// process-wide, and a window that leaves it changed paints every window drawn after it.
        /// </summary>
        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { Draw(inRect); }
        }

        private void Draw(Rect inRect)
        {
            float textHeight = Text.CalcHeight(notice, inRect.width);
            Widgets.Label(new Rect(inRect.x, inRect.y, inRect.width, textHeight), notice);

            var button = new Rect(inRect.x, inRect.yMax - ButtonHeight, inRect.width, ButtonHeight);
            if (Widgets.ButtonText(button, "RR_Generation_NormalAcknowledge".Translate()))
            { Close(false); }
        }
    }
}
