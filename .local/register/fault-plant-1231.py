# -*- coding: utf-8 -*-
"""Plant every fault the door-run proof exists to catch."""
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join('.local', 'register', 'proof-gate-door-run.py')

RUN = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'GateDoorRun.cs')
BINDING = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'NativeGateBinding.cs')
FOOTPRINT = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'GateFootprint.cs')
COMP = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGate.cs')
KEYS = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed',
                    'RR_NativeGate.xml')

FAULTS = [
    ('an extension becomes a gate in its own right', BINDING,
     u'                return !IsRunExtension && NativeDoorProvider() &&',
     u'                return NativeDoorProvider() &&'),

    ('the rect stops being the run, so width is per door again', FOOTPRINT,
     u'            get { return RunRect; }',
     u'            get { return parent == null || !parent.Spawned ? CellRect.Empty : parent.OccupiedRect(); }'),

    ('the cell count goes back to the def size, so a run costs one door to power', FOOTPRINT,
     u'                CellRect rect = GateOccupiedRect;\n                if (rect.Area > 0) { return rect.Area; }',
     u'                CellRect rect = CellRect.Empty;\n                if (rect.Area > 0) { return rect.Area; }'),

    ('a bounding box with a hole in it counts as an opening', RUN,
     u'                if (union.Area != extensions.Count + own.Area) { return own; }',
     u'                // solidity check removed'),

    ('a run may exceed the legal gate sizes', RUN,
     u'                if (!LegalGateFootprint(new IntVec2(union.Width, union.Height))) { return own; }',
     u'                // legality check removed'),

    ('a working gate can be re-cut', RUN,
     u'            if (IsOpening || IsSpinningUp) { return CompanyActionResult.Refused("RR_GateRun_ActiveCannotExtend"); }\n'
     u'            if (parent == null || !parent.Spawned || parent.Map == null)',
     u'            if (parent == null || !parent.Spawned || parent.Map == null)'),

    ('releasing leaves extensions pointing at a released host', RUN,
     u'                if (other != null && other.nativeRunHost == parent) { other.nativeRunHost = null; }',
     u'                if (other != null && other.nativeRunHost == parent) { }'),

    ('the run stops being saved', RUN,
     u'            Scribe_References.Look(ref nativeRunHost, "rr_gateRunHost");',
     u'            // host reference no longer saved'),

    ('the save method stops being called', COMP,
     u'            ExposeGateRun();',
     u'            // ExposeGateRun no longer called'),

    ('candidates stop being sorted', RUN,
     u'            found.Sort(delegate(Thing left, Thing right)',
     u'            NoSortAtAll(delegate(Thing left, Thing right)'),

    ('the banned word comes back into player text', KEYS,
     u'<RR_GateRun_Label>Opening: {0} door(s), {1} wide</RR_GateRun_Label>',
     u'<RR_GateRun_Label>Doorway: {0} door(s), {1} wide</RR_GateRun_Label>'),
]


def run_proof():
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

print('  planted fault                                                  exit  caught')
ok = True
for label, rel, old, new in FAULTS:
    s = backups[rel]
    assert old in s, 'fault anchor missing in %s: %r' % (rel, old[:70])
    assert s.count(old) == 1, 'fault anchor not unique in %s: %r' % (rel, old[:70])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    code, out = run_proof()
    caught = code != 0
    print('  %-61s %-5d %s' % (label, code, 'yes' if caught else 'NO -- THE PROOF IS BLIND'))
    if not caught:
        ok = False
        print(out[-500:])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s)

code, out = run_proof()
print('  %-61s %-5d %s' % ('restored', code, 'clean' if code == 0 else 'STILL FAILING'))
sys.exit(0 if ok and code == 0 else 1)
