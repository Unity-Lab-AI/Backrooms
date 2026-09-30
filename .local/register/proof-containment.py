# -*- coding: utf-8 -*-
"""Assert containment is visible across every owned map, that the procedure acts, and that
nothing here forms a second opinion beside a rule Core already shows.

Row 761, three of its five remaining halves: **containment rooms**, **security procedures** and
**alarm / escape response**.

The finding that shaped all of it: Core already ships four containment alerts --
`Alert_InsufficientContainmentStrength`, `Alert_DangerousActivity`, `Alert_EntityNeedsTend` and
`Alert_NeedHoldingPlatform` -- and **every one reads `Find.CurrentMap`**. That is right for
RimWorld, where a colony is a map, and wrong for a mod whose premise is several live maps at once.
So the gap is not *"containment has no warning"*, it is *"containment has no warning about the maps
you are not looking at"*, and the two alerts here cover exactly that and nothing else.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
KEYED = os.path.join(MOD, "Languages", "English", "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError("unbalanced body for %r" % signature)


watch = strip_cs_comments(read(os.path.join(SRC, "Threats", "ContainmentWatch.cs")))
alerts = strip_cs_comments(read(os.path.join(SRC, "Presentation",
                                             "RimroomsContainmentAlerts.cs")))
protocol = strip_cs_comments(read(os.path.join(SRC, "Company", "ContainmentProtocol.cs")))
gizmo = strip_cs_comments(read(os.path.join(SRC, "Company", "ContainmentAlarmGizmo.cs")))
campaign = strip_cs_comments(read(os.path.join(SRC, "Company",
                                               "RimroomsCampaignComponent.cs")))
services = strip_cs_comments(read(os.path.join(SRC, "Company", "CampaignServices.cs")))
console = strip_cs_comments(read(os.path.join(SRC, "Gate", "CompRimroomsGateConsole.cs")))
report = strip_cs_comments(read(os.path.join(SRC, "Facilities", "FacilityReport.cs")))
pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsFacilities.cs")))
categories = read(os.path.join(MOD, "Defs", "RimroomsFacilityDefs",
                               "RR_FacilityCategories.xml"))
company_keys = read(os.path.join(KEYED, "RR_Company.xml"))
portal_keys = read(os.path.join(KEYED, "RR_Portals.xml"))

print("")
print("containment is seen across every owned map, which is the whole gap")
print("-" * 78)

holders = body_of(watch, "List<HolderState> OccupiedHolders()")
check("the sweep walks every loaded map rather than one",
      "Find.Maps" in holders and "campaign.OwnsMap(map)" in holders,
      "-- reading a single map is precisely the limitation this file exists to lift")
check("and it never reads the map on screen to decide what to collect",
      "Find.CurrentMap" not in watch,
      "-- the survey is map-agnostic; only the two alerts care which map is in view")
check("the cache is keyed on the tick AND the game object",
      "ReferenceEquals(game, cachedGame)" in holders,
      "-- a second save landing on the same tick would otherwise return the first game's "
      "despawned things")
# The risk is a DEF reference, which would need a MayRequire gate and would cover no modded
# holder. `CompHoldingPlatformTarget` is a comp *type* in the base assembly and is fine -- an
# earlier version of this check matched the substring and flagged it, which was the check being
# wrong rather than the code.
check("holders are matched by capability, never by an expansion defName",
      "TryGetComp<CompEntityHolder>()" in watch and
      "ThingRequestGroup.EntityHolder" in watch and
      "ThingDefOf.HoldingPlatform" not in watch and '"HoldingPlatform"' not in watch and
      "ThingDefOf." not in watch,
      "-- CompEntityHolder is in the base assembly, so this needs no gate and covers a "
      "modded holder with nothing naming it")
collect = body_of(watch, "void Collect(Map map)")
check("escaping is Core's own flag, not a judgement of ours",
      "target.isEscaping" in collect,
      "-- nothing here may decide that a subject is getting out")
check("unpowered reads the holder's own power trader",
      "CompPowerTrader" in collect and "power.PowerOn" in collect)

print("")
print("the alerts never speak about the map Core is already speaking about")
print("-" * 78)

for cls, field in (("Alert_RimroomsContainmentBreachElsewhere", "Escaping"),
                   ("Alert_RimroomsContainmentUnpoweredElsewhere", "Unpowered")):
    body = body_of(alerts, "class %s : Alert" % cls)
    check("%s skips the current map" % cls,
          "state.Map == Find.CurrentMap) { continue; }" in body,
          "-- two alerts about one platform teach a player to scroll past both")
    check("%s reads the shared survey rather than sweeping itself" % cls,
          "ContainmentWatch.OccupiedHolders()" in body,
          "-- an alert with its own sweep can disagree with the pane and the procedure")
    check("%s reports on %s" % (cls, field), "state.%s" % field in body)

unpowered = body_of(alerts, "class Alert_RimroomsContainmentUnpoweredElsewhere : Alert")
check("the unpowered alert stands down for a platform already being escaped from",
      "if (state.Escaping) { continue; }" in unpowered,
      "-- otherwise one platform produces both a critical and a high alert")
check("neither alert restates containment strength or activity level",
      "ContainmentStrength" not in alerts and "ActivityLevel" not in alerts and
      "CompActivity" not in alerts,
      "-- Alert_InsufficientContainmentStrength and Alert_DangerousActivity already judge "
      "both, and a second opinion beside a shown rule is the defect this project keeps "
      "catching in presentation work")
check("the two priorities are Critical then High",
      "AlertPriority.Critical" in alerts and "AlertPriority.High" in alerts)

print("")
print("the security procedure is one standing order, and it acts")
print("-" * 78)

execute = body_of(protocol, "int Execute(RimroomsCampaignComponent campaign)")
check("the response calls the gate's own existing cutoff",
      "gate.TriggerEmergencyCutoff().Success" in execute,
      "-- the same method the player's own cutoff button calls, so the two cannot disagree "
      "about what closing a connection means")
check("it only touches designated gates that are actually open",
      "gate.IsDesignated" in execute and "gate.IsOpening" in execute)
check("it only touches maps the company owns",
      "campaign.OwnsMap(map)" in execute)
check("the procedure opens nothing, moves nobody and touches no subject",
      not re.search(r"TryAcceptPawn|EjectContents|DeSpawn|GenSpawn|OpenPortal|isEscaping\s*=",
                    protocol),
      "-- it is one call on gates that are already open, and nothing else")
tick = body_of(protocol, "void TickProcedure(RimroomsCampaignComponent campaign)")
check("the procedure is latched so one incident fires it once",
      "campaign.BreachResponded" in tick and "campaign.NoteBreachResponded()" in tick)
check("and the latch is rearmed only when nothing anywhere is getting out",
      "campaign.ClearBreachResponded();" in tick,
      "-- rearming during a breach would slam the doors twice for one incident")
check("the procedure never re-decides what a breach is",
      "ContainmentWatch.AnyBreach()" in tick and "isEscaping" not in protocol,
      "-- ContainmentWatch reports Core's flag; forming a second opinion here is how a "
      "chokepoint stops being one")
alarm = body_of(protocol, "CompanyActionResult SoundTheAlarm(RimroomsCampaignComponent campaign)")
check("the manual alarm runs the same body as the automatic procedure",
      "Execute(campaign)" in alarm,
      "-- two code paths for slam-the-doors are two chances to disagree")
check("the manual alarm refuses rather than reporting a success that closed nothing",
      "RR_Containment_NothingOpen" in alarm,
      "-- a button that claims success while doing nothing teaches a player it is broken")
check("the alarm latches too, so the automatic path cannot fire on top of it",
      "campaign.NoteBreachResponded();" in alarm)

print("")
print("the standing order is saved, defaulted safe, and reachable")
print("-" * 78)

check("the order and the latch are both persisted",
      'Scribe_Values.Look(ref cutConnectionsOnBreach, "rr_cutConnectionsOnBreach", true);'
      in campaign and
      'Scribe_Values.Look(ref breachResponded, "rr_breachResponded", false);' in campaign)
check("the order defaults to armed, so an older save loads safe",
      "private bool cutConnectionsOnBreach = true;" in campaign and
      '"rr_cutConnectionsOnBreach", true)' in campaign,
      "-- Scribe hands back the default for a missing field; defaulting to false would "
      "silently disarm every existing save")
check("the order is written only through the protocol",
      "internal void SetCutConnectionsOnBreach(bool cut)" in campaign and
      "campaign.SetCutConnectionsOnBreach(cut);" in protocol and
      campaign.count("cutConnectionsOnBreach = ") == 2,
      "-- one declaration-with-initialiser and one setter; a third writer would be a second "
      "place that decides the order")
check("the procedure is actually ticked",
      "ContainmentProtocol.TickProcedure(this);" in services,
      "-- a procedure nothing calls is a procedure that never runs, which is the defect that "
      "left the whole campaign unreachable until 0.12.11-dev")
check("the alarm gizmo is attached to the console",
      "Company.ContainmentAlarmGizmo.For(parent)" in console)
check("the gizmo holds no rule of its own",
      "ContainmentProtocol.SoundTheAlarm(campaign)" in gizmo and
      "TriggerEmergencyCutoff" not in gizmo and "isEscaping" not in gizmo,
      "-- every condition and the whole effect belong to the protocol")
check("the gizmo is on a comms console and not on a machining table",
      "console is Building_CommsConsole" in gizmo,
      "-- the same component is on both, and orders are not given from a machining table")
check("it is disabled with its reason rather than hidden",
      "alarm.Disable(" in gizmo,
      "-- invariant 28: a button that vanishes teaches nothing")

print("")
print("containment rooms: the tenth facility category, matched by capability")
print("-" * 78)

check("the category def exists with a description",
      "<defName>RR_Facility_Containment</defName>" in categories and
      "<includeContainment>true</includeContainment>" in categories and
      "<description>" in categories.split("RR_Facility_Containment")[1][:900])
check("it names no expansion def at all",
      "HoldingPlatform" not in categories and "Electroharvester" not in categories,
      "-- a <li> naming an Anomaly defName is read by check-dlc-gating as an ungated "
      "expansion reference, and would cover no modded holder either")
matches = body_of(report, "public bool Matches(Building building)")
check("the match is by comp, plus Core's own prisoner-bed test",
      "TryGetComp<CompEntityHolder>()" in matches and "bed.ForPrisoners" in matches,
      "-- containment is not an Anomaly-only idea here; on a Core-only install a prisoner "
      "bed is the only kind there is")
check("the containment branch is gated on the flag, so no other category picks it up",
      "if (includeContainment)" in matches)

print("")
print("the branch can read all of it")
print("-" * 78)

containment_pane = body_of(pane, "void DrawContainment(Listing_Standard listing")
check("the pane reads the shared survey rather than counting holders itself",
      "Threats.ContainmentWatch.OccupiedHolders()" in containment_pane,
      "-- the pane, the alerts and the procedure must not disagree about what is held")
check("the pane actually draws the count",
      'listing.Label("RR_Containment_Held".Translate(holders.Count))' in containment_pane,
      "-- a key present in the file is not a claim that anything is drawn")
check("the pane states the standing order in BOTH directions",
      '"RR_Containment_ProcedureOn".Translate()' in containment_pane and
      '"RR_Containment_ProcedureOff".Translate()' in containment_pane,
      "-- a procedure only described when armed is unreadable exactly when it matters")
check("the pane can flip the order",
      "ContainmentProtocol.SetCutOnBreach(campaign, !cut)" in containment_pane)
check("the pane section is reached from the facilities pane",
      "DrawContainment(listing, campaign);" in pane)

for key in ("RR_Containment_Held", "RR_Containment_Escaping", "RR_Containment_Unpowered",
            "RR_Containment_ProcedureOn", "RR_Containment_ProcedureOff",
            "RR_Containment_Arm", "RR_Containment_Disarm", "RR_Containment_AlarmLabel",
            "RR_Containment_AlarmDesc", "RR_Containment_NothingOpen",
            "RR_Letter_ContainmentCutLabel", "RR_Letter_ContainmentCutText"):
    check("%s is translated" % key, "<%s>" % key in company_keys)
for key in ("RR_Alert_ContainmentBreach", "RR_Alert_ContainmentBreachDesc",
            "RR_Alert_ContainmentUnpowered", "RR_Alert_ContainmentUnpoweredDesc"):
    check("%s is translated" % key, "<%s>" % key in portal_keys)

check("every keyed string used here is a literal, never assembled",
      not re.search(r'"RR_(Containment|Alert_Containment)\w*"\s*\+', watch + alerts +
                    protocol + gizmo + pane),
      "-- an assembled key cannot be checked, and this project has caught that five times")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: containment is visible everywhere it exists, the procedure acts, and "
      "Core keeps the map in view to itself")
