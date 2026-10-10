# -*- coding: utf-8 -*-
"""Two defects in the claims just added to `proof-stranded-crew.py`.

1. **Wrong helper name.** The proof's comment stripper is `strip_comments`, not `no_comments`.
   The verification caught it; the block had already been written, so this repairs it in place.

2. **`"Pawn" not in register` is a substring test masquerading as a type test, and it is
   FALSE.** `NoteLostPawn`, `TakeLostPawnName`, `LostPawnCapacity`, `lostPawnNames` and
   `LostPawnCount` all contain the letters `Pawn`. The claim would have failed on names that
   prove the opposite of what it feared.

   **This is the duplicate-string trap again** -- 0.12.75-dev's label claim asserted an
   expression appearing in two overrides and held while no bond was named. A claim has to assert
   the thing, not letters that happen to spell it. What matters is whether the file references
   the **`Pawn` type**: a field, a parameter, a cast, a generic argument, or a saved reference.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stranded-crew.py")

EDITS = [
    (u'register = no_comments(io.open(os.path.join(',
     u'register = strip_comments(io.open(os.path.join('),

    (u'''      and "public string TakeLostPawnName()" in register
      and "Pawn" not in register,''',
     u'''      and "public string TakeLostPawnName()" in register
      # **NOT `"Pawn" not in register`.** That is a substring test wearing a type test's clothes,
      # and it is false: `NoteLostPawn`, `TakeLostPawnName`, `LostPawnCapacity`, `lostPawnNames`
      # and `LostPawnCount` all contain those letters. Duplicate-string trap, same shape as
      # 0.12.75-dev's label claim. What matters is whether the **type** is referenced at all.
      and not any(token in register for token in
                  ("List<Pawn>", "Pawn pawn", "Pawn ", "(Pawn", "<Pawn>", "Pawn)")),'''),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:52]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u"no_comments" in after:
    failures.append("the wrong helper name is still referenced")
if u'and "Pawn" not in register,' in after:
    failures.append("the substring test is still there")
if u'("List<Pawn>", "Pawn pawn", "Pawn ", "(Pawn", "<Pawn>", "Pawn)")' not in after:
    failures.append("the type test was not written")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("helper name corrected; the substring test replaced with a type test")
