# -*- coding: utf-8 -*-
"""The strings a player reads about a marker, written to the shape of each surface."""
import io
import os

MOD = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6')
KEYED = os.path.join(MOD, 'Languages', 'English', 'Keyed')

# Surfaces, per Core's own measured practice:
#   gizmo-label      short, no full stop
#   gizmo-desc       prose, ends a sentence (Core: 93%)
#   float-menu row   a thing you pick, no full stop (Core: 7%)
#   inspect line     terse, no trailing full stop
strings = u"""<?xml version="1.0" encoding="utf-8"?>
<LanguageData>

  <!-- Route markers. A glow pod a crew has designated, and the colour is what it means. -->

  <RR_Marker_Designate>Mark this pod</RR_Marker_Designate>
  <RR_Marker_Change>Change what it marks</RR_Marker_Change>
  <RR_Marker_DesignateDesc>Designate this glow pod as a route marker and choose what it means. The colour of its light is the meaning, so a crew can read it from the far end of a corridor without stopping.\\n\\nA designated marker stops ageing: an undesignated pod dies after about twenty days, and a way home that expires is not a way home.\\n\\nThere is no limit on how many you place.</RR_Marker_DesignateDesc>
  <RR_Marker_Clear>Stop marking</RR_Marker_Clear>
  <RR_Marker_ClearDesc>Return this pod to an ordinary glow pod. Its light goes back to its own colour and it begins ageing again.</RR_Marker_ClearDesc>
  <RR_Marker_NoTypes>No marker types loaded</RR_Marker_NoTypes>

  <RR_Marker_Label>{0} ({1})</RR_Marker_Label>
  <RR_Marker_Inspect>Marking: {0}</RR_Marker_Inspect>
  <RR_Marker_InspectRoom>Recorded junction: room {0}</RR_Marker_InspectRoom>
  <RR_Marker_Mismatch>This marker still records room {0}, and it is no longer in that room</RR_Marker_Mismatch>
  <RR_Marker_RepeatedLabel>Room {0} again?</RR_Marker_RepeatedLabel>

</LanguageData>
"""

path = os.path.join(KEYED, 'RR_Markers.xml')
io.open(path, 'w', encoding='utf-8', newline='').write(strings)
print('  wrote %s' % path)

# The unmarked-corridor warning still told the player to place a survey tag.
p = os.path.join(KEYED, 'RR_FieldAndThreats.xml')
text = io.open(p, encoding='utf-8-sig').read()
old = (u'<RR_Event_CorridorUnmarked>The corridor seems to repeat, but there is no numbered '
       u'reference at room {0}. Place a survey tag at that known junction, then approach again '
       u'to compare the route.</RR_Event_CorridorUnmarked>')
new = (u'<RR_Event_CorridorUnmarked>The corridor seems to repeat, and there is nothing marking '
       u'room {0}. Set a glow pod down at that junction and mark it as the route home, then '
       u'come back and compare.</RR_Event_CorridorUnmarked>')
assert old in text
text = text.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(text)
print('  rewrote the unmarked-corridor warning')

# Procurement: company-issue marker pods.
p = os.path.join(MOD, 'Defs', 'RimroomsProcurementCatalogDefs', 'RR_ProcurementCatalog.xml')
text = io.open(p, encoding='utf-8-sig').read()
entry = u"""  <RimroomsAsyncIndustries.Procurement.RimroomsProcurementCatalogDef>
    <defName>RR_Procurement_MarkerPods</defName>
    <label>Glow pods</label>
    <description>Live glow pods, crated. The company buys them from insect-hive salvagers by the pallet because a branch that cannot mark its own way back out files a great many more casualty reports.\\n\\nThey arrive packed for installation, and there is no limit on how many a branch may hold.</description>
    <thingDefName>GlowPod</thingDefName>
    <unitPriceUsd>4000</unitPriceUsd>
    <dispatchDelayTicks>60000</dispatchDelayTicks>
    <leadTimeTicks>120000</leadTimeTicks>
    <maxOrderQuantity>500</maxOrderQuantity>
  </RimroomsAsyncIndustries.Procurement.RimroomsProcurementCatalogDef>
"""
anchor = u'  <RimroomsAsyncIndustries.Procurement.RimroomsProcurementCatalogDef>\n    <defName>RR_Procurement_Steel</defName>'
assert anchor in text
text = text.replace(anchor, entry + anchor, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(text)
print('  added the marker-pod catalogue entry')
