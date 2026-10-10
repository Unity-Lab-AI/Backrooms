# -*- coding: utf-8 -*-
"""Surface the integration readout, and say every position in the player's own language."""
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
sub("src/RimroomsAsyncIndustries/UI/OperationsFacilities.cs",
    u"            DrawDebriefs(listing, campaign);\n            listing.GapLine();",
    u"            DrawDebriefs(listing, campaign);\n"
    u"            listing.GapLine();\n"
    u"            DrawIntegrations(listing);\n"
    u"            listing.GapLine();")

sub("src/RimroomsAsyncIndustries/UI/OperationsFacilities.cs",
    u"        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)",
    u'''        /// <summary>
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

        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)''')

# ------------------------------------------------------------------ the strings
sub("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Company.xml",
    u"</LanguageData>",
    u"""
  <!-- Rows 764, 765, 766, 784: what optional mods are loaded and what this mod does about each.
       Every position is the register's own words turned into something a player can read, and
       every one ends in the same caveat because nothing has been tested in play. -->
  <RR_Integration_Heading>Optional mods this company has a position on: {0} of {1} loaded</RR_Integration_Heading>
  <RR_Integration_Caveat>None of these has been tested in play. Loaded means present, not proven.</RR_Integration_Caveat>
  <RR_Integration_RowActive>{0} - loaded (register row {1})</RR_Integration_RowActive>
  <RR_Integration_RowAbsent>{0} - not loaded (register row {1})</RR_Integration_RowAbsent>
  <RR_Integration_OpenWorld>Open the world map</RR_Integration_OpenWorld>

  <RR_Integration_VehicleFrameworkName>Vehicle Framework</RR_Integration_VehicleFrameworkName>
  <RR_Integration_VehicleFrameworkPosition>Vehicles stay entirely the other mod's business. Nothing here needs one: a gate is opened on foot, a crew walks through it, and no route, contract or expedition will ever ask you for a vehicle.</RR_Integration_VehicleFrameworkPosition>

  <RR_Integration_RimWorldTogetherName>RimWorld Together</RR_Integration_RimWorldTogetherName>
  <RR_Integration_RimWorldTogetherPosition>Each player runs their own company: their own facility, their own gate, their own discoveries, their own research and their own books. Visits and supply exchange are the other mod's features and work as it makes them work. There is no shared map, no shared research, and nothing here transfers a case file or a crew between companies.</RR_Integration_RimWorldTogetherPosition>

  <RR_Integration_GravshipOneName>Vanilla Gravship Expanded - Chapter 1</RR_Integration_GravshipOneName>
  <RR_Integration_GravshipOnePosition>Orbital travel is a separate way to get about and stays that way. Its air, fuel, power, heat and crew systems are untouched. A gate remains the only way into the Backrooms, and nothing here reads or changes a gravship.</RR_Integration_GravshipOnePosition>

  <RR_Integration_VehiclesExpandedName>Vanilla Vehicles Expanded</RR_Integration_VehiclesExpandedName>
  <RR_Integration_VehiclesExpandedPosition>Use its vehicles for whatever you like - staging a team, moving stock, carrying somebody home. None of it is required and none of it is changed here.</RR_Integration_VehiclesExpandedPosition>

  <RR_Integration_GravshipTwoName>Vanilla Gravship Expanded - Chapter 2</RR_Integration_GravshipTwoName>
  <RR_Integration_GravshipTwoPosition>Its orbital combat, contracts and salvage are its own and are not patched. Nothing it fights will ever turn up in a Backrooms space: what lives in there is drawn only from this mod's own list of inhabitants, and that is checked on every build.</RR_Integration_GravshipTwoPosition>
</LanguageData>""")

print("integration readout wired")
