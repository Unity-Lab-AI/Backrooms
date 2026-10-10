# -*- coding: utf-8 -*-
"""My own absence claim read my own comments. Forty-first instance.

`"EnsureAssemblyBill" not in console` failed against correct code, because the comment explaining
why that method is gone names it -- which is exactly what a comment about a removed thing does.
`proof-coordinate-layout.py` has carried a comment-free `code()` view since 0.12.62-dev for this
precise reason and `proof-generation-batch.py` strips comments outright. **This proof had neither,
so it gets one.**

Writing the rule down has never been enough. What works is that the plants and the proofs refuse,
immediately, every time.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

HELPER_ANCHOR = u'''def _read_mod(*parts):'''

HELPER = u'''def _code(text):
    """The source with its line comments removed.

    **An absence claim cannot read raw source.** `"EnsureAssemblyBill" not in console` failed
    against correct code because the comment explaining the method's removal names it. Forty-first
    instance of that trap in this project; `proof-coordinate-layout.py` has had this view since
    0.12.62-dev and `proof-generation-batch.py` strips comments outright.
    """
    kept = []
    for line in text.split(chr(10)):
        if line.lstrip().startswith("//"):
            continue
        kept.append(line)
    return chr(10).join(kept)


''' + HELPER_ANCHOR

EDITS = [
    (u'console = _read(_SRC, "Gate", "CompRimroomsGateConsole.cs")\n'
     u'nativebinding = _read(_SRC, "Gate", "NativeGateBinding.cs")',
     u'console = _read(_SRC, "Gate", "CompRimroomsGateConsole.cs")\n'
     u'nativebinding = _read(_SRC, "Gate", "NativeGateBinding.cs")\n'
     u'# Comment-free views, for the absence clauses only.\n'
     u'console_code = _code(console)\n'
     u'nativebinding_code = _code(nativebinding)'),

    (u'      and "EnsureAssemblyBill" not in console\n'
     u'      and "EnsureAssemblyBill" not in nativebinding\n'
     u'      and "BillStack.AddBill" not in console\n'
     u'      and "new Bill_Production(" not in console,',
     u'      and "EnsureAssemblyBill" not in console_code\n'
     u'      and "EnsureAssemblyBill" not in nativebinding_code\n'
     u'      and "BillStack.AddBill" not in console_code\n'
     u'      and "new Bill_Production(" not in console_code,'),

    (u'      and "existing.repeatMode = BillRepeatModeDefOf.RepeatCount;" not in console\n'
     u'      and "existing.suspended = Gate.AssemblyComplete" not in console,',
     u'      and "existing.repeatMode = BillRepeatModeDefOf.RepeatCount;" not in console_code\n'
     u'      and "existing.suspended = Gate.AssemblyComplete" not in console_code,'),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:58]))
if text.count(HELPER_ANCHOR) != 1:
    problems.append("%d of HELPER_ANCHOR" % text.count(HELPER_ANCHOR))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
text = text.replace(HELPER_ANCHOR, HELPER, 1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("the absence clauses read a comment-free view")
