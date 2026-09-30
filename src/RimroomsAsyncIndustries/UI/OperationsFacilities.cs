using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Facilities;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private readonly FacilityReport facilityReport = new FacilityReport();
        private string facilityCategory;
        private int facilityPage;

        /// <summary>
        /// What the branch is holding across every map it owns, and the standing order for a
        /// breach.
        ///
        /// Deliberately **not** limited to the headquarters, unlike the rest of this pane. The
        /// facility report is an HQ readiness report and that is right for beds and benches; a
        /// containment count that stopped at the HQ would hide the exact thing
        /// <see cref="Threats.ContainmentWatch"/> exists to surface — a platform on a
        /// coordinate you are not looking at.
        ///
        /// It reads `ContainmentWatch` rather than counting holders itself, so the pane, the
        /// two alerts and the procedure cannot disagree about how many subjects are held.
        /// </summary>
        private void DrawContainment(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            List<Threats.ContainmentWatch.HolderState> holders =
                Threats.ContainmentWatch.OccupiedHolders();
            int escaping = 0;
            int unpowered = 0;
            for (int index = 0; index < holders.Count; index++)
            {
                if (holders[index].Escaping) { escaping++; }
                else if (holders[index].Unpowered) { unpowered++; }
            }
            listing.Label("RR_Containment_Held".Translate(holders.Count));
            if (escaping > 0) { listing.Label("RR_Containment_Escaping".Translate(escaping)); }
            if (unpowered > 0) { listing.Label("RR_Containment_Unpowered".Translate(unpowered)); }

            // The standing order, said out loud in both states. A procedure the player cannot
            // read is a procedure they cannot plan around, and this one closes connections.
            bool cut = ContainmentProtocol.CutOnBreach(campaign);
            listing.Label(cut ? "RR_Containment_ProcedureOn".Translate()
                : "RR_Containment_ProcedureOff".Translate());
            if (listing.ButtonText(cut ? "RR_Containment_Disarm".Translate()
                : "RR_Containment_Arm".Translate()))
            {
                CompanyActionResult result = ContainmentProtocol.SetCutOnBreach(campaign, !cut);
                if (!result.Success)
                {
                    Messages.Message(result.MessageKey.Translate(),
                        MessageTypeDefOf.RejectInput, false);
                }
            }
        }

        /// <summary>
        /// Who has come home and not reported in, and the button that takes the report.
        ///
        /// The interviewer is chosen here rather than by the player, from the colonists standing
        /// on the same map, highest Social first with ties broken on load id so the choice is
        /// deterministic and a reload cannot change who took the report. The same rule witness
        /// interviews use.
        ///
        /// Every row is drawn whether or not it can be actioned, with the refusal on the button,
        /// because *"nobody here is good enough at talking to take this report"* is exactly the
        /// thing a player needs told.
        /// </summary>
        private void DrawDebriefs(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            var holds = campaign.OutstandingDebriefs().ToList();
            if (holds.Count == 0)
            { listing.Label("RR_Debrief_NoneOutstanding".Translate()); return; }
            listing.Label("RR_Debrief_Outstanding".Translate(holds.Count));
            foreach (Company.DebriefHold hold in holds.Take(8))
            {
                Pawn crewMember = hold.Crew;
                string name = string.IsNullOrEmpty(hold.CrewName)
                    ? "RR_Debrief_UnknownStaff".Translate().ToString() : hold.CrewName;
                Pawn interviewer = DebriefInterviewerFor(campaign, crewMember);
                string blocker = campaign.DebriefBlocker(crewMember, interviewer);
                if (blocker != null)
                {
                    listing.Label("RR_Debrief_Row".Translate(name, blocker.Translate()));
                    continue;
                }
                if (listing.ButtonText("RR_Debrief_Take".Translate(name,
                    interviewer.LabelShortCap)))
                {
                    CompanyActionResult result =
                        campaign.DebriefCrewMember(crewMember, interviewer);
                    if (!result.Success)
                    {
                        Messages.Message(result.MessageKey.Translate(),
                            MessageTypeDefOf.RejectInput, false);
                    }
                }
            }
        }

        /// <summary>
        /// The most capable colleague standing where this crew member is, or null. Never the crew
        /// member themselves -- <c>DebriefBlocker</c> refuses that anyway, but offering it would
        /// put a button on the screen whose only possible outcome is a refusal.
        /// </summary>
        private static Pawn DebriefInterviewerFor(RimroomsCampaignComponent campaign,
            Pawn crewMember)
        {
            if (crewMember == null || crewMember.Map == null) { return null; }
            return crewMember.Map.mapPawns.FreeColonistsSpawned
                .Where(candidate => candidate != null && candidate != crewMember &&
                    !candidate.Downed && !candidate.InMentalState && candidate.skills != null)
                .OrderByDescending(candidate =>
                {
                    SkillRecord skill = candidate.skills.GetSkill(SkillDefOf.Social);
                    return skill == null || skill.TotallyDisabled ? -1 : skill.Level;
                })
                .ThenBy(candidate => candidate.ThingID, StringComparer.Ordinal)
                .FirstOrDefault();
        }

        /// <summary>
        /// Which optional mods this package has a recorded position on are loaded, and what that
        /// position is.
        ///
        /// Rows 764, 765, 766 and 784. The register forbids patching any of them -- *"no patch
        /// or code/assets copied"* for both gravship chapters, *"do not add vehicles solely
        /// because the framework is installed"* for the vehicle framework -- so what a hook can
        /// honestly be is this: **a statement, in the game, of what is installed and what this
        /// mod does about it.** Until now that answer lived only in a register HTML file outside
        /// the game.
        ///
        /// **Every line ends with the same caveat and that is deliberate.** No game has ever
        /// been launched from this repository, so *"supported"* is a claim nobody has earned and
        /// row 791 forbids exactly that kind of statement. The readout says *installed* and
        /// *untested in play*, separately, because they are different facts.
        ///
        /// The links are `OpenNativeTab`, the same helper the bed summary above uses: row 765
        /// asks for *"operations links"* and a button that opens the game's own surface is the
        /// whole of that, with nothing patched.
        /// </summary>
        private void DrawIntegrations(Listing_Standard listing)
        {
            System.Collections.Generic.IReadOnlyList<Core.IntegrationState> tracked =
                Core.InstalledIntegrations.AllInOrder();
            listing.Label("RR_Integration_Heading".Translate(
                Core.InstalledIntegrations.ActiveCount(), tracked.Count));
            listing.Label("RR_Integration_Caveat".Translate());
            for (int index = 0; index < tracked.Count; index++)
            {
                Core.IntegrationState state = tracked[index];
                string name = state.NameKey.Translate();
                listing.Label(state.Active
                    ? "RR_Integration_RowActive".Translate(name, state.RegisterRow)
                    : "RR_Integration_RowAbsent".Translate(name, state.RegisterRow));
                // The position is said in both states on purpose: a player deciding whether to
                // install one of these needs to know what this mod will do with it beforehand.
                listing.Label(state.PositionKey.Translate());
            }
            if (listing.ButtonText("RR_Integration_OpenWorld".Translate()))
            { OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("World")); }
        }

        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            if (!FacilityReport.Available(campaign.Headquarters))
            { listing.Label("RR_Company_MapUnavailable".Translate()); return; }
            facilityReport.RefreshIfNeeded(campaign);
            listing.Label("RR_Fac_Explanation".Translate());
            if (listing.ButtonText("RR_Fac_Refresh".Translate())) { facilityReport.RefreshIfNeeded(campaign, true); }
            listing.Label("RR_Fac_SummaryAge".Translate(Math.Max(0, Find.TickManager.TicksGame - facilityReport.CapturedTick)));
            listing.Label("RR_Fac_BedSummary".Translate(facilityReport.OrdinaryBedSlots,
                facilityReport.OrdinaryBedOwners, facilityReport.OrdinaryBedOccupants));
            listing.Label("RR_Fac_OtherBeds".Translate(facilityReport.MedicalSlots, facilityReport.OtherBedSlots));
            listing.Label("RR_Fac_BedLimit".Translate());
            if (facilityReport.StaffWithoutOwnedBeds.Count > 0)
            { listing.Label("RR_Fac_UnassignedStaff".Translate(string.Join(", ", facilityReport.StaffWithoutOwnedBeds.ToArray()))); }
            if (facilityReport.StaffNeedingCare.Count > 0)
            { listing.Label("RR_Fac_CareStaff".Translate(string.Join(", ", facilityReport.StaffNeedingCare.ToArray()))); }
            if (facilityReport.RefreshErrors > 0) { listing.Label("RR_Fac_ObservationErrors".Translate(facilityReport.RefreshErrors)); }
            if (listing.ButtonText("RR_Fac_OpenAssignments".Translate()))
            { OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign")); }
            listing.GapLine();
            DrawContainment(listing, campaign);
            listing.GapLine();
            DrawDebriefs(listing, campaign);
            listing.GapLine();
            DrawIntegrations(listing);
            listing.GapLine();

            string filter = facilityCategory == null ? "RR_Fac_All".Translate().ToString() :
                facilityCategory == "" ? "RR_Fac_Unclassified".Translate().ToString() :
                DefDatabase<RimroomsFacilityCategoryDef>.GetNamedSilentFail(facilityCategory)?.LabelCap.ToString() ?? facilityCategory;
            if (listing.ButtonText("RR_Fac_Filter".Translate(filter)))
            {
                var options = new List<FloatMenuOption> { new FloatMenuOption("RR_Fac_All".Translate(), () => SetFacilityFilter(null)) };
                foreach (RimroomsFacilityCategoryDef definition in DefDatabase<RimroomsFacilityCategoryDef>.AllDefsListForReading.OrderBy(d => d.displayOrder))
                {
                    string id = definition.defName;
                    int count = facilityReport.Buildings.Count(b => b.CategoryId == id);
                    options.Add(new FloatMenuOption(definition.LabelCap + " (" + count + ")", () => SetFacilityFilter(id)));
                }
                options.Add(new FloatMenuOption("RR_Fac_Unclassified".Translate(), () => SetFacilityFilter("")));
                Find.WindowStack.Add(new FloatMenu(options));
            }
            // What the chosen category is actually for. Owner direction 2026-09-29: "all mod
            // ingame decriptions and informational informations for everything is properly in
            // the cards like the game does currently". A row of bare nouns tells a player
            // nothing the word did not already tell them.
            RimroomsFacilityCategoryDef chosen = string.IsNullOrEmpty(facilityCategory) ? null
                : DefDatabase<RimroomsFacilityCategoryDef>.GetNamedSilentFail(facilityCategory);
            if (chosen != null && !string.IsNullOrEmpty(chosen.description))
            { listing.Label(chosen.description); }
            List<FacilityBuildingObservation> rows = facilityReport.Buildings.Where(b => facilityCategory == null ||
                (b.CategoryId ?? "") == facilityCategory).ToList();
            const int pageSize = 12;
            int pages = Math.Max(1, (rows.Count + pageSize - 1) / pageSize);
            facilityPage = Math.Max(0, Math.Min(facilityPage, pages - 1));
            listing.Label("RR_Fac_Page".Translate(facilityPage + 1, pages, rows.Count));
            if (facilityPage > 0 && listing.ButtonText("RR_Fac_Previous".Translate())) { facilityPage--; }
            if (facilityPage + 1 < pages && listing.ButtonText("RR_Fac_Next".Translate())) { facilityPage++; }
            if (rows.Count == 0) { listing.Label("RR_Fac_None".Translate()); }
            foreach (FacilityBuildingObservation row in rows.Skip(facilityPage * pageSize).Take(pageSize))
            {
                listing.GapLine();
                listing.Label(row.Label);
                listing.Label("RR_Fac_Condition".Translate(row.HitPoints, row.MaxHitPoints));
                if (row.HasRoom)
                {
                    string temperature = float.IsNaN(row.Temperature) || float.IsInfinity(row.Temperature)
                        ? "RR_Fac_Unavailable".Translate().ToString() : row.Temperature.ToString("F1") + " °C";
                    listing.Label("RR_Fac_Room".Translate(row.RoomLabel, row.RoomCells, row.UnroofedCells, temperature));
                    if (row.Outdoors) { listing.Label("RR_Fac_OutdoorTemperature".Translate()); }
                }
                else { listing.Label("RR_Fac_NoRoom".Translate()); }
                if (row.PowerOn.HasValue)
                { listing.Label((row.PowerOn.Value ? "RR_Fac_Powered" : "RR_Fac_Unpowered").Translate()); }
                if (row.InteractionCellClear.HasValue)
                { listing.Label((row.InteractionCellClear.Value ? "RR_Fac_InteractionClear" : "RR_Fac_InteractionBlocked").Translate()); }
                if (row.BedTypeKey != null)
                { listing.Label("RR_Fac_BedRow".Translate(row.BedTypeKey.Translate(), row.BedSlots, row.BedOwners, row.BedOccupants)); }
                Building target = row.Building;
                if (listing.ButtonText("RR_Fac_Inspect".Translate(row.Label)))
                {
                    if (FacilityReport.Inspectable(target, campaign.Headquarters)) { CameraJumper.TryJumpAndSelect(target); }
                    else { Messages.Message("RR_Fac_TargetUnavailable".Translate(), MessageTypeDefOf.RejectInput, false); }
                }
                if (FacilityReport.Inspectable(target, campaign.Headquarters) && target.TryGetComp<CompRimroomsGate>()?.IsDesignated == true &&
                    listing.ButtonText("RR_Fac_OpenMachine".Translate())) { selectedPane = 7; scrollPosition = UnityEngine.Vector2.zero; }
            }
        }

        private void SetFacilityFilter(string id)
        { facilityCategory = id; facilityPage = 0; scrollPosition = UnityEngine.Vector2.zero; }
    }
}
