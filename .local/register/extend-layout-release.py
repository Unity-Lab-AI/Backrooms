# -*- coding: utf-8 -*-
"""Release claims. Added to the layout proof because release is the counterpart of the budget."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

text = io.open(PROOF, encoding="utf-8").read()
ANCHOR = 'print("")\nif failures:'

NEW = '''print("")
print("LETTING A PLACE GO, SO A MACHINE GATE CAN AIM DEEPER")
print("-" * 78)

# Owner direction, 2026-09-30: *"yeah so if the player discovers and goes through a natural gate
# how do they turn them off to use the machine gates for more controll and aiming deeper?"*, and
# the trap named: *"get 5 natural gates u cant use a machine gate"*. They chose an Operations
# held-places list with a Release button.
release = read(os.path.join(SRC, "Generation", "CoordinateRelease.cs"))
records = read(os.path.join(SRC, "Company", "CampaignRecords.cs"))
emergence = read(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"))
places = read(os.path.join(SRC, "UI", "OperationsHeldPlaces.cs"))
optabs = read(os.path.join(SRC, "UI", "MainTabWindow_Operations.cs"))

check("THE TRAP IS REAL: A DISCOVERY COSTS A SLOT IMMEDIATELY",
      "DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry)"
      in read(os.path.join(SRC, "Portals", "PortalAddressService.cs")),
      "-- RegisterNaturalAddress generates the site AT DISCOVERY, because a natural edge is "
      "registered against the far side's own ReturnAnchor and that Thing does not exist until the "
      "map does. The previous checkpoint's record claimed discovery was free; it was wrong, and "
      "the budget check in Discover is load-bearing rather than over-eager")

check("a deliberate release is written down in the save",
      "internal bool releasedByPlayer;" in records
      and 'Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);' in records,
      "-- a released coordinate has no site and surveyed rooms, which is byte-for-byte what a "
      "broken reference looks like. Only a flag can tell them apart")

check("THE EXEMPTION IS THE ONLY WAY PAST THE EXPLORED-GRAPH GUARD",
      "bool releasedAndRebuildable = coordinate.releasedByPlayer &&" in service
      and "if (!releasedAndRebuildable && coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready"
      in service,
      "-- the guard exists so a broken reference cannot replace an already explored graph, and "
      "that is still exactly right for a fault")

check("and it still refuses a competing owner or a live map",
      "!Find.WorldObjects.AllWorldObjects.OfType<RimroomsDestinationMapParent>().Any(owner => owner.CoordinateId == coordinate.Id) &&"
      in service
      and "!Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id)"
      in service,
      "-- those are real conflicts rather than an explored graph, and a release is required to "
      "have removed both")

check("THE EXEMPTION IS SPENT THE MOMENT THE PLACE EXISTS AGAIN",
      "coordinate.releasedByPlayer = false;" in service,
      "-- an exemption that outlives its reason is a hole: it would let a genuinely broken "
      "reference through on some later load")

# The ORDER of the teardown is the whole of its safety, so it is measured as an ordering.
remember_at = release.find("RememberOn(edge.First, coordinate, map);")
forget_at = release.find("network.ForgetConnection(shelved[index].Id);")
teardown_at = release.find("Current.Game.DeinitAndRemoveMap(map, false);")
check("THE DOORS ARE TOLD WHERE THEY LED BEFORE THE EDGES ARE REMOVED",
      remember_at >= 0 and forget_at >= 0 and remember_at < forget_at,
      "-- the edge is the only record of the pairing. Remove it first and the door becomes an "
      "ordinary marked door with the place behind it unreachable for ever. Remember at %d, "
      "forget at %d" % (remember_at, forget_at))

check("AND THE EDGES ARE REMOVED BEFORE THE MAP IS TORN DOWN",
      forget_at >= 0 and teardown_at >= 0 and forget_at < teardown_at,
      "-- every endpoint lives on the map being destroyed, so the other order leaves records "
      "pointing at nothing. Forget at %d, teardown at %d" % (forget_at, teardown_at))

check("the place itself is kept, so re-opening returns to the SAME place",
      "coordinate.site = null;" in release
      and "coordinate.status = CoordinateStatus.Discovered;" in release
      and "Coordinates.Remove" not in release
      and "coordinate.rooms" not in release,
      "-- the record and its rooms survive; only the map and the world object go. A release that "
      "discarded the graph would give the player a different place back")

check("nothing is remembered onto the map being destroyed",
      "anchor.Map == releasing)" in release,
      "-- the far endpoint is about to cease to exist, so writing the pairing onto it would be "
      "writing it onto nothing")

release_at = release.find("internal static string RefusalFor(")
refusal_body = release[release_at:release.find(chr(10) + "        }", release_at)] \\
    if release_at >= 0 else ""
for needle, why in [
        ("RR_Release_Headquarters", "the headquarters is not a place you let go of"),
        ("RR_Release_CrewInside", "a released map takes its contents with it, people included"),
        ("RR_Release_CrossingInFlight", "invariant 55: nobody may be part-way through"),
        ("RR_Release_NotHeldOpen", "a place with no live map has nothing to release")]:
    check("release refuses: " + needle, release_at >= 0 and needle in refusal_body, "-- " + why)

check("A PRISONER OR AN ANIMAL COUNTS AS SOMEBODY INSIDE",
      "pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony" in refusal_body,
      "-- colonists are not the only thing the player would lose")

check("the network's one removal is narrow and deliberate",
      "internal bool ForgetConnection(string connectionId)" in network
      and network.count("connections.Remove(") == 1,
      "-- the load path forbids silently removing an edge, because a broken-looking edge is "
      "evidence. This is neither silent nor a fault: the player asked, and every endpoint is "
      "about to stop existing")

check("THE DOOR REMEMBERS WHERE IT LED, AND IT IS SAVED",
      "private string shelvedCoordinateId;" in emergence
      and 'Scribe_Values.Look(ref shelvedCoordinateId, "rr_emergenceShelvedCoordinate");' in emergence
      and "emergence.RememberShelvedPlace(coordinate.Id);" in release,
      "-- a natural gate is permanently open and is never closed; what is released is the space "
      "behind it, and the door is the only thing left that knows which space")

reopen_at = emergence.find("private CompanyActionResult Reopen(")
reopen_body = emergence[reopen_at:emergence.find(chr(10) + "        }", reopen_at)] \\
    if reopen_at >= 0 else ""
check("re-opening goes through the same path that first created it",
      reopen_at >= 0 and "PortalAddressService.RegisterNaturalAddress(" in reopen_body,
      "-- nothing bespoke, so there is no second implementation to drift")

check("A FAILED RE-OPEN LEAVES THE DOOR STILL OFFERING TO TRY",
      reopen_at >= 0 and "if (registered.Success) { ForgetShelvedPlace(); }" in reopen_body,
      "-- forgetting on failure would strand the place for ever over a transient refusal")

check("re-opening is refused, and visibly, when the budget is full",
      "Disabled = !room," in emergence and "RR_Release_ReopenNoRoomDesc" in emergence,
      "-- disabled rather than hidden: a player at their limit needs to see what they are at the "
      "limit of")

check("THE HELD-PLACES PANE EXISTS AND IS REACHABLE",
      "private void DrawHeldPlaces(Listing_Standard listing, RimroomsCampaignComponent campaign)"
      in places
      and "case 12: DrawHeldPlaces(listing, campaign); break;" in optabs
      and '"RR_UI_Places"' in optabs
      and "HelpPane = 13" in optabs,
      "-- a pane nothing dispatches to is the defect check-wiring exists for, and the help pane "
      "index moves with it or help opens the places list")

check("it shows the colonies too, because they are the other half of the budget",
      "map.IsPlayerHome &&" in places and "RR_Release_ColonyRow" in places,
      "-- a player counting slots needs to see why three of five are gone before they blame the "
      "Backrooms")

check("the release is confirmed and the loss is counted first",
      "ItemsLeftBehind" in places and "destructive: true" in places
      and "RR_Release_Confirm" in places,
      "-- the interior regenerates from its seed, so anything left inside is gone; that is the "
      "honest price of not holding it open and the player is told the number")

check("NEITHER OUTCOME IS SILENT",
      "RR_Release_Failed" in places and "RR_Release_Done" in places,
      "-- the player pressed a button to free a slot, and a slot either was or was not freed")

release_keys = ["RR_Release_Heading", "RR_Release_Budget", "RR_Release_Button",
                "RR_Release_Confirm", "RR_Release_Done", "RR_Release_Failed",
                "RR_Release_Blocked", "RR_Release_Inactive", "RR_Release_UnknownPlace",
                "RR_Release_NotHeldOpen", "RR_Release_Headquarters", "RR_Release_CrewInside",
                "RR_Release_CrossingInFlight", "RR_Release_ReopenLabel",
                "RR_Release_ReopenNoRoomDesc", "RR_Event_CoordinateReleased", "RR_UI_Places"]
missing_keys = [key for key in release_keys if ("<" + key + ">") not in keyed]
check("every release string the player can meet is written",
      not missing_keys,
      "-- a refusal the player cannot read is a silent failure: %s" % missing_keys)

''' + ANCHOR

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("release claims added")
