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
    write_verified(path, original.replace(old, new, 1), "plant into")
    code = subprocess.call([sys.executable, ".local/register/proof-areas-and-debrief.py"],
                           stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    write_verified(path, original, "restore")
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
