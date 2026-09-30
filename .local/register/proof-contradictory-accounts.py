# -*- coding: utf-8 -*-
"""Assert a second crew member's account is filed rather than discarded, and that a dispute counts.

The property this exists for
---------------------------
The prep material asks for it in these words:

    "return with contradictory accounts"                  -- UNIVERSE_ADAPTATION.md
    "return with contradictory accounts that open a case" -- SYSTEMS_CATALOG.md

and `docs/CAMPAIGN_CHART.md` line 226 -- the authority, which beats any prep document -- asks
tutorial request 5 for:

    | 5 | **Report a disagreement** | 2 | distortion logs | analyse a distortion record *
      two crew accounts of the same room |

**Two crew accounts of the same room were impossible.** `EvidenceObservationRecord.StableId` is
per-room only for a room survey:

    return observationKind == EvidenceObservationKinds.RoomSurvey
        ? evidenceId + ":observation:" + observationKind + ":" + observedRoom
        : evidenceId + ":observation:" + observationKind;

so one evidence record held exactly one route mismatch, one recorder gap and one entity sighting --
one witness each. `RecordEncounterObservations` meanwhile loops over **every** present, non-downed
crew member, and files the mismatch and the gap with the *same* witness. So per record,
`LivingWitnessCount("distortion")` could return at most **one**, and the second crew member's
account was either silently merged (identical facts returned `Existing()`) or silently thrown away
(different facts returned `RR_Company_ReceiptMismatch`) -- and the site tick ignores the result
either way. `RR_Request_ReportADisagreement` asks for **two**, so it was satisfiable only across two
separate coordinates, never by a disagreement.

Four things have to stay true:

  * **NOTHING IS DISCARDED.** Agreement is corroboration, disagreement is a dispute, and both are
    saved. The old refusal must not come back.

  * **A DISPUTE COUNTS AS TESTIMONY.** Somebody was there and said something. A company that drops
    testimony because it is inconvenient is not what this campaign is about, and dropping it would
    also make a disagreement *reduce* the witness count, which is backwards.

  * **ONE PERSON IS ONE ACCOUNT.** A crew standing still ticks every fifteen ticks. Without a
    duplicate guard the account list grows without bound and `LivingWitnessCount` inflates, which
    would pay out a request on one person's word repeated.

  * **THE FROZEN REPORT MUST NOTICE.** `EvidenceAnalysisReport` snapshots observations, and
    `IsValidFor` compares the snapshot against the live record with `SameSnapshot`. A new saved
    field that those two do not know about makes a report compare equal to a record that has since
    gained a dispute -- silently.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    """This change is explained at length in the files it changes, and those comments quote the
    refusal key and the chart line repeatedly. A naive search would be satisfied by prose."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unbalanced body for %r" % signature)


observations = strip_cs_comments(read(os.path.join(SRC, "Company", "EvidenceObservations.cs")))
line = strip_cs_comments(read(os.path.join(SRC, "Company", "RequestLine.cs")))
site = strip_cs_comments(read(os.path.join(SRC, "Threats", "FirstSliceSiteComponent.cs")))
pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsEvidence.cs")))
requests = read(os.path.join(MOD, "Defs", "RimroomsRequestDefs", "RR_Requests.xml"))
investigation_keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Investigation.xml"))
field_keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_FieldAndThreats.xml"))

print("")
print("proof: a second crew account is filed, a dispute counts, and one person is one account")
print("")

# ------------------------------------------------------------------ 1. nothing is discarded
print("1. the second account is filed instead of refused")
record_body = body_of(observations, "public CompanyActionResult RecordFieldObservation(")
check("the prior-observation branch no longer refuses as a receipt mismatch",
      "RR_Company_ReceiptMismatch" not in record_body,
      "-- that refusal WAS the discard, and the caller ignores results")
check("an account is filed whether or not it agrees",
      "prior.AddAccount(" in record_body and "SameFact(" in record_body,
      "-- SameFact decides agrees, not whether anything is recorded")
check("agreement is passed through rather than assumed",
      re.search(r"bool\s+agrees\s*=\s*prior\.SameFact\(", record_body) is not None)

# ------------------------------------------------------------------ 2. a dispute is testimony
print("")
print("2. a dispute counts as an account")
witness_body = body_of(line, "private int LivingWitnessCount(")
check("the witness count reads the accounts list",
      "observation.Accounts" in witness_body,
      "-- without this a second crew member is invisible to a Testify route")
check("it does NOT filter accounts by agreement",
      "Agrees" not in witness_body,
      "-- a disagreement would otherwise REDUCE the witness count, which is backwards")
check("an account witness is still checked alive and employed",
      "speaker.Dead" in witness_body and "IsEmployedPawn(speaker)" in witness_body,
      "-- the route asks for LIVING employed witnesses, and a dead one cannot speak")
