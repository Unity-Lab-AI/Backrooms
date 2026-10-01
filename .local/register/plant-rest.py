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
    ("the roof provider grows a Backrooms exception of its own", ROOF,
     "            Area area = map.areaManager == null ? null : map.areaManager.NoRoof;",
     "            if (map.ParentHolder != null) { int Coordinate = 0; Coordinate++; }\n"
     "            Area area = map.areaManager == null ? null : map.areaManager.NoRoof;"),

    ("the pane goes silent when nobody is waiting", PANE,
     '            { listing.Label("RR_Debrief_NoneOutstanding".Translate()); return; }',
     '            { return; }'),

    ("the interviewer choice stops being deterministic", PANE,
     "                .ThenBy(candidate => candidate.ThingID, StringComparer.Ordinal)\n", ""),

    ("the pane offers the crew member as their own interviewer", PANE,
     "candidate != null && candidate != crewMember &&", "candidate != null &&"),

    ("the debrief pane is never reached", PANE,
     "            DrawDebriefs(listing, campaign);\n", ""),
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
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) != 1:
        print("PLANT SETUP BROKEN (%d matches): %s" % (original.count(old), label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1), "plant into")
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, ".local/register/proof-areas-and-debrief.py"],
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
