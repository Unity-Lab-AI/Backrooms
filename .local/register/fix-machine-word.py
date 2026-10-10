# -*- coding: utf-8 -*-
"""Two real vocabulary violations in my own wiki, and one narrow exemption for a pane name.

`check-doc-conformance.py` flagged five uses of *"the machine"* across the new wiki. **Two were
genuine** -- I called the gate "the machine" in a nav table, in the one document set whose whole
job is to use the project's words. Those are fixed in the prose.

**Three were the pane's actual name.** `RR_OperationsExpeditions.xml` declares
`<RR_UI_Machine>Machine</RR_UI_Machine>`, so the Operations pane a player is looking for is
labelled exactly *Machine*. A page that cannot write *"the Machine pane"* cannot tell anybody
where to click.

So the exemption is **the two-word phrase `Machine pane` only**, capital M, nothing else. The ban
on calling a gate "the machine" is otherwise untouched -- which matters, because it just caught me
twice.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")
README = os.path.join(REPO, "README.md")
INDEX = os.path.join(REPO, "docs", "wiki", "index.md")

# ---------------------------------------------------------------- the two real violations
EDITS = [
    (README, u"| **[Gates and connections](docs/wiki/gates.md)** | The machine and what fits through it |",
     u"| **[Gates and connections](docs/wiki/gates.md)** | The gate, and what fits through it |"),
    (INDEX, u"| **[Gates and connections](gates.md)** | The machine, what it holds open, what fits through |",
     u"| **[Gates and connections](gates.md)** | The gate, what it holds open, what fits through |"),
]

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:46], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8").read()
    io.open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new, 1))

# ---------------------------------------------------------------- the narrow exemption
OLD = u'''DOC_BANNED = [(term, re.compile(r"\\b" + term.replace(" ", r"\\s+") + r"s?\\b", re.I))
              for term in DOC_BANNED_TERMS]'''

NEW = u'''DOC_BANNED = [(term, re.compile(r"\\b" + term.replace(" ", r"\\s+") + r"s?\\b", re.I))
              for term in DOC_BANNED_TERMS]

# **One exemption, and it is two words wide.** The Operations pane a player clicks is labelled
# exactly `Machine` -- `RR_OperationsExpeditions.xml` declares
# `<RR_UI_Machine>Machine</RR_UI_Machine>` -- so a page that cannot write *"the Machine pane"*
# cannot tell anybody where to click.
#
# Capital M, immediately followed by `pane`. **Nothing else.** The ban on calling a gate "the
# machine" is otherwise untouched, which matters: it caught two real violations in the wiki's own
# first draft, in the one document set whose whole job is to use the project's words.
DOC_BANNED_EXEMPT = re.compile(r"\\bMachine\\s+pane\\b")'''

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("BANNED ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("two real violations fixed; exemption constant added")
print("NEXT: the exemption has to be APPLIED, not merely defined -- see apply-machine-exempt.py")
