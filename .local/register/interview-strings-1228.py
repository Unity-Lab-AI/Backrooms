# -*- coding: utf-8 -*-
"""The interview's player-facing words.

Every refusal is a literal key, and every one of them can actually happen -- invariant 136 wants a
workflow whose clauses can refuse, and a refusal nobody can read is a refusal that may as well
return false. The wording says what to DO about it wherever there is something to do.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed')

INVESTIGATION = [
    ('RR_UI_InterviewPrompt',
     u'Two crew do not agree about this. {0} can take both statements and file one of them as the '
     u'company’s version; the other stays on the record either way.'),
    ('RR_UI_FileAccount', u'File {0}’s account'),
    ('RR_UI_AccountFiled',
     u'Filed: the company accepts {0}’s account, after an interview by {1} on day {2}. The '
     u'other account remains on the record.'),
    ('RR_Interview_NoInterviewer',
     u'Nobody on staff can take a statement about this. An interviewer needs Social {0}, has to be '
     u'awake, able to talk and not one of the crew who gave an account.'),
    ('RR_Interview_Inactive', u'The branch is not operating, so nothing can be filed.'),
    ('RR_Interview_RecordUnavailable',
     u'That record or that observation is no longer on the company’s books.'),
    ('RR_Interview_RecordClosed',
     u'Analysis on this record is already complete. A filed conclusion is not reopened; the '
     u'disagreement stays on the record as it was when the report was written.'),
    ('RR_Interview_NotDisputed', u'Nobody disagrees about this observation.'),
    ('RR_Interview_NoSuchAccount', u'That account is not on this observation.'),
    ('RR_Interview_WitnessUnavailable',
     u'The person who gave that account is dead or no longer employed here, so the company will not '
     u'file it on their behalf.'),
    ('RR_Interview_InterviewerUnavailable',
     u'The interviewer is unavailable. They must be employed, awake, able to talk, and not in a '
     u'mental break.'),
    ('RR_Interview_InterviewerIsWitness',
     u'That staff member gave one of these accounts. Somebody else has to take the statements.'),
    ('RR_Interview_InterviewerUnskilled',
     u'That staff member is not experienced enough with people to take a statement the company will '
     u'file.'),
]

PORTALS = [
    ('RR_Event_AccountFiled',
     u'{0}: the company has filed {1}’s account after an interview by {2}. The disagreeing '
     u'account stays on the record.'),
]


def insert(filename, anchor, rows):
    path = os.path.join(KEYED, filename)
    s = io.open(path, encoding='utf-8').read()
    assert anchor in s, '%s: anchor missing' % filename
    block = u''
    for key, value in rows:
        assert u'<%s>' % key not in s, '%s already declares %s' % (filename, key)
        block += u'  <%s>%s</%s>\n' % (key, value, key)
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(anchor, block + anchor, 1))
    print('%s: %d string(s) added' % (filename, len(rows)))


insert('RR_Investigation.xml', u'  <RR_UI_AccountAgrees>', INVESTIGATION)
insert('RR_Portals.xml', u'  <RR_Portals_ApproachCellReserved>', PORTALS)
