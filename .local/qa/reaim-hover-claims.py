# -*- coding: utf-8 -*-
"""Two proof claims asserted the Label call the hover pass replaced.

Both are re-aimed at how the text reaches the player now, and **both get
stronger**: each one additionally asserts that the text is on the HOVER rather
than merely present in the file. That distinction did not exist before -- a
single `Label` could only be drawn or absent -- and it is exactly the distinction
the owner's direction turns on: *"things can be shortend and more concise and
dirrect  with tools tips would less cluter it making them all concise and
accurate"*. Present-but-nowhere-visible is the failure neither claim could see.
"""
import io
import sys

NL = chr(10)

EDITS = [
    # ------------------------------------- the survey contract keeps its terms
    (".local/register/proof-planner-and-missions.py",
     'check("the survey terms are still shown on a survey contract",' + NL
     + "      'if (!contract.IsOddSupply)' in terms" + NL
     + '      and \'listing.Label("RR_UI_ContractTerms".Translate());\' in terms,' + NL
     + '      "-- the old text was right for the contract it was written for")',

     'check("the survey terms are still shown on a survey contract",' + NL
     + "      'if (!contract.IsOddSupply)' in terms" + NL
     + '      # **ON THE HOVER OF THE PANE\'S OWN HEADING, which is a stronger assertion than the'
     + NL
     + '      # one it replaces.** This used to check that the string was passed to `Label`; it now'
     + NL
     + '      # checks that it is the `detail:` of a `DrawHeading` whose `heading:` is the short'
     + NL
     + '      # line, so a pass that dropped the hover and left the heading -- forty-one words of'
     + NL
     + '      # survey method silently gone -- fails here instead of reading as a tidy-up.' + NL
     + '      and \'heading: "RR_UI_ContractTermsBrief".Translate(),\' in terms' + NL
     + '      and \'detail: "RR_UI_ContractTerms".Translate());\' in terms,' + NL
     + '      "-- the old text was right for the contract it was written for, and every word of it '
     + 'is "' + NL
     + '      "still reachable -- it moved to the heading\'s tooltip rather than being cut")'),

    # ------------------------------------------ the objective names the review
    (".local/register/proof-review-exposure.py",
     'check("and the objective hint names review as the next step",' + NL
     + '      \'else if (campaign.AwaitsReview(record)) { key = "RR_UI_NextReview"; pane = 6; }\''
     + NL
     + '      in expeditions_ui' + NL
     + '      and "public bool AwaitsReview(EvidenceRecord record)" in review' + NL
     + '      and "<RR_UI_NextReview>" in investigation_keyed,' + NL
     + '      "-- a workflow the player is never told about is one nobody runs")',

     'check("and the objective hint names review as the next step",' + NL
     + '      # **TWO KEYS PER BRANCH NOW, and the claim asserts both.** The objective line draws'
     + NL
     + '      # a three-word `brief` and carries the full instruction on its hover, so this checks'
     + NL
     + '      # the branch sets BOTH -- a branch that set only the long key would show a blank'
     + NL
     + '      # objective, and one that set only the brief would lose the instruction entirely.'
     + NL
     + '      \'else if (campaign.AwaitsReview(record))\' in expeditions_ui' + NL
     + '      and \'{ key = "RR_UI_NextReview"; brief = "RR_UI_NextReviewBrief"; pane = 6; }\''
     + NL
     + '      in expeditions_ui' + NL
     + '      and "public bool AwaitsReview(EvidenceRecord record)" in review' + NL
     + '      and "<RR_UI_NextReview>" in investigation_keyed' + NL
     + '      and "<RR_UI_NextReviewBrief>" in expeditions_keyed,' + NL
     + '      "-- a workflow the player is never told about is one nobody runs")'),
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
    print("%-38s re-aimed and strengthened" % path.split("/")[-1])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
