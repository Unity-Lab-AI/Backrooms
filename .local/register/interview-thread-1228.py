# -*- coding: utf-8 -*-
"""Thread the interview fields through snapshot, equality, validity and save.

Exactly the discipline 0.12.25-dev needed for the accounts list, and for exactly the same reason:
`EvidenceAnalysisReport` freezes a snapshot of the observations and `IsValidFor` compares it back
with `SameSnapshot`. A saved field those two do not know about lets a frozen report agree with a
record it no longer matches, with **no observable symptom until much later**.

The interview additionally refuses to run on an analysed record, so in practice a settlement cannot
appear after a report is frozen. Both protections ship: the refusal is the rule, and the snapshot
comparison is what catches the rule being wrong.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'EvidenceObservations.cs')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:80]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:80]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ snapshot copies it
sub('''                accounts = (accounts ?? new List<WitnessAccountRecord>())
                    .Where(a => a != null).Select(a => a.SnapshotCopy()).ToList()
            };''',
    '''                accounts = (accounts ?? new List<WitnessAccountRecord>())
                    .Where(a => a != null).Select(a => a.SnapshotCopy()).ToList(),
                filedWitnessLoadId = filedWitnessLoadId,
                interviewer = interviewer,
                interviewerLoadId = interviewerLoadId,
                interviewerName = interviewerName,
                interviewTick = interviewTick
            };''')

# ------------------------------------------------------------------ equality notices it
sub('''                recorderCarrierName == other.recorderCarrierName && SameAccounts(other);''',
    '''                recorderCarrierName == other.recorderCarrierName && SameAccounts(other) &&
                filedWitnessLoadId == other.filedWitnessLoadId &&
                interviewerLoadId == other.interviewerLoadId &&
                interviewerName == other.interviewerName && interviewTick == other.interviewTick;''')

# ------------------------------------------------------------------ validity constrains it
sub('''            List<string> speakers = WitnessLoadIds.ToList();
            if (speakers.Distinct(StringComparer.Ordinal).Count() != speakers.Count) { return false; }''',
    '''            List<string> speakers = WitnessLoadIds.ToList();
            if (speakers.Distinct(StringComparer.Ordinal).Count() != speakers.Count) { return false; }

            // A settlement is only coherent if it settles something, files an account that is
            // actually on this record, and names who took the statement. A half-written settlement
            // would read as "the company filed somebody's account" without saying whose.
            if (interviewTick >= 0)
            {
                if (!Disputed || string.IsNullOrWhiteSpace(filedWitnessLoadId) ||
                    string.IsNullOrWhiteSpace(interviewerLoadId) ||
                    string.IsNullOrWhiteSpace(interviewerName) ||
                    !speakers.Contains(filedWitnessLoadId, StringComparer.Ordinal) ||
                    string.Equals(interviewerLoadId, filedWitnessLoadId, StringComparison.Ordinal))
                { return false; }
            }
            else if (!string.IsNullOrEmpty(filedWitnessLoadId) ||
                !string.IsNullOrEmpty(interviewerLoadId) || !string.IsNullOrEmpty(interviewerName))
            {
                // Settlement details without a tick is the same defect from the other side.
                return false;
            }''')

# ------------------------------------------------------------------ the save
sub('''            Scribe_Collections.Look(ref accounts, "rr_accounts", LookMode.Deep);''',
    '''            Scribe_Collections.Look(ref accounts, "rr_accounts", LookMode.Deep);
            Scribe_Values.Look(ref filedWitnessLoadId, "rr_filedWitnessLoadId");
            Scribe_References.Look(ref interviewer, "rr_interviewer");
            Scribe_Values.Look(ref interviewerLoadId, "rr_interviewerLoadId");
            Scribe_Values.Look(ref interviewerName, "rr_interviewerName");
            Scribe_Values.Look(ref interviewTick, "rr_interviewTick", -1);''')

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('interview fields threaded: SnapshotCopy, SameSnapshot, IsValidFor, ExposeData')
