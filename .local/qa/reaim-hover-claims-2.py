# -*- coding: utf-8 -*-
"""Three more claims that asserted the Label call the hover pass replaced.

All three carry the same rationale in their own message -- *"a key present in the
file is not a claim that anything is drawn"* -- and that rationale is **exactly
right and is why they failed**. The text is still drawn; it is drawn through
`DrawHeading` now, and a claim written against `listing.Label(` could not tell
the difference between *moved to a hover* and *deleted*.

Each is re-aimed at the argument that carries it, and each **keeps that
rationale** by asserting the specific argument rather than the key's presence
anywhere in the file:

  * the debrief count asserts `heading:`, because the count is the thing a player
    must see without hovering;
  * the integration heading asserts `heading:` and the caveat asserts `detail:`,
    which is a finer distinction than the single `Label` claim could make;
  * the gate card's integrity readout asserts the array element rather than three
    adjacent tokens, because the array gained `NextStepReadout()` at the front
    and wrapped.
"""
import io
import sys

NL = chr(10)

EDITS = [
    # --------------------------------------------------- the debrief count
    (".local/register/proof-areas-and-debrief.py",
     'check("the pane lists who is waiting",' + NL
     + '      \'"RR_Debrief_Outstanding".Translate(holds.Count)\' in debrief_pane and' + NL
     + '      \'listing.Label("RR_Debrief_Outstanding"\' in debrief_pane,' + NL
     + '      "-- a key present in the file is not a claim that anything is drawn")',

     'check("the pane lists who is waiting",' + NL
     + '      # **THE COUNT IS ON SCREEN; THE RULE BEHIND IT IS ON THE HOVER.** Owner,' + NL
     + '      # 2026-10-04: *"with tools tips would less cluter it"*. So the assertion is finer' + NL
     + '      # than it was: `heading:` must carry the count, because a player has to see it' + NL
     + '      # without hovering, and `detail:` must carry the standing rule that none of them go' + NL
     + '      # out again until they report. A key present in the file is still not a claim that' + NL
     + '      # anything is drawn -- and now neither is a key present in a tooltip.' + NL
     + '      \'heading: "RR_Debrief_Count".Translate(holds.Count)\' in debrief_pane and' + NL
     + '      \'detail: "RR_Debrief_Outstanding".Translate(holds.Count)\' in debrief_pane,' + NL
     + '      "-- a key present in the file is not a claim that anything is drawn, and a count a '
     + 'player "' + NL
     + '      "has to hover to find is a count they will not find")'),

    # ------------------------------------------- the gate card's integrity readout
    (".local/register/proof-gate-subsystems.py",
     'check("and the readout is actually joined into the inspect string",' + NL
     + '      "footprint, integrityText, operatorText" in gate,' + NL
     + '      "-- a key present in the file is not a claim that anything is drawn")',

     'check("and the readout is actually joined into the inspect string",' + NL
     + '      # **THE ARRAY GAINED `NextStepReadout()` AT THE FRONT AND WRAPPED**, so these three' + NL
     + '      # tokens are no longer adjacent -- owner, 2026-10-04: *"that gate should tell you' + NL
     + '      # next step in the game world"*. The claim is the same: this readout is an element of' + NL
     + '      # the array that gets joined, not merely a local that was computed.' + NL
     + '      "footprint, integrityText," in gate and' + NL
     + '      "new[] { NextStepReadout(), status," in gate,' + NL
     + '      "-- a key present in the file is not a claim that anything is drawn, and a local '
     + 'that is "' + NL
     + '      "computed and never joined is the defect this claim exists for")'),

    # ------------------------------------------------- the integrations readout
    (".local/register/proof-integrations.py",
     'check("the pane draws the heading with the live count",' + NL
     + '      \'listing.Label("RR_Integration_Heading".Translate(\' in pane and' + NL
     + '      "Core.InstalledIntegrations.ActiveCount()" in pane,' + NL
     + '      "-- a key present in the file is not a claim that anything is drawn")' + NL
     + 'check("the caveat is drawn every time, not only when something is loaded",' + NL
     + '      \'listing.Label("RR_Integration_Caveat".Translate());\' in pane,' + NL
     + '      "-- loaded means present, not proven, and that has to be said unconditionally")',

     'check("the pane draws the heading with the live count",' + NL
     + '      \'heading: "RR_Integration_Heading".Translate(\' in pane and' + NL
     + '      "Core.InstalledIntegrations.ActiveCount()" in pane,' + NL
     + '      "-- a key present in the file is not a claim that anything is drawn")' + NL
     + '# **STILL UNCONDITIONAL, AND NOW A FINER ASSERTION THAN IT WAS.** The caveat moved to the' + NL
     + '# count\'s hover -- owner, 2026-10-04: *"with tools tips would less cluter it"* -- and' + NL
     + '# *"loaded means present, not proven"* is the definition of that count rather than a' + NL
     + '# separate announcement. It is still said on every draw: it is the `detail:` of the' + NL
     + '# heading itself, so there is no state in which the heading appears without it.' + NL
     + 'check("the caveat is drawn every time, not only when something is loaded",' + NL
     + '      \'detail: "RR_Integration_Caveat".Translate());\' in pane and' + NL
     + '      # On the heading, which is drawn unconditionally -- not on a row inside the loop,' + NL
     + '      # where it would appear once per tracked mod or not at all.' + NL
     + '      pane.index(\'detail: "RR_Integration_Caveat"\')' + NL
     + '      < pane.index("for (int index = 0; index < tracked.Count; index++)"),' + NL
     + '      "-- loaded means present, not proven, and that has to be said unconditionally")'),
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("CLAIM NOT UNIQUE (%d) in %s" % (text.count(old), path.split("/")[-1]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-40s re-aimed" % path.split("/")[-1])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
