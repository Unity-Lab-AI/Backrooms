# -*- coding: utf-8 -*-
"""Prove every claim about gate capacity, blind dialling, boarding up and release can fail.

These four features all shipped and **nothing guarded two of them** -- `MaximumOperationalGates`
and `PortalBoardUp` had zero proofs between them. A feature that works today and has no claim on it
is a feature that breaks on the day somebody tidies it.

Three plants are the ones worth naming:

* **The teardown order reversed.** Nothing visibly breaks: the map still goes, the player still
  gets their budget back. The doors just quietly stop knowing where they led, and that place is
  unreachable for ever. There is no error and no log line.
* **The depth cap moved ahead of the way home.** The deepest natural band becomes a trap, which is
  the exact thing the comment above it says it must not be.
* **`Rand` in the blind dial.** It dials, it finds somewhere, it reads fine -- and the address is
  different after a reload, so a place the player wrote down is gone.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-gate-capacity-and-release.py"]

BINDING = "src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs"
GATE = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"
DIAL = "src/RimroomsAsyncIndustries/Portals/PortalRandomDial.cs"
BOARD = "src/RimroomsAsyncIndustries/Portals/PortalBoardUp.cs"
FRONTIER = "src/RimroomsAsyncIndustries/Portals/NaturalFrontierService.cs"
HELD = "src/RimroomsAsyncIndustries/UI/OperationsHeldPlaces.cs"
RELEASE = "src/RimroomsAsyncIndustries/Generation/CoordinateRelease.cs"
RECORDS = "src/RimroomsAsyncIndustries/Company/CampaignRecords.cs"
EMERGENCE = "src/RimroomsAsyncIndustries/Portals/CompRimroomsEmergence.cs"

_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def read_bytes(path):
    return io.open(path, "rb").read()


def write_verified(path, data):
    """Bytes in, bytes out. A BOM is part of a file and must survive a plant untouched."""
    for _ in range(6):
        try:
            io.open(path, "wb").write(data)
            if read_bytes(path) == data:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


PLANTS = [
    # ---- three operational gates --------------------------------------------------------
    ("the gate cap stops being three", BINDING,
     "internal const int MaximumOperationalGates = 3;",
     "internal const int MaximumOperationalGates = 9;", 1),

    ("the count looks at one map, granting three more per map", BINDING,
     "            List<Map> maps = Find.Maps;",
     "            List<Map> maps = new List<Map> { Find.CurrentMap };", 1),

    ("a gate counts itself, so two gates read as three", BINDING,
     "if (other == null || other == this || !other.nativeDesignated) { continue; }",
     "if (other == null || !other.nativeDesignated) { continue; }", 1),

    ("an undesignated door counts as an operational gate", BINDING,
     "if (other == null || other == this || !other.nativeDesignated) { continue; }",
     "if (other == null || other == this) { continue; }", 1),

    # ---- the blind dial -----------------------------------------------------------------
    ("the blind dial reaches for Rand, so a dialled place moves on reload", DIAL,
     "            int draw = CampaignSeed.Derive(campaign.BranchSeed, \"dial:depth:\" + index, 1);",
     "            int draw = Rand.Int;", 1),

    # Planted as REAL CODE, not a comment: the proof strips comments deliberately, so the first
    # version was testing nothing and reported MISSED with the claim entirely innocent. Same
    # mistake as the foreign-stamp plant last batch.
    ("the blind dial generates a map, so dialling spends the budget", DIAL,
     "        internal const string DialPrefix = ",
     "        static void Eager() { EnsureSite(); }\n"
     "        internal const string DialPrefix = ", 1),

    ("the blind depth is bounded by a literal instead of the constant", DIAL,
     "            while ((depth + 1) * (depth + 1) <= span && depth < DeepestBlindDial) { depth++; }",
     "            while ((depth + 1) * (depth + 1) <= span && depth < 99) { depth++; }", 1),

    ("the dial stops being offered on the gate", GATE,
     '                    defaultLabel = "RR_Dial_RandomLabel".Translate(),',
     '                    defaultLabel = "RR_Dial_Removed".Translate(),', 1),

    # ---- boarding a doorway up ----------------------------------------------------------
    ("boarding up becomes instant, so it is a button and not work", BOARD,
     "internal const int BoardUpTicks = 420;", "internal const int BoardUpTickCount = 420;", 1),

    ("boarding up becomes free", BOARD,
     "internal const int WoodCost = 25;", "internal const int WoodPrice = 25;", 1),

    ("the cost stops being checked against the map", BOARD,
     "    internal static int WoodOnMap(Map map)",
     "    internal static int WoodOnMapUnused(Map map)", 1),

    ("the door is boarded without knowing where it led", BOARD,
     "    internal static CoordinateRecord PlaceBehind(RimroomsCampaignComponent campaign, Thing door)",
     "    internal static CoordinateRecord PlaceBehindUnused(RimroomsCampaignComponent campaign, Thing door)",
     1),

    ("the gizmo stops asking what is behind the door", EMERGENCE,
     "PortalBoardUp.PlaceBehind(boardCampaign, parent) != null",
     "true", 1),

    # ---- the depth cap ------------------------------------------------------------------
    ("the natural depth cap becomes a literal", FRONTIER,
     "internal const int MaximumNaturalDepth = 6;",
     "internal const int MaximumNaturalBand = 6;", 1),

    ("the cap silently mints a shallower place instead of refusing", FRONTIER,
     '            { return CompanyActionResult.Refused("RR_Frontier_BeyondNaturalReach"); }',
     "            { depth = MaximumNaturalDepth; }", 1),

    ("the supersession record is deleted from the source", FRONTIER,
     "Raised from 3 to 6", "Set to 6", 1),

    # ---- letting a place go -------------------------------------------------------------
    ("THE TEARDOWN ORDER IS REVERSED -- the place becomes unreachable, silently", RELEASE,
     "                RememberOn(edge.First, coordinate, map);\n"
     "                RememberOn(edge.Second, coordinate, map);",
     "                // told later", 1),

    ("a crew on the map no longer refuses the release", RELEASE,
     '            { return "RR_Release_CrewInside"; }', "            { }", 1),

    ("an animal or a prisoner stops counting as somebody", RELEASE,
     "(pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony)",
     "pawn.Faction == Faction.OfPlayer && pawn.RaceProps.Humanlike", 1),

    ("a crossing part-way through no longer refuses the release", RELEASE,
     '{ return "RR_Release_CrossingInFlight"; }', "{ }", 1),

    ("the headquarters becomes releasable", RELEASE,
     'if (campaign.Headquarters == map) { return "RR_Release_Headquarters"; }', "", 1),

    ("the coordinate record is discarded, so re-opening finds a different place", RELEASE,
     "            coordinate.status = CoordinateStatus.Discovered;", "", 1),

    ("the release stops being remembered in the save", RECORDS,
     'Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);', "", 1),

    ("releasing forgets to set the field it saves", RELEASE,
     "            coordinate.releasedByPlayer = true;", "", 1),

    ("a SECOND place tears a map down, so the ordering rules have two owners", RELEASE,
     "            Current.Game.DeinitAndRemoveMap(map, false);",
     "            Current.Game.DeinitAndRemoveMap(map, false);\n"
     "            if (false) { Current.Game.DeinitAndRemoveMap(map, false); }", 1),

    # ---- the held-places list -----------------------------------------------------------
    ("the list decides for itself instead of asking the release guard", HELD,
     "                string refusal = CoordinateRelease.RefusalFor(campaign, record);",
     "                string refusal = null;", 1),

    ("a refusal becomes a silent disabled row", HELD,
     '"RR_Release_Blocked"', '"RR_Release_BlockedUnused"', 1),

    ("the list stops saying what would be left behind", HELD,
     "                int items = CoordinateRelease.ItemsLeftBehind(record);",
     "                int items = 0;", 1),

    ("the list stops showing what is held against the budget", HELD,
     "OpenMapBudget.Held, OpenMapBudget.Budget),\n                detail:",
     "0, 0),\n                detail:", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = read_bytes(path)
    needle = old.encode("utf-8")
    if original.count(needle) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:55], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(needle, new.encode("utf-8"), 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable] + PROOF,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == want
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted %d)"
          % ("CAUGHT " if ok else "MISSED!", label, code, want))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
