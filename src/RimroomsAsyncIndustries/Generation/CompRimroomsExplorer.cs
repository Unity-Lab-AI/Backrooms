using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    public sealed class CompProperties_RimroomsExplorer : CompProperties
    {
        public CompProperties_RimroomsExplorer() { compClass = typeof(CompRimroomsExplorer); }
    }

    /// <summary>
    /// A per-pawn explore order, toggled like drafting.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"and i think we need a explore option thats
    /// toggleable like drafting. so the pawns will go room to room exploring the maze of the map
    /// attempting to explore the seed completely until toggled off or completed with a pop notice
    /// "PAwn radioed in exploration complete" or something appropriate"*.
    ///
    /// ## Drafting is the right comparison and it sets the shape
    ///
    /// A toggle the player flips, on one pawn at a time, that **overrides ordinary work while it is
    /// on and releases the pawn when it is off.** Not a work type with a priority, because a priority
    /// means *when you have nothing better to do* and exploring a maze is a thing you send somebody to
    /// go and do.
    ///
    /// ## It marks nothing itself, which is the whole reason it is small
    ///
    /// `FirstSliceSiteComponent` already marks a room surveyed when somebody carrying a record book
    /// stands in it, and has since long before this existed. **So exploring only has to walk the
    /// pawn**; the marking, the event line and the observation all happen exactly as they do when a
    /// player walks a crew through by hand. One derivation of *what makes a room surveyed*, and the
    /// book still matters — which is correct, because a survey nobody recorded is a walk.
    ///
    /// ## The comp is dormant on everybody who was not asked
    ///
    /// It sits on `Human` by patch, like `CompRimroomsSurvivor`, and does nothing at all until the
    /// player toggles it. Installing this mod must never change anybody who was not asking for it.
    /// </summary>
    public sealed class CompRimroomsExplorer : ThingComp
    {
        /// <summary>Whether the player has this pawn exploring. Saved, like a draft state.</summary>
        private bool exploring;

        /// <summary>Whether this pawn has been told the coordinate is finished.</summary>
        private bool reportedComplete;

        public bool Exploring { get { return exploring; } }

        private Pawn Pawn { get { return parent as Pawn; } }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref exploring, "rr_exploring", false);
            Scribe_Values.Look(ref reportedComplete, "rr_exploreReported", false);
        }

        /// <summary>
        /// Turn it off.
        ///
        /// Called by the player, and by the map component when a coordinate is finished. **Clearing
        /// the report flag here rather than when it is set** means a pawn sent to a second coordinate
        /// is told about that one too, instead of staying silent because they had already radioed in
        /// once in their life.
        /// </summary>
        public void StopExploring()
        {
            exploring = false;
            reportedComplete = false;
        }

        /// <summary>Whether this pawn has already radioed in about the space they are standing in.</summary>
        public bool ReportedComplete { get { return reportedComplete; } }

        public void NoteReportedComplete() { reportedComplete = true; }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            Pawn pawn = Pawn;
            // **Offered only where exploring means something.** A colonist standing in the home base
            // has nothing to explore, and a toggle that can be switched on and does nothing is worse
            // than one that is absent: the player would conclude the feature is broken.
            if (pawn == null || pawn.Map == null || pawn.Faction != Faction.OfPlayer
                || !pawn.IsColonistPlayerControlled || pawn.Dead || pawn.Downed)
            { yield break; }
            if (!(pawn.Map.Parent is RimroomsDestinationMapParent)) { yield break; }

            yield return new Command_Toggle
            {
                defaultLabel = "RR_UI_Explore".Translate(),
                defaultDesc = "RR_UI_ExploreDesc".Translate(),
                // Core's own draft icon, because the owner's comparison is drafting and the player
                // already knows what that button means. No new art.
                icon = ContentFinder<UnityEngine.Texture2D>.Get("UI/Commands/Draft", true),
                isActive = () => exploring,
                toggleAction = delegate
                {
                    if (exploring) { StopExploring(); return; }
                    exploring = true;
                    reportedComplete = false;
                    // Drops whatever they were doing, exactly as drafting does, so the order takes
                    // effect now rather than when the current haul finishes.
                    if (pawn.jobs != null) { pawn.jobs.EndCurrentJob(Verse.AI.JobCondition.InterruptForced); }
                },
            };
        }

        public override string CompInspectStringExtra()
        {
            return exploring ? "RR_UI_ExploreActive".Translate().ToString() : null;
        }
    }
}
