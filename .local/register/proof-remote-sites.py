# -*- coding: utf-8 -*-
"""Assert that a remote base is a costly responsibility rather than free map ownership.

The property this exists for
----------------------------
Arc 5's principle, from `CAMPAIGN_CONTENT_CATALOG.md`:

    "Remote sites need people, supplies, signals, protection, and an exit plan...
     A remote base is a costly responsibility rather than free map ownership."

That is a design claim, and a design claim with nothing enforcing it decays into a list of
features. Three things have to stay true:

  * **Registering costs something every day.** If the surcharge is ever removed, disconnected or
    quietly folded into base overhead, map ownership becomes free again and the arc's one stated
    principle is gone with no test failing.
  * **A coordinate is never a site.** A Backrooms coordinate is somewhere you go, not somewhere
    you keep. The naive version of this feature counted coordinates, which is both wrong on its
    own terms and the reason a surcharge would have computed zero.
  * **Nothing here acquires anything.** RimWorld already lets a colony settle a second tile.
    Acquisition is the game's; recognition is ours. A mod that invented its own settling would be
    fighting Core for no reason and would be the first thing to break on a Core update.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//"))


sites = strip_comments(io.open(os.path.join(SRC, "Company", "RemoteSites.cs"),
                               encoding="utf-8-sig").read())
services = strip_comments(io.open(os.path.join(SRC, "Company", "CampaignServices.cs"),
                                  encoding="utf-8-sig").read())
pane = strip_comments(io.open(os.path.join(SRC, "UI", "OperationsRemoteSites.cs"),
                              encoding="utf-8-sig").read())
tab = strip_comments(io.open(os.path.join(SRC, "UI", "MainTabWindow_Operations.cs"),
                             encoding="utf-8-sig").read())

all_source = ""
for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
    all_source += strip_comments(io.open(path, encoding="utf-8-sig").read())

print("")

# 1. It costs. THE claim.
check("a daily surcharge is computed for held sites",
      "DailyRemoteSiteOverheadUsd" in sites,
      "-- map ownership would be free and the arc's one principle would be gone")
check("the surcharge is billed as its own daily obligation",
      re.search(r'AddObligation\(dayId \+ ":sites", "RR_Ledger_RemoteSites",\s*'
                r'DailyRemoteSiteOverheadUsd', services) is not None,
      "-- computed and never charged is the same as not existing")
# The divisor became capability-aware at 0.12.18-dev (Commerce tier 3 improves it 4 -> 6), so the
# literal moved from the constant to OverheadDivisorInForce. The PROPERTY is unchanged and is what
# is asserted: the surcharge is still a division of the branch's OWN overhead, and both the base
# and the improved divisor are still ratios rather than absolutes.
check("the surcharge is a ratio of the branch's own overhead, not an absolute",
      "dailyOverheadUsd / OverheadDivisorInForce" in sites,
      "-- one absolute number is a rounding error for Async and ruinous for the Store")
check("both the base and the improved divisor are ratios of base overhead",
      "internal const int RemoteSiteOverheadDivisor = 4;" in sites
      and "internal const int EfficientRemoteSiteOverheadDivisor = 6;" in sites
      and "EfficientRemoteSiteOverheadDivisor : RemoteSiteOverheadDivisor" in sites,
      "-- a tier-3 unlock that swapped in a flat discount would break the same principle the "
      "base divisor exists to protect")
check("the site cap has exactly one source for the refusal and the readout",
      "remoteSites.Count >= RemoteSiteCap" in sites and "campaign.RemoteSiteCap" in pane
      and "RimroomsCampaignComponent.MaximumRemoteSites" not in pane,
      "-- the number a player is SHOWN and the number that REFUSES them could disagree")
check("the surcharge counts only LIVE sites",
      "each * LiveRemoteSiteCount" in sites,
      "-- a branch would be billed for a place it can no longer reach")

# 2. A coordinate is never a site. Both in the service and before the click.
check("registration refuses a Backrooms coordinate",
      re.search(r"if \(map\.Parent is RimroomsDestinationMapParent\)\s*\{?\s*"
                r"return CompanyActionResult\.Refused\(\"RR_Site_CoordinateNotASite\"\)", sites) is not None,
      "-- a destination would be billed as a base, and the surcharge would count transients")
check("the pane says so before the click too",
      '"RR_Sites_BlockedCoordinate"' in pane,
      "-- the player would be offered a button that refuses")
check("registration refuses the headquarters",
      '"RR_Site_IsHeadquarters"' in sites,
      "-- the branch's own place would be billed twice")
check("registration refuses a place the branch does not hold",
      '"RR_Site_NotYours"' in sites)

# 3. Acquisition is the game's. Nothing here settles, creates a settlement or generates a map.
banned = ["WorldObjectMaker.MakeWorldObject", "GetOrGenerateMap", "SettleInEmptyTileUtility",
          "MapGenerator.GenerateMap"]
for token in banned:
    check("remote sites do not use %s" % token, token not in sites,
          "-- acquisition is RimWorld's; recognition is ours")

# 4. Ownership. The whole point of registering is that the branch's systems reach the place, and
#    that is one predicate rather than five features.
check("OwnsMap consults the registered sites",
      "IsRegisteredRemoteSite(map)" in services,
      "-- work, portals and emergence anchors would not reach a registered site")
check("OwnsMap still answers coordinates before falling through",
      re.search(r"if \(site != null\)\s*\{\s*return coordinates\.Any", services) is not None,
      "-- a coordinate must never fall through to the site check")

# 5. Releasing is free. Nothing in this mod has a deadline but the gate, and a release fee is a
#    cost for changing your mind.
release = re.search(r"public CompanyActionResult ReleaseRemoteSite\(string id\).*?\n        \}",
                    sites, re.S)
release_text = release.group(0) if release else ""
check("the release path was found", bool(release_text))
check("releasing a site charges nothing",
      bool(release_text) and "PostTransaction" not in release_text
      and "AddObligation" not in release_text,
      "-- a fee for changing your mind is a deadline wearing a different hat")

# 6. Reachable at all. A feature with no surface is a feature nobody has.
check("the sites pane is registered in the tab list", '"RR_UI_Sites"' in tab,
      "-- the pane would exist and be unreachable")
check("the pane is dispatched", "DrawRemoteSites(listing, campaign)" in tab)

# 7. Every string it shows exists. A missing one is a raw key on screen.
keyed = ""
for path in glob.glob(os.path.join(MOD, "Languages", "English", "Keyed", "*.xml")):
    keyed += io.open(path, encoding="utf-8-sig").read()
for key in sorted(set(re.findall(r'"(RR_Sites?_\w+|RR_Site_\w+|RR_UI_Sites|RR_Ledger_RemoteSites'
                                 r'|RR_Event_RemoteSite\w+)"', sites + pane + tab))):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed,
          "-- the player would be shown the raw key")

# --------------------------------------------------------------------------- deliveries
# Arc 5 names "company-to-site logistics". Procurement had the headquarters written into it in
# seven places, while `ProcurementOrderRecord.receivingMap` already existed and the DELIVERY path
# already honoured it -- so only the selection was pinned.
procurement = strip_comments(io.open(os.path.join(SRC, "Procurement",
                                                  "RimroomsProcurementComponent.cs"),
                                     encoding="utf-8-sig").read())
proc_ui = strip_comments(io.open(os.path.join(SRC, "UI", "OperationsProcurement.cs"),
                                 encoding="utf-8-sig").read())

print("")
check("the branch decides where it may receive", "CanReceiveDeliveryAt" in sites,
      "-- nothing would distinguish a site on the books from any map at all")
#    Keyed off the GUARD, not the refusal string. Counting the string passed a planted fault
#    that replaced the condition with `if (false)` and left the string sitting there unused.
check("quoting guards the destination against the books",
      "if (!campaign.CanReceiveDeliveryAt(destination))" in procurement,
      "-- any map at all could be named as a delivery address")
check("redirecting guards the destination against the books",
      "if (!campaign.CanReceiveDeliveryAt(redirectTo))" in procurement,
      "-- an in-flight order could be rerouted anywhere")
check("both guards refuse with a string the player can read",
      procurement.count('"RR_Proc_DestinationNotOnTheBooks"') >= 2,
      "-- a guard that refuses silently teaches nothing")
check("the quote takes its destination from the zone's own map",
      "Map destination = receivingZone == null ? null : receivingZone.Map;" in procurement,
      "-- passing a map separately lets the two disagree")
check("the quote no longer pins the destination to the headquarters",
      "receivingMap = campaign.Headquarters," not in procurement,
      "-- a site could be billed daily and never receive anything")
check("accepting validates against the quote's own destination",
      "IsReceivingZoneValid(quote.receivingMap, quote.receivingZone, itemDef)" in procurement,
      "-- a quote to a site would be refused at acceptance")
check("accepting checks the zone still sits on that destination",
      "quote.receivingZone.Map != quote.receivingMap" in procurement,
      "-- a zone moved between quoting and accepting would deliver into the wrong place")

# THE latent bug. The redirect updated the zone and not the map. Harmless while one map was
# allowed; the moment a second became legal, a cross-map redirect would leave the order pointing
# at the old map and the delivery check would refuse it on every attempt, for ever.
check("redirecting updates the receiving MAP, not only the zone",
      "order.receivingMap = redirectTo;" in procurement,
      "-- a cross-map redirect would stick awaiting a condition that can never come true")
redirect_assign = procurement.find("order.receivingMap = redirectTo;")
zone_assign = procurement.find("order.receivingZone = receivingZone;")
check("the map is set alongside the zone it belongs to",
      redirect_assign != -1 and zone_assign != -1 and abs(zone_assign - redirect_assign) < 200,
      "-- the two must move together or a later reader sees a mismatched pair")

# A site's map can be unloaded; the headquarters' cannot. The reason shown had to stop saying HQ.
check("an unloaded destination no longer blames the headquarters",
      '"RR_Proc_ReceivingMapUnavailable"' in procurement,
      "-- a site shipment would report the HQ as missing")

# Reachable at all: the menu has to offer site stockpiles or the feature is paperwork only.
check("the order menu lists stockpiles at every destination",
      "DeliveryStockpiles(campaign)" in proc_ui,
      "-- only headquarters stockpiles would be offered")
check("the headquarters-only listing is gone",
      "HeadquartersStockpiles(" not in proc_ui,
      "-- the old listing would still be the one in use")
check("a stockpile says where it is when there is more than one place",
      "StockpileLabel(" in proc_ui,
      "-- two stockpiles named Stockpile on different maps would be indistinguishable")

for key in ("RR_Proc_DestinationNotOnTheBooks", "RR_Proc_ReceivingMapUnavailable",
            "RR_Proc_AtHeadquarters", "RR_Proc_ZoneAtPlace"):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed,
          "-- the player would be shown the raw key")

# --------------------------------------------------------------------------- staffing
# Arc 5: "remote sites need people". The consequence is that a shipment bound for an empty place
# WAITS -- a supplier does not unload with nobody to sign for it.
print("")
check("the branch can tell whether anybody is at a site", "IsSiteStaffed" in sites,
      '-- "remote sites need people" would be a sentence in a document')

staffed = re.search(r"public bool IsSiteStaffed\(Map map\).*?\n        \}", sites, re.S)
staffed_text = staffed.group(0) if staffed else ""
check("the staffing check was found", bool(staffed_text))
check("staffing requires somebody present on that map",
      "pawn.Map != map" in staffed_text,
      "-- staff anywhere at all would count as staffing every site")
check("staffing does not count the downed",
      "pawn.Downed" in staffed_text,
      "-- somebody unconscious on the floor cannot take delivery of anything")
check("staffing does not count prisoners or slaves",
      "pawn.IsPrisoner" in staffed_text and "pawn.IsSlave" in staffed_text,
      "-- neither is staff, and neither chose to be there")
check("staffing counts only the employed and living",
      "member.employed" in staffed_text and "pawn.Dead" in staffed_text)

# THE design. Two predicates, and the split is the point: the address is acceptable if the place
# is on the books, and the ARRIVAL needs somebody there. Ordering ahead must stay possible.
check("unloading is a separate question from addressing", "public bool CanUnloadAt" in sites,
      "-- one predicate would either punish ordering ahead or make staffing mean nothing")
unload = re.search(r"public bool CanUnloadAt\(Map map\).*?\n        \}", sites, re.S)
unload_text = unload.group(0) if unload else ""
check("unloading builds on the address check",
      "CanReceiveDeliveryAt(map)" in unload_text,
      "-- an unregistered place could be unloaded into by a staffed crew")
check("the headquarters is never held to the staffing rule",
      "if (map == headquarters) { return true; }" in unload_text,
      "-- a branch with nobody at home has a bigger problem and the clean-up team owns it")

# The order path must gate ARRIVAL, not the quote. Gating the quote punishes planning.
check("arrival waits when nobody is there",
      'SetAwaiting(order, "RR_Proc_SiteUnstaffed", now)' in procurement,
      "-- a shipment would land in an empty field")
check("arrival uses the unload check, not the address check",
      "campaign.CanUnloadAt(order.receivingMap)" in procurement,
      "-- staffing would not be consulted at the moment it matters")
#    No conditional fallback. The first version of this claim had one, keyed off a method name
#    that does not exist in the file, so it collapsed to a trivially-true expression and could
#    never fail. One call site is the whole intent and cannot degenerate.
check("staffing is consulted at exactly one place, the arrival",
      procurement.count("CanUnloadAt") == 1,
      "-- a second call site would almost certainly be gating the ORDER, which punishes planning")
check("quoting, accepting and redirecting use the address check only",
      procurement.count("CanReceiveDeliveryAt") == 3,
      "-- ordering ahead while the crew walks there must stay possible")
check("a waiting shipment is not a lost one",
      "SetAwaiting" in procurement and "SetRecovery(order, \"RR_Proc_SiteUnstaffed\")" not in procurement,
      "-- an unstaffed site must never turn a paid order into a recovery case")

# The player has to be able to see which site is holding their shipments.
check("the pane distinguishes unstaffed from unreachable",
      '"RR_Sites_RowUnstaffed"' in pane,
      "-- the state that quietly holds shipments would look identical to a healthy one")

for key in ("RR_Proc_SiteUnstaffed", "RR_Sites_RowUnstaffed"):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed,
          "-- the player would be shown the raw key")

# --------------------------------------------------------------------------- the exit plan
# Arc 5 names an "exit plan" among what a remote site needs. A gate could only ever be designated
# at the headquarters, because `SameNativeHeadquartersThing` compared `parent.Map` against
# `campaign.Headquarters` -- so the exit plan was unreachable however many sites a branch held.
binding = strip_comments(io.open(os.path.join(SRC, "Gate", "NativeGateBinding.cs"),
                                 encoding="utf-8-sig").read())
emergence = strip_comments(io.open(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"),
                                   encoding="utf-8-sig").read())

print("")
check("the branch can say where it operates", "public bool OperatesAt" in sites,
      "-- a gate would have nowhere but the headquarters to stand")
check("operating and receiving share one place-set",
      "private bool IsBranchPlace" in sites
      and "public bool CanReceiveDeliveryAt(Map map) { return IsBranchPlace(map); }" in sites
      and "public bool OperatesAt(Map map) { return IsBranchPlace(map); }" in sites,
      "-- two definitions of the branch's own places would drift apart")

# THE change. The gate no longer pins itself to the headquarters map.
check("the gate no longer requires the headquarters map",
      "parent.Map == campaign.Headquarters" not in binding,
      "-- arc 5's exit plan would stay unreachable")
check("the gate asks where the branch operates",
      "campaign.OperatesAt(parent.Map)" in binding,
      "-- any map at all could host a company gate")

# THE consequence, and it is the good one. A gate at a site needs its own equipment AT that site.
check("gate infrastructure must stand on the gate's own map",
      "thing.Map == parent.Map" in binding,
      "-- a remote gate could be run off the equipment back at headquarters, which is the whole "
      "thing arc 5 says a site must not get for free")

# A designated gate must never appear inside a Backrooms coordinate. It is excluded by
# construction -- a coordinate can never be registered -- which is the check nobody can forget.
place = re.search(r"private bool IsBranchPlace\(Map map\).*?\n        \}", sites, re.S)
place_text = place.group(0) if place else ""
check("the place-set was found", bool(place_text))
check("the place-set admits only the headquarters and registered sites",
      bool(place_text) and "headquarters == map" in place_text and "record.Live" in place_text
      and "RimroomsDestinationMapParent" not in place_text,
      "-- a coordinate admitted here would host a designated gate, against invariant 12")

# A way out may come up at a site too, and that came free from the ownership predicate rather
# than from a second rule. Assert it still routes that way.
check("a way out may come up anywhere the branch owns",
      "campaign.OwnsMap(map)" in emergence,
      "-- emergence anchors would be headquarters-only again")
check("a way out still refuses a coordinate",
      "map.Parent is RimroomsDestinationMapParent" in emergence,
      "-- a way out could come up inside the Backrooms, which is where it leads FROM")

# The refusal a player reads must no longer say "headquarters map" now that it is not true.
check("the binding refusal no longer claims headquarters only",
      "on the active company headquarters map" not in keyed,
      "-- the message would contradict what the code now allows")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a remote base costs something, and a coordinate is never one")
