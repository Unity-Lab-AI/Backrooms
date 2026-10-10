# -*- coding: utf-8 -*-
"""Claims and plants for the four defects behind the owner's three refusal messages."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-gate-links-carry.py")

# ---------------------------------------------------------------------- claims
ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''frontier = _read(_SRC, "Portals", "NaturalFrontierService.cs")
guarantee = _read(_SRC, "Portals", "GuaranteedFrontiers.cs")
services = _read(_SRC, "Company", "CampaignServices.cs")

# ------------------------------------------ a gate is never a door somebody needs
# Owner: *"i found a door that was a gate, but it was where a normal door should of been (gates
# natural need to not also be used and needed as normal doors, becasue on the other side was the
# rest of the backrooms map)"*. The guarantee collected EVERY door on the coordinate and picked
# two, so a door between two rooms could become a permanently open one-way gate and take an
# ordinary route away.
check("A NATURAL GATE IS ONLY EVER A DEAD-END DOOR",
      "internal static bool LeadsNowhere(Thing door)" in frontier
      and "return open == 1;" in frontier
      and 'if (!LeadsNowhere(door)) { return "RR_Frontier_LeadsNowhere"; }' in frontier
      and "if (!NaturalFrontierService.LeadsNowhere(door)) { continue; }" in guarantee,
      "-- checked inside `Evaluate`, so the glow, the float menu and the discovery all agree, AND "
      "inside the guarantee, so the chosen pair cannot be doors the service would then refuse. "
      "`FalseOpening` already builds *\\"doors to now where\\"* onto rock, so **the door that should "
      "not be there is the one that leads somewhere else**")

check("and another door counts as a way through, not as rock",
      "side.Walkable(map) || side.GetEdifice(map) is Building_Door" in frontier,
      "-- two doors in a row is still a route somebody walks")

# ------------------------------- the string length that capped the Backrooms at two
# **THE BIGGEST OF THE FOUR.** A coordinate's id embeds its parent's entire id, so a discovery id
# grew about eighty characters per level: 88 for the first step inward, 168 for the second -- past
# the 128 limit, refused with `RR_Company_InvalidRequest`, *"that request is not valid for this
# branch"*. `MaximumNaturalDepth` was unreachable and *"the backrooms never ends persay"* could
# not happen.
check("GOING DEEPER IS NOT CAPPED BY A STRING LENGTH",
      "public const int MaximumDiscoveryIdLength = 128;" in services
      and "discoveryId.Length > MaximumDiscoveryIdLength" in services
      and "private static string DiscoveryIdFor(FrontierOrigin origin, Thing door)" in frontier
      and "if (full.Length <= RimroomsCampaignComponent.MaximumDiscoveryIdLength) { return full; }"
      in frontier,
      "-- the composer reads the limit the enforcer uses. A validator and its caller carrying "
      "separate copies of one number is the defect this project has paid for three times in a week")

check("and the long form is kept whenever it fits, so saved coordinates still resolve",
      'string full = origin.OriginId + ":" + position;' in frontier
      and 'return "o" + first.ToString("x8") + second.ToString("x8") + ":" + position;' in frontier,
      "-- byte-for-byte what it always was below the limit, and an id that would be refused never "
      "existed in a save to begin with. **Two hashes, not one**: a single 31-bit FNV value shared "
      "by two parents would merge two different places into one coordinate, which is worse than "
      "any refusal")

# ----------------------------------- a way out is not a way deeper, and both work now
# A deeper find registers a portal EDGE. A way out saves a world-exit record and registers NO
# edge, because leaving for the world map is a caravan. The first draft asked for an edge in both
# cases, so a world exit recorded correctly and then reported that surveying was unavailable.
check("A WAY OUT AND A WAY DEEPER ARE BOTH WALKABLE FROM THE MENU",
      "PortalConnectionRecord edge = EdgeFor();" in gatecomp
      and "if (edge != null)" in gatecomp
      and "campaign.WorldExitFor(parent) != null" in gatecomp
      and "Show(WalkOutToWorld());" in gatecomp,
      "-- the edge for a deeper find, the caravan for a way out. Asking `EdgeFor()` for a world "
      "exit returns null BY DESIGN, and the first draft read that as a failure and said "
      "*\\"surveying doors is unavailable\\"*, which is neither true nor useful")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("five claims added")

# ----------------------------------------------------------------------- plants
P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------------------- a gate on a door somebody needs
    ("A NATURAL GATE LANDS ON AN ORDINARY INTERIOR DOOR AGAIN", FRONTIER,
     '        if (!LeadsNowhere(door)) { return "RR_Frontier_LeadsNowhere"; }',
     '        if (false) { return "RR_Frontier_LeadsNowhere"; }'),

    ("the guarantee picks from every door on the map again", GUARANTEE,
     "                if (!NaturalFrontierService.LeadsNowhere(door)) { continue; }" + chr(10), ""),

    ("a door with two ways out counts as a dead end", FRONTIER,
     "            return open == 1;", "            return open <= 2;"),

    ("and a second door beside it stops counting as a route", FRONTIER,
     "                if (side.Walkable(map) || side.GetEdifice(map) is Building_Door) { open++; }",
     "                if (side.Walkable(map)) { open++; }"),

    # ------------------- the string length that capped the Backrooms at two levels
    ("GOING DEEPER IS CAPPED BY A STRING LENGTH AGAIN", FRONTIER,
     "            string discoveryId = DiscoveryIdFor(origin, door);",
     '            string discoveryId = origin.OriginId + ":" + origin.KeyPrefix +' + chr(10)
     + '                door.Position.x + "," + door.Position.z;'),

    ("the composer carries its own copy of the limit", SERVICES,
     "                discoveryId.Length > MaximumDiscoveryIdLength ||",
     "                discoveryId.Length > 128 ||"),

    ("the shortened id drops one of its two hashes, so two places can merge", FRONTIER,
     '            return "o" + first.ToString("x8") + second.ToString("x8") + ":" + position;',
     '            return "o" + first.ToString("x8") + ":" + position;'),

    # --------------------------------------- a way out offered a crossing that does not exist
    ("A WAY OUT IS OFFERED A MAP CROSSING THAT DOES NOT EXIST", COMP,
     "                RimroomsCampaignComponent campaign = Campaign();" + chr(10)
     + "                if (campaign != null && campaign.WorldExitFor(parent) != null)",
     "                RimroomsCampaignComponent campaign = Campaign();" + chr(10)
     + "                if (false)"),

    # --------------------------------------- a recorded gate that nothing could enter
    ("A DISCOVERED GATE GOES DARK AND DEAD AGAIN", COMP,
     "            if (!IsLiveGate && !IsRecordedGate)", "            if (!IsLiveGate)"),

    ("the recorded gate stops being lit", COMP,
     "        public bool ShouldBeLitNow() { return IsLiveGate || recordedGate || frontierGate; }",
     "        public bool ShouldBeLitNow() { return IsLiveGate || frontierGate; }"),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(P_ANCHOR, P_NEW, 1)

# The suite needs the three extra targets.
T_ANCHOR = u'COMP = SRC + "/Portals/CompRimroomsEmergence.cs"'
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d" % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(T_ANCHOR, T_ANCHOR
                      + u'\nFRONTIER = SRC + "/Portals/NaturalFrontierService.cs"'
                      + u'\nGUARANTEE = SRC + "/Portals/GuaranteedFrontiers.cs"'
                      + u'\nSERVICES = SRC + "/Company/CampaignServices.cs"', 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite)
print("ten plants added")
