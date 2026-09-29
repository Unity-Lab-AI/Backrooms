using RimroomsAsyncIndustries.Gate;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// Renaming one remembered address through the game's own rename dialog — the same one
    /// used for zones, caravans and storage groups, and already used by this mod for the
    /// company name.
    ///
    /// `Dialog_Rename&lt;T&gt;` is abstract, so a concrete subclass is required even when it adds
    /// nothing. That is worth doing rather than writing a bespoke window: the player gets an
    /// interaction they already know, and there is no second rename UI to keep consistent with
    /// the first.
    ///
    /// A blank name is accepted here, unlike the company's, because
    /// <see cref="GateHistoryEntry.RenamableLabel"/> falls back to the coordinate's own label
    /// when cleared. Clearing a name is how a player undoes a rename, and refusing it would
    /// leave them stuck with a label they no longer want.
    /// </summary>
    public sealed class Dialog_RenameGateAddress : Dialog_Rename<GateHistoryEntry>
    {
        public Dialog_RenameGateAddress(GateHistoryEntry entry) : base(entry) { }
    }
}
