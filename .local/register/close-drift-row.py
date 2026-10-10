# -*- coding: utf-8 -*-
"""Close the register-drift row. The owner named the cause and it verifies exactly.

Owner, 2026-10-01, verbatim: *"6 row gap is dlcs"*.

It is, precisely. `tools/register-query.py` parses **295 rows** and the live load order holds
**289 other mods**. Rows **4 through 9** are `Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`
and `Odyssey` -- six rows that are not third-party mods at all. **295 - 6 = 289**, which is the
live count with nothing left over.

**So there was no drift.** The row was opened as an unexamined gap, which was the honest state at
the time, and the owner closed it in five words.

## One thing worth recording while closing it

Register rows 5 to 9 carry **stance `Optional`**, and row 5 carries **firmness `Provisional`**.
The owner has now made all five expansions **hard dependencies**. That is the register being
**guidance rather than law** working exactly as the owner's standing correction says it should:
*"remmebr its not law but guidance"*. The row is not wrong; it is superseded, and by the only
authority that can supersede it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

OLD = u"""- [ ] **The register drift this surfaced, not yet resolved** - `tools/register-query.py` parses
  **295 rows** against **289 live other-mods**. The live load order is the right source for a
  dependency list and was used; **the gap between the two is unexamined** and belongs to the
  register, not to About.xml"""

NEW = u"""- [x] **The register drift this surfaced, not yet resolved** - `tools/register-query.py` parses
  **295 rows** against **289 live other-mods**. The live load order is the right source for a
  dependency list and was used; **the gap between the two is unexamined** and belongs to the
  register, not to About.xml. **CLOSED by the owner, verbatim: *"6 row gap is dlcs"*.** Verified
  rather than taken: rows **4-9** are `Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly` and
  `Odyssey` -- six rows that are not third-party mods. **295 - 6 = 289**, the live count exactly,
  nothing left over. **There was no drift.** Worth recording while closing it: rows 5-9 carry
  stance **`Optional`** and row 5 carries firmness **`Provisional`**, and the owner has made all
  five expansions **hard dependencies** - which is *"remmebr its not law but guidance"* working as
  intended. The rows are not wrong, they are superseded, by the only authority that can supersede
  them"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(TODO, encoding="utf-8").read()
if u'*"6 row gap is dlcs"*' not in after:
    print("VERBATIM MISSING")
    raise SystemExit(1)
if u"- [ ] **The register drift" in after:
    print("ROW STILL OPEN")
    raise SystemExit(1)
print("drift row closed; owner's words verbatim; every original word kept")
