# -*- coding: utf-8 -*-
"""Assert that a portal does not extend into the real world.

The property this exists for
---------------------------
Owner direction, 2026-09-29:

    "in the real world maps the portals dont extend into the real world environment so in the
     real world you can mine and build and explore directly behind the gates with out actually
     effecting the gate"

A portal is **its own door cell and nothing else**. It claims no radius, reserves no cells and
projects nothing onto the local map.

That was broken in a way nobody could have seen from a single file. `PortalEndpointRecord`
snapshotted the cell a traveller stands on at registration, and `RimroomsPortalNetwork.Availability`
validated that saved cell forever after -- so a wall built on it reported `Obstructed` **for the
life of the save**, with three other walkable cells beside the same door. No error, no message, no
crash: a permanently open gate that had simply stopped working.

The fix has two halves and both must hold:
  * the approach cell is **re-derived** when it has been built over, and
  * the anchor cell is **not**, because that snapshot is what stops a moved door silently
    redirecting a saved route.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


record = io.open(os.path.join(SRC, "Portals", "PortalConnectionRecord.cs"), encoding="utf-8-sig").read()
network = io.open(os.path.join(SRC, "Portals", "RimroomsPortalNetwork.cs"), encoding="utf-8-sig").read()
address = io.open(os.path.join(SRC, "Portals", "PortalAddressService.cs"), encoding="utf-8-sig").read()

# 1. The repair exists at all.
repair = re.search(r"internal bool TryRepairApproach\(\).*?\n        \}", record, re.S)
check("the endpoint can repair its approach cell", repair is not None,
      "-- a wall built beside a gate would brick it for the life of the save")
body = repair.group(0) if repair else ""

# 2. THE other half. It must not touch the anchor cell. That snapshot is the guard against a
#    moved door silently redirecting a saved route, and refreshing it would trade one silent
#    failure for a worse one.
check("the repair does not reassign the anchor cell",
      bool(body) and not re.search(r"anchorCell\s*=", body),
      "-- a moved door could then silently redirect a saved route")
check("the repair reassigns only the approach cell",
      bool(body) and re.search(r"approachCell\s*=", body) is not None)

# 3. It must re-derive through the single implementation, not invent its own scan. The comment
#    on ApproachCellFor says so in as many words: "callers must not re-derive it".
check("the repair re-derives through PortalAddressService.ApproachCellFor",
      "PortalAddressService.ApproachCellFor(" in body,
      "-- a second derivation would drift from the one every other caller uses")
check("ApproachCellFor is still the single derivation",
      len(re.findall(r"internal static IntVec3 ApproachCellFor", address)) == 1)

# 4. A door genuinely sealed on all four sides must report unusable rather than pretend.
check("the repair fails when no cell beside the door is standable",
      bool(body) and re.search(r"if \(!fresh\.IsValid\) \{ return false; \}", body) is not None,
      "-- it would report a usable approach that nobody can stand on")

# 5. The repair must run BEFORE availability tests standability, or it changes nothing.
i_repair = network.find("TryRepairApproach()")
i_test = network.find("ApproachCell.Standable(")
check("availability repairs before it tests standability",
      i_repair != -1 and i_test != -1 and i_repair < i_test,
      "-- the repair would run too late to matter")

# 6. THE safety claim. A receipt stores the approach cell it began with and refuses to continue
#    if it changed, which is what stops a transfer losing a pawn (invariant 55). Moving the cell
#    under a live transfer would trip that guard and abort a legitimate crossing.
inflight = re.search(r"if \(!CrossingInFlight\(edge\)\)\s*\{\s*edge\.First\.TryRepairApproach\(\);",
                     network, re.S)
check("the repair is skipped while a crossing is in flight", inflight is not None,
      "-- repairing under a live transfer trips the guard that protects a pawn mid-move")
check("CrossingInFlight asks the crossing service for receipts",
      re.search(r"RimroomsPortalCrossingService crossings = Current\.Game\.GetComponent", network) is not None)
check("CrossingInFlight compares against the connection id",
      "receipt.ConnectionId == edge.Id" in network,
      "-- a broader match would freeze repairs on unrelated connections")

# 7. Nothing anywhere may reserve, claim or protect cells around a portal. A portal is its own
#    door cell. If any of these ever appear in the portal sources, somebody has started
#    projecting the gate onto the map.
portal_sources = {}
for path in sorted(glob.glob(os.path.join(SRC, "Portals", "*.cs"))):
    portal_sources[os.path.basename(path)] = io.open(path, encoding="utf-8-sig").read()
banned = ["ReserveCell", "ClaimRadius", "portalRadius", "ProtectedRadius", "ReservedCells"]
for token in banned:
    holders = [name for name, text in portal_sources.items() if token in text]
    check("no portal source uses %s" % token, not holders,
          "-- found in " + ", ".join(holders) + "; a portal reserves nothing")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a portal is its own door cell and reserves nothing around it")
