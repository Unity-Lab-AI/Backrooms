using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// The one place a Rimrooms screen hands the player off to the rest of the game.
    ///
    /// **Owner direction, verbatim:** *"Make each screen deep-link to the relevant pawn,
    /// building, map, quest, item, research project, evidence record, contract, or RWT site"*,
    /// under the standing *"all the tabs of operations are well designed for a tripple A Mod"*.
    ///
    /// ## What was already there, and the three that were not
    ///
    /// Jumping to a **thing** worked in four places — the evidence item, the clue landmark, the
    /// recovery original and the headquarters centre — each with its own copy of the call and its
    /// own idea of what to do when the jump was impossible. A **pawn**, a **building** and a
    /// **research project** had no route out at all.
    ///
    /// The research one was the worst of the three, and it was not merely missing. The locked
    /// supply tier row printed `tier.requiredResearchDefName` **straight at the player** — an
    /// internal identifier like `MicroelectronicsBasics` — with a null action behind it. So the
    /// one screen that told somebody they needed a research project named it in a form the game
    /// never shows anywhere else and gave them no way to go and look at it.
    ///
    /// ## A link that cannot go anywhere is disabled, never silent
    ///
    /// `CameraJumper.CanJump` is asked first and the answer is handed back, so a caller can grey
    /// the row out and say why. *"A button that can only refuse is worse than no button"* is this
    /// package's own rule, from the catalogue gizmo, and a float-menu row with a null action that
    /// looks identical to one with a real action is the same defect wearing a different coat.
    /// </summary>
    internal static class OperationsLinks
    {
        /// <summary>
        /// Whether a jump to this target would actually arrive.
        ///
        /// Asked through Core's own answer rather than by testing `Spawned`, because Core also
        /// handles a pawn in a caravan, a thing held by somebody, and a target on the world map —
        /// all three of which a Rimrooms screen can be holding a reference to.
        /// </summary>
        internal static bool CanReach(GlobalTargetInfo target)
        {
            return target.IsValid && CameraJumper.CanJump(target);
        }

        /// <summary>
        /// Takes the player to a thing and selects it. A pawn and a building both come here;
        /// Core's own target adjustment is what makes one call correct for both.
        /// </summary>
        internal static void Show(GlobalTargetInfo target)
        {
            if (!CanReach(target)) { return; }
            CameraJumper.TryJumpAndSelect(target);
            // The Operations window stays where it is. Closing it would be a guess about what the
            // player wanted, and the gate's own address commands set the precedent: a link moves
            // the camera, it does not take the screen away.
        }

        /// <summary>
        /// Opens the research tab with this project selected.
        ///
        /// Core's own route: the tab is switched through `MainTabsRoot` and the window is then
        /// asked to select the project, which is the same public `Select` the research tree's own
        /// search box calls. **Nothing is set as the current project** — a deep link shows a
        /// player where something is; choosing to research it is still theirs.
        /// </summary>
        internal static void ShowResearch(ResearchProjectDef project)
        {
            if (project == null) { return; }
            MainButtonDef button = MainButtonDefOf.Research;
            if (button == null) { return; }
            Find.MainTabsRoot.SetCurrentTab(button);
            MainTabWindow_Research window = button.TabWindow as MainTabWindow_Research;
            if (window != null) { window.Select(project); }
        }

        /// <summary>
        /// The project a defName names, or null.
        ///
        /// `GetNamedSilentFail` rather than `GetNamed`, because the name can come from a def that
        /// references DLC research on a Core-only install — the same case
        /// <c>SupplyTierResearchMet</c> already handles by leaving the tier shut. A link to
        /// nothing is simply not offered.
        /// </summary>
        internal static ResearchProjectDef ResearchNamed(string defName)
        {
            return string.IsNullOrEmpty(defName)
                ? null : DefDatabase<ResearchProjectDef>.GetNamedSilentFail(defName);
        }

        /// <summary>
        /// What to call a research project on screen.
        ///
        /// **This exists because the alternative shipped.** A locked tier row printed the raw
        /// defName, which is an identifier the game shows the player nowhere else. Falls back to
        /// the defName only when the project genuinely is not loaded, where there is nothing
        /// better to say and saying nothing would make the lock unexplainable.
        /// </summary>
        internal static string ResearchLabel(string defName)
        {
            ResearchProjectDef project = ResearchNamed(defName);
            return project == null ? (defName ?? "") : project.LabelCap.ToString();
        }
    }
}
