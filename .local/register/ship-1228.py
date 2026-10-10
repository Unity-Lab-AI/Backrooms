# -*- coding: utf-8 -*-
"""Ledger for 0.12.28-dev: nobody is lying."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def sub(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    write(rel, s.replace(old, new, 1))


sub('CHANGELOG.md', u'## 0.12.27-dev', u"""## 0.12.28-dev - 2026-09-29 - nobody is lying

- **You can now settle a disagreement between two crew.** A staff member takes both statements and the company files one of them as its version of events.
- **Neither crew member is wrong, and the game does not pretend otherwise.** Both accounts were checked against the coordinate when they were given. They disagree because the marker moved between the two visits - which is a thing that happens down there.
- **The account you do not file stays on the record**, with the name of the person who gave it. Nothing is erased.
- **An interviewer needs Social 4**, has to be awake and able to talk, and cannot be one of the crew who gave an account. If nobody on staff qualifies, the readout says so and says what is needed.
- **A finished analysis cannot be reopened.** Once a report is written, the disagreement stays on the record exactly as it was.

Full record: [nobody is lying](docs/implementation/INTERVIEW_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.27-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - nobody is lying (0.12.28-dev)

**Verbatim user quote:** *"get it done"*

### What shipped

The interview half of `TODO.md`'s *"Add analyze/interview/compare/review workflows"* - the thing 0.12.25-dev left with nothing to resolve it.

### Files touched

`src/.../Company/EvidenceInterview.cs` **new**, `src/.../Company/EvidenceObservations.cs`, `src/.../UI/OperationsEvidence.cs`, `1.6/Languages/English/Keyed/RR_Investigation.xml`, `1.6/Languages/English/Keyed/RR_Portals.xml`, `.local/register/proof-interview.py` **new**, `.local/register/fault-plant-1228.py` **new**, `docs/implementation/INTERVIEW_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **I WENT IN TO BUILD A LIE DETECTOR AND THE CODE MADE THAT IMPOSSIBLE, AND BETTER.** `RecordFieldObservation` evaluates `validFact` - `HasDisplacedMarker` against the real map - **before** it ever looks for a prior observation. So a disputing account **was already checked and found true**. Both crew are telling the truth; they disagree because **the marker moved between their two observations**, and silent between-visit displacement has shipped since 0.10.3-dev. **This is what that mechanic looks like from inside an evidence file.**
- **So an interview decides which account the CORPORATION files, not who is right** - the game cannot know who is right, because both are. That is a much better fit for this campaign, and it means **no invented statistic**. RimWorld has no reliability, honesty or credibility stat and the register is explicit: *"Keep the company's evaluation based on actual pawn traits, skills, and relationships."* The only skill consulted is `SkillDefOf.Social`, and the proof asserts no other `SkillDefOf` and no word like *reliability* appears in the file.
- **BOTH ACCOUNTS SURVIVE.** `Settle()` touches no fact field at all: it records which account was filed and deletes nothing. `Disputed` and `Settled` are kept as two separate questions, so a settled fact is **still disputed** and the readout keeps naming the witness whose account was not filed. **An evidence chain that erased the testimony it declined would be worth less than one that keeps both and says which.** Fault-planted: adding `markerNumber = 0;` to `Settle()` fails the proof.
- **Nine refusals, all translated, all reachable** - invariant 136. The one that protects the save is `RR_Interview_RecordClosed`: `EvidenceAnalysisReport` freezes a snapshot and `IsValidFor` compares it back with `SameSnapshot`, so settling after a report was written would let the frozen report agree with a record it no longer matches, **silently**. Two protections ship rather than one - the refusal is the rule, and the settlement fields are threaded through `SameSnapshot`, `SnapshotCopy` and `IsValidFor` anyway, which is what catches the rule being wrong.
- **A settlement cannot be half-written.** `IsValidFor` rejects a settlement with nothing to settle, no filed account or no interviewer named - **and settlement details with no tick**, which is the shape a partial save would produce. It also rejects a record whose interviewer is the filed witness, which the action already refuses, so the guard and the validity check disagree about nothing.
- **Social 4, matching the Intellectual 4 the analysis workflow already asks**, so the two desk jobs in this campaign ask comparable things of a pawn.
- **NO PRISONER MECHANIC IS TOUCHED**, per the register's *"Keep custody, casework, and interview goals reachable through vanilla prisoner controls"*. These are employed staff giving statements to a colleague, and the proof asserts the file contains no `prisoner`, `warden`, `detain`, `guest` or `IsSlave` at all.
- **The interviewer pick is deterministic.** Most socially capable employed staff member who is not one of the people being interviewed, **breaking ties on load id** rather than staff-list order - invariant 26. Without it the readout names a different interviewer between frames. It enforces **the same skill floor as the action**, because a button naming somebody the action would then refuse is worse than no button. And when nobody qualifies the pane **says so and names the requirement** rather than hiding the section: a missing button is not information.
- **Twenty-fifth proof, 44 claims, fault-planted nine ways and caught 9 of 9.** Three of the nine cannot be found by reading - settling rewriting a fact, the snapshot stopping its comparison, and a half-written settlement validating - because none changes behaviour a player could see until a report is frozen or a save is reloaded mid-settlement.
- Build 0.12.28-dev, **176 C# files, 87 package files**, **0 warnings, 0 errors**. Assembly `44D6083F3ED4DF1191563A6940524F2E23BC5336E64376A299BD7F852205307C`, identical across two clean rebuilds. Ten checkers pass, **twenty-five** proofs exit zero. **No game was launched, so nobody has ever been interviewed about anything.**

---

## Completed sessions""")

print('ledger written for 0.12.28-dev')
