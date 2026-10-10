# -*- coding: utf-8 -*-
"""The facilities-pane containment section, and every keyed string the procedure needs."""
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


# ------------------------------------------------------------------ the pane section
# Placed immediately after the bed summary and before the category filter, because it is a
# branch-wide statement rather than a per-building one, and the filter below it is per-building.
sub("src/RimroomsAsyncIndustries/UI/OperationsFacilities.cs",
    u"""            if (listing.ButtonText("RR_Fac_OpenAssignments".Translate()))
            { OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign")); }
            listing.GapLine();""",
    u"""            if (listing.ButtonText("RR_Fac_OpenAssignments".Translate()))
            { OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign")); }
            listing.GapLine();
            DrawContainment(listing, campaign);
            listing.GapLine();""")

sub("src/RimroomsAsyncIndustries/UI/OperationsFacilities.cs",
    u"        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)",
    u"""        /// <summary>
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

        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)""")

# ------------------------------------------------------------------ the strings
COMPANY = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Company.xml"
sub(COMPANY, u"</LanguageData>",
    u"""
  <!-- Containment: the procedure, the alarm and what the branch is holding. Row 761. -->
  <RR_Containment_Held>Subjects held across every site: {0}</RR_Containment_Held>
  <RR_Containment_Escaping>Getting loose right now: {0}. Whatever is on that platform is on its way off it.</RR_Containment_Escaping>
  <RR_Containment_Unpowered>Holding without power: {0}. A platform with no power will not hold for long.</RR_Containment_Unpowered>
  <RR_Containment_ProcedureOn>Standing order: if anything gets loose, every open connection is cut and the crews come home.</RR_Containment_ProcedureOn>
  <RR_Containment_ProcedureOff>Standing order: connections stay open through a containment failure. Nothing will be closed for you.</RR_Containment_ProcedureOff>
  <RR_Containment_Arm>Cut connections on a containment failure</RR_Containment_Arm>
  <RR_Containment_Disarm>Leave connections open through a containment failure</RR_Containment_Disarm>
  <RR_Containment_AlarmLabel>Sound the containment alarm</RR_Containment_AlarmLabel>
  <RR_Containment_AlarmDesc>Cut every connection the company has open, right now, and start the return window on each so the crews walk home.\\n\\nThis is the same action the standing order takes by itself when something gets loose. Use it when you can see the problem coming and the order is disarmed.</RR_Containment_AlarmDesc>
  <RR_Containment_NothingOpen>There is nothing open to cut. No connection is live.</RR_Containment_NothingOpen>
  <RR_Letter_ContainmentCutLabel>Containment failure: connections cut</RR_Letter_ContainmentCutLabel>
  <RR_Letter_ContainmentCutText>Something is coming off a holding platform, and the standing order was to shut the doors.\\n\\nConnections cut: {0}. Every crew on the far side is inside its return window and walking back. You can disarm this order from the facilities pane if you would rather decide each time yourself.</RR_Letter_ContainmentCutText>
</LanguageData>""")

# ------------------------------------------------------------------ the alert strings
PORTALS = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"
sub(PORTALS, u"</LanguageData>",
    u"""
  <!-- Containment alerts. These speak ONLY about maps the player is not looking at; the base
       game already warns about containment strength, activity and tending on the map in view. -->
  <RR_Alert_ContainmentBreach>Containment failing elsewhere</RR_Alert_ContainmentBreach>
  <RR_Alert_ContainmentBreachDesc>Something is coming off a holding platform at a site you are not currently looking at.\\n\\nThe base game warns you about containment on the map you have open. This warns you about every other place the company holds something, because a breach at home while you are watching a crew work is exactly the one you will miss.</RR_Alert_ContainmentBreachDesc>
  <RR_Alert_ContainmentUnpowered>Containment without power elsewhere</RR_Alert_ContainmentUnpowered>
  <RR_Alert_ContainmentUnpoweredDesc>A holding platform with something on it has lost power, at a site you are not currently looking at.\\n\\nA platform without power will not hold. Restore the power, or move the subject, before it decides to leave.</RR_Alert_ContainmentUnpoweredDesc>
</LanguageData>""")

print("pane and strings wired")
