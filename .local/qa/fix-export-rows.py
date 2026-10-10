# -*- coding: utf-8 -*-
"""Unwrap the prose bullets in the new section: a wrapped `- ` line reads as a stranded
continuation to check-queue-integrity.py, and it is right to say so."""
import io
import re
import sys

NL = chr(10)
TODO = "docs/TODO.md"
MARK = "## Owner direction — a second pair of repos: the mod and the public face only (2026-10-05)"

text = io.open(TODO, encoding="utf-8").read()
if MARK not in text:
    print("section not found")
    sys.exit(1)
head, tail = text.split(MARK, 1)

lines = tail.split(NL)
out = []
for line in lines:
    # A continuation is an indented, non-empty line following a bullet. Join it up rather than
    # leaving it stranded; the queue's rule is that a row is one line.
    if (out and re.match(r"^\s{2,}\S", line) and out[-1].lstrip().startswith("- ")
            and not out[-1].lstrip().startswith("- [")):
        out[-1] = out[-1].rstrip() + " " + line.strip()
        continue
    out.append(line)

io.open(TODO, "w", encoding="utf-8", newline=NL).write(head + MARK + NL.join(out))
print("unwrapped %d line(s)" % (len(lines) - len(out)))
