# -*- coding: utf-8 -*-
"""Plant the starvation defect back into the operator job and require the proof to refuse it.

Each plant below is a way the fix could be undone, and the first one is **the exact defect that
killed a colonist**: the need check removed from the job driver.
"""
import io
import sys

NL = chr(10)
P = ".local/register/plant-gate-circuit.py"
ANCHOR = "PLANTS = [" + NL

LINES = [
'PLANTS = [',
'    # ============================================ the defect that killed a colonist, replanted',
'    # Owner, 2026-10-06: *"current a pawn dies at the comms console"*. The station toil is',
'    # ToilCompleteMode.Never and the job is not suspendable, so removing the need check restores',
'    # a pawn who stands there until they starve. Nothing else in the battery can see it.',
'    ("THE OPERATOR\'S NEED CHECK IS REMOVED FROM THE FailOn, which is how a pawn starved", DRIVER,',
'     "            this.FailOn(() => GateWatch.MustLeave(pawn)" + NL',
'     + "                || GateWatch.Releases(pawn, Gate == null ? GateWatchPosture.Balanced : Gate.WatchPosture));",',
'     "", PROOF),',
'',
'    ("and removed from the per-tick check, leaving only the slower FailOn", DRIVER,',
'     "                else if (GateWatch.MustLeave(pawn)" + NL',
'     + "                    || GateWatch.Releases(pawn, gate.WatchPosture))" + NL',
'     + "                { EndJobWith(JobCondition.InterruptForced); }",',
'     "", PROOF),',
'',
'    # ============================================ the floor is weakened rather than removed',
'    ("THE FLOOR STOPS KNOWING ABOUT STARVATION", WATCH,',
'     "if (food != null && food.CurCategory >= HungerCategory.Starving) { return true; }",',
'     "if (false) { return true; }", PROOF),',
'',
'    ("the floor stops knowing about exhaustion", WATCH,',
'     "if (rest != null && rest.CurCategory >= RestCategory.Exhausted) { return true; }",',
'     "if (false) { return true; }", PROOF),',
'',
'    ("the floor stops noticing a burning pawn", WATCH,',
'     "if (pawn.IsBurning()) { return true; }", "", PROOF),',
'',
'    ("the floor stops noticing a pawn bleeding out", WATCH,',
'     "&& pawn.health.hediffSet.BleedRateTotal > 0.1f;", "&& false;", PROOF),',
'',
'    # ============================================ a posture gains the power to override the floor',
'    # The ordering IS the safety argument, so this plants its reversal.',
'    ("A NEVER-LEAVE POSTURE IS ADDED TO THE ENUM", WATCH,',
'     "        Strict = 2,", "        Strict = 2," + NL + NL + "        Never = 3,", PROOF),',
'',
'    ("Strict grows tolerance of its own past the floor", WATCH,',
'     "                case GateWatchPosture.Strict:", "                case GateWatchPosture.Mild:",',
'     PROOF),',
'',
'    # ============================================ the saved default falls back to enum zero',
'    ("THE SAVED DEFAULT BECOMES Mild BY OMISSION, which enum 0 would do silently", GATE,',
'     "private GateWatchPosture watchPosture = GateWatchPosture.Balanced;",',
'     "private GateWatchPosture watchPosture;", PROOF),',
'',
'    # ============================================ the player cannot read the dropdown',
'    ("a watch posture loses its player-facing string", GATEKEYED,',
'     "<RR_GateWatch_StrictDesc>", "<RR_GateWatch_StrictDescription>", PROOF),',
'',
]


def main():
    text = io.open(P, encoding="utf-8-sig").read()
    if "GateWatch.MustLeave" in text:
        print("plants already present")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    # Paths the new plants need, declared beside the ones already there.
    marker = 'PROOF = ".local/register/proof-gate-circuit.py"'
    if text.count(marker) != 1:
        print("path marker not unique; refusing")
        return 1
    text = text.replace(
        marker,
        marker + NL
        + 'DRIVER = "src/RimroomsAsyncIndustries/Gate/JobDriver_RimroomsGate.cs"' + NL
        + 'WATCH = "src/RimroomsAsyncIndustries/Gate/GateWatchPosture.cs"', 1)
    text = text.replace(ANCHOR, NL.join(LINES), 1)
    io.open(P, "w", encoding="utf-8", newline=NL).write(text)
    print("appended the starvation plants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
