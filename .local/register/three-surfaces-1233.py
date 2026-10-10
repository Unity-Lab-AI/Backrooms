# -*- coding: utf-8 -*-
"""Three player-facing surfaces that were missing over mechanics that already worked.

  * **889 -- a confirmation on the beacon sale.** The gizmo shows the total and the click is the
    commitment. With a full beacon that is a large irreversible action, and Core has
    `Dialog_MessageBox.CreateConfirmation` for exactly this.

  * **1010 -- a readout of a coordinate's band.** `CoordinatePressureLadder.BandFor` decides how
    hostile a space is, drives anomaly events and gates incursion, and **has never been shown to a
    player.** The pacing was inferable only by being hurt by it.

  * **832 -- the crossing order on the door.** `PortalCrossingService` and
    `PortalTraversalPolicy.OrderedCrossingFailureKey` both work and are ordered from the Atlas
    pane. What was missing is the order, and its refusal reason, **on the door itself**.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding='utf-8').read()
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    print('edited %s' % rel)


SRC = os.path.join('src', 'RimroomsAsyncIndustries')

# ------------------------------------------------------------------ 889: confirm the sale
edit(os.path.join(SRC, 'Economy', 'CompRimroomsCreditBeacon.cs'),
     u'''                icon = TexCommand.ForbidOff,
                action = SellValuables,
            };''',
     u'''                icon = TexCommand.ForbidOff,
                // Confirmed rather than immediate. Selling everything inside the radius is large
                // and irreversible, and the gizmo's own description is the only warning a player
                // gets otherwise -- read after the click, which is too late. Core ships the
                // confirmation dialog for exactly this, so no window of ours is added.
                action = delegate
                {
                    Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                        "RR_Exchange_SellConfirm".Translate(
                            itemCount.ToString("N0"),
                            (oddValue + ordinaryValue).ToString("N0")),
                        SellValuables, false, null, WindowLayer.Dialog));
                },
            };''')

# ------------------------------------------------------------------ 1010: the band readout
edit(os.path.join(SRC, 'Threats', 'CoordinatePressureLadder.cs'),
     u'        public static Band BandFor(CoordinateRecord coordinate, float colonyWealth)',
     u'''        /// <summary>
        /// The band a player can read, as a keyed label.
        ///
        /// The ladder has decided how hostile a space is since 0.8.4-dev -- it drives anomaly
        /// events and gates incursion -- and **was never shown to anybody.** The pacing was
        /// inferable only by being hurt by it, which is the opposite of invariant 28's learnable
        /// rule.
        ///
        /// Keys are literals rather than built from the enum name. A key assembled at run time
        /// cannot be checked in either direction, and this project has caught that pattern five
        /// times.
        /// </summary>
        public static string BandLabelKey(Band band)
        {
            switch (band)
            {
                case Band.Quiet: return "RR_Band_Quiet";
                case Band.Unsettled: return "RR_Band_Unsettled";
                case Band.Active: return "RR_Band_Active";
                case Band.Hostile: return "RR_Band_Hostile";
                default: return "RR_Band_Quiet";
            }
        }

        public static Band BandFor(CoordinateRecord coordinate, float colonyWealth)''')

print('two surfaces edited; the door order follows in its own file')
