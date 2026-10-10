"""Inventory docs/TODO.md: every heading, every status marker, with nesting depth.

Read-only. Prints a map so the extraction can be planned against real structure
rather than an assumption about it.
"""

import re
import sys

PATH = "docs/TODO.md"

MARKER = re.compile(r"^(\s*)- \[( |x|~|T)\]")
HEADING = re.compile(r"^(#{1,6}) (.*)$")
BOLD_DIRECTION = re.compile(r"^\*\*(Verbatim|Owner|What|Where|Sequencing|Four items|Nine items)")

with open(PATH, encoding="utf-8") as handle:
    lines = handle.read().split("\n")

counts = {" ": 0, "x": 0, "~": 0, "T": 0}
depths = {}

for index, line in enumerate(lines, start=1):
    heading = HEADING.match(line)
    if heading:
        print(f"{index:>5}  {'#' * len(heading.group(1)):<7} {heading.group(2)[:90]}")
        continue
    marker = MARKER.match(line)
    if marker:
        indent = len(marker.group(1))
        status = marker.group(2)
        counts[status] += 1
        depths.setdefault((indent, status), 0)
        depths[(indent, status)] += 1
        continue
    if BOLD_DIRECTION.match(line):
        print(f"{index:>5}  DIRECT  {line[:90]}")

print()
print("counts:", counts)
print("by (indent, status):")
for key in sorted(depths):
    print("   ", key, depths[key])
print("total lines:", len(lines))
