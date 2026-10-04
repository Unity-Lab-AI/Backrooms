using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Personnel
{
    /// <summary>
    /// A qualification one person holds, earned by doing the training work.
    ///
    /// **Owner direction, verbatim:** *"Add configurable company roles, staff schedules,
    /// certifications, training jobs, field history, trust/stress/exposure and equipment
    /// familiarity; preserve pawn autonomy and vanilla skill/trait systems"*. Roles, field
    /// history, exposure and equipment familiarity all shipped. **Certifications and training
    /// jobs were the remainder.**
    ///
    /// ## This is the person-level twin of a company project, and that is deliberate
    ///
    /// `RimroomsProjectDef` is the branch's ladder: insight, work and completed logs buy a named
    /// capability the whole branch has. A certification is the same idea asked of **one person** —
    /// and the distinction is the whole point of the owner's row, which lists *roles* and
    /// *certifications* as separate things. A role is what somebody is assigned to do. A
    /// certification is what they have been trained to do, and it stays with them rather than
    /// with the branch.
    ///
    /// ## The training job is a real bill, not a button
    ///
    /// *"training jobs"* is the owner's word, and a job is work somebody does. So each
    /// certification names a `RecipeDef` the player adds to a bench as an ordinary bill, exactly
    /// like `RR_AssembleMachineGate`: a pawn walks over, works, and the
    /// <see cref="RecipeWorker_RimroomsCertification"/> records the qualification against the pawn
    /// who did it. No new work giver, no new job driver, no new building — Core's bill system is
    /// already precisely this mechanism.
    ///
    /// **And Core enforces the skill floor, not this mod.** The recipe carries
    /// `skillRequirements`, so RimWorld itself refuses to let an unqualified pawn take the bill.
    /// That matters beyond tidiness: a floor checked after the work was done would mean a player
    /// could spend six thousand ticks of somebody's day and be told no at the end.
    ///
    /// ## Pawn autonomy and vanilla systems are preserved, which the row asks for explicitly
    ///
    /// Nothing here grants a skill, a trait, a hediff or a passion. A certification is a record
    /// the **company** keeps; the pawn is unchanged and gains the ordinary learning from doing the
    /// work, because the recipe declares a `workSkill` and Core handles the rest.
    /// </summary>
    public sealed class RimroomsCertificationDef : Def
    {
        /// <summary>
        /// The company role this belongs to, from <see cref="PersonnelRoles"/>.
        ///
        /// Recorded rather than enforced: a certification is **never** refused because of
        /// somebody's current assignment. People get moved between roles, and a branch that
        /// trained its engineer and then needed them on operations has not wasted the training.
        /// The role is what the readouts group by.
        /// </summary>
        public string role;

        /// <summary>The training bill that grants this. One recipe, one certification.</summary>
        public string recipeDefName;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(label))
            { yield return "A certification must have a label; a player reads it on a person."; }
            if (string.IsNullOrEmpty(description))
            { yield return "A certification must have a description; it is shown in the card."; }
            if (string.IsNullOrEmpty(role) || !PersonnelRoles.Valid(role))
            {
                yield return "RimroomsCertificationDef " + defName + " names role '"
                    + (role ?? "") + "', which is not a company role.";
            }
            // **A CERTIFICATION WITH NO TRAINING JOB CANNOT BE EARNED.** It would appear in every
            // readout as something a person might hold and there would be no way to get it, which
            // is the hollow-unlock defect the project tree already refuses.
            if (string.IsNullOrEmpty(recipeDefName))
            {
                yield return "RimroomsCertificationDef " + defName +
                    " names no training recipe, so nobody could ever earn it.";
            }
        }

        /// <summary>
        /// The certification a finished training bill grants, or null.
        ///
        /// Looked up by the recipe rather than the other way round, because that is the direction
        /// the question is asked in: the bill completes and the worker has to know what it was
        /// for. One `RecipeWorker` serves every certification this way, so adding one is a def
        /// edit and no new class.
        /// </summary>
        public static RimroomsCertificationDef ForRecipe(RecipeDef recipe)
        {
            if (recipe == null) { return null; }
            return DefDatabase<RimroomsCertificationDef>.AllDefsListForReading.FirstOrDefault(
                candidate => candidate != null
                    && string.Equals(candidate.recipeDefName, recipe.defName,
                        System.StringComparison.Ordinal));
        }

        /// <summary>
        /// Every certification, ordered so a readout cannot depend on def load order.
        ///
        /// The same rule the materials, the archetypes and the fixture tells all follow: database
        /// order changes with the installed mod list.
        /// </summary>
        public static List<RimroomsCertificationDef> AllInOrder()
        {
            return DefDatabase<RimroomsCertificationDef>.AllDefsListForReading
                .OrderBy(definition => definition.role, System.StringComparer.Ordinal)
                .ThenBy(definition => definition.defName, System.StringComparer.Ordinal)
                .ToList();
        }
    }
}
