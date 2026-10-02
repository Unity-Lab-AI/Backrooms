# -*- coding: utf-8 -*-
"""Planted faults against corporation contact, the record-book delivery, and the quest line.

**`proof-corporate-contact.py` had no plant suite at all.** It is one of the oldest proofs in the
battery and nothing had ever tested whether its claims could fail -- which is the same shape as
the defect it sits next to: the laboratory start shipped no record book, and no claim, checker or
plant noticed until the owner hit it in a running game.

A proof nobody plants against is a proof nobody has checked.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

DELIVERY = "src/RimroomsAsyncIndustries/Company/RecordBookDelivery.cs"
SERVICES = "src/RimroomsAsyncIndustries/Company/CampaignServices.cs"
LINE = "src/RimroomsAsyncIndustries/Company/RequestLine.cs"
STARTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsStartDefs/RR_Starts.xml"
REQUESTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRequestDefs/RR_Requests.xml"

PROOF = ".local/register/proof-corporate-contact.py"

NL = chr(10)

PLANTS = [
    # ====================================================== the delivery, built and unreachable
    ("THE BOOK DELIVERY IS BUILT AND NOTHING TICKS IT", SERVICES,
     "            if (now % 60 == 45) { TickRecordBookDelivery(); }" + NL, "", PROOF),

    ("the delivery stops waiting for a finished gate", DELIVERY,
     "            if (!HasFinishedGate()) { return; }" + NL, "", PROOF),

    ("a designated but uncalibrated gate counts as finished", DELIVERY,
     "gate.IsDesignated && gate.Calibrated", "gate.IsDesignated", PROOF),

    ("THE DELIVERY BECOMES A TAP, SENDING BOOKS TO A BRANCH THAT HAS THEM", DELIVERY,
     "            if (AnyRecordBookHeld(book)) { return; }" + NL, "", PROOF),

    ("a book in somebody's pack stops counting", DELIVERY,
     "                    if (pawn.inventory.innerContainer.Contains(book)) { return true; }" + NL,
     "", PROOF),

    ("a book on a floor or a shelf stops counting", DELIVERY,
     "                if (map.listerThings != null" + NL
     + "                    && map.listerThings.ThingsOfDef(book).Count > 0)" + NL
     + "                { return true; }" + NL, "", PROOF),

    ("the delivery resolves the book by name instead of asking the dispatch", DELIVERY,
     "ThingDef book = Expedition.ExpeditionCargo.RecordBookDef;",
     'ThingDef book = DefDatabase<ThingDef>.GetNamedSilentFail("TextBook");', PROOF),

    ("the spare goes, so losing one book blocks the branch again", DELIVERY,
     "private const int RecordBookDeliveryCount = 2;",
     "private const int RecordBookDeliveryCount = 1;", PROOF),

    ("an empty crate is announced anyway", DELIVERY,
     "            if (payload.Count == 0) { return; }" + NL, "", PROOF),

    # ====================================================== the quest line
    ("A SCENARIO GATE APPEARS IN THE QUEST LINE", LINE,
     "            if (!corporationContact) { return; }",
     '            if (!corporationContact) { return; }' + NL
     + '            if (scenarioId != "async_industries") { return; }', PROOF),

    ("the first tutorial request stops being power-the-gate", REQUESTS,
     "<tutorialOrder>0</tutorialOrder>", "<tutorialOrder>9</tutorialOrder>", PROOF),

    # ====================================================== the owner's contact rule
    ("a start that should begin outside contact begins inside it", STARTS,
     "<beginsInCorporationContact>false</beginsInCorporationContact>",
     "<beginsInCorporationContact>true</beginsInCorporationContact>", PROOF),
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
