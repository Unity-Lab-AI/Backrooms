# -*- coding: utf-8 -*-
"""Plant every fault the interview proof exists to catch."""
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join('.local', 'register', 'proof-interview.py')

INT = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'EvidenceInterview.cs')
OBS = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'EvidenceObservations.cs')
PANE = os.path.join('src', 'RimroomsAsyncIndustries', 'UI', 'OperationsEvidence.cs')

FAULTS = [
    ('an analysed record can be reopened', INT,
     u'''            if (record.analyzedTick >= 0 || record.analysisReport != null)
            { return CompanyActionResult.Refused("RR_Interview_RecordClosed"); }''',
     u'            // frozen-report guard removed'),

    ('the interviewer may be one of the witnesses', INT,
     u'''            if (observation.WitnessLoadIds.Contains(interviewerId, StringComparer.Ordinal))
            { return CompanyActionResult.Refused("RR_Interview_InterviewerIsWitness"); }''',
     u'            // self-interview guard removed'),

    ('the skill floor stops being enforced by the action', INT,
     u'''            if (interviewer.skills.GetSkill(SkillDefOf.Social).Level < MinimumInterviewerSocial)
            { return CompanyActionResult.Refused("RR_Interview_InterviewerUnskilled"); }''',
     u'            // skill floor removed'),

    ('an account not on the observation can be filed', INT,
     u'''            if (string.IsNullOrWhiteSpace(filedWitnessLoadId) ||
                !observation.WitnessLoadIds.Contains(filedWitnessLoadId, StringComparer.Ordinal))
            { return CompanyActionResult.Refused("RR_Interview_NoSuchAccount"); }''',
     u'            // membership guard removed'),

    ('the picker becomes order-dependent instead of deterministic', INT,
     u'''                if (skill > bestSkill || (skill == bestSkill &&
                    string.Compare(loadId, bestId, StringComparison.Ordinal) < 0))''',
     u'                if (skill > bestSkill)'),

    ('settling rewrites the observation fact', OBS,
     u'            filedWitnessLoadId = filedLoadId;',
     u'            filedWitnessLoadId = filedLoadId;\n            markerNumber = 0;'),

    ('the analysis snapshot stops comparing the settlement', OBS,
     u'                filedWitnessLoadId == other.filedWitnessLoadId &&',
     u'                true &&'),

    ('a half-written settlement becomes valid', OBS,
     u'''            else if (!string.IsNullOrEmpty(filedWitnessLoadId) ||
                !string.IsNullOrEmpty(interviewerLoadId) || !string.IsNullOrEmpty(interviewerName))
            {
                // Settlement details without a tick is the same defect from the other side.
                return false;
            }''',
     u'            // half-written guard removed'),

    ('no available interviewer hides the section instead of saying so', PANE,
     u'''                listing.Label("RR_Interview_NoInterviewer".Translate(
                    RimroomsCampaignComponent.MinimumInterviewerSocial));
                return;''',
     u'                return;'),
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
        print(out[-600:])
    io.open(full(rel), 'w', encoding='utf-8', newline='').write(s)

code, out = run()
print('  %-57s %-5d %s' % ('restored', code, 'clean' if code == 0 else 'STILL FAILING'))
sys.exit(0 if ok and code == 0 else 1)
