# -*- coding: utf-8 -*-
"""Refuse to proceed while a planted fault is still in the source tree.

Why this exists
---------------
**A plant suite has left a deliberate fault in the working tree three times**, twice deleting
`Campaign.NoteReturnedFromField(...)` out of `RimroomsExpeditionComponent.cs` and once deleting
`!anchor.Destroyed` out of `RimroomsPortalNetwork.cs`. Each one would have shipped silently if a
build had gone out before the next `git status`.

The suites plant a fault, run a proof, and restore. Two defects made that unsafe and both are
fixed: a leaked `devnull` handle raised `OSError` mid-run, and fifteen of the sixteen suites had
no `finally`, so the restore -- the one line that makes a destructive instrument safe -- was the
one line unprotected.

**But `finally` does not survive the process being killed.** An interrupted sweep -- a cancelled
command, a closed terminal, a reboot -- stops python between the plant and the restore, and no
amount of exception handling helps. That is exactly how the third one happened.

So the suites write a **sentinel** naming the file they are about to mutate, and delete it after
restoring. If the sentinel exists, a plant is either running right now or was killed with a fault
on disk, and **either way nothing should be built or staged.** The sentinel names the file, so
recovery is one `git checkout` of the path it prints.

A false alarm costs one command. A missed one ships a deliberate fault.
"""
import glob
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# **GLOBBED, because there is one sentinel per suite now.** They shared a single path until
# 0.12.72-dev, so a later suite's success deleted an earlier suite's unresolved failure and this
# checker reported a clean tree with `campaign.ClearBreachResponded();` missing from the source.
SENTINELS = os.path.join(REPO, ".local", "register", ".plant-in-progress*")


def main():
    stale = sorted(glob.glob(SENTINELS))
    if not stale:
        print("OK: no planted fault is in the source tree.")
        return 0

    try:
        detail = "; ".join(io.open(path, encoding="utf-8").read().strip()
                            for path in stale)
    except Exception as problem:
        detail = "(the sentinel could not be read: %s)" % problem

    print("FAILED: a planted fault may still be in the source tree.")
    print("")
    print("  %s" % detail)
    print("")
    print("A plant suite is either running right now, or was killed between planting a fault and")
    print("restoring the file. Nothing should be built or staged until that file is back.")
    print("")
    print("  git status --porcelain       # see what is modified")
    print("  git checkout -- <the file>   # restore it")
    for path in stale:
        print("  rm %s" % path)
    print("")
    print("If a suite is running, wait for it to finish and run this again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
