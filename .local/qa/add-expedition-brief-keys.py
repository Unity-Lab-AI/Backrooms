# -*- coding: utf-8 -*-
"""The short lines that replace the expedition pane's paragraphs on screen.

Owner direction, 2026-10-04, verbatim: *"things can be shortend and more concise
and dirrect  with tools tips would less cluter it making them all concise and
accurate"*.

**Nothing below shortens an existing string.** Every paragraph keeps every word
and moves to the hover; these are the new short lines that draw in its place. The
owner's own *"accurate"* is the reason it works that way round -- a label that
fits because it dropped the condition it was describing is worse than the
paragraph it replaced.

`RR_UI_CurrentObjective` is the one existing string that changes, from a bare
heading to a heading with the objective's own short name in it, because the
objective line is the single most important line in the pane and *"Current
company objective"* alone says nothing a player can act on.

**Written with the Write tool rather than a heredoc**, per the standing note in
`docs/NOW.md`: a heredoc has mangled escapes thirteen times in this repository,
once putting real newlines inside a keyed string.
"""
import io
import sys

NL = chr(10)
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/"
EXPEDITIONS = KEYED + "RR_OperationsExpeditions.xml"
FIELD = KEYED + "RR_FieldAndThreats.xml"

# (file, anchor line to insert AFTER, lines to add)
# Each new key sits beside the long string it is the short form of, so a
# translator meets them as a pair and nobody can update one and miss the other.
ADDITIONS = [
    (EXPEDITIONS,
     "  <RR_UI_OpenObjective>Open the work board for this objective</RR_UI_OpenObjective>",
     [
         "  <RR_UI_NextAssemblyBrief>Assemble the gate</RR_UI_NextAssemblyBrief>",
         "  <RR_UI_NextCalibrationBrief>Calibrate the gate</RR_UI_NextCalibrationBrief>",
         "  <RR_UI_NextRecoveryBrief>Recover the stranded crew</RR_UI_NextRecoveryBrief>",
         "  <RR_UI_NextFieldSurveyBrief>Survey the site</RR_UI_NextFieldSurveyBrief>",
         "  <RR_UI_NextDispatchBrief>Dispatch a crew</RR_UI_NextDispatchBrief>",
         "  <RR_UI_NextRecoverEvidenceBrief>Bring the record book home"
         "</RR_UI_NextRecoverEvidenceBrief>",
         "  <RR_UI_NextAnalysisBrief>Analyse the record book</RR_UI_NextAnalysisBrief>",
         "  <RR_UI_NextReviewBrief>Review the finished report</RR_UI_NextReviewBrief>",
         "  <RR_UI_NextTelemetryBrief>Research Gate Telemetry</RR_UI_NextTelemetryBrief>",
         "  <RR_UI_NextRevisitBrief>Revisit the surveyed site</RR_UI_NextRevisitBrief>",
         "  <RR_UI_NextLeadTitle>Next lead</RR_UI_NextLeadTitle>",
     ]),
    (EXPEDITIONS,
     "  <RR_UI_StrandedInstructions>The crew and site remain saved. Restore power, recharge "
     "the return reserve and staff the console, then open a new recovery window. If the team "
     "cannot walk, prepare one headquarters relief worker to enter and carry casualties back."
     "</RR_UI_StrandedInstructions>",
     ["  <RR_UI_StrandedTitle>Crew stranded; the site is still held</RR_UI_StrandedTitle>"]),
    (EXPEDITIONS,
     "  <RR_UI_DispatchInstructions>Select one to three available field staff. Keep the "
     "assigned operator at headquarters. Load the shared kit, allow the physical pickup jobs "
     "to finish, and equip the guard using normal RimWorld equipment controls. Dispatch orders "
     "the team to walk to the gate; the opening begins after final readiness checks."
     "</RR_UI_DispatchInstructions>",
     ["  <RR_UI_DispatchTitle>Choose up to three crew, then load the kit</RR_UI_DispatchTitle>"]),
    (EXPEDITIONS,
     "  <RR_UI_SelectMachine>View the gate and its controls</RR_UI_SelectMachine>",
     ["  <RR_UI_MachineControlsTitle>Machine controls</RR_UI_MachineControlsTitle>"]),
    (FIELD,
     "  <RR_UI_FieldObjectives>Survey the six required room families with the record book, "
     "document the route mismatch, carry the book home and shelve it in the records archive. "
     "A clear entity observation and all three original crew returning qualify for the bonus. "
     "Set glow pods down at known junctions and designate them as route markers to counter the "
     "loop.</RR_UI_FieldObjectives>",
     ["  <RR_UI_FieldObjectivesTitle>Contract objectives</RR_UI_FieldObjectivesTitle>"]),
]

REWORDED = [
    (EXPEDITIONS,
     "  <RR_UI_CurrentObjective>Current company objective</RR_UI_CurrentObjective>",
     "  <RR_UI_CurrentObjective>Objective: {0}</RR_UI_CurrentObjective>"),
]

# The resurvey heading and the entity room line live beside their own long forms,
# both of which are in the expeditions file and the field file respectively.
ADDITIONS.append((
    EXPEDITIONS,
    "  <RR_UI_ResurveyPurpose>Return to the same saved site to inspect unexplored rooms, "
    "retrieve remaining salvage or equipment, recover crew, or continue building. Previous "
    "discoveries and construction persist. The initial survey payment and insight are "
    "one-time; this visit does not grant them again.</RR_UI_ResurveyPurpose>",
    ["  <RR_UI_ResurveyTitle>Resurvey; the survey payment does not come twice"
     "</RR_UI_ResurveyTitle>"]))

problems = 0
touched = {}


def load(path):
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8-sig").read().split(NL)
    return touched[path]


for path, anchor, additions in ADDITIONS:
    lines = load(path)
    if additions[0] in lines:
        print("already present: %s" % additions[0].strip()[:62])
        continue
    if lines.count(anchor) != 1:
        print("ANCHOR NOT UNIQUE (%d) in %s: %s"
              % (lines.count(anchor), path.split("/")[-1], anchor.strip()[:72]))
        problems += 1
        continue
    at = lines.index(anchor)
    touched[path] = lines[:at + 1] + additions + lines[at + 1:]
    print("added %d key(s) after %s" % (len(additions), anchor.strip()[:56]))

for path, old, new in REWORDED:
    lines = load(path)
    if new in lines:
        print("already reworded: %s" % new.strip()[:62])
        continue
    if lines.count(old) != 1:
        print("REWORD TARGET NOT UNIQUE (%d): %s" % (lines.count(old), old.strip()[:72]))
        problems += 1
        continue
    lines[lines.index(old)] = new
    print("reworded %s" % old.strip()[:62])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    # utf-8-sig on the way back out: every keyed file in this package carries a
    # BOM and RimWorld's own loader wrote them that way.
    io.open(path, "w", encoding="utf-8-sig", newline=NL).write(NL.join(touched[path]))
    print("wrote %s" % path.split("/")[-1])
