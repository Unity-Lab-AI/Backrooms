# -*- coding: utf-8 -*-
"""Remote sites need people: a shipment waits until somebody is there to receive it."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ who is where
sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'RemoteSites.cs'),
    u'        /// <summary>Somewhere a shipment may be sent, for a menu. Headquarters first.</summary>',
u'''        /// <summary>
        /// Whether anybody the branch employs is actually standing at this place.
        ///
        /// **Arc 5: *"remote sites need people"*.** A site with nobody at it is a line on a
        /// ledger, and the consequence is that a shipment bound for it **waits** — a supplier
        /// does not unload into an empty field with nobody to sign for it.
        ///
        /// **Employed, alive, and present.** Not downed: somebody unconscious on the floor cannot
        /// take delivery of anything, and pretending otherwise would make the rule a formality.
        /// A prisoner or a slave is not staff and never counted.
        ///
        /// Checked live. A site is staffed when people are there and unstaffed the moment they
        /// leave, which is the honest reading of *"needs people"* and needs no assignment to
        /// maintain, no record to go stale and nothing for the player to remember to update.
        /// </summary>
        public bool IsSiteStaffed(Map map)
        {
            if (map == null) { return false; }
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn pawn = member.pawn;
                if (pawn == null || pawn.Dead || pawn.Destroyed || !pawn.Spawned) { continue; }
                if (pawn.Map != map || pawn.Downed) { continue; }
                if (pawn.IsPrisoner || pawn.IsSlave) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether a shipment may actually be unloaded here **now**.
        ///
        /// Distinct from <see cref="CanReceiveDeliveryAt"/> on purpose, and the split is the whole
        /// design of this piece:
        ///
        /// * **The address** is acceptable if the place is on the books. A player may order ahead
        ///   while the crew is still walking there, which is what anybody would actually do.
        /// * **The arrival** needs somebody present. The shipment waits, the cargo stays held and
        ///   the payment stays recorded — nothing is lost and the fix is obvious.
        ///
        /// Gating the order instead would have punished planning, and gating nothing would have
        /// made *"remote sites need people"* a sentence in a document.
        ///
        /// **The headquarters is never held to this.** A branch with nobody alive at home has a
        /// bigger problem, and the clean-up team already owns it.
        /// </summary>
        public bool CanUnloadAt(Map map)
        {
            if (!CanReceiveDeliveryAt(map)) { return false; }
            if (map == headquarters) { return true; }
            return IsSiteStaffed(map);
        }

        /// <summary>Somewhere a shipment may be sent, for a menu. Headquarters first.</summary>''')
print('IsSiteStaffed and CanUnloadAt added')

# ------------------------------------------------------------------ arrival waits for people
sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Procurement',
                 'RimroomsProcurementComponent.cs'),
    u"""            if (!Find.Maps.Contains(order.receivingMap))
            { SetAwaiting(order, "RR_Proc_ReceivingMapUnavailable", now); return 0; }""",
u"""            if (!Find.Maps.Contains(order.receivingMap))
            { SetAwaiting(order, "RR_Proc_ReceivingMapUnavailable", now); return 0; }
            // Arc 5: *"remote sites need people"*. A supplier does not unload into an empty field
            // with nobody to sign for it, so the shipment WAITS rather than failing -- the cargo
            // is held, the payment is recorded, and it lands as soon as somebody is there.
            //
            // Checked at arrival and not at ordering, deliberately: a player should be able to
            // order ahead while the crew is still walking there.
            if (!campaign.CanUnloadAt(order.receivingMap))
            { SetAwaiting(order, "RR_Proc_SiteUnstaffed", now); return 0; }""")
print('arrival now waits for somebody to be there')

# ------------------------------------------------------------------ the pane says which
sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'UI', 'OperationsRemoteSites.cs'),
    u"""                    listing.Label(record.Live
                        ? "RR_Sites_Row".Translate(record.Label).ToString()
                        : "RR_Sites_RowUnreachable".Translate(record.Label).ToString());""",
u"""                    // Three states, not two. "Reachable but nobody there" is the one a player
                    // needs to see, because it is the one that quietly holds their shipments.
                    string row;
                    if (!record.Live) { row = "RR_Sites_RowUnreachable".Translate(record.Label).ToString(); }
                    else if (!campaign.IsSiteStaffed(record.Site.Map))
                    { row = "RR_Sites_RowUnstaffed".Translate(record.Label).ToString(); }
                    else { row = "RR_Sites_Row".Translate(record.Label).ToString(); }
                    listing.Label(row);""")
print('sites pane now shows staffing')

# ------------------------------------------------------------------ strings
for rel, keys, block in [
    (os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed',
                  'RR_Procurement.xml'),
     ['RR_Proc_SiteUnstaffed'],
     u'  <RR_Proc_SiteUnstaffed>Nobody is at the place this shipment is bound for. The supplier '
     u'will not unload with no one to receive it; the order and its cargo are held until somebody '
     u'is there.</RR_Proc_SiteUnstaffed>\n'),
    (os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed',
                  'RR_Operations.xml'),
     ['RR_Sites_RowUnstaffed'],
     u'  <RR_Sites_RowUnstaffed>{0} - on the books and reachable, but nobody is there. Shipments '
     u'to it will wait.</RR_Sites_RowUnstaffed>\n'),
]:
    p = os.path.join(REPO, rel)
    s = io.open(p, encoding='utf-8-sig').read()
    for key in keys:
        assert key not in s, key
    i = s.rindex(u'</LanguageData>')
    io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + block + s[i:])
    ET.parse(p)
    print('strings added to %s' % os.path.basename(rel))
