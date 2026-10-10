# -*- coding: utf-8 -*-
"""Async's starting research, and the Furniture & Knickknack Store start."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6')


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:60])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ roles: 5 was Async-only
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Scenario', 'RimroomsStartDef.cs')
sub(p,
    u'            if (roles == null || roles.Count != 5) { yield return "Async Industries requires five distinct starting roles."; }',
    u'            // Five was the Async Industries roster written as a rule for every start. The\n'
    u'            // Store opens with three ordinary people and the solo/group start with as few\n'
    u'            // as one, so the real rule is "at least one, and no more than the company\n'
    u'            // recognises". A start with no roles has nobody to assign work to.\n'
    u'            if (roles == null || roles.Count < 1 || roles.Count > 5)\n'
    u'            { yield return "A start needs between one and five distinct starting roles."; }')

# ------------------------------------------------------------------ Async starting research
p = os.path.join(MOD, 'Defs', 'RimroomsStartDefs', 'RR_Starts.xml')
sub(p, u"""         This one is the first slice and begins with nothing finished. -->
    <completedProjects />""",
u"""         **Corrected 2026-09-29 on owner direction.** This start listed NOTHING finished, which
         contradicted the direction it was written under: "Async industries starts with this tech
         research and other basic gate techs it needs to operate and begin researching and gate
         operations at basic levels". Owner's answer at the fork: all seven tier 0 roots, plus the
         gate ladder's first rung.

         So Async opens able to operate a gate properly and with a foot in the door on every
         branch, which is what an authorised branch of a company that has done this before would
         actually have. The Store and Solo/Group starts list nothing, and that difference is now
         real rather than a note.

         NOTE, chosen knowingly: RR_GateTelemetry puts PortalWindowTier at 1, which is the floor
         at which something may follow a crew out. Async is therefore exposed to incursion from
         the first opening. That is the cost of starting equipped and the owner took it. -->
    <completedProjects>
      <li>RR_GateTelemetry</li>
      <li>RR_Facilities_ReserveDiscipline</li>
      <li>RR_Fieldcraft_ReturnDrill</li>
      <li>RR_Measurement_SecondReading</li>
      <li>RR_Spatial_CoordinateAtlas</li>
      <li>RR_Entities_EarlyWarning</li>
      <li>RR_Logistics_StandingOrders</li>
      <li>RR_Commerce_NegotiatedTerms</li>
    </completedProjects>""")

# ------------------------------------------------------------------ the Store start def
store = u"""
  <!-- ==================================================================================== -->
  <!-- FURNITURE AND KNICKKNACK STORE                                                       -->
  <!--                                                                                      -->
  <!-- Contract: docs/SCENARIOS.md, the furniture_knickknack_store card. A 50x50 shop with   -->
  <!-- a sales floor, stockroom, office, staff room and a back room nobody uses, three       -->
  <!-- ordinary people, and no corporation.                                                  -->
  <!--                                                                                      -->
  <!-- beginsInCorporationContact is FALSE and completedProjects is EMPTY, and both of those  -->
  <!-- are the point. No clean-up team, no unsolicited courier, no research already done.     -->
  <!-- Owner: "the other two scenerios need special treatment in theri layout and starts".    -->
  <!-- Reaching contact is the achievement here, not the starting condition.                  -->
  <!--                                                                                      -->
  <!-- The threshold in the back room is an ordinary door, because that is exactly what a    -->
  <!-- gate is in this mod before anybody designates it. Nothing here claims a breach system  -->
  <!-- that does not exist; the shop simply has a door in the back that should not be there,  -->
  <!-- and what it becomes is the player's decision.                                          -->
  <!-- ==================================================================================== -->
  <RimroomsAsyncIndustries.Scenario.RimroomsStartDef>
    <defName>RR_FurnitureStoreStart</defName>
    <label>Furniture and Knickknack Store opening</label>
    <scenarioId>furniture_knickknack_store</scenarioId>
    <beginsInCorporationContact>false</beginsInCorporationContact>
    <defaultCompanyName>Furniture and Knickknack</defaultCompanyName>
    <scenarioVersion>1</scenarioVersion>
    <completedProjects />
    <mapSize>50</mapSize>
    <mapGenerator>RR_Headquarters</mapGenerator>
    <outdoorTerrain>Soil</outdoorTerrain>
    <floorTerrain>Concrete</floorTerrain>
    <wallStuff>BlocksGranite</wallStuff>
    <arrivalCell>(18, 0, 12)</arrivalCell>
    <stockCell>(34, 0, 16)</stockCell>
    <!-- A shop is a building, not a compound: the outer rectangle is the premises itself,
         roofed and floored, and the rooms inside it are partitions. The one-cell gaps
         between them are the corridors, and they join into a ring so nothing is sealed. -->
    <rooms>
      <li><x>8</x><z>8</z><width>34</width><height>30</height><roofed>true</roofed><floor>true</floor></li>
      <li><x>10</x><z>10</z><width>18</width><height>14</height><roofed>true</roofed><floor>true</floor></li>
      <li><x>29</x><z>10</z><width>11</width><height>14</height><roofed>true</roofed><floor>true</floor></li>
      <li><x>10</x><z>25</z><width>10</width><height>10</height><roofed>true</roofed><floor>true</floor></li>
      <li><x>21</x><z>25</z><width>9</width><height>10</height><roofed>true</roofed><floor>true</floor></li>
      <li><x>31</x><z>25</z><width>9</width><height>10</height><roofed>true</roofed><floor>true</floor></li>
    </rooms>
    <doors>
      <li>(18, 0, 8)</li>
      <li>(18, 0, 10)</li>
      <li>(27, 0, 16)</li>
      <li>(29, 0, 16)</li>
      <li>(14, 0, 25)</li>
      <li>(25, 0, 25)</li>
      <li>(35, 0, 25)</li>
      <li>(35, 0, 34)</li>
    </doors>
    <buildings>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(13, 0, 13)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(17, 0, 13)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(21, 0, 13)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(13, 0, 20)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(17, 0, 20)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(21, 0, 20)</cell></li>
      <li><thing>StandingLamp</thing><cell>(25, 0, 13)</cell></li>
      <li><thing>StandingLamp</thing><cell>(25, 0, 20)</cell></li>
      <li><thing>Table2x2c</thing><stuff>WoodLog</stuff><cell>(24, 0, 17)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(32, 0, 13)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(36, 0, 13)</cell></li>
      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(32, 0, 20)</cell></li>
      <li><thing>StandingLamp</thing><cell>(37, 0, 17)</cell></li>
      <li><thing>WoodFiredGenerator</thing><cell>(36, 0, 22)</cell><fuelFraction>0.5</fuelFraction></li>
      <li><thing>Battery</thing><cell>(33, 0, 22)</cell><batteryFraction>0.4</batteryFraction></li>
      <li><thing>Table1x2c</thing><stuff>WoodLog</stuff><cell>(13, 0, 30)</cell></li>
      <li><thing>Stool</thing><stuff>WoodLog</stuff><cell>(15, 0, 30)</cell></li>
      <li><thing>CommsConsole</thing><cell>(17, 0, 32)</cell></li>
      <li><thing>StandingLamp</thing><cell>(12, 0, 32)</cell></li>
      <li><thing>Bed</thing><stuff>WoodLog</stuff><cell>(23, 0, 27)</cell></li>
      <li><thing>Bed</thing><stuff>WoodLog</stuff><cell>(25, 0, 27)</cell></li>
      <li><thing>Bed</thing><stuff>WoodLog</stuff><cell>(27, 0, 27)</cell></li>
      <li><thing>ElectricStove</thing><cell>(23, 0, 32)</cell></li>
      <li><thing>Table2x2c</thing><stuff>WoodLog</stuff><cell>(26, 0, 32)</cell></li>
      <li><thing>Stool</thing><stuff>WoodLog</stuff><cell>(28, 0, 32)</cell></li>
      <li><thing>Heater</thing><cell>(22, 0, 30)</cell></li>
      <li><thing>StandingLamp</thing><cell>(33, 0, 32)</cell></li>
    </buildings>
    <conduits>
      <li><start>(33, 0, 22)</start><length>14</length><alongX>false</alongX></li>
      <li><start>(14, 0, 24)</start><length>22</length><alongX>true</alongX></li>
      <li><start>(28, 0, 12)</start><length>13</length><alongX>false</alongX></li>
      <li><start>(17, 0, 24)</start><length>9</length><alongX>false</alongX></li>
      <li><start>(23, 0, 24)</start><length>9</length><alongX>false</alongX></li>
    </conduits>
    <!-- Three ordinary people, not a trained crew. The contract's owner/manager, employee and
         night guard, mapped onto company roles the rest of the mod already understands, because
         a role here is an assignment rather than a class. -->
    <roles>
      <li>
        <id>operations</id><mustFight>false</mustFight>
        <skills><Social>7</Social><Intellectual>3</Intellectual></skills>
        <workTypes><li>Warden</li><li>Hauling</li></workTypes>
      </li>
      <li>
        <id>medical_logistics</id><mustFight>false</mustFight>
        <skills><Cooking>5</Cooking><Medicine>3</Medicine><Plants>3</Plants></skills>
        <workTypes><li>Cooking</li><li>Doctor</li><li>Growing</li></workTypes>
      </li>
      <li>
        <id>security</id><mustFight>true</mustFight>
        <skills><Shooting>5</Shooting><Melee>4</Melee></skills>
        <workTypes><li>Hauling</li></workTypes>
      </li>
    </roles>
    <!-- A shop's economy, not a research branch's. No corporate allocation: 200 silver in the
         till and whatever the stock is worth. Wages and overhead are three people and a
         building, which is why they are a fraction of Async's. -->
    <initialFundingUsd>200000</initialFundingUsd>
    <dailyWageUsd>300</dailyWageUsd>
    <dailyOverheadUsd>1500</dailyOverheadUsd>
    <surveyRewardUsd>500000</surveyRewardUsd>
    <surveyBonusUsd>100000</surveyBonusUsd>
  </RimroomsAsyncIndustries.Scenario.RimroomsStartDef>

