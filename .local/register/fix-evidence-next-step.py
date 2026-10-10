# -*- coding: utf-8 -*-
"""A found route recording never said what to do with it.

Owner: *"there is a weird route thing name a self in one of the rooms and this is kinda weird and
odd"*, then *"route thing name was on a shelf .. furnature in the back rooms i meant"*, then the
actual complaint: **"it was confusing at what i was suppose to do with it"**.

The item is working content, not a bug: a physical route recording left on a shelf by somebody
who was in the Backrooms before you. **What was broken is that nothing told the player that.**
Clicking it gave:

    Case status: Unanalysed
    Analysis: 0%

-- a status readout for a procedure the player has not been told exists. The description explains
it in four sentences, and nobody reads a description on a shelf in a maze.

So the inspect string ends with **the next thing to do**, in one line, phrased as an instruction
rather than as a state: carry it home, put it on the shelf you designate as the records archive,
then analyse it at a powered field analysis bench. The unregistered case gets the same treatment
-- it used to say *"inspect the company record"*, which is a thing to look at rather than a thing
to do.

**No mechanic changed.** The item, the comp, the recovery order and the analysis bench are all
exactly as they were. The player is simply told.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed", "RR_Investigation.xml")
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Investigation",
                    "CompRouteEvidence.cs")

K_EDITS = [
    (u"  <RR_Evidence_Inspect>Case status: {0}\\nAnalysis: {1}</RR_Evidence_Inspect>",
     u"  <RR_Evidence_Inspect>Case status: {0}\\nAnalysis: {1}\\n{2}</RR_Evidence_Inspect>\n"
     u"  <RR_Evidence_NextStep>Right-click it with a colonist to carry it out. Take it home, put "
     u"it on the shelf you designate as the records archive, then analyse it at a powered field "
     u"analysis bench.</RR_Evidence_NextStep>"),

    (u"  <RR_Evidence_Unregistered>Evidence has no branch case record. Preserve the item and "
     u"inspect the company record.</RR_Evidence_Unregistered>",
     u"  <RR_Evidence_Unregistered>Somebody left this here before you. It has no case record on "
     u"this branch yet - carry it out and take it home, and it will open one.</RR_Evidence_Unregistered>"),
]

keyed = io.open(KEYED, encoding="utf-8-sig").read()
problems = []
for old, _ in K_EDITS:
    if keyed.count(old) != 1:
        problems.append("%d of %r" % (keyed.count(old), old[:56]))
if problems:
    for problem in problems:
        print("KEYED ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in K_EDITS:
    keyed = keyed.replace(old, new, 1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(keyed)
print("keyed: the next step is written, and the unregistered line says what to do")

C_OLD = u'''                : "RR_Evidence_Inspect".Translate(("RR_EvidenceStatus_" + record.Status).Translate(),
                    (record.AnalysisWork / WorkRequired).ToString("P0")).ToString();'''
C_NEW = u'''                // **THE NEXT THING TO DO, not just the state.** Owner, on finding one on a
                // shelf in the Backrooms: *"it was confusing at what i was suppose to do with
                // it"*. A status readout is only useful to somebody who already knows the
                // procedure exists, and the description that explains it is four sentences long
                // on an item lying in a maze.
                : "RR_Evidence_Inspect".Translate(("RR_EvidenceStatus_" + record.Status).Translate(),
                    (record.AnalysisWork / WorkRequired).ToString("P0"),
                    "RR_Evidence_NextStep".Translate()).ToString();'''

comp = io.open(COMP, encoding="utf-8").read()
if comp.count(C_OLD) != 1:
    print("COMP ANCHOR PROBLEM: %d" % comp.count(C_OLD))
    raise SystemExit(1)
io.open(COMP, "w", encoding="utf-8", newline="").write(comp.replace(C_OLD, C_NEW, 1))
print("the inspect string ends with the instruction")
