# -*- coding: utf-8 -*-
"""Third pass: the last five panes, so *"all the tabs"* is true rather than most.

Owner direction, 2026-10-04, verbatim: *"and all the tabs of operations are well
designed for a tripple A Mod currently it looks like its all just text wall and
shit"*.

**The evidence pane is the interesting one and it needed a different answer.**
Its five long strings are not instructions at all -- each one is a *refusal with
its criteria*: nobody can take a statement because an interviewer needs Social
{0}, nobody can review because a reviewer needs Intellectual {0} and cannot be
the analyst. Those are the house `DrawAction` case: the control the player is
looking for, disabled, with the criteria on it. Printing the criteria instead of
the control is what made the pane read as prose.

`OperationsConnectedWork` is left alone deliberately: 48 words in ten keys, none
over eleven words, and it is drawn inside the portal pane. There is nothing in it
to move, and moving something to prove the pass touched every file would make it
worse.
"""
import io
import sys

NL = chr(10)
UI = "src/RimroomsAsyncIndustries/UI/"

REPLACEMENTS = [
    # ------------------------------------------------------------------- evidence
    # The sign-off control, disabled, carrying whichever criterion is unmet. Three
    # separate early returns each printed a paragraph and then drew nothing.
    (UI + "OperationsEvidence.cs",
     '            listing.Label("RR_UI_ReviewAwaiting".Translate());',
     '            DrawHeading(listing, heading: "RR_UI_ReviewAwaitingBrief".Translate(),\n'
     '                detail: "RR_UI_ReviewAwaiting".Translate());'),

    (UI + "OperationsEvidence.cs",
     '                listing.Label("RR_Review_DisputesOutstanding".Translate(disputes));\n'
     '                return;',
     '                // **THE SIGN-OFF BUTTON APPEARS, DISABLED, SAYING WHY.** It used to be a\n'
     '                // paragraph and then nothing, so the player could not tell whether sign-off\n'
     '                // was blocked or simply unimplemented.\n'
     '                DrawAction(listing, label: "RR_UI_SignOffReport".Translate(),\n'
     '                    refusal: "RR_Review_DisputesOutstanding".Translate(disputes));\n'
     '                return;'),

    (UI + "OperationsEvidence.cs",
     '                listing.Label("RR_Review_NoReviewer".Translate(\n'
     '                    RimroomsCampaignComponent.MinimumReviewerIntellectual));\n'
     '                return;',
     '                DrawAction(listing, label: "RR_UI_SignOffReport".Translate(),\n'
     '                    refusal: "RR_Review_NoReviewer".Translate(\n'
     '                        RimroomsCampaignComponent.MinimumReviewerIntellectual));\n'
     '                return;'),

    (UI + "OperationsEvidence.cs",
     '                listing.Label("RR_Interview_NoInterviewer".Translate(campaign.InterviewerSocialFloor));\n'
     '                return;',
     '                // Same shape: the thing a player wants is "take the statements", so that is\n'
     '                // what they see, off, with the Social floor on it.\n'
     '                DrawAction(listing, label: "RR_UI_TakeStatements".Translate(),\n'
     '                    refusal: "RR_Interview_NoInterviewer".Translate(\n'
     '                        campaign.InterviewerSocialFloor));\n'
     '                return;'),

    (UI + "OperationsEvidence.cs",
     '            listing.Label("RR_UI_InterviewPrompt".Translate(interviewer.LabelShortCap));',
     '            // Who can take the statements is the line; what filing one of them means to the\n'
     '            // company record is the consequence, and it only matters as you reach for it.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_UI_InterviewBrief".Translate(interviewer.LabelShortCap),\n'
     '                detail: "RR_UI_InterviewPrompt".Translate(interviewer.LabelShortCap));'),

    # ---------------------------------------------------------- evidence recovery
    (UI + "OperationsEvidenceRecovery.cs",
     '            listing.Label("RR_EvidenceRecovery_Title".Translate());\n'
     '            listing.Label("RR_EvidenceRecovery_Explanation".Translate());',
     '            DrawHeading(listing, heading: "RR_EvidenceRecovery_Title".Translate(),\n'
     '                detail: "RR_EvidenceRecovery_Explanation".Translate());'),

    # ------------------------------------------------------------- remote sites
    (UI + "OperationsRemoteSites.cs",
     '            listing.Label("RR_Sites_Heading".Translate());\n'
     '            listing.Gap(6f);',
     '            DrawHeading(listing, heading: "RR_Sites_Heading".Translate(),\n'
     '                detail: "RR_Sites_None".Translate());\n'
     '            listing.Gap(6f);'),

    # --------------------------------------------------------------- crew planner
    # The planner is already a dense readout -- twenty-two keys, the longest
    # seventeen words. Its one genuine paragraph is the operator bonus, which is a
    # rule rather than a reading of this candidate.
    (UI + "OperationsCrewPlanner.cs",
     '                    listing.Label("RR_Plan_ExposureKnowsRoute".Translate(\n'
     '                        trips.ToString(CultureInfo.CurrentCulture)));',
     '                    DrawHeading(listing,\n'
     '                        heading: "RR_Plan_ExposureKnowsRouteBrief".Translate(\n'
     '                            trips.ToString(CultureInfo.CurrentCulture)),\n'
     '                        detail: "RR_Plan_ExposureKnowsRoute".Translate(\n'
     '                            trips.ToString(CultureInfo.CurrentCulture)));'),
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
    print("%-32s rewired %s" % (path.split("/")[-1], old.strip().split(NL)[0][:56]))

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
