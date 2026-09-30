using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// Known-good IMGUI state for the duration of one window draw, restored afterwards.
    ///
    /// ## Why this exists: the first bug a real launch found
    ///
    /// Owner report, first launch ever, 2026-09-30: the company setup page opens after EdB Prepare
    /// Carefully with **its title and both buttons drawn and its body completely empty**, and
    /// **nothing in the log** — no exception, no error.
    ///
    /// Unity's IMGUI is a pile of global state. `GUI.color`, `Text.Font` and `Text.Anchor` are
    /// process-wide, and every mod's `OnGUI` runs against the same pile. A mod that sets
    /// `GUI.color` and returns without restoring it leaves **every window drawn afterwards**
    /// painting in that colour — and if its alpha is zero, painting nothing at all.
    ///
    /// **Not one of this package's six window entry points reset any of it.** Core's own
    /// `Page.DrawPageTitle` and `Page.DoBottomButtons` set what they need, which is exactly why
    /// the frame was visible and only our content was not. With 288 other mods loaded, inheriting
    /// global draw state is not bad luck; it is a matter of time.
    ///
    /// ## This is the other half of a claim made at 0.12.40-dev
    ///
    /// That checkpoint asserted this package **authors no colour and no font size** in anything a
    /// player reads, so the player's own contrast and scale settings apply. That was true and it
    /// is still true. What went unexamined is that authoring nothing is not the same as
    /// **assuming nothing**: a window that sets no colour inherits one.
    ///
    /// `check-display-style.py` had to be taught the difference. It still refuses an authored
    /// colour; it now permits exactly this file's reset-to-white-and-restore, because the rule's
    /// purpose is *do not impose a palette*, and defending against a leaked one is the opposite of
    /// imposing one.
    ///
    /// ## Restoring, not just resetting
    ///
    /// The previous values are put back on the way out. Leaving `GameFont.Small` set would make
    /// this package the mod that breaks the next one, which is the whole failure being fixed.
    /// </summary>
    public struct RimroomsWindowState : IDisposable
    {
        private readonly Color color;
        private readonly GameFont font;
        private readonly TextAnchor anchor;
        private readonly bool wordWrap;

        private RimroomsWindowState(bool unused)
        {
            color = GUI.color;
            font = Text.Font;
            anchor = Text.Anchor;
            wordWrap = Text.WordWrap;

            // Core's own defaults for a window body. `Color.white` is not a colour choice: it is
            // the absence of a tint, which is what lets the player's own settings decide.
            GUI.color = Color.white;
            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.UpperLeft;
            Text.WordWrap = true;
        }

        /// <summary>
        /// Opens a draw with known state. Use in a `using` block so the restore cannot be skipped
        /// by an early return or a throw:
        /// <code>using (RimroomsWindowState.Clean()) { ... }</code>
        /// </summary>
        public static RimroomsWindowState Clean()
        {
            return new RimroomsWindowState(true);
        }

        public void Dispose()
        {
            GUI.color = color;
            Text.Font = font;
            Text.Anchor = anchor;
            Text.WordWrap = wordWrap;
        }
    }
}
