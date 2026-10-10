# -*- coding: utf-8 -*-
"""Two corrections to the laboratory start, both measured off the owner's running game.

## 1. The record book, which every expedition requires and the start never shipped

`ExpeditionCargo.RecordBooksRequired` is **1**, of `CompRouteEvidence.NativeCarrierDef` -- Core's
`TextBook`. The live scan found **112 fixtures across 17 types and not one book**, so
`RR_Exp_MissingRecordBook` refuses the first dispatch on a fresh laboratory start, every time.
Owner, from the game: *"if i use approach gate and dispach to coordinate it says no book, i have
no books"*.

The recorder was folded into a book at 0.12.24-dev and **the start's stock was never updated to
carry one.** Two go on the archive shelves: one to take, one in reserve.

## 2. The door the owner had to cut, at relative (51, 24)

Diffed by position against the live map, with the facility origin solved at **(120, 120)** from
three single-instance devices. Exactly one live opening has no authored counterpart, and **no
authored door is missing**.

(51, 24) is in the **compound's east perimeter wall**, at the dead end of the east-west service
corridor -- the run `((9, 24), 42, True)` conduits along. The authored layout walls that corridor
off at its east end, so the owner cut an exterior door. It is authored now.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILDER = os.path.join(REPO, ".local", "register", "build-async-facility.py")

# ---------------------------------------------------------------- the book
OLD_FIXTURE = u'''    # --- the corridor nook between them
    ("HorseshoesPin",       (20, 33), {"stuff": "Steel"}),
]'''

NEW_FIXTURE = u'''    # --- the corridor nook between them
    ("HorseshoesPin",       (20, 33), {"stuff": "Steel"}),
    # --- the archive: THE RECORD BOOKS, without which no expedition can be dispatched
    #
    # `ExpeditionCargo.RecordBooksRequired` is 1, of Core's `TextBook`. The start shipped none,
    # so `RR_Exp_MissingRecordBook` refused the first dispatch on every fresh laboratory start.
    # Owner, from a running game: *"if i use approach gate and dispach to coordinate it says no
    # book, i have no books"*.
    #
    # The recorder was folded into the book at 0.12.24-dev and the stock was never updated to
    # carry one. **Two**: one to take into the field, one in reserve, because a branch that
    # loses its only book cannot work until it makes another.
    ("TextBook",            (11, 47), {}),
    ("TextBook",            (14, 47), {}),
]'''

text = io.open(BUILDER, encoding="utf-8").read()
if text.count(OLD_FIXTURE) != 1:
    print("FIXTURE ANCHOR PROBLEM: %d" % text.count(OLD_FIXTURE))
    raise SystemExit(1)
text = text.replace(OLD_FIXTURE, NEW_FIXTURE, 1)

# ---------------------------------------------------------------- the door
OLD_DOOR = u"""    (18, 46),   # archive   -> west corridor"""
NEW_DOOR = u"""    (18, 46),   # archive   -> west corridor
    # The one opening the owner had to cut themselves, found by diffing live doors against
    # authored ones with the facility origin solved at (120, 120): the compound's EAST
    # PERIMETER WALL at the dead end of the east-west service corridor. The corridor the
    # `((9, 24), 42, True)` conduit run follows was walled off at its east end, so there was no
    # way out of the facility on that side.
    (51, 24),   # service corridor -> outside, east perimeter"""

if text.count(OLD_DOOR) != 1:
    print("DOOR ANCHOR PROBLEM: %d" % text.count(OLD_DOOR))
    raise SystemExit(1)
text = text.replace(OLD_DOOR, NEW_DOOR, 1)
io.open(BUILDER, "w", encoding="utf-8", newline="").write(text)

after = io.open(BUILDER, encoding="utf-8").read()
failures = []
if after.count(u'("TextBook",') != 2:
    failures.append("expected two TextBook fixtures, found %d" % after.count(u'("TextBook",'))
if u"(51, 24),   # service corridor -> outside, east perimeter" not in after:
    failures.append("the owner's door was not authored")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("builder updated: two record books on the archive shelves, and the east perimeter door")