check("the filed witness is still counted",
      "witnesses.Add(observation.WitnessLoadId)" in witness_body)
check("a disputed observation is recognisable",
      "public bool Disputed" in observations)

# ------------------------------------------------------------------ 3. one person, one account
print("")
print("3. one person is one account")
add_body = body_of(observations, "internal bool AddAccount(")
check("a witness already on the record is refused",
      "foreach (string existing in WitnessLoadIds)" in add_body,
      "-- a crew standing still ticks every fifteen ticks")
check("the duplicate check includes the witness who FILED the fact",
      "witnessLoadId" in body_of(observations, "internal IEnumerable<string> WitnessLoadIds"),
      "-- otherwise the filer corroborates themselves and one person counts twice")
check("a null witness or an unset tick is refused",
      "accountWitness == null" in add_body and "atTick < 0" in add_body)
check("duplicate speakers make the record invalid",
      "Distinct(StringComparer.Ordinal).Count() != speakers.Count" in
      body_of(observations, "internal bool IsValidFor(string evidenceId"),
      "-- validity is the backstop for the guard above")

# ------------------------------------------------------------------ 4. the frozen report notices
print("")
print("4. the analysis snapshot cannot go stale silently")
check("SameSnapshot compares accounts",
      "SameAccounts(other)" in body_of(observations, "internal bool SameSnapshot(EvidenceObservationRecord other)"),
      "-- a report would otherwise equal a record that has since gained a dispute")
check("accounts are compared in order",
      "mine.Count != theirs.Count" in body_of(observations, "private bool SameAccounts("),
      "-- order-insensitive comparison would hide reordered testimony")
check("SnapshotCopy deep-copies each account",
      "a.SnapshotCopy()" in body_of(observations, "internal EvidenceObservationRecord SnapshotCopy()"),
      "-- aliasing the live list means the frozen report keeps changing")
check("each account is validated as strictly as the fact it attaches to",
      "!a.IsValidFor(rooms)" in body_of(observations, "internal bool IsValidFor(string evidenceId"))

# ------------------------------------------------------------------ 5. saved, and old saves load
print("")
print("5. it saves, and a save without accounts is still true")
check("accounts are saved deeply",
      'Scribe_Collections.Look(ref accounts, "rr_accounts", LookMode.Deep)' in observations,
      "-- LookMode.Value would save nothing; these are IExposable rows")
check("a save with no accounts loads as an empty list, not null",
      "accounts == null" in observations and "accounts = new List<WitnessAccountRecord>()" in observations)
check("the observation schema version was NOT bumped",
      "CurrentObservationSchemaVersion = 1" in read(os.path.join(SRC, "Company", "CampaignRecords.cs")),
      "-- that version distinguishes booleans predating structured observations; an empty account "
      "list needs no such distinction, because empty is the honest answer for an old save")
check("the account row is itself saveable",
      "public sealed class WitnessAccountRecord : IExposable" in observations)

# ------------------------------------------------------------------ 6. the player is told
print("")
print("6. the player can see it, which is the difference from discarding it")
check("the site tick notes a newly opened disagreement",
      '"RR_Event_AccountsDisagree"' in site)
check("it compares the dispute state across the recording call",
      "disputedBefore" in body_of(site, "private void RecordEncounterObservations("),
      "-- the result is ignored here, so before-and-after is the only honest reading")
check("the note fires once rather than every fifteen ticks",
      "!disputedBefore && HasDisputedAccount(record)" in site)
check("the evidence readout names every account",
      "observation.Accounts" in pane and "RR_UI_AccountAgrees" in pane and "RR_UI_AccountDisagrees" in pane,
      "-- the note tells the player the readout names them, so it has to")
for key in ("RR_UI_AccountAgrees", "RR_UI_AccountDisagrees"):
    check("%s is translated" % key, "<%s>" % key in investigation_keys)
check("RR_Event_AccountsDisagree is translated",
      "<RR_Event_AccountsDisagree>" in field_keys)

# ------------------------------------------------------------------ 7. the request it unblocks
print("")
print("7. the request the chart authorises is the one this reaches")
block = requests[requests.index("RR_Request_ReportADisagreement"):]
block = block[:block.index("</RimroomsAsyncIndustries.Company.RimroomsRequestDef>")]
check("request 5 still asks for two accounts of a distortion",
      "<kind>Testify</kind>" in block and "<logKind>distortion</logKind>" in block and
      "<count>2</count>" in block,
      "-- if this changes, the feature above is answering a question nobody asks")
check("a distortion observation is still what carries a distortion log",
      "EvidenceObservationKinds.RouteMismatch" in body_of(line, "private static bool ObservationCarries("),
      "-- the accounts hang off those observations")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a second account is filed, a dispute is testimony, and one person counts once")
