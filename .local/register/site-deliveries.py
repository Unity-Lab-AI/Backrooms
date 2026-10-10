# -*- coding: utf-8 -*-
"""Company-to-site logistics: procurement may deliver to a registered site.

Arc 5 names "company-to-site logistics" and procurement was pinned to the headquarters in seven
places -- but `ProcurementOrderRecord.receivingMap` already existed and the DELIVERY path already
used it. Only the selection and its validation were fixed, so this widens the selection and fixes
a latent bug the widening would otherwise have exposed.
"""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ where a branch may receive
sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'RemoteSites.cs'),
    u'''        /// <summary>Whether this map is a registered site. The third clause of <c>OwnsMap</c>.</summary>''',
u'''        /// <summary>
        /// Whether the parent corporation will deliver a shipment to this map.
        ///
        /// **Arc 5 names "company-to-site logistics"**, and procurement had the headquarters
        /// written into it in seven places. The headquarters, or any site on the books that the
        /// branch can currently reach — and nowhere else, because a supplier will not unload into
        /// a place the branch has not accepted responsibility for.
        ///
        /// A Backrooms coordinate is excluded by construction: it can never be registered, so it
        /// can never be a delivery address. Which is correct — a supplier does not drive into a
        /// hole in the world.
        /// </summary>
        public bool CanReceiveDeliveryAt(Map map)
        {
            if (map == null || !Find.Maps.Contains(map)) { return false; }
            if (headquarters == map) { return true; }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record != null && record.Live && record.site == map.Parent) { return true; }
            }
            return false;
        }

        /// <summary>Somewhere a shipment may be sent, for a menu. Headquarters first.</summary>
        public List<Map> DeliveryDestinations()
        {
            List<Map> destinations = new List<Map>();
            if (headquarters != null && Find.Maps.Contains(headquarters)) { destinations.Add(headquarters); }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record == null || !record.Live || record.site.Map == null) { continue; }
                if (!destinations.Contains(record.site.Map)) { destinations.Add(record.site.Map); }
            }
            return destinations;
        }

        /// <summary>Whether this map is a registered site. The third clause of <c>OwnsMap</c>.</summary>''')
print('CanReceiveDeliveryAt added')

p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Procurement', 'RimroomsProcurementComponent.cs')

# ------------------------------------------------------------------ quoting
sub(p, u"""            if (!IsReceivingZoneValid(campaign.Headquarters, receivingZone, itemDef))
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }

            int stackLimit = CurrentStackLimit(itemDef);""",
u"""            // The destination is the zone's own map, not the headquarters. A stockpile already
            // knows where it is, so nothing has to be passed in and the two can never disagree.
            Map destination = receivingZone == null ? null : receivingZone.Map;
            if (!campaign.CanReceiveDeliveryAt(destination))
            { return CompanyActionResult.Refused("RR_Proc_DestinationNotOnTheBooks"); }
            if (!IsReceivingZoneValid(destination, receivingZone, itemDef))
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }

            int stackLimit = CurrentStackLimit(itemDef);""")

sub(p, u'                receivingMap = campaign.Headquarters,',
       u'                receivingMap = destination,')

# ------------------------------------------------------------------ accepting
sub(p, u"""                !IsReceivingZoneValid(campaign.Headquarters, quote.receivingZone, itemDef) ||
                quote.receivingMap != campaign.Headquarters || quote.receivingZoneId != quote.receivingZone.ID)""",
u"""                !IsReceivingZoneValid(quote.receivingMap, quote.receivingZone, itemDef) ||
                !campaign.CanReceiveDeliveryAt(quote.receivingMap) ||
                quote.receivingZone.Map != quote.receivingMap ||
                quote.receivingZoneId != quote.receivingZone.ID)""")

# ------------------------------------------------------------------ redirecting, and the latent bug
sub(p, u"""            if (!IsReceivingZoneValid(campaign.Headquarters, receivingZone, itemDef))
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }
            if (order.receivingZone == receivingZone) { return CompanyActionResult.Existing(); }""",
u"""            Map redirectTo = receivingZone == null ? null : receivingZone.Map;
            if (!campaign.CanReceiveDeliveryAt(redirectTo))
            { return CompanyActionResult.Refused("RR_Proc_DestinationNotOnTheBooks"); }
            if (!IsReceivingZoneValid(redirectTo, receivingZone, itemDef))
            { return CompanyActionResult.Refused("RR_Proc_ReceivingZoneInvalid"); }
            if (order.receivingZone == receivingZone) { return CompanyActionResult.Existing(); }""")

sub(p, u"""            order.receivingZone = receivingZone;
            order.receivingZoneId = receivingZone.ID;
            order.receivingZoneLabel = receivingZone.label;""",
u"""            // **`receivingMap` was NOT updated here, and that was a latent bug.** It was
            // harmless while every zone lived on the one allowed map; the moment a second map
            // became legal, redirecting across maps would leave the order pointing at the old
            // one, and the delivery check compares the zone against `order.receivingMap` --
            // so the shipment would be refused every attempt, for ever, awaiting a condition
            // that could never come true.
            order.receivingMap = redirectTo;
            order.receivingZone = receivingZone;
            order.receivingZoneId = receivingZone.ID;
            order.receivingZoneLabel = receivingZone.label;""")

# ------------------------------------------------------------------ the delivery-time message
sub(p, u"""            if (!Find.Maps.Contains(order.receivingMap))
            { SetAwaiting(order, "RR_Proc_HeadquartersUnavailable", now); return 0; }""",
u"""            // A site's map can be unloaded while the headquarters' cannot, so the reason had to
            // stop saying "HQ". The shipment waits rather than failing: the cargo is held and the
            // payment is already recorded.
            if (!Find.Maps.Contains(order.receivingMap))
            { SetAwaiting(order, "RR_Proc_ReceivingMapUnavailable", now); return 0; }""")
print('procurement widened to registered sites, and the redirect bug fixed')

# ------------------------------------------------------------------ strings
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Procurement.xml')
s = io.open(p, encoding='utf-8-sig').read()
for key in ('RR_Proc_DestinationNotOnTheBooks', 'RR_Proc_ReceivingMapUnavailable'):
    assert key not in s, key
block = (u'  <RR_Proc_DestinationNotOnTheBooks>The supplier will not unload there. A shipment goes '
         u'to headquarters, or to a site this branch has put on the books.</RR_Proc_DestinationNotOnTheBooks>\n'
         u'  <RR_Proc_ReceivingMapUnavailable>The place this shipment is bound for is not loaded. '
         u'The paid order and its held cargo remain saved.</RR_Proc_ReceivingMapUnavailable>\n')
i = s.rindex(u'</LanguageData>')
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + block + s[i:])
ET.parse(p)
print('strings added and parsed')
