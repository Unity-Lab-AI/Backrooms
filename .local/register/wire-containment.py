# -*- coding: utf-8 -*-
"""Wire the containment procedure: campaign state, the tick, and the tenth facility category."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


CAMPAIGN = "src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs"

# ------------------------------------------------------------------ the two saved fields
sub(CAMPAIGN, u"        private bool corporationContact;\n",
    u"""        private bool corporationContact;

        /// <summary>
        /// The branch's standing order for a containment failure: cut every open connection.
        ///
        /// **Defaults to true**, which is the safe reading and also the one a save written
        /// before this field existed gets for free — `Scribe_Values` hands back the default
        /// for a missing field, so an older save loads with the procedure armed rather than
        /// with a silently disarmed one. See <see cref="ContainmentProtocol"/>.
        /// </summary>
        private bool cutConnectionsOnBreach = true;

        /// <summary>
        /// Whether the procedure has already fired for the incident in progress. Latched so a
        /// second subject starting to escape during the same breach does not slam the doors a
        /// second time, and cleared only when nothing anywhere is getting out.
        ///
        /// Saved, because a save made mid-breach must reload mid-breach rather than re-firing
        /// the procedure and sending a second letter about connections that are already shut.
        /// </summary>
        private bool breachResponded;
""")

# ------------------------------------------------------------------ the accessors
sub(CAMPAIGN, u"        public bool CorporationContact { get { return corporationContact; } }",
    u"""        public bool CorporationContact { get { return corporationContact; } }

        public bool CutConnectionsOnBreach { get { return cutConnectionsOnBreach; } }

        public bool BreachResponded { get { return breachResponded; } }

        // Written only through ContainmentProtocol, which owns every rule about when the
        // procedure runs. These are stores, not decisions.
        internal void SetCutConnectionsOnBreach(bool cut) { cutConnectionsOnBreach = cut; }

        internal void NoteBreachResponded() { breachResponded = true; }

        internal void ClearBreachResponded() { breachResponded = false; }""")

# ------------------------------------------------------------------ persistence
sub(CAMPAIGN,
    u'            Scribe_Values.Look(ref corporationContact, "rr_corporationContact", false);',
    u'            Scribe_Values.Look(ref corporationContact, "rr_corporationContact", false);\n'
    u'            Scribe_Values.Look(ref cutConnectionsOnBreach, "rr_cutConnectionsOnBreach", true);\n'
    u'            Scribe_Values.Look(ref breachResponded, "rr_breachResponded", false);')

# ------------------------------------------------------------------ the tick
sub("src/RimroomsAsyncIndustries/Company/CampaignServices.cs",
    u"            // The clean-up team. Checked often enough to land inside Core's 400-tick",
    u"""            // The containment procedure. Same cadence as the clean-up team and for the same
            // reason: it has to land inside the window where a response still means something,
            // and it is cheap -- a latched bool, then a holder list that is built at most once
            // per tick and is empty on any branch holding nothing.
            if (now % 60 == 15) { ContainmentProtocol.TickProcedure(this); }
            // The clean-up team. Checked often enough to land inside Core's 400-tick""")

# ------------------------------------------------------------------ capability matching
sub("src/RimroomsAsyncIndustries/Facilities/FacilityReport.cs",
    u"""        public List<string> buildingDefNames = new List<string>();
        public bool includePowerSources;
        public int displayOrder;""",
    u"""        public List<string> buildingDefNames = new List<string>();
        public bool includePowerSources;

        /// <summary>
        /// Match anything that can hold a contained subject, by **capability** rather than by
        /// name: any building carrying `CompEntityHolder`, plus any bed Core classifies as a
        /// prisoner bed.
        ///
        /// Named defs were the first design and were wrong twice over. `HoldingPlatform` is an
        /// Anomaly defName, so a `<li>` naming it would be read by `check-dlc-gating.py` as an
        /// ungated expansion reference; and a named list covers no modded holder. Matching the
        /// comp covers a modded holder for free, needs no gate at all because
        /// `CompEntityHolder` lives in the always-present base assembly, and on an install
        /// without Anomaly simply matches nothing.
        ///
        /// Prisoner beds are in because containment is not an Anomaly-only idea in this mod: a
        /// branch holding somebody it brought back is a branch with a containment problem, and
        /// on a Core-only install that is the only kind there is.
        /// </summary>
        public bool includeContainment;

        public int displayOrder;""")

sub("src/RimroomsAsyncIndustries/Facilities/FacilityReport.cs",
    u"""            return (buildingDefNames != null && buildingDefNames.Contains(building.def.defName)) || (includePowerSources &&
                (building.TryGetComp<CompPowerPlant>() != null || building.TryGetComp<CompPowerBattery>() != null));""",
    u"""            if (includeContainment)
            {
                if (building.TryGetComp<CompEntityHolder>() != null) { return true; }
                var bed = building as Building_Bed;
                if (bed != null && bed.ForPrisoners) { return true; }
            }
            return (buildingDefNames != null && buildingDefNames.Contains(building.def.defName)) || (includePowerSources &&
                (building.TryGetComp<CompPowerPlant>() != null || building.TryGetComp<CompPowerBattery>() != null));""")

print("containment wired")
