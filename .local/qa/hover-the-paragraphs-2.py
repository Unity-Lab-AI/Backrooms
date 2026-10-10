# -*- coding: utf-8 -*-
"""Second pass: the panes whose words-per-action was worst because nothing clicks.

Owner direction, 2026-10-04, verbatim: *"all things should be done to make it
more of a utility, not  a text wall"*.

**The tool's headline metric found these, not a reading of the source.** Four of
them draw between 100 and 190 words and offer **nothing to click at all**:
`OperationsCrewPlanner` 174 words and zero controls, `OperationsContractTerms`
101 and zero, `OperationsHeldPlaces` 187 words behind one button. A pane like
that is a page of prose by definition, whatever its individual strings say.

Same rule throughout: the long text keeps every word and becomes the hover of the
short line already above it, or of the control it is the small print for.
"""
import io
import sys

NL = chr(10)
UI = "src/RimroomsAsyncIndustries/UI/"

REPLACEMENTS = [
    # ---------------------------------------------------------------- held places
    # 63 words on what releasing a place means, 26 on the budget, under a two-word
    # heading. The explanation is the definition of the heading; the budget line is
    # the number the explanation is about.
    (UI + "OperationsHeldPlaces.cs",
     '            listing.Label("RR_Release_Heading".Translate());\n'
     '            listing.Gap(6f);\n'
     '            listing.Label("RR_Release_Budget".Translate(OpenMapBudget.Held, OpenMapBudget.Budget));\n'
     '            listing.Label("RR_Release_Explanation".Translate());',
     '            DrawHeading(listing, heading: "RR_Release_Heading".Translate(),\n'
     '                detail: "RR_Release_Explanation".Translate());\n'
     '            listing.Gap(6f);\n'
     '            // **THE BUDGET LINE IS THE ONE NUMBER THIS PANE EXISTS FOR**, so it stays on\n'
     '            // screen; the twenty-six words explaining why a Backrooms level costs a map slot\n'
     '            // exactly as a colony does are the reasoning behind it, and reasoning does not\n'
     '            // change between visits.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_Release_Held".Translate(OpenMapBudget.Held, OpenMapBudget.Budget),\n'
     '                detail: "RR_Release_Budget".Translate(OpenMapBudget.Held, OpenMapBudget.Budget));'),

    (UI + "OperationsHeldPlaces.cs",
     '                listing.Label("RR_Release_ShelvedHeading".Translate());',
     '                // How to get back to a shelved place, on the heading for the list of them.\n'
     '                DrawHeading(listing, heading: "RR_Release_ShelvedHeading".Translate(),\n'
     '                    detail: "RR_Release_ShelvedHint".Translate());'),

    (UI + "OperationsHeldPlaces.cs",
     '                listing.Label("RR_Release_ShelvedHint".Translate());\n'
     '            }',
     '            }'),

    # ------------------------------------------------------------------- requests
    # The two silences are the pane's whole content when there is no request, and
    # both are 33 words of fiction explaining an empty panel. They stay readable
    # without hovering -- but each gets a short line in front of it so the pane
    # says what state it is in at a glance.
    (UI + "OperationsRequests.cs",
     '                listing.Label("RR_Requests_NoContact".Translate());',
     '                DrawHeading(listing, heading: "RR_Requests_NoContactBrief".Translate(),\n'
     '                    detail: "RR_Requests_NoContact".Translate());'),

    (UI + "OperationsRequests.cs",
     '                listing.Label(campaign.PastTheHinge\n'
     '                    ? "RR_Requests_PastTheHinge".Translate()\n'
     '                    : "RR_Requests_NoneOpen".Translate());',
     '                if (campaign.PastTheHinge)\n'
     '                {\n'
     '                    DrawHeading(listing, heading: "RR_Requests_PastTheHingeBrief".Translate(),\n'
     '                        detail: "RR_Requests_PastTheHinge".Translate());\n'
     '                }\n'
     '                else { listing.Label("RR_Requests_NoneOpen".Translate()); }'),

    # ------------------------------------------------------- laboratory binding
    (UI + "OperationsLaboratoryBinding.cs",
     '            listing.Label("RR_Lab_Heading".Translate());\n'
     '            listing.Label("RR_Lab_Explanation".Translate());',
     '            DrawHeading(listing, heading: "RR_Lab_Heading".Translate(),\n'
     '                detail: "RR_Lab_Explanation".Translate());'),

    (UI + "OperationsLaboratoryBinding.cs",
     '            listing.Label((readiness.Success ? "RR_Lab_Ready" : readiness.MessageKey).Translate());\n'
     '            listing.Label("RR_Lab_NativeResearch".Translate());',
     '            // **THE READINESS LINE STAYS; THE REASSURANCE MOVES.** Thirty-nine words saying\n'
     '            // ordinary research still works through native controls is a standing fact about\n'
     '            // the game, not a fact about this bench, and it was drawn under a readiness\n'
     '            // verdict as though it qualified it.\n'
     '            DrawHeading(listing,\n'
     '                heading: (readiness.Success ? "RR_Lab_Ready" : readiness.MessageKey).Translate(),\n'
     '                detail: "RR_Lab_NativeResearch".Translate());'),

    (UI + "OperationsLaboratoryBinding.cs",
     '            listing.Label("RR_Lab_Candidates".Translate(candidates.Count, laboratoryBenchPage + 1, pages));',
     '            // The count and the page are the readout; that an unpowered bench may be\n'
     '            // designated and simply will not work is the caveat on it.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_Lab_CandidateCount".Translate(candidates.Count,\n'
     '                    laboratoryBenchPage + 1, pages),\n'
     '                detail: "RR_Lab_Candidates".Translate(candidates.Count,\n'
     '                    laboratoryBenchPage + 1, pages));'),

    # --------------------------------------------------------- contract terms
    # 41 words of survey method where the pane has no control of its own at all.
    # The contract row above it is drawn by the caller, so this pane gets the one
    # short line it was missing and puts the method on it.
    (UI + "OperationsContractTerms.cs",
     '                listing.Label("RR_UI_ContractTerms".Translate());\n'
     '                return;',
     '                DrawHeading(listing, heading: "RR_UI_ContractTermsBrief".Translate(),\n'
     '                    detail: "RR_UI_ContractTerms".Translate());\n'
     '                return;'),

    (UI + "OperationsContractTerms.cs",
     '            listing.Label("RR_UI_DemandDelivered".Translate(\n'
     '                contract.DeliveredCount.ToString("N0"), contract.RequiredCount.ToString("N0")));\n'
     '            listing.Label("RR_UI_DemandOddOnly".Translate());',
     '            // What counts toward the delivery, on the delivery count.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_UI_DemandDelivered".Translate(\n'
     '                    contract.DeliveredCount.ToString("N0"),\n'
     '                    contract.RequiredCount.ToString("N0")),\n'
     '                detail: "RR_UI_DemandOddOnly".Translate());'),
]

USING = "using static RimroomsAsyncIndustries.UI.OperationsControls;" + NL

problems = 0
touched = {}

for path, old, new in REPLACEMENTS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old.strip()[:84]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-32s rewired %s" % (path.split("/")[-1], old.strip().split(NL)[0][:58]))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    text = touched[path]
    if USING not in text:
        at = text.index(NL + "namespace ")
        text = text[:at] + NL + USING + text[at:]
        print("added the static import to %s" % path.split("/")[-1])
    io.open(path, "w", encoding="utf-8", newline=NL).write(text)
    print("wrote %s" % path.split("/")[-1])
