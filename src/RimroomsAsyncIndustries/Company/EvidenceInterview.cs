using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Settling a disagreement between two crew accounts of the same fact.
    ///
    /// 0.12.25-dev made a second crew member's account a saved thing: corroborating if it matches
    /// the filed fact, **disputing** if it does not. Nothing resolved a dispute, which is the
    /// missing half of `TODO.md`'s *"analyze/interview/compare/review workflows"* — compare shipped
    /// and interview did not.
    ///
    /// **NOBODY IS LYING, AND THAT IS THE WHOLE DESIGN.** `RecordFieldObservation` validates a fact
    /// through `HasDisplacedMarker` **before** it ever looks for a prior observation, so a disputing
    /// account was already checked against the map and found true. Two honest accounts conflict
    /// because **the marker moved between the two observations** — silent between-visit displacement
    /// has shipped since 0.10.3-dev, and this is what it looks like from the inside.
    ///
    /// So an interview cannot be a lie detector, and this deliberately invents no reliability stat.
    /// RimWorld has none, and the register is explicit about not pretending otherwise:
    ///
    ///     "Keep the company's evaluation based on actual pawn traits, skills, and relationships."
    ///
    /// What an interview does is decide **which account the company files**, which is a corporation
    /// choosing its version of events. The other account is never deleted: it stays on the record
    /// with its witness named, because an evidence chain that discards inconvenient testimony is
    /// worth nothing.
    ///
    /// The register's other instruction on this is honoured by construction:
    ///
    ///     "Keep custody, casework, and interview goals reachable through vanilla prisoner controls."
    ///
    /// **No prisoner mechanic is touched.** These are employed staff giving accounts to a colleague.
    /// Nothing detains anybody, and nothing here can be reached through a prisoner interaction.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// The Social skill a staff member needs to take a statement the company will file.
        ///
        /// Four, matching the Intellectual 4 the analysis workflow already asks for, so the two
        /// desk jobs in this campaign ask comparable things of a pawn. A real skill on a real pawn,
        /// per the register.
        /// </summary>
        public const int MinimumInterviewerSocial = 4;

        /// <summary>
        /// Who the company would send, or null if nobody can go.
        ///
        /// The most socially capable employed staff member who is not one of the people being
        /// interviewed. Deterministic on ties by load id, because a readout that names a different
        /// interviewer each frame is a readout nobody trusts — and invariant 26: sort before
        /// choosing.
        /// </summary>
        public Pawn InterviewerFor(EvidenceObservationRecord observation)
        {
            if (observation == null) { return null; }
            var speakers = new HashSet<string>(observation.WitnessLoadIds, StringComparer.Ordinal);
            Pawn best = null;
            int bestSkill = -1;
            string bestId = null;
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn candidate = member.pawn;
                if (!CanInterview(candidate)) { continue; }
                string loadId = candidate.GetUniqueLoadID();
                if (speakers.Contains(loadId)) { continue; }
                int skill = candidate.skills.GetSkill(SkillDefOf.Social).Level;
                if (skill < MinimumInterviewerSocial) { continue; }
                if (skill > bestSkill || (skill == bestSkill &&
                    string.Compare(loadId, bestId, StringComparison.Ordinal) < 0))
                {
                    best = candidate;
                    bestSkill = skill;
                    bestId = loadId;
                }
            }
            return best;
        }

        private static bool CanInterview(Pawn pawn)
        {
            return pawn != null && !pawn.Dead && !pawn.Destroyed && pawn.Spawned && !pawn.Downed &&
                !pawn.InMentalState && pawn.Faction == Faction.OfPlayer && pawn.skills != null &&
                pawn.health != null && pawn.health.capacities.CapableOf(PawnCapacityDefOf.Talking);
        }

        /// <summary>
        /// File one account as the company's version of a disputed fact.
        ///
        /// Every clause here can refuse, which invariant 136 requires: a workflow whose checks
        /// cannot fail is a workflow that has not been thought about. In particular an **analysed**
        /// record refuses, because its report is frozen and reopening a filed conclusion would make
        /// the snapshot disagree with the record it was taken from.
        /// </summary>
        public CompanyActionResult SettleDisputedAccount(EvidenceRecord record,
            EvidenceObservationRecord observation, string filedWitnessLoadId, Pawn interviewer)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Interview_Inactive"); }
            if (record == null || !evidence.Any(e => ReferenceEquals(e, record)) ||
                observation == null || record.observations == null ||
                !record.observations.Any(o => ReferenceEquals(o, observation)))
            { return CompanyActionResult.Refused("RR_Interview_RecordUnavailable"); }

            // A frozen report is the company's filed conclusion. It does not get reopened.
            if (record.analyzedTick >= 0 || record.analysisReport != null)
            { return CompanyActionResult.Refused("RR_Interview_RecordClosed"); }

            if (!observation.Disputed) { return CompanyActionResult.Refused("RR_Interview_NotDisputed"); }
            if (observation.Settled) { return CompanyActionResult.Existing(); }

            if (string.IsNullOrWhiteSpace(filedWitnessLoadId) ||
                !observation.WitnessLoadIds.Contains(filedWitnessLoadId, StringComparer.Ordinal))
            { return CompanyActionResult.Refused("RR_Interview_NoSuchAccount"); }

            // The person whose account is being filed has to still be here to stand behind it.
            Pawn speaker = observation.PawnForAccount(filedWitnessLoadId);
            if (speaker == null || speaker.Dead || speaker.Destroyed || !IsEmployedPawn(speaker))
            { return CompanyActionResult.Refused("RR_Interview_WitnessUnavailable"); }

            if (!CanInterview(interviewer) || !IsEmployedPawn(interviewer))
            { return CompanyActionResult.Refused("RR_Interview_InterviewerUnavailable"); }
            string interviewerId = interviewer.GetUniqueLoadID();
            if (observation.WitnessLoadIds.Contains(interviewerId, StringComparer.Ordinal))
            { return CompanyActionResult.Refused("RR_Interview_InterviewerIsWitness"); }
            if (interviewer.skills.GetSkill(SkillDefOf.Social).Level < MinimumInterviewerSocial)
            { return CompanyActionResult.Refused("RR_Interview_InterviewerUnskilled"); }

            observation.Settle(filedWitnessLoadId, interviewer, interviewerId,
                Find.TickManager.TicksGame);
            RecordEvent("RR_Event_AccountFiled", record.coordinateId,
                speaker.LabelShortCap.ToString(), interviewer.LabelShortCap.ToString());
            return CompanyActionResult.Applied();
        }

        /// <summary>Every fact on this record that two crew disagree about and nobody has settled.</summary>
        public IEnumerable<EvidenceObservationRecord> UnsettledDisputes(EvidenceRecord record)
        {
            if (record == null || record.observations == null) { yield break; }
            for (int index = 0; index < record.observations.Count; index++)
            {
                EvidenceObservationRecord observation = record.observations[index];
                if (observation != null && observation.Disputed && !observation.Settled)
                { yield return observation; }
            }
        }
    }
}
