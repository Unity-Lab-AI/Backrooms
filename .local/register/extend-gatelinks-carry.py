# -*- coding: utf-8 -*-
"""Stage-four claims: a natural gate can be broken or carried, and the route follows."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

text = io.open(PROOF, encoding="utf-8").read()

# Find the file's own tail so the claims land before the verdict.
TAIL = 'print("")\nif failures:'
if text.count(TAIL) != 1:
    print("TAIL ANCHOR PROBLEM: %d" % text.count(TAIL))
    raise SystemExit(1)

NEW = '''print("")
print("A NATURAL GATE IS AN OBJECT YOU OWN: BREAK IT AND LOSE IT, CARRY IT AND KEEP IT")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"so we need a way to deconstruct natural gates too i
# think"*, *"and then u lose them forever but maybe allow minify move"*, and *"they are just doors
# too right that dont need the mechine gate systems"*.
#
# The third was confirmed by live measurement rather than inference: the natural gate in the
# owner's running game was a plain RimWorld.Building_Door in steel, already offering Deconstruct,
# Uninstall, Reinstall and the emergence gizmo, with no power, console, calibration or assembly.
import os as _os
_SRC = _os.path.join(REPO, "src", "RimroomsAsyncIndustries")


def _read(*parts):
    return io.open(_os.path.join(*parts), encoding="utf-8", errors="replace").read()


records = _read(_SRC, "Portals", "PortalConnectionRecord.cs")
network = _read(_SRC, "Portals", "RimroomsPortalNetwork.cs")
crossing = _read(_SRC, "Portals", "PortalCrossingService.cs")
comp = _read(_SRC, "Portals", "CompRimroomsEmergence.cs")
warning = _read(_SRC, "Portals", "PortalDoorWarning.cs")
portal_keyed = io.open(_os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6",
                                     "Languages", "English", "Keyed", "RR_Portals.xml"),
                       encoding="utf-8-sig", errors="replace").read()

check("A DESTROYED GATE STILL ENDS ITS ROUTE, WHICH IS WHAT THE OWNER ASKED FOR",
      "ValidDoor(endpoint.Anchor, endpoint.ApproachCell)" in network
      and "!anchor.Destroyed" in network,
      "-- *\\"and then u lose them forever\\"*. EndpointPresent refuses an edge whose anchor is "
      "destroyed, so the route is gone the moment the door is. That already held; nothing had to "
      "be added for it")

check("and the player is warned before they do it",
      "RR_Portals_RemoveWayInConfirm" in warning and "destructive: breaking" in warning,
      "-- informed consent rather than prohibition, which is what the owner asked for on "
      "2026-09-29 and this mod cannot honestly do otherwise: Core decides destructibility at the "
      "def level")

follow_at = records.find("internal bool TryFollowMovedAnchor(Thing thing, IntVec3 approach)")
follow_body = records[follow_at:records.find(chr(10) + "        }", follow_at)] \\
    if follow_at >= 0 else ""

check("A CARRIED GATE TAKES ITS ROUTE WITH IT",
      follow_at >= 0
      and "public int NotifyAnchorInstalled(Thing anchor)" in network
      and "network.NotifyAnchorInstalled(parent)" in comp,
      "-- *\\"but maybe allow minify move\\"*. Before this, uninstalling lost the route exactly "
      "as destroying did, because EndpointPresent also requires Anchor.Position == AnchorCell")

check("IT ONLY EVER FOLLOWS THE SAME DOOR, NEVER A LOOKALIKE",
      follow_at >= 0 and "anchor != thing) { return false; }" in follow_body,
      "-- the snapshot this replaces existed so a moved door could not silently redirect a "
      "route. A different door rebuilt in the same cell is not this endpoint and never becomes "
      "one, so a route cannot be captured by building something that looks like it")

check("a move is refused unless the door is on ground the branch owns",
      "if (!OwnsMap(Campaign, anchor.Map)) { return 0; }" in network,
      "-- the same test registration had to pass")

check("NOBODY CAN BE MID-CROSSING WHEN A ROUTE MOVES",
      "public bool IsConnectionInFlight(string connectionId)" in crossing
      and "!receipt.IsTerminal" in crossing
      and "crossings.IsConnectionInFlight(edge.Id)) { continue; }" in network,
      "-- invariant 55: a receipt that is not terminal is a pawn part-way through. The route is "
      "left broken and visible rather than re-pointed under a traveller, which is the safer of "
      "the two")

check("loading a save is not a move",
      "if (respawningAfterLoad || parent == null || Current.Game == null) { return; }" in comp,
      "-- respawningAfterLoad means the door is being restored where it already was and the "
      "saved route already points there; re-anchoring then would turn every load into a move")

check("uninstalling and deconstructing no longer say the same thing",
      "RR_Portals_MoveWayInConfirm" in warning
      and "<RR_Portals_MoveWayInConfirm>" in portal_keyed
      and "<RR_Portals_WayThroughMoved>" in portal_keyed
      and "bool carrying = map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall) != null;"
      in warning,
      "-- telling a player the same thing for both would be telling them something false about "
      "one of them, and the red destructive confirmation is reserved for the one that is")

''' + TAIL

io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(TAIL, NEW, 1))
print("stage-four claims added to proof-gate-links")
