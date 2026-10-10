"""Dump the open rows that carry finished-work narrative, to a UTF-8 file.

Written to a file rather than printed: the Windows console is cp1252 and these
rows contain arrows and em dashes, which is what broke the last attempt.
"""

import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

ROW = re.compile(r"^\s*- \[( |~|T)\]")
SHIPPED = re.compile(
    r"\b(BUILT|SHIPPED|DONE|RECONCILED|SWEPT|PROVED|CLOSED|DECIDED AGAINST"
    r"|PARTLY BUILT|HELD|ANSWERED|RETIRED|FIXED)\b"
)

lines = io.open(os.path.join(REPO, "docs", "TODO.md"), encoding="utf-8").read().split("\n")

out = []
total = 0
for number, line in enumerate(lines, start=1):
    if ROW.match(line) and SHIPPED.search(line):
        total += len(line) + 1
        out.append(u"=" * 100)
        out.append(u"LINE %d  (%d chars)" % (number, len(line)))
        out.append(u"=" * 100)
        out.append(line)
        out.append(u"")

out.append(u"TOTAL: %d rows, %.1f KB" % (len([l for l in out if l.startswith("LINE")]),
                                         total / 1024.0))

path = os.path.join(HERE, "dirty-rows.txt")
io.open(path, "w", encoding="utf-8", newline="").write(u"\n".join(out))
print("wrote %s" % path)
