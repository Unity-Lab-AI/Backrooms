# -*- coding: utf-8 -*-
"""Plant every fault the tier 4 proof exists to catch, including the ones about absences."""
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join('.local', 'register', 'proof-research-tier4.py')

DEFS = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Defs', 'RimroomsProjectDefs',
                    'RR_CompanyProjects.xml')
GATE = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGate.cs')
FRONTIER = os.path.join('src', 'RimroomsAsyncIndustries', 'Portals', 'NaturalFrontierService.cs')
PRESSURE = os.path.join('src', 'RimroomsAsyncIndustries', 'Threats', 'BackroomsPressure.cs')
SPINUP = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'GateSpinUp.cs')

FAULTS = [
    ('a tier 4 project grants a capability nothing reads', DEFS,
     u'<li>RR_Cap_SteadyNerve</li>',
     u'<li>RR_Cap_NerveOfSteel</li>'),

    ('a tier 4 prerequisite points at another branch', DEFS,
     u'<li>RR_Spatial_CoordinateReading</li></prerequisiteProjects>',
     u'<li>RR_Commerce_SiteEfficiency</li></prerequisiteProjects>'),

    ('a seventh tier 4 project appears for Logistics', DEFS,
     u'    <defName>RR_Entities_SteadyNerve</defName>',
     u'''    <defName>RR_Logistics_Somehow</defName>
    <label>Somehow</label>
    <description>Promises something.</description>
    <insightCost>5</insightCost>
    <workRequired>18000</workRequired>
    <minimumIntellectual>7</minimumIntellectual>
  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>
    <defName>RR_Entities_SteadyNerve</defName>'''),

    ('a fifth rung is added to the gate ladder', GATE,
     u'            "RR_GateStandingConnection",\n        };',
     u'            "RR_GateStandingConnection",\n            "RR_GateSomethingMore",\n        };'),

    ('the per-coordinate frontier cap becomes a research knob', FRONTIER,
     u'                    Cap = MaximumFrontiersPerCoordinate,',
     u'                    Cap = campaign.HasCapability("RR_Cap_SurfaceReading") ? 3 : MaximumFrontiersPerCoordinate,'),

    ('the natural depth reach becomes a research knob', FRONTIER,
     u'        internal const int MaximumNaturalDepth = 3;',
     u'        internal const int MaximumNaturalDepth = 4;'),

    ('the penalty ceiling drops to the minimum', PRESSURE,
     u'        private const int SteadyNervePenalty = 6;',
     u'        private const int SteadyNervePenalty = 1;'),

    ('practised dialling makes a gate free', SPINUP,
     u'        private const float PractisedDiallingFactor = 0.8f;',
     u'        private const float PractisedDiallingFactor2 = 0.8f;'),
]


def run():
    p = subprocess.Popen([sys.executable, PROOF], cwd=REPO,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()[0].decode('utf-8', 'replace')
    return p.returncode, out


def full(rel):
    return os.path.join(REPO, rel)


backups = {}
for _, rel, _, _ in FAULTS:
    if rel not in backups:
        backups[rel] = io.open(full(rel), encoding='utf-8').read()

print('  planted fault                                              exit  caught')
ok = True
for label, rel, old, new in FAULTS:
    s = backups[rel]
    assert old in s, 'fault anchor missing in %s: %r' % (rel, old[:70])
    assert s.count(old) == 1, 'fault anchor not unique in %s: %r' % (rel, old[:70])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    code, out = run()
    caught = code != 0
    print('  %-57s %-5d %s' % (label, code, 'yes' if caught else 'NO -- THE PROOF IS BLIND'))
    if not caught:
        ok = False
        print(out[-500:])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s)

code, out = run()
print('  %-57s %-5d %s' % ('restored', code, 'clean' if code == 0 else 'STILL FAILING'))
sys.exit(0 if ok and code == 0 else 1)
