# -*- coding: utf-8 -*-
"""Close what this batch actually built. Status marker only; evidence appended to the row LINE.

## THE EVIDENCE GOES ON THE ROW'S OWN LINE, and the previous closer got that wrong

The 0.12.82 through 0.12.85 closers computed the row's end as
`text.find(NL + "- [", at)` and appended there -- which is past the blank line
after the row, so the evidence landed on a line of its own. The archiver then
moved the bullet and left the evidence behind: **twelve stranded lines across four
published versions**, recovered on 2026-10-04 and recorded in
`docs/FINALIZED.md` under *Recovered row bodies*.

This closer appends to the end of the **first line** of the row and nothing else,
and `tools/check-queue-integrity.py` now fails on any closure evidence that is
not on a row.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 # ======================================================= the Operations panel, pane by pane
 ('- [ ] **"we need to make the whole operations panel thing alot less of a text wall its like a fucking novel when it doesnt need to be"**',
  'CLOSED 0.12.86-dev, and the row’s own condition was met first: **"less" is a number and '
  'it was measured before anything was cut.** `tools/check-operations-density.py` reports '
  'on-screen words, hover words, controls and words-per-action **per pane**, as a ratchet. The '
  'panel went from **4,015 on-screen words to 2,551**, with **1,583 words moved onto hovers** '
  'and words-per-action from **32.9 to 22.6**. '
  '**The tool was blind in two ways and both were fixed before the figures were believed.** It '
  'counted keys assigned to a variable and translated later as **zero** — 367 words of the '
  'longest instructions in the panel, including the whole eleven-branch objective chain — so '
  '`indirect_groups` now resolves them and charges the **worst** branch rather than the sum, '
  'because exactly one draws per frame. And it read comments as code: a comment of mine '
  'containing the word *tooltip* reclassified a heading into the hover bucket, so the scan now '
  'strips comments with a string-aware scanner. Two ceilings went **up** when the blindness was '
  'removed and then came down by the work; a ratchet whose baseline was measured by a blind '
  'instrument is a ratchet holding the wrong line.'),

 ('- [ ] **"for example one of many things that can be done and all things should be done to make it more of a utility, not  a text wall"**',
  'CLOSED 0.12.86-dev. *"all things should be done"* is the binding half and the green/red '
  'readout was named as **one example**, so the work was a **house style** rather than a list of '
  'edits: `UI/OperationsControls.cs` holds two primitives — `DrawHeading`, a short line with '
  'the whole explanation on hover, and `DrawAction`, a control that stays visible and **says why '
  'when it will not work**. Seventeen panes rewritten by hand would have been seventeen chances '
  'for the hover to attach to the label instead of the row and for *"well designed"* to mean '
  'something different on every tab. They began as private methods on the window and were moved '
  'to a static class with `using static`, because `PersonnelView` and '
  '`Dialog_ConfirmApplicantHire` could not reach them and held **130 words** of the personnel '
  'pane between them — a primitive the dialogs cannot call is a primitive the panel gets a '
  'second copy of.'),

 ('- [ ] **"and all the tabs of operations are well designed for a tripple A Mod currently it looks like its all just text wall and shit"**',
  'CLOSED 0.12.86-dev. **Every one of the eighteen pane files was measured and named**, not the '
  'worst few: MainTab **421→195**, Expeditions **477→215**, Personnel **413→217**, '
  'PortalNetwork **396→288**, Procurement **323→262**, Facilities **312→229**, '
  'GateBinding **282→189**, Evidence **183→78**, HeldPlaces **187→86**, '
  'LaboratoryBinding **148→61**, Requests **157→102**, ContractTerms **101→47**, '
  'EvidenceRecovery **62→40**, CrewPlanner **174→163**. '
  '**Three were deliberately left alone and the reason is recorded in each.** `OperationsHelp` '
  'is where prose is the product. `OperationsRemoteSites` holds 48 words in six keys, none over '
  'fourteen, and both long ones are live readouts — a first attempt hung the empty-list '
  'message on its heading as a definition, which is a tooltip that lies whenever the list is not '
  'empty. `OperationsConnectedWork` is 48 words in ten keys drawn inside the portal pane. '
  '**And three messages stay on screen on purpose**: the unsupported-save warning, the '
  'missing-policy fault, and `RR_Portals_NoLaboratoryAddress` — which exists because of the '
  'owner’s own *"what do i do to get this gate open? ive tried everything"*, and hiding it '
  'behind a hover would re-break the thing it fixed.'),

 ('- [ ] **"and everything that the machine needs to start up should be able to do in the worlkd from the devices themselfes with pawns controls and actrions not just in the opetaions tab"**',
  'CLOSED 0.12.86-dev. A designated gate already offered eleven commands on the door — '
  'history, blind dial, abort, crossing, equipment links, the run fallback, cutoff, kill switch, '
  'operator, calibrate, staff. **The two it did not offer were the two the owner named**, and '
  '`Gate/GateAddressControls.cs` is both: setting the address and opening the connection. So a '
  'player can now build, crew, calibrate, aim and open the machine without opening the panel at '
  'all. **Nothing is reimplemented** — it calls `RegisterLaboratoryAddress` and '
  '`BeginSpinUp`, the same two the pane calls, with the same freeze notice in front of the one '
  'that builds a map. A second **surface** on one authority, which is the opposite of a second '
  'derivation of one rule.'),

 ('- [ ] **"ie setting the cordinace and all of those things need  to show"**',
  'CLOSED 0.12.86-dev as the hardest case it was named as. **Set this gate’s address** is a '
  'command on the door: a float menu of every known place, each shown by its **address code and '
  'depth** and never its raw id, per the same message’s *"only like the !A-01 address code '
  'is needed to be displayed to thew player"*. A float menu row has nowhere to put a tooltip '
  'carrying the internal identifier, so that rule is harder here than in the panel. '
  '**And both commands grey out with a reason rather than disappearing** — the standing '
  'answer to *"ive done like 50 things in a row and its still not opening"*, because a command '
  'that vanishes when it cannot run teaches a player nothing. The freeze notice is legal from a '
  'gizmo for the same reason it is legal from the pane’s button: neither is waiting on a '
  'return value, which is what lets the work move into a long event and the warning draw first. '
  'That is also why the **gate-enter path still cannot do this** and stays recorded rather than '
  'claimed.'),

 ('- [ ] **"and when u set a door to be a gatew  that gate should tell you next step in the game world not just in the operations tab and machine tab"**',
  'CLOSED 0.12.86-dev. The eleven start-up checks moved out of a private method on the Operations '
  'window into `Gate/GateStartupChecklist.cs`, and the door’s inspect card names the first '
  'unfinished one — **first on the card**, above ten readouts that all answered *what is the '
  'state* and none of which answered *what do I do*. **The extraction is proved to have changed '
  'nothing**: the step list normalises byte-for-byte identical to the original, which is the test '
  'a behaviour-preserving move has to pass. '
  '**Answering it on the door had exactly two options and the other one is the defect this '
  'project keeps meeting** — writing the eleven conditions a second time is what made '
  '`RR_Gate_CalibrationUnavailable` read *"the gate is not ready for calibration"* for eight '
  'causes including *already calibrated*. So there is one list, a claim asserts the window holds '
  '**no second copy**, and a plant proves that claim can fail. The not-designated guard comes '
  'first and has its own plant, because this component sits on **every Core door in the game** '
  'and a line computed above that return would put gate advice on every bedroom door on the map.'),

 # ========================================================= the stand-alone declaration
 ('- [ ] **"rework mod to not need any depeancie mods"** — **the declaration half, which is small and is the half the player actually feels.**',
  'CLOSED 0.12.86-dev, and **provably lossless.** `About.xml` declared **293 hard '
  '`modDependencies`** and **294 `loadAfter`** entries. Measured before a line was written: '
  '**every single declared packageId was already in `loadAfter`**, which additionally carries '
  '`Ludeon.RimWorld`. So the block carried **no ordering information the load-order block did '
  'not already carry** — 1,462 lines of it — and deleting it removes a '
  'missing-dependency wall and a manager’s red list while changing the load order by '
  'nothing at all. The identity is re-proved inside the script that did it, because *"they are '
  'all in loadAfter"* read off a terminal once is not a reason to delete 1,462 lines. '
  '**A plant then found the gap this created.** With nothing declared, the rule *every declared '
  'dependency must also be ordered* has nothing to iterate, so `loadAfter` became the one thing '
  'carrying the whole weight and the one thing nobody checked — '
  '`plant-dependencies.py` reported **MISSED** when a former dependency was deleted from the '
  'order. `check-register-compliance.py` now requires `loadAfter` to match the 294-row profile '
  'register **exactly**, keyed to the register so adding a mod updates the rule by updating the '
  'register. The cost it guards is measured: this package sat at **position 197 of 296** in the '
  'owner’s live load order with **99 mods loading after it**.'),

 ('- [ ] **"rework mod to not need any depeancie mods"** — **the five expansions are their own decision inside this**,',
  'CLOSED 0.12.86-dev. The five `Ludeon.RimWorld.*` entries came out of `modDependencies` with '
  'the other 288 and remain in `loadAfter`. **This returns D4 to the position it held when it was '
  'first recorded** — *"Core-only campaign; all five DLC optional detected content"*, '
  '2026-09-27 — which the 2026-10-01 amendment had reversed. The guards stay; the '
  'conditional-layer work in Major M4 is what makes declaring nothing honest rather than merely '
  'quiet. `GATE_0_DECISIONS.md`, `ROADMAP.md` and `ARCHITECTURE.md` are amended in this same '
  'commit and **every superseded owner quote is struck in place, not deleted** — a decision '
  'log that erases the decision it replaced cannot be audited.'),

 ('- [ ] **"rework mod to not need any depeancie mods"** — **the claim rule tightens rather than relaxes.**',
  'CLOSED 0.12.86-dev, and the rule **inverted rather than being removed.** Until now the '
  'dangerous sentence was *"this needs nothing"* while `About.xml` declared 293; that sentence is '
  'now true, and the dangerous one is *"this works with everything"*, which nobody has shown. '
  '`check_broad_compatibility` refuses ten such phrasings in any living document, **only while '
  'the declared count is zero** — which is exactly when a reader has no declaration to '
  'calibrate against and silence reads as a guarantee. D1 is unmoved: *"do not announce '
  'compatibility until validation is complete"*. `ROADMAP.md` already listed *"Promising '
  'compatibility with every mod simply because the server has `AllowAllMods` enabled"* as a '
  'non-goal and **nothing enforced it until now.** Proved by hand before being believed: a '
  'planted sentence in `ARCHITECTURE.md` was reported with its line number, and the plant that '
  'tried to disable the rule itself was **retired as uncatchable by construction**, with the '
  'reason left in the suite — it changes nothing observable while no correct document '
  'contains an offending phrase, and the plant that adds one already proves the rule fires.'),

 ('- [ ] **A CHECKER CURRENTLY ENFORCES THE OPPOSITE, and it will block this work on the first run.**',
  'CLOSED 0.12.86-dev, and **the row was half right in a way worth recording.** It predicted the '
  'build gate would fail on correct documents. It did not: `check_dependency_claims` opens with '
  '`if declared <= 0: return`, so dropping the block disabled the old rule by itself and nothing '
  'failed. What the row got right is the part that is **not** automatic — that the rule had '
  'to be dealt with in the same change rather than left pointing the wrong way. It was: the '
  'printed label said *"no living document may say there are none"* in both directions and now '
  'states both halves, and the inverted rule above took its place.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0

for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:92]))
        problems += 1
        continue
    at = text.index(anchor)
    # **THE ROW'S OWN LINE, and nothing past it.** This is the fix for the stranding defect.
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
