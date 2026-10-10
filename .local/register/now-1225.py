# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.25-dev and set the next task."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:90]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:90]
    s = s.replace(old, new, 1)


sub(u'| Published | **0.12.24-dev**.', u'| Published | **0.12.25-dev**.')
sub(u'| Assembly | SHA-256 `B382E45C0ADF918FFF8BBAAC643C88DAB1B7CF8F0E9CDA74D60ABB22617030BE`, '
    u'reproduced by **three** clean recompiles.',
    u'| Assembly | SHA-256 `23D01F47CBECAB5D810E3FB3418D17AAFD0F3FF0D3A8903B1398D8CB30736DBE`, '
    u'reproduced by two clean recompiles.')
sub(u'| Proofs | **TWENTY-TWO** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-THREE** in `.local/register/proof-*.py`.')

# ------------------------------------------------------------------ next task
sub(u"""## DO THIS FIRST — contradictory accounts, and the interview that resolves them

Queue item 4. **From the prep material, and it is the oldest unbuilt content direction left**: a
returning crew whose accounts of the same coordinate **do not agree**, and a workflow that resolves
which account the company files.

Three things to establish before writing a line, in this order:

1. **`python tools/register-query.py use RR-EVD` and `use RR-STA`.** The prisoner, casework and
   interview families have real instructions in them — *"Keep custody, casework, and interview goals
   reachable through vanilla prisoner controls"* — and RR-STA is the largest trace at 149 rows.
2. **Read `docs/CAMPAIGN_CHART.md` before the prep documents.** The chart is the authority and beats
   any prep document; the prep names the feature, the chart says where it sits.
3. **Find the real read site first.** Invariant 136 deleted four tier 3 projects for being unlocks
   with nothing to unlock. `EvidenceObservationRecord` already saves `witness`, `witnessLoadId` and
   `witnessRoomIndex` per observation, and `EvidenceObservationKinds.RecorderGap` already exists and
   already requires a prior `RouteMismatch` on the same room and marker. **A contradiction may
   already be expressible in the saved schema** — check that before adding anything to it.""",
    u"""## DO THIS FIRST — the in-game text names four items that no longer exist

**Nine player-facing strings instruct the player to use retired equipment.** Found while writing the
disagreement note at 0.12.25-dev, by grepping the language files for the names of everything this
mod has retired. This is shipped, player-visible, and the worst kind: the tutorial text tells
somebody to do something they cannot do.

| Retired | When | Strings still naming it |
|---|---|---|
| **return beacon** | 0.9.9-dev | `RR_Event_CorridorMismatch`, `RR_UI_FieldObjectives`, `RR_Clue_Text_borrowed_corridor`, `RR_UI_EvidenceFieldWorkRemaining` |
| **survey tag** | 0.10.7-dev → `GlowPod` | `RR_Clue_Text_service_passage`, `RR_UI_FieldObjectives`, `RR_Clue_Text_borrowed_corridor`, `RR_UI_EvidenceFieldWorkRemaining` |
| **evidence case** | 0.10.9-dev → designated `Shelf` | `RR_Event_EvidenceSecured`, `RR_UI_NextRecoverEvidence`, `RR_UI_NextAnalysis`, `RR_UI_FieldObjectives` |
| **field recorder** | 0.12.24-dev → `TextBook` | `RR_UI_EvidenceFieldWorkRemaining`, `RR_Observation_room_survey`, `RR_UI_FieldObjectives` |

Three things to get right:

1. **A marker is still numbered.** `CompRimroomsMarker.Number` is live, so *"numbered tag"* becomes
   *"numbered marker"* or *"numbered glow pod"* — the **marker** survived, only the item changed.
   Do not delete the numbering along with the tag.
2. **Custody is a place now, not an item.** *"return it with the evidence case"* becomes *"bring it
   to the shelf designated as the records archive"*. That is a different instruction, not a reword.
3. **Make it a check, and make it a shape rather than a list.** Invariant 214. A **tenth checker**
   asserting *"no player-facing string names a def this package does not declare"* cannot go stale
   the way a list of four names will. Fault-plant it by putting *"return beacon"* back.

---

## Done, 0.12.25-dev — two crew who disagree

The prep material's *"contradictory accounts"*, the oldest unbuilt content direction left. **The
contradiction was already being computed and thrown away** as a receipt mismatch, and chart line 226
asks request 5 for *"two crew accounts of the same room"* — which was unreachable, because one
evidence record could only ever carry one witness per fact. Accounts are saved now, corroborating or
disputing, **a dispute counts as testimony**, and the readout names them. Full record:
[two crew who disagree](implementation/CONTRADICTORY_ACCOUNTS_IMPLEMENTATION.md).

**Nothing resolves a dispute yet**, and that is said plainly rather than implied: the interview is
the checkpoint after next.""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.24 | **The recorder became the book** — the last authored gameplay item retired without a save break, a dead end closed, and the register made readable |',
    u'| 0.12.24 | **The recorder became the book** — the last authored gameplay item retired without a save break, a dead end closed, and the register made readable |\n'
    u'| 0.12.25 | **Two crew who disagree** — the prep material’s contradictory accounts. **The contradiction was already computed and discarded**, and a tutorial request was unreachable as the chart writes it |')
sub(u'## What shipped this session, 0.7.1 → 0.12.24', u'## What shipped this session, 0.7.1 → 0.12.25')

# ------------------------------------------------------------------ invariants
anchor = (u'220. **A LAW that points at a document its own tool cannot open is a LAW that gets skipped.**')
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
221. **A refusal is a place where information goes to die.** `RR_Company_ReceiptMismatch` was
     *computing* the contradiction this campaign's prep material asks for, and then discarding it —
     and the only caller ignores results, so nothing anywhere saw it. **When a guard refuses
     something interesting, ask what it knew.**
222. **A new saved field must be threaded through every snapshot, copy and validity check that
     existed before it.** `EvidenceAnalysisReport` freezes observations and compares them back with
     `SameSnapshot`; a field those do not know about makes a frozen report agree with a record it no
     longer matches, **with no observable symptom until much later**. Fault-plant those two
     specifically — they cannot be found by reading.
223. **Do not let a reading of the queue substitute for reading the code.** The row said two crew
     who disagree was *"a short step from a mechanism that exists"*. It was not a step from
     anything: the mechanism existed and threw the answer away. **The row was optimistic in the
     wrong direction, which is rarer and worse than a stale row.**""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.25-dev, next task set')
