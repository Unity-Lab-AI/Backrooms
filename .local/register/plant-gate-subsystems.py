# -*- coding: utf-8 -*-
"""Plant a fault, run the proof, require exit 1, restore. Verified writes.

Includes the two plants that check the **widened scope** of the older proof: it read one file of
a partial class and kept passing when a seventh failure reason was added to another file of the
same class. A plant that adds an eighth reason must now fail both proofs.
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
INTEG = SRC + "/Gate/GateIntegrity.cs"
GATE = SRC + "/Gate/CompRimroomsGate.cs"
HIST = SRC + "/Gate/GateConnectionHistory.cs"
P_SUB = ".local/register/proof-gate-subsystems.py"
P_AREA = ".local/register/proof-areas-and-debrief.py"

# (label, path, old, new, which proof must fail)

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
    ("the integrity threshold becomes an absolute hit-point count", INTEG,
     "                return (float)parent.HitPoints / maximum;",
     "                return parent.HitPoints;", P_SUB),

    ("a damaged gate stops losing calibration", INTEG,
     "            calibrated = false;\n            stablePowerTicks = 0;\n", "", P_SUB),

    ("a live opening is dropped instead of going through the emergency path", INTEG,
     '            if (IsOpening && !IsEmergency)\n'
     '            { EnterEmergency("RR_Gate_IntegrityLost"); }\n', "", P_SUB),

    ("the player is never told", INTEG,
     "            Find.LetterStack.ReceiveLetter(", "            Noop(", P_SUB),

    ("the integrity tick is never called", GATE, "            TickIntegrity();\n", "", P_SUB),

    ("opening stops refusing on a broken machine", GATE,
     "            if (IntegrityFailureKey != null)\n"
     "            { return CompanyActionResult.Refused(IntegrityFailureKey); }\n", "", P_SUB),

    ("the readout is computed but never drawn", GATE,
     # The card's array gained `NextStepReadout()` at the front on 2026-10-04 and wrapped,
     # so this needle's neighbours moved onto the next line. Same fault: a readout that is
     # computed and never joined into the card.
     "footprint, integrityText,", "footprint,", P_SUB),

    ("the readout starts shouting on a perfectly sound gate", GATE,
     "            string integrityText = IntegritySound ? null",
     "            string integrityText = false ? null", P_SUB),

    ("AN EIGHTH FAILURE REASON ARRIVES UNANNOUNCED", INTEG,
     '            { EnterEmergency("RR_Gate_IntegrityLost"); }',
     '            { EnterEmergency("RR_Gate_IntegrityLost"); EnterEmergency("RR_Gate_Sneaky"); }',
     P_SUB),

    ("AN EIGHTH REASON, checked by the OTHER proof's widened scope", INTEG,
     '            if (!calibrated) { return; }',
     '            if (!calibrated) { EnterEmergency("RR_Gate_Sneaky2"); return; }', P_AREA),

    ("no-data reliability starts reading as a real rate", HIST,
     "                return recorded <= 0 ? -1f : (float)completed / recorded;",
     "                return recorded <= 0 ? 1f : (float)completed / recorded;", P_SUB),

    ("a second writer of the outcome counts appears", HIST,
     "            if (emergency) { emergencies++; }",
     "            if (emergency) { emergencies++; emergencies++; }", P_SUB),

    ("the outcome is filed against the wrong address", HIST,
     "                if (entry != null && string.Equals(entry.coordinateId, historyCoordinateId,\n"
     "                    StringComparison.Ordinal))\n"
     "                { entry.NoteOutcome(emergency); break; }",
     "                if (entry != null)\n"
     "                { entry.NoteOutcome(emergency); break; }", P_SUB),

    # Anchored INSIDE the method rather than across the next declaration. The old anchor reached
    # forward to `public int ClearConnectionHistory()` to disambiguate the two
    # `historyCoordinateId = null;` sites, and that made it break the moment a doc comment was
    # moved onto that member. The preceding two lines disambiguate it just as well and are local
    # to the method the claim is about.
    ("the remembered coordinate is left stale", HIST,
     "                { entry.NoteOutcome(emergency); break; }\n            }\n"
     "            historyCoordinateId = null;\n        }",
     "                { entry.NoteOutcome(emergency); break; }\n            }\n        }", P_SUB),

    ("the outcome is filed AFTER failureKey is cleared, so every trip reads as a success", GATE,
     "            NoteOpeningOutcome(IsEmergency);\n"
     "            if (!string.IsNullOrEmpty(portalOpeningId))",
     "            if (!string.IsNullOrEmpty(portalOpeningId))", P_SUB),

    ("the counts stop being saved", HIST,
     '            Scribe_Values.Look(ref completed, "rr_completed", 0);\n', "", P_SUB),

    ("the player can no longer read the reliability row", HIST,
     "                new FloatMenuOption(ReliabilityRow(entry), null),\n", "", P_SUB),

    ("randomness creeps into the subsystem", INTEG,
     "        internal void TickIntegrity()\n        {",
     "        internal void TickIntegrity()\n        {\n            if (Rand.Bool) { }", P_SUB),
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


caught = 0
for label, path, old, new, proof in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) != 1:
        print("PLANT SETUP BROKEN (%d matches): %s" % (original.count(old), label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, proof],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
