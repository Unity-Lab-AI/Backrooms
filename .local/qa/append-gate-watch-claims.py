# -*- coding: utf-8 -*-
"""Append the operator-safety claims to `proof-gate-circuit.py`.

Written as a file rather than a heredoc, and with every detail string on ONE line, because the
first attempt split string literals across lines and produced a `SyntaxError` -- the same class of
mistake the recorded rule about heredocs exists for.
"""
import io
import sys

NL = chr(10)
P = ".local/register/proof-gate-circuit.py"
ANCHOR = 'print("")' + NL + 'if failures:'

LINES = [
'# ============================================ the operator leaves before their body gives out',
'#',
'# **A colonist starved at the console in the first launch.** Owner, 2026-10-06: *"current a pawn',
'# dies at the comms console... and we cant have them not going to eat or finding saftey"*. It was',
'# fatal by construction and needed three things at once: `suspendable: false`, a',
'# `ToilCompleteMode.Never` station, and a `FailOn` that tested the gate, the calibration, the',
'# operator identity, `Downed` and `InMentalState` and **not one need**.',
'#',
'# So the claims below are about the FLOOR, not the setting. A posture tunes WHEN an operator',
'# leaves; nothing tunes WHETHER.',
'posture = no_comments(read(SRC, "Gate", "GateWatchPosture.cs"))',
'driver = no_comments(read(SRC, "Gate", "JobDriver_RimroomsGate.cs"))',
'jobs = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",',
'                         "JobDefs", "RR_GateJobs.xml"))',
'enum_body = posture.split("public enum GateWatchPosture")[1].split("}")[0]',
'',
'check("THE OPERATOR JOB CHECKS A NEED AT ALL, which it did not when a pawn starved at it",',
'      "GateWatch.MustLeave(pawn)" in driver,',
'      "-- without it the only exits were collapse or the player noticing")',
'',
'check("and it is asked in the FailOn AND every tick, counted rather than assumed",',
'      driver.count("GateWatch.MustLeave(pawn)") == 2,',
'      "-- a FailOn runs on the driver\'s own cadence; crossing into starvation between two of them is the window the defect lived in")',
'',
'check("THE FLOOR IS THE GAME\'S OWN CATEGORIES: starving, exhausted, burning, bleeding out",',
'      "HungerCategory.Starving" in posture and "RestCategory.Exhausted" in posture',
'      and "IsBurning()" in posture and "BleedRateTotal" in posture,',
'      "-- each is a state where standing still is the thing doing the harm, and each is Core\'s threshold rather than a number chosen here")',
'',
'check("THE FLOOR IS ASKED BEFORE THE POSTURE, so no posture can switch it off",',
'      posture.index("MustLeave") < posture.index("Releases"),',
'      "-- the ordering IS the safety argument")',
'',
'check("AND NO POSTURE MEANS NEVER LEAVE, because that value does not exist",',
'      "Mild" in enum_body and "Balanced" in enum_body and "Strict" in enum_body',
'      and "Never" not in enum_body,',
'      "-- a value meaning never leave would be one typo away from the bug this file exists to fix")',
'',
'check("Strict adds no tolerance of its own beyond the floor",',
'      "case GateWatchPosture.Strict:" in posture,',
'      "-- it returns false and lets the floor decide rather than carrying looser numbers of its own")',
'',
'check("the saved default is written out rather than inherited from a zeroed field",',
'      "GateWatchPosture.Balanced" in no_comments(read(SRC, "Gate", "CompRimroomsGate.cs")),',
'      "-- Mild is enum 0, so an absent saved value has to be resolved to Balanced explicitly")',
'',
'check("THE JOB DEF RECORDS WHY IT IS STILL NOT SUSPENDABLE",',
'      "suspendable" in jobs and "MustLeave" in jobs,',
'      "-- suspendable would give exactly the mild posture and could not express the other two, so the mod keeps the decision and carries the duty")',
'',
'for watch_key in ("RR_GateWatch_Label", "RR_GateWatch_Strict", "RR_GateWatch_StrictDesc",',
'                  "RR_GateWatch_Mild", "RR_GateWatch_Balanced"):',
'    check("%s is translated" % watch_key, ("<%s>" % watch_key) in keyed,',
'          "-- a dropdown showing a raw key is a dropdown nobody can use")',
'',
]


def main():
    text = io.open(P, encoding="utf-8-sig").read()
    if "GateWatch.MustLeave" in text:
        print("claims already present")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(P, "w", encoding="utf-8", newline=NL).write(
        text[:at] + NL.join(LINES) + text[at:])
    print("appended %d line(s) of claims" % len(LINES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
