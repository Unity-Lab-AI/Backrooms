# -*- coding: utf-8 -*-
"""Re-aim the gate-step claims at the extracted checklist, and add the new one.

The eleven checks moved from `UI/OperationsGateSteps.cs` (a private method on the
Operations window) to `Gate/GateStartupChecklist.cs`, so the door can answer
*"what do I do next"* without the window. Owner, 2026-10-04: *"and when u set a
door to be a gatew  that gate should tell you next step in the game world not
just in the operations tab and machine tab"*.

**Three claims are re-aimed and every one of them gets stronger, not weaker.**

  * The eleven-steps claim now also asserts the window holds **no second copy**.
    That is the single-authority property the move exists to create, and it is
    the thing that would silently rot if the list were ever pasted back.
  * The next-up claim asserts the window **asks** the checklist rather than
    searching the list itself, which is what lets the door give the same answer.
  * A fourth claim is added for the behaviour that was actually built: the gate's
    own inspect card names the step, from the same list, **after** the
    not-designated guard -- because this component sits on every Core door in the
    game and a line computed before that guard would print start-up advice on
    every bedroom door on the map.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-starts.py"

REPLACEMENTS = [
    # ------------------------------------------------- read the new file as well
    ('_steps = _file("UI", "OperationsGateSteps.cs")',
     '_steps = _file("UI", "OperationsGateSteps.cs")\n'
     '# **THE ELEVEN CHECKS ARE NO LONGER IN THE WINDOW.** Owner, 2026-10-04: *"and when u set a\n'
     '# door to be a gatew  that gate should tell you next step in the game world not just in the\n'
     '# operations tab and machine tab"*. The list is read by the door now as well, so it lives in\n'
     '# the gate\'s own namespace and the window draws it.\n'
     '_checklist = _file("Gate", "GateStartupChecklist.cs")'),

    # ------------------------------------------------- eleven steps, one copy only
    ('check("and there are ELEVEN of them, each with a done flag and a how",\n'
     '      all(("Number = %d," % n) in _steps for n in range(1, 12))\n'
     '      and all((\'"RR_Steps_%dLabel"\' % n) in _steps for n in range(1, 12))\n'
     '      and all((\'"RR_Steps_%dHow"\' % n) in _steps for n in range(1, 12))\n'
     '      and "public string How;" in _steps\n'
     '      and "public bool Done;" in _steps,\n'
     '      "-- a step with a label and no instruction is the panel the owner was already looking at")',

     'check("and there are ELEVEN of them, each with a done flag and a how",\n'
     '      all(("Number = %d," % n) in _checklist for n in range(1, 12))\n'
     '      and all((\'"RR_Steps_%dLabel"\' % n) in _checklist for n in range(1, 12))\n'
     '      and all((\'"RR_Steps_%dHow"\' % n) in _checklist for n in range(1, 12))\n'
     '      and "public string How;" in _checklist\n'
     '      and "public bool Done;" in _checklist,\n'
     '      "-- a step with a label and no instruction is the panel the owner was already looking at")\n'
     '\n'
     '# **AND THERE IS EXACTLY ONE LIST OF THEM.** This is the property the extraction exists to\n'
     '# create and the one that would rot silently: pasting the eleven conditions back into the\n'
     '# window would compile, pass every other claim here, and then drift from the door. Two\n'
     '# derivations of one rule is the defect this project keeps meeting -- it is what made\n'
     '# `RR_Gate_CalibrationUnavailable` read *"the gate is not ready for calibration"* for eight\n'
     '# conditions including *already calibrated*.\n'
     'check("AND THE WINDOW HOLDS NO SECOND COPY OF THEM",\n'
     '      "Number = 1," not in _steps\n'
     '      and "struct GateStep" not in _steps\n'
     '      and "GateStartupChecklist.Steps(gate)" in _steps,\n'
     '      "-- the window draws the list and does not own it, so the status board and the door\'s "\n'
     '      "own inspect card cannot disagree about whether something is done")'),

    # ---------------------------------------------- the window asks for the next
    ('check("AND THE FIRST UNFINISHED ONE IS NAMED ON ITS OWN LINE",\n'
     '      "GateStep next = steps.FirstOrDefault(step => !step.Done);" in _steps\n'
     '      and \'"RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)\' in _steps\n'
     '      and \'"RR_Steps_Progress".Translate(\' in _steps,',

     'check("AND THE FIRST UNFINISHED ONE IS NAMED ON ITS OWN LINE",\n'
     '      "GateStartupChecklist.NextIncomplete(steps)" in _steps\n'
     '      and "internal static GateStep NextIncomplete(" in _checklist\n'
     '      and "steps.FirstOrDefault(step => !step.Done)" in _checklist\n'
     '      and \'"RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)\' in _steps\n'
     '      and \'"RR_Steps_Progress".Translate(\' in _steps,'),

    # ------------------------------------------------------------- the order claim
    ('check("THE ORDER MATCHES WHAT THE CODE ACTUALLY ENFORCES",\n'
     '      _steps.index("Number = 4,") < _steps.index("Number = 5,")\n'
     '      and _steps.index("Number = 8,") < _steps.index("Number = 10,")\n'
     '      and "workshop != null && workshop.IsGateControl" in _steps\n'
     '      and "station != null && station.IsGateControl" in _steps,',

     'check("THE ORDER MATCHES WHAT THE CODE ACTUALLY ENFORCES",\n'
     '      _checklist.index("Number = 4,") < _checklist.index("Number = 5,")\n'
     '      and _checklist.index("Number = 8,") < _checklist.index("Number = 10,")\n'
     '      and "workshop != null && workshop.IsGateControl" in _checklist\n'
     '      and "station != null && station.IsGateControl" in _checklist,'),
]

# The new claim goes immediately before the refusals block, so it sits with the rest
# of the start-up reading rather than at the end of the file.
ANCHOR = "# ---------------------------------------------- the refusals name their cause"

NEW_CLAIM = '''# ------------------------------------------- the DOOR says what to do next, in the world
# Owner, 2026-10-04, verbatim: *"and when u set a door to be a gatew  that gate should tell you
# next step in the game world not just in the operations tab and machine tab"*.
#
# **The card carried ten readouts and not one answer.** Condition, operator, kill switch,
# servicing, power reserve and its breakdown, the ramp, the equipment links, the live window --
# every one of them answering *what is the state* and none of them *what do I do*. The owner's
# report about the panel was *"ive done like 50 things in a row and its still not opening"*; this
# is the same gap on the object itself.
check("THE GATE'S OWN INSPECT CARD NAMES THE NEXT STEP",
      "private string NextStepReadout()" in _gate
      and "GateStartupChecklist.Steps(this)" in _gate
      and "GateStartupChecklist.NextIncomplete(steps)" in _gate
      and '"RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)' in _gate,
      "-- and it asks the SAME list the status board draws, so the door and the window cannot "
      "tell a player two different next steps")

check("and it is FIRST on the card",
      _gate.index("NextStepReadout()") < _gate.index('string ramp = SpinUpReadout();')
      and _gate.index("{ NextStepReadout(), status,") > 0,
      "-- it is the only line on that card a stuck player needs, and it was being added under ten "
      "lines of state")

# **THE GUARD IS THE LOAD-BEARING PART AND IT IS EASY TO LOSE.** `CompProperties_RimroomsGate` is
# attached to EVERY Core door by the native binding patch, so a next-step line computed before the
# `!IsDesignated` return would print gate start-up advice on every bedroom door on the map.
check("AND EVERY OTHER DOOR IN THE GAME STAYS SILENT",
      _gate.index('if (!IsDesignated) { return null; }')
      < _gate.index("{ NextStepReadout(), status,"),
      "-- the not-designated return comes FIRST, so a door nobody made a gate says nothing at all")

'''

text = io.open(PROOF, encoding="utf-8").read()
problems = 0

for old, new in REPLACEMENTS:
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d): %r" % (text.count(old), old.split(NL)[0][:84]))
        problems += 1
        continue
    text = text.replace(old, new)
    print("re-aimed: %s" % old.split(NL)[0][:72])

if NEW_CLAIM.split(NL)[0] in text:
    print("new claim already present")
elif text.count(ANCHOR) != 1:
    print("ANCHOR NOT UNIQUE (%d) for the new claim" % text.count(ANCHOR))
    problems += 1
else:
    text = text.replace(ANCHOR, NEW_CLAIM + ANCHOR)
    print("added 3 new claims for the door's own next-step line")

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(PROOF, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % PROOF)
