# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.26-dev: ten checkers, and set the next task."""
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


sub(u'| Published | **0.12.25-dev**.', u'| Published | **0.12.26-dev**.')
sub(u'| Assembly | SHA-256 `23D01F47CBECAB5D810E3FB3418D17AAFD0F3FF0D3A8903B1398D8CB30736DBE`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `0E265705F23D1CC907E25CF48C767B5548ED99F8EB3588FD992DD9488DD68EA5`, '
    u'reproduced by two clean recompiles.')
sub(u'| Checkers | **NINE**, all passing |',
    u'| Checkers | **TEN**, all passing. The tenth, `check-retired-content.py`, refuses player-facing '
    u'text that names equipment this mod retired — **fourteen strings were doing it** |')
sub(u'7. **Every checker** (NINE): `check-package-integrity.py`, `check-keyed-strings.py`, '
    u'`check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, '
    u'`check-campaign-absolutes.py`, `check-doc-conformance.py`, `check-register-compliance.py`, '
    u'`research/audit-gate0.py`.',
    u'7. **Every checker** (TEN): `check-package-integrity.py`, `check-keyed-strings.py`, '
    u'`check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, '
    u'`check-campaign-absolutes.py`, `check-doc-conformance.py`, `check-register-compliance.py`, '
    u'`check-retired-content.py`, `research/audit-gate0.py`.')

# ------------------------------------------------------------------ next task
sub(u"""## DO THIS FIRST — the in-game text names four items that no longer exist

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
   the way a list of four names will. Fault-plant it by putting *"return beacon"* back.""",
    u"""## DO THIS FIRST — the interview that resolves a disagreement

Queue item 4's remainder, and `TODO.md`'s *"Add analyze/interview/compare/review workflows"*, where
**compare now ships and interview does not.** Two crew who disagree produce a saved dispute
(0.12.25-dev) and **nothing resolves it.** That is the piece that makes a dispute a decision rather
than a note.

What already exists, so this is not built from nothing:

- **`EvidenceObservationRecord.Disputed`** and the `WitnessAccountRecord` list, each with a named
  witness, their room, and what they place the marker at.
- **`CaseRecord`** — id, `titleKey`, `coordinateId`, `evidenceIds`, `closed` — one per coordinate,
  created at contract time in `CampaignServices.cs:127`. **A case is where a resolution belongs.**
- The Operations panes, and `DrawEvidenceDetails` already rendering each account.

Four things to settle before writing a line:

1. **`python tools/register-query.py use RR-STA`** — 149 rows, and the interview instruction is
   explicit: *"Keep custody, casework, and interview goals reachable through vanilla prisoner
   controls"*. **These are employed staff, not prisoners** — do not reach for detention mechanics.
2. **Do not invent a reliability stat.** RimWorld has none, and the register says *"Keep the
   company's evaluation based on actual pawn traits, skills, and relationships"*. Real and available:
   `SkillDefOf.Social` on the interviewer, and real traits.
3. **Decide what resolution MEANS** before writing it. Filing one account as the company's version
   is honest for a corporation. Deciding who is *right* is not something the game can know.
4. **A resolution must be refusable.** Invariant 136: every clause has to be able to refuse. No
   interviewer available, a witness dead, a witness no longer employed, the evidence already
   analysed — each is a real reason it cannot happen, and each needs a keyed refusal.

---

## Done, 0.12.26-dev — the in-game text names only what exists

**Fourteen pieces of player-facing text told the player to use retired equipment**, and three keys
were labelling defs that stopped existing long ago. I found nine by eye; **the check found fourteen,
then two more in def descriptions** — and my first version of the check would have passed while one
of them sat in a live research project, because its def pattern was blind to this mod's own
namespaced def types. Full record:
[the in-game text stops naming things that do not exist](implementation/RETIRED_VOCABULARY_IMPLEMENTATION.md).""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.25 | **Two crew who disagree** — the prep material’s contradictory accounts. **The contradiction was already computed and discarded**, and a tutorial request was unreachable as the chart writes it |',
    u'| 0.12.25 | **Two crew who disagree** — the prep material’s contradictory accounts. **The contradiction was already computed and discarded**, and a tutorial request was unreachable as the chart writes it |\n'
    u'| 0.12.26 | **The in-game text names only what exists** — fourteen strings instructed the player to use retired gear. **A tenth checker**, and an archive hole repaired so its derivation is complete |')
sub(u'## What shipped this session, 0.7.1 → 0.12.25', u'## What shipped this session, 0.7.1 → 0.12.26')

# ------------------------------------------------------------------ invariants
anchor = u'223. **Do not let a reading of the queue substitute for reading the code.**'
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
224. **A string that resolves is not a string that is true.** `check-keyed-strings.py` verifies
     every key resolves and every used key exists; fourteen strings satisfied it while instructing
     the player to use a return beacon, a survey tag, an evidence case or a field recorder. **Text
     can be well-formed, translated, referenced and wrong.**
225. **A derived list is only as complete as what it derives from.** The retired-content check
     derives its names from the archive, and `RR_ReturnBeacon` had never been archived — so the
     check would have been quietly partial **and passed**. Repair the source before trusting the
     derivation.
226. **A rule that reads defs must know this mod's OWN def types.** My first retired-content check
     listed Core def types only, so it was blind to `RimroomsProjectDef`, `RimroomsRequestDef` and
     the procurement catalogue — most of what this mod authors. It would have passed with the defect
     in a live research project description.
227. **Retiring a thing leaves its WORDS behind, and they need a disposition.** Whether the concept
     survived the item cannot be derived: an emergency return is live while its cutoff is not; an
     analysis bench is live while the custom building is not. Record the decision **with its
     reason**, and make a new retirement fail until somebody makes it.""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.26-dev, ten checkers, next task set')
