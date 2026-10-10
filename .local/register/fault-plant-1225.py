# -*- coding: utf-8 -*-
"""Plant every fault this proof exists to catch, one at a time, and restore after each.

Two of these are the silent kind: a snapshot that stops comparing accounts, and a copy that
aliases the live list. Neither changes any observable behaviour until an analysis report is
frozen and the record then gains a dispute -- at which point the report quietly agrees with a
record it no longer matches.
"""
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join('.local', 'register', 'proof-contradictory-accounts.py')

OBS = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'EvidenceObservations.cs')
LINE = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'RequestLine.cs')
SITE = os.path.join('src', 'RimroomsAsyncIndustries', 'Threats', 'FirstSliceSiteComponent.cs')

FAULTS = [
    ('the old receipt-mismatch refusal comes back', OBS,
     u'bool agrees = prior.SameFact(kind, roomIndex, referencedRoomIndex, markerNumber, witnessRoom.index);',
     u'''if (!prior.SameFact(kind, roomIndex, referencedRoomIndex, markerNumber, witnessRoom.index))
                { return CompanyActionResult.Refused("RR_Company_ReceiptMismatch"); }
                bool agrees = true;'''),

    ('a disagreement stops counting as testimony', LINE,
     u'                        if (!IsEmployedPawn(speaker)) { continue; }',
     u'                        if (!IsEmployedPawn(speaker) || !account.Agrees) { continue; }'),

    ('the duplicate-witness guard is removed', OBS,
     u'''            foreach (string existing in WitnessLoadIds)
            {
                if (string.Equals(existing, loadId, StringComparison.Ordinal)) { return false; }
            }''',
     u'            // guard removed'),

    ('the analysis snapshot stops comparing accounts', OBS,
     u'recorderCarrierName == other.recorderCarrierName && SameAccounts(other);',
     u'recorderCarrierName == other.recorderCarrierName;'),

    ('the snapshot aliases the live account list', OBS,
     u'''                accounts = (accounts ?? new List<WitnessAccountRecord>())
                    .Where(a => a != null).Select(a => a.SnapshotCopy()).ToList()''',
     u'                accounts = accounts'),

    ('the site tick stops telling the player', SITE,
     u'{ Note("RR_Event_AccountsDisagree", Coordinate.Label, witness.LabelShortCap.ToString()); }',
     u'{ }'),
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

print('  planted fault                                        exit  caught')
ok = True
for label, rel, old, new in FAULTS:
    s = backups[rel]
    assert old in s, 'fault anchor missing in %s: %r' % (rel, old[:60])
    assert s.count(old) == 1, 'fault anchor not unique in %s' % rel
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    code, out = run()
    caught = code != 0
    print('  %-51s %-5d %s' % (label, code, 'yes' if caught else 'NO -- THE PROOF IS BLIND'))
    if not caught:
        ok = False
        print(out[-700:])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s)

code, out = run()
print('  %-51s %-5d %s' % ('restored', code, 'clean' if code == 0 else 'STILL FAILING'))
sys.exit(0 if ok and code == 0 else 1)
