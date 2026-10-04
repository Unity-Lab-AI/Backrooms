using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// The two primitives every Operations pane needs to stop being a text wall.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"and all the tabs of operations are well designed for a tripple A Mod currently it looks
    /// like its all just text wall and shit"*, *"all things should be done to make it more of a
    /// utility, not  a text wall"*, and the method: *"things can be shortend and more concise and
    /// dirrect  with tools tips would less cluter it making them all concise and accurate"*.
    ///
    /// ## Why these are shared rather than written per pane
    ///
    /// The machine tab was rewritten first and it worked — 356 on-screen words to 58. But it was
    /// rewritten **by hand**, with its own row drawing, its own tooltip call and its own
    /// highlight. Seventeen panes done that way is seventeen chances for the hover to be attached
    /// to the label instead of the row, for one pane to signal a tooltip and the next not to, and
    /// for *"well designed"* to mean something different on every tab. **A house style that lives
    /// in one place is the only kind that survives seventeen edits.**
    ///
    /// Two primitives, because the panel only ever does two things wrong:
    ///
    ///   * `DrawHeading` — a paragraph of instruction on screen where a short line and a hover
    ///     would do. This is the text wall itself.
    ///   * `DrawAction` — a refusal **printed instead of the control it refuses**, so the player
    ///     reads a sentence about a button that is not there. The control stays, disabled, with
    ///     the reason on hover: the same *"disabled with a reason rather than hidden"* rule the
    ///     board-up command on the gate already follows.
    ///
    /// ## Nothing is shortened by deletion
    ///
    /// *"accurate"* is the binding half of the owner's sentence. A label that fits because it
    /// dropped the condition it was describing is worse than the paragraph it replaced, so every
    /// full instruction below still exists and still says every word — it moved to the hover.
    /// `tools/check-operations-density.py` measures the two separately for exactly this reason,
    /// and it reads the argument labels on these calls to do it.
    ///
    /// ## A static class rather than another partial of the window
    ///
    /// It began as a partial of `MainTabWindow_Operations`, which made it unreachable from the
    /// two places in the personnel pane that needed it most: `PersonnelView.DrawDetails` is a
    /// static helper and `Dialog_ConfirmApplicantHire` is its own window, and between them they
    /// held **130 words** of the pane's instruction. A primitive the dialogs cannot call is a
    /// primitive the panel will get a second copy of. Callers take it in with
    /// `using static RimroomsAsyncIndustries.UI.OperationsControls;` so the call sites stay as
    /// short as the pane code around them.
    /// </summary>
    internal static class OperationsControls
    {
        /// <summary>
        /// How a hoverable line signals that it has more to say: Core's own highlight, the same
        /// cue the gate status board uses. **Deliberately not an icon or a cue word** — a cue
        /// word costs on-screen words, which is the thing being reduced, and one consistent
        /// behaviour across every pane teaches itself after the first hover.
        /// </summary>
        internal static void HoverCue(Rect region, TaggedString detail)
        {
            // **NO TEXT, NO CUE.** A highlight that promises a tooltip and then shows nothing is
            // worse than no highlight at all, and Core's own button already highlights itself —
            // so painting a second one over an ordinary enabled button would both lie and
            // double-draw.
            if (detail.NullOrEmpty()) { return; }
            if (Mouse.IsOver(region)) { Widgets.DrawHighlight(region); }
            TooltipHandler.TipRegion(region, detail);
        }

        /// <summary>
        /// A short line on screen, the whole explanation on hover.
        ///
        /// **Call it with named arguments.** `heading:` and `detail:` are what
        /// `check-operations-density.py` reads to tell the two apart, and a positional call would
        /// make the measurement count both as neither — which is how the first version of that
        /// tool reported a pane as fixed while it still drew 356 words.
        /// </summary>
        internal static void DrawHeading(Listing_Standard listing, TaggedString heading,
            TaggedString detail)
        {
            Rect row = listing.GetRect(Text.LineHeight);
            Widgets.Label(row, heading);
            HoverCue(row, detail);
        }

        /// <summary>
        /// A control that is always there, and says why when it will not work.
        ///
        /// Returns true only on a real click of an enabled button. Pass a `refusal:` and the
        /// button draws disabled with that text on hover; pass none and it is an ordinary button.
        /// `detail:` is the hover for a button that works and still has something to explain —
        /// an offer with a condition attached, rather than a control that is off.
        ///
        /// **The refusal has to be on the control, not above it.** A pane that prints *"Select
        /// and designate a native gate before dispatch"* where the dispatch button would be is
        /// asking the player to work out which missing button the sentence is about. This also
        /// keeps the pane's shape stable as state changes, so nothing jumps under the cursor.
        ///
        /// A refusal wins over a detail when both are given: the reason a thing will not work is
        /// always more urgent than what it would have done.
        /// </summary>
        internal static bool DrawAction(Listing_Standard listing, TaggedString label,
            TaggedString refusal, TaggedString detail = default(TaggedString))
        {
            bool allowed = refusal.NullOrEmpty();
            Rect row = listing.GetRect(30f);
            // `active: false` is Core's own disabled button: greyed, no mouseover sound, no
            // click. Asked for rather than imitated with a colour, so the player's own UI
            // settings still apply to it.
            bool clicked = Widgets.ButtonText(row, label, true, true, allowed);
            HoverCue(row, allowed ? detail : refusal);
            listing.Gap(listing.verticalSpacing);
            return allowed && clicked;
        }
    }
}
