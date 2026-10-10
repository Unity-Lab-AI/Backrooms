# -*- coding: utf-8 -*-
"""Arc 5's exit plan: a gate may be built at a registered site, not only at headquarters."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ one place-set, two questions
sub(os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'RemoteSites.cs'),
    u"""        public bool CanReceiveDeliveryAt(Map map)
        {
            if (map == null || !Find.Maps.Contains(map)) { return false; }
            if (headquarters == map) { return true; }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record != null && record.Live && record.site == map.Parent) { return true; }
            }
            return false;
        }""",
u"""        public bool CanReceiveDeliveryAt(Map map) { return IsBranchPlace(map); }

        /// <summary>
        /// Whether the branch **operates** here: whether it may build and run a facility on this
        /// map, which arc 5 calls the site's *"exit plan"* — a gate of its own.
        ///
        /// **A separate question from <see cref="CanReceiveDeliveryAt"/> that currently has the
        /// same answer.** Both delegate to one place-set so they cannot drift while they agree,
        /// and they are named apart because they are not the same thing: a site could one day be
        /// too remote for a supplier and still perfectly fine to build a gate on, and at that
        /// point one predicate would be wrong for one of them.
        /// </summary>
        public bool OperatesAt(Map map) { return IsBranchPlace(map); }

        /// <summary>
        /// The headquarters, or a site on the books the branch can currently reach.
        ///
        /// **A Backrooms coordinate is excluded by construction**, because it can never be
        /// registered — which is what keeps a designated gate out of a coordinate without a
        /// second check to forget. Invariant 12: what is down there is a natural gate, with no
        /// operator, no power and no address book, and it is not the company's doing.
        /// </summary>
        private bool IsBranchPlace(Map map)
        {
            if (map == null || !Find.Maps.Contains(map)) { return false; }
            if (headquarters == map) { return true; }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record != null && record.Live && record.site == map.Parent) { return true; }
            }
            return false;
        }""")
print('OperatesAt added beside CanReceiveDeliveryAt')

# ------------------------------------------------------------------ the gate stops being HQ-only
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Gate', 'NativeGateBinding.cs')
sub(p, u"""        private bool SameNativeHeadquartersThing(Thing thing)
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            return campaign != null && campaign.CanOperate && campaign.Headquarters != null &&
                parent.Spawned && parent.Map == campaign.Headquarters && parent.Faction == Faction.OfPlayer &&
                thing != null && !thing.Destroyed && thing.Spawned && thing.Map == parent.Map && thing.Faction == Faction.OfPlayer;
        }""",
u"""        /// <summary>
        /// Whether this thing is player-owned infrastructure standing **on the same map as the
        /// gate**, at a place the branch operates.
        ///
        /// **Arc 5's exit plan.** This used to require `parent.Map == campaign.Headquarters`, so a
        /// gate could only ever be designated at the headquarters and the arc's *"exit plan"* was
        /// unreachable however many sites a branch held. It now asks
        /// <see cref="RimroomsCampaignComponent.OperatesAt"/>: the headquarters, or a site on the
        /// books.
        ///
        /// **A Backrooms coordinate is still excluded**, because a coordinate can never be
        /// registered as a site. What is down there is a natural gate — no operator, no power, no
        /// address book — and invariant 12 keeps it that way without a second check to forget.
        ///
        /// **The `thing.Map == parent.Map` clause is untouched, and it is the good consequence.**
        /// A gate at a remote site needs its own console, its own bound battery and its own
        /// assembly bench **at that site**. You cannot run a gate at the far end of the world off
        /// the equipment in your headquarters, which is exactly what *"remote sites need people,
        /// supplies, signals, protection, and an exit plan"* is asking for.
        ///
        /// The name is kept. Eleven call sites read it as "the branch's own infrastructure, here",
        /// which is what it has always meant and still means; only the set of valid "here"s grew.
        /// </summary>
        private bool SameNativeHeadquartersThing(Thing thing)
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            return campaign != null && campaign.CanOperate && campaign.OperatesAt(parent.Map) &&
                parent.Spawned && parent.Faction == Faction.OfPlayer &&
                thing != null && !thing.Destroyed && thing.Spawned && thing.Map == parent.Map && thing.Faction == Faction.OfPlayer;
        }""")
print('gate binding widened to any place the branch operates')

# ------------------------------------------------------------------ the refusal stops saying HQ
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_NativeGate.xml')
sub(p, u'  <RR_NativeGate_HeadquartersRequired>Choose existing player-owned infrastructure on the active company headquarters map.</RR_NativeGate_HeadquartersRequired>',
       u'  <RR_NativeGate_HeadquartersRequired>Choose existing player-owned infrastructure standing on this same map, at the headquarters or at a site the branch has on the books. A gate runs on the equipment beside it, never on equipment somewhere else.</RR_NativeGate_HeadquartersRequired>')
ET.parse(p)
print('refusal string corrected and parsed')
