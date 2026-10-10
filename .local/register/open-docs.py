# -*- coding: utf-8 -*-
"""The public documentation direction, verbatim, every clause its own row."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - the public wiki - 2026-10-01 (0.12.77-dev)

Owner, verbatim:

> **"make sure to update all the public facing doc and workflow docs(remember public facing docs
> are concise easy to read and have no in house dev names and no todo numbering and no actual work
> information but are concise and informatitve laying out the full wiki of the dame how to play how
> to set it all up rimsort all of it, we will add links later to the mod workfshop and collection
> workshop for this collection and mod makeing sure all are propely all linked to gether when we
> build a github page repo deployed hosting the full howto readmes and wiki of the full mod and all
> of that( the mod registar can be a good resources fo laying everyhting out but public facing
> documnets ARE NOT to be text walls get to each point in as short a way as possible"**

- [~] **"make sure to update all the public facing doc and workflow docs"**
- [~] **"public facing docs are concise easy to read"**
- [~] **"and have no in house dev names"**
- [~] **"and no todo numbering"**
- [~] **"and no actual work information"**
- [~] **"but are concise and informatitve"**
- [~] **"laying out the full wiki of the dame how to play how to set it all up rimsort all of it"**
- [~] **"we will add links later to the mod workfshop and collection workshop for this collection
  and mod"** - placeholders authored now, clearly marked, so the page has the slots and nothing
  claims a link that does not exist yet
- [~] **"makeing sure all are propely all linked to gether"**
- [~] **"when we build a github page repo deployed hosting the full howto readmes and wiki of the
  full mod and all of that"**
- [~] **"the mod registar can be a good resources fo laying everyhting out"**
- [~] **"public facing documnets ARE NOT to be text walls get to each point in as short a way as
  possible"**
- [~] **`docs/HOWTO.md` IS IN THE READER-FACING LIST AND IS NOT A READER DOCUMENT.** It opens
  *"This is the practical guide for anyone (human or build agent) opening this repository"* and
  carries in-house tooling names, owner-decision identifiers, branch cascade procedure, the
  task-record pattern and the workflow ledger. **It violates three of the owner's four rules at
  once** and has been held to the reader vocabulary by `check-doc-conformance.py` for its whole
  life, which is why nobody noticed it was the wrong kind of document
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))

after = io.open(TODO, encoding="utf-8").read()
for phrase in (u"ARE NOT to be text walls get to each point in as short a way as possible",
               u"no in house dev names"):
    if phrase not in after:
        print("VERBATIM MISSING: %s" % phrase)
        raise SystemExit(1)
print("TODO opened for the public wiki; owner's words verbatim and verified")
