# -*- coding: utf-8 -*-
"""Plants for the release claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

text = io.open(PLANT, encoding="utf-8").read()

PATHS = 'PARENT = SRC + "/Generation/RimroomsDestinationMapParent.cs"'
PATHS_NEW = ('PARENT = SRC + "/Generation/RimroomsDestinationMapParent.cs"\n'
             'RELEASE = SRC + "/Generation/CoordinateRelease.cs"\n'
             'RECORDS = SRC + "/Company/CampaignRecords.cs"\n'
             'EMERGENCE = SRC + "/Portals/CompRimroomsEmergence.cs"\n'
             'PLACES = SRC + "/UI/OperationsHeldPlaces.cs"\n'
             'OPTABS = SRC + "/UI/MainTabWindow_Operations.cs"\n'
             'ADDRESS = SRC + "/Portals/PortalAddressService.cs"')

ANCHOR = "]\n\n\ndef write_verified"

NEW = '''    # ------------------------------------------------------ letting a place go
    ("THE DISCOVERY-COSTS-A-SLOT FACT STOPS HOLDING", ADDRESS,
     "DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry)",
     "DestinationService.EnsureSiteUnused(campaign, coordinate, out siteMap, out siteEntry)"),

    ("a release stops being written to the save", RECORDS,
     '            Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);' + NL,
     ""),

    ("THE EXPLORED-GRAPH GUARD STOPS EXEMPTING A DELIBERATE RELEASE", SERVICE,
     "            if (!releasedAndRebuildable && coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||",
     "            if (coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||"),

    ("THE EXEMPTION STARTS BYPASSING A LIVE MAP TOO", SERVICE,
     "                !Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id);",
     "                true;"),

    ("THE EXEMPTION OUTLIVES ITS REASON", SERVICE,
     "            coordinate.releasedByPlayer = false;" + NL, ""),

    ("THE EDGES ARE REMOVED BEFORE THE DOORS ARE TOLD WHERE THEY LED", RELEASE,
     "                RememberOn(edge.First, coordinate, map);" + NL
     + "                RememberOn(edge.Second, coordinate, map);" + NL,
     ""),

    ("THE MAP IS TORN DOWN BEFORE THE EDGES ARE REMOVED", RELEASE,
     "            for (int index = 0; index < shelved.Count; index++)" + NL
     + "            { network.ForgetConnection(shelved[index].Id); }",
     "            Current.Game.DeinitAndRemoveMap(map, false);" + NL
     + "            for (int index = 0; index < shelved.Count; index++)" + NL
     + "            { network.ForgetConnection(shelved[index].Id); }"),

    ("a release discards the graph, so the place comes back different", RELEASE,
     "            coordinate.status = CoordinateStatus.Discovered;",
     "            coordinate.rooms = null;"),

    ("the pairing is written onto the map being destroyed", RELEASE,
     "            if (anchor == null || anchor.Destroyed || anchor.Map == null || anchor.Map == releasing)",
     "            if (anchor == null || anchor.Destroyed || anchor.Map == null)"),

    ("RELEASING THE HEADQUARTERS BECOMES POSSIBLE", RELEASE,
     '            if (campaign.Headquarters == map) { return "RR_Release_Headquarters"; }' + NL, ""),

    ("A PLACE WITH PEOPLE IN IT BECOMES RELEASABLE", RELEASE,
     '            { return "RR_Release_CrewInside"; }', '            { }'),

    ("a prisoner or an animal stops counting as somebody inside", RELEASE,
     "pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony))",
     "pawn.Faction == Faction.OfPlayer && pawn.RaceProps.Humanlike))"),

    ("A PLACE SOMEBODY IS CROSSING INTO BECOMES RELEASABLE", RELEASE,
     '                    if (crossings.IsConnectionInFlight(edge.Id)) { return "RR_Release_CrossingInFlight"; }' + NL,
     ""),

    ("the network gains a second, wider removal", NETWORK,
     "            connections.Remove(edge);",
     "            connections.Remove(edge);" + NL
     + "            connections.RemoveAll(other => other == null);"),

    ("THE DOOR STOPS REMEMBERING WHERE IT LED", EMERGENCE,
     '            Scribe_Values.Look(ref shelvedCoordinateId, "rr_emergenceShelvedCoordinate");' + NL,
     ""),

    ("the release stops telling the door anything", RELEASE,
     "            emergence.RememberShelvedPlace(coordinate.Id);",
     "            emergence.ForgetShelvedPlace();"),

    ("re-opening stops using the path that created it", EMERGENCE,
     "            CompanyActionResult registered = PortalAddressService.RegisterNaturalAddress(" + NL
     + "                parent, ApproachCell, shelved);",
     "            CompanyActionResult registered = CompanyActionResult.Applied();"),

    ("A FAILED RE-OPEN STRANDS THE PLACE FOR EVER", EMERGENCE,
     "            if (registered.Success) { ForgetShelvedPlace(); }", "            ForgetShelvedPlace();"),

    ("re-opening stops being refused at the budget", EMERGENCE,
     "                Disabled = !room,", "                Disabled = false,"),

    ("THE HELD-PLACES PANE IS NEVER DISPATCHED TO", OPTABS,
     "                case 12: DrawHeldPlaces(listing, campaign); break;" + NL, ""),

    ("the help pane index is left behind and help opens the places list", OPTABS,
     "        private const int HelpPane = 13;", "        private const int HelpPane = 12;"),

    ("the pane stops showing the colonies that fill the budget", PLACES,
     "                listing.Label(\\"RR_Release_ColonyRow\\".Translate(colonies[index].Parent.Label));",
     "                continue;"),

    ("A RELEASE STOPS BEING CONFIRMED", PLACES,
     "                            destructive: true,", "                            destructive: false,"),

    ("A FAILED RELEASE BECOMES SILENT", PLACES,
     '                Messages.Message("RR_Release_Failed".Translate(label, refusal.Translate()),',
     '                Messages.Message("".Translate(),'),

    ("a release refusal loses its keyed string", KEYED,
     "<RR_Release_CrewInside>", "<RR_Release_CrewInsideUnused>"),

    ("the places pane label is never written", KEYED,
     "<RR_UI_Places>", "<RR_UI_PlacesUnused>"),

''' + ANCHOR

problems = []
if text.count(PATHS) != 1:
    problems.append("paths %d" % text.count(PATHS))
if text.count(ANCHOR) != 1:
    problems.append("list %d" % text.count(ANCHOR))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(PATHS, PATHS_NEW, 1).replace(ANCHOR, NEW, 1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(text)
print("release plants added")
