using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What a branch has to have done before the corporation will take its call.
    ///
    /// Owner direction, given while this was being built, verbatim: *"once they "contact the
    /// cvompany in comms" they can start async quest line"*.
    ///
    /// The chart calls reaching contact **the achievement** for the two starts that open without
    /// it, so the call cannot be a free button on a console somebody built on day one. What it
    /// asks for is the whole first loop, done once:
    ///
    ///   * a **powered** comms console, operated by somebody who can work it;
    ///   * a coordinate the branch has actually been into;
    ///   * an **analysed** record — which means a crew found the place, went in with a book,
    ///     came home with it, and somebody sat down and read it.
    ///
    /// That last one is the whole of `RR_GateTelemetry`'s prerequisite chain in miniature, and it
    /// is the thing that makes the call worth taking: **you are not asking for help, you are
    /// telling them you have something.**
    ///
    /// Every clause refuses separately with its own reason, per invariant 136, and the gizmo shows
    /// that reason on a disabled button rather than hiding itself — a player should be able to see
    /// what the call is waiting for.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Why the call cannot be placed, or null when it can.
        ///
        /// Returned as a keyed string so the gizmo, the action and any future readout all say the
        /// same thing. Checked live, because every condition can change minute to minute.
        /// </summary>
        public string CorporationCallBlocker(Thing console)
        {
            if (!CanOperate) { return "RR_Contact_Inactive"; }
            if (corporationContact) { return "RR_Contact_AlreadyInContact"; }

            if (console == null || !console.Spawned || console.Map == null ||
                !(console is Building_CommsConsole) || console.Faction != Faction.OfPlayer)
            { return "RR_Contact_NoConsole"; }
            if (!OwnsMap(console.Map)) { return "RR_Contact_NotOurs"; }
            CompPowerTrader power = console.TryGetComp<CompPowerTrader>();
            if (power != null && !power.PowerOn) { return "RR_Contact_Unpowered"; }

            if (!AnyEmployedOperator(console.Map)) { return "RR_Contact_NoOperator"; }
            if (coordinates.Count == 0) { return "RR_Contact_NoCoordinate"; }
            if (!AnyAnalysedRecord()) { return "RR_Contact_NoFinding"; }
            return null;
        }

        /// <summary>
        /// Place the call. One-way, like the state it sets.
        ///
        /// Re-checks every condition rather than trusting the gizmo that offered it: a button can
        /// be clicked on the same tick the generator goes off.
        /// </summary>
        public CompanyActionResult CallTheCorporation(Thing console)
        {
            string blocker = CorporationCallBlocker(console);
            if (blocker != null) { return CompanyActionResult.Refused(blocker); }

            CompanyActionResult result = EstablishCorporationContact();
            if (!result.Success) { return result; }

            // Said out loud, once. The tutorial line will start offering on the company's next
            // cadence tick and the player should know why their screen is about to change.
            Messages.Message("RR_Contact_Established".Translate(CompanyName),
                MessageTypeDefOf.PositiveEvent, false);
            return result;
        }

        /// <summary>Somebody employed here who could actually work a console.</summary>
        private bool AnyEmployedOperator(Map map)
        {
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn pawn = member.pawn;
                if (pawn == null || pawn.Dead || pawn.Destroyed || !pawn.Spawned) { continue; }
                if (pawn.Map != map || pawn.Downed || pawn.InMentalState) { continue; }
                if (pawn.health == null ||
                    !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Talking)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// A record somebody has finished reading.
        ///
        /// `analyzedTick` rather than the analysis report, because the report is a snapshot taken
        /// at completion and a legacy save can carry a completed analysis without one.
        /// </summary>
        private bool AnyAnalysedRecord()
        {
            for (int index = 0; index < evidence.Count; index++)
            {
                EvidenceRecord record = evidence[index];
                if (record != null && record.analyzedTick >= 0) { return true; }
            }
            return false;
        }
    }
}
