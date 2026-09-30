# Nobody is lying — 0.12.28-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the interview half of the analyse/interview/compare/review
workflows, and the thing 0.12.25-dev left with nothing to resolve it.

---

## The discovery that decided the design

I went in expecting to build a lie detector — two accounts, one of them wrong, somebody working out
which. **Reading the order of operations in `RecordFieldObservation` made that impossible, and
better.**

`validFact` is evaluated **before** the code ever looks for a prior observation:

```csharp
case EvidenceObservationKinds.RouteMismatch:
    validFact = witnessRoom.index == roomIndex && HasDisplacedMarker(
        coordinate, map, roomIndex, referencedRoomIndex, markerNumber);
    break;
...
if (!validFact) { return CompanyActionResult.Refused("RR_Evidence_NotReady"); }
...
if (prior != null) { /* the account branch */ }
```

So **a disputing account was already checked against the map and found true.** Both crew are
telling the truth. They disagree because **the marker moved between their two observations** — and
silent between-visit displacement has shipped since 0.10.3-dev, *"something is not where you left
it"*. This is what that mechanic looks like from the inside of an evidence file.

That settles what an interview can honestly be. Not *who is right* — the game cannot know, because
both are. It is **which account the corporation files**, which is a very different and much more
fitting thing for this campaign to be about.

**And it means no invented statistic.** RimWorld has no reliability, honesty or credibility stat,
and the register is explicit:

> *"Keep the company's evaluation based on actual pawn traits, skills, and relationships."*

The only skill consulted is `SkillDefOf.Social` on a real pawn. The proof asserts no other
`SkillDefOf` appears in the file and that no word like *reliability* or *credibility* does either.

---

## Both accounts survive, deliberately

Settling records **which** account is filed. It does not rewrite the fact and does not delete the
other account.

| | |
|---|---|
| `Disputed` | somebody who was there disagrees |
| `Settled` | the company has chosen which version it files |

Two separate questions, kept separate. A settled fact is **still disputed** — the disagreement is
permanent, and the readout keeps naming the witness whose account was not filed.

An evidence chain that erased the testimony it declined would be worth less than one that keeps both
and says which. `Settle()` touches no fact field at all, and the proof fault-plants exactly that:
adding `markerNumber = 0;` to it fails.

---

## Every clause can refuse, and one refusal matters more than the rest

Invariant 136: a workflow whose checks cannot fail has not been thought about. Nine refusals, all
translated, all reachable:

| Refusal | When |
|---|---|
| `RR_Interview_Inactive` | the branch is not operating |
| `RR_Interview_RecordUnavailable` | the record or observation is off the books |
| **`RR_Interview_RecordClosed`** | **analysis is complete** — see below |
| `RR_Interview_NotDisputed` | nobody disagreed |
| `RR_Interview_NoSuchAccount` | the account is not on this observation |
| `RR_Interview_WitnessUnavailable` | the person who gave it is dead or no longer employed |
| `RR_Interview_InterviewerUnavailable` | not employed, asleep, downed, cannot talk, mental break |
| `RR_Interview_InterviewerIsWitness` | they gave one of the accounts themselves |
| `RR_Interview_InterviewerUnskilled` | below Social 4 |

**`RecordClosed` is the one that protects the save.** `EvidenceAnalysisReport` freezes a snapshot of
the observations and `IsValidFor` compares it back with `SameSnapshot`. Settling after a report was
written would let the frozen report agree with a record it no longer matches — silently, with no
symptom until much later.

So two protections ship, not one:

- the **refusal** is the rule, and
- the settlement fields are **threaded through `SameSnapshot`, `SnapshotCopy` and `IsValidFor`
  anyway**, which is what catches the rule being wrong.

That is the same discipline the accounts list needed at 0.12.25-dev, and the same two fault plants
prove it: *"the analysis snapshot stops comparing the settlement"* and *"a half-written settlement
becomes valid"*.

### A settlement cannot be half-written

`IsValidFor` rejects both directions:

- a settlement with no disagreement to settle, no filed account, or no interviewer named
- **settlement details with no tick** — which is the shape a partial save would produce

And it rejects a record where the interviewer is the filed witness, which the action already
refuses. The guard and the validity check disagree about nothing.

---

## Social 4, and no prisoner mechanic

Four, matching the **Intellectual 4** the analysis workflow already asks for, so the two desk jobs
in this campaign ask comparable things of a pawn.

The register's other instruction on this subject:

> *"Keep custody, casework, and interview goals reachable through vanilla prisoner controls."*

**Nothing here touches a prisoner mechanic.** These are employed staff giving statements to a
colleague. The proof asserts the file contains no `prisoner`, `warden`, `detain`, `guest` or
`IsSlave` at all — not as a guard, not as a comment. Vanilla prisoner controls remain the only way
to interview a prisoner, which is what the row asks for.

---

## Who the company would send

`InterviewerFor` names the most socially capable employed staff member who is not one of the people
being interviewed, **breaking ties on load id** rather than staff-list order — invariant 26, sort
before choosing. Without that the readout names a different interviewer between frames, which is a
readout nobody trusts.

It enforces **the same skill floor as the action**, because a button naming somebody the action
would then refuse is worse than no button.

And when nobody qualifies, the pane **says so** and names the requirement, rather than hiding the
section. A missing button is not information.

---

## The proof, fault-planted nine ways

`.local/register/proof-interview.py` — the **twenty-fifth** — asserts **44 claims** across six
groups.

| Planted fault | Exit | Caught |
|---|---|---|
| an analysed record can be reopened | 1 | ✓ |
| the interviewer may be one of the witnesses | 1 | ✓ |
| the skill floor stops being enforced by the action | 1 | ✓ |
| an account not on the observation can be filed | 1 | ✓ |
| the picker becomes order-dependent instead of deterministic | 1 | ✓ |
| **settling rewrites the observation fact** | 1 | ✓ |
| **the analysis snapshot stops comparing the settlement** | 1 | ✓ |
| **a half-written settlement becomes valid** | 1 | ✓ |
| no available interviewer hides the section instead of saying so | 1 | ✓ |
| *restored* | **0** | — |

The three in bold cannot be found by reading. None changes any behaviour a player could see until a
report has been frozen, or until a save is reloaded mid-settlement.

---

## Receipts

| | |
|---|---|
| Version | 0.12.28-dev |
| Build | **176 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `44D6083F3ED4DF1191563A6940524F2E23BC5336E64376A299BD7F852205307C`, identical across two clean rebuilds |
| New gameplay content | **none.** Saved fields on an existing record, fourteen keyed strings |
| Save break | **none.** Additive, and an old save has settled nothing — which is true of it |
| Invented statistics | **zero**, and the proof asserts it |
| Prisoner mechanics touched | **none**, and the proof asserts that too |
| Register | `use RR-STA` (149 rows) and `use RR-EVD`; two instructions applied |
| Checkers | **ten**, all passing |
| Proofs | **twenty-five**, all exiting zero |
| Planted faults caught | **9 of 9** |
| Game launched | **no.** Nobody has ever been interviewed about anything |
