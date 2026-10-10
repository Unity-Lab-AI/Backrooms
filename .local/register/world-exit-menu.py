# -*- coding: utf-8 -*-
"""A way OUT is not a way deeper, and the float menu only knew how to do one of them.

Owner: *"anoother door said somthing like you cant doo that, request is not valid for this
branch"* and *"it must be something about generationg the next world map or deeper backrroms idk
for sure"*. **Their read is exactly right.**

Two different things are recorded for the two kinds of way onward, and I wired one:

  * **deeper** -> `PortalAddressService.RegisterNaturalAddress` mints a coordinate and registers a
    portal **edge** between this door and the new place's threshold. `EdgeFor()` finds it and a
    pawn is ordered across.
  * **out to the world** -> `RecordWorldExit` saves a `WorldExitRecord` with a planet tile. **It
    registers no edge at all**, because leaving the Backrooms for the world map is a caravan, not
    a map-to-map crossing -- `CaravanExitMapUtility.ExitMapAndCreateCaravan` does the leaving.

So `FrontierOptions` recorded the world exit, asked `EdgeFor()` for an edge that by design does
not exist, got null, and showed `RR_Frontier_Unavailable` -- *"surveying doors is unavailable until
this branch is operating"* -- which is not true and tells the player nothing.

The way out already had a working player route: a `Command_Action` gizmo calling
`LeaveThroughWorldExit`, which is **the only path in the mod that reaches Core's caravan
formation**. The float menu now offers that same call for a world-exit door, so there is one
decision point and not a second opinion about it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")

OLD = u"""                CompanyActionResult found = NaturalFrontierService.Discover(parent);
                if (!found.Success) { Show(found); return; }
                // Painted on the click, not up to an interval later, and for the same reason
                // marking a door is: a player who acts and sees nothing change assumes it failed.
                RefreshGateAppearance();
                PortalConnectionRecord edge = EdgeFor();
                if (edge == null)
                {
                    Show(CompanyActionResult.Refused("RR_Frontier_Unavailable"));
                    return;
                }
                Show(PortalTravelService.OrderCrossing(selPawn, edge));"""

NEW = u"""                CompanyActionResult found = NaturalFrontierService.Discover(parent);
                if (!found.Success) { Show(found); return; }
                // Painted on the click, not up to an interval later, and for the same reason
                // marking a door is: a player who acts and sees nothing change assumes it failed.
                RefreshGateAppearance();

                // **A WAY OUT IS NOT A WAY DEEPER, AND THEY ARE RECORDED DIFFERENTLY.** A deeper
                // find mints a coordinate and registers a portal EDGE between this door and the
                // new place's threshold. A way out to the world saves a `WorldExitRecord` with a
                // planet tile and **registers no edge at all**, because leaving the Backrooms for
                // the world map is a caravan rather than a map-to-map crossing.
                //
                // The first draft asked `EdgeFor()` in both cases, so a world exit recorded
                // correctly and then reported *"surveying doors is unavailable until this branch
                // is operating"* -- which is not true and says nothing. The owner read it as
                // *"somthing about generationg the next world map or deeper backrroms"*, which
                // is precisely what it was.
                PortalConnectionRecord edge = EdgeFor();
                if (edge != null)
                {
                    Show(PortalTravelService.OrderCrossing(selPawn, edge));
                    return;
                }
                RimroomsCampaignComponent campaign = Campaign();
                if (campaign != null && campaign.WorldExitFor(parent) != null)
                {
                    // The SAME call the gizmo makes, which is the only path in the mod that
                    // reaches Core's caravan formation. One decision point, not a second
                    // opinion about it -- see WorldExit.cs for why that matters.
                    Show(campaign.LeaveThroughWorldExit(parent));
                    return;
                }
                Show(CompanyActionResult.Refused("RR_Frontier_Unavailable"));"""

text = io.open(COMP, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(COMP, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the float menu walks out to the world as well as deeper in")
