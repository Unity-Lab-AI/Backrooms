using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    /// <summary>
    /// Puts <see cref="RimroomsRecordBook"/> on Core's `TextBook`, in code, after every mod has
    /// loaded.
    ///
    /// ## WHY NOT AN XML PATCH, WHICH IS WHERE THIS STARTED
    ///
    /// Core declares `thingClass` on the **abstract** parent:
    ///
    /// ```xml
    /// <ThingDef Name="BookBase" Abstract="True">
    ///   <thingClass>Book</thingClass>
    /// ```
    ///
    /// Patches run before inheritance resolves, so `Defs/ThingDef[defName="TextBook"]/thingClass`
    /// matches nothing and the only operation that works on the child is a `PatchOperationReplace`.
    /// **`check-compliance` rule 3 refused exactly that, and the rule was right:** a replace takes
    /// ownership of a def and the last mod to load wins. Patching `BookBase` instead would have
    /// handed this class to `Novel`, `Schematic` and `Tome` as well -- three defs this mod has no
    /// business touching.
    ///
    /// **Binding here is strictly more precise than any xpath could be**, which is the same
    /// argument `FixtureTellService` already makes for attaching its comp at startup: this runs
    /// after inheritance has resolved and after every mod's defs are loaded, so it reads the value
    /// that is actually in play rather than the one somebody authored.
    ///
    /// ## AND IT CAN REFUSE, WHICH A PATCH CANNOT
    ///
    /// `thingClass` is single-valued. A patch would win or lose by load order and say nothing
    /// either way. **This asks first:** the class is replaced only when it is still Core's own
    /// `Book`. If another mod has already changed it, the binding leaves that mod's class alone and
    /// reports the fact, because two mods silently fighting over one field is worse than one mod
    /// visibly declining.
    ///
    /// ## WHAT THIS CANNOT DO, STATED RATHER THAN DISCOVERED LATER
    ///
    /// **A book already in a saved game keeps the class it was saved with.** RimWorld writes the
    /// runtime type into the save -- `ScribeExtractor.SaveableFromNode` reads a `Class` attribute
    /// and instantiates that -- so a textbook saved as `Verse.Book` loads as `Verse.Book` no matter
    /// what the def now says. **This fix therefore applies to every book created from this version
    /// onward and not to books that already exist in an old save.**
    ///
    /// That is a limitation and not a bug, and it has an in-game remedy that needs no migration:
    /// `RecordBookDelivery` sends two correct books whenever a branch holds **none anywhere**, so
    /// destroying a wrongly-titled pair gets a correctly-titled pair back. A migration that
    /// destroyed and rebuilt a book in place was considered and rejected -- `CompRouteEvidence`
    /// binds through `GetUniqueLoadID()`, a new object has a new one, and quietly re-pointing a
    /// bound evidence record is how a case gets lost. `SAVE_MIGRATION_POLICY.md` owns that call,
    /// not this file.
    /// </summary>
    [StaticConstructorOnStartup]
    internal static class RecordBookClassBinding
    {
        /// <summary>Whether the binding was made, for the checker and for the log line.</summary>
        internal static bool Bound { get; private set; }

        static RecordBookClassBinding()
        {
            ThingDef book = DefDatabase<ThingDef>.GetNamedSilentFail("TextBook");
            // No TextBook means no Core books at all, which is a game this mod cannot be running
            // in. Silence is right: there is nothing to warn anybody about.
            if (book == null) { return; }

            if (book.thingClass == typeof(RimroomsRecordBook))
            {
                // Already ours. Reached if anything ever runs this twice; saying nothing is correct.
                Bound = true;
                return;
            }

            if (book.thingClass != typeof(Book))
            {
                // **DECLINE LOUDLY RATHER THAN WIN QUIETLY.** Another mod owns this field. Taking
                // it would break whatever they built; taking it silently would make the breakage
                // unattributable. The company label and the journal description stay off, and the
                // inspect card -- which is a comp and still works -- carries the guidance instead.
                Log.Warning("[Rimrooms] TextBook's thingClass is " + book.thingClass
                    + ", not Verse.Book, so another mod owns it. Leaving it alone: the company "
                    + "record book keeps the game's own title and description. The book's inspect "
                    + "card still explains what it is for.");
                return;
            }

            book.thingClass = typeof(RimroomsRecordBook);
            Bound = true;
        }
    }
}
