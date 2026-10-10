"""Size every `##` section of docs/TODO.md and show its marker census.

Shows where the bytes are, not where the rows are. A section can hold two open
rows and two thousand words of finished-session narrative, and a row count says
it is open work while a byte count says most of it is history.
"""

import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

MARKER = re.compile(r"^\s*- \[( |x|~|T)\]")
H2 = re.compile(r"^## (.*)$")

lines = io.open(os.path.join(REPO, "docs", "TODO.md"), encoding="utf-8").read().split("\n")

bounds = [(H2.match(line).group(1), index)
          for index, line in enumerate(lines) if H2.match(line)]

out = []
out.append(u"%-8s %-6s %-26s %s" % ("BYTES", "ROWS", "CENSUS", "SECTION"))
out.append(u"-" * 118)

total_history = 0
for position, (title, start) in enumerate(bounds):
    end = bounds[position + 1][1] if position + 1 < len(bounds) else len(lines)
    span = lines[start:end]
    size = sum(len(line) + 1 for line in span)
    counts = {" ": 0, "x": 0, "~": 0, "T": 0}
    row_bytes = 0
    for line in span:
        found = MARKER.match(line)
        if found:
            counts[found.group(1)] += 1
            row_bytes += len(line) + 1
    rows = sum(counts.values())
    prose = size - row_bytes
    out.append(u"%-8d %-6d [ ]%-3d [~]%-3d [T]%-3d prose %-6d %s"
               % (size, rows, counts[" "], counts["~"], counts["T"], prose, title[:52]))
    # A launch-findings / checkpoint section is a dated record by its title.
    if re.search(r"\d\.\d+\.\d+-dev|launch findings|DONE", title):
        total_history += prose

out.append(u"")
out.append(u"prose inside sections whose titles are dated checkpoint records: %.1f KB"
           % (total_history / 1024.0))
out.append(u"whole file: %.1f KB" % (sum(len(line) + 1 for line in lines) / 1024.0))

path = os.path.join(HERE, "section-sizes.txt")
io.open(path, "w", encoding="utf-8", newline="").write(u"\n".join(out))
print(u"\n".join(out).encode("ascii", "replace").decode("ascii"))
