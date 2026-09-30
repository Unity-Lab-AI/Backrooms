using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// One crew member who has come home and not yet reported in.
    ///
    /// Carries the load id and the name beside the live reference, exactly as
    /// <c>WitnessAccountRecord</c> does, so a hold reads correctly in a save whose pawns are not
    /// loaded and survives a pawn being despawned, carried or killed.
    /// </summary>
    public sealed class DebriefHold : IExposable
    {
        internal Pawn crew;
        internal string crewLoadId;
        internal string crewName;
        internal string coordinateId;
        internal int tick = -1;

        public Pawn Crew { get { return crew; } }
        public string CrewLoadId { get { return crewLoadId; } }
        public string CrewName { get { return crewName; } }
        public string CoordinateId { get { return coordinateId; } }
        public int Tick { get { return tick; } }

        internal bool IsValid
        {
            get { return !string.IsNullOrWhiteSpace(crewLoadId) && tick >= 0; }
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref crew, "rr_debriefCrew", true);
            Scribe_Values.Look(ref crewLoadId, "rr_debriefCrewLoadId");
            Scribe_Values.Look(ref crewName, "rr_debriefCrewName");
            Scribe_Values.Look(ref coordinateId, "rr_debriefCoordinateId");
            Scribe_Values.Look(ref tick, "rr_debriefTick", -1);
        }
    }

    /// <summary>
    /// **Staff debrief, and quarantine, which turned out to be the same mechanism.**
    ///
    /// The last two halves of row 761. They are built together because building them apart would
    /// have meant inventing something for quarantine to be about.
    ///
    /// ## Quarantine cannot be medical here, and that is a measurement rather than an opinion
    ///
    /// The obvious reading of *"quarantine"* is *hold somebody until an infection clears*. This
    /// package has **no `HediffDefs` folder at all** — measured, not assumed — so there is no
    /// exposure, contamination or illness of this mod's own to clear. Inventing one would be new
    /// gameplay content, which the standing existing-content-only constraint forbids, and it would
    /// also duplicate what Core's own health system already does to anybody who comes back hurt.
    ///
    /// So quarantine here is the **other** thing the word means in a company that sends people
    /// into places it does not understand: **you do not go back out until you have reported in.**
    /// That gives the debrief a consequence, gives quarantine a mechanism, and invents nothing.
    ///
    /// ## Where the hold bites, and where it deliberately does not
    ///
    /// It bites on <c>Dispatch</c>, beside the kit check — the company will not **send** an
    /// undebriefed crew member out again.
    ///
    /// It does **not** bite on `PortalTraversalPolicy`. That was the first instinct and it is
    /// wrong: traversal is the chokepoint every crossing in the mod passes through, including a
    /// player walking one colonist through a door by hand, and a company procedure has no business
    /// refusing that. A player who wants somebody on the far side can always put them there. What
    /// the company controls is whether it **dispatches an expedition**, and that is exactly the
    /// scope of a quarantine rule.
    ///
    /// ## What raises a hold
    ///
    /// `Complete(run)` — the moment an expedition's whole crew is back at the headquarters. That
    /// is the one place in the code where *"they came home"* is already known, so nothing new has
    /// to detect it. A stranded, aborted or abandoned trip raises nothing: those people either are
    /// not home or are the subject of a different procedure.
    ///
    /// ## What a debrief needs, and why it reuses the interview floor
    ///
    /// Somebody else has to take the report, and they have to be able to take it. The Social floor
    /// is <see cref="RimroomsCampaignComponent.InterviewerSocialFloor"/> — **the same floor
    /// witness interviews use**, which already drops when the branch has completed
    /// `RR_Measurement_StatementDiscipline`. One floor for both, because a branch that has
    /// practised taking statements has practised taking statements; a second number here would be
    /// a second opinion about the same capability.
    ///
    /// **Nobody debriefs themselves.** That is the whole point of a debrief, and it is the first
    /// refusal.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py family "staff psychology"` — one of the seven families the register retro
    /// sweep has not reached, so its rows were read directly here rather than through the sweep.
    /// Their shared instruction is to *"use the active trait, memory, social-fight, relationship,
    /// conversion, and faction-reaction rules when generating applicants, workplace incidents, and
    /// crew histories"* and to *"keep the company's evaluation based on actual pawn traits, skills
    /// and relationships"*, with the watch *"preserve native jobs, needs, guest/faction ownership,
    /// and social behavior"*.
    ///
    /// That is honoured by what this deliberately does **not** do: **no thought, no mood effect and
    /// no hediff.** A debrief that handed out a `ThoughtDef` would be this mod writing a social
    /// consequence on top of mods whose whole job is social consequence, and it would need a new
    /// def. The only thing a debrief changes is whether the company will send that person out
    /// again — a company rule about a company decision, which is the one thing no other mod owns.
    /// The Social skill is read and never written, so a trait or relationship mod changes who is
    /// good at taking a report and nothing else.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        private List<DebriefHold> debriefHolds = new List<DebriefHold>();

        /// <summary>
        /// A cap, because this is a saved list that grows on every returned trip. Reached only by
        /// a branch that has brought home more than this many people and debriefed none of them,
        /// at which point the oldest hold is dropped rather than the list being allowed to grow
        /// without bound. Dropping the oldest is the right way round: the newest report is the one
        /// still worth hearing.
        /// </summary>
        private const int MaximumDebriefHolds = 64;

        public IReadOnlyList<DebriefHold> DebriefHolds { get { return debriefHolds; } }

        /// <summary>
        /// Whether this crew member owes the company a report. Read by expedition dispatch, and by
        /// the pane so a player can see who is waiting.
        /// </summary>
        public bool AwaitingDebrief(Pawn pawn)
        {
            return HoldFor(pawn) != null;
        }

        internal DebriefHold HoldFor(Pawn pawn)
        {
            if (pawn == null || debriefHolds == null) { return null; }
            string loadId = pawn.GetUniqueLoadID();
            for (int index = 0; index < debriefHolds.Count; index++)
            {
                DebriefHold hold = debriefHolds[index];
                if (hold == null || !hold.IsValid) { continue; }
                if (hold.crew == pawn ||
                    string.Equals(hold.crewLoadId, loadId, StringComparison.Ordinal))
                { return hold; }
            }
            return null;
        }

        /// <summary>
        /// Raise a hold for everybody who just came home. Called from expedition completion,
        /// which is the one place that fact is already established.
        ///
        /// Idempotent per pawn: completing twice, or a save reloaded across a completion, cannot
        /// stack two holds on one person.
        /// </summary>
        internal void NoteReturnedFromField(IEnumerable<Pawn> crew, string coordinateId)
        {
            if (crew == null) { return; }
            debriefHolds = debriefHolds ?? new List<DebriefHold>();
            foreach (Pawn pawn in crew)
            {
                if (pawn == null || pawn.Dead || pawn.Destroyed) { continue; }
                if (HoldFor(pawn) != null) { continue; }
                debriefHolds.Add(new DebriefHold
                {
                    crew = pawn,
                    crewLoadId = pawn.GetUniqueLoadID(),
                    crewName = pawn.LabelShortCap,
                    coordinateId = coordinateId,
                    tick = Find.TickManager == null ? 0 : Find.TickManager.TicksGame
                });
                while (debriefHolds.Count > MaximumDebriefHolds) { debriefHolds.RemoveAt(0); }
            }
        }

        /// <summary>
        /// Why this crew member cannot be debriefed by this interviewer right now, or null.
        ///
        /// Separated from <see cref="DebriefCrewMember"/> so the surface can disable a button and
        /// show the reason rather than letting a player click and be told no — invariant 28, the
        /// rule has to be learnable.
        /// </summary>
        public string DebriefBlocker(Pawn crewMember, Pawn interviewer)
        {
            if (!CanOperate) { return "RR_Company_Unavailable"; }
            if (crewMember == null || interviewer == null) { return "RR_Debrief_NobodyToReport"; }
            if (HoldFor(crewMember) == null) { return "RR_Debrief_NothingToReport"; }
            // The whole point of a debrief. Also the only refusal that can never be worked around
            // by waiting, which is why it is first.
            if (interviewer == crewMember) { return "RR_Debrief_SelfReport"; }
            if (interviewer.Dead || interviewer.Destroyed || !interviewer.Spawned)
            { return "RR_Debrief_NobodyToReport"; }
            if (!interviewer.IsColonist) { return "RR_Debrief_NotStaff"; }
            if (interviewer.Downed || interviewer.InMentalState)
            { return "RR_Debrief_InterviewerUnfit"; }
            if (interviewer.Map == null || !OwnsMap(interviewer.Map))
            { return "RR_Debrief_NotOurs"; }
            // Home, not the far side. A report given standing in the room you are reporting about
            // is not a debrief, and the crew member has to actually be back.
            if (crewMember.Map == null || crewMember.Map != Headquarters)
            { return "RR_Debrief_NotHome"; }
            if (crewMember.Dead || crewMember.Destroyed) { return "RR_Debrief_NothingToReport"; }
            if (interviewer.Map != crewMember.Map) { return "RR_Debrief_NotTogether"; }
            if (interviewer.skills == null) { return "RR_Debrief_InterviewerUnfit"; }
            SkillRecord social = interviewer.skills.GetSkill(SkillDefOf.Social);
            if (social == null || social.TotallyDisabled ||
                social.Level < InterviewerSocialFloor)
            { return "RR_Debrief_InterviewerUnskilled"; }
            return null;
        }

        /// <summary>
        /// Take the report. Clears the hold and records that it happened.
        ///
        /// Records nothing about *what* was said, deliberately: the field observations were
        /// already written down where they were made, by `RecordFieldObservation`, and a second
        /// account written here would be a second source of truth about the same trip. This
        /// records only that the report was given, by whom, to whom — which is the thing that was
        /// missing.
        /// </summary>
        public CompanyActionResult DebriefCrewMember(Pawn crewMember, Pawn interviewer)
        {
            string blocker = DebriefBlocker(crewMember, interviewer);
            if (blocker != null) { return CompanyActionResult.Refused(blocker); }
            DebriefHold hold = HoldFor(crewMember);
            if (hold == null) { return CompanyActionResult.Refused("RR_Debrief_NothingToReport"); }
            debriefHolds.Remove(hold);
            RecordEvent("RR_Event_StaffDebriefed", crewMember.GetUniqueLoadID());
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Every held crew member who is at the headquarters and could be debriefed now. Used by
        /// the pane; the blocker is still asked per pair, because who is available to take the
        /// report is not a property of the person giving it.
        /// </summary>
        public IEnumerable<DebriefHold> OutstandingDebriefs()
        {
            if (debriefHolds == null) { yield break; }
            for (int index = 0; index < debriefHolds.Count; index++)
            {
                DebriefHold hold = debriefHolds[index];
                if (hold != null && hold.IsValid) { yield return hold; }
            }
        }

        private void ExposeDebriefs()
        {
            Scribe_Collections.Look(ref debriefHolds, "rr_debriefHolds", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                debriefHolds = debriefHolds ?? new List<DebriefHold>();
                // A hold whose pawn is gone from the save is dropped rather than kept as a row
                // that can never be cleared and would block dispatch forever.
                debriefHolds.RemoveAll(hold => hold == null || !hold.IsValid);
            }
        }
    }
}
