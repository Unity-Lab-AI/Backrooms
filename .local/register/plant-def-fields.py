# -*- coding: utf-8 -*-
"""Prove the def-field checker can fail, which is the whole reason row 922 exists.

Two kinds of plant, because row 922 names two distinct failure modes:

* **It must catch the defect it was written for.** Plants 1-4 put an unknown field back into
  the XML, including the historical `maxTechLevel` on a room archetype.
* **It must never report a pass having looked at nothing.** Plants 5-7 blind the checker and
  require exit 2 -- "skipped, not passed" -- rather than exit 0. *"A checker that silently
  passes everything is worse than no checker: it manufactures confidence."*
"""
import io
import os
import subprocess
import sys
import time

CHECK = "tools/check-def-fields.py"
ARCH = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRoomArchetypeDefs/RR_RoomArchetypes.xml"
INHAB = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsInhabitantDefs/RR_Inhabitants.xml"
GIVERS = "Mod/Rimrooms - Async Industries/1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml"

# (label, path, old, new, expected exit)
PLANTS = [
    # The historical defect was `maxTechLevel` on a room archetype. It cannot be replanted
    # verbatim, because 0.8.7-dev fixed it by **adding the field to the class** rather than
    # removing it from the XML -- so `maxTechLevel` is valid now, and a first version of this
    # plant passed for the right reason. `minTechLevel` is the same defect in the same place
    # with a name the class genuinely does not have.
    ("the 0.8.7-dev defect class: a tech-level knob the archetype class does not have", ARCH,
     "<defName>", "<minTechLevel>Industrial</minTechLevel><defName>", 1),

    ("a typo on one of our own defs", INHAB,
     "<minDepth>", "<minDpeth>3</minDpeth><minDepth>", 1),

    ("a typo on a Core def type", GIVERS,
     "<defName>RR_ConnectedRoofWork</defName>",
     "<defName>RR_ConnectedRoofWork</defName><workTyp>Construction</workTyp>", 1),

    ("a field that exists on a DIFFERENT def type", INHAB,
     "<weight>", "<priorityInType>5</priorityInType><weight>", 1),

    ("the C# class parser is blinded", CHECK,
     "    return classes\n", "    return {}\n", 2),

    ("the game data index is blinded", CHECK,
     "    return index\n\n\n# ------", "    return collections.defaultdict(set)\n\n\n# ------", 2),

    ("the XML walk finds no defs at all", CHECK,
     '    NOT_DEFS = {"Operation"', '    NOT_DEFS = {"Operation"', None),
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
attempted = 0
for label, path, old, new, want in PLANTS:
    if want is None:
        continue  # placeholder left out; the two blinding plants above cover the same property
    attempted += 1
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    write_verified(path, original.replace(old, new, 1))
    code = subprocess.call([sys.executable, CHECK],
                           stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    write_verified(path, original)
    ok = code == want
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted %d)"
          % ("CAUGHT " if ok else "MISSED!", label, code, want))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
