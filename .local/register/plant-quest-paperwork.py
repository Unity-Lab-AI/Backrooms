# -*- coding: utf-8 -*-
"""Planted faults against `tools/check-quest-paperwork.py`.

**It passed on its second run and caught three real faults on its first**, which is the only kind of
first run worth trusting -- it found three declared write-up kinds no request asked for. That proves
one rule. The other nine get a fault aimed at each, including the two the whole design rests on: a
second caller of `FileWriteUp`, and a stamp that happens before the record is written.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

PAPERWORK = "src/RimroomsAsyncIndustries/Company/QuestPaperwork.cs"
DRIVER = "src/RimroomsAsyncIndustries/Company/JobDriver_WriteUp.cs"
GIVER = "src/RimroomsAsyncIndustries/Company/WorkGiver_WriteUp.cs"
SETTLEMENT = "src/RimroomsAsyncIndustries/Company/EvidenceSettlement.cs"
DEFS = "src/RimroomsAsyncIndustries/Company/WriteUpDefs.cs"
KINDS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsWriteUpDefs/RR_WriteUps.xml"
REQUESTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRequestDefs/RR_Requests.xml"
DESK = "Mod/Rimrooms - Async Industries/1.6/Defs/ThingDefs_Buildings/RR_RecordsDesk.xml"

CHECK = "tools/check-quest-paperwork.py"

NL = chr(10)

PLANTS = [
    # ======================================================= rules 1 and 2, one writer each
    ("A SECOND CALLER FILES A WRITE-UP, which is the whole design undone", DRIVER,
     "                target.Campaign.FileWriteUpAndStamp(target.Request, target.Kind);",
     "                target.Request.FileWriteUp(target.Kind.defName);", CHECK),

    ("A SECOND CALLER STAMPS A BOOK, so the record and the receipt can drift apart", GIVER,
     "            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(\"RR_WriteUp\");",
     "            request.FileWriteUp(kind.defName);" + NL
     + "            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(\"RR_WriteUp\");",
     CHECK),

    # ======================================================= rule 3, the record goes first
    ("THE BOOK IS STAMPED BEFORE THE RECORD IS WRITTEN, so a book can claim unrecorded work",
     PAPERWORK,
     "            if (!request.FileWriteUp(kind.defName)) { return false; }" + NL
     + "            Thing book = BookFor(request);" + NL
     + "            CompRouteEvidence stamp = book == null ? null : book.TryGetComp<CompRouteEvidence>();" + NL
     + "            if (stamp != null) { stamp.StampForQuest(request.Id, request.WriteUpsFiled.Count); }",
     "            Thing book = BookFor(request);" + NL
     + "            CompRouteEvidence stamp = book == null ? null : book.TryGetComp<CompRouteEvidence>();" + NL
     + "            if (stamp != null) { stamp.StampForQuest(request.Id, request.WriteUpsFiled.Count); }" + NL
     + "            if (!request.FileWriteUp(kind.defName)) { return false; }",
     CHECK),

    # ======================================================= rule 4, nothing dead
    ("a declared write-up kind stops being asked for by any request", REQUESTS,
     "      <li>RR_WriteUp_LabNotes</li>", "      <li></li>", CHECK),

    # ======================================================= rule 5, nothing unresolved
    ("A REQUEST ASKS FOR A KIND THAT DOES NOT EXIST, which is a light that never comes on",
     REQUESTS,
     "      <li>RR_WriteUp_Analysis</li>", "      <li>RR_WriteUp_Typo</li>", CHECK),

    # ======================================================= rule 6, every precondition handled
    ("a precondition stops being handled, so that paperwork can never be written", PAPERWORK,
     "                case WriteUpPrecondition.EvidenceAnalysed:", "                case (WriteUpPrecondition)99:",
     CHECK),

    ("THE DEFAULT CASE WAVES AN UNKNOWN PRECONDITION THROUGH, handing out free paperwork",
     PAPERWORK,
     "                default:", "                default: return true;" + NL + "                case (WriteUpPrecondition)98:",
     CHECK),

    # ======================================================= rules 7 and 8, the need floor
    ("THE JOB'S PER-TICK NEED FLOOR GOES, so a pawn starves at a desk between job checks", DRIVER,
     "                if (GateWatch.MustLeave(pawn))" + NL
     + "                { EndJobWith(JobCondition.InterruptForced); return; }",
     "                if (false)" + NL
     + "                { EndJobWith(JobCondition.InterruptForced); return; }", CHECK),

    ("the work giver stops asking the floor, so a starving pawn is offered the job on a loop", GIVER,
     "            if (GateWatch.MustLeave(pawn)) { return null; }", "", CHECK),

    # ======================================================= rule 9, the desk and its art
    ("THE DESK GETS ITS OWN TEXTURE, which is the art rule the retired items were retired for",
     DESK, "      <texPath>Things/Building/Furniture/Table1x2</texPath>",
     "      <texPath>RR_RecordsDesk/Desk</texPath>", CHECK),

    ("the work giver stops naming the desk, so it is built and nothing looks at it", GIVER,
     'thing.def.defName != "RR_RecordsDesk"', 'thing.def.defName != "SomethingElse"', CHECK),

    # ======================================================= rule 10, one custody derivation
    ("A SECOND CUSTODY DERIVATION APPEARS, so the book and the record disagree about an archive",
     SETTLEMENT, "        internal bool HasArchivedCustody(Thing item)",
     "        internal bool HasArchivedCustody(Thing other) { return true; }" + NL
     + "        internal bool HasArchivedCustody(Thing item)", CHECK),
]

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


print("baseline -- the verifier must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = dict((path, io.open(path, encoding="utf-8").read())
               for path in set(plant[1] for plant in PLANTS))

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in opening.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every touched file verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
