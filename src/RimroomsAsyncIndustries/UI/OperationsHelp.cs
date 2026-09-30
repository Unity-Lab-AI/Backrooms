using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// RR-UI: the help pane -- the glossary, the keyboard path, and the readability position.
    /// Rows 822 and 833 ask for a *"tutorial/guide, help glossary, keyboard/controller paths"*
    /// and *"color/contrast/readability options, scalable UI"*.
    ///
    /// Three things about this pane are deliberate.
    ///
    /// It draws **outside** <c>DrawCompany</c>, so it works with no game loaded and with no
    /// company branch established. A glossary that only opens once you already understand the
    /// mod well enough to have started it is not help.
    ///
    /// The keyboard line reads the player's **live** binding through <c>MainKeyLabel</c>, not
    /// the default this package ships. Core's <c>KeyBindingDefGenerator</c> emits
    /// <c>MainTab_RR_Operations</c> from the def's <c>defaultHotKey</c> and the player may
    /// rebind it in Key Bindings; help that named the shipped key would be wrong for anybody
    /// who did.
    ///
    /// Nothing here sets a colour or a font size. That is the whole of this package's answer to
    /// contrast and scale: every readout uses Core's own <c>GameFont</c> values and Core's own
    /// palette, so the player's Options -- UI scale, font, colourblind mode -- apply to this
    /// mod exactly as they apply to the base game. <c>check-display-style.py</c> refuses an
    /// authored colour or an authored font in any readout file, because an absolute with no
    /// check behind it is a promise.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        /// <summary>Every word this package uses where RimWorld has none of its own.</summary>
        private static readonly string[] GlossaryKeys =
        {
            "RR_Help_TermGate", "RR_Help_TermConnection", "RR_Help_TermThreshold",
            "RR_Help_TermCoordinate", "RR_Help_TermBand", "RR_Help_TermBranch",
            "RR_Help_TermRequest", "RR_Help_TermContract", "RR_Help_TermDispatch",
            "RR_Help_TermDebrief", "RR_Help_TermEvidence", "RR_Help_TermInsight",
            "RR_Help_TermFacility", "RR_Help_TermSite",
        };

        private static void DrawHelp(Listing_Standard listing)
        {
            listing.Label("RR_Help_Heading".Translate());
            listing.Gap(8f);

            // What the player is meant to do, in the order the campaign asks for it. This is
            // the same sequence `docs/TUTORIAL_SCRIPT.md` scripts and the mission line drives;
            // it is restated here because a player reads help in game, not in a repository.
            listing.Label("RR_Help_FirstSession".Translate());
            listing.GapLine();

            listing.Label("RR_Help_KeyboardHeading".Translate());
            listing.Label("RR_Help_KeyboardTab".Translate(OperationsKeyLabel()));
            listing.Label("RR_Help_KeyboardRebind".Translate());
            listing.Label("RR_Help_KeyboardNative".Translate());
            listing.GapLine();

            listing.Label("RR_Help_ReadabilityHeading".Translate());
            listing.Label("RR_Help_Readability".Translate());
            listing.Label("RR_Help_Scale".Translate());
            listing.GapLine();

            listing.Label("RR_Help_GlossaryHeading".Translate());
            for (int i = 0; i < GlossaryKeys.Length; i++)
            {
                listing.Label(GlossaryKeys[i].Translate());
                listing.Gap(4f);
            }
            listing.GapLine();

            listing.Label("RR_Help_Untested".Translate());
        }

        /// <summary>
        /// The key this tab is bound to right now, or a plain statement that it is bound to
        /// nothing. <c>hotKey</c> is <c>[Unsaved]</c> and is filled in by Core's generator, so
        /// it is null whenever <c>defaultHotKey</c> was never set -- and null-checking it is
        /// cheaper than assuming a generator ran.
        /// </summary>
        private static string OperationsKeyLabel()
        {
            MainButtonDef self = DefDatabase<MainButtonDef>.GetNamedSilentFail("RR_Operations");
            if (self == null || self.hotKey == null)
            {
                return "RR_Help_KeyboardUnbound".Translate().ToString();
            }
            return self.hotKey.MainKeyLabel;
        }
    }
}
