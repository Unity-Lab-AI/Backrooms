# -*- coding: utf-8 -*-
"""Plant every fault the corporate-contact proof exists to catch."""
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join('.local', 'register', 'proof-corporate-contact.py')

CONTACT = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'CorporateContact.cs')
GIZMO = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'CorporateContactGizmo.cs')
CONSOLE = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGateConsole.cs')
LINE = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'RequestLine.cs')
STARTS = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Defs', 'RimroomsStartDefs',
                      'RR_Starts.xml')

FAULTS = [
    ('the gizmo stops being yielded, so the call is unreachable again', CONSOLE,
     u'''            foreach (Gizmo gizmo in Company.CorporateContactGizmo.For(parent))
            { yield return gizmo; }''',
     u'            // provider removed'),

    ('the call stops requiring an analysed record', CONTACT,
     u'            if (!AnyAnalysedRecord()) { return "RR_Contact_NoFinding"; }',
     u'            // finding requirement removed'),

    ('the call stops requiring a coordinate', CONTACT,
     u'            if (coordinates.Count == 0) { return "RR_Contact_NoCoordinate"; }',
     u'            // coordinate requirement removed'),

    ('the call stops requiring power', CONTACT,
     u'''            CompPowerTrader power = console.TryGetComp<CompPowerTrader>();
            if (power != null && !power.PowerOn) { return "RR_Contact_Unpowered"; }''',
     u'            // power requirement removed'),

    ('the action trusts the button instead of re-checking', CONTACT,
     u'            string blocker = CorporationCallBlocker(console);\n            if (blocker != null) { return CompanyActionResult.Refused(blocker); }\n\n            CompanyActionResult result = EstablishCorporationContact();',
     u'            CompanyActionResult result = EstablishCorporationContact();'),

    ('the gizmo hides instead of showing its reason', GIZMO,
     u'            if (blocker != null) { call.Disable(blocker.Translate()); }',
     u'            if (blocker != null) { yield break; }'),

    ('the gizmo appears on a machining table too', GIZMO,
     u'            if (!(console is Building_CommsConsole)) { yield break; }',
     u'            // console-kind check removed'),

    ('the tutorial line stops gating on contact, so the call means nothing', LINE,
     u'            if (!corporationContact) { return; }\n            // One at a time. A second offer while the first is open would turn a tutorial that',
     u'            // gate removed\n            // One at a time. A second offer while the first is open would turn a tutorial that'),

    ('a start is given contact instead of earning it', STARTS,
     u'    <beginsInCorporationContact>false</beginsInCorporationContact>\n    <defaultCompanyName>Furniture and Knickknack</defaultCompanyName>',
     u'    <beginsInCorporationContact>true</beginsInCorporationContact>\n    <defaultCompanyName>Furniture and Knickknack</defaultCompanyName>'),
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

print('  planted fault                                                exit  caught')
ok = True
for label, rel, old, new in FAULTS:
    s = backups[rel]
    assert old in s, 'fault anchor missing in %s: %r' % (rel, old[:70])
    assert s.count(old) == 1, 'fault anchor not unique in %s: %r' % (rel, old[:70])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    code, out = run()
    caught = code != 0
    print('  %-59s %-5d %s' % (label, code, 'yes' if caught else 'NO -- THE PROOF IS BLIND'))
    if not caught:
        ok = False
        print(out[-600:])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s)

code, out = run()
print('  %-59s %-5d %s' % ('restored', code, 'clean' if code == 0 else 'STILL FAILING'))
sys.exit(0 if ok and code == 0 else 1)
