# -*- coding: utf-8 -*-
"""Stage five strings. A refusal the player cannot read is a silent failure."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Portals.xml")

text = io.open(KEYED, encoding="utf-8-sig").read()
ANCHOR = "  <!-- Owner direction, 2026-09-30: \"and then u lose them forever but maybe allow minify move\"."

NEW = u"""  <!-- Letting a place go, so a machine gate can aim deeper. Owner direction, 2026-09-30:
       "yeah so if the player discovers and goes through a natural gate how do they turn them off
       to use the machine gates for more controll and aiming deeper?" and "get 5 natural gates u
       cant use a machine gate". The chosen shape was an Operations held-places list.

       A natural gate is permanently open and is never closed. What is released is the space
       behind it, which regenerates from its own seed when it is opened again - the same rooms in
       the same shape, and none of the contents. -->
  <RR_UI_Places>Places</RR_UI_Places>
  <RR_Release_Heading>Places held open</RR_Release_Heading>
  <RR_Release_Budget>Holding {0} of {1}. A Backrooms level costs a loaded map exactly as a colony does, and the limit is the maximum number of colonies set in Options.</RR_Release_Budget>
  <RR_Release_Explanation>Releasing a place does not close the way to it. The door stays permanently open and remembers where it led, and the place can be opened again from that door. What is lost is everything left inside: the space is found again as it is, not as you left it.</RR_Release_Explanation>
  <RR_Release_ColonyRow>Colony: {0} — cannot be released here.</RR_Release_ColonyRow>
  <RR_Release_NoneHeld>This company is holding no Backrooms levels open.</RR_Release_NoneHeld>
  <RR_Release_PlaceRow>{0}, depth {1}</RR_Release_PlaceRow>
  <RR_Release_LeftBehind>{0} item(s) would be left behind.</RR_Release_LeftBehind>
  <RR_Release_Blocked>Cannot release: {0}</RR_Release_Blocked>
  <RR_Release_Button>Release this place</RR_Release_Button>
  <RR_Release_ConfirmTitle>Release a place</RR_Release_ConfirmTitle>
  <RR_Release_Confirm>Stop holding {0} open?\\n\\nThe way in stays permanently open and remembers where it led, so you can open this place again from the same door. Everything left inside will be gone: {1} item(s), and anything your people built there.</RR_Release_Confirm>
  <RR_Release_Done>{0} is no longer held open. Holding {1}.</RR_Release_Done>
  <RR_Release_Failed>{0} could not be released: {1}</RR_Release_Failed>
  <RR_Release_ShelvedHeading>Released, and reachable again from the door that found them</RR_Release_ShelvedHeading>
  <RR_Release_ShelvedRow>{0}, depth {1}</RR_Release_ShelvedRow>
  <RR_Release_ShelvedHint>Select the door that led to one of these and use Open this place again.</RR_Release_ShelvedHint>
  <RR_Release_ReopenLabel>Open this place again</RR_Release_ReopenLabel>
  <RR_Release_ReopenDesc>Hold this place open again. It will be the same rooms in the same shape, and none of what was left inside. Holding {0}.</RR_Release_ReopenDesc>
  <RR_Release_ReopenNoRoomDesc>This company is already holding open as many places as it can ({0}). Release one from the Places pane in Operations first.</RR_Release_ReopenNoRoomDesc>

  <!-- The release refusals. Each names itself, because a player who pressed Release and saw
       nothing happen has been told nothing. -->
  <RR_Release_Inactive>this branch is not operating</RR_Release_Inactive>
  <RR_Release_UnknownPlace>that place is not on this company's records</RR_Release_UnknownPlace>
  <RR_Release_NotHeldOpen>that place is not being held open</RR_Release_NotHeldOpen>
  <RR_Release_Headquarters>that is this company's headquarters</RR_Release_Headquarters>
  <RR_Release_CrewInside>somebody is still inside</RR_Release_CrewInside>
  <RR_Release_CrossingInFlight>somebody is part-way through a way into it</RR_Release_CrossingInFlight>

""" + ANCHOR

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(text.replace(ANCHOR, NEW, 1))
print("stage five strings written")
