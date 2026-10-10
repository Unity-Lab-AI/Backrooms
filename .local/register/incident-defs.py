# -*- coding: utf-8 -*-
"""The mod's first IncidentDefs, their keyed strings, and the package manifest."""
import io
import json
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6')

# --------------------------------------------------------------------------- the defs
defs_dir = os.path.join(MOD, 'Defs', 'IncidentDefs')
if not os.path.isdir(defs_dir):
    os.makedirs(defs_dir)

incidents = u"""﻿<?xml version="1.0" encoding="utf-8"?>
<Defs>

  <!-- ==================================================================================== -->
  <!-- THE MOD'S FIRST INCIDENTS                                                            -->
  <!--                                                                                      -->
  <!-- Owner decision at the storyteller fork, verbatim: "Both - guaranteed floor,           -->
  <!-- storyteller flavour". Until these, EVERY event in this mod fired from its own         -->
  <!-- component tick, so whichever storyteller the player chose had never heard of it.      -->
  <!--                                                                                      -->
  <!-- There is deliberately NO StorytellerDef. It is an exclusive slot the player would     -->
  <!-- have to give up Cassandra or Randy for, and it needs portrait art the no-new-art      -->
  <!-- rule forbids. The part of a storyteller that behaves like a director is the worker's  -->
  <!-- CanFireNowSub, and that is ours without owning the slot.                              -->
  <!--                                                                                      -->
  <!-- What is NOT here, on purpose: the clean-up team, because a guarantee must not be      -->
  <!-- subject to the two questions a storyteller asks; incursion, because invariant 53      -->
  <!-- keeps exactly one door into that exception; and anything inside a coordinate,         -->
  <!-- because what happens down there is paced by arrival and depth.                        -->
  <!--                                                                                      -->
  <!-- Both are Core-only and carry no MayRequire. Both are Misc rather than a threat        -->
  <!-- category: neither damages a pawn, destroys a thing or blocks a route.                 -->
  <!-- ==================================================================================== -->

  <IncidentDef>
    <defName>RR_Incident_ThresholdBleed</defName>
    <label>threshold bleed</label>
    <category>Misc</category>
    <targetTags>
      <li>Map_PlayerHome</li>
    </targetTags>
    <workerClass>RimroomsAsyncIndustries.Incidents.IncidentWorker_RimroomsThresholdBleed</workerClass>
    <baseChance>0.8</baseChance>
    <minRefireDays>5</minRefireDays>
    <letterDef>NeutralEvent</letterDef>
    <letterLabel>Threshold bleed</letterLabel>
    <letterText>Something came out the near side.

The gate is shut. The room it stands in is not quite as it was: the wrongness that lives behind the threshold does not always stay behind it, and a branch that works a hole in the world is a branch that occasionally finds the hole working back.

It is the same handful of things the space does when you are standing in it, and the same answers work here. Nothing was destroyed and nobody was hurt.</letterText>
  </IncidentDef>

  <IncidentDef>
    <defName>RR_Incident_CorporationDelivery</defName>
    <label>unsolicited delivery</label>
    <category>Misc</category>
    <targetTags>
      <li>Map_PlayerHome</li>
    </targetTags>
    <workerClass>RimroomsAsyncIndustries.Incidents.IncidentWorker_RimroomsCorporationDelivery</workerClass>
    <baseChance>0.5</baseChance>
    <minRefireDays>15</minRefireDays>
    <letterDef>PositiveEvent</letterDef>
    <letterLabel>Unsolicited delivery</letterLabel>
    <letterText>A crate nobody ordered.

The parent corporation does not do this out of kindness. It has money in this branch, the branch works better with supplies in it than without, and the arithmetic on that is not complicated enough to need approval from anybody.

There is no invoice and there is no note. There rarely is.</letterText>
  </IncidentDef>

</Defs>
"""
p = os.path.join(defs_dir, 'RR_Incidents.xml')
io.open(p, 'w', encoding='utf-8', newline='').write(incidents)
ET.parse(p)
print('wrote and parsed %s' % os.path.relpath(p, REPO))

# --------------------------------------------------------------------------- keyed strings
p = os.path.join(MOD, 'Languages', 'English', 'Keyed', 'RR_Requests.xml')
s = io.open(p, encoding='utf-8-sig').read()
block = u"""  <RR_Event_ThresholdBleed>The space came out the near side. Whatever it did, it did in the room a gate stands in.</RR_Event_ThresholdBleed>
  <RR_Event_CorporationDelivery>The parent corporation sent supplies nobody asked for. It protects what it has money in.</RR_Event_CorporationDelivery>
"""
anchor = u'  <RR_Event_FacilityRelief>'
assert anchor in s, 'keyed anchor missing'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
ET.parse(p)
print('keyed strings added and parsed')

# --------------------------------------------------------------------------- manifest
p = os.path.join(REPO, 'tools', 'package-files.json')
manifest = json.load(io.open(p, encoding='utf-8-sig'))
entry = '1.6/Defs/IncidentDefs/RR_Incidents.xml'
assert entry not in manifest['files'], 'already listed'
manifest['files'].append(entry)
manifest['files'].sort()
io.open(p, 'w', encoding='utf-8', newline='').write(
    u'﻿' + json.dumps(manifest, indent=2, ensure_ascii=False) + u'\n')
print('manifest now lists %d files' % len(manifest['files']))
