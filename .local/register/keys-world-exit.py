# -*- coding: utf-8 -*-
"""Keyed strings for the way out onto the world map, 0.12.21-dev.

Surface conventions, from tools/check-display-style.py:
  * a command label  -- a thing the player picks, no full stop
  * a command tooltip / description -- prose, ends a sentence
  * a refusal -- prose, ends a sentence, says what to do about it where there is something
  * an activity-feed event -- prose, ends a sentence

The vocabulary rule from 0.10.2 applies: a plain door is a "door", never a "doorway"; the
far-side arrival point is a "threshold". None of these strings may imply a clock.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6',
                    'Languages', 'English', 'Keyed', 'RR_Portals.xml')

BLOCK = u"""
  <!-- ==================================================================================
       A way out onto the world map, 0.12.21-dev.

       A found way out used to need a door the player had already marked on a map the branch
       already owned. With nothing marked the way out became a way deeper instead, so a branch
       with no marked door could never get out at all.

       Now it leads to a world tile the branch does not hold. Under the five-map cap the tile is
       claimed and the crew walks onto a new map; at or over the cap they form a caravan.
       ================================================================================== -->

  <RR_WorldExit_LeaveLabel>Walk out through this door</RR_WorldExit_LeaveLabel>
  <RR_WorldExit_LeaveDesc>Somewhere on the other side of this door is open sky. Whoever is standing here goes through, and comes out somewhere on the map that is not where they started.\\n\\nIf the company can take on another place, that is where they arrive and it becomes yours. If it is already running as many places as it can, they come out as a caravan and have to make their own way from there.</RR_WorldExit_LeaveDesc>

  <RR_WorldExit_NotHere>Nothing about this door leads outside. A way out has to be found by surveying one, and this is not one of them.</RR_WorldExit_NotHere>
  <RR_WorldExit_DoorUnavailable>That door is not standing where it was.</RR_WorldExit_DoorUnavailable>
  <RR_WorldExit_DestinationGone>Whatever was on the other side is no longer anywhere on the map. Nobody has moved.</RR_WorldExit_DestinationGone>
  <RR_WorldExit_NoAnchorTile>The company has nowhere on the map to reckon from, so there is no telling where this comes out.</RR_WorldExit_NoAnchorTile>
  <RR_WorldExit_NoTileFound>The survey found the way out but nowhere for it to lead. Nothing on the far side would hold anybody.</RR_WorldExit_NoTileFound>
  <RR_WorldExit_NobodyHere>Nobody is standing at this door. Bring whoever is leaving to it first.</RR_WorldExit_NobodyHere>
  <RR_WorldExit_CouldNotClaim>The place on the far side could not be taken on. Nobody has moved, and the door is still there.</RR_WorldExit_CouldNotClaim>
  <RR_WorldExit_NoArrivalCell>There is nowhere to stand on the far side. Nobody has moved.</RR_WorldExit_NoArrivalCell>
  <RR_WorldExit_NobodyMoved>Nobody made it through, and everybody is back where they were standing.</RR_WorldExit_NobodyMoved>
  <RR_WorldExit_CouldNotForm>They could not set out from there. Nobody has moved.</RR_WorldExit_CouldNotForm>

  <RR_Event_WorldExitFound>A survey found a way out that does not lead back to anywhere the company holds. It comes out somewhere on the map instead.</RR_Event_WorldExitFound>
  <RR_Event_WorldExitUsed>{0} went out through a door and came out under open sky.</RR_Event_WorldExitUsed>
  <RR_Event_WorldExitClaimed>The company has taken on {0}. Whoever walked out is standing in it.</RR_Event_WorldExitClaimed>
  <RR_Event_WorldExitCaravan>The company is already running as many places as it can, so {0} set out on foot instead.</RR_Event_WorldExitCaravan>
"""

s = io.open(PATH, encoding='utf-8-sig').read()
anchor = u'\n</LanguageData>'
assert anchor in s, 'closing tag not found'
assert u'RR_WorldExit_LeaveLabel' not in s, 'block already applied'
io.open(PATH, 'w', encoding='utf-8-sig', newline='').write(s.replace(anchor, BLOCK + anchor, 1))
print('world-exit keyed strings added')
