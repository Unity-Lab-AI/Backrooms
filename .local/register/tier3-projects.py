# -*- coding: utf-8 -*-
"""Research tier 3: one project per branch, 0.12.18-dev.

Tier 3 is "remote operations: support more than one site; work beyond headquarters".

At 0.12.5-dev this tier was DELETED rather than written, because a knob sweep found nothing to
move for four of the seven branches: the systems such an unlock would modify did not exist. That
was the right call and it is recorded in BUILD_ORDER_CORRECTION.md.

Arc 5 wrote those systems (0.12.6-dev to 0.12.9-dev), so the sweep was run again and now finds a
real, observable read site for EVERY branch:

  Facilities   MaximumRemoteSites 8 -> 12          the Sites pane says "3 of 12"
  Commerce     overhead divisor 4 -> 6             the Sites pane's daily figure drops
  Logistics    CanUnloadAt staffing bypass         a shipment lands at an empty site
  Spatial      FrontierRarity 12 -> 8              ways onward are found sooner
  Fieldcraft   EmergenceShare 3 -> 2               ways OUT to the world come up more often
  Measurement  SurveyTicks 600 -> 420              the survey progress bar is visibly shorter
  Entities     BestShelterRate 0.20 -> 0.12        a built room holds the pressure back better

Two restraints were kept deliberately:

  * MaximumFrontiersPerCoordinate is NOT touched. Its own summary says raising it is a design
    decision rather than a tuning knob, because the cap is what keeps a chain of spaces finite.
    Spatial makes the two a branch may find arrive sooner; it never makes them three.
  * BestShelterRate never reaches zero. A coordinate is always wearing, and no player may build a
    room that makes the place ordinary.

Ladder shape, matching tiers 0-2 exactly: insight 4, three route logs, two distortion logs, and
the first tier to require an ENTITY log -- you have to have met something.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6',
                    'Defs', 'RimroomsProjectDefs', 'RR_CompanyProjects.xml')

PROJECTS = [
    ('RR_Facilities_SiteNetwork', 'Site Network', 'RR_Facilities_StandbyDiscipline',
     'RR_Cap_SiteNetwork',
     u'Holding places costs the branch attention as much as money, and the limit has never been '
     u'the money. Standing arrangements, a rota that covers more than one address, and a filing '
     u'system that does not lose a site.\n\nTwelve places on the books instead of eight. The '
     u'Sites pane stops refusing, and the bill goes up accordingly.'),

    ('RR_Commerce_SiteEfficiency', 'Site Economies', 'RR_Commerce_SpecialistRecruitment',
     'RR_Cap_SiteEfficiency',
     u'Every site was being administered as though it were the first one. Consolidate the '
     u'paperwork, the communications and the supply arrangements, and the marginal place stops '
     u'costing what the original did.\n\nEach site adds a sixth of base overhead per day instead '
     u'of a quarter. Proportionate, so it is worth the same to a shop as to a corporation.'),

    ('RR_Logistics_UnattendedDelivery', 'Unattended Delivery', 'RR_Logistics_ForwardDispatch',
     'RR_Cap_UnattendedDelivery',
     u'The supplier has been refusing to unload where nobody is standing to sign for it, which is '
     u'ordinary practice and has cost this branch a great deal of waiting.\n\nThe arrangement is '
     u'now on file: a registered site is a place a crate may simply be left. A place that is not '
     u'on the books still refuses, and always will.'),

    ('RR_Spatial_CoordinateReading', 'Coordinate Reading', 'RR_Spatial_KnownAddress',
     'RR_Cap_CoordinateReading',
     u'A space gives itself away before it gives anything else away. Which doorway sits wrong in '
     u'its frame, which corridor is a foot too long, which junction the carpet was laid '
     u'through.\n\nRoughly one doorway in eight leads onward rather than one in twelve. **The '
     u'limit of two ways onward per coordinate does not move, and will not:** it is what keeps a '
     u'chain of spaces finite.'),

    ('RR_Fieldcraft_WayHomeDiscipline', 'Way Home Discipline', 'RR_Fieldcraft_ReliefWatch',
     'RR_Cap_WayHomeDiscipline',
     u'Crews have been finding the way deeper more often than the way out, and the company has '
     u'stopped believing that is chance. Train for the exit first and the exit is what gets '
     u'found.\n\nA survey turns up a way out into the world on one draw in two instead of one in '
     u'three. The branch does not go less deep; it comes back out more often.'),

    ('RR_Measurement_RapidSurvey', 'Rapid Survey', 'RR_Measurement_ReferenceStandards',
     'RR_Cap_RapidSurvey',
     u'Most of a survey was establishing what ordinary looks like. With reference standards '
     u'already in hand, a crew measures the difference instead of the whole.\n\nA survey takes '
     u'about ten seconds of standing there rather than fourteen. Visible on the progress bar, '
     u'which is a short time to be standing still in a place like that.'),

    ('RR_Entities_SpaceDiscipline', 'Space Discipline', 'RR_Entities_ContainmentProtocol',
     'RR_Cap_SpaceDiscipline',
     u'A built room was already the only thing that slowed the place down. Knowing what is in the '
     u'space changes how the room is built: sightlines, thresholds, what is left in the open and '
     u'what is not.\n\nA properly built room holds it back considerably better. **It never stops '
     u'entirely.** A coordinate is always wearing, and nothing will make it somewhere to live.'),
]

BLOCK = u"""
  <!-- =====================================================================================
       TIER 3 - remote operations: support more than one site; work beyond headquarters.

       This tier was DELETED rather than written at 0.12.5-dev, because a knob sweep found
       nothing to move for four of the seven branches: the systems an unlock would modify did
       not exist. Arc 5 wrote them between 0.12.6-dev and 0.12.9-dev, and the sweep now finds a
       real, observable read site for EVERY branch. Record: BUILD_ORDER_CORRECTION.md.

       Every capability below is read by real code, and proof-research-branches.py asserts
       exactly that: an unlock a player is told about and that changes nothing is worse than no
       unlock, because it is a lie on the card.

       Ladder shape matches tiers 0-2: insight 4, three route logs, two distortion logs, and the
       first tier to require an ENTITY log. You have to have met something.
       ===================================================================================== -->

"""


def project(def_name, label, prereq, capability, description):
    return (u'  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>\n'
            u'    <defName>%s</defName>\n'
            u'    <label>%s</label>\n'
            u'    <description>%s</description>\n'
            u'    <insightCost>4</insightCost>\n'
            u'    <workRequired>14000</workRequired>\n'
            u'    <minimumIntellectual>6</minimumIntellectual>\n'
            u'    <requiredRouteLogs>3</requiredRouteLogs>\n'
            u'    <requiredDistortionLogs>2</requiredDistortionLogs>\n'
            u'    <requiredEntityLogs>1</requiredEntityLogs>\n'
            u'    <prerequisiteProjects><li>%s</li></prerequisiteProjects>\n'
            u'    <grantsCapabilities><li>%s</li></grantsCapabilities>\n'
            u'  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>\n'
            % (def_name, label, description, prereq, capability))


s = io.open(PATH, encoding='utf-8-sig').read()
anchor = u'\n</Defs>'
assert anchor in s, 'closing tag not found'
assert u'RR_Facilities_SiteNetwork' not in s, 'already applied'
body = BLOCK + u'\n'.join(project(*p) for p in PROJECTS)
io.open(PATH, 'w', encoding='utf-8-sig', newline='').write(s.replace(anchor, body + anchor, 1))
print('tier 3 authored: %d projects, one per branch' % len(PROJECTS))
