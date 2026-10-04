using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// RR-UI: the crew and cargo planner. Row 728.
    ///
    /// Everything here is a **readout**. Nothing in this file refuses anything, and the row's own
    /// constraint is why: *"must not own connection existence"*. `Dispatch` is still the only
    /// authority on whether a crossing happens; this tells the player what it is about to say
    /// and, for the first time, **which person and which reason**.
    ///
    /// Before this, a crew of three with one problem produced `RR_Exp_InvalidCrew` — one key
    /// covering five different conditions across three people, naming none of them.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        private void DrawCrewPlanner(Listing_Standard listing, RimroomsCampaignComponent campaign,
            CompRimroomsGate gate)
        {
            listing.Label("RR_Plan_Heading".Translate());

            // Every candidate, ready or not, with the reason. Listed rather than filtered: a
            // staff member who has vanished from the list is indistinguishable from one who was
            // never hired, and the whole point is to say what is wrong.
            List<CrewPlanner.CandidateReport> candidates = CrewPlanner.Candidates(campaign, gate);
            if (candidates.Count == 0) { listing.Label("RR_Plan_NoStaff".Translate()); }
            foreach (CrewPlanner.CandidateReport candidate in candidates)
            {
                string name = candidate.Pawn == null
                    ? "RR_Plan_Missing".Translate().ToString()
                    : candidate.Pawn.LabelShortCap;
                listing.Label(candidate.Ready
                    ? "RR_Plan_RowReady".Translate(name, Kilograms(candidate.FreeMass))
                    : "RR_Plan_RowUnready".Translate(name, candidate.ReasonKey.Translate()));

                // **Staff prior exposure, said out loud.** The operator's own experience of an
                // address takes work off the dial, and a discount nobody can see is a discount
                // the player reads as noise. A novice is named a novice rather than left blank,
                // for the same reason this list shows unready candidates instead of hiding them.
                int trips = campaign.FieldTripsFor(candidate.Pawn);
                string address = gate == null ? null : gate.SpinUpCoordinateId;
                if (trips <= 0) { listing.Label("RR_Plan_ExposureNone".Translate()); }
                else if (campaign.HasBeenTo(candidate.Pawn, address))
                {
                    DrawHeading(listing,
                        heading: "RR_Plan_ExposureKnowsRouteBrief".Translate(
                            trips.ToString(CultureInfo.CurrentCulture)),
                        detail: "RR_Plan_ExposureKnowsRoute".Translate(
                            trips.ToString(CultureInfo.CurrentCulture)));
                }
                else
                {
                    listing.Label("RR_Plan_ExposureTrips".Translate(
                        trips.ToString(CultureInfo.CurrentCulture)));
                }
            }
            listing.GapLine();

            // The selected crew, as a crew. Composition is a property of the group, not of any
            // one person, which is the half of row 728 that no per-pawn check could cover.
            listing.Label("RR_Plan_SelectedCount".Translate(
                selectedCrew.Count.ToString(CultureInfo.CurrentCulture),
                CrewPlanner.MaxCrew.ToString(CultureInfo.CurrentCulture)));
            if (selectedCrew.Count > CrewPlanner.MaxCrew)
            { listing.Label("RR_Plan_TooMany".Translate()); }
            else if (selectedCrew.Count == 0)
            { listing.Label("RR_Plan_NoneSelected".Translate()); }

            foreach (SkillDef skill in CrewPlanner.ReadSkills())
            {
                int best = CrewPlanner.BestLevel(selectedCrew, skill);
                listing.Label(best < 0
                    ? "RR_Plan_SkillAbsent".Translate(skill.LabelCap)
                    : "RR_Plan_SkillBest".Translate(skill.LabelCap,
                        best.ToString(CultureInfo.CurrentCulture)));
            }
            List<SkillDef> missing = CrewPlanner.MissingSkills(selectedCrew);
            if (missing.Count > 0)
            {
                // A gap, not a refusal. A player may have good reasons to send two shooters and
                // no medic, and this mod does not get to overrule that.
                listing.Label("RR_Plan_SkillGaps".Translate(
                    string.Join(", ", missing.Select(skill => skill.LabelCap.ToString()).ToArray())));
            }

            listing.Label("RR_Plan_CargoSpace".Translate(Kilograms(CrewPlanner.FreeMass(selectedCrew))));
            listing.GapLine();

            // The window and what holding it costs. Both read off the gate, so a gate with more
            // tiers earned quotes a longer window and a larger bill without anything here
            // changing.
            listing.Label("RR_Plan_WindowHeading".Translate());
            if (gate == null || !gate.IsDesignated)
            {
                listing.Label("RR_Plan_NoGate".Translate());
                return;
            }
            if (gate.PortalOpeningIsIndefinite)
            {
                listing.Label("RR_Plan_WindowSustained".Translate(
                    Watts(gate.OpeningPowerDrawWatts)));
            }
            else
            {
                listing.Label("RR_Plan_Window".Translate(
                    Hours(gate.PortalWindowTicksForTier),
                    gate.PortalWindowTier.ToString(CultureInfo.CurrentCulture)));
                float energy = CrewPlanner.OpeningEnergyWattDays(gate);
                listing.Label(energy < 0f
                    ? "RR_Plan_CostUnknown".Translate()
                    : "RR_Plan_Cost".Translate(WattDays(energy), Watts(gate.OpeningPowerDrawWatts)));
            }
            listing.Label("RR_Plan_Reserve".Translate(
                WattDays(gate.ReturnReserveStoredWattDays),
                WattDays(gate.EmergencyReturnCostWattDays)));
            if (gate.ReturnReserveStoredWattDays < gate.EmergencyReturnCostWattDays)
            { listing.Label("RR_Plan_ReserveShort".Translate()); }
        }

        private static string Kilograms(float mass)
        {
            return mass.ToString("F1", CultureInfo.CurrentCulture);
        }

        private static string Watts(float watts)
        {
            return watts.ToString("N0", CultureInfo.CurrentCulture);
        }

        private static string WattDays(float wattDays)
        {
            return wattDays.ToString("F1", CultureInfo.CurrentCulture);
        }

        /// <summary>
        /// Ticks as in-game hours. `GenDate.TicksPerHour` rather than a divisor written here,
        /// because a constant of our own would be a second opinion about how long an hour is.
        /// </summary>
        private static string Hours(int ticks)
        {
            return ((float)ticks / GenDate.TicksPerHour).ToString("F1", CultureInfo.CurrentCulture);
        }
    }
}
