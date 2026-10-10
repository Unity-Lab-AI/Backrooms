# -*- coding: utf-8 -*-
"""Attach the alarm gizmo, add the facilities-pane protocol row, the def, and the strings."""
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


# ------------------------------------------------------------------ the gizmo
SKIP = ("src/RimroomsAsyncIndustries/Gate/CompRimroomsGateConsole.cs",
    u"            foreach (Gizmo gizmo in Company.CorporateContactGizmo.For(parent))",
    u"            foreach (Gizmo gizmo in Company.ContainmentAlarmGizmo.For(parent))\n"
    u"            { yield return gizmo; }\n"
    u"            foreach (Gizmo gizmo in Company.CorporateContactGizmo.For(parent))")

# ------------------------------------------------------------------ the tenth category
sub("Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsFacilityDefs/RR_FacilityCategories.xml",
    u"  <RimroomsAsyncIndustries.Facilities.RimroomsFacilityCategoryDef>\n"
    u"    <defName>RR_Facility_Storage</defName>",
    u"""  <!-- Containment is matched by capability rather than by name, so there is no
       buildingDefNames list here at all: includeContainment picks up anything carrying
       CompEntityHolder plus any bed Core classifies as a prisoner bed. Naming the shipped
       holding platform would have been an ungated expansion reference in a Core-only mod,
       and would have covered no modded holder. -->
  <RimroomsAsyncIndustries.Facilities.RimroomsFacilityCategoryDef>
    <defName>RR_Facility_Containment</defName><label>containment</label><description>Where what you brought back is held. A platform without power is a platform that is about to let go, and a branch that cannot see its own containment from the far side of a gate finds out about a breach when it walks into one.</description><displayOrder>95</displayOrder>
    <includeContainment>true</includeContainment>
  </RimroomsAsyncIndustries.Facilities.RimroomsFacilityCategoryDef>
  <RimroomsAsyncIndustries.Facilities.RimroomsFacilityCategoryDef>
    <defName>RR_Facility_Storage</defName>""")

print("gizmo and def wired")
