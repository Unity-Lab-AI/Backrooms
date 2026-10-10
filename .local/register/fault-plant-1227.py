# -*- coding: utf-8 -*-
"""Plant every fault the approach-cell proof exists to catch."""
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join('.local', 'register', 'proof-gate-approach.py')

WORKER = os.path.join('src', 'RimroomsAsyncIndustries', 'Portals', 'PlaceWorker_GateApproach.cs')
PATCH = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Patches',
                     'RR_GateApproachPlacement.xml')
KEYS = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed',
                    'RR_Portals.xml')

FAULTS = [
    ('a conduit-class passable thing stops being allowed', WORKER,
     u'if (definition.passability == Traversability.Standable) { return AcceptanceReport.WasAccepted; }',
     u'// allowance removed'),

    ('the saved snapshot cell is protected instead of the live one', WORKER,
     u'IntVec3 approach = PortalAddressService.ApproachCellFor(door);',
     u'IntVec3 approach = endpoint.AnchorCell;'),

    ('only the centre cell is tested, not the footprint', WORKER,
     u'CellRect footprint = GenAdj.OccupiedRect(loc, rot, definition.Size);',
     u'CellRect footprint = CellRect.SingleCell(loc);'),

    ('a thrown exception stops allowing the placement', WORKER,
     u'''            catch (Exception)
            {
                // Never let this be the reason somebody cannot build. See the class note.
                return AcceptanceReport.WasAccepted;
            }''',
     u'''            catch (Exception)
            {
                return new AcceptanceReport("broken");
            }'''),

    ('an invalid approach cell starts reserving anyway', WORKER,
     u'if (!approach.IsValid || !footprint.Contains(approach)) { return AcceptanceReport.WasAccepted; }',
     u'if (!footprint.Contains(approach)) { return AcceptanceReport.WasAccepted; }'),

    ('the patch replaces the list instead of appending', PATCH,
     u'    <nomatch Class="PatchOperationAdd">\n'
     u'      <xpath>Defs/ThingDef[@Name="BuildingBase"]</xpath>',
     u'    <nomatch Class="PatchOperationReplace">\n'
     u'      <xpath>Defs/ThingDef[@Name="BuildingBase"]</xpath>'),

    ('the refusal stops mentioning that flooring is allowed', KEYS,
     u'Lay a floor here if you like, but nothing can be built on it',
     u'Nothing can be built on it'),
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
    assert old in s, 'fault anchor missing in %s: %r' % (rel, old[:60])
    assert s.count(old) == 1, 'fault anchor not unique in %s: %r' % (rel, old[:60])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    code, out = run()
    caught = code != 0
    print('  %-57s %-5d %s' % (label, code, 'yes' if caught else 'NO -- THE PROOF IS BLIND'))
    if not caught:
        ok = False
        print(out[-700:])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s)

code, out = run()
print('  %-57s %-5d %s' % ('restored', code, 'clean' if code == 0 else 'STILL FAILING'))
sys.exit(0 if ok and code == 0 else 1)
