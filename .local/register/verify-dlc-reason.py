# -*- coding: utf-8 -*-
"""Verify the `check-dlc-gating.py` reason fix, distinguishing a live claim from a quoted one.

**`reaim-dlc-reason.py` refused its own successful edit.** It searched the result for the phrase
it had removed -- and the replacement prose *quotes* that phrase in the sentence explaining the
removal. The write had already landed; only the verification was wrong.

**This is the SIXTH instance of an instrument reading its own explanatory prose**, and the first
where the instrument was mine rather than one of the checkers:

  * 0.12.46-dev -- `check-compliance.py` flagged a patch for containing `PatchOperationReplace`
    in the comment explaining why a replace is wrong. It strips XML comments now.
  * 0.12.75-dev -- `check-register-compliance.py` refused a patch whose comment contained
    `statBases`, in the sentence saying the value *cannot* be a `statBases` entry. It strips
    comments now too.
  * and three before those.

The fix is the same one both checkers took: **assert against the live form, not the mention.** A
removed claim quoted inside the explanation of its removal is the record working correctly, which
is exactly why the record is kept.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-dlc-gating.py")

text = io.open(CHECKER, encoding="utf-8").read()

# The stale reason AS A LIVE ASSERTION. This is the sentence that claimed it, in the form it
# claimed it in: a red error *in a mod whose entire claim* is Core-only.
LIVE = u"a red error in a mod whose entire claim is that it needs nothing but Core."

# The same words AS A QUOTATION, inside the sentence that retires them. Italicised, and
# immediately followed by the statement that it is no longer true.
QUOTED = (u"*a mod" + chr(10)
          + u"whose entire claim is that it needs nothing but Core* -- is **no longer true")

failures = []
if LIVE in text:
    failures.append("the stale reason is still asserted as a live claim")
if QUOTED not in text:
    failures.append("the retired claim is not quoted in the sentence that retires it, so a "
                    "reader cannot see what changed or why")
if u"keep the graceful guard anyway" not in text:
    failures.append("the owner's posture answer is not recorded as the replacement reason")
if u"MayRequire" not in text:
    failures.append("the rule itself no longer names MayRequire")

# And the rule must be untouched: the mechanism, not the prose, is what ships.
for required in (u"def that references DLC-only content without a MayRequire gate",
                 u"Anything defined outside `Core` is DLC-only."):
    if required not in text:
        failures.append("the RULE changed, not only its reason: missing %r" % required[:52])

print("")
for failure in failures:
    print("  FAIL %s" % failure)
if failures:
    print("")
    print("VERIFICATION FAILED: %d problem(s)" % len(failures))
    raise SystemExit(1)
print("  OK   the stale reason is gone as a live claim")
print("  OK   it is quoted once, in the sentence retiring it, so the change is legible")
print("  OK   the replacement reason is the owner's own posture answer")
print("  OK   the rule itself is unchanged")
print("")
print("VERIFIED: reason replaced, rule intact")
