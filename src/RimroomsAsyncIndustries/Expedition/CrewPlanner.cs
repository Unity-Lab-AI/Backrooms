using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Expedition
{
    /// <summary>
    /// Why a staff member is or is not ready to go, named, before the button is pressed.
    ///
    /// **Row 728, verbatim:** *"Add crew composition and cargo planner with
    /// skill/health/weight/gate-window checks, ready/unready reasons, and cost preview.
    /// (optional mission UI under the connected-colony contract; must not own connection
    /// existence)"*.
    ///
    /// ## Every check the row asks for was already enforced. None of them was named
    ///
    /// `Dispatch` refuses on fifteen distinct grounds, and `CheckCrew` collapses **five** of
    /// them — wrong crew size, a duplicate, cannot walk, not employed, and by extension downed,
    /// dead, in a mental break or incapable of moving — into the single key
    /// `RR_Exp_InvalidCrew`. A player who ticks two boxes and is told *"invalid crew"* cannot
    /// tell which of three people is the problem or which of five problems it is.
    ///
    /// So this is not a second set of checks. It is **the same conditions, attributed**: one
    /// reason per person, read from the same state `CheckCrew` reads, so the panel cannot say
    /// ready about somebody dispatch will refuse.
    ///
    /// ## It must not own connection existence, and it does not
    ///
    /// The row's own constraint. This class returns a **report and never a refusal** — there is
    /// no `CompanyActionResult` anywhere in it, nothing calls it from `Dispatch`, `CheckCrew` or
    /// any gate code, and removing it entirely would change no outcome in the game. `Dispatch`
    /// remains the only authority on whether a crossing happens. The proof asserts that by
    /// construction: this type is referenced from `UI/` and nowhere else.
    ///
    /// Which also means it is allowed to be wrong in the safe direction. If it ever disagreed
    /// with dispatch, the player would be told no by dispatch — never yes by dispatch after
    /// being told no here.
    /// </summary>
    public static class CrewPlanner
    {
        // **THERE IS NO CREW CAP, AND THERE NEVER SHOULD HAVE BEEN ONE.**
        //
        // Owner direction, 2026-10-06, verbatim: *"rememberber pawns can cross gate as they plkease so
        // no max number"*, and when asked where three came from: *"dont know where 3 came from"*.
        //
        // **They were right, and the provenance is the whole answer.** Three is the number of staff
        // roles the Async Industries start ships, and `SCENARIOS.md` ties a records bonus to *"all
        // three crew"* returning. That is a **scenario's starting headcount**. `MaxCrew = 3` turned it
        // into a design cap by writing it down somewhere else, and nothing anywhere ever asked the
        // owner whether a crew had a maximum size.
        //
        // **It never refused anything either**, which is why it survived unnoticed: this class's own
        // documentation says it *"returns a report and never a refusal"* and that *"removing it
        // entirely would change no outcome in the game."* So the cap was a sentence in a panel that
        // looked like a rule.
        //
        // What the planner reports now is the crew's **composition** — whether the skills a field trip
        // uses are covered — which is the half of its job that was ever real. A player may send one
        // person or everybody.
        // (No constant is declared. A cap of `int.MaxValue` is still a cap somebody can read as a
        // rule, and nothing needs the number: the absence IS the rule.)

        /// <summary>
        /// The skills a field trip actually uses, and what each one is for. Core's own skills,
        /// no new content: intellectual for the record work, medicine for a casualty, shooting
        /// for whatever follows the crew to the threshold.
        /// </summary>
        private static readonly SkillDef[] FieldSkills =
        {
            SkillDefOf.Intellectual, SkillDefOf.Medicine, SkillDefOf.Shooting,
        };

        /// <summary>One candidate, and the first reason they cannot go.</summary>
        public struct CandidateReport
        {
            public Pawn Pawn;
            public bool Ready;

            /// <summary>Keyed. Null when ready.</summary>
            public string ReasonKey;

            /// <summary>How much more this person could carry, in kilograms.</summary>
            public float FreeMass;
        }

        /// <summary>
        /// The first reason this person cannot be dispatched, or null.
        ///
        /// **Ordered most-specific first.** A downed pawn is also carrying nothing and also has
        /// spare capacity, and reporting the capacity would be true and useless. The order is
        /// the order a person reading the panel would want to hear it.
        /// </summary>
        public static CandidateReport Assess(RimroomsCampaignComponent campaign,
            CompRimroomsGate gate, Pawn pawn)
        {
            var report = new CandidateReport { Pawn = pawn, Ready = false };
            if (pawn == null) { report.ReasonKey = "RR_Plan_Missing"; return report; }

            report.FreeMass = pawn.inventory == null || !MassUtility.CanEverCarryAnything(pawn)
                ? 0f : Math.Max(0f, MassUtility.FreeSpace(pawn));

            if (pawn.Dead) { report.ReasonKey = "RR_Plan_Dead"; return report; }
            if (campaign == null || !campaign.Staff.Any(s => s.Employed && s.Pawn == pawn))
            { report.ReasonKey = "RR_Plan_NotEmployed"; return report; }
            if (gate != null && pawn == gate.AssignedOperator)
            { report.ReasonKey = "RR_Plan_IsOperator"; return report; }
            if (campaign.AwaitingDebrief(pawn))
            { report.ReasonKey = "RR_Plan_AwaitingDebrief"; return report; }
            if (pawn.Downed) { report.ReasonKey = "RR_Plan_Downed"; return report; }
            if (pawn.InMentalState) { report.ReasonKey = "RR_Plan_MentalState"; return report; }
            if (pawn.health == null ||
                !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Moving))
            { report.ReasonKey = "RR_Plan_CannotMove"; return report; }
            if (!pawn.Spawned || pawn.Map != campaign.Headquarters)
            { report.ReasonKey = "RR_Plan_NotAtHeadquarters"; return report; }
            if (pawn.carryTracker != null && pawn.carryTracker.CarriedThing != null)
            { report.ReasonKey = "RR_Plan_Hauling"; return report; }
            if (!ExpeditionCargo.CheckCapacity(pawn).Success)
            { report.ReasonKey = "RR_Plan_OverCapacity"; return report; }

            report.Ready = true;
            return report;
        }

        /// <summary>Every employed staff member, assessed, ordinally by name.</summary>
        public static List<CandidateReport> Candidates(RimroomsCampaignComponent campaign,
            CompRimroomsGate gate)
        {
            var found = new List<CandidateReport>();
            if (campaign == null) { return found; }
            foreach (StaffRecord member in campaign.Staff
                .Where(s => s != null && s.Employed && s.Pawn != null)
                .OrderBy(s => s.Name, StringComparer.Ordinal))
            {
                found.Add(Assess(campaign, gate, member.Pawn));
            }
            return found;
        }

        /// <summary>
        /// The field skills nobody in this crew has.
        ///
        /// A gap is not a refusal and is deliberately not treated as one — a player may have
        /// good reasons to send two shooters and no medic. It is information the panel had no
        /// way to show, and the only way a player could previously learn it was by needing it.
        /// </summary>
        public static List<SkillDef> MissingSkills(IEnumerable<Pawn> crew)
        {
            var missing = new List<SkillDef>();
            List<Pawn> members = (crew ?? Enumerable.Empty<Pawn>())
                .Where(pawn => pawn != null && pawn.skills != null).ToList();
            for (int index = 0; index < FieldSkills.Length; index++)
            {
                SkillDef skill = FieldSkills[index];
                if (skill == null) { continue; }
                bool held = members.Any(pawn =>
                {
                    SkillRecord record = pawn.skills.GetSkill(skill);
                    return record != null && !record.TotallyDisabled && record.Level > 0;
                });
                if (!held) { missing.Add(skill); }
            }
            return missing;
        }

        /// <summary>The best level in a skill across the crew, or -1 when nobody has it.</summary>
        public static int BestLevel(IEnumerable<Pawn> crew, SkillDef skill)
        {
            int best = -1;
            if (skill == null) { return best; }
            foreach (Pawn pawn in crew ?? Enumerable.Empty<Pawn>())
            {
                if (pawn == null || pawn.skills == null) { continue; }
                SkillRecord record = pawn.skills.GetSkill(skill);
                if (record == null || record.TotallyDisabled) { continue; }
                if (record.Level > best) { best = record.Level; }
            }
            return best;
        }

        /// <summary>The field skills this planner reads, for the panel to enumerate.</summary>
        public static IEnumerable<SkillDef> ReadSkills()
        {
            for (int index = 0; index < FieldSkills.Length; index++)
            {
                if (FieldSkills[index] != null) { yield return FieldSkills[index]; }
            }
        }

        /// <summary>How much this crew could carry between them, in kilograms.</summary>
        public static float FreeMass(IEnumerable<Pawn> crew)
        {
            float total = 0f;
            foreach (Pawn pawn in crew ?? Enumerable.Empty<Pawn>())
            {
                if (pawn == null || pawn.inventory == null) { continue; }
                if (!MassUtility.CanEverCarryAnything(pawn)) { continue; }
                total += Math.Max(0f, MassUtility.FreeSpace(pawn));
            }
            return total;
        }

        /// <summary>
        /// What holding the connection for its whole window will draw, in watt-days.
        ///
        /// Watt-days because that is the unit RimWorld already prints on a battery, so the
        /// number can be compared against the reserve without converting anything. Built from
        /// the gate's own props rather than from constants here, so tuning the gate tunes the
        /// preview.
        ///
        /// Returns -1 for a connection that does not count down. At the indefinite tier there
        /// is no total to quote, only a rate, and inventing a number for it would be worse than
        /// saying so.
        /// </summary>
        public static float OpeningEnergyWattDays(CompRimroomsGate gate)
        {
            if (gate == null) { return -1f; }
            if (gate.PortalOpeningIsIndefinite) { return -1f; }
            int ticks = gate.PortalWindowTicksForTier;
            if (ticks <= 0) { return -1f; }
            double days = (double)ticks / GenDate.TicksPerDay;
            return (float)(gate.OpeningPowerDrawWatts * days);
        }
    }
}
