#!/usr/bin/env python3
"""Re-run ValidateRecordRelationships' conditions against a save, naming the one that fails.

**The fields are scribed with an `rr_` prefix and the first diagnostic did not know that**, so it
reported every collection as empty on a save holding 44 projects, 4 contracts, 4 coordinates, 3
staff and a case. An all-zero reading of a 49 MB save should have been suspicious on its face.

Read-only. Mirrors `RimroomsCampaignComponent.ValidateRecordRelationships` condition by condition,
because the game collapses all of them into one fault key and logs no cause.
"""
import importlib.util
import io
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "diag", os.path.join(HERE, "diagnose-campaign-integrity.py"))
_diag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_diag)

SAVES = os.path.expanduser(
    "~/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves")


def value(node, tag, default=""):
    found = node.find("rr_" + tag)
    if found is None:
        found = node.find(tag)
    return (found.text or default).strip() if found is not None else default


def children(node, tag):
    found = node.find("rr_" + tag)
    if found is None:
        found = node.find(tag)
    return list(found) if found is not None else []


def main(argv):
    name = argv[0] if argv else None
    if not name:
        print(__doc__)
        return 1
    path = os.path.join(SAVES, name + ".rws")
    text = io.open(path, encoding="utf-8", errors="replace").read()
    root = ET.fromstring(_diag.campaign_block(text))

    coordinates = children(root, "coordinates")
    cases = children(root, "cases")
    evidence = children(root, "evidence")
    staff = children(root, "staff")
    contracts = children(root, "contracts")
    projects = children(root, "projects")

    coordinate_ids = set(value(c, "id") for c in coordinates)
    print("coordinates: %d  %s" % (len(coordinates), sorted(i[:34] for i in coordinate_ids)[:2]))
    print("cases      : %d" % len(cases))
    print("evidence   : %d" % len(evidence))
    print("staff      : %d" % len(staff))
    print("contracts  : %d" % len(contracts))
    print("projects   : %d" % len(projects))
    print("")

    faults = []

    # ---- staff: a pawnLoadId that is blank or repeated -------------------------------------
    seen = set()
    for member in staff:
        pawn = value(member, "pawnLoadId")
        if not pawn:
            faults.append("a staff record has a blank pawnLoadId")
        elif pawn in seen:
            faults.append("two staff records share pawnLoadId %r" % pawn)
        seen.add(pawn)

    # ---- cases: coordinate must exist, evidenceIds must resolve -----------------------------
    evidence_by_id = dict((value(e, "id"), e) for e in evidence)
    for case in cases:
        case_id = value(case, "id")
        coordinate = value(case, "coordinateId")
        if coordinate not in coordinate_ids:
            faults.append("case %r names coordinate %r, which is not in the save"
                          % (case_id[:28], coordinate[:34]))
        ids = [(li.text or "").strip() for li in children(case, "evidenceIds")]
        if len(ids) != len(set(ids)):
            faults.append("case %r repeats an evidence id" % case_id[:28])
        for evidence_id in ids:
            owner = evidence_by_id.get(evidence_id)
            if owner is None:
                faults.append("case %r claims evidence %r, which does not exist"
                              % (case_id[:28], evidence_id[:28]))
            elif value(owner, "caseId") != case_id:
                faults.append("case %r claims evidence %r, which belongs to case %r"
                              % (case_id[:28], evidence_id[:28], value(owner, "caseId")[:28]))

    # ---- contracts -------------------------------------------------------------------------
    for contract in contracts:
        template = value(contract, "templateId")
        coordinate = value(contract, "coordinateId")
        thing = value(contract, "requiredThingDefName")
        count = value(contract, "requiredCount", "0")
        rooms_needed = value(contract, "requiredSurveyedRooms", "0")
        odd = bool(thing) and count.isdigit() and int(count) > 0
        mission = odd and rooms_needed.isdigit() and int(rooms_needed) > 0
        if mission:
            if coordinate not in coordinate_ids:
                faults.append("consignment mission %r names a coordinate not in the save" % template[:34])
        elif odd:
            if coordinate:
                faults.append("odd-supply contract %r carries a coordinate id" % template[:34])
        elif coordinate not in coordinate_ids:
            faults.append("contract %r names coordinate %r, which is not in the save"
                          % (template[:30], coordinate[:34]))
        for field in ("basePaymentUsd", "bonusUsd", "requiredCount", "deliveredCount"):
            raw = value(contract, field, "0")
            if raw.lstrip("-").isdigit() and int(raw) < 0:
                faults.append("contract %r has a negative %s (%s)" % (template[:30], field, raw))
        if not template:
            faults.append("a contract has a blank templateId")

    # ---- projects --------------------------------------------------------------------------
    committed_incomplete = 0
    for project in projects:
        def_name = value(project, "researchDefName")
        completed = value(project, "completed", "False").lower() == "true"
        commited = value(project, "insightCommitted", "False").lower() == "true"
        operation = value(project, "insightOperationId")
        work = value(project, "workDone", "0")
        if not def_name:
            faults.append("a project record has a blank researchDefName")
        if completed and not commited:
            faults.append("project %r is completed but insight was never committed" % def_name[:34])
        if commited and not operation:
            faults.append("project %r committed insight with no operation id" % def_name[:34])
        if commited and not completed:
            committed_incomplete += 1
        try:
            if float(work or 0) < 0:
                faults.append("project %r has negative workDone" % def_name[:34])
        except ValueError:
            faults.append("project %r has a non-numeric workDone (%r)" % (def_name[:34], work))
    if committed_incomplete > 1:
        faults.append("%d projects have insight committed while incomplete; at most one is allowed"
                      % committed_incomplete)

    # ---- coordinates and their rooms -------------------------------------------------------
    for coordinate in coordinates:
        cid = value(coordinate, "id")[:30]
        for field in ("generatorVersion", "roomLibraryVersion"):
            raw = value(coordinate, field, "0")
            if not raw.isdigit() or int(raw) <= 0:
                faults.append("coordinate %r has %s=%r, which must be above zero"
                              % (cid, field, raw))
        rooms = children(coordinate, "rooms")
        indices = set()
        for room in rooms:
            index = value(room, "index", "0")
            width = value(room, "width", "0")
            height = value(room, "height", "0")
            family = value(room, "familyId")
            if not index.lstrip("-").isdigit() or int(index) < 0:
                faults.append("coordinate %r has a room with index %r" % (cid, index))
                continue
            if int(index) in indices:
                faults.append("coordinate %r repeats room index %s" % (cid, index))
            indices.add(int(index))
            if not width.isdigit() or int(width) <= 0 or not height.isdigit() or int(height) <= 0:
                faults.append("coordinate %r room %s has size %sx%s" % (cid, index, width, height))
            if not family:
                faults.append("coordinate %r room %s has a blank familyId" % (cid, index))
        for room in rooms:
            index = value(room, "index", "0")
            for link in children(room, "links"):
                target = (link.text or "").strip()
                if not target.lstrip("-").isdigit():
                    faults.append("coordinate %r room %s links to %r" % (cid, index, target))
                elif int(target) == int(index):
                    faults.append("coordinate %r room %s links to itself" % (cid, index))
                elif int(target) not in indices:
                    faults.append("coordinate %r room %s links to missing room %s"
                                  % (cid, index, target))

    print("")
    if faults:
        print("FAILS %d CONDITION(S):" % len(faults))
        shown = {}
        for fault in faults:
            key = fault.split(" room ")[0] if " room " in fault else fault
            shown[key] = shown.get(key, 0) + 1
        for fault in list(dict.fromkeys(faults))[:14]:
            print("  - %s" % fault)
        if len(faults) > 14:
            print("  ... and %d more" % (len(faults) - 14))
        return 1
    print("EVERY RELATIONSHIP CONDITION PASSES on this save's own data.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
