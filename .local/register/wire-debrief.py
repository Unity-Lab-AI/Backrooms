# -*- coding: utf-8 -*-
"""Wire staff debrief and quarantine: persistence, the completion hook, the dispatch refusal,
the pane surface and every keyed string."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


# ------------------------------------------------------------------ persistence
sub("src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs",
    u'            Scribe_Values.Look(ref breachResponded, "rr_breachResponded", false);',
    u'            Scribe_Values.Look(ref breachResponded, "rr_breachResponded", false);\n'
    u'            ExposeDebriefs();')

# ------------------------------------------------------------------ the hold is raised on return
sub("src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs",
    u"""        private void Complete(ExpeditionRecord run)
        {
            run.status = ExpeditionStatus.Completed;
            run.closedTick = Find.TickManager.TicksGame;
            CloseOwnedOpening(run);
            UpdateReturned(run);
            ExpeditionCargo.Reconcile(run);
            Notify("RR_Exp_Returned");
        }""",
    u"""        private void Complete(ExpeditionRecord run)
        {
            run.status = ExpeditionStatus.Completed;
            run.closedTick = Find.TickManager.TicksGame;
            CloseOwnedOpening(run);
            UpdateReturned(run);
            ExpeditionCargo.Reconcile(run);
            // Everybody who came home owes the company a report, and this is the one place in
            // the code where "they came home" is already established -- Complete is reached from
            // AllAtHeadquarters. Raising the hold anywhere else would mean detecting a return a
            // second way. A stranded, aborted or abandoned trip raises nothing: those people
            // either are not home or belong to a different procedure. Idempotent per pawn, so a
            // save reloaded across a completion cannot stack two holds on one person.
            Campaign.NoteReturnedFromField(run.crew, run.coordinateId);
            Notify("RR_Exp_Returned");
        }""")

# ------------------------------------------------------------------ the quarantine: dispatch refuses
sub("src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs",
    u"""            check = ExpeditionCargo.CheckKit(crew);
            if (!check.Success) { return check; }
            string id = Campaign.BranchId + ":expedition:" + Guid.NewGuid().ToString("N");""",
    u"""            check = ExpeditionCargo.CheckKit(crew);
            if (!check.Success) { return check; }
            // Quarantine, and it is the whole of it: the company will not send somebody back out
            // who has not reported in from the last trip. Deliberately here rather than in
            // PortalTraversalPolicy -- a player walking one colonist through a door by hand is
            // not a company dispatch, and a procedure has no business refusing it.
            for (int index = 0; index < crew.Count; index++)
            {
                if (Campaign.AwaitingDebrief(crew[index]))
                { return Refuse("RR_Exp_AwaitingDebrief"); }
            }
            string id = Campaign.BranchId + ":expedition:" + Guid.NewGuid().ToString("N");""")

# ------------------------------------------------------------------ the pane
sub("src/RimroomsAsyncIndustries/UI/OperationsFacilities.cs",
    u"            DrawContainment(listing, campaign);\n            listing.GapLine();",
    u"            DrawContainment(listing, campaign);\n"
    u"            listing.GapLine();\n"
    u"            DrawDebriefs(listing, campaign);\n"
    u"            listing.GapLine();")

sub("src/RimroomsAsyncIndustries/UI/OperationsFacilities.cs",
    u"        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)",
    u'''        /// <summary>
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

        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)''')

# ------------------------------------------------------------------ strings
COMPANY = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Company.xml"
sub(COMPANY, u"</LanguageData>",
    u"""
  <!-- Staff debrief, and quarantine, which is the same mechanism: you do not go back out until
       you have reported in. Row 761, last two halves. -->
  <RR_Debrief_Outstanding>Crew home and not yet debriefed: {0}. None of them will be sent out again until they have reported in.</RR_Debrief_Outstanding>
  <RR_Debrief_NoneOutstanding>Every returned crew member has reported in.</RR_Debrief_NoneOutstanding>
  <RR_Debrief_Row>{0} - cannot be debriefed: {1}</RR_Debrief_Row>
  <RR_Debrief_Take>Debrief {0} (report taken by {1})</RR_Debrief_Take>
  <RR_Debrief_UnknownStaff>a former employee</RR_Debrief_UnknownStaff>
  <RR_Debrief_NobodyToReport>there is nobody here to take the report</RR_Debrief_NobodyToReport>
  <RR_Debrief_NothingToReport>they have nothing outstanding to report</RR_Debrief_NothingToReport>
  <RR_Debrief_SelfReport>nobody debriefs themselves</RR_Debrief_SelfReport>
  <RR_Debrief_NotStaff>only company staff can take a debrief</RR_Debrief_NotStaff>
  <RR_Debrief_InterviewerUnfit>whoever would take the report is in no state to take it</RR_Debrief_InterviewerUnfit>
  <RR_Debrief_InterviewerUnskilled>nobody here is a good enough talker to take the report</RR_Debrief_InterviewerUnskilled>
  <RR_Debrief_NotOurs>that is not one of the company's sites</RR_Debrief_NotOurs>
  <RR_Debrief_NotHome>they are not back at the headquarters yet</RR_Debrief_NotHome>
  <RR_Debrief_NotTogether>the two of them are not in the same place</RR_Debrief_NotTogether>
  <RR_Event_StaffDebriefed>Staff debriefed after returning from the field</RR_Event_StaffDebriefed>
</LanguageData>""")

sub("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Expedition.xml",
    u"</LanguageData>",
    u"""  <RR_Exp_AwaitingDebrief>Somebody on this crew has not reported in from the last trip. Debrief them from the facilities pane before sending them out again.</RR_Exp_AwaitingDebrief>
</LanguageData>""")

print("debrief and quarantine wired")
