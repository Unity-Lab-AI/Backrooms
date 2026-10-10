# -*- coding: utf-8 -*-
"""Claims for the two defects the owner found in play. Neither had one.

**This is why both reached a running game.**

* Nothing asserted that a start ships the items its own systems require. `ExpeditionCargo`
  demands one `TextBook` and the laboratory start spawned none, so the first dispatch on every
  fresh lab start refused -- and no proof, checker or plant noticed.
* Nothing asserted that a crossing checks the door. `OrderCrossing` validated the approach cell
  and never asked whether the gate would open, so a locked door refused with no reason at all.

The first claim is **derived, not listed**: it reads `RecordBooksRequired` and the carrier def out
of the source and then looks for that def in the start. A hand-typed item list here would be a
second derivation that goes stale the first time the requirement changes -- which is exactly how
the recorder-to-book change at 0.12.24-dev slipped past.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STARTS = os.path.join(REPO, ".local", "register", "proof-starts.py")
CIRCUIT = os.path.join(REPO, ".local", "register", "proof-gate-circuit.py")

# ---------------------------------------------------------------- 1. the start ships the book
starts = io.open(STARTS, encoding="utf-8").read()
ANCHOR = u"print(\"\")\n"
if starts.count(ANCHOR) < 1:
    print("STARTS ANCHOR PROBLEM")
    raise SystemExit(1)

BOOK_CLAIM = u'''
# =============================================================== what a dispatch requires
# **The owner found this in a running game**: *"if i use approach gate and dispach to coordinate
# it says no book, i have no books"*. `ExpeditionCargo.RecordBooksRequired` is 1, of
# `CompRouteEvidence.NativeCarrierDef`, and the laboratory start spawned none -- so the first
# dispatch on every fresh lab start refused, and nothing in the battery noticed.
#
# **Derived, never listed.** The count and the def name are read out of the source, so a change
# to either fails here instead of silently making the start short. A hand-typed list is how the
# recorder-to-book change at 0.12.24-dev slipped past in the first place.
_cargo = io.open(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Expedition",
                              "ExpeditionCargo.cs"), encoding="utf-8-sig").read()
_route = io.open(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Investigation",
                              "CompRouteEvidence.cs"), encoding="utf-8-sig").read()
_required = re.search(r"RecordBooksRequired\\s*=\\s*(\\d+)", _cargo)
_carrier = re.search(r'GetNamedSilentFail\\("([A-Za-z_]+)"\\)', _route)
_starts_xml = io.open(os.path.join(
    REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs", "RimroomsStartDefs",
    "RR_Starts.xml"), encoding="utf-8-sig").read()
_lab = re.search(r"<scenarioId>async_industries</scenarioId>.*?(?=<RimroomsStartDef>|$)",
                 _starts_xml, re.S)
_lab_block = _lab.group(0) if _lab else ""
_book_count = len(re.findall(r"<thing>%s</thing>" % (_carrier.group(1) if _carrier else "NOPE"),
                             _lab_block))

check("THE LABORATORY START SHIPS THE BOOK EVERY DISPATCH REQUIRES",
      _required is not None and _carrier is not None
      and _book_count >= int(_required.group(1)),
      "-- `ExpeditionCargo` needs %s of %r and the start spawns %d. **A start that cannot run "
      "its own first objective is the defect the owner hit in play**"
      % (_required.group(1) if _required else "?",
         _carrier.group(1) if _carrier else "?", _book_count))

check("and it ships a spare, because a branch that loses its only book cannot work",
      _book_count >= 2,
      "-- one to take into the field and one in reserve")

'''

index = starts.rindex(u"\nif failures:")
starts = starts[:index] + BOOK_CLAIM + starts[index:]
io.open(STARTS, "w", encoding="utf-8", newline="").write(starts)

# ---------------------------------------------------------------- 2. the crossing asks the door
circuit = io.open(CIRCUIT, encoding="utf-8").read()
DOOR_CLAIM = u'''
# =============================================================== the door itself
# **The owner's gate read `Door locked` with every other condition green**: calibrated, operator
# on station, connection open, charge ten times the opening cost. `OrderCrossing` validated the
# APPROACH cell -- on the near side -- and never asked whether the door would open, so the crew
# were ordered somewhere they could reach through something they could not pass, with no reason.
check("A CROSSING ASKS WHETHER THE GATE'S DOOR WILL ACTUALLY OPEN",
      "private static string DoorBlockerKey(PortalConnectionRecord connection, Pawn pawn)" in travel
      and "string doorBlock = DoorBlockerKey(connection, pawn);" in travel
      and "door.PawnCanOpen(pawn)" in travel,
      "-- **DEFINED AND CALLED.** Found in a running game, where a locked door refused every "
      "crossing silently")

check("and it asks through Core, so a re-classed door answers for itself",
      "as Building_Door" in travel and "DoorsExpanded" not in travel,
      "-- `PawnCanOpen` is public and virtual. The owner's gate is a door another mod re-classed, "
      "and nothing here names that mod or references its assembly")

check("and a held-open or already-open door is never refused",
      "if (door.HoldOpen || door.FreePassage) { return null; }" in travel,
      "-- neither needs permission, and refusing one would break a gate the player had "
      "deliberately pinned open")

'''
index = circuit.rindex(u'\nprint("")\nif failures:')
circuit = circuit[:index] + DOOR_CLAIM + circuit[index:]
io.open(CIRCUIT, "w", encoding="utf-8", newline="").write(circuit)

after_starts = io.open(STARTS, encoding="utf-8").read()
after_circuit = io.open(CIRCUIT, encoding="utf-8").read()
failures = []
if u"THE LABORATORY START SHIPS THE BOOK EVERY DISPATCH REQUIRES" not in after_starts:
    failures.append("the book claim was not added")
if u"A CROSSING ASKS WHETHER THE GATE'S DOOR WILL ACTUALLY OPEN" not in after_circuit:
    failures.append("the door claim was not added")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("claims added: the start ships the book (derived), and the crossing asks the door")
