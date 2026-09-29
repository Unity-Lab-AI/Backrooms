using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>Selected people are native-owned. This is a receipt, never a pawn generator or holder.</summary>
    public sealed class RimroomsStartupComponent : GameComponent
    {
        private int schemaVersion = 1;
        private string startDefName;
        private bool accepted;
        private PlanetTile selectedTile = PlanetTile.Invalid;
        private List<Pawn> selected = new List<Pawn>();
        private List<string> pawnIds = new List<string>();
        private List<string> roles = new List<string>();
        private List<string> supplySummary = new List<string>();
        private string companyName;
        public bool Accepted { get { return accepted && schemaVersion == 1; } }
        public IReadOnlyList<string> SupplySummary { get { return supplySummary.AsReadOnly(); } }
        public string CompanyName { get { return companyName; } }

        public RimroomsStartupComponent(Game game) { }

        /// <summary>
        /// The name offered at setup: the start's own suggestion, its label, or a neutral
        /// fallback. Only a suggestion — every start may replace it.
        /// </summary>
        public static string SuggestedName(RimroomsStartDef start)
        {
            if (start == null) { return "RR_Company_UnnamedCompany".Translate().ToString(); }
            if (!string.IsNullOrWhiteSpace(start.defaultCompanyName)) { return start.defaultCompanyName.Trim(); }
            return string.IsNullOrWhiteSpace(start.label)
                ? "RR_Company_UnnamedCompany".Translate().ToString() : start.label;
        }

        /// <summary>
        /// Accept a typed name, or fall back to the suggestion. Never stores an empty or
        /// over-long name, so the branch can always be referred to by something.
        /// </summary>
        private static string NormalizeName(string proposed, RimroomsStartDef start)
        {
            string trimmed = proposed == null ? null : proposed.Trim();
            if (string.IsNullOrEmpty(trimmed) ||
                trimmed.Length > RimroomsAsyncIndustries.Company.RimroomsCampaignComponent.MaximumCompanyNameLength)
            { return SuggestedName(start); }
            return trimmed;
        }

        public void Accept(RimroomsStartDef start, IList<Pawn> pawns, IList<string> assignedRoles,
            List<string> supplies, string chosenCompanyName)
        {
            startDefName = start.defName;
            companyName = NormalizeName(chosenCompanyName, start);
            selectedTile = Find.GameInitData.startingTile;
            selected = new List<Pawn>(pawns);
            pawnIds = selected.Select(p => p.GetUniqueLoadID()).ToList();
            roles = new List<string>(assignedRoles);
            supplySummary = new List<string>(supplies);
            accepted = true;
        }

        internal bool TryRead(RimroomsStartDef start, out List<Pawn> pawns, out List<string> assignedRoles)
        {
            pawns = new List<Pawn>();
            assignedRoles = new List<string>();
            List<Pawn> live;
            string reason;
            if (!Accepted || start == null || startDefName != start.defName || Find.GameInitData == null ||
                Find.GameInitData.startingTile != selectedTile ||
                !StartupReview.TrySelected(out live, out reason) || !selected.SequenceEqual(live) ||
                pawnIds.Count != selected.Count || roles.Count != selected.Count) { return false; }
            for (int i = 0; i < selected.Count; i++)
            {
                if (selected[i].GetUniqueLoadID() != pawnIds[i] || !start.roles.Any(r => r.id == roles[i])) { return false; }
            }
            pawns = new List<Pawn>(selected);
            assignedRoles = new List<string>(roles);
            return true;
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref schemaVersion, "rr_startupSchema", 1, true);
            Scribe_Values.Look(ref startDefName, "rr_setupStartDef");
            Scribe_Values.Look(ref companyName, "rr_startupCompanyName");
            Scribe_Values.Look(ref accepted, "rr_setupAccepted");
            Scribe_Values.Look(ref selectedTile, "rr_setupTile", PlanetTile.Invalid);
            Scribe_Collections.Look(ref selected, "rr_setupPawns", LookMode.Reference);
            Scribe_Collections.Look(ref pawnIds, "rr_setupPawnIds", LookMode.Value);
            Scribe_Collections.Look(ref roles, "rr_setupRoles", LookMode.Value);
            Scribe_Collections.Look(ref supplySummary, "rr_setupSupplySummary", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                selected = selected ?? new List<Pawn>();
                pawnIds = pawnIds ?? new List<string>();
                roles = roles ?? new List<string>();
                supplySummary = supplySummary ?? new List<string>();
            }
        }
    }

    internal static class StartupReview
    {
        internal static bool TrySelected(out List<Pawn> pawns, out string reason)
        {
            pawns = new List<Pawn>();
            reason = "RR_Setup_InvalidRoster";
            GameInitData init = Find.GameInitData;
            if (init == null || init.startingAndOptionalPawns == null || init.startingPawnCount < 1 ||
                init.startingPawnCount > 20 || init.startingPawnCount > init.startingAndOptionalPawns.Count) { return false; }
            // Native optional candidates are not selected staff; do not alter either native list.
            pawns = init.startingAndOptionalPawns.Take(init.startingPawnCount).ToList();
            if (pawns.Distinct().Count() != pawns.Count || pawns.Any(p => p == null || p.Destroyed || p.Dead ||
                p.RaceProps == null || !p.RaceProps.Humanlike)) { return false; }
            if (!init.startingTile.Valid) { reason = "RR_Setup_InvalidTile"; return false; }
            reason = null;
            return true;
        }

        internal static List<string> SupplySummary()
        {
            // Never call PlayerStartingThings here: that API creates actual objects.
            var lines = new List<string>();
            if (Find.Scenario != null)
            {
                foreach (ScenPart part in Find.Scenario.AllParts)
                {
                    foreach (string entry in part.GetSummaryListEntries("PlayerStartsWith"))
                    { if (!string.IsNullOrEmpty(entry)) { lines.Add(entry); } }
                    if (!(part is ScenPart_StartingThing_Defined) && !(part is ScenPart_RimroomsStart) &&
                        !(part is ScenPart_ConfigPage_ConfigureStartingPawnsBase))
                    {
                        string summary = part.Summary(Find.Scenario);
                        if (!string.IsNullOrEmpty(summary) && !lines.Contains(summary)) { lines.Add(summary); }
                    }
                }
            }
            return lines;
        }

        internal static List<string> Warnings(Pawn pawn, RimroomsStaffRole role)
        {
            var warnings = new List<string>();
            if (pawn.Downed || !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Moving) ||
                !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
            { warnings.Add("RR_Setup_LimitedCapacity".Translate().ToString()); }
            if (role.mustFight && pawn.WorkTagIsDisabled(WorkTags.Violent))
            { warnings.Add("RR_Setup_NoViolence".Translate().ToString()); }
            foreach (WorkTypeDef work in role.workTypes)
            {
                if (pawn.WorkTypeIsDisabled(work)) { warnings.Add("RR_Setup_DisabledWork".Translate(work.LabelCap).ToString()); }
            }
            foreach (SkillRequirement skill in role.skills)
            {
                SkillRecord record = pawn.skills == null ? null : pawn.skills.GetSkill(skill.skill);
                if (record == null || record.TotallyDisabled || record.Level < skill.minLevel)
                { warnings.Add("RR_Setup_AdvisorySkill".Translate(skill.skill.LabelCap, skill.minLevel).ToString()); }
            }
            return warnings;
        }
    }
}
