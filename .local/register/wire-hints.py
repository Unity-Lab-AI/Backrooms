# -*- coding: utf-8 -*-
"""Wire the solo/group hints into save and tick, and add their strings."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'RimroomsCampaignComponent.cs'),
    u'            ExposeFacilityRelief();',
    u'            ExposeFacilityRelief();\n            ExposeSoloGroupHints();')

sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'CampaignServices.cs'),
    u'            if (now % 60 == 30) { TickFacilityRelief(); }',
    u'            if (now % 60 == 30) { TickFacilityRelief(); }\n'
    u'            // The solo/group start has no request line, so this is the only guidance it\n'
    u'            // gets. Slow: these are thoughts, not business, and they fire once each.\n'
    u'            if (now % 250 == 125) { TickSoloGroupHints(); }')
print('hints wired into save and tick')

# ------------------------------------------------------------------ the hints themselves
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Scenario.xml')
s = io.open(p, encoding='utf-8-sig').read()
keys = ['RR_Hint_contact', 'RR_Hint_surface', 'RR_Hint_comms', 'RR_Hint_doorsRunOut',
        'RR_Event_SoloGroupHint']
for k in keys:
    assert k not in s, k
block = (
    u'  <RR_Hint_contact>Somebody needs to be told about this. Not for help, necessarily. Just so '
    u'it is written down somewhere that is not in here.</RR_Hint_contact>\n'
    u'  <RR_Hint_surface>Open sky. Nobody is going to believe a word of it, and there is nothing '
    u'standing here that we did not walk out of.</RR_Hint_surface>\n'
    u'  <RR_Hint_comms>The radio works. Whether anyone on the other end has a category for what we '
    u'would be reporting is a separate question.</RR_Hint_comms>\n'
    u'  <RR_Hint_doorsRunOut>The doors stop going anywhere new around here. Whatever is further in, '
    u'nobody is going to walk to it.</RR_Hint_doorsRunOut>\n'
    u'  <RR_Event_SoloGroupHint>Somebody said something worth remembering.</RR_Event_SoloGroupHint>\n')
i = s.rindex(u'</LanguageData>')
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + block + s[i:])
ET.parse(p)
print('hint strings added and parsed')
