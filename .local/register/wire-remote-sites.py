# -*- coding: utf-8 -*-
"""Wire remote sites into save, ownership, billing, the pane list and the strings."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ save
sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'RimroomsCampaignComponent.cs'),
    u'            ExposeSoloGroupHints();',
    u'            ExposeSoloGroupHints();\n            ExposeRemoteSites();')

p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'CampaignServices.cs')

# ------------------------------------------------------------------ ownership, the third clause
sub(p, u"""            if (headquarters == map) { return true; }
            RimroomsDestinationMapParent site = map.Parent as RimroomsDestinationMapParent;
            return site != null && coordinates.Any(record => record != null &&
                record.site == site && record.id == site.CoordinateId);""",
u"""            if (headquarters == map) { return true; }
            RimroomsDestinationMapParent site = map.Parent as RimroomsDestinationMapParent;
            if (site != null)
            {
                return coordinates.Any(record => record != null &&
                    record.site == site && record.id == site.CoordinateId);
            }
            // Arc 5's third clause. A registered site is the branch's own place, so connected
            // work reaches it, a gate may anchor there and a way out may come up on it -- which
            // is *"people, supplies, signals, protection, and an exit plan"* stated as one
            // predicate rather than five features. A coordinate is checked above and returns
            // there either way, because a destination is never a base.
            return IsRegisteredRemoteSite(map);""")

# ------------------------------------------------------------------ the bill
sub(p, u"""                AddObligation(dayId + ":overhead", "RR_Ledger_Overhead", dailyOverheadUsd, nextOperatingCostTick);""",
u"""                AddObligation(dayId + ":overhead", "RR_Ledger_Overhead", dailyOverheadUsd, nextOperatingCostTick);
                // Arc 5: *"a remote base is a costly responsibility rather than free map
                // ownership"*. Its own obligation rather than folded into overhead, so the
                // player can see on the ledger what the places are costing them and decide
                // whether to keep them. Zero for a branch holding none, which is every branch
                // until somebody registers one.
                AddObligation(dayId + ":sites", "RR_Ledger_RemoteSites",
                    DailyRemoteSiteOverheadUsd, nextOperatingCostTick);""")
print('save, ownership and billing wired')

# ------------------------------------------------------------------ the pane
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'UI', 'MainTabWindow_Operations.cs')
sub(p, u'"RR_UI_Facilities", "RR_UI_Procurement" };',
       u'"RR_UI_Facilities", "RR_UI_Procurement", "RR_UI_Sites" };')
sub(p, u'                case 10: DrawProcurement(listing, campaign); break;',
       u'                case 10: DrawProcurement(listing, campaign); break;\n'
       u'                case 11: DrawRemoteSites(listing, campaign); break;')
print('sites pane added')

# ------------------------------------------------------------------ the strings
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Operations.xml')
s = io.open(p, encoding='utf-8-sig').read()
block = u"""  <RR_UI_Sites>Sites</RR_UI_Sites>
  <RR_Sites_Heading>Places this branch runs beyond its headquarters.</RR_Sites_Heading>
  <RR_Sites_Summary>{0} of {1} sites on the books, costing {2} a day on top of ordinary overhead.</RR_Sites_Summary>
  <RR_Sites_None>None. Nothing is being paid for, and nothing beyond headquarters is the branch's responsibility.</RR_Sites_None>
  <RR_Sites_Row>{0} - on the books and reachable.</RR_Sites_Row>
  <RR_Sites_RowUnreachable>{0} - on the books but out of reach. It is not being billed while that is true.</RR_Sites_RowUnreachable>
  <RR_Sites_Release>Take {0} off the books</RR_Sites_Release>
  <RR_Sites_RegisterCurrent>Put {0} on the books</RR_Sites_RegisterCurrent>
  <RR_Sites_NoCurrentMap>No map in view to register.</RR_Sites_NoCurrentMap>
  <RR_Sites_BlockedHeadquarters>This is the headquarters. It is already the branch's own place.</RR_Sites_BlockedHeadquarters>
  <RR_Sites_BlockedCoordinate>A Backrooms coordinate is somewhere you go, not somewhere you keep.</RR_Sites_BlockedCoordinate>
  <RR_Sites_BlockedNotYours>The branch does not hold this place.</RR_Sites_BlockedNotYours>
  <RR_Sites_BlockedAlready>Already on the books.</RR_Sites_BlockedAlready>
  <RR_Sites_BlockedTooMany>The branch is running as many places as it can account for.</RR_Sites_BlockedTooMany>
  <RR_Site_MapUnavailable>That map is not available.</RR_Site_MapUnavailable>
  <RR_Site_IsHeadquarters>The headquarters is not a remote site.</RR_Site_IsHeadquarters>
  <RR_Site_CoordinateNotASite>A Backrooms coordinate is a destination, not a base.</RR_Site_CoordinateNotASite>
  <RR_Site_NotYours>The branch does not hold that place.</RR_Site_NotYours>
  <RR_Site_TooMany>The branch cannot account for another site.</RR_Site_TooMany>
  <RR_Site_NotRegistered>That site is not on the books.</RR_Site_NotRegistered>
  <RR_Ledger_RemoteSites>Remote sites</RR_Ledger_RemoteSites>
  <RR_Event_RemoteSiteRegistered>A place beyond headquarters went on the books. It costs something every day now.</RR_Event_RemoteSiteRegistered>
  <RR_Event_RemoteSiteReleased>A place came off the books. No fee, no notice, and the colony there is still the player's own business.</RR_Event_RemoteSiteReleased>
"""
for key in ('RR_UI_Sites', 'RR_Sites_Heading', 'RR_Ledger_RemoteSites'):
    assert key not in s, key
i = s.rindex(u'</LanguageData>')
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + block + s[i:])
ET.parse(p)
print('strings added and parsed')