</Defs>
"""
sub(p, u'\n</Defs>\n', store)
ET.parse(p)
print('start defs written and parsed')

# ------------------------------------------------------------------ the Store scenario
p = os.path.join(MOD, 'Defs', 'ScenarioDefs', 'RR_Scenarios.xml')
scenario = u"""
  <ScenarioDef ParentName="ScenarioBase">
    <defName>RR_FurnitureStore</defName>
    <label>Furniture and Knickknack Store</label>
    <description>Run a small furniture and knickknack shop with a door in the back that should not be there.

Three ordinary people, a sales floor, a stockroom and two hundred silver in the till. There is no corporation, no research and no rescue: nobody is watching this place, and nothing is coming if it goes wrong.

One expected customer has not come back out. What the door is, and what you do about it, is entirely yours to decide. Reaching Async Industries at all is an achievement here rather than a starting condition.

Three people by default. Customise your staff and stock with native setup or Prepare Carefully as you prefer.</description>
    <scenario>
      <summary>A small shop, three ordinary people, and an anomalous threshold in the back room. No corporation, no research, and no rescue until you earn one.</summary>
      <parts>
        <li Class="ScenPart_ConfigPage_ConfigureStartingPawns">
          <def>ConfigPage_ConfigureStartingPawns</def>
          <pawnCount>3</pawnCount>
          <pawnChoiceCount>6</pawnChoiceCount>
          <allowedDevelopmentalStages>Adult</allowedDevelopmentalStages>
        </li>
        <li Class="RimroomsAsyncIndustries.Scenario.ScenPart_RimroomsStart">
          <def>RR_CompanyStart</def>
          <startDef>RR_FurnitureStoreStart</startDef>
          <visible>false</visible>
        </li>
        <li Class="RimroomsAsyncIndustries.Scenario.ScenPart_RimroomsArrival">
          <def>RR_CompanyArrival</def>
          <method>Standing</method>
          <visible>false</visible>
        </li>
        <!-- A shop's stock and a shop's petty cash. No company kit, no field recorder, no
             glow pods: everything this start would need for an expedition is something it
             has to acquire, which is the difference between it and Async Industries. -->
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>Silver</thingDef><count>200</count></li>
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>WoodLog</thingDef><count>200</count></li>
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>Cloth</thingDef><count>120</count></li>
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>Steel</thingDef><count>80</count></li>
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>MealSimple</thingDef><count>24</count></li>
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>MedicineHerbal</thingDef><count>8</count></li>
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>Gun_Revolver</thingDef><count>1</count></li>
      </parts>
    </scenario>
  </ScenarioDef>

  <MapGeneratorDef>"""
sub(p, u'\n  <MapGeneratorDef>', scenario)
ET.parse(p)
print('store scenario written and parsed')
