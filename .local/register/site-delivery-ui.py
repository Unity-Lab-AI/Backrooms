# -*- coding: utf-8 -*-
"""Offer stockpiles at every place the branch may receive, not only the headquarters."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'UI', 'OperationsProcurement.cs')

sub(p, u"""        private static List<Zone_Stockpile> HeadquartersStockpiles(RimroomsCampaignComponent campaign)
        {
            if (campaign.Headquarters == null || campaign.Headquarters.zoneManager == null) { return new List<Zone_Stockpile>(); }
            return campaign.Headquarters.zoneManager.AllZones.OfType<Zone_Stockpile>()
                .Where(zone => zone != null && zone.Map == campaign.Headquarters)
                .OrderBy(zone => zone.label, StringComparer.CurrentCultureIgnoreCase).ThenBy(zone => zone.ID).ToList();
        }""",
u"""        /// <summary>
        /// Every stockpile the supplier will unload into: the headquarters', and those at any site
        /// the branch has put on the books.
        ///
        /// **Arc 5's "company-to-site logistics".** This listed only the headquarters', which
        /// meant a registered site could be billed for daily and never receive a shipment — the
        /// paperwork without the point.
        ///
        /// Headquarters first, then sites in registration order, and within a map by label. An
        /// ordinal tiebreak on the zone ID so the list cannot follow scan order and shuffle
        /// between openings (invariant 26, applied to a menu).
        /// </summary>
        private static List<Zone_Stockpile> DeliveryStockpiles(RimroomsCampaignComponent campaign)
        {
            var zones = new List<Zone_Stockpile>();
            foreach (Map destination in campaign.DeliveryDestinations())
            {
                if (destination == null || destination.zoneManager == null) { continue; }
                zones.AddRange(destination.zoneManager.AllZones.OfType<Zone_Stockpile>()
                    .Where(zone => zone != null && zone.Map == destination)
                    .OrderBy(zone => zone.label, StringComparer.CurrentCultureIgnoreCase)
                    .ThenBy(zone => zone.ID));
            }
            return zones;
        }

        /// <summary>
        /// A stockpile's name, said with where it is when the branch holds more than one place.
        ///
        /// Qualified only when it needs to be: a branch with a headquarters and nothing else would
        /// read "Stockpile (headquarters)" on every row, which is noise teaching nothing.
        /// </summary>
        private static string StockpileLabel(RimroomsCampaignComponent campaign, Zone_Stockpile zone)
        {
            if (zone == null) { return string.Empty; }
            if (campaign.DeliveryDestinations().Count <= 1) { return zone.label; }
            string where = zone.Map == campaign.Headquarters
                ? "RR_Proc_AtHeadquarters".Translate().ToString()
                : (zone.Map.Parent == null ? zone.Map.ToString() : zone.Map.Parent.LabelCap);
            return "RR_Proc_ZoneAtPlace".Translate(zone.label, where).ToString();
        }""")

sub(p, u'            List<Zone_Stockpile> zones = HeadquartersStockpiles(campaign);',
       u'            List<Zone_Stockpile> zones = DeliveryStockpiles(campaign);')

# The menu says where each stockpile is.
sub(p, u"""                bool accepts = itemDef == null || (captured.settings != null && captured.settings.AllowedToAccept(itemDef));
                string label = captured.label + (accepts ? "" : " - " + "RR_Proc_ZoneFilterRejects".Translate().ToString());""",
u"""                bool accepts = itemDef == null || (captured.settings != null && captured.settings.AllowedToAccept(itemDef));
                RimroomsCampaignComponent labelCampaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                string name = labelCampaign == null ? captured.label : StockpileLabel(labelCampaign, captured);
                string label = name + (accepts ? "" : " - " + "RR_Proc_ZoneFilterRejects".Translate().ToString());""")
print('procurement UI now offers site stockpiles')

# ------------------------------------------------------------------ strings
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Procurement.xml')
s = io.open(p, encoding='utf-8-sig').read()
for key in ('RR_Proc_AtHeadquarters', 'RR_Proc_ZoneAtPlace'):
    assert key not in s, key
block = (u'  <RR_Proc_AtHeadquarters>headquarters</RR_Proc_AtHeadquarters>\n'
         u'  <RR_Proc_ZoneAtPlace>{0} at {1}</RR_Proc_ZoneAtPlace>\n')
i = s.rindex(u'</LanguageData>')
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + block + s[i:])
ET.parse(p)
print('strings added and parsed')
