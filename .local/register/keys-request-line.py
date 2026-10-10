# -*- coding: utf-8 -*-
"""Keyed strings for the request line reaching the player, 0.12.11-dev.

Surface conventions, from tools/check-display-style.py:
  * letter label  -- short, no terminal punctuation (Core: 2% carry any)
  * letter body   -- prose, ends with a full stop (Core: 62%)
  * button text   -- a command the player picks, no full stop
  * ledger reason -- a noun phrase, no full stop, matching RR_Ledger_SurveyPayment
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6',
                    'Languages', 'English', 'Keyed', 'RR_Requests.xml')

BLOCK = u"""
  <!-- ==================================================================================
       The request line reaching the player, 0.12.11-dev.

       The seven requests above shipped in 0.11.1 and 0.11.2 and nothing read them. These are
       the strings for the surface that presents one: the pane, the two letters, the ledger
       reasons and the refusals.

       No string here mentions a deadline, a window or running out of time. There is no field
       to put one in, and there must be no wording that implies one.
       ================================================================================== -->

  <!-- The pane -->
  <RR_Requests_Heading>Corporation requests</RR_Requests_Heading>
  <RR_Requests_NoContact>Nobody from the parent corporation has been in touch. Until they have, there is no work coming in and nothing here to read. Whatever this branch does next, it decides on its own.</RR_Requests_NoContact>
  <RR_Requests_NoneOpen>Nothing is being asked for at the moment.</RR_Requests_NoneOpen>
  <RR_Requests_PastTheHinge>The company has stopped naming things. It asked for six, it asked where this branch intended to take it, and it got an answer. What comes next comes from what this branch has become.</RR_Requests_PastTheHinge>
  <RR_Requests_DefMissing>A request this branch was working on is no longer installed: {0}. The record stays until it is cancelled.</RR_Requests_DefMissing>
  <RR_Requests_OpenRow>{0} ({1})</RR_Requests_OpenRow>
  <RR_Requests_StatusOffered>on the table</RR_Requests_StatusOffered>
  <RR_Requests_StatusAccepted>accepted</RR_Requests_StatusAccepted>
  <RR_Requests_Payment>Payment on completion: ${0}</RR_Requests_Payment>
  <RR_Requests_Bonus>Bonus if nobody on the books when this was accepted is lost: ${0}</RR_Requests_Bonus>
  <RR_Requests_NoDeadline>There is no time limit. The company waits.</RR_Requests_NoDeadline>

  <!-- Routes. Every authored route is drawn whether or not the branch can take it yet, per the
       owner decision "filter picks the family, card never shrinks". -->
  <RR_Requests_RoutesHeading>Ways through this. Any one of them finishes it.</RR_Requests_RoutesHeading>
  <RR_Requests_RouteRow>{0} {1}</RR_Requests_RouteRow>
  <RR_Requests_RouteRowDerived>{0} {1} (open to this branch because of what it has built)</RR_Requests_RouteRowDerived>
  <RR_Requests_RouteDesc>    {0}</RR_Requests_RouteDesc>
  <RR_Requests_RouteDone>[done]</RR_Requests_RouteDone>
  <RR_Requests_RouteOpen>[   ]</RR_Requests_RouteOpen>
  <RR_Requests_RouteUnrecorded>an unrecorded route</RR_Requests_RouteUnrecorded>

  <!-- The two verbs -->
  <RR_Requests_Accept>Accept this request</RR_Requests_Accept>
  <RR_Requests_Cancel>Turn it down</RR_Requests_Cancel>

  <!-- History -->
  <RR_Requests_HistoryHeading>Already dealt with</RR_Requests_HistoryHeading>
  <RR_Requests_HistoryCompleted>{0} - finished by {1}, day {2}.</RR_Requests_HistoryCompleted>
  <RR_Requests_HistoryCompletedWithBonus>{0} - finished by {1}, day {2}. The bonus was paid: everybody came back.</RR_Requests_HistoryCompletedWithBonus>
  <RR_Requests_HistoryCancelled>{0} - turned down.</RR_Requests_HistoryCancelled>

  <!-- Refusals -->
  <RR_Request_NotOffered>The corporation has not asked for that.</RR_Request_NotOffered>
  <RR_Request_AlreadyResolved>That request has already been dealt with.</RR_Request_AlreadyResolved>

  <!-- Letters. Label short and unpunctuated, body prose. -->
  <RR_Letter_RequestOfferedTitle>Request: {0}</RR_Letter_RequestOfferedTitle>
  <RR_Letter_RequestOfferedBody>{0}

There is no date on this and there will not be one. Open the Operations tab, look at the contracts pane, and take it on when {1} is ready to.</RR_Letter_RequestOfferedBody>
  <RR_Letter_RequestCompletedTitle>Request met: {0}</RR_Letter_RequestCompletedTitle>
  <RR_Letter_RequestCompletedBody>The company has what it asked for. {0} was finished by {1}, and ${2} has gone into the account.</RR_Letter_RequestCompletedBody>

  <!-- Ledger reasons. Noun phrases, matching RR_Ledger_SurveyPayment. -->
  <RR_Ledger_RequestPayment>Corporation request met</RR_Ledger_RequestPayment>
  <RR_Ledger_RequestBonus>Request met with the whole crew intact</RR_Ledger_RequestBonus>

  <!-- Activity feed -->
  <RR_Event_RequestOffered>The corporation has asked for something: {0}.</RR_Event_RequestOffered>
  <RR_Event_RequestAccepted>The branch took on the corporation's request.</RR_Event_RequestAccepted>
  <RR_Event_RequestCancelled>The branch turned the corporation's request down. Nothing follows from it.</RR_Event_RequestCancelled>
  <RR_Event_RequestCompleted>A corporation request was met: {0}.</RR_Event_RequestCompleted>
  <RR_Event_RequestBonus>The bonus was paid, ${0}. Everybody on the books when the work was taken on is still here.</RR_Event_RequestBonus>
"""

s = io.open(PATH, encoding='utf-8').read()
anchor = u'\n</LanguageData>'
assert anchor in s, 'closing tag not found'
assert u'RR_Requests_Heading' not in s, 'block already applied'
s = s.replace(anchor, BLOCK + anchor, 1)
io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('request-line keyed strings added')
