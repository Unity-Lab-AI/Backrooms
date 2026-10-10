# -*- coding: utf-8 -*-
"""Sixteen suites shared ONE sentinel, so a later suite erased an earlier one's failure.

## The fourth time a planted fault reached the working tree, and the checker was blind to it

`plant-containment.py` planted a fault, ran the proof, and then its restore raised
`OSError: [Errno 22] Invalid argument` writing the file back. The `finally` is written so that
`_rr_unmark()` is **never reached** when the restore throws -- which is correct, and the sentinel
really was left behind.

**And then `plant-coordinate-layout.py` ran, and its own `_rr_unmark()` deleted it.** One sentinel
path, sixteen writers: a later suite's success erases an earlier suite's unresolved failure.
`check-plant-residue.py` then reported `OK: no planted fault is in the source tree` while
`campaign.ClearBreachResponded();` was missing from `ContainmentProtocol.cs`.

Three instances of this defect were fixed by devnull handling, by a `finally`, and by inventing the
sentinel. **This is the first one the sentinel itself could not see**, and it is the shape the
sentinel was invented for.

## What changes

* **The sentinel name carries the suite's own filename**, so no suite can clear another's. The
  checker globs them, so any number of stale ones are reported together.
* **The restore retries and then verifies.** The error that caused this was transient -- the same
  path had just been written successfully twice -- so one retry would have made it a non-event.
  A restore that still cannot be verified leaves the sentinel and exits non-zero, which stops the
  sweep instead of planting the next fault on top.
"""
import glob
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTER = os.path.join(REPO, ".local", "register")
CHECKER = os.path.join(REPO, "tools", "check-plant-residue.py")

OLD_PREAMBLE = u'''_RR_SENTINEL = os.path.join(".local", "register", ".plant-in-progress")


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass
'''

NEW_PREAMBLE = u'''# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))
'''

patched = 0
for suite in sorted(glob.glob(os.path.join(REGISTER, "plant-*.py"))):
    text = io.open(suite, encoding="utf-8").read()
    if text.count(OLD_PREAMBLE) != 1:
        print("PREAMBLE ANCHOR PROBLEM in %s: %d" % (os.path.basename(suite),
                                                     text.count(OLD_PREAMBLE)))
        raise SystemExit(1)
    text = text.replace(OLD_PREAMBLE, NEW_PREAMBLE, 1)
    # The two suites that still wrote the restore bare go through the verified form.
    text = text.replace(u'io.open(path, "w", encoding="utf-8", newline="").write(original)\n        _rr_unmark()',
                        u'_rr_restore(path, original)\n        _rr_unmark()')
    if "import time" not in text:
        text = text.replace(u"import sys\n", u"import sys\nimport time\n", 1)
    io.open(suite, "w", encoding="utf-8", newline="").write(text)
    patched += 1
print("%d suites now carry their own sentinel and a verified, retrying restore" % patched)

OLD_CHECK = u'SENTINEL = os.path.join(REPO, ".local", "register", ".plant-in-progress")'
NEW_CHECK = u'''# **GLOBBED, because there is one sentinel per suite now.** They shared a single path until
# 0.12.72-dev, so a later suite's success deleted an earlier suite's unresolved failure and this
# checker reported a clean tree with `campaign.ClearBreachResponded();` missing from the source.
SENTINELS = os.path.join(REPO, ".local", "register", ".plant-in-progress*")'''

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD_CHECK) != 1:
    print("CHECKER ANCHOR PROBLEM: %d" % text.count(OLD_CHECK))
    raise SystemExit(1)
text = text.replace(OLD_CHECK, NEW_CHECK, 1)
text = text.replace(u"    if not os.path.isfile(SENTINEL):",
                    u"    stale = sorted(glob.glob(SENTINELS))\n    if not stale:", 1)
text = text.replace(u'        detail = io.open(SENTINEL, encoding="utf-8").read().strip()',
                    u'        detail = "; ".join(io.open(path, encoding="utf-8").read().strip()\n'
                    u'                            for path in stale)', 1)
text = text.replace(u'    print("  rm .local/register/.plant-in-progress")',
                    u'    for path in stale:\n        print("  rm %s" % path)', 1)
if "import glob" not in text:
    text = text.replace(u"import io\n", u"import glob\nimport io\n", 1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text)
print("check-plant-residue.py globs every suite's sentinel")
