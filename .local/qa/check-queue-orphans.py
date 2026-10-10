"""Report headings and bold lead-ins with no rows under them, in a queue file.

A heading or a `**...:**` lead-in standing over nothing reads as outstanding
work when there is none left beneath it. Run over the post-move preview to
confirm the archive left the queue readable, and over docs/TODO.md afterwards.

Usage: python .local/qa/check-queue-orphans.py <path>
"""

import io
import re
import sys

HEAD = re.compile(r"^(#{2,6}) (.*)$")
LEAD_IN = re.compile(r"^\*\*.*:(\*\*)?\s*$")
ROW = re.compile(r"^\s*- \[( |x|~|T)\]")

path = sys.argv[1] if len(sys.argv) > 1 else "docs/TODO.md"
lines = io.open(path, encoding="utf-8").read().split("\n")

anchors = [index for index, line in enumerate(lines)
           if HEAD.match(line) or LEAD_IN.match(line)]

problems = 0
for position, anchor in enumerate(anchors):
    end = anchors[position + 1] if position + 1 < len(anchors) else len(lines)
    body = lines[anchor + 1:end]
    if any(ROW.match(line) for line in body):
        continue
    if not any(line.strip() for line in body):
        problems += 1
        print("EMPTY   %5d  %s" % (anchor + 1, lines[anchor][:88]))

print()
print("%s: %d anchors, %d standing over nothing" % (path, len(anchors), problems))
