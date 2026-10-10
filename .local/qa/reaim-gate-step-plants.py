# -*- coding: utf-8 -*-
"""Re-aim the gate-step plants at the extracted checklist -- and fix two that could never run.

## THE SUITE WAS CRASHING, NOT PASSING

`plant-startplacement.py` builds its baseline with `plant[4] for plant in PLANTS`.
**Two entries carried only four elements**, so the generator raised
`IndexError: tuple index out of range` before a single plant was set -- and it did
that on the line that prints `baseline`, which looks like the start of a run. The
suite has therefore proved nothing since those two were added, and the previous
publication's battery did not catch it because the record counted checkers and
proofs. Both are given the proof command they were missing.

## Three anchors moved with the checklist

The eleven checks are now in `Gate/GateStartupChecklist.cs`, so three plants were
searching the window for text that is no longer in it. A plant whose needle is
absent is the worst kind of green: it reports nothing wrong because it changed
nothing.

## And the ramp-progress plant was aimed at text that exists NOWHERE

Its needle expects `How = ramping` indented by sixteen spaces. The method moved
and its body sits at a different indent, so the needle matched neither file. Both
indent-sensitive needles are rewritten to the indentation the code actually has,
and the audit that found this -- comparing every needle against both files -- is
the only reason it was visible.
"""
import io
import sys

NL = chr(10)
PLANTS = ".local/register/plant-startplacement.py"

CHECKLIST_CONST = (
    '# **THE ELEVEN CHECKS LEFT THE WINDOW.** Owner, 2026-10-04: *"and when u set a door to be a\n'
    '# gatew  that gate should tell you next step in the game world not just in the operations tab\n'
    '# and machine tab"*. `Gate/GateStartupChecklist.cs` is the one list; the window draws it and\n'
    "# the door's inspect card names the first unfinished one. Plants against the steps belong here\n"
    '# now -- aimed at the window they matched nothing, which registers as "nothing broke".\n'
    'CHECKLIST = "src/RimroomsAsyncIndustries/Gate/GateStartupChecklist.cs"\n'
)

