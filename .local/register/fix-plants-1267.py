# -*- coding: utf-8 -*-
"""This suite's plants are five-tuples, and mine were four.

`plant-startplacement.py` names the proof to run **per plant** -- `(label, path, old, new,
command)` -- because it covers two proofs. My seven plants were written in the four-tuple shape
every other suite uses, so the runner raised `IndexError` on `plant[4]` before planting anything.

**It failed loudly and planted nothing**, which is the behaviour that matters: an instrument that
cannot run must not look like one that ran.

My claims went into `proof-starts.py`, so that is the command each of them names.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

STARTS_PROOF = u'STARTS_PROOF = ".local/register/proof-starts.py"'

EDITS = [
    # Bind the proof these seven plants are judged by, beside the existing PROOF binding.
    (u'PROOF = ".local/register/proof-startplacement.py"',
     u'PROOF = ".local/register/proof-startplacement.py"\n' + STARTS_PROOF),

    (u'''     '                    insightOperationId = done ? projectId + ":insight" : null,' + chr(10), ""),''',
     u'''     '                    insightOperationId = done ? projectId + ":insight" : null,' + chr(10), "",
     STARTS_PROOF_NAME),'''),

    (u'''     '                    insightOperationId = done ? projectId + ":insight" : null,',
     '                    insightOperationId = done ? "" : null,'),''',
     u'''     '                    insightOperationId = done ? projectId + ":insight" : null,',
     '                    insightOperationId = done ? "" : null,', STARTS_PROOF_NAME),'''),

    (u'''     "(!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))",
     "(!p.insightCommitted || true)"),''',
     u'''     "(!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))",
     "(!p.insightCommitted || true)", STARTS_PROOF_NAME),'''),

    (u'''    ("the corporate start stops beginning with its research finished", STARTS,
     "      <li>RR_GateTelemetry</li>" + chr(10), ""),''',
     u'''    ("the corporate start stops beginning with its research finished", STARTS,
     "      <li>RR_GateTelemetry</li>" + chr(10), "", STARTS_PROOF_NAME),'''),

    (u'''     + "                yield break;" + chr(10) + "            }",
     "            if (!IsDesignated) { yield break; }"),''',
     u'''     + "                yield break;" + chr(10) + "            }",
     "            if (!IsDesignated) { yield break; }", STARTS_PROOF_NAME),'''),

    (u'''    ("the toggle appears on a door away from the headquarters", GATECOMP,
     "                || campaign.Headquarters != parent.Map",
     "                || false"),''',
     u'''    ("the toggle appears on a door away from the headquarters", GATECOMP,
     "                || campaign.Headquarters != parent.Map",
     "                || false", STARTS_PROOF_NAME),'''),

    (u'''    ("the toggle binds the first of several providers instead of refusing", GATECOMP,
     "                    if (console == null || battery == null || bench == null)",
     "                    if (false)"),''',
     u'''    ("the toggle binds the first of several providers instead of refusing", GATECOMP,
     "                    if (console == null || battery == null || bench == null)",
     "                    if (false)", STARTS_PROOF_NAME),'''),
]

text = io.open(SUITE, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:62]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
# The placeholder above is replaced with the binding's NAME, not its value.
text = text.replace(u"STARTS_PROOF_NAME", u"STARTS_PROOF")
io.open(SUITE, "w", encoding="utf-8", newline="").write(text)
print("seven plants are five-tuples naming proof-starts.py")
