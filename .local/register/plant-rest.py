# -*- coding: utf-8 -*-
"""The five plants that did not complete, with a retried write.

Two things went wrong on the first run and both are worth recording:

1. **One plant was mine, not a proof gap.** The *"grows a Backrooms exception"* plant hid its
   evidence inside a `/* */` comment, and the proof strips comments before searching -- correctly,
   because a claim about behaviour must not be satisfiable by a comment. The plant now writes real
   code.

2. **A restore write failed with `OSError 22` and left a planted fault on disk.** `io.open(w)`
   truncates before writing, so a failed write is not a no-op: it can leave a file empty or half
   written. Every write here is retried, and the file is read back and compared before the next
   plant is attempted, so a silent half-restore cannot happen again.
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
ROOF = SRC + "/ConnectedWork/Providers/RoofWorkProvider.cs"
PANE = SRC + "/UI/OperationsFacilities.cs"
PAPER = SRC + "/Economy/BondPaper.cs"
BONDCOMP = SRC + "/Economy/CompRimroomsBond.cs"
BONDSVC = SRC + "/Economy/BondService.cs"
HANDLING = SRC + "/Economy/BondHandling.cs"
TREASURY = SRC + "/Company/BondTreasury.cs"
BONDTEXT = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Bonds.xml")
BONDS_PROOF = ".local/register/proof-bonds.py"
AREAS_PROOF = ".local/register/proof-areas-and-debrief.py"


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
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


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    # ------------------------------------------------------------------ the bonds
    # Nothing in this battery had ever claimed anything about bonds, which is why five defects
    # shipped in one feature. Four of the five were the same shape: built, correct, unreachable.
    ("THE CARRIER'S CLASS IS NEVER SWAPPED, SO THE LABEL GOES BACK TO A NOVEL TITLE", BONDSVC,
     "                { bond.thingClass = typeof(Book_RimroomsBond); }",
     "                { }", BONDS_PROOF),

    ("the label override stops reading the face value", PAPER,
     '                return "RR_Bond_Label".Translate(CreditDenominations.ShortName(bond.FaceValue));',
     "                return base.LabelNoCount;", BONDS_PROOF),

    ("an ordinary novel loses its own name too", PAPER,
     "                if (bond == null) { return base.LabelNoCount; }",
     "                if (bond == null) { return null; }", BONDS_PROOF),

    ("THE DEAD COMP HOOK COMES BACK, READING LIKE A FIX", BONDCOMP,
     "        public override string CompInspectStringExtra()",
     "        public override string TransformLabel(string label)" + chr(10)
     + "        {" + chr(10)
     + '            return "RR_Bond_Label".Translate(faceValue);' + chr(10)
     + "        }" + chr(10) + chr(10)
     + "        public override string CompInspectStringExtra()", BONDS_PROOF),

    ("the label stops being the value and goes back to a bare word", BONDTEXT,
     "  <RR_Bond_Label>{0} credit bearer bond</RR_Bond_Label>",
     "  <RR_Bond_Label>company bond</RR_Bond_Label>", BONDS_PROOF),

    ("A BOND GOES BACK TO BEING WORTH A NOVEL", PAPER,
     "            if (face > 0L) { value = face; }", "            return;", BONDS_PROOF),

    ("the stat part is written and never added to the stat", BONDSVC,
     "                        market.parts.Add(valuePart);", "                        _ = valuePart;",
     BONDS_PROOF),

    ("the value part stops asking for a thing, so it answers for defs too", PAPER,
     "            if (!request.HasThing) { return 0L; }", "            if (false) { return 0L; }",
     BONDS_PROOF),

    ("DEPOSIT IS DEFINED AND NEVER OFFERED", BONDCOMP,
     "                action = delegate { Show(BondHandling.Deposit(parent)); }",
     "                action = delegate { }", BONDS_PROOF),

    ("combine is defined and never offered", BONDCOMP,
     "                action = delegate { Show(BondHandling.Combine(parent)); }",
     "                action = delegate { }", BONDS_PROOF),

    ("the treasury loses the deposit it is asked for", TREASURY,
     "        internal CompanyActionResult DepositBondPaper(",
     "        internal CompanyActionResult DepositBondPaperUnused(", BONDS_PROOF),

    ("COMBINING STOPS BALANCING THE LEDGER", TREASURY,
     '            CompanyActionResult paid = PostTransaction(operationId + ".out", -payable,',
     '            CompanyActionResult paid = PostTransaction(operationId + ".out", 0L,',
     BONDS_PROOF),

    ("combining shreds a pile it cannot improve", HANDLING,
     "            if (wanted >= paper.Count && remainder <= 0L)",
     "            if (false)", BONDS_PROOF),

    ("a refusal goes silent", BONDCOMP,
     '            Messages.Message((result.MessageKey ?? "RR_Bond_NoneInRange").Translate(),',
     "            if (false) Messages.Message((result.MessageKey ?? \"RR_Bond_NoneInRange\").Translate(),",
     BONDS_PROOF),

    ("the description stops describing the instrument", BONDTEXT,
     "COMPANY BEARER BOND", "A company bearer bond", BONDS_PROOF),

    ("the roof provider grows a Backrooms exception of its own", ROOF,
     "            Area area = map.areaManager == null ? null : map.areaManager.NoRoof;",
     "            if (map.ParentHolder != null) { int Coordinate = 0; Coordinate++; }\n"
     "            Area area = map.areaManager == null ? null : map.areaManager.NoRoof;", AREAS_PROOF),

    ("the pane goes silent when nobody is waiting", PANE,
     '            { listing.Label("RR_Debrief_NoneOutstanding".Translate()); return; }',
     '            { return; }', AREAS_PROOF),

    ("the interviewer choice stops being deterministic", PANE,
     "                .ThenBy(candidate => candidate.ThingID, StringComparer.Ordinal)\n", "", AREAS_PROOF),

    ("the pane offers the crew member as their own interviewer", PANE,
     "candidate != null && candidate != crewMember &&", "candidate != null &&", AREAS_PROOF),

    ("the debrief pane is never reached", PANE,
     "            DrawDebriefs(listing, campaign);\n", "", AREAS_PROOF),
]


def write_verified(path, text, what):
    """Write, then read back and compare. A truncating write that fails is not a no-op."""
    for attempt in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not %s %s -- CHECK THIS FILE BY HAND\n" % (what, path))
    sys.exit(3)


caught = 0
# **THE PROOF COMES FROM THE ROW.** This suite ran one fixed proof for every plant, which is
# fine while every plant belongs to one subsystem and wrong the moment one does not: a bond plant
# run against the areas proof would pass and prove nothing. Same shape
# `plant-startplacement.py` already uses.
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) != 1:
        print("PLANT SETUP BROKEN (%d matches): %s" % (original.count(old), label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1), "plant into")
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what makes a destructive
        # instrument safe, and it was the one line not protected: a leaked devnull handle raised
        # OSError mid-run twice and left planted source on disk both times.
        write_verified(path, original, "restore")
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
