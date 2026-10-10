# -*- coding: utf-8 -*-
"""Natural portals reach through depth 3. Deeper needs a gate the player built."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Portals', 'NaturalFrontierService.cs')

# ------------------------------------------------------------------ the constant
sub(p, u"""        /// <summary>
        /// Roughly one doorway in this many is a frontier.""",
u"""        /// <summary>
        /// The deepest coordinate a found doorway will ever lead to.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"with natural portals deeper to an extent
        /// till they would need to buidl theri own gate"*, and the depth chosen at the fork was
        /// **through depth 3**.
        ///
        /// So the Backrooms hands a branch three bands for free -- the shallow yellow rooms and
        /// two steps in -- and then stops handing out doorways. Going further is a machine's job,
        /// which is the convergence this start needs: the place gives you enough to learn on and
        /// then asks you to become an engineer.
        ///
        /// **This caps going DEEPER, never coming OUT.** The way-out draw runs first and is not
        /// subject to this, because a crew standing at depth 3 must always be able to find a door
        /// that leads home. Capping both would have turned the deepest natural band into a trap,
        /// and invariant 28 forbids an unavoidable failure.
        ///
        /// **It does not restrain the player, only the free doorways.** Owner, verbatim: *"this
        /// is all open eneded they can play how they choose"*. A built gate reaches any depth it
        /// has earned, exactly as before.
        /// </summary>
        internal const int MaximumNaturalDepth = 3;

        /// <summary>
        /// Roughly one doorway in this many is a frontier.""")

# ------------------------------------------------------------------ the cap, at minting
sub(p, u"""            int depth = source == null ? 1 : source.Depth + 1;
            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);""",
u"""            int depth = source == null ? 1 : source.Depth + 1;
            // The natural chain stops here. Checked AFTER the way-out attempt above, so a crew
            // at the deepest natural band can still find a door home -- capping both directions
            // would make that band a trap.
            //
            // Refused rather than silently minting a shallower space: a doorway that led
            // somewhere other than where it should would be a quieter and worse lie than being
            // told plainly that nothing natural goes further than this.
            if (depth > MaximumNaturalDepth)
            { return CompanyActionResult.Refused("RR_Frontier_BeyondNaturalReach"); }
            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);""")

print('natural depth cap wired')

# ------------------------------------------------------------------ the keyed string
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Portals.xml')
s = io.open(p, encoding='utf-8-sig').read()
key = u'  <RR_Frontier_BeyondNaturalReach>The doorway goes on, and nothing anybody can walk through goes with it. Whatever is past this is only reachable through a gate of your own.</RR_Frontier_BeyondNaturalReach>\n'
assert 'RR_Frontier_BeyondNaturalReach' not in s, 'key already present'
i = s.rindex(u'</LanguageData>')
s = s[:i] + key + s[i:]
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
ET.parse(p)
print('keyed string added and parsed')
