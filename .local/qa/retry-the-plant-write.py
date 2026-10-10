# -*- coding: utf-8 -*-
"""The plant write gets the same retry the restore already had.

## What happened, on the full-battery run of 0.12.86-dev

`plant-areas-and-debrief.py` died at `OSError: [Errno 22] Invalid argument` while
**writing a planted fault** to `OperationsFacilities.cs`, twelve plants into
thirteen. It failed safely: the sentinel is written before the plant, so
`tools/check-plant-residue.py` refused the tree immediately and the file turned
out to be untouched -- `heading: "RR_Debrief_Count".Translate(holds.Count)` still
present, the diff still only the day's own edits, the file ending properly.

**The suite already knew about this exact failure and had already handled it in
one direction.** `_rr_restore`'s own docstring says it: *"The failure this exists
for was transient -- `OSError: [Errno 22]` on a path this same loop had already
written twice -- so a retry turns it into a non-event."* The restore retries five
times. The plant write, two lines above it, did not retry at all -- so a
transient on the way in aborted the sweep while the identical transient on the
way out was a non-event.

The asymmetry is the bug. A destructive instrument that cannot finish is an
instrument whose remaining plants never run, and this suite had eleven of
twenty-five still to set.
"""
import io
import sys

NL = chr(10)
PATH = ".local/register/plant-areas-and-debrief.py"

HELPER = '''def _rr_plant(path, planted):
    """Write the planted fault, with the same retry the restore has.

    **The asymmetry this fixes aborted a full-battery run.** `_rr_restore` below
    retries five times against `OSError: [Errno 22]` -- a transient this loop has
    hit repeatedly on a path it had already written twice. The plant write did
    not retry, so the same transient on the way in killed the sweep while on the
    way out it was a non-event.

    The sentinel is written before this is called and stays if every attempt
    fails, so a half-written plant is refused by `check-plant-residue.py` rather
    than built on. Raising with it in place is deliberate: the next plant must
    not be set on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(planted)
            if io.open(path, encoding="utf-8").read() == planted:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.4 * (attempt + 1))
    raise SystemExit("FATAL: could not plant into %s after five attempts (%s). The sentinel is "
                     "left in place on purpose -- run tools/check-plant-residue.py and check "
                     "that file by hand before building anything." % (path, last))


'''

EDITS = [
    ("def _rr_restore(path, original):", HELPER + "def _rr_restore(path, original):"),
    ('    io.open(path, "w", encoding="utf-8", newline="").write(original.replace(old, new, 1))',
     "    _rr_plant(path, original.replace(old, new, 1))"),
]

text = io.open(PATH, encoding="utf-8").read()
problems = 0

if "_rr_plant" in text:
    print("already retrying")
    sys.exit(0)

if NL + "import time" + NL not in text:
    old = NL + "import sys" + NL
    if text.count(old) != 1:
        print("COULD NOT FIND A SINGLE `import sys` (%d)" % text.count(old))
        problems += 1
    else:
        text = text.replace(old, NL + "import sys" + NL + "import time" + NL, 1)
        print("added `import time`")

for old, new in EDITS:
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d): %r" % (text.count(old), old.strip()[:76]))
        problems += 1
        continue
    text = text.replace(old, new)
    print("patched: %s" % old.strip()[:70])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % PATH)
