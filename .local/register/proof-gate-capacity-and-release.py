# -*- coding: utf-8 -*-
"""Claims about how many gates a branch runs, blind dialling, boarding a doorway up, and letting
a place go.

Four owner directions sat satisfied-but-unguarded. Measured before writing a line of this file:
`MaximumOperationalGates` and `PortalBoardUp` had **zero** proofs between them, while
`MaximumNaturalDepth` already had five. So the work here was never building the features -- they
ship -- it was that nothing stopped them regressing.

THE DIRECTIONS
--------------
**Three operational gates, not three addresses per gate.** Owner, 2026-10-04, correcting their own
sentence inside the same message: *"not three address per gate!!! up to three differnt operational
gates that can call any address and we need a Random address option not just company requested task
and quests at specific xcorrdinates"*. The arithmetic is theirs too: *"so u can have three addrerss
called at once wich would give 4 of 5 open maps"*.

**A way to turn a natural doorway off.** Owner: *"how do they turn them off to use the machine gates
for more controll and aiming deeper?"* and *"get 5 natural gates u cant use a machine gate"*.

**And the depth cap is NOT three.** The queue still records *"option 1"* from 2026-09-29 as natural
reach *"through depth 3"*. `NaturalFrontierService` says in its own words: **raised from 3 to 6 at
0.12.49-dev on owner direction 2026-09-30**, because *"the original three bands were chosen when a
level was 60x60 and two doors wide"*. The row is stale in its number and the source records why,
which is the treatment this project gives a supersession.

Absence claims go through `code_only`: every one of these files names the thing it avoids in order
to explain itself.
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
BINDING = os.path.join(SRC, "Gate", "NativeGateBinding.cs")
GATE = os.path.join(SRC, "Gate", "CompRimroomsGate.cs")
DIAL = os.path.join(SRC, "Portals", "PortalRandomDial.cs")
BOARD = os.path.join(SRC, "Portals", "PortalBoardUp.cs")
FRONTIER = os.path.join(SRC, "Portals", "NaturalFrontierService.cs")
HELD = os.path.join(SRC, "UI", "OperationsHeldPlaces.cs")
RELEASE = os.path.join(SRC, "Generation", "CoordinateRelease.cs")
RECORDS = os.path.join(SRC, "Company", "CampaignRecords.cs")


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def code_only(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


def flat(text):
    return " ".join(text.split())


def uses(text, name):
    """True when `name` appears as a WHOLE identifier, not as the prefix of a longer one.

    **THE SUBSTRING TRAP, KILLED ONCE INSTEAD OF CASE BY CASE.** `"WoodOnMap" in text` stays true
    when a plant renames it `WoodOnMapUnused`; so does `"PlaceBehind"` against `PlaceBehindUnused`,
    and `"RR_Release_Blocked"` against `RR_Release_BlockedUnused`. Three plants walked straight past
    three claims that way in one run, and the same trap had already caught me on
    `PAGES_NEGATORS_UNUSED` and on a definition line containing its own call text.

    A word boundary refuses all of them: after `WoodOnMap` in `WoodOnMapUnused` comes `U`, which is
    a word character, so there is no boundary and no match. Written as a helper so the next claim
    gets it for free rather than needing to remember.
    """
    return re.search(r"\b" + re.escape(name) + r"\b", text) is not None


def slice_member(text, name):
    """A member body cut to the next member signature, never to the next brace."""
    match = re.search(r"(?m)^\s*(?:public|private|internal|protected)[^\n;=]*\b"
                      + re.escape(name) + r"\s*\(", text)
    if not match:
        return ""
    rest = text[match.end():]
    following = re.search(r"(?m)^\s*(?:public|private|internal|protected)\s", rest)
    return text[match.start():match.end() + (following.start() if following else len(rest))]


binding = code_only(read(BINDING))
gate = code_only(read(GATE))
dial = code_only(read(DIAL))
board = code_only(read(BOARD))
frontier = code_only(read(FRONTIER))
held = code_only(read(HELD))
release = code_only(read(RELEASE))
records = code_only(read(RECORDS))

CLAIMS = []


def claim(label, ok, detail=""):
    CLAIMS.append((label, bool(ok), detail))


# ---------------------------------------------------- three operational gates, not three addresses
claim("the cap is declared as a constant rather than written inline",
      re.search(r"internal const int MaximumOperationalGates\s*=\s*3\s*;", binding) is not None)
count = slice_member(binding, "OperationalGateCount")
claim("the count walks EVERY loaded map, not just this one",
      "Find.Maps" in count and "for (int index = 0" in count,
      "operational is a property of the branch; counting one map would grant three more per map")
claim("the count is filtered to this branch",
      "nativeBranchId" in count and "branch" in count)
claim("a gate does not count itself",
      "other == this" in count)
claim("only designated gates count",
      "nativeDesignated" in count)
claim("the cap is read, not merely declared",
      binding.count("MaximumOperationalGates") >= 2,
      "a constant nobody reads is a number in a comment")
claim("THE CAP IS ON GATES AND NOT ON ADDRESSES",
      "MaximumOperationalGates" in binding
      and not re.search(r"MaximumAddresses|AddressesPerGate", binding),
      "the owner corrected their own phrasing: 'not three address per gate!!!'")

# -------------------------------------------------------------- the random address option
claim("a blind dial exists at all",
      os.path.isfile(DIAL) and "internal static class PortalRandomDial" in dial)
claim("the gate offers it as a command the player clicks",
      "RR_Dial_RandomLabel" in gate and "PortalRandomDial.Dial(" in gate)
claim("DIALLING CREATES AN ADDRESS, NOT A MAP",
      uses(dial, "DialPrefix") and not uses(dial, "GenerateMap")
      and not uses(dial, "EnsureSite"),
      "nothing is generated until somebody crosses, so dialling is free and the open-map budget "
      "is only spent when a place is actually opened")
claim("the blind dial is bounded",
      re.search(r"internal const int DeepestBlindDial\s*=\s*\d+\s*;", dial) is not None)
claim("the blind depth is DERIVED FROM THE SEED, never from Rand",
      "CampaignSeed.Derive(" in dial and not re.search(r"\bRand\.", dial),
      "dial twice and get the same place; reload and it is still there")
claim("the depth draw is bounded by the constant rather than by a literal",
      "depth < DeepestBlindDial" in slice_member(dial, "BlindDepth"),
      "the method also multiplies the constant, so containment alone passed a plant that "
      "replaced the loop bound with a literal")
claim("a dialled place is counted, so the feature can be read back",
      "DialledCount" in dial)

# ------------------------------------------------------- boarding a natural doorway up
claim("boarding up exists",
      os.path.isfile(BOARD) and "internal static class PortalBoardUp" in board)
claim("IT IS REAL WORK, NOT A BUTTON",
      re.search(r"internal const int BoardUpTicks\s*=\s*\d+\s*;", board) is not None
      and "JobDefName" in board,
      "a job a pawn walks to and performs, which is what every other costed action here is")
claim("it costs something, declared as a constant",
      re.search(r"internal const int WoodCost\s*=\s*\d+\s*;", board) is not None)
claim("the cost is checked against what is actually on the map",
      re.search(r"internal static int WoodOnMap\(", board) is not None
      and board.count("WoodOnMap(") >= 2,
      "DEFINITION AND A CALLER: a plant renamed the definition and the surviving call site "
      "kept the identifier alive, so even a word-boundary test passed")
claim("it names the place behind the door before closing it",
      re.search(r"internal static CoordinateRecord PlaceBehind\(", board) is not None
      and board.count("PlaceBehind(") >= 2,
      "a doorway boarded up without knowing where it led would make that place unreachable")
claim("it refuses with a named reason rather than failing silently",
      "RefusalFor" in board and "CompanyActionResult" in board)
claim("ordering and finishing are separate, so an interrupted job changes nothing",
      "Order(" in board and "Finish(" in board)
claim("the gizmo is offered only where there is something to board up",
      "PortalBoardUp.PlaceBehind(" in code_only(read(os.path.join(SRC, "Portals",
                                                                  "CompRimroomsEmergence.cs"))))

# --------------------------------------------------- the depth cap, and the row that is stale
claim("the natural depth cap is a constant",
      re.search(r"internal const int MaximumNaturalDepth\s*=\s*6\s*;", frontier) is not None)
claim("the supersession from three to six is RECORDED IN THE SOURCE",
      "Raised from 3 to 6" in read(FRONTIER),
      "the queue still records the 2026-09-29 answer of depth 3; the source says why it moved")
claim("the cap refuses rather than quietly minting a shallower place",
      "RR_Frontier_BeyondNaturalReach" in frontier,
      "a doorway that led somewhere other than where it should is a quieter and worse lie")
claim("the cap is checked AFTER the way home, so the deepest band is not a trap",
      flat(frontier).index("RR_Frontier_BeyondNaturalReach")
      > flat(frontier).index("int depth = source == null"))
claim("the cap bounds the free doorways and not the player's own gates",
      "does not restrain the player" in read(FRONTIER))

# ------------------------------------------------------------ letting a place go
claim("the held-places list exists as the owner chose",
      os.path.isfile(HELD) and "RR_Release_Heading" in held)
claim("it shows what is held against the budget, in BOTH the heading and the detail",
      held.count("OpenMapBudget.Held") == 2 and held.count("OpenMapBudget.Budget") == 2,
      "containment passed a plant that blanked one of the two")
claim("it asks the release guard rather than deciding for itself",
      "CoordinateRelease.RefusalFor(" in held)
claim("A REFUSAL IS THE ROW'S OWN STATE, NOT A DISABLED BUTTON",
      uses(held, "RR_Release_Blocked"),
      "a greyed-out button says no without saying why")
claim("it says what would be left behind before anything is released",
      "CoordinateRelease.ItemsLeftBehind(" in held)
claim("the release is remembered in the save, which is the field the row asked for",
      'Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false)' in records)
claim("releasing sets that field",
      "coordinate.releasedByPlayer = true" in release)
claim("the coordinate RECORD survives a release, so re-opening returns to the same place",
      "coordinate.site = null" in release and "DeinitAndRemoveMap" in release
      and "coordinate.status = CoordinateStatus.Discovered" in release)
claim("a crew on the map refuses the release, animals and prisoners included",
      "RR_Release_CrewInside" in release
      and "IsPrisonerOfColony" in release and "Faction.OfPlayer" in release)
claim("a crossing part-way through refuses the release",
      "RR_Release_CrossingInFlight" in release)
claim("the headquarters can never be released",
      "RR_Release_Headquarters" in release)
claim("doors are told where they led BEFORE the edges go, and the edges BEFORE the map",
      flat(release).index("RememberOn(edge.First")
      < flat(release).index("ForgetConnection")
      < flat(release).index("DeinitAndRemoveMap"),
      "reversing any two of those is how a place becomes unreachable")
claim("exactly one place in the whole mod tears a map down",
      sum(code_only(read(os.path.join(base, name))).count("DeinitAndRemoveMap")
          for base, dirs, names in os.walk(SRC)
          for name in names if name.endswith(".cs")) == 1,
      "a second teardown is a second set of ordering rules to get wrong")

# ---------------------------------------------------------------------------------- report
bad = [(label, detail) for label, ok, detail in CLAIMS if not ok]
for label, ok, detail in CLAIMS:
    print("%s  %s" % ("ok   " if ok else "FAIL!", label))
    if detail and not ok:
        print("       %s" % detail)
print("")
print("%d of %d claims hold" % (len(CLAIMS) - len(bad), len(CLAIMS)))
sys.exit(1 if bad else 0)
