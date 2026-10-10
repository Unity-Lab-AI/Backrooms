# -*- coding: utf-8 -*-
"""The state edits NOW.md is still missing for 0.12.39-dev.

**Written as one script that asserts everything first and writes once at the end**, because that
is the failure this keeps hitting: a `sub()` helper that throws mid-script leaves the file
untouched, so the edits *before* the throw are silently lost too. It has now happened twice in
this session -- at 0.12.38-dev six state edits vanished, and here eight did.

The fix is the order: every anchor is checked before any replacement is committed to the string,
and the single write happens only after all of them succeed. Nothing partial, nothing silent.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

EDITS = [
    (u"| Published | **0.12.38-dev**.", u"| Published | **0.12.39-dev**."),
    (u"| Build | **190 C# files, 87 package files**",
     u"| Build | **191 C# files, 87 package files**"),
    (u"SHA-256 `24BF762A9D3C767167102FFCABCC77E08B418A0DF062E34AC6D9706FA4F7DE7C`",
     u"SHA-256 `13031FCBAE5FB6238197D3EB36AD6B2AE0042B91E4B5F05E0AFF6252A736EFCD`"),
    (u"| Proofs | **THIRTY-FIVE** in `.local/register/proof-*.py`.",
     u"| Proofs | **THIRTY-SIX** in `.local/register/proof-*.py`."),
    (u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.38-dev**.",
     u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.39-dev**."),
    (u"## What shipped this session, 0.7.1 → 0.12.38",
     u"## What shipped this session, 0.7.1 → 0.12.39"),
    (u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 64 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 48 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 470 done
```""",
     u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 59 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 48 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 475 done
```"""),
    (u"## The scope lesson from 0.12.38-dev, because it will happen again",
     u"""## VERIFY THE PROOF PASSES BEFORE YOU PLANT ANYTHING

At 0.12.39-dev a fault-plant run reported **17 of 17 caught** and it was **worthless**. A fix to
the proof had introduced a syntax error, so the proof exited non-zero unconditionally and **every
plant registered as caught**. It looked like a clean sweep.

**A plant run against a broken proof proves nothing and looks perfect.** The first step of every
plant run is now:

```
python .local/register/proof-<name>.py >/dev/null 2>&1; echo "must be 0: $?"
```

and only then plant. The harness already re-reads every write to guard against a half-restore
(0.12.36-dev); this is the other half of the same lesson.

**And the same shape bit the doc scripts twice.** A patch script whose `sub()` throws part way
leaves the file untouched, so the edits *before* the throw are lost silently — six state edits at
0.12.38-dev, eight at 0.12.39-dev, both found only by grepping the file afterwards. **Assert every
anchor first, write once at the end, and grep the result.**

---

## The scope lesson from 0.12.38-dev, because it will happen again"""),
]

# Every anchor is checked before anything is committed, so a missing one cannot cost the others.
text = original
problems = []
for old, new in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("all %d state edits applied in one write" % len(EDITS))
