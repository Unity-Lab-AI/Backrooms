# -*- coding: utf-8 -*-
"""Arcs 5 to 8: the thirteen remaining generated request families, 0.12.13-dev.

Every family is one item named in `CAMPAIGN_CHART.md`, nothing invented:

  arc 5, "Build beyond headquarters"  -- relay stations, caches, field shelters, guarded leases,
                                         resupply, evacuation
  arc 6, "Respond to the outside world" -- witnesses, missing residents, public danger
  arc 7, "Expand industrial reach"    -- heavy cargo, staff across the wider world
  arc 8, "Enter deeper systems"       -- combining known families, one unfamiliar rule at a time

Every route resolves against a def that already exists, which is the whole point of
`proof-request-generation.py`: a route naming something that is not there can never fire and
nothing else in the project will say so.

  things (all catalogue-carried, so Purchase can refuse before contact):
      ComponentIndustrial, MealSurvivalPack, MedicineIndustrial, Silver, Steel, WoodLog
  logs:     route, distortion, entity
  projects: Logistics_Relays, Commerce_Leases, Commerce_NegotiatedTerms, Logistics_StandingOrders,
            Fieldcraft_ReturnDrill, Entities_Detection, Entities_ContainmentProtocol,
            Logistics_ForwardDispatch, Commerce_SpecialistRecruitment, Spatial_CoordinateAtlas,
            Measurement_Corroboration
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6')
DEFS = os.path.join(MOD, 'Defs', 'RimroomsRequestDefs', 'RR_Requests.xml')
KEYED = os.path.join(MOD, 'Languages', 'English', 'Keyed', 'RR_Requests.xml')


def family(def_name, label, description, arc, payment, routes):
    lines = [u'  <RimroomsAsyncIndustries.Company.RimroomsRequestDef>',
             u'    <defName>%s</defName>' % def_name,
             u'    <label>%s</label>' % label,
             u'    <description>%s</description>' % description,
             u'    <arc>%d</arc>' % arc,
             u'    <paymentUsd>%d</paymentUsd>' % payment,
             u'    <successRoutes>']
    for route in routes:
        lines.append(u'      <li>')
        lines.append(u'        <kind>%s</kind>' % route['kind'])
        lines.append(u'        <labelKey>%sLabel</labelKey>' % route['key'])
        lines.append(u'        <descriptionKey>%sDesc</descriptionKey>' % route['key'])
        if 'thing' in route:
            lines.append(u'        <thingDefName>%s</thingDefName>' % route['thing'])
            lines.append(u'        <count>%d</count>' % route['count'])
        if 'log' in route:
            lines.append(u'        <logKind>%s</logKind>' % route['log'])
            if route.get('count', 1) != 1:
                lines.append(u'        <count>%d</count>' % route['count'])
        if 'project' in route:
            lines.append(u'        <projectDefName>%s</projectDefName>' % route['project'])
        if 'redirect' in route:
            lines.append(u'        <redirectTo>%s</redirectTo>' % route['redirect'])
        lines.append(u'      </li>')
    lines.append(u'    </successRoutes>')
    lines.append(u'  </RimroomsAsyncIndustries.Company.RimroomsRequestDef>')
    return u'\n'.join(lines)


FAMILIES = [
    # ---------------------------------------------------------------- arc 5
    ('RR_Request_RelayStation', 5, 10000000,
     u'a relay station between here and there',
     u'Signals do not carry out of a coordinate, and the company has decided that is a problem it '
     u'is willing to pay to stop hearing about. It wants a relay standing between the branch and '
     u'whatever it is working.\\n\\nBuild the understanding, or hand over the hardware and let '
     u'somebody else work it out.',
     [{'kind': 'Research', 'key': 'RR_Route_RelayWork', 'project': 'RR_Logistics_Relays'},
      {'kind': 'Deliver', 'key': 'RR_Route_RelayParts', 'thing': 'ComponentIndustrial', 'count': 30}]),

    ('RR_Request_FieldCache', 5, 12000000,
     u'a cache nobody has to carry',
     u'Every crew that has come home short has come home short of the same two things. The company '
     u'wants them already out there, sitting where the next crew will need them.\\n\\nFood or '
     u'medicine. It is not fussy, and it is not sending either.',
     [{'kind': 'Deliver', 'key': 'RR_Route_CacheRations', 'thing': 'MealSurvivalPack', 'count': 25},
      {'kind': 'Purchase', 'key': 'RR_Route_CacheMedicine', 'thing': 'MedicineIndustrial', 'count': 15}]),

    ('RR_Request_FieldShelter', 5, 13000000,
     u'somewhere out there to stand still',
     u'A shelter is the difference between a crew that waits out a bad hour and a crew that walks '
     u'into it. The company has priced both and prefers the first.\\n\\nTimber or steel. Whatever '
     u'the branch can get to the place it is needed.',
     [{'kind': 'Deliver', 'key': 'RR_Route_ShelterTimber', 'thing': 'WoodLog', 'count': 400},
      {'kind': 'Purchase', 'key': 'RR_Route_ShelterSteel', 'thing': 'Steel', 'count': 150}]),

    ('RR_Request_GuardedLease', 5, 16000000,
     u'a lease with somebody standing on it',
     u'The company wants a place held on paper and held in fact, and it has noticed those are two '
     u'different achievements.\\n\\nGet the terms written, or commit to the negotiating work and '
     u'let the paperwork follow.',
     [{'kind': 'Research', 'key': 'RR_Route_LeaseWork', 'project': 'RR_Commerce_Leases'},
      {'kind': 'Redirect', 'key': 'RR_Route_LeaseTerms', 'redirect': 'RR_Commerce_NegotiatedTerms'}]),

    ('RR_Request_Resupply', 5, 14000000,
     u'a resupply run that happens without being asked',
     u'The company is tired of authorising the same shipment every time somebody runs out. It '
     u'wants the branch to make the problem stop being a decision.\\n\\nStanding orders, or enough '
     u'rations bought outright that the question does not come up for a while.',
     [{'kind': 'Research', 'key': 'RR_Route_ResupplyStanding', 'project': 'RR_Logistics_StandingOrders'},
      {'kind': 'Purchase', 'key': 'RR_Route_ResupplyBulk', 'thing': 'MealSurvivalPack', 'count': 40}]),

    ('RR_Request_Evacuation', 5, 18000000,
     u'a way to get everyone out at once',
     u'Coming home one at a time works until the day it does not. The company wants a branch that '
     u'can empty a place on purpose rather than by attrition.\\n\\nDrill it, or show them somebody '
     u'who has already walked a route out and can lead the rest.',
     [{'kind': 'Research', 'key': 'RR_Route_EvacuationDrill', 'project': 'RR_Fieldcraft_ReturnDrill'},
      {'kind': 'Testify', 'key': 'RR_Route_EvacuationGuide', 'log': 'route'}]),

    # ---------------------------------------------------------------- arc 6
    ('RR_Request_TownWitnesses', 6, 15000000,
     u'a town that saw something',
     u'A door opened somewhere it had no business opening, in front of people who live there. The '
     u'company would like the account to come from somebody it employs.\\n\\nA first-hand account '
     u'or a filed one. The difference matters more to the branch than it does to the company.',
     [{'kind': 'Testify', 'key': 'RR_Route_WitnessAccount', 'log': 'entity'},
      {'kind': 'Document', 'key': 'RR_Route_WitnessFiled', 'log': 'entity'}]),

    ('RR_Request_MissingResidents', 6, 19000000,
     u'residents who are not where they live',
     u'People have stopped being where they are supposed to be, and the pattern of it is the part '
     u'the company finds interesting.\\n\\nIt will take detection work it can reuse, or somebody '
     u'who has been close enough to one of these things to describe it.',
     [{'kind': 'Research', 'key': 'RR_Route_MissingDetection', 'project': 'RR_Entities_Detection'},
      {'kind': 'Testify', 'key': 'RR_Route_MissingAccount', 'log': 'entity'}]),

    ('RR_Request_PublicDanger', 6, 24000000,
     u'something out where people are',
     u'Whatever came through is no longer in a corridor nobody visits. The company has been asked '
     u'to make it somebody else\'s problem, and has decided the branch is somebody else.\\n\\nA '
     u'containment capability, or the hardware for one.',
     [{'kind': 'Research', 'key': 'RR_Route_DangerContainment', 'project': 'RR_Entities_ContainmentProtocol'},
      {'kind': 'Deliver', 'key': 'RR_Route_DangerHardware', 'thing': 'ComponentIndustrial', 'count': 25}]),

    # ---------------------------------------------------------------- arc 7
    ('RR_Request_HeavyCargo', 7, 30000000,
     u'cargo that does not fit through a door',
     u'The company has sold capacity it does not have, across a distance it has not tried. It is '
     u'confident this is the branch\'s problem now.\\n\\nForward dispatch, or simply enough metal '
     u'in one place that the shortfall stops being visible.',
     [{'kind': 'Research', 'key': 'RR_Route_CargoDispatch', 'project': 'RR_Logistics_ForwardDispatch'},
      {'kind': 'Purchase', 'key': 'RR_Route_CargoBulk', 'thing': 'Steel', 'count': 600}]),

    ('RR_Request_StaffTransfer', 7, 34000000,
     u'people who know what they are looking at',
     u'The branch has been running on whoever was nearest. The company would like that to stop '
     u'being true before something expensive is misread.\\n\\nRecruit properly, or pay enough that '
     u'somebody else\'s specialist becomes available.',
     [{'kind': 'Research', 'key': 'RR_Route_StaffRecruit', 'project': 'RR_Commerce_SpecialistRecruitment'},
      {'kind': 'Purchase', 'key': 'RR_Route_StaffBuyIn', 'thing': 'Silver', 'count': 3000}]),

    # ---------------------------------------------------------------- arc 8
    ('RR_Request_CombinedFamilies', 8, 38000000,
     u'a place that is two places at once',
     u'Deeper down, the shapes stop belonging to one family. The company wants that written up by '
     u'somebody who noticed it happening rather than somebody who read about it.\\n\\nA filed '
     u'record of the disagreement, or the atlas work that makes it predictable.',
     [{'kind': 'Document', 'key': 'RR_Route_CombinedRecord', 'log': 'distortion'},
      {'kind': 'Research', 'key': 'RR_Route_CombinedAtlas', 'project': 'RR_Spatial_CoordinateAtlas'}]),

    ('RR_Request_UnfamiliarRule', 8, 45000000,
     u'one rule nobody has seen before',
     u'Something down there is behaving consistently, and consistently wrong. The company has '
     u'decided that is worth more than anything the branch has brought back so far.\\n\\nDocument '
     u'it, or do the corroboration work that turns one account into a finding.',
     [{'kind': 'Document', 'key': 'RR_Route_UnfamiliarRecord', 'log': 'entity'},
      {'kind': 'Research', 'key': 'RR_Route_UnfamiliarCorroboration', 'project': 'RR_Measurement_Corroboration'}]),
]

ROUTE_STRINGS = [
    ('RR_Route_RelayWork', u'Do the relay work',
     u'Finish the relay project and the branch owns the capability rather than renting it. Slower, and the company stops asking about signals.'),
    ('RR_Route_RelayParts', u'Hand over the hardware',
     u'Deliver the components and let the relay be somebody else\'s build. Faster, and the branch learns nothing it will not need later.'),
    ('RR_Route_CacheRations', u'Stock it with rations',
     u'Survival packs, out where the next crew will reach them before they need them. The cheap answer and the one that actually gets used.'),
    ('RR_Route_CacheMedicine', u'Stock it with medicine',
     u'Order industrial medicine and put it in the cache. More expensive, and it covers the situation rations do not.'),
    ('RR_Route_ShelterTimber', u'Build it out of timber',
     u'Haul wood to the place it is wanted. Cheap, quick and exactly as durable as wood is.'),
    ('RR_Route_ShelterSteel', u'Buy steel and do it properly',
     u'Order the metal and build something that will still be standing next season. The company notices the difference and does not pay extra for it.'),
    ('RR_Route_LeaseWork', u'Do the leasing work',
     u'Complete the leases project and the branch can hold ground on paper. The company treats this as the real answer.'),
    ('RR_Route_LeaseTerms', u'Start negotiating instead',
     u'Commit to the negotiated-terms work and the company accepts the intent. Declaring a direction is enough here; arriving is not required.'),
    ('RR_Route_ResupplyStanding', u'Put standing orders in place',
     u'Finish the standing-orders work and the shipment stops being a decision anybody has to make. What the company actually wanted.'),
    ('RR_Route_ResupplyBulk', u'Just buy a great deal of food',
     u'Order rations in quantity and the question goes away for a while. It comes back.'),
    ('RR_Route_EvacuationDrill', u'Drill the return',
     u'Complete the return-drill work so a crew can leave together and on purpose. The company files this under things it hopes never to need.'),
    ('RR_Route_EvacuationGuide', u'Put your guide in front of them',
     u'An employee who has walked a route out and is still on the books can lead the rest. Worth nothing the day they leave.'),
    ('RR_Route_WitnessAccount', u'Your own person tells them',
     u'An employee who saw it, and is still here, speaks to it directly. The company prefers this because it can be questioned.'),
    ('RR_Route_WitnessFiled', u'Give them the filed record',
     u'An analysed entity record says the same thing on paper, and keeps saying it after the witness has gone.'),
    ('RR_Route_MissingDetection', u'Do the detection work',
     u'Finish the detection project. The company gets something it can sell to the next town as well as this one.'),
    ('RR_Route_MissingAccount', u'Have somebody describe it',
     u'An employee who got close enough to one of these things, and came back, closes this without further work.'),
    ('RR_Route_DangerContainment', u'Do the containment work',
     u'Complete the containment protocol. Expensive, and the only route that leaves the branch able to do this again.'),
    ('RR_Route_DangerHardware', u'Deliver the hardware and step back',
     u'Components on the ground, and the problem formally handed on. Nobody involved believes this is a solution.'),
    ('RR_Route_CargoDispatch', u'Do the forward dispatch work',
     u'Finish forward dispatch and the branch can move weight across distance. The company has already sold this.'),
    ('RR_Route_CargoBulk', u'Buy the tonnage outright',
     u'Order enough metal that the shortfall stops being visible on anybody\'s paperwork. Ruinously expensive and completely effective.'),
    ('RR_Route_StaffRecruit', u'Recruit specialists properly',
     u'Complete the recruitment work and the branch stops running on whoever was nearest.'),
    ('RR_Route_StaffBuyIn', u'Pay somebody else\'s specialist',
     u'Enough silver moves the problem to a competitor\'s hiring department. The company respects this more than it admits.'),
    ('RR_Route_CombinedRecord', u'File the disagreement',
     u'An analysed distortion record of a place that stopped belonging to one family. The paperwork the company can put in front of a client.'),
    ('RR_Route_CombinedAtlas', u'Do the atlas work',
     u'Complete the coordinate atlas and the combination stops being a surprise. The company would rather own the map than the anecdote.'),
    ('RR_Route_UnfamiliarRecord', u'Write the thing down',
     u'An analysed entity record of whatever is behaving consistently and wrongly. One account, properly filed.'),
    ('RR_Route_UnfamiliarCorroboration', u'Do the corroboration work',
     u'Complete the corroboration project and one account becomes a finding. This is the version the company can charge for.'),
]

DEF_BLOCK = (u"""
  <!-- ===================================================================================
       ARCS 5 TO 8, GENERATED. One family per item the chart names, nothing invented.

         arc 5  relay stations, caches, field shelters, guarded leases, resupply, evacuation
         arc 6  witnesses, missing residents, public danger
         arc 7  heavy cargo, staff across the wider world
         arc 8  combining known families, one unfamiliar rule at a time

       Every route resolves against a def that already exists. A route naming something that is
       not there can never fire, still counts toward the two-different-kinds rule, and nothing
       but proof-request-generation.py will say so.
       =================================================================================== -->

""" + u'\n\n'.join(family(name, label, description, arc, payment, routes)
                   for name, arc, payment, label, description, routes in FAMILIES) + u'\n')

KEY_BLOCK = (u"""
  <!-- Arcs 5 to 8 generated families. Route label: a thing the player picks, no full stop.
       Route description: prose, ends a sentence. -->

""" + u'\n'.join(
    u'  <%sLabel>%s</%sLabel>\n  <%sDesc>%s</%sDesc>' % (key, label, key, key, desc, key)
    for key, label, desc in ROUTE_STRINGS) + u'\n')


def append_before_close(path, anchor, block, guard):
    s = io.open(path, encoding='utf-8-sig').read()
    assert anchor in s, '%s: closing tag not found' % path
    assert guard not in s, '%s: block already applied' % path
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(s.replace(anchor, block + anchor, 1))
    print('updated %s' % os.path.basename(path))


append_before_close(DEFS, u'\n</Defs>', DEF_BLOCK, u'RR_Request_RelayStation')
append_before_close(KEYED, u'\n</LanguageData>', KEY_BLOCK, u'RR_Route_RelayWorkLabel')
print('%d families, %d route strings' % (len(FAMILIES), len(ROUTE_STRINGS)))
