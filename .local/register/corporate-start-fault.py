# -*- coding: utf-8 -*-
"""The corporate start disabled itself on turn one, and it has always done so.

Owner: *"it says : Company Records could not be reconsiled blah blah blah.... and none of our
buttons work"*.

`[Rimrooms][Save] Campaign integrity failed; company actions are disabled` is logged on the line
**immediately before** `[Rimrooms][Company] Initialized ... scenario=async_industries`, because
`InitializeBranch` calls `ValidateSavedState()` as its last act -- so the records it just seeded
are the records that failed.

## The one missing field

`BuildProjectTree` writes a pre-completed project as

    completed        = done,
    insightCommitted = done,
    workDone         = done ? definition.workRequired : 0f,

and **never sets `insightOperationId`.** `ValidateRecordRelationships` requires

    (!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))

so every pre-completed project is an integrity fault, `stateFaultKey` is set, and `CanOperate`
goes false -- which is every button in the mod refusing, which is exactly what the owner saw.

**Only the corporate start names completed projects.** The store and the lone-survivor starts
carry `<completedProjects />`, so `done` is always false, `insightCommitted` is false, the clause
passes and they start clean. So this has been true since the corporate start was written and no
launch had reached it until now.

## The fix

The comment beside the field already stated the intent -- *"a project that begins finished has had
its insight paid for by whoever ran this branch before you"* -- and a paid insight has a receipt.
The id is the same format the live commit path writes in `InvestigationServices`,
`project.id + ":insight"`, taken from the record's own id so the two cannot drift.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICES = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "CampaignServices.cs")

OLD = u"""                records.Add(new ProjectRecord
                {
                    id = branchId + ":project:" + definition.defName,
                    researchDefName = definition.defName,
                    completed = done,
                    // A project that begins finished has had its insight paid for by whoever
                    // ran this branch before you. Leaving it uncommitted would offer the player
                    // a "start" button on work that is already done.
                    insightCommitted = done,
                    workDone = done ? definition.workRequired : 0f,
                });"""

NEW = u"""                string projectId = branchId + ":project:" + definition.defName;
                records.Add(new ProjectRecord
                {
                    id = projectId,
                    researchDefName = definition.defName,
                    completed = done,
                    // A project that begins finished has had its insight paid for by whoever
                    // ran this branch before you. Leaving it uncommitted would offer the player
                    // a "start" button on work that is already done.
                    insightCommitted = done,
                    // **AND A PAID INSIGHT HAS A RECEIPT.** This field was never set, and
                    // `ValidateRecordRelationships` requires a committed insight to carry one --
                    // so every pre-completed project was a save-integrity fault, `stateFaultKey`
                    // was set during `InitializeBranch` itself, `CanOperate` went false and
                    // **every button in the mod refused.** Owner: *"it says : Company Records
                    // could not be reconsiled ... and none of our buttons work"*.
                    //
                    // Only the corporate start names completed projects -- the other two carry
                    // an empty list -- so it is the only start this ever broke, and it broke it
                    // on turn one, from the day it was written.
                    //
                    // The same format `InvestigationServices` writes when the player commits an
                    // insight, built from the record's own id so the two cannot drift.
                    insightOperationId = done ? projectId + ":insight" : null,
                    workDone = done ? definition.workRequired : 0f,
                });"""

text = io.open(SERVICES, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(SERVICES, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("a pre-completed project carries the receipt its commitment implies")
