# -*- coding: utf-8 -*-
"""Ledger for 0.12.25-dev: two crew who disagree."""
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


sub('CHANGELOG.md', u'## 0.12.24-dev', u"""## 0.12.25-dev - 2026-09-29 - two crew who disagree

- **A second crew member's account of the same thing is now kept.** Before, whoever spoke first was the only one on the record: an identical account was folded into theirs and a **different** account was thrown away silently.
- **Two crew who disagree about one room now produce a real disagreement.** The company files the first account, keeps the second, and the evidence readout names both, who gave them, when, and where each of them puts the marker.
- **You are told when it happens**, once, at the coordinate.
- **A disagreement still counts as testimony.** The company does not pretend the second person never spoke, so the contract that asks you to report a disagreement is now satisfied by an actual disagreement instead of only by visiting two different coordinates.
- **One person counts once**, however long they stand there.
- **Nothing in your save breaks.** A save with no accounts on record simply has none, which is true of it.

**Not yet:** nothing resolves a disagreement. The accounts sit on the record and the analysis reports them; deciding which one the company files is the next piece of work.

Full record: [two crew who disagree](docs/implementation/CONTRADICTORY_ACCOUNTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.24-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - two crew who disagree (0.12.25-dev)

**Verbatim user quote:** *"read now.md to continue the working count of the remain doable work of the build whicvh shall be ALL build work completed 100% no exceptions!!! perfectly and masterfully for exactly how Rimworld requires it in order to work. and we need to make sure we are refrenceing the lore and prep when building out all the content and ingame information and items and benches and quests and all of that that might need updated per the guidace on the mods in the columns of the mod registar"*

### What shipped

The prep material's *"contradictory accounts"*, which was the oldest unbuilt content direction left - and the shipped defect that made chart line 226 unreachable as written.

### Files touched

`src/.../Company/EvidenceObservations.cs`, `src/.../Company/RequestLine.cs`, `src/.../Threats/FirstSliceSiteComponent.cs`, `src/.../UI/OperationsEvidence.cs`, `1.6/Languages/English/Keyed/RR_Investigation.xml`, `1.6/Languages/English/Keyed/RR_FieldAndThreats.xml`, `.local/register/proof-contradictory-accounts.py` **new**, `.local/register/fault-plant-1225.py` **new**, `docs/implementation/CONTRADICTORY_ACCOUNTS_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE CONTRADICTION WAS ALREADY BEING COMPUTED AND THROWN AWAY.** `EvidenceObservationRecord.StableId` is per-room for **only** a room survey, so one evidence record held exactly one route mismatch, one recorder gap and one entity sighting - **one witness each** - while `RecordEncounterObservations` loops over every present crew member and files both with the **same** witness. The second person's account was either merged into the first (identical facts, `Existing()`) or **refused as `RR_Company_ReceiptMismatch`** (different facts), and the site tick ignores the result either way. **A disagreement between two crew standing in one room left no trace anywhere in the save.**
- **A TUTORIAL REQUEST WAS UNREACHABLE AS THE CHART DESCRIBES IT.** `docs/CAMPAIGN_CHART.md` line 226 asks request 5 for *"two crew accounts of the same room"*, and `RR_Request_ReportADisagreement` asks a Testify route for `count 2` on distortion logs. Since `LivingWitnessCount("distortion")` could return at most **one per evidence record**, that request was only ever satisfiable **across two separate coordinates** - never by an actual disagreement, which is the thing it is named after.
- **A dispute counts as testimony, and that is the design decision here.** Filtering disputes out of `LivingWitnessCount` would make a disagreement *reduce* the witness count, so the request named *"report a disagreement"* would get harder the moment one happened. Somebody was there and said something.
- **One person is one account.** A crew standing still ticks every fifteen ticks, so `AddAccount` refuses any witness already on the record **including the one who filed the fact** - otherwise the filer corroborates themselves, the list grows without bound, and a Testify route pays out on one person's word repeated. `IsValidFor` asserts it again as a backstop.
- **THREE PLACES A NEW SAVED FIELD COULD HAVE ROTTED SILENTLY.** `EvidenceAnalysisReport` freezes a snapshot and `IsValidFor` compares it to the live record via `SameSnapshot`. Threaded through all three: `SameSnapshot` gains `SameAccounts` (else a frozen report compares **equal** to a record that has since gained a dispute), `SnapshotCopy` deep-copies each account (else the report **aliases** the live list), and `IsValidFor` validates each account and rejects duplicate speakers. **Accounts are compared in order**, because order-insensitive comparison would hide reordered testimony.
- **No schema version bump, deliberately.** `observationSchemaVersion` exists to distinguish booleans predating structured observations and its own comment forbids synthesizing rows from them. An old save has **no accounts and that is true of it**; empty needs no version to be honest.
- **Register guidance applied, three instructions.** *"Keep custody, casework, and interview goals reachable through vanilla prisoner controls"* - no prisoner mechanics touched; these are employed staff giving accounts. *"leave native social-fight logic intact and keep Rimrooms staff/case records separate"* - a dispute is a row on an evidence record, **no thought or mood is written**, so two crew who disagree do not start a social fight. *"Keep the company's evaluation based on actual pawn traits, skills, and relationships"* - nothing invents a reliability stat RimWorld does not have.
- **The event string was written AFTER the readout existed.** It tells the player the evidence readout names the accounts, so the readout had to name them first. A string promising a screen that does not exist is a lie with a translation key.
- **Stated plainly rather than implied: nothing resolves a dispute yet.** The interview workflow - `TODO.md` *"Add analyze/interview/compare/review workflows"*, where grep confirms analysis ships and interview does not - is the next checkpoint. The request that asks for two accounts is satisfied by the accounts existing, not by resolving them, so this is not a dead end.
- **Twenty-third proof, 29 claims, fault-planted six ways, caught 6 of 6.** Two of the six are the silent kind - a snapshot that stops comparing accounts, and a copy that aliases the live list - and neither changes observable behaviour until a report is frozen and the record then gains a dispute.
- Build 0.12.25-dev, **174 C# files, 86 package files**, **0 warnings, 0 errors**. Assembly `23D01F47CBECAB5D810E3FB3418D17AAFD0F3FF0D3A8903B1398D8CB30736DBE`, identical across two clean rebuilds. Nine checkers pass, **twenty-three** proofs exit zero. **No game was launched, so nobody has ever disagreed about anything in this mod.**

---

## Completed sessions""")

print('ledger written for 0.12.25-dev')
