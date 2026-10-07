using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// What the generator does to a thing it has just placed so that the thing's existence makes
    /// no work.
    ///
    /// ## Owner direction, 2026-10-07, verbatim
    ///
    /// *"i didnt say ban pots i said mark them forbidden"*, and *"and mark anything else u build
    /// that similar has an action like a pot does"*.
    ///
    /// ## The two actions a placed thing can create, and the mark for each
    ///
    /// **A thing can be a work target.** A pot wants sowing, a bench wants its bills, loot wants
    /// hauling. The forbidden flag is Core's own mark for *"not yet"*: the thing is there, a player
    /// can see the red cross on it, and nothing works it until somebody un-forbids it.
    /// `UnexploredWorkMapComponent` does that when the cell has been seen.
    ///
    /// **A thing can be a destination.** A shelf is a `Building_Storage`, and Core's hauling asks
    /// every storage on the map whether it is a better place for every item -- **it never asks
    /// whose it is, and it never asks whether it is forbidden.** So a shelf placed in a corridor
    /// nobody has walked would have had a crew hauling the branch's stock into the dark from the
    /// tick the coordinate existed. `StoragePriority.Unstored` is Core's own mark for a storage
    /// that is nobody's choice yet: no item is ever moved there, and a player who wants it raises
    /// the priority from the shelf's own tab.
    ///
    /// **One method, every placer.** The room dressing, the family fixtures and the corridor
    /// fixtures all placed things their own way, and the corridor path was the one that forbade
    /// nothing; the owner found it by watching pawns run. A rule written in one place cannot be
    /// forgotten by the next placer somebody adds.
    /// </summary>
    internal static class GeneratedContent
    {
        internal static void Quieten(Thing thing)
        {
            if (thing == null || !thing.Spawned) { return; }
            thing.SetForbidden(true, warnOnFail: false);
            var storage = thing as Building_Storage;
            if (storage != null && storage.settings != null)
            { storage.settings.Priority = StoragePriority.Unstored; }
        }
    }
}
