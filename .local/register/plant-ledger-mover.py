# -*- coding: utf-8 -*-
"""Plant the failures proof-ledger-mover.py exists to catch, and require it to catch them.

The first fault below is **the exact wrong fix that shipped on 2026-10-06** and was caught by
reading a diff rather than by any instrument: measuring a heading's body to the next *anchor*, which
counts a `**...:**` lead-in as the end of the section and sweeps four headings away from their own
content. The second removes the residue case the sweep was extended for. The third restores the
original bug, where a heading emptied in an earlier batch could never be cleaned.

`tools/archive-finished-todo.py` is the instrument `.claude/CONSTRAINTS.md §FINALIZED BEFORE
DELETE` names as the proof of verbatim transfer, and until this suite it had **no plant and no proof
of its own** -- which is why a wrong fix to it reached a real ledger.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-ledger-mover.py"]

MOVER = "tools/archive-finished-todo.py"

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


def read_bytes(path):
    return io.open(path, "rb").read()


def write_verified(path, data):
    """Bytes in, bytes out, verified. A byte-order mark is part of a file and must survive."""
    for _ in range(6):
        try:
            io.open(path, "wb").write(data)
            if read_bytes(path) == data:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


PLANTS = [
    # ---- the wrong fix that actually shipped ----------------------------------------------
    # A lead-in is an anchor, so measuring to `end` stops at it and the section reads as empty.
    # This is not a hypothetical: it was applied to docs/TEST.md and removed four headings from
    # above the owner's own verbatim quotes.
    ("A HEADING IS SWEPT AWAY FROM ITS OWN CONTENT, because a lead-in ends the body measurement",
     MOVER,
     "                following = next((h for h in headings if h > anchor), len(lines))",
     "                following = end", 1),

    # **A THIRD PLANT WAS WRITTEN HERE AND DELETED, because it asserted something untrue.** It
    # removed the `if H3.match(lines[anchor])` restriction on the blank test, claiming that letting a
    # `LEAD_IN` anchor be treated as residue is a defect. It is not: the guard above it already
    # returns for any anchor with a kept, non-blank line in its body, and a lead-in standing over
    # genuinely nothing **is** residue -- the sweep's own docstring says it handles "any `###`
    # heading or bold lead-in whose whole body has already gone." The restriction is explicitness,
    # not correctness, so nothing breaks when it goes and the plant reported MISSED, correctly.
    #
    # Recorded rather than quietly dropped. A plant whose claim is false has to be deleted instead
    # of weakened, which is the same answer three loophole plants got in `plant-cue-consumer`.

    # ---- the residue case stops being handled --------------------------------------------
    # Reverting to the original condition. It looks like a simplification and it is the bug that
    # left an empty heading in docs/TEST.md from the day the file was created.
    ("A HEADING EMPTIED IN AN EARLIER BATCH CAN NEVER BE CLEANED AGAIN",
     MOVER,
     "            if not moving and not blank:",
     "            if not moving:", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = read_bytes(path)
    needle = old.encode("utf-8")
    if original.count(needle) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:55], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(needle, new.encode("utf-8"), 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable] + PROOF,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == 1
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted 1)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
