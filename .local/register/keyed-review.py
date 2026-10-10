# -*- coding: utf-8 -*-
"""Player-facing text for the review workflow.

Every refusal `ReviewAnalysis` can return gets a string. **A refusal with no string prints a raw
key at the player**, and a control that refuses in silence is how somebody concludes a button is
broken -- which cost the owner an afternoon on the gate at 0.12.73-dev.

Written as a file: the prose carries apostrophes, and that trap has been hit thirteen times.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED_DIR = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                         "English", "Keyed")
TARGET = os.path.join(KEYED_DIR, "RR_Investigation.xml")

ADDITION = u"""
  <!-- Review: the fourth workflow. A second person signs a finished report off, or returns it. -->

  <RR_UI_ReviewAwaiting>This report has not been signed off. A second pair of eyes decides whether the branch stands behind it.</RR_UI_ReviewAwaiting>
  <RR_UI_ReviewPrompt>{0} can review the report.</RR_UI_ReviewPrompt>
  <RR_UI_SignOffReport>Review the report</RR_UI_SignOffReport>
  <RR_UI_ReviewEndorsed>Signed off by {0} on day {1}. The branch stands behind this report.</RR_UI_ReviewEndorsed>
  <RR_UI_ReviewReturned>Returned by {0} on day {1}. There was not enough on the record to stand behind.</RR_UI_ReviewReturned>
  <RR_UI_ReviewerUnknown>a reviewer no longer on the payroll</RR_UI_ReviewerUnknown>
  <RR_UI_NextReview>Have somebody review the finished report. The branch does not act on a finding nobody has checked.</RR_UI_NextReview>
  <RR_Review_Endorsed>{0} signed the report off.</RR_Review_Endorsed>
  <RR_Review_Returned>{0} returned the report. There was not enough on it.</RR_Review_Returned>
  <RR_Review_NoReviewer>Nobody on the payroll can review this. A reviewer needs Intellectual {0} and cannot be the analyst who wrote it.</RR_Review_NoReviewer>
  <RR_Review_DisputesOutstanding>{0} accounts on this record are still disputed. Settle them first; a sign-off on a contradiction is worth nothing.</RR_Review_DisputesOutstanding>
  <RR_Review_Inactive>The company cannot act on this branch.</RR_Review_Inactive>
  <RR_Review_RecordUnavailable>That record is not on the branch books.</RR_Review_RecordUnavailable>
  <RR_Review_NotAnalysed>There is nothing to review until the analysis is finished.</RR_Review_NotAnalysed>
  <RR_Review_NoReport>That record carries no analysis report.</RR_Review_NoReport>
  <RR_Review_AlreadyReviewed>This report has already been signed off.</RR_Review_AlreadyReviewed>
  <RR_Review_ReviewerUnavailable>That reviewer cannot work right now.</RR_Review_ReviewerUnavailable>
  <RR_Review_ReviewerIsAnalyst>The analyst cannot review their own report. That is the whole point of a review.</RR_Review_ReviewerIsAnalyst>
  <RR_Review_ReviewerUnskilled>That reviewer does not have the Intellectual skill to read the report critically.</RR_Review_ReviewerUnskilled>
  <RR_Event_ReviewEndorsed>{0} reviewed a finished report and the branch stands behind it.</RR_Event_ReviewEndorsed>
  <RR_Event_ReviewReturned>{0} reviewed a finished report and returned it. There was not enough on the record.</RR_Event_ReviewReturned>
"""

if not os.path.isfile(TARGET):
    # No investigation keyed file: fall back to the requests file, which already carries the
    # interview strings this sits beside.
    TARGET = os.path.join(KEYED_DIR, "RR_Requests.xml")

text = io.open(TARGET, encoding="utf-8-sig").read()
CLOSE = u"</LanguageData>"
if text.count(CLOSE) != 1:
    print("ANCHOR PROBLEM in %s: %d" % (os.path.basename(TARGET), text.count(CLOSE)))
    raise SystemExit(1)
io.open(TARGET, "w", encoding="utf-8-sig", newline="").write(
    text.replace(CLOSE, ADDITION + CLOSE, 1))

after = io.open(TARGET, encoding="utf-8-sig").read()

# Every refusal key the service can return must exist, read OUT OF THE SOURCE rather than from a
# list typed here -- a hand-kept list is a second derivation that goes stale.
service = io.open(os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company",
                              "EvidenceReview.cs"), encoding="utf-8-sig").read()
keys = set(re.findall(r'"(RR_(?:Review|Event_Review)[A-Za-z_]*)"', service))
missing = sorted(key for key in keys if (u"<%s>" % key) not in after)

failures = []
if missing:
    failures.append("keys the service returns with no string: %s" % ", ".join(missing))
for ui_key in ("RR_UI_ReviewAwaiting", "RR_UI_ReviewPrompt", "RR_UI_SignOffReport",
               "RR_UI_ReviewEndorsed", "RR_UI_ReviewReturned", "RR_UI_NextReview",
               "RR_UI_ReviewerUnknown"):
    if (u"<%s>" % ui_key) not in after:
        failures.append("%s is missing" % ui_key)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("review strings written to %s; %d service keys all covered"
      % (os.path.basename(TARGET), len(keys)))
