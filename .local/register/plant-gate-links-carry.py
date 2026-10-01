# -*- coding: utf-8 -*-
"""Plants for the carry-a-doorway claims. Plant, require exit 1, restore. Verified writes."""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
RECORDS = SRC + "/Portals/PortalConnectionRecord.cs"
NETWORK = SRC + "/Portals/RimroomsPortalNetwork.cs"
CROSSING = SRC + "/Portals/PortalCrossingService.cs"
COMP = SRC + "/Portals/CompRimroomsEmergence.cs"
WARNING = SRC + "/Portals/PortalDoorWarning.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"
DOORPATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml"
PROOF = ".local/register/proof-gate-links.py"
NL = chr(10)

PLANTS = [
    ("A DESTROYED DOOR STOPS ENDING ITS ROUTE", NETWORK,
     "            return anchor is Building_Door && anchor.Spawned && !anchor.Destroyed &&",
     "            return anchor is Building_Door && anchor.Spawned &&"),

    ("the deconstruct warning stops being destructive", WARNING,
     "                destructive: breaking,", "                destructive: false,"),

    ("A CARRIED DOOR STOPS TAKING ITS ROUTE WITH IT", RECORDS,
     "        internal bool TryFollowMovedAnchor(Thing thing, IntVec3 approach)",
     "        internal bool TryFollowMovedAnchorUnused(Thing thing, IntVec3 approach)"),

    ("the network never hears that a door was installed", COMP,
     "            int moved = network.NotifyAnchorInstalled(parent);",
     "            int moved = 0;"),

    ("the network stops offering to move a route at all", NETWORK,
     "        public int NotifyAnchorInstalled(Thing anchor)",
     "        public int NotifyAnchorInstalledUnused(Thing anchor)"),

    ("A ROUTE STARTS FOLLOWING A DIFFERENT DOOR IN THE SAME CELL", RECORDS,
     "            if (thing == null || anchor == null || anchor != thing) { return false; }",
     "            if (thing == null || anchor == null) { return false; }"),

    ("a route can move onto ground the branch does not own", NETWORK,
     "            if (!OwnsMap(Campaign, anchor.Map)) { return 0; }" + NL, ""),

    ("A ROUTE MOVES WHILE SOMEBODY IS PART-WAY THROUGH IT", NETWORK,
     "                if (crossings != null && crossings.IsConnectionInFlight(edge.Id)) { continue; }" + NL,
     ""),

    ("the in-flight test stops looking at live receipts", CROSSING,
     "            return receipts.Any(receipt => receipt != null && !receipt.IsTerminal &&",
     "            return receipts.Any(receipt => receipt != null &&"),

    ("the in-flight test disappears", CROSSING,
     "        public bool IsConnectionInFlight(string connectionId)",
     "        public bool IsConnectionInFlightUnused(string connectionId)"),

    ("LOADING A SAVE STARTS COUNTING AS A MOVE", COMP,
     "            if (respawningAfterLoad || parent == null || Current.Game == null) { return; }",
     "            if (parent == null || Current.Game == null) { return; }"),

    ("uninstall and deconstruct go back to saying the same thing", WARNING,
     '                (breaking ? "RR_Portals_RemoveWayInConfirm" : "RR_Portals_MoveWayInConfirm").Translate(),',
     '                "RR_Portals_RemoveWayInConfirm".Translate(),'),

    ("the uninstall designation stops being recognised", WARNING,
     "            bool carrying = map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall) != null;",
     "            bool carrying = false;"),

    ("the move message is never written", KEYED,
     "<RR_Portals_WayThroughMoved>", "<RR_Portals_WayThroughMovedUnused>"),

    ("the move confirmation is never written", KEYED,
     "<RR_Portals_MoveWayInConfirm>", "<RR_Portals_MoveWayInConfirmUnused>"),
    # ------------------------------------------ 0.12.53-dev: a gate looks like a gate
    ("A LIVE GATE STOPS BEING BLUE", COMP,
     "                if (live) { colorable.SetColor(LiveTintColor); }",
     "                if (false) { colorable.SetColor(LiveTintColor); }"),

    ("a live gate stops casting light", COMP,
     "                glower.GlowRadius = live ? LiveGlowRadius : 0f;",
     "                glower.GlowRadius = 0f;"),

    ("the glower comp is never added to the door", DOORPATCH,
     '<li Class="CompProperties_Glower">', '<li Class="CompProperties_GlowerUnused">'),

    # THE DOOR GOES INVISIBLE AGAIN. `ColorInt.ToColor` divides alpha by 255, so reusing the
    # glow constant as a tint paints the door at zero opacity -- which is exactly what the owner
    # reported as a missing door, with the glow still lighting the room around it.
    ("THE DOOR IS TINTED WITH THE GLOW CONSTANT AND GOES INVISIBLE", COMP,
     "if (live) { colorable.SetColor(LiveTintColor); }",
     "if (live) { colorable.SetColor(LiveGlowColor.ToColor); }"),

    ("the tint loses its opacity", COMP,
     "220f / 255f, 1f);", "220f / 255f, 0f);"),

    ("the colourable comp is never added to the door", DOORPATCH,
     "<compClass>CompColorable</compClass>", "<compClass>CompColorableUnused</compClass>"),

    # THE DEFECT THAT COST THE SEVENTH LAUNCH, PLANTED WHERE IT WAS BORN. This plant used to
    # mangle `Class="CompProperties_Colorable"` -- a type that does not exist -- so it proved a
    # broken line was load-bearing. Now it restores that line and requires the proof to refuse
    # it, which is the opposite verdict on the same string.
    ("THE COLOURABLE COMP GOES BACK TO THE CLASS THAT DOES NOT EXIST", DOORPATCH,
     "          <li>\n            <compClass>CompColorable</compClass>\n          </li>",
     '          <li Class="CompProperties_Colorable" />'),

    ("EVERY DOOR IN THE GAME STARTS GLOWING", COMP,
     "    public class CompRimroomsEmergence : ThingComp, IThingGlower",
     "    public class CompRimroomsEmergence : ThingComp"),

    ("the glow veto stops asking whether this is a live gate", COMP,
     "        public bool ShouldBeLitNow() { return IsLiveGate; }",
     "        public bool ShouldBeLitNow() { return true; }"),

    ("the patch default radius stops being dark", DOORPATCH,
     "<glowRadius>0</glowRadius>", "<glowRadius>8</glowRadius>"),

    ("A MARKED DOOR WITH NO WAY THROUGH STARTS GLOWING", COMP,
     "                if (!IsDesignated || parent == null || Verse.Current.Game == null) { return false; }",
     "                if (parent == null || Verse.Current.Game == null) { return false; }"),

    ("the live test stops asking the network", COMP,
     "                RimroomsPortalNetwork network = Verse.Current.Game.GetComponent<RimroomsPortalNetwork>();" + chr(10)
     + "                if (network == null || network.Connections == null) { return false; }",
     "                RimroomsPortalNetwork network = null;" + chr(10)
     + "                if (network == null) { return true; }"),

    ("a dead gate keeps its colour", COMP,
     "                else if (colorable.Active) { colorable.Disable(); }", "                else { }"),

    # ------------------------------------------ and is walked through like one
    ("RIGHT-CLICKING THE GATE NO LONGER OFFERS TO WALK THROUGH IT", COMP,
     "        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)",
     "        public IEnumerable<FloatMenuOption> CompFloatMenuOptionsUnused(Pawn selPawn)"),

    ("the menu stops ordering a real crossing", COMP,
     "                Show(PortalTravelService.OrderCrossing(selPawn, subject));",
     "                Show(CompanyActionResult.Applied());"),

    ("THE MENU STARTS DECIDING ELIGIBILITY ITSELF", COMP,
     "            string refusal = RimroomsPortalCrossingService.EligibilityFailureKey(selPawn);",
     "            string refusal = selPawn.Drafted ? \"RR_PortalTravel_NoPerson\" : null;"),

    ("a pawn who cannot cross is hidden instead of told why", COMP,
     "                yield return new FloatMenuOption(" + chr(10)
     + '                    "RR_DoorCross_EnterRefused".Translate(refusal.Translate()), null);',
     "                yield break;"),

    ("the menu is offered on a door that is not a live gate", COMP,
     "            if (!IsLiveGate) { yield break; }", "            if (false) { yield break; }"),

    ("the enter string is never written", KEYED,
     "<RR_DoorCross_Enter>", "<RR_DoorCross_EnterUnused>"),

    ("the refusal string is never written", KEYED,
     "<RR_DoorCross_EnterRefused>", "<RR_DoorCross_EnterRefusedUnused>"),

]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the target must pass before anything is planted")
code = subprocess.call([sys.executable, PROOF],
                       stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
print("  exit %d  %s" % (code, PROOF))
if code != 0:
    sys.stderr.write("BASELINE BROKEN: the proof already fails, so every plant would register as "
                     "caught and the run would prove nothing.\n")
    sys.exit(2)
print("")

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    write_verified(path, original.replace(old, new, 1))
    code = subprocess.call([sys.executable, PROOF],
                           stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    write_verified(path, original)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
