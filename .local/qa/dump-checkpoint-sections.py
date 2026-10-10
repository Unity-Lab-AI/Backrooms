"""Dump the dated-checkpoint `##` sections of docs/TODO.md to a UTF-8 file.

These are finished session records by their own titles -- a launch finding, a
coordinate rebuild stage, a doc sweep. Each still holds a few open rows, which
is why the section-level mover left them: a section with an open row in it is
not a closed record. The rows belong in the queue; the record belongs in the
archive. This dump is so the split can be authored by reading, not guessed.
"""

import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

H2 = re.compile(r"^## (.*)$")
DATED = re.compile(r"\d\.\d+\.\d+-dev|launch findings|Releasing a place|doc sweep")

lines = io.open(os.path.join(REPO, "docs", "TODO.md"), encoding="utf-8").read().split("\n")
bounds = [(H2.match(line).group(1), index)
          for index, line in enumerate(lines) if H2.match(line)]

out = []
for position, (title, start) in enumerate(bounds):
    end = bounds[position + 1][1] if position + 1 < len(bounds) else len(lines)
    if not DATED.search(title):
        continue
    out.append(u"#" * 110)
    out.append(u"SECTION lines %d-%d  (%d bytes)" % (start + 1, end, sum(len(l) + 1 for l in lines[start:end])))
    out.append(u"#" * 110)
    out.extend(lines[start:end])
    out.append(u"")

path = os.path.join(HERE, "checkpoint-sections.txt")
io.open(path, "w", encoding="utf-8", newline="").write(u"\n".join(out))
print("wrote %s  (%d lines)" % (path, len(out)))
