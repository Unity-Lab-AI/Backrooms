using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    public sealed class CompProperties_RimroomsFixtureTell : CompProperties
    {
        public CompProperties_RimroomsFixtureTell()
        {
            compClass = typeof(CompRimroomsFixtureTell);
        }
    }

    /// <summary>
    /// Where a player reads the one exact wrong thing about an object they found.
    ///
    /// **Owner direction, 2026-10-04, verbatim:** *"not just room shape echoes but echos of thier
    /// inhabitance in weird ways and items and equipment and production benches"*.
    ///
    /// This is the object half of the same mechanism <see cref="Threats.CompRimroomsSurvivor"/>
    /// carries for people: the fact lives **on the thing, for as long as the thing exists**, not
    /// in a letter that fired once and scrolled away. `THREAT_DESIGN_SHEETS.md` requires *"a
    /// visible or otherwise accessible warning"* and forbids colour or sound as the only cue.
    ///
    /// ## Dormant unless marked, which is the whole safety argument
    ///
    /// <see cref="FixtureTellService"/> attaches this to every definition the generator is capable
    /// of placing, which is a few hundred defs and includes ordinary Core furniture a player has
    /// in their own colony. **So the overwhelming majority of the instances of this comp in any
    /// game are on things nobody marked**, and every member below returns early for them: no
    /// inspect line, no stacking change, nothing saved beyond a null string.
    ///
    /// That is the same dormant-until-designated pattern the gate, emergence, credit-beacon and
    /// survivor comps all use on Core defs, and it is the reason installing this mod cannot change
    /// a shelf somebody already owns.
    /// </summary>
    public sealed class CompRimroomsFixtureTell : ThingComp
    {
        /// <summary>
        /// Saved. The <see cref="RimroomsFixtureTellDef"/> a coordinate marked this object with,
        /// or null for everything else in the game.
        ///
        /// A defName rather than a resolved def, because this is saved on a thing that can outlive
        /// a content change: a tell removed from the package must leave the object standing and
        /// silent rather than throw on load. Same reasoning as the inhabitant family on a pawn.
        /// </summary>
        private string tell;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref tell, "rr_fixtureTell");
        }

        /// <summary>Whether a coordinate marked this particular object.</summary>
        public bool Marked { get { return !string.IsNullOrEmpty(tell); } }

        /// <summary>Marks this object with what is wrong about it.</summary>
        internal void Mark(RimroomsFixtureTellDef definition)
        {
            if (definition != null) { tell = definition.defName; }
        }

        /// <summary>The one exact wrong fact about this object, or null.</summary>
        public string Tell
        {
            get
            {
                if (string.IsNullOrEmpty(tell)) { return null; }
                RimroomsFixtureTellDef definition =
                    DefDatabase<RimroomsFixtureTellDef>.GetNamedSilentFail(tell);
                if (definition == null || string.IsNullOrEmpty(definition.tellKey)) { return null; }
                return definition.tellKey.Translate().ToString();
            }
        }

        public override string CompInspectStringExtra()
        {
            return Tell;
        }

        /// <summary>
        /// Keeps a marked stack from being merged into an unmarked one.
        ///
        /// **Without this the fact would be silently destroyed by hauling.** Core's
        /// <c>Thing.CanStackWith</c> compares def, stuff and hit points and does not look at comp
        /// data, so a marked stack of steel dropped onto an ordinary one would merge and the tell
        /// would survive or vanish depending on which thing happened to absorb the other. A
        /// readable warning that disappears because somebody tidied up is not a readable warning.
        ///
        /// **And it changes nothing for anybody who is not carrying a tell.** Two unmarked things
        /// both reach the last line and stack exactly as they always did, which matters because
        /// this comp sits on Core resource defs in every colony in the game.
        /// </summary>
        public override bool AllowStackWith(Thing other)
        {
            if (!base.AllowStackWith(other)) { return false; }
            CompRimroomsFixtureTell theirs = other == null
                ? null : other.TryGetComp<CompRimroomsFixtureTell>();
            string mine = string.IsNullOrEmpty(tell) ? null : tell;
            string theirTell = theirs == null || string.IsNullOrEmpty(theirs.tell)
                ? null : theirs.tell;
            return string.Equals(mine, theirTell, System.StringComparison.Ordinal);
        }

        /// <summary>
        /// Carries the tell onto a piece split off this stack, so a partial haul does not leave
        /// an unmarked piece that can merge into ordinary stock.
        /// </summary>
        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            if (string.IsNullOrEmpty(tell)) { return; }
            CompRimroomsFixtureTell split = piece == null
                ? null : piece.TryGetComp<CompRimroomsFixtureTell>();
            if (split != null) { split.tell = tell; }
        }
    }
}
