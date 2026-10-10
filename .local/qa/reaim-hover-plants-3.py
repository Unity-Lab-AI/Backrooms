# -*- coding: utf-8 -*-
"""The last five plant anchors the hover passes moved.

Each fault being planted is unchanged -- *"this text stops reaching the player"*.
Only the line that carries the text has moved, from a `listing.Label(...)` call to
a `heading:` or `detail:` argument on the shared primitives in
`UI/OperationsControls.cs`.

Two of these get **stronger** than they were. A `DrawHeading` call names its two
arguments separately, so a plant can now break the short line and leave the hover
intact, or the reverse -- where a single `Label` could only be broken wholesale.
"""
import io
import sys

NL = chr(10)

EDITS = [
    # ---------------------------------------------------- the debrief count
    (".local/register/plant-areas-and-debrief.py",
     '     \'listing.Label("RR_Debrief_Outstanding".Translate(holds.Count));\','
     + NL
     + '     \'string unused = "RR_Debrief_Outstanding".Translate(holds.Count);\'',

     '     # The count draws through `DrawHeading` now: `RR_Debrief_Count` on screen, and the'
     + NL
     + '     # standing rule that none of them go out again until they report on the hover.'
     + NL
     + '     # Emptying the heading is what stops the player seeing the count.' + NL
     + '     \'heading: "RR_Debrief_Count".Translate(holds.Count),\',' + NL
     + '     \'heading: TaggedString.Empty,\''),

    # ------------------------------------------- the gate card's readout array
    (".local/register/plant-gate-subsystems.py",
     '     "footprint, integrityText, operatorText", "footprint, operatorText", P_SUB),',

     '     # The card\'s array gained `NextStepReadout()` at the front on 2026-10-04 and wrapped,'
     + NL
     + '     # so this needle\'s neighbours moved onto the next line. Same fault: a readout that is'
     + NL
     + '     # computed and never joined into the card.' + NL
     + '     "footprint, integrityText,", "footprint,", P_SUB),'),

    # ------------------------------------------------ the integrations heading
    (".local/register/plant-integrations.py",
     '    ("the readout stops drawing the heading", PANE,' + NL
     + '     \'listing.Label("RR_Integration_Heading".Translate(\',' + NL
     + '     \'string unusedHeading = "RR_Integration_Heading".Translate(\', PROOF),',

     '    ("the readout stops drawing the heading", PANE,' + NL
     + '     \'heading: "RR_Integration_Heading".Translate(\',' + NL
     + '     \'unusedHeading: "RR_Integration_Heading".Translate(\', PROOF),'),

    # ----------------------------------------------- odd-origin stock only
    (".local/register/plant-planner-and-missions.py",
     '    ("the pane stops saying ordinary stock will not do", TERMS,' + NL
     + '     \'listing.Label("RR_UI_DemandOddOnly".Translate());\', "// nothing", PROOF),',

     '    ("the pane stops saying ordinary stock will not do", TERMS,' + NL
     + '     \'                detail: "RR_UI_DemandOddOnly".Translate());\',' + NL
     + '     \'                detail: TaggedString.Empty);\', PROOF),'),

    # --------------------------------------------- the objective chain's branch
    # The objective line carries two keys per branch now: a short `brief` that draws and the
    # full `key` on the hover. Removing the branch is still exactly the fault.
    (".local/register/plant-review-exposure.py",
     '     \'            else if (campaign.AwaitsReview(record)) '
     + '{ key = "RR_UI_NextReview"; pane = 6; }\'',

     '     \'            else if (campaign.AwaitsReview(record))\' + NL' + NL
     + '     + \'            { key = "RR_UI_NextReview"; brief = "RR_UI_NextReviewBrief"; '
     + 'pane = 6; }\''),
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("NEEDLE NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old.strip().split(NL)[0][:76]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-36s re-aimed" % path.split("/")[-1])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
