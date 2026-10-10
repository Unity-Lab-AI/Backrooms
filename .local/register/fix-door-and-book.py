# -*- coding: utf-8 -*-
"""The two blockers the owner hit in play: a locked gate door, and a start with no record book.

Both were diagnosed from the running game and **neither was fixed** until this.

## 1. A locked door stopped every crossing and nothing said so

The live gate's inspect string opened with **`Door locked`**. It is a
`DoorsExpanded.Building_DoorRemote`, which replaces Core's `Autodoor` thingClass and adds remote
locking.

`OrderCrossing` checks that the approach cell is standable and that the pawn can reach it -- the
cell on the **near** side. It never asks whether the door will open. So the pawn was ordered to a
cell it could reach, through a door it could not pass, and the player got no reason at all.

`Building_Door.PawnCanOpen(Pawn)` is **public and virtual** in Core, so the Doors Expanded override
answers for a remotely locked door without this code naming that mod or referencing its assembly.

## 2. The laboratory start ships no book, and every expedition needs one

`ExpeditionCargo.RecordBooksRequired` is **1**, of `CompRouteEvidence.NativeCarrierDef` -- Core's
`TextBook`. The live start spawns **112 fixtures across 17 types and not one book**, so
`RR_Exp_MissingRecordBook` refuses the first dispatch on a fresh laboratory start, every time.

The recorder was folded into a book at 0.12.24-dev and **the start's stock was never updated to
carry one.** Two go in -- one to use and one in reserve -- on the archive shelves, which is where
a branch would keep them.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRAVEL = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals", "PortalTravelService.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Portals.xml")
BUILDER = os.path.join(REPO, ".local", "register", "build-async-facility.py")

# ---------------------------------------------------------------- 1. the door
OLD = u"""            string fit = PortalTraversalPolicy.FitFailureKey(pawn, DoorwayWidth(connection));
            if (fit != null) { return CompanyActionResult.Refused(fit); }"""

NEW = u"""            string fit = PortalTraversalPolicy.FitFailureKey(pawn, DoorwayWidth(connection));
            if (fit != null) { return CompanyActionResult.Refused(fit); }

            // **A locked gate is a gate nobody walks through, and nothing used to say so.**
            // The checks below ask whether the APPROACH cell is standable and reachable -- that
            // cell is on the near side. None of them asks whether the door itself will open, so
            // a crew was ordered to a cell they could reach, through a door they could not pass,
            // and the player got no reason at all.
            //
            // `Building_Door.PawnCanOpen` is public and virtual in Core, so a door whose
            // thingClass another mod replaced answers for itself. Nothing here names that mod.
            string doorBlock = DoorBlockerKey(connection, pawn);
            if (doorBlock != null) { return CompanyActionResult.Refused(doorBlock); }"""

text = io.open(TRAVEL, encoding="utf-8-sig").read()
if text.count(OLD) != 1:
    print("TRAVEL ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)

HELPER_ANCHOR = u"""        /// <summary>Reconcile one interrupted crossing. Never invents a person or item.</summary>"""
HELPER = u'''        /// <summary>
        /// Why this person cannot pass the gate's own door, or null when they can.
        ///
        /// **Found in a running game**, where the gate read `Door locked` and every other
        /// condition was green: calibrated, operator on station, connection open, charge ten
        /// times what the opening cost. The crossing refused for no stated reason because
        /// nothing asked the door.
        ///
        /// Asked through Core's `Building_Door`, whose `PawnCanOpen` is public and virtual, so a
        /// door another mod has re-classed answers for itself. A gate that is not a
        /// `Building_Door` at all is left alone rather than guessed about.
        /// </summary>
        private static string DoorBlockerKey(PortalConnectionRecord connection, Pawn pawn)
        {
            if (connection == null || connection.First == null || pawn == null) { return null; }
            var door = connection.First.Anchor as Building_Door;
            if (door == null) { return null; }
            // Held open is passable whatever else is true, and a door standing open now is
            // passable for anyone -- neither needs permission.
            if (door.HoldOpen || door.FreePassage) { return null; }
            return door.PawnCanOpen(pawn) ? null : "RR_PortalTravel_DoorLocked";
        }

'''
if text.count(HELPER_ANCHOR) != 1:
    print("HELPER ANCHOR PROBLEM: %d" % text.count(HELPER_ANCHOR))
    raise SystemExit(1)
text = text.replace(HELPER_ANCHOR, HELPER + HELPER_ANCHOR, 1)
io.open(TRAVEL, "w", encoding="utf-8-sig", newline="").write(text)

ADDITION = u"""  <RR_PortalTravel_DoorLocked>That gate's door is locked, so nobody can walk through it. Select the door and unlock it, or set it to hold open.</RR_PortalTravel_DoorLocked>
"""
keyed = io.open(KEYED, encoding="utf-8-sig").read()
CLOSE = u"</LanguageData>"
if keyed.count(CLOSE) != 1:
    print("KEYED ANCHOR PROBLEM: %d" % keyed.count(CLOSE))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    keyed.replace(CLOSE, ADDITION + CLOSE, 1))

after_travel = io.open(TRAVEL, encoding="utf-8-sig").read()
after_keyed = io.open(KEYED, encoding="utf-8-sig").read()
failures = []
if u"private static string DoorBlockerKey(" not in after_travel:
    failures.append("the door check was not defined")
if u"string doorBlock = DoorBlockerKey(connection, pawn);" not in after_travel:
    failures.append("THE DOOR CHECK IS DEFINED AND NEVER CALLED")
if u"door.PawnCanOpen(pawn)" not in after_travel:
    failures.append("Core's own passability question is not asked")
if u"<RR_PortalTravel_DoorLocked>" not in after_keyed:
    failures.append("the refusal has no string")
if u"DoorsExpanded" in after_travel:
    failures.append("the fix names another mod's type; it must go through Building_Door")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("1. a locked gate door now refuses by name, through Core's own virtual PawnCanOpen")
print("2. NEXT: the record book goes into the start -- see add-start-book.py")
