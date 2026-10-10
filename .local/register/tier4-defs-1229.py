# -*- coding: utf-8 -*-
"""Author research tier 4: six projects, and two branches deliberately without one.

Scaled from tier 3 -- insight 4, work 14000, Intellectual 6, 3 route + 2 distortion + 1 entity --
to insight 5, work 18000, Intellectual 7, 4 route + 3 distortion + 2 entity. Each has its tier 3
project as its prerequisite, so a branch still climbs its own ladder.

NOT WRITTEN, and this is the part that matters:

  * **Logistics** -- lead time, dispatch delay, order capacity and unattended delivery are claimed
    by tiers 1, 2, 0 and 3. What remains in Procurement is `MaximumOpenOrders` (100),
    `MaximumPhysicalStacksPerOrder` (4096) and `MaximumStacksDeliveredPerTick` (4): safety bounds
    a player will never reach. A fifth Logistics project would be a hollow unlock, and 0.12.5-dev
    deleted four of those.

  * **The gate line** -- its fourth rung is already *"a connection that no longer counts down"*.
    There is nothing above indefinite, so a fifth rung is impossible by construction.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Defs',
                    'RimroomsProjectDefs', 'RR_CompanyProjects.xml')

HEADER = u"""
  <!-- ==================================================================================== -->
  <!-- TIER 4 - THE PRACTISED BRANCH                                                        -->
  <!--                                                                                      -->
  <!-- SIX projects, not eight, and the two absences are the important part of this tier.    -->
  <!--                                                                                      -->
  <!-- LOGISTICS HAS NO TIER 4. Lead time, dispatch delay, order capacity and unattended     -->
  <!-- delivery are already taken by tiers 1, 2, 0 and 3. What is left in Procurement is     -->
  <!-- MaximumOpenOrders at 100, MaximumPhysicalStacksPerOrder at 4096 and                   -->
  <!-- MaximumStacksDeliveredPerTick at 4 - safety bounds no player will ever reach, not     -->
  <!-- knobs. A project here would promise something and change nothing, which is exactly    -->
  <!-- what 0.12.5-dev deleted four projects for.                                            -->
  <!--                                                                                       -->
  <!-- THE GATE LINE HAS NO TIER 4 EITHER, and cannot. Its fourth rung is already "a          -->
  <!-- connection that no longer counts down". There is nothing above indefinite.            -->
  <!--                                                                                       -->
  <!-- Every one of the six moves a number a player can name the effect of, and every one of -->
  <!-- those numbers was unclaimed before this tier. Two restraints from 0.12.18-dev held:   -->
  <!-- the per-coordinate frontier cap is not a research knob, so Spatial took the            -->
  <!-- ORDINARY-MAP rarity instead; and shelter never reaches zero, so Entities took the      -->
  <!-- penalty ceiling rather than the shelter rate a second time. MaximumNaturalDepth stays  -->
  <!-- at three, because the owner answered "option 1" on exactly that question.              -->
  <!-- ==================================================================================== -->

"""

PROJECTS = [
    ('RR_Facilities_PractisedDialling', u'Practised Dialling',
     u'Stop treating every opening as a first attempt. Written procedure, a checklist somebody '
     u'actually follows, and an operator who is not reading the manual while the reserve drains.'
     u'\\n\\nBringing any gate up takes a fifth less work, on every route rather than only the '
     u'familiar ones. The floor still applies, so a well-worn address is quick but never free.',
     'RR_Facilities_SiteNetwork', 'RR_Cap_PractisedDialling'),

    ('RR_Fieldcraft_Decompression', u'Decompression',
     u'What to do with people in the hours after they come out. Somewhere to sit, somebody to talk '
     u'to, and a rule that nobody goes straight back down.'
     u'\\n\\nA crew shakes the place off twice as fast once they are out of it. It does nothing at '
     u'all while they are still down there: the coordinate is not less hostile, the rotation is '
     u'simply better.',
     'RR_Fieldcraft_WayHomeDiscipline', 'RR_Cap_Decompression'),

    ('RR_Commerce_OpenMarket', u'Open Market',
     u'Find out what ordinary salvage is actually worth before the company quotes you for it. Two '
     u'more buyers on the list and a clerk who has read the last six settlements.'
     u'\\n\\nThe company pays close to market for ordinary goods instead of well under it. The odd '
     u'premium is untouched - a branch learns to stop being fleeced on scrap, not to make the '
     u'Backrooms pay better.',
     'RR_Commerce_SiteEfficiency', 'RR_Cap_OpenMarket'),

    ('RR_Measurement_StatementDiscipline', u'Statement Discipline',
     u'A form, an order to ask the questions in, and the discovery that most of taking a statement '
     u'is not talent.'
     u'\\n\\nMost of the branch can now take a statement the company will file, rather than only '
     u'its most sociable staff. On a small crew, where the one person good with people is often a '
     u'witness themselves, this is the difference between settling a disagreement and living with '
     u'it.',
     'RR_Measurement_RapidSurvey', 'RR_Cap_StatementDiscipline'),

    ('RR_Spatial_SurfaceReading', u'Surface Reading',
     u'The tells are the same on this side. Doors that open onto the wrong depth of building, '
     u'corridors nobody remembers commissioning, a room count that does not match the outside.'
     u'\\n\\nWays in turn up on your own maps noticeably more often. It changes nothing about how '
     u'many a single coordinate can hold, or how deep the found chain reaches - only how often a '
     u'door on the surface turns out to be one.',
     'RR_Spatial_CoordinateReading', 'RR_Cap_SurfaceReading'),

    ('RR_Entities_SteadyNerve', u'Steady Nerve',
     u'Name the thing, write down what it did, and give the next crew the page. Most of what the '
     u'place does to people is done by not being explicable.'
     u'\\n\\nThe worst the Backrooms can weigh on somebody drops from severe to noticeable. It '
     u'never reaches nothing: a branch can learn to carry the place, and cannot learn to stop '
     u'feeling it.',
     'RR_Entities_SpaceDiscipline', 'RR_Cap_SteadyNerve'),
]

TEMPLATE = u"""  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>%s</defName>
    <label>%s</label>
    <description>%s</description>
    <insightCost>5</insightCost>
    <workRequired>18000</workRequired>
    <minimumIntellectual>7</minimumIntellectual>
    <requiredRouteLogs>4</requiredRouteLogs>
    <requiredDistortionLogs>3</requiredDistortionLogs>
    <requiredEntityLogs>2</requiredEntityLogs>
    <prerequisiteProjects><li>%s</li></prerequisiteProjects>
    <grantsCapabilities><li>%s</li></grantsCapabilities>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>

"""

s = io.open(PATH, encoding='utf-8').read()
assert u'RR_Facilities_PractisedDialling' not in s, 'tier 4 already authored'

block = HEADER
for defName, label, description, prerequisite, capability in PROJECTS:
    block += TEMPLATE % (defName, label, description, prerequisite, capability)

closing = u'</Defs>'
assert s.rstrip().endswith(closing)
index = s.rindex(closing)
s = s[:index] + block + s[index:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('tier 4 authored: %d projects, Logistics and the gate line deliberately absent' % len(PROJECTS))
