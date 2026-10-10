# -*- coding: utf-8 -*-
"""Wire the facility relief into save and tick, and add its keyed strings."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, old, new, enc='utf-8-sig'):
    p = os.path.join(REPO, rel)
    s = io.open(p, encoding=enc).read()
    assert old in s, '%s: anchor not found' % rel
    assert s.count(old) == 1, '%s: anchor not unique' % rel
    s = s.replace(old, new, 1)
    io.open(p, 'w', encoding=enc, newline='').write(s)
    print('updated %s' % rel)


# --------------------------------------------------------- save
edit('src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs',
     u'            ExposeCorporateSupply();',
     u'            ExposeCorporateSupply();\n            ExposeFacilityRelief();')

# --------------------------------------------------------- tick
edit('src/RimroomsAsyncIndustries/Company/CampaignServices.cs',
     u'            if (now % 60 == 0) { UpdateOddSupplyContracts(); }',
     u'            if (now % 60 == 0) { UpdateOddSupplyContracts(); }\n'
     u'            // The clean-up team. Checked often enough to land inside Core\'s 400-tick\n'
     u'            // game-over countdown, and cheap: a bool, then a scan that stops at the\n'
     u'            // first living employee.\n'
     u'            if (now % 60 == 30) { TickFacilityRelief(); }')

# --------------------------------------------------------- keyed strings
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Requests.xml')
s = io.open(p, encoding='utf-8-sig').read()
block = u"""  <RR_Event_FacilityRelief>A corporation clean-up team cleared the site, requisitioned a replacement crew and left supplies. The branch is open again.</RR_Event_FacilityRelief>
  <RR_Relief_Title>Clean-up team</RR_Relief_Title>
  <RR_Relief_Body>The parent corporation does not write off a branch it has on its books.

A clean-up team came in on all-access passes, removed {1} hostiles from the site and left. Behind them: {0} replacement staff and enough supplies to start again.

Nobody asked {2} whether it wanted the help, and no invoice came with it. The crew are on the ordinary wage from today.</RR_Relief_Body>
"""
anchor = u'  <RR_Event_CorporationContact>'
assert anchor in s, 'keyed anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('updated keyed strings')
ET.parse(p)
print('keyed XML parses clean')
