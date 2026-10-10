# -*- coding: utf-8 -*-
"""Close the recorder-fold row: the fold shipped, and it now has the plants it never had."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **NEXT: build the recorder fold.**',
  'CLOSED 0.12.96-dev. **The fold shipped; what was missing was anybody ever watching it hold.** '
  'The row is one line from 0.12.14-dev and comes from the decision *"Field recorder → the book is '
  'the recorder. One Core `TextBook`: carried in blank, written in the field, carried home as the '
  'evidence. lose the book, lose the run."* '
  '**It is folded.** `ExpeditionCargo.RecordBookDef` resolves through '
  '`CompRouteEvidence.NativeCarrierDef` — not a def-name string, because *"a def-name string would '
  'match another mod\'s TextBook just as happily"* — and that predicate requires **Core '
  'provenance** and **exactly one** of our comps. `TryFindRecordBook` finds it in a crew member\'s '
  'inventory, the carrier must be a living spawned member of the run, and `RecordBookDelivery` '
  'exists so nobody meets `RR_Exp_MissingRecordBook` with no idea what a record book is. '
  '**And the four read sites are real, counted rather than asserted:** `RecorderGap` is handled in '
  '**two** switches inside `EvidenceObservations` — recording it and reading it back are separate, '
  'and a kind handled by one and not the other is an observation that is **stored and never '
  'surfaces** — raised by `FirstSliceSiteComponent`, and treated as a finding by `RequestLine`. '
  'Four, which is what the row said. '
  '**`RecorderGap` appeared in no proof at all**, so the fold could have un-folded one site at a '
  'time with no symptom but an expedition that quietly stopped noticing a missing book. Six claims '
  'now cover it, including one that refuses the literal `"recorder_gap"` anywhere but its own '
  'declaration — a string typed at four call sites is four chances to typo it into silence. '
  '**And `proof-record-book.py` had 34 claims and NO plant suite**, which is the condition that '
  'makes a proof decorative: a claim nobody has watched refuse is indistinguishable from a comment '
  'that agrees with itself. `plant-record-book.py` is new and lands **11 of 11**. '
  '**Two of its plants were wrong before they were right, both my error:** one renamed a '
  'declaration while the reference that the claim actually reads lived in another file, and one '
  'aimed at a constant\'s name when the claim was about refusing on null. **A third exposed a weak '
  'claim:** `QueueLoadout` reads two masses — the pawn\'s carried thing and the item being loaded — '
  'and a claim for bare `GetStatValue(StatDefOf.Mass)` passed while a plant replaced the item\'s '
  'read with a constant. The claim now names the item.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:85]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