REPLACEMENTS = [
    # ------------------------------------------- the constant the re-aimed plants need
    ('STEPS = "src/RimroomsAsyncIndustries/UI/OperationsGateSteps.cs"',
     'STEPS = "src/RimroomsAsyncIndustries/UI/OperationsGateSteps.cs"\n' + CHECKLIST_CONST),

    # ------------------------------------------------------- ramp is not an open connection
    ('    ("A RAMPING CONNECTION COUNTS AS OPEN AGAIN", STEPS,\n'
     '     "                Done = haveGate && gate.IsOpening,",\n'
     '     "                Done = haveGate && (gate.IsOpening || gate.IsSpinningUp),", STARTS_PROOF),',

     '    ("A RAMPING CONNECTION COUNTS AS OPEN AGAIN", CHECKLIST,\n'
     '     "                Done = haveGate && gate.IsOpening,",\n'
     '     "                Done = haveGate && (gate.IsOpening || gate.IsSpinningUp),", STARTS_PROOF),'),

    # ----------------------------------------------------- the ramp's live percentage
    # The needle was indented for the window's nesting and matches neither file now.
    ('    ("the ramp stops reporting its progress", STEPS,\n'
     '     "                How = ramping" + CHR_NL\n'
     '     + \'                    ? "RR_Steps_11HowRamping".Translate(\',\n'
     '     "                How = false" + CHR_NL\n'
     '     + \'                    ? "RR_Steps_11HowRamping".Translate(\', STARTS_PROOF),',

     '    ("the ramp stops reporting its progress", CHECKLIST,\n'
     '     "                How = ramping" + CHR_NL\n'
     '     + \'                    ? "RR_Steps_11HowRamping".Translate(\',\n'
     '     "                How = false" + CHR_NL\n'
     '     + \'                    ? "RR_Steps_11HowRamping".Translate(\', STARTS_PROOF),'),

    # ------------------------------------------------------------ a step loses its how
    ('    ("A STEP LOSES ITS INSTRUCTION", STEPS,\n'
     '     \'                How = "RR_Steps_9How".Translate(),\', "                How = null,", STARTS_PROOF),',

     '    ("A STEP LOSES ITS INSTRUCTION", CHECKLIST,\n'
     '     \'                How = "RR_Steps_9How".Translate(),\', "                How = null,", STARTS_PROOF),'),

    # -------------------------------------------------- the gate-control reads
    ('    ("the gate-control steps stop reading the components", STEPS,\n'
     '     "                Done = workshop != null && workshop.IsGateControl,",\n'
     '     "                Done = true,", STARTS_PROOF),',

     '    ("the gate-control steps stop reading the components", CHECKLIST,\n'
     '     "                Done = workshop != null && workshop.IsGateControl,",\n'
     '     "                Done = true,", STARTS_PROOF),\n'
     '\n'
     '    # **THE SINGLE AUTHORITY ITSELF, PLANTED.** The whole point of the move is that there is\n'
     '    # one list; a second copy pasted back into the window would compile and drift. The claim\n'
     '    # that forbids it has to be shown to fail, or it is a comment.\n'
     '    ("THE WINDOW GROWS ITS OWN SECOND COPY OF THE STEPS AGAIN", STEPS,\n'
     '     "            CompRimroomsGate gate = CurrentGate(campaign);",\n'
     '     "            CompRimroomsGate gate = CurrentGate(campaign);" + CHR_NL\n'
     '     + "            int unused = 0; if (unused == 1) { } // Number = 1,", STARTS_PROOF),\n'
     '\n'
     "    # ------------------- the door says what to do next, in the world\n"
     '    ("THE DOOR STOPS NAMING THE NEXT STEP", GATECOMP,\n'
     '     "{ NextStepReadout(), status,", "{ status,", STARTS_PROOF),\n'
     '\n'
     '    ("the next step stops being FIRST on the card", GATECOMP,\n'
     '     "new[] { NextStepReadout(), status,", "new[] { status, NextStepReadout(),", STARTS_PROOF),\n'
     '\n'
     '    # **THE GUARD EVERY DOOR IN THE GAME DEPENDS ON.** This component is attached to every\n'
     '    # Core door by the native binding patch. Move the next-step line above the\n'
     '    # not-designated return and every bedroom door on the map starts giving gate advice.\n'
     '    ("THE NOT-DESIGNATED GUARD STOPS COMING FIRST", GATECOMP,\n'
     '     "            if (!IsDesignated) { return null; }" + CHR_NL,\n'
     '     "", STARTS_PROOF),'),

    # ------------------------------------- the two entries that could never be run
    ('    ("THE ROWS GO BACK TO CARRYING THEIR OWN INSTRUCTIONS", STEPS,\n'
     "     '            TooltipHandler.TipRegion(row, step.Done',\n"
     "     '            TooltipHandler.TipRegion(row, false'),",

     '    # **FOUR ELEMENTS, SO THE WHOLE SUITE CRASHED.** `plant[4]` on this tuple raised\n'
     '    # `IndexError` while printing the baseline, which reads like the start of a run. Neither\n'
     '    # this plant nor the ninety-five after it had been set since the day it was added.\n'
     '    ("THE ROWS GO BACK TO CARRYING THEIR OWN INSTRUCTIONS", STEPS,\n'
     "     '            TooltipHandler.TipRegion(row, step.Done',\n"
     "     '            TooltipHandler.TipRegion(row, false', STARTS_PROOF),"),

    ('    ("THE STATUS LIGHT LOSES ITS GLYPH, so the state is carried by hue alone", STEPS,\n'
     '     "            Widgets.CheckboxDraw(light.xMax + 4f, row.y, step.Done, true, StatusRowHeight);"\n'
     '     + CHR_NL, ""),',

     '    ("THE STATUS LIGHT LOSES ITS GLYPH, so the state is carried by hue alone", STEPS,\n'
     '     "            Widgets.CheckboxDraw(light.xMax + 4f, row.y, step.Done, true, StatusRowHeight);"\n'
     '     + CHR_NL, "", HELP_PROOF),'),
]

text = io.open(PLANTS, encoding="utf-8").read()
problems = 0

for old, new in REPLACEMENTS:
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d): %r" % (text.count(old), old.strip().split(NL)[0][:80]))
        problems += 1
        continue
    text = text.replace(old, new)
    print("patched: %s" % old.strip().split(NL)[0][:72])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(PLANTS, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % PLANTS)
