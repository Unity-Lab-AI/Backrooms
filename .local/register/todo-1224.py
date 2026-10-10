# -*- coding: utf-8 -*-
"""Close the two TODO rows 0.12.24-dev finished. Status changes and appended evidence only.

LAW: never delete TODO info. Every original word of both rows stays exactly where it was; a
closure note is appended after it. Row 664 also carries a correction rather than a deletion --
it names `RR_MakeEvidenceCase` as remaining, and that recipe has not existed for fourteen
checkpoints, so the row was stale in a way nobody had measured.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'TODO.md')

s = io.open(PATH, encoding='utf-8').read()

FIELD_GEAR_OLD = (u'**Still open:** retiring the `RR_FieldRecorder` *def* itself, which is the one '
                  u'genuinely buyable carryable item left, and needs a migration decision because '
                  u'saved Things reference it.')
FIELD_GEAR_NEW = (u'**CLOSED, 0.12.24-dev — and the migration decision was the owner’s: '
                  u'*"Fold it into the record book crews already carry"*.** The kit is now Core’s '
                  u'`TextBook`, resolved through `CompRouteEvidence.NativeCarrierDef` rather than by '
                  u'name, and **the def was NOT deleted** — so there is no save break. It stays '
                  u'loadable because saves contain recorders, and is never granted or sold again: the '
                  u'recipe retired with its whole file, both scenario grants became `TextBook`, and '
                  u'`tradeability` is `None`. **All four field-gear replacements are now done.** The '
                  u'answer had been written down at 0.9.9-dev and sat for fourteen checkpoints because '
                  u'no proof asserted anything about it. Record: '
                  u'[the recorder became the book](implementation/RECORD_BOOK_IMPLEMENTATION.md).')

RECIPES_OLD = u'Remaining: `RR_MakeFieldRecorder`, `RR_MakeEvidenceCase`.'
RECIPES_NEW = (u'Remaining: `RR_MakeFieldRecorder`, `RR_MakeEvidenceCase`. '
               u'— **CLOSED, 0.12.24-dev. The row was stale by one:** `RR_MakeEvidenceCase` had '
               u'already gone with the sealed case in 0.10.9-dev and nobody updated this line, so the '
               u'remaining count was one, not two. `RR_MakeFieldRecorder` is **retired with its whole '
               u'file** — `RR_FieldFabricationBase` had no other child — and the package '
               u'allowlist no longer names it. Its precondition was met first: '
               u'`RR_Procurement_RecordBooks` wires the procurement route, so a branch that loses its '
               u'book orders another instead of being unable to dispatch anyone. **One recipe remains '
               u'of the original five, `RR_AssembleMachineGate`, live and kept.**')

for old, new in ((FIELD_GEAR_OLD, FIELD_GEAR_NEW), (RECIPES_OLD, RECIPES_NEW)):
    assert old in s, 'anchor missing: %r' % old[:70]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:70]
    s = s.replace(old, new, 1)

# Status markers: both rows are done now, so [~] becomes [x]. The description is untouched.
for marker in (u'- [~] **Legacy field gear**', u'- [~] **Five recipes.**'):
    assert marker in s, marker
    s = s.replace(marker, marker.replace(u'[~]', u'[x]'), 1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('TODO: two rows closed, every original word kept')
