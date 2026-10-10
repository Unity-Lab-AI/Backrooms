# -*- coding: utf-8 -*-
"""Insert the tier 2 research band into RR_CompanyProjects.xml."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Defs',
                 'RimroomsProjectDefs', 'RR_CompanyProjects.xml')
s = io.open(p, encoding='utf-8-sig').read()

tier2 = u"""  <!-- ==================================================================================== -->
  <!-- TIER 2 - REPEATABLE OPERATIONS                                                       -->
  <!--                                                                                      -->
  <!-- "Revisit known coordinates; reduce preventable failures." docs/CAMPAIGN_CHART.md 3.1. -->
  <!--                                                                                      -->
  <!-- Each requires its own tier 1 sibling AND a completed distortion log. Tier 1 asked     -->
  <!-- only for route logs because it is about having been through once. This band is about  -->
  <!-- having been through often enough for something to have gone wrong, so the space has   -->
  <!-- to have misbehaved while somebody was recording it.                                   -->
  <!--                                                                                      -->
  <!-- EVERY ONE OF THESE MOVES A KNOB NO OTHER PROJECT TOUCHES. Tier 1 had three            -->
  <!-- capabilities that superseded their tier 0 sibling because they shared a number; here  -->
  <!-- there is nothing to supersede, so a player reading two cards gets two independent     -->
  <!-- effects and neither card has to explain the other.                                    -->
  <!--                                                                                      -->
  <!-- Three knobs named in the previous handoff were dropped after checking their read      -->
  <!-- sites, and the replacements are below. stablePowerTicksRequired is 60 ticks, one      -->
  <!-- second. MaximumOpenOrders is a sanity cap of 100 open orders. Catalogue               -->
  <!-- maxOrderQuantity is already 500 to a million per row. A project moving any of those   -->
  <!-- would have granted a capability that real code reads, changing a number no player     -->
  <!-- could ever notice, which proof-research-branches.py cannot catch BECAUSE the read     -->
  <!-- site is real. A live read site is not the same thing as a live effect.                -->
  <!-- ==================================================================================== -->

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Facilities_StandbyDiscipline</defName>
    <label>Standby Discipline</label>
    <description>Find out which of the standby systems genuinely have to stay warm between connections and which were only ever left running because nobody had asked.

A designated gate costs half as much to keep while it is closed. It changes nothing about what an open connection draws; this is the bill for the days the gate is doing nothing but staying ready.</description>
    <insightCost>3</insightCost>
    <workRequired>11000</workRequired>
    <minimumIntellectual>6</minimumIntellectual>
    <requiredRouteLogs>2</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Facilities_EfficientAperture</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_StandbyDiscipline</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Fieldcraft_ReliefWatch</defName>
    <label>Relief Watch</label>
    <description>Drill the handover at the console until an operator being called away is a relief rather than an interruption. Somebody always knows where the dial was left.

An unattended ramp loses a quarter as much progress. It still lapses if nobody comes back, because a ramp nobody is watching is not an operation.</description>
    <insightCost>3</insightCost>
    <workRequired>10000</workRequired>
    <minimumIntellectual>6</minimumIntellectual>
    <requiredRouteLogs>2</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Fieldcraft_RescueTraining</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_ReliefWatch</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Measurement_ReferenceStandards</defName>
    <label>Reference Standards</label>
    <description>Keep a set of references the branch trusts, so calibration is a comparison against something known instead of deriving the whole scale again from first principles.

Calibrating a gate assembly takes two fifths less work.</description>
    <insightCost>3</insightCost>
    <workRequired>11000</workRequired>
    <minimumIntellectual>7</minimumIntellectual>
    <requiredRouteLogs>2</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Measurement_Corroboration</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_ReferenceStandards</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Spatial_KnownAddress</defName>
    <label>Known Address</label>
    <description>Write down what the dial actually did last time rather than trusting whoever ran the console to remember it, and a route the branch has walked before stops being dialled from scratch.

Every previous connection to an address makes the next one to it markedly faster. A first visit is exactly as slow as it ever was, and a well worn route is still never free.</description>
    <insightCost>3</insightCost>
    <workRequired>12000</workRequired>
    <minimumIntellectual>6</minimumIntellectual>
    <requiredRouteLogs>3</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Spatial_AlternateExits</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_KnownAddress</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Entities_ContainmentProtocol</defName>
    <label>Containment Protocol</label>
    <description>Turn what the branch has learned about being followed into written procedure at the threshold, and then hold the crews to it.

Nothing follows a crew out through a connection until the aperture is opened wider than Field Stability allows. The procedure buys back a whole rung of the gate ladder, and a branch that pushes the aperture hard without it has opened the door wider for something that was already interested.</description>
    <insightCost>3</insightCost>
    <workRequired>13000</workRequired>
    <minimumIntellectual>7</minimumIntellectual>
    <requiredRouteLogs>2</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Entities_Detection</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_ContainmentProtocol</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Logistics_ForwardDispatch</defName>
    <label>Forward Dispatch</label>
    <description>Stop letting a repeat order queue behind somebody else and their paperwork. The supplier holds the branch's standing arrangements on file and acts on them.

A shipment leaves in half the time. Combined with the branch's own relays this is what finally moves an arrival rather than running into the floor of a shipment that had not left yet.</description>
    <insightCost>3</insightCost>
    <workRequired>10000</workRequired>
    <minimumIntellectual>5</minimumIntellectual>
    <requiredRouteLogs>2</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Logistics_Relays</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_ForwardDispatch</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Commerce_SpecialistRecruitment</defName>
    <label>Specialist Recruitment</label>
    <description>Keep a standing brief with the parent corporation's recruiters instead of describing the branch from nothing every time it needs somebody.

The branch may ask for applicants again in half the time. The corporation was never going to refuse; it was going to take a while to get around to it.</description>
    <insightCost>3</insightCost>
    <workRequired>10000</workRequired>
    <minimumIntellectual>6</minimumIntellectual>
    <requiredRouteLogs>2</requiredRouteLogs>
    <requiredDistortionLogs>1</requiredDistortionLogs>
    <prerequisiteProjects><li>RR_Commerce_Leases</li></prerequisiteProjects>
    <grantsCapabilities><li>RR_Cap_SpecialistRecruitment</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

"""

anchor = u"  <!-- The window-tier ladder."
assert anchor in s, 'ladder anchor not found'
assert tier2.count(u'<!--') == tier2.count(u'-->'), 'unbalanced comment markers'
s = s.replace(anchor, tier2 + anchor, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('tier 2 block inserted')

# The gotcha that has now cost five separate failures: a double hyphen inside an XML
# comment. The build does not parse def XML, so only this catches it here.
ET.parse(p)
print('XML parses clean')
