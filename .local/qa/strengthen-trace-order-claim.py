# -*- coding: utf-8 -*-
"""The trace-order claim was weaker than its own intent, and the plant proved it.

## What happened

The claim asserted `index(RecordTrace) < index(ReceiveLetter)`. The plant moved
`RecordTrace` to sit **after** the `letterLabelKey` early return but still before
`ReceiveLetter` -- so the claim held and the suite reported MISSED.

**The claim was not wrong about ordering; it was asking the wrong question.** The
property that matters is not *which call comes first in the file*, it is **that a
missing letter key cannot lose the record.** `Announce` opens with

    if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }

and anything below that line is conditional on an event having a letter at all.
An event with no letter is legal -- `letterLabelKey` is optional on the def --
and before this change such an event would have left no trace and sent no notice,
which is the complete silence the whole register exists to end.

So the claim now asserts `RecordTrace` comes before **the early return**, which is
the real guarantee, and the plant moves it after that return, which is the real
regression.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-unnerving-register.py"
PLANTS = ".local/register/plant-unnerving-register.py"

OLD_CLAIM = (
    'check("THE TRACE IS RECORDED BEFORE THE LETTER IS SENT",' + NL
    + '      "RecordTrace(map, coordinate, definition, focus);" in event_service' + NL
    + '      and event_service.index("RecordTrace(map, coordinate, definition, focus);")' + NL
    + '      < event_service.index("Find.LetterStack.ReceiveLetter("),' + NL
    + '      "-- the letter is the half that can fail, on a missing key or a suppressed notification. "'
    + NL
    + '      "Ordering it first would make the durable record the optional one")'
)

NEW_CLAIM = (
    "# **THE CLAIM A PLANT CORRECTED.** The first version compared this call's position against"
    + NL
    + "# `ReceiveLetter` and a plant slipped between the two: moved below the early return but"
    + NL
    + "# above the send, it still satisfied the ordering and the suite reported MISSED. The"
    + NL
    + "# property that matters is not which call is first in the file -- it is that **a missing"
    + NL
    + "# letter key cannot lose the record.** `letterLabelKey` is optional on the def, and"
    + NL
    + "# `Announce` returns on it, so anything below that line is conditional on the event having"
    + NL
    + "# a letter at all. Such an event used to leave no trace AND send no notice: complete"
    + NL
    + "# silence, which is what this whole register exists to end." + NL
    + 'check("THE TRACE IS RECORDED BEFORE THE LETTER CAN BE SKIPPED",' + NL
    + '      "RecordTrace(map, coordinate, definition, focus);" in event_service' + NL
    + '      and event_service.index("RecordTrace(map, coordinate, definition, focus);")' + NL
    + '      < event_service.index("if (string.IsNullOrEmpty(definition.letterLabelKey)) '
    + '{ return; }")' + NL
    + '      and event_service.index("RecordTrace(map, coordinate, definition, focus);")' + NL
    + '      < event_service.index("Find.LetterStack.ReceiveLetter("),' + NL
    + '      "-- a letterless event is legal, and before this it left no trace and sent no notice. "'
    + NL
    + '      "Recording below that early return makes the durable half the optional one")'
)

OLD_PLANT = (
    '    ("THE TRACE IS WRITTEN AFTER THE LETTER, making the durable record the optional half",'
    + NL
    + "     EVENT_SERVICE," + NL
    + '     "            RecordTrace(map, coordinate, definition, focus);" + CHR_NL + CHR_NL' + NL
    + '     + "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + CHR_NL'
    + NL
    + '     + "            Find.LetterStack.ReceiveLetter(",' + NL
    + '     "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + CHR_NL'
    + NL
    + '     + "            RecordTrace(map, coordinate, definition, focus);" + CHR_NL' + NL
    + '     + "            Find.LetterStack.ReceiveLetter(", PROOF),'
)

NEW_PLANT = (
    "    # **THIS PLANT CORRECTED ITS OWN CLAIM.** The first version moved the record below the"
    + NL
    + "    # early return but kept it above the send, which satisfied an ordering claim that was"
    + NL
    + "    # asking the wrong question. It now moves the record past the return entirely, which is"
    + NL
    + "    # the real regression: a letterless event leaves nothing at all." + NL
    + '    ("THE TRACE IS WRITTEN BELOW THE LETTER EARLY RETURN, so a letterless event records '
    + 'nothing",' + NL
    + "     EVENT_SERVICE," + NL
    + '     "            RecordTrace(map, coordinate, definition, focus);" + CHR_NL + CHR_NL' + NL
    + '     + "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }",' + NL
    + '     "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + CHR_NL'
    + NL
    + '     + "            RecordTrace(map, coordinate, definition, focus);", PROOF),'
)

EDITS = [(PROOF, OLD_CLAIM, NEW_CLAIM), (PLANTS, OLD_PLANT, NEW_PLANT)]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s" % (text.count(old), path.split("/")[-1]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-36s strengthened" % path.split("/")[-1])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
